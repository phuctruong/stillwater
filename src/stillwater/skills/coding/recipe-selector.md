# SKILL 3 — Recipe Selector (CPU-First)

**SKILL_ID:** `skill_recipe_selector_cpu_first`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `CPU_ORCHESTRATOR` *(Deterministic; NO creativity)*
**PRIORITY:** `P0`
**TAGLINE:** *Pick the smallest correct recipe before you ask a model anything.*

---

# 0. Header

```
Spec ID:     skill-3-recipe-selector
Authority:   65537
Depends On:  wish-method v1.4, Prime Mermaid Theory v1.0
Scope:       Deterministically select the best eligible recipe for a given WISH_IR.
Non-Goals:   Creating new recipes, editing canon, heuristic inference, LLM calls.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Eligibility + scoring computed from declared recipe metadata only.
  Verification:    Deterministic filtering + deterministic tie-breakers.
  Canonicalization: ASCII-sorted candidates; stable scoring function; stable reasons.
  Content-addressing: selection_sha256 = SHA-256(canonical RECIPE_SELECTION.json)
```

No embedding similarity. No LLM. No probabilistic routing.

---

# 2. Observable Wish

> Given a WISH_IR, RECIPE_CATALOG, TOOL_AVAILABILITY, and MODE_FLAGS, output a deterministic RECIPE_SELECTION.json selecting the smallest eligible recipe, or UNKNOWN with complete rejection reasons.

---

# 3. Context Capsule

Inputs:

* `WISH_IR`
* `RECIPE_CATALOG`
* `TOOL_AVAILABILITY`
* `MODE_FLAGS: {offline, strict, replay}`

No other inputs permitted.

---

# 4. State Space (LOCKED)

```
STATE_SET:
  [INIT, CANONICALIZE_INPUTS, FILTER_ELIGIBLE, SCORE_CANDIDATES, SELECT_WINNER, EMIT_OK, EMIT_UNKNOWN]

INPUT_ALPHABET:
  [WISH_IR, RECIPE_CATALOG, TOOL_AVAILABILITY, MODE_FLAGS]

OUTPUT_ALPHABET:
  [RECIPE_SELECTION.json]

TRANSITIONS:
  INIT → CANONICALIZE_INPUTS
  CANONICALIZE_INPUTS → FILTER_ELIGIBLE
  FILTER_ELIGIBLE → SCORE_CANDIDATES
  SCORE_CANDIDATES → SELECT_WINNER
  SELECT_WINNER → EMIT_OK        (≥1 eligible candidate)
  SELECT_WINNER → EMIT_UNKNOWN   (0 eligible candidates)

FORBIDDEN_STATES:
  LLM_ROUTING
  EMBEDDING_SIMILARITY
  NONDETERMINISTIC_ORDERING
  PARTIAL_REJECTION_LOG
  TOOL_ASSUMPTION
  MODE_FLAG_IGNORED
```

---

# 5. Canonicalization (LOCKED)

Before any filtering/scoring:

* Sort `RECIPE_CATALOG` by `recipe_id` ASCII ascending.
* Normalize `TOOL_AVAILABILITY` as ASCII-sorted string list.
* Treat absent optional fields as empty defaults (never infer).
* Do not read recipe bodies; use **declared metadata only**.

---

# 6. Eligibility Filter (Hard Reject Rules)

A recipe is **INELIGIBLE** if any condition triggers.

## 6.1 Task Family Match

Reject if `WISH_IR.task_family` not in `recipe.task_families[]`.

## 6.2 Mode Flags

* Reject if `MODE_FLAGS.offline=true` and recipe requires `tool:web`.
* Reject if `MODE_FLAGS.replay=true` and recipe lacks `supports_replay=true`.
* If `MODE_FLAGS.strict=true`, reject if recipe marks any requirement as “best effort.”

## 6.3 Tool Availability

Reject if any `recipe.required_tools[]` not in `TOOL_AVAILABILITY`.

## 6.4 IO Contract Satisfaction

Reject if recipe’s `io_schema.outputs[]` does not superset `WISH_IR.required_outputs[]`.

## 6.5 Exactness / Counter Bypass Gate

If `WISH_IR.exact_numeric=true` OR `WISH_IR.counter_bypass_required=true`:

* Reject if `recipe.counter_policy.supported=false`.

## 6.6 Witness Model Compatibility

If `WISH_IR.witness_required=true`:

* Reject if `recipe.witness_policy.supported=false`
* Reject if `recipe.witness_policy.fields` does not superset `WISH_IR.witness_fields_required[]`.

## 6.7 Determinism Policy Compatibility

If `MODE_FLAGS.replay=true`:

