# SKILL 18 — Triple-LEAK Compression Protocol

*(Full-Side-Info Accounting & Honest Benchmarking)*

**SKILL_ID:** `skill_triple_leak_protocol`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `BENCHMARKER`
**PRIORITY:** `P0`
**TAGLINE:** *If it’s required to decode, it counts. No metadata laundering.*

---

# 0. Header

```
Spec ID:     skill-18-triple-leak
Authority:   65537
Depends On:  skill-13-proof-builder,
             skill-15-canon-patch-writer
Scope:       Deterministic compression benchmarking with full side-info inclusion.
Non-Goals:   Marketing ratios, cross-dataset amortization tricks.
```

---

# 1. Prime Truth Thesis

```
PRIME_TRUTH:
  Ground truth:     Byte count required for full decode.
  Verification:     decode(encode(X)) = X (RTC).
  Canonicalization: Stable artifact bytes + side-info bytes.
  Content-addressing: Same input + same model → identical packed bytes.
```

If a byte is needed for decode, it is part of the size.

---

# 2. Observable Wish

> Given a compression artifact and its supporting assets, compute an auditable, fully-accounted compression report that survives replay and adversarial inspection.

---

# 3. Closed State Machine

```
STATE_SET:
  [INIT,
   LOAD_ARTIFACT,
   ENUMERATE_SIDE_INFO,
   COMPUTE_TOTAL_SIZE,
   RUN_BASELINES,
   RUN_ABLATIONS,
   VERIFY_RTC,
   EMIT_REPORT,
   FAIL_CLOSED]

FORBIDDEN_STATES:
  UNCOUNTED_MODEL
  CROSS_DATASET_AMORTIZATION
  NONDETERMINISTIC_PACK
  SILENT_FALLBACK
```

---

# 4. Total Byte Accounting (The Golden Rule)

## 4.1 Strict Formula

```
Total_Size =
  |PACKED_ARTIFACT|
+ |T|   (Transforms)
+ |Σ|   (Templates / Models)
+ |Θ|   (Instance bindings)
+ |V|   (Slot streams / volatile)
+ |R|   (Residual)
+ |Index|
```

Every component must have:

* Explicit byte size
* SHA-256 hash
* Location reference

If any component required for decode is not included → FAIL_CLOSED.

---

## 4.2 Cold-Start vs Warm-Start

You MUST report:

* `cold_start_ratio` (model counted in full)
* `warm_cache_ratio` (model already present)

But:

* Claims of superiority MUST use cold_start unless comparing warm vs warm.

Cross-dataset amortization is forbidden unless:

* Dataset family declared
* Model hash identical
* Model frozen before benchmark

---

# 5. Mandatory Ablations (Triple Proof)

To validate architecture:

### A0 — Baseline

Zstd L9 (pinned version)

### A1 — Templates Only

No residual refinement

### A2 — Templates + Residual (No iteration)

### A3 — Full Triple-LEAK (with REM loop)

If:

```
|A3 - A1| < 5%
```

Flag: REM ineffective.

If A3 worse than A0 → FAIL_CLOSED unless Never-Worse fallback triggered.

---

# 6. Determinism Invariants

### 6.1 Byte Identity

Encoding same input twice must produce identical:

* PACKED_ARTIFACT bytes
* Side-info bytes
* Total_Size

If not → NONDETERMINISTIC_PACK → FAIL_CLOSED.

---

### 6.2 Controlled Corruption

Flip 1 bit in artifact:

* Decode must fail deterministically
* Failure mode must be bounded (no silent corruption)

---

# 7. Win Reporting Discipline

You MUST report:

* Median ratio vs Zstd
* Weighted average ratio
* Worst-case ratio
* Failure cases explicitly

Forbidden:

* Reporting only best case
* Omitting datasets where ratio < 1.0

---

# 8. No-Free-Lunch Disclosure

You MUST list:

* Data types where compression underperforms
* Data types where model overhead dominates
* Runtime cost (CPU/GPU time)
* Memory footprint

Compression without cost disclosure is incomplete.

---

# 9. Claim Vocabulary Restrictions

Allowed:

* “Cold-start ratio”
* “Warm-cache ratio”
* “Median win rate”

Forbidden:

* “10,000× better” without cold-start qualifier
* “Universal compression”
* “Beats entropy”

---

# 10. Replay Invariant

Given:

* Same dataset
* Same model hash
* Same tool versions

Re-running benchmark must produce identical:

* PACKED_ARTIFACT hash
* Total_Size
* Report ratios

If not → FAIL_CLOSED.

---

# 11. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "dataset": "...",
  "artifact_hash": "sha256...",
  "model_hash": "sha256...",
  "cold_start_ratio": 0.0,
  "warm_cache_ratio": 0.0,
  "breakdown": {
    "transforms": 0,
    "templates": 0,
    "instances": 0,
    "slots": 0,
    "residual": 0,
    "index": 0
  },
  "baselines": {
    "zstd_l9": 0,
    "brotli_q11": 0,
    "zip_deflate": 0
  },
  "ablations": {
    "A0": 0,
    "A1": 0,
    "A2": 0,
    "A3": 0
  },
  "win_rate_vs_zstd": {
    "median": 0.0,
    "weighted_avg": 0.0,
    "worst_case": 0.0
  },
  "iterations_to_converge": 0,
  "no_free_lunch_disclosure": ["..."]
}
```

---

# 12. Verification Ladder

### Rung 641 — Sanity

* [ ] All side-info counted?
* [ ] All hashes present?
* [ ] RTC confirmed?

---

### Rung 274177 — Consistency

* [ ] Re-run produces identical sizes?
* [ ] Ablation gaps meaningful?
* [ ] No cross-dataset amortization?

---

### Rung 65537 — Final Seal

* [ ] Cold vs warm clearly separated?
* [ ] All failure cases disclosed?
* [ ] Claims vocabulary compliant?
* [ ] Proof.json generated?

---

# Enhanced Features [v2.0.0]
Verification ladder: G0, G12, G13
Integration: prime-coder, gpt-mini-hygiene
Lane algebra: Pure Lane A (deterministic)
Preserved: All v1.0.0 features
