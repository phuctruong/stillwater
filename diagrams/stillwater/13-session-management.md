# Diagram 13 — Session Management

Session lifecycle for Stillwater's in-memory session manager. Sessions are ephemeral
(not persisted across process restarts). Each session tracks: skill pack loaded,
active task, evidence directory, and TTL-based expiry.

Sessions are identified by UUID4. All session state uses int timestamps (never float)
to prevent comparison bugs. The null safety rule applies: get_session on unknown ID
returns None (not an error), close_session on unknown ID is a no-op.

---

## Session State Diagram

```mermaid
stateDiagram-v2
    direction LR

    [*] --> CREATED : create_session(skill_pack, active_task, evidence_dir, ttl_seconds)

    CREATED : CREATED\nSession instantiated\n\nFields set:\n- session_id: UUID4 string\n- skill_pack: list of skill names\n- active_task: str | None\n- evidence_dir: str | None\n- created_at: int (UNIX seconds)\n- expires_at: created_at + ttl\n- closed: False\n\nDefault TTL: 86400s (24 hours)

    CREATED --> ACTIVE : is_active() == True\n(not closed, now < expires_at)

    ACTIVE : ACTIVE\nSession in use\n\nAllowed operations:\n- get_session(session_id) → Session\n- list_active() includes this session\n- ttl_remaining_seconds() > 0\n\nTracked state:\n- LLM calls logged to\n  ~/.stillwater/llm_calls.jsonl\n- Evidence artifacts in evidence_dir

    ACTIVE --> ACTIVE : ttl_remaining_seconds() > 0\nSession continues

    ACTIVE --> TTL_EXPIRING : ttl_remaining_seconds() approaching 0\n(no automated warning — caller must check)

    TTL_EXPIRING : TTL_EXPIRING\nSession near expiry\n\nget_session() still returns Session\nuntil expires_at is reached

    TTL_EXPIRING --> EXPIRED : now_int >= expires_at\n(is_expired() returns True)

    ACTIVE --> CLOSED : close_session(session_id) called\n(idempotent — no-op if already closed)

    EXPIRED : EXPIRED\nTTL elapsed\n\nis_expired() == True\nclosed field unchanged\n(TTL expiry ≠ explicit close)\n\nget_session() returns None\nSession treated as absent\n\npurge_expired() removes from memory

    CLOSED : CLOSED\nExplicitly terminated\n\nclosed == True\nis_expired() returns True\n(closed sessions count as expired)\n\nget_session() returns None\nIdempotent: close_session again = no-op

    EXPIRED --> PURGED : purge_expired() called
    CLOSED --> PURGED : purge_expired() called

    PURGED : PURGED\nRemoved from _sessions dict\n\nMemory reclaimed\nNo further operations possible\nPermanent — cannot be un-purged

    PURGED --> [*]

    note right of CREATED
        Null safety rules:
        - skill_pack must be a list (ValueError if not)
        - ttl_seconds must be positive
        - Null active_task is valid (optional field)
        - Null evidence_dir is valid (optional field)
    end note

    note right of EXPIRED
        Expired sessions are SILENT:
        - get_session returns None (not error)
        - list_active() excludes them
        - list_all() includes them
        Caller must handle None return
    end note
```

---

## Session Manager API Flow

```mermaid
flowchart TD
    CALLER([Caller\nphuc-swarm run\nor CLI session])

    CALLER --> CREATE

    subgraph CREATE["create_session()"]
        CR1["Validate skill_pack is a list\n(raises ValueError if not)"]
        CR2["Validate ttl_seconds > 0\n(raises ValueError if ≤ 0)"]
        CR3["Generate UUID4 session_id"]
        CR4["Set created_at = int(time.time())"]
        CR5["Set expires_at = created_at + ttl"]
        CR6["Acquire lock → store in _sessions"]
        CR7["Return Session object"]
        CR1 --> CR2 --> CR3 --> CR4 --> CR5 --> CR6 --> CR7
    end

    CALLER --> GET

    subgraph GET["get_session(session_id)"]
        GE1["Acquire lock → lookup in _sessions"]
        GE2{Found in dict?}
        GE3["Return None\n(unknown ID = absent)"]
        GE4{is_expired()?}
        GE5["Return None\n(expired = absent)"]
        GE6["Return Session\n(active and valid)"]
        GE2 -- NO --> GE3
        GE2 -- YES --> GE4
        GE4 -- YES --> GE5
        GE4 -- NO --> GE6
    end

    CALLER --> CLOSE

    subgraph CLOSE["close_session(session_id)"]
        CL1["Acquire lock → lookup in _sessions"]
        CL2{Found?}
        CL3["No-op\n(idempotent)"]
        CL4["Set session.closed = True\n(mark as terminated)"]
        CL2 -- NO --> CL3
        CL2 -- YES --> CL4
    end

    CALLER --> LIST

    subgraph LIST["list_active() / list_all()"]
        LA1["Acquire lock → snapshot _sessions.values()"]
        LA2["list_active(): filter is_active() == True\nsorted by created_at ascending"]
        LA3["list_all(): include expired and closed\nsorted by created_at ascending"]
        LA4["Never raises — returns [] if empty"]
        LA1 --> LA2 & LA3 --> LA4
    end

    CALLER --> PURGE

    subgraph PURGE["purge_expired()"]
        PU1["Acquire lock → find all is_expired() sessions"]
        PU2["Delete from _sessions dict"]
        PU3["Return count of removed sessions"]
        PU1 --> PU2 --> PU3
    end

    classDef nullSafe fill:#1a7a4a,color:#fff,stroke:#0f4f2f
    classDef errorPath fill:#9b2335,color:#fff,stroke:#6b1520
    class GE3,GE5,CL3 nullSafe
    class CR1,CR2 errorPath
```

