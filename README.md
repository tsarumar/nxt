# Omar Zid university robotics guide

Open **https://tsarumar.github.io/nxt/** on the university computer.

The site walks through one suggested day: open the work, learn the basics,
follow the exercises, test four projects, practice explaining them, and save notes.
No installation or GitHub sign-in is needed to view the browser demonstration.

## Keep your notes

Notes and checklist progress stay in your current browser. They are never sent
to GitHub. Use **Save my notes** to download readable text before leaving.
To continue on another computer, save and load a progress JSON file from the
page's move-progress controls. Clearing the browser does not delete exported files.

## Use offline

Download `downloads/Omar_Zid_University_Kit.zip`, extract all files, then open
`index.html`. Keep the `kit` folder alongside the guide files. The same notes,
reports and replays work without an internet connection. Exported progress can
be loaded into either the public site or the downloaded version.

## Evidence and scope

The kit contains eight PDF reports and eight editable Word reports, the combined
report, NXC sources, numerical models, measurements, figures and supplied material.
Robot measurements are simulated. Project animation replays saved numerical
traces; the scanner-speed and wheel calculators run in the browser. Re-running
Python regenerates data, but does not automatically update the fixed reports
or embedded replay. Hardware compilation and physical NXT/Bluetooth tests remain
unverified. Coordinate frames B and D were not defined in the supplied lecture;
their transforms are given symbolically.

The website's checkboxes and notes record your own checks and explanations;
they are not an automatic grade or proof of physical robot performance.

## Hosting

This is a buildless static site, served by GitHub Pages from the repository's
publishing branch. `.nojekyll` preserves the supplied static filenames.
No database, third-party runtime, tracking, account or API key is required.
Development-only `qa/` and `tools/` folders are excluded from version control.
