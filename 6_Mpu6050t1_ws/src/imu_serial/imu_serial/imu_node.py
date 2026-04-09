import rclpy
from rclpy.node import Node
import serial
from sensor_msgs.msg import Imu
import time

class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)

        serial_port = self.get_parameter('serial_port').value
        baud_rate = self.get_parameter('baud_rate').value

        self.get_logger().info(f'Connecting to {serial_port} @ {baud_rate}')

        # 串口连接
        while True:
            try:
                self.ser = serial.Serial(serial_port, baud_rate, timeout=0.01)
                break
            except Exception as e:
                self.get_logger().warn(f'Serial failed: {e}, retry...')
                time.sleep(2)

        self.get_logger().info("Serial connected")

        # 发布器
        self.pub = self.create_publisher(Imu, '/imu/data', 10)

        # 缓冲区（关键！！！）
        self.buffer = ""

        # 定时器（更快一点）
        self.timer = self.create_timer(0.005, self.read_serial)

    def read_serial(self):
        try:
            # 读取所有可用数据（关键）
            data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')

            if not data:
                return

            self.buffer += data

            # 按行拆包
            while '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                line = line.strip()

                self.process_line(line)

        except Exception as e:
            self.get_logger().error(f"Serial error: {e}")

    def process_line(self, line):
        parts = line.split(',')

        if len(parts) != 13:
            return

        try:
            data = list(map(int, parts))
        except:
            return

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        # 四元数
        msg.orientation.w = data[0] / 100.0
        msg.orientation.x = data[1] / 100.0
        msg.orientation.y = data[2] / 100.0
        msg.orientation.z = data[3] / 100.0

        # 加速度
        msg.linear_acceleration.x = data[4] / 100.0
        msg.linear_acceleration.y = data[5] / 100.0
        msg.linear_acceleration.z = data[6] / 100.0

        # 角速度
        msg.angular_velocity.x = data[7] / 100.0
        msg.angular_velocity.y = data[8] / 100.0
        msg.angular_velocity.z = data[9] / 100.0

        # covariance
        # msg.orientation_covariance[0] = -1
        # msg.angular_velocity_covariance[0] = -1
        # msg.linear_acceleration_covariance[0] = -1

        self.pub.publish(msg)

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