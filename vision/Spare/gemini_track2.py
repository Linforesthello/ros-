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
    """
    双色球体跟踪节点：
    1. 支持橙色+蓝色双色掩膜合并。
    2. 引入动态 ROI (感兴趣区域) 锁定机制，防止远距离脱锁。
    3. 修复卡尔曼滤波矩阵类型不匹配导致的崩溃问题。
    """
    def __init__(self):
        super().__init__('ball_tracker_node')

        # --- [参数定义: 双色 HSV 阈值] ---
        # 橙色范围
        self.hsv_orange_lower = np.array([5, 120, 120])
        self.hsv_orange_upper = np.array([22, 255, 255])
        # 蓝色范围
        self.hsv_blue_lower = np.array([100, 120, 120])
        self.hsv_blue_upper = np.array([130, 255, 255])

        # --- [ROI 注意力机制参数] ---
        self.tracking_state = 'SEARCHING' # 'SEARCHING' 或 'TRACKING'
        self.roi_window_size = 150        # ROI 搜索窗口大小 (像素)
        self.lost_frames_count = 0
        self.max_lost_frames = 20         # 丢失多少帧后重置为全图搜索

        self.bridge = CvBridge()

        # --- [卡尔曼滤波器初始化] ---
        # 状态向量: [x, y, vx, vy], 测量向量: [x, y]
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.005
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 10
        self.kf.errorCovPost = np.eye(4, dtype=np.float32)

        # --- 相机参数与通信 ---
        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        self.cam_info_sub = self.create_subscription(
            CameraInfo, '/camera/color/camera_info', self.camera_info_callback, 10)
        
        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')

        self.ts = message_filters.ApproximateTimeSynchronizer([self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)

        self.ball_pub = self.create_publisher(PointStamped, 'tracked_ball', 10)
        self.get_logger().info("双色球体 ROI 跟踪节点已就绪。")

    def camera_info_callback(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.get_logger().info(f"内参加载成功: fx:{self.fx} cx:{self.cx}")
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
        # 修复 DeprecationWarning，使用 .item() 提取标量
        pred_x = int(prediction[0].item())
        pred_y = int(prediction[1].item())

        # --- 2. 划定 ROI 注意力区域 ---
        roi_x_min, roi_y_min = 0, 0
        if self.tracking_state == 'TRACKING':
            roi_x_min = max(0, pred_x - self.roi_window_size // 2)
            roi_y_min = max(0, pred_y - self.roi_window_size // 2)
            roi_x_max = min(img_w, pred_x + self.roi_window_size // 2)
            roi_y_max = min(img_h, pred_y + self.roi_window_size // 2)
            search_image = color_image[roi_y_min:roi_y_max, roi_x_min:roi_x_max]
            cv2.rectangle(color_image, (roi_x_min, roi_y_min), (roi_x_max, roi_y_max), (255, 255, 0), 2)
        else:
            search_image = color_image

        # --- 3. 双色掩膜处理 ---
        hsv_image = cv2.cvtColor(search_image, cv2.COLOR_BGR2HSV)
        mask_o = cv2.inRange(hsv_image, self.hsv_orange_lower, self.hsv_orange_upper)
        mask_b = cv2.inRange(hsv_image, self.hsv_blue_lower, self.hsv_blue_upper)
        mask = cv2.bitwise_or(mask_o, mask_b) # 合并橙蓝颜色

        # 轻度降噪，保持小目标轮廓
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_ball = False
        best_global_x, best_global_y = pred_x, pred_y
        final_state = prediction

        if contours:
            # 寻找 ROI 内最接近预测位置的轮廓
            min_dist = float('inf')
            target_contour = None
            for cnt in contours:
                ((lx, ly), radius) = cv2.minEnclosingCircle(cnt)
                if radius > 2: # 远距离目标半径非常小
                    gx, gy = lx + roi_x_min, ly + roi_y_min
                    dist = np.sqrt((gx - pred_x)**2 + (gy - pred_y)**2)
                    if dist < min_dist:
                        min_dist, target_contour = dist, cnt
                        best_global_x, best_global_y, best_radius = gx, gy, radius

            if target_contour is not None:
                found_ball = True
                # --- 4. 状态重置与校正 (核心修复: 强制 float32) ---
                if self.tracking_state == 'SEARCHING':
                    # 发现目标瞬间，强制重置滤波器状态，消除累积偏移
                    init_state = np.array([[best_global_x], [best_global_y], [0], [0]], dtype=np.float32)
                    self.kf.statePost = init_state
                    self.kf.statePre = init_state
                    self.get_logger().info(f"锁定目标: Px({int(best_global_x)}, {int(best_global_y)})")

                measure = np.array([[np.float32(best_global_x)], [np.float32(best_global_y)]], dtype=np.float32)
                final_state = self.kf.correct(measure)
                self.tracking_state = 'TRACKING'
                self.lost_frames_count = 0

        # --- 5. 丢失逻辑 ---
        if not found_ball:
            self.lost_frames_count += 1
            if self.lost_frames_count > self.max_lost_frames:
                self.tracking_state = 'SEARCHING'

        # --- 6. 发布与绘制 ---
        if self.tracking_state == 'TRACKING' or found_ball:
            cx_pix = max(0, min(img_w - 1, int(final_state[0].item())))
            cy_pix = max(0, min(img_h - 1, int(final_state[1].item())))

            try:
                # 尝试获取深度
                d_val = depth_image[cy_pix, cx_pix]
                if d_val == 0: # 邻域均值滤波防止单像素深度缺失
                    patch = depth_image[max(0, cy_pix-2):cy_pix+3, max(0, cx_pix-2):cx_pix+3]
                    v_d = patch[patch > 0]
                    d_val = np.median(v_d) if len(v_d) > 0 else 0

                if d_val > 0:
                    z = float(d_val) / 1000.0
                    x = (cx_pix - self.cx) * z / self.fx
                    y = (cy_pix - self.cy) * z / self.fy
                    
                    p_msg = PointStamped()
                    p_msg.header = color_msg.header
                    p_msg.point.x, p_msg.point.y, p_msg.point.z = x, y, z
                    self.ball_pub.publish(p_msg)
            except Exception: pass

            # 绘制绿色滤波点与红色视觉点
            cv2.circle(color_image, (cx_pix, cy_pix), 5, (0, 255, 0), -1)
            if found_ball:
                cv2.circle(color_image, (int(best_global_x), int(best_global_y)), int(best_radius), (0, 0, 255), 2)

        cv2.putText(color_image, f"Mode: {self.tracking_state}", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.imshow("Ball Tracker Pro", color_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = BallTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()