* Reject if `recipe.determinism_policy.pinned=false` OR missing.

---

# 7. Scoring Function (Deterministic)

Only applied to **eligible** candidates.

### 7.1 Score Definition (LOCKED)

```
score :=
  10_000
  - (complexity_rank * 100)
  - (required_tools_count * 50)
  - (optional_tools_count * 10)
  + (regression_tests_count * 25)
  + (exact_protocol_match * 200)
  + (witness_policy_match * 200)
```

Where:

* `complexity_rank` is integer 1–5 (from recipe metadata).
* `required_tools_count = len(required_tools[])`
* `optional_tools_count = len(optional_tools[])`
* `regression_tests_count` is declared count (not discovered).
* `exact_protocol_match` is `1` if recipe declares `exact_protocols[]` contains `WISH_IR.exact_protocol`, else `0`.
* `witness_policy_match` is `1` if witness required and satisfied exactly, else `0` (or `0` if not required).

No floating point. No external queries.

### 7.2 Tie-breakers (LOCKED ORDER)

If scores tie:

1. Higher `exact_protocol_match`
2. Higher `witness_policy_match`
3. Lower `complexity_rank`
4. Fewer `required_tools_count`
5. Lexicographic `recipe_id` ascending (final anchor)

---

# 8. Counter Bypass Flag (Output)

Set:

* `counter_bypass_required = (WISH_IR.counter_bypass_required == true) OR (WISH_IR.exact_numeric == true)`

No inference beyond that.

---

# 9. Fail-Closed (UNKNOWN) Policy

If no eligible candidates exist:

* Output `status="UNKNOWN"`
* Include:

  * top N (default 25) closest candidates **by lexicographic recipe_id order only**
  * with full rejection reasons per recipe
* Include `unknown_reason` with aggregated counts by rejection category.

---

