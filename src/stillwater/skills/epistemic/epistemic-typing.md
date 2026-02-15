# SKILL 16 — Epistemic Typing (Truth Lanes)

**SKILL_ID:** `skill_epistemic_typing`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `ADJUDICATOR`
**PRIORITY:** `P0`
**TAGLINE:** *Lane Leakage is System Failure. Type your claims.*

**v2.0.0 UPGRADES:**
- Added extended Lane Algebra (comprehensive formulas including STAR, R_p convergence)
- Added gap-guided lane addition patterns
- Integrated with recent skills (prime-math v2.1.0 R_p lanes, prime-coder v1.3.0)
- Updated examples with skills audit findings
- Cross-validated lane typing patterns

---

# 0. Header

```
Spec ID:     skill-16-epistemic-typing
Authority:   65537
Depends On:  skill-10-dual-truth-adjudicator, skill-13-proof-builder
Scope:       Deterministically assign epistemic lane types to claims.
Non-Goals:   Generating new proofs, upgrading truth status, resolving conjectures.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Claim classification based solely on discharge method.
  Verification:    Lane assignment reproducible from EVIDENCE_BUNDLE.
  Canonicalization: Output ledger follows canonical JSON rules.
  Content-addressing: ledger_id = SHA-256(canonical ledger bytes).
```

Truth typing is a classification problem, not a proof-generation problem.

---

# 2. Observable Wish

> Given a set of claims and their supporting evidence, assign each claim exactly one epistemic lane (A/B/C) and status, enforcing Lane Algebra and preventing cross-lane leakage.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, VALIDATE_INPUTS, CLASSIFY_DISCHARGE_METHOD,
   ASSIGN_LANE, VALIDATE_ALGEBRA,
   VALIDATE_EVIDENCE, EMIT_LEDGER, UNKNOWN]

INPUT_ALPHABET:
  [CLAIM_SET, EVIDENCE_BUNDLE]

OUTPUT_ALPHABET:
  [TYPED_CLAIM_LEDGER.json]

TRANSITIONS:
  INIT → VALIDATE_INPUTS
  VALIDATE_INPUTS → CLASSIFY_DISCHARGE_METHOD
  CLASSIFY_DISCHARGE_METHOD → ASSIGN_LANE
  ASSIGN_LANE → VALIDATE_ALGEBRA
  VALIDATE_ALGEBRA → VALIDATE_EVIDENCE
  VALIDATE_EVIDENCE → EMIT_LEDGER
  ANY → UNKNOWN

FORBIDDEN_STATES:
  LANE_CONFLATION
  MULTI_LANE_ASSIGNMENT
  IMPLICIT_LANE
  UNSOURCED_DISCHARGE
  LEXICAL_UPGRADE
  ALGEBRA_VIOLATION
