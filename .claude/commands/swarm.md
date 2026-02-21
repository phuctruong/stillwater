# /swarm — Launch a Single Typed Swarm Agent

Dispatch one typed sub-agent with the correct model, skill pack, and CNF capsule. Enforces phuc-orchestration discipline — no inline deep work, no skill-less dispatch.

## Usage

```
/swarm scout    "map the oauth3/ directory and list all missing files"
/swarm coder    "implement AgencyToken schema in oauth3/token.py"
/swarm skeptic  "verify the coder's AgencyToken implementation at rung 274177"
/swarm planner  "design the OAuth3 consent flow for solace-browser"
/swarm writer   "write the OAuth3 spec for papers/oauth3-spec-v0.1.md"
/swarm math     "prove the behavioral hash collision bound for rung 65537"
/swarm security "audit oauth3/enforcement.py for injection vulnerabilities"
/swarm janitor  "clean up stale evidence/ artifacts older than 7 days"
/swarm --list   # Show all roles + models + skill packs
```

ARGUMENTS: $ARGUMENTS

## Role Registry

| Role | Model | Skill Pack | Rung Default | When To Use |
|------|-------|-----------|--------------|-------------|
| `scout` | haiku | prime-safety | 641 | File mapping, gap analysis, research |
| `janitor` | haiku | prime-safety + phuc-cleanup | 641 | Cleanup, archival, log hygiene |
| `graph-designer` | haiku | prime-safety + prime-mermaid | 641 | State machines, FSM diagrams, PM triplets |
| `coder` | sonnet | prime-safety + prime-coder | 641 | Bugfix, feature, refactor, new files |
| `planner` | sonnet | prime-safety + phuc-forecast | 641 | Architecture, risk analysis, roadmap |
| `forecaster` | sonnet | prime-safety + phuc-forecast | 641 | DREAM→FORECAST→DECIDE→ACT→VERIFY cycle |
| `skeptic` | sonnet | prime-safety + prime-coder + phuc-forecast | 274177 | Verification, review, red-team |
| `writer` | sonnet | prime-safety + software5.0-paradigm | 641 | Papers, docs, whitepapers, long-form |
| `mathematician` | opus | prime-safety + prime-math | 274177 | Proofs, exact computation, hash bounds |
| `security-auditor` | opus | prime-safety + prime-coder | 65537 | Security scans, exploit repro, gate check |
| `final-audit` | opus | prime-safety + prime-coder + phuc-forecast | 65537 | Promotion gate, rung 65537 seal |

## NORTHSTAR Load (Mandatory)

Every `/swarm` dispatch automatically:
1. Reads NORTHSTAR.md from the current project directory
2. Injects the northstar metric into the agent's CNF capsule
3. Asks: does this task serve the northstar? (ALIGNED / DRIFT)

NORTHSTAR paths:
- /home/phuc/projects/stillwater/NORTHSTAR.md
- /home/phuc/projects/solace-browser/NORTHSTAR.md
- /home/phuc/projects/solace-cli/NORTHSTAR.md
- /home/phuc/projects/solaceagi/NORTHSTAR.md

## Instructions for Claude

When user runs `/swarm [role] "[task]"`:

### Step 1 — Validate Input
1. Role must be in the table above. If unknown: list valid roles and stop.
2. Task must be quoted string. If missing: ask for it.
3. Detect project from cwd or from task text (look for project keywords).

### Step 2 — Load NORTHSTAR
Read the project's NORTHSTAR.md. Extract:
- Mission (1 line)
- Northstar metric (the key number: stars / rung / hit rate / MRR)
- Current rung

### Step 3 — Load Skill Files
From `/home/phuc/projects/stillwater/skills/`:
- Always load: `prime-safety.md` (FULL content — never summarized)
- Load domain skill per role (see table above):
  - prime-coder.md for coder/skeptic/security-auditor
  - phuc-forecast.md for planner/forecaster/skeptic/final-audit
  - phuc-cleanup.md for janitor
  - prime-mermaid.md for graph-designer
  - prime-math.md for mathematician
  - software5.0-paradigm.md for writer

### Step 4 — Determine Rung Target
- Use table default unless:
  - Task contains "security" / "audit" / "rung 65537" → upgrade to 65537
  - Task contains "verify" / "review" / "skeptic" → minimum 274177
  - User explicitly states rung in task → use that rung

### Step 5 — Build CNF Capsule

