---
id: diagram-61-solace-browser-openclaw-parity
type: diagram
added_at: 2026-02-24
title: "Solace Browser vs OpenClaw — Competitive Parity and Execution Plan"
persona: Tim Berners-Lee
related: [diagram-60, diagram-58, diagram-59]
---

# Diagram 61: Solace Browser OpenClaw Parity

## Overview

This diagram maps OpenClaw feature parity against the Stillwater/Solace Browser northstar and defines implementation order.
The plan prioritizes real differentiators first: OAuth3 consent, revocation, evidence, and recipe-backed browser automation.

## Diagram

### Diagram 1: Competitive Feature Matrix (OpenClaw vs Stillwater)

```mermaid
flowchart LR
    subgraph OC[OpenClaw Baseline]
        OC1[Browser automation recipes]
        OC2[Chrome extension]
        OC3[Session persistence]
        OC4[Multi-tab management]
        OC5[Form filling + extraction]
        OC6[Scheduled tasks + API integrations]
    end

    subgraph SW[Stillwater / Solace Browser Target]
        SW1[Recipe wiring over 21 combos]
        SW2[PM triplet + recipe system]
        SW3[OAuth3 token persistence]
        SW4[Twin browser orchestration]
        SW5[PZip HTML snapshots + recipe forms]
        SW6[Swarm dispatch + webhook API]
    end

    OC1 --> SW1
    OC2 --> SW2
    OC3 --> SW3
    OC4 --> SW4
    OC5 --> SW5
    OC6 --> SW6

    OCX[No consent/revoke/audit/rung verification] --> SWX[OAuth3 consent + revoke + evidence + rung gates]
```

### Diagram 2: Implementation Priority Order

```mermaid
flowchart TD
    P1[TASK-031 Diagram] --> P2[TASK-038 Browser server integration]
    P2 --> P3[TASK-041 Vendor home screen + Add Site]
    P3 --> P4[TASK-043 Live discovery pipeline]
    P4 --> P5[TASK-042 Store extension: PrimeWiki + snapshots + recipes]
    P5 --> P6[TASK-039 CAPTCHA + proxy + benchmark]
    P6 --> P7[TASK-044 CLI machine webservices + OAuth3]
    P7 --> P8[Operational rollout and QA hardening]
```

### Diagram 3: Integration Flow (Admin API -> Browser -> PM Triplets -> Recipes)

```mermaid
sequenceDiagram
    participant A as Stillwater Admin API
    participant B as Solace Browser Server
    participant D as Discovery Engine
    participant T as PM Triplet Store
    participant R as Recipe Engine
    participant S as Stillwater Store

    A->>B: POST /browser/spawn + scopes
    B->>D: map site + capture DOM states
    D->>T: write .mmd + .sha256 + .prime-mermaid.md
    D->>R: generate task recipes
    R->>B: execute + verify recipe steps
    B->>S: upload primewiki/snapshots/recipes
    S-->>A: contribution status + audit refs
```

### Diagram 4: OAuth3 Advantage Flow (Grant -> Scope -> Execute -> Evidence -> Revoke)

```mermaid
flowchart LR
    G[Grant scope] --> V[Validate token + scope]
    V --> E[Execute browser action]
    E --> L[Log evidence + hash chain]
    L --> R[Revoke token]
    R --> X[Further action denied]

    G -. least privilege .-> V
    E -. step-up required for high risk .-> L
```

## Invariants

- Every remote browser action is OAuth3-scoped and revocable.
- Every discovery and execution event emits audit evidence with stable references.
- PM triplets are canonical for page/state snapshots (`.mmd`, `.sha256`, `.prime-mermaid.md`).
- Recipe execution must be replayable from stored artifacts.

## Derivations

- TASK-038/041/043/044 service contracts derive from this flow.
- Store schema for PrimeWiki/snapshots/recipes derives from Diagram 3.
- OAuth3 endpoint and policy checks derive from Diagram 4.
