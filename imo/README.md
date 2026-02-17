# imo/

This folder contains the Math Olympiad (IMO) demo code and tests.

Primary runnable artifact:
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`

Code:
- `imo/src/imo_2024_solver_proper.py` (deterministic/offline path)
- `imo/src/geometry_lemma_library.py` (executable lemma scaffolding)
- `imo/src/imo_solver_real.py` (optional LLM-backed path)

## Proof Pipeline (Prime Diagram)

```mermaid
flowchart TB
  P["Problem statement"] --> PARSE["Parse -> formal objects"]
  PARSE --> LEM["Lemma library (executable)"]
  LEM --> WIT["Witnesses (lane-tagged evidence)"]
  WIT --> CHECK["Checks / tests"]
  CHECK --> OUT["Solved artifact + verification output"]
```

## Verification Ladder (Prime Rungs)

```mermaid
flowchart LR
  R641["641: sanity"] --> R274177["274177: stress"] --> R65537["65537: gate"]
```

## Run

```bash
python -m nbconvert --execute --to notebook --inplace HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb
```

