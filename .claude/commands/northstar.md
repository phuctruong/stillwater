# /northstar — Load Project NORTHSTAR

Display the NORTHSTAR.md for the current project — the guiding vision, key metrics,
and how phuc-forecast + swarms serve the mission.

## Usage

```
/northstar                  # Display current project NORTHSTAR.md
/northstar --check          # Verify NORTHSTAR.md exists and is complete
/northstar --align [task]   # Check if task aligns with northstar before starting
```

## What It Does

1. **Read** `NORTHSTAR.md` from current project root
2. **Display** mission, north star metric, and current rung status
3. **Align check** — does this task serve the northstar or drift from it?

## Instructions for Claude

When user runs `/northstar`:
1. Read `NORTHSTAR.md` from current working directory
2. Display: Mission, Northstar Metric, Current Rung, Model Strategy
3. If NORTHSTAR.md missing: remind user to create it via `stillwater init project`

When user runs `/northstar --align [task]`:
1. Read NORTHSTAR.md
2. Ask: does `[task]` directly serve the northstar metric?
3. Output: ALIGNED | DRIFT (with brief reason)
4. If DRIFT: suggest how to reframe the task to align

## Why This Matters

Every Claude Code session starts cold. The northstar grounds the session immediately:
- What is this project trying to achieve?
- What rung are we at vs. where we need to be?
- Which swarm agents serve this goal?
- What is explicitly out of scope?

Without a northstar, Claude drifts to solving whatever is in front of it.
With a northstar, every action is measured against the mission.

## Related Commands

- `/remember` — Store northstar decisions in persistent memory
- `/phuc-swarm planner "..."` — Plan work aligned to northstar
- `/distill NORTHSTAR.md` — Compress northstar to key=value facts for `/remember`
