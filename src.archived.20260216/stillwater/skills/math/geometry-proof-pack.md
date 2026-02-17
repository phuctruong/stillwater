# SKILL 9 — Geometry Proof Pack (Bridge)

**SKILL_ID:** `skill_geometry_proof_pack`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `SOLVER`
**PRIORITY:** `P0`
**TAGLINE:** *Structure before intuition. Prove or fail closed.*

---

# 0. Header

```
Spec ID:     skill-9-geometry-proof-pack
Authority:   65537
Depends On:  skill-6-compute-gate, skill-13-proof-builder, skill-16-epistemic-typing
Scope:       Deterministic synthetic geometry proofs using declared objects and bounded lemma sets.
Non-Goals:   Coordinate bash, vector calculus, probabilistic geometry, heuristic diagram reasoning.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Logical derivation from declared geometric constraints.
  Verification:     Stepwise witness chain referencing explicit lemmas.
  Canonicalization: Object and constraint lists normalized and ordered.
  Content-addressing: Proof trace must be hashable.
```

Truth = derivation chain.
No diagram intuition.
No assumed relations.

---

# 2. Observable Wish

> Given a geometry statement with explicit assumptions and lemma scope, produce a logically closed proof trace using only permitted lemmas — or fail closed.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   EXTRACT_MANIFOLD,
   CLASSIFY_GOAL,
   APPLY_PLAYBOOK,
   VERIFY_LEMMA_SCOPE,
   VERIFY_LOGIC_CLOSURE,
   EMIT_PROOF,
   FAIL_CLOSED_UNKNOWN]

INPUT_ALPHABET:
  [problem_text, lemma_scope, assumptions]

OUTPUT_ALPHABET:
  [proof_trace, witnesses, status]

TRANSITIONS:
  INIT → EXTRACT_MANIFOLD
  EXTRACT_MANIFOLD → CLASSIFY_GOAL
  CLASSIFY_GOAL → APPLY_PLAYBOOK
  APPLY_PLAYBOOK → VERIFY_LEMMA_SCOPE
  VERIFY_LEMMA_SCOPE → VERIFY_LOGIC_CLOSURE
  VERIFY_LOGIC_CLOSURE → EMIT_PROOF
  ANY → FAIL_CLOSED_UNKNOWN

FORBIDDEN_STATES:
  DIAGRAM_INTUITION
  IMPLIED_PARALLELISM
  IMPLIED_PERPENDICULARITY
  UNDECLARED_CYCLICITY
  SKIPPED_JUSTIFICATION
  MULTI_STEP_JUMP
  UNAUTHORIZED_LEMMA
