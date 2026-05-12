# 完整工作区跨架构 Git 同步方案

## 现状分析

当前工作区是一个**单 Git 仓库**，包含 3 个 ROS2 工作区 + 独立工具代码。树莓派（aarch64）与开发机（x86_64）共用同一仓库，通过 `git push/pull` 同步。

## 逐项分析：哪些应同步，哪些不应

### ✅ 必须同步

| 目录/文件 | 说明 |
|-----------|------|
| `6_Mpu6050t1_ws/src/` | ROS2 包源码，跨架构通用 |
| `6_Mpu6050t1_ws/doc/` | 项目文档 |
| `imu_odom_ws/src/`、`scripts/`、`setup.py` | ROS2 包源码，跨架构通用 |
| `unitree_goM80106/CMakeLists.txt` | **编译入口**，已内置架构检测 |
| `unitree_goM80106/src/*.cpp` | C++ 源码，跨架构通用 |
| `unitree_goM80106/include/` | 头文件，跨架构通用 |
| `unitree_goM80106/lib/*.so` | 链接库（同时包含 arm64 和 x64） |
| `command/can_command.py` | CAN 通信工具 |
| `control/*.py` | 电机控制脚本（含停车逻辑） |
| `vision/` | 视觉代码 |
| `frames/*.gv` | GraphViz 源文件 |
| 文档类 `.md` | 项目/烧录/操作记录 |

### ❌ 禁止同步

| 目录/文件 | 原因 | 当前状态 |
|-----------|------|----------|
| `unitree_goM80106/build/` | CMake 构建产物，架构绑定 | ❌ 被追踪（75文件） |
| 各 ws 的 `build/`、`install/`、`log/` | colcon 构建产物 | 未追踪 ✅ |

### ⚠️ 机器本地状态（不建议同步）

| 文件 | 原因 |
|------|------|
| `command/.can_counter.json` | 运行时计数器 |
| `.vscode/browse.vc.db*` | VSCode IntelliSense 数据库（1.1GB） |
| `.marscode/deviceInfo.json` | IDE 设备配置 |

---

## 树莓派端侧目录规划：ros2_ws + Docker 共享

树莓派上存在一个 Docker 共享目录 `ros2_ws/`，不能改名。
**直接将仓库克隆到 `ros2_ws/` 下即可，完全兼容。**

### 目录结构（树莓派侧）

```
~/ros2_ws/                          ← Docker 共享目录（不改名）
├── .git/                           ← 仓库元数据
├── .gitignore
├── 6_Mpu6050t1_ws/                 ← 实际的 ROS2 工作区（colcon 构建在此目录内）
│   ├── src/
│   ├── build/   (被忽略)
│   ├── install/ (被忽略)
│   └── log/     (被忽略)
├── imu_odom_ws/                    ← 另一个 ROS2 工作区
│   ├── src/
│   ├── build/   (被忽略)
│   ├── install/ (被忽略)
│   └── log/     (被忽略)
├── unitree_goM80106/               ← C++ 项目
│   ├── CMakeLists.txt
│   ├── src/
│   ├── include/
│   ├── lib/
│   └── build/   (被忽略)
├── command/
├── control/
├── vision/
└── ...
```

### 为什么可以这样做

`ros2_ws/` 是**仓库的父目录名**，与 Git 仓库内容无关。Git 只管理仓库内部的文件，不管仓库被 clone 到哪个路径。

克隆后的 ROS2 工作区路径变为 `~/ros2_ws/6_Mpu6050t1_ws/`，目录层级多了一层，但这不影响：
- `colcon build` 在包目录内执行
- Docker 容器通过 volume 挂载 `ros2_ws/` 即可访问所有子目录

### 树莓派上初始化

```bash
# 在树莓派上
cd ~
git clone git@<remote>:<repo>.git ros2_ws

# 进入某个 ROS2 工作区构建
cd ~/ros2_ws/6_Mpu6050t1_ws
colcon build

# Docker 内（假设挂载 ~/ros2_ws → /ros2_ws）
docker exec -it <container> bash
cd /ros2_ws/6_Mpu6050t1_ws
source install/setup.bash
ros2 run <pkg> <node>
```

### 开发机目录不变

```
~/Lin_workspace/                    ← 开发机保持原名
├── .git/
├── 6_Mpu6050t1_ws/
├── imu_odom_ws/
├── unitree_goM80106/
└── ...
```

跨机器的目录名不同（`Lin_workspace` vs `ros2_ws`），完全无关紧要。

---

## 完整 .gitignore

```gitignore
# ========== Python ==========
__pycache__/
*.py[cod]
*.egg-info/

# ========== 构建产物（架构相关，禁止同步） ==========
build/
install/
log/
devel/

# ========== 编译中间文件 ==========
*.o
*.a
# 保留跨架构共享库
!unitree_goM80106/lib/*.so

# ========== IDE / 编辑器 ==========
.idea/
.vscode/
# 保留可共享的 VSCode 配置
!/.vscode/settings.json
!/.vscode/c_cpp_properties.json
!/.vscode/launch.json
!/.vscode/tasks.json
.marscode/

# ========== 运行时状态 ==========
.can_counter.json

# ========== 生成产物（可选） ==========
*.pdf
```

---

## 执行步骤

### 第 1 步：修复已追踪的构建产物（开发机执行）

```bash
# 移除 build/ 的 Git 追踪（不删磁盘文件）
git rm -r --cached unitree_goM80106/build/

# 移除运行时状态
git rm --cached command/.can_counter.json
git rm --cached .marscode/deviceInfo.json
```

### 第 2 步：更新 .gitignore

将上述完整 .gitignore 写入。

### 第 3 步：提交并推送（开发机）

```bash
git add .gitignore
git commit -m "gitignore: 移除构建产物追踪，支持跨架构 Git 同步"
git push
```

### 第 4 步：树莓派拉取

```bash
cd ~/ros2_ws
git pull

# 清理之前可能被拉下来的 x86 构建产物
rm -rf unitree_goM80106/build
cd unitree_goM80106 && mkdir build && cd build && cmake .. && make
```
