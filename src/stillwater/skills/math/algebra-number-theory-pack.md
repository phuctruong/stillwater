# SKILL 7 — Algebra / Number Theory Pack (Exact)

**SKILL_ID:** `skill_algebra_number_theory_pack`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `SOLVER`
**PRIORITY:** `P0`
**TAGLINE:** *Closed-form when safe; otherwise route or refuse.*

---

# 0. Header

```
Spec ID:     skill-7-algebra-number-theory-pack
Authority:   65537
Depends On:  skill-6-compute-gate, skill-13-proof-builder
Scope:       Exact algebraic and elementary number theory under bounded symbolic limits.
Non-Goals:   Heuristic factorization, probabilistic primality, asymptotics.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Exact integer or exact rational result.
  Verification:     Deterministic derivation trace OR tool computation.
  Canonicalization: Output emitted as canonical integer/fraction string.
  Content-addressing: Witness bundle hashable.
```

No floats.
No approximations.
No probabilistic claims.

---

# 2. Observable Wish

> Given a well-specified algebra or number theory task and Compute Gate verdict, return an exact result with explicit verification trace — or fail closed.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   PARSE_PROBLEM,
   CLASSIFY_FAMILY,
   APPLY_PLAYBOOK,
   VALIDATE_CONDITIONS,
   VALIDATE_SANITY,
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
  APPLY_PLAYBOOK → VALIDATE_CONDITIONS
  VALIDATE_CONDITIONS → VALIDATE_SANITY
  VALIDATE_SANITY → EMIT_RESULT
  ANY → FAIL_CLOSED_UNKNOWN

FORBIDDEN_STATES:
  ASSUMED_FACTORIZATION
  UNVERIFIED_CONGRUENCE
  FLOAT_ARITHMETIC
  PROBABILISTIC_PRIME
  SKIPPED_GCD_CHECK
  IMPLICIT_DOMAIN_ASSUMPTION
```

---

# 4. Routing Discipline (Integration with Skill 6)

If:

```
compute_gate_verdict = ROUTE_TO_COUNTER
```

→ This skill MUST NOT compute symbolically.
→ Return:

```
status = "UNKNOWN"
reason_tag = "ROUTED_TO_COUNTER"
```

Symbolic execution allowed only when:

```
compute_gate_verdict = ALLOW_SYMBOLIC
```

---

# 5. Family Classification (LOCKED)

Each problem MUST be classified as:

* `FACTORIZATION`
* `TOTIENT`
* `CRT`
* `MULTIPLICATIVE_ORDER`
* `LEGENDRE_FACTORIAL`
* `MODULAR_ARITHMETIC`
* `DIVISOR_COUNT`
* `GCD_LCM`
* `UNKNOWN`

Ambiguous classification → FAIL_CLOSED_UNKNOWN.

---

# 6. Deterministic Playbooks

---

## 6.1 FACTORIZATION

### Hard Bound:

Symbolic allowed only if:

```
N ≤ 100
```

For N > 100 → route to counter.

### Required Trace:

* Trial division list:

  * primes ≤ √N
* Explicit remainder checks

Forbidden:

* “obvious factorization”
* Skipping primes
* Probabilistic tests

---

## 6.2 TOTIENT (φ)

### Required Steps:

1. Factorize N (see above rule)
2. Apply:

```
φ(N) = N ∏ (1 - 1/p_i)
```

3. Simplify exactly
4. Sanity check:

   * If N > 2 and φ(N) odd → FAIL_CLOSED_UNKNOWN

---

## 6.3 CRT (Chinese Remainder Theorem)

### Required:

1. List each congruence
2. Verify moduli are pairwise coprime:

   * Explicit gcd(m_i, m_j) checks
3. Compute solution
4. Verification block:

```
result mod m_i = a_i
```

If any fail → FAIL_CLOSED_UNKNOWN.

Forbidden:

* Skipping gcd
* Using formula without verification
* Claiming uniqueness without proof

---

## 6.4 MULTIPLICATIVE ORDER ordₘ(a)

Preconditions:

* gcd(a, m) = 1 must be shown.

Required:

1. Compute φ(m)
2. Factor φ(m)
3. Enumerate divisors d in ascending order
4. Verify:

```
a^d ≡ 1 (mod m)
```

Stop at first valid d.

Symbolic allowed only if:

* φ(m) ≤ 100
* divisor count ≤ 8

Otherwise → route to counter.

---

## 6.5 LEGENDRE (Trailing Zeros)

Required:

List every term:

```
⌊N/5⌋
⌊N/25⌋
⌊N/125⌋
...
```

until 5ᵏ > N.

Verification:

* Explicit summation list
* No skipped powers

---

## 6.6 GCD / LCM

Required:

* Euclidean algorithm trace
* Back-substitution if needed

Forbidden:

* Mental gcd claim
* Skipping remainder steps

---

# 7. Sanity Invariants

Before emission:

* All outputs exact integers or rational strings
* No decimals
* No approximations
* φ(N) even for N > 2
* CRT solution satisfies all congruences
* gcd conditions verified
* Domain assumptions explicit

If violated → FAIL_CLOSED_UNKNOWN.

---

# 8. Witness Requirements

| Family        | Required Witness                          |
| ------------- | ----------------------------------------- |
| FACTORIZATION | `trial_division_trace://`                 |
| TOTIENT       | `factor_trace://` + `totient_formula://`  |
| CRT           | `gcd_checks://` + `verification_block://` |
| ORDER         | `modular_exponent_trace://`               |
| LEGENDRE      | `term_list://`                            |
| GCD           | `euclidean_trace://`                      |

