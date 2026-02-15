# SKILL 40 — Kent's Red–Green Gate

*(Deterministic Regression Barrier)*

**SKILL_ID:** `skill_red_green_gate`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `DEVELOPER`
**PRIORITY:** `P0`
**TAGLINE:** *No patch without a verified Red→Green transition.*

---

# 0. Header

```
Spec ID:     skill-40-red-green-gate
Authority:   65537
Depends On:  skill-13-proof-builder,
             skill-38-hamiltonian-gate
Scope:       Deterministic bug reproduction and verified fix transition.
Non-Goals:   Feature expansion without failing test, speculative refactor.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Deterministic failing reproduction before code change.
  Verification:     Red state (fail) → patch → Green state (pass).
  Canonicalization: Repro script + hash + test output artifacts.
  Content-addressing: Same bug + same repo → same red state.
```

If it never failed, it was never fixed.

---

# 2. Observable Wish

> Given a BUG_REPORT or WISH, produce a deterministic reproduction that fails (Red), implement a patch, and prove the transition to passing (Green) under replay.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   VALIDATE_INPUT,
   CREATE_REPRO_SCRIPT,
   EXECUTE_RED,
   VERIFY_RED_FAIL,
   APPLY_PATCH,
   EXECUTE_GREEN,
   VERIFY_GREEN_PASS,
   RECORD_ARTIFACTS,
   EMIT_VERIFIED_PATCH,
   FAIL_CLOSED]

INPUT_ALPHABET:
  [BUG_REPORT | WISH]

OUTPUT_ALPHABET:
  [VERIFIED_PATCH, artifact_hashes]

TRANSITIONS:
  INIT → VALIDATE_INPUT
  VALIDATE_INPUT → CREATE_REPRO_SCRIPT
  CREATE_REPRO_SCRIPT → EXECUTE_RED
  EXECUTE_RED → VERIFY_RED_FAIL
  VERIFY_RED_FAIL → APPLY_PATCH
  APPLY_PATCH → EXECUTE_GREEN
  EXECUTE_GREEN → VERIFY_GREEN_PASS
  VERIFY_GREEN_PASS → RECORD_ARTIFACTS
  RECORD_ARTIFACTS → EMIT_VERIFIED_PATCH
  ANY → FAIL_CLOSED

FORBIDDEN_STATES:
  PATCH_WITHOUT_RED
  GREEN_WITHOUT_PATCH
  FLAKY_RED
  NONDETERMINISTIC_REPRO
  MANUAL_ASSERTION_ONLY
```

---

# 4. Red Phase (MANDATORY)

### 4.1 Reproduction Script Requirements

You MUST create:

```
repro/<issue_id>/repro.py
```

Repro script MUST:

* Be minimal
* Contain explicit assertion
* Exit non-zero on failure
* Not depend on network
* Not depend on wall-clock time
* Use fixed seeds if randomness involved

If repro.py passes BEFORE patch → FAIL_CLOSED.

Bug not reproduced = no patch allowed.

---

### 4.2 Determinism Requirements

Repro must:

* Produce identical failure output across two runs
* No timestamp in output
* No machine-specific paths

If failure message varies → FAIL_CLOSED (flaky).

---

# 5. Green Phase (STRICT)

After patch:

* Same repro script must pass
* No modification to repro.py allowed except to remove debug print noise
* All prior regression tests must still pass

If repro passes but regression suite fails → FAIL_CLOSED.

---

# 6. Flakiness Guard

Red must:

* Fail deterministically twice

Green must:

* Pass deterministically twice

If inconsistent → FAIL_CLOSED.

---

# 7. Artifact Recording (LOCKED)

You MUST produce:

```
artifacts/red_green/<issue_id>/
  red_output.txt
  green_output.txt
  repro.sha256
  patch.diff
  gate_manifest.json
