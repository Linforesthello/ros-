#!/usr/bin/env python3
import cv2
import numpy as np

def main():
    # 初始化摄像头
    # 注意：Astra Pro 在 Linux 下可能有多个 video 节点。
    # 如果 0 打不开或不是彩色画面，请尝试修改为 1, 2 等。
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("错误：无法打开摄像头。请检查连接或设备索引。")
        return

    print("开始运行... 按 'q' 键退出程序。")

    while True:
        # 1. 读取帧
        ret, frame = cap.read()
        if not ret:
            print("无法接收帧，退出...")
            break

        # 2. 预处理：高斯模糊（减少图像噪点，使轮廓更平滑）
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        
        # 3. 转换颜色空间：BGR -> HSV
        # HSV 空间比 RGB 更容易分离颜色
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # 4. 定义红色的 HSV 阈值范围
        # 红色在 HSV 色相环(0-180)的两端，所以需要定义两个范围并合并
        
        # 范围 1 (0-10)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        
        # 范围 2 (170-180)
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        # 创建掩膜 (Mask)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)  # 合并两个红色区间的掩膜

        # 5. 形态学操作：腐蚀与膨胀（去除背景中的小白点噪嘴）
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 6. 寻找轮廓
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        center = None

        # 如果找到了轮廓
        if len(contours) > 0:
            # 找到面积最大的轮廓（假设最大的红色块是球）
            c = max(contours, key=cv2.contourArea)
            
            # 计算最小外接圆
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            
            # 计算质心 (Centroid) 用来做中心点
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # 只有当半径大于一定像素时才认为是有效的球体
                if radius > 10:
                    # 在原图上画出圆圈和中心点
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    
                    # 打印像素坐标
                    print(f"[识别结果] 中心坐标: ({int(x)}, {int(y)}) | 半径: {radius:.1f}")

        # 显示处理后的图像
        cv2.imshow("Ball Detection", frame)
        # 可选：显示二值化掩膜查看效果
        # cv2.imshow("Mask", mask)

        # 按 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
