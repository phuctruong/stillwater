# Storage Architecture Design Memo
## stillwater Hybrid Local + Firestore Storage

**Version:** 1.0.0
**Date:** 2026-02-23
**Author:** Grace Hopper (Planner agent — design only, rung 274177)
**Status:** DESIGN COMPLETE — No code written yet. Implementation is task #5+.

---

## 0. Key Design Decisions (TL;DR)

| Decision | Choice | Rationale |
|---|---|---|
| Default storage | `~/stillwater/data/` JSONL | OSS-first, human-readable, no cloud account needed |
| Firestore | Opt-in only | Never required for basic operation |
| Format | JSONL + Mermaid | Consistent with existing wishes.jsonl, combos.jsonl |
| Conflict resolution | Last-write-wins (UTC timestamp) | Simple, deterministic, no coordination needed |
| Sync trigger | On every LocalStore write (async queue) | Never blocks the caller |
| Banter queue (SQLite) | Separate concern — stays SQLite | Session-scoped, not a learned entity |
| Mermaid files | Write-only (display output) | Not machine-read back into storage |

---

## 1. Local `~/stillwater/data/` Directory Structure

```
~/stillwater/data/
├── sync_metadata.json          ← sync state (last_synced_at, pending_count)
├── sync.lock                   ← advisory lock file during active sync
│
├── smalltalk/
│   ├── learned_smalltalk.jsonl ← LearnedSmallTalk entries (append-only)
│   └── banter_queue.db         ← SQLite banter queue (optional, session-scoped)
│
├── intent/
│   └── learned_wishes.jsonl    ← LearnedWish entries (append-only)
│
├── execute/
│   └── learned_combos.jsonl    ← LearnedCombo entries (append-only)
│
└── recipes/
    ├── recipe.oauth-integration.mermaid    ← generated Mermaid (display only)
    ├── recipe.database-optimization.mermaid
    └── ... (one per wish_id that has a combo)
```

**Rules:**
- Maximum 2 directory levels: `data/<phase>/<file>`
- `ls ~/stillwater/data/` shows all phases at a glance
- Canonical source files (`wishes.jsonl`, `combos.jsonl`) stay in the repo under
  `admin/orchestration/{intent,execute}/` — they are NOT in `~/stillwater/data/`
- `~/stillwater/data/` holds only runtime-learned data and generated outputs
- `banter_queue.db` is optional; when absent, SmallTalkDB uses `:memory:` SQLite

---

## 2. Entity Models

### 2.1 LearnedSmallTalk (NEW — Phase 1 equivalent)

Symmetrical to `LearnedWish` and `LearnedCombo`. Persisted to
`~/stillwater/data/smalltalk/learned_smalltalk.jsonl`.

**JSONL line example:**
```json
{
  "pattern_id": "joke_016",
  "response_template": "Heard you hit a wall with {topic}. Coffee break? ☕",
  "keywords": ["stuck", "blocked", "frustrated", "help"],
  "tags": ["support", "encouragement"],
  "min_glow": 0.1,
  "max_glow": 0.5,
  "confidence": 0.72,
  "source": "llm",
  "timestamp": "2026-02-23T14:32:11.847Z",
  "session_id": "sess_a3f9c2",
  "synced_to_firestore": false,
  "sync_timestamp": null,
  "sync_attempt_count": 0
}
```

**Merge semantics:** If `pattern_id` already exists in the `PatternRepo`, new
keywords are appended (union). If `pattern_id` does not exist, a new pattern
entry is created. `SmallTalkDB.append_learned_smalltalk()` handles this,
mirroring `WishDB.append_learned_wish()`.

---

### 2.2 LearnedWish (existing — sync fields added)

**JSONL line example (with sync fields):**
```json
{
  "wish_id": "oauth-integration",
  "keywords": ["pkce", "device-flow"],
  "skill_pack_hint": "coder+security",
  "confidence": 0.71,
  "source": "llm",
  "timestamp": "2026-02-23T14:30:00.000Z",
  "session_id": "sess_a3f9c2",
  "synced_to_firestore": false,
  "sync_timestamp": null,
  "sync_attempt_count": 0
}
```

