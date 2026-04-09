第一次反馈
[WARN] [1775706275.389059159] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.402710720] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.424103616] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.438206679] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.458585186] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.473653162] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.488404442] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.507835389] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.527919054] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
[WARN] [1775706275.538775677] [imu_node]: Could not convert serial data to float: "Quat(x100): w:99 x:0 y:0 z:3 | Att(deg*10): P:0 R:0 Y:37"
^Clin@lin-virtual-machine:~$ 


# 26040902
lin@lin-virtual-machine:~$ ros2 run imu_serial imu_node
[INFO] [1775706902.200027172] [imu_node]: Trying to connect to serial port: /dev/ttyACM0 at baud rate: 115200
[INFO] [1775706902.201281963] [imu_node]: Successfully connected to serial port.
[WARN] [1775706902.256133501] [imu_node]: Could not convert serial data to int: ",0,3,0,0,42"

# 26040903
^Clin@lin-virtual-machine:~$ ros2 run imu_serial imu_node
[INFO] [1775706976.377054170] [imu_node]: Trying to connect to serial port: /dev/ttyACM0 at baud rate: 115200
[INFO] [1775706976.379072628] [imu_node]: Successfully connected to serial port.
[WARN] [1775706976.454129398] [imu_node]: Received data packet with length 1. Expected 7.
^Clin@lin-virtual-machine:~$ 

# 26040904
lin@lin-virtual-machine:~$ ros2 run imu_serial imu_node
[INFO] [1775707074.143646858] [imu_node]: Trying to connect to serial port: /dev/ttyACM0 at baud rate: 115200
[INFO] [1775707074.144761710] [imu_node]: Successfully connected to serial port.
[INFO] [1775707074.145011157] [imu_node]: Warming up serial port, discarding initial data...
[INFO] [1775707074.152139455] [imu_node]: Warm-up complete. Starting to read data.

---
header:
  stamp:
    sec: 1775707101
    nanosec: 406356919
  frame_id: imu_link
orientation:
  x: 0.0
  y: 0.0
  z: -0.05
  w: 0.99
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
^Clin@lin-virtual-machine:~$ 

# 26040905
lin@lin-virtual-machine:~$ ros2 topic list 
/clicked_point
/goal_pose
/imu/data
/initialpose
/parameter_events
/rosout
/tf
/tf_static
lin@lin-virtual-machine:~$ 

但是rviuz2没有topic以及link都没有


# 26040906
lin@lin-virtual-machine:~/Lin_workspace/6_Mpu6050t1_ws$ source install/setup.bash
lin@lin-virtual-machine:~/Lin_workspace/6_Mpu6050t1_ws$ rviz2
Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway.
[INFO] [1775707434.304723055] [rviz2]: Stereo is NOT SUPPORTED
[INFO] [1775707434.304811557] [rviz2]: OpenGl version: 4.5 (GLSL 4.5)
[INFO] [1775707434.375741972] [rviz2]: Stereo is NOT SUPPORTED
rviz中仍然没有link,topic

# 26040907
如何确认ros是否收到串口数据？“lin@lin-virtual-machine:~$ ros2 topic list
/imu/data
/parameter_events
/rosout
lin@lin-virtual-machine:~$ 
”
## -2
---
header:
  stamp:
    sec: 1775708245
    nanosec: 680026434
  frame_id: imu_link
orientation:
  x: 0.06
  y: 0.0
  z: -0.59
  w: 0.79
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
^Clin@lin-virtual-machine:~$ 

## -3
lin@lin-virtual-machine:~$ ros2 topic list
/imu/data
/parameter_events
/rosout
lin@lin-virtual-machine:~$ ros2 topic list
/parameter_events
/rosout
lin@lin-virtual-machine:~$ ros2 topic list
/parameter_events
/rosout
lin@lin-virtual-machine:~$ ros2 topic list
/parameter_events
/rosout
lin@lin-virtual-machine:~$ ros2 topic list
/parameter_events
/rosout
lin@lin-virtual-machine:~$ ros2 topic list
/parameter_events
/rosout
lin@lin-virtual-machine:~$ 

