# Contributing to Stillwater

> "Absorb what is useful, discard what is useless, add what is essentially your own." — Bruce Lee

## Session Protocol (Start Here)

Stillwater uses a **haiku-first orchestration model**. Open Claude Code with haiku as the main session
coordinator. Sub-agents (sonnet/opus) do the domain work via swarms.

```
1. /northstar   → load NORTHSTAR.md (mission + model strategy)
2. /remember    → reload persistent memory from .claude/memory/context.md
3. work         → natural language OR /phuc-swarm for guaranteed dispatch
4. /remember    → save decisions before closing session
```

**When to use `/phuc-swarm` explicitly:**
If Claude starts writing code or doing deep work inline instead of dispatching a swarm — that's
the `INLINE_DEEP_WORK` forbidden state. Use `/phuc-swarm coder "..."` to force correct dispatch.

| Role | Command | Model | When to use |
|---|---|---|---|
| Coder | `/phuc-swarm coder "..."` | sonnet | bugfix, feature, refactor |
| Planner | `/phuc-swarm planner "..."` | sonnet | architecture, design |
| Skeptic | `/phuc-swarm skeptic "..."` | sonnet | verify, review |
| Mathematician | `/phuc-swarm mathematician "..."` | opus | proofs, exact arithmetic |
| Security | `/phuc-swarm security "..."` | opus | security audit, exploit review |
| Scout | `/phuc-swarm scout "..."` | haiku | research, inventory |

---

## Quick Links

| Contribution Type | Guide |
|---|---|
| Skills, recipes, swarm agents | [`community/CONTRIBUTING.md`](community/CONTRIBUTING.md) |
| Skill authoring | [`community/SKILL-AUTHORING-GUIDE.md`](community/SKILL-AUTHORING-GUIDE.md) |
| Recipe authoring | [`community/RECIPE-AUTHORING-GUIDE.md`](community/RECIPE-AUTHORING-GUIDE.md) |
| Swarm design | [`community/SWARM-DESIGN-GUIDE.md`](community/SWARM-DESIGN-GUIDE.md) |
| Papers | Follow existing structure in [`papers/`](papers/); see [`papers/00-index.md`](papers/00-index.md) |

## Code Contributions (tests, notebooks, CLI)

1. Fork and clone the repo
2. Install: `pip install -e .`
3. Start session: `claude --model haiku` → `/northstar` → `/remember`
4. Run tests: `pytest imo/tests/ -x`
5. All skill/recipe/swarm changes must pass the appropriate verification rung (641 → 274177 → 65537)
6. Open a PR — reviewers will apply [`skills/prime-reviewer.md`](skills/prime-reviewer.md) discipline

## Verification Rungs

| Rung | Meaning | Required For |
|---|---|---|
| 641 | Local correctness (red/green gate + no regressions) | Any PR |
| 274177 | Stability (seed sweep + replay) | New skills/swarms |
| 65537 | Promotion (adversarial + security + drift explained) | Security-touching, API surface changes |

See [`papers/03-verification-ladder.md`](papers/03-verification-ladder.md) for the full ladder specification.
