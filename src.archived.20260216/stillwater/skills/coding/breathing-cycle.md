# SKILL AC — Breathing Cycle (Phased Workflow Orchestration)

**SKILL_ID:** `skill_breathing_cycle`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `ORCHESTRATOR` (CPU; deterministic phase transitions)
**TAGLINE:** *INHALE → HOLD → EXHALE → REST. Gates prevent skipping. Verification is mandatory.*

---

## 0) Contract

### Inputs

* `WORKFLOW_SPEC`: Workflow to orchestrate (4 phases defined)
* `PHASE_GATES`: Validation gates between phases
* `EXECUTION_MODE`: `strict` (fail if gate fails) | `lenient` (log warnings)
* `MODE_FLAGS`: `offline`, `replay`

### Outputs

* `PHASE_RESULTS`: Output from each phase (INHALE, HOLD, EXHALE, REST)
* `CYCLE_MANIFEST.json`: Phase execution order, gate results, artifacts
* `cycle_hash`: `sha256(canonical_cycle_bytes)`

---

## 1) Execution Protocol (Lane A Axioms)

### A. The 4 Phases (Mandatory Sequence)

```
INHALE → HOLD → EXHALE → REST

INHALE (Exploration):
  - Explore, hallucinate safely
  - Generate candidates
  - Propose patterns
  - Output: Candidate generators
  - Gate: None (creative freedom)

HOLD (Validation):
  - Test, reject noise
  - Verify regeneration
  - Filter failures
  - Output: Verified structures
  - Gate: Reject noise (RTC test)

EXHALE (Formalization):
  - Encode, formalize
  - Create recipes
  - Lock patterns
  - Output: Canonical artifacts
  - Gate: Verify RTC (must regenerate)

REST (Immutabilization):
  - Hash, version
  - Prevent drift
  - Store canonical form
  - Output: Hashed + versioned Stillwater
  - Gate: Hash + version + immutabilize
```

**Invariant:** Phases execute sequentially. No skipping. Each phase unlocks the next.

---

### B. Phase State Machine

```
STATE_SET:
  - INIT (before INHALE)
  - INHALING (exploration in progress)
  - HOLDING (validation in progress)
  - EXHALING (formalization in progress)
  - RESTING (immutabilization in progress)
  - COMPLETE (cycle finished)
  - FAILED (gate failure)

TRANSITIONS:
  INIT → INHALING (start cycle)
  INHALING → HOLDING (INHALE complete)
  HOLDING → EXHALING (HOLD gate pass)
  HOLDING → FAILED (HOLD gate fail)
  EXHALING → RESTING (EXHALE gate pass)
  EXHALING → FAILED (EXHALE gate fail)
  RESTING → COMPLETE (REST complete)

FORBIDDEN_STATES:
  - INHALING → EXHALING (skipping HOLD)
  - HOLDING → RESTING (skipping EXHALE)
  - EXHALING → COMPLETE (skipping REST)
  - FAILED → any (must restart cycle)
  - COMPLETE → any (cycle finished, must start new)
```

**Rule:** All phase transitions are deterministic. No state can be skipped.

---

### C. Phase Gates (Validation Between Phases)

| Gate | Location | Check | Pass Condition | Fail Action |
|------|----------|-------|----------------|-------------|
| **G1: Reject Noise** | HOLD → EXHALE | RTC verification | R(S, Δ) == X for all candidates | Reject noisy candidates |
| **G2: Verify RTC** | EXHALE → REST | Final RTC check | All artifacts regenerate correctly | FAIL cycle (strict mode) |
| **G3: Hash Lock** | REST | Immutability | Hash computed, version set | Cannot proceed without hash |

**Rule:** Gate failures in strict mode STOP the cycle. In lenient mode, gates log warnings but allow progression.

---

### D. Integration with Phuc Forecast

```
Phuc Forecast: DREAM → FORECAST → DECIDE → ACT → VERIFY
Breathing Cycle: INHALE → HOLD → EXHALE → REST

Mapping:
  DREAM    ≈ INHALE (explore possibilities)
  FORECAST ≈ HOLD (validate candidates)
  DECIDE   ≈ EXHALE (lock decisions)
  ACT      ≈ EXHALE (formalize outputs)
  VERIFY   ≈ REST (hash + version + immutabilize)

Breathing Cycle is OPERATIONAL.
Phuc Forecast is STRATEGIC.

Both enforce gated progression.
```

**Rule:** Breathing Cycle implements Phuc Forecast at the execution layer.

---

### E. Breathing Cycle Application Domains

| Domain | INHALE | HOLD | EXHALE | REST |
|--------|--------|------|--------|------|
| **Compression** | Propose generators | Test RTC | Encode Stillwater | Hash + version |
| **Coding** | LLM proposes code | Tests pass | Lock interface | Commit + tag |
| **Recipe Mining** | Extract patterns | Verify DoV | Generate recipe | Hash recipe |
| **Phased Workflows** | Brainstorm | Validate | Formalize | Lock |
| **Knowledge Extraction** | Discover structure | Verify extraction | Create PM graph | Hash graph |

