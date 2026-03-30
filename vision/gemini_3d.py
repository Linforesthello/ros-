#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PointStamped
import message_filters

class BallTrackerNode(Node):
    def __init__(self):
        super().__init__('ball_tracker_node')

        # --- [参数定义] ---
        self.hsv_orange_lower = np.array([5, 120, 100])
        self.hsv_orange_upper = np.array([25, 255, 255])
        self.hsv_blue_lower = np.array([100, 120, 100])
        self.hsv_blue_upper = np.array([135, 255, 255])

        # --- [ROI 动态调整参数] ---
        self.tracking_state = 'SEARCHING'
        self.last_z = 1.0                # 上一次有效的深度
        self.base_roi_size = 180         # 1.0米时的基准 ROI 大小
        self.lost_frames_count = 0
        self.max_lost_frames = 15 

        self.bridge = CvBridge()

        # --- [卡尔曼滤波器] ---
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.005
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 10
        self.kf.errorCovPost = np.eye(4, dtype=np.float32)

        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        self.cam_info_sub = self.create_subscription(CameraInfo, '/camera/color/camera_info', self.camera_info_callback, 10)
        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')
        self.ts = message_filters.ApproximateTimeSynchronizer([self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)
        self.ball_pub = self.create_publisher(PointStamped, 'tracked_ball', 10)

    def camera_info_callback(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.destroy_subscription(self.cam_info_sub)

    def image_callback(self, color_msg, depth_msg):
        if not self.camera_info_received: return
        try:
            color_image = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth_image = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        except Exception: return

        img_h, img_w = color_image.shape[:2]

        # --- 1. 卡尔曼预测 ---
        prediction = self.kf.predict()
        pred_x, pred_y = int(prediction[0].item()), int(prediction[1].item())

        # --- 2. 动态计算 ROI 大小 (根据深度反比例缩放) ---
        # 如果 z=1m, size=180; 如果 z=4m, size=45 (但设定最小值为 60 防止太小搜不到)
        dynamic_roi_size = int(max(60, self.base_roi_size / self.last_z))
        
        roi_x_min, roi_y_min = 0, 0
        if self.tracking_state == 'TRACKING':
            roi_x_min = max(0, pred_x - dynamic_roi_size // 2)
            roi_y_min = max(0, pred_y - dynamic_roi_size // 2)
            roi_x_max = min(img_w, pred_x + dynamic_roi_size // 2)
            roi_y_max = min(img_h, pred_y + dynamic_roi_size // 2)
            search_image = color_image[roi_y_min:roi_y_max, roi_x_min:roi_x_max]
            cv2.rectangle(color_image, (roi_x_min, roi_y_min), (roi_x_max, roi_y_max), (255, 255, 0), 2)
        else:
            search_image = color_image

        # --- 3. 视觉识别 ---
        hsv = cv2.cvtColor(search_image, cv2.COLOR_BGR2HSV)
        mask = cv2.bitwise_or(cv2.inRange(hsv, self.hsv_orange_lower, self.hsv_orange_upper),
                              cv2.inRange(hsv, self.hsv_blue_lower, self.hsv_blue_upper))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_ball = False
        best_gx, best_gy = pred_x, pred_y
        final_state = prediction

        if contours:
            min_dist = float('inf')
            target_cnt = None
            for cnt in contours:
                ((lx, ly), radius) = cv2.minEnclosingCircle(cnt)
                if radius > 1.5: # 4m外可能只有不到2像素
                    gx, gy = int(lx + roi_x_min), int(ly + roi_y_min)
                    dist = np.sqrt((gx - pred_x)**2 + (gy - pred_y)**2)
                    if dist < min_dist:
                        min_dist, target_cnt = dist, cnt
                        best_gx, best_gy, best_r = gx, gy, radius

            if target_cnt is not None:
                found_ball = True
                if self.tracking_state == 'SEARCHING':
                    init_state = np.array([[best_gx], [best_gy], [0], [0]], dtype=np.float32)
                    self.kf.statePost = init_state
                    self.kf.statePre = init_state
                
                measure = np.array([[np.float32(best_gx)], [np.float32(best_gy)]], dtype=np.float32)
                final_state = self.kf.correct(measure)
                self.tracking_state = 'TRACKING'
                self.lost_frames_count = 0

        # --- 4. 丢失处理 ---
        if not found_ball:
            self.lost_frames_count += 1
            if self.lost_frames_count > self.max_lost_frames:
                self.tracking_state = 'SEARCHING'

        # --- 5. 深度处理与发布 ---
        if self.tracking_state == 'TRACKING' or found_ball:
            cx_p = max(0, min(img_w - 1, int(final_state[0].item())))
            cy_p = max(0, min(img_h - 1, int(final_state[1].item())))

            try:
                d_val = depth_image[cy_p, cx_p]
                # 深度覆盖搜索：如果中心点无效，扩大范围找深度
                if d_val == 0:
                    patch = depth_image[max(0, cy_p-3):cy_p+4, max(0, cx_p-3):cx_p+4]
                    v_d = patch[patch > 0]
                    if len(v_d) > 0: d_val = np.median(v_d)

                if d_val > 0:
                    z_m = float(d_val) / 1000.0
                    self.last_z = z_m # 更新深度，用于下一帧缩放 ROI
                    
                    x_m = (cx_p - self.cx) * z_m / self.fx
                    y_m = (cy_p - self.cy) * z_m / self.fy
                    
                    p_msg = PointStamped()
                    p_msg.header = color_msg.header
                    p_msg.point.x, p_msg.point.y, p_msg.point.z = x_m, y_m, z_m
                    self.ball_pub.publish(p_msg)
            except Exception: pass

            cv2.circle(color_image, (cx_p, cy_p), 5, (0, 255, 0), -1)
            if found_ball:
                cv2.circle(color_image, (best_gx, best_gy), int(best_r), (0, 0, 255), 2)

        cv2.putText(color_image, f"Mode:{self.tracking_state} Z:{self.last_z:.2f}m", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        cv2.imshow("Adaptive ROI Tracker", color_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = BallTrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()