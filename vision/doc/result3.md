# result3：中远距离识别优化实现总结

> 对应需求文档：`doc/goal3.md`
> 修改文件：`good/gpt_CommandLine.py`

---

## 一、改动总览

| 位置 | 参数/逻辑 | 修改前 | 修改后 | 解决问题 |
|------|---------|-------|-------|---------|
| `__init__` 第 78 行 | `density_min_pixels` | `20` | `10` | 追踪阶段远距离 peak 值偏低导致丢球 |
| `_collect_candidates` 第 208 行 | `area < N` | `80` | `40` | 4m 处先验采集单色面积约 76px²，原 80 误拒 |
| `image_callback` tracking 分支 | 掩码清零逻辑 | 按 `target_color` 清零另一色掩码 | 移除，始终双色检测 | 球体自身蓝色信息被丢弃 |
| `image_callback` tracking 分支 | 第二次 `_detect_by_density` 调用 | 重新调用（单色掩码） | 移除，复用顶部双色结果 | 冗余计算 |

---

## 二、各改动详细说明

### 2.1 `density_min_pixels`: 20 → 10

**根因**：`_peak_center` 内有过滤：`if dm.max() < self.density_min_pixels: return None, None`。
`dm.max()` 是单个格子内的像素计数，与格子面积正相关。真实场景中 HSV 覆盖率不足（侧面、阴影、运动模糊），有效像素远少于理论值，峰值格子像素数容易跌破 20，导致正常距离（1~2m）也失败。

```python
# 修改前
self.density_min_pixels = 20

# 修改后
self.density_min_pixels = 10   # 实际场景HSV覆盖率不足时峰值像素偏低，10更合理
```

**安全性**：追踪阶段有先验位置（`dist_px < 80px`）+ 深度（`depth_diff < 0.5m`）双门限，低阈值引入的假阳性会被过滤。

---

### 2.2 `area < 80` → `area < 40`（先验采集阶段）

**根因**：定量计算（fx_scaled=300，球半径 0.12m，60% HSV 覆盖率）：

| 距离 | 像素半径 | 单色连通域面积估算 | 原门限结果 |
|------|---------|----------------|---------|
| 2 m  | 18 px   | ~305 px²       | 通过 ✅  |
| 3 m  | 12 px   | ~136 px²       | 通过 ✅  |
| 4 m  |  9 px   |  ~76 px²       | 误拒 ❌  |

4m 处约 76px² < 80px²，先验采集阶段直接检测不到球，用户永远看不到候选。

```python
# 修改前
if area < 80:

# 修改后
if area < 40:   # 4m 处单色面积约76px²，原80误拒，降至40保留
```

**安全性**：先验采集结果经 `_aggregate_and_print` 距离合并去噪后由用户人工确认，假阳性不会进入追踪。

---

### 2.3 追踪阶段移除单色掩码清零（核心修复）

**问题**：修改前 tracking 分支按 `target_color` 清零另一色掩码后重新检测：

```python
# 修改前（错误）
if self.target_color == 'yellow':
    mask_blue = np.zeros_like(mask_blue)   # ← 丢弃球体一半的像素信号
found, ... = self._detect_by_density(mask_yellow, mask_blue, ...)
```

**根因**：这个球是**黄蓝两色**，清零蓝色 = 丢弃一半球体像素。球体转动时蓝面朝前、或蓝色光照更好时，检测完全依赖仅剩的黄色像素，中远距离尤其脆弱。

**为何原设计有此逻辑**：防止场景中其他同色物体干扰。但先验位置门限（`dist_px < 80px`）+ 深度门限（`depth_diff < 0.5m`）已足够排除干扰物，无需牺牲球体本身信号。

**修改后**：

```python
# 修改后
elif self.prior_state == 'tracking':
    # 直接复用顶部已做的双色密度检测结果（found/center_x/center_y/radius）
    # 黄蓝掩码全部保留：球本身就是黄蓝两色，场景干扰由先验位置+深度双门限过滤
    pass  # found/... 已在第 372 行赋值
    if found and draw_radius > 5:
        ...
```

同时消除了原来的**第二次重复检测**（降低CPU占用）。

---

## 三、曾经引入又回滚的改动

### `grid_size`: 16 → 8（已回滚）

**初始判断**：4m 处球直径仅 18px，grid=16 时球只跨 1 格，密度峰值不明显。

**实际效果**：引发近距离和中距离识别全部失效。

**根因**：`dm.max() < density_min_pixels` 是最早的过滤关卡，`dm.max()` 与格子面积成正比：

| grid_size | 格子面积 | 30% HSV 覆盖 1m 处峰值 |
|-----------|---------|----------------------|
| 16 px     | 256 px² | ~96 px ≫ 10 ✅        |
| 8 px      | 64 px²  | ~24 px（正常时）      |
| 8 px      | 64 px²  | ~8 px（HSV稍差）< 10 ❌ |

格子缩小 4 倍 → 峰值像素缩小 4 倍 → HSV 覆盖率稍有波动即跌破 `density_min_pixels`，在最早一关就返回 `found=False`。**已回滚至 16。**

---

## 四、当前有效参数

| 参数 | 值 | 说明 |
|------|----|------|
| `grid_size` | `16` | 格子边长，4m 处球跨 1 格但峰值仍够；8 会在 HSV 差时打断近距离检测 |
| `density_min_pixels` | `10` | 原 20 在真实场景峰值不足，10 更鲁棒 |
| `area < N`（先验采集）| `40` | 原 80 在 4m 处误拒单色连通域 |
| 掩码清零 | **移除** | 双色全保留，信号更强，干扰由先验门限过滤 |

---

## 五、状态机与数据流（改动后）

```
image_callback
  │
  ├─ 图像解码 → 缩放 → HSV → mask_yellow / mask_blue → 形态学处理
  │
  ├─ _detect_by_density(mask_yellow, mask_blue)  ← 双色，只调用一次
  │     └─ found / center_x / center_y / radius / norm_density
  │
  ├─ 热力图叠加（双色密度图）
  │
  └─ 状态分发
       ├── collecting  → _collect_candidates(area≥40) → candidates.extend
       ├── waiting_input → 等待终端输入
       └── tracking    → 直接用上方 found/center/radius
                           → 先验门限（dist_px + depth_diff）
                           → EMA 更新先验
                           → 发布坐标
```
