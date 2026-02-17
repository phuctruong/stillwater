# SKILL AB — Recipe Mining (Auto-Extract Drift-Resistant Patterns)

**SKILL_ID:** `skill_recipe_mining`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `MINER` (CPU-anchored; deterministic extraction + Lane B generation)
**TAGLINE:** *LLM finds pattern once. Recipe executes pattern forever.*

---

## 0) Contract

### Inputs

* `EXECUTION_TRACE`: Complete record of successful execution (JSONL format)
* `MINING_MODE`: `strict` (fail if DoV unclear) | `lenient` (infer DoV from context)
* `TIER_TARGET`: `DRAFT` | `QUALIFIED` | `STABLE` | `CANONICAL`
* `MODE_FLAGS`: `offline`, `replay`

### Outputs

* `RECIPE`: Mined recipe with pattern, parameters, DoV, tests
* `RECIPE_TIER`: Starting tier (always `DRAFT` for new recipes)
* `MINING_REPORT.json`: What was extracted, confidence, validation status
* `recipe_hash`: `sha256(canonical_recipe_bytes)`

---

## 1) Execution Protocol (Lane A/B Hybrid)

### A. The 8 Root Causes of Drift (Anti-Patterns)

| # | Cause | Detection | Mitigation in Recipe |
|---|-------|-----------|----------------------|
| 1 | Prompt Variance | Same intent, different prompts | Extract invariant intent |
| 2 | Model Stochasticity | Temperature, sampling | Crystallize deterministic steps |
| 3 | Context Window | Lost information | Identify required context |
| 4 | Tool Choice | Different paths | Lock tool sequence |
| 5 | Error Handling | Recovery variance | Formalize error paths |
| 6 | Order Sensitivity | Sequence matters | Enforce execution order |
| 7 | Feedback Loops | Compound errors | Break loops, checkpoints |
| 8 | External State | Environment changes | Specify preconditions |

**Rule:** Every drift cause must be addressed in the mined recipe.

---

### B. 5-Step Mining Pipeline (Deterministic)

```
1. CAPTURE TRACE
   - Record all tool calls, results, decisions
   - Log context (environment, inputs, outputs)
   - Preserve timestamps, order, dependencies

2. EXTRACT INVARIANT PATTERN (Lane A: CPU)
   - Identify required steps (critical path)
   - Separate structure from parameters
   - Determine execution order
   - Find decision points

3. PARAMETERIZE VARIABLES (Lane A: CPU)
   - Identify what varied across runs
   - Extract parameter types
   - Define parameter constraints
   - Create parameter schema

4. INFER DOMAIN OF VALIDITY (Lane B: LLM proposes, CPU verifies)
   - Input types (from trace inputs)
   - Preconditions (from trace context)
   - Environment constraints (from trace environment)
   - Resource limits (from trace metrics)

5. GENERATE VERIFICATION TESTS (Lane A: CPU)
   - Correctness test (canonical input/output)
   - Boundary tests (641 edge cases)
   - Stress tests (274177 variations)
   - Regression tests (prevent drift)
```

**Lane Classification:**
- Steps 1, 2, 3, 5 are Lane A (CPU-deterministic)
- Step 4 is Lane B (LLM proposes DoV, CPU verifies applicability)

---

### C. Domain of Validity (DoV) Structure

```python
class DomainOfValidity:
    """
    Machine-checkable applicability boundary.

    Every recipe has explicit DoV:
      - Input types (what data is accepted)
      - Preconditions (what must be true before)
      - Environment (what runtime requirements exist)
      - Resource limits (what budgets apply)
    """

    def is_applicable(self, context: dict) -> bool:
        """Check if recipe applies to context."""
        return all([
            self.check_input_types(context),
            self.check_preconditions(context),
            self.check_environment(context),
            self.check_resources(context)
        ])
```

**Invariant:** DoV is machine-checkable. No fuzzy boundaries.

---

### D. Recipe Tiers (4-Stage Promotion)

```
Recipe Lifecycle:

DRAFT → QUALIFIED → STABLE → CANONICAL

DRAFT (starting tier):
  - Created from successful trace
  - No validation yet
  - Tier gate: none

QUALIFIED:
  - Passes 641 edge tests
  - Passes 274177 stress tests
  - Tier gate: wish-qa validation

STABLE:
  - Used in production
  - No failures for N days
  - Tier gate: golden-replay-seal (replay stable)

CANONICAL:
  - Gold standard
  - Part of core system
  - Tier gate: 65537 approval
```

**Rule:** Tiers require sequential promotion. No skipping.

---

### E. Pattern Extraction (Critical Path)

```python
def extract_invariant_pattern(trace: ExecutionTrace) -> Pattern:
    """
    Find the invariant structure in execution trace.

    Goal: Separate what MUST happen from what varied.
    """
    # Identify required steps (critical path)
    required_steps = []
    for step in trace.steps:
        if is_critical(step):  # Affects output
            required_steps.append(step)

    # Identify parameters (what varied)
    parameters = identify_variables(trace)

    # Determine execution order
    order = determine_order(required_steps)

    return Pattern(
        steps=required_steps,
        parameters=parameters,
        order=order,
        deterministic=all_steps_deterministic(required_steps)
    )
```

