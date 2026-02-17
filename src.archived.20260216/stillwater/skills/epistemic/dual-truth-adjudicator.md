# SKILL 10 — Dual-Truth Adjudicator (Classical vs Framework)

**SKILL_ID:** `skill_dual_truth_adjudicator`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `ADJUDICATOR`
**PRIORITY:** `P0`
**TAGLINE:** *Separate truth domains. Never conflate.*

---

# 0. Header

```
Spec ID:     skill-10-dual-truth-adjudicator
Authority:   65537
Depends On:  wish-method v1.4 §1.2 (Witnessed Answer Principle)
Scope:       Deterministically classify claim across classical and framework domains.
Non-Goals:   Producing new proofs, resolving open conjectures, speculative reasoning.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Canonical peer-reviewed mathematical consensus for classical domain;
                   Framework-internal artifacts for framework domain.
  Verification:    Witness citation or artifact hash required for any "proven/refuted/resolved".
  Canonicalization: Output JSON sorted, deterministic.
  Content-addressing: Verdict hash = SHA-256(canonical output JSON).
```

Truth in this skill is classification only — not proof generation.

---

# 2. Observable Wish

> Given a mathematical or theoretical claim, output dual classical and framework status without conflating domains, and include required witnesses for any resolved status.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, CLASSIFY_CLAIM, IDENTIFY_DOMAIN, CHECK_CLASSICAL_STATUS,
   CHECK_FRAMEWORK_STATUS, VALIDATE_WITNESS,
   EMIT_VERDICT, UNKNOWN]

INPUT_ALPHABET:
  [claim_text, framework_context, mode_flags]

OUTPUT_ALPHABET:
  [EPISTEMIC_VERDICT.json]

TRANSITIONS:
  INIT → CLASSIFY_CLAIM
  CLASSIFY_CLAIM → IDENTIFY_DOMAIN
  IDENTIFY_DOMAIN → CHECK_CLASSICAL_STATUS
  CHECK_CLASSICAL_STATUS → CHECK_FRAMEWORK_STATUS
  CHECK_FRAMEWORK_STATUS → VALIDATE_WITNESS
  VALIDATE_WITNESS → EMIT_VERDICT
  ANY → UNKNOWN

FORBIDDEN_STATES:
  DOMAIN_CONFLATION
  UNSOURCED_PROOF
  IMPLIED_RESOLUTION
  FRAMEWORK_UPGRADE
  CLASSICAL_DOWNGRADE_WITHOUT_EVIDENCE
  VAGUE_WITNESS
```

---

# 4. Non-Conflation Invariant (LOCKED)

### Formal Rule:

```
framework_status == resolved
DOES NOT IMPLY
classical_status == proven
```

Explicit mapping:

| Condition                        | Allowed Classical Status |
| -------------------------------- | ------------------------ |
| framework resolved               | open OR unknown          |
| framework resolved_within_bounds | open                     |
| framework refuted                | open OR unknown          |
| classical proven                 | proven                   |
| classical refuted                | refuted                  |

Any automatic upgrade → UNKNOWN.

---

# 5. Witness Requirements (STRICT)

### For classical_status:

If `proven` or `refuted`:

Must include:

* Named mathematician(s)
* Publication venue or consensus record
* Year
* Recognized acceptance

Examples:

* Wiles (FLT)
* Perelman (Poincaré)
* Appel/Haken (Four Color)

If no canonical peer-reviewed acceptance → classical_status = open OR unknown.

### For framework_status:

If `resolved` or `refuted`:

Must include:

* Framework artifact ID OR
* Canonical proof hash OR
* Named framework theorem reference

If missing → UNKNOWN.

---

# 6. Framework Scoping Rules

```
claim_type:
  classical_only
  framework_only
  mixed
```

Rules:

* If claim references framework-only constructs (e.g., Resolution Math), classical_status = not_applicable.
* If claim is classical but evaluated via framework, claim_type = mixed.

---

# 7. Strict Status Vocabulary (LOCKED)

### Classical

* proven
* open
* refuted
* unknown
* not_applicable

### Framework

* resolved
* resolved_within_bounds
* open
* refuted
* not_applicable

No other status strings allowed.

---

# 8. Strict Mode Handling

If `mode_flags.strict=true`:

* Any missing witness → UNKNOWN
* Any ambiguous classification → UNKNOWN
* No narrative explanation allowed beyond structured reasoning fields

---

# 9. Verification Ladder

### 641 — Identification

* [ ] Claim domain correctly classified
* [ ] Famous conjecture correctly recognized
* [ ] Framework reference correctly parsed

### 274177 — Boundary Verification

* [ ] Bounded verification not mistaken for general proof
* [ ] Finite computational check not upgraded to theorem
* [ ] Framework scope explicitly stated

### 65537 — Final Adjudication

* [ ] Dual fields present
* [ ] Non-conflation invariant satisfied
* [ ] All proven/resolved statuses have typed witness
* [ ] Output canonicalized

---

# 10. Output Schema (LOCKED)

```json
{
  "verdict_version": "1.0.0",
  "classical_status": "proven|open|refuted|unknown|not_applicable",
  "framework_status": "resolved|resolved_within_bounds|open|refuted|not_applicable",
  "claim_type": "classical_only|framework_only|mixed",
  "framework_scope": "string or null",
  "classical_witness": {
    "source": "string or null",
    "year": "int or null"
  },
  "framework_witness": {
    "artifact_id": "string or null",
    "hash": "string or null"
  },
  "non_conflation_guard": "PASS|TRIGGERED"
}
```

Rules:

* Keys sorted ASCII ascending
* Null explicitly included if no witness
* Exactly one trailing newline
* No narrative prose outside structured fields

---

# 11. Ambiguity Handling

Return UNKNOWN if:

* Conflicting classical sources exist
* Framework artifact cannot be verified
* Claim ambiguous or underspecified
* Missing publication confirmation
* Non-conflation guard triggered

Never speculate.

---

# 12. Anti-Optimization Clause (LOCKED — AOC-1)

> Coders MUST NOT compress this spec, merge invariants, infer intent from prose, or weaken the non-conflation rule. Redundancy is anti-compression armor.

---

# 13. Enhanced Features [NEW v2.0.0]

## Verification Ladder Enhancement
**Maps to wish-qa:** G11 (Epistemic - domain separation), G12 (Witness - classical/framework witnesses required)

## Integration with Recent Skills
- **epistemic-typing v2.0.0**: Classical=Lane A, Framework=Lane B separation
- **axiomatic-truth-lanes v2.0.0**: Non-conflation = MIN operator enforcement
- **prime-math v2.1.0**: Classical proofs require dual witnesses

## Compression Insights
**Non-conflation invariant:** Framework resolved ≠ Classical proven (prevents epistemic upgrades)
**Witness typing:** Classical (peer-review) vs Framework (artifact hash)

## Lane Algebra
- Classical status: Lane A (peer-reviewed proof)
- Framework status: Lane B (framework artifact)
- Verdict: MIN(classical, framework) = no automatic upgrades

## What Changed v1.0.0 → v2.0.0
**Preserved:** All v1.0.0 features (non-conflation, witness requirements, 6 FORBIDDEN_STATES)
**New:** Verification ladder gate mapping, integration documentation, compression insights, lane algebra
**Impact:** Reliability 10/10 maintained, integration improved
