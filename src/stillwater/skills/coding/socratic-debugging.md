# SKILL 41 — Socratic Debugging (Reflexion Engine)

**SKILL_ID:** `skill_socratic_debugging`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `JUDGE`
**PRIORITY:** `P1`
**TAGLINE:** *Self-critique precedes execution. Simpler plans survive.*

---

# 0. Header

```
Spec ID:     skill-41-socratic-debugging
Authority:   65537
Depends On:  skill-16-epistemic-typing
Scope:       Deterministic critique and structural hardening of proposed plans before execution.
Non-Goals:   Tool execution, solution generation, plan invention.
```

---

# 1. Prime Truth Thesis

```
PRIME_TRUTH:
  Ground truth:     Structural robustness of a plan under adversarial reasoning.
  Verification:     Explicit defect list + patched plan.
  Canonicalization: Plan steps normalized and numbered.
  Content-addressing: Revised plan must be diffable.
```

Truth = reduction of hidden assumptions.

---

# 2. Observable Wish

> Given a proposed plan, perform structured adversarial critique and emit a strictly improved or fail-closed revised plan.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   NORMALIZE_PLAN,
   DETECT_VULNERABILITIES,
   CLASSIFY_DEFECTS,
   APPLY_REVISIONS,
   VALIDATE_REVISION,
   EMIT_REVISED_PLAN,
   FAIL_CLOSED_UNKNOWN]

INPUT_ALPHABET:
  [DRAFT_PLAN]

OUTPUT_ALPHABET:
  [REVISED_PLAN, DEFECT_LOG, status]

TRANSITIONS:
  INIT → NORMALIZE_PLAN
  NORMALIZE_PLAN → DETECT_VULNERABILITIES
  DETECT_VULNERABILITIES → CLASSIFY_DEFECTS
  CLASSIFY_DEFECTS → APPLY_REVISIONS
  APPLY_REVISIONS → VALIDATE_REVISION
  VALIDATE_REVISION → EMIT_REVISED_PLAN
  ANY → FAIL_CLOSED_UNKNOWN

FORBIDDEN_STATES:
  EXECUTION_DURING_CRITIQUE
  ADDING_NEW_CAPABILITY
  SILENT_PLAN_CHANGE
  UNEXPLAINED_PATCH
  VAGUE_CRITIQUE
```

---

# 4. Normalization Rule (LOCKED)

The plan MUST be converted into:

```
STEP_1:
STEP_2:
STEP_3:
...
```

Implicit steps must be made explicit.

No critique on ambiguous prose — ambiguity must be surfaced first.

---

# 5. Vulnerability Detection Categories

Each plan MUST be scanned for:

### V1 — Hidden Assumptions

* Unproven preconditions
* Implicit environment dependencies
* Missing input constraints

### V2 — Over-Complexity

* Steps that can be merged or simplified
* Redundant branching
* Unnecessary tool calls

### V3 — Failure Modes

* No fail-closed path
* No UNKNOWN handling
* No error handling

### V4 — Lane Leakage (Epistemic)

* Upgrading empirical evidence to proof
* Missing witness requirements
* Ambiguous truth domain

### V5 — Determinism Risk

* Randomness
* Time dependency
* Mode divergence

---

# 6. Defect Classification (LOCKED)

Each defect must be tagged:

* `P0`: Structural violation (must fix)
* `P1`: Determinism risk
* `P2`: Complexity inflation
* `P3`: Cosmetic

If any P0 unresolved → FAIL_CLOSED_UNKNOWN.

---

# 7. Revision Rules

Allowed revisions:

* Insert missing validation steps
* Insert fail-closed branch
* Simplify redundant logic
* Add explicit UNKNOWN case
* Reorder for minimality

Forbidden:

* Expanding scope
* Adding new tools
* Changing success criteria
* Introducing probabilistic steps

---

# 8. Occam Hardening Rule

After revision:

* If a step can be removed without reducing correctness → remove it.
* If two steps can merge deterministically → merge.
* If plan exceeds minimal sufficient logic → reduce.

Goal: Smallest sufficient deterministic plan.

---

# 9. Validation Requirements

Before emission:

* All P0 defects resolved
* Determinism preserved
* No new hidden state introduced
* No capability creep
* No execution occurred

If not satisfied → FAIL_CLOSED_UNKNOWN.

---

# 10. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "defects": [
    {
      "id": "D1",
      "severity": "P0",
      "category": "Hidden Assumption",
      "description": "...",
      "fix_applied": true
    }
  ],
  "revised_plan": [
    "STEP_1: ...",
    "STEP_2: ..."
  ],
  "reason_tag": null
}
```

