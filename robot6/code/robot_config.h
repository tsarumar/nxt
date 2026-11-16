// robot_config.h - settings shared by ALL programs.
// Change things ONLY here. Run 01_port_check first to see your ports.

// Robot 6: the motor cables are in ports A and C (B is empty)
#define LEFT   OUT_C      // left wheel motor   (swap A and C if 01_port_check shows the opposite)
#define RIGHT  OUT_A      // right wheel motor
#define BOTH   OUT_AC     // both wheels

#define COLOR  IN_3       // color sensor, looking down at the floor
#define SONAR  IN_4       // ultrasonic sensor, looking forward

#define WHEEL_D     5.6   // wheel diameter in cm   (fix with 00_calibrate)
#define TURN_FACTOR 2.1   // motor degrees per 1 degree of robot turn (fix with 00_calibrate)

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
  RotateMotorEx(BOTH, 45, CmToDeg(cm), 0, true, true);
}

void TurnRight(int angle)
{
  RotateMotorEx(BOTH, 35, angle * TURN_FACTOR, 100, true, true);
}

void TurnLeft(int angle)
{
  RotateMotorEx(BOTH, 35, angle * TURN_FACTOR, -100, true, true);
}

void WaitEnter()
{
  until(ButtonPressed(BTNCENTER, false));
  until(!ButtonPressed(BTNCENTER, false));
  Wait(200);
}
