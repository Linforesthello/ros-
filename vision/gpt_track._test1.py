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
    这个节点使用卡尔曼滤波器来稳定地跟踪橙色和蓝色球体，
    并计算其在相机坐标系下的三维坐标。
    """
    def __init__(self):
        super().__init__('ball_tracker_node')

        # --- 参数定义 ---
        # 设置橙色和蓝色的HSV范围
        self.hsv_lower_orange = np.array([10, 100, 100])
        self.hsv_upper_orange = np.array([25, 255, 255])
        self.hsv_lower_blue = np.array([100, 100, 100])
        self.hsv_upper_blue = np.array([140, 255, 255])

        # --- 工具初始化 ---
        self.bridge = CvBridge()

        # --- 卡尔曼滤波器初始化 ---
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], np.float32) * 0.003
        self.kf.measurementNoiseCov = np.array([[1,0],[0,1]], np.float32) * 15
        
        self.last_measurement = None
        self.last_prediction = None

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
        prediction = self.kf.predict()
        final_state = prediction  # 假设没有找到球，最终位置就是预测位置

        # --- 2. 计算搜索区域 (ROI) ---
        search_radius = 50  # 初步设置搜索半径
        x_min, x_max = max(0, int(prediction[0]) - search_radius), min(color_image.shape[1], int(prediction[0]) + search_radius)
        y_min, y_max = max(0, int(prediction[1]) - search_radius), min(color_image.shape[0], int(prediction[1]) + search_radius)

        # 3. 只对搜索区域进行目标检测
        roi_image = color_image[y_min:y_max, x_min:x_max]
        hsv_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)

        # 生成橙色和蓝色的掩码
        mask_orange = cv2.inRange(hsv_roi, self.hsv_lower_orange, self.hsv_upper_orange)
        mask_blue = cv2.inRange(hsv_roi, self.hsv_lower_blue, self.hsv_upper_blue)

        # 合并橙色和蓝色的掩码
        mask = cv2.bitwise_or(mask_orange, mask_blue)

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_ball = False
        if contours:
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
                found_ball = True
                ((x, y), radius) = cv2.minEnclosingCircle(best_contour)
                measurement = np.array([[np.float32(x)], [np.float32(y)]])
                final_state = self.kf.correct(measurement)
                self.last_measurement = measurement
        
        # --- 4. 获取最终位置 ---
        center_x, center_y = int(final_state[0]), int(final_state[1])

        # --- 5. 计算并发布三维坐标 ---
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

                # --- 6. 可视化调试 ---
                cv2.circle(color_image, (center_x, center_y), 10, (0, 255, 0), 2)
                cv2.putText(color_image, "Tracked", (center_x + 15, center_y + 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                if found_ball:
                    ((x, y), radius) = cv2.minEnclosingCircle(best_contour)
                    cv2.circle(color_image, (int(x), int(y)), int(radius), (0, 0, 255), 2)

        except IndexError:
            self.get_logger().warn(f"跟踪坐标 ({center_x}, {center_y}) 超出深度图像边界。")

        # --- 7. FPS 计算与显示 ---
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