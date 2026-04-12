 1630  git commit -m "Linux丨obsidian部署"
 1631  git push
 1632  git remote -v
 1633  ls ~/.ssh
 1634  cat ~/.ssh/id_ed25519.pub
 1635  ssh -T git@github.com
 1636  nano ~/.ssh/config
 1637  git remote set-url origin git@github.com:Linforesthello/Open-Notes-Library.git
 1638  git push
 1639  git remote set-url origin https://github.com/Linforesthello/Open-Notes-Library.git
 1640  git push
 1641  git remote set-url origin https://github.com/Linforesthello/Open-Notes-Library.git
 1642  git push
 1643  git credential reject
 1644  git remote -v
 1645  git push
 1646  git add .
 1647  cd Downloads/
 1648  ls
 1649  chmod +x Obsidian-1.12.7.AppImage 
 1650  l
 1651  ls
 1652  clear
 1653  l
 1654  ./Obsidian-1.12.7.AppImage 
 1655  chmod +x ~/Downloads/Obsidian-1.12.7.AppImage
 1656  ls
 1657  sudo ln -s ~/Downloads/Obsidian-1.12.7.AppImage /usr/local/bin/obsidian
 1658  poweroff 
 1659  exit
 1660  ls /dev/ttyACM0 
 1661  rviz2
 1662  pip install pyserial
 1663  source ~/.bashrc 
 1664  clear
 1665  ros2 run imu_serial imu_node
 1666  source install/setup.bash
 1667  source ~/.bashrc 
 1668  ros2 run imu_serial imu_node
 1669  clear
 1670  ros2 run imu_serial imu_node
 1671  source install/setup.bash
 1672  ros2 run imu_serial imu_node
 1673  clear
 1674  ros2 run imu_serial imu_node
 1675  clear
 1676  ros2 run imu_serial imu_node
 1677  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM0
 1678  ros2 topic echo /imu/data
 1679  clear
 1680  ros2 topic echo /imu/data
 1681  clear
 1682  ros2 topic echo /imu/data
 1683  poweroff 
 1684  ros2 topic echo /imu/data
 1685  clear
 1686  ros2 topic list 
 1687  obsidian 
 1688  cd src/
 1689  ros2 pkg create --build-type ament_python imu_serial
 1690  cd ..
 1691  clear
 1692  export ROS_LOCALHOST_ONLY=1
 1693  source install/setup.bash
 1694  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM0
 1695  ls
 1696  cd 6_Mpu6050_ros_t1/
 1697  ls
 1698  cd src/
 1699  cd ..
 1700  colcon build
 1701  ls
 1702  clear
 1703  ls
 1704  l
 1705  clear
 1706  ls
 1707  cd src/
 1708  ls
 1709  ros2 pkg create my_robot_pkg --build-type ament_python
 1710  cd ..
 1711  colcon build/
 1712  colcon build
 1713  colcon build --symlink-install
 1714  colcon build --symlink-install
 1715  clear
 1716  ls
 1717  colcon build --symlink-install
 1718  tree -L 2
 1719  colcon build --symlink-install
 1720  source ~/.bashrc
 1721  colcon build --symlink-install
 1722  tree -L 2
 1723  clear
 1724  colcon build
 1725  ros2 run imu_serial imu_node
 1726  source install/setup.bash
 1727  ros2 run imu_serial imu_node
 1728  colcon build
 1729  source install/setup.bash
 1730  colcon build
 1731  source install/setup.bash
 1732  colcon build
 1733  source install/setup.bash
 1734  colcon build
 1735  source install/setup.bash
 1736  colcon build
 1737  source install/setup.bash
 1738  rviz2
 1739  export ROS_LOCALHOST_ONLY=1
 1740  source install/setup.bash
 1741  ros2 topic list 
 1742  rviz2
 1743  tree -L 2
 1744  tree -L 3
 1745  clear
 1746  cd ~/ProjectRequirement/MCU/Lin_STM32/STM32_F103C8T6/STM32_Now/
 1747  ls
 1748  git add .
 1749  git commit -m "Linux丨Mpu6050,更新了文件架构，后面以此为基准"
 1750  git push
 1751  rviz2
 1752  cd /home/lin/Lin_workspace/6_Mpu6050t1_ws
 1753  export ROS_LOCALHOST_ONLY=1
 1754  source install/setup.bash
 1755  rviz2
 1756  export ROS_LOCALHOST_ONLY=1
 1757  rviz2
 1758  ros2 topic list 
 1759  clear
 1760  git add .
 1761  git commit -m "Linux丨Mpu6050输出格式规范化，已经介入ros,可从topic echo看到数据变化"
 1762  git push
 1763  cd .
 1764  cd ..
 1765  colcon build
 1766  source install/setup.bash
 1767  export ROS_LOCALHOST_ONLY=1
 1768  ros2 run imu_serial imu_node
 1769  colcon build
 1770  export ROS_LOCALHOST_ONLY=1
 1771  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM1
 1772  cd src/
 1773  python3 imu_node.py 
 1774  cd ..
 1775  colcon build
 1776  exit
 1777  ros2 topic echo /imu/data
 1778  clear
 1779  ros2 node list
 1780  lsof /dev/ttyACM0
 1781  ros2 topic echo /imu/data
 1782  lsof /dev/ttyACM0
 1783  ros2 pkg list | grep imu_serial
 1784  ros2 run imu_serial imu_node
 1785  source /opt/ros/humble/setup.bash
 1786  source ~/Lin_workspace/6_Mpu6050t1_ws/install/setup.bash
 1787  ros2 run imu_serial imu_node
 1788  echo $ROS_DOMAIN_ID
 1789  ros2 run imu_serial imu_node
 1790  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM0 
 1791  cd /home/lin/Lin_workspace/6_Mpu6050t1_ws
 1792  export ROS_LOCALHOST_ONLY=1
 1793  source install/setup.bash
 1794  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM0
 1795  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM1
 1796  export ROS_LOCALHOST_ONLY=1
 1797  source install/setup.bash
 1798  ros2 run imu_serial imu_node --ros-args -p serial_port:=/dev/ttyACM1
 1799  ros2 run imu_serial imu_node
 1800  clear
 1801  ource /opt/ros/humble/setup.bash
 1802  source /opt/ros/humble/setup.bash
 1803  source ~/Lin_workspace/6_Mpu6050t1_ws/install/setup.bash
 1804  rviz2 
 1805  ros2 topic list]
 1806  ros2 topic list
 1807  clear
 1808  ros2 topic list
 1809  source ~/.bashrc 
 1810  ros2 topic list
 1811  ros2 run imu_serial imu_node
 1812  clear
 1813  source /opt/ros/humble/setup.bash
 1814  source ~/Lin_workspace/6_Mpu6050t1_ws/install/setup.bash
 1815  ros2 topic list
 1816  echo $ROS_DOMAIN_ID
 1817  ros2 topic list
 1818  clear
 1819  ros2 topic list
 1820  cd ~
 1821  clear
 1822  ros2 run rqt_console 
 1823  ros2 run rqt_console rqt_console 
 1824  ros2 run rqt_graph rqt_graph 
 1825  ls /dev/ttyACM*
 1826  sudo chmod 666 /dev/ttyACM0
 1827  ls /dev/ttyACM*
 1828  clear
 1829  ls /dev/ttyACM*
 1830  source /opt/ros/humble/setup.bash
 1831  source ~/Lin_workspace/6_Mpu6050t1_ws/install/setup.bash
 1832  ls /dev/ttyACM*
 1833  clear
 1834  ros2 topic echo /imu/data 
 1835  source ~/.bashrc 
 1836  clear
 1837  cd ../..
 1838  git add .
 1839  git commit -m "Linux丨Mpu6050输出格式规范化，已经介入ros,可从topic echo看到数据变化"
 1840  git push
 1841  cd ..
 1842  colcon build
 1843  ros2 topic echo /tf_static
 1844  source ~/.bashrc 
 1845  clear
 1846  ros2 topic echo /tf_static
 1847  ros2 topic list 
 1848  source ~/.bashrc
 1849  ros2 topic list 
 1850  source ~/.bashrc
 1851  ros2 topic list 
 1852  clear
 1853  ros2 topic list 
 1854  source ~/.bashrc
 1855  clear
 1856  ros2 topic list 
 1857  ros2 run rqt_console rqt_console 
 1858  obsidian 
 1859  ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map imu_link
 1860  clear
 1861  source ~/.bashrc
 1862  ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map imu_link
 1863  rviz2
 1864  source ~/.bashrc
 1865  source ~/.bashrccle
 1866  clear
 1867  rviz2
 1868  ros2 run tf2_tools view_frames
 1869  source ~/.bashrc
 1870  ros2 run tf2_tools view_frames
 1871  clear
 1872  ros2 topic echo /imu/data 
 1873  source ~/.bashrc
 1874  ros2 topic echo /imu/data 
 1875  source ~/.bashrc
 1876  ros2 topic echo /imu/data 
 1877  clear
 1878  ros2 topic echo /imu/data 
 1879  source ~/.bashrc
 1880  ros2 topic echo /imu/data 
 1881  sudo apt install ros-humble-rviz-imu-plugin
 1882  ros2 run imu_serial imu_node 
 1883  source ~/.bashrc 
 1884  ros2 run imu_serial imu_node 
 1885  source ~/.bashrc 
 1886  ros2 run imu_serial imu_node 
 1887  source ~/.bashrc 
 1888  clear
 1889  ros2 run imu_serial imu_node 
 1890  ls /dev/ttyACM0 
 1891  ls /dev/ttyACM*
 1892  source ~/.bashrc
 1893  ls /dev/ttyACM*
 1894  source ~/.bashrc
 1895  ls /dev/ttyACM*
 1896  source ~/.bashrc
 1897  ls /dev/ttyACM*
 1898  ros2 topic hz /imu/data
 1899  ros2 run tf2_ros tf2_echo map imu_link
 1900  git add .
 1901  git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"
 1902  git push
 1903  git add .
 1904  git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"
 1905  git push
 1906  git add .
 1907  git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"
 1908  git push
 1909  git remote -v
 1910  ssh -vT git@198.18.0.7
 1911  ping 198.18.0.7
 1912  git remote -v
 1913  ssh -vT git@github.com
 1914  cat ~/.ssh/config
 1915  git config --global credential.helper
 1916  nautilus .
 1917  git rm -r --cached 6_Mpu6050t1_ws/build
 1918  git rm -r --cached 6_Mpu6050t1_ws/install
 1919  git rm -r --cached 6_Mpu6050t1_ws/log
 1920  git rm -r --cached .vscode
 1921  nautilus .
 1922  exit
 1923  ros2 run rqt_graph rqt_graph 
 1924  obsidian 
 1925  reboot 
 1926  cd ..
 1927  cd 6_Mpu6050t1_ws/
 1928  git add .
 1929  cd ..
 1930  git add .
 1931  git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"
 1932  git push
 1933  git status
 1934  git push
 1935  git pull
 1936  clear
 1937  git remote set-url origin https://github.com/Linforesthello/ros-.git
 1938  git add .
 1939  git commit -m "Liunx丨完善了stm32端侧Mpu6050数据格式,完善imu_node.py,成功接入ros并在rviz2中显示,更新了claude api"
 1940  git push
 1941  git config --global credential.helper
 1942  git add .
 1943  git commit -m "Linux丨更新了.gitignore"
 1944  git push
 1945  git add .
 1946  git commit -m "Linux丨更新了.gitignore"
 1947  git push
 1948  git add .
 1949  git commit -m "Linux丨更新了.gitignore"
 1950  git push
 1951  git add .
 1952  git commit -m "Linux丨更新了.gitignore,从git上删除了已经追踪的无必要文件"
 1953  git push
 1954  git rm -r --cached 6_Mpu6050t1_ws/build
 1955  git rm -r --cached 6_Mpu6050t1_ws/install
 1956  git rm -r --cached 6_Mpu6050t1_ws/log
 1957  git rm -r --cached .vscode
 1958  git add .gitignore
 1959  git commit --amend --no-edit
 1960  git push
 1961  git rm -r --cached unitree_goM80106/build
 1962  git add .
 1963  git commit -m "Linux丨更新了.gitignore,从git上删除了已经追踪的无必要文件"
 1964  git push
 1965  git rm -r --cached unitree_goM80106/build
 1966  git rm -r --cached unitree_goM80106/include
 1967  git rm -r --cached unitree_goM80106/lib
 1968  git commit -m "Linux丨删掉了unitree,太大了"
 1969  git push
 1970  git rm -r --cached vision/other/
 1971  git push
 1972  git add .
 1973  git commit -m "Linux丨删掉了unitree,太大了"
 1974  git push
 1975  git reset origin/master
 1976  git commit -m "Linux丨还能成功吗"
 1977  git push]
 1978  git push
 1979  git add .
 1980  git commit -m "Linux丨经历了git提交异常文件过大,重新整理提交和giignore“
 1981  git commit -m "Linux丨经历了git提交异常文件过大,重新整理提交和giignore"
 1982  git push
 1983  git add .
 1984  git commit -m "Linux丨经历了git提交异常文件过大,重新整理提交和giignore"
 1985  git push
 1986  nautilus .
 1987  git status
 1988  git add .
 1989  git status
 1990  clear
 1991  git diff --cached
 1992  nload 
 1993  poweroff 
 1994  gparted 
 1995  poweroff 
 1996  history
lin@lin-virtual-machine:~$ 