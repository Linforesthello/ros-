#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseArray, Pose
import message_filters
import time

class VolleyballMasterTracker(Node):
    def __init__(self):
        super().__init__('volleyball_master_tracker')

        # --- [1. 物理参数与场域定义] ---
        self.GRAVITY = 9.81         
        self.COURT_HALF_LENGTH = 6.7 # 羽毛球场中线位置（假设相机在底线）
        
        # --- [2. 视觉阈值 (融合黄、蓝双色排球)] ---
        self.hsv_yellow = (np.array([15, 80, 80]), np.array([40, 255, 255]))
        self.hsv_blue = (np.array([100, 100, 80]), np.array([135, 255, 255]))

        # --- [3. 追踪与状态管理] ---
        self.balls = {} # ID -> {kf, last_seen, side}
        self.next_id = 0
        self.max_lost_time = 0.5         # 丢帧容忍时间（秒）
        self.last_z = 1.5                
        self.base_roi_size = 250         # 1.0米时的 ROI 像素尺寸

        self.bridge = CvBridge()
        self.camera_info_received = False
        self.last_time = time.time()

        # --- [4. ROS2 通信接口] ---
        self.info_sub = self.create_subscription(CameraInfo, '/camera/color/camera_info', self.info_cb, 10)
        self.color_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')
        # 同步频率设置为 20Hz (0.05s)
        self.ts = message_filters.ApproximateTimeSynchronizer([self.color_sub, self.depth_sub], 10, 0.05)
        self.ts.registerCallback(self.process_callback)

        self.pos_pub = self.create_publisher(PoseArray, '/ball_tracking/current_poses', 10)
        self.pred_pub = self.create_publisher(PoseArray, '/ball_tracking/predicted_impacts', 10)

    def info_cb(self, msg):
        if not self.camera_info_received:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
            self.camera_info_received = True

    def create_kf(self, pos):
        """创建 6 维卡尔曼滤波器: [x, y, z, vx, vy, vz]"""
        kf = cv2.KalmanFilter(6, 3)
        kf.transitionMatrix = np.eye(6, dtype=np.float32)
        kf.measurementMatrix = np.zeros((3, 6), np.float32)
        kf.measurementMatrix[0:3, 0:3] = np.eye(3)
        # 针对高速排球调优噪声参数
        kf.processNoiseCov = np.eye(6, dtype=np.float32) * 0.005
        kf.measurementNoiseCov = np.eye(3, dtype=np.float32) * 0.01
        kf.statePost[:3, 0] = pos
        return kf

    def get_prediction(self, state):
        """物理落点预测：计算排球撞击地面(Z=0)的 (x, y) 坐标"""
        x, y, z, vx, vy, vz = state.flatten()
        # 物理公式: z + vz*t - 0.5*g*t^2 = 0
        a = -0.5 * self.GRAVITY
        b = vz
        c = z
        delta = b**2 - 4*a*c
        if delta < 0 or z <= 0.1: return None # 无落地解或球已落地
        
        t_hit = (-b - np.sqrt(delta)) / (2*a) # 求解正向时间
        if t_hit < 0: return None
        
        pred_x = float(x + vx * t_hit)
        pred_y = float(y + vy * t_hit)
        return (pred_x, pred_y, 0.0)

    def process_callback(self, color_msg, depth_msg):
        if not self.camera_info_received: return
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        try:
            img = self.bridge.imgmsg_to_cv2(color_msg, 'bgr8')
            depth = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        except: return
        h, w = img.shape[:2]

        # --- 1. 视觉识别 (全图多目标检测) ---
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.bitwise_or(cv2.inRange(hsv, *self.hsv_yellow), cv2.inRange(hsv, *self.hsv_blue))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 120: continue
            (ux, uy), rad = cv2.minEnclosingCircle(cnt)
            ix, iy = int(ux), int(uy)
            
            # 安全深度采样 (5x5 中值滤波防止空洞)
            roi = depth[max(0,iy-2):min(h,iy+3), max(0,ix-2):min(w,ix+3)]
            valid_d = roi[roi > 0]
            if valid_d.size > 0:
                zm = float(np.median(valid_d)) / 1000.0 # mm -> m
                xm = (ux - self.cx) * zm / self.fx
                ym = (uy - self.cy) * zm / self.fy
                detections.append(np.array([xm, ym, zm], dtype=np.float32))

        # --- 2. 数据关联与卡尔曼更新 ---
        used_idx = []
        for b_id, b_data in list(self.balls.items()):
            kf = b_data['kf']
            # 更新状态转移矩阵中的 dt
            kf.transitionMatrix[0,3] = kf.transitionMatrix[1,4] = kf.transitionMatrix[2,5] = dt
            pred = kf.predict()
            
            best_dist, best_idx = 1.2, -1 # 1.2米匹配阈值
            for i, det in enumerate(detections):
                if i in used_idx: continue
                dist = np.linalg.norm(det - pred[:3, 0])
                if dist < best_dist:
                    best_dist, best_idx = dist, i
            
            if best_idx != -1:
                kf.correct(detections[best_idx].reshape(3,1))
                b_data['last_seen'] = now
                used_idx.append(best_idx)
            elif now - b_data['last_seen'] > self.max_lost_time:
                del self.balls[b_id] # 彻底丢失

        # 录入新目标
        for i, det in enumerate(detections):
            if i not in used_idx:
                self.balls[self.next_id] = {'kf': self.create_kf(det), 'last_seen': now}
                self.next_id += 1

        # --- 3. 结果计算与数值安全拦截 ---
        msg_pos, msg_pre = PoseArray(), PoseArray()
        msg_pos.header = msg_pre.header = color_msg.header

        for b_id, b_data in self.balls.items():
            s = b_data['kf'].statePost
            x, y, z = s[0,0], s[1,0], s[2,0]
            vy = s[4,0]

            # [安全阀] 拦截 NaN 或 零深度，防止 int() 转换崩溃
            if not np.isfinite([x, y, z]).all() or z < 0.1:
                continue

            # 发布当前 Pose
            p = Pose()
            p.position.x, p.position.y, p.position.z = float(x), float(y), float(z)
            msg_pos.poses.append(p)

            # 落地预测 (仅针对飞向己方的球: vy < -0.2)
            impact = self.get_prediction(s)
            if impact and vy < -0.2:
                ip = Pose()
                ip.position.x, ip.position.y, ip.position.z = impact
                msg_pre.poses.append(ip)
                # UI投影预测落点（显示在画面底部）
                ix_u = int(np.clip(impact[0]*self.fx/z + self.cx, 0, w-1)) 
                cv2.drawMarker(img, (ix_u, h-50), (0, 255, 255), cv2.MARKER_TILTED_CROSS, 25, 3)

            # 投影回像素坐标进行可视化
            u = int(np.clip(x * self.fx / z + self.cx, 0, w-1))
            v = int(np.clip(y * self.fy / z + self.cy, 0, h-1))
            
            # 根据坐标判断半场 (绿色: 己方, 红色: 对方)
            color = (0, 255, 0) if y < self.COURT_HALF_LENGTH else (0, 0, 255)
            cv2.circle(img, (u, v), 18, color, 3)
            cv2.putText(img, f"ID:{b_id} Z:{z:.1f}m", (u+15, v-15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        self.pos_pub.publish(msg_pos)
        self.pred_pub.publish(msg_pre)
        
        cv2.imshow("Volleyball Tracker V4.0", img)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = VolleyballMasterTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()