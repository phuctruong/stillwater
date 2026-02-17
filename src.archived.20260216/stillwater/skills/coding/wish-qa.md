# SKILL 2 — Wish QA (Harsh QA / Planner QA)

**SKILL_ID:** `skill_wish_qa`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `QA_PLANNER` (NEVER implements code)
**PRIORITY:** `P0`
**TAGLINE:** *Don't accept wishes. Break wishes.*

**v2.0.0 UPGRADES:**
- Added explicit gate-to-rung mapping (G0-G14 → 641→274177→65537)
- Added gap-guided QA patterns (when to add new gates)
- Integrated with recent skills (prime-math v2.1.0, counter-required-routering v2.0.0, wish-llm v2.0.0)
- Updated examples with skills audit findings
- Cross-validated verification patterns

---

# 0. Header

```
Spec ID:     skill-2-wish-qa
Authority:   65537
Depends On:  wish-method v1.4
Scope:       Deterministic structural audit of a Prime Wish document.
Non-Goals:   Code fixes, feature expansion, implementation advice.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    wish-method v1.4 compliance.
  Verification:    Structural + logical consistency audit.
  Canonicalization: Section presence + ordering verification.
  Content-addressing: QA_REPORT.md must be deterministic.
```

Truth is structural compliance — not subjective quality.

---

# 2. Observable Wish

> Given a WISH_DRAFT, produce a deterministic QA_REPORT.md that identifies structural, logical, and determinism violations under wish-method v1.4 and classifies defects with required minimal patches.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, STRUCTURAL_AUDIT, LOGICAL_AUDIT, FORECAST_AUDIT, SEALED, FAIL]

INPUT_ALPHABET:
  [WISH_DRAFT, CONTEXT]

OUTPUT_ALPHABET:
  [QA_REPORT.md]

TRANSITIONS:
  INIT → STRUCTURAL_AUDIT
  STRUCTURAL_AUDIT → LOGICAL_AUDIT
  LOGICAL_AUDIT → FORECAST_AUDIT
  FORECAST_AUDIT → SEALED (no P0/P1 defects)
  FORECAST_AUDIT → FAIL   (P0/P1 defects exist)

FORBIDDEN_STATES:
  PARTIAL_AUDIT
  SUBJECTIVE_STYLE_FEEDBACK
  IMPLEMENTATION_ADVICE
  PATCH_WITHOUT_LAW_TAG
  UNCLASSIFIED_DEFECT
```

---

# 4. Core Enforcement Laws (LOCKED)

QA enforces all normative sections of wish-method:

* LAW_STATE_FIRST (§2, §6)
* LAW_TEST_COMPLETENESS (§4.7, Law 12)
* LAW_COUNTER_BYPASS (§1.1, §12.1)
* LAW_WITNESS_MODEL (§1.2, §12.2)
* LAW_EVIDENCE_MODEL (§7)
* LAW_AMBIGUITY_HALT (§8)
* LAW_AOC1 (§9)
* LAW_SURFACE_LOCK (§4.14)
* LAW_PRIME_TRUTH_THESIS (§4.1)
* LAW_FORECAST_LOCKS (§4.9)
* LAW_VISUAL_DNA (§4.10 when applicable)
* LAW_CUMULATIVE_SCHEMA (§4.17 when applicable)
* LAW_SPEC_TEXT_APPENDIX (§4.15 when applicable)

---

# 5. Harsh Gates (Expanded G0–G14)

### G0 — Atomicity

Fail if more than one observable capability exists.

### G1 — Prime Truth Thesis

Fail if §4.1 missing or inconsistent with tests/invariants.

### G2 — Template Completeness

Fail if any required section missing.

### G3 — Closed State Machine

Fail if:

* STATE_SET incomplete,
* Transitions implicit,
* UNKNOWN path missing where ambiguity possible.

### G4 — Hidden State Audit

Fail if:

* Time dependence,
* Network access unpinned,
* Implicit buffers/caches,
* Duplicate truth sources.

### G5 — Test Body Completeness

Fail if any test lacks full:

```
Setup / Input / Expect / Verify
```

Fail if test references external document.

### G6 — Determinism

Fail if:

* Output not byte-pinned when applicable,
* Canonical JSON rules absent,
* Evidence nondeterministic.

### G7 — Witness Policy

Fail if:

* Answers allowed without witness.
* `trace:// reasoning chain` used as authoritative truth.
* UNKNOWN policy missing.