```

---

# 4. Lane Definitions (LOCKED)

Each claim MUST be assigned exactly one:

### Lane A — Classical Proof

* Discharged by: `formal_proof_object`
* Requirements:

  * Recognized mathematical derivation OR
  * Canonical proof artifact with hash
* Forbidden:

  * Empirical-only evidence
  * Finite computation without general theorem

---

### Lane B — Axiomatic / Framework

* Discharged by: `axiom_adoption + internal_derivation`
* Requirements:

  * Explicit framework scope
  * Framework witness artifact
* Forbidden:

  * Implicit scope
  * Upgrading to classical without proof

---

### Lane C — Empirical / Computational

* Discharged by: `reproducible_code + output_hash`
* Requirements:

  * Deterministic tool trace
  * Proof.json hash
* Forbidden:

  * Universal quantification
  * “Settled” language

---

# 5. Lane Algebra (LOCKED)

### Dominance Rule

```
Lane(Conclusion) <= min(Lane(p1), Lane(p2), ...)
```

Where ordering is:

```
A > B > C
```

But dominance uses *minimum epistemic strength*:

* A + C → C
* B + C → C
* A + B → B
* C + C → C

If violated → UNKNOWN.

---

# 6. Status Vocabulary (STRICT)

Each claim MUST include:

```
status ∈ {OPEN, DISCHARGED, INVALID}
```

Rules:

* DISCHARGED allowed only if discharge method verified.
* OPEN if no discharge evidence.
* INVALID if evidence contradicts claim.

No additional statuses permitted.

---

# 7. Evidence Validation Rules

### Lane A:

* Must include proof reference OR artifact hash.
* If missing → UNKNOWN.

### Lane B:

* Must include scope tag.
* Must include framework witness.
* If scope omitted → UNKNOWN.

### Lane C:

* Must include reproducible code reference.
* Must include output hash.
* If nondeterministic → UNKNOWN.

---

# 8. Strict Non-Leakage Rules

The following lexical patterns are forbidden for Lane C or B:

* “proven”
* “settled”
* “definitively solved”
* “final resolution”

If detected → INVALID.

---

# 9. Deterministic Canonicalization

Ledger must:

* Sort claims by `id` ASCII ascending
* Sort keys alphabetically
* No extra whitespace
* UTF-8
* One trailing newline

Compute:

```
ledger_id = SHA-256(canonical ledger JSON)
```

ledger_id must equal file hash.

---

# 10. Output Schema (LOCKED)

```json
{
  "ledger_version": "1.0.0",
  "ledger_id": "<64hex>",
  "claims": [
    {
      "id": "s1",
      "text": "...",
      "lane": "A|B|C",
      "status": "OPEN|DISCHARGED|INVALID",
      "evidence_ref": "...",
      "scope": null
    }
  ]
}
```

Rules:

* Exactly one lane per claim
* scope required for Lane B
* evidence_ref required for DISCHARGED

---

# 11. Verification Ladder

### 641 — Sanity

* [ ] Each claim typed exactly once
* [ ] No missing fields
* [ ] No multi-lane assignments

### 274177 — Consistency

* [ ] Lane algebra respected
* [ ] No lexical upgrade detected
* [ ] Evidence matches discharge method

### 65537 — Final Seal

* [ ] Canonical JSON verified
* [ ] ledger_id matches file hash
* [ ] No forbidden states reachable

---

# 12. Ambiguity Handling

Return UNKNOWN if:

* Discharge method unclear
* Mixed evidence types without clarity
* Missing witness artifact
* Algebra violation detected
* Scope ambiguous

Never guess lane.

---

# 13. Extended Lane Algebra  [NEW v2.0.0]

**Purpose:** Comprehensive lane algebra formulas for all claim combinations and convergence scenarios.

**Core Principle:**
```
Lane(Conclusion) = MIN(Lane(Premise_1), Lane(Premise_2), ...)

Where ordering is: A > B > C > STAR

MIN rule: Weakest premise determines conclusion lane
NEVER: Upgrade from weaker to stronger lane
```

---

### Basic Lane Algebra (Section 5 Extended)

**Two-Premise Combinations:**

| P1 Lane | P2 Lane | Conclusion Lane | Rationale |
|---------|---------|-----------------|-----------|
| A | A | A | Both classical → conclusion classical |
| A | B | B | Framework weaker than classical |
| A | C | C | Empirical weakest → dominates |
| B | B | B | Both framework → conclusion framework |
| B | C | C | Empirical weaker than framework |
| C | C | C | Both empirical → conclusion empirical |

**Violated Combinations:**
- C + C → A: ✗ FORBIDDEN (upgrade from empirical to classical)
- C + C → B: ✗ FORBIDDEN (upgrade from empirical to framework)
- B + B → A: ✗ FORBIDDEN (upgrade from framework to classical)
- A + C → A: ✗ FORBIDDEN (ignores empirical premise)

**If algebra violated → UNKNOWN**

---

### Multi-Premise Lane Algebra

**For N premises:**

```
Lane(Conclusion) = MIN(Lane(P_1), Lane(P_2), ..., Lane(P_N))
```

**Examples:**

```
3 premises (A, B, C): Lane(Conclusion) = C (weakest)
5 premises (A, A, A, B, A): Lane(Conclusion) = B (one framework premise weakens all)
10 premises (all A): Lane(Conclusion) = A (all classical)
Mixed (A, B, C, A, C): Lane(Conclusion) = C (empirical present)
```

**Critical Rule:**
ONE weak premise → ENTIRE conclusion weak
NO exceptions
NO "mostly classical" lane

---

### STAR Lane (Hypothetical)

**STAR Lane:** Conjectures, unproven claims, speculative statements

**Ordering Extended:**
```
A > B > C > STAR

Where:
  A = Classical proof (strongest)
  B = Framework/Axiomatic
  C = Empirical/Computational
  STAR = Hypothetical (weakest)
