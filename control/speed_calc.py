#!/usr/bin/env python3
"""速度-十六进制 快速转换工具
   有符号8位: 0x00~0x7F → 0~127 (正), 0x80~0xFF → -128~-1 (负)
"""

def speed_to_hex(speed):
    return f"0x{speed & 0xFF:02X}"

def hex_to_speed(hex_str):
    val = int(hex_str.strip(), 16)
    return val if val <= 127 else val - 256

def main():
    print("速度 ↔ 十六进制转换 (q 退出)")
    while True:
        inp = input("输入 (十进制速度 或 0xXX): ").strip()
        if inp.lower() == 'q':
            break
        if inp.startswith("0x") or inp.startswith("0X"):
            h = inp[2:]
            print(f"  {hex_to_speed(h)}")
        else:
            try:
                s = int(inp)
                print(f"  {speed_to_hex(s)}")
            except ValueError:
                print("  无效输入")

if __name__ == "__main__":
    main()
