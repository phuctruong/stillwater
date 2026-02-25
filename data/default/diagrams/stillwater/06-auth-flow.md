# Auth Flow

API key generation, validation, rate limiting, and reputation scoring for the
Stillwater Store. Based entirely on `src/store/auth.py`.

## Key Format

```
sw_sk_<32 hex chars>
       ^--- 128 bits of entropy (secrets.token_hex(16) -> 32 hex chars)

key_id:   acct_<uuid4 hex>   (stored in DB, returned to developer)
key_hash: HMAC-SHA256(raw_key, HMAC_SECRET)   (stored in DB, raw key never stored)

HMAC_SECRET: env STILLWATER_HMAC_SECRET
             default: "[SET VIA ENV: STILLWATER_HMAC_SECRET]" (override in production)
```

## Key Generation Flow

```mermaid
sequenceDiagram
    participant DEV as Developer
    participant API as Store API<br/>POST /store/register
    participant AUTH as auth.py
    participant DB as db.py<br/>(_Store singleton)

    DEV->>API: POST /store/register {name, account_type}
    API->>AUTH: generate_api_key()
    AUTH->>AUTH: hex_part = secrets.token_hex(16)<br/>(16 bytes -> 32 hex chars)
    AUTH->>AUTH: raw_key = "sw_sk_" + hex_part
    AUTH->>AUTH: key_id = "acct_" + uuid4().hex
    AUTH->>AUTH: key_hash = HMAC-SHA256(raw_key, _HMAC_SECRET)
    AUTH-->>API: (raw_key, key_id, key_hash)
    API->>DB: create_api_key(key_id, key_hash, name, ...)
    DB-->>API: APIKey record (key_hash stored, raw_key never stored)
    API-->>DEV: {key_id, raw_key}<br/>Show raw_key ONCE — never again
```

## Request Authentication Flow

```mermaid
sequenceDiagram
    participant CLIENT as API Client
    participant FASTAPI as FastAPI<br/>(store endpoint)
    participant AUTH as auth.require_api_key()
    participant LOOKUP as auth.lookup_api_key()
    participant DB as db.get_api_key_by_hash()

    CLIENT->>FASTAPI: POST /store/submit<br/>Authorization: Bearer sw_sk_<hex>
    FASTAPI->>AUTH: HTTPBearer extracts credentials
    AUTH->>AUTH: validate_key_format(raw_key)<br/>Check: starts with "sw_sk_"<br/>Check: hex_part len == 32<br/>Check: all hex chars valid
    alt format invalid
        AUTH-->>FASTAPI: None
        FASTAPI-->>CLIENT: HTTP 401<br/>"Missing API key"
    end
    AUTH->>LOOKUP: lookup_api_key(raw_key)
    LOOKUP->>LOOKUP: key_hash = HMAC-SHA256(raw_key, _HMAC_SECRET)
    LOOKUP->>DB: get_api_key_by_hash(key_hash)
    DB-->>LOOKUP: APIKey record or None
    alt not found
        LOOKUP-->>AUTH: None
        AUTH-->>FASTAPI: raise HTTP 401
        FASTAPI-->>CLIENT: HTTP 401<br/>"Invalid or inactive API key"
    end
    LOOKUP->>LOOKUP: Check record.status == "active"
    alt status != "active"
        LOOKUP-->>AUTH: None
        AUTH-->>FASTAPI: raise HTTP 401
        FASTAPI-->>CLIENT: HTTP 401<br/>"Invalid or inactive API key"
    end
    LOOKUP-->>AUTH: APIKey record
    AUTH-->>FASTAPI: APIKey (dependency injection)
    FASTAPI->>FASTAPI: Continue to endpoint handler
```

## Rate Limiting Flow