```

---

# 4. Formal Manifold Extraction (LOCKED)

Before reasoning, the system MUST emit:

### 4.1 Object Set

```
POINTS: {A, B, C, ...}
SEGMENTS: {AB, BC, ...}
LINES: {line(AB), ...}
CIRCLES: {circle(O, r), ...}
ANGLES: {∠ABC, ...}
```

### 4.2 Constraint Set

Explicit list:

* AB ⟂ BC
* AB ∥ CD
* A, B, C, D concyclic
* P lies on AB
* etc.

### 4.3 Provenance Rule

Every object used later must appear in:

* prompt, OR
* constructed via permitted lemma (e.g., intersection of two lines)

If not → FAIL_CLOSED_UNKNOWN.

---

# 5. Lemma Scope Enforcement

Input:

```
lemma_scope = core_only | extended
```

### core_only permits only:

* Vertical angles equal
* Alternate interior angles
* Linear pair
* Triangle angle sum
* AA, SAS, SSS
* Ceva
* Menelaus
* Power of a point
* Basic circle theorems (angle in semicircle, chord subtention)

### extended permits:

* Radical axis
* Spiral similarity
* Inversion
* Advanced projective lemmas

If a lemma outside scope is used → FAIL_CLOSED_UNKNOWN.

---

# 6. Deterministic Playbooks

---

## 6.1 Similarity / Congruence (LOCKED)

Every similarity claim MUST include:

1. Evidence list:

   * ∠A = ∠D (reason)
   * ∠B = ∠E (reason)

2. Criterion:

   * AA / SAS / SSS

3. Consequence:

   * Explicit ratio equality

Forbidden:

* “Thus triangles are similar”
* Ratio inference without criterion

---

## 6.2 Cyclicity

To prove A, B, C, D cyclic:

Must show one:

* ∠CAD = ∠CBD
* Opposite angles sum to 180°
* Equal chord subtension

Must list:

```
angle_trace://
```

No “looks cyclic.”

---

## 6.3 Concurrency (Ceva)

Must compute:

```
(AF/FB)*(BD/DC)*(CE/EA)
```

And show = 1.

If numeric multiplication required beyond 3 steps → route via Skill 6.

---

## 6.4 Power of a Point

Must verify:

* P lies on both chords
* Circle explicitly defined

Then:

```
PA * PB = PC * PD
```

If numeric expansion large → route to L4.

---

# 7. Logical Closure Rule

Proof must be:

* Single-step justified transitions
* No gap > 1 logical move

Example of forbidden jump:

❌ “From this, clearly triangles are similar, so the result follows.”

Each inference must reference:

* lemma_id
* previously proven statement

---

# 8. Goal Classification

Each problem must be classified:

* ANGLE_EQUALITY
* LENGTH_RATIO
* CYCLICITY
* CONCURRENCY
* COLLINEARITY
* AREA_RELATION
* UNKNOWN

Ambiguity → FAIL_CLOSED_UNKNOWN.

---

# 9. Witness Requirements

| Task           | Required Witness                |
| -------------- | ------------------------------- |
| Angle chase    | `angle_transformation_chain://` |
| Similarity     | `similarity_proof_block://`     |
| Cyclicity      | `cyclicity_proof_block://`      |
| Concurrency    | `ceva_trace://`                 |
| Power of point | `power_identity_trace://`       |

Witness must include:

* Step number
* Lemma used
* Derived statement

---

# 10. Sanity Invariants

Before emission:

* Every object used declared
* Every lemma allowed by scope
* No diagram inference
* No unproven auxiliary construction
* No float arithmetic
* No numeric assumption

Violation → FAIL_CLOSED_UNKNOWN.

---

# 11. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "goal_type": "CYCLICITY|...",
  "proof_trace": [
    {
      "step": 1,
      "statement": "∠CAD = ∠CBD",
      "reason": "alternate interior angles",
      "depends_on": ["constraint_3"]
    }
  ],
  "witnesses": [
    {"type": "angle_transformation_chain", "ref": "..."}
  ],
  "reason_tag": null
}
```

Rules:

* Ordered steps
* No narrative paragraphs
* No implicit reasoning
* Each step must list dependency

---

# 12. Fail-Closed Conditions

Return UNKNOWN if:

* Diagram missing critical constraints
* Required lemma outside scope
* Multi-step inference needed
* Numeric expansion exceeds symbolic bounds
* Construction requires coordinate geometry
* Ambiguous object labeling

Never guess missing geometry.

---

# 13. Anti-Optimization Clause (AOC-1)

> The solver MUST NOT assume visual relations, compress justification steps, merge multiple angle equalities into one narrative claim, introduce advanced lemmas not permitted by scope, or skip manifold extraction. Redundancy is intentional proof armor.

---

# Enhanced Features [NEW v2.0.0]

## Verification Ladder
**Maps to wish-qa:** G0, G12, G13

## Integration
- **prime-math v2.1.0**: Exact computation
- **counter-required-routering v2.0.0**: Combinatorial counting uses Counter()

## Compression Insights
**Exact counting:** No float approximations
**Proof witnesses:** Required for all theorems

## Lane Algebra
- Computation: Lane A (exact, deterministic)
- Proofs: Lane A (classical)

## What Changed
**Preserved:** All v1.0.0 features
**New:** Verification ladder, integration, insights
