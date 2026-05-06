# 球体检测节点 — 完整架构与流程文档

## 一、项目概览

本目录包含三个球体检测 ROS2 节点的迭代版本，目标是在 RGB-D 相机画面中检测**黄蓝双色球体**，输出其在相机坐标系下的三维坐标。

| 文件 | 定位 | 状态 |
|------|------|------|
| `gpt_CommandLine.py` | 主力版本（密度聚类 + 先验选择） | 当前使用 |
| `dynamic_ball_tracker_node.py` | V2：轮廓检测 + 动静过滤 | 旧版，表现不理想 |
| `260506_test.py` | V4 实验版：EMA 速度估计 + 丢失预测 + 重力模型 | 测试中 |

---

## 二、系统架构（主力版本 gpt_CommandLine.py）

### 2.1 ROS 节点拓扑

```
  /camera/color/camera_info ──► camera_info_callback ──► 存储 fx,fy,cx,cy
  /camera/color/image_raw   ─┐
                               ├── message_filters.ApproximateTimeSynchronizer (slop=0.1s)
  /camera/depth/image_raw   ─┘      │
                                     ▼
                              image_callback()  ◄── 主处理入口
                                     │
                                     ▼
                              /detected_ball (PointStamped)  ◄── 3D坐标发布
```

- **输入 Topic：**
  - `/camera/color/camera_info` (`CameraInfo`) — 相机内参，接收一次后自动取消订阅
  - `/camera/color/image_raw` (`Image`) — 彩色图像
  - `/camera/depth/image_raw` (`Image`) — 深度图像（单位：mm）

- **输出 Topic：**
  - `/detected_ball` (`geometry_msgs/PointStamped`) — 目标球的相机坐标系 3D 坐标 (x, y, z)，单位：米

- **时间同步：** `ApproximateTimeSynchronizer`，队列深度 10，时间窗口 ±0.1s

### 2.2 节点内部架构

```
BallDetectorNode
├── 显示线程 _display_loop          — 独立线程，~30fps 刷新 imshow
├── 用户输入线程 _wait_user_input    — 独立线程，阻塞 stdin 等待目标选择
├── ROS 回调 image_callback          — 主流水线（见下节）
├── 先验状态机                        — collecting → waiting_input → tracking
├── 轨迹缓存 trajectory_points       — deque(maxlen=30)，按帧记录 3D 坐标
└── 显示缓存 _display_image + Lock   — 回调写入，显示线程读取
```

### 2.3 图像预处理流水线

```
color_msg ──► cv_bridge (BGR8)       depth_msg ──► cv_bridge (passthrough)
     │                                                    │
     ▼                                                    ▼
resize(0.5x, INTER_LINEAR)                    resize(0.5x, INTER_NEAREST)
     │                                                    │
     ▼                                                    │
BGR → HSV                                                (保留mm单位)
     │
     ├──► cv2.inRange(yellow_lower, yellow_upper) → mask_yellow
     │         ├── erode 2× → dilate 2×（独立处理）
     │
     └──► cv2.inRange(blue_lower, blue_upper)   → mask_blue
               ├── erode 2× → dilate 2×（独立处理）
```

**关键设计：** 黄、蓝掩码分别处理形态学操作，保持颜色贡献独立性，不提前合并。

### 2.4 内参处理

```
原始内参 msg.k[0..5]  × img_scale(0.5) → 缩放后内参 (fx, fy, cx, cy)
每次回调内局部变量计算，避免累积误差。
```

---

## 三、检测算法：网格密度聚类 (`_detect_by_density`)

### 3.1 算法流程

```
mask_yellow ──► 提取前景像素坐标 ──► np.histogram2d(grid_size=16) ──► dm_y + n_y
mask_blue   ──► 提取前景像素坐标 ──► np.histogram2d(grid_size=16) ──► dm_b + n_b
                                                                          │
                                                                          ▼
                                              total_pixels < density_min_pixels(10) → 无球
                                                                          │
                                                                          ▼
                                              各自找密度峰值格子中心 (cx_y, cy_y), (cx_b, cy_b)
                                                                          │
                                                                          ▼
                                              以各自像素数 n_y / n_b 加权平均 → 最终球心 (cx, cy)
                                                                          │
                                                                          ▼
                                              合并密度图 threshold=peak×0.25 → 有效像素面积 → 等效半径
```