```mermaid
sequenceDiagram
    participant ENDPOINT as Store Endpoint
    participant RATE as auth.check_rate_limit()
    participant DB as db.count_recent_submissions()

    ENDPOINT->>RATE: check_rate_limit(api_key)
    RATE->>DB: count_recent_submissions(<br/>  key_id=api_key.key_id<br/>  window_seconds=86400<br/>)
    Note over DB: Counts submissions from this key<br/>in last 86400s (24h rolling window)<br/>Normalises "Z" suffix for fromisoformat()<br/>Excludes tz-naive timestamps if present
    DB-->>RATE: count (int)
    alt count >= RATE_LIMIT_MAX (10)
        RATE-->>ENDPOINT: raise HTTP 429<br/>"Rate limit exceeded: 10/24h"
    else count < 10
        RATE-->>ENDPOINT: (no error — continue)
    end
```

## Reputation Scoring Flow

```mermaid
flowchart TD
    classDef ok fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef fail fill:#7a2d2d,color:#fff,stroke:#5c1a1a
    classDef active fill:#1a5cb5,color:#fff,stroke:#0f3d80

    REVIEW_ACCEPT["Reviewer: accept skill"]
    REVIEW_REJECT["Reviewer: reject skill"]

    APPLY_REP["apply_reputation(key_id, accepted: bool)"]
    GET_RECORD["db.get_api_key_by_id(key_id)\n-> APIKey or None"]

    ACCEPT_DELTA["+1.0 reputation\naccepted_count += 1"]
    REJECT_DELTA["-0.5 reputation\nrejected_count += 1"]

    UPDATE["db.update_api_key(key_id,\n  {reputation: new_value\n   accepted_count or rejected_count: N})"]

    REVIEW_ACCEPT --> APPLY_REP
    REVIEW_REJECT --> APPLY_REP
    APPLY_REP --> GET_RECORD
    GET_RECORD -->|"None (key deleted)"| NOOP["no-op (return)"]
    GET_RECORD -->|"accepted=True"| ACCEPT_DELTA
    GET_RECORD -->|"accepted=False"| REJECT_DELTA
    ACCEPT_DELTA --> UPDATE
    REJECT_DELTA --> UPDATE

    class ACCEPT_DELTA ok
    class REJECT_DELTA fail
    class APPLY_REP,GET_RECORD,UPDATE active
```

## Auth Constants Summary

```mermaid
flowchart LR
    classDef const fill:#5a5a5a,color:#fff,stroke:#333

    C1["KEY_PREFIX = 'sw_sk_'"]
    C2["KEY_HEX_LENGTH = 32\n(128 bits entropy)"]
    C3["RATE_LIMIT_MAX = 10\nsubmissions per window"]
    C4["RATE_LIMIT_WINDOW_SECONDS = 86400\n(24 hours)"]
    C5["REPUTATION_ACCEPT = +1.0"]
    C6["REPUTATION_REJECT = -0.5"]
    C7["HMAC: sha256\nenv: STILLWATER_HMAC_SECRET\ndefault: '[SET VIA ENV: STILLWATER_HMAC_SECRET]'"]

    class C1,C2,C3,C4,C5,C6,C7 const
```

## Source Files

- `src/store/auth.py` — `generate_api_key()`, `_hash_key()`, `validate_key_format()`, `lookup_api_key()`, `require_api_key()`, `check_rate_limit()`, `apply_reputation()` (lines 1-188)
- `src/store/db.py` — `get_api_key_by_hash()`, `count_recent_submissions()`, `update_api_key()`

## Coverage

- Key format: `sw_sk_<32hex>` with 128 bits entropy via `secrets.token_hex`
- HMAC-SHA256 hashing: raw key -> hash stored in DB, raw key never persisted
- Format validation: prefix check + length check + hex char check
- FastAPI dependency injection via `HTTPBearer` + `Security()`
- Rate limiting: rolling 24-hour window, max 10 submissions per key
- Reputation scoring: +1.0 on accept, -0.5 on reject
- All constants extracted directly from `auth.py` source