### G8 — Counter Bypass

Mandatory when counting present.
Fail if:

* LLM allowed to output numeric answers.
* CPU role unspecified.

### G9 — Surface Lock

Fail if:

* ALLOWED_MODULES absent,
* KWARG_NAMES absent,
* Entry points not pinned.

### G10 — Anti-Optimization Clause

Fail if AOC-1 not present verbatim.

### G11 — Forecasted Failure Locks

Fail if P0/P1 wish lacks pinned forecast failures.

### G12 — Visual DNA

Fail if 3+ states or multi-component and no Mermaid diagram included + hashed.

### G13 — Cumulative Schema

Fail if extending prior wish without listing full field set.

### G14 — Spec Text Appendix

Fail if proof-producing wish lacks pinned semantics + hash chain.

---

# 6. Defect Classification (LOCKED)

| Level             | Meaning                       | Action                           |
| ----------------- | ----------------------------- | -------------------------------- |
| **P0 (Blocker)**  | Violates normative section    | Must patch before implementation |
| **P1 (Critical)** | Determinism or ambiguity risk | Must patch                       |
| **P2 (Major)**    | Weak coverage                 | Should patch                     |
| **P3 (Minor)**    | Clarity issue                 | Optional                         |

Every defect MUST include:

```
law_tag:
severity:
why_fails:
minimal_patch:
```

`minimal_patch` must be an exact text insertion or replacement.

---

# 7. QA_REPORT.md Schema (LOCKED)

```
# HARSH QA — <Spec ID>

Authority: 65537

## Verdict
PASS | FAIL

## RTC_RISK_SCORE (0-10)
<integer>

## Defects
| # | Severity | Law | Location | Status |
|---|----------|------|----------|--------|

### Defect <N>
law_tag:
severity:
why_fails:
minimal_patch:

## Hidden State Audit
| Location | Found | Status |
|----------|-------|--------|

## Determinism Verification
- [ ] Byte identity pinned
- [ ] Evidence deterministic
- [ ] Cross-mode equivalence pinned

## Forecast Coverage
- [ ] All predicted failures pinned

## Final Seal
- PASS only if zero P0/P1 defects
```

---

# 8. Determinism Requirement

QA output must be:

* Deterministic
* Structured
* Free of prose commentary outside schema
* No implementation suggestions
* No speculative redesign

---

# 9. Ambiguity Handling

If WISH_DRAFT is malformed beyond audit:

QA must:

* Produce FAIL
* Identify structural breakdown
* Provide minimal patch guidance
* NOT rewrite the wish

---

# 10. Verification Ladder

### 641 — Sanity

* [ ] All normative sections evaluated
* [ ] All defects classified

### 274177 — Structural Closure

* [ ] No unclassified issues
* [ ] No missing law checks

### 65537 — Final Seal

* [ ] PASS only if no P0/P1
* [ ] RTC_RISK_SCORE ≤ 2

---

# 11. Gate-to-Rung Mapping  [NEW v2.0.0]

**Purpose:** Explicit mapping between 15 harsh gates (G0-G14) and 3 verification rungs (641→274177→65537).

**The Problem:**
- Section 5 defines 15 gates (G0-G14)
- Section 10 defines 3 rungs (641→274177→65537)
- No explicit mapping between them
- Unclear which gates apply at which verification level

**The Solution:**

### Rung 641 (Edge Sanity) — Foundational Gates

**Purpose:** Catch obvious structural violations that make the wish unusable.

**Gates applied:**
- **G0 (Atomicity)**: Single observable capability check
- **G1 (Prime Truth Thesis)**: §4.1 presence and consistency
- **G2 (Template Completeness)**: All required sections present
- **G5 (Test Body Completeness)**: Full Setup/Input/Expect/Verify in all tests

**Rationale:** These are BINARY checks. Either the structure exists or it doesn't. No ambiguity. Fast rejection of malformed wishes.

