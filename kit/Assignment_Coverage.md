# Assignment coverage for Omar Zid

| Supplied task | Report and implementation | Evidence |
|---|---|---|
| Introduction: basic I/O, concurrent tasks, mutex, logging | Introduction evidence report; 00a_intro_io_parallel.nxc | Button/motor/sensor and shared-state code; setup instructions |
| Introduction: 360 degree scan, file, screen, most free heading, red stop | Introduction report; 00_intro_scan.nxc | 108 observations, polar map, selected 30 degree heading and red-stop event trace |
| Report 1: shaft position, requested angles, resets | Report 1; 01_motor_measurements.nxc | 60 simulated repeat trials, calibration, reference angle, uncertainty, time and reset trace |
| Report 2: sonar speed, accuracy and field of view | Report 2; 02_sensor_measurements.nxc | Distance and angular trials, latency/update/response separation, calibration and uncertainty |
| Report 2: color, lighting, resolution and a further sensor | Report 2; 02_sensor_measurements.nxc | 270 color trials, normalized/raw channels, classification failures and gyro bias/integration example |
| Project 1: expel objects, retain robot, stop when clean, map | Project 1; 03_project1_clean_ring.nxc | Nominal, dense and empty ring traces; geometric margins; ejection CSV and LCD-style map |
| Project 2: count variable groups, screen, append Scanner.txt, send sum | Project 2; 04_project2_barcode.nxc and 04b_barcode_receiver.nxc | 150 speed/noise trials, append records and explicitly emulated send/receive payload |
| Project 3: configurable N, unknown rectangles, near original line | Project 3; 05_project3_obstacle_navigation.nxc | Three scene traces, sensed-corner model, goal displacement, route length and body clearance |
| Project 4: one color sensor, PID, one lap | Project 4; 06_project4_pid_line.nxc | P/PI/PID traces, gain units, anti-windup, disturbance recovery and independently checked full lap |
| Basis of kinematics tasks 1 to 4 | Kinematics solutions; simulation/kinematics.py | Worked rotations/translations with units and inverse checks |
| Direct kinematics missing axes and transforms | Kinematics solutions; simulation/kinematics.py | Reconstructed right-handed axes and numeric visible-frame transforms; B and D formulas are symbolic because those frames are absent |

The computational evidence is simulated. The NXC sources are hardware implementations that still require compilation, calibration and physical testing. Python models do not execute the NXC code. BricxCC installation, an actual NXT screen, brick memory access and physical Bluetooth are described or emulated rather than claimed as observed device operations.