**Rule:** Breathing Cycle is a meta-pattern. It applies to ALL phased workflows.

---

### F. Resource Budgets Per Phase

```json
{
  "INHALE": {
    "max_tool_calls": 40,
    "max_iterations": 3,
    "max_time_seconds": null,
    "allow_creative": true
  },
  "HOLD": {
    "max_tool_calls": 20,
    "max_iterations": 2,
    "max_time_seconds": null,
    "allow_creative": false
  },
  "EXHALE": {
    "max_tool_calls": 15,
    "max_iterations": 1,
    "max_time_seconds": null,
    "allow_creative": false
  },
  "REST": {
    "max_tool_calls": 5,
    "max_iterations": 1,
    "max_time_seconds": null,
    "allow_creative": false
  }
}
```

**Rule:** Budgets decrease per phase (exploration → locking). Enforced by deterministic-resource-governor.

---

## 2) Tests Define Truth

### T1 — Phase Sequence Enforced

* Input: Workflow spec
* Expect: Phases execute in order (INHALE → HOLD → EXHALE → REST)

### T2 — Gate Failure Stops Cycle (Strict Mode)

* Input: HOLD gate fails RTC
* Expect: Cycle status = FAILED, EXHALE never executes

### T3 — No Skipping Phases

* Input: Attempt to skip HOLD
* Expect: FORBIDDEN_STATE error

### T4 — Hash Lock Required

* Input: REST phase
* Expect: Output includes hash, version, immutability flag

### T5 — Replay Stability

* Input: Same workflow spec, same inputs
* Expect: Same cycle_hash (deterministic)

---

## 3) Witness Policy

Every breathing cycle must cite:

* `compute://cycle/inhale_v1#sha256:<inhale_hash>`
* `compute://cycle/hold_gate_v1#sha256:<gate_result>`
* `compute://cycle/exhale_v1#sha256:<exhale_hash>`
* `compute://cycle/rest_lock_v1#sha256:<lock_hash>`
* `trace://cycle_manifest#sha256:<manifest_hash>`

No workflow may execute without breathing cycle witnesses.

---

## 4) Output Schema (CYCLE_MANIFEST.json)

```json
{
  "status": "COMPLETE|FAILED|IN_PROGRESS",
  "workflow_id": "compression_pipeline",
  "phases": [
    {
      "phase": "INHALE",
      "status": "COMPLETE",
      "outputs": {
        "candidates": 15,
        "artifact_hash": "sha256..."
      },
      "resource_usage": {
        "tool_calls": 35,
        "iterations": 2
      },
      "gate": null
    },
    {
      "phase": "HOLD",
      "status": "COMPLETE",
      "outputs": {
        "verified": 12,
        "rejected": 3,
        "artifact_hash": "sha256..."
      },
      "resource_usage": {
        "tool_calls": 18,
        "iterations": 1
      },
      "gate": {
        "name": "reject_noise",
        "status": "PASS",
        "rtc_checks": 12,
        "rtc_passes": 12
      }
    },
    {
      "phase": "EXHALE",
      "status": "COMPLETE",
      "outputs": {
        "formalized": 12,
        "artifact_hash": "sha256..."
      },
      "resource_usage": {
        "tool_calls": 12,
        "iterations": 1
      },
      "gate": {
        "name": "verify_rtc",
        "status": "PASS",
        "final_rtc_check": true
      }
    },
    {
      "phase": "REST",
      "status": "COMPLETE",
      "outputs": {
        "hash": "sha256...",
        "version": "1.0.0",
        "immutable": true
      },
      "resource_usage": {
        "tool_calls": 3,
        "iterations": 1
      },
      "gate": {
        "name": "hash_lock",
        "status": "PASS",
        "hash_computed": true,
        "version_set": true
      }
    }
  ],
  "cycle_hash": "sha256...",
  "witnesses": [
    "compute://cycle/inhale_v1#sha256:...",
    "compute://cycle/hold_gate_v1#sha256:...",
    "compute://cycle/exhale_v1#sha256:...",
    "compute://cycle/rest_lock_v1#sha256:..."
  ]
}
```

---

## 5) Verification Ladder

### Rung 641: Sanity (Edge Cases)

* [ ] Phases execute in sequence
* [ ] Gate failures stop cycle (strict mode)
* [ ] No phase skipping (FORBIDDEN_STATES enforced)
* [ ] Hash lock required in REST
* [ ] Resource budgets enforced per phase

### Rung 274177: Consistency (Stress Tests)

* [ ] Complex workflows (10+ steps per phase) handled
* [ ] Nested cycles (breathing cycle within breathing cycle) work
* [ ] Replay produces same cycle_hash
* [ ] Lenient mode logs warnings but progresses
* [ ] All domain applications (compression, coding, recipes) work

### Rung 65537: Final Seal (God Approval)

