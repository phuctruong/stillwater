---
id: design-combo
type: combo
wish: design
agents: [planner]
skills: [prime-safety, prime-coder]
rung_target: 641
model_tier: sonnet
description: "System design with architecture diagrams and interface specs"
---

# Design Combo

## Agents
- **planner** (sonnet) -- design system architecture, define interfaces, produce diagrams

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (interface specifications, evidence bundle)

## Execution Flow

```mermaid
flowchart LR
    A[Gather Requirements] --> B[Design Architecture]
    B --> C[Define Interfaces]
    C --> D[Draw Diagrams]
    D --> E[Review Feasibility]
    E --> F{Design Sound?}
    F -->|Yes| G[Evidence Bundle]
    F -->|No| B
```

## Evidence Required
- design.md (architecture document with diagrams)
- interfaces.json (API or module interface specifications)
- feasibility_check.json (resource and complexity assessment)
- env_snapshot.json (reproducibility)

## Notes
- Design combo produces artifacts, not code
- Output feeds into feature-combo or refactor-combo for implementation
- Diagrams use mermaid format for version-control friendliness
