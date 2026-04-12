# imu_odom_ws 问题排查日志

## 问题
`ros2 run imu_odom_ws imu_odometry_node` 报 `No executable found`

## 根本原因
`setup.py` 中使用 `console_scripts` 的 entry_points，setuptools 会将可执行文件安装到 `install/imu_odom_ws/bin/`，但 `ros2 run` 只在 `install/<pkg>/lib/<pkg>/` 下查找可执行文件，导致找不到。

## 解决方案

1. 创建 `scripts/imu_odometry_node` 脚本文件：
```python
#!/usr/bin/env python3
from imu_odom_ws.imu_odometry_node import main
main()
```

2. 修改 `setup.py`，通过 `data_files` 将脚本安装到 ROS2 期望的路径：
```python
data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('lib/' + package_name, ['scripts/imu_odometry_node']),  # 关键行
],
```

3. 重新构建：
```bash
rm -rf build install log
colcon build
source install/setup.bash
ros2 run imu_odom_ws imu_odometry_node
```

## 注意
这也是 `ros2 pkg create` 官方模板的标准做法，应避免单独依赖 `console_scripts` 来注册 ROS2 节点入口。
