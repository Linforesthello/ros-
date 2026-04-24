#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from collections import deque          # ★ 修复1：O(1) 双端队列替代 list
import threading                        # ★ 修复3：显示线程解耦
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

        # --- 参数定义（黄蓝双色球）---
        # 黄色范围
        self.yellow_lower = np.array([20, 100, 100])
        self.yellow_upper = np.array([35, 255, 255])
        # 蓝色范围
        self.blue_lower = np.array([100, 100, 50])
        self.blue_upper = np.array([130, 255, 255])

        # --- 球体物理参数 ---
        self.ball_diameter_m = 0.24          # 球体直径 0.24m
        self.ball_radius_m   = self.ball_diameter_m / 2.0
        self.dist_min_m      = 0.2           # 最小有效距离
        self.dist_max_m      = 7.0           # 最大有效距离
        # 像素半径合理性校验容差（允许估算值的 ±70%）
        # 黄蓝双色球掩码常有缺口，±50% 过窄，先用 0.7 调通后再收紧
        self.radius_tolerance = 0.7

        # ★ 修复2：图像处理缩放比例（降至 50%，处理像素量减少 75%）
        self.img_scale = 0.5

        # --- 工具初始化 ---
        self.bridge = CvBridge()

        # --- 相机内参（存储原始分辨率下的值）---
        self.camera_info_received = False
        self.fx, self.fy, self.cx, self.cy = 0.0, 0.0, 0.0, 0.0

        # ★ 修复1：deque(maxlen=30) 代替 list + pop(0)
        #   - append 超出上限时自动从左侧弹出，O(1) 无内存移位
        #   - 每条记录格式：(timestamp_sec, x_m, y_m, z_m, px, py)
        self.trajectory_points = deque(maxlen=30)

        # ★ 修复3：显示帧缓存 + 互斥锁，供独立显示线程读取
        self._display_image = None
        self._display_lock  = threading.Lock()
        self._display_thread = threading.Thread(
            target=self._display_loop, daemon=True)
        self._display_thread.start()

        # --- ROS 通信 ---
        self.cam_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',
            self.camera_info_callback,
            10)

        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')

        self.ts = message_filters.ApproximateTimeSynchronizer(
            [self.color_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.image_callback)

        # ── 网格密度聚类参数 ─────────────────────────────────
        self.grid_size          = 16   # 格子边长（像素，基于 img_scale=0.5 后分辨率）
        self.show_heatmap       = True # 是否叠加密度热力图（调试用，上线可关）
        self.density_min_pixels = 20   # 峰值格子最低有效像素数，低于此视为无球

        self.ball_pub = self.create_publisher(PointStamped, 'detected_ball', 10)

        self.get_logger().info("球体检测节点已启动，等待相机数据...")

    # ★ 修复3：独立显示线程 — waitKey 阻塞只影响此线程，不占用 ROS 回调线程
    def _display_loop(self):
        """以 ~30fps 刷新显示窗口，与 ROS 回调完全解耦。"""
        cv2.namedWindow("Ball Detection and Trajectory", cv2.WINDOW_NORMAL)
        while True:
            with self._display_lock:
                frame = self._display_image
            if frame is not None:
                cv2.imshow("Ball Detection and Trajectory", frame)
            cv2.waitKey(33)   # ~30fps，阻塞在显示线程，不影响任何回调

    def _detect_by_density(self, mask, grid_size):
        """
        网格密度图聚类，替代 findContours + minEnclosingCircle。

        算法：
          1. 提取掩码前景像素坐标 (x, y)
          2. 用 np.histogram2d 统计各格子内前景像素数量
          3. 密度峰值格子中心 = 球心
          4. 统计密度 ≥ 峰值25% 的格子内总像素数 → 等效半径

        Returns
        -------
        found        : bool    是否找到有效球体
        center_x/y   : int     球心像素坐标（缩放图像坐标系）
        radius       : float   密度等效半径（用于半径合理性验证，对应原 area-radius）
        draw_radius  : float   同 radius（用于绘图，与原 draw_radius 接口一致）
        norm_density : ndarray 归一化密度图 (float32, 0~1)，供热力图渲染
        """
        h, w = mask.shape[:2]
        yx = np.where(mask > 0)

        # 像素数不足时直接返回
        if yx[0].size < self.density_min_pixels:
            empty = np.zeros(
                (h // grid_size + 1, w // grid_size + 1), dtype=np.float32)
            return False, 0, 0, 0.0, 0.0, empty

        y_coords = yx[0].astype(np.float32)
        x_coords = yx[1].astype(np.float32)

        # 构造网格密度图（histogram2d 的 x/y 轴对应图像列/行）
        x_bins = np.arange(0, w + grid_size, grid_size)
        y_bins = np.arange(0, h + grid_size, grid_size)
        hist, x_edges, y_edges = np.histogram2d(
            x_coords, y_coords, bins=[x_bins, y_bins])
        density_map = hist.T            # 转置使 shape 与 (rows, cols) 对齐

        # 密度峰值格子
        peak_flat_idx = np.argmax(density_map)
        peak_row, peak_col = np.unravel_index(peak_flat_idx, density_map.shape)
        peak_val = density_map[peak_row, peak_col]

        if peak_val < self.density_min_pixels:
            return False, 0, 0, 0.0, 0.0, np.zeros_like(density_map, dtype=np.float32)

        # 球心 = 峰值格子的像素中心
        center_x = int((x_edges[peak_col]     + x_edges[peak_col + 1]) / 2.0)
        center_y = int((y_edges[peak_row]     + y_edges[peak_row + 1]) / 2.0)

        # 密度等效半径：统计密度 ≥ 峰值25% 的格子内前景像素总数，再用 √(A/π) 换算
        density_threshold = peak_val * 0.25
        valid_pixels = float(np.sum(density_map[density_map >= density_threshold]))
        radius = float(np.sqrt(valid_pixels / np.pi))
        draw_radius = radius

        # 归一化密度图（0~1），用于热力图渲染
        norm_density = density_map.astype(np.float32)
        max_val = norm_density.max()
        if max_val > 0:
            norm_density /= max_val

        return True, center_x, center_y, radius, draw_radius, norm_density

    def camera_info_callback(self, msg):
        """
        接收并存储相机内参的回调函数。
        """
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True
            self.get_logger().info(
                f"成功接收到相机内参: fx={self.fx}, fy={self.fy}, cx={self.cx}, cy={self.cy}")
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

        # ★ 修复2：分辨率缩放（50% → 处理像素量降低 75%）
        #   彩色图用默认双线性插值；深度图用 INTER_NEAREST 避免插值引入伪深度值
        s = self.img_scale
        color_image = cv2.resize(color_image, (0, 0), fx=s, fy=s)
        depth_image = cv2.resize(depth_image, (0, 0), fx=s, fy=s,
                                 interpolation=cv2.INTER_NEAREST)
        # 内参等比缩放（局部变量，不修改原始内参，避免累积误差）
        fx = self.fx * s
        fy = self.fy * s
        cx = self.cx * s
        cy = self.cy * s

        # 1. 颜色分割：将 BGR 图像转为 HSV，分别提取黄色和蓝色掩码后合并。
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        mask_yellow = cv2.inRange(hsv_image, self.yellow_lower, self.yellow_upper)
        mask_blue   = cv2.inRange(hsv_image, self.blue_lower,   self.blue_upper)
        mask = cv2.bitwise_or(mask_yellow, mask_blue)

        # 2. 形态学处理：腐蚀和膨胀，以消除噪声并巩固目标区域。
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 3. 网格密度图聚类检测（替代 findContours + minEnclosingCircle）
        found, center_x, center_y, radius, draw_radius, norm_density = \
            self._detect_by_density(mask, self.grid_size)

        # 热力图叠加（show_heatmap=True 时，将密度分布以半透明 JET 色图叠加到彩色帧）
        if self.show_heatmap and norm_density.size > 0:
            h_img, w_img = color_image.shape[:2]
            heatmap_u8 = (norm_density * 255).astype(np.uint8)
            heatmap_u8 = cv2.resize(heatmap_u8, (w_img, h_img),
                                    interpolation=cv2.INTER_NEAREST)
            heatmap_color = cv2.applyColorMap(heatmap_u8, cv2.COLORMAP_JET)
            color_image = cv2.addWeighted(color_image, 0.65, heatmap_color, 0.35, 0)

        if found and draw_radius > 5:
            # 十字准星标记球心（密度峰值位置）
            cs = 12
            cv2.line(color_image,
                     (center_x - cs, center_y), (center_x + cs, center_y), (0, 255, 0), 2)
            cv2.line(color_image,
                     (center_x, center_y - cs), (center_x, center_y + cs), (0, 255, 0), 2)

            # 5. 查询深度值：在球心周围取 11×11 邻域，去零后取中位数。
            try:
                h_img, w_img = depth_image.shape[:2]
                r_patch = 5
                y0_p = max(0, center_y - r_patch)
                y1_p = min(h_img, center_y + r_patch + 1)
                x0_p = max(0, center_x - r_patch)
                x1_p = min(w_img, center_x + r_patch + 1)
                patch = depth_image[y0_p:y1_p, x0_p:x1_p].flatten()
                valid = patch[patch > 0]
                if valid.size == 0:
                    self.get_logger().info(
                        f"球心({center_x},{center_y})邻域内无有效深度，"
                        f"邻域大小={patch.size}，跳过本帧。"
                    )
                depth = int(np.median(valid)) if valid.size > 0 else 0
                if depth > 0:
                    # 6. 三维坐标计算（使用缩放后的局部内参）
                    z_meters = float(depth) / 1000.0
                    x_meters = (center_x - cx) * z_meters / fx
                    y_meters = (center_y - cy) * z_meters / fy

                    # ── 距离范围过滤 ──────────────────────────────────────────
                    if not (self.dist_min_m <= z_meters <= self.dist_max_m):
                        self.get_logger().debug(
                            f"距离 {z_meters:.2f}m 超出有效范围 "
                            f"[{self.dist_min_m}, {self.dist_max_m}]m，丢弃。"
                        )

                    else:
                        # ── 像素半径合理性验证（用密度等效半径）──────────────
                        expected_radius_px = fx * self.ball_radius_m / z_meters
                        lo = expected_radius_px * (1.0 - self.radius_tolerance)
                        hi = expected_radius_px * (1.0 + self.radius_tolerance)
                        if not (lo <= radius <= hi):
                            self.get_logger().debug(
                                f"密度等效半径 {radius:.1f}px"
                                f" 不在期望范围 [{lo:.1f}, {hi:.1f}]px"
                                f"（期望={expected_radius_px:.1f}px，距离={z_meters:.2f}m），丢弃。"
                            )
                        else:
                            # 7. 发布坐标
                            point_msg = PointStamped()
                            point_msg.header = color_msg.header
                            point_msg.point.x = x_meters
                            point_msg.point.y = y_meters
                            point_msg.point.z = z_meters
                            self.ball_pub.publish(point_msg)

                            self.get_logger().info(
                                f"检测到目标：3D坐标 = ({x_meters:.2f}, {y_meters:.2f}, {z_meters:.2f})m")

                            # 在图像上绘制当前球的位置标记
                            cv2.circle(color_image, (center_x, center_y), int(draw_radius), (0, 255, 255), 2)
                            cv2.circle(color_image, (center_x, center_y), 5, (0, 0, 255), -1)

                            # --- 保存轨迹点（deque 自动维护 maxlen，O(1)）---
                            timestamp_sec = self.get_clock().now().nanoseconds * 1e-9
                            self.trajectory_points.append(
                                (timestamp_sec, x_meters, y_meters, z_meters, center_x, center_y)
                            )

            except IndexError:
                self.get_logger().warn(
                    f"球心坐标 ({center_x}, {center_y}) 超出深度图像边界。")

        # ★ 修复3：将帧推送给显示线程，回调本身立即返回，不再阻塞
        with self._display_lock:
            self._display_image = color_image


def main(args=None):
    rclpy.init(args=args)
    node = BallDetectorNode()
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
