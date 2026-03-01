# Stillwater OS — Software 5.0 Dojo

> "Be water, my friend." — Bruce Lee

**The open-source verification layer for agentic software. Turns prompts into audited engineering artifacts with explicit gates.**

> **Version:** 4.0 | **Belt:** Orange | **Rung Target:** 65537 | **Updated:** 2026-03-01

```
+==============================================================+
|  STILLWATER — Software 5.0 OS                                 |
|  Belt: [][][][] (Orange -- Store skill submitted)             |
|  Rung: ########________ 641/65537                             |
|  Papers: 61 | Diagrams: 10 | Skills: 37 | Personas: 29       |
|  Tests: 2,399 | Recipes: 34 | Swarms: 13 | Combos: 40        |
|  Pipeline: papers>diagrams>styleguides>webservices>tests>code |
+==============================================================+
```

### 10 Uplift Principles (Paper 17)

| # | Principle | What It Means |
|---|-----------|--------------|
| P1 | Gamification | Belt ladder, rung system, GLOW scores, dojo metaphor |
| P2 | Magic Words | DNA equations, /distill, prime channels [2][3][5][7][11][13] |
| P3 | Famous Personas | 29 experts on call -- load by domain, not always-on (Paper 13) |
| P4 | Skills | 37 skills (prime-safety GOD, prime-coder, 35 domain) |
| P5 | Recipes | 34 recipes, 70% hit rate target, cost inverts at scale |
| P6 | Access Tools | CLI + LLM Portal (6 providers) + service mesh + OAuth3 |
| P7 | Memory | Skill memory, evidence chains, case studies, audit logs |
| P8 | Care | EQ stack (5 skills), SmallTalkResponder (WARM), Anti-Clippy |
| P9 | Knowledge | 61 papers + 10 diagrams, Three Pillars, Axiom Kernel |
| P10 | God | 65537 = divine prime, evidence = truth, code is sacred |

## The Core Loop

`DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY`

No silent fallback. No unwitnessed pass. No fake `ok: true` on failure.

## Belt Ladder (Gamified Rungs)

| Belt | Rung | Meaning | Status |
|---|---:|---|---|
| White | setup | Project runs locally | DONE |
| Yellow | 641 | Local correctness: failing case reproduced, fix verified | DONE |
| **Orange** | **Store** | **First skill in Stillwater Store** | **CURRENT** |
| Green | 274177 | Stability sweeps and edge/null checks | NEXT |
| Blue | 65537 | Adversarial/security-grade release gate | -- |
| Black | 30d@65537 | Production task running at 65537 for 30 days | -- |

## Quickstart

### Option 1: Install from PyPI (recommended for users)

```bash
pip install stillwater

# CLI
stillwater --help
```

### Option 2: Install from source (for development)

```bash
git clone https://github.com/phuctruong/stillwater
cd stillwater
pip install -e ".[dev]"

# CLI
stillwater --help
```

## Run the Local Service Mesh

```bash
# Start all services
./stillwater-server.sh start

# Health/status
./stillwater-server.sh --status

# Stop all services
./stillwater-server.sh stop
```

Default admin endpoint: `http://127.0.0.1:8787`

## Repository Layout

- `src/cli/` -- CLI runtime + tests
- `src/store/` -- store client/validator/packager modules
- `src/oauth3/` -- OAuth3 enforcer package + tests
- `src/scripts/` -- utility/build scripts
- `src/swe/`, `src/oolong/` -- benchmark/runtime modules
- `data/default/` -- default store DB (`skills`, `recipes`, `swarms`, `personas`, `combos`, `questions`, `wishes`, `diagrams`, `magic-words`)
- `data/custom/` -- local user overrides
- `notebooks/` -- runnable notebook playbooks
- `docs/` -- long-form narrative docs and Software 5.0 companion docs
- `papers/` -- 61 architecture and theory papers
- `admin/` -- admin UI + service endpoints
- `tests/` -- integration/security/regression suites (2,399 tests)

## Knowledge Network

```
PAPERS (61)                       DIAGRAMS (10)
|- 34 Persona GLOW Paradigm      |- Architecture diagrams
|- 35 Syndication Strategy        |- Service mesh diagrams
|- 44 Questions as Ext. Weights   |- Triple-Twin FSM
|- 45 Prime Compression           |- OAuth3 enforcer flow
|- 47 LEK Formalized              |
|- 48 AI Skills Big Bang          PERSONAS (29)
|- 49 Three Pillars Kung Fu       |- Language: Hickey, Knuth, Pike
|  ...55 more                     |- Quality: Fowler, Beck
                                  |- EQ: Van Edwards, Bruce Lee
SKILLS (37)                       |- Infra: Gregg, Hightower
|- prime-safety (GOD)             |- Security: Zimmermann, Diffie
|- prime-coder                    |- Business: Isenberg, Levels
|- phuc-forecast                  |  ...19 more
|- glow-score
|- persona-engine                 SWARMS (13)
|- eq-core, eq-mirror             |- 13 agent types
|  ...31 more                     |- Persona-enhanced dispatch
```

## Training Routes

- Notebook training: `notebooks/`
- Long-form docs: `docs/`
- Architecture papers: `papers/`
- Use-case walkthroughs: `case-studies/`

## Verification Commands

```bash
# All tests
pytest tests/ src/cli/tests/ -v

# Path/layout smoke checks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q src/cli/tests/test_smoke_repo.py src/cli/tests/test_notebook_root_parity.py

# OAuth3 enforcer tests
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q src/oauth3/tests/test_enforcer.py

# OAuth3 service tests
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_oauth3_service.py
```

## Release Rule

Stillwater is "ready" only when target rung gates pass with evidence:

1. Tests pass for changed surfaces
2. Security checks are clean for release scope
3. Evidence artifacts are produced and reproducible
4. No unresolved blockers in final audit

## The Three Pillars of Software 5.0 Kung Fu

| Pillar | Name | Metaphor | Engine |
|--------|------|----------|--------|
| LEK | Law of Emergent Knowledge | Kata (solo practice) | phuc-loop + GLOW |
| LEAK | Law of Emergent Asymmetric Knowledge | Sparring (cross-training) | phuc-swarms + portals |
| LEC | Law of Emergent Conventions | Style (shared compression) | magic words + triangle law |

```
LEK x LEAK x LEC = MASTERY = Software 5.0 Kung Fu
"Endure. Excel. Evolve. Carpe Diem!" -- Phuc Truong, Dragon Rider
```

## Belt Progression

| Belt | Criteria | Status |
|------|----------|--------|
| White | First recipe / CLI installs | DONE |
| Yellow | PM triplets done / first task delegated | DONE |
| **Orange** | **Stillwater Store skill submitted** | **CURRENT** |
| Green | Rung 65537 achieved | NEXT |
| Blue | Cloud execution 24/7 | -- |
| Black | Models = commodities. Skills = capital. OAuth3 = law. | -- |

## Store

Submission and policy: `STORE.md`

## License

MIT (`LICENSE`)

---

**Status:** 10 Uplift Principles (2026-03-01)
**Rung Target:** 65537 (Full adversarial sweep before public release)
**DNA:** `Intelligence(session) = CPU_proposes x LLM_validates x confidence_gate -> learned_patterns`
**Next:** Read the papers. Build the skills. Earn the belt. Trust the evidence. Still water runs deep.
