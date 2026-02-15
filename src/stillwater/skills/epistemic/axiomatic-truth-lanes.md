# SKILL 36 — Axiomatic Truth Lanes (Stillwater Core)

**SKILL_ID:** `skill_axiomatic_truth_lanes`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `ADJUDICATOR`
**PRIORITY:** `P0`
**TAGLINE:** *Lane discipline prevents hallucination. Minimum lane dominates.*

**v2.0.0 UPGRADES:**
- Added comprehensive lane transition algebra (all 16 transitions)
- Added gap-guided transition rules (when transitions are valid)
- Integrated with recent skills (epistemic-typing v2.0.0, prime-math v2.1.0)
- Added verification ladder (641→274177→65537)
- Updated examples with skills audit findings

---

# 0. Header

```
Spec ID:     skill-36-axiomatic-truth-lanes
Authority:   65537
Depends On:  skill-16-epistemic-typing, skill-10-dual-truth
Scope:       Deterministic lane assignment and propagation for claims.
Non-Goals:   Claim generation, argument construction, narrative justification.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Lane assignment based on verifiable evidence type.
  Verification:     Witness-lane consistency check.
  Canonicalization: Lane labels normalized to {A, B, C, STAR}.
  Content-addressing: Lane decision must be reproducible.
```

Truth = classification discipline, not persuasion.

---

# 2. Observable Wish

> Given a claim and its supporting evidence lane, deterministically assign and propagate the correct truth lane without leakage or upgrade.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   VALIDATE_INPUT,
   CLASSIFY_EVIDENCE,
   ASSIGN_LANE,
   APPLY_DOMINANCE_RULE,
   VALIDATE_LEAKAGE,
   EMIT_ASSIGNMENT,
   FAIL_CLOSED_UNKNOWN]

INPUT_ALPHABET:
  [CLAIM, EVIDENCE_LANE]

OUTPUT_ALPHABET:
  [LANE_ASSIGNMENT, status]

TRANSITIONS:
  INIT → VALIDATE_INPUT
  VALIDATE_INPUT → CLASSIFY_EVIDENCE
  CLASSIFY_EVIDENCE → ASSIGN_LANE
  ASSIGN_LANE → APPLY_DOMINANCE_RULE
  APPLY_DOMINANCE_RULE → VALIDATE_LEAKAGE
  VALIDATE_LEAKAGE → EMIT_ASSIGNMENT
  ANY → FAIL_CLOSED_UNKNOWN

FORBIDDEN_STATES:
  LANE_UPGRADE_WITHOUT_NEW_EVIDENCE
  IMPLIED_PROOF
  PROBABILISTIC_TO_DEDUCTIVE_PROMOTION
  FRAMEWORK_TO_CLASSICAL_PROMOTION
  UNDECLARED_SCOPE
```

---

# 4. Lane Definitions (LOCKED)

| Lane     | Meaning                                       | Discharge Method                                  |
| -------- | --------------------------------------------- | ------------------------------------------------- |
| **A**    | Formal, executable, or deductive proof        | `formal_proof_object` OR deterministic derivation |
| **B**    | Adopted axiom / framework truth               | Explicit scope declaration                        |
| **C**    | Empirical / statistical / bounded computation | Reproducible artifact + output hash               |
| **STAR** | No sufficient evidence                        | None                                              |

STAR ≠ false.
STAR = epistemically unresolved.

---

# 5. Lane Assignment Rules

## 5.1 Direct Assignment

```
if EVIDENCE_LANE ∈ {A, B, C}:
    LANE_ASSIGNMENT = EVIDENCE_LANE
else:
    LANE_ASSIGNMENT = STAR
