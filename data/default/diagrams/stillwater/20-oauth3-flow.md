# Diagram 20: OAuth3 Token Lifecycle

**Description:** OAuth3 is the planned formal standard for AI agency delegation. It extends OAuth2 with consent-bound, evidence-gated, rung-verified permissions for both web actions (click, fill, navigate) and machine actions (file read/write, terminal commands, tunnel). The full token lifecycle covers: request → consent → grant → store → use → refresh → revoke. Scope hierarchy ties each permission category to a minimum rung requirement.

---

## Token Lifecycle: Full Sequence

```mermaid
sequenceDiagram
    participant USER as User / Human Principal
    participant AGENT as AI Agent (solace-browser / solace-cli)
    participant VAULT as OAuth3 Vault (AES-256-GCM, local)
    participant CONSENT as Consent UI
    participant RESOURCE as Resource (LinkedIn / Gmail / File system)
    participant AUDIT as Audit Trail (hash-chained JSONL)

    Note over USER,AUDIT: Phase 1: Token Request
    AGENT->>USER: Request delegation: scope=web.linkedin.post rung=641
    USER->>CONSENT: Open consent UI (explicit, not implicit)
    CONSENT-->>USER: Show: what will be posted, when, on whose behalf
    USER->>CONSENT: Approve (explicit consent)
    CONSENT->>VAULT: Generate token (AES-256-GCM, 256-bit)
    VAULT-->>AGENT: OAuth3 token (scoped, expiring)
    VAULT->>AUDIT: Log: token_issued {scope, rung, ts, agent_id}

    Note over USER,AUDIT: Phase 2: Token Use
    AGENT->>VAULT: Present token for scope=web.linkedin.post
    VAULT->>VAULT: Validate: scope match, not expired, rung met
    VAULT-->>AGENT: Authorized
    AGENT->>RESOURCE: Perform action (LinkedIn post)
    RESOURCE-->>AGENT: Result (URL, snapshot)
    AGENT->>AUDIT: Log: action_performed {scope, rung, evidence_hash, ts}

    Note over USER,AUDIT: Phase 3: Refresh
    AGENT->>VAULT: Token expiring — refresh request
    VAULT->>USER: Notify: agent requests renewal
    USER->>VAULT: Approve renewal (or deny → revoke)
    VAULT->>VAULT: Rotate token (new AES key, new expiry)
    VAULT->>AUDIT: Log: token_refreshed {old_hash, new_hash, ts}

    Note over USER,AUDIT: Phase 4: Revoke
    USER->>VAULT: Revoke token for scope=web.linkedin.post
    VAULT->>VAULT: Mark token revoked (append-only)
    VAULT->>AUDIT: Log: token_revoked {scope, reason, ts}
    VAULT-->>AGENT: 401 Unauthorized on next use
```

---

## Scope Hierarchy and Rung Requirements

```mermaid
flowchart TD
    subgraph WEB_SCOPES["Web Scopes (solace-browser)"]
        W1["web.*.read\nRead-only: browse, scrape, observe\nRung minimum: 641\nExample: LinkedIn profile read"]
        W2["web.*.write\nWrite actions: post, fill form, click submit\nRung minimum: 641\nExample: LinkedIn post, Gmail send"]
        W3["web.*.admin\nAdmin actions: delete, publish, manage\nRung minimum: 274177\nExample: LinkedIn page admin, Gmail delete"]
        W4["web.*.auth\nAuthentication delegation\nRung minimum: 65537\nExample: OAuth2 token management"]

        W1 --> W2 --> W3 --> W4
    end

    subgraph MACHINE_SCOPES["Machine Scopes (solace-cli / Universal Portal)"]
        M1["machine.file.read\nmachine.file.list\nNon-destructive, local only\nRung minimum: 641"]
        M2["machine.file.write\nmachine.terminal.allowlist\nIrreversible writes\nRung minimum: 274177"]
        M3["machine.file.delete\nmachine.terminal.execute\nmachine.tunnel\nSecurity-critical\nRung minimum: 65537"]

        M1 --> M2 --> M3
    end

    subgraph RUNG_GATE["Rung Gate Enforcement"]
        RG1["Rung 641\nLocal correctness\nred/green test + evidence complete\nApplies to: web.read, web.write, machine.file.read"]
        RG2["Rung 274177\nStability\nseed sweep + replay + null edge\nApplies to: web.admin, machine.file.write"]
        RG3["Rung 65537\nProduction confidence\nadversarial + security + behavioral hash\nApplies to: web.auth, machine.delete, machine.tunnel"]

        RG1 --> RG2 --> RG3
    end

    W1 & M1 -.->|"satisfies"| RG1
    W2 -.->|"satisfies"| RG1
    W3 & M2 -.->|"satisfies"| RG2
    W4 & M3 -.->|"satisfies"| RG3
```

