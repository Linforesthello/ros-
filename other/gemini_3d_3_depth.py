#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PointStamped
import message_filters
import time

class BallTrackerNode(Node):
    def __init__(self):
        super().__init__('ball_tracker_node')

        # --- [1. 宽松的 HSV 阈值] ---
        # 调低了饱和度(S)下限到 70，明度(V)下限到 50，适应弱光
        self.orange_low = np.array([0, 70, 50]);  self.orange_high = np.array([25, 255, 255])
        self.blue_low = np.array([100, 70, 50]);  self.blue_high = np.array([130, 255, 255])

        self.tracking_state = 'SEARCHING'
        self.last_z = 1.0
        self.lost_count = 0
        self.found_count = 0  # 连续发现计数

        self.bridge = CvBridge()
        self.prev_time = time.time()
        
        # --- [2. 简化卡尔曼 - 仅作平滑用] ---
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

        # --- [3. ROS 通信] ---
        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        self.info_sub = self.create_subscription(CameraInfo, '/camera/color/camera_info', self.info_cb, 10)
        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')
        self.ts = message_filters.ApproximateTimeSynchronizer([self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)
        self.ball_pub = self.create_publisher(PointStamped, 'tracked_ball', 10)

    def info_cb(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True

    def image_callback(self, color_msg, depth_msg):
        if not self.camera_info_received: return
        try:
            img = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        except: return

        h, w = img.shape[:2]
        
        # --- 1. 动态 ROI 决策 ---
        # 如果还没锁定，或者丢帧了，直接全图搜索，不玩花哨的预测
        if self.tracking_state == 'SEARCHING':
            search_area = img
            offset_x, offset_y = 0, 0
        else:
            # 锁定状态下，使用预测中心开启 ROI
            pred = self.kf.predict()
            roi_size = int(max(150, 250 / self.last_z))
            x1 = max(0, int(pred[0].item() - roi_size//2))
            y1 = max(0, int(pred[1].item() - roi_size//2))
            x2 = min(w, x1 + roi_size); y2 = min(h, y1 + roi_size)
            search_area = img[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)

        # --- 2. 识别逻辑 ---
        hsv = cv2.cvtColor(search_area, cv2.COLOR_BGR2HSV)
        m1 = cv2.inRange(hsv, self.orange_low, self.orange_high)
        m2 = cv2.inRange(hsv, self.blue_low, self.blue_high)
        mask = cv2.bitwise_or(m1, m2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        found_now = False
        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 50:  # 面积阈值，过滤杂点
                ((ux, uy), rad) = cv2.minEnclosingCircle(c)
                gx, gy = int(ux + offset_x), int(uy + offset_y)
                
                # 采样深度
                z_roi = depth[max(0, gy-2):gy+3, max(0, gx-2):gx+3]
                z_vals = z_roi[z_roi > 0]
                
                if z_vals.size > 0:
                    zm = float(np.median(z_vals)) / 1000.0
                    self.last_z = zm
                    found_now = True
                    self.found_count += 1
                    
                    # 更新卡尔曼
                    self.kf.correct(np.array([[np.float32(gx)], [np.float32(gy)]], dtype=np.float32))
                    
                    # 发布坐标 (仅在连续找到 2 帧后才信任并进入 TRACKING)
                    if self.found_count > 2:
                        self.tracking_state = 'TRACKING'
                        self.lost_count = 0
                        xm = (gx - self.cx) * zm / self.fx
                        ym = (gy - self.cy) * zm / self.fy
                        p = PointStamped(); p.header = color_msg.header
                        p.point.x, p.point.y, p.point.z = xm, ym, zm
                        self.ball_pub.publish(p)
                    
                    cv2.circle(img, (gx, gy), int(rad), (0, 0, 255), 3)
                    cv2.putText(img, f"Dist: {zm:.2f}m", (gx, gy-20), 1, 1.5, (0, 255, 0), 2)

        if not found_now:
            self.found_count = 0
            self.lost_count += 1
            if self.lost_count > 10:
                self.tracking_state = 'SEARCHING'

        # FPS & UI
        fps = 1.0 / (time.time() - self.prev_time)
        self.prev_time = time.time()
        cv2.putText(img, f"FPS: {int(fps)} | {self.tracking_state}", (20, 40), 1, 2, (255, 0, 255), 2)
        cv2.imshow("Final Rescue Tracker", img)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = BallTrackerNode()
    rclpy.spin(node)
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()