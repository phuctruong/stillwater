# Claims And Evidence (Repo Policy)

This repo is documentation-first. Trust comes from runnable artifacts, not prose.

## Lanes (Evidence Strength)

```mermaid
flowchart LR
  A["Lane A: Replayable in-repo evidence (tests, tool output, checked artifacts)"]
  B["Lane B: Framework truth (within stated assumptions/axioms)"]
  C["Lane C: Heuristic / probabilistic (LLM output, intuition, pattern match)"]
  STAR["STAR: Unknown (insufficient evidence)"]
  A --> B --> C --> STAR
```

## Rule: Numbers Need Artifacts

If you state a numeric claim (accuracy %, success rate, failure probability, energy per query), you must provide at least one of:
- a runnable script/notebook in this repo that reproduces it, or
- a link to an external artifact (dataset + exact command + hashes) and label it **external**

Otherwise, label it as:
- **Hypothesis** (plausible but not reproduced here), or
- **Illustrative example** (toy numbers used for explanation)

```mermaid
flowchart TB
  CLAIM["Claim includes a number"] --> ART{"Has runnable artifact?"}
  ART -->|Yes| LANE_A["Lane A candidate"]
  ART -->|No| EXT{"External artifact linked?"}
  EXT -->|Yes| EXT_OK["Label: External result"]
  EXT -->|No| HYP["Label: Hypothesis / illustrative"]
```

## Rule: No Placeholder Citations

Do not ship references like `(arXiv id TBD)` or `CVE-YYYY-NNNN (placeholder)`.

If you don’t have the identifier yet:
- remove the identifier, keep author/title, and add `TODO: add id/url`

## Rule: “Formal Proof” Is Reserved

“Formal proof” is only allowed when there is a machine-checkable proof artifact and a checker.

Otherwise use:
- “proof narrative”
- “executable checks”
- “operational gate”
- “demo verification”

## Reviewer Checklist

```mermaid
flowchart TB
  R["Reviewer"] --> Q1{"Any placeholders?"}
  Q1 -->|Yes| FIX1["Remove/mark TODO"]
  Q1 -->|No| Q2{"Any strong numbers?"}
  Q2 -->|Yes| Q3{"Reproduced in repo?"}
  Q3 -->|No| FIX2["Label external/hypothesis or remove"]
  Q3 -->|Yes| OK["OK"]
```

