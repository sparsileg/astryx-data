# Astryx Change Log

## Version 1.3.0
June 17, 2026

- To Do List chart views now show an altitude graph inside each target's
  visibility bar, displaying the target's altitude across the night on a
  fixed 0–90° scale so curves are comparable across targets. Issue 147.
- Clicking a bar in any To Do List chart view (Rise Time, Type, Best Month)
  now selects that target and opens its detail view, matching the behavior
  of list mode links. Issue 147.
- Fixed Viewfinder not updating to the current target when navigating to
  the view after selecting a new target elsewhere in the app. Issue 148.

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
- Added chart and list toggle to all three To Do List views (Type, Best Month,
  Rise Time). The chart shows observable targets as a Gantt-style visibility
  timeline with group label rows as separators. All views now show an imaging
  status indicator (empty, half-filled, or filled circle) indicating whether
  a target has no sessions, an active project, or a completed project in the
  Imaging Log. Trailing commas removed from Type and Best Month list views.
  Best Month "Not Observable" group renamed to "No Best Month Data". Issue
  143.

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
