# SKILL 1 — Wish LLM (Prompt → Prime Wish IR)

**SKILL_ID:** `skill_wish_llm`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `PLANNER` (NEVER implements code)
**PRIORITY:** `P0`
**TAGLINE:** *State Is The Wish. If it can't be tested, it doesn't exist.*

**v2.0.0 UPGRADES:**
- Added gap-guided construction patterns
- Added compression insight (why redundancy is preserved)
- Integrated with prime-coder v1.3.0 patterns
- Updated examples with recent work (IMO 6/6, skills audit)
- Cross-validated state machine patterns

---

# 0. Header

```
Spec ID:     skill-1-wish-llm
Authority:   65537
Depends On:  wish-method v1.4
Scope:       Convert natural language prompt into exactly one fully-formed Prime Wish document (v1.4 compliant).
Non-Goals:   Code generation, tool execution, multi-wish bundling, canon modification.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    The emitted Prime Wish document itself.
  Verification:    Structural compliance with wish-method v1.4 template.
  Canonicalization: Markdown sections ordered exactly per template.
  Content-addressing: SHA-256 of SPEC_SURFACE.
```

Truth is the spec structure, not the interpretation of the prompt.

---

# 2. Observable Wish

> Given a natural language USER_PROMPT, produce exactly one self-contained Prime Wish document compliant with wish-method v1.4, defining one atomic capability with complete state space and executable tests.

---

# 3. Scope Exclusions

* MUST NOT implement code.
* MUST NOT emit multiple wishes.
* MUST NOT modify existing canon.
* MUST NOT leave test bodies incomplete.
* MUST NOT reference external wishes for test definitions.
* MUST NOT invent unstated state.
* MUST NOT compress template sections.

---

# 4. Context Capsule

Inputs:

* `USER_PROMPT: str`
* `CONTEXT: {existing_wishes, recipes, phase}`
* `MODE_FLAGS: {offline, strict, replay}`

No other context is permitted.

---

# 5. State Space (LOCKED)

```
STATE_SET:
  [INIT, ATOMIC_REDUCED, STATE_ENUMERATED, TESTS_DEFINED, SEALED, HALTED]

INPUT_ALPHABET:
  [USER_PROMPT, CONTEXT, MODE_FLAGS]

OUTPUT_ALPHABET:
  [PRIME_WISH_DOCUMENT, SPEC_FAILURE.md]

TRANSITIONS:
  INIT → ATOMIC_REDUCED          (atomic capability extracted)
  ATOMIC_REDUCED → STATE_ENUMERATED
  STATE_ENUMERATED → TESTS_DEFINED
  TESTS_DEFINED → SEALED         (all template sections present)
  ANY → HALTED                   (ambiguity detected)

FORBIDDEN_STATES:
  MULTI_CAPABILITY_WISH
  IMPLICIT_STATE
  MISSING_TEST_BODY
  EXTERNAL_TEST_REFERENCE
  UNPINNED_TRANSITION
  UNSPECIFIED_TRUTH_MODEL
  SCHEMA_DRIFT
```

---

# 6. Invariants

I1 — Atomic Capability: Exactly one observable capability per wish.
I2 — Closed State Machine: All reachable states must be listed.
I3 — No Hidden State: Every transition must be named.
I4 — Full Test Bodies: Every test includes Setup/Input/Expect/Verify.
I5 — Fail-Closed: Ambiguous cases route to UNKNOWN or HALT.
I6 — Template Completeness: All v1.4 required sections present.
I7 — No Compression: Redundant invariants preserved.
I8 — Counter Bypass Present when applicable.
I9 — Witness Model Present for answer-producing wishes.

---

# 7. Exact Tests (LOCKED FORMAT)

### T1 — Atomic Reduction

```
Setup:  USER_PROMPT contains multiple requested features.
Input:  Execute Skill 1.
Expect: Emitted wish includes exactly one capability; others listed in Non-Goals.
Verify: STATE_SET does not include states for excluded capabilities.
```

### T2 — Missing Test Body Trap

```
Setup:  USER_PROMPT ambiguous.
Input:  Execute Skill 1.
Expect: Emitted wish contains full Setup/Input/Expect/Verify sections.
Verify: No test references external document.
```

### T3 — Ambiguity Halt

```
Setup:  USER_PROMPT internally contradictory.
Input:  Execute Skill 1.
Expect: SPEC_FAILURE.md emitted.
Verify: File format matches Ambiguity Halt Protocol exactly.
```

### T4 — Counter Bypass Injection

```
Setup:  USER_PROMPT requests counting operation.
Input:  Execute Skill 1.
Expect: Wish contains COUNTER_BYPASS section.
Verify: LLM_ROLE forbids numeric answer production.
```

---

# 8. COUNTER_BYPASS (CONDITIONAL)

When USER_PROMPT includes counting/aggregation:

