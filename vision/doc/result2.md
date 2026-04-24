# result2：先验目标选择实现总结

> 对应需求文档：`doc/goal2.md`
> 修改文件：`good/gpt_CommandLine.py`

---

## 一、改动总览

| 位置 | 改动类型 | 说明 |
|------|---------|------|
| `__init__` | 修改 | `self.candidates` 类型 `{}` → `[]` |
| `_collect_candidates` | 重写 | 质心矩定位、area 阈值 80、返回 list |
| `_aggregate_and_print` | 重写 | 像素距离合并、编号从 0、线程启动方式 |
| `_wait_user_input` | 简化 | 自身即线程函数，移除内嵌闭包 |
| `image_callback` | 重构 | 新增三路状态分发 + 先验门限 + EMA 更新 |

---

## 二、各部分详细说明

### 2.1 `self.candidates` 初始化

```python
# 修改前
self.candidates = {}   # dict，以网格 key 去重

# 修改后
self.candidates = []   # list，多帧 append/extend 累积
```

`_collect_candidates` 现在每帧返回一个 list，由 `image_callback` 用 `.extend()` 追加，
`_aggregate_and_print` 遍历该 list 做像素距离合并，数据结构更直观。

---

### 2.2 `_collect_candidates` 重写

**签名变化**

```python
# 修改前
def _collect_candidates(self, mask_yellow, mask_blue, depth_image, fx, cx, cy, fy)

# 修改后
def _collect_candidates(self, mask_yellow, mask_blue, depth_image, fx, cx, cy, color_image)
```

**核心变化**

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| 球心定位 | `cv2.minEnclosingCircle` | `cv2.moments` 质心矩（更稳定）|
| 面积阈值 | 50 px² | **80 px²**（缩放后坐标系合理下限）|
| 返回方式 | 直接写 `self.candidates` dict | **返回 list**，由调用方累积 |
| 深度查询 | 5×5 邻域中位数 | 保持 11×11（r=5）邻域中位数 |

---

### 2.3 `_aggregate_and_print` 重写

**合并逻辑**

原来以网格坐标 `(px//GATE, py//GATE)` 做 dict key 去重；  
现在改为：遍历候选列表，**像素距离 < `prior_gate_px`（80px）且同色** 才合并，用滚动均值更新坐标和深度。

**编号规则**

```python
# 修改前：从 1 开始
for idx, cand in enumerate(sorted_cands, start=1):

# 修改后：从 0 开始（与 goal2 一致）
for idx, cand in enumerate(sorted_cands):
```

**线程启动**

```python
# 修改前：在 _wait_user_input 内部再起线程
self._wait_user_input()   # 该函数内 Thread(target=_input_thread).start()

# 修改后：直接以 _wait_user_input 本身为线程目标
t = threading.Thread(target=self._wait_user_input, daemon=True)
t.start()
```

---

### 2.4 `_wait_user_input` 简化

移除了内嵌的 `_input_thread` 闭包，函数自身即为线程目标函数，逻辑不变，层级更清晰。

---

### 2.5 `image_callback` 状态分发（核心新增）

在掩码生成和热力图叠加之后，原先直接进入 `if found and draw_radius > 5` 的检测逻辑
现改为三路状态分发：

```
prior_state
 ├── 'collecting'     → 采集候选帧，显示进度，帧数够后调用 _aggregate_and_print
 ├── 'waiting_input'  → 画面提示等待输入，不执行任何检测
 └── 'tracking'       → 先验过滤 → 检测 → 门限判断 → EMA 更新 → 发布
```

#### collecting 分支

```python
frame_cands = self._collect_candidates(...)
self.candidates.extend(frame_cands)
self.prior_count += 1
cv2.putText(..., f"先验采集中 {self.prior_count}/{self.prior_frames} ...", ...)
if self.prior_count >= self.prior_frames:
    self._aggregate_and_print()
```

#### waiting_input 分支

```python
cv2.putText(..., "等待选择目标编号...", ...)
```

#### tracking 分支

1. **颜色掩码过滤**：按 `target_color` 将另一色掩码置零，抑制同场景其他颜色干扰

    ```python
    if self.target_color == 'yellow':
        mask_blue = np.zeros_like(mask_blue)
    elif self.target_color == 'blue':
        mask_yellow = np.zeros_like(mask_yellow)
    ```

2. **先验门限双阈值拒绝**

    ```python
    dist_px    = hypot(center_x - px_prior, center_y - py_prior)
    depth_diff = abs(z_meters - z_prior)

    if dist_px > prior_gate_px or depth_diff > 0.5:
        # 丢弃（debug 日志）
    ```

3. **EMA 滚动更新先验**（α = 0.3）

    ```python
    alpha = 0.3
    target_prior['px'] = (1-α)*px_prior + α*center_x
    target_prior['py'] = (1-α)*py_prior + α*center_y
    target_prior['z_m'] = (1-α)*z_prior + α*z_meters
    ```

4. 通过后执行距离范围过滤 → 像素半径合理性验证 → 发布 `PointStamped` → 追加轨迹点（与原有逻辑相同）

---

## 三、状态机完整流程

```
节点启动
  │
  ▼  prior_state = 'collecting'
每帧：_collect_candidates → candidates.extend()
prior_count 累计到 prior_frames(3)
  │
  ▼  _aggregate_and_print()
打印候选列表（编号从 0，按距离排序）
prior_state → 'waiting_input'，启动输入线程
  │
  ▼  _wait_user_input()（独立线程）
用户输入编号 → 验证 → 写入 target_prior / target_color
prior_state → 'tracking'
  │
  ▼  tracking 分支（每帧）
颜色掩码过滤 → 密度检测 → 先验门限（dist_px + depth_diff）
→ EMA 更新先验 → 半径验证 → 发布坐标
```

---

## 四、关键参数

| 参数 | 值 | 说明 |
|------|----|------|
| `prior_frames` | 3 | 先验采集帧数 |
| `prior_gate_px` | 80 px | 追踪阶段位置门限（缩放后坐标系）|
| `depth_diff` 阈值 | 0.5 m | 追踪阶段深度差门限 |
| EMA α | 0.3 | 先验位置滚动更新速率 |
| `density_min_pixels` | 20 | 密度图有效峰值最低像素数 |
| `area` 阈值 | 80 px² | 候选连通域最小面积（缩放后）|
