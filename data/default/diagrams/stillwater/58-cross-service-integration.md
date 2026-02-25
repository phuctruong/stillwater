---
id: diagram-58-cross-service-integration
type: diagram
added_at: 2026-02-24
title: "Cross-Service Integration: CLI -> Orchestration -> Recipe -> Evidence"
persona: Roy Fielding
related: [diagram-60, diagram-59]
---

# Diagram 58: Cross-Service Integration

## Overview

End-to-end request flow for `"fix the login bug"` and the tuning loop that updates seeds in `data/custom/`.

## Diagram

### Main Flow

```mermaid
sequenceDiagram
    participant CLI as CLI/User
    participant ADMIN as Admin (8787)
    participant ORCH as Orchestration (8795)
    participant P1 as Phase1 CPU
    participant P2 as Phase2 CPU
    participant P3 as Phase3 CPU
    participant RE as Recipe Engine (8789)
    participant LLM as LLM Portal (8788)
    participant EV as Evidence Pipeline (8790)

    CLI->>ADMIN: request (fix the login bug)
    ADMIN->>ORCH: POST /api/orchestrate/process

    ORCH->>P1: classify (task)
    P1-->>ORCH: label=task (CPU hit)

    ORCH->>P2: intent
    P2-->>ORCH: label=bugfix

    ORCH->>P3: execution selection
    P3-->>ORCH: label=bugfix-combo

    ORCH->>RE: load bugfix recipe
    RE->>LLM: optional LLM step
    LLM-->>RE: completion
    RE-->>ORCH: execution plan

    ORCH->>EV: audit entry (phase + combo)
    RE->>EV: audit entry (recipe route)
    LLM->>EV: audit entry (llm call)

    ORCH-->>ADMIN: response + evidence_bundle_id
    ADMIN-->>CLI: final response
```

### Customization Flow

```mermaid
sequenceDiagram
    participant AI as AI Agent
    participant ORCH as Orchestration (8795)
    participant REG as DataRegistry
    participant FS as data/custom

    AI->>ORCH: POST /api/phases/1/seeds
    ORCH->>REG: save_data_file("seeds/phase1_custom.jsonl")
    REG->>FS: write overlay file

    AI->>ORCH: POST /api/orchestrate/process
    ORCH-->>AI: new seed impacts prediction

    AI->>ORCH: POST /api/phases/1/test
    ORCH-->>AI: pytest result
```

## Invariants

- Orchestration is the only phase gateway for pipeline execution.
- All persisted tuning changes are overlay writes (`data/custom/*`).
- Evidence capture happens per step, not only at final response.

## Derivations

- If CPU confidence misses threshold, same flow holds with LLM fallback in phase runner.
- The customization loop is safe to run repeatedly; default data remains untouched.
