# Skills

> "Absorb what is useful, discard what is useless, and add what is specifically your own." — Bruce Lee

Prompt-loadable skill packs. Each file is a structured YAML/markdown constraint pack. Load the full file — do not summarize or compress. Compressed skills drift.

**Version:** 1.0.0 | **Date:** 2026-02-20 | **Auth:** 65537

---

## Core Skills (Load These First)

| Skill | What It Does | When To Load |
|-------|-------------|--------------|
| `prime-safety.md` | Tool safety, authority ordering, fail-closed envelope | Always. Load first. |
| `prime-coder.md` | RED/GREEN gate, evidence contract, verification ladder | Any coding or patching task |
| `phuc-forecast.md` | DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY loop | Planning, architecture, decisions |
| `phuc-context.md` | Context Normal Form, anti-rot capsule, compaction | Long sessions, multi-agent chains |

The `core/` directory at repo root contains always-on canonical copies of these four skills. They serve as the baseline for divergence detection.

---

## Verification Ladder (Rung Targets)

Every skill-backed task must declare a rung target before claiming PASS. Like belt ranks, you earn them — you do not claim them.

| Rung | Belt Equivalent | What You Prove |
|------|----------------|----------------|
| **641** | White belt of proof | Local correctness: RED/GREEN gate passed, no regressions, evidence complete |
| **274177** | Brown belt of proof | Stability: seed sweep (3+ seeds), replay stability, null edge cases covered |
| **65537** | Black belt of proof | Promotion: adversarial sweeps, security gate, behavioral hash drift explained |

---

## Specialist Skills

| Skill | What It Does |
|-------|-------------|
| `prime-math.md` | Witness-first reasoning, exact arithmetic, halting certificates |
| `phuc-orchestration.md` | Multi-agent dispatch, swarm phase ownership, context isolation |
| `phuc-swarms.md` | Swarm design, agent chain FSM, phase handoff contracts |

---

## Swarm Agent Types (swarms/)

Each file in `swarms/` defines a typed agent role: persona, skill pack, required artifacts, FSM, and forbidden states. Load as a sub-agent session with a CNF capsule.

| File | Agent Role | Persona | Skill Pack | Default Rung |
|------|-----------|---------|------------|-------------|
| `swarms/scout.md` | Map codebase, identify gaps | Ken Thompson | prime-safety + prime-coder | 641 |
| `swarms/forecaster.md` | Plan and premortem | Grace Hopper | prime-safety + phuc-forecast | 641 |
| `swarms/judge.md` | Score and approve artifacts | Ada Lovelace | prime-safety + prime-coder | 274177 |
| `swarms/coder.md` | Write patches with evidence | Donald Knuth | prime-safety + prime-coder | 641 |
| `swarms/skeptic.md` | Challenge and stress-test | Alan Turing | prime-safety + prime-coder | 274177 |
| `swarms/mathematician.md` | Exact arithmetic and proofs | Emmy Noether | prime-safety + prime-math | 274177 |
| `swarms/writer.md` | Write clear human-readable docs | Richard Feynman | prime-safety + software5.0-paradigm | 641 |
| `swarms/janitor.md` | Clean up and simplify | Edsger Dijkstra | prime-safety + prime-coder | 641 |
| `swarms/security-auditor.md` | Security scan and exploit repro | Bruce Schneier | prime-safety + prime-coder | 65537 |
| `swarms/context-manager.md` | Context hygiene and CNF capsules | Barbara Liskov | prime-safety + phuc-context | 641 |
| `swarms/planner.md` | Structured planning and milestones | Grace Hopper | prime-safety + phuc-forecast | 641 |
| `swarms/graph-designer.md` | Architecture diagrams and flows | Ada Lovelace | prime-safety | 641 |
| `swarms/podcast.md` | Podcast scripts and dialogue | Richard Feynman | prime-safety | 641 |
| `swarms/social-media.md` | Social content, hooks, thumbnails | MrBeast | prime-safety + phuc-forecast | 641 |
| `swarms/wish-manager.md` | Wish decomposition and tracking | Ada Lovelace | prime-safety + phuc-forecast | 641 |
| `swarms/final-audit.md` | Final Audit (repo-wide compliance) | Linus Torvalds | prime-safety + prime-coder + phuc-forecast | 65537 |

---

## Rule: Load Skills Whole

Do not summarize, paraphrase, or compress a skill file before loading it. The invariants are in the structure. A summarized skill is a broken skill.

---

## See Also

- `community/GETTING-STARTED.md` — how to use skills, recipes, and swarms
- `community/SKILL-AUTHORING-GUIDE.md` — how to write a new skill
- `community/SCORING-RUBRIC.md` — 5-criterion binary scorecard for skill quality
- `papers/00-index.md` — theory behind the verification ladder and gate system

---

## Author

**Phuc Vinh Truong** — Coder, entrepreneur, theorist, writer.

| Link | URL |
|---|---|
| Personal site | https://www.phuc.net |
| IF Theory (physics) | https://github.com/phuctruong/if |
| PZIP (compression) | https://www.pzip.net |
| SolaceAGI (persistent AI) | https://www.solaceagi.com |
| Support this work | https://ko-fi.com/phucnet |
| Contact | phuc@phuc.net |
| GitHub | https://github.com/phuctruong |
| Stillwater repo | https://github.com/phuctruong/stillwater |

*Building open, reproducible, verifiable AI infrastructure — "Linux of AGI."*
