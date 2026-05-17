#!/usr/bin/env python3
import serial
import curses
import time
import glob
import threading
import io

# 串口设置
BAUD_RATE = 115200

# 时序配置（统一管理）
MAIN_LOOP_TIMEOUT_MS = 10   # 主循环 getch() 超时(毫秒)
RX_POLL_INTERVAL = 0.01     # RX 线程轮询间隔(秒)
AUTO_REPEAT_INTERVAL = 0.01 # 自动发送间隔(秒)

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
serial_lock = threading.Lock()
print(f"已连接: {SERIAL_PORT}")

def refresh_log(log_lines, log_win, lock):
    """刷新日志子窗口（线程安全）"""
    with lock:
        log_win.erase()
        h, w = log_win.getmaxyx()
        visible = log_lines[-(h - 2):]
        for i, line in enumerate(visible):
            try:
                log_win.addstr(i, 0, line[:w - 1])
            except curses.error:
                pass
        log_win.refresh()

def send_command(command_str, log_lines, log_win, lock):
    """通过串口发送命令（命令是十六进制字节流），并在日志窗口显示"""
    timestamp = time.strftime('%H:%M:%S')
    try:
        command_bytes = bytes.fromhex(command_str.replace(' ', ''))
        with serial_lock:
            ser.write(command_bytes)
    except (ValueError, serial.SerialException) as e:
        with lock:
            log_lines.append(f"[{timestamp}] ERR: {e}")
        refresh_log(log_lines, log_win, lock)
        return

    with lock:
        log_lines.append(f"[{timestamp}] TX: {command_str.upper()}")
    refresh_log(log_lines, log_win, lock)

def rx_reader(log_lines, log_win, lock, stop_event):
    """后台线程：持续读取串口回调数据并显示到日志窗口（行缓冲，避免粘包错位）"""
    buf = io.BytesIO()
    while not stop_event.is_set():
        try:
            data = b''
            with serial_lock:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
            if not data:
                time.sleep(RX_POLL_INTERVAL)
                continue
            buf.write(data)
            buf.seek(0)
            content = buf.read()
            lines = content.split(b'\n')
            buf.seek(0)
            buf.truncate()
            buf.write(lines[-1])   # 不完整行存回
            for line in lines[:-1]:
                text = line.decode('ascii', errors='replace').strip()
                if text:
                    timestamp = time.strftime('%H:%M:%S')
                    with lock:
                        log_lines.append(f"[{timestamp}] RX: {text}")
                    refresh_log(log_lines, log_win, lock)
        except serial.SerialException:
            timestamp = time.strftime('%H:%M:%S')
            with lock:
                log_lines.append(f"[{timestamp}] ERR: 串口断线，RX 线程退出")
            refresh_log(log_lines, log_win, lock)
            break
        time.sleep(RX_POLL_INTERVAL)