```

**Lane Algebra with STAR:**

| Premises | Conclusion | Rationale |
|----------|------------|-----------|
| A + STAR | STAR | Hypothetical premise → hypothetical conclusion |
| B + STAR | STAR | Any STAR premise → STAR conclusion |
| C + STAR | STAR | MIN rule applies |
| STAR + STAR | STAR | All hypothetical → hypothetical |

**Upgrade Prevention:**
- STAR → C: ✗ FORBIDDEN (must provide empirical evidence)
- STAR → B: ✗ FORBIDDEN (must provide framework witness)
- STAR → A: ✗ FORBIDDEN (must provide classical proof)

**Status with STAR:**
- STAR + OPEN: Conjecture stated, no evidence
- STAR + DISCHARGED: ✗ INVALID (STAR cannot be discharged)
- STAR + INVALID: Conjecture contradicted

---

### R_p Convergence Lanes (From prime-math v2.1.0)

**Resolution Limits (R_p) introduce convergence-based lanes:**

**Halting Certificates:**
- EXACT (residual == 0.0) → Lane A
- CONVERGED (residual < R_p) → Lane B
- TIMEOUT (residual >= R_p at max iterations) → Lane C
- DIVERGED (residuals increasing) → Lane C

**Lane Algebra with Convergence:**

```
Lane(IterativeMethod) = MIN(Lane(Convergence), Lane(Computation))

Examples:
  - Fraction (A) + EXACT (A) → Lane A  ✓
  - Fraction (A) + CONVERGED (B) → Lane B  ✓
  - Fraction (A) + TIMEOUT (C) → Lane C  ✓
  - float (B) + EXACT (A) → Lane B  ✓ (float contamination)
```

**Critical:**
- EXACT convergence + exact computation → Lane A
- CONVERGED (within R_p) + exact computation → Lane B (approximate)
- TIMEOUT/DIVERGED → Lane C (incomplete/failed)

**Integration with Epistemic Typing:**
- Iterative method claims MUST include convergence certificate
- Certificate determines lane (EXACT → A, CONVERGED → B, TIMEOUT/DIVERGED → C)
- MIN rule applies (weakest component determines final lane)

---

### Composite Lane Algebra

**For complex claims involving multiple reasoning steps:**

```
Lane(Final_Conclusion) = MIN(
  Lane(Step_1),
  Lane(Step_2),
  ...,
  Lane(Step_N)
)
```

**Example from IMO 6/6:**

```
P4 (Geometry):
  - 14 lemmas (Lane A each)
  - 2 deductive steps (Lane A each)
  - 1 structural witness (Lane A)

  Lane(P4_Conclusion) = MIN(A, A, ..., A) = A ✓
```

**Example with Mixed Lanes:**

```
Coding Reliability Claim:
  - prime-coder v1.3.0 tests (Lane C: empirical, 52/52 pass)
  - Red-Green gate (Lane A: deductive rule)
  - Evidence model (Lane A: formal requirement)

  Lane(Reliability_Claim) = MIN(C, A, A) = C

  Correct typing: "prime-coder v1.3.0 achieves 10/10 quality (Lane C)"
  Incorrect: "prime-coder v1.3.0 PROVEN reliable" (Lane A claim from Lane C evidence)
