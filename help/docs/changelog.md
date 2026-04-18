# Astryx Change Log

## Version 1.2.0
April 18, 2026

- Fixed session analysis log parser to correctly exclude flat frame sessions
  from analysis, resolving negative gap values and incorrect subs-per-dither
  counts. Issue 144.
- Replaced the single "Between Subs" session parameter with a learned algorithm
  that automatically derives sub gap and dither duration from analyzed session
  logs using an exponential moving average. The only user-settable parameter is
  now "Frames per Dither" (0 = no dither). The sequence planner computes
  between-sub overhead automatically from the learned values. Issue 145.

## Version 1.1.1
March 25, 2026

- Added a feedback email address (feedback@astryx.tools) to the About
  view. #137.
- In Sequence Planner, removed the 'Cal' label that was associated with a
  flip and just let the Cal event after the flip be the one that is
  displayed. #138
- Fixed a few CSS/styling bugs with the To Do chart and Filter Targets
  buttons. #139
- Added a new flat theme with warm medium brown, cream text, and amber gold
  accent colors. #140
- Backup indicator at bottom of sidebar didn't collapse properly with the
  sidebar. #141

## Version 1.1.0
March 23, 2026

- Link tutorials. Starting with **Getting Started**, each tutorial,
  after completion, will point to the next suggested tutorial. Issue 127.
- Add Change Log. After release 1.0.0, any installed changes will be included in
  a Change Log, accessible from the system menu. Issues 86, 128.
- Fix charts not being redrawn properly when sidebar is collapsed and
  opened. Issue 129.
- Fixed improperly scaled values in wind bar on Daily Visibility
  chart. Improved styling for better UX. Issue 130.
- Add tooltips to weather bars on Daily Visibility view. Issue 131.
- Fix CSS rendering problem on Sequence Planner chart background when
  switching themes. Issue 132.
- Balance sequence planner chart margins. Issue 133.
- Added additional optimization to Sequence Planner and fixed some bugs. Issues 134, 135.

  ---
