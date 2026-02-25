---
id: review-combo
type: combo
wish: review
recipe: review-security-scan-veto
agents: [skeptic]
skills: [prime-safety, prime-coder]
rung_target: 641
model_tier: sonnet
description: "Code review with edge case detection and quality gates"
---

# Review Combo

## Agents
- **skeptic** (sonnet) -- review code quality, detect edge cases, verify correctness

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (quality gates, evidence bundle)

## Execution Flow

```mermaid
flowchart LR
    A[Read Code Changes] --> B[Check Style & Conventions]
    B --> C[Analyze Logic]
    C --> D[Detect Edge Cases]
    D --> E[Run Tests]
    E --> F{Quality Gate Passed?}
    F -->|Yes| G[Evidence Bundle]
    F -->|No| H[Document Issues]
    H --> G
```

## Evidence Required
- review_findings.json (issues found, categorized by severity)
- edge_cases.json (identified edge cases and their coverage)
- test_results.json (test pass/fail status)
- env_snapshot.json (reproducibility)

## Notes
- Skeptic agent is adversarial by design -- it looks for problems
- Review findings include severity classification: critical, warning, info
- Edge case detection is mandatory -- every review must check boundary conditions