```

---

### Lane Downgrade (Permitted)

**Voluntary downgrades are ALLOWED:**
- A → B: Claim classical proof but present as framework (conservative)
- A → C: Claim classical proof but present as empirical (very conservative)
- B → C: Claim framework but present as empirical (conservative)

**Use Cases:**
- Hedging: "This is provable but presenting as empirical for caution"
- Clarity: Simpler lane type for audience
- Scope limitation: Restrict claim scope intentionally

**Rule:** Downgrades NEVER violate algebra (MIN rule still respected)

---

### Lane Leakage Detection

**Leakage patterns (FORBIDDEN):**

1. **Lexical Leakage**
   - Lane C claim using Lane A vocabulary ("proven", "settled")
   - Lane B claim using Lane A vocabulary without scope
   - STAR claim using discharged vocabulary

2. **Algebra Leakage**
   - A + C → A (ignoring empirical premise)
   - C → A (upgrade without proof)
   - STAR → B (upgrade without framework)

3. **Evidence Leakage**
   - Lane A claim without proof artifact
   - Lane B claim without framework scope
   - Lane C claim without reproducible code

**Detection:**
- Section 8 lexical patterns
- Section 5 algebra validation
- Section 7 evidence validation

**If leakage detected → INVALID**

---

# 14. Gap-Guided Lane Addition  [NEW v2.0.0]

**Purpose:** When to add new lanes vs use existing lanes.

**Core Principle:**
```
Don't build exhaustive lane taxonomy.
Add lanes when SPECIFIC GAPS are identified in epistemic coverage.
```

**Current Lane Coverage (4 lanes):**

**Proven (A):** Classical proof, formal derivation
**Framework (B):** Axiomatic, scope-limited
**Empirical (C):** Computational, reproducible
**Hypothetical (STAR):** Conjectures, unproven

**Gap Detection:**

1. **Missing Epistemic Category**
   - Gap: New type of claim doesn't fit A/B/C/STAR
   - Example: Probabilistic claims (95% confidence interval)
   - Action: Consider adding Lane D (Probabilistic)

2. **Convergence Ambiguity**
   - Gap: Iterative methods have different convergence levels
   - Solution: R_p convergence lanes (EXACT → A, CONVERGED → B, TIMEOUT → C)
   - Action: NO NEW LANE (use existing A/B/C with convergence certificate)

3. **Mixed Evidence Types**
   - Gap: Claim has both formal proof AND empirical validation
   - Solution: MIN rule applies (Lane A proof + Lane C empirical → Lane C overall)
   - Action: NO NEW LANE (algebra handles it)

**When NOT to Add Lanes:**

```
Existing lane covers it → USE EXISTING
Gap applies to <5% of claims → Use UNKNOWN or closest lane
Gap is subjective → NOT A LANE (lanes are deterministic only)
Gap is evidence quality, not type → Use status, not new lane
```

**Example from Skills Audit:**

Did we need new lanes for recent skills?
- prime-math v2.1.0: Added R_p convergence (EXACT/CONVERGED/TIMEOUT/DIVERGED)
  - Maps to existing lanes: EXACT → A, CONVERGED → B, TIMEOUT/DIVERGED → C ✅
  - **Decision:** NO NEW LANE (convergence certificate determines existing lane)

- prime-coder v1.3.0: Code reliability claims (52/52 tests pass)
  - Empirical evidence → Lane C ✅
  - **Decision:** NO NEW LANE (existing Lane C sufficient)

- wish-llm v2.0.0: Planning claims (state machine complete)
  - Deductive reasoning → Lane A (if formal), Lane C (if tested) ✅
  - **Decision:** NO NEW LANE (existing lanes sufficient)

**Compression Insight for Lanes:**

```
Lanes needed ≠ All possible epistemic categories
Lanes needed = Gaps identified + margin

