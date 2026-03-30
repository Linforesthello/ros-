#!/usr/bin/env python3
import serial
import curses
import time
import glob

# 串口设置
BAUD_RATE = 115200

def select_port():
    ports = sorted(glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*'))
    if not ports:
        print("未找到可用串口，使用默认 /dev/ttyACM0")
        return '/dev/ttyACM0'
    print("可用串口：")
    for i, p in enumerate(ports):
        print(f"  {i}: {p}")
    while True:
        try:
            idx = int(input(f"请输入串口编号 (0-{len(ports)-1}): "))
            if 0 <= idx < len(ports):
                return ports[idx]
        except ValueError:
            pass
        print("输入无效，请重试")

SERIAL_PORT = select_port()
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print(f"已连接: {SERIAL_PORT}")

def send_command(command_str):
    """通过串口发送命令（命令是十六进制字节流）"""
    command_bytes = bytes.fromhex(command_str.replace(' ', ''))  # 转换为字节流
    ser.write(command_bytes)

def main(stdscr):
    """主程序，处理键盘输入控制"""
    curses.curs_set(0)  # 隐藏光标
    stdscr.nodelay(1)   # 设置为非阻塞模式
    stdscr.timeout(100)  # 设置输入超时

    # 存储每个按键对应的十六进制命令
    commands = {
      #   ord('w'): 'AA 01 24 01 00 00 02 11 55',  # 前进
        ord('s'): 'AA 01 01 01 00 00 02 11 00',  # 全体停止
        ord('z'): 'AA 01 02 01 00 00 02 11 00',  # 转向停
        ord('x'): 'AA 01 03 01 00 00 02 11 00',  # 动力停
      #   方向
        ord('f'): 'AA 01 23 01 00 00 02 11 55',  # 左转
        ord('g'): 'AA 01 23 01 00 00 02 11 00',  # 左转停止
        ord('j'): 'AA 01 25 01 00 00 02 11 55',  # 右后电机向前
        ord('h'): 'AA 01 25 01 00 00 02 11 00',  # 右后电机停
      #   动力
        ord('c'): 'AA 01 24 01 00 00 02 11 55',  # 左前电机向前
        ord('v'): 'AA 01 24 01 00 00 02 11 00',  # 左前电机停
        ord('n'): 'AA 01 26 01 00 00 02 11 55',  # 右前电机向前
        ord('b'): 'AA 01 26 01 00 00 02 11 00',  # 右前电机停
        
    }

    pressed_keys = set()  # 记录当前被按下的键
    last_time = time.time()  # 记录时间，用来控制发送频率

    while True:
        key = stdscr.getch()  # 获取按键
        current_time = time.time()

        if key == ord('q'):  # 按 'q' 退出程序
            break
        elif key in commands:
            if key not in pressed_keys:
                pressed_keys.add(key)  # 添加到按下的键集合
                send_command(commands[key])  # 发送命令

        # 模拟连续发送命令流
        if pressed_keys:
            if current_time - last_time >= 0.1:  # 每100ms发送一次
                for key in pressed_keys:
                    send_command(commands[key])  # 连续发送命令流
                last_time = current_time  # 更新时间戳

        # 清空已经释放的按键
        for key in list(pressed_keys):
            if stdscr.getch() == -1:  # 如果该键已经松开，移除它
                pressed_keys.remove(key)

if __name__ == "__main__":
    curses.wrapper(main)