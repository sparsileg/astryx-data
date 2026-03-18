# Sequence Planner

## Overview

The Sequence Planner helps you plan an optimal imaging session across
pinned targets for a given night. It determines the best order to image
your targets, allocates time to each one, accounts for equipment overhead
events, and visualizes the entire session on a timeline. If you are imaging
only one target, the Sequence Planner will provide the complete schedule
of events using user-defined session settings.

The planner works entirely from your pinned targets, your selected observer
location, and the session settings you provide. It requires no internet
connection.

---

## Session Boundaries

The session begins at astronomical dusk (sun below -18°), a user-defined
start time, or when your first target reaches minimum altitude. The session
ends at astronomical dawn, or when the last target sets below your minimum
altitude — whichever comes first.

**Important:** The session end time depends on which target is scheduled
last. A target that remains visible until dawn extends the session longer
than one that sets at 3 AM. The planner accounts for this when optimizing
target order.

---

## Target Allocation

Time is divided equally among all targets as a starting point, with targets
ordered by earliest set time — the target that sets soonest below your
minimum altitude is scheduled first, ensuring limited-visibility targets
are imaged before they become inaccessible. Targets visible all night are
scheduled last. Each target receives an equal percentage of the total
session time. You can adjust individual target allocations using the
sliders in the Target Allocation section — reducing one target's time
increases the others proportionally.

Each target's net imaging time is its allocated time minus all overhead
events that occur during its window.

---

## Overhead Events

The following overhead events consume imaging time and are accounted for in
the exposure count calculation:

### Autofocus (AF)
If enabled, autofocus:

- Runs once at the **start of every target**
- Runs once **after every meridian flip**
- Runs **periodically** throughout each target at the interval you specify
- The AF timer resets after every AF event — whether periodic, post-flip,
  or at a target transition

### Calibration
- Runs once at the **start of every target**
- Also runs as part of the meridian flip sequence

### Meridian Flip
Occurs when a target transits (crosses the meridian). The full flip sequence is:

1. Wait for transit plus the user-configured offset, then pause imaging
2. Flip operation (user-configured duration)
3. Pause after flip (same duration as pause before)
4. Perform guiding calibration

A flip offset can be applied to trigger the flip slightly before or after
the exact transit time.

### Between Subs
A brief gap between each exposure (download time, dithering, etc.).

---

## Initial Target Ordering

Before any optimization, targets are ordered by **earliest set time** —
the target that sets soonest below your minimum altitude is scheduled
first. Targets that remain visible all night are scheduled last.

This ensures targets with limited visibility windows are imaged while they
are still accessible.

---

## Sequence Optimization

When **Sequence Optimization** is enabled, the planner runs a second pass
to find a better target order and boundary allocation than the default
equal-split. The algorithm has two components:

### Pass 1: Permutation Search

All possible orderings of your targets are evaluated. For 2 targets there
are 2 permutations; for 3 targets there are 6; for 4 targets there are 24.
This is practical for the typical 2–4 target session.

For each permutation:
- The session window is recalculated (since the last target determines
  when the session ends)
- Flip boundary optimization is applied (see Pass 2 below)
- The total exposure count across all targets is calculated

The permutation with the highest total exposure count is selected as the
candidate result.

### Pass 2: Flip Boundary Optimization

For each target that has a meridian flip, the planner tries three boundary
positions relative to the transition to the next target:

**Option A — Exclude the flip:** End the current target just before the
flip pause begins. The flip overhead is avoided entirely, and the saved
time is given to the next target.

**Option B — Include and extend the flip:** Extend the current target's
window to include the full flip sequence plus additional post-flip imaging
time, at the expense of the next target's allocation.

**Option C — Absorb the next target's flip:** When the next target also
has a meridian flip, extend the current target's boundary past that flip,
so the next target begins with the telescope already on the correct side
of the meridian. This can eliminate two flip overhead events with a single
boundary adjustment.

All three options are scored by total exposure count. The best result is
kept.

### Acceptance Threshold

The optimized result is only accepted if it improves total exposure count
by at least **5%** over the baseline equal-allocation result. If the
improvement is smaller than 5%, the original equal allocation is kept.
This prevents the optimizer from accepting marginally better but
unbalanced distributions — for example, giving one target very few
exposures just to squeeze out one extra sub overall.

The 5% threshold is configurable via `TRANSITION_OPTIMIZATION_THRESHOLD`
in `config.js`.

---

## Constraints and Assumptions

### Altitude
Targets must be above your configured minimum altitude to be scheduled.
The global minimum altitude from Settings is used as the default, but can
be overridden per session. If the first target is below minimum altitude at
the start of the session, the session start is delayed until it rises. If a
target sets before dawn, the session ends at that point.

### Horizon Profile
If your observer location has a horizon profile defined and horizon use is
enabled, targets blocked by the horizon are flagged with an orange
crosshatch overlay on the timeline. The planner does not currently split
a target's imaging window around a horizon obstruction.

### Equal Exposure Time
All targets in a session are assumed to use the same exposure duration.
Each target row has its own exposure time input, but the optimizer scores
permutations using the first target's exposure time as a proxy for the
session. Varying exposure times between targets may cause the optimizer to
make slightly suboptimal decisions. This is a known limitation of the
current optimizer.

### Meridian Flip Timing
The flip is triggered at transit plus the flip offset you specify. The
planner cannot communicate with your equipment — it models the flip as a
fixed overhead block. Actual flip timing depends on your imaging software.

### No Moon Avoidance
Moon position and phase are not currently factored into the sequencing
algorithm. Moon data is displayed on the Daily Visibility view and can
inform your manual target selection, but the sequence planner does not
automatically avoid targets near a bright moon.

---

## Manual Overrides

The optimizer's result is a suggestion. You can:

- **Drag targets** to reorder them in the Target Allocation section
- **Adjust sliders** to give more or less time to individual targets
- **Click Reset & Optimize** to return to the optimizer's suggested order
  with equal allocations

The timeline updates immediately whenever you make changes.

---

## Known Limitations

- Does not stop imaging when obstructed based on a horizon profile
- Does not take the moon position into account
- The optimizer is practical for 2–4 targets; sessions with 5+ targets
  produce many permutations and may benefit from a heuristic approach
  rather than exhaustive search
