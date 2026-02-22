# Combo 8a — Hackathon Lightning (2-Hour Sprint)

The lightning sprint is for when you have 2 hours and one clear goal. No committees. No scope debates. One thing. Ship it.

---

# W_HACKATHON_LIGHTNING — 2-Hour Build Contract

**WISH_ID:** `wish_hackathon_lightning`
**PRIORITY:** HIGH
**CLASS:** execution
**DEPENDS_ON:** `wish_hackathon_sprint`
**VARIANT_OF:** `wish_hackathon_sprint`

---

## Goal

Ship one concrete artifact in 2 hours. The artifact must be demo-able at the end.

A 2-hour sprint is appropriate for:
- Writing one new skill file
- Creating one paper or analysis
- Building one recipe or combo
- Fixing one confirmed bug with evidence
- Producing one swarm agent definition

---

## Invariants

1. **One artifact only**: no multi-output sprints. One thing, completely done.
2. **Time box is 120 minutes, hard**: no extensions.
3. **Demo in the last 10 minutes**: if there is no demo, there is no PASS.
4. **Scout is compressed**: 15 minutes max. If you do not know what to build, do not start a lightning sprint.
5. **GLOW minimum 45**: lower bar than standard sprint due to compressed time.

---

## Forbidden States

All forbidden states from `wish_hackathon_sprint`, plus:
* `MULTI_ARTIFACT_LIGHTNING` — attempting more than one artifact in a 2-hour sprint
* `SCOUT_OVER_15_MIN` — scout phase consuming more than 12.5% of time box

---

## Required Artifacts

* `evidence/sprint.json` (compressed: start/end/artifact/scope_cuts)
* `evidence/demo.md` (what was shipped)
* `evidence/glow_score.json`

---

# R_HACKATHON_LIGHTNING — 2-Hour Sprint Recipe

**RECIPE_ID:** `recipe_hackathon_lightning_v1`
**SATISFIES:** `wish_hackathon_lightning`

---

## Phase Timeline (2-hour sprint = 120 minutes)

```
Phase 1 — Scout + Plan  (0:00 – 0:15)   12.5% — 15 min cap; NORTHSTAR check + scope lock
Phase 2 — Build         (0:15 – 1:30)   62.5% — 75 min; one artifact, no new scope
Phase 3 — Verify        (1:30 – 1:50)   17%   — 20 min; evidence + skeptic check
Phase 4 — Demo + Close  (1:50 – 2:00)   8%    — 10 min; demo.md + GLOW + commit
```

---

## Phase 1 — Scout + Plan (15 minutes hard cap)

**Model**: haiku (speed) or sonnet (if NORTHSTAR check needed)
**Persona**: hackathon-master

Questions to answer in 15 minutes:
1. What is the one artifact being built? (name it exactly)
2. Does it align to NORTHSTAR? (yes/no — if no, abort)
3. What is the demo target? (one sentence: "The demo shows X running and producing Y")
4. What is NOT in scope? (list 3 things explicitly cut)
5. What is the rung target? (641 for most lightning sprints)

Outputs:
* `LightningSprint.json`:
  * `artifact_name`
  * `demo_target` (one sentence)
  * `scope_cuts[]` (3 items minimum)
  * `persona_pack[]`
  * `rung_target`
  * `northstar_alignment` (yes/no + why)

Fail-closed: if 15 minutes pass without `LightningSprint.json`, abort the sprint. Run a standard sprint instead.

---

## Phase 2 — Build (75 minutes)

**Model**: sonnet
**Persona**: domain persona from `LightningSprint.json` + hackathon-master as scope guard

Rules:
* Build only what is in `demo_target`. Nothing else.
* If you hit a blocker in the first 30 minutes that cannot be resolved in 10 minutes → scope-cut and simplify.
* If you hit a blocker in the last 45 minutes → simplify the demo, not the timeline.
* Commit early. An imperfect committed artifact beats a perfect uncommitted one.

Scope cut trigger (hard): if build is not 60% complete by the 75-minute mark → emit a scope cut, reduce `demo_target`, continue.

---

## Phase 3 — Verify (20 minutes)

**Model**: sonnet
**Persona**: kent-beck (if code) / fda-auditor (if evidence-heavy)

Checks (time-capped — 20 minutes, not exhaustive):
* Does the artifact match `demo_target`? (binary: yes/no)
* Run the minimum test suite (if code): `pytest -q --timeout=30`
* Check for any HIGH security issues (prime-safety gate — non-negotiable)
* Confirm evidence files exist

If verify fails:
* One pass only to fix the specific failure
* Do not open new scope
* 10-minute fix cap, then proceed to Close regardless

---

## Phase 4 — Demo + Close (10 minutes)

**Model**: haiku (speed)
**Persona**: hackathon-master

Write `evidence/demo.md` in under 5 minutes:
```markdown
# Lightning Sprint Demo — {artifact_name}

## What Was Built
{one paragraph}

## How to Run / See It
{exact command or URL}

## Rung Achieved
{641|274177|65537}

## What Was Cut
{scope_cuts from LightningSprint.json}

## GLOW
G:{g} L:{l} O:{o} W:{w} Total:{total}
```

GLOW calculation for lightning sprints:

```
G (Growth):    +8 committed artifact; +4 upgrade; +3 rung 274177+
L (Learning):  +8 blocker/discovery logged; +4 scope cut documented; +3 cited prior art
O (Output):    +8 artifact committed + demo-able; +4 evidence bundle complete; +3 tests pass
W (Wins):      +8 NORTHSTAR aligned; +4 case-study updated; +3 ROADMAP advanced

Target: 50+ (lightning pace)
Minimum to PASS: 45
```

Commit format:
```
feat: {artifact_name} — lightning sprint {date}

GLOW {total} [G:{g} L:{l} O:{o} W:{w}]
Sprint: 120min lightning | Scope cuts: {N}
Demo: {demo_target one-liner}
```

---

## When to Use Lightning vs Standard

| Signal | Use Lightning | Use Standard |
|--------|--------------|--------------|
| Clear artifact, clear demo | Yes | No |
| Fuzzy requirements | No | Yes |
| Single file / skill / paper | Yes | No |
| Multi-file feature | No | Yes |
| 2 hours available | Yes | No |
| 4+ hours available | No | Yes |
| First time building this type | No | Yes |
| Refining / extending existing | Yes | Sometimes |

---

## Why the 15-Minute Scout Cap

Scout creep is the #1 killer of lightning sprints. The scout is not research — it is a yes/no NORTHSTAR check and a scope lock. If you need more than 15 minutes of discovery, you do not have enough clarity for a lightning sprint. Run a standard sprint instead.

The 75-minute build phase only works if the scope is locked before it starts. Scout caps enforce that discipline.
