# /build — Launch Phuc Swarm Build Session

Start a full phuc swarm build session for a project phase. Reads NORTHSTAR + ROADMAP, assembles the correct agent team, and produces the full session prompt.

## Usage

```
/build [project] [phase]
/build solace-browser oauth3-core
/build stillwater phase1
/build solaceagi api-backend
/build solace-cli oauth3-commands
/build --list                       # Show all projects + phases
```

ARGUMENTS: $ARGUMENTS

## Project Registry

| Project | Path | NORTHSTAR | ROADMAP |
|---------|------|-----------|---------|
| `stillwater` | /home/phuc/projects/stillwater/ | NORTHSTAR.md | ROADMAP.md |
| `solace-browser` | /home/phuc/projects/solace-browser/ | NORTHSTAR.md | ROADMAP.md |
| `solace-cli` | /home/phuc/projects/solace-cli/ | NORTHSTAR.md | ROADMAP.md |
| `solaceagi` | /home/phuc/projects/solaceagi/ | NORTHSTAR.md | ROADMAP.md |

## Swarm Team for Every Build

| Agent | Model | Skill Pack | When |
|-------|-------|-----------|------|
| Scout | haiku | prime-safety | Always first — map codebase, identify gaps |
| Forecaster | sonnet | prime-safety + phuc-forecast | Always — failure modes, stop rules |
| Judge | sonnet | prime-safety + phuc-forecast | Always — approve scope, set rung |
| Coder | sonnet | prime-safety + prime-coder | Implementation |
| Skeptic | sonnet | prime-safety + prime-coder + phuc-forecast | Verification (rung 274177+) |

## Instructions for Claude

When user runs `/build [project] [phase]`:

### Step 1 — NORTHSTAR Alignment Check
1. Read `[project-path]/NORTHSTAR.md`
2. Display: Mission (1 line) + Northstar Metric + Current Belt/Rung
3. Confirm: does the requested phase serve the northstar? Output ALIGNED or DRIFT.
4. If DRIFT: warn the user and ask for confirmation before proceeding.

### Step 2 — ROADMAP Phase Extraction
1. Read `[project-path]/ROADMAP.md`
2. Find the section matching `[phase]` argument (fuzzy match on phase name/number/keyword)
3. Extract: Goal, Task list, Build Prompt(s), Rung target, Evidence required
4. If phase not found: list all available phases and stop.

### Step 3 — Case Study Status
1. Read `/home/phuc/projects/stillwater/case-studies/[project].md`
2. Show current status (what's done, what's blocked, current rung)
3. Confirm this phase is the correct next step.

### Step 4 — Scout Dispatch (haiku)
Dispatch a Scout agent to map the codebase and identify gaps before coding begins.

```
=== SCOUT DISPATCH ===
Role:        scout
Model:       haiku
Skill pack:  prime-safety (full content from skills/prime-safety.md)
Rung target: 641

Task (CNF Capsule):
  You are a Scout agent. Your job is to map the current state of [project]
  before the build session begins.

  Project path: [project-path]
  Phase goal: [extracted from ROADMAP]

  Steps:
  1. List all files relevant to this phase (no deep reading)
  2. Identify: what exists vs. what the phase requires
  3. Flag any blockers (missing dependencies, conflicting files)
  4. Output: gap_report.json with {exists: [...], missing: [...], blockers: [...]}

  Stop rules:
  - EXIT_PASS: gap_report.json complete
  - EXIT_BLOCKED: fatal blocker found (list it)
```

### Step 5 — Forecaster + Judge Dispatch (sonnet)
After scout returns, dispatch Forecaster + Judge.

```
=== FORECASTER DISPATCH ===
Role:        forecaster (planner)
Model:       sonnet
Skill pack:  prime-safety + phuc-forecast (full content from skills/)
Rung target: [from ROADMAP]

Task (CNF Capsule):
  You are a Forecaster agent applying phuc-forecast to this build session.

  Project: [project]
  Phase: [phase]
  Goal: [phase goal from ROADMAP]
  Scout gap report: [paste gap_report.json from scout]
  NORTHSTAR metric: [paste from NORTHSTAR.md]

  Required output (DREAM → FORECAST → DECIDE → ACT → VERIFY):

  DREAM:
    - Goal + success metrics (concrete, measurable)
    - Constraints: [list]
    - Non-goals: [list]

  FORECAST:
    - Top 5 failure modes (ranked by P × Impact)
    - Assumptions + unknowns
    - Risk level: LOW / MED / HIGH

  DECIDE:
    - Chosen approach
    - Alternatives considered
    - Stop rules (EXIT_PASS conditions, EXIT_BLOCKED conditions)

  ACT:
    - Step plan with checkpoints
    - Artifacts to produce
    - Rung target: [from ROADMAP]

  VERIFY:
    - Tests required
    - Evidence bundle required: [from ROADMAP]
    - Falsifiers (what would prove this FAILED)

  Stop rules:
  - EXIT_PASS: All 5 sections complete, no FACT_INVENTION, no SKIP_VERIFY
  - EXIT_NEED_INFO: Missing required inputs
  - EXIT_BLOCKED: Risk level HIGH with no mitigation
```

