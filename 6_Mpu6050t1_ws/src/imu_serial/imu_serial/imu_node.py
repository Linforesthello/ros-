import rclpy
from rclpy.node import Node
import serial
from sensor_msgs.msg import Imu, MagneticField
from geometry_msgs.msg import Vector3Stamped
import time

class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)

        serial_port = self.get_parameter('serial_port').value
        baud_rate   = self.get_parameter('baud_rate').value

        self.get_logger().info(f'Connecting to {serial_port} @ {baud_rate}')

        # 串口连接（带重试）
        while True:
            try:
                self.ser = serial.Serial(serial_port, baud_rate, timeout=0.01)
                break
            except Exception as e:
                self.get_logger().warn(f'Serial failed: {e}, retry...')
                time.sleep(2)

        self.get_logger().info('Serial connected')

        # 发布器
        self.pub_imu = self.create_publisher(Imu,            '/imu/data',    10)
        self.pub_mag = self.create_publisher(MagneticField,  '/imu/mag',     10)
        self.pub_rpy = self.create_publisher(Vector3Stamped, '/imu/rpy',     10)

        # 接收缓冲区
        self.buffer = ''

        # 定时读取（5 ms）
        self.timer = self.create_timer(0.005, self.read_serial)

    # ------------------------------------------------------------------
    def read_serial(self):
        try:
            data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
            if not data:
                return

            self.buffer += data

            while '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                line = line.strip()
                if line:
                    self.process_line(line)

        except Exception as e:
            self.get_logger().error(f'Serial error: {e}')

    # ------------------------------------------------------------------
    # 串口帧格式（16 字段，逗号分隔）：
    #   [0]  w   * 100     四元数
    #   [1]  x   * 100
    #   [2]  y   * 100
    #   [3]  z   * 100
    #   [4]  ax  * 100     线加速度  m/s²
    #   [5]  ay  * 100
    #   [6]  az  * 100
    #   [7]  gx  * 100     角速度    rad/s
    #   [8]  gy  * 100
    #   [9]  gz  * 100
    #   [10] Pitch * 10    欧拉角    °
    #   [11] Roll  * 10
    #   [12] Yaw   * 10
    #   [13] mx  * 10      磁场      μT
    #   [14] my  * 10
    #   [15] mz  * 10
    # ------------------------------------------------------------------
    def process_line(self, line):
        parts = line.split(',')
        if len(parts) != 16:
            return

        try:
            d = list(map(int, parts))
        except ValueError:
            return

        stamp = self.get_clock().now().to_msg()

        # ---------- /imu/data ----------
        imu = Imu()
        imu.header.stamp    = stamp
        imu.header.frame_id = 'imu_link'

        imu.orientation.w = d[0]  / 100.0
        imu.orientation.x = d[1]  / 100.0
        imu.orientation.y = d[2]  / 100.0
        imu.orientation.z = d[3]  / 100.0

        imu.linear_acceleration.x = d[4]  / 100.0
        imu.linear_acceleration.y = d[5]  / 100.0
        imu.linear_acceleration.z = d[6]  / 100.0

        imu.angular_velocity.x = d[7]  / 100.0
        imu.angular_velocity.y = d[8]  / 100.0
        imu.angular_velocity.z = d[9]  / 100.0

        # 协方差（-1 = 未知）
        imu.orientation_covariance[0]         = -1.0
        imu.angular_velocity_covariance[0]    = -1.0
        imu.linear_acceleration_covariance[0] = -1.0

        self.pub_imu.publish(imu)

        # ---------- /imu/mag ----------
        mag = MagneticField()
        mag.header.stamp    = stamp
        mag.header.frame_id = 'imu_link'

        mag.magnetic_field.x = d[13] / 10.0   # μT
        mag.magnetic_field.y = d[14] / 10.0
        mag.magnetic_field.z = d[15] / 10.0

        mag.magnetic_field_covariance[0] = -1.0

        self.pub_mag.publish(mag)

        # ---------- /imu/rpy ----------
        rpy = Vector3Stamped()
        rpy.header.stamp    = stamp
        rpy.header.frame_id = 'imu_link'

        rpy.vector.x = d[11] / 10.0   # Roll  °
        rpy.vector.y = d[10] / 10.0   # Pitch °
        rpy.vector.z = d[12] / 10.0   # Yaw   °

        self.pub_rpy.publish(rpy)

    # ------------------------------------------------------------------
    def destroy_node(self):
        self.ser.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = ImuNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