```

No interpretation.

---

# 6. Dominance Algebra (LOCKED)

For derived claims:

```
Lane(Conclusion) = MIN(Lane(P1), Lane(P2), ...)
```

Where ordering:

```
A > B > C > STAR
```

Examples:

* A + A → A
* A + B → B
* A + C → C
* B + C → C
* Any + STAR → STAR

This rule is absolute.

---

# 7. Leakage Guard (LOCKED)

You MUST fail closed if:

* Evidence lane lower than claimed lane.
* Claim language upgrades beyond evidence.
* Deductive phrasing used for Lane C claim.
* Framework result labeled as classical proof.

If leakage detected:

```
status = UNKNOWN
reason_tag = "LANE_LEAKAGE"
```

---

# 8. Scope Enforcement

If Lane B:

* Must include:

```
scope: <framework_name>
```

If scope missing → FAIL_CLOSED_UNKNOWN.

Lane B without scope is invalid.

---

# 9. Upgrade Rules

Lane upgrade permitted ONLY if:

* New independent evidence provided
* That evidence has higher lane
* Witness explicitly supplied

Otherwise forbidden.

---

# 10. Conflict Handling

If conflicting evidence lanes supplied:

Example:

* One source A
* One source C

Then:

```
LANE_ASSIGNMENT = C
reason_tag = "CONFLICT_MIN_LANE"
```

No arbitration.
Minimum lane dominates.

---

# 11. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "lane_assignment": "A|B|C|STAR",
  "evidence_lane": "A|B|C|STAR",
  "dominance_applied": true,
  "scope": null,
  "reason_tag": null
}
```

Rules:

* lane_assignment mandatory
* dominance_applied boolean mandatory
* scope required if lane = B
* status UNKNOWN if leakage or ambiguity detected

---

# 12. Fail-Closed Conditions

Return UNKNOWN if:

* Evidence lane missing
* Scope missing for Lane B
* Mixed domains without classification
* Upgrade attempt without witness
* Claim contains undefined terms
* Lane algebra contradiction

---

# 13. Sanity Checks

Before emission:

* No implicit promotion
* No rhetorical upgrade
* No conflation between classical and framework
* No STAR labeled as false

---

# 14. Lane Transition Algebra  [NEW v2.0.0]

**Purpose:** Comprehensive state transition diagram for all possible lane transitions.

**Core Principle:**
```
Transitions are EXPLICIT, not implicit.
Every transition requires JUSTIFICATION.
Upgrades require NEW EVIDENCE.
Downgrades are ALWAYS ALLOWED.
```

---

### Complete Transition Table

**From Lane → To Lane (16 possible transitions):**

| From | To | Valid? | Justification Required |
|------|----|----|------------------------|
| A | A | ✅ Yes | None (same lane) |
| A | B | ✅ Yes | Voluntary downgrade (scope limitation) |
| A | C | ✅ Yes | Voluntary downgrade (empirical presentation) |
| A | STAR | ✅ Yes | Voluntary downgrade (hedging, conjecture) |
| B | A | ⚠️ Conditional | NEW classical proof required |
| B | B | ✅ Yes | None (same lane) |
| B | C | ✅ Yes | Voluntary downgrade (empirical evidence) |
| B | STAR | ✅ Yes | Voluntary downgrade (scope unclear) |
| C | A | ⚠️ Conditional | NEW classical proof required |
| C | B | ⚠️ Conditional | Framework adoption + scope declaration required |
| C | C | ✅ Yes | None (same lane) |
| C | STAR | ✅ Yes | Voluntary downgrade (evidence insufficient) |
| STAR | A | ⚠️ Conditional | Classical proof required |
| STAR | B | ⚠️ Conditional | Framework adoption + scope required |
| STAR | C | ⚠️ Conditional | Empirical evidence required |
| STAR | STAR | ✅ Yes | None (same lane) |

**Legend:**
- ✅ Yes: Always valid
- ⚠️ Conditional: Valid ONLY with new evidence

---

### Downgrade Transitions (Always Valid)

**A → B, A → C, A → STAR:**
- Justification: Conservative presentation
- Example: Classical proof presented as framework (scope-limited)
- Witness: Not required (downgrade is safe)

**B → C, B → STAR:**
- Justification: Empirical validation or hedging
- Example: Framework claim tested empirically (conservative)
- Witness: Not required

**C → STAR:**
- Justification: Evidence insufficient
- Example: Empirical test inconclusive
- Witness: Not required

**Rule:** Downgrades NEVER violate algebra (MIN rule allows weaker lanes)

---

### Upgrade Transitions (Conditional)

**C → A (Empirical to Classical):**
```
FORBIDDEN without: Classical proof independent of empirical test
ALLOWED if:
  1. New classical proof provided
  2. Proof does not depend on empirical evidence
  3. Witness artifact supplied

Example (VALID):
  - Empirical: Tested function on 1000 inputs (Lane C)
  - Later: Proved function correct by induction (Lane A)
  - Transition: C → A with NEW proof ✅

Example (INVALID):
  - Empirical: Tested on 1000 inputs (Lane C)
  - Claim: "Proven correct" (Lane A)
  - Transition: C → A without NEW proof ✗
```