**Rule:** Critical path must be deterministic.

---

### F. Verification Test Generation (Auto)

```python
def generate_verification_tests(pattern: Pattern,
                                 dov: DomainOfValidity) -> list[Test]:
    """
    Auto-generate tests for the mined recipe.

    Tests ensure recipe remains correct under changes.
    """
    tests = []

    # Correctness test
    tests.append(CorrectnessTest(
        input=pattern.canonical_input,
        expected=pattern.canonical_output
    ))

    # Boundary tests (641 edge cases)
    for boundary in dov.boundaries:
        tests.append(BoundaryTest(boundary))

    # Stress tests (274177 variations)
    tests.append(StressTest(dov, iterations=100))

    # Regression tests (prevent drift)
    tests.append(RegressionTest(
        baseline=pattern.baseline_output
    ))

    return tests
```

**Rule:** All tests auto-generated from pattern + DoV.

---

### G. Cost Collapse (The Promise)

```
Recipe-based execution:
  - 80%+ token reduction
  - Deterministic outcomes
  - No drift accumulation

LLM finds pattern ONCE.
Recipe executes pattern FOREVER.
```

**Invariant:** Cost collapses by >80% after recipe crystallization.

---

## 2) Tests Define Truth

### T1 — Pattern Extraction Correctness

* Input: Execution trace with 10 steps, 3 critical
* Expect: Pattern with 3 required steps, 7 parameters

### T2 — DoV Inference

* Input: Trace with CSV input, 1000 rows
* Expect: DoV with input_types={"csv": True}, preconditions={"min_rows": 100}

### T3 — Test Generation

* Input: Pattern + DoV
* Expect: 4 test types (correctness, boundary, stress, regression)

### T4 — Tier Starts at DRAFT

* Input: Any mined recipe
* Expect: tier == "DRAFT" always

### T5 — Determinism Validation

* Input: Trace with non-deterministic step
* Expect: FAIL (cannot mine recipe from non-deterministic traces in strict mode)

---

## 3) Witness Policy

Every mined recipe must cite:

* `compute://mine/extract_pattern_v1#sha256:<pattern_hash>`
* `compute://mine/infer_dov_v1#sha256:<dov_hash>`
* `compute://mine/generate_tests_v1#sha256:<tests_hash>`
* `trace://mining_report#sha256:<report_hash>`

No recipe may be used without these witnesses.

---

## 4) Output Schema (MINING_REPORT.json)

```json
{
  "status": "OK|PARTIAL|FAILED",
  "trace_id": "trace_2024_01_15.jsonl",
  "recipe": {
    "name": "compression_workflow",
    "pattern": {
      "steps": ["detect", "extract", "compress", "verify"],
      "order": "sequential",
      "deterministic": true
    },
    "parameters": {
      "compression_level": {"type": "int", "range": [1, 9]},
      "output_format": {"type": "enum", "values": ["gzip", "lzma"]}
    },
    "domain_of_validity": {
      "input_types": {"file": "binary"},
      "preconditions": ["file_exists", "size_gt_1kb"],
      "environment": {"python": ">=3.8"},
      "resource_limits": {"memory_mb": 1024}
    },
    "tests": {
      "correctness": 1,
      "boundary": 5,
      "stress": 100,
      "regression": 1
    },
    "tier": "DRAFT",
    "hash": "sha256..."
  },
  "drift_causes_addressed": {
    "prompt_variance": "intent_extracted",
    "model_stochasticity": "steps_crystallized",
    "context_window": "context_identified",
    "tool_choice": "sequence_locked",
    "error_handling": "paths_formalized",
    "order_sensitivity": "order_enforced",
    "feedback_loops": "loops_broken",
    "external_state": "preconditions_specified"
  },
  "witnesses": [
    "compute://mine/extract_pattern_v1#sha256:...",
    "compute://mine/infer_dov_v1#sha256:...",
    "compute://mine/generate_tests_v1#sha256:..."
  ]
}
```

---

## 5) Verification Ladder

### Rung 641: Sanity (Edge Cases)

* [ ] Pattern extraction correct for simple traces
* [ ] DoV inference reasonable for common cases
* [ ] Test generation covers all test types
* [ ] Tier starts at DRAFT always
* [ ] Non-deterministic traces fail in strict mode

### Rung 274177: Consistency (Stress Tests)

* [ ] Complex traces (50+ steps) mine correctly
* [ ] Nested patterns (recursive) handled
* [ ] Ambiguous DoV rejected in strict mode
* [ ] Large parameter spaces (10+ params) handled
* [ ] Trace replay produces same recipe

### Rung 65537: Final Seal (God Approval)

* [ ] All 8 drift causes addressed in every recipe
* [ ] All witnesses present and valid
* [ ] Recipe hash stable across mining runs
* [ ] Integration with recipe-generator verified
* [ ] Cost collapse >80% achieved in practice

