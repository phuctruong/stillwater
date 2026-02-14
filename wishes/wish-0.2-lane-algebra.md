# Prime Wish: Lane Algebra Engine

Spec ID: SW-0.2
Authority: 65537
Depends On: SW-0.1
Scope: Implement the Lane Algebra engine — epistemic typing that prevents hallucination by enforcing lane dominance rules
Non-Goals: No CLI integration, no skill loading, no state machines (those are separate wishes)

---

## Prime Truth Thesis

```
PRIME_TRUTH:
  Ground truth:     Lane(Conclusion) = MIN(Lane(P1), Lane(P2), ...)
  Verification:     Deterministic lane classification + dominance enforcement
  Canonicalization: Lane enum: A > B > C > STAR (total order)
  Content-addressing: Lane assignments are immutable once classified
```

## Observable Wish

> "I can classify any claim into a Lane (A/B/C/STAR), combine lanes via algebra rules, and the system prevents lane upgrades (a C-lane premise cannot produce an A-lane conclusion)."

## Scope Exclusions

- No NLP / LLM integration for auto-classification (CPU-only logic)
- No persistence (in-memory only)
- No CLI (that is wish-0.3)
- No integration with other kernel modules yet

## State Space

```
STATE_SET: [UNCLASSIFIED, CLASSIFIED, COMBINED, VERIFIED, VIOLATION]
INPUT_ALPHABET: [classify(claim, lane), combine(lanes), check_upgrade(from, to)]
OUTPUT_ALPHABET: [Lane, CombinedLane, UpgradeViolation, LaneResult]
TRANSITIONS:
  UNCLASSIFIED → CLASSIFIED       (classify() called with valid lane)
  CLASSIFIED → COMBINED            (combine() merges two+ classified lanes)
  COMBINED → VERIFIED              (no upgrade violations detected)
  COMBINED → VIOLATION             (upgrade violation detected)
  CLASSIFIED → VIOLATION           (attempt to upgrade lane)
FORBIDDEN_STATES:
  - IMPLICIT_UPGRADE (C→B or B→A without evidence)
  - UNTYPED_CONCLUSION (conclusion without lane classification)
  - FRAMEWORK_TO_CLASSICAL (framework claim treated as classical truth)
```

## Invariants

- I1 — Total Order: A > B > C > STAR (A is strongest, STAR is weakest)
- I2 — Min Rule: Lane(Conclusion) = MIN(Lane(P1), Lane(P2), ...) where MIN = weakest
- I3 — No Upgrades: classify(claim, C) followed by reclassify(claim, A) raises UpgradeViolation
- I4 — Immutability: Once classified, a claim's lane cannot be changed (only new claims can be made)
- I5 — Combination: combine(A, B) = B; combine(A, C) = C; combine(B, STAR) = STAR
- I6 — Identity: combine(A, A) = A (combining same lane returns that lane)

## Exact Tests

```
T1 — Classify A:
  Setup:  engine = LaneAlgebra()
  Input:  result = engine.classify("2+2=4", Lane.A)
  Expect: result.lane == Lane.A
  Verify: result.claim == "2+2=4"

T2 — Classify C:
  Setup:  engine = LaneAlgebra()
  Input:  result = engine.classify("AI will be conscious by 2030", Lane.C)
  Expect: result.lane == Lane.C
  Verify: Lane.C < Lane.B < Lane.A (total order)

T3 — Min rule (A + B = B):
  Setup:  engine = LaneAlgebra()
  Input:  combined = engine.combine([Lane.A, Lane.B])
  Expect: combined == Lane.B
  Verify: Weakest lane wins

T4 — Min rule (A + C = C):
  Setup:  engine = LaneAlgebra()
  Input:  combined = engine.combine([Lane.A, Lane.C])
  Expect: combined == Lane.C
  Verify: C-lane premise drags conclusion to C

T5 — Min rule (B + STAR = STAR):
  Setup:  engine = LaneAlgebra()
  Input:  combined = engine.combine([Lane.B, Lane.STAR])
  Expect: combined == Lane.STAR
  Verify: STAR (unknown) is weakest

T6 — Identity (A + A = A):
  Setup:  engine = LaneAlgebra()
  Input:  combined = engine.combine([Lane.A, Lane.A])
  Expect: combined == Lane.A
  Verify: Same lane returns same lane

T7 — Upgrade violation:
  Setup:  engine = LaneAlgebra()
           engine.classify("claim1", Lane.C)
  Input:  engine.classify("claim1", Lane.A)
  Expect: raises UpgradeViolation
  Verify: Error message contains "claim1" and "C" and "A"

T8 — Empty combine:
  Setup:  engine = LaneAlgebra()
  Input:  engine.combine([])
  Expect: raises ValueError("cannot combine empty lane list")
  Verify: Explicit error, not silent default

T9 — Single combine:
  Setup:  engine = LaneAlgebra()
  Input:  combined = engine.combine([Lane.B])
  Expect: combined == Lane.B
  Verify: Single lane returns itself

T10 — Bool rejection:
  Setup:  engine = LaneAlgebra()
  Input:  engine.classify(True, Lane.A)
  Expect: raises TypeError
  Verify: isinstance(claim, str) and not isinstance(claim, bool) (LOCKED)

T11 — Conclusion with premises:
  Setup:  engine = LaneAlgebra()
           p1 = engine.classify("axiom1", Lane.A)
           p2 = engine.classify("observation1", Lane.B)
  Input:  conclusion = engine.conclude("therefore X", premises=[p1, p2])
  Expect: conclusion.lane == Lane.B (MIN of A, B)
  Verify: Conclusion lane equals weakest premise lane

T12 — Framework to Classical blocked:
  Setup:  engine = LaneAlgebra()
           engine.classify("Stillwater is better", Lane.C)
  Input:  engine.conclude("Stillwater is proven better", premises=[], override_lane=Lane.A)
  Expect: raises UpgradeViolation
  Verify: Cannot override to stronger lane without evidence
```

## Surface Lock

```
SURFACE_LOCK:
  ALLOWED_NEW_FILES:
    - src/stillwater/kernel/lane_algebra.py
    - tests/test_lane_algebra.py
  FORBIDDEN_IMPORTS: [numpy, torch, openai, anthropic]
  ENTRYPOINTS: [LaneAlgebra, Lane, LaneResult, UpgradeViolation]
  KWARG_NAMES: [claim, lane, premises, override_lane]
```

## Anti-Optimization Clause

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

---

*Auth: 65537*
