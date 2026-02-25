---
id: docs-combo
type: combo
wish: docs
agents: [writer]
skills: [prime-safety]
rung_target: 641
model_tier: haiku
description: "Documentation writing with accuracy verification"
---

# Docs Combo

## Agents
- **writer** (haiku) -- write clear documentation, verify accuracy against code

## Skill Pack
- prime-safety (god-skill, always first)

## Execution Flow

```mermaid
flowchart LR
    A[Read Source Code] --> B[Identify Gaps]
    B --> C[Draft Documentation]
    C --> D[Verify Against Code]
    D --> E{Accurate?}
    E -->|Yes| F[Evidence Bundle]
    E -->|No| C
```

## Evidence Required
- PATCH_DIFF (documentation changes)
- accuracy_check.json (cross-reference of docs against actual code behavior)
- env_snapshot.json (reproducibility)

## Notes
- Uses **haiku** model tier -- documentation does not require heavy reasoning
- Writer agent focuses on clarity, completeness, and accuracy
- No test gate required, but accuracy verification against source is mandatory