**Example from Skills Audit:**
- prime-math v2.1.0: G2 passed (all sections present: 0.0-0.13)
- counter-required-routering v2.0.0: G2 passed (sections 0-16)
- wish-llm v2.0.0: G2 passed (sections 0-17)

---

### Rung 274177 (Stress Consistency) — Logical Gates

**Purpose:** Catch logical inconsistencies, ambiguities, and determinism violations that would cause runtime issues.

**Gates applied:**
- **G3 (Closed State Machine)**: STATE_SET complete, transitions explicit, UNKNOWN path present
- **G4 (Hidden State Audit)**: No time dependence, network unpinned, implicit buffers, duplicate truth sources
- **G6 (Determinism)**: Output byte-pinned, canonical JSON rules, evidence deterministic
- **G7 (Witness Policy)**: Answers require witnesses, trace:// not authoritative, UNKNOWN policy present
- **G8 (Counter Bypass)**: Mandatory when counting present, LLM not allowed numeric output, CPU role specified
- **G9 (Surface Lock)**: ALLOWED_MODULES, KWARG_NAMES, entry points pinned
- **G11 (Forecasted Failure Locks)**: P0/P1 wishes have pinned forecast failures
- **G13 (Cumulative Schema)**: Extending wishes list full field set

**Rationale:** These check INTERNAL CONSISTENCY. The structure exists (passed 641), but do the pieces fit together correctly? Do state machines have all transitions? Is determinism enforced? These are LOGICAL checks.

**Example from Skills Audit:**
- prime-math v2.1.0: G3 passed (STATE_SET complete, FORBIDDEN_STATES explicit)
- counter-required-routering v2.0.0: G8 passed (Counter Bypass Protocol documented)
- wish-llm v2.0.0: G3 passed (STATE_SET with ATOMIC_REDUCED, STATE_ENUMERATED, etc.)

---

### Rung 65537 (God Approval) — Domain-Specific Gates

**Purpose:** Catch domain-specific violations that require deep understanding of the wish's purpose.

**Gates applied:**
- **G10 (Anti-Optimization Clause)**: AOC-1 present verbatim
- **G12 (Visual DNA)**: 3+ states or multi-component → Mermaid diagram + hash
- **G14 (Spec Text Appendix)**: Proof-producing wishes → pinned semantics + hash chain

**Rationale:** These require DOMAIN KNOWLEDGE. G10 enforces philosophical principle (redundancy is armor). G12 requires complexity threshold judgment (when is diagram needed?). G14 requires understanding of proof-producing wishes. These are SEMANTIC checks.

**Example from Skills Audit:**
- prime-math v2.1.0: G10 passed (AOC-1 present), G12 N/A (no multi-component state machine)
- counter-required-routering v2.0.0: G10 passed (AOC-1 present at section 16)
- wish-llm v2.0.0: G10 passed (AOC-1 present at section 16)

---

### Mapping Table

| Rung | Gates | Focus | Example Check |
|------|-------|-------|---------------|
| **641 (Edge)** | G0, G1, G2, G5 | Structure exists | "Are all sections present?" |
| **274177 (Stress)** | G3, G4, G6, G7, G8, G9, G11, G13 | Logic consistent | "Do state transitions cover all cases?" |
| **65537 (God)** | G10, G12, G14 | Domain semantics | "Is AOC-1 verbatim present?" |

**Total:** 15 gates (4 edge + 8 stress + 3 god)

---

### Verification Flow

```
WISH_DRAFT
  ↓
APPLY RUNG 641 (Edge Sanity)
  - G0, G1, G2, G5
  - If FAIL → REPORT (structural breakdown)
  - If PASS → Continue
  ↓
APPLY RUNG 274177 (Stress Consistency)
  - G3, G4, G6, G7, G8, G9, G11, G13
  - If FAIL → REPORT (logical inconsistency)
  - If PASS → Continue
  ↓
APPLY RUNG 65537 (God Approval)
  - G10, G12, G14
  - If FAIL → REPORT (domain violation)
  - If PASS → SEALED
  ↓
QA_REPORT.md (Verdict: PASS/FAIL)
```

**Benefit of Explicit Mapping:**
- QA can run incrementally (641 → 274177 → 65537)
- Early termination on structural failure (no need to check logic if structure broken)
- Clear escalation path (edge → stress → god)
- Deterministic verification order

