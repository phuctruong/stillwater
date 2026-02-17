# Stillwater OS

Mission: `MESSAGE-TO-HUMANITY.md`

This repo is documentation-first and runnable:
- papers: `papers/00-index.md`
- notebooks: runnable demos (offline by default)
- skills: prompt-loadable packs for coding, math, safety, orchestration

```mermaid
flowchart TB
  H["MESSAGE-TO-HUMANITY.md"] --> IDX["papers/00-index.md"]
  IDX --> P["papers/*.md"]
  IDX --> N["Root notebooks (*.ipynb)"]
  IDX --> S["skills/*.md"]
  N --> A["Artifacts: outputs cached in notebooks"]
  S --> A
```

## Start Here (Prime Path)

1. Read `MESSAGE-TO-HUMANITY.md` (why this exists).
2. Run `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb` (how the orchestration works).
3. Skim `papers/00-index.md` (map of concepts and what is verifiable here).

## What To Run

Notebooks (portable demo mode runs offline by default):
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`

SWE guide (markdown):
- `HOW-TO-CRUSH-SWE-BENCHMARK.md`

## Quick Start

```bash
python -m pip install -e ".[dev]"
```

Execute a notebook (writes outputs back into the notebook for peer review):
```bash
python -m nbconvert --execute --to notebook --inplace PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb
```

## Phuc Swarms (DREAM -> VERIFY)

```mermaid
stateDiagram-v2
  [*] --> DREAM
  DREAM --> FORECAST
  FORECAST --> DECIDE
  DECIDE --> ACT
  ACT --> VERIFY
  VERIFY --> [*]
```

## Verification Ladder (Prime Rungs)

```mermaid
flowchart LR
  R641["641: Edge sanity"] --> R274177["274177: Stress / determinism"]
  R274177 --> R65537["65537: Production gate"]
```

## Optional: Enable LLM-Backed Runs

Default configuration is offline demo mode (`llm_config.yaml` provider `offline`).

To enable LLM-backed cells (optional):
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

```mermaid
sequenceDiagram
  participant NB as Notebook
  participant CFG as LLM Config (llm_config.yaml)
  participant WR as Local Wrapper (optional)
  participant CLI as Claude CLI (optional)
  NB->>CFG: read provider
  alt offline demo (default)
    CFG-->>NB: provider=offline
    NB-->>NB: deterministic demo path
  else LLM-backed
    CFG-->>NB: provider=claude-code / api
    NB->>WR: POST /api/generate
    WR->>CLI: invoke model
    CLI-->>WR: text
    WR-->>NB: response
  end
```

## Notes On Claims

This repo tries to be conservative:
- if something is reproducible, it should be runnable here and linked
- if a number/percentage is not reproduced here, treat it as a hypothesis

## Helper CLI

After install:
```bash
stillwater print
stillwater paths --json
```

## Contributing

See `CONTRIBUTING.md`.
