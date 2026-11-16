# Robot 6 - NXT programs and reports

Omar Zid, Simão Nambi - Informatics in Robotics

## How to use on the lab computer

1. Download this repo (green **Code** button > **Download ZIP**) and unzip it.
2. Open `robot6/code/01_port_check.nxc` in BricxCC.
3. F5 = compile, F6 = download to the robot, F7 = run.
4. Keep `robot_config.h` in the same folder as the programs. Ports and wheel settings are changed only there.

## Programs (run them one at a time, in this order)

Names are short on purpose: the NXT only accepts names up to 15 characters.

| File | Task |
|---|---|
| 01_port_check | check which port has which sensor/motor |
| 02_calibrate | 50 cm drive + full turn, to set WHEEL_D and TURN_FACTOR |
| 03_basics | intro: buttons, sensors, 2 tasks, mutex, file |
| 04_scanner360 | intro final task: 360 scan, file, screen map, go to free side, stop on red |
| 05_motors | Report 1 extra motor test (optional) |
| 06_sonar | Report 2: ultrasonic speed, accuracy, field of view |
| 07_color | Report 2: color sensor speed, colours, intensity, height |
| 08_ring | Project 1 |
| 09_bars + 09b_receiver | Project 2 (09b goes on the other robot) |
| 10_obstacles | Project 3 |
| 11_line_pid | Project 4 |

Reports are in `reports/`. Report 1 was done separately.