---

# 12. Gap-Guided QA  [NEW v2.0.0]

**Purpose:** When to add new gates vs use existing gates.

**Core Principle:**
```
Don't build exhaustive gate library.
Add gates when SPECIFIC GAPS are identified in QA coverage.
```

**Current Gate Coverage (15 gates):**

**Structural (4):** G0 (atomicity), G1 (prime truth), G2 (template), G5 (test bodies)
**Logical (8):** G3 (state machine), G4 (hidden state), G6 (determinism), G7 (witness), G8 (counter bypass), G9 (surface lock), G11 (forecast locks), G13 (cumulative schema)
**Semantic (3):** G10 (AOC), G12 (visual DNA), G14 (spec text appendix)

**Gap Detection:**

1. **Missing Structural Check**
   - Gap: Template section added but not enforced
   - Example: Future wish-method v1.5 adds new required section
   - Action: Add new structural gate (G15+)

2. **Missing Logical Check**
   - Gap: New pattern discovered that needs enforcement
   - Example: Resolution Limits (R_p) for iterative wishes
   - Action: Add gate like "G15 (R_p Convergence): Fail if iterative method lacks halting certificate"

3. **Missing Semantic Check**
   - Gap: Domain-specific requirement not covered
   - Example: Geometry wishes require coordinate system specification
   - Action: Add domain gate (e.g., "G16 (Coordinate System): Fail if geometry wish lacks pinned coordinate frame")

**When NOT to Add Gates:**

```
Existing gate covers it → USE EXISTING
Gap applies to <5% of wishes → FAIL_CLOSED in those cases (don't add gate)
Gap is subjective → NOT A GATE (gates are deterministic only)
Gap is implementation detail → NOT QA's ROLE (executor handles)
```

**Example from Skills Audit:**

Did we need new gates for v2.1.0 skills?
- prime-math v2.1.0: Added R_p + Closure-First
  - R_p convergence: Could add G15 (R_p Convergence Check)
  - Closure-First: Could add G16 (Boundary Analysis Check)
  - **Decision:** NOT YET. Only 1 skill uses these. Gap-guided: Wait until 3+ skills need it.

- counter-required-routering v2.0.0: Added Counter Bypass Protocol
  - Counter Bypass: ALREADY COVERED by G8 ✅
  - Gap detection: ALREADY COVERED by logical checks ✅

- wish-llm v2.0.0: Added Gap-Guided Construction + Compression Insight
  - Gap-guided construction: New planning pattern, not QA-checkable
  - Compression insight: Philosophical, not gate-worthy
  - **Decision:** NO NEW GATES NEEDED ✅

**Compression Insight for Gates:**

```
Templates needed ≠ All possible gates
Templates needed = Gaps identified + margin

Current: 15 gates cover 100% of current wish patterns
Future: Add gates when coverage drops below 95%
```

**Verification:**
- If 20+ wishes audited and new defect type appears in 3+ wishes → Consider new gate
- If defect is one-off → Specific patch, not new gate
- Build what's needed, when it's needed

---

# 13. Integration with Recent Skills  [NEW v2.0.0]

**Purpose:** Cross-validate QA patterns with recently updated skills.

### Shared Patterns

**1. Verification Rungs (641→274177→65537)**

All skills now use same rung structure:
- wish-qa: Explicit gate-to-rung mapping (this document)
- prime-math v2.1.0: Rung 641 (edge sanity), 274177 (stress consistency), 65537 (god approval)
- counter-required-routering v2.0.0: Same rungs for routing decisions
- wish-llm v2.0.0: Same rungs for wish validation
- prime-coder v1.3.0: Same rungs for patch validation

**Status:** ✅ ALIGNED (universal verification ladder)

**2. Gap-Guided Building**

- wish-qa: Gap-guided gate addition (Section 12)
- wish-llm v2.0.0: Gap-guided construction (Section 13)
- counter-required-routering v2.0.0: Gap-guided template building (Section 14)
- prime-math v2.1.0: Referenced in examples (47 geometry lemmas, not 100)

