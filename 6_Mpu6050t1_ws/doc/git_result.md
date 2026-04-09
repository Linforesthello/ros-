
## -1
lin@lin-virtual-machine:~/Lin_workspace$ git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"
[master 0799518] Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api
 217 files changed, 8695 insertions(+), 1 deletion(-)
 create mode 100644 .vscode/browse.vc.db
 create mode 100644 .vscode/browse.vc.db-shm
 create mode 100644 .vscode/browse.vc.db-wal
 create mode 100644 .vscode/c_cpp_properties.json
 create mode 100644 .vscode/settings.json
 create mode 100644 6_Mpu6050t1_ws/build/.built_by
 create mode 100644 6_Mpu6050t1_ws/build/COLCON_IGNORE
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/build/lib/imu_serial/__init__.py
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/build/lib/imu_serial/imu_node.py
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/colcon_build.rc
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/colcon_command_prefix_setup_py.sh
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/colcon_command_prefix_setup_py.sh.env
 create mode 120000 6_Mpu6050t1_ws/build/imu_serial/imu_serial
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/PKG-INFO
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/SOURCES.txt
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/dependency_links.txt
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/entry_points.txt
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/requires.txt
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/top_level.txt
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/zip-safe
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/install.log
 create mode 120000 6_Mpu6050t1_ws/build/imu_serial/package.xml
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/prefix_override/__pycache__/sitecustomize.cpython-310.pyc
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/prefix_override/sitecustomize.py
 create mode 120000 6_Mpu6050t1_ws/build/imu_serial/resource/imu_serial
 create mode 120000 6_Mpu6050t1_ws/build/imu_serial/setup.cfg
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/share/imu_serial/hook/pythonpath_develop.dsv
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/share/imu_serial/hook/pythonpath_develop.ps1
 create mode 100644 6_Mpu6050t1_ws/build/imu_serial/share/imu_serial/hook/pythonpath_develop.sh
 create mode 100644 6_Mpu6050t1_ws/doc/goal.md
 create mode 100644 6_Mpu6050t1_ws/doc/result.md
 create mode 100644 6_Mpu6050t1_ws/doc/trae.md
 create mode 100644 6_Mpu6050t1_ws/install/.colcon_install_layout
 create mode 100644 6_Mpu6050t1_ws/install/COLCON_IGNORE
 create mode 100644 6_Mpu6050t1_ws/install/_local_setup_util_ps1.py
 create mode 100644 6_Mpu6050t1_ws/install/_local_setup_util_sh.py
 create mode 100755 6_Mpu6050t1_ws/install/imu_serial/lib/imu_serial/imu_node
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/PKG-INFO
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/SOURCES.txt
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/dependency_links.txt
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/entry_points.txt
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/requires.txt
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/top_level.txt
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/zip-safe
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/__init__.py
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/__pycache__/__init__.cpython-310.pyc
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/__pycache__/imu_node.cpython-310.pyc
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/imu_node.py
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/ament_index/resource_index/packages/imu_serial
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/colcon-core/packages/imu_serial
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/ament_prefix_path.dsv
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/ament_prefix_path.ps1
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/ament_prefix_path.sh
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/pythonpath.dsv
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/pythonpath.ps1
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/pythonpath.sh
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.bash
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.dsv
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.ps1
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.sh
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.xml
 create mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.zsh
 create mode 100644 6_Mpu6050t1_ws/install/local_setup.bash
 create mode 100644 6_Mpu6050t1_ws/install/local_setup.ps1
 create mode 100644 6_Mpu6050t1_ws/install/local_setup.sh
 create mode 100644 6_Mpu6050t1_ws/install/local_setup.zsh
 create mode 100644 6_Mpu6050t1_ws/install/setup.bash
 create mode 100644 6_Mpu6050t1_ws/install/setup.ps1
 create mode 100644 6_Mpu6050t1_ws/install/setup.sh
 create mode 100644 6_Mpu6050t1_ws/install/setup.zsh
 create mode 100644 6_Mpu6050t1_ws/log/COLCON_IGNORE
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-35-07/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-35-07/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/logger_all.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/events.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/command.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/stdout.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/stdout_stderr.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/streams.log
 create mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/logger_all.log
 create mode 120000 6_Mpu6050t1_ws/log/latest
 create mode 120000 6_Mpu6050t1_ws/log/latest_build
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/imu_serial/__init__.py
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/imu_serial/imu_node.py
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/package.xml
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/resource/imu_serial
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/setup.cfg
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/setup.py
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/test/test_copyright.py
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/test/test_flake8.py
 create mode 100644 6_Mpu6050t1_ws/src/imu_serial/test/test_pep257.py
 create mode 100644 command/.can_counter.json
 rename {other => vision/other}/detect_ball.py (100%)
 rename {other => vision/other}/gemini_3d_2.py (100%)
 rename {other => vision/other}/gemini_3d_3_depth.py (100%)
