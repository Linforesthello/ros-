import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math


def quat_from_yaw(yaw):
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class ImuOdomNode(Node):

    def __init__(self):
        super().__init__('imu_odom_node')

        # ===== 状态变量 =====
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.last_time = self.get_clock().now()

        # ===== 假设速度（你可以改成 cmd_vel 或电机速度）=====
        self.v = 0.0      # m/s（先设0，测试SLAM可改0.1）
        
        # IMU yaw输入（你可以替换成订阅 /imu）
        self.yaw_rate = 0.0

        # ===== 发布器 =====
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # ===== IMU订阅（如果你已经有yaw）=====
        self.create_subscription(
            Odometry,
            '/imu_odom_input',   # 或你改成 /imu
            self.imu_callback,
            10
        )

        # ===== 主循环 =====
        self.timer = self.create_timer(0.02, self.update)  # 50Hz

    # =========================
    # IMU输入（yaw）
    # =========================
    def imu_callback(self, msg):
        # 假设 yaw 放在 orientation.z (你可改成你的格式)
        # 如果你直接发 yaw（rad），可以这样：
        self.yaw_rate = msg.twist.twist.angular.z

    # =========================
    # 主更新
    # =========================
    def update(self):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        # ===== IMU积分 yaw =====
        self.yaw += self.yaw_rate * dt

        # ===== 里程计模型 =====
        self.x += self.v * math.cos(self.yaw) * dt
        self.y += self.v * math.sin(self.yaw) * dt

        # ===== 发布 ODOM =====
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y

        q = quat_from_yaw(self.yaw)
        odom.pose.pose.orientation = q

        odom.twist.twist.linear.x = self.v
        odom.twist.twist.angular.z = self.yaw_rate

        self.odom_pub.publish(odom)

        # ===== 发布 TF =====
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = "odom"
        t.child_frame_id = "base_link"

        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0

        t.transform.rotation = q

        self.tf_broadcaster.sendTransform(t)


def main():
    rclpy.init()
    node = ImuOdomNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()