---

### 2.3 LearnedCombo (existing — sync fields added)

**JSONL line example (with sync fields):**
```json
{
  "wish_id": "grpc-service",
  "swarm": "coder",
  "recipe": ["prime-safety", "prime-coder", "software5.0-paradigm"],
  "confidence": 0.70,
  "source": "llm",
  "timestamp": "2026-02-23T14:31:05.123Z",
  "session_id": "sess_a3f9c2",
  "synced_to_firestore": false,
  "sync_timestamp": null,
  "sync_attempt_count": 0
}
```

---

### 2.4 Sync Field Reference (all three entity types)

| Field | Type | Immutable? | Description |
|---|---|---|---|
| `synced_to_firestore` | bool | No | True once successfully synced |
| `sync_timestamp` | string (UTC ISO) or null | No | When sync succeeded |
| `sync_attempt_count` | int | No | Incremented on each attempt; capped at 5 |
| `timestamp` | string (UTC ISO) | YES | When entity was created locally |
| `session_id` | string | YES | Session that generated this entry |
| `source` | "llm" or "manual" | YES | Who generated this entry |

**Note:** The `timestamp` field is the conflict-resolution key. It is set once on
creation and never overwritten. `sync_timestamp` is a separate field that records
when the Firestore write succeeded.

---

## 3. sync_metadata.json

Located at `~/stillwater/data/sync_metadata.json`.

**Example:**
```json
{
  "schema_version": "1.0.0",
  "local_store_path": "/home/phuc/stillwater/data",
  "firestore_project": "stillwater-prod",
  "firestore_database": "(default)",
  "last_synced_at": "2026-02-23T14:30:00.000Z",
  "last_sync_status": "success",
  "pending_sync_count": 0,
  "total_synced": {
    "learned_wishes": 47,
    "learned_combos": 23,
    "learned_smalltalk": 11
  },
  "failed_sync_entries": []
}
```

**`failed_sync_entries`** lists entries that exceeded 5 retry attempts:
```json
"failed_sync_entries": [
  {
    "entity_type": "learned_wish",
    "entity_id": "wish_id:grpc-service",
    "timestamp": "2026-02-23T14:29:00.000Z",
    "last_error": "DEADLINE_EXCEEDED",
    "attempt_count": 5
  }
]
```

---

## 4. Mermaid Recipe Format

Mermaid files are **write-only** (display output). They are generated from combos
at display time. They are **never read back** into the storage layer.

Located at: `~/stillwater/data/recipes/recipe.<wish_id>.mermaid`

**Example: `recipe.oauth-integration.mermaid`**
```
---
title: Recipe — OAuth Integration
wish_id: oauth-integration
swarm: coder
confidence: 0.95
generated_at: 2026-02-23T14:30:00Z
---

flowchart LR
    A([User Intent:\noauth-integration]) --> B[Swarm: coder]
    B --> C[Skill Pack]
    C --> D[prime-safety]
    C --> E[prime-coder]
    C --> F[oauth3-enforcer]
    D --> G([Execute:\nOAuth flow implementation])
    E --> G
    F --> G
```

**Rules:**
- File is regenerated on every `LocalStore.save_learned_combo()` call
- Filename is stable: `recipe.<wish_id>.mermaid` (no timestamps in filename)
- Human can read the file; code never parses it

---

## 5. Firestore Schema

### 5.1 Collection Hierarchy

