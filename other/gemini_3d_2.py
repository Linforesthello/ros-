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

        # --- [基准参数] ---
        self.hsv_orange_lower = np.array([5, 120, 100])
        self.hsv_orange_upper = np.array([25, 255, 255])
        self.hsv_blue_lower = np.array([100, 120, 100])
        self.hsv_blue_upper = np.array([135, 255, 255])

        # --- [跟踪与 ROI] ---
        self.tracking_state = 'SEARCHING'
        self.last_z = 1.0                
        self.base_roi_size = 200         
        self.lost_frames_count = 0
        self.max_lost_frames = 15 

        self.bridge = CvBridge()
        self.prev_time = time.time()
        self.fps = 0.0

        # --- [卡尔曼滤波器] ---
        # 状态: [x, y, vx, vy] (像素空间)
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.01
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 8

        # --- [相机内参] ---
        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        self.cam_info_sub = self.create_subscription(CameraInfo, '/camera/color/camera_info', self.camera_info_callback, 10)
        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')

        self.ts = message_filters.ApproximateTimeSynchronizer([self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)

        self.ball_pub = self.create_publisher(PointStamped, 'tracked_ball', 10)
        self.get_logger().info("基准深度跟踪节点已启动")

    def camera_info_callback(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.destroy_subscription(self.cam_info_sub)

    def get_robust_depth(self, depth_img, u, v, win_size=5):
        """ 在像素(u,v)周围采样，获取稳健的深度值 """
        h, w = depth_img.shape
        u, v = int(u), int(v)
        u_min, u_max = max(0, u - win_size//2), min(w, u + win_size//2)
        v_min, v_max = max(0, v - win_size//2), min(h, v + win_size//2)
        
        roi = depth_img[v_min:v_max, u_min:u_max]
        valid_depths = roi[roi > 0] # 剔除无效值
        if len(valid_depths) == 0:
            return 0.0
        return float(np.median(valid_depths))

    def image_callback(self, color_msg, depth_msg):
        if not self.camera_info_received: return

        # 计算 FPS
        now = time.time()
        self.fps = 1.0 / (now - self.prev_time)
        self.prev_time = now

        try:
            color_img = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth_img = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        except: return

        h, w = color_img.shape[:2]

        # 1. 卡尔曼预测
        prediction = self.kf.predict()
        pred_u, pred_v = int(prediction[0].item()), int(prediction[1].item())

        # 2. ROI 裁剪 (基于深度动态缩放)
        roi_size = int(max(100, self.base_roi_size / self.last_z))
        u_min, v_min = max(0, pred_u - roi_size//2), max(0, pred_v - roi_size//2)
        u_max, v_max = min(w, pred_u + roi_size//2), min(h, pred_v + roi_size//2)

        if self.tracking_state == 'TRACKING':
            search_area = color_img[v_min:v_max, u_min:u_max]
            cv2.rectangle(color_img, (u_min, v_min), (u_max, v_max), (255, 255, 0), 2)
        else:
            search_area = color_img

        # 3. 颜色识别
        hsv = cv2.cvtColor(search_area, cv2.COLOR_BGR2HSV)
        mask = cv2.bitwise_or(cv2.inRange(hsv, self.hsv_orange_lower, self.hsv_orange_upper),
                              cv2.inRange(hsv, self.hsv_blue_lower, self.hsv_blue_upper))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_ball = False
        if contours:
            # 找到面积最大的轮廓
            c = max(contours, key=cv2.contourArea)
            ((lu, lv), radius) = cv2.minEnclosingCircle(c)
            
            if radius > 2:
                # 转换回全图像素坐标
                gu = int(lu + (u_min if self.tracking_state == 'TRACKING' else 0))
                gv = int(lv + (v_min if self.tracking_state == 'TRACKING' else 0))
                
                # 获取深度
                z_raw = self.get_robust_depth(depth_img, gu, gv)
                if z_raw > 0:
                    found_ball = True
                    self.last_z = z_raw / 1000.0
                    
                    # 卡尔曼校正
                    if self.tracking_state == 'SEARCHING':
                        self.kf.statePost = np.array([[gu],[gv],[0],[0]], np.float32)
                    self.kf.correct(np.array([[np.float32(gu)],[np.float32(gv)]], np.float32))
                    
                    self.tracking_state = 'TRACKING'
                    self.lost_frames_count = 0
                    
                    # 发布世界坐标 (X, Y, Z)
                    xm = (gu - self.cx) * self.last_z / self.fx
                    ym = (gv - self.cy) * self.last_z / self.fy
                    
                    point_msg = PointStamped()
                    point_msg.header = color_msg.header
                    point_msg.point.x, point_msg.point.y, point_msg.point.z = xm, ym, self.last_z
                    self.ball_pub.publish(point_msg)
                    
                    cv2.circle(color_img, (gu, gv), int(radius), (0, 0, 255), 2)

        if not found_ball:
            self.lost_frames_count += 1
            if self.lost_frames_count > self.max_lost_frames:
                self.tracking_state = 'SEARCHING'

        # UI 显示
        cv2.putText(color_img, f"FPS: {int(self.fps)} Z: {self.last_z:.2f}m State: {self.tracking_state}", 
                    (10, 30), 1, 1.5, (0, 255, 0), 2)
        cv2.imshow("Base Depth Tracker", color_img)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = BallTrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()