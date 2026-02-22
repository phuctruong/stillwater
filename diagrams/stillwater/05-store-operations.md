# Store CRUD Operations

CRUD and lifecycle flows for the Stillwater Store, based on `store/db.py`.
The store is a thread-safe in-memory singleton backed by JSON files.

## Persistence Architecture

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef store fill:#7a2d7a,color:#fff,stroke:#5c1a5c
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef io fill:#4a4a4a,color:#fff,stroke:#333

    subgraph MEMORY ["In-Memory Singleton (_Store)"]
        DICT_KEYS["_api_keys: Dict[str, dict]\n{ key_id: APIKey fields }"]
        DICT_SKILLS["_skills: Dict[str, dict]\n{ skill_id: ReviewRecord fields }"]
        LOCK["threading.Lock\nguards all mutations\nsingle-process only"]
    end

    subgraph DISK ["JSON File Persistence"]
        KEY_FILE["scratch/store_db/api_keys.json\n(or STILLWATER_STORE_DATA_DIR env)"]
        SKILLS_FILE["scratch/store_db/skills.json"]
    end

    STARTUP["load(data_dir)\nIdempotent\nReads both files\nSets _loaded=True"]
    MUTATE["Any mutation method\ncreate / update"]
    SAVE["save(data_dir)\nWrites both files atomically\njson.dumps(indent=2, default=str)"]
    RESET["reset()\nClear all data\n(used in tests)"]

    STARTUP --> DISK
    DISK -->|"json.loads"| MEMORY
    MUTATE --> LOCK
    LOCK --> MEMORY
    SAVE --> DISK

    class DICT_KEYS,DICT_SKILLS,LOCK active
    class KEY_FILE,SKILLS_FILE io
    class STARTUP,SAVE,RESET gate
```

## API Key CRUD

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000

    CREATE_KEY["create_api_key(\n  key_id, key_hash, name\n  account_type='human'\n  description=''\n)\n-> APIKey"]

    GET_BY_ID["get_api_key_by_id(key_id)\n-> Optional[APIKey]\nNone if not found"]

    GET_BY_HASH["get_api_key_by_hash(key_hash)\n-> Optional[APIKey]\nLinear scan (used during auth)"]

    UPDATE_KEY["update_api_key(key_id, updates: dict)\nKeyError if not found\nUsed for reputation scoring\n+ rate limit tracking"]

    LIST_KEYS["list_api_keys()\n-> List[APIKey]\nAll keys (no pagination)"]

    STORE_DB[("_api_keys\ndict")]

    CREATE_KEY --> STORE_DB
    GET_BY_ID --> STORE_DB
    GET_BY_HASH --> STORE_DB
    UPDATE_KEY --> STORE_DB
    LIST_KEYS --> STORE_DB

    class CREATE_KEY,GET_BY_ID,GET_BY_HASH,UPDATE_KEY,LIST_KEYS active
    class STORE_DB gate
```

## Skill / Submission CRUD

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000

    CREATE_SKILL["create_skill(record: ReviewRecord)\n-> ReviewRecord\nStores model_dump(mode='json')"]

    GET_SKILL["get_skill(skill_id)\n-> Optional[ReviewRecord]\nNone if not found"]

    GET_BY_NAME["get_skill_by_name(skill_name)\n-> Optional[ReviewRecord]\nLinear scan by name"]

    UPDATE_SKILL["update_skill(skill_id, updates: dict)\nKeyError if not found\nUsed by review: status, rung_verified\nreviewed_at, review_notes, behavior_hash"]

    LIST_SKILLS["list_skills(\n  status=None|SkillStatus\n  page=1, per_page=20\n)\n-> (List[ReviewRecord], int total)\nSorted by submitted_at DESC"]

    COUNT_RECENT["count_recent_submissions(\n  key_id, window_seconds=86400\n)\n-> int\nRolling 24h window\nUsed by rate limiter"]

    STORE_DB[("_skills\ndict")]

    CREATE_SKILL --> STORE_DB
    GET_SKILL --> STORE_DB
    GET_BY_NAME --> STORE_DB
    UPDATE_SKILL --> STORE_DB
    LIST_SKILLS --> STORE_DB
    COUNT_RECENT --> STORE_DB

    class CREATE_SKILL,GET_SKILL,GET_BY_NAME,UPDATE_SKILL,LIST_SKILLS,COUNT_RECENT active
    class STORE_DB gate