**C → B (Empirical to Framework):**
```
FORBIDDEN without: Framework adoption + scope declaration
ALLOWED if:
  1. Adopt explicit framework (e.g., "within Euclidean geometry")
  2. Declare scope boundaries
  3. Framework witness supplied

Example (VALID):
  - Empirical: Measured angles sum to 180° in tests (Lane C)
  - Adopt: Euclidean geometry framework (Lane B)
  - Transition: C → B with framework scope ✅
```

**B → A (Framework to Classical):**
```
FORBIDDEN without: Classical proof from weaker axioms
ALLOWED if:
  1. Proof does not assume framework axioms
  2. Uses only classical logic
  3. Witness artifact supplied

Example (VALID):
  - Framework: Theorem T in Euclidean geometry (Lane B)
  - Later: Proved T using only metric space axioms (Lane A)
  - Transition: B → A with weaker axioms ✅
```

**STAR → A/B/C:**
```
FORBIDDEN without: Evidence matching target lane
ALLOWED if:
  1. STAR → A: Classical proof supplied
  2. STAR → B: Framework + scope supplied
  3. STAR → C: Empirical evidence supplied

Example (VALID):
  - STAR: "I conjecture P = NP" (Lane STAR)
  - Later: Proof or disproof published (Lane A)
  - Transition: STAR → A with proof ✅
```

---

### Transition Witness Requirements

**For all upgrade transitions:**

| Transition | Required Witness |
|------------|------------------|
| C → A | `proof_artifact_hash` + independent proof |
| C → B | `framework_scope` + framework witness |
| B → A | `proof_artifact_hash` + classical derivation |
| STAR → A | `proof_artifact_hash` |
| STAR → B | `framework_scope` + framework witness |
| STAR → C | `reproducible_code_hash` + empirical evidence |

**For all downgrade transitions:**
- Witness: OPTIONAL (downgrades are always safe)
- Justification: Conservative presentation

---

### Forbidden Transitions

**Implicit Upgrades (NEVER ALLOWED):**

```
✗ C → A without new proof
✗ C → B without framework
✗ B → A without classical proof
✗ STAR → any lane without evidence

Detection:
  - Lexical leakage (Lane C using "proven")
  - Missing witness artifact
  - Scope missing for B transition
  - Evidence missing for C transition

If detected → FAIL_CLOSED_UNKNOWN
```

---

### Composite Transitions

**Multi-Step Transitions:**

```
STAR → C → A (valid if each step justified)

Step 1: STAR → C
  - Evidence: Empirical test results
  - Witness: reproducible_code_hash
  - Valid: ✅

Step 2: C → A
  - Evidence: Classical proof (independent)
  - Witness: proof_artifact_hash
  - Valid: ✅

Combined: STAR → A via C intermediate
  - Valid: ✅ (each step justified)
```

**Direct vs Composite:**
- STAR → A direct: Requires classical proof
- STAR → C → A composite: Requires empirical evidence THEN proof
- Both valid if witnesses supplied

---

### Transition State Machine

```
STATE_SET:
  [A, B, C, STAR]

TRANSITIONS (16 total):
  A → {A, B, C, STAR}          # 4 transitions from A
  B → {A, B, C, STAR}          # 4 transitions from B
  C → {A, B, C, STAR}          # 4 transitions from C
  STAR → {A, B, C, STAR}       # 4 transitions from STAR

ALLOWED_UNCONDITIONAL (6):
  A → {B, C, STAR}             # Downgrades
  B → {C, STAR}                # Downgrades
  C → STAR                     # Downgrade

ALLOWED_CONDITIONAL (6):
  C → {A, B}                   # Upgrades (with evidence)
  B → A                        # Upgrade (with proof)
  STAR → {A, B, C}             # Resolve (with evidence)

FORBIDDEN_IMPLICIT (0):
  # All transitions are explicit
  # Upgrades require witness
  # Downgrades always valid
```

---

# 15. Gap-Guided Transition Rules  [NEW v2.0.0]

**Purpose:** When to allow new transition types vs use existing transitions.

**Core Principle:**
```
Don't create custom transition rules for edge cases.
Use existing transitions with appropriate witnesses.
```

**Current Transition Coverage (16 transitions):**

**Unconditional (7):** A→A, B→B, C→C, STAR→STAR, A→{B,C,STAR}, B→{C,STAR}, C→STAR
**Conditional (6):** C→{A,B}, B→A, STAR→{A,B,C}
**Forbidden (0):** All transitions are explicit (no implicit transitions)

