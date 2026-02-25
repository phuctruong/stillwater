---
id: research-combo
type: combo
wish: research
agents: [scout]
skills: [prime-safety, phuc-forecast]
rung_target: 641
model_tier: haiku
description: "Exploration and research with structured findings"
---

# Research Combo

## Agents
- **scout** (haiku) -- explore solution space, compare alternatives, produce structured findings

## Skill Pack
- prime-safety (god-skill, always first)
- phuc-forecast (structured analysis, risk assessment)

## Execution Flow

```mermaid
flowchart LR
    A[Define Research Question] --> B[Explore Sources]
    B --> C[Compare Alternatives]
    C --> D[Assess Trade-offs]
    D --> E[Structured Findings]
    E --> F[Evidence Bundle]
```

## Evidence Required
- research_findings.md (structured analysis with sources)
- comparison_matrix.json (alternatives compared on key dimensions)
- recommendation.md (recommended approach with justification)
- env_snapshot.json (reproducibility)

## Notes
- Uses **haiku** model tier -- research is breadth-first, not depth-first
- Scout agent excels at pattern recognition and breadth search
- Research output feeds into plan-combo or feature-combo as next step
