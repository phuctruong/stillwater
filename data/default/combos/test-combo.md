---
id: test-combo
type: combo
wish: test
recipe: run-test
agents: [coder]
skills: [prime-safety, prime-coder]
rung_target: 641
model_tier: sonnet
description: "Comprehensive test writing with coverage analysis"
---

# Test Combo

## Agents
- **coder** (sonnet) -- write tests, analyze coverage gaps, ensure edge cases covered

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (test gate, evidence bundle)

## Execution Flow

```mermaid
flowchart LR
    A[Analyze Coverage Gaps] --> B[Write Unit Tests]
    B --> C[Write Integration Tests]
    C --> D[Run Full Suite]
    D --> E{Coverage Target Met?}
    E -->|Yes| F[Evidence Bundle]
    E -->|No| B
```

## Evidence Required
- test_results.json (all tests pass)
- coverage_report.json (coverage metrics before and after)
- PATCH_DIFF (new test code)
- env_snapshot.json (reproducibility)
