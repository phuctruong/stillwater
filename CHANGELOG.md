# Changelog

All notable changes to Stillwater are documented here.

## [1.3.0] — 2026-02-20

### Added
- **SOFTWARE-5.0-PARADIGM.md** — Bruce Lee / martial arts framing of the Software 5.0 paradigm
- **AI-UPLIFT.md** — coins "AI Uplift": the measurable delta of skill-loaded vs raw LLM sessions
- **QUICKSTART.md** — 5-minute onboarding guide for new users
- **CONTRIBUTING.md** — root-level contribution guide with verification rung table
- **docs/skills-browser.html** — interactive skill browser (search, filter by rung/type/tag)
- **skills/prime-reviewer.md** — Lane A/B/C typed code review; only Lane A may block
- **skills/prime-mcp.md** — MCP server creation with per-tool security declarations (rung 65537)
- **skills/prime-hooks.md** — All 13 Claude Code hook event types + UV single-file Python templates
- **skills/phuc-loop.md** — Autonomous loop with halting certificates (Stillwater-grade Ralph pattern)
- **swarms/learner.md** — Ada Lovelace persona; Claudeception skill self-extraction pattern
- **swarms/** — 17 typed swarm agents (scout, forecaster, judge, coder, skeptic, mathematician, writer, janitor, security-auditor, context-manager, planner, graph-designer, podcast, social-media, wish-manager, final-audit, learner)
- **community/** — SKILL-AUTHORING-GUIDE, RECIPE-AUTHORING-GUIDE, SWARM-DESIGN-GUIDE, SCORING-RUBRIC
- **recipes/** — 8 community recipes (null-zero-audit, dual-fsm-detection, skill-expansion, swarm-pipeline, etc.)
- **papers/23–26** — Software 5.0 extension economy, skill scoring theory, persona-based review, community skill database
- **ripples/** — Per-instance customization layer (data-science, security-audit, web-dev templates)
- **MANIFEST.json** — Full repo manifest
- **.github/workflows/publish.yml** — OIDC trusted publisher workflow (auto-publishes on `v*` tag)
- LEK corrected throughout: **Law of Emergent Knowledge** (from *phuc.net/books/law-of-emergent-knowledge/*)

### Changed
- CLI version aligned: `__init__.py` + `pyproject.toml` both at `1.3.0`
- Package name on PyPI: `stillwater` (was `stillwater-os`)
- `papers/05-software-5.0.md` — LEK definition corrected, All-In podcast data added
- `SOFTWARE-5.0-PARADIGM.md` — economics section sharpened with Jason Calacanis $300/day quote
- All core skills — QUICK LOAD summary blocks added for tiered loading
- `pyproject.toml` — added `[tool.pytest.ini_options]` with explicit testpaths

### Fixed
- `stillwater --version` version drift (was showing 1.2.4 while pyproject.toml said 1.3.0)
- Missing root `CONTRIBUTING.md` (README linked to it; now created)

### Published
- **PyPI:** `pip install stillwater` — [pypi.org/project/stillwater/](https://pypi.org/project/stillwater/)

---

## [1.2.4] — 2026-01-15

- v1.2.4 baseline: core skills, phuc-forecast, prime-coder, prime-safety, phuc-swarms
- IMO benchmark notebooks
- Oolong solver
- SWE diagnostic

---

## [1.0.0] — 2025-10-01

- Initial release: Software 5.0 thesis, verification ladder concept, lane algebra
