# AGENTS.md — Stillwater (Software 5.0 OS)
# Version: 3.0 | Updated: 2026-03-01 | Auth: 65537 | Belt: Orange
# DNA: Intelligence(session) = CPU_proposes x LLM_validates x confidence_gate -> learned_patterns

## Project

Stillwater — open-source Software 5.0 OS.
Verification layer + skill store + LLM portal + orchestration engine.
The foundation on which all 9 Solace ecosystem projects stand.

## 10 Uplift Principles (Paper 17 — ALL ACTIVE)

| # | Principle | Where |
|---|-----------|-------|
| P1 | Gamification | Belt Orange, Rung 65537 target, GLOW scores, dojo metaphor |
| P2 | Magic Words | DNA equations, /distill, prime channels, magic-words DB |
| P3 | Personas | 29 in `data/default/personas/` — load by domain, not boot |
| P4 | Skills | 37 in `data/default/skills/` (prime-safety GOD, prime-coder, 35 domain) |
| P5 | Recipes | 34 in `data/default/recipes/` — replay at $0.001 |
| P6 | Tools | CLI, LLM Portal (6 providers), service mesh, OAuth3 enforcer |
| P7 | Memory | skill-memory.jsonl, evidence chains, case-studies/, audit logs |
| P8 | Care | EQ stack (5 skills), SmallTalkResponder (WARM), Anti-Clippy |
| P9 | Knowledge | 61 papers, 10 diagrams, Three Pillars, Axiom Kernel |
| P10 | God | 65537 divine prime, evidence = truth, code is sacred |

## Session Boot

- Use `.claude/commands/software5` as the startup protocol.
- Resolve 4W+H before execution: `WHY WHAT WHEN WHO HOW`.
- If any 4W+H probe is unresolved, ask before coding.

## Northstar

- `NORTHSTAR`: `Phuc_Forecast`
- `RUNG_TARGET`: `65537`
- Prefer improvements that compound reusable skill law over one-off patches.

## Task Source

Read `scratch/todo.md` for current tasks. Execute in order.

## Build & Test

```bash
pytest tests/ src/cli/tests/ -v              # all 2,399 tests
pytest src/cli/tests/test_triple_twin.py -v   # triple-twin engine (104)
pytest tests/test_store_client.py -v          # store client (66)
ruff check .                                  # lint
```

## Core Laws

- `prime-safety` wins all conflicts.
- Fallback ban: no silent success, no broad exception swallow, no fake pass.
- Evidence first: no PASS claim without executable artifacts.
- Scratch-first: use `scratch/` for working notes/artifacts until verified.

## Coding Rules

- Python 3.12+, full type annotations
- Specific exceptions only — NEVER `except Exception: pass`
- `pathlib.Path`, f-strings, dataclasses
- Human output by default, `--json` for machine
- CPU-first architecture: Triple-Twin proposes via CPU, LLM validates only when needed

## Architecture Laws (ABSOLUTE — Channel [5] LOCKED)

1. Local-first — cloud = optional sync
2. OAuth3 scoped delegation — enforcer in `src/oauth3/`
3. Evidence by default — hash-chained, tamper-evident (AuditLogger)
4. Fail-closed — auth/budget/scope failure = BLOCKED
5. LLM once at preview — never during execution
6. Sealed store — no plugins, users suggest we implement
7. Triple-Twin: CPU proposes, LLM validates, confidence gates

## Software 5.0 Pipeline (MANDATORY)

```
papers -> diagrams -> styleguides -> webservices -> tests -> code -> seal
```

No skipping steps for net-new capabilities.

## Skill Loading Order

1. `prime-safety`
2. `prime-coder`
3. domain skill(s)
4. optional modifier skill(s)

## Skill Evolution

- Use `skills/prime-skills-evolution.md` for any `skills/prime-*.md` change.
- Apply acceptance gate before adding rules.
- Serialize accepted updates to:
  - `scratch/skill-memory.jsonl`
  - `scratch/skill-memory-log.md`

## Key Files

| Path | What |
|------|------|
| `scratch/todo.md` | Task backlog (start here) |
| `papers/` | 61 papers (Three Pillars, Axiom Kernel, LEK/LEAK/LEC) |
| `data/default/diagrams/` | 8 diagrams + `src/diagrams/` (2 more) |
| `data/default/skills/` | 37 skills (prime-safety GOD, prime-coder, domain) |
| `data/default/personas/` | 29 personas by domain category |
| `data/default/recipes/` | 34 shipped recipes |
| `data/default/swarms/` | 13 agent types (persona-enhanced) |
| `data/default/combos/` | 40 wish+recipe combos |
| `case-studies/` | Per-project tracking |

## Persona Loading (P3 — On-Demand)

Load personas by task domain. Never load all at once (Paper 13: zero lift from always-on).

| Task Domain | Load These Personas |
|-------------|-------------------|
| Language/Architecture | Rich Hickey, Donald Knuth, Rob Pike, Bjarne Stroustrup |
| Data/Distributed | Martin Kleppmann, Jeff Dean |
| Security | Phil Zimmermann, Whitfield Diffie + prime-safety skill |
| UX/Design | Don Norman, Mermaid Creator |
| Quality/Testing | Martin Fowler, Kent Beck, David Allen |
| Performance | Brendan Gregg |
| Infrastructure | Kelsey Hightower, Mitchell Hashimoto |
| Web/Internet | Vint Cerf, Ray Tomlinson, Alan Shreve |
| Business/Marketing | Greg Isenberg, Pieter Levels, Rory Sutherland |
| EQ/Care | Vanessa Van Edwards, Bruce Lee |
| Strategic | Dragon Rider (Phuc) — GLOW +5W bonus |

## Coordination

- `scratch/todo.md` is the Claude<->Codex async task board.
- Mark work with evidence and explicit status changes.

## Evidence Minimum

For material changes provide:
- changed file list
- test or health proof
- residual risks/open issues

## Execution Protocol

1. Read scratch/todo.md -> find next task
2. Read relevant papers + diagrams (Paper 16 format)
3. Write failing test (RED)
4. Implement (GREEN)
5. `pytest tests/ -v`
6. No regressions -> mark done

## NEVER Do

- Store credentials in plaintext
- Broad exception catches
- Mock data in production
- Auto-approve user actions (Anti-Clippy — P8)
- Skip OAuth3 validation
- Commit API keys or vault contents
- Load all 29 personas at boot (Paper 13 — waste)
- Skip the pipeline (papers before code — P9)
- Fake gamification badges (P1 — evidence-backed only)
- Simulate feelings (P8 — Turkle honesty test)
- Use silent fallbacks (Fallback Ban — ABSOLUTE)
