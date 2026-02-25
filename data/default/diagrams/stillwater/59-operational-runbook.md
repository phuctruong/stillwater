---
id: diagram-59-operational-runbook
type: diagram
added_at: 2026-02-24
title: "Operational Runbook: Startup, Shutdown, Health, Logs, Emergency"
persona: Mitchell Hashimoto
related: [diagram-58, diagram-60]
---

# Diagram 59: Operational Runbook

## Overview

Runbook for `stillwater-server.sh`: dependency startup order, reverse shutdown, readiness probes, log paths, and incident handling.

## Diagram

### Startup Sequence

```mermaid
flowchart TD
    S0[Start stillwater-server.sh] --> S1[Admin 8787]
    S1 --> H1{GET /api/health == 200?}
    H1 -->|yes| S2[CPU 8792]
    S2 --> H2{health ok}
    H2 -->|yes| S3[Evidence 8790]
    S3 --> H3{health ok}
    H3 -->|yes| S4[OAuth3 8791]
    S4 --> H4{health ok}
    H4 -->|yes| S5[LLM Portal 8788]
    S5 --> H5{health ok}
    H5 -->|yes| S6[Recipe 8789]
    S6 --> H6{health ok}
    H6 -->|yes| S7[Orchestration 8795]
    S7 --> H7{health ok}
    H7 -->|yes| S8[Tunnel 8793]
    S8 --> H8{health ok}
    H8 -->|yes| S9[Cloud Bridge 8794]
    S9 --> H9{health ok}
    H9 -->|yes| DONE[Admin UI ready]

    H1 -->|no| FAIL[Abort startup]
    H2 -->|no| FAIL
    H3 -->|no| FAIL
    H4 -->|no| FAIL
    H5 -->|no| FAIL
    H6 -->|no| FAIL
    H7 -->|no| FAIL
    H8 -->|no| FAIL
    H9 -->|no| FAIL
```

### Shutdown Sequence (Reverse + Drain)

```mermaid
flowchart LR
    A[--stop] --> B[Cloud Bridge]
    B --> C[Tunnel]
    C --> D[Orchestration]
    D --> E[Recipe]
    E --> F[LLM Portal]
    F --> G[OAuth3]
    G --> H[Evidence]
    H --> I[CPU]
    I --> J[Admin]

    note1[Drain in-flight requests before SIGTERM,
then SIGKILL on timeout]:::note
```

### Health Probes and Log Locations

```mermaid
flowchart TD
    P[Probe Model] --> L1[Liveness: process exists by PID]
    P --> R1[Readiness: GET /api/health HTTP 200]

    LOG[Log Paths] --> A1[~/.stillwater/logs/admin.log]
    LOG --> A2[~/.stillwater/logs/llm-portal.log]
    LOG --> A3[~/.stillwater/logs/orchestration-service.log]
    LOG --> A4[~/.stillwater/logs/*.log per service]
```

### Emergency Procedures

```mermaid
flowchart TD
    INCIDENT[Incident Detected] --> TYPE{Type}
    TYPE -->|Service crash| R1[Restart single service + probe]
    TYPE -->|Registry corruption| R2[Backup/rotate ~/.stillwater/service_registry.json then rediscover]
    TYPE -->|Repeated failure| R3[Run --stop then clean restart]
    TYPE -->|Auth failure/OAuth3 down| R4[Fail closed, deny mutating calls]

    R1 --> EV[Record incident in evidence logs]
    R2 --> EV
    R3 --> EV
    R4 --> EV
```

## Invariants

- Readiness gate before dependency startup.
- Reverse-order shutdown to avoid dangling upstream callers.
- OAuth3 outage is fail-closed for write paths.

## Derivations

- Single script controls lifecycle state through PID files in `~/.stillwater/pids/`.
- `--status` combines liveness (PID) and readiness (`/api/health`) per service.
