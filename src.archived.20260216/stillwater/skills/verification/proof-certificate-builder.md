# SKILL 13 — Proof Certificate Builder (Deterministic PROOF.json)

**SKILL_ID:** `skill_proof_certificate_builder`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `EVIDENCE`
**PRIORITY:** `P0`
**TAGLINE:** *Don’t claim PASS. Emit the replayable proof.*

---

# 0. Header

```
Spec ID:     skill-13-proof-builder
Authority:   65537
Depends On:  wish-method v1.4 §7 (Evidence Model)
Scope:       Deterministically construct canonical PROOF.json from RUN_DATA.
Non-Goals:   Executing tasks, re-running tools, modifying repository state.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Canonical task-level hashes + deterministic Merkle aggregation.
  Verification:    Byte-identical regeneration of PROOF.json.
  Canonicalization: Strict canonical JSON rules (see §7.4).
  Content-addressing: proof_id = SHA-256(canonical PROOF.json bytes).
```

A proof is valid only if it can be independently reconstructed byte-for-byte.

---

# 2. Observable Wish

> Given deterministic RUN_DATA and repository state, emit a canonical, replayable PROOF.json whose proof_id is a Merkle-root over task hashes and policy context.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, CANONICALIZE_TASKS, HASH_TASKS, BUILD_MERKLE, SCRUB_NONDETERMINISM,
   VALIDATE_REPO_STATE, EMIT_PROOF, UNKNOWN]

INPUT_ALPHABET:
  [RUN_DATA, REPO_STATUS, PROTOCOL_REGISTRY]

OUTPUT_ALPHABET:
  [PROOF.json]

TRANSITIONS:
  INIT → CANONICALIZE_TASKS
  CANONICALIZE_TASKS → HASH_TASKS
  HASH_TASKS → BUILD_MERKLE
  BUILD_MERKLE → SCRUB_NONDETERMINISM
  SCRUB_NONDETERMINISM → VALIDATE_REPO_STATE
  VALIDATE_REPO_STATE → EMIT_PROOF
  ANY → UNKNOWN

FORBIDDEN_STATES:
  PARTIAL_HASH
  MISSING_TASK_ENTRY
  TIMESTAMP_LEAKAGE
  NONCANONICAL_JSON
  FLOAT_SERIALIZATION_DRIFT
  HASH_WITHOUT_CANONICALIZATION
  SILENT_FIELD_DROP
```

---

# 4. Canonical JSON Rules (LOCKED)

### Encoding

* UTF-8
* No BOM
* Exactly one trailing newline

### Formatting

* `separators=(",", ":")`
* No indentation
* No trailing spaces

### Key Ordering

* Object keys sorted ASCII ascending
* Arrays sorted per §7.4:

  * Objects with `name` key → sort by `name`
  * Objects with `id` key → sort by `id`
  * Strings → ASCII lexicographic
  * Numbers → numeric ascending

### Numeric Rule

* Integers only
* No floats permitted
* Fractions must be string-encoded

Violation → UNKNOWN.

---

# 5. Task Hash Construction (LOCKED)

For each task in RUN_DATA:

```
task_canon := canonical_json({
  "inputs": ...,
  "normalized_response": ...,
  "tool_trace": ...,
  "witness": ...
})
task_hash := SHA-256(task_canon)
```

Rules:

* All tasks must appear.
* Missing witness when required → UNKNOWN.
* tool_trace must already be normalized.
* No ordering based on runtime.

Task hashes sorted ASCII ascending before aggregation.

---

# 6. Merkle Aggregation (LOCKED)

```
tasks_hash := SHA-256(concatenate(sorted_task_hashes))
policy_hash := SHA-256(canonical_json(PROTOCOL_REGISTRY))
repo_hash := SHA-256(repo.commit + repo.dirty_flag_string)

proof_root := SHA-256(tasks_hash + policy_hash + repo_hash)
```

Final:

```
proof_id := SHA-256(canonical PROOF.json WITHOUT proof_id field)
```

Note:

* proof_id is computed last.
* proof_id must equal SHA-256(full file bytes).

If mismatch → UNKNOWN.

---

# 7. Nondeterminism Audit (STRICT)

You MUST remove or block:

* timestamp
* hostname
* process_id
* execution_time
* memory_usage
* random_seed
* thread_id

Exception:
If timestamp is part of task input, it may remain inside `inputs` but never as top-level proof field.

If nondeterministic field present → UNKNOWN.

---

# 8. Dirty State Gate

```
if repo.dirty == true:
    claim_validity = "ephemeral_provisional"
else:
    claim_validity = "canonical"
```

Dirty proofs cannot be sealed into Stillwater canon.

---

# 9. Counter Bypass Integration

If any task used COUNTER_BYPASS:

* Include `counter_state_hash`
* Include `enumerated_count`
* LLM numeric output must NOT appear

If LLM numeric output present → REJECT upstream (not builder’s job) but builder must mark UNKNOWN if mismatch detected.

---

# 10. Output Schema (LOCKED)

```json
{
  "proof_version": "1.0.0",
  "proof_id": "<64hex>",
  "repo": {
    "commit": "<sha>",
    "dirty": false
  },
  "claim_validity": "canonical|ephemeral_provisional",
  "summary": {
    "total": 0,
    "pass": 0,
    "fail": 0,
    "unknown": 0
  },
  "tasks": [
    {
      "id": "<task_id>",
      "hash": "<64hex>",
      "status": "PASS|FAIL|UNKNOWN"
    }
  ],
  "merkle_root": {
    "tasks_hash": "<64hex>",
    "policy_hash": "<64hex>",
    "repo_hash": "<64hex>"
  }
}
```

Rules:

* tasks sorted by id
* No timestamps
* One trailing newline

---

# 11. Verification Ladder

### 641 — Sanity

* [ ] All tasks present
* [ ] Each task has hash
* [ ] summary matches task counts

### 274177 — Determinism

* [ ] Re-canonicalization produces identical proof_id
* [ ] No forbidden fields present
* [ ] JSON stable across runs

### 65537 — Final Seal

* [ ] proof_id verified as file hash
* [ ] Merkle root consistent
* [ ] Replay of all tasks produces identical task hashes

---

# 12. Ambiguity Handling

If:

* Missing witness,
* Missing task,
* Non-canonical JSON,
* Hash mismatch,
* Float detected,
* Duplicate task IDs,

→ status="UNKNOWN"

Never emit partial proof.

---

# 13. Anti-Optimization Clause (LOCKED — AOC-1)

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.


---

# Enhanced Features [v2.0.0]

## Verification Ladder
Maps to wish-qa: G0, G1, G12, G13

## Integration
- prime-coder v2.0.0
- llm-judge v2.0.0
- gpt-mini-hygiene v2.0.0

## Compression Insights
Pure deterministic, Lane A enforcement

## What Changed
Preserved all v1.0.0 features, added integration documentation