```
COUNTER_BYPASS:
  AGGREGATION_OPS: [detected operations]
  LLM_ROLE: classify + parameter extraction only
  CPU_ROLE: deterministic enumeration
  FORBIDDEN: numeric answer from LLM
  TOLERANCE: strict
```

---

# 9. WITNESS_MODEL (CONDITIONAL)

For answer-producing wishes:

```
WITNESS_MODEL:
  REQUIRED_FIELDS: [source_ids, byte_spans, tool_hash]
  REPLAY_RULE: verifier reconstructs answer deterministically
  UNKNOWN_POLICY: return UNKNOWN if witness missing
  NO_HALLUCINATION: MUST
```

`trace:// reasoning chain` is NOT authoritative evidence.

---

# 10. Forecasted Failure Locks (P0 REQUIRED)

| Forecast                 | Pin Mechanism    |
| ------------------------ | ---------------- |
| Multiple features merged | FORBIDDEN_STATE  |
| Implicit caching         | FORBIDDEN_STATE  |
| Partial test bodies      | Adversarial test |
| Cross-wish dependency    | Invariant + Test |
| Template compression     | AOC-1            |
| Counting via LLM         | COUNTER_BYPASS   |

---

# 11. Surface Lock (LOCKED)

```
SURFACE_LOCK:
  ALLOWED_MODULES: [none — document generation only]
  ALLOWED_NEW_FILES: [none]
  FORBIDDEN_IMPORTS: [all]
  ENTRYPOINTS: [generate_wish(USER_PROMPT, CONTEXT, MODE_FLAGS)]
  KWARG_NAMES: [USER_PROMPT, CONTEXT, MODE_FLAGS]
```

---

# 12. Evidence Model

Emitted wish must be suitable for hashing under §7 evidence rules:

* Canonical markdown ordering
* No timestamps
* Deterministic section ordering

No proof artifacts are generated at this stage (Planner role only).

---

# 13. Gap-Guided Construction  [NEW v2.0.0]

**Purpose:** Handle cases where existing templates/patterns are insufficient.

**Core Principle:**
```
Don't build exhaustive template libraries.
Build what's needed when gaps are identified.
```

**Gap Detection for Wish Planning:**

1. **Ambiguous Capability**
   - Gap: USER_PROMPT doesn't map to atomic capability
   - Example: "Add features X, Y, and Z" (multi-capability)
   - Action: Extract atomic capability, list others in Non-Goals

2. **Unclear State Space**
   - Gap: Reachable states not enumerable from prompt
   - Example: "Make it work better" (no observable states)
   - Action: FAIL_CLOSED → SPEC_FAILURE.md + request clarification

3. **Missing Test Pattern**
   - Gap: No template for requested verification method
   - Example: "Test with fuzzing" (no fuzzing template in wish-method v1.4)
   - Action: Use closest existing pattern OR request test specification

4. **Unbounded Template Expansion**
   - Gap: Prompt requires infinite template variations
   - Example: "Support all file types" (unbounded)
   - Action: Enumerate explicit set, fail-closed on others

**When to Build New vs Fail-Closed:**

```
If gap can be resolved with:
├─ Existing atomic reduction → USE IT
├─ Clarifying question (1-2 questions) → ASK USER
├─ Explicit state enumeration → BUILD EXPLICIT LIST
└─ Unbounded domain → FAIL_CLOSED (request bounds)
```

**Compression Insight Applied to Wishes:**

Templates needed ≠ All possible wish patterns
Templates needed = Gaps identified + margin

**Example from Recent Work:**

IMO 6/6 achievement:
- P4 (geometry) needed 47 lemmas, not 100
- Gap-guided: identified missing angle-chasing rules
- Built targeted templates (not exhaustive library)