def main(stdscr):
    """主程序，处理键盘输入控制"""
    curses.curs_set(0)  # 隐藏光标
    stdscr.nodelay(1)   # 设置为非阻塞模式
    stdscr.timeout(MAIN_LOOP_TIMEOUT_MS)  # 主循环超时(ms)

    # 存储每个按键对应的十六进制命令
    # 命令结构: AA 01 <ID> 01 00 00 02 11 <DATA>
    # DATA: 4B (开), 00 (关)
    # 4B = 75 (十六进制)，表示前进/转动；00 表示停止
    
    # 正0x32->50,逆0xCE->50
    commands = {
        # --- 全局命令 ---
        # 0x101: 全体停止
        ord('s'): 'AA 01 01 01 00 00 02 11 00',  # 全体停止
        # 0x102: 转向电机控制
        ord('a'): 'AA 01 02 01 00 00 02 11 4B',  # 转向全体前进
        ord('z'): 'AA 01 02 01 00 00 02 11 00',  # 转向全体停
        # 0x103: 动力电机控制
        ord('d'): 'AA 01 03 01 00 00 02 11 32',  # 动力全体前进
        ord('e'): 'AA 01 03 01 00 00 02 11 00',  # 动力全体停

        # --- 转向控制 (方向) ---
        # 0x123: 左前方向
        ord('f'): 'AA 01 23 01 00 00 02 11 4B',  # 左前轮-左转
        ord('g'): 'AA 01 23 01 00 00 02 11 00',  # 左前轮-方向停
        ord('h'): 'AA 01 23 01 00 00 02 11 B5',  # 左前逆向
        # 0x125: 右后方向
        ord('j'): 'AA 01 25 01 00 00 02 11 4B',  # 右后轮-方向控制
        ord('k'): 'AA 01 25 01 00 00 02 11 00',  # 右后轮-方向停
        ord('l'): 'AA 01 25 01 00 00 02 11 B5',  # 右后轮-逆向

        # --- 动力控制 ---
        # 0x124: 左前动力
        ord('x'): 'AA 01 24 01 00 00 02 11 3C',  # 左前轮-前进
        ord('c'): 'AA 01 24 01 00 00 02 11 00',  # 左前轮-动力停
        ord('v'): 'AA 01 24 01 00 00 02 11 C4',  # 左前轮-逆向
        # 0x126: 右后动力
        ord('b'): 'AA 01 26 01 00 00 02 11 3C',  # 右后轮-前进
        ord('n'): 'AA 01 26 01 00 00 02 11 00',  # 右后轮-动力停
        ord('m'): 'AA 01 26 01 00 00 02 11 C4',  # 右后轮-逆向

        # 反馈测试
        ord('t'): 'AA 01 23 02 00 00 01 01',
        ord('y'): 'AA 01 24 02 00 00 01 01',
        ord('u'): 'AA 01 25 02 00 00 01 01',
        ord('i'): 'AA 01 26 02 00 00 01 01',

        # 调试日志开启/关闭指令
        ord('1'): 'AA 02 23 01 00 00 01 04',
        ord('2'): 'AA 02 23 01 00 00 01 05',
        ord('3'): 'AA 02 24 01 00 00 01 04',
        ord('4'): 'AA 02 24 01 00 00 01 05',
        ord('5'): 'AA 02 25 01 00 00 01 04',
        ord('6'): 'AA 02 25 01 00 00 01 05',
        ord('7'): 'AA 02 26 01 00 00 01 04',
        ord('8'): 'AA 02 26 01 00 00 01 05',
    }

    # 按键说明文字
    help_text = [
        "=== 电机控制 | 按 q 退出 ===",
        " s: 全体停止    a/z: 转向前进/停    d/e: 动力前进/停",
        " f/h: 左前转向  j/l: 右后转向",
        " c/v: 左前动力  b/m: 右后动力",
        " r: 自动发送(关闭)    (按 r 切换 重复发送)",
        "-" * 50,
        "  收发日志 (TX=发送 / RX=回调):",
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
    lock = threading.Lock()

    # 自动发送状态
    last_command = None          # 上次发送的命令
    auto_repeat_enabled = False  # 自动发送开关
    last_send_time = 0

    # 启动 RX 后台线程
    stop_event = threading.Event()
    rx_thread = threading.Thread(target=rx_reader, args=(log_lines, log_win, lock, stop_event), daemon=True)
    rx_thread.start()

    try:
        while True:
            key = stdscr.getch()  # 10ms 超时，非阻塞

            # 按 'q' 退出程序
            if key == ord('q'):
                break

            # 按 'r' 切换自动发送
            if key == ord('r'):
                auto_repeat_enabled = not auto_repeat_enabled
                interval_ms = int(AUTO_REPEAT_INTERVAL * 1000)
                help_text[4] = (f" r: 自动发送({'开启 ' + str(interval_ms) + 'ms' if auto_repeat_enabled else '关闭'})    "
                                f"(按 r 切换)")
                stdscr.addstr(4, 0, help_text[4][:total_cols - 1])
                stdscr.refresh()
                if auto_repeat_enabled:
                    last_send_time = 0  # 立即发送一次

            # 命令按键
            if key in commands:
                last_command = commands[key]
                send_command(last_command, log_lines, log_win, lock)
                last_send_time = time.time()

            # 自动发送逻辑：开启且有上次命令时，按间隔重复发送
            if auto_repeat_enabled and last_command:
                now = time.time()
                if now - last_send_time >= AUTO_REPEAT_INTERVAL:
                    send_command(last_command, log_lines, log_win, lock)
                    last_send_time = now
    finally:
        stop_event.set()
        rx_thread.join(timeout=1)
        ser.close()

if __name__ == "__main__":
    curses.wrapper(main)
