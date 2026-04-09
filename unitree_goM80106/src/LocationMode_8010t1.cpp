#include <unistd.h>
#include <cmath>
#include "serialPort/SerialPort.h"
#include "unitreeMotor/unitreeMotor.h"

int main() {

  SerialPort  serial("/dev/ttyACM0");
  MotorCmd    cmd;
  MotorData   data;

  const float gearRatio  = -6.33*queryGearRatio(MotorType::GO_M8010_6);
  const float targetPos  = 20.0f * gearRatio;  // 输出端 3.14 rad -> 电机轴
  const float stepSize   = 0.15f;             // 每次最大步进（rad，电机轴），安全缓变

  // 先读一次当前位置，避免启动时从 0 出发导致突然反转
  cmd.motorType = MotorType::GO_M8010_6;
  data.motorType = MotorType::GO_M8010_6;
  cmd.mode = queryMotorMode(MotorType::GO_M8010_6, MotorMode::FOC);
  cmd.id = 0; cmd.kp = 0; cmd.kd = 0; cmd.q = 0; cmd.dq = 0; cmd.tau = 0;
  serial.sendRecv(&cmd, &data);
  float cmdPos = data.q;  // 从实际位置出发

  while(true)
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

    usleep(200);  // 200ms 周期，配合缓变步进
  }

}