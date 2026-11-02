# NXC programs for Omar Zid

These are hardware source programs, separate from the executed Python simulations. They require an NXT 2.0 compatible firmware and an NBC/NXC compiler. Compilation and physical testing have not been verified here. The official downloadable compiler links returned HTML or could not be retrieved, so no `.rxe` file or successful compiler result is claimed.

## Files

| Program | Assignment | Output |
|---|---|---|
| 00_intro_scan.nxc | 360 degree environment scanner, polar LCD map, best corridor, red stop | Intro.txt |
| 00a_intro_io_parallel.nxc | Introductory buttons, motors, sensors, parallel tasks and mutex | IntroIO.txt |
| 01_motor_measurements.nxc | Signed shaft rotation, tacho/rotation display and resets | Motor.txt |
| 02_sensor_measurements.nxc | Sonar range/timing/angular sweep, full/raw color and red LED intensity | Sensors.txt |
| 03_project1_clean_ring.nxc | Search, push, boundary stop, retreat, empty scans and ejection estimate map | Ring.txt |
| 04_project2_barcode.nxc | Hysteresis/debounced bar count, grouped display, time, append and radio sum | Scanner.txt |
| 04b_barcode_receiver.nxc | Second-brick count receiver with acknowledgement | LCD |
| 05_project3_obstacle_navigation.nxc | Configurable N cm endpoint with range-probed detours | Navigate.txt |
| 06_project4_pid_line.nxc | One-sensor PID with calibration, anti-windup, velocity feedback and lap marker | Line.txt |
| common_config.nxc | Shared dimensions, odometry, file handling and bounded motion | Include only |

## Build and start

Keep each program and `common_config.nxc` in the same folder. Open one program in BricxCC and select an NXT 2.0 target. Compile the source before downloading it. A typical command-line invocation, once the official compiler is installed, is:

```text
nbc.exe -v=128 00_intro_scan.nxc -O=00_intro_scan.rxe
```

Do not download `common_config.nxc` by itself. Repeat compilation for the individual task files. Verify the compiler accepts the firmware setting used by your installation.

Default wiring: B left wheel, C right wheel, S1 downward color sensor, S4 forward ultrasonic sensor. A positive wheel command must move the chassis forward; reverse polarity/configuration if your build differs. Press ENTER when the program asks to start; EXIT requests a stop. Test while the chassis is lifted first. Fault messages stop motion on stalls, timeouts, invalid readings or file errors. File allocations are finite; clear/export old logs using BricxCC when full. BricxCC Tools > NXT Screen with polling can show the LCD remotely; its file tools can inspect program/data files and free storage.

## Per-assignment setup

- Introduction: use a red floor strip and a clear initial scan area. The NXC source stops at the first red observation and verifies a second while stopped. The report model conservatively includes sensor delay and braking while moving, so its stop distance is not a prediction of this exact source execution.
- Motor report: lift wheels; motor B is the tested shaft and C remains stopped. The source includes positive and negative 45, 450 and 650 degree commands. Add physical repeat trials and independently observe shaft position; a tacho display alone does not prove absolute physical accuracy. The report's independent angle/encoder comparison is simulated.
- Sensors: follow prompts for target distances, a 500 mm angular-test target and labeled surfaces. The reported API duration has millisecond tick granularity and is distinct from sensor update/response latency. Echo flight time is calculated using 343 m/s, not measured by the API. Repeat acquisition under measured lighting and standoff conditions for a physical version of the extended report.
- Ring: assumed outer radius 600 mm, black inner edge 580 mm, chassis radius 75 mm, pusher and color sensor 150 mm forward, object radius 20 mm and clear central staging area. The pusher reaches the boundary with zero tolerance in the ideal geometry. The map is an odometry/contact estimate. Empty sonar scans are conditional on detectable objects, beam coverage and no hidden objects. The NXC source uses repeated empty scans and tighter acquisition checks than the ideal simulation.
- Scanner: measure a 300 mm scan travel that starts and ends on white. Pass the sensor through all bar heights. Calibrate the assumed reflectance thresholds 35 and 65 and power-to-speed relation; the 60 mm/s numerical speed is not established by setting a motor power. Pair the receiver as Bluetooth slave and the sender as master connection 1 before starting. Mailbox 1 carries the sum and mailbox 2 acknowledges it. Retries replace the displayed sum rather than adding it repeatedly.
- Navigation: use LEFT/RIGHT to change N by 10 cm, then ENTER. N is forward displacement, not total detour length. The model assumes isolated convex rectangles with open floor for a detour. Odometry depends on measured wheel/track dimensions and slip. A timeout indicates failure to find a route.
- Line follower: mount one sensor 35 mm ahead, calibrate black then white, and use a single broad transverse start/finish marker. The controller arms lap detection after 1500 mm of encoder travel; this is a configured track assumption, not a universal lap detector. Verify the steering sign on the chosen edge. The Python experiment uses calibrated black 20/white 80, 110 mm/s speed and a circular track with a unique marker. Source wheel-speed feedback and physical motor calibration differ from the numerical wheel model; its gains are a starting point.

## API references

- Supplied `__NXC_tutorial.pdf`: tasks, mutexes, sensors, files and Bluetooth.
- Supplied `_NXC_min.pdf`: introductory BricxCC/NXC reference.
- [Official NXC API](https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/index.html)
- [Official NXC definitions and signatures](https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/_n_x_c_defs_8h.html)
- [Official NBC/NXC releases](https://bricxcc.sourceforge.net/nbc/release/index.html)

Source review confirms one main task per program, balanced syntax delimiters, shared include availability and the declared sensor/motor wiring. This is source review, not a replacement for a compiler or hardware test.
