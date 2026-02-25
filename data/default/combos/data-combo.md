---
id: data-combo
type: combo
wish: data
agents: [coder]
skills: [prime-safety, prime-coder, prime-data]
rung_target: 641
model_tier: sonnet
description: "Data processing — ETL pipelines, analytics, queries, and dataset management"
---

# Data Combo

## Agents
- **coder** (sonnet) -- build data pipelines, run queries, analyze datasets, generate reports

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (implementation)
- prime-data (data pipeline expertise)

## Execution Flow

```mermaid
flowchart LR
    A[Define Data Task] --> B[Extract Source Data]
    B --> C[Transform / Clean]
    C --> D[Load / Analyze]
    D --> E[Generate Report]
    E --> F[Evidence Bundle]
```

## Evidence Required
- pipeline.py or query.sql (executable data code)
- data_report.md (analysis results)
- sample_output.json (representative data sample)
- env_snapshot.json (reproducibility)

## Notes
- Data operations should be idempotent where possible
- Large datasets are processed in chunks to manage memory
- Sensitive data must be masked in reports and evidence
