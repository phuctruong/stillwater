---
id: deploy-combo
type: combo
wish: deploy
agents: [coder]
skills: [prime-safety, devops]
rung_target: 641
model_tier: sonnet
description: "Safe deployment with rollback plan and health checks"
---

# Deploy Combo

## Agents
- **coder** (sonnet) -- prepare deployment, run pre-flight checks, execute rollout

## Skill Pack
- prime-safety (god-skill, always first)
- devops (deployment procedures, rollback protocols)

## Execution Flow

```mermaid
flowchart LR
    A[Pre-flight Checks] --> B[Build Artifacts]
    B --> C[Deploy to Staging]
    C --> D[Health Check]
    D --> E{Healthy?}
    E -->|Yes| F[Deploy to Production]
    E -->|No| G[Rollback]
    F --> H[Post-deploy Verify]
    H --> I[Evidence Bundle]
    G --> J[Incident Report]
```

## Evidence Required
- deploy_log.json (deployment steps and outcomes)
- health_check.json (pre and post-deploy health status)
- rollback_plan.md (documented rollback procedure)
- env_snapshot.json (reproducibility)