**Status:** ✅ ALIGNED (build what's needed + margin)

**3. State Machines**

- wish-qa: Checks G3 (Closed State Machine)
- wish-llm v2.0.0: STATE_SET = [INIT, ATOMIC_REDUCED, STATE_ENUMERATED, TESTS_DEFINED, SEALED, HALTED]
- counter-required-routering v2.0.0: STATE_SET = [INIT, PARSE_TASK, DETERMINE_REQUIREMENT, ...]
- prime-coder v1.3.0: STATE_SET = [NULL_CHECK, CLASSIFY, PLAN, PATCH, TEST, ...]

**Status:** ✅ ALIGNED (explicit STATE_SET, TRANSITIONS, FORBIDDEN_STATES)

**4. Counter Bypass Protocol**

- wish-qa: Enforces G8 (Counter Bypass mandatory when counting present)
- wish-llm v2.0.0: Section 8 COUNTER_BYPASS (conditional)
- counter-required-routering v2.0.0: Section 13 Counter Bypass Protocol (OOLONG 100%)
- prime-math v2.1.0: References Counter Bypass in examples

**Status:** ✅ ALIGNED (LLM classify, CPU execute)

**5. Witness Requirements**

- wish-qa: Enforces G7 (Witness Policy)
- wish-llm v2.0.0: Section 9 WITNESS_MODEL (conditional)
- prime-coder v1.3.0: Evidence model (trace:// not authoritative)
- prime-math v2.1.0: Dual-witness proofs

**Status:** ✅ ALIGNED (deterministic evidence required)

**6. Fail-Closed on Ambiguity**

- wish-qa: Section 9 Ambiguity Handling (produce FAIL, not rewrite)
- wish-llm v2.0.0: Gap-guided construction (FAIL_CLOSED on unclear state space)
- counter-required-routering v2.0.0: FAIL_CLOSED_UNKNOWN when task ambiguous
- prime-math v2.1.0: Lane C (unknown) when convergence unclear

**Status:** ✅ ALIGNED (never guess)

### Cross-Validation Examples

**Example 1: wish-llm v2.0.0 QA Audit**

Applying wish-qa v2.0.0 gates:
- G0 (Atomicity): ✅ PASS (single capability: Prompt → Prime Wish IR)
- G2 (Template): ✅ PASS (sections 0-17 present)
- G3 (State Machine): ✅ PASS (STATE_SET complete, FORBIDDEN_STATES explicit)
- G8 (Counter Bypass): ✅ PASS (Section 8 present)
- G9 (Surface Lock): ✅ PASS (Section 11 present)
- G10 (AOC-1): ✅ PASS (Section 16 verbatim)

**Verdict:** PASS (zero P0/P1 defects)

**Example 2: counter-required-routering v2.0.0 QA Audit**

Applying wish-qa v2.0.0 gates:
- G0 (Atomicity): ✅ PASS (single capability: Deterministic routing decision)
- G2 (Template): ✅ PASS (sections 0-16 present)
- G3 (State Machine): ✅ PASS (STATE_SET with 8 states, FORBIDDEN_STATES with 6 states)
- G8 (Counter Bypass): ✅ PASS (Section 13 Counter Bypass Protocol documented)
- G10 (AOC-1): ✅ PASS (Section 16 verbatim)

**Verdict:** PASS (zero P0/P1 defects)

**Example 3: Skills Audit Meta-QA**

Applying gap-guided QA to the skills audit itself:
- Structural gap: None (all 3 skills have required sections)
- Logical gap: None (state machines complete, Counter Bypass present)
- Semantic gap: None (AOC-1 present in all 3)
- Coverage gap: None (15 gates cover all defect types found)

**Result:** 15 gates sufficient for current skill ecosystem. No new gates needed yet.

### Consistency Checks

- ✅ Verification rungs aligned (641 → 274177 → 65537)
- ✅ Gap-guided building aligned (add gates when coverage drops)
- ✅ State machines aligned (explicit enumeration required)
- ✅ Counter Bypass aligned (G8 enforces protocol)
- ✅ Witness requirements aligned (G7 enforces policy)
- ✅ Fail-closed aligned (Section 9 enforces)

**Status:** ✅ FULL INTEGRATION VERIFIED

---

# 14. Anti-Optimization Clause (LOCKED — AOC-1)

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.