```

## Submission Lifecycle

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef fail fill:#7a2d2d,color:#fff,stroke:#5c1a1a
    classDef ok fill:#2d7a2d,color:#fff,stroke:#1a5c1a

    DEV["Developer\nwith sw_sk_ key"]

    AUTH_CHECK["auth.require_api_key()\nExtract Bearer token\nValidate format sw_sk_<32hex>\nHMAC-SHA256 lookup in DB\nCheck status == 'active'"]

    RATE_CHECK["auth.check_rate_limit()\ncount_recent_submissions(key_id, 86400)\nMAX = 10 per 24h\nHTTP 429 if exceeded"]

    RUNG_CHECK["rung_validator.RungValidator\nverify_evidence(evidence_dir, rung_target)\nplan.json + tests.json + behavior_hash.txt\n3-seed consensus check"]

    CREATE["db.create_skill(ReviewRecord)\nskill_id = uuid4()\nstatus = 'pending'\nsubmitted_at = utcnow()"]

    UPDATE_SUBMISSION_COUNT["db.update_api_key(key_id,\n  {submission_count: +1})"]

    PENDING[("status: pending\nAwaiting review")]

    REVIEW["Reviewer runs:\nstillwater review [accept|reject]\nor API: POST /store/review"]

    ACCEPT["db.update_skill(\n  {status: 'accepted'\n   rung_verified: N\n   reviewed_at: utcnow()\n   behavior_hash: sha256\n   review_notes: ...})\nauth.apply_reputation(key_id, True)\n  -> reputation += 1.0\n  -> accepted_count += 1"]

    REJECT["db.update_skill(\n  {status: 'rejected'\n   reviewed_at: utcnow()\n   review_notes: ...})\nauth.apply_reputation(key_id, False)\n  -> reputation -= 0.5\n  -> rejected_count += 1"]

    PUBLISHED[("status: accepted\nVisible via\nGET /store/skills")]
    REJECTED_STATE[("status: rejected\nNot visible in\ndefault listing")]

    DEV --> AUTH_CHECK
    AUTH_CHECK -->|"401"| FAIL_AUTH["HTTP 401\nInvalid/inactive key"]
    AUTH_CHECK -->|"ok"| RATE_CHECK
    RATE_CHECK -->|"429"| FAIL_RATE["HTTP 429\nRate limit exceeded"]
    RATE_CHECK -->|"ok"| RUNG_CHECK
    RUNG_CHECK -->|"INVALID"| FAIL_RUNG["HTTP 422\nEvidence bundle invalid"]
    RUNG_CHECK -->|"VALID"| CREATE
    CREATE --> UPDATE_SUBMISSION_COUNT
    UPDATE_SUBMISSION_COUNT --> PENDING
    PENDING --> REVIEW
    REVIEW --> ACCEPT
    REVIEW --> REJECT
    ACCEPT --> PUBLISHED
    REJECT --> REJECTED_STATE

    class DEV,CREATE,UPDATE_SUBMISSION_COUNT active
    class AUTH_CHECK,RATE_CHECK,RUNG_CHECK gate
    class FAIL_AUTH,FAIL_RATE,FAIL_RUNG fail
    class PUBLISHED,PENDING ok
```

## Source Files

- `store/db.py` — `_Store` class, all CRUD methods, `load()`, `save()`, `reset()`
- `store/models.py` — `ReviewRecord`, `APIKey`, `SkillStatus`
- `store/auth.py` — `require_api_key()`, `check_rate_limit()`, `apply_reputation()`
- `store/rung_validator.py` — `RungValidator.verify_evidence()`

## Coverage

- In-memory singleton architecture with `threading.Lock` guard
- JSON file persistence paths and environment variable override
- All API key CRUD methods with signatures and return types
- All skill/submission CRUD methods including pagination and rolling-window count
- Full submission lifecycle: auth -> rate limit -> rung validation -> create -> review -> accept/reject
- Reputation delta values: +1.0 accept, -0.5 reject (from `auth.py`)