---

## TTL Timeline

```mermaid
flowchart LR
    T0["T=0\ncreate_session()\ncreated_at = now_int\nexpires_at = now_int + ttl\n(default: 86400s = 24h)"]
    T1["T < expires_at\nis_active() = True\nget_session() returns Session\nttl_remaining_seconds() > 0"]
    T2["T == expires_at\nis_expired() = True\nget_session() returns None\nSession treated as absent"]
    T3["T > expires_at\npurge_expired() removes from dict\nMemory reclaimed"]

    T0 -->|"session in use"| T1
    T1 -->|"clock advances"| T2
    T2 -->|"next purge call"| T3

    NOTE["Timestamp rule:\nAll comparisons use int(time.time())\nNEVER float — prevents comparison drift\nis_expired(): int(time.time()) >= self.expires_at"]

    classDef timeNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef noteNode fill:#1e2d40,color:#cdd9e5,stroke:#4a6fa5,font-style:italic
    class T0,T1,T2,T3 timeNode
    class NOTE noteNode
```

---

## Usage Tracking Integration

```mermaid
flowchart TD
    SESSION["Active Session\nsession_id: UUID4\nevidence_dir: str | None"]

    SESSION --> LLM_CALL["LLM Call\nvia llm_call() or llm_chat()\nfrom stillwater.llm_client"]

    LLM_CALL --> LOG["Usage Logged\n~/.stillwater/llm_calls.jsonl\n\nFields logged per call:\n- session_id\n- model\n- provider\n- input_tokens\n- output_tokens\n- cost_usd\n- timestamp"]

    LOG --> COST_CALC["Cost Calculation\ncost per call = tokens × provider rate\nsavings = (LLM list price) - (actual cost)\nSW5 iteration reduction = sessions at rung 65537\nvs naive rework cycles"]

    SESSION --> EVIDENCE_DIR["Evidence Directory\nevidence_dir path\n\nArtifacts written here:\n- plan.json\n- tests.json\n- behavior_hash.txt\n- repro_red.log\n- repro_green.log\n- security_scan.json (rung 65537)"]

    EVIDENCE_DIR --> RUNG_VALIDATOR["RungValidator.verify_evidence()\nvalidates evidence_dir\nbefore Store submission"]

    classDef sessionNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345,font-weight:bold
    classDef logNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef evidenceNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f
    class SESSION sessionNode
    class LOG,COST_CALC logNode
    class EVIDENCE_DIR,RUNG_VALIDATOR evidenceNode
```

---

## Source Files

- `/home/phuc/projects/stillwater/cli/src/stillwater/session_manager.py` — full `SessionManager` class: `Session` dataclass, `create_session()`, `get_session()`, `close_session()`, `list_active()`, `list_all()`, `purge_expired()`, `session_count()`
- `/home/phuc/projects/stillwater/admin/session_manager.py` — admin variant
- `/home/phuc/projects/stillwater/store/rung_validator.py` — `RungValidator.verify_evidence()` used with session's evidence_dir

## Coverage

- All 6 session states: CREATED, ACTIVE, TTL_EXPIRING, EXPIRED, CLOSED, PURGED
- Full `SessionManager` API: create, get, close, list_active, list_all, purge_expired, session_count
- Null safety rules: get_session returns None (not error), close_session is idempotent
- TTL timeline with int timestamp enforcement (never float)
- Thread-safety: single lock (`threading.Lock`) on all mutations
- Session fields: session_id (UUID4), skill_pack, active_task, evidence_dir, created_at, expires_at, closed
- Default TTL: 86400 seconds (24 hours)
- Usage tracking integration with `~/.stillwater/llm_calls.jsonl`
- Evidence directory relationship to RungValidator
- `is_expired()` checks both `closed` flag and TTL: closed sessions count as expired