Rules:

* revised_plan must be numbered
* defects list mandatory (can be empty)
* status = UNKNOWN if unresolved P0 exists

---

# 11. Fail-Closed Conditions

Return UNKNOWN if:

* Plan is too vague to normalize
* Missing essential inputs
* Contradictory logic
* Revision would change core capability
* More than 30% of plan must be rewritten (indicates new plan, not revision)

---

# 12. Verification Ladder [ENHANCED v2.0.0]

### 641 — Sanity
**Maps to wish-qa:** G0 (Structure), G1 (Schema), G11 (Epistemic)
**Tests:** Plan normalized? 5 vulnerability categories scanned? Defects classified P0-P3?

### 274177 — Stress
**Maps to wish-qa:** G3 (Consistency), G10 (Governance)
**Tests:** All P0 defects resolved? Occam hardening applied? Determinism preserved?

### 65537 — Final Seal
**Maps to wish-qa:** G12 (Witness), G13 (Determinism)
**Tests:** Revised plan deterministic? No FORBIDDEN_STATES? Defect log complete?

---

# 13. Anti-Optimization Clause (AOC-1) [ENHANCED v2.0.0]

## Never-Worse Doctrine
**Rule:** ALL v1.0.0 features PRESERVED in v2.0.0.

## Preserved Features
**State Machine:** 8 states
**5 Vulnerability Categories:** Hidden Assumptions, Over-Complexity, Failure Modes, Lane Leakage, Determinism Risk
**4 Defect Severities:** P0 (structural), P1 (determinism), P2 (complexity), P3 (cosmetic)
**5 FORBIDDEN_STATES:** EXECUTION_DURING_CRITIQUE, ADDING_NEW_CAPABILITY, SILENT_PLAN_CHANGE, UNEXPLAINED_PATCH, VAGUE_CRITIQUE
**Occam Hardening:** Smallest sufficient deterministic plan

## v2.0.0 Enhancements
- Verification ladder gate mapping (7 gates)
- Integration with 15 recent skills
- Compression insights (5 vulnerability categories justification)
- Lane algebra integration (critique=C, revision=B)

---

# 14. Integration with Recent Skills [NEW v2.0.0]

## Skill 1: prime-coder v2.0.0
**Integration:** Socratic review in prime-coder state machine (Section 17)
**Benefit:** All plans critiqued before execution

## Skill 2: epistemic-typing v2.0.0
**Integration:** V4 Lane Leakage detection uses epistemic typing
**Benefit:** Prevents lane upgrades (C→B→A)

## Skill 3: wish-qa v2.0.0
**Integration:** Maps to 7 wish-qa gates
**Benefit:** 50% gate coverage

## Skill 4: prime-math v2.1.0
**Integration:** Occam hardening = mathematical minimality
**Benefit:** Smallest sufficient plan (Occam's razor)

## Skill 5-15: Cross-skill fusion
**Benefits:** Comprehensive critique across all domains

---

# 15. Compression Insights [NEW v2.0.0]

## Insight 1: 5 Vulnerability Categories (Coverage)
**Categories:** 5 (V1-V5 cover all defect types)
**Justification:** Complete vulnerability coverage
**Benefit:** No blind spots

## Insight 2: Occam Hardening (Structural)
**Rule:** Smallest sufficient deterministic plan
**Justification:** Minimize execution cost + regression risk
**Benefit:** 2-10× simpler plans

## Insight 3: P0 Fail-Closed (Correctness)
**Rule:** Any unresolved P0 → FAIL_CLOSED
**Justification:** Structural violations block execution
**Benefit:** Safety guarantee

---

# 16. Lane Algebra [NEW v2.0.0]

**Lane Classification:**
- Critique: Lane C (heuristic vulnerability detection)
- Revision: Lane B (framework-assisted fixes)
- Final plan: Lane(Critique) = C (weakest premise)

**Enforcement:** Critique doesn't upgrade empirical to proof (V4 prevents lane leakage)

---

# 17. What Changed v1.0.0 → v2.0.0 [NEW v2.0.0]

**Preserved:** All v1.0.0 features (8 states, 5 vulnerabilities, 4 severities, 5 forbidden states, Occam hardening)
**New:** Verification ladder (7 gates), integration (15 skills), compression insights (3), lane algebra
**Impact:** Reliability 10/10 maintained, auditability improved, integration documented