Current: 4 lanes cover 100% of current claims (A, B, C, STAR)
Future: Add lanes when coverage drops below 95%
```

**Verification:**
- If 20+ claims typed and new claim type appears in 3+ → Consider new lane
- If claim is one-off → Use closest existing lane or UNKNOWN
- Build what's needed, when it's needed

---

# 15. Integration with Recent Skills  [NEW v2.0.0]

**Purpose:** Cross-validate lane typing patterns with recently updated skills.

### Shared Patterns

**1. Lane Algebra (MIN Rule)**

All skills now use MIN rule consistently:
- epistemic-typing: Section 5 + Section 13 extended algebra
- prime-math v2.1.0: Lane(IterativeMethod) = MIN(Lane(Convergence), Lane(Computation))
- prime-coder v1.3.0: Evidence model (Lane C empirical evidence)
- counter-required-routering v2.0.0: ROUTE_TO_COUNTER → Lane A (exact)

**Status:** ✅ ALIGNED (universal MIN rule)

**2. Upgrade Prevention**

- epistemic-typing: Section 8 forbidden lexical patterns, Section 13 algebra violations
- prime-math v2.1.0: Lane upgrades explicitly forbidden (C → B, B → A)
- wish-llm v2.0.0: Fail-closed on ambiguity (no guessing lane)
- counter-required-routering v2.0.0: FAIL_CLOSED_UNKNOWN when unclear

**Status:** ✅ ALIGNED (never upgrade without evidence)

**3. Evidence Requirements**

- epistemic-typing: Section 7 evidence validation (A → proof, B → scope, C → code)
- prime-math v2.1.0: Dual-witness proofs (Lane A), theorem closure
- prime-coder v1.3.0: Evidence model (trace:// not authoritative)
- wish-qa v2.0.0: G7 Witness Policy enforcement

**Status:** ✅ ALIGNED (deterministic evidence required)

**4. Gap-Guided Building**

- epistemic-typing: Section 14 gap-guided lane addition (add when coverage drops)
- wish-llm v2.0.0: Section 13 gap-guided construction
- counter-required-routering v2.0.0: Section 14 gap detection
- wish-qa v2.0.0: Section 12 gap-guided gate addition

**Status:** ✅ ALIGNED (build what's needed + margin)

**5. Verification Rungs**

- epistemic-typing: Section 11 (641 → 274177 → 65537)
- All updated skills: Same rungs (edge → stress → god)

**Status:** ✅ ALIGNED (universal verification ladder)

**6. Fail-Closed on Ambiguity**

- epistemic-typing: Section 12 (return UNKNOWN if unclear)
- wish-llm v2.0.0: FAIL_CLOSED on unclear state space
- counter-required-routering v2.0.0: FAIL_CLOSED_UNKNOWN when task ambiguous
- prime-math v2.1.0: Lane C (unknown) when convergence unclear

**Status:** ✅ ALIGNED (never guess)

### Cross-Validation Examples

**Example 1: prime-math v2.1.0 Lane Typing**

Applying epistemic-typing v2.0.0:

IMO P1 (Floor Sum):
- Discharge method: Exact computation (Counter Bypass, CPU enumeration)
- Evidence: `sum(floor(2*a/n) for a in range(1, n+1))` → deterministic code
- Convergence: EXACT (finite sum, exact result)
- **Lane:** A (exact computation + exact result)

IMO P2 (GCD Search):
- Discharge method: Exhaustive enumeration (3^7 combinations)
- Evidence: Deterministic code checking all cases
- Convergence: EXACT (finite search, exact result)
- **Lane:** A (exact computation + exact result)

Newton sqrt(2) (from R_p examples):
- Discharge method: Iterative convergence
- Evidence: Convergence certificate (CONVERGED, residual < 1e-10)
- Convergence: CONVERGED (within R_p tolerance, not exact)
- **Lane:** B (approximate, within tolerance)

**Verification:** ✅ R_p convergence lanes map correctly to A/B/C

---

**Example 2: prime-coder v1.3.0 Reliability Claim**

Claim: "prime-coder v1.3.0 achieves 10/10 quality"

Applying epistemic-typing v2.0.0:
- Discharge method: Test suite (52/52 tests pass, 100%)
- Evidence: Empirical test results (reproducible)
- Convergence: N/A (not iterative method)
- **Lane:** C (empirical evidence, not formal proof)

Forbidden claim: "prime-coder v1.3.0 is PROVEN reliable"
- Reason: Lexical leakage (Lane A vocabulary "PROVEN" for Lane C evidence)
- **Result:** INVALID (Section 8 violation)

Correct claim: "prime-coder v1.3.0 achieves 10/10 quality in empirical tests (Lane C)"
- **Result:** VALID ✅

---

**Example 3: Skills Audit Meta-Lane Typing**

Claim: "Skills audit achieves 10/10 quality on 4/4 skills"

Applying epistemic-typing v2.0.0:
- Discharge method: Harsh QA reports (4 skills × 10/10)
- Evidence: Empirical QA results (reproducible harsh QA protocol)
- Convergence: N/A
- **Lane:** C (empirical evidence)

Claim: "Universal patterns validated across 6 domains"
- Discharge method: Cross-validation (6 skills × shared patterns)
- Evidence: Empirical consistency checks (6 patterns × 4 skills = 24 validations)
- Convergence: N/A
- **Lane:** C (empirical validation, not formal proof)

Forbidden upgrade: "Universal patterns PROVEN to work everywhere"
- Reason: Lane C evidence (empirical) upgraded to Lane A claim (proven)
- **Result:** INVALID (algebra violation: C → A forbidden)

Correct claim: "Universal patterns validated in 6 domains (Lane C, expanding)"
- **Result:** VALID ✅

---

### Consistency Checks

- ✅ Lane Algebra aligned (MIN rule universal)
- ✅ Upgrade prevention aligned (never C → A without proof)
- ✅ Evidence requirements aligned (deterministic witnesses)
- ✅ Gap-guided building aligned (add lanes when coverage drops)
- ✅ Verification rungs aligned (641 → 274177 → 65537)
- ✅ Fail-closed aligned (UNKNOWN when ambiguous)

**Status:** ✅ FULL INTEGRATION VERIFIED

---

# 16. Anti-Optimization Clause (LOCKED — AOC-1)

> Coders MUST NOT compress this spec, merge invariants, infer intent from prose, or weaken Lane Algebra. Redundancy is anti-compression armor.