All witnesses must be deterministic and replayable.

---

# 9. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "family": "TOTIENT|CRT|...",
  "answer": "exact_integer_or_fraction_string",
  "witnesses": [
    {"type": "trial_division_trace", "ref": "..."}
  ],
  "reason_tag": null
}
```

Rules:

* answer as string
* witnesses mandatory for OK
* family mandatory

---

# 10. Verification Ladder

### 641 — Sanity

* [ ] All gcd checks shown
* [ ] No float arithmetic
* [ ] All factor checks explicit

### 274177 — Consistency

* [ ] CRT verification block correct
* [ ] Order verified by exponentiation
* [ ] φ parity invariant holds

### 65537 — Final Seal

* [ ] Exact integer/rational output
* [ ] Deterministic witness
* [ ] No forbidden states reachable

---

# 11. Fail-Closed Conditions

Return UNKNOWN if:

* N > symbolic bound
* gcd condition not met
* φ(m) too large
* Too many divisors
* Domain unclear
* Moduli not coprime
* Any sanity invariant fails

Never assume missing structure.

---

# 12. Anti-Optimization Clause (AOC-1)

> Coders MUST NOT assume factorization, skip gcd checks, widen symbolic bounds, replace integer arithmetic with floats, or weaken verification requirements. Redundancy is intentional anti-hallucination armor.

---

# Enhanced Features [NEW v2.0.0]

## Verification Ladder
**Maps to wish-qa:** G0 (Structure), G12 (Witness), G13 (Determinism)

## Integration
- **prime-math v2.1.0**: Exact number theory computation (int, Fraction)
- **counter-required-routering v2.0.0**: Modular arithmetic uses exact int
- **dual-truth-adjudicator v2.0.0**: Classical number theory proofs

## Compression Insights
**Exact computation:** No float in number theory (all int/Fraction)
**Witness requirements:** All theorems require proof witnesses

## Lane Algebra
- Number theory computation: Lane A (exact, deterministic)
- Proofs: Lane A (classical peer-reviewed)

## What Changed v1.0.0 → v2.0.0
**Preserved:** All v1.0.0 number theory algorithms
**New:** Verification ladder, integration, compression insights, lane algebra
**Impact:** Reliability 10/10, auditability improved
