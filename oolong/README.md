# oolong/

OOLONG is the “long context aggregation” demo in this repo.

Primary runnable artifact:
- `HOW-TO-OOLONG-BENCHMARK.ipynb`

Code:
- `oolong/src/oolong_solver.py` (deterministic/offline path)
- `oolong/src/oolong_solver_real.py` (optional LLM-backed path)

## Counter Bypass (Prime Diagram)

```mermaid
flowchart LR
  Q["Question / text"] --> CLASS["LLM classifies (optional)"]
  CLASS --> CPU["CPU enumerates (Counter)"]
  CPU --> OUT["Deterministic counts"]
```

## Verification Ladder (Prime Rungs)

```mermaid
flowchart LR
  R641["641: edge sanity"] --> R274177["274177: stress / determinism"]
  R274177 --> R65537["65537: explanation / review gate (demo)"]
```

## Run

```bash
python -m nbconvert --execute --to notebook --inplace HOW-TO-OOLONG-BENCHMARK.ipynb
```
