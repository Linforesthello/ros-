#include <unistd.h>
#include <cmath>
#include "serialPort/SerialPort.h"
#include "unitreeMotor/unitreeMotor.h"

#include <csignal>
#include <iostream>

static volatile sig_atomic_t running = 1;

void signalHandler(int) {
  running = 0;
}


int main() {

  SerialPort  serial("/dev/ttyACM1");
  MotorCmd    cmd;
  MotorData   data;

  std::signal(SIGINT, signalHandler);

  const float gearRatio  = -6.33*queryGearRatio(MotorType::GO_M8010_6);
  const float targetPos  = 5.0f * gearRatio;  // 输出端 3.14 rad -> 电机轴
  const float stepSize   = 0.70f;             // 每次最大步进（rad，电机轴），安全缓变

  // 先读一次当前位置，避免启动时从 0 出发导致突然反转
  cmd.motorType = MotorType::GO_M8010_6;
  data.motorType = MotorType::GO_M8010_6;
  cmd.mode = queryMotorMode(MotorType::GO_M8010_6, MotorMode::FOC);
  cmd.id = 0; 
  cmd.kp = 0; 
  cmd.kd = 0; 
  cmd.q = 0; 
  cmd.dq = 0; 
  cmd.tau = 0;
  serial.sendRecv(&cmd, &data);
  float cmdPos = data.q;  // 从实际位置出发

  while(running)
  {
    // 缓慢逼近目标，避免瞬间大力矩
    if (std::fabs(targetPos - cmdPos) > stepSize)
      cmdPos += (targetPos > cmdPos) ? stepSize : -stepSize;
    else
      cmdPos = targetPos;

    cmd.motorType = MotorType::GO_M8010_6;
    data.motorType = MotorType::GO_M8010_6;
    cmd.mode = queryMotorMode(MotorType::GO_M8010_6,MotorMode::FOC);
    cmd.id   = 0;
    cmd.kp   = 0.15;
    cmd.kd   = 0.1;
    cmd.q    = cmdPos;  
    cmd.dq   = 0.0;
    cmd.tau  = 0.0;
    serial.sendRecv(&cmd, &data);

    std::cout <<  std::endl;
    std::cout << "motor.q: "      << data.q      << std::endl;
    std::cout << "motor.temp: "   << data.temp   << std::endl;
    std::cout << "motor.dq: "     << data.dq     << std::endl;
    std::cout << "motor.merror: " << data.merror << std::endl;
    std::cout <<  std::endl;

    usleep(200);
  }

  // 第1步：渐进撤力（保持位置目标不变，逐步降低 kp，加大 kd 吸收动能）
  for (int i = 0; i < 100; i++) {
    float t = (100 - i) / 100.0f;       // 1.0 → 0.0
    cmd.kp = 0.15f * t;                 // 位置刚度递减
    cmd.kd = 0.1f * (2.0f - t);         // 阻尼递增：0.1 → 0.2
    cmd.q = cmdPos;                     // 维持当前位置目标
    serial.sendRecv(&cmd, &data);
    usleep(200);
  }

  // 第2步：力矩已接近 0，切换到停止模式
  cmd.mode = 0;
  cmd.dq  = 0.0f;
  cmd.q   = 0.0f;
  cmd.tau = 0.0f;
  cmd.kp  = 0.0f;
  cmd.kd  = 0.0f;
  serial.sendRecv(&cmd, &data);

  return 0;
}