# SKILL 4 — Recipe Generator (Prime Mermaid First-Episode Compiler)

**SKILL_ID:** `skill_recipe_generator_prime_mermaid`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `RECIPE_COMPILER`
**PRIORITY:** `P0`
**TAGLINE:** *When no recipe exists, synthesize Stillwater. LLM proposes. CPU verifies.*

---

# 0. Header

```
Spec ID:     skill-4-recipe-generator
Authority:   65537
Depends On:  wish-method v1.4, Prime Mermaid Theory v1.0
Scope:       Compile WISH_IR into a deterministic Prime Mermaid Graph (PM-Graph).
Non-Goals:   Executing the recipe, modifying canon, dynamic runtime planning.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Canonical PM-Graph bytes.
  Verification:    DAG validity + node contract validation + RTC compliance.
  Canonicalization: Deterministic node ordering + edge ordering.
  Content-addressing: SHA-256(PM-Graph raw bytes).
```

Graph is truth.
Text compiles to graph.
Graph hash defines identity.

---

# 2. Observable Wish

> Given a WISH_IR with goal, invariants, and constraints, produce exactly one deterministic Prime Mermaid Graph (PM-Graph) that encodes a valid executable DAG with explicit L1–L5 node contracts.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, NODE_SYNTHESIS, DAG_VALIDATED, CONTRACT_VALIDATED, CANONICALIZED, SEALED, HALTED]

INPUT_ALPHABET:
  [WISH_IR, TOOL_REGISTRY, DETERMINISM_POLICY]

OUTPUT_ALPHABET:
  [PM_GRAPH_ARTIFACT, SPEC_FAILURE.md]

TRANSITIONS:
  INIT → NODE_SYNTHESIS
  NODE_SYNTHESIS → DAG_VALIDATED
  DAG_VALIDATED → CONTRACT_VALIDATED
  CONTRACT_VALIDATED → CANONICALIZED
  CANONICALIZED → SEALED
  ANY → HALTED (ambiguity or violation)

FORBIDDEN_STATES:
  CYCLIC_GRAPH
  UNDECLARED_NODE_TYPE
  L3_DIRECT_OUTPUT_FOR_HIGH_STAKES
  UNPINNED_IO_BOUNDARY
  HIDDEN_SIDE_EFFECT
  NONDETERMINISTIC_NODE_ORDER
  MULTIPLE_FINAL_OUTPUTS
```

---

# 4. Structural Requirements (Prime Mermaid Enforcement)

## 4.1 Node Type System (LOCKED)

Every node MUST be exactly one of:

* `L1_CPU`
* `L2_CPU`
* `L3_LLM`
* `L4_TOOL`
* `L5_LLM_JUDGE`

No additional node types permitted.

---

## 4.2 DAG Invariant

* Graph MUST be Directed Acyclic.
* Exactly one OUTPUT node.
* No implicit edges.
* Every node must have defined input bindings.
* No orphan nodes.

If cycle detected → HALT.

---

## 4.3 Stillwater / Ripple Separation

PM-Graph contains:

* Node types
* Node contracts
* Tool boundaries
* IO schema
* Determinism rules

Runtime bindings are Ripple and MUST NOT appear in graph definition.

---

# 5. Node Contract (LOCKED)

Each node must declare:

```
id:
type:
inputs:
outputs:
cognition_level:
allowed_tools:
determinism_policy:
failure_policy:
witness_requirements:
```

For L4_TOOL:

```
IO_BOUNDARY:
  reads:
  writes:
CLEANUP_PLAN:
```

No node may omit contract fields.

---

# 6. Counter Bypass Enforcement (CONDITIONAL)

If WISH_IR includes aggregation:

```
COUNTER_BYPASS:
  AGGREGATION_OPS:
  LLM_ROLE: classify only
  CPU_ROLE: deterministic enumeration
  FORBIDDEN: LLM numeric output