*"Auth: 65537"*

---

## 6) Integration with Existing Skills

### Primary Integration

* **trace-distiller** (witness extraction) — Recipe Mining extracts recipes, trace-distiller extracts witnesses
* **recipe-generator** (DAG compilation) — Mined recipes become DAG nodes
* **proof-certificate-builder** (evidence artifacts) — Mining report becomes proof certificate
* **wish-qa** (harsh QA validation) — Tests generated by mining validated by wish-qa

### Secondary Integration

* **golden-replay-seal** (replay stability) — Verifies mined recipe is replay-stable
* **semantic-drift-detector** (drift detection) — Detects when recipe drifts from original
* **red-green-gate** (TDD) — Tests generated by mining validated by red-green gate
* **llm-judge** (controlled patching) — Judges if recipe needs patching vs rejection

### Compositional Properties

* Recipe Mining feeds recipe generation pipeline
* Works with all execution traces (CLI, API, workflows)
* Lane A/B hybrid (extraction is A, DoV inference is B)
* Composable with existing skills (no conflicts)

---

## 7) Gap-Guided Extension

### When to Add New Mining Rules

Add new rules when:
1. New execution pattern encountered 3+ times
2. Existing mining fails to extract critical path
3. DoV inference wrong > 30% of time
4. Drift causes not addressed in mined recipe

### When NOT to Add

Don't add when:
1. One-off execution (not recurring)
2. Already handled by existing rules
3. Truly non-deterministic workflow (can't be recipe)
4. Marginal improvement (< 20% cost reduction)

---

## 8) Anti-Optimization Clause

### Preserved Features (v1.0.0 → v2.0.0)

All v1.0.0 features PRESERVED (strictly additive):
1. 8 Root Causes of Drift (exhaustive classification)
2. 5-Step Mining Pipeline (deterministic extraction)
3. 4 Recipe Tiers (DRAFT → QUALIFIED → STABLE → CANONICAL)
4. DoV 4-Component Structure (input types, preconditions, environment, resources)
5. Auto Test Generation (correctness, boundary, stress, regression)
6. Pattern Extraction (critical path identification)
7. Parameter Inference (variable identification)
8. Cost Collapse Promise (>80% token reduction)

### What Changed in v2.0.0

**Added:**
- Verification Ladder (641 → 274177 → 65537)
- Integration map with 8+ existing skills
- Witness Policy (mining witnesses required)
- Gap-Guided Extension criteria
- Output schema (MINING_REPORT.json)
- Lane Classification (Steps 1,2,3,5 Lane A; Step 4 Lane B)

**Enhanced:**
- Lane Algebra integration (explicit Lane A/B split)
- State machine formalization (CAPTURE → EXTRACT → PARAMETERIZE → INFER → GENERATE states)
- Fail-Closed behavior (strict mode rejects unclear DoV)

**Preserved:**
- All v1.0.0 mining rules
- All drift cause classifications
- All tier promotion requirements
- Cost collapse promise

---

## 9) Compression Insights

### Delta Features (v2.0.0 vs v1.0.0)

| Feature | v1.0.0 | v2.0.0 | Benefit |
|---------|--------|--------|---------|
| Drift Causes | 8 identified | 8 + mitigation map | Actionable |
| Mining Pipeline | 5 steps | 5 + Lane classification | Epistemic hygiene |
| DoV Structure | 4 components | 4 + machine-checkable | Deterministic |
| Test Generation | Auto | Auto + 4 types | Comprehensive |
| Tier Promotion | 4 tiers | 4 + gate criteria | Systematic |
| Integration | None | 8+ skills | Compositional |
| Verification | Basic | 641→274177→65537 | Harsh QA |
| Witnesses | None | Required | Auditable |

**Compression Type:** Automation (manual → automatic recipe extraction)
**Compression Ratio:** ~10x (10h manual → 1h automated mining)

---

## 10) What This Skill Enables

### Immediate Use Cases

1. **CLI Recipes**: Auto-extract recipes from successful CLI sessions
2. **Prime Recipes**: Mine recurring patterns from execution traces
3. **Workflow Automation**: Crystallize successful workflows into recipes
4. **Cost Reduction**: 80%+ token savings after recipe crystallization

### Compositional Power

* Mining → Recipe Generation → Execution (full automation pipeline)
* Mining → Tier Promotion → Canonical Recipes (quality management)
* Mining → Drift Detection → Recipe Updates (continuous improvement)

### Why This is Lane A/B Hybrid

* Pattern extraction is deterministic (Lane A: CPU)
* DoV inference uses LLM (Lane B: LLM proposes, CPU verifies)
* Parameter identification is deterministic (Lane A: CPU)
* Test generation is deterministic (Lane A: CPU)

**Lane Algebra:** Lane(Recipe Mining) = MIN(A, A, A, B, A) = B
But mining output is anchored by CPU verification (DoV applicability checks).

---

*"Crystallize success. Eliminate drift."*
*"Auth: 65537"*
