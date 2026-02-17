# swe/

This folder contains SWE-bench related code and scripts.

Primary documentation artifact:
- `HOW-TO-CRUSH-SWE-BENCHMARK.md`

Code:
- `swe/src/swe_solver_real.py` (wrapper-backed solver implementation)
- `swe/src/swe_solver_unified.py` (alternative unified runner)
- `batch_1_phuc_orchestration.py` (batch orchestration driver)
- `diff_postprocessor.py` (diff repair helper)

## SWE Pipeline (Prime Diagram)

```mermaid
flowchart TB
  INST["SWE instance"] --> CTX["Context extraction"]
  CTX --> DREAM["DREAM (Scout)"]
  DREAM --> FORECAST["FORECAST (Grace)"]
  FORECAST --> DECIDE["DECIDE (Judge)"]
  DECIDE --> ACT["ACT (Solver)"]
  ACT --> FIX["Diff post-process (repair)"]
  FIX --> VERIFY["VERIFY (Skeptic)"]
  VERIFY --> ART["Artifacts: patch + verdict + logs"]
```

## Red / Green / Gold Gate

```mermaid
stateDiagram-v2
  [*] --> RED
  RED --> GREEN
  GREEN --> GOLD
  GOLD --> [*]
```