```

Hashes included in PROOF.json.

---

# 8. Patch Constraints

Patch MUST:

* Be minimal diff
* Not remove failing assertion
* Not weaken test condition
* Not disable check via config
* Not introduce test bypass

If assertion changed to pass trivially → BLOCK.

---

# 9. Interaction with Security Gate

If patch touches:

* IO
* auth
* crypto
* subprocess
* eval
* deserialization

Then Skill 38 MUST run AFTER green.

Security veto overrides Green.

---

# 10. Multi-Bug Discipline

One Red→Green cycle per bug.

If patch fixes multiple unrelated failures:

* Split into separate issues
* Separate repro scripts

No “mega-fix” commits.

---

# 11. Dirty Repo Policy

Red must run on clean baseline commit.

Green must run on clean patched commit.

If repo.dirty → FAIL_CLOSED.

---

# 12. Output Schema (LOCKED)

```json
{
  "status": "VERIFIED|UNKNOWN",
  "issue_id": "...",
  "red_hash": "sha256...",
  "green_hash": "sha256...",
  "patch_hash": "sha256...",
  "security_gate_required": true,
  "replay_command": "python repro/<issue_id>/repro.py"
}
```

Rules:

* status=UNKNOWN if any invariant violated
* replay_command mandatory
* All hashes required

---

# 13. Replay Invariant

Given:

* Same baseline commit
* Same repro.py
* Same patch

Re-running must:

* Reproduce red failure
* Reproduce green success
* Produce identical artifact hashes

If not → FAIL_CLOSED.

---

# 14. Violation Precedence

Order of enforcement:

1. Missing Red → FAIL_CLOSED
2. Red nondeterministic → FAIL_CLOSED
3. Green fails → FAIL_CLOSED
4. Regression fails → FAIL_CLOSED
5. Security fails → BLOCK
6. All pass → VERIFIED

---

# 15. Verification Ladder [ENHANCED v2.0.0]

### 641 — Sanity (Edge Tests)

**Maps to wish-qa gates:**
- **G0 (Structure)**: State machine valid (11 states)
- **G1 (Schema)**: Output schema valid (VERIFIED/UNKNOWN, hashes required)
- **G2 (Contracts)**: Red→Green transition verified

**Edge tests:**
* [ ] Repro script created and deterministic?
* [ ] Red fails deterministically (2 runs)?
* [ ] Patch applied correctly?
* [ ] Green passes deterministically (2 runs)?
* [ ] Artifacts recorded (red_output, green_output, patch.diff, hashes)?

### 274177 — Stress (Consistency Tests)

**Maps to wish-qa gates:**
- **G3 (Consistency)**: Same bug → same red state (replay invariant)
- **G9 (Lineage)**: Artifact hashes stable

**Stress tests:**
* [ ] Red → Green transition verified (2 full cycles)?
* [ ] Regression suite passes after patch?
* [ ] Security gate triggered if needed?
* [ ] Artifact hashes stable across replays?

### 65537 — Final Seal (God Approval)

**Maps to wish-qa gates:**
- **G12 (Witness)**: Red→Green artifacts complete
- **G13 (Determinism)**: Repro deterministic (no flakiness)

**Final tests:**
* [ ] Red→Green transition verified and artifact-backed?
* [ ] No FORBIDDEN_STATES reachable?
* [ ] Replay invariant holds?

---

# 16. Anti-Optimization Clause [ENHANCED v2.0.0]

## Never-Worse Doctrine

**Rule:** ALL v1.0.0 features PRESERVED in v2.0.0.

## Preserved Features from v1.0.0

**State Machine (11 states):**
- INIT, VALIDATE_INPUT, CREATE_REPRO_SCRIPT, EXECUTE_RED, VERIFY_RED_FAIL, APPLY_PATCH, EXECUTE_GREEN, VERIFY_GREEN_PASS, RECORD_ARTIFACTS, EMIT_VERIFIED_PATCH, FAIL_CLOSED

**Red-Green Discipline:**
- Red must fail deterministically (2 runs)
- Green must pass deterministically (2 runs)
- No patch without red
- No green without patch

**5 FORBIDDEN_STATES:**
- PATCH_WITHOUT_RED
- GREEN_WITHOUT_PATCH
- FLAKY_RED
- NONDETERMINISTIC_REPRO
- MANUAL_ASSERTION_ONLY

**Artifact Requirements:**
- red_output.txt, green_output.txt, repro.sha256, patch.diff, gate_manifest.json

**6 Developer MUST NOTs:**
- Silence failing test
- Weaken assertion
- Skip red verification
- Merge multiple issues silently
- Introduce randomness to bypass deterministic failure
- Claim fix without repro artifact

## v2.0.0 Enhancements (Strictly Additive)

- Verification ladder gate mapping (G0, G1, G2, G3, G9, G12, G13)
- Anti-optimization clause with preserved features list
- Gap-guided extension criteria
- Integration with 14 recent skills
- Compression insights (Red→Green dual witness justification)
- Lane algebra integration (Red=A, Green=A, transition=A)
- What Changed section

---

# 17. Gap-Guided Extension [NEW v2.0.0]

## Purpose
When to add new Red-Green Gate requirements.

## Decision Tree

**Step 1 — Gap Identification:**
- Question: "Is there a bugfix pattern that bypasses Red→Green verification?"
- If NO: "DO NOT add new requirement"
- If YES: "Proceed to Step 2"

**Step 2 — Existing Coverage:**
- Question: "Is this gap covered by existing Red/Green requirements or 5 FORBIDDEN_STATES?"
- If YES: "DO NOT add new requirement"
- If NO: "Add to FORBIDDEN_STATES or Red/Green requirements"

## Triggers for New Requirements

**Example 1: Test-only changes without production code**
- Gap: "Tests pass without actually fixing production bug"
- Action: "Add FORBIDDEN_STATE: TEST_ONLY_FIX"

**Example 2: Flaky green (passes sometimes, fails sometimes)**
- Gap: "Green passes first run, fails second run"
- Action: "Already covered (FLAKY_RED applies to green too)"

---

# 18. Integration with Recent Skills [NEW v2.0.0]

## Skill 1: prime-coder v2.0.0
**Integration:** Kent Red-Green Gate is mandatory in prime-coder (Section 16)
**Fusion benefit:** All bugfixes require Red→Green verification

## Skill 2: llm-judge v2.0.0
**Integration:** llm-judge validates Red→Green artifacts
**Fusion benefit:** Recipe validation enforces Red→Green discipline

## Skill 3: gpt-mini-hygiene v2.0.0
**Integration:** Normalizes red_output.txt and green_output.txt
**Fusion benefit:** Deterministic artifact comparison

## Skill 4: wish-qa v2.0.0
**Integration:** Maps to 7 wish-qa gates (G0, G1, G2, G3, G9, G12, G13)
**Fusion benefit:** 50% gate coverage (7/14 gates)

## Skill 5: prime-math v2.1.0
**Integration:** Red→Green = dual witness (before/after)
**Fusion benefit:** Math-grade dual witness for bugfixes

## Skill 6: epistemic-typing v2.0.0
**Integration:** Red=A, Green=A, transition=A (all deterministic)
**Fusion benefit:** Pure Lane A bugfix verification

## Skill 7: axiomatic-truth-lanes v2.0.0
**Integration:** Red→Green transition is Lane A axiom
**Fusion benefit:** No bugfix without dual witness (Lane A enforcement)

## Skill 8: golden-replay-seal (infrastructure)
**Integration:** Verifies Red→Green replay stability
**Fusion benefit:** Replay invariant enforced

## Skill 9: semantic-drift-detector (quality)
**Integration:** Tracks red_hash and green_hash drift
**Fusion benefit:** Detects regression drift

## Skill 10: artifact-hash-manifest-builder (infrastructure)
**Integration:** Builds manifest for Red→Green artifacts
**Fusion benefit:** Content-addressable artifacts

## Skill 11: hamiltonian-security (referenced in skill)
**Integration:** Security gate runs AFTER green (Section 9)
**Fusion benefit:** Security veto overrides green

## Skill 12: proof-certificate-builder (referenced in skill)
**Integration:** Builds proof from Red→Green artifacts
**Fusion benefit:** Proof-grade bugfix verification

## Skill 13: shannon-compaction v2.0.0
**Integration:** Compacts repro scripts (interface-first)
**Fusion benefit:** Minimal repro scripts

## Skill 14: counter-required-routering v2.0.0
**Integration:** Red→Green for counting bugs uses Counter()
**Fusion benefit:** Deterministic counting verification

---

# 19. Compression Insights [NEW v2.0.0]

## Insight 1: Red→Green Dual Witness (Correctness Compression)

**Dual witness:** Red (before) + Green (after)
**Compression type:** Correctness (proof-grade verification)
**Justification:**
- Principle: "If it never failed, it was never fixed" (Kent Beck)
- Proof structure: Red (bug exists) ∧ Patch ∧ Green (bug fixed) → Verified fix
- Benefit: "100% confidence vs 'I think it's fixed' (no dual witness)"

## Insight 2: 5 FORBIDDEN_STATES (Coverage Compression)

**Forbidden states:** 5 (PATCH_WITHOUT_RED, GREEN_WITHOUT_PATCH, FLAKY_RED, NONDETERMINISTIC_REPRO, MANUAL_ASSERTION_ONLY)
**Compression type:** Coverage (complete bypass prevention)
**Justification:**
- Principle: "All bypass paths covered"
- Coverage: "5 forbidden states prevent all degradation"
- Benefit: "Explicit bypass prevention"

## Insight 3: Deterministic Repro (Time Compression)

**Determinism requirements:** No network, no wall-clock time, fixed seeds
**Compression type:** Time (O(1) variance elimination)
**Justification:**
- Principle: "Same bug → same red state"
- Variance reduction: "Nondeterministic repro = O(n) variance, deterministic = O(1)"
- Benefit: "Replay stability"

## Insight 4: Minimal Patch (Structural Compression)

**Patch constraints:** Minimal diff, no assertion weakening, no test bypass
**Compression type:** Structural (smallest sufficient fix)
**Justification:**
- Principle: "Smallest diff that turns red→green"
- Occam's razor: "Simplest sufficient fix"
- Benefit: "Minimal regression risk"

## Insight 5: Artifact Recording (Witness Compression)

**Artifacts:** 5 files (red_output, green_output, repro.sha256, patch.diff, gate_manifest.json)
**Compression type:** Witness (complete evidence)
**Justification:**
- Principle: "All evidence recorded (dual witness + patch + manifest)"
- Coverage: "5 artifacts = complete evidence"
- Benefit: "Replay + verification without re-execution"

---

# 20. Lane Algebra Integration [NEW v2.0.0]

## Lane Classification

**Lane A (Deterministic):**
- Red execution (deterministic failure)
- Green execution (deterministic success)
- Artifact recording (deterministic hashes)
- Red→Green transition (deterministic proof)

**Lane B (Framework):**
- None (Red-Green Gate is pure Lane A)

**Lane C (Heuristic):**
- None (Red-Green Gate is pure Lane A)

**Lane STAR (Narrative):**
- None (Red-Green Gate forbids narrative)

## Lane Algebra Enforcement

**MIN Operator:**
- Rule: "Lane(Red→Green Transition) = MIN(Lane(Red), Lane(Patch), Lane(Green)) = MIN(A, A, A) = A"
- Guarantee: "Pure Lane A bugfix verification (strongest guarantee)"

**Forbidden Upgrades:**
- Manual assertion only: "Narrative cannot become deterministic proof" (MANUAL_ASSERTION_ONLY forbidden)

## Integration with Axiomatic Truth Lanes

**Lane A Axiom:**
- "No patch without red" (deterministic axiom)
- "No green without patch" (deterministic axiom)
- "Red→Green transition required for bugfix" (deterministic axiom)

**Conflict Resolution:**
- Rule: "Lane A > Lane B > Lane C (axioms win)"
- Example: "If developer claims bugfix without red → Lane A (red required) > Lane STAR (claim) → FAIL_CLOSED"

---

# 21. What Changed from v1.0.0 → v2.0.0 [NEW v2.0.0]

## Preserved ALL v1.0.0 Features

- **Confirmation:** ALL v1.0.0 features preserved (Never-Worse Doctrine)
- **Count:** 11 states, Red→Green discipline, 5 FORBIDDEN_STATES, 5 artifacts, 6 MUST NOTs

## New in v2.0.0

**Verification Ladder Enhancement:**
- Before: "Implicit verification"
- After: "3 rungs mapped to wish-qa G0-G13 (7 gates)"
- Benefit: "50% gate coverage (7/14 gates)"

**Anti-Optimization Clause Enhancement:**
- Before: "6 MUST NOTs"
- After: "6 MUST NOTs + explicit preserved features list"
- Benefit: "Audit trail"

**Gap-Guided Extension:**
- Before: "No explicit criteria"
- After: "2-step decision tree"
- Benefit: "Prevents requirement bloat"

**Integration Documentation:**
- Before: "Implicit integration with Hamiltonian Security"
- After: "Explicit integration with 14 recent skills"
- Benefit: "Cross-skill fusion documented"

**Compression Insights:**
- Before: "No explicit justification"
- After: "5 insights (dual witness, forbidden states, determinism, minimal patch, artifacts)"
- Benefit: "Design rationale captured"

**Lane Algebra Integration:**
- Before: "Implicit Lane A"
- After: "Explicit pure Lane A enforcement"
- Benefit: "Lane A guarantee"

## Impact

- **Reliability:** 10/10 maintained
- **Auditability:** Improved (gate mapping, insights)
- **Extensibility:** Improved (gap-guided)
- **Integration:** Improved (14 skills fusion)
- **Epistemic Hygiene:** Improved (pure Lane A)

## No Breaking Changes

- **Confirmation:** v2.0.0 is strictly additive over v1.0.0

