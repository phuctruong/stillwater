---
id: integrate-combo
type: combo
wish: integrate
agents: [coder]
skills: [prime-safety, prime-coder, prime-api]
rung_target: 641
model_tier: sonnet
description: "API integration with testing and documentation"
---

# Integrate Combo

## Agents
- **coder** (sonnet) -- implement API integrations, webhooks, and service connections

## Skill Pack
- prime-safety (god-skill, always first)
- prime-coder (coding agent with red/green gate)
- prime-api (API design expertise)

## Execution Flow

```mermaid
flowchart LR
    A[Analyze Integration Requirements] --> B[Design API Contract]
    B --> C[Implement Integration]
    C --> D[Write Integration Tests]
    D --> E{Tests Pass?}
    E -->|Yes| F[Evidence Bundle]
    E -->|No| C
```

## Evidence Required
- integration_tests.py (passing test suite)
- api_contract.md (endpoint documentation)
- env_snapshot.json (reproducibility)

## Notes
- Integration work connects external services to the codebase
- All API calls must be authenticated and rate-limited
- Webhook handlers must be idempotent