## -4
lin@lin-virtual-machine:~$ ros2 topic list
/parameter_events
/rosout
lin@lin-virtual-machine:~$ 
仍然没有，换其他方法



### -1 问题总结

#### 1. 当前状态

*   **数据链路已完全打通 (成功)**：
    *   STM32 -> 串口 -> `imu_node` -> `/imu/data` 话题。
    *   我们已经通过 `ros2 topic echo /imu/data` 命令**亲眼看到**了 IMU 数据的实时滚动，这证明了从硬件到软件的数据流是**健康且正常的**。

*   **ROS2 网络通信已修复 (成功)**：
    *   通过在每个终端使用 `export ROS_LOCALHOST_ONLY=1`，我们解决了节点间互相“看不见”的问题。
    *   `ros2 topic list` 现在可以正确显示 `imu_node` 发布的话题。

*   **最终的可视化出现问题 (待解决)**：
    *   尽管数据已经在 ROS 网络中流动，但在 RViz2 中仍然看不到 `/imu/data` 话题和 `imu_link` 坐标系。

#### 2. 问题根源分析

**核心问题不在代码，而在【环境】。**

这 100% 是一个 ROS 环境配置问题。根本原因在于：**启动 RViz2 的那个终端，没有和启动 `imu_node` 的终端处于完全相同的、被正确配置过的 ROS 环境中。**

#### 3. 唯一的解决方案

解决这个问题的唯一方法，就是养成一个标准的、肌肉记忆般的 ROS 操作习惯。对于我们当前的项目，在**打开任何一个新的终端**后，都必须**严格按顺序**执行以下三步，缺一不可：

1.  **`cd /home/lin/Lin_workspace/6_Mpu6050t1_ws`** (进入工作区)
2.  **`export ROS_LOCALHOST_ONLY=1`** (加入本地网络)
3.  **`source install/setup.bash`** (激活工作区)

只要保证运行 `imu_node` 的终端和运行 `rviz2` 的终端都执行了这三步，RViz2 就一定能看到话题。

#### 换用web-gpt解决（更换了主体函数）

---
header:
  stamp:
    sec: 1775710813
    nanosec: 627884132
  frame_id: imu_link
orientation:
  x: -0.04
  y: -0.07
  z: -0.46
  w: 0.87
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 643071099
  frame_id: imu_link
orientation:
  x: -0.06
  y: -0.08
  z: -0.47
  w: 0.87
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 657564104
  frame_id: imu_link
orientation:
  x: -0.07
  y: -0.09
  z: -0.47
  w: 0.87
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 667667023
  frame_id: imu_link
orientation:
  x: -0.08
  y: -0.1
  z: -0.47
  w: 0.86
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 682879445
  frame_id: imu_link
orientation:
  x: -0.09
  y: -0.11
  z: -0.47
  w: 0.86
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 697778609
  frame_id: imu_link
orientation:
  x: -0.1
  y: -0.12
  z: -0.47
  w: 0.86
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 712920899
  frame_id: imu_link
orientation:
  x: -0.1
  y: -0.13
  z: -0.47
  w: 0.86
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 727640401
  frame_id: imu_link
orientation:
  x: -0.1
  y: -0.15
  z: -0.48
  w: 0.85
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 743167763
  frame_id: imu_link
orientation:
  x: -0.11
  y: -0.16
  z: -0.48
  w: 0.85
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775710813
    nanosec: 752713049
  frame_id: imu_link
orientation:
  x: -0.1
  y: -0.17
  z: -0.48
  w: 0.84
orientation_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.0
  y: 0.0
  z: 0.0
linear_acceleration_covariance:
- -1.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---

#### 还是不行
---
header:
  stamp:
    sec: 1775722281
    nanosec: 758931748
  frame_id: imu_link
orientation:
  x: 0.0
  y: 0.0
  z: 0.09
  w: 0.99
orientation_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: -0.01
  y: 0.0
  z: 9.81
linear_acceleration_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775722281
    nanosec: 774205627
  frame_id: imu_link
orientation:
  x: 0.0
  y: 0.0
  z: 0.09
  w: 0.99
orientation_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: 0.01
  y: 0.01
  z: 9.83
