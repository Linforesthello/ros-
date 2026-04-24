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
        # S 下界由 100 → 50：覆盖球体边缘/阴影侧蓝色（S 50~100 区间原先全部丢失）
        self.blue_lower = np.array([100, 50, 50])
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
        self.density_min_pixels = 10   # 峰值格子最低有效像素数；原20在4m处边界（约23px），降至10覆盖HSV波动

        self.ball_pub = self.create_publisher(PointStamped, 'detected_ball', 10)

        # ── 先验选择状态机 ──────────────────────────────────────────
        self.prior_state   = 'collecting'   # 'collecting' → 'waiting_input' → 'tracking'
        self.prior_frames  = 3              # 取前 N 帧做候选检测（多帧提升深度稳定性）
        self.prior_count   = 0              # 已采集帧数
        self.candidates    = []             # [{'px', 'py', 'z_m', 'color', 'area'}, ...]（多帧累积）
        self.prior_menu    = {}             # {编号: 候选}（打印给用户后暂存）
        self.target_prior  = None           # 锁定后的先验：{px, py, z_m, color}
        self.target_color  = None           # 'yellow' | 'blue'（锁定后只检测此颜色）
        self.prior_gate_px = 80             # 追踪阶段先验位置门（缩放后坐标系，像素）

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

    def _detect_by_density(self, mask_yellow, mask_blue, grid_size):
        """
        网格密度图聚类，替代 findContours + minEnclosingCircle。

        黄蓝分别建密度图，以各自像素数为权重加权平均峰值坐标 → 球心。
        解决"黄色掩码像素远多于蓝色时蓝色贡献被压制"的问题。

        算法：
          1. 对 mask_yellow / mask_blue 分别提取前景像素坐标
          2. 各自用 np.histogram2d 构造网格密度图
          3. 各自找到密度峰值格子中心 (cx_Y, cy_Y) / (cx_B, cy_B)
          4. 以各自总像素数为权重加权平均 → 最终球心
          5. 合并密度图用于热力图渲染

        Returns
        -------
        found        : bool    是否找到有效球体
        center_x/y   : int     球心像素坐标（缩放图像坐标系）
        radius       : float   密度等效半径（用于半径合理性验证）
        draw_radius  : float   同 radius（用于绘图）
        norm_density : ndarray 归一化合并密度图 (float32, 0~1)，供热力图渲染
        """
        h, w = mask_yellow.shape[:2]
        x_bins = np.arange(0, w + grid_size, grid_size)
        y_bins = np.arange(0, h + grid_size, grid_size)
        empty  = np.zeros((len(y_bins)-1, len(x_bins)-1), dtype=np.float32)

        def _build_density(mask):
            """对单色掩码建密度图，返回 (density_map, x_edges, y_edges, n_pixels)"""
            yx = np.where(mask > 0)
            n  = yx[0].size
            if n < self.density_min_pixels:
                return np.zeros_like(empty), x_bins, y_bins, 0
            yc = yx[0].astype(np.float32)
            xc = yx[1].astype(np.float32)
            hist, xe, ye = np.histogram2d(xc, yc, bins=[x_bins, y_bins])
            return hist.T.astype(np.float32), xe, ye, n

        dm_y, xe, ye, n_y = _build_density(mask_yellow)
        dm_b, _,  _,  n_b = _build_density(mask_blue)

        total = n_y + n_b
        if total < self.density_min_pixels:
            return False, 0, 0, 0.0, 0.0, empty

        # 合并密度图（用于半径估算和热力图）
        combined = dm_y + dm_b

        # 各自峰值格子中心
        def _peak_center(dm, xe, ye):
            if dm.max() < self.density_min_pixels:
                return None, None
            pr, pc = np.unravel_index(np.argmax(dm), dm.shape)
            cx = int((xe[pc] + xe[pc + 1]) / 2.0)
            cy = int((ye[pr] + ye[pr + 1]) / 2.0)
            return cx, cy

        cx_y, cy_y = _peak_center(dm_y, xe, ye)
        cx_b, cy_b = _peak_center(dm_b, xe, ye)

        # 加权平均球心（只有一种颜色有效时退化为单色结果）
        if cx_y is None and cx_b is None:
            return False, 0, 0, 0.0, 0.0, empty
        elif cx_y is None:
            center_x, center_y = cx_b, cy_b
        elif cx_b is None:
            center_x, center_y = cx_y, cy_y
        else:
            center_x = int((cx_y * n_y + cx_b * n_b) / total)
            center_y = int((cy_y * n_y + cy_b * n_b) / total)

        # 密度等效半径（基于合并密度图）
        peak_val = combined.max()
        density_threshold = peak_val * 0.25
        valid_pixels = float(np.sum(combined[combined >= density_threshold]))
        radius      = float(np.sqrt(valid_pixels / np.pi))
        draw_radius = radius

        # 归一化合并密度图（0~1），用于热力图渲染
        norm_density = combined.copy()
        if peak_val > 0:
            norm_density /= peak_val

        return True, center_x, center_y, radius, draw_radius, norm_density

    # ── 先验阶段：采集单帧所有候选 ─────────────────────────────────
    def _collect_candidates(self, mask_yellow, mask_blue, depth_image, fx, cx, cy, color_image):
        """
        在先验采集阶段（prior_state='collecting'）调用。
        对黄、蓝两色掩码各自检测连通域，以质心矩定位候选球心，
        返回本帧所有候选列表（每帧独立返回，由调用方合并到 self.candidates）。

        返回格式::
            [{'px': int, 'py': int, 'z_m': float, 'color': str, 'area': float}, ...]
        """
        candidates = []
        h_img, w_img = depth_image.shape[:2]

        for color_label, mask in [('yellow', mask_yellow), ('blue', mask_blue)]:
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 40:          # 过滤噪声小块；原80在4m处会误拒单色面积约76px²，降至40保留
                    continue
                M = cv2.moments(cnt)
                if M['m00'] == 0:
                    continue
                px = int(M['m10'] / M['m00'])
                py = int(M['m01'] / M['m00'])

                # 11×11 邻域中位数深度（防单像素无效值）
                r = 5
                patch = depth_image[max(0, py-r):min(h_img, py+r+1),
                                     max(0, px-r):min(w_img, px+r+1)].flatten()
                valid = patch[patch > 0]
                if valid.size == 0:
                    continue
                z_m = int(np.median(valid)) * 0.001

                if not (self.dist_min_m <= z_m <= self.dist_max_m):
                    continue

                candidates.append({'px': px, 'py': py, 'z_m': z_m,
                                    'color': color_label, 'area': area})
        return candidates

    # ── 先验阶段：打印候选列表并启动用户输入线程 ───────────────────
    def _aggregate_and_print(self):
        """
        在 prior_count == prior_frames 时调用，聚合多帧候选并打印供选择。
        合并规则：像素距离 < prior_gate_px 且同色的候选视为同一目标，取均值。
        编号从 0 开始，与 goal2 保持一致。
        """
        GATE = self.prior_gate_px
        merged = []   # list of {'px', 'py', 'z_sum', 'z_cnt', 'color', 'area'}

        for raw in self.candidates:
            placed = False
            for m in merged:
                if m['color'] != raw['color']:
                    continue
                dist = np.hypot(raw['px'] - m['px'], raw['py'] - m['py'])
                if dist < GATE:
                    # 滚动均值合并
                    n = m['z_cnt']
                    m['px']    = (m['px']    * n + raw['px'])    / (n + 1)
                    m['py']    = (m['py']    * n + raw['py'])    / (n + 1)
                    m['z_sum'] += raw['z_m']
                    m['z_cnt'] += 1
                    m['area']   = max(m['area'], raw['area'])
                    placed = True
                    break
            if not placed:
                merged.append({'px': raw['px'], 'py': raw['py'],
                               'z_sum': raw['z_m'], 'z_cnt': 1,
                               'color': raw['color'], 'area': raw['area']})

        if not merged:
            self.get_logger().warn("先验阶段未检测到候选，重新采集…")
            self.candidates  = []
            self.prior_count = 0
            return

        # 按距离从近到远排序
        sorted_cands = sorted(merged, key=lambda c: c['z_sum'] / c['z_cnt'])

        self.prior_menu = {}
        print("\n" + "="*55)
        print("  检测到以下候选球体（请输入编号确认目标）：")
        print(f"  {'编号':>4}  {'颜色':^8}  {'u(px)':>6}  {'v(px)':>6}  {'距离(m)':>8}")
        print("-"*55)
        for idx, cand in enumerate(sorted_cands):   # 从 0 开始编号
            z_avg = cand['z_sum'] / cand['z_cnt']
            print(f"  [{idx:>2}]   {cand['color']:^8}  "
                  f"{int(cand['px']):>6}  {int(cand['py']):>6}  {z_avg:>8.2f}")
            self.prior_menu[idx] = {**cand, 'z_m': z_avg}
        print("="*55)

        self.prior_state = 'waiting_input'
        # 在独立线程中等待输入，不阻塞 ROS 回调
        t = threading.Thread(target=self._wait_user_input, daemon=True)
        t.start()

    def _wait_user_input(self):
        """在独立线程中等待用户从终端输入目标编号（非阻塞 ROS 回调）。"""
        while True:
            try:
                raw = input("  请输入目标编号（回车确认）：").strip()
                idx = int(raw)
                if idx not in self.prior_menu:
                    print(f"  ✗ 编号 {idx} 无效，请重新输入（范围 0~{len(self.prior_menu)-1}）。")
                    continue
            except ValueError:
                print("  ✗ 请输入整数编号。")
                continue

            chosen = self.prior_menu[idx]
            self.target_prior = {
                'px': chosen['px'],
                'py': chosen['py'],
                'z_m': chosen['z_m'],
                'color': chosen['color'],
            }
            self.target_color = chosen['color']
            self.prior_state  = 'tracking'
            print(f"\n  ✓ 已锁定目标 [{idx}]：颜色={chosen['color']}，"
                  f"位置=({int(chosen['px'])}, {int(chosen['py'])})px，"
                  f"距离={chosen['z_m']:.2f}m\n")
            self.get_logger().info(
                f"锁定目标：color={self.target_color}，"
                f"px=({int(chosen['px'])},{int(chosen['py'])})，"
                f"z={chosen['z_m']:.2f}m")
            break

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

        # 1. 颜色分割：将 BGR 图像转为 HSV，分别提取黄色和蓝色掩码。
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        mask_yellow = cv2.inRange(hsv_image, self.yellow_lower, self.yellow_upper)
        mask_blue   = cv2.inRange(hsv_image, self.blue_lower,   self.blue_upper)

        # 2. 形态学处理：对各色掩码分别腐蚀+膨胀，保留颜色贡献的独立性（不提前合并）。
        mask_yellow = cv2.erode(mask_yellow, None, iterations=2)
        mask_yellow = cv2.dilate(mask_yellow, None, iterations=2)
        mask_blue   = cv2.erode(mask_blue,   None, iterations=2)
        mask_blue   = cv2.dilate(mask_blue,  None, iterations=2)

        # 3. 网格密度图聚类检测（替代 findContours + minEnclosingCircle）
        #    传入分离掩码，内部以像素数加权平均黄蓝各自的密度峰值坐标 → 球心
        found, center_x, center_y, radius, draw_radius, norm_density = \
            self._detect_by_density(mask_yellow, mask_blue, self.grid_size)

        # 热力图叠加（show_heatmap=True 时，将密度分布以半透明 JET 色图叠加到彩色帧）
        if self.show_heatmap and norm_density.size > 0:
            h_img, w_img = color_image.shape[:2]
            heatmap_u8 = (norm_density * 255).astype(np.uint8)
            heatmap_u8 = cv2.resize(heatmap_u8, (w_img, h_img),
                                    interpolation=cv2.INTER_NEAREST)
            heatmap_color = cv2.applyColorMap(heatmap_u8, cv2.COLORMAP_JET)
            color_image = cv2.addWeighted(color_image, 0.65, heatmap_color, 0.35, 0)

        # ── 顶层状态机分发 ──────────────────────────────────────────────
        if self.prior_state == 'collecting':
            # 采集候选并累积到 self.candidates（list）
            frame_cands = self._collect_candidates(
                mask_yellow, mask_blue, depth_image, fx, cx, cy, color_image)
            self.candidates.extend(frame_cands)
            self.prior_count += 1

            # 在画面上提示进度
            progress_txt = f"先验采集中 {self.prior_count}/{self.prior_frames} ..."
            cv2.putText(color_image, progress_txt, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

            if self.prior_count >= self.prior_frames:
                self._aggregate_and_print()   # 内部会切换到 waiting_input 并启动线程

        elif self.prior_state == 'waiting_input':
            cv2.putText(color_image, "等待选择目标编号...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        elif self.prior_state == 'tracking':
            # 追踪阶段：直接复用顶部已做的双色密度检测结果（found/center_x/center_y/radius）
            # 黄蓝掩码全部保留：目标球本身就是黄蓝两色，场景干扰由先验位置+深度双门限过滤
            pass  # found/center_x/center_y/radius/draw_radius 已在上方第372行赋值

            if found and draw_radius > 5:
                # ── 先验门限双阈值过滤 ──────────────────────────────
                px_prior = self.target_prior['px']
                py_prior = self.target_prior['py']
                z_prior  = self.target_prior['z_m']

                dist_px = np.hypot(center_x - px_prior, center_y - py_prior)

                # 查询当前深度
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
                        f"球心({center_x},{center_y})邻域内无有效深度，跳过本帧。")
                else:
                    depth = int(np.median(valid))
                    z_meters = depth * 0.001
                    depth_diff = abs(z_meters - z_prior)

                    # 双阈值：像素距离 AND 深度差
                    if dist_px > self.prior_gate_px or depth_diff > 0.5:
                        self.get_logger().debug(
                            f"先验门限拒绝：dist_px={dist_px:.1f}px "
                            f"depth_diff={depth_diff:.2f}m")
                    else:
                        # ── EMA 更新先验（α=0.3）──────────────────
                        alpha = 0.3
                        self.target_prior['px'] = (1 - alpha) * px_prior + alpha * center_x
                        self.target_prior['py'] = (1 - alpha) * py_prior + alpha * center_y
                        self.target_prior['z_m'] = (1 - alpha) * z_prior + alpha * z_meters

                        x_meters = (center_x - cx) * z_meters / fx
                        y_meters = (center_y - cy) * z_meters / fy

                        # 十字准星
                        cs = 12
                        cv2.line(color_image,
                                 (center_x - cs, center_y), (center_x + cs, center_y),
                                 (0, 255, 0), 2)
                        cv2.line(color_image,
                                 (center_x, center_y - cs), (center_x, center_y + cs),
                                 (0, 255, 0), 2)

                        # ── 距离范围过滤 ──────────────────────────────────────────
                        if not (self.dist_min_m <= z_meters <= self.dist_max_m):
                            self.get_logger().debug(
                                f"距离 {z_meters:.2f}m 超出有效范围 "
                                f"[{self.dist_min_m}, {self.dist_max_m}]m，丢弃。")
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
                                # 发布坐标
                                point_msg = PointStamped()
                                point_msg.header = color_msg.header
                                point_msg.point.x = x_meters
                                point_msg.point.y = y_meters
                                point_msg.point.z = z_meters
                                self.ball_pub.publish(point_msg)

                                self.get_logger().info(
                                    f"检测到目标：3D坐标 = "
                                    f"({x_meters:.2f}, {y_meters:.2f}, {z_meters:.2f})m")

                                cv2.circle(color_image,
                                           (center_x, center_y), int(draw_radius),
                                           (0, 255, 255), 2)
                                cv2.circle(color_image,
                                           (center_x, center_y), 5, (0, 0, 255), -1)

                                timestamp_sec = self.get_clock().now().nanoseconds * 1e-9
                                self.trajectory_points.append(
                                    (timestamp_sec, x_meters, y_meters, z_meters,
                                     center_x, center_y)
                                )

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