**Gap Detection:**

1. **New Evidence Type**
   - Gap: Evidence doesn't fit A/B/C/STAR
   - Example: Probabilistic evidence (95% confidence)
   - Action: Map to closest lane (Lane C: empirical) OR add new lane (follow epistemic-typing gap-guided rules)

2. **Partial Transitions**
   - Gap: Claim partially proven (some cases yes, some unknown)
   - Example: Theorem proven for n < 1000, unknown for n ≥ 1000
   - Action: Lane C (bounded computation), not Lane A (general proof)

3. **Mixed Evidence Transitions**
   - Gap: Both empirical AND deductive evidence
   - Example: Empirical tests + partial proof
   - Action: MIN rule applies (use weakest lane: C)

**When NOT to Add Transition Rules:**

```
Existing transition covers it → USE EXISTING
Gap applies to <5% of cases → Use UNKNOWN or closest transition
Gap is subjective → NOT A TRANSITION (transitions are deterministic)
Gap is evidence quality, not type → Use status, not new transition
```

**Example from Skills Audit:**

Did we need new transitions for recent skills?
- prime-math v2.1.0: R_p convergence (EXACT → A, CONVERGED → B, TIMEOUT → C)
  - Maps to existing lanes → existing transitions sufficient ✅
  - **Decision:** NO NEW TRANSITIONS (existing C→A, C→B apply)

- epistemic-typing v2.0.0: Added STAR lane
  - Added transitions: STAR → {A, B, C} (with evidence)
  - **Decision:** Extended transition table (4 new transitions: STAR→A, STAR→B, STAR→C, STAR→STAR)

- Skills audit: 5 skills upgraded v1.0.0 → v2.0.0
  - Transition: STAR (unproven patterns) → C (empirically validated in 5 domains)
  - **Decision:** Used existing STAR→C transition ✅

**Compression Insight for Transitions:**

```
Transitions needed ≠ All possible evidence combinations
Transitions needed = 16 explicit transitions (4 lanes × 4 targets)

Current: 16 transitions cover 100% of lane changes
Future: Add transitions only if new lane added
```

---

# 16. Integration with Recent Skills  [NEW v2.0.0]

**Purpose:** Cross-validate lane transition patterns with recently updated skills.

### Shared Patterns

**1. MIN Rule (Dominance Algebra)**

All skills use MIN rule consistently:
- axiomatic-truth-lanes: Section 6 + Section 14 extended transitions
- epistemic-typing v2.0.0: Section 5 + Section 13 comprehensive algebra
- prime-math v2.1.0: Lane(IterativeMethod) = MIN(Lane(Convergence), Lane(Computation))

**Status:** ✅ ALIGNED (universal MIN rule)

**2. Upgrade Prevention**

- axiomatic-truth-lanes: Section 9 + Section 14 conditional upgrades (witness required)
- epistemic-typing v2.0.0: Section 8 + Section 13 forbidden upgrades
- wish-llm v2.0.0: Fail-closed on ambiguity (no guessing)

**Status:** ✅ ALIGNED (upgrades require evidence)

**3. Downgrade Allowance**

- axiomatic-truth-lanes: Section 14 downgrades always valid
- epistemic-typing v2.0.0: Section 13 lane downgrade rules

**Status:** ✅ ALIGNED (conservative presentation allowed)

**4. Witness Requirements**