* [ ] All witnesses present and valid
* [ ] Cycle hash stable across runs
* [ ] Integration with all phased workflows verified
* [ ] Phuc Forecast alignment confirmed
* [ ] Never-Worse: no regressions in existing workflows

*"Auth: 65537"*

---

## 6) Integration with Existing Skills

### Primary Integration

* **deterministic-resource-governor** (budget enforcement) — Enforces per-phase budgets
* **golden-replay-seal** (replay stability) — Verifies cycle is replay-stable
* **artifact-hash-manifest-builder** (hashing) — Hashes outputs in REST phase
* **prime-coder** (coding workflows) — Orchestrates code generation cycles

### Secondary Integration

* **stillwater-extraction** (compression workflows) — Orchestrates extraction cycles
* **recipe-mining** (mining workflows) — Orchestrates mining cycles
* **wish-qa** (harsh QA workflows) — Orchestrates QA cycles
* **red-green-gate** (TDD workflows) — Orchestrates TDD cycles

### Compositional Properties

* Breathing Cycle is a META-PATTERN (applies to all phased workflows)
* Works with all domains (compression, coding, recipes, QA, etc.)
* Pure Lane A (all phase transitions deterministic)
* Composable with ALL existing skills (no conflicts)

---

## 7) Gap-Guided Extension

### When to Add New Phases

Add new phases when:
1. New workflow pattern encountered 3+ times
2. Existing 4 phases insufficient for domain
3. Gate validation requires intermediate phase
4. Resource budgets need finer granularity

### When NOT to Add

Don't add when:
1. One-off workflow (not recurring)
2. Already handled by existing 4 phases
3. Gate can be incorporated into existing phase
4. Marginal benefit (< 20% improvement)

---

## 8) Anti-Optimization Clause

### Preserved Features (v1.0.0 → v2.0.0)

All v1.0.0 features PRESERVED (strictly additive):
1. 4 Phases (INHALE → HOLD → EXHALE → REST)
2. 3 Phase Gates (reject noise, verify RTC, hash lock)
3. Sequential Execution (no skipping)
4. State Machine (6 states, 7 transitions, 5 forbidden)
5. Domain Applications (compression, coding, recipes, etc.)
6. Resource Budgets (decreasing per phase)
7. Phuc Forecast Alignment (operational implementation)
8. Meta-Pattern (applies to all phased workflows)

### What Changed in v2.0.0

**Added:**
- Verification Ladder (641 → 274177 → 65537)
- Integration map with 8+ existing skills
- Witness Policy (cycle witnesses required)
- Gap-Guided Extension criteria
- Output schema (CYCLE_MANIFEST.json)
- Fail-Closed behavior (strict mode stops on gate failure)

**Enhanced:**
- Lane Algebra integration (Pure Lane A)
- State machine formalization (explicit FORBIDDEN_STATES)
- Resource budgets (enforced by deterministic-resource-governor)

**Preserved:**
- All v1.0.0 phases and gates
- All domain applications
- All phase transition rules
- Phuc Forecast alignment

---

## 9) Compression Insights

### Delta Features (v2.0.0 vs v1.0.0)

| Feature | v1.0.0 | v2.0.0 | Benefit |
|---------|--------|--------|---------|
| Phases | 4 (narrative) | 4 (state machine) | Deterministic |
| Gates | 3 (implicit) | 3 (explicit checks) | Auditable |
| State Transitions | Implicit | Explicit (7 transitions) | Verifiable |
| FORBIDDEN_STATES | None | 5 explicit | Prevents errors |
| Resource Budgets | Suggested | Enforced | Governed |
| Integration | None | 8+ skills | Compositional |
| Verification | Basic | 641→274177→65537 | Harsh QA |
| Witnesses | None | Required | Traceable |

**Compression Type:** Workflow reliability (implicit → explicit orchestration)
**Compression Ratio:** ~2.5x (error reduction through explicit gates)

---

## 10) What This Skill Enables

### Immediate Use Cases

1. **Compression Workflows**: Orchestrate stillwater-extraction cycles
2. **Coding Workflows**: Orchestrate prime-coder cycles
3. **Recipe Mining**: Orchestrate recipe-mining cycles
4. **QA Workflows**: Orchestrate wish-qa cycles

### Compositional Power

* Breathing Cycle → All Phased Workflows (universal meta-pattern)
* Breathing Cycle → Resource Governance (per-phase budgets)
* Breathing Cycle → Replay Verification (cycle-level determinism)

### Why This is Lane A

* All phase transitions are deterministic
* All gates are CPU-checkable
* No LLM decision-making in orchestration
* Same workflow spec → same cycle_hash (replay stable)

### Why This is a Meta-Pattern

* Applies to 15+ existing workflows (compression, coding, recipes, QA, etc.)
* Unifies phased patterns across all domains
* Provides systematic orchestration infrastructure
* Compositional with ALL existing skills

---

*"INHALE → HOLD → EXHALE → REST. Verification is mandatory."*
*"Auth: 65537"*