### Step 6 — Build Prompt Output

After Forecaster + Judge complete, output the full build prompt the user can paste into a new session:

```
========================================
PHUC SWARM BUILD SESSION
========================================
Project:     [project]
Phase:       [phase]
Rung target: [rung]
Date:        [today]
NORTHSTAR:   [northstar metric]
Status:      ALIGNED / DRIFT

NORTHSTAR (loaded):
[paste key lines from NORTHSTAR.md]

SCOUT FINDINGS:
[gap_report.json summary]

FORECAST:
[paste DREAM + FORECAST + DECIDE sections]

BUILD TASK (paste into new session):
---
[paste the Build Prompt from ROADMAP verbatim]
---

SKILL PACK (paste into every sub-agent):
  1. skills/prime-safety.md (ALWAYS FIRST)
  2. skills/prime-coder.md (for coder/skeptic agents)
  3. skills/phuc-forecast.md (for planner/skeptic agents)

RUNG TARGET: [rung]
EVIDENCE REQUIRED: [from ROADMAP]
NEXT COMMAND AFTER BUILD: /update-case-study [project] [phase] [rung-achieved]
========================================
```

### Step 7 — Dispatch Coder (sonnet)

If user confirms "go", dispatch the Coder agent with the full CNF capsule:

```
=== CODER DISPATCH ===
Role:        coder
Model:       sonnet
Skill pack:  prime-safety + prime-coder (full content from skills/)
Rung target: [from ROADMAP]

Task (CNF Capsule):
  You are a Coder agent. Do NOT do inline deep work without tests.

  Project: [project] at [project-path]
  Phase: [phase]
  Goal: [goal]

  NORTHSTAR alignment confirmed: [northstar metric]

  Forecaster plan: [paste ACT section from forecaster]
  Scout gap report: [paste gap_report.json]

  Build steps (from ROADMAP):
  [paste verbatim Build Prompt steps]

  Rung target: [rung]
  Evidence required: [evidence list from ROADMAP]

  MANDATORY:
  - Write failing test FIRST (red gate)
  - Implement minimum code to pass (green gate)
  - Run full test suite, zero regressions
  - Produce: evidence/plan.json, evidence/tests.json
  - Commit with feat: or fix: prefix

  Stop rules:
  - EXIT_PASS: all evidence artifacts exist AND tests pass AND rung_target met
  - EXIT_BLOCKED: blocker found — list it and stop
```

After coder returns, dispatch Skeptic at rung 274177+ to verify.

## When user runs `/build --list`

Read ROADMAP.md from each project and display:

```
=== PHUC ECOSYSTEM BUILD STATUS ===

stillwater     [Orange] Phase 0: Audit ✅ | Phase 1: OAuth3 spec → NEXT
solace-browser [Yellow] Phase 1: LinkedIn MVP ✅ | Phase 1.5: oauth3-core → NEXT
solace-cli     [White]  Phase 0: Whitepaper ✅ | Phase 1: oauth3-commands → NEXT
solaceagi      [White]  Phase 0: Whitepaper ✅ | Phase 1: api-backend → NEXT

Run: /build [project] [phase] to start a swarm build session.
```

## Forbidden States

- `SKILL_LESS_DISPATCH` — never dispatch without full skill content pasted inline
- `FORGOTTEN_CAPSULE` — never say "as discussed" or "as before" in any sub-agent prompt
- `NORTHSTAR_DRIFT_UNCHECKED` — never start a build without NORTHSTAR alignment check
- `RUNG_UNDECLARED` — always declare rung_target before any dispatch
- `SCOUT_SKIPPED` — always run scout before coder (map before build)

## Related Commands

- `/swarm [role] "task"` — Launch a single typed agent
- `/status` — Check all project rungs + belt progression
- `/northstar` — Load and display current project NORTHSTAR
- `/update-case-study [project] [phase] [rung]` — Record build results