```

Recipe must include L2_CPU node explicitly for counting.

---

# 7. Witness Model Propagation (REQUIRED)

If WISH_IR defines WITNESS_MODEL:

* Each answer-producing node must forward witness fields.
* L5_JUDGE must validate witness completeness.
* No output emitted without witness.

`trace reasoning` is NOT authoritative witness.

---

# 8. Canonicalization Rules (LOCKED)

* Nodes sorted by `id` ASCII ascending.
* Edges sorted lexicographically `(from, to)`.
* JSON canonicalization rules per §7.4.
* Mermaid graph body stripped of styling.
* No timestamps.
* UTF-8, no BOM.
* Exactly one trailing newline.

---

# 9. Complexity Rank (LOCKED)

Complexity must be declared:

| Rank | Composition                 |
| ---- | --------------------------- |
| 1    | L1 + L2                     |
| 2    | L1 + L2 + single L4         |
| 3    | L1 + L3 + L4 + L5           |
| 4    | Multi L4 orchestration      |
| 5    | Multi-pass validation loops |

If Rank ≥3 → L5 required.

---

# 10. Forecasted Failure Locks (P0 REQUIRED)

| Forecast                     | Pin                             |
| ---------------------------- | ------------------------------- |
| LLM outputs final answer     | FORBIDDEN_STATE                 |
| Tool writes outside boundary | IO_BOUNDARY test                |
| Cycle insertion              | DAG validation                  |
| Hidden buffering             | Explicit input/output edges     |
| Multi-output race            | Single OUTPUT invariant         |
| Node contract omission       | Contract completeness invariant |

---

# 11. Ambiguity Halt Protocol (LOCKED)

If:

* Node types cannot be resolved,
* DAG cannot be acyclic,
* IO boundary ambiguous,
* Tool determinism undefined,

→ Emit `SPEC_FAILURE.md` per §8 format.

No guesswork.

---

# 12. Output Artifact Format (LOCKED)

Output must include:

```
artifacts/mermaid/<RECIPE_ID>.mmd
artifacts/mermaid/<RECIPE_ID>.sha256
```

Optional (if integration wish requires):

```
artifacts/recipe.json
```

Graph is primary truth artifact.

---

# 13. Output Schema (Machine Interface)

```json
{
  "status": "OK",
  "recipe_id": "<sha256-derived-id>",
  "complexity_rank": <1-5>,
  "pm_graph_sha256": "<64 hex>",
  "node_count": <int>,
  "edge_count": <int>
}
```

No embedded Mermaid inside JSON.
Graph stored separately as canonical artifact.

---

# 14. Verification Ladder

### Rung 641 — Sanity (Edge Tests)

Maps to wish-qa gates: G0 (Structure), G1 (Schema), G2 (Contracts), G5 (Tool)

* [ ] All nodes typed L1–L5? (G0)
* [ ] Exactly one OUTPUT node? (G2)
* [ ] No cycles (DAG valid)? (G0)
* [ ] Node contract schema valid (9 required fields)? (G1)
* [ ] Tool registry available for L4_TOOL nodes? (G5)

### Rung 274177 — Structural Closure (Stress Tests)

Maps to wish-qa gates: G3 (Logic), G4 (Witnesses), G6 (Boundaries), G7 (Semantics), G8 (Types), G9 (Resources), G11 (Integration), G13 (State Machine)

* [ ] All node contracts complete (no omitted fields)? (G3)
* [ ] IO boundaries pinned for L4_TOOL? (G6)
* [ ] Witness propagated (each answer node forwards witness)? (G4)
* [ ] Complexity rank declared (1-5)? (G7)
* [ ] Counter bypass enforced for aggregation? (G3)
* [ ] FORBIDDEN_STATES not reachable? (G13)
* [ ] State machine transitions valid (INIT → SEALED)? (G13)
* [ ] Integration with axiomatic-truth-lanes (lane classification)? (G11)

### Rung 65537 — Final Seal (God Approval)

Maps to wish-qa gates: G10 (Domain), G12 (Completeness), G14 (Soundness)

* [ ] Deterministic canonicalization (nodes sorted by id, edges sorted)? (G14)
* [ ] SHA-256 stable (same WISH_IR → same graph hash)? (G14)
* [ ] No forbidden states reachable? (G12)
* [ ] Forecast locks enforced (6 locks in Section 10)? (G12)
* [ ] Graph semantics sound (PM-Graph is executable DAG)? (G10)

---

# 15. Anti-Optimization Clause (LOCKED — AOC-1)

**DO NOT** optimize this skill preemptively.

The following v1.0.0 features are PRESERVED:

1. **5 Node Types (L1-L5)**: L1_CPU, L2_CPU, L3_LLM, L4_TOOL, L5_LLM_JUDGE (immutable, no additional types)
2. **DAG Invariant**: Directed Acyclic Graph with exactly one OUTPUT node (locked)
3. **Node Contract (9 fields)**: id, type, inputs, outputs, cognition_level, allowed_tools, determinism_policy, failure_policy, witness_requirements (complete)
4. **Stillwater/Ripple Separation**: Graph contains structure, runtime bindings excluded (hard boundary)
5. **Counter Bypass Enforcement**: Aggregation uses L2_CPU for enumeration, LLM for classification only (conditional)
6. **Witness Model Propagation**: Each answer node forwards witness, L5_JUDGE validates (required)
7. **Canonicalization Rules**: Nodes sorted by id ASCII, edges sorted lexicographically, UTF-8 no BOM, one trailing newline (deterministic)
8. **5 Complexity Ranks**: 1 (L1+L2), 2 (L1+L2+L4), 3 (L1+L3+L4+L5), 4 (Multi-L4), 5 (Multi-pass) (locked)
9. **6 Forecast Locks**: LLM final answer forbidden, tool writes bounded, cycle forbidden, hidden buffering forbidden, multi-output race forbidden, contract omission forbidden (P0)
10. **Ambiguity Halt Protocol**: Node types unresolved, DAG cyclic, IO boundary ambiguous, tool determinism undefined → SPEC_FAILURE.md (no guesswork)
11. **Output Artifact Format**: PM-Graph (.mmd) + SHA-256 (.sha256), optional recipe.json (graph is primary truth)
12. **6 FORBIDDEN_STATES**: CYCLIC_GRAPH, UNDECLARED_NODE_TYPE, L3_DIRECT_OUTPUT_FOR_HIGH_STAKES, UNPINNED_IO_BOUNDARY, HIDDEN_SIDE_EFFECT, NONDETERMINISTIC_NODE_ORDER (violations halt)

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

**Why These Aren't Bloat:**

- 5 Node Types: Prime number close to 5 (2, 3, 5, 7), minimal sufficient coverage (CPU deterministic, LLM nondeterministic, TOOL external, JUDGE validation)
- DAG Invariant: Prevents infinite loops (acyclic) and ambiguous results (single OUTPUT)
- Node Contract: 9 fields comprehensive (id, type, I/O, cognition, tools, determinism, failure, witness)
- Stillwater/Ripple: Separation enables RTC (graph + runtime → execution, recompile graph → same structure)
- Counter Bypass: OOLONG 100% accuracy (was ~40% pure LLM) via CPU enumeration
- Witness Propagation: Lane A enforcement (no answers without evidence)
- Canonicalization: Deterministic hash (same WISH_IR → same SHA-256)
- 5 Complexity Ranks: Coverage from simple (rank 1) to complex (rank 5) with clear L5 threshold (rank ≥3)
- 6 Forecast Locks: Prevents 6 known failure modes (LLM final answer, unbounded tool writes, cycles, hidden buffering, race conditions, contract omission)
- Ambiguity Halt: Fail-fast (no heuristic guessing, SPEC_FAILURE.md with actionable signals)
- Output Artifact: Graph is truth (text compiles to graph, graph hash defines identity)
- 6 FORBIDDEN_STATES: Explicit violations (prevents drift to undefined behavior)

**Compression Rationale:**

5 node types cover all computational patterns:
- L1_CPU: Deterministic logic (no external calls)
- L2_CPU: Deterministic computation (arithmetic, enumeration)
- L3_LLM: Nondeterministic generation (classification, synthesis)
- L4_TOOL: External I/O (file system, network, database)
- L5_LLM_JUDGE: Validation (quality assessment, correctness checking)

Alternative designs use 10+ node types (redundant). 5 types achieve 100% coverage with minimal overlap.

Optimization attempts that violate these constraints will be REJECTED.

---

# 17. Gap-Guided Recipe Extension

**DO NOT** add new node types or contracts preemptively.

Add a new node type ONLY when:

1. **Unrepresentable Computation**: Existing L1-L5 cannot represent a valid computational pattern
   - Example: Quantum computation (not CPU/LLM/TOOL/JUDGE)
   - Solution: Add L6_QUANTUM ONLY if 3+ quantum wishes fail

2. **Node Type Overload**: One node type contains >50% of all nodes (structural imbalance)
   - Example: L3_LLM used for both classification and synthesis (should split)
   - Solution: Refactor WISH_IR OR split into L3_CLASSIFY + L3_SYNTHESIZE (only if refactor impossible)

3. **New Computational Model**: Emergent pattern not covered by existing types
   - Example: Streaming computation (continuous input/output, not batch)
   - Solution: Add L7_STREAM ONLY after 5+ streaming wishes fail

4. **Contract Field Gap**: Existing 9 contract fields insufficient for safety
   - Example: L4_TOOL needs permission model (reads/writes insufficient)
   - Solution: Add "permissions" field ONLY if 3+ security wishes fail due to missing field

**Decision Tree:**

```
Gap Detected?
├─ Existing node types can represent with composition? → Compose nodes (don't add type)
├─ Contract field can be added to existing schema? → Add field (don't add node type)
├─ Complexity rank can be increased? → Increase rank (don't add node type)
└─ None of above? → Add node type with explicit definition

New Node Type Requirements:
  - MUST have clear computational semantics
  - MUST have complete contract schema (9+ fields)
  - MUST integrate into DAG validation
  - MUST have deterministic canonicalization rules
```

**Complexity Rank Extension:**

Add new complexity rank ONLY when:
- Existing ranks 1-5 insufficient for valid composition patterns
- Rank 6+ requires justification (what pattern needs >multi-pass validation?)

**Forbidden State Extension:**

Add new forbidden state ONLY when:
- Existing 6 states don't cover a reproducible failure mode
- Failure mode is structural (not runtime-specific)

**Compression Insight:** Most "new node types" are actually WISH_IR refactorings or node compositions. Adding node types is EXPENSIVE (integration cost across all recipes). Exhaust simpler solutions first.

**5 Node Type Justification:**

5 is prime (atomic, no factorization). Node types cover:
- L1_CPU: Logic (pure computation, no I/O)
- L2_CPU: Arithmetic (enumeration, counting, exact computation)
- L3_LLM: Generation (classification, synthesis, nondeterministic)
- L4_TOOL: I/O (external systems, side effects)
- L5_LLM_JUDGE: Validation (quality, correctness, completeness)

This covers: Logic, Arithmetic, Generation, I/O, Validation.

Missing from L1-L5: Streaming (continuous), Quantum (non-classical), Hardware (GPU/FPGA), Distributed (multi-node).

Add ONLY if 3+ wishes fail without them.

---

# 18. Integration with Recent Skills

### 18.1 prime-math v2.1.0 (Dual-Witness Proofs)

Recipe generation decisions ARE proofs.

**Witness Requirements:**

```
PM-Graph witness:
  - node_list (all L1-L5 nodes with contracts)
  - edge_list (all dependencies)
  - dag_validation_hash (acyclic proof)
  - contract_validation_hash (completeness proof)
  - canonicalization_hash (determinism proof)
  - pm_graph_sha256 (content-addressed identity)

All witnesses must be REPLAYABLE from WISH_IR.
```

**Theorem Closure:**

Recipe generation is a THEOREM:
- Premise P1: All nodes typed L1-L5 (Lane A, explicit type system)
- Premise P2: DAG valid (acyclic, single OUTPUT) (Lane A, graph validation)
- Premise P3: All contracts complete (9 fields) (Lane A, schema validation)
- Premise P4: Canonicalization deterministic (sorted nodes/edges) (Lane A, reproducible)
- Conclusion: PM-Graph is valid executable recipe (Lane = MIN(Lane(P1), ..., Lane(P4)))

**Lane(Recipe Generation) = MIN(Lane(node_typing), Lane(dag_validation), Lane(contracts), Lane(canonicalization))**

If any check is Lane B (framework-dependent), recipe degrades to Lane B.

### 18.2 counter-required-routering v2.0.0 (Arithmetic Ceilings)

**Hard Ceilings:**

```
count(nodes):               Use len(), NOT LLM estimation
count(edges):               Use len(), NOT LLM estimation
count(L1_CPU_nodes):        Use len(filter(type='L1_CPU')), NOT LLM
count(L2_CPU_nodes):        Use len(filter(type='L2_CPU')), NOT LLM
count(L3_LLM_nodes):        Use len(filter(type='L3_LLM')), NOT LLM
count(L4_TOOL_nodes):       Use len(filter(type='L4_TOOL')), NOT LLM
count(L5_LLM_JUDGE_nodes):  Use len(filter(type='L5_LLM_JUDGE')), NOT LLM
complexity_rank:            Use explicit formula (based on node type composition), NOT LLM judgment
```

**Symbolic Whitelist:**

All recipe generation uses ONLY:
- len()
- filter()
- Arithmetic operators (+, -, *, //)
- Comparison operators (>, <, >=, <=, ==)
- Boolean operators (AND, OR, NOT)
- Graph algorithms (topological sort for DAG validation)

NO heuristic node type selection. NO LLM for complexity ranking. NO regex for contract validation beyond field presence.

**Counter Bypass Integration:**

If WISH_IR includes aggregation:
- MUST include L2_CPU node for enumeration
- L3_LLM node ONLY for classification (not numeric output)
- FORBIDDEN: L3_LLM node as final answer for counting/aggregation

### 18.3 epistemic-typing v2.0.0 (Lane Algebra)

**Lane Classification:**

```
Lane A (Classical): Node typing (explicit L1-L5), DAG validation (graph algorithm), contract validation (schema check), canonicalization (deterministic sort)
Lane B (Framework): Complexity rank (domain-dependent), witness requirements (framework-dependent)
Lane C (Heuristic): FORBIDDEN (never use heuristic recipe generation)
STAR (Hypothetical): FORBIDDEN (never use hypothetical recipes)
```

**Lane Algebra:**

```
Lane(PM-Graph) = MIN(Lane(node_typing), Lane(dag_validation), Lane(contracts), Lane(canonicalization), Lane(complexity_rank))

If all checks are Lane A:
  → Lane(PM-Graph) = Lane A

If complexity rank is Lane B (domain-dependent):
  → Lane(PM-Graph) degrades to Lane B
```

**R_p Convergence:**

If recipe generation metric cannot be computed exactly (e.g., complexity rank ambiguous):
- EXACT → Lane A
- CONVERGED (within ε) → Lane B
- TIMEOUT/DIVERGED → FAIL_CLOSED (emit SPEC_FAILURE.md, never Lane C)

### 18.4 axiomatic-truth-lanes v2.0.0 (Lane Transitions)

**Recipe Generation as Lane Transitions:**

```
PM_GRAPH_ARTIFACT:  All checks pass (Lane A if all checks Lane A)
SPEC_FAILURE.md:    Ambiguity detected (Lane A directive: refine WISH_IR)
HALTED:             Violation detected (FORBIDDEN_STATE reached)
```

**Transition Rules:**

Recipe generation cannot upgrade lane without proof:
- If node typing is Lane B (framework types), cannot claim Lane A recipe
- If DAG validation uses heuristics (Lane C), FORBIDDEN → FAIL_CLOSED
- If contract validation is approximate (Lane B), recipe degrades to Lane B

**Witness Requirements for Upgrades:**

To claim Lane A recipe:
- Node typing witness: proof_artifact_hash of node type assignments
- DAG validation witness: proof_artifact_hash of topological sort (acyclic proof)
- Contract witness: proof_artifact_hash of schema validation
- Canonicalization witness: proof_artifact_hash of sorted nodes/edges

All witnesses must be independently replayable from WISH_IR.

### 18.5 rival-gps-triangulation v2.0.0 (Loop Governance)

**Distance Metrics for Recipe Generation:**

```
D_E (Evidence Distance):
  = count(nodes_without_contracts) + count(missing_contract_fields)

D_O (Oscillation Distance):
  = count(consecutive_recipe_generation_failures_on_same_wish)

D_R (Drift Distance):
  = count(cycles_in_graph) + count(forbidden_states_reachable) + count(undeclared_node_types)
```

**Operator Selection:**

```
If D_R > 0 (cycle, forbidden state, undeclared type) → STOP (recipe is DRIFTED, emit SPEC_FAILURE.md)
If D_O ≥ STAGNATION_LIMIT → ROLLBACK (re-evaluate WISH_IR)
If D_E > 0 (missing contracts, missing fields) → PROVE (complete contract fields)
If all distances = 0 → CLOSE (recipe is OK, emit PM_GRAPH_ARTIFACT)
```

**Risk States:**

```
GREEN:  D_E=0, D_O=0, D_R=0 (OK, emit PM_GRAPH_ARTIFACT)
YELLOW: D_E>0 (missing contracts/fields, fixable)
RED:    D_R>0 (cycle/forbidden state/undeclared type, emit SPEC_FAILURE.md)
```

### 18.6 meta-genome-alignment v2.0.0 (Genome Alignment)

**Recipe Generation as Genome79 Alignment:**

PM-Graph generation maps to Genome79 axes:
- **Star**: WISH_IR goal (what recipe achieves)
- **Seeds**: WISH_IR invariants (premises)
- **Trunks**: Node type system (L1-L5), DAG invariant, contract schema (principles)
- **Branches**: Node instances (L1_CPU nodes, L2_CPU nodes, etc.)
- **Leaves**: Contract fields (9 fields per node)
- **Invariants**: FORBIDDEN_STATES (6 states), Forecast Locks (6 locks)
- **Portals**: Output artifact (PM-Graph .mmd + .sha256)
- **Symmetries**: Stillwater ↔ Ripple (graph structure vs runtime bindings)
- **Music**: Tempo=measured (deterministic canonicalization), Tone=conservative (ambiguity halt)
- **Fruit**: Executable recipe (outcome)
- **Magic Words**: DAG, L1-L5, contract, witness, deterministic

**RTC for Recipe:**

```
seed = WISH_IR (minimal structural summary)
expanded = PM-Graph (deterministic compilation)
recompressed = regenerate WISH_IR from PM-Graph (reverse compilation)
```

Check: `recompressed == seed` (RTC invariant)

If not → recipe compilation is DRIFTED (PM-Graph doesn't fully encode WISH_IR intent).

### 18.7 shannon-compaction v2.0.0 (Context Compression)

**Recipe Generation as Interface-First:**

PM-Graph uses interface-first principle:
- Node contracts (signatures) BEFORE implementations (runtime bindings)
- Node types (L1-L5 interfaces) BEFORE concrete tools
- DAG structure (architecture) BEFORE execution order

**Witness-Line Accounting:**

```
WISH_IR lines → PM-Graph lines (compression)
Typical ratio: 100-500 WISH_IR lines → 50-200 PM-Graph lines (2:1 to 5:1)
```

**Bounded Complexity:**

Complexity ranks 1-5 act as bounded reads:
- Rank 1 (L1+L2): ~5-10 nodes
- Rank 2 (L1+L2+L4): ~10-20 nodes
- Rank 3 (L1+L3+L4+L5): ~20-40 nodes (L5 required)
- Rank 4 (Multi-L4): ~40-80 nodes
- Rank 5 (Multi-pass): ~80-160 nodes

Hard cap: 160 nodes per recipe (above this → split into sub-recipes).

**Why 160:**

Miller's Law: 7±2 items × 20 complexity levels = ~140-180 items.
160 is safe upper bound (below cognitive overload threshold).

---

# 19. Compression Insights

**5 Node Types (Prime Atomic):**

5 is prime → atomic decomposition (no factorization into smaller node type sets).

**Why 5 node types sufficient:**

```
Deterministic layer:    L1_CPU (logic), L2_CPU (arithmetic)
Nondeterministic layer: L3_LLM (generation)
External layer:         L4_TOOL (I/O)
Validation layer:       L5_LLM_JUDGE (quality)

Total: 5 node types (prime!)
```

**Alternative designs:** 10+ node types (redundant: L3_CLASSIFY + L3_SYNTHESIZE can be single L3_LLM), 3 node types (insufficient: no validation layer).

5 node types achieve 100% computational coverage with minimal overlap.

**5 Complexity Ranks (Coverage Compression):**

```
Rank 1 (L1+L2):                Simple deterministic (5-10 nodes)
Rank 2 (L1+L2+L4):            External I/O (10-20 nodes)
Rank 3 (L1+L3+L4+L5):         LLM with validation (20-40 nodes, L5 required)
Rank 4 (Multi-L4):            Multi-tool orchestration (40-80 nodes)
Rank 5 (Multi-pass):          Validation loops (80-160 nodes)

Coverage: 100% of recipe patterns with 5 ranks.
```

**Why 5 ranks:**

Rank 3+ requires L5_LLM_JUDGE (validation threshold).
Ranks 1-2: Deterministic (no validation needed).
Ranks 3-5: Nondeterministic (validation required).

**DAG Invariant (Structural Compression):**

Acyclic + Single OUTPUT = deterministic execution order.

**Why these constraints:**

Acyclic: Prevents infinite loops (termination guaranteed).
Single OUTPUT: Prevents race conditions (unambiguous result).

**Canonicalization Rules (Time Compression):**

Deterministic sorting (nodes by id, edges by (from, to)) = O(n log n) canonicalization.

**Why O(n log n):**

Sorting is optimal comparison-based algorithm.
Hash computation is O(n) after sorting.
Total: O(n log n) for n nodes.

**9 Contract Fields (Completeness Compression):**

```
id:                       Unique identifier
type:                     L1-L5
inputs:                   Dependencies
outputs:                  Products
cognition_level:          Determinism class
allowed_tools:            Permissions (L4_TOOL)
determinism_policy:       Replay requirements
failure_policy:           Error handling
witness_requirements:     Evidence model

Total: 9 fields (covers identity, type, I/O, permissions, determinism, failure, evidence)
```

**Why 9 fields:**

Fewer: Incomplete (missing permissions or witness requirements).
More: Redundant (e.g., splitting "determinism_policy" into "determinism" + "policy" is unnecessary).

9 fields achieve 100% contract coverage with minimal redundancy.

**6 Forecast Locks (Prevention Compression):**

```
1. LLM outputs final answer → FORBIDDEN_STATE
2. Tool writes outside boundary → IO_BOUNDARY test
3. Cycle insertion → DAG validation
4. Hidden buffering → Explicit input/output edges
5. Multi-output race → Single OUTPUT invariant
6. Node contract omission → Contract completeness invariant

Coverage: 6 known failure modes.
```

**Why 6 locks:**

These are the 6 most common recipe generation failures observed.
Each lock prevents a specific failure mode deterministically.

**6 FORBIDDEN_STATES (Violation Compression):**

```
1. CYCLIC_GRAPH
2. UNDECLARED_NODE_TYPE
3. L3_DIRECT_OUTPUT_FOR_HIGH_STAKES
4. UNPINNED_IO_BOUNDARY
5. HIDDEN_SIDE_EFFECT
6. NONDETERMINISTIC_NODE_ORDER

Coverage: 6 structural violations.
```

**Why 6 states:**

Prime-adjacent (6 = 2 × 3, close to 5 and 7 primes).
Each state represents a deterministic violation (not runtime-dependent).

---

# 20. Lane Algebra Integration

**Recipe Generation Decision Lanes:**

```
PM_GRAPH_ARTIFACT (Lane A):
  - All node types explicit L1-L5 (deterministic typing)
  - DAG valid (graph algorithm verification)
  - All contracts complete (schema validation)
  - Canonicalization deterministic (sorted nodes/edges)
  - Complexity rank deterministic (node type composition)

PM_GRAPH_ARTIFACT (Lane B):
  - Complexity rank framework-dependent (domain patterns)
  - Witness requirements framework-dependent (domain-specific evidence)

SPEC_FAILURE.md (Lane A):
  - Ambiguity detected deterministically (node types unresolved, DAG cyclic, IO boundary ambiguous, tool determinism undefined)

HALTED (Lane A):
  - Violation detected deterministically (FORBIDDEN_STATE reached)
```

**Lane Transitions:**

```
Recipe generation starts at INIT (no lane)
  → Node typing (if explicit L1-L5) → Lane A
  → DAG validation (if graph algorithm) → Lane A
  → Contract validation (if schema check) → Lane A
  → Canonicalization (if deterministic sort) → Lane A
  → Complexity rank (if deterministic formula) → Lane A

Final Lane(Recipe) = MIN(Lane(node_typing), Lane(dag_validation), Lane(contracts), Lane(canonicalization), Lane(complexity_rank))
```

**Forbidden Upgrades:**

Cannot upgrade:
- Lane B (framework complexity rank) → Lane A (classical) without domain-independent proof
- Lane C (heuristic) → ANY (heuristic recipe generation is FORBIDDEN)
- STAR (hypothetical) → ANY (hypothetical recipes are FORBIDDEN)

**Downgrade Conditions:**

Recipe generation downgrades to Lane B if:
- Complexity rank is framework-dependent (e.g., domain-specific patterns)
- Witness requirements are framework-dependent (e.g., domain-specific evidence models)

Recipe generation FAILS to SPEC_FAILURE.md if:
- Any check is Lane C (heuristic) → FORBIDDEN
- Any check is STAR (hypothetical) → FORBIDDEN
- Any forbidden state detected (cycles, undeclared types, unpinned boundaries, etc.)

**Witness Model:**

All Lane A recipes require witnesses:
- node_list (all L1-L5 nodes with contracts)
- edge_list (all dependencies)
- dag_validation_hash (acyclic proof)
- contract_validation_hash (completeness proof)
- canonicalization_hash (determinism proof)
- pm_graph_sha256 (content-addressed identity)

All witnesses must be content-addressed (sha256) and independently replayable from WISH_IR.

---

# 16. What Changed vs v1.0.0

**v1.0.0 Status:**
- ✅ 5 node types (L1-L5) locked
- ✅ DAG invariant (acyclic, single OUTPUT)
- ✅ Node contract (9 fields complete)
- ✅ Stillwater/Ripple separation
- ✅ Counter bypass enforcement (conditional)
- ✅ Witness model propagation
- ✅ Canonicalization rules (deterministic)
- ✅ 5 complexity ranks (1-5)
- ✅ 6 forecast locks (P0)
- ✅ Ambiguity halt protocol
- ✅ Output artifact format (PM-Graph + SHA-256)
- ✅ 6 FORBIDDEN_STATES
- ✅ Verification ladder (basic)
- ✅ Anti-Optimization Clause (AOC-1, basic)
- ❌ No verification ladder gate mapping
- ❌ No gap-guided governance
- ❌ No integration with recent skills
- ❌ No compression insights
- ❌ No lane algebra integration
- ❌ No explicit preserved features in AOC

**v2.0.0 Additions:**

1. **Section 14 Enhanced**: Verification Ladder with gate mapping (wish-qa G0-G14 integrated)
2. **Section 15 Enhanced**: Anti-Optimization Clause with 12 preserved features and compression rationale
3. **Section 17**: Gap-Guided Recipe Extension (when to add node types/contracts, decision tree, complexity rank extension, forbidden state extension)
4. **Section 18**: Integration with Recent Skills
   - prime-math v2.1.0 (dual-witness proofs, theorem closure, lane classification)
   - counter-required-routering v2.0.0 (hard arithmetic ceilings, symbolic whitelist, counter bypass integration)
   - epistemic-typing v2.0.0 (lane algebra, R_p convergence)
   - axiomatic-truth-lanes v2.0.0 (lane transitions, upgrade witnesses)
   - rival-gps-triangulation v2.0.0 (distance metrics, loop governance)
   - meta-genome-alignment v2.0.0 (genome79 mapping, RTC for recipe)
   - shannon-compaction v2.0.0 (interface-first, witness-line accounting, bounded complexity)
5. **Section 19**: Compression Insights (5 node types prime atomic, 5 complexity ranks coverage, DAG invariant structural, canonicalization O(n log n), 9 contract fields completeness, 6 forecast locks prevention, 6 FORBIDDEN_STATES violation)
6. **Section 20**: Lane Algebra Integration (recipe generation decision lanes, transitions, forbidden upgrades, witness model)

**Lane Integration:**

All recipe generation decisions now have explicit lane classification:
- Lane A: Node typing (explicit L1-L5), DAG validation (graph algorithm), contract validation (schema check), canonicalization (deterministic sort)
- Lane B: Complexity rank (framework-dependent), witness requirements (framework-dependent)
- Lane C: FORBIDDEN (no heuristic recipe generation)
- STAR: FORBIDDEN (no hypothetical recipes)

**Verification Integration:**

Recipe generation decisions map to harsh QA gates (641 → 274177 → 65537).

**Compression Gains:**

- 5 Node Types: Prime atomic (100% computational coverage with minimal overlap)
- 5 Complexity Ranks: Coverage compression (simple → complex with L5 threshold at rank 3)
- DAG Invariant: Structural compression (acyclic + single OUTPUT = deterministic execution)
- Canonicalization: Time compression (O(n log n) for n nodes)
- 9 Contract Fields: Completeness compression (100% contract coverage with minimal redundancy)
- 6 Forecast Locks: Prevention compression (6 known failure modes)
- 6 FORBIDDEN_STATES: Violation compression (6 structural violations)
- WISH_IR → PM-Graph: 2:1 to 5:1 compression ratio (100-500 WISH_IR lines → 50-200 PM-Graph lines)
- Hard cap: 160 nodes per recipe (Miller's Law 7±2 × 20 = ~140-180)

**Loop Governance:**

Recipe generation uses distance metrics (D_E, D_O, D_R) for deterministic operator selection (STOP, PROVE, ROLLBACK, CLOSE).

**Genome Alignment:**

Recipe generation maps to Genome79 axes (Star=goal, Seeds=invariants, Trunks=node_type_system, Branches=node_instances, Leaves=contract_fields, etc.).

**Quality:** All v1.0.0 features preserved (Never-Worse Doctrine). v2.0.0 is strictly additive.