---

## Vault Storage Architecture

```mermaid
flowchart TD
    subgraph VAULT_ARCH["OAuth3 Vault (solace-cli — PRIVATE)"]
        direction TB
        KEY_GEN["256-bit AES key\ngenerated at vault init\n(stored in local keychain or file, not memory)"]

        subgraph TOKEN_STORE["Token Store (AES-256-GCM)"]
            T1["token_id → encrypted blob\n(scope + expiry + agent_id + nonce + ciphertext)"]
            T2["index: scope → [token_ids]\n(for lookup by scope)"]
            T3["revocation list: [token_ids]\n(append-only, never delete)"]
        end

        subgraph AUDIT_LOG["Hash-Chained Audit Trail"]
            A1["Entry N: {ts, action, scope, agent_id, evidence_hash}"]
            A2["Entry N hash = SHA-256(entry_N + hash_N-1)"]
            A3["Tamper-evident: any change\nbreaks chain from that point"]
        end

        KEY_GEN --> TOKEN_STORE
        TOKEN_STORE --> AUDIT_LOG
    end

    subgraph FDA["FDA 21 CFR Part 11 Alignment"]
        F1["ALCOA+ compliance:\n- Attributable: agent_id on every action\n- Legible: human-readable JSONL\n- Contemporaneous: ts = action time, not log time\n- Original: pzip HTML snapshot = what agent saw\n- Accurate: hash-chained, tamper-evident"]

        F2["Electronic signature = OAuth3 consent\n(user approval = legally binding delegation)"]

        F3["Audit trail = append-only JSONL\n(never update, never delete)"]
    end

    VAULT_ARCH --> FDA
```

---

## OAuth3 vs OAuth2: Key Differences

```mermaid
flowchart LR
    subgraph OAUTH2["OAuth2 (existing standard)"]
        direction TB
        O2_1["Designed for: humans delegating to apps"]
        O2_2["Consent: single screen, vague scopes"]
        O2_3["Evidence: none"]
        O2_4["Revocation: best-effort"]
        O2_5["Audit: none standard"]
        O2_6["AI agent support: none"]
    end

    subgraph OAUTH3["OAuth3 (planned extension)"]
        direction TB
        O3_1["Designed for: humans delegating to AI agents"]
        O3_2["Consent: explicit, action-level, not vague"]
        O3_3["Evidence: required (rung-gated bundles)"]
        O3_4["Revocation: guaranteed, auditable"]
        O3_5["Audit: hash-chained, tamper-evident"]
        O3_6["AI agent support: first-class"]
    end

    OAUTH2 -->|"extends and strengthens"| OAUTH3

    subgraph WHY_UNCOPYABLE["Why Token-Revenue Incentives Can Slow OAuth3 Adoption"]
        WU1["OpenAI, Anthropic: token revenue\nmodel requires high token usage"]
        WU2["OAuth3 recipe hit rate 70%+ →\nreduces token usage by 70%"]
        WU3["Implementing OAuth3 would\ncannibalise their own revenue"]
        WU4["Strategic moat: consent-native\narchitectures adopt OAuth3 faster"]

        WU1 --> WU2 --> WU3 --> WU4
    end
```

---

## Consent UI Flow