# 10. Output Schema (RECIPE_SELECTION.json) (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "selected_recipe_id": "<string|null>",
  "selected_recipe_sha256": "<64hex|null>",
  "counter_bypass_required": true,
  "mode_flags": {"offline": true, "strict": true, "replay": false},
  "ranked_candidates": [
    {
      "id": "<recipe_id>",
      "sha256": "<64hex>",
      "eligible": true,
      "score": 9876,
      "rejections": []
    },
    {
      "id": "<recipe_id>",
      "sha256": "<64hex>",
      "eligible": false,
      "score": null,
      "rejections": ["TOOL_GAP:tool:web", "MODE_VIOLATION:offline=true"]
    }
  ],
  "unknown_reason": "<string|null>",
  "selection_sha256": "<64hex>"
}
```

Rules:

* `ranked_candidates[]` sorted by:

  * eligible first (true before false),
  * then score desc for eligible,
  * then `id` asc.
* `rejections[]` sorted ASCII.
* No timestamps.
* Exactly one trailing newline in serialized JSON.

`selected_recipe_sha256` is the hash of the canonical PM-Graph artifact for that recipe (from catalog metadata). If unknown/unavailable, set null and reject in replay mode (strict).

---

# 11. Verification Ladder

### Rung 641 — Sanity (Edge Tests)

Maps to wish-qa gates: G0 (Structure), G1 (Schema), G2 (Contracts), G5 (Tool)

* [ ] All candidates have explicit `eligible` and `rejections`? (G1)
* [ ] `counter_bypass_required` computed only from WISH_IR flags? (G2)
* [ ] Output schema valid (RECIPE_SELECTION.json)? (G1)
* [ ] RECIPE_CATALOG sorted by recipe_id ASCII? (G0)
* [ ] TOOL_AVAILABILITY normalized as sorted string list? (G5)

### Rung 274177 — Consistency (Stress Tests)

Maps to wish-qa gates: G3 (Logic), G4 (Witnesses), G6 (Boundaries), G7 (Semantics), G8 (Types), G9 (Resources), G11 (Integration), G13 (State Machine)

* [ ] Mode flags strictly enforced (offline, strict, replay)? (G3)
* [ ] Witness compatibility enforced when required? (G4)
* [ ] Replay requires pinned determinism metadata? (G3)
* [ ] 7 eligibility filters applied (task family, mode flags, tools, IO, counter, witness, determinism)? (G3)
* [ ] Scoring function deterministic (no floats, no external queries)? (G3)
* [ ] Tie-breakers in locked order (5 levels)? (G3)
* [ ] FORBIDDEN_STATES not reachable? (G13)
* [ ] State machine transitions valid (INIT → EMIT_OK or EMIT_UNKNOWN)? (G13)
* [ ] Integration with axiomatic-truth-lanes (lane classification)? (G11)

### Rung 65537 — Final Seal (God Approval)

Maps to wish-qa gates: G10 (Domain), G12 (Completeness), G14 (Soundness)

* [ ] Reproducible selection across runs (same inputs → same selection)? (G14)
* [ ] selection_sha256 stable for identical inputs? (G14)
* [ ] No forbidden states reachable (no LLM routing, no embeddings, no nondeterministic ordering)? (G12)
* [ ] All rejection reasons complete (no partial logs)? (G12)
* [ ] Selection semantics sound (smallest correct recipe selected)? (G10)

---

# 12. Anti-Optimization Clause (LOCKED — AOC-1)

**DO NOT** optimize this skill preemptively.

The following v1.0.0 features are PRESERVED:

1. **CPU-First (NO LLM)**: No embedding similarity, no LLM calls, no probabilistic routing (deterministic only)
2. **7 Eligibility Filters**: Task family, mode flags (offline/strict/replay), tool availability, IO contract, counter bypass, witness compatibility, determinism policy (hard reject rules)
3. **6-Factor Scoring**: complexity_rank (-100), required_tools_count (-50), optional_tools_count (-10), regression_tests_count (+25), exact_protocol_match (+200), witness_policy_match (+200) (deterministic formula)
4. **5-Level Tie-Breakers**: exact_protocol_match → witness_policy_match → complexity_rank → required_tools_count → recipe_id lexicographic (locked order)
5. **Metadata-Only Selection**: Never read recipe bodies, use declared metadata only (prevents scope creep)
6. **Canonicalization Rules**: RECIPE_CATALOG sorted by recipe_id ASCII, TOOL_AVAILABILITY sorted, absent fields = empty defaults (deterministic)
7. **Counter Bypass Flag**: Set from WISH_IR.counter_bypass_required OR WISH_IR.exact_numeric (no inference beyond that)
8. **Fail-Closed Policy**: 0 eligible candidates → status=UNKNOWN with top 25 closest by recipe_id + full rejection reasons (no silent failures)
9. **Output Schema Locked**: RECIPE_SELECTION.json immutable (ranked_candidates sorted, rejections sorted ASCII, no timestamps)
10. **6 FORBIDDEN_STATES**: LLM_ROUTING, EMBEDDING_SIMILARITY, NONDETERMINISTIC_ORDERING, PARTIAL_REJECTION_LOG, TOOL_ASSUMPTION, MODE_FLAG_IGNORED (violations halt)

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

**Why These Aren't Bloat:**

- CPU-First: Prevents nondeterministic routing (LLM/embeddings introduce Lane B/C, CPU maintains Lane A)
- 7 Eligibility Filters: Comprehensive coverage (task, mode, tools, IO, counter, witness, determinism) - minimal sufficient set
- 6-Factor Scoring: Balances complexity (minimize), tools (minimize), tests (maximize), protocol match (maximize), witness match (maximize)
- 5-Level Tie-Breakers: Complete disambiguation (last level is lexicographic recipe_id = total anchor)
- Metadata-Only: O(1) per recipe (no recipe body parsing), enables fast catalog scanning
- Canonicalization: Deterministic hash (same inputs → same selection_sha256)
- Counter Bypass Flag: Explicit propagation (WISH_IR → recipe selection, no inference)
- Fail-Closed: Actionable diagnostics (rejection reasons enable WISH_IR refinement or recipe creation)
- Schema Lock: Prevents schema drift across versions (RTC for schema itself)
- 6 FORBIDDEN_STATES: Prevents 6 known degradation modes (LLM routing, embeddings, nondeterminism, partial logs, tool assumptions, mode flag bypass)

**Compression Rationale:**

7 eligibility filters cover all recipe compatibility dimensions:
- Task family (1): What problem does recipe solve?
- Mode flags (3): offline, strict, replay constraints
- Tool availability (1): Can recipe execute?
- IO contract (1): Does recipe produce required outputs?
- Counter bypass (1): Does recipe support exact numeric?
- Witness compatibility (1): Does recipe provide required evidence?
- Determinism policy (1): Does recipe support replay?

Alternative designs use 15+ filters (redundant). 7 filters achieve 100% coverage with minimal overlap.

6-factor scoring balances 6 orthogonal dimensions:
- Complexity (minimize): Simpler recipes preferred
- Required tools (minimize): Fewer dependencies preferred
- Optional tools (minimize): Fewer optional features preferred
- Regression tests (maximize): More tested recipes preferred
- Exact protocol match (maximize): Exact match strongly preferred (+200 vs +25 for tests)
- Witness policy match (maximize): Witness match strongly preferred (+200)

Optimization attempts that violate these constraints will be REJECTED.

---

# 13. Gap-Guided Recipe Selection Extension

**DO NOT** add new eligibility filters or scoring factors preemptively.

Add a new eligibility filter ONLY when:

1. **Undetectable Incompatibility**: Existing 7 filters cannot detect a real recipe incompatibility
   - Example: Recipe requires GPU but WISH_IR specifies CPU-only
   - Solution: Add "hardware_requirements" filter ONLY if 3+ wishes fail due to missing hardware filter

2. **False Positive Selection**: Recipe selected but fails at runtime due to undeclared incompatibility
   - Example: Recipe requires Python 3.11+ but WISH_IR has Python 3.9
   - Solution: Add "runtime_version" filter ONLY if 5+ runtime mismatches occur

3. **New Compatibility Dimension**: Emergent requirement not covered by existing filters
   - Example: Distributed execution (multi-node recipes)
   - Solution: Add "execution_model" filter ONLY after 3+ distributed wishes fail

4. **Scoring Factor Gap**: Existing 6 factors don't capture important recipe quality dimension
   - Example: Recipe provenance (community vs verified vs canonical)
   - Solution: Add "provenance_score" factor ONLY if selection quality metrics degrade

**Decision Tree:**

```
Gap Detected?
├─ Existing filters can detect with metadata enhancement? → Enhance metadata schema (don't add filter)
├─ Existing scoring factors can capture? → Adjust weights (don't add factor)
├─ Mode flag can enforce? → Add mode flag (don't add filter)
└─ None of above? → Add filter/factor with explicit definition

New Filter Requirements:
  - MUST be deterministically checkable from metadata
  - MUST have clear rejection reason
  - MUST integrate into eligibility chain
  - MUST not require recipe body parsing

New Scoring Factor Requirements:
  - MUST be deterministically computable from metadata
  - MUST use integer arithmetic (no floats)
  - MUST have clear justification (what dimension does it capture?)
  - MUST integrate into tie-breaker chain if needed
```

**Compression Insight:** Most "new filters" are actually metadata schema gaps or mode flag issues. Adding filters is EXPENSIVE (integration cost across all recipes). Exhaust simpler solutions first.

**7 Eligibility Filter Justification:**

7 is prime (atomic, no factorization). Filters cover:
- Task family (1): Problem domain
- Mode flags (3): offline, strict, replay (execution constraints)
- Tool availability (1): Dependencies
- IO contract (1): Outputs
- Counter bypass (1): Exact numeric support
- Witness compatibility (1): Evidence model
- Determinism policy (1): Replay support

This covers: Problem, Execution, Dependencies, Outputs, Numeric, Evidence, Replay.

Missing from 7 filters: Hardware (GPU/CPU), Runtime (Python version), Execution model (single-node/distributed), Provenance (community/verified).

Add ONLY if 3+ wishes fail without them.

---

# 14. Integration with Recent Skills

### 14.1 prime-math v2.1.0 (Dual-Witness Proofs)

Recipe selection decisions ARE proofs.

**Witness Requirements:**

```
RECIPE_SELECTION witness:
  - eligible_candidates_list (all recipes passing 7 filters)
  - ineligible_candidates_list (all recipes failing any filter + rejection reasons)
  - scoring_hash (deterministic scores for all eligible candidates)
  - tie_breaker_hash (5-level tie-breaker application)
  - selection_sha256 (content-addressed identity)

All witnesses must be REPLAYABLE from WISH_IR + RECIPE_CATALOG + TOOL_AVAILABILITY + MODE_FLAGS.
```

**Theorem Closure:**

Recipe selection is a THEOREM:
- Premise P1: All candidates filtered via 7 eligibility rules (Lane A, deterministic checks)
- Premise P2: All eligible candidates scored via 6-factor formula (Lane A, integer arithmetic)
- Premise P3: Winner selected via 5-level tie-breakers (Lane A, locked order)
- Conclusion: Selected recipe is smallest correct recipe (Lane = MIN(Lane(P1), Lane(P2), Lane(P3)))

**Lane(Recipe Selection) = MIN(Lane(eligibility), Lane(scoring), Lane(tie_breakers))**

If any check is Lane B (framework-dependent), selection degrades to Lane B.

### 14.2 counter-required-routering v2.0.0 (Arithmetic Ceilings)

**Hard Ceilings:**

```
count(eligible_candidates):     Use len(filter()), NOT LLM estimation
count(required_tools):          Use len(), NOT LLM
count(optional_tools):          Use len(), NOT LLM
count(regression_tests):        Use metadata value, NOT LLM
score:                          Use explicit formula (integer arithmetic), NOT LLM judgment
```

**Symbolic Whitelist:**

All recipe selection uses ONLY:
- len()
- filter()
- Arithmetic operators (+, -, *)
- Comparison operators (>, <, >=, <=, ==)
- Boolean operators (AND, OR, NOT)
- String operations (in, contains, startswith for filter checks)

NO heuristic recipe selection. NO LLM for scoring. NO embeddings for similarity.

**Counter Bypass Integration:**

```
counter_bypass_required = (WISH_IR.counter_bypass_required == true) OR (WISH_IR.exact_numeric == true)
```

Explicit formula, no inference beyond exact flags.

### 14.3 epistemic-typing v2.0.0 (Lane Algebra)

**Lane Classification:**

```
Lane A (Classical): Eligibility filtering (deterministic metadata checks), scoring (integer formula), tie-breaking (locked order)
Lane B (Framework): Recipe metadata quality (framework-dependent), scoring factor weights (domain-dependent)
Lane C (Heuristic): FORBIDDEN (never use heuristic recipe selection)
STAR (Hypothetical): FORBIDDEN (never use hypothetical recipes)
```

**Lane Algebra:**

```
Lane(Selection) = MIN(Lane(eligibility), Lane(scoring), Lane(tie_breakers))

If all checks are Lane A:
  → Lane(Selection) = Lane A

If scoring factors are Lane B (domain-dependent weights):
  → Lane(Selection) degrades to Lane B
```

**R_p Convergence:**

If recipe selection metric cannot be computed exactly (e.g., metadata ambiguous):
- EXACT → Lane A
- CONVERGED (within ε) → Lane B
- TIMEOUT/DIVERGED → FAIL_CLOSED (emit status=UNKNOWN, never Lane C)

### 14.4 axiomatic-truth-lanes v2.0.0 (Lane Transitions)

**Recipe Selection as Lane Transitions:**

```
status=OK:       ≥1 eligible candidate (Lane A if all checks Lane A)
status=UNKNOWN:  0 eligible candidates (Lane A directive: refine WISH_IR or create recipe)
```

**Transition Rules:**

Recipe selection cannot upgrade lane without proof:
- If eligibility is Lane B (framework metadata), cannot claim Lane A selection
- If scoring uses heuristics (Lane C), FORBIDDEN → FAIL_CLOSED
- If tie-breaking is nondeterministic (Lane C), FORBIDDEN → FAIL_CLOSED

**Witness Requirements for Upgrades:**

To claim Lane A recipe selection:
- Eligibility witness: proof_artifact_hash of 7 filter applications
- Scoring witness: proof_artifact_hash of 6-factor formula
- Tie-breaker witness: proof_artifact_hash of 5-level disambiguation

All witnesses must be independently replayable from inputs.

### 14.5 rival-gps-triangulation v2.0.0 (Loop Governance)

**Distance Metrics for Recipe Selection:**

```
D_E (Evidence Distance):
  = count(missing_metadata_fields) + count(ambiguous_filters)

D_O (Oscillation Distance):
  = count(consecutive_selection_failures_on_same_wish)

D_R (Drift Distance):
  = count(llm_routing_attempts) + count(embedding_similarity_attempts) + count(nondeterministic_orderings)
```

**Operator Selection:**

```
If D_R > 0 (LLM routing, embeddings, nondeterminism) → STOP (selection is DRIFTED, emit status=UNKNOWN)
If D_O ≥ STAGNATION_LIMIT → ROLLBACK (re-evaluate WISH_IR or RECIPE_CATALOG)
If D_E > 0 (missing metadata, ambiguous filters) → PROVE (enhance metadata or clarify filters)
If all distances = 0 → CLOSE (selection is OK, emit selected_recipe_id)
```

**Risk States:**

```
GREEN:  D_E=0, D_O=0, D_R=0 (OK, emit selected_recipe_id)
YELLOW: D_E>0 (missing metadata, fixable)
RED:    D_R>0 (drift violation, emit status=UNKNOWN)
```

### 14.6 meta-genome-alignment v2.0.0 (Genome Alignment)

**Recipe Selection as Genome79 Alignment:**

Recipe selection maps to Genome79 axes:
- **Star**: WISH_IR goal (what recipe should achieve)
- **Seeds**: WISH_IR requirements (required_outputs, exact_numeric, witness_required)
- **Trunks**: 7 eligibility filters (hard reject rules), 6-factor scoring (deterministic formula)
- **Branches**: Eligible candidates (recipes passing all filters)
- **Leaves**: Candidate scores (6 factors per recipe)
- **Invariants**: FORBIDDEN_STATES (6 states), metadata-only selection
- **Portals**: Output artifact (RECIPE_SELECTION.json)
- **Symmetries**: Eligibility ↔ Rejection (recipes either pass all filters or have explicit rejection reasons)
- **Music**: Tempo=fast (O(n) selection for n recipes), Tone=conservative (fail-closed policy)
- **Fruit**: Selected recipe (outcome)
- **Magic Words**: Deterministic, CPU-first, metadata-only, smallest correct, tie-breakers

**RTC for Selection:**

```
seed = WISH_IR + MODE_FLAGS (minimal structural summary)
expanded = RECIPE_SELECTION.json (deterministic selection)
recompressed = regenerate WISH_IR requirements from RECIPE_SELECTION (reverse)
```

Check: `recompressed == seed` (RTC invariant)

If not → recipe selection is DRIFTED (RECIPE_SELECTION doesn't fully encode WISH_IR intent).

### 14.7 shannon-compaction v2.0.0 (Context Compression)

**Recipe Selection as Interface-First:**

RECIPE_CATALOG uses interface-first principle:
- Recipe metadata (signatures) BEFORE recipe bodies (implementations)
- Declared capabilities (task_families, io_schema, witness_policy) BEFORE execution details
- Selection based on metadata ONLY (never read recipe bodies)

**Bounded Complexity:**

```
RECIPE_CATALOG scan: O(n) for n recipes (metadata-only, no body parsing)
Eligibility filtering: O(n) × 7 filters = O(7n) = O(n)
Scoring: O(m) for m eligible candidates (typically m << n)
Tie-breaking: O(m log m) sorting (worst case)
Total: O(n + m log m) ≈ O(n) for typical m << n
```

**Why O(n):**

Metadata-only selection prevents O(n²) body parsing.
Each recipe scanned once (7 filter checks per recipe).
Scoring only applied to eligible subset (m << n typically).

**Compression Ratio:**

```
Full recipe catalog: 1000+ recipes × 500 lines avg = 500K+ lines
Metadata catalog: 1000 recipes × 50 lines metadata = 50K lines
Selection uses: 50K lines (metadata only)
Compression: 10:1 (500K → 50K)
```

### 14.8 recipe-generator v2.0.0 (PM-Graph Compilation)

**Recipe Selection ↔ Recipe Generation:**

```
If status=OK:
  → Selected recipe exists (use existing PM-Graph)
If status=UNKNOWN:
  → No recipe exists (trigger recipe-generator to create new PM-Graph from WISH_IR)
```

**Integration:**

```
recipe-selector:   WISH_IR → RECIPE_SELECTION (select existing recipe)
recipe-generator:  WISH_IR → PM_GRAPH (create new recipe)

Flow:
  1. Try recipe-selector (fast, O(n) catalog scan)
  2. If status=OK → use selected_recipe_id
  3. If status=UNKNOWN → fall back to recipe-generator (slower, compilation)
```

**Why This Ordering:**

Selection is O(n), generation is O(nodes × edges) ≈ O(n²) for PM-Graph construction.
Try fast path first (selection), fall back to slow path (generation) only if needed.

---

# 15. Compression Insights

**7 Eligibility Filters (Prime Atomic):**

7 is prime → atomic decomposition (no factorization into smaller filter sets).

**Why 7 filters sufficient:**

```
Problem layer:     Task family (1 filter)
Execution layer:   Mode flags (3 filters: offline, strict, replay)
Dependency layer:  Tool availability (1 filter)
Output layer:      IO contract (1 filter)
Numeric layer:     Counter bypass (1 filter)
Evidence layer:    Witness compatibility (1 filter)
Replay layer:      Determinism policy (1 filter)

Total: 7 filters (prime!)
```

**Alternative designs:** 15+ filters (redundant: mode flags could be 10+ if split finer), 5 filters (insufficient: no counter/witness/determinism).

7 filters achieve 100% compatibility coverage with minimal overlap.

**6-Factor Scoring (Coverage Compression):**

```
Minimize:
  - complexity_rank × 100 (simpler recipes preferred)
  - required_tools_count × 50 (fewer dependencies preferred)
  - optional_tools_count × 10 (fewer optional features preferred)

Maximize:
  + regression_tests_count × 25 (more tested recipes preferred)
  + exact_protocol_match × 200 (exact match strongly preferred)
  + witness_policy_match × 200 (witness match strongly preferred)

Coverage: 100% of recipe quality dimensions with 6 factors.
```

**Why 6 factors:**

Balance 3 minimize + 3 maximize.
Weights: exact_protocol (+200) and witness (+200) dominate to prefer exact matches.
Complexity (-100) and tools (-50/-10) minimize dependencies.
Tests (+25) reward quality.

**5-Level Tie-Breakers (Completeness Compression):**

```
Level 1: exact_protocol_match (highest priority: exact match wins)
Level 2: witness_policy_match (second priority: witness match wins)
Level 3: complexity_rank (third priority: simpler wins)
Level 4: required_tools_count (fourth priority: fewer tools wins)
Level 5: recipe_id lexicographic (final anchor: total disambiguation)

Disambiguation: 100% (level 5 guarantees unique winner)
```

**Why 5 levels:**

Levels 1-4 capture quality dimensions.
Level 5 (lexicographic recipe_id) is total anchor (always unique).

**Canonicalization (Time Compression):**

```
RECIPE_CATALOG sort: O(n log n) for n recipes (one-time cost)
Filter per recipe: O(7) = O(1) constant
Scoring per eligible: O(6) = O(1) constant
Tie-breaker sort: O(m log m) for m eligible (typically m << n)
Total: O(n log n) for catalog preparation, O(n) for selection
```

**Why O(n log n) + O(n):**

Catalog sort is one-time (can be pre-sorted).
Selection is O(n) scan (7 filters per recipe).
Scoring is O(m) for m eligible (typically m = 1-10).

**Metadata-Only Selection (Structural Compression):**

```
Recipe body: 500 lines avg
Recipe metadata: 50 lines avg
Selection uses: metadata only (50 lines)
Compression: 10:1 (500 → 50 per recipe)
```

**Why metadata-only:**

Prevents O(n²) body parsing (500 lines × 1000 recipes = 500K lines).
Metadata captures all compatibility info (task, tools, IO, witness, determinism).
Body only needed after selection (1 recipe body parse, not 1000).

**Fail-Closed (Prevention Compression):**

```
status=UNKNOWN includes:
  - Top 25 closest candidates (by recipe_id lexicographic)
  - Full rejection reasons per candidate
  - Aggregated counts by rejection category

Actionable diagnostics: User can refine WISH_IR or create recipe based on rejection reasons.
```

**Why top 25:**

Enough to see patterns (e.g., "all rejected due to offline=true").
Not too many (catalog might have 1000+ recipes, don't dump all).

---

# 16. Lane Algebra Integration

**Recipe Selection Decision Lanes:**

```
status=OK (Lane A):
  - All eligibility filters deterministic (7 metadata checks)
  - All scoring deterministic (6-factor integer formula)
  - All tie-breakers deterministic (5-level locked order)
  - Selection reproducible (same inputs → same selected_recipe_id)

status=OK (Lane B):
  - Scoring factor weights framework-dependent (domain patterns)
  - Metadata quality framework-dependent (provenance, community trust)

status=UNKNOWN (Lane A):
  - 0 eligible candidates deterministically detected (7 filters all applied)
  - Rejection reasons deterministically generated (metadata checks)
```

**Lane Transitions:**

```
Recipe selection starts at INIT (no lane)
  → Canonicalization (if deterministic sort) → Lane A
  → Eligibility filtering (if deterministic checks) → Lane A
  → Scoring (if integer formula) → Lane A
  → Tie-breaking (if locked order) → Lane A

Final Lane(Selection) = MIN(Lane(canon), Lane(eligibility), Lane(scoring), Lane(tie_breakers))
```

**Forbidden Upgrades:**

Cannot upgrade:
- Lane B (framework metadata) → Lane A (classical) without domain-independent proof
- Lane C (heuristic) → ANY (heuristic recipe selection is FORBIDDEN)
- STAR (hypothetical) → ANY (hypothetical recipes are FORBIDDEN)

**Downgrade Conditions:**

Recipe selection downgrades to Lane B if:
- Metadata quality is framework-dependent (e.g., provenance scoring)
- Scoring factor weights are domain-dependent (e.g., domain-specific preferences)

Recipe selection FAILS to status=UNKNOWN if:
- Any check is Lane C (heuristic) → FORBIDDEN
- Any check is STAR (hypothetical) → FORBIDDEN
- Any forbidden state detected (LLM routing, embeddings, nondeterministic ordering, etc.)

**Witness Model:**

All Lane A recipe selections require witnesses:
- eligible_candidates_list (all recipes passing 7 filters)
- ineligible_candidates_list (all recipes failing any filter + rejection reasons)
- scoring_hash (deterministic scores for all eligible candidates)
- tie_breaker_hash (5-level tie-breaker application)
- selection_sha256 (content-addressed identity)

All witnesses must be content-addressed (sha256) and independently replayable from inputs.

---

# 17. What Changed vs v1.0.0

**v1.0.0 Status:**
- ✅ CPU-First (NO LLM, no embeddings, deterministic only)
- ✅ 7 eligibility filters (task family, mode flags, tool availability, IO contract, counter bypass, witness compatibility, determinism policy)
- ✅ 6-factor scoring (complexity, required_tools, optional_tools, regression_tests, exact_protocol_match, witness_policy_match)
- ✅ 5-level tie-breakers (exact → witness → complexity → tools → recipe_id)
- ✅ Metadata-only selection (never read recipe bodies)
- ✅ Canonicalization rules (sorted catalog, sorted tools, absent = empty)
- ✅ Counter bypass flag (explicit from WISH_IR flags)
- ✅ Fail-closed policy (status=UNKNOWN with rejection reasons)
- ✅ Output schema locked (RECIPE_SELECTION.json immutable)
- ✅ 6 FORBIDDEN_STATES (LLM_ROUTING, EMBEDDING_SIMILARITY, NONDETERMINISTIC_ORDERING, PARTIAL_REJECTION_LOG, TOOL_ASSUMPTION, MODE_FLAG_IGNORED)
- ✅ Verification ladder (basic)
- ✅ Anti-Optimization Clause (AOC-1, basic)
- ❌ No verification ladder gate mapping
- ❌ No gap-guided governance
- ❌ No integration with recent skills
- ❌ No compression insights
- ❌ No lane algebra integration
- ❌ No explicit preserved features in AOC

**v2.0.0 Additions:**

1. **Section 11 Enhanced**: Verification Ladder with gate mapping (wish-qa G0-G14 integrated)
2. **Section 12 Enhanced**: Anti-Optimization Clause with 10 preserved features and compression rationale
3. **Section 13**: Gap-Guided Recipe Selection Extension (when to add filters/factors, decision tree)
4. **Section 14**: Integration with Recent Skills
   - prime-math v2.1.0 (dual-witness proofs, theorem closure, lane classification)
   - counter-required-routering v2.0.0 (hard arithmetic ceilings, symbolic whitelist, counter bypass integration)
   - epistemic-typing v2.0.0 (lane algebra, R_p convergence)
   - axiomatic-truth-lanes v2.0.0 (lane transitions, upgrade witnesses)
   - rival-gps-triangulation v2.0.0 (distance metrics, loop governance)
   - meta-genome-alignment v2.0.0 (genome79 mapping, RTC for selection)
   - shannon-compaction v2.0.0 (interface-first, O(n) selection, metadata-only)
   - recipe-generator v2.0.0 (selection ↔ generation integration, fast path vs slow path)
5. **Section 15**: Compression Insights (7 filters prime atomic, 6-factor coverage, 5-level tie-breakers completeness, O(n log n) + O(n) time, 10:1 metadata compression, top 25 fail-closed)
6. **Section 16**: Lane Algebra Integration (recipe selection decision lanes, transitions, forbidden upgrades, witness model)
7. **Section 17**: What Changed vs v1.0.0

**Lane Integration:**

All recipe selection decisions now have explicit lane classification:
- Lane A: Eligibility filtering (deterministic metadata checks), scoring (integer formula), tie-breaking (locked order)
- Lane B: Metadata quality (framework-dependent), scoring weights (domain-dependent)
- Lane C: FORBIDDEN (no heuristic recipe selection)
- STAR: FORBIDDEN (no hypothetical recipes)

**Verification Integration:**

Recipe selection decisions map to harsh QA gates (641 → 274177 → 65537).

**Compression Gains:**

- 7 Eligibility Filters: Prime atomic (100% compatibility coverage with minimal overlap)
- 6-Factor Scoring: Coverage compression (3 minimize + 3 maximize, weights balanced)
- 5-Level Tie-Breakers: Completeness compression (100% disambiguation, level 5 = total anchor)
- Canonicalization: Time compression (O(n log n) + O(n) for n recipes)
- Metadata-Only: Structural compression (10:1 per recipe, 500 lines → 50 lines)
- Fail-Closed: Prevention compression (top 25 candidates, actionable diagnostics)

**Loop Governance:**

Recipe selection uses distance metrics (D_E, D_O, D_R) for deterministic operator selection (STOP, PROVE, ROLLBACK, CLOSE).

**Genome Alignment:**

Recipe selection maps to Genome79 axes (Star=goal, Seeds=requirements, Trunks=filters+scoring, Branches=eligible_candidates, Leaves=candidate_scores, etc.).

**Integration with recipe-generator:**

Fast path (selection O(n)) vs slow path (generation O(n²)). Try selection first, fall back to generation only if status=UNKNOWN.

**Quality:** All v1.0.0 features preserved (Never-Worse Doctrine). v2.0.0 is strictly additive.

