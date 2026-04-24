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
    引入动态 ROI (感兴趣区域) 注意力机制的球体跟踪节点。
    针对 4-5m 远距离小目标进行了形态学和阈值的专门优化。
    """
    def __init__(self):
        super().__init__('ball_tracker_node')

        # --- 参数定义 ---
        self.hsv_lower = np.array([10, 100, 100])
        self.hsv_upper = np.array([25, 255, 255])
        
        # [新增] ROI 注意力机制参数
        self.tracking_state = 'SEARCHING' # 状态: 'SEARCHING' (全图搜索) 或 'TRACKING' (ROI跟踪)
        self.roi_window_size = 100        # ROI 搜索窗口的边长 (像素)
        self.lost_frames_count = 0        # 丢失目标的帧数计数器
        self.max_lost_frames = 15         # 丢失超过多少帧后，放弃 ROI 回到全图搜索

        # --- 工具初始化 ---
        self.bridge = CvBridge()

        # --- 卡尔曼滤波器初始化 ---
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], np.float32) * 0.003
        self.kf.measurementNoiseCov = np.array([[1,0],[0,1]], np.float32) * 15
        
        self.last_measurement = None

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

        self.get_logger().info("球体跟踪节点已启动 (带注意力ROI机制)，等待相机数据...")

    def camera_info_callback(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.get_logger().info(f"成功接收到相机内参: fx={self.fx}, fy={self.fy}, cx={self.cx}, cy={self.cy}")
            self.destroy_subscription(self.cam_info_sub)

    def image_callback(self, color_msg, depth_msg):
        if not self.camera_info_received:
            return

        try:
            color_image = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth_image = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        except Exception as e:
            self.get_logger().error(f"图像转换失败: {e}")
            return

        img_h, img_w = color_image.shape[:2]

        # --- 1. 卡尔曼预测 ---
        prediction = self.kf.predict()
        pred_x, pred_y = int(prediction[0]), int(prediction[1])
        final_state = prediction

        # --- 2. 划定注意力区域 (ROI) ---
        roi_x_min, roi_y_min = 0, 0
        
        if self.tracking_state == 'TRACKING':
            # 限制 ROI 边界，防止越界
            roi_x_min = max(0, pred_x - self.roi_window_size // 2)
            roi_y_min = max(0, pred_y - self.roi_window_size // 2)
            roi_x_max = min(img_w, pred_x + self.roi_window_size // 2)
            roi_y_max = min(img_h, pred_y + self.roi_window_size // 2)
            
            # 裁剪图像
            search_image = color_image[roi_y_min:roi_y_max, roi_x_min:roi_x_max]
            
            # 绘制 ROI 框以供调试
            cv2.rectangle(color_image, (roi_x_min, roi_y_min), (roi_x_max, roi_y_max), (255, 255, 0), 2)
            cv2.putText(color_image, "ROI Search", (roi_x_min, max(10, roi_y_min - 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        else:
            search_image = color_image

        # --- 3. 视觉检测 (仅在 Search Image 中进行) ---
        hsv_image = cv2.cvtColor(search_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.hsv_lower, self.hsv_upper)
        
        # [关键修改] 远距离小目标不能过度腐蚀！改用轻微的开运算去噪，闭运算填补空洞
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_ball = False
        if contours:
            min_dist = float('inf')
            best_contour = None
            
            for contour in contours:
                ((local_x, local_y), radius) = cv2.minEnclosingCircle(contour)
                # [关键修改] 降低最小半径限制，5米外球可能只有 3-5 像素
                if radius > 3:  
                    # 将局部坐标转换为全局坐标
                    global_x = local_x + roi_x_min
                    global_y = local_y + roi_y_min
                    
                    dist = np.sqrt((global_x - pred_x)**2 + (global_y - pred_y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        best_contour = contour
                        best_global_x = global_x
                        best_global_y = global_y
                        best_radius = radius
            
            if best_contour is not None:
                found_ball = True
                measurement = np.array([[np.float32(best_global_x)], [np.float32(best_global_y)]])
                
                # --- 4. 状态机与卡尔曼校正 ---
                final_state = self.kf.correct(measurement)
                
                # 打印像素位置信息 (满足你的需求)
                self.get_logger().info(f"锁定目标! 像素坐标: X={int(best_global_x)}, Y={int(best_global_y)}, R={int(best_radius)}")
                
                self.tracking_state = 'TRACKING'
                self.lost_frames_count = 0

        # --- 处理丢失逻辑 ---
        if not found_ball:
            self.lost_frames_count += 1
            if self.lost_frames_count > self.max_lost_frames:
                if self.tracking_state == 'TRACKING':
                    self.get_logger().warn("丢失目标过久，切换为全图广域搜索！")
                self.tracking_state = 'SEARCHING'

        # --- 5. 获取最终位置 ---
        center_x = max(0, min(img_w - 1, int(final_state[0])))
        center_y = max(0, min(img_h - 1, int(final_state[1])))

        # --- 6. 计算三维坐标并发布 ---
        try:
            depth = depth_image[center_y, center_x]
            # [新增] 如果中心点没有深度，在周围找一个有效的深度值 (防止噪点导致深度为0)
            if depth == 0:
                region = depth_image[max(0, center_y-2):min(img_h, center_y+3), 
                                     max(0, center_x-2):min(img_w, center_x+3)]
                valid_depths = region[region > 0]
                if len(valid_depths) > 0:
                    depth = np.median(valid_depths)

            if depth > 0:
                z_meters = float(depth) / 1000.0
                x_meters = (center_x - self.cx) * z_meters / self.fx
                y_meters = (center_y - self.cy) * z_meters / self.fy

                point_msg = PointStamped()
                point_msg.header = color_msg.header
                point_msg.point.x, point_msg.point.y, point_msg.point.z = x_meters, y_meters, z_meters
                self.ball_pub.publish(point_msg)

        except IndexError:
            pass # 已在前面限制了越界，这里通常不会触发

        # --- 7. 可视化调试 ---
        color = (0, 255, 0) if self.tracking_state == 'TRACKING' else (0, 165, 255)
        cv2.circle(color_image, (center_x, center_y), 5, color, -1)
        cv2.putText(color_image, f"State: {self.tracking_state}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if found_ball:
             cv2.circle(color_image, (int(best_global_x), int(best_global_y)), int(best_radius), (0, 0, 255), 2)

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