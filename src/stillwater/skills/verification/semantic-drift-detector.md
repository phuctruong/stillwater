# SKILL 17 — Semantic Drift Detector

*(Deterministic Canon Stability Guard)*

**SKILL_ID:** `skill_semantic_drift_detector`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `MONITOR`
**PRIORITY:** `P0`
**TAGLINE:** *Definitions are Stillwater. Drift is entropy.*

---

# 0. Header

```
Spec ID:     skill-17-semantic-drift
Authority:   65537
Depends On:  skill-15-canon-patch-writer,
             skill-13-proof-builder
Scope:       Detection of semantic, permission, and policy drift in canonical terms.
Non-Goals:   Subjective “tone” changes without canonical impact.
```

---

# 1. Prime Truth Thesis

```
PRIME_TRUTH:
  Ground truth:     Canonical definition hash + permission surface.
  Verification:     Byte-level diff + usage mapping diff.
  Canonicalization: Sorted JSON definitions.
  Content-addressing: Same term + same history → same drift score.
```

Drift must be computable, not “felt.”

---

# 2. Observable Wish

> Detect when a canonical term’s meaning, authority, or permission surface has changed beyond allowed tolerance.

---

# 3. Closed State Machine

```
STATE_SET:
  [INIT,
   LOAD_CANONICAL,
   COMPARE_DEFINITION,
   COMPARE_USAGE,
   COMPARE_PERMISSIONS,
   COMPUTE_SEVERITY,
   EMIT_REPORT,
   FAIL_CLOSED]

FORBIDDEN_STATES:
  EMBEDDING_ONLY_DECISION
  UNHASHED_DEFINITION
  HEURISTIC_OVERRIDE
```

---

# 4. Deterministic Drift Signals

All primary signals must be hash-based and reproducible.

---

## 4.1 Definition Drift (DD)

Definition:

```
DD = normalized_diff_ratio(
        canonical_definition_vN,
        canonical_definition_vN-1
     )
```

Rules:

* Canonical definitions must be normalized JSON.
* Pure whitespace changes ignored.
* Alias additions without semantic change → DD=0.

If definition not versioned → FAIL_CLOSED.

---

## 4.2 Permission Surface Shift (PSS)

Permission Surface = set of allowed actions unlocked by term.

Example:

* "Verified" originally required proof_hash.
* Now allows narrative reasoning.

Compute:

```
PSS = |permissions_new - permissions_old|
```

If PSS > 0 → severity escalates.

This is the highest-weight signal.

---

## 4.3 Usage Distribution Shift (UDS)

Deterministic measure:

* Map term occurrences to:

  * Skill contexts
  * Node types (L1–L5)
  * Canon directories
  * Task families

Compute:

```
UDS = JaccardDistance(previous_context_set, current_context_set)
```

No embeddings required.

---

## 4.4 Embedding Shift (ES) (Optional / Non-Authoritative)

May compute cosine shift, but:

* Cannot be sole trigger.
* Used only as supporting signal.

If embedding unavailable → ignore.

---

# 5. Severity Classification (Deterministic)

Severity determined strictly by rule table:

### LOW (Benign)

* DD > 0
* PSS = 0
* UDS small (<0.1)

Action: ACCEPT

---

### MEDIUM (Domain Expansion)

* UDS >= 0.1
* PSS = 0

Action: REQUIRE_ALIAS_MAPPING

---

### HIGH (Policy Drift)

* PSS >= 1
* DD > threshold

Action: REQUIRE_CANON_PATCH_WISH

---

### CRITICAL (Adversarial or Gate Bypass)

Triggered if:

* Term now permits bypass of:

  * Counter gate
  * Non-conflation
  * Security gate
  * Red-Green gate

OR

* Term downgraded evidence requirement

Action: QUARANTINE_TERM

---

# 6. Quarantine Protocol

If severity = CRITICAL:

* Block:

  * Promotion to Stillwater
  * Proof emission
  * Canon sealing
* Require:

  * Manual audit
  * New versioned term (e.g., term_v2)
  * Alias mapping document

Original term remains frozen.

---

# 7. Forking Discipline

If drift legitimate:

* Create:

  ```
  term_id_v2
  ```
* Add:

  ```
  alias_map.json
  ```
* Freeze v1 definition
* Update index

No silent mutation allowed.

---

# 8. Replay Invariant

Given:

* Same TERM_REGISTRY
* Same HISTORICAL_SNAPSHOT
* Same USAGE_CORPUS

Drift output MUST be identical.

If severity differs between runs → FAIL_CLOSED.

---

# 9. Output Schema (LOCKED)

```json
{
  "status": "CLEAR|ALERT|QUARANTINE|UNKNOWN",
  "term_id": "...",
  "definition_hash_old": "sha256...",
  "definition_hash_new": "sha256...",
  "signals": {
    "definition_diff": 0.0,
    "permission_shift": 0,
    "usage_divergence": 0.0,
    "embedding_distance": null
  },
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "recommended_action": "ACCEPT|AUDIT|FORK|ROLLBACK|BLOCK_PROMOTION",
  "requires_canon_patch": true
}
```

Rules:

* permission_shift integer
* usage_divergence float [0,1]
* embedding_distance nullable
* recommended_action must match severity table

---

# 10. Verification Ladder

### Rung 641 — Sanity

* [ ] Are canonical hashes present?
* [ ] Are permissions enumerated?
* [ ] Are context sets defined?

---

### Rung 274177 — Consistency

* [ ] Recompute diff → same DD?
* [ ] Recompute context sets → same UDS?
* [ ] Severity matches rule table?

---

### Rung 65537 — Final Seal

* [ ] Replay produces identical severity?
* [ ] No embedding-only decisions?
* [ ] No permission changes without explicit PSS increment?


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
