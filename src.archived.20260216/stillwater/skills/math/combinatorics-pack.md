# SKILL 8 — Combinatorics Pack (Exact)

**SKILL_ID:** `skill_combinatorics_pack`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `SOLVER`
**PRIORITY:** `P0`
**TAGLINE:** *Count by decomposition; refuse if constraints can’t be proven exactly.*

---

# 0. Header

```
Spec ID:     skill-8-combinatorics-pack
Authority:   65537
Depends On:  skill-6-compute-gate, skill-13-proof-builder
Scope:       Exact combinatorial counting under symbolic bounds.
Non-Goals:   Asymptotics, approximations, heuristic counting, Monte Carlo.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Exact integer count.
  Verification:     Decomposition + algebra trace OR tool computation.
  Canonicalization: Result emitted as exact integer string.
  Content-addressing: witness bundle hashable.
```

All answers must be:

* Exact integer
* No floats
* No approximations
* No “~”
* No asymptotics

---

# 2. Observable Wish

> Given a well-specified counting problem and Compute Gate verdict, return an exact integer result with full decomposition witnesses — or fail closed.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   PARSE_PROBLEM,
   CLASSIFY_FAMILY,
   APPLY_PLAYBOOK,
   VALIDATE_CONSTRAINTS,
   VALIDATE_BOUNDS,
   EMIT_RESULT,
   FAIL_CLOSED_UNKNOWN]

INPUT_ALPHABET:
  [problem_text, compute_gate_verdict]

OUTPUT_ALPHABET:
  [answer, witnesses, status]

TRANSITIONS:
  INIT → PARSE_PROBLEM
  PARSE_PROBLEM → CLASSIFY_FAMILY
  CLASSIFY_FAMILY → APPLY_PLAYBOOK
  APPLY_PLAYBOOK → VALIDATE_CONSTRAINTS
  VALIDATE_CONSTRAINTS → VALIDATE_BOUNDS
  VALIDATE_BOUNDS → EMIT_RESULT
  ANY → FAIL_CLOSED_UNKNOWN

FORBIDDEN_STATES:
  HEURISTIC_PATTERN_MATCH
  UNPROVEN_SYMMETRY
  FLOAT_EVALUATION
  UNCHECKED_IE
  IMPLICIT_BOUNDARY
  UNBOUNDED_CASE_SPLIT
```

---

# 4. Routing Discipline (Strict Integration with Skill 6)

If `compute_gate_verdict = ROUTE_TO_COUNTER`
→ This skill MUST NOT execute symbolic counting.
→ Immediately return:

```
status = "UNKNOWN"
reason_tag = "ROUTED_TO_COUNTER"
```

This skill only executes when:

```
compute_gate_verdict = ALLOW_SYMBOLIC
```

---

# 5. Family Classification (LOCKED)

Each problem MUST be classified into exactly one:

* `GRID_PATH`
* `STARS_AND_BARS`
* `INCLUSION_EXCLUSION`
* `NO_ADJACENCY`
* `SURJECTION`
* `PERMUTATION_WITH_CONSTRAINT`
* `BINOMIAL_DIRECT`
* `UNKNOWN`

If classification ambiguous → FAIL_CLOSED_UNKNOWN.

---

# 6. Deterministic Playbooks (Strict)

---

## 6.1 GRID_PATH (Monotone)

### Required Decomposition:

1. Map:

   * Start S(x₁,y₁)
   * End T(x₂,y₂)
   * Required P
   * Forbidden F
2. Validate:

   * Δx ≥ 0
   * Δy ≥ 0
3. Total paths:

   ```
   C(Δx + Δy, Δx)
   ```
4. Forbidden subtraction only if F lies on monotone path.
5. Validate monotonic reachability explicitly.

### Forbidden:

* Skipping coordinate validation
* Using symmetry assumption
* Assuming F lies between S and T without proof

---

## 6.2 STARS AND BARS (Restricted)

### Required Trace:

If xᵢ ≥ Lᵢ:

```
yᵢ = xᵢ - Lᵢ
Σ yᵢ = N - Σ Lᵢ
```

Must verify:

```
N - Σ Lᵢ ≥ 0
```

Final formula:

```
C(N - Σ Lᵢ + k - 1, k - 1)
```

Forbidden:

* Skipping substitution trace
* Applying formula without verifying non-negativity

---

## 6.3 INCLUSION–EXCLUSION

Symbolic limit:

```
Max sets = 3
```

Must enumerate:

```
|A|, |B|, |C|,
|A∩B|, |A∩C|, |B∩C|,
|A∩B∩C|
```

Forbidden:

* IE for >3 sets (Route to counter)
* Assuming pairwise independence
* Skipping intersection validation

---

## 6.4 NO ADJACENCY

Linear:

```
C(n - k + 1, k)
```

Circular:

```
(n / (n - k)) * C(n - k, k)
```

Must verify:

* Linear vs circular explicitly
* n ≥ k
* n - k ≥ 0

---

## 6.5 SURJECTION

Must use:

```
k! * S(n, k)
```

OR inclusion–exclusion expansion:

```
Σ (-1)^i C(k,i)(k-i)^n
```

If n > 10 → Route to counter.

---

# 7. Boundary Validation Rules

Before emitting result:

* All binomial coefficients valid (n ≥ k ≥ 0)
* All intermediate values integer
* No negative counts
* No fractional outputs

If violated → FAIL_CLOSED_UNKNOWN.

---

# 8. Witness Requirements (Typed)

| Family     | Required Witness                     |
| ---------- | ------------------------------------ |
| GRID_PATH  | `coordinate_map://` + monotone proof |
| STARS_BARS | `transformation_trace://`            |
| IE         | `intersection_table://`              |
| NO_ADJ     | `gap_mapping://`                     |
| SURJECTION | `stirling_trace://` OR IE expansion  |

All witnesses must be:

* Deterministic
* Text-normalized
* Replayable

---

# 9. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "family": "GRID_PATH|STARS_AND_BARS|...",
  "answer": "exact_integer_string",
  "witnesses": [
    {"type": "transformation_trace", "ref": "..."}
  ],
  "reason_tag": null
}
```

Rules:

* answer must be string (no float)
* family required
* witnesses required for OK

---

# 10. Verification Ladder

### 641 — Sanity

* [ ] All intermediate values valid
* [ ] All binomial parameters valid
* [ ] No float operations used

### 274177 — Consistency

* [ ] Playbook steps explicitly followed
* [ ] All constraints validated
* [ ] No skipped boundary check

### 65537 — Final Seal

* [ ] Exact integer output
* [ ] Deterministic witness
* [ ] No forbidden states reachable

---

# 11. Fail-Closed Conditions

Return UNKNOWN if:

* Problem ambiguous
* Family unclear
* Constraint incomplete
* Symbolic bounds exceeded
* Inclusion-exclusion >3 sets
* Surjection n > 10
* Any boundary condition unverified

Never infer missing constraints.

---

# 12. Anti-Optimization Clause (AOC-1)

> Coders MUST NOT relax symbolic limits, increase IE bound, skip coordinate validation, infer symmetry, or merge boundary checks. Redundancy is intentional anti-hallucination armor.

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
