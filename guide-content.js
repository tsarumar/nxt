/* Omar Zid: one suggested study day, using the supplied robotics package.
   This file contains content only. The page owns navigation and note storage.
   360 study minutes + 70 break minutes = 09:00–16:10 suggested schedule.
   The day is a plan, not a promise of a grade or a finished physical robot. */
window.GUIDE_STEPS = [
  {
    id: 'start',
    title: '1. Open the work',
    minutes: 20,
    timeBlock: '09:00–09:20',
    goal: 'Find the demonstration, the reports and your notes. You do not need to code today.',
    actions: [
      'Open the demonstration link below in a new tab. Keep this guide open so you can return and write notes.',
      'Check that the name Omar Zid and eight assignment tabs appear. Open the complete PDF too.',
      'Remember these units: mm means millimeters, cm means centimeters, s means seconds, and ° means degrees of rotation. 10 mm = 1 cm.',
      'A simulation is a robot modeled on a computer. Play shows saved simulation results; it does not connect to a real robot.',
      'If you download the kit, extract the ZIP and keep the whole folder together. You can view the demonstration without installing Python.'
    ],
    links: [
      { label: 'Open the demonstration', href: 'kit/Start_Here.html#1' },
      { label: 'Open all reports together', href: 'kit/Omar_Zid_Complete_Robotics.pdf' },
      { label: 'Read the short original guide', href: 'kit/00_READ_ME_FIRST.txt' }
    ],
    checks: [
      { id: 'files-open', label: 'Open the demonstration and complete PDF.', expected: 'The eight tabs, pictures and PDF pages appear.' }
    ],
    explainPrompts: [
      'What is the difference between a saved simulation and a test on a real robot?'
    ],
    notePrompts: [
      'Which university computer and browser am I using?',
      'Which file or link did not open, if any? Write the exact name.'
    ]
  },
  {
    id: 'basics',
    title: '2. Learn the basic parts',
    minutes: 70,
    timeBlock: '09:20–10:30',
    goal: 'Study the introduction, then motors, then sensors. Learn what each part does before the projects.',
    actions: [
      'Spend about 15 minutes on Introduction scanner. Find the map, the chosen direction and the red stop. A scanner checks the space around the robot.',
      'Spend about 25 minutes on Report 1. A motor turns a shaft. A tacho count is the recorded rotation; resetting its zero does not physically move the shaft back.',
      'In the wheel calculator, keep diameter 56 mm and rotation 450°. Read the calculated travel. This assumes a directly driven wheel with no slipping.',
      'Spend about 30 minutes on Report 2. Sonar estimates distance; a color sensor reads light and color. Find one table and one graph.',
      'Notice that the time to call a sensor function is different from the time for a changed target to appear in its readings. These tabs have plots and reports, not Play buttons.'
    ],
    links: [
      { label: 'Introduction and wheel calculator', href: 'kit/Start_Here.html#1' },
      { label: 'Motor report', href: 'kit/reports/01_Report_1_Exploring_motors.pdf' },
      { label: 'Sensor report', href: 'kit/reports/02_Report_2_Exploring_sonar_and_color_sensors.pdf' },
      { label: 'Sensor plots and tables', href: 'kit/Start_Here.html#3' }
    ],
    checks: [
      { id: 'intro-result', label: 'Read the introduction results.', expected: 'Chosen direction 30°; final simulated travel 678.0 mm.' },
      { id: 'wheel-result', label: 'Check the calculator at 56 mm and 450°.', expected: 'Calculated signed wheel travel: 219.91 mm.' },
      { id: 'sensor-results', label: 'Find the color test result in Report 2.', expected: '270 trials; about 97.04% correct. Some errors remain in the data.' }
    ],
    explainPrompts: [
      'What do the motors, sonar and color sensor each do?',
      'Why can a 450° rotation be more than one complete turn?',
      'Why does a repeated sensor reading not always mean a new measurement?'
    ],
    notePrompts: [
      'Write one calculation and include its units.',
      'Which sensor result did I find? Which part still needs explaining?'
    ],
    breakAfter: { minutes: 15, label: 'Take a short break', timeBlock: '10:30–10:45' }
  },
  {
    id: 'kinematics',
    title: '3. Understand position and turning',
    minutes: 40,
    timeBlock: '10:45–11:25',
    goal: 'Read the worked kinematics exercises. Kinematics means describing position and movement.',
    actions: [
      'Open the kinematics report. Start with the numbered point exercises before the larger coordinate-frame drawing.',
      'A coordinate frame is a starting point and a set of directions used to describe a position. A translation moves the starting point; a rotation turns the directions.',
      'Choose one worked exercise. Find the starting values, the operation and the answer. Follow the written steps slowly; you do not need to memorize every matrix.',
      'The lecture does not state a physical length unit, so the report uses u. Frames B and D are missing from the supplied drawing; their answers are formulas, not invented numbers.'
    ],
    links: [
      { label: 'Kinematics worked solutions', href: 'kit/reports/07_Kinematics_exercise_solutions.pdf' },
      { label: 'Kinematics drawing and tables', href: 'kit/Start_Here.html#8' }
    ],
    checks: [
      { id: 'kinematics-example', label: 'Follow one point exercise from start to answer.', expected: 'You can point to the given values, calculation and final coordinates.' },
      { id: 'missing-frames', label: 'Find the note about frames B and D.', expected: 'Their transforms are symbolic because the source drawing does not define them.' }
    ],
    explainPrompts: [
      'What changes when I move a frame? What changes when I turn it?'
    ],
    notePrompts: [
      'Which exercise did I follow, and what was its result?',
      'Which symbol or step should I ask the teacher to explain?'
    ]
  },
  {
    id: 'ring',
    title: '4. Test Clean the Ring',
    minutes: 45,
    timeBlock: '11:25–12:10',
    goal: 'See how the robot pushes objects outside the ring, then checks whether any remain.',
    actions: [
      'Open Project 1 and click Play. The default replay rate is faster than real time; the displayed elapsed time still comes from the saved simulation.',
      'Try Pause, Restart and the timeline slider. Then move the slider to the end or let the replay finish.',
      'Check the objects-expelled result. Open the report and find the ring dimensions, a calculation and the final map.',
      'Practice a short explanation: the task, what the robot does and the result you checked.'
    ],
    links: [
      { label: 'Play Clean the Ring', href: 'kit/Start_Here.html#4' },
      { label: 'Clean the Ring report', href: 'kit/reports/03_Project_1_Clean_the_Ring.pdf' }
    ],
    checks: [
      { id: 'ring-9', label: 'Finish the ring replay.', expected: 'Objects expelled = 9 / 9. Elapsed time is about 175.96 s.' }
    ],
    explainPrompts: [
      'How does the robot search, push an object and check the ring again?',
      'Which dimensions matter when keeping the robot inside the ring?'
    ],
    notePrompts: [
      'How many objects were expelled, and what time did I see?',
      'Write one assumption that would need checking on a real ring.'
    ],
    breakAfter: { minutes: 40, label: 'Lunch and a rest', timeBlock: '12:10–12:50' }
  },
  {
    id: 'bars',
    title: '5. Test the Bar Scanner',
    minutes: 50,
    timeBlock: '12:50–13:40',
    goal: 'Count the bars and see why moving too fast can miss them.',
    actions: [
      'Open Project 2, click Play and check the final bar count.',
      'Find Try a scanning speed below the replay. Set it to 60 mm/s, then 150 mm/s, then 300 mm/s. Write the count shown at each setting.',
      'Replay rate only changes how fast you watch. The separate scanning-speed slider changes the counting experiment.',
      'Open the report and find the result log. The Bluetooth exchange is emulated: it demonstrates a message without testing a real radio connection.'
    ],
    links: [
      { label: 'Play the Bar Scanner and try speeds', href: 'kit/Start_Here.html#5' },
      { label: 'Bar Scanner report', href: 'kit/reports/04_Project_2_SCANNER.pdf' },
      { label: 'Open the saved scanner log', href: 'kit/data/projects/Scanner.txt' }
    ],
    checks: [
      { id: 'bars-14', label: 'Finish the bar-scanner replay.', expected: 'Bars counted = 14 / 14.' },
      { id: 'bar-speed', label: 'Try the separate speed experiment.', expected: '60 mm/s: 14 / 14 in 5.00 s. 150 mm/s: 7 / 14 in 2.00 s. 300 mm/s: 3 / 14 in 1.00 s.' }
    ],
    explainPrompts: [
      'Why can the faster run count fewer bars?',
      'Why is an emulated message different from a physical Bluetooth test?'
    ],
    notePrompts: [
      'Write the three speeds, counts and times I observed.',
      'What speed would I choose in this model, and why?'
    ]
  },
  {
    id: 'navigation-line',
    title: '6. Test the last two projects',
    minutes: 75,
    timeBlock: '13:40–14:55',
    goal: 'Check obstacle avoidance, then the line follower. Give each project its own short explanation.',
    actions: [
      'Spend about 35 minutes on Project 3. Play the route around the two obstacles. At the end, compare Forward progress and Line deviation with the expected values.',
      'In its report, notice that 1600 mm is forward progress. The total route is longer because the robot goes around obstacles.',
      'Spend about 40 minutes on Project 4. Play the complete circuit. PID is an automatic steering correction that responds to error while following the line.',
      'Open the line-follower report. Find the P, PI and PID comparison. RMS error is one way of summarizing the size of the tracking error over the run; lower is better for this comparison.',
      'Record the two outcomes separately. A successful computer route or lap does not prove the real NXC program has run.'
    ],
    links: [
      { label: 'Play Obstacle Avoidance', href: 'kit/Start_Here.html#6' },
      { label: 'Obstacle Avoidance report', href: 'kit/reports/05_Project_3_Obstacle_Avoidance.pdf' },
      { label: 'Play the PID Line Follower', href: 'kit/Start_Here.html#7' },
      { label: 'PID Line Follower report', href: 'kit/reports/06_Project_4_Single_Sensor_PID_Line_Follower.pdf' }
    ],
    checks: [
      { id: 'nav-1600', label: 'Finish the obstacle-avoidance replay.', expected: 'Forward progress = 1600.0 mm. Line deviation = 0.0 mm. Elapsed time is about 247.64 s.' },
      { id: 'pid-lap', label: 'Finish the PID line-follower replay.', expected: 'One complete circuit; elapsed time = 20.88 s. The report gives PID RMS error of about 0.639 mm.' }
    ],
    explainPrompts: [
      'Why are forward progress and total route length different?',
      'What does PID keep correcting while the robot follows the line?'
    ],
    notePrompts: [
      'Navigation: write the final progress, deviation and time I saw.',
      'Line follower: write the lap time and one result from the P/PI/PID table.',
      'Which project do I need to replay or discuss with the teacher?'
    ],
    breakAfter: { minutes: 15, label: 'Take a short break', timeBlock: '14:55–15:10' }
  },
  {
    id: 'show-and-check',
    title: '7. Practice showing the work',
    minutes: 60,
    timeBlock: '15:10–16:10',
    goal: 'Run a short demonstration, write what you checked and decide what is still needed.',
    actions: [
      'Close extra tabs. Open the demonstration and complete PDF again as if the teacher has just arrived.',
      'For each project, say what it should do, show the replay, read its final result and point to one report calculation with units.',
      'Use your own words. If you cannot explain a step, write a question and return to that part of the report.',
      'Check the readiness list below honestly. Save or export your notes before leaving the university computer, using the note controls on this page.',
      'If a real robot is required, read the hardware setup instructions with your teacher. The NXC programs still need compilation, calibration and physical testing. Real Bluetooth also needs two bricks and a connection test.'
    ],
    links: [
      { label: 'Open the demonstration again', href: 'kit/Start_Here.html#4' },
      { label: 'Open all reports together', href: 'kit/Omar_Zid_Complete_Robotics.pdf' },
      { label: 'Real-robot setup instructions', href: 'kit/code/README.md' }
    ],
    checks: [
      { id: 'four-results', label: 'Repeat the four project outcomes without looking at this guide.', expected: 'Ring 9 / 9; bars 14 / 14; navigation 1600.0 mm and 0.0 mm deviation; PID one circuit in 20.88 s.' }
    ],
    explainPrompts: [
      'What was each task, how does the model do it and what result did I check?',
      'Which inputs are assumed? What would I measure on the real robot?',
      'What is complete today, and what do I still need help with?'
    ],
    notePrompts: [
      'Write a two-minute explanation in my own words.',
      'Write what I tested, the results I observed and any problems.',
      'Write my next action and the questions I will ask the teacher.'
    ],
    readinessItems: [
      { id: 'ready-files', label: 'The demonstration, pictures and reports open on this computer.', expected: 'Open the complete PDF and each project once.' },
      { id: 'ready-replays', label: 'I checked all four project outcomes.', expected: 'Use the four results listed above; record what you saw.' },
      { id: 'ready-controls', label: 'I can use Play, Pause, Restart and the timeline.', expected: 'Try each control in a project replay.' },
      { id: 'ready-explain', label: 'I can explain each task and one calculation with units.', expected: 'Say the explanation aloud and show its place in the report.' },
      { id: 'ready-evidence', label: 'I can clearly say that the measurements are simulated.', expected: 'Do not describe the saved results as physical robot tests.' },
      { id: 'ready-notes', label: 'I saved my notes somewhere I can keep.', expected: 'Check the saved or exported note file before leaving this computer.' }
    ],
    statusNote: 'These checks support readiness to show the computer demonstration. A physical robot is ready only after the programs compile, download and complete their tasks on the real build, with working stopping controls and recorded measurements. This six-hour study plan is a suggested day, not a guarantee of a grade, understanding or physical readiness.'
  }
];