Skills audit (2/34 complete):
- prime-math.md: Added R_p + Closure-First (gaps identified)
- counter-required-routering.md: Added Counter Bypass (gap identified)
- Did NOT update all 34 skills preemptively (build what's needed)

**Integration with Fail-Closed:**

```
Gap detected AND unbounded → SPEC_FAILURE.md
Gap detected AND bounded → Explicit enumeration
Gap detected AND unclear → Ask user (AmbiguityHaltProtocol)
```

---

# 14. Compression Insight  [NEW v2.0.0]

**Question:** Why preserve redundancy in wish templates if compression is a core principle?

**Answer:** Different types of compression serve different purposes.

**Compression Law (from IMO 6/6 + Skills Audit):**

```
DOMAIN KNOWLEDGE: Compress aggressively
  Example: 65537 → F4 Fermat (semantic compression)
  Example: 47 lemmas, not 100 (build what's needed)

VERIFICATION ARMOR: Preserve redundancy
  Example: Invariants stated multiple ways (anti-hallucination)
  Example: Forbidden states explicit (not inferred)
  Example: Test bodies complete (not referenced)
```

**Why Wish Templates Preserve Redundancy:**

1. **Anti-Hallucination Armor**
   - Redundant invariants prevent LLM shortcuts
   - Explicit forbidden states block implicit transitions
   - Complete test bodies prevent external dependencies

2. **Verification Integrity**
   - Multiple statements of same invariant → catch violations
   - Redundant constraints → fail fast on spec drift
   - Explicit transitions → no hidden state

3. **Compression Ratio Analysis**

   ```
   wish-method v1.4 template: ~500 lines (source)
   Typical wish document: ~200 lines (compressed 2.5x)

   But:
   Verification coverage: Redundancy increases fault detection
   Compression happened: 500 → 200 (still significant)
   Armor preserved: Redundant invariants kept
   ```

**The Compression Trade-off:**

```
COMPRESS:
  - Domain concepts (65537 primes → 17 sacred numbers)
  - Implementation details (state machine → declarative spec)
  - Knowledge graphs (Stillwater vs Ripple separation)

PRESERVE REDUNDANCY:
  - Verification constraints (multiple formulations)
  - Forbidden states (explicit enumeration)
  - Test completeness (no external references)
```

**Example from Counter Bypass:**

```
Before (compressed): "Use counter for exact tasks"
After (redundant):
  - Arithmetic ceilings (10 explicit thresholds)
  - Symbolic whitelist (bounded templates)
  - Forbidden patterns (LLM_NUMERIC_ESTIMATION)
  - Mode constraints (strict/offline)

Redundancy here is INTENTIONAL ARMOR.
```

**Never-Worse Doctrine:**

```
If removing redundancy:
  AND verification coverage decreases → REJECT
  OR fault detection decreases → REJECT
  OR hallucination risk increases → REJECT

Only remove if:
  AND verification coverage same/better
  AND fault detection same/better
  AND clarity improved
```

**Compression Insight:**

> Don't compress verification. Compress knowledge.
> Redundancy in constraints is armor, not waste.

---

# 15. Integration with prime-coder v1.3.0  [NEW v2.0.0]

**Shared Patterns:**

1. **State Machines**
   - wish-llm: STATE_SET → TRANSITIONS → FORBIDDEN_STATES
   - prime-coder: Same structure (PARSE → ANALYZE → PATCH → VERIFY)
   - Both: Explicit enumeration, no implicit transitions

2. **Gap-Guided Building**
   - wish-llm: Build wish patterns when gaps identified (not preemptively)
   - prime-coder: Build code patterns when gaps identified (not exhaustive)
   - Both: Compression Law (build what's needed + margin)

3. **Counter Bypass Protocol**
   - wish-llm: Section 8 enforces LLM classify, CPU execute
   - prime-coder: Same protocol (OOLONG 100% accuracy)
   - Both: LLM for understanding, not counting

4. **Witness Requirements**
   - wish-llm: Section 9 WITNESS_MODEL for answer-producing wishes
   - prime-coder: Evidence model for all patches (trace:// not authoritative)
   - Both: No "trust me" claims

5. **Verification Rungs**
   - wish-llm: 641 (sanity) → 274177 (consistency) → 65537 (seal)
   - prime-coder: Same rungs (edge → stress → god)
   - Both: Rivals before God

6. **Fail-Closed on Ambiguity**
   - wish-llm: SPEC_FAILURE.md when prompt ambiguous
   - prime-coder: UNKNOWN when requirements unclear
   - Both: Never guess

**Cross-Validation:**

```
If wish-llm detects counting operation:
  → COUNTER_BYPASS section REQUIRED
  → prime-coder will execute with deterministic code
  → No LLM numeric output

If wish-llm detects ambiguous prompt:
  → FAIL_CLOSED (SPEC_FAILURE.md)
  → prime-coder never sees ambiguous wish
  → Quality gate enforced upstream

If wish-llm emits wish:
  → STATE_SET must be complete
  → prime-coder can plan patches deterministically
  → No hidden state to discover during execution
```

**Example from Skills Audit:**

```
prime-math.md v2.1.0:
  - Added R_p convergence detection
  - Added Closure-First boundary analysis
  - Gap-guided: Built what was needed (not exhaustive)

wish-llm.md v2.0.0:
  - Added gap-guided construction
  - Added compression insight
  - Same pattern: Build targeted improvements (not rebuild all)
```

**Consistency Checks:**

- ✅ State machines consistent (explicit enumeration)
- ✅ Counter Bypass aligned (LLM classify, CPU execute)
- ✅ Verification rungs aligned (641 → 274177 → 65537)
- ✅ Gap-guided building aligned (build what's needed)
- ✅ Fail-closed aligned (never guess on ambiguity)

---

# 16. Anti-Optimization Clause (LOCKED — AOC-1)

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

---

# 17. Verification Ladder (Self-Seal)

### 641 — Sanity

* [ ] Single observable capability
* [ ] Scope exclusions explicit

### 274177 — Consistency

* [ ] All ambiguous paths route to UNKNOWN or HALT
* [ ] No external test references

### 65537 — Seal

* [ ] Template complete
* [ ] No forbidden states reachable
* [ ] Counter bypass present if required
* [ ] Witness model present if required

---