### 3.2 与轮廓法的对比

| 维度 | 密度聚类 (当前) | 轮廓法 (旧版) |
|------|:---:|:---:|
| 抗掩码碎片 | 强（稀疏像素可聚类） | 弱（缺口导致轮廓断裂） |
| 黄蓝独立贡献 | 像素数加权平均 | 先合并再 findContours，小色域被大色域淹没 |
| 参数敏感性 | 仅 grid_size, density_min_pixels | 轮廓层级、面积阈值、形态学核大小联动 |

---

## 四、先验选择状态机

```
                    ┌──────────────────────────────────────┐
                    │                                      │
                    ▼                                      │
  ┌──────────┐  前N帧采集完  ┌──────────────┐  用户选择   ┌──────────┐
  │collecting│──────────────►│waiting_input │───────────►│ tracking │
  └──────────┘               └──────────────┘             └──────────┘
       │                         │                            │
  _collect_candidates()    打印候选列表                  锁定 target_prior
  每帧用 findContours      等待 stdin 输入                target_color
  累积到 candidates[]                                    双阈值过滤 + EMA
```

### 4.1 collecting 阶段

- 帧数：`prior_frames = 3`（取前 3 帧）
- 每帧调用 `_collect_candidates()`：在两个掩码上分别跑 `findContours`，面积 < 40px² 的过滤
- 矩计算质心，邻域 11×11 中值深度 → 候选列表
- 候选格式：`{px, py, z_m, color, area}`
- 全部追加到 `self.candidates[]`

### 4.2 waiting_input 阶段

- `_aggregate_and_print()` 合并多帧候选：
  - 同色 + 像素距离 < `prior_gate_px(80)` → 同一目标，滚动均值合并
  - 按平均距离从近到远排序
  - 终端打印候选表格（编号从 0 开始）
- 启动独立线程 `_wait_user_input()` 阻塞等待 stdin 输入目标编号
- 选中的候选成为 `target_prior` + `target_color`

### 4.3 tracking 阶段

- 只对 `target_color` 对应颜色的掩码做检测（性能优化选项，当前仍对双色都做密度聚类）
- 密度聚类结果通过**先验双阈值过滤**（见下节）

---

## 五、追踪阶段判断/过滤链

### 5.1 完整检测判断流水线

```
密度聚类检测 (found, center_x, center_y, radius)
  │
  ├─ draw_radius ≤ 5 ────────────────────► 丢弃（无有效密度区域）
  │
  ├─ 深度查询（11×11邻域中值）
  │     ├─ 无有效深度 ──────────────────► 跳过本帧
  │     └─ 有效深度 → z_meters
  │
  ├─ 双阈值门限（先验位置过滤）
  │     │  pixel_dist > prior_gate_px(80) ──► 丢弃
  │     │  depth_diff > 0.5m ───────────────► 丢弃
  │     └─ 通过
  │
  ├─ 距离范围过滤
  │     │  z_meters < 0.2m or > 7.0m ───────► 丢弃
  │     └─ 通过
  │
  ├─ 像素半径合理性验证
  │     │  expected_r = fx × ball_radius(0.12m) / z
  │     │  tolerance = ±70%
  │     │  密度等效半径 outside [lo, hi] ──► 丢弃
  │     └─ 通过
  │
  └─ 全部通过 ──► 发布 PointStamped + 更新轨迹 + EMA 更新先验
```

### 5.2 EMA 更新（阻止先验漂移）

```
alpha = 0.8
new_prior_px = 0.2 × old + 0.8 × current
new_prior_py = 0.2 × old + 0.8 × current
new_prior_z  = 0.2 × old + 0.8 × current
```

### 5.3 关键阈值汇总

