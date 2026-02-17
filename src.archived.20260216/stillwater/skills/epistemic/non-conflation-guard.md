# SKILL 11 — Non-Conflation Guard (Hard Enforcement)

**SKILL_ID:** `skill_non_conflation_guard`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `GUARD`
**PRIORITY:** `P0`
**TAGLINE:** *Framework ≠ Classical. Bounds ≠ Infinity. Checks ≠ Proof.*

---

# 0. Header

```
Spec ID:     skill-11-non-conflation-guard
Authority:   65537
Depends On:  skill-10-dual-truth-adjudicator,
             skill-36-axiomatic-truth-lanes
Scope:       Hard enforcement preventing epistemic conflation in final prose outputs.
Non-Goals:   Claim adjudication (handled by Skill 10), lane assignment (Skill 36).
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Classical status determined only by classical proof.
  Verification:     Witness-backed dual-status consistency check.
  Canonicalization: Deterministic scan of final prose for upgrade language.
  Content-addressing: Same draft + same statuses → same verdict.
```

No rhetorical upgrade permitted.

---

# 2. Observable Wish

> Given a final prose answer and dual truth statuses, block any output that conflates framework resolution, empirical verification, or bounded computation with classical proof.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   VALIDATE_INPUT,
   LOAD_BASELINE_TABLE,
   SCAN_PROSE,
   DETECT_UPGRADE_PATTERN,
   VALIDATE_WITNESS,
   APPLY_ADJUDICATION_MATRIX,
   EMIT_PASS,
   BLOCK_OUTPUT,
   FAIL_CLOSED]

INPUT_ALPHABET:
  [draft_answer, classical_status, framework_status, witnesses]

OUTPUT_ALPHABET:
  [status, verdict, reason_tag, violation_details]

TRANSITIONS:
  INIT → VALIDATE_INPUT
  VALIDATE_INPUT → LOAD_BASELINE_TABLE
  LOAD_BASELINE_TABLE → SCAN_PROSE
  SCAN_PROSE → DETECT_UPGRADE_PATTERN
  DETECT_UPGRADE_PATTERN → VALIDATE_WITNESS
  VALIDATE_WITNESS → APPLY_ADJUDICATION_MATRIX
  APPLY_ADJUDICATION_MATRIX → EMIT_PASS
  ANY → BLOCK_OUTPUT
  ANY → FAIL_CLOSED

FORBIDDEN_STATES:
  CLASSICAL_UPGRADE_WITHOUT_PROOF
  COMPUTATION_TO_THEOREM_LEAP
  FRAMEWORK_TO_CLASSICAL_PROMOTION
  IMPLIED_SETTLEMENT
  SILENT_DOWNGRADE
```

---

# 4. Baseline Conjecture Table (LOCKED)

The following are **OPEN by default** unless canonical peer-reviewed proof is provided:

* Riemann Hypothesis
* Goldbach Conjecture
* Twin Prime Conjecture
* P vs NP
* Collatz Conjecture
* Navier–Stokes Existence

If draft_answer claims any of these are classically proven:

* Witness MUST be canonical historical citation.
* Otherwise → BLOCK.

No interpretation allowed.

---

# 5. Upgrade Detection Rules (Deterministic)

The system MUST scan prose for upgrade triggers when:

```
classical_status ∈ {open, unknown}
```

### 5.1 Hard Trigger Phrases

Examples (case-insensitive):

* “settles the conjecture”
* “proves the Riemann Hypothesis”
* “classical proof”
* “therefore the conjecture is true”
* “this establishes the theorem”
* “solves P vs NP”
* “fully resolved in mathematics”

If such phrase appears AND classical_status ≠ proven → BLOCK.

---

### 5.2 Computational Leap Detection

If prose contains:

* “verified up to”
* “checked for all n ≤”
* “no counterexample found”

AND conclusion implies universal truth → BLOCK.

Bounded verification ≠ proof.

---

# 6. Witness Validation

If classical_status = proven:

* Must include witness in:

  * canon://
  * peer-reviewed citation
  * recognized historical proof

If witness absent → BLOCK.

---

# 7. Adjudication Matrix (LOCKED)

| Framework Status | Classical Status | Prose Claim          | Verdict |
| ---------------- | ---------------- | -------------------- | ------- |
| resolved         | open             | proven               | BLOCK   |
| resolved         | open             | resolved (framework) | PASS    |
| verified up to N | open             | proven for all N     | BLOCK   |
| proven           | proven           | proven               | PASS    |

Framework resolution may not promote classical status.

---

# 8. Fail-Closed Behavior

If:

* Status fields missing
* Witness ambiguous
* Prose contains ambiguous upgrade language
* Mixed domain terminology without classification

Then:

```
status = UNKNOWN
verdict = reject_status_conflation
reason_tag = insufficient_epistemic_clarity
```

Entire draft discarded.

---

# 9. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "verdict": "pass|reject_status_conflation",
  "reason_tag": null,
  "violation_details": {
    "culprit_phrase": null,
    "classical_status": "...",
    "framework_status": "...",
    "required_baseline": "open|proven"
  }
}
```

Rules:

* status=UNKNOWN for any conflation
* culprit_phrase required if BLOCK
* required_baseline must reflect correct classical state

---

# 10. Determinism Invariant

Given identical:

* draft_answer
* classical_status
* framework_status
* witnesses

The guard MUST produce identical verdict.

No interpretive drift allowed.

---

# 11. Precedence Rules

Precedence order:

1. Missing statuses → FAIL_CLOSED
2. Baseline table violation → BLOCK
3. Upgrade phrase without proof → BLOCK
4. Computational leap → BLOCK
5. All checks pass → OK

Security and truth lanes outrank rhetorical content.

---

# 12. Anti-Optimization Clause (AOC-1)

The Guard MUST NOT:

* Rephrase output to hide conflation
* Downgrade strong claims automatically
* Replace “proven” with “resolved” silently
* Infer missing witnesses
* Treat computational evidence as classical proof

If conflation occurs → discard entire draft.

No partial salvage.


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
