---
id: performance-combo
type: combo
wish: performance
agents: [coder]
skills: [prime-safety, prime-coder]
rung_target: 641
model_tier: sonnet
description: "Performance optimization with benchmark evidence"
---

# Performance Combo

## Agents
- **coder** (sonnet) -- profile bottlenecks, optimize code, benchmark before and after

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (evidence bundle, test gate)

## Execution Flow

```mermaid
flowchart LR
    A[Profile Baseline] --> B[Identify Bottleneck]
    B --> C[Apply Optimization]
    C --> D[Benchmark After]
    D --> E{Improvement Verified?}
    E -->|Yes| F[Run Regression Tests]
    F --> G{No Regressions?}
    G -->|Yes| H[Evidence Bundle]
    G -->|No| C
    E -->|No| B
```

## Evidence Required
- benchmark_before.json (baseline performance metrics)
- benchmark_after.json (optimized performance metrics)
- test_results.json (no regressions)
- PATCH_DIFF (optimization code)
- env_snapshot.json (reproducibility)