| 参数 | 值 | 含义 |
|------|-----|------|
| `yellow_lower` | HSV(20, 100, 100) | 黄色下界 |
| `yellow_upper` | HSV(35, 255, 255) | 黄色上界 |
| `blue_lower` | HSV(100, 50, 50) | 蓝色下界（S 降低到 50 覆盖阴影侧） |
| `blue_upper` | HSV(130, 255, 255) | 蓝色上界 |
| `ball_diameter_m` | 0.24 | 球体直径 (m) |
| `ball_radius_m` | 0.12 | 球体半径 (m) |
| `dist_min_m` | 0.2 | 最小有效距离 (m) |
| `dist_max_m` | 7.0 | 最大有效距离 (m) |
| `radius_tolerance` | 0.7 (±70%) | 半径验证容差 |
| `img_scale` | 0.5 | 图像缩放比例 |
| `grid_size` | 16 | 密度图格子边长 (px) |
| `density_min_pixels` | 10 | 峰值格子最低有效像素数 |
| `prior_frames` | 3 | 先验采集帧数 |
| `prior_gate_px` | 80 | 追踪阶段先验像素距离门限 |
| `depth_gate` | 0.5m | 追踪阶段深度差门限 |

---

## 六、3D 坐标计算

```
x = (center_x - cx) × z / fx   — 相机右 +x
y = (center_y - cy) × z / fy   — 相机下 +y
z = depth_median × 0.001       — 相机前 +z
```

其中 `(cx, cy)` 为缩放后光心，`(fx, fy)` 为缩放后焦距，`z` 由 11×11 邻域深度中值取 mm→m 转换。

---

## 七、迭代版本对比

### 7.1 dynamic_ball_tracker_node.py（旧版）

| 维度 | 描述 |
|------|------|
| 检测算法 | findContours（取最大轮廓） |
| 掩码处理 | 黄蓝先 OR 合并再做形态学 |
| 先验 | 无采集阶段，直接 tracking |
| 过滤 | 深度门限 = max(0.5, z_prior×0.5) 自适应 |
| 发布策略 | 仅发布运动目标（v > 0.2 m/s） |
| EMA α | 0.6 |
| 问题 | 轮廓法对掩码缺口敏感；仅发布动态球，静态球不输出 |

### 7.2 260506_test.py（实验版 V4）

| 维度 | 描述 |
|------|------|
| 检测算法 | findContours（取最大轮廓） |
| 深度质量判定 | 标准差检查：std < max(0.02m, z×0.1) |
| 速度估计 | EMA (α=0.4) |
| 丢失预测 | 恒速外推 + Y 轴重力项 (**9.8m/s²**) |
| 丢失容忍 | max_lost_frames = 10 帧 |
| 发布策略 | 检测到即发 + 丢失预测期间持续发布 |
| 新能力 | 支持短暂遮挡后位置预测 |
| 问题 | 无先验选择，场景多球时无法区分目标 |

---

## 八、输入输出规范

### 输入

| 信源 | 类型 | 频率 | 说明 |
|------|------|------|------|
| `/camera/color/camera_info` | CameraInfo | 单次 | 内参矩阵 K，仅用 k[0~5] |
| `/camera/color/image_raw` | Image (BGR8) | ~30Hz | 彩色帧 |
| `/camera/depth/image_raw` | Image (16UC1) | ~30Hz | 深度帧 (mm) |

### 输出

| Topic | 类型 | 频率 | 说明 |
|------|------|------|------|
| `/detected_ball` | PointStamped | 有效检测时每帧发布 | x=右, y=下, z=前 (m) |

### 可视化窗口

- 窗口名：`"Ball Detection and Trajectory"`
- 热力图叠加（可选 `show_heatmap=True`）：半透明 JET 色图显示密度分布
- 追踪时：绿色十字准星 + 黄色圆环（等效半径）+ 红色实心圆心点
- 采集时：文本提示进度

---

## 九、轨迹记录

`trajectory_points`（deque, maxlen=30）每帧追加一条记录：

```python
(timestamp_sec, x_m, y_m, z_m, pixel_x, pixel_y)
```

当前未做持久化或发布路径，仅内存保留最近 30 帧。