lin@lin-virtual-machine:~/Lin_workspace$ git push
kex_exchange_identification: Connection closed by remote host
Connection closed by 198.18.0.7 port 22
fatal: 无法读取远程仓库。

请确认您有正确的访问权限并且仓库存在。
lin@lin-virtual-machine:~/Lin_workspace$ git status
位于分支 master
您的分支领先 'origin/master' 共 1 个提交。
  （使用 "git push" 来发布您的本地提交）

无文件要提交，干净的工作区
lin@lin-virtual-machine:~/Lin_workspace$ git push
kex_exchange_identification: Connection closed by remote host
Connection closed by 198.18.0.7 port 22
fatal: 无法读取远程仓库。

请确认您有正确的访问权限并且仓库存在。
lin@lin-virtual-machine:~/Lin_workspace$ git pull
kex_exchange_identification: Connection closed by remote host
Connection closed by 198.18.0.7 port 22
fatal: 无法读取远程仓库。

请确认您有正确的访问权限并且仓库存在。
lin@lin-virtual-machine:~/Lin_workspace$ 

## -2
lin@lin-virtual-machine:~/Lin_workspace$ git remote -v
origin  git@github.com:Linforesthello/ros-.git (fetch)
origin  git@github.com:Linforesthello/ros-.git (push)
lin@lin-virtual-machine:~/Lin_workspace$ ssh -vT git@198.18.0.7
OpenSSH_8.9p1 Ubuntu-3ubuntu0.14, OpenSSL 3.0.2 15 Mar 2022
debug1: Reading configuration data /home/lin/.ssh/config
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: /etc/ssh/ssh_config line 19: include /etc/ssh/ssh_config.d/*.conf matched no files
debug1: /etc/ssh/ssh_config line 21: Applying options for *
debug1: Connecting to 198.18.0.7 [198.18.0.7] port 22.
debug1: Connection established.
debug1: identity file /home/lin/.ssh/id_rsa type -1
debug1: identity file /home/lin/.ssh/id_rsa-cert type -1
debug1: identity file /home/lin/.ssh/id_ecdsa type -1
debug1: identity file /home/lin/.ssh/id_ecdsa-cert type -1
debug1: identity file /home/lin/.ssh/id_ecdsa_sk type -1
debug1: identity file /home/lin/.ssh/id_ecdsa_sk-cert type -1
debug1: identity file /home/lin/.ssh/id_ed25519 type 3
debug1: identity file /home/lin/.ssh/id_ed25519-cert type -1
debug1: identity file /home/lin/.ssh/id_ed25519_sk type -1
debug1: identity file /home/lin/.ssh/id_ed25519_sk-cert type -1
debug1: identity file /home/lin/.ssh/id_xmss type -1
debug1: identity file /home/lin/.ssh/id_xmss-cert type -1
debug1: identity file /home/lin/.ssh/id_dsa type -1
debug1: identity file /home/lin/.ssh/id_dsa-cert type -1
debug1: Local version string SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.14
kex_exchange_identification: Connection closed by remote host
Connection closed by 198.18.0.7 port 22
lin@lin-virtual-machine:~/Lin_workspace$ ping 198.18.0.7
PING 198.18.0.7 (198.18.0.7) 56(84) bytes of data.
64 bytes from 198.18.0.7: icmp_seq=1 ttl=64 time=3.36 ms
64 bytes from 198.18.0.7: icmp_seq=2 ttl=64 time=0.118 ms
64 bytes from 198.18.0.7: icmp_seq=3 ttl=64 time=0.097 ms
^C
--- 198.18.0.7 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2045ms
rtt min/avg/max/mdev = 0.097/1.190/3.355/1.530 ms
lin@lin-virtual-machine:~/Lin_workspace$ 

## -3
lin@lin-virtual-machine:~/Lin_workspace$ git remote -v
origin  git@github.com:Linforesthello/ros-.git (fetch)
origin  git@github.com:Linforesthello/ros-.git (push)
lin@lin-virtual-machine:~/Lin_workspace$ 

debug1: identity file /home/lin/.ssh/id_ed25519-cert type -1
debug1: identity file /home/lin/.ssh/id_ed25519_sk type -1
debug1: identity file /home/lin/.ssh/id_ed25519_sk-cert type -1
debug1: identity file /home/lin/.ssh/id_xmss type -1
debug1: identity file /home/lin/.ssh/id_xmss-cert type -1
debug1: identity file /home/lin/.ssh/id_dsa type -1
debug1: identity file /home/lin/.ssh/id_dsa-cert type -1
debug1: Local version string SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.14
kex_exchange_identification: Connection closed by remote host
Connection closed by 198.18.0.7 port 22
lin@lin-virtual-machine:~/Lin_workspace$ 


## 几点说明：

build/ / install/ / log/ — 忽略 ROS2 和 CMake 的编译产物
!unitree_goM80106/lib/*.so — 保留 lib/ 下的预编译 SDK（.so 文件），这些是项目依赖，不是构建产物
__pycache__/ / *.py[cod] — Python 缓存
*.log — ROS2 日志文件
如果 unitree_goM80106/lib/ 下的 .so 文件不需要提交（比如有其他分发方式），可以去掉那行例外规则。

## 文件大小
lin@lin-virtual-machine:~/Lin_workspace$ git remote set-url origin https://github.com/Linforesthello/ros-.git
lin@lin-virtual-machine:~/Lin_workspace$ git add .
^C
lin@lin-virtual-machine:~/Lin_workspace$ git add .
lin@lin-virtual-machine:~/Lin_workspace$ git add .
lin@lin-virtual-machine:~/Lin_workspace$ git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"

[master 4d5ba60] Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api
 3 files changed, 302 insertions(+)
 create mode 100644 6_Mpu6050t1_ws/doc/git_result.md
lin@lin-virtual-machine:~/Lin_workspace$ 
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 231, 完成.
对象计数中: 100% (231/231), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (193/193), 完成.
^C入对象中:   1% (4/219), 9.00 MiB | 87.00 KiB/s 
lin@lin-virtual-machine:~/Lin_workspace$ git config --global credential.helper
lin@lin-virtual-machine:~/Lin_workspace$ git add .
lin@lin-virtual-machine:~/Lin_workspace$ git commit -m "Linux丨更新了.gitignore"
[master 1bab46b] Linux丨更新了.gitignore
 2 files changed, 32 insertions(+), 1 deletion(-)
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 238, 完成.
对象计数中: 100% (238/238), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (199/199), 完成.
^C入对象中:   2% (6/225), 7.20 MiB | 82.00 KiB/s 
lin@lin-virtual-machine:~/Lin_workspace$ git add .
lin@lin-virtual-machine:~/Lin_workspace$ git commit -m "Linux丨更新了.gitignore"
位于分支 master
您的分支领先 'origin/master' 共 3 个提交。
  （使用 "git push" 来发布您的本地提交）

无文件要提交，干净的工作区
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 238, 完成.
对象计数中: 100% (238/238), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (199/199), 完成.
error: 无法倒回 rpc post 数据 - 尝试增加 http.postBuffer
error: RPC 失败。curl 56 GnuTLS recv error (-54): Error in the pull function.
send-pack: unexpected disconnect while reading sideband packet
写入对象中: 100% (225/225), 705.72 MiB | 7.11 MiB/s, 完成.
总共 225（差异 99），复用 0（差异 0），包复用 0
fatal: 远端意外挂断了
Everything up-to-date
lin@lin-virtual-machine:~/Lin_workspace$ git add .
lin@lin-virtual-machine:~/Lin_workspace$ git commit -m "Linux丨更新了.gitignore"
位于分支 master
您的分支领先 'origin/master' 共 3 个提交。
  （使用 "git push" 来发布您的本地提交）

无文件要提交，干净的工作区
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 238, 完成.
对象计数中: 100% (238/238), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (199/199), 完成.
^C入对象中:   2% (6/225), 1.98 MiB | 89.00 KiB/s 
lin@lin-virtual-machine:~/Lin_workspace$ 

### -1
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 244, 完成.
对象计数中: 100% (244/244), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (205/205), 完成.
^C入对象中:  17% (40/231), 7.84 MiB | 64.00 KiB/s 
lin@lin-virtual-machine:~/Lin_workspace$ git rm -r --cached 6_Mpu6050t1_ws/build
fatal: 路径规格 '6_Mpu6050t1_ws/build' 未匹配任何文件
lin@lin-virtual-machine:~/Lin_workspace$ git rm -r --cached 6_Mpu6050t1_ws/install
fatal: 路径规格 '6_Mpu6050t1_ws/install' 未匹配任何文件
lin@lin-virtual-machine:~/Lin_workspace$ git rm -r --cached 6_Mpu6050t1_ws/log
fatal: 路径规格 '6_Mpu6050t1_ws/log' 未匹配任何文件
lin@lin-virtual-machine:~/Lin_workspace$ git rm -r --cached .vscode
fatal: 路径规格 '.vscode' 未匹配任何文件
lin@lin-virtual-machine:~/Lin_workspace$ git add .gitignore
lin@lin-virtual-machine:~/Lin_workspace$ git commit --amend --no-edit
[master 480b5b7] Linux丨更新了.gitignore,从git上删除了已经追踪的无必要文件
 Date: Thu Apr 9 17:36:17 2026 +0800
 200 files changed, 83 insertions(+), 6826 deletions(-)
 delete mode 100644 .vscode/browse.vc.db
 delete mode 100644 .vscode/browse.vc.db-shm
 delete mode 100644 .vscode/browse.vc.db-wal
 delete mode 100644 .vscode/c_cpp_properties.json
 delete mode 100644 .vscode/settings.json
 delete mode 100644 6_Mpu6050t1_ws/build/.built_by
 delete mode 100644 6_Mpu6050t1_ws/build/COLCON_IGNORE
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/build/lib/imu_serial/__init__.py
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/build/lib/imu_serial/imu_node.py
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/colcon_build.rc
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/colcon_command_prefix_setup_py.sh
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/colcon_command_prefix_setup_py.sh.env
 delete mode 120000 6_Mpu6050t1_ws/build/imu_serial/imu_serial
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/PKG-INFO
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/SOURCES.txt
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/dependency_links.txt
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/entry_points.txt
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/requires.txt
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/top_level.txt
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/imu_serial.egg-info/zip-safe
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/install.log
 delete mode 120000 6_Mpu6050t1_ws/build/imu_serial/package.xml
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/prefix_override/__pycache__/sitecustomize.cpython-310.pyc
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/prefix_override/sitecustomize.py
 delete mode 120000 6_Mpu6050t1_ws/build/imu_serial/resource/imu_serial
 delete mode 120000 6_Mpu6050t1_ws/build/imu_serial/setup.cfg
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/share/imu_serial/hook/pythonpath_develop.dsv
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/share/imu_serial/hook/pythonpath_develop.ps1
 delete mode 100644 6_Mpu6050t1_ws/build/imu_serial/share/imu_serial/hook/pythonpath_develop.sh
 delete mode 100644 6_Mpu6050t1_ws/install/.colcon_install_layout
 delete mode 100644 6_Mpu6050t1_ws/install/COLCON_IGNORE
 delete mode 100644 6_Mpu6050t1_ws/install/_local_setup_util_ps1.py
 delete mode 100644 6_Mpu6050t1_ws/install/_local_setup_util_sh.py
 delete mode 100755 6_Mpu6050t1_ws/install/imu_serial/lib/imu_serial/imu_node
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/PKG-INFO
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/SOURCES.txt
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/dependency_links.txt
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/entry_points.txt
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/requires.txt
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/top_level.txt
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial-0.0.0-py3.10.egg-info/zip-safe
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/__init__.py
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/__pycache__/__init__.cpython-310.pyc
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/__pycache__/imu_node.cpython-310.pyc
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/lib/python3.10/site-packages/imu_serial/imu_node.py
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/ament_index/resource_index/packages/imu_serial
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/colcon-core/packages/imu_serial
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/ament_prefix_path.dsv
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/ament_prefix_path.ps1
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/ament_prefix_path.sh
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/pythonpath.dsv
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/pythonpath.ps1
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/hook/pythonpath.sh
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.bash
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.dsv
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.ps1
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.sh
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.xml
 delete mode 100644 6_Mpu6050t1_ws/install/imu_serial/share/imu_serial/package.zsh
 delete mode 100644 6_Mpu6050t1_ws/install/local_setup.bash
 delete mode 100644 6_Mpu6050t1_ws/install/local_setup.ps1
 delete mode 100644 6_Mpu6050t1_ws/install/local_setup.sh
 delete mode 100644 6_Mpu6050t1_ws/install/local_setup.zsh
 delete mode 100644 6_Mpu6050t1_ws/install/setup.bash
 delete mode 100644 6_Mpu6050t1_ws/install/setup.ps1
 delete mode 100644 6_Mpu6050t1_ws/install/setup.sh
 delete mode 100644 6_Mpu6050t1_ws/install/setup.zsh
 delete mode 100644 6_Mpu6050t1_ws/log/COLCON_IGNORE
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-35-07/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-35-07/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-39-05/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-41-07/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-42-52/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-25/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-46-31/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-50-35/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-54-41/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-56-10/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_11-57-39/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-27-06/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-28-34/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_12-46-38/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-22-38/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-23-43/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-25-46/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-27-56/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_13-47-48/logger_all.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/events.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/command.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/stdout.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/stdout_stderr.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/imu_serial/streams.log
 delete mode 100644 6_Mpu6050t1_ws/log/build_2026-04-09_16-06-48/logger_all.log
 delete mode 120000 6_Mpu6050t1_ws/log/latest
 delete mode 120000 6_Mpu6050t1_ws/log/latest_build
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 244, 完成.
对象计数中: 100% (244/244), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (205/205), 完成.
写入对象中:  17% (40/231), 1.87 MiB | 78.00 KiB/s 

### 成了？
lin@lin-virtual-machine:~/Lin_workspace$ git push
枚举对象中: 44, 完成.
对象计数中: 100% (44/44), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (29/29), 完成.
写入对象中: 100% (32/32), 18.83 KiB | 2.35 MiB/s, 完成.
总共 32（差异 10），复用 0（差异 0），包复用 0
remote: Resolving deltas: 100% (10/10), completed with 8 local objects.
To https://github.com/Linforesthello/ros-.git
   d11abb8..49c261d  master -> master
lin@lin-virtual-machine:~/Lin_workspace$ 