```mermaid
flowchart TD
    TRIGGER["AI Agent requests action\n(e.g. 'Post this article to LinkedIn')"]

    TRIGGER --> CONSENT_SCREEN["Consent UI renders:\n\n'Agent X wants to:\n  - POST to LinkedIn as You\n  - Scope: web.linkedin.post\n  - Rung: 641 (local correctness verified)\n  - Expires: 24 hours\n  - Evidence: tests.json + plan.json attached'\n\n[APPROVE] [APPROVE ONCE] [DENY]"]

    CONSENT_SCREEN --> DECISION{"User decision"}
    DECISION -->|"APPROVE"| GRANT["Issue token\n(AES-256-GCM)\nLog to audit trail"]
    DECISION -->|"APPROVE ONCE"| GRANT_ONCE["Issue one-use token\n(expires after single use)"]
    DECISION -->|"DENY"| DENY["Log denial\nAgent receives 403\nNo action taken"]

    GRANT & GRANT_ONCE --> AGENT_PROCEED["Agent proceeds with action\nunder token scope"]
    AGENT_PROCEED --> EVIDENCE["Generate evidence:\n- pzip HTML snapshot (what agent saw)\n- action log\n- result URL\n- behavioral hash"]
    EVIDENCE --> AUDIT_APPEND["Append to audit trail\n(hash-chained)"]
```

---

## Implementation Roadmap (OAuth3 Build Phases)

```mermaid
flowchart LR
    subgraph P1["Phase 1 — OAuth3 Spec (stillwater)"]
        P1A["oauth3-spec skill\n(formal specification)"]
        P1B["Scope taxonomy defined\n(web + machine)"]
        P1C["Rung requirements documented"]
    end

    subgraph P2["Phase 2 — OAuth3 Core (solace-browser)"]
        P2A["Token issuance module\n(AES-256-GCM)"]
        P2B["Consent UI\n(explicit, action-level)"]
        P2C["Revocation API"]
    end

    subgraph P3["Phase 3 — OAuth3 Vault (solace-cli PRIVATE)"]
        P3A["Local vault storage\n(persistent, encrypted)"]
        P3B["CLI auth commands\n(sw auth login, sw auth revoke)"]
        P3C["Team tokens (Enterprise)"]
    end

    subgraph P4["Phase 4 — OAuth3 Enforcer (stillwater Store)"]
        P4A["oauth3-enforcer skill\n(rung gate for all scopes)"]
        P4B["Store requires OAuth3\nfor all published skills"]
        P4C["Rung 65537 certification\nfor production skills"]
    end

    subgraph P5["Phase 5 — External Adoption"]
        P5A["OAuth3 v1.0 spec published\n(IETF or similar)"]
        P5B["1 external AI platform\nadopts OAuth3"]
        P5C["NORTHSTAR metric achieved"]
    end

    P1 --> P2 --> P3 --> P4 --> P5
```

---

## Source Files

- `NORTHSTAR.md` — OAuth3 strategic position, scope hierarchy, rung semantics for machine layer
- `ROADMAP.md` — OAuth3 build phases (Phase 2: oauth3-spec skill, Phase 3: store governance)
- `admin/session_manager.py` — AES-256-GCM pattern (same architecture as OAuth3 vault)
- `admin/llm_portal.py` — Phase 3 `/api/providers/auth` (memory-only key pattern)
- `case-studies/solace-browser.md` — OAuth3 core module build plan
- `case-studies/solace-cli.md` — OAuth3 vault commands (PRIVATE)

---

## Coverage

- Complete token lifecycle: request → consent → grant → store → use → refresh → revoke
- Scope hierarchy: web.read, web.write, web.admin, web.auth; machine.file.*, machine.terminal.*, machine.tunnel
- Rung requirements per scope type (641 / 274177 / 65537)
- Vault storage: AES-256-GCM, nonce-per-write, local only
- Hash-chained audit trail for FDA 21 CFR Part 11 compliance (ALCOA+)
- OAuth2 vs OAuth3 comparison: AI-first design, evidence requirement, guaranteed revocation
- Why token-revenue incentives can slow OAuth3 adoption (strategic moat)
- Consent UI: explicit action-level approval, one-use tokens, deny path
- 5-phase implementation roadmap from spec to external adoption
