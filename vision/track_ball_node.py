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
    这个节点使用卡尔曼滤波器来稳定地跟踪特定颜色的球体，
    并计算其在相机坐标系下的三维坐标。
    """
    def __init__(self):
        super().__init__('ball_tracker_node')

        # --- 参数定义 ---
        self.hsv_lower = np.array([10, 100, 100])
        self.hsv_upper = np.array([25, 255, 255])

        # --- 工具初始化 ---
        self.bridge = CvBridge()

        # --- 卡尔曼滤波器初始化 ---
        # 状态向量 [x, y, vx, vy] - (x,y)是像素坐标, (vx,vy)是像素速度
        # 测量向量 [x, y] - 我们只能从图像中直接测量位置
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        # 过程噪声协方差 (Q): 进一步降低，让轨迹更平滑
        self.kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], np.float32) * 0.003
        
        # 测量噪声协方差 (R): 大幅增加，让滤波器更能抵抗测量抖动
        self.kf.measurementNoiseCov = np.array([[1,0],[0,1]], np.float32) * 15
        
        self.last_measurement = None
        self.last_prediction = None

        # --- ROI (感兴趣区域) --- 
        self.roi = None
        self.lost_count = 0

        # --- FPS 监视器 --- 
        self.frame_count = 0
        self.start_time = time.time()

        # --- 相机内参 ---
        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        # --- ROS 通信 ---
        self.cam_info_sub = self.create_subscription(
            CameraInfo, '/camera/color/camera_info', self.camera_info_callback, 10)
        
        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')

        self.ts = message_filters.ApproximateTimeSynchronizer(
            [self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)

        self.ball_pub = self.create_publisher(PointStamped, 'tracked_ball', 10)

        self.get_logger().info("球体跟踪节点已启动，等待相机数据...")

    def camera_info_callback(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.get_logger().info(f"成功接收到相机内参: fx={self.fx}, fy={self.fy}, cx={self.cx}, cy={self.cy}")
            self.destroy_subscription(self.cam_info_sub)

    def image_callback(self, color_msg, depth_msg):
        if not self.camera_info_received:
            self.get_logger().warn("尚未接收到相机内参，跳过图像处理。")
            return

        try:
            color_image = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth_image = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        except Exception as e:
            self.get_logger().error(f"图像转换失败: {e}")
            return

        # --- 1. 卡尔曼预测 ---
        # 在进行任何视觉检测前，先让卡尔曼滤波器预测一下球当前应该在哪里。
        prediction = self.kf.predict()
        final_state = prediction  # 首先，假设我们没有找到球，最终位置就是预测位置

        # --- 2. 视觉检测 (在ROI内) ---
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

        # 创建一个掩码，如果定义了ROI，则只关注ROI区域
        mask = np.zeros(hsv_image.shape[:2], dtype="uint8")
        if self.roi is not None:
            x, y, w, h = self.roi
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
            hsv_image = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)

        color_mask = cv2.inRange(hsv_image, self.hsv_lower, self.hsv_upper)
        color_mask = cv2.erode(color_mask, None, iterations=2)
        color_mask = cv2.dilate(color_mask, None, iterations=2)
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_ball = False
        if contours:
            # --- 3. 结合预测与检测 ---
            # 不再是简单找最大轮廓，而是找离“预测位置”最近的轮廓。
            min_dist = float('inf')
            best_contour = None
            for contour in contours:
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                if radius > 10:
                    dist = np.sqrt((x - prediction[0])**2 + (y - prediction[1])**2)
                    if dist < min_dist:
                        min_dist = dist
                        best_contour = contour
            
            if best_contour is not None:
                # 找到了一个符合预测的球
                found_ball = True
                ((x, y), radius) = cv2.minEnclosingCircle(best_contour)
                measurement = np.array([[np.float32(x)], [np.float32(y)]])
                
                # --- 4. 卡尔曼校正 ---
                # 用本次的测量值来“校正”卡尔曼滤波器的内部状态。
                # correct() 方法会返回校正后的状态，我们用它来更新 final_state
                final_state = self.kf.correct(measurement)
                self.last_measurement = measurement

                # --- 更新ROI ---
                self.lost_count = 0
                roi_size = int(radius * 3) # ROI大小设为球半径的3倍
                min_roi_size = 50 # 最小ROI尺寸，防止目标太小时窗口过小
                if roi_size < min_roi_size:
                    roi_size = min_roi_size
                self.roi = (int(x - roi_size/2), int(y - roi_size/2), roi_size, roi_size)

            else: # 如果在ROI内没找到
                self.lost_count += 1
                if self.lost_count > 15: # 如果连续15帧丢失目标，则重置ROI进行全局搜索
                    self.roi = None
                    self.lost_count = 0
                    self.get_logger().info("目标丢失，重置ROI进行全局搜索...")
        else: # 如果全局搜索没找到
            if self.roi is not None: # 如果之前有ROI，说明是丢失了
                self.lost_count += 1
                if self.lost_count > 15:
                    self.roi = None
                    self.lost_count = 0
                    self.get_logger().info("目标丢失，重置ROI进行全局搜索...")
        
        # --- 5. 获取最终位置 (无论是否检测到) ---
        # final_state 变量现在包含了最优估计 (如果检测到，就是校正后的；如果没检测到，就是预测的)。
        center_x, center_y = int(final_state[0]), int(final_state[1])

        # --- 6. 计算、发布并可视化三维坐标 ---
        depth_text = "Depth: N/A"
        try:
            depth = depth_image[center_y, center_x]
            if depth > 0:
                z_meters = float(depth) / 1000.0
                x_meters = (center_x - self.cx) * z_meters / self.fx
                y_meters = (center_y - self.cy) * z_meters / self.fy

                point_msg = PointStamped()
                point_msg.header = color_msg.header
                point_msg.point.x, point_msg.point.y, point_msg.point.z = x_meters, y_meters, z_meters
                self.ball_pub.publish(point_msg)
                
                depth_text = f"Depth: {z_meters:.2f}m" # 更新深度文本

        except IndexError:
            self.get_logger().warn(f"跟踪坐标 ({center_x}, {center_y}) 超出深度图像边界。")

        # --- 7. 可视化调试 ---
        # 绘制ROI区域
        if self.roi is not None:
            x, y, w, h = self.roi
            cv2.rectangle(color_image, (x, y), (x+w, y+h), (255, 0, 0), 2) # 蓝色ROI框

        # 绘制最终的跟踪位置
        cv2.circle(color_image, (center_x, center_y), 10, (0, 255, 0), 2) # 绿色跟踪点
        cv2.putText(color_image, "Tracked", (center_x + 15, center_y + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 绘制深度信息
        cv2.putText(color_image, depth_text, (center_x + 15, center_y + 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 如果视觉也检测到了，用不同颜色绘制出来以作对比
        if found_ball:
            ((x, y), radius) = cv2.minEnclosingCircle(best_contour)
            cv2.circle(color_image, (int(x), int(y)), int(radius), (0, 0, 255), 2) # 红色检测圆

        # --- FPS 计算与显示 ---
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 2.0: # 每2秒更新一次FPS
            fps = self.frame_count / elapsed_time
            self.get_logger().info(f"图像处理帧率 (FPS): {fps:.2f}")
            self.frame_count = 0
            self.start_time = time.time()

        cv2.imshow("Ball Tracking", color_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = BallTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("节点被手动终止。")
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()