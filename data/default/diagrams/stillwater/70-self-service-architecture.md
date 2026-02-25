---
id: diagram-70-self-service-architecture
type: diagram
added_at: 2026-02-24
title: "Stillwater Self-Service Architecture (4 Modes + OAuth3 + Tier Gates)"
persona: Barbara Liskov
related: [diagram-58, diagram-60, diagram-61]
---

# Diagram 70: Self-Service Architecture

## Diagram 1: Four Modes

```mermaid
flowchart TB
    U[User/Agent] --> M{Mode}

    M --> C1[Mode 1: Cloud-only]
    M --> L1[Mode 2: Local-only]
    M --> H1[Mode 3: Hybrid-A\nLocal control + cloud tasks]
    M --> H2[Mode 4: Hybrid-B\nCloud control + local execution]

    subgraph Cloud[solaceagi.com Cloud]
      CA[API Gateway]
      CB[Store + Billing + OAuth3 Vault]
      CC[Managed LLM + Task Queue]
    end

    subgraph Local[Stillwater/Browser Local]
      LA[Admin + CLI]
      LB[Browser + Machine Layer]
      LC[Local Evidence Store]
    end

    C1 --> CA --> CB --> CC
    L1 --> LA --> LB --> LC
    H1 --> LA --> CA
    H1 --> CC --> LB
    H2 --> CA --> LB
    H2 --> LB --> LC
```

## Diagram 2: API Key + OAuth3 Flow

```mermaid
sequenceDiagram
    participant R as Register
    participant A as Auth Layer
    participant O as OAuth3
    participant E as Executor
    participant V as Evidence

    R->>A: Create account + issue sw_sk_ key
    A->>A: Hash key + store key doc
    A-->>R: Return raw key once

    R->>A: Authorization: Bearer sw_sk_...
    A->>A: verify_api_key() (hash lookup)
    A-->>R: account_id + tier

    R->>O: Grant scoped token
    O-->>R: token_id + scopes + expiry

    R->>E: Execute action with scope
    E->>O: validate scope + revocation + step-up
    E->>V: write audit evidence (who/when/what/hash)
    R->>O: revoke token
```

## Diagram 3: Tunnel Architecture (Modes 3/4)

```mermaid
flowchart LR
    subgraph LocalHost[Local Node]
      LCLI[CLI/Admin]
      LTUN[Secure Tunnel Agent]
      LSRV[Local Browser/Machine Service]
    end

    subgraph CloudPlane[Cloud Control Plane]
      CTUN[Tunnel Broker]
      CAP[Cloud API]
      CJOB[Job Orchestrator]
    end

    LCLI --> LTUN
    LTUN <--> CTUN
    CAP --> CTUN
    CJOB --> CAP
    CTUN --> LSRV
    LSRV --> LTUN
```

## Diagram 4: Tier Gates by Mode

```mermaid
flowchart TB
    W[white\nlocal-only baseline] --> Y[yellow\nmanaged llm + limited cloud]
    Y --> O[orange\nhybrid modes + oauth3 vault]
    O --> G[green\nteam/cloud twin + longer retention]
    G --> B[black\nenterprise controls + private store]

    W -. allowed .-> M2[Mode 2]
    Y -. allowed .-> M1[Mode 1]
    O -. allowed .-> M3[Mode 3]
    G -. allowed .-> M4[Mode 4]
    B -. allowed .-> M1
    B -. allowed .-> M2
    B -. allowed .-> M3
    B -. allowed .-> M4
```

## Diagram 5: Component Placement Matrix

```mermaid
flowchart TD
    subgraph A[Mode 1 Cloud-only]
      A1[Cloud API]
      A2[Cloud Executor]
      A3[Cloud Store]
    end

    subgraph B[Mode 2 Local-only]
      B1[Local Admin/CLI]
      B2[Local Browser + Machine]
      B3[Local Evidence]
    end

    subgraph C[Mode 3 Hybrid-A]
      C1[Local UI + Consent]
      C2[Cloud Scheduling + LLM]
      C3[Tunnel Bridge]
    end

    subgraph D[Mode 4 Hybrid-B]
      D1[Cloud UI/API]
      D2[Remote Local Execution]
      D3[Bidirectional Evidence Sync]
    end
```

## Invariants

- API keys are never stored raw; only hashes are persisted.
- Every privileged action must pass OAuth3 scope checks.
- Tunnel links are explicit, revocable, and auditable.
- Tier enforcement is fail-closed (unknown tier => lowest privileges).
- Every execution path emits evidence with stable references.