linear_acceleration_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775722281
    nanosec: 789184803
  frame_id: imu_link
orientation:
  x: 0.0
  y: 0.0
  z: 0.09
  w: 0.99
orientation_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: -0.04
  y: 0.0
  z: 9.89
linear_acceleration_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---
header:
  stamp:
    sec: 1775722281
    nanosec: 800952752
  frame_id: imu_link
orientation:
  x: 0.0
  y: 0.0
  z: 0.09
  w: 0.99
orientation_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
angular_velocity:
  x: 0.0
  y: 0.0
  z: 0.0
angular_velocity_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
linear_acceleration:
  x: -0.02
  y: 0.01
  z: 9.84
linear_acceleration_covariance:
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
- 0.0
---

lin@lin-virtual-machine:~$ ros2 topic list 
/clicked_point
/goal_pose
/imu/data
/initialpose
/parameter_events
/rosout
/tf
/tf_static
lin@lin-virtual-machine:~$ 

lin@lin-virtual-machine:~$ ros2 topic echo /tf_static
transforms:
- header:
    stamp:
      sec: 1775722113
      nanosec: 948034814
    frame_id: map
  child_frame_id: imu_link
  transform:
    translation:
      x: 0.0
      y: 0.0
      z: 0.0
    rotation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
---


lin@lin-virtual-machine:~$ ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map imu_link
[WARN] [1775722113.922530424] []: Old-style arguments are deprecated; see --help for new-style arguments
[INFO] [1775722113.949416652] [static_transform_publisher_nI064wN1JeuBQVrq]: Spinning until stopped - publishing transform
translation: ('0.000000', '0.000000', '0.000000')
rotation: ('0.000000', '0.000000', '0.000000', '1.000000')
from 'map' to 'imu_link'

lin@lin-virtual-machine:~$ ros2 topic hz /imu/data
average rate: 66.870
	min: 0.006s max: 0.023s std dev: 0.00361s window: 68
average rate: 66.774
	min: 0.005s max: 0.023s std dev: 0.00351s window: 135
average rate: 66.727
	min: 0.005s max: 0.024s std dev: 0.00340s window: 202
average rate: 66.639
	min: 0.005s max: 0.024s std dev: 0.00312s window: 269
average rate: 66.710
	min: 0.005s max: 0.025s std dev: 0.00303s window: 337
^Clin@lin-virtual-machine:~$ 


^Clin@lin-virtual-machine:~$ ros2 run tf2_ros tf2_echo map imu_link
[INFO] [1775723423.939967260] [tf2_echo]: Waiting for transform map ->  imu_link: Invalid frame ID "map" passed to canTransform argument target_frame - frame does not exist
[INFO] [1775723425.923508307] [tf2_echo]: Waiting for transform map ->  imu_link: Invalid frame ID "map" passed to canTransform argument target_frame - frame does not exist
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
At time 0.0
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [0.000, -0.000, 0.000]
- Matrix:
  1.000  0.000  0.000  0.000
  0.000  1.000  0.000  0.000
  0.000  0.000  1.000  0.000
  0.000  0.000  0.000  1.000
^C[INFO] [1775723438.184310630] [rclcpp]: signal_handler(SIGINT/SIGTERM)
lin@lin-virtual-machine:~$ 



这是stm32端侧的数据格式
printf("%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld\r\n",
            (long)(imu_output.orientation[0] * 100),
            (long)(imu_output.orientation[1] * 100),
            (long)(imu_output.orientation[2] * 100),
            (long)(imu_output.orientation[3] * 100),
+           (long)(imu_output.linear_acceleration[0] * 100),
+           (long)(imu_output.linear_acceleration[1] * 100),
+           (long)(imu_output.linear_acceleration[2] * 100),
+           (long)(imu_output.angular_velocity[0] * 100),
+           (long)(imu_output.angular_velocity[1] * 100),
+           (long)(imu_output.angular_velocity[2] * 100),
+           (long)(imu_data.Pitch * 10), // Pitch, Roll, Yaw 仍使用度, 方便观察
+           (long)(imu_data.Roll * 10),
+           (long)(imu_data.Yaw * 10));


#### 成功！