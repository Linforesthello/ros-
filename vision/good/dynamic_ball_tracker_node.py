#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from collections import deque
import threading
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PointStamped
import message_filters

class BallDetectorNode(Node):
    def __init__(self):
        super().__init__('ball_detector_node')

        # 颜色
        self.yellow_lower = np.array([20, 100, 100])
        self.yellow_upper = np.array([35, 255, 255])
        self.blue_lower   = np.array([100, 50, 50])
        self.blue_upper   = np.array([130, 255, 255])

        # 物理参数
        self.ball_radius_m = 0.12
        self.dist_min_m = 0.2
        self.dist_max_m = 7.0
        self.radius_tolerance = 0.7

        self.img_scale = 0.5

        self.bridge = CvBridge()

        # 相机内参
        self.camera_info_received = False
        self.fx = self.fy = self.cx = self.cy = 0.0

        # 轨迹
        self.trajectory_points = deque(maxlen=30)

        # === 动态检测参数 ===
        self.vel_threshold = 0.2
        self.vel_deadzone  = 0.05
        self.is_dynamic    = False

        # 显示线程
        self._display_image = None
        self._display_lock  = threading.Lock()
        threading.Thread(target=self._display_loop, daemon=True).start()

        # ROS
        self.create_subscription(CameraInfo,
                                 '/camera/color/camera_info',
                                 self.camera_info_callback, 10)

        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')

        self.ts = message_filters.ApproximateTimeSynchronizer(
            [self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)

        self.ball_pub = self.create_publisher(PointStamped, 'detected_ball', 10)

        # 简化：直接 tracking（跳过先验）
        self.prior_state = 'tracking'
        self.target_prior = {'px':0,'py':0,'z_m':0}
        self.prior_gate_px = 120

        self.get_logger().info("节点启动")

    def _display_loop(self):
        cv2.namedWindow("view", cv2.WINDOW_NORMAL)
        while True:
            with self._display_lock:
                frame = self._display_image
            if frame is not None:
                cv2.imshow("view", frame)
            cv2.waitKey(30)

    def camera_info_callback(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True

    def image_callback(self, color_msg, depth_msg):
        if not self.camera_info_received:
            return

        color = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
        depth = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')

        s = self.img_scale
        color = cv2.resize(color, (0,0), fx=s, fy=s)
        depth = cv2.resize(depth, (0,0), fx=s, fy=s, interpolation=cv2.INTER_NEAREST)

        fx, fy = self.fx*s, self.fy*s
        cx, cy = self.cx*s, self.cy*s

        hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
        mask_y = cv2.inRange(hsv, self.yellow_lower, self.yellow_upper)
        mask_b = cv2.inRange(hsv, self.blue_lower, self.blue_upper)

        mask = cv2.bitwise_or(mask_y, mask_b)
        mask = cv2.erode(mask, None, 2)
        mask = cv2.dilate(mask, None, 2)

        cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return

        cnt = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(cnt) < 50:
            return

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            return

        cx_px = int(M["m10"]/M["m00"])
        cy_px = int(M["m01"]/M["m00"])

        patch = depth[cy_px-3:cy_px+4, cx_px-3:cx_px+4].flatten()
        valid = patch[patch>0]
        if valid.size == 0:
            return

        z = np.median(valid)*0.001

        # === 深度门限（自适应）===
        z_prior = self.target_prior['z_m']
        depth_gate = max(0.5, z_prior*0.5)

        dist_px = np.hypot(cx_px-self.target_prior['px'], cy_px-self.target_prior['py'])

        if self.target_prior['z_m'] != 0:
            if dist_px > self.prior_gate_px or abs(z-z_prior) > depth_gate:
                return

        # EMA更新
        alpha = 0.6
        self.target_prior['px'] = (1-alpha)*self.target_prior['px'] + alpha*cx_px
        self.target_prior['py'] = (1-alpha)*self.target_prior['py'] + alpha*cy_px
        self.target_prior['z_m'] = (1-alpha)*z_prior + alpha*z

        x = (cx_px-cx)*z/fx
        y = (cy_px-cy)*z/fy

        timestamp = self.get_clock().now().nanoseconds*1e-9

        self.trajectory_points.append((timestamp,x,y,z,cx_px,cy_px))

        # === 动态检测 ===
        if len(self.trajectory_points) >= 2:
            t0,x0,y0,z0,_,_ = self.trajectory_points[-2]
            dt = timestamp - t0

            if dt > 0:
                v = np.sqrt((x-x0)**2 + (y-y0)**2 + (z-z0)**2)/dt

                if v < self.vel_deadzone:
                    v = 0

                self.is_dynamic = v > self.vel_threshold

        # === 发布（只发动态）===
        if self.is_dynamic:
            msg = PointStamped()
            msg.header = color_msg.header
            msg.point.x = x
            msg.point.y = y
            msg.point.z = z
            self.ball_pub.publish(msg)

        # === 可视化 ===
        cv2.circle(color,(cx_px,cy_px),10,(0,255,255),2)

        txt = "DYNAMIC" if self.is_dynamic else "STATIC"
        col = (0,0,255) if self.is_dynamic else (255,255,255)

        cv2.putText(color, txt, (cx_px+10,cy_px-10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)

        with self._display_lock:
            self._display_image = color


def main():
    rclpy.init()
    node = BallDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()