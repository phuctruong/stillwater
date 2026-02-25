---
id: bugfix-combo
type: combo
wish: bugfix
recipe: bugfix
agents: [coder, skeptic]
skills: [prime-safety, prime-coder]
rung_target: 641
model_tier: sonnet
description: "Systematic bug fixing with red/green test gate"
---

# Bugfix Combo

## Agents
- **coder** (sonnet) -- localize bug, write failing test, apply fix, run tests
- **skeptic** (sonnet) -- verify fix doesn't introduce regressions, check edge cases

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (red/green gate, evidence bundle)

## Execution Flow

```mermaid
flowchart LR
    A[Localize Bug] --> B[Write Red Test]
    B --> C[Apply Fix]
    C --> D[Run Tests]
    D --> E{All Green?}
    E -->|Yes| F[Evidence Bundle]
    E -->|No| C
```

## Evidence Required
- test_results.json (red-to-green proof)
- PATCH_DIFF (the actual fix)
- env_snapshot.json (reproducibility)
