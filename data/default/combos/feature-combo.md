---
id: feature-combo
type: combo
wish: feature
agents: [coder]
skills: [prime-safety, prime-coder]
rung_target: 641
model_tier: sonnet
description: "New feature development with test coverage"
---

# Feature Combo

## Agents
- **coder** (sonnet) -- implement new feature, write tests, ensure coverage

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (evidence bundle, test gate)

## Execution Flow

```mermaid
flowchart LR
    A[Understand Requirements] --> B[Design Implementation]
    B --> C[Write Code]
    C --> D[Write Tests]
    D --> E[Run Tests]
    E --> F{All Green?}
    F -->|Yes| G[Evidence Bundle]
    F -->|No| C
```

## Evidence Required
- test_results.json (all tests pass)
- PATCH_DIFF (new feature code)
- env_snapshot.json (reproducibility)
