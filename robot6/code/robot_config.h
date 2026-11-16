// robot_config.h - settings shared by ALL programs.
// Change things ONLY here. Run 01_port_check first to see your ports.

// Robot 6: the motor cables are in ports A and B (C is empty)
#define LEFT   OUT_B      // left wheel motor
#define RIGHT  OUT_A      // right wheel motor
#define BOTH   OUT_AB     // both wheels
#define DIR    -1         // -1: our motors are mounted backwards (+1 for a normal robot)

#define COLOR  IN_3       // color sensor, looking down at the floor
#define SONAR  IN_4       // ultrasonic sensor, looking forward

#define WHEEL_D     2.8   // cm moved per motor turn / pi. Measured: 50 cm asked -> 25 cm driven (gears), so 5.6 * 25 / 50
#define TURN_FACTOR 4.2   // motor degrees per 1 degree of robot turn. Measured: 360 asked -> 180 turned, so 2.1 * 2

// --- small helpers used by most programs ---
long CmToDeg(float cm)
{
  return cm * 360 / (3.1416 * WHEEL_D);
}

float DegToCm(long deg)
{
  return deg * 3.1416 * WHEEL_D / 360;
}

void Move(float cm)                     // forward (negative = back)
{
  RotateMotorEx(BOTH, 45, CmToDeg(cm) * DIR, 0, true, true);
}

void TurnRight(int angle)
{
  RotateMotorEx(BOTH, 35, angle * TURN_FACTOR * DIR, 100, true, true);
}

void TurnLeft(int angle)
{
  RotateMotorEx(BOTH, 35, angle * TURN_FACTOR * DIR, -100, true, true);
}

void Forward(int power)                // drive forward until Off(BOTH)
{
  OnFwdReg(BOTH, power * DIR, OUT_REGMODE_SYNC);
}

long Travel(long startDeg)             // motor degrees driven forward since startDeg
{
  return (MotorRotationCount(LEFT) - startDeg) * DIR;
}

void WaitEnter()
{
  until(ButtonPressed(BTNCENTER, false));
  until(!ButtonPressed(BTNCENTER, false));
  Wait(200);
}
