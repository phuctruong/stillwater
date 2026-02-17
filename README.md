# Stillwater OS (Open Repo)

This repo is an open, runnable documentation spine for the mission in `MESSAGE-TO-HUMANITY.md`.

It contains:
- `papers/`: first-principles notes + operational papers (start at `papers/00-index.md`)
- `skills/`: prompt-loadable “skills” for coding, math, safety, and orchestration
- root notebooks: peer-reviewable demos that execute end-to-end
- `src/`: a local wrapper + LLM config helpers (optional)

## What To Run (Start Here)

Notebooks (portable demo mode runs offline by default):
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`

SWE guide (markdown):
- `HOW-TO-CRUSH-SWE-BENCHMARK.md`

Papers index:
- `papers/00-index.md`

## Quick Start

```bash
python -m pip install -e ".[dev]"
```

Execute a notebook (writes outputs back into the notebook for peer review):
```bash
python -m nbconvert --execute --to notebook --inplace PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb
```

## Optional: Enable LLM-Backed Runs

Some scripts can call a local HTTP wrapper (Claude Code wrapper or equivalent).

1. Read `src/WRAPPER-SETUP-GUIDE.md`
2. Start the wrapper (example):
```bash
python3 src/claude_code_wrapper.py --port 8080
```
3. Enable LLM-backed cells:
```bash
export STILLWATER_ENABLE_LLM_REAL=1
export STILLWATER_WRAPPER_URL=http://localhost:8080/api/generate
```

## Notes On Claims

This repo tries to be conservative:
- If something is reproducible, it should be runnable here and linked.
- If a number/percentage is not reproduced here, treat it as a hypothesis.

## Helper CLI

After install:
```bash
stillwater print
stillwater paths --json
```

## Contributing

See `CONTRIBUTING.md`.

