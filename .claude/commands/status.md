# /status — Phuc Ecosystem Status Dashboard

Read all case-study files + NORTHSTAR metrics and display the full ecosystem state: belt, rung, phase, and next recommended action for every project.

## Usage

```
/status                   # Full ecosystem dashboard
/status stillwater        # Single project status
/status solace-browser    # Single project status
/status --rungs           # Rung ladder view only
/status --next            # Next recommended build actions only
```

ARGUMENTS: $ARGUMENTS

## Instructions for Claude

When user runs `/status`:

### Step 1 — Read All Case Studies

Read these files in parallel:
- `/home/phuc/projects/stillwater/case-studies/stillwater-itself.md`
- `/home/phuc/projects/stillwater/case-studies/solace-browser.md`
- `/home/phuc/projects/stillwater/case-studies/solace-cli.md`
- `/home/phuc/projects/stillwater/case-studies/solaceagi.md`

Also read NORTHSTAR.md for the northstar metrics baseline:
- `/home/phuc/projects/stillwater/NORTHSTAR.md`

### Step 2 — Read Memory

Read `/home/phuc/projects/stillwater/.claude/memory/context.md` for:
- `current_phase_*` keys (latest phase per project)
- `rung_*` keys (latest rung achieved per project)
- `blocker_*` keys (any active blockers)

### Step 3 — Display Dashboard

```
==================================================
PHUC ECOSYSTEM STATUS — [TODAY's DATE]
==================================================

MASTER EQUATION:
  Intelligence(system) = Memory × Care × Iteration
  Memory  = [count] skills + [count] recipes + [count] swarms
  Care    = Verification ladder: 641 → 274177 → 65537
  Iteration = Never-Worse doctrine + git versioning

NORTHSTAR METRICS (from NORTHSTAR.md):
  GitHub stars:       [now] / [Q2 target] / [2026 target]
  Rung 65537 projects:[now] / [Q2 target] / [2026 target]
  Store skills:       [now] / [Q2 target] / [2026 target]
  Recipe hit rate:    [now] / [Q2 target] / [2026 target]

--------------------------------------------------
PROJECT STATUS
--------------------------------------------------

stillwater     [BELT]  Rung [X]
  Phase done:  [list completed phases from case study]
  Phase next:  [next phase from ROADMAP]
  Blockers:    [none | list]
  Last build:  [date from case study if available]
  Run:         /build stillwater [next-phase]

solace-browser [BELT]  Rung [X]
  Phase done:  [list completed phases from case study]
  Phase next:  [next phase]
  Blockers:    [none | list]
  Last build:  [date from case study if available]
  Run:         /build solace-browser [next-phase]

solace-cli     [BELT]  Rung [X]
  Phase done:  [list completed phases from case study]
  Phase next:  [next phase]
  Blockers:    [none | list]
  Last build:  [date from case study if available]
  Run:         /build solace-cli [next-phase]

solaceagi      [BELT]  Rung [X]
  Phase done:  [list completed phases from case study]
  Phase next:  [next phase]
  Blockers:    [none | list]
  Last build:  [date from case study if available]
  Run:         /build solaceagi [next-phase]

--------------------------------------------------
BELT PROGRESSION SUMMARY
--------------------------------------------------

  White  [✓] = rung 641 achieved
  Yellow [✓] = rung 274177 achieved
  Orange [✓] = first skill in Stillwater Store
  Green  [ ] = rung 65537 achieved
  Blue   [ ] = cloud execution 24/7
  Black  [ ] = Models=commodities, Skills=capital, OAuth3=law

--------------------------------------------------
RECOMMENDED NEXT ACTION
--------------------------------------------------

  Priority 1 (highest leverage):
    [project] — [phase] — [why this phase unblocks the most]
    Command: /build [project] [phase]

  Priority 2:
    [project] — [phase]
    Command: /build [project] [phase]

  Priority 3:
    [project] — [phase]
    Command: /build [project] [phase]

==================================================
```

### Step 4 — Belt Criteria Check

For each project, apply belt progression logic:

| Belt | Criteria |
|------|----------|
| White | rung 641 achieved on at least 1 verified output |
| Yellow | rung 274177 achieved (seed sweep + replay) |
| Orange | first skill submitted to Stillwater Store |
| Green | rung 65537 achieved (adversarial + security gate) |
| Blue | Cloud execution running 24/7 (no babysitting needed) |
| Black | Production task at rung 65537 for 30 consecutive days |

### Step 5 — Priority Ranking

Rank next build actions by impact:
1. Any blocker that blocks 2+ projects = Priority 1
2. Phase that unblocks the northstar metric = Priority 2
3. Phase that achieves next belt = Priority 3

## When user runs `/status [project]`

Same as above but scoped to one project. Show:
- Case study full content
- ROADMAP phases: done / in-progress / todo
- Belt progress
- Next `/build` command

## When user runs `/status --rungs`

Show only the rung ladder view:

```
RUNG LADDER (current state):

Rung 641 (local correctness):
  stillwater     [X] achieved
  solace-browser [X] achieved
  solace-cli     [ ] not yet
  solaceagi      [ ] not yet

Rung 274177 (stability + replay):
  stillwater     [ ] not yet
  solace-browser [ ] not yet
  solace-cli     [ ] not yet
  solaceagi      [ ] not yet

Rung 65537 (production + security gate):
  stillwater     [ ] not yet (target: Month 3)
  solace-browser [ ] not yet
  solace-cli     [ ] not yet
  solaceagi      [ ] not yet

Integration rung (ecosystem):
  MIN(all projects) = [lowest rung across all projects]
  Current: [value]
  Bottleneck: [project with lowest rung]
```

## When user runs `/status --next`

Show ONLY the next recommended actions:

```
NEXT ACTIONS (ranked by leverage):

1. /build [project] [phase] — [1 line reason]
2. /build [project] [phase] — [1 line reason]
3. /build [project] [phase] — [1 line reason]

Start with #1. Run /build [project] [phase] to launch the swarm.
```

## Related Commands

- `/build [project] [phase]` — Launch a build session
- `/hub` — Full ecosystem overview including pricing + strategy
- `/update-case-study [project] [phase] [rung]` — Record completed build
- `/northstar` — Load NORTHSTAR for current project
- `/remember` — View persistent memory for rung/phase tracking
