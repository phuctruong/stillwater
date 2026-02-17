# Papers

Start here: `00-index.md`

This folder is the long-form documentation for the concepts used by the runnable artifacts in repo.

## Map (Papers -> Artifacts)

```mermaid
flowchart TB
  IDX["papers/00-index.md"] --> LA["papers/01-lane-algebra.md"]
  IDX --> CB["papers/02-counter-bypass.md"]
  IDX --> VL["papers/03-verification-ladder.md"]
  IDX --> RG["papers/04-red-green-gate.md"]
  IDX --> SW["papers/05-software-5.0.md"]

  LA --> N3["PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb"]
  CB --> N1["HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb"]
  VL --> N2["HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb"]
  RG --> N3
  SW --> N3

  IDX --> SWE["HOW-TO-CRUSH-SWE-BENCHMARK.ipynb"]
```

## Claim Hygiene (Prime Lanes)

If a paper makes a claim, it should be clear what lane it is in:

```mermaid
flowchart LR
  A["Lane A: Proven (replayable evidence)"] --> B["Lane B: Framework truth (within an axiom system)"]
  B --> C["Lane C: Heuristic (probabilistic)"]
  C --> STAR["STAR: Unknown (insufficient evidence)"]
```

## What Reviewers Can Run

- Notebooks:
  - `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`
  - `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
  - `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
- SWE guide:
  - `HOW-TO-CRUSH-SWE-BENCHMARK.md`

## Update Rule

If you change a notebook or solver in a way that changes the conceptual story:
1. update the relevant paper(s)
2. update `00-index.md`
