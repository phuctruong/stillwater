---
id: diagram-60-orchestration-service
type: diagram
added_at: 2026-02-24
title: "Orchestration Service API (Triple-Twin + Swarm-First Interface)"
persona: Barbara Liskov
related: [diagram-58, diagram-59, diagram-57]
---

# Diagram 60: Orchestration Service API

## Overview

This contract exposes Triple-Twin orchestration as HTTP: Phase 1 (small-talk), Phase 2 (intent), Phase 3 (execution).
The interface is swarm-first: swarms and combos are first-class, then skills/recipes/personas.

## Diagram

### Diagram 1: Orchestration Service API

```mermaid
flowchart TD
    CLIENT[AI Agent / CLI] --> P[POST /api/orchestrate/process]
    CLIENT --> P1[POST /api/orchestrate/phase1]
    CLIENT --> P2[POST /api/orchestrate/phase2]
    CLIENT --> P3[POST /api/orchestrate/phase3]

    P --> TT[TripleTwinEngine]
    P1 --> PH1[Phase 1: SmallTalk]
    P2 --> PH2[Phase 2: Intent]
    P3 --> PH3[Phase 3: Execution]

    CLIENT --> STATS[GET /api/orchestrate/stats]
    CLIENT --> PHASES[GET /api/orchestrate/phases]
```

### Diagram 2: Swarm-First Interface Hierarchy

```mermaid
flowchart LR
    AGENT[AI Agent] --> SWLIST[GET /api/swarms]
    AGENT --> SWGET[GET /api/swarms/{id}]
    AGENT --> SWDISPATCH[POST /api/swarms/{id}/dispatch]

    AGENT --> CBLIST[GET /api/combos]
    AGENT --> CBGET[GET /api/combos/{id}]
    AGENT --> CBEXEC[POST /api/combos/{id}/execute]

    AGENT --> SK[GET /api/skills]
    AGENT --> RC[GET /api/recipes]
    AGENT --> PS[GET /api/personas]
```

### Diagram 3: Customization and Testing API

```mermaid
flowchart TD
    TUNE[AI Tuner] --> GS[GET /api/phases/{n}/seeds]
    TUNE --> PS[POST /api/phases/{n}/seeds]
    TUNE --> GC[GET /api/phases/{n}/config]
    TUNE --> PC[PUT /api/phases/{n}/config]

    QA[QA Agent] --> PT[POST /api/phases/{n}/test]
    QA --> PP[POST /api/orchestrate/test]
    QA --> TR[GET /api/phases/{n}/test-results]

    PS --> CUSTOM[data/custom/* overlay]
    PC --> CUSTOM
```

### Diagram 4: End-to-End AI Agent Flow

```mermaid
sequenceDiagram
    participant A as AI Agent
    participant O as Orchestration Service (8795)
    participant C as Combo Catalog
    participant S as Swarm Service
    participant E as Evidence Pipeline

    A->>O: GET /api/orchestrate/phases
    O-->>A: phases + thresholds + labels

    A->>O: POST /api/orchestrate/process {"text":"fix the login bug"}
    O-->>A: phase1/2/3 + matched_combo + matched_swarm

    A->>C: GET /api/combos/{matched_combo}
    C-->>A: combo contract (wish+recipe+persona)

    A->>S: POST /api/swarms/{matched_swarm}/dispatch
    S-->>A: completion + metadata

    O->>E: capture evidence
    S->>E: capture evidence
```

## Invariants

- Every API call must emit an audit/evidence record.
- All tuning writes target `data/custom/` only; `data/default/` remains immutable.
- Test endpoints run real pytest commands (no mock test execution).
- Swarm dispatch is OAuth3-protected (L2 scope gate).

## Derivations

- Diagram -> service contract: each endpoint maps to a concrete route in `admin/services/orchestration_service.py` and `admin/services/swarm_service.py`.
- Service -> tests: unit tests validate lifecycle, orchestration behavior, customization overlay, catalog reads, and audit chain integrity.
- Service -> CLI: `stillwater-server.sh` starts orchestration after dependencies and gates startup on `/api/health`.
