# SKILL 15 — Canon Patch Writer (Deterministic Canon Evolution)

**SKILL_ID:** `skill_canon_patch_writer`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `CANON_EVOLUTION`
**PRIORITY:** `P0`
**TAGLINE:** *Canon changes are proofs, not opinions.*

---

# 0. Header

```
Spec ID:     skill-15-canon-patch-writer
Authority:   65537
Depends On:  wish-method v1.4, Evidence Model §7, Prime Mermaid Theory v1.0
Scope:       Produce a deterministic, atomic, content-addressed PATCH_BUNDLE
             that evolves canon without violating sealed invariants.
Non-Goals:   Executing the patch, performing git commits, resolving merge conflicts.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Byte-level canonical diff + manifest hash chain.
  Verification:    Replayable patch application + offline gate execution.
  Canonicalization: LF endings, sorted JSON, path ASC ordering.
  Content-addressing: patch_id = SHA-256(canonical PATCH_BUNDLE contents).
```

Canon evolves only through deterministic artifacts.
If it cannot be replayed offline, it does not exist.

---

# 2. Observable Wish

> Given a PROPOSAL and supporting EVIDENCE, emit a deterministic, atomic PATCH_BUNDLE that updates canon while preserving index integrity, seal discipline, and replay guarantees.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, VALIDATE_INPUTS, DIFF_GENERATED, INDEX_VALIDATED,
   MANIFEST_BUILT, GATES_DEFINED, SEALED, INVALID]

INPUT_ALPHABET:
  [PROPOSAL, TARGET_CANON, EVIDENCE]

OUTPUT_ALPHABET:
  [PATCH_BUNDLE, INVALID_REPORT]

TRANSITIONS:
  INIT → VALIDATE_INPUTS
  VALIDATE_INPUTS → DIFF_GENERATED
  DIFF_GENERATED → INDEX_VALIDATED
  INDEX_VALIDATED → MANIFEST_BUILT
  MANIFEST_BUILT → GATES_DEFINED
  GATES_DEFINED → SEALED
  ANY → INVALID

FORBIDDEN_STATES:
  PARTIAL_PATCH
  UNSYNCHRONIZED_INDEX
  UNHASHED_FILE
  TIMESTAMPED_ARTIFACT
  SILENT_OVERRIDE
  NON_CANONICAL_JSON
  MULTI_TRANSACTION_PATCH
```

---

# 4. Input Validation

Reject if:

* `PROPOSAL` missing required metadata (id, sha256, version).
* `EVIDENCE` missing required proof artifacts.
* `TARGET_CANON` path outside approved workspace.
* Any file path contains `..` or absolute root reference.

If any missing → INVALID.

---

# 5. Index Invariant (LOCKED)

For each asset type:

| Type   | Required Index                   |
| ------ | -------------------------------- |
| Skill  | `canon/skills/index.json`        |
| Recipe | `canon/prime-recipes/index.json` |
| Wish   | `canon/wishes/index.json`        |

Rules:

* Index must contain entry for new asset.
* If asset updated, index version incremented.
* Index entries sorted ASCII by ID.
* Index JSON canonicalized per §7.4.
* Index hash included in MANIFEST.

Failure → INVALID.

---

# 6. Atomic Commit Discipline (LOCKED)

PATCH_BUNDLE must contain:

```
PATCH.diff
MANIFEST.json
GATES.json
(optional) STILLWATER_SEAL_REQUEST.md
```

### 6.1 PATCH.diff

* Unified diff format.
* Paths sorted ASCII ascending.
* No binary blobs.
* No CRLF endings.
* No trailing whitespace.

---

### 6.2 MANIFEST.json (LOCKED)

```json
{
  "before": [{"path": "...", "sha256": "..."}],
  "after":  [{"path": "...", "sha256": "..."}],
  "touched_paths": ["..."],
  "index_paths": ["..."],
  "patch_sha256": "..."
}
```

Rules:

* Arrays sorted by `path`.
* SHA-256 lowercase.
* Exactly one trailing newline.

---

### 6.3 GATES.json (LOCKED)

Defines deterministic replay commands:

```json
{
  "offline_required": true,
  "commands": [
    "python3 -m tools.validate_canon",
    "pytest -q"
  ]
}
```

Rules:

* Commands must run offline.
* No network.
* No environment mutation.
* Deterministic order.

---

# 7. Stillwater Seal Discipline (LOCKED)

If `PROPOSAL.seal_intent == "stillwater"`:

Must include:

```
STILLWATER_SEAL_REQUEST.md
```

Must contain:

* Benchmark comparison
* Never-Worse proof
* Regression summary
* Explicit OVERRIDE_WISH reference (if modifying sealed artifact)

Forbidden:

* Editing sealed artifact without override reference.
* Silent invariant weakening.

Violation → INVALID.

---

# 8. Byte-Level Canonicalization Rules (LOCKED)

* LF only.
* UTF-8 without BOM.
* No trailing spaces.
* JSON sorted keys.
* No indentation noise in diff.
* One trailing newline per file.
* No timestamps.
* No machine IDs.

---

# 9. Circular Dependency Guard

Detect if:

* New skill references asset added later in same patch.
* Index entry depends on file not included in patch.
* Cross-reference to asset not yet sealed.

If detected → INVALID.

---

# 10. Patch Identity (LOCKED)

After bundle construction:

```
patch_id := SHA-256(concatenation of all bundle file bytes in path ASC order)
```

patch_id must be included in:

* MANIFEST.json
* Output JSON

---

# 11. Output Schema (LOCKED)

```json
{
  "status": "OK|INVALID",
  "patch_id": "<64hex|null>",
  "bundle_path": "artifacts/canon_patches/<patch_id>/",
  "index_updates": ["skills", "recipes", "wishes"],
  "gate_commands": ["python3 -m tools.validate_canon"],
  "invalid_reason": "<string|null>"
}
```

Rules:

* index_updates sorted ASCII.
* invalid_reason required if status="INVALID".
* Deterministic field order.
* One trailing newline.

---

# 12. Verification Ladder

### 641 — Sanity

* [ ] All new files in allowed workspace
* [ ] Index synchronized
* [ ] No missing manifest entries

### 274177 — Structural Integrity

* [ ] Patch applies cleanly
* [ ] Manifest hashes match after content
* [ ] Gates executable offline

### 65537 — Final Seal

* [ ] No circular dependencies
* [ ] No forbidden states reachable
* [ ] patch_id reproducible
* [ ] Replay produces byte-identical canon

---

# 13. Ambiguity Handling

If:

* Index update ambiguous,
* Multiple candidate override wishes,
* Evidence insufficient to validate Never-Worse,

→ INVALID (not auto-patch).

---

# 14. Anti-Optimization Clause (LOCKED — AOC-1)

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
