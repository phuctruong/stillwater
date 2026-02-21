# Changelog

All notable changes to Stillwater are documented here.

## [1.5.0] — 2026-02-21

### The Stillwater Store Opens

> "Be water, my friend." — Bruce Lee

The Stillwater Store is a gated, account-required marketplace for official AI skills
(Apple App Store model). To be listed, you need an account. To submit, you need an API key.
Ecosystem lock-in begins here.

### Added

- **`STORE.md`** — Stillwater Store policy doc, developer agreement, submission process
- **`POST /stillwater/accounts/register`** — account registration API; returns `sw_sk_` API key
- **`GET /stillwater/accounts/me`** — profile endpoint (requires Bearer sw_sk_...)
- **Auth middleware** on `POST /suggest` — all Store submissions require `Authorization: Bearer sw_sk_...`
- **`GET /stillwater/health/persistence`** — distinguishes Firestore vs in-memory mode
- **`stillwater evidence init [--dir]`** — scaffold all 11 prime-coder evidence template files
- **`stillwater evidence verify [--dir] [--rung]`** — validate evidence bundle at rung 641/274177/65537
- **`web/start.sh`** — replaces supervisord; explicit health-wait + autorestart loop for uvicorn; Firestore fully connected on Cloud Run
- **Bandit + pip-audit in CI** (`ci.yml` and `publish.yml`) — supply chain security gate
- **`skills/prime-moltbot.md` v1.1.0** — FSM includes REGISTER_ACCOUNT as step 0; Store auth header in submit
- **`web/stillwater/store.html`** — Stillwater Store skills browser at `www.solaceagi.com/stillwater/store.html`
- **Case study integrity** — 5 fabricated case studies with invented author names deleted; only 2 real ones remain

### Infrastructure

- Single-container nginx + uvicorn deployment on Cloud Run (us-central1)
- Build context changed from `web/` to repo root (enables COPY from `solace/api/`)
- Cloud Build trigger fixed: uses `web/Dockerfile`, deploys on port 80
- `--min-instances 1` + `--cpu-boost` for reduced cold-start latency

### Fixed

- uvicorn single-worker mode (removed `--workers 2` which caused Cloud Run instability)
- api_server.py import path bug (`stillwater_router` is in `/app/`, not `/solace/api/`)
- Fake case studies with invented author names (violated editorial integrity)

---

## [1.4.0] — 2026-02-20

### Added

- **AI-bootstrapped community commons** — community/ onboarding docs, scoring rubric
- **MoltBot integration** — `skills/prime-moltbot.md` v1.0.0 for Store submission workflow
- **papers/27-30** — The Cheating Theorem, Software 5.0 in One Session, AI-native community platform
- **`AI-UPLIFT.md`** — manifesto: measurable uplift from skill-loaded vs raw LLM sessions
- **swarms/learner.md** — Ada Lovelace persona; Claudeception skill self-extraction pattern
- **Competitive analysis** — v4 score: 81/100 (vs 77 in v3)

---

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