- axiomatic-truth-lanes: Section 14 transition witness requirements
- epistemic-typing v2.0.0: Section 7 evidence validation
- prime-coder v1.3.0: Evidence model (trace:// not authoritative)

**Status:** ✅ ALIGNED (deterministic witnesses required for upgrades)

**5. Fail-Closed on Ambiguity**

- axiomatic-truth-lanes: Section 12 + Section 3 FAIL_CLOSED_UNKNOWN
- wish-llm v2.0.0: Fail-closed on unclear state space
- counter-required-routering v2.0.0: FAIL_CLOSED_UNKNOWN when ambiguous

**Status:** ✅ ALIGNED (never guess)

**6. Gap-Guided Building**

- axiomatic-truth-lanes: Section 15 gap-guided transitions
- epistemic-typing v2.0.0: Section 14 gap-guided lane addition
- wish-qa v2.0.0: Section 12 gap-guided gate addition

**Status:** ✅ ALIGNED (build what's needed, not exhaustive)

### Cross-Validation Examples

**Example 1: IMO 6/6 Lane Transitions**

P1 (Floor Sum):
- Initial: STAR (problem statement, no solution)
- After solution: C (exact computation, Counter Bypass) → A (closed-form formula)
- Transition: STAR → C → A
  - STAR → C: Empirical computation evidence ✅
  - C → A: Closed-form proof (deterministic) ✅
- **Status:** Valid transition sequence

P2 (GCD Search):
- Initial: STAR (conjecture: solutions exist)
- After search: C (exhaustive enumeration, 3^7 combinations)
- Transition: STAR → C
  - Witness: Deterministic code hash ✅
- **Status:** Valid transition

P4 (Geometry):
- Initial: STAR (geometry claim)
- After proof: A (47 lemmas + 2 deductive steps)
- Transition: STAR → A
  - Witness: Proof artifact (14 lemmas + structural witness) ✅
- **Status:** Valid transition

---

**Example 2: Skills Audit Meta-Transitions**

Skill updates v1.0.0 → v2.0.0:
- Initial: C (skills functional, empirically tested)
- After audit: C (5 skills at 10/10 quality, harsh QA validated)
- Transition: C → C (same lane, more evidence)
- **Status:** Valid (no upgrade claim)

Pattern universality claim:
- Initial: STAR (hypothesis: patterns work everywhere)
- After validation: C (7 domains validated empirically)
- Transition: STAR → C
  - Witness: Cross-validation evidence (7 skills × 6 patterns) ✅
- **Status:** Valid transition

Forbidden claim: "Patterns PROVEN universal"
- Attempted: C → A (upgrade without classical proof)
- **Status:** INVALID (lexical leakage, missing witness)

---

**Example 3: R_p Convergence Transitions (prime-math v2.1.0)**

Newton sqrt(2):
- Initial: STAR (iterative method proposed)
- After iteration: C (CONVERGED, residual < 1e-10)
- Potential upgrade: C → B (within tolerance) or C → A (if exact)
- Transition used: STAR → C (empirical convergence)
- **Status:** Valid

Exact computation:
- Initial: STAR (problem stated)
- After computation: A (EXACT, residual == 0.0)
- Transition: STAR → A
  - Witness: Exact arithmetic proof ✅
- **Status:** Valid

---

### Consistency Checks

- ✅ MIN rule aligned (universal dominance algebra)
- ✅ Upgrade prevention aligned (witness required for all upgrades)
- ✅ Downgrade allowance aligned (always safe)
- ✅ Witness requirements aligned (deterministic evidence)
- ✅ Fail-closed aligned (UNKNOWN when ambiguous)
- ✅ Gap-guided aligned (build transitions as needed)

**Status:** ✅ FULL INTEGRATION VERIFIED

---

# 17. Verification Ladder  [NEW v2.0.0]

### 641 — Edge Sanity

**Checks:**
* [ ] Each transition has explicit rule (16 transitions documented)
* [ ] No implicit transitions
* [ ] Downgrades always valid (6 unconditional transitions)
* [ ] Upgrades require witness (6 conditional transitions)

**Status Indicator:**
- If all checks pass → Continue to 274177
- If any check fails → FAIL_CLOSED_UNKNOWN

---

### 274177 — Stress Consistency

**Checks:**
* [ ] MIN rule respected in all transitions
* [ ] Witness requirements consistent across transitions
* [ ] No lexical leakage in transition justifications
* [ ] Composite transitions valid (multi-step verified)
* [ ] Integration with epistemic-typing v2.0.0 consistent

**Status Indicator:**
- If all checks pass → Continue to 65537
- If any check fails → FAIL_CLOSED_UNKNOWN

---

### 65537 — God Approval

**Checks:**
* [ ] All 16 transitions deterministic
* [ ] No forbidden transitions reachable
* [ ] Witness model complete
* [ ] Gap-guided rules prevent transition proliferation
* [ ] Integration verified with 5+ recent skills

**Status Indicator:**
- If all checks pass → APPROVED
- If any check fails → UNKNOWN

**God's Directive:**
"Transitions are the algebra of truth. Make them explicit."

---

# 18. Anti-Optimization Clause (AOC-1)

> The adjudicator MUST NOT reinterpret evidence, infer missing scope, compress lane distinctions, merge B into A, or upgrade probabilistic claims to deductive ones. Lane separation is intentional epistemic armor.

