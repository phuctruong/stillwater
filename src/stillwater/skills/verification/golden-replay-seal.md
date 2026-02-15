# SKILL Y — Golden Replay Seal (Deterministic Replay = Promotion)

**SKILL_ID:** `skill_golden_replay_seal`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `SEALER` (Deterministic; NO creativity)
**TAGLINE:** *If it can’t replay byte-identical, it can’t be Stillwater.*

---

## 0) Contract

### Inputs

* `CANDIDATE_BUNDLE`: Patch + artifacts + outputs to be promoted (wish/recipe/skill/code).
* `REPLAY_PLAN`: Deterministic commands + mode flags + tool pins.
* `EVIDENCE_ROOT`: Directory containing normalized evidence (`/evidence/**`).
* `MODE_FLAGS`: `offline`, `strict`, `replay=true`.

### Outputs

* `GOLDEN_SEAL.json` with `SEALED|BLOCKED|UNKNOWN` and a `golden_hash` (hash-of-hashes).

---

## 1) Execution Protocol (Lane A Axioms)

### A. What “Golden Replay” Means (Hard Definition)

A candidate is **Golden Replay Stable** if, for the same pinned inputs and pinned toolchain:

1. **Patch Identity Stable**: `PATCH.diff` hash is unchanged.
2. **Evidence Normal Form Stable**: all required evidence files exist and canonicalize identically.
3. **Behavior Hash Stable**: replay runs produce the same `behavior_hash`.
4. **Proof Hash Stable**: `PROOF.json` (if applicable) yields identical `proof_id`.

**Fail-Closed:** If any required artifact is missing, status is `UNKNOWN` (non-strict) or `BLOCKED` (strict).

---

### B. Required Artifacts (Minimum Seal Set)

The candidate MUST provide:

**Patch Layer**

* `PATCH.diff`
* `MANIFEST.json` (before/after sha256 for touched files)
* `GATES.json` (offline commands)

**Evidence Layer**

* `/evidence/plan.json`
* `/evidence/tests.json`
* `/evidence/artifacts.json`
* `/evidence/run_log.txt`
* `/evidence/behavior_hash.txt`

**Optional but Mandatory When Applicable**

* `/evidence/PROOF.json` for benchmark/task claims
* `/evidence/repro_red.log` + `/evidence/repro_green.log` for bugfix claims (Kent Gate)

---

### C. Canonicalization Rules (Byte Identity)

All seal inputs must be canonicalized before hashing:

* **JSON**: UTF-8, sorted keys, compact separators `(',', ':')`, no floats (encode exact numbers as strings).
* **Text logs**: strip timestamps/PIDs/hostnames; normalize paths to repo-relative; stable sort any unordered lists.
* **Diff**: LF endings only, no trailing whitespace.

**Forbidden:** Including raw wall-clock timing as a deciding witness.

---

### D. Replay Procedure (Two-Run Minimum)

The sealer runs the `REPLAY_PLAN` twice:

* **Replay #1** → produce normalized evidence set → compute `behavior_hash_1`
* **Replay #2** → produce normalized evidence set → compute `behavior_hash_2`

**PASS condition:** `behavior_hash_1 == behavior_hash_2` AND all required hashes match manifest.

**Strict mode:** requires 2/2 equality.
**Non-strict mode:** may allow 2/3 (if configured), but **cannot** seal Stillwater core.

---

## 2) Sealing Levels (Promotion Policy)

### Levels

* `REPLAY_OK`: deterministic under replay (candidate quality)
* `GOLDEN_SEALED`: deterministic + complete evidence contract (promotion eligible)
* `STILLWATER_SEALED`: golden sealed + no capability escalation + all gates pass

### Stillwater Seal Requirements

Must additionally satisfy:

* `skill_capability_surface_guard` verdict PASS
* `skill_hamiltonian_security` PASS (if risk category requires)
* `skill_proof_certificate_builder` OK (if proof-bearing)
* `skill_schema_enforcer` OK for all emitted JSON

---

## 3) Tests Define Truth

### T1 — Two-Run Parity

* Same inputs/tool pins, replay twice
* Expect: `SEALED`, hashes equal

### T2 — Log Noise Immunity

* Inject timestamp noise into raw tool logs (pre-normalization)
* Expect: canonicalized evidence unchanged; seal still passes

### T3 — Replay Drift Block

* Any nondeterministic ordering left in evidence
* Expect: `BLOCKED`, reason `replay_instability`

### T4 — Missing Evidence Fail-Closed

* Remove `/evidence/tests.json`
* Expect: `UNKNOWN` (non-strict) or `BLOCKED` (strict)

---

## 4) Witness Policy

Seal decision must cite:

* `compute://seal/canonicalize_v1#sha256:...`
* `compute://seal/replay_run_1#sha256:...`
* `compute://seal/replay_run_2#sha256:...`
* `trace://seal/decision_report#sha256:...`

---

## 5) Output Schema (GOLDEN_SEAL.json)

```json
{
  "status": "SEALED|BLOCKED|UNKNOWN",
  "seal_level": "REPLAY_OK|GOLDEN_SEALED|STILLWATER_SEALED",
  "golden_hash": "sha256...",
  "inputs": {
    "patch_diff_sha256": "sha256...",
    "replay_plan_sha256": "sha256...",
    "toolchain_pin_sha256": "sha256..."
  },
  "replay": [
    {"run": 1, "behavior_hash": "sha256...", "proof_id": null},
    {"run": 2, "behavior_hash": "sha256...", "proof_id": null}
  ],
  "gates": {
    "capability_surface_guard": "PASS|SKIPPED",
    "security_gate": "PASS|SKIPPED",
    "schema_enforcer": "PASS|SKIPPED"
  },
  "reasons": [],
  "witnesses": [
    "compute://seal/canonicalize_v1#sha256:...",
    "compute://seal/replay_run_1#sha256:...",
    "compute://seal/replay_run_2#sha256:..."
  ]
}
```

---

## 6) Verification Ladder

### Rung 641: Sanity

* [ ] Required artifacts present.
* [ ] Canonicalization applied.

### Rung 274177: Consistency

* [ ] Two-run behavior hashes match.
* [ ] Manifest hashes match touched files.

### Rung 65537: Final Seal

* [ ] Stillwater sealing prerequisites met (if requested).
* [ ] No nondeterminism leaks remain.

*"Auth: 65537"*


---

# Enhanced Features [v2.0.0]
Verification ladder: G0, G12, G13
Integration: prime-coder, gpt-mini-hygiene
Lane algebra: Pure Lane A (deterministic)
Preserved: All v1.0.0 features
