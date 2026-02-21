# /update-case-study — Record Build Session Results

After a build session completes, update the project's case study file with what was built, the rung achieved, and whether belt progression criteria were met.

## Usage

```
/update-case-study [project] [phase] [rung-achieved]
/update-case-study solace-browser oauth3-core 641
/update-case-study stillwater phase1 641
/update-case-study solaceagi api-backend 274177
/update-case-study solace-cli oauth3-commands 641
```

ARGUMENTS: $ARGUMENTS

## Project → Case Study File Map

| Project | Case Study File |
|---------|----------------|
| `stillwater` | /home/phuc/projects/stillwater/case-studies/stillwater-itself.md |
| `solace-browser` | /home/phuc/projects/stillwater/case-studies/solace-browser.md |
| `solace-cli` | /home/phuc/projects/stillwater/case-studies/solace-cli.md |
| `solaceagi` | /home/phuc/projects/stillwater/case-studies/solaceagi.md |

## Belt Progression Criteria

| Belt | Automatic when... |
|------|------------------|
| White | rung_achieved >= 641 AND first verified output exists |
| Yellow | rung_achieved >= 274177 (seed sweep + replay complete) |
| Orange | first skill submitted to Stillwater Store AND accepted |
| Green | rung_achieved >= 65537 (adversarial + security gate passed) |
| Blue | cloud execution confirmed 24/7 (no manual intervention) |
| Black | Green belt held for 30 consecutive days in production |

## Instructions for Claude

When user runs `/update-case-study [project] [phase] [rung-achieved]`:

### Step 1 — Validate Arguments

1. `project` must be one of: stillwater, solace-browser, solace-cli, solaceagi
2. `phase` — any string (e.g., "phase1", "oauth3-core", "api-backend")
3. `rung-achieved` must be one of: 641, 274177, 65537

If any argument is missing or invalid: list valid values and stop. Do NOT guess.

### Step 2 — Read Current Case Study

Read the case study file for the project. Extract:
- Current belt
- Current rung
- What is already listed as completed
- Current metrics table values

### Step 3 — Ask for Build Artifacts

If the user has not provided artifact details, ask:

```
What artifacts were produced in this build session?
  1. Files created (list paths)
  2. Tests passing? (yes/no + test command used)
  3. Evidence bundle exists? (evidence/plan.json, evidence/tests.json)
  4. Git commit SHA (if committed)
  5. Any blockers encountered?

You can also paste the agent's output directly and I will extract these.
```

Wait for user response before continuing.

### Step 4 — Check Belt Progression

Apply belt criteria:

```
Current belt: [X]
Rung achieved: [rung]

Belt progression check:
  White:  [ACHIEVED | not yet — need: rung 641]
  Yellow: [ACHIEVED | not yet — need: rung 274177]
  Orange: [ACHIEVED | not yet — need: Stillwater Store submission]
  Green:  [ACHIEVED | not yet — need: rung 65537]

Belt upgrade: [none | WHITE → YELLOW | etc.]
```

If belt upgraded: announce it clearly.

### Step 5 — Update Case Study File

Add a new build record to the case study. The format to append:

```markdown
## Build Record: [phase] — [TODAY's DATE]

**Phase**: [phase]
**Rung achieved**: [rung]
**Belt after**: [belt]
**Date**: [TODAY's DATE]

### What was built
[List files created, summarized from user input]

### Evidence bundle
- Files created: [list]
- Tests: [pass/fail + count]
- Git commit: [SHA or "not committed yet"]
- evidence/plan.json: [exists | missing]
- evidence/tests.json: [exists | missing]

### Metrics updated
[Update any metric that changed — e.g., "OAuth3 implementation: 0% → 40%"]

### Next phase
[Extract from ROADMAP.md what comes next]
```

Also update the metrics table at the top of the case study (if any metric changed).

If belt progressed: update the `**Belt**: X` line at the top of the case study.
If rung progressed: update the `**Rung**: X` line at the top.

Write the updated file. Confirm: "Updated case-studies/[project].md".

### Step 6 — Update Memory

Auto-save to `.claude/memory/context.md` via `/remember`:

```
current_phase_[project]: [phase] completed [TODAY's DATE]
rung_[project]: [rung-achieved]
belt_[project]: [belt]
```

### Step 7 — Suggest Next Action

Read the project's ROADMAP.md and output:

```
=== CASE STUDY UPDATED ===

Project:     [project]
Phase done:  [phase]
Rung:        [rung-achieved]
Belt:        [belt] [upgrade note if applicable]
Date:        [TODAY's DATE]

Next phase from ROADMAP:
  [next phase name + 1 line goal]

Suggested next command:
  /build [project] [next-phase]

Or check full ecosystem status:
  /status
```

## Example Session

```
User: /update-case-study solace-browser oauth3-core 641

Claude:
Validating...
  project: solace-browser ✅
  phase: oauth3-core ✅
  rung: 641 ✅

Reading case-studies/solace-browser.md...
Current belt: Yellow | Current rung: 641

What artifacts were produced?
[Claude asks for artifact details]

User: Created oauth3/token.py, oauth3/scopes.py, oauth3/enforcement.py.
Tests: 12 passing (pytest tests/test_oauth3.py -v). Committed: abc1234.

Claude:
Belt progression check:
  White:  ACHIEVED (rung 641 ✅)
  Yellow: ACHIEVED (rung 641 ✅ — already at Yellow)
  Orange: not yet (need Store submission)
  Green:  not yet (need rung 65537)

No belt upgrade this phase. Still Yellow.

Updating case-studies/solace-browser.md...
Writing build record for oauth3-core (2026-02-21)...
Updated metrics: OAuth3 implementation 0% → 60%

Saving to memory:
  current_phase_solace-browser: oauth3-core completed 2026-02-21
  rung_solace-browser: 641

=== CASE STUDY UPDATED ===
Project:     solace-browser
Phase done:  oauth3-core
Rung:        641
Belt:        Yellow (no change)
Date:        2026-02-21

Next phase from ROADMAP: oauth3-consent (Consent UI)
Command: /build solace-browser oauth3-consent
```

## Related Commands

- `/build [project] [phase]` — Launch the next build session
- `/status` — View full ecosystem status after update
- `/hub` — Central overview with updated metrics
- `/remember` — View persistent memory (includes rung/belt tracking)
