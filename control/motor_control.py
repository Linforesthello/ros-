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

def send_command(command_str, log_lines, log_win):
    """通过串口发送命令（命令是十六进制字节流），并在日志窗口显示"""
    command_bytes = bytes.fromhex(command_str.replace(' ', ''))  # 转换为字节流
    ser.write(command_bytes)

    # 记录发送日志
    timestamp = time.strftime('%H:%M:%S')
    log_lines.append(f"[{timestamp}] TX: {command_str.upper()}")

    # 刷新日志窗口
    log_win.erase()
    h, w = log_win.getmaxyx()
    visible = log_lines[-(h - 2):]  # 只显示最新的几行
    for i, line in enumerate(visible):
        try:
            log_win.addstr(i, 0, line[:w - 1])
        except curses.error:
            pass
    log_win.refresh()

def main(stdscr):
    """主程序，处理键盘输入控制"""
    curses.curs_set(0)  # 隐藏光标
    stdscr.nodelay(1)   # 设置为非阻塞模式
    stdscr.timeout(100)  # 设置输入超时

    # 存储每个按键对应的十六进制命令
    # 命令结构: AA 01 <ID> 01 00 00 02 11 <DATA>
    # DATA: 55 (开), 00 (关)
    commands = {
        # --- 全局命令 ---
        # 0x101: 全体停止
        ord('s'): 'AA 01 01 01 00 00 02 11 00',  # 全体停止
        # 0x102: 转向电机控制
        ord('a'): 'AA 01 02 01 00 00 02 11 55',  # 转向全体前进
        ord('z'): 'AA 01 02 01 00 00 02 11 00',  # 转向全体停
        # 0x103: 动力电机控制
        ord('d'): 'AA 01 03 01 00 00 02 11 55',  # 动力全体前进
        ord('x'): 'AA 01 03 01 00 00 02 11 00',  # 动力全体停

        # --- 转向控制 (方向) ---
        # 0x123: 左前方向
        ord('f'): 'AA 01 23 01 00 00 02 11 55',  # 左前轮-左转
        ord('g'): 'AA 01 23 01 00 00 02 11 00',  # 左前轮-方向停
        # 0x125: 右后方向
        ord('j'): 'AA 01 25 01 00 00 02 11 55',  # 右后轮-方向控制
        ord('h'): 'AA 01 25 01 00 00 02 11 00',  # 右后轮-方向停
        # (缺少: 左后、右前转向控制)

        # --- 动力控制 ---
        # 0x124: 左前动力
        ord('c'): 'AA 01 24 01 00 00 02 11 55',  # 左前轮-前进
        ord('v'): 'AA 01 24 01 00 00 02 11 00',  # 左前轮-动力停
        # 0x126: 右后动力
        ord('n'): 'AA 01 26 01 00 00 02 11 55',  # 右后轮-前进
        ord('b'): 'AA 01 26 01 00 00 02 11 00',  # 右后轮-动力停
        # (缺少: 左后、右前动力控制)
    }

    # 按键说明文字
    help_text = [
        "=== 电机控制 | 按 q 退出 ===",
        " s: 全体停止    a/z: 转向前进/停    d/x: 动力前进/停",
        " f/g: 左前转向  j/h: 右后转向",
        " c/v: 左前动力  n/b: 右后动力",
        "-" * 50,
        "  发送日志:",
    ]

    total_rows, total_cols = stdscr.getmaxyx()
    help_rows = len(help_text)

    # 绘制顶部说明区
    for i, line in enumerate(help_text):
        try:
            stdscr.addstr(i, 0, line[:total_cols - 1])
        except curses.error:
            pass
    stdscr.refresh()

    # 创建日志子窗口（剩余区域）
    log_rows = total_rows - help_rows
    log_win = curses.newwin(log_rows, total_cols, help_rows, 0)
    log_lines = []

    while True:
        key = stdscr.getch()  # 获取按键, 由于 stdscr.timeout(100) 此处为非阻塞，超时返回-1

        if key == ord('q'):  # 按 'q' 退出程序
            break

        # 当检测到有效按键时，发送一次对应命令
        # 这种模式适用于发送"开始"和"停止"类型的指令
        # 如果按住一个键，系统会自动重复发送该键，从而实现连续控制
        if key in commands:
            send_command(commands[key], log_lines, log_win)

if __name__ == "__main__":
    curses.wrapper(main)