```
You are a [ROLE] agent (model: [MODEL]).

NORTHSTAR (mandatory context — do not ignore):
  Project: [project]
  Mission: [1 line from NORTHSTAR.md]
  Northstar metric: [key metric]
  Current rung: [current rung]
  NORTHSTAR alignment: ALIGNED (confirmed before dispatch)

## Loaded Skills

<BEGIN_SKILL name="prime-safety" version="2.1.0">
[FULL CONTENT of skills/prime-safety.md — no summarization]
</BEGIN_SKILL>

<BEGIN_SKILL name="[domain-skill]" version="[version]">
[FULL CONTENT of skills/[domain-skill].md — no summarization]
</BEGIN_SKILL>

## Task (CNF Capsule)

task_id:       [ROLE]-[DATE]-[SHORT_HASH]
task_request:  [FULL task text — no "as before", no "as discussed"]
project:       [project name]
project_path:  [absolute path]
constraints:   [explicit constraints from context]
context:       [full relevant context — no summaries, no references]
rung_target:   [641 | 274177 | 65537]
model:         [haiku | sonnet | opus]

## Expected Artifacts

[List exactly what this agent must produce — file paths, JSON schemas, test logs]

## Stop Rules

EXIT_PASS if:
  - [concrete measurable condition 1]
  - [concrete measurable condition 2]
  - evidence artifacts all exist on disk

EXIT_BLOCKED if:
  - fatal blocker encountered (list it explicitly)
  - evidence cannot be produced
  - rung_target cannot be met without scope expansion

EXIT_NEED_INFO if:
  - required input is missing or ambiguous

## Forbidden States (loaded from prime-safety)

- UNWITNESSED_PASS: never claim PASS without artifacts
- SILENT_RELAXATION: never lower the rung without explicit approval
- NULL_ZERO_COERCION: never coerce null to 0 or ""
- INLINE_DEEP_WORK: sub-agents must not do >100 lines without evidence gates
- SUMMARY_AS_EVIDENCE: prose "it works" is not evidence
```

### Step 6 — Dispatch and Await

Dispatch via Task tool with correct subagent_type:
- haiku roles: use haiku
- sonnet roles: use sonnet
- opus roles: use opus

Await artifacts. Reject prose summaries as Lane A evidence.

### Step 7 — Report

```
=== SWARM COMPLETE: [ROLE] ===
Role:        [role]
Model:       [model]
Rung target: [rung]
Rung achieved: [actual rung from agent]
NORTHSTAR: ALIGNED

Artifacts received:
  [list actual artifact files]

Integration rung: MIN([coder rung], [skeptic rung]) = [integration rung]

Status: PASS | BLOCKED | NEED_INFO
```

## When user runs `/swarm --list`

Display the full role registry table above. Check each skill file exists:

```
=== SWARM ROLES AVAILABLE ===

Role              Model    Default Rung   Skill Pack              Status
scout             haiku    641            prime-safety            ✅
janitor           haiku    641            prime-safety+cleanup    ✅
graph-designer    haiku    641            prime-safety+mermaid    ✅
coder             sonnet   641            prime-safety+coder      ✅
planner           sonnet   641            prime-safety+forecast   ✅
forecaster        sonnet   641            prime-safety+forecast   ✅
skeptic           sonnet   274177         prime-safety+coder+fc   ✅
writer            sonnet   641            prime-safety+sw5.0      ✅
mathematician     opus     274177         prime-safety+math       ✅
security-auditor  opus     65537          prime-safety+coder      ✅
final-audit       opus     65537          prime-safety+coder+fc   ✅

Skills directory: /home/phuc/projects/stillwater/skills/
```

## Swarm Rung = MIN(all contributing agents)

If coder achieves rung 641 and skeptic achieves rung 274177:
Integration rung = 641. Never claim higher than the minimum.

## Forbidden States

- `SKILL_LESS_DISPATCH` — dispatched without full skill content pasted inline
- `FORGOTTEN_CAPSULE` — agent prompt says "as before", "as discussed", "recall that"
- `NORTHSTAR_SKIPPED` — NORTHSTAR.md not read before dispatch
- `WRONG_MODEL` — haiku for security-auditor, opus for scout (unnecessary cost + capability mismatch)
- `RUNG_UNDECLARED` — rung_target not in CNF capsule
- `SUMMARY_AS_EVIDENCE` — agent prose accepted as Lane A evidence

## Related Commands

- `/build [project] [phase]` — Full build session with Scout → Forecaster → Coder → Skeptic pipeline
- `/phuc-swarm [role] "[task]"` — Alias; same behavior as /swarm
- `/status` — Check ecosystem status before dispatching
- `/northstar` — Load NORTHSTAR for current project
