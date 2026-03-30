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

class BallDetectorNode(Node):
    """
    这个节点用于检测特定颜色的球体，并计算其在相机坐标系下的三维坐标。
    """
    def __init__(self):
        super().__init__('ball_detector_node')

        # --- 参数定义 ---
        self.hsv_lower = np.array([10, 100, 100])  # 定义颜色范围 (橙色球)
        self.hsv_upper = np.array([25, 255, 255])

        # --- 工具初始化 ---
        self.bridge = CvBridge()

        # --- 相机内参 ---
        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        # --- 存储轨迹的历史点 ---
        self.trajectory_points = []

        # --- ROS 通信 ---
        self.cam_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',
            self.camera_info_callback,
            10)

        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')

        self.ts = message_filters.ApproximateTimeSynchronizer([self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)

        self.ball_pub = self.create_publisher(PointStamped, 'detected_ball', 10)

        self.get_logger().info("球体检测节点已启动，等待相机数据...")

    def camera_info_callback(self, msg):
        """
        接收并存储相机内参的回调函数。
        """
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.get_logger().info(f"成功接收到相机内参: fx={self.fx}, fy={self.fy}, cx={self.cx}, cy={self.cy}")
            self.destroy_subscription(self.cam_info_sub)

    def image_callback(self, color_msg, depth_msg):
        """
        处理同步后的彩色和深度图像，执行检测和定位。
        """
        if not self.camera_info_received:
            self.get_logger().warn("尚未接收到相机内参，跳过图像处理。")
            return

        # 将 ROS 图像消息转换为 OpenCV 格式。
        try:
            color_image = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth_image = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"图像转换失败: {e}")
            return

        # 1. 颜色分割：将 BGR 图像转为 HSV，并根据设定的颜色范围创建掩码。
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.hsv_lower, self.hsv_upper)

        # 2. 形态学处理：腐蚀和膨胀，以消除噪声并巩固目标区域。
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 3. 轮廓检测：在掩码中找到所有物体的轮廓。
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 如果有找到轮廓，才进行后续处理
        if contours:
            # 4. 找到最大轮廓，并计算其最小外接圆。
            largest_contour = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)

            # 只处理半径大于一定阈值的轮廓，以过滤掉小的噪声。
            if radius > 10:
                center_x, center_y = int(x), int(y)

                # 5. 查询深度值：从深度图像中获取球心位置的深度。
                try:
                    depth = depth_image[center_y, center_x]
                    # 深度值大于0才有效。
                    if depth > 0:
                        # 6. 三维坐标计算：使用相机内参将2D像素坐标和深度值转换为3D空间坐标。
                        z_meters = float(depth) / 1000.0  # 将毫米转换为米
                        x_meters = (center_x - self.cx) * z_meters / self.fx
                        y_meters = (center_y - self.cy) * z_meters / self.fy

                        # 7. 发布坐标：将计算出的3D坐标封装成 PointStamped 消息并发布。
                        point_msg = PointStamped()
                        point_msg.header = color_msg.header  # 使用与输入图像相同的时间戳和坐标系
                        point_msg.point.x = x_meters
                        point_msg.point.y = y_meters
                        point_msg.point.z = z_meters
                        self.ball_pub.publish(point_msg)

                        # 输出坐标到命令行
                        self.get_logger().info(f"检测到目标：3D坐标 = ({x_meters:.2f}, {y_meters:.2f}, {z_meters:.2f})m")

                        # (可选) 在图像上绘制当前球的位置标记
                        cv2.circle(color_image, (center_x, center_y), int(radius), (0, 255, 255), 2)
                        cv2.circle(color_image, (center_x, center_y), 5, (0, 0, 255), -1)

                        # --- 保存轨迹点 ---
                        self.trajectory_points.append((center_x, center_y, x_meters, y_meters, z_meters))

                except IndexError:
                    self.get_logger().warn(f"球心坐标 ({center_x}, {center_y}) 超出深度图像边界。")

            # 绘制轨迹线，仅在图像中显示最后一个位置的标记
            if len(self.trajectory_points) > 1:
                for i in range(1, len(self.trajectory_points)):
                    prev_point = self.trajectory_points[i - 1]
                    curr_point = self.trajectory_points[i]
                    prev_x, prev_y, prev_z = prev_point[2], prev_point[3], prev_point[4]
                    curr_x, curr_y, curr_z = curr_point[2], curr_point[3], curr_point[4]

                    # 绘制轨迹线
                    cv2.line(color_image, (prev_point[0], prev_point[1]), (curr_point[0], curr_point[1]), (255, 0, 0), 2)

        # (可选) 显示处理后的图像窗口。
        cv2.imshow("Ball Detection and Trajectory", color_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = BallDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("节点被手动终止。")
    finally:
        # 清理资源
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()