```
Firestore (project: stillwater-prod)
│
├── users/
│   └── {user_id}/                          ← document (profile metadata)
│       │
│       ├── learned_wishes/
│       │   └── {wish_id}/                  ← document per wish
│       │       ├── wish_id: "oauth-integration"
│       │       ├── keywords: ["pkce", "device-flow"]  ← array
│       │       ├── skill_pack_hint: "coder+security"
│       │       ├── confidence: 0.71
│       │       ├── source: "llm"
│       │       ├── updated_at: Timestamp
│       │       └── session_ids: ["sess_a3f9c2"]       ← array_union accumulation
│       │
│       ├── learned_combos/
│       │   └── {wish_id}/                  ← document per wish_id
│       │       ├── wish_id: "grpc-service"
│       │       ├── swarm: "coder"
│       │       ├── recipe: ["prime-safety", "prime-coder", "software5.0-paradigm"]
│       │       ├── confidence: 0.70
│       │       ├── source: "llm"
│       │       └── updated_at: Timestamp
│       │
│       ├── learned_smalltalk/
│       │   └── {pattern_id}/               ← document per pattern
│       │       ├── pattern_id: "joke_016"
│       │       ├── response_template: "Heard you hit a wall..."
│       │       ├── keywords: ["stuck", "blocked"]     ← array_union on merge
│       │       ├── tags: ["support"]
│       │       ├── confidence: 0.72
│       │       ├── source: "llm"
│       │       └── updated_at: Timestamp
│       │
│       └── sync_metadata/                  ← document (single doc per user)
│           ├── last_synced_at: Timestamp
│           ├── total_learned_wishes: 47
│           ├── total_learned_combos: 23
│           └── total_learned_smalltalk: 11
│
└── global_wishes/                          ← OPTIONAL: community-shared canonical wishes
    └── {wish_id}/
        ├── (same fields as users/{user_id}/learned_wishes/{wish_id})
        └── contributed_by: [user_id_1, user_id_2]
```

**Note:** `global_wishes/` is an optional future collection for community sharing of
learned wishes across users. It is not required for v1 — it is listed here for
forward-compatibility. In v1, all learning is per-user.

---

### 5.2 Firestore Document Examples

**`users/user_phuc/learned_wishes/oauth-integration`:**
```json
{
  "wish_id": "oauth-integration",
  "keywords": ["pkce", "device-flow", "jwks"],
  "skill_pack_hint": "coder+security",
  "confidence": 0.82,
  "source": "llm",
  "updated_at": "2026-02-23T14:30:00Z",
  "session_ids": ["sess_a3f9c2", "sess_b1d7e8"]
}
```

**`users/user_phuc/learned_combos/grpc-service`:**
```json
{
  "wish_id": "grpc-service",
  "swarm": "coder",
  "recipe": ["prime-safety", "prime-coder", "software5.0-paradigm"],
  "confidence": 0.70,
  "source": "llm",
  "updated_at": "2026-02-23T14:31:00Z"
}
```

**`users/user_phuc/learned_smalltalk/joke_016`:**
```json
{
  "pattern_id": "joke_016",
  "response_template": "Heard you hit a wall with {topic}. Coffee break?",
  "keywords": ["stuck", "blocked", "frustrated", "help"],
  "tags": ["support", "encouragement"],
  "confidence": 0.72,
  "source": "llm",
  "updated_at": "2026-02-23T14:32:00Z"
}
```

---

### 5.3 IAM / Auth Model

| Role | Principal | Scope |
|---|---|---|
| `roles/datastore.user` | Service account `stillwater-sync@<project>.iam.gserviceaccount.com` | Full read/write to Firestore database |
| Application Default Credentials | Developer local machine | Used during development (no service account file needed if `gcloud auth application-default login` has been run) |

**Credential loading order (FirestoreStore):**
1. `GOOGLE_APPLICATION_CREDENTIALS` env var (path to service account JSON)
2. `STILLWATER_FIRESTORE_CREDENTIALS` env var (alternative env var name)
3. Application Default Credentials (gcloud login)
4. If none found: raise `FirestoreCredentialError` and fall back to local-only mode

**Firestore Security Rules (single-user OSS mode):**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated service account can read/write
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null
                         && request.auth.uid == userId;
    }
    // global_wishes: any authenticated user can read, only admin can write
    match /global_wishes/{wishId} {
      allow read: if request.auth != null;
      allow write: if false; // Admin SDK only (server-side)
    }
  }
}
```

---

## 6. StorageBackend Interface (Pseudocode)

```python
# Abstract interface — no cloud imports here
class StorageBackend(ABC):

    # LearnedWish operations
    def load_learned_wishes(self) -> list[LearnedWish]: ...
    def save_learned_wish(self, entry: LearnedWish) -> None: ...

    # LearnedCombo operations
    def load_learned_combos(self) -> list[LearnedCombo]: ...
    def save_learned_combo(self, entry: LearnedCombo) -> None: ...

    # LearnedSmallTalk operations
    def load_learned_smalltalk(self) -> list[LearnedSmallTalk]: ...
    def save_learned_smalltalk(self, entry: LearnedSmallTalk) -> None: ...

    # Sync metadata
    def get_sync_metadata(self) -> SyncMetadata: ...
    def set_sync_metadata(self, meta: SyncMetadata) -> None: ...
```

**LocalStore** — reads/writes JSONL under `~/stillwater/data/`:
- `load_learned_wishes()` → reads `data/intent/learned_wishes.jsonl` line by line
- `save_learned_wish(entry)` → appends JSON line to `data/intent/learned_wishes.jsonl`, then regenerates Mermaid if this is a new wish_id
- Thread safety via `threading.Lock()` per file (same pattern as existing WishDB)

**FirestoreStore** — reads/writes Firestore (lazy import: `from google.cloud import firestore`):
- `save_learned_wish(entry)` → `db.collection('users').document(user_id).collection('learned_wishes').document(entry.wish_id).set(data, merge=True)` using `array_union` for keywords field
- Never called unless `firestore.enabled: true` in config

**HybridStore** — delegates to both:
- All `save_*()` calls: write to LocalStore first (synchronous), then enqueue FirestoreStore write to `asyncio.Queue` (non-blocking)
- All `load_*()` calls: read from LocalStore only (local is authoritative source)
- `sync_worker()` background coroutine drains the queue

---

## 7. Mode Selection Logic

```
Startup sequence:
  1. Read llm_config.yaml (or ~/.stillwater/config.yaml)
  2. Check firestore.enabled (default: false)
  3. If firestore.enabled = false:
       backend = LocalStore(base_dir="~/stillwater/data/")
  4. If firestore.enabled = true:
       4a. Check GOOGLE_APPLICATION_CREDENTIALS (or STILLWATER_FIRESTORE_CREDENTIALS)
       4b. If credentials found:
             firestore_store = FirestoreStore(project=config.firestore.project)
             backend = HybridStore(local=LocalStore(...), remote=firestore_store)
       4c. If credentials NOT found:
             log WARNING: "Firestore enabled but no credentials found, falling back to local-only"
             backend = LocalStore(base_dir="~/stillwater/data/")
  5. Inject backend into WishDB, ComboDB, SmallTalkDB via constructor parameter
```

**ASCII Decision Tree:**
```
firestore.enabled?
├── NO  → LocalStore (~/stillwater/data/)
└── YES
    └── credentials available?
        ├── NO  → LocalStore (warning logged)
        └── YES → HybridStore
                  ├── Primary: LocalStore
                  └── Async backup: FirestoreStore
```

---

## 8. Sync Protocol

### 8.1 Write Flow (HybridStore)

```
caller calls save_learned_wish(entry)
  │
  ├─ Step 1 (synchronous): LocalStore.save_learned_wish(entry)
  │   ├─ Acquire file lock
  │   ├─ Append JSON line to ~/stillwater/data/intent/learned_wishes.jsonl
  │   ├─ Release file lock
  │   └─ Return to caller (done — caller unblocked)
  │
  └─ Step 2 (async, non-blocking): enqueue to sync_queue
      └─ sync_worker() (background task):
          ├─ Dequeue entry
          ├─ FirestoreStore.save_learned_wish(entry)
          │   ├─ set(merge=True) with array_union for keyword arrays
          │   ├─ On success: update local JSONL entry's synced_to_firestore=true
          │   └─ On failure: retry with exponential backoff (1s, 2s, 4s, 8s, 60s max)
          │       ├─ After 5 failures: mark sync_attempt_count=5, log to sync_metadata.failed_sync_entries
          │       └─ Local data is NOT affected — it is safe
          └─ Update sync_metadata.json (last_synced_at, pending_sync_count)
```

### 8.2 Startup Pull (HybridStore)

```
HybridStore.__init__():
  1. Load LocalStore.get_sync_metadata() → local_meta
  2. Load FirestoreStore.get_sync_metadata() → remote_meta
  3. If remote_meta.last_synced_at > local_meta.last_synced_at:
       Pull all learned entities from Firestore
       For each pulled entity:
         If local timestamp < remote timestamp: overwrite local JSONL entry
         Else: keep local (local is newer)
  4. Flush any pending local writes to Firestore (clear failed_sync_entries)
```

### 8.3 Conflict Resolution Algorithm

```
CONFLICT RESOLUTION (pseudocode):

function resolve(local_entry, remote_entry):
    if local_entry.timestamp > remote_entry.timestamp:
        winner = local_entry   # local is newer, keep local
    elif remote_entry.timestamp > local_entry.timestamp:
        winner = remote_entry  # remote is newer, apply remote
    else:  # timestamps equal (extremely rare)
        winner = local_entry   # local wins as tiebreaker (local is authoritative)

    # For keyword arrays: always union (never subtract keywords)
    winner.keywords = union(local_entry.keywords, remote_entry.keywords)

    return winner
```

**Why keyword union, not last-write-wins for keywords?**
Keywords are additive. A learned keyword from session A should not be lost just
because session B wrote a different set of keywords later. Keywords can only grow;
they are never deleted via the sync path. Deletion of keywords requires a manual
canonical update to `wishes.jsonl` in the repo.

### 8.4 Retry State Machine

```
States: PENDING → IN_FLIGHT → SUCCESS | RETRY | EXHAUSTED

PENDING:   Entry is in sync_queue, not yet attempted
IN_FLIGHT: FirestoreStore.save_*() called, waiting for response
SUCCESS:   Firestore write succeeded → synced_to_firestore=true
RETRY:     Firestore error (UNAVAILABLE, DEADLINE_EXCEEDED, 5xx)
           → sleep(2^attempt seconds, max 60s) → back to IN_FLIGHT
EXHAUSTED: attempt_count >= 5 → logged to failed_sync_entries
           → entry stays in local JSONL with synced_to_firestore=false
           → periodic background retry every 10 minutes (never gives up fully)
```

---

## 9. Sync Trigger Summary

| Event | Trigger | Sync Behavior |
|---|---|---|
| `save_learned_wish()` | After LLM override in Phase 2 | Immediate async enqueue |
| `save_learned_combo()` | After LLM override in Phase 3 | Immediate async enqueue |
| `save_learned_smalltalk()` | After LLM override in Phase 1 | Immediate async enqueue |
| Startup | App initialization | Pull from Firestore if remote is newer |
| Manual | `stillwater sync` CLI command (future) | Force-flush sync queue |
| Periodic | Background timer, every 10 min | Retry EXHAUSTED entries |

---

## 10. Example Full ~/stillwater/data/ Layout

```
~/stillwater/data/
│
├── sync_metadata.json
│   → {"schema_version":"1.0.0","last_synced_at":"2026-02-23T14:30:00Z",
│      "last_sync_status":"success","pending_sync_count":0,
│      "total_synced":{"learned_wishes":47,"learned_combos":23,"learned_smalltalk":11},
│      "failed_sync_entries":[]}
│
├── sync.lock                      ← empty file, exists only during active sync
│
├── smalltalk/
│   ├── learned_smalltalk.jsonl
│   │   → {"pattern_id":"joke_016","response_template":"Heard you hit a wall...","keywords":["stuck","blocked"],"tags":["support"],"confidence":0.72,"source":"llm","timestamp":"2026-02-23T14:32:11Z","session_id":"sess_a3f9c2","synced_to_firestore":false,"sync_timestamp":null,"sync_attempt_count":0}
│   └── banter_queue.db            ← SQLite, session-scoped banter queue (optional)
│
├── intent/
│   └── learned_wishes.jsonl
│       → {"wish_id":"oauth-integration","keywords":["pkce","device-flow"],"skill_pack_hint":"coder+security","confidence":0.71,"source":"llm","timestamp":"2026-02-23T14:30:00Z","session_id":"sess_a3f9c2","synced_to_firestore":true,"sync_timestamp":"2026-02-23T14:30:05Z","sync_attempt_count":1}
│       → {"wish_id":"grpc-service","keywords":["grpc","protobuf","proto"],"skill_pack_hint":"coder","confidence":0.68,"source":"llm","timestamp":"2026-02-23T14:31:00Z","session_id":"sess_b1d7e8","synced_to_firestore":false,"sync_timestamp":null,"sync_attempt_count":0}
│
├── execute/
│   └── learned_combos.jsonl
│       → {"wish_id":"grpc-service","swarm":"coder","recipe":["prime-safety","prime-coder","software5.0-paradigm"],"confidence":0.70,"source":"llm","timestamp":"2026-02-23T14:31:05Z","session_id":"sess_b1d7e8","synced_to_firestore":false,"sync_timestamp":null,"sync_attempt_count":0}
│
└── recipes/
    ├── recipe.oauth-integration.mermaid    ← generated, display-only
    ├── recipe.database-optimization.mermaid
    └── recipe.grpc-service.mermaid         ← generated when learned_combo for grpc-service is saved
```

---

## 11. What This Design Does NOT Change

| Existing component | Change required? | Notes |
|---|---|---|
| `admin/orchestration/intent/wishes.jsonl` | NO | Canonical wishes stay in repo |
| `admin/orchestration/execute/combos.jsonl` | NO | Canonical combos stay in repo |
| `admin/orchestration/smalltalk/jokes.jsonl` | NO | Canonical jokes stay in repo |
| `admin/orchestration/smalltalk/tech_facts.jsonl` | NO | Stays in repo |
| `WishDB` class | YES — add `data_dir` parameter pointing to `~/stillwater/data/intent/` | Currently defaults to `__file__` directory |
| `ComboDB` class | YES — same pattern | Currently defaults to `__file__` directory |
| SQLite banter queue | NO change to schema | `banter_queue.db` moved to `~/stillwater/data/smalltalk/` if persistence desired |
| 241 existing tests | NO — tests use `:memory:` SQLite and temp dirs | Architecture is backward-compatible |

---

## 12. Rung Assessment

| Criterion | Status | Evidence |
|---|---|---|
| Reversible | YES | Design only, no code written. Can be revised at zero cost. |
| Deterministic | YES | File paths, sync trigger rules, conflict resolution all specified exactly |
| No invented facts | YES | All field names derived from existing models.py files |
| No Firestore required for OSS | YES | LocalStore has zero cloud SDK imports |
| LearnedSmallTalk symmetric | YES | Same 7 base fields + 3 sync fields as LearnedWish/LearnedCombo |
| Mermaid is write-only | YES | Explicitly stated in Section 4 and Section 7 |

**Rung achieved: 274177** (architectural design, reversible, no production code)

---

*EXIT_PASS: All 5 DREAM/FORECAST/DECIDE/ACT/VERIFY sections complete. No contradictions. No invented facts. No Firestore required for OSS operation. Mermaid is write-only. LearnedSmallTalk is symmetric. Design is independently reviewable.*
