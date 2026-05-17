# Fix2 计划: motor_control.py 健壮性修复

## 背景

基于对 `control/motor_control.py` 的代码审查以及 `control/doc/fix_comparison/fix1.md` 历史修复记录，Fix1 解决了行缓冲粘包问题，但程序仍存在多个健壮性问题：串口资源未释放、TX/RX 并发无保护、异常处理缺失等。

## 问题清单与修复方案

| 优先级 | 问题 | 修复方案 |
|--------|------|----------|
| P0 | 程序退出不关闭串口，端口被占用 | `finally` 中添加 `ser.close()` |
| P0 | TX/RX 共用 serial 对象无互斥，并发可能导致数据错乱 | 用同一把 `threading.Lock` 保护所有 `ser.read/write` 调用 |
| P1 | `send_command` 无异常处理，非法 hex 或串口断线会崩溃 | 加 try/except，异常写入日志而非崩溃 |
| P1 | RX 线程 `log_lines.append` 不加锁，与 `send_command` 中加锁的 append 存在竞态 | 统一在锁保护下追加日志 |
| P2 | RX 线程断线后静默退出，主线程仍在发命令 | 检测到 SerialException 后通知主线程停止 |
| P2 | 模块级代码 (select_port + serial.Serial) 在 import 时立即执行 | 移到 `main()` 或 `if __name__` 作用域内 |

## 涉及文件

- `control/motor_control.py` — 所有改动集中于此文件

## 详细改动

### 1. ~~模块级代码延迟执行~~ ❌ 未实施

将全局的 `SERIAL_PORT` 赋值和 `ser = serial.Serial(...)` 移到 `main()` 函数中，通过参数传递给子函数。

**改动方式**:
- 删除模块级的 `SERIAL_PORT = select_port()` 和 `ser = serial.Serial(...)` 
- `main()` 改为先选端口再打开串口，将 `ser` 作为参数传递给子线程和命令函数
- `send_command` 和 `rx_reader` 增加 `ser` 参数

> **未采用原因**：用户保留模块级代码，避免改变程序结构。

### 2. 串口访问加锁 + 退出关闭

**改动方式**:
- 引入 `serial_lock = threading.Lock()`，所有 `ser.read()` / `ser.in_waiting` / `ser.write()` 都在锁保护下执行
- `finally` 中添加 `ser.close()`

### 3. TX/RX 统一的串口锁

```python
# rx_reader 中
with serial_lock:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)

# send_command 中
with serial_lock:
    ser.write(command_bytes)
```

### 4. `send_command` 异常保护

```python
def send_command(ser, command_str, ...):
    try:
        command_bytes = bytes.fromhex(command_str.replace(' ', ''))
        with serial_lock:
            ser.write(command_bytes)
    except (ValueError, serial.SerialException) as e:
        with lock:
            log_lines.append(f"[{timestamp}] ERR: {e}")
        refresh_log(...)
        return
```

### 5. 统一日志追加锁保护

`rx_reader` 中 `log_lines.append` 和 `refresh_log` 都放到 `with lock:` 内：

```python
with lock:
    log_lines.append(...)
    refresh_log(...)
```

### 6. 断线检测

- `rx_reader` 捕获 `SerialException` 时，写入错误日志后退出
- `send_command` 捕获 `SerialException` 时写入错误日志
- 暂不加重连逻辑，先保证安全退出，待实际测试后迭代

## 验证方法

1. 程序启动能正常选择串口、建立连接
2. 按键发送命令，日志窗口显示 TX 和 RX 数据
3. 拔掉串线缆，程序不崩溃（写操作被 try 保护）
4. `q` 退出后，端口已被释放（可重新连接）
5. 长时间运行，日志不出现截断错位（Fix1 回归验证）

## 不在此次修复范围

- 命令十六进制字符串抽象化/宏定义（可读性改进，非必要）
- 串口自动重连（先安全退出，后续按需迭代）

## 改动记录

| 日期 | 版本 | 类别 | 说明 |
|------|------|------|------|
| 2026-05-17 | Fix2 | 串口锁 | 新增全局 `serial_lock`，保护 TX/RX 线程对 `ser` 的并发访问 |
| 2026-05-17 | Fix2 | 异常保护 | `send_command` 加 try/except，捕获 `ValueError`(hex) 和 `SerialException`(断线)，写入日志不崩溃 |
| 2026-05-17 | Fix2 | 日志加锁 | `rx_reader` 中 `log_lines.append` 和 `refresh_log` 统一在 `lock` 保护下，消除与 `send_command` 的竞态 |
| 2026-05-17 | Fix2 | 断线检测 | `rx_reader` 捕获 `SerialException` 时写入错误日志再退出，不再静默消失 |
| 2026-05-17 | Fix2 | 资源释放 | `finally` 中添加 `ser.close()`，退出后释放串口端口 |
| 2026-05-17 | Fix2 | 锁死锁修复 | 发现 `refresh_log` 在 `with lock:` 内部被调用而自身也获取同一 `Lock`(不可重入)，导致死锁。修复：`refresh_log` 移到 `with lock:` 外部 |
| 2026-05-17 | Fix2 | 响应延迟修复 | 发现 `rx_reader` 中 `time.sleep(0.05)` 在 `serial_lock` 内部执行，空等时持有锁 50ms，阻塞主线程发命令。修复：无数据时先释放锁再 sleep |
| 2026-05-17 | Fix2 | 自动发送 | 新增 `r` 键切换 50ms 间隔重复发送上次命令，`timeout(100)` → `timeout(10)` 提供精度。按其他命令键切换发送内容，继续自动发送 |

### 修复过程 Bug 记录

| Bug | 症状 | 根因 | 修复 |
|-----|------|------|------|
| 日志锁死锁 | TX/RX 日志不显示 | `threading.Lock` 不可重入：`refresh_log` 在 `with lock:` 内被调用 | `refresh_log()` 移到 `with lock:` 块外 |
| 按键响应极慢 | 按键后延迟 ~50ms 才响应，`q` 退不出 | `rx_reader` 在 `serial_lock` 内 sleep(50ms)，阻塞主线程 `send_command` | 先释放 `serial_lock`，再到锁外 sleep |
