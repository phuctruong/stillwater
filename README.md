# Stillwater OS — Software 5.0 Dojo

> "Be water, my friend." — Bruce Lee

Stillwater is an open-source verification layer for agentic software.
It turns prompts into audited engineering artifacts with explicit gates.

## The Core Loop

`DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY`

No silent fallback. No unwitnessed pass. No fake `ok: true` on failure.

## Belt Ladder (Gamified Rungs)

| Belt | Rung | Meaning |
|---|---:|---|
| White | setup | Project runs locally |
| Yellow | 641 | Local correctness: failing case reproduced, fix verified |
| Green | 274177 | Stability sweeps and edge/null checks |
| Black | 65537 | Adversarial/security-grade release gate |

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

- `src/cli/` — CLI runtime + tests
- `src/store/` — store client/validator/packager modules
- `src/oauth3/` — OAuth3 enforcer package + tests (moved from root)
- `src/scripts/` — utility/build scripts
- `src/swe/`, `src/oolong/` — benchmark/runtime modules
- `data/default/` — default store DB (`skills`, `recipes`, `swarms`, `personas`, `combos`, `questions`, `wishes`, `diagrams`, `magic-words`)
- `data/custom/` — local user overrides
- `notebooks/` — runnable notebook playbooks
- `docs/` — long-form narrative docs and Software 5.0 companion docs
- `papers/` — architecture and theory papers
- `admin/` — admin UI + service endpoints
- `tests/` — integration/security/regression suites

## Training Routes

- Notebook training: `notebooks/`
- Long-form docs: `docs/`
- Architecture papers: `papers/`
- Use-case walkthroughs: `case-studies/`

## Verification Commands

```bash
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

## Store

Submission and policy: `STORE.md`

## Cleanup Notes

Root was cleaned for runtime focus.
Archived planning/reference materials live in `scratch/root-cleanup/`.

## License

MIT (`LICENSE`)
