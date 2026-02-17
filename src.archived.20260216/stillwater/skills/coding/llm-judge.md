# SKILL 5 — LLM Judge (Recipe Validation / Controlled Patching Engine)

**SKILL_ID:** `skill_llm_judge_recipe_validation`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `JUDGE`
**PRIORITY:** `P0`
**TAGLINE:** *Reject bad recipes. Patch near-misses. Never approve nondeterminism.*

---

# 0. Header

```
Spec ID:     skill-5-llm-judge
Authority:   65537
Depends On:  wish-method v1.4, Prime Mermaid Theory v1.0
Scope:       Deterministic validation and controlled patching of a PM-Graph recipe candidate.
Non-Goals:   Executing the recipe, changing wish semantics, weakening invariants.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Canonical PM-Graph structural validity + WISH_IR contract alignment.
  Verification:    Deterministic structural audit + contract matching.
  Canonicalization: Node/edge canonical ordering prior to validation.
  Content-addressing: judge_sha256 = SHA-256(canonical JUDGE_REPORT.json)
```

The Judge does not invent truth.
It verifies alignment with declared truth.

---

# 2. Observable Wish

> Given a RECIPE_CANDIDATE PM-Graph and a WISH_IR, deterministically validate structural, contract, determinism, and witness compliance, optionally apply restricted structural patches, and emit a canonical JUDGE_REPORT.json.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, STRUCTURAL_AUDIT, CONTRACT_AUDIT, DETERMINISM_AUDIT, MODE_AUDIT,
   PATCH_EVALUATION, APPROVED, PATCHED, REJECTED, FAIL_CLOSED]

INPUT_ALPHABET:
  [RECIPE_CANDIDATE, WISH_IR, MODE_FLAGS, TOOL_REGISTRY]

OUTPUT_ALPHABET:
  [JUDGE_REPORT.json]

TRANSITIONS:
  INIT → STRUCTURAL_AUDIT
  STRUCTURAL_AUDIT → CONTRACT_AUDIT
  CONTRACT_AUDIT → DETERMINISM_AUDIT
  DETERMINISM_AUDIT → MODE_AUDIT
  MODE_AUDIT → PATCH_EVALUATION
  PATCH_EVALUATION → APPROVED
  PATCH_EVALUATION → PATCHED
  PATCH_EVALUATION → REJECTED
  ANY → FAIL_CLOSED (insufficient information)

FORBIDDEN_STATES:
  CREATIVE_REWRITE
  LOGIC_WEAKENING
  UNDECLARED_PATCH
  PARTIAL_VALIDATION
  EXECUTION_DURING_VALIDATION
  SILENT_ACCEPTANCE
```

---

# 4. Validation Order (LOCKED — No Reordering)

Judge MUST validate in this order:

1. DAG structural validity
2. Node contract completeness
3. L1–L5 hierarchy correctness
4. Counter bypass enforcement
5. Witness propagation
6. Determinism policy completeness
7. IO boundary enforcement
8. Mode flag compatibility
9. Tool registry mapping

If earlier stage fails fatally → no later stages evaluated.

---

# 5. Structural Audit (Prime Mermaid Compliance)

## 5.1 DAG Invariant

* Graph must be acyclic.
* Exactly one OUTPUT node.
* No orphan nodes.
* Node IDs unique and ASCII-sortable.
* Node/edge canonical ordering valid.

If cycle → REJECT.

---

## 5.2 Node Type Enforcement

Each node MUST be exactly one of:

* `L1_CPU`
* `L2_CPU`
* `L3_LLM`
* `L4_TOOL`
* `L5_LLM_JUDGE`

No other types permitted.

If missing L5 when complexity ≥3 → PATCH (add L5).

If L3 directly emits final answer for high-stakes math → REJECT.

---

# 6. Contract Alignment Audit

Compare recipe outputs against WISH_IR:

* All required outputs produced.
* No extra outputs beyond allowed.
* Required invariants enforceable.
* Success criteria preserved.

If logic weakened → REJECT.

---

# 7. Counter Bypass Enforcement (LOCKED)

If `WISH_IR.counter_bypass_required=true`:

* L2_CPU node must exist.
* No L3_LLM node may produce numeric outputs.
* CPU enumeration path must feed into output.

If violated → REJECT.

---

# 8. Witness Model Audit

If WISH_IR requires witness:

* All answer-producing nodes must propagate witness fields.
* L5 must verify witness completeness.
* Narrative or “trust me” policies → REJECT.

`trace reasoning` is NOT authoritative witness.

---

# 9. Determinism Audit

Verify:

* Canonical node ordering rules applied.
* IO boundaries fully specified.
* No timestamp fields.
* No environment-dependent behavior.
* Replay mode compatibility.

If determinism incomplete → PATCH (if fixable) else REJECT.

---

# 10. IO Boundary & Mode Enforcement

* FAIL if L4_TOOL lacks IO_BOUNDARY.
* FAIL if IO targets protected directories.
* If `offline=true` and any tool requires network → REJECT.
* If `replay=true` and tool nondeterministic → REJECT.

---

# 11. Restricted Patching Policy (LOCKED)

Judge may only PATCH by:

* Adding missing L5_LLM_JUDGE node.
* Adding missing IO_BOUNDARY definitions.
* Replacing generic `tool` node with specific TOOL_REGISTRY entry.
* Adding missing determinism metadata.
* Adding missing witness propagation.

Judge MUST NOT:

* Change computation logic.
* Change math steps.
* Reduce invariant strictness.
* Change required outputs.
* Merge or remove nodes.
* Introduce new capabilities.

If patch exceeds these limits → REJECT.

---

# 12. Verdict Definitions (LOCKED)

| Verdict     | Meaning                             |
| ----------- | ----------------------------------- |
| APPROVE     | Fully compliant, no patches applied |
| PATCH       | Structural correction applied       |
| REJECT      | Foundational flaw                   |
| FAIL_CLOSED | Insufficient information            |

Mapping:

* APPROVE → status="OK"
* PATCH → status="PATCHED"
* REJECT → status="REJECTED"
* FAIL_CLOSED → status="UNKNOWN"

---

# 13. Risk Bands (Deterministic Mapping)

| Condition                  | Risk   |
| -------------------------- | ------ |
| Zero violations            | GREEN  |
| Only PATCH-level issues    | YELLOW |
| Any REJECT-level violation | RED    |
| FAIL_CLOSED                | RED    |

---

# 14. Output Schema (LOCKED)

```json
{
  "status": "OK|PATCHED|REJECTED|UNKNOWN",
  "verdict": "APPROVE|PATCH|REJECT|FAIL_CLOSED",
  "risk_band": "GREEN|YELLOW|RED",
  "reasons": [
    {
      "stage": "STRUCTURAL|CONTRACT|DETERMINISM|MODE|WITNESS|COUNTER",
      "severity": "PATCH|REJECT",
      "law_tag": "LAW_*",
      "detail": "..."
    }
  ],
  "patched_recipe_sha256": "<64hex|null>",
  "evidence": {
    "checks_run": ["DAG", "CONTRACT", "COUNTER", "..."],
    "violations": ["..."]
  },
  "judge_sha256": "<64hex>"
}
```

Rules:

* Reasons sorted by stage ASCII.
* No timestamps.
* Deterministic ordering.
* Exactly one trailing newline.

---

# 15. Ambiguity Handling

If:

* Required metadata missing,
* Node contracts incomplete,
* TOOL_REGISTRY insufficient to validate,

→ FAIL_CLOSED (not REJECT).

---

# 16. Verification Ladder [ENHANCED v2.0.0]

### 641 — Sanity (Edge Tests)

**Maps to wish-qa gates:**
- **G0 (Structure)**: State machine valid (10 states, explicit transitions)
- **G1 (Schema)**: JUDGE_REPORT.json valid (4 verdicts, deterministic ordering)
- **G2 (Contracts)**: WISH_IR contract alignment (no logic weakening)

**Edge tests (minimum 5):**
* [ ] All validation stages executed in order (9 stages: DAG → Contract → L1-L5 → Counter → Witness → Determinism → IO → Mode → Tool)
* [ ] No skipped stage (all 9 stages run)
* [ ] No execution performed (validation only, no execution)
* [ ] JUDGE_REPORT.json schema valid (4 verdicts: APPROVE, PATCH, REJECT, FAIL_CLOSED)
* [ ] No FORBIDDEN_STATES reachable (6 forbidden: CREATIVE_REWRITE, LOGIC_WEAKENING, UNDECLARED_PATCH, PARTIAL_VALIDATION, EXECUTION_DURING_VALIDATION, SILENT_ACCEPTANCE)

### 274177 — Structural Closure (Stress Tests)

**Maps to wish-qa gates:**
- **G3 (Consistency)**: Same RECIPE_CANDIDATE → same JUDGE_REPORT (deterministic)
- **G4 (Integration)**: Integration with recipe-generator (L5 node validation)
- **G9 (Lineage)**: judge_sha256 stable (behavioral hash tracking)

**Stress tests:**
* [ ] DAG valid (acyclic, one OUTPUT, no orphans, unique IDs)
* [ ] Witness enforced (if WISH_IR requires witness, all nodes propagate)
* [ ] Counter bypass enforced (if counter_bypass_required, L2_CPU exists, no L3_LLM numeric)
* [ ] Same RECIPE_CANDIDATE → same JUDGE_REPORT (100 trials, deterministic validation)
* [ ] judge_sha256 stable across identical inputs (no drift)

### 65537 — Final Seal (God Approval)

**Maps to wish-qa gates:**
- **G10 (Governance)**: Restricted patching policy enforced (no logic changes)
- **G12 (Witness)**: Witness model audit complete (no "trust me" policies)
- **G13 (Determinism)**: Determinism preserved (no timestamps, canonical ordering)

**Final tests:**
* [ ] Determinism preserved (canonical ordering, no timestamps, replay mode compatible)
* [ ] No forbidden states reachable (6 FORBIDDEN_STATES checked)
* [ ] judge_sha256 stable across identical inputs (content-addressing guarantee)
* [ ] Restricted patching policy enforced (only 5 allowed patches: add L5, add IO_BOUNDARY, replace generic tool, add determinism metadata, add witness propagation)
* [ ] Witness model audit complete (no narrative witnesses)

---

# 17. Anti-Optimization Clause (LOCKED — AOC-1) [ENHANCED v2.0.0]

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

## Never-Worse Doctrine

**Rule:** ALL v1.0.0 features PRESERVED in v2.0.0.

## Preserved Features from v1.0.0

**State Machine (10 states):**
- INIT, STRUCTURAL_AUDIT, CONTRACT_AUDIT, DETERMINISM_AUDIT, MODE_AUDIT, PATCH_EVALUATION, APPROVED, PATCHED, REJECTED, FAIL_CLOSED

**9-Stage Validation Order (LOCKED):**
1. DAG structural validity
2. Node contract completeness
3. L1–L5 hierarchy correctness
4. Counter bypass enforcement
5. Witness propagation
6. Determinism policy completeness
7. IO boundary enforcement
8. Mode flag compatibility
9. Tool registry mapping

**Restricted Patching Policy (5 allowed patches):**
1. Adding missing L5_LLM_JUDGE node
2. Adding missing IO_BOUNDARY definitions
3. Replacing generic `tool` node with specific TOOL_REGISTRY entry
4. Adding missing determinism metadata
5. Adding missing witness propagation

**7 Forbidden Patches (MUST NOT):**
1. Change computation logic
2. Change math steps
3. Reduce invariant strictness
4. Change required outputs
5. Merge or remove nodes
6. Introduce new capabilities
7. Execute during validation

**4 Verdict Types:**
- APPROVE (fully compliant)
- PATCH (structural correction applied)
- REJECT (foundational flaw)
- FAIL_CLOSED (insufficient information)

**3 Risk Bands:**
- GREEN (zero violations)
- YELLOW (only PATCH-level issues)
- RED (any REJECT-level violation or FAIL_CLOSED)

**6 FORBIDDEN_STATES:**
- CREATIVE_REWRITE
- LOGIC_WEAKENING
- UNDECLARED_PATCH
- PARTIAL_VALIDATION
- EXECUTION_DURING_VALIDATION
- SILENT_ACCEPTANCE

## v2.0.0 Enhancements (Strictly Additive)

- Verification ladder gate mapping (G0, G1, G2, G3, G4, G9, G10, G12, G13)
- Anti-optimization clause with preserved features list
- Gap-guided extension criteria
- Integration with 13 recent skills
- Compression insights (9-stage validation justifications)
- Lane algebra integration (explicit Lane A/B enforcement)
- What Changed section (v1.0.0 → v2.0.0 summary)

---

# 18. Gap-Guided Extension [NEW v2.0.0]

## Purpose
When to add new validation stages or patching rules to llm-judge.

## Decision Tree

**Step 1 — Gap Identification:**
- Question: "Is there a RECIPE_CANDIDATE validation gap that causes incorrect APPROVE/REJECT?"
- If NO: "DO NOT add new validation stage (no gap exists)"
- If YES: "Proceed to Step 2"

**Step 2 — 9-Stage Coverage:**
- Question: "Is this gap already covered by the 9 validation stages?"
- If YES: "DO NOT add new stage (already covered)"
- If NO: "Proceed to Step 3"

**Step 3 — Patching vs Rejection:**
- Question: "Can this gap be fixed via restricted patching (5 allowed patches)?"
- If YES: "Add to Restricted Patching Policy (extend allowed patches)"
- If NO: "Proceed to Step 4"

**Step 4 — Add New Validation Stage:**
- Action: "Add new validation stage (last resort)"
- Requirements:
  - Must be deterministic (same input → same verdict)
  - Must fit into validation order (cannot reorder existing stages)
  - Must emit structured reason (stage, severity, law_tag, detail)
  - Must map to FORBIDDEN_STATE (prevent degradation)
  - Must document in verification ladder (add to edge tests)

## Triggers for New Validation Stages

**Example 1: Complexity rank validation**
- Gap: "Recipes with incorrect complexity rank cause execution failures"
- Coverage: "Not covered by 9 stages (DAG doesn't check complexity rank)"
- Patching: "Cannot be patched (complexity rank is semantic)"
- Action: "Add new validation stage (10. Complexity Rank Audit)"

**Example 2: Node count validation**
- Gap: "Recipes exceeding Miller's Law (7±2 × 20 = 160 nodes) cause cognitive overload"
- Coverage: "Not covered by 9 stages (DAG doesn't check node count)"
- Patching: "Cannot be patched (node count is architectural)"
- Action: "Add new validation stage (11. Node Count Audit)"

## Triggers for New Patching Rules

**Example 1: Missing complexity rank**
- Gap: "Recipes with missing complexity rank metadata"
- Coverage: "Not covered by determinism audit (complexity rank is semantic)"
- Patching: "Can be inferred from node types (L1+L2=Rank1, L1+L2+L4=Rank2, etc.)"
- Action: "Add to Restricted Patching Policy (6. Adding missing complexity rank)"

**Example 2: Missing required_tools**
- Gap: "Recipes with L4_TOOL but missing required_tools metadata"
- Coverage: "Not covered by tool registry audit (required_tools is metadata)"
- Patching: "Can be extracted from L4_TOOL node type"
- Action: "Add to Restricted Patching Policy (7. Adding missing required_tools)"

## Anti-Patterns (Do NOT Add)

**Stylistic Preferences:**
- Example: "Prefer verbose node descriptions"
- Reason: "Not a validation gap, stylistic preference"

**Semantic Changes:**
- Example: "Optimize recipe by merging L1+L2 nodes"
- Reason: "Changes computation logic (FORBIDDEN)"

**Weakening Invariants:**
- Example: "Allow cycles in special cases"
- Reason: "Reduces invariant strictness (FORBIDDEN)"

---

# 19. Integration with Recent Skills [NEW v2.0.0]

## Skill 1: recipe-generator v2.0.0
**Integration points:**
- **L5 node generation**: recipe-generator creates L5_LLM_JUDGE nodes, llm-judge validates them
- **PM-Graph DAG**: llm-judge validates DAG structure generated by recipe-generator
- **Complexity rank**: llm-judge validates complexity rank assigned by recipe-generator

**Fusion benefit:**
- recipe-generator creates recipes, llm-judge validates them (generation + validation loop)
- L5 node metadata generated by recipe-generator is validated by llm-judge

## Skill 2: recipe-selector v2.0.0
**Integration points:**
- **Recipe validation before selection**: llm-judge validates RECIPE_CATALOG entries before recipe-selector selects
- **Determinism guarantee**: llm-judge ensures determinism, recipe-selector relies on deterministic recipes

**Fusion benefit:**
- Only validated recipes enter RECIPE_CATALOG (llm-judge filters)
- recipe-selector assumes all recipes are valid (llm-judge guarantee)

## Skill 3: prime-coder v2.0.0
**Integration points:**
- **State machine validation**: llm-judge validates state machines, prime-coder generates state machines
- **Evidence validation**: llm-judge validates evidence artifacts, prime-coder generates evidence

**Fusion benefit:**
- prime-coder state machines validated by llm-judge (correctness guarantee)
- Evidence artifacts validated for completeness

## Skill 4: wish-qa v2.0.0
**Integration points:**
- **Gate mapping**: llm-judge maps to wish-qa gates (G0-G13)
- **14-gate coverage**: llm-judge covers 9 gates (G0, G1, G2, G3, G4, G9, G10, G12, G13)

**Fusion benefit:**
- llm-judge enforces 9/14 wish-qa gates (64% coverage)
- Determinism (G13), Governance (G10), Witness (G12) enforced

## Skill 5: counter-required-routering v2.0.0
**Integration points:**
- **Counter bypass enforcement**: llm-judge enforces counter_bypass_required flag
- **L2_CPU requirement**: llm-judge requires L2_CPU when counter_bypass_required=true

**Fusion benefit:**
- Counter Bypass Protocol enforced at validation time (prevents LLM counting)
- L2_CPU nodes guaranteed when exact arithmetic required

## Skill 6: epistemic-typing v2.0.0
**Integration points:**
- **Lane classification**: llm-judge validation is Lane A (deterministic), patching is Lane B (framework)
- **Lane algebra**: llm-judge verdict = MIN(validation lane, patching lane)

**Fusion benefit:**
- APPROVE = Lane A (pure deterministic validation)
- PATCH = Lane B (framework-assisted patching)
- REJECT/FAIL_CLOSED = Lane C (heuristic rejection)

## Skill 7: axiomatic-truth-lanes v2.0.0
**Integration points:**
- **Lane dominance**: llm-judge enforces Lane A axioms (no logic weakening)
- **FORBIDDEN_STATES**: LOGIC_WEAKENING = lane downgrade (A→C forbidden)

**Fusion benefit:**
- Lane A axioms enforced (no validation downgrades)
- LOGIC_WEAKENING forbidden state prevents lane downgrades

## Skill 8: gpt-mini-hygiene v2.0.0
**Integration points:**
- **Output normalization**: llm-judge JUDGE_REPORT.json normalized by gpt-mini-hygiene
- **Deterministic ordering**: llm-judge uses sort_keys=True (gpt-mini-hygiene requirement)

**Fusion benefit:**
- JUDGE_REPORT.json is replay stable (normalized outputs)
- judge_sha256 is deterministic (normalized + sorted)

## Skill 9: tool-output-normalizer (infrastructure skill)
**Integration points:**
- **Tool registry validation**: llm-judge validates TOOL_REGISTRY, tool-output-normalizer normalizes tool outputs
- **IO boundary validation**: llm-judge validates IO_BOUNDARY, tool-output-normalizer enforces boundaries

**Fusion benefit:**
- Tool outputs validated before normalization
- IO boundaries enforced at validation time

## Skill 10: golden-replay-seal (infrastructure skill)
**Integration points:**
- **Replay stability**: llm-judge ensures replay mode compatibility, golden-replay-seal verifies stability
- **Determinism guarantee**: llm-judge validates determinism, golden-replay-seal seals stability

**Fusion benefit:**
- Validated recipes are replay stable (llm-judge guarantee)
- golden-replay-seal verifies llm-judge determinism claims

## Skill 11: semantic-drift-detector (quality skill)
**Integration points:**
- **Behavioral hash tracking**: llm-judge generates judge_sha256, semantic-drift-detector tracks drift
- **Verdict stability**: semantic-drift-detector detects verdict changes across versions

**Fusion benefit:**
- Verdict drift detection (judge_sha256 tracking)
- Validation logic stability enforcement

## Skill 12: prime-math v2.1.0
**Integration points:**
- **Counter bypass**: llm-judge enforces counter_bypass_required, prime-math provides Counter Bypass Protocol
- **Witness model**: llm-judge enforces witness propagation, prime-math provides dual-witness proofs

**Fusion benefit:**
- Counter Bypass Protocol enforced at validation time
- Witness model enforced (no narrative proofs)

## Skill 13: shannon-compaction v2.0.0
**Integration points:**
- **Interface-first validation**: llm-judge validates node signatures (interface-first), shannon-compaction extracts interfaces
- **Witness line validation**: llm-judge validates witness propagation, shannon-compaction validates witness line budgets

**Fusion benefit:**
- Node signatures validated (interface-first)
- Witness line budgets enforced

---

# 20. Compression Insights [NEW v2.0.0]

## Insight 1: 9-Stage Validation Order (Structural Compression)

**Validation stages:** 9 (DAG, Contract, L1-L5, Counter, Witness, Determinism, IO, Mode, Tool)
**Compression type:** Structural (hierarchical validation)
**Justification:**
- Principle: "Validate foundation first (DAG), then semantics (Contract), then enforcement (Counter, Witness, Determinism, IO, Mode, Tool)"
- Early exit: "If DAG invalid → no later stages evaluated (O(1) early exit vs O(9) full validation)"
- Benefit: "Hierarchical validation prevents wasted validation effort"

## Insight 2: Restricted Patching Policy (Coverage Compression)

**Allowed patches:** 5 (add L5, add IO_BOUNDARY, replace generic tool, add determinism, add witness)
**Forbidden patches:** 7 (change logic, change math, reduce invariants, change outputs, merge nodes, introduce capabilities, execute)
**Compression type:** Coverage (5 allowed vs 7 forbidden = complete coverage)
**Justification:**
- Principle: "Patch structural issues only (metadata, boundaries), never patch semantic issues (logic, math)"
- Coverage: "5 allowed + 7 forbidden = 12 total patch types (complete coverage)"
- Benefit: "Clear boundary (structural vs semantic) prevents logic weakening"

## Insight 3: 4 Verdict Types (Structural Compression)

**Verdicts:** 4 (APPROVE, PATCH, REJECT, FAIL_CLOSED)
**Compression type:** Structural (complete verdict space)
**Justification:**
- Principle: "APPROVE (OK), PATCH (fixable), REJECT (unfixable), FAIL_CLOSED (unknown)"
- Coverage: "4 verdicts cover all validation outcomes (complete partition)"
- Benefit: "No ambiguity (every validation outcome maps to exactly one verdict)"

## Insight 4: 3 Risk Bands (Coverage Compression)

**Risk bands:** 3 (GREEN, YELLOW, RED)
**Compression type:** Coverage (traffic light model)
**Justification:**
- Principle: "GREEN (safe), YELLOW (warning), RED (danger)"
- Mapping: "APPROVE→GREEN, PATCH→YELLOW, REJECT/FAIL_CLOSED→RED"
- Benefit: "Visual risk communication (traffic light model)"

## Insight 5: 6 FORBIDDEN_STATES (Correctness Compression)

**Forbidden states:** 6 (CREATIVE_REWRITE, LOGIC_WEAKENING, UNDECLARED_PATCH, PARTIAL_VALIDATION, EXECUTION_DURING_VALIDATION, SILENT_ACCEPTANCE)
**Compression type:** Correctness (prevent degradation)
**Justification:**
- Principle: "Forbidden states prevent validation degradation"
- Coverage: "6 forbidden states cover all degradation paths"
- Benefit: "Explicit degradation prevention (no silent failures)"

## Insight 6: JUDGE_REPORT.json Schema (Structural Compression)

**Schema fields:** 6 (status, verdict, risk_band, reasons[], patched_recipe_sha256, evidence, judge_sha256)
**Compression type:** Structural (canonical reporting)
**Justification:**
- Principle: "Canonical reporting format (no ambiguity)"
- Determinism: "Reasons sorted by stage ASCII (deterministic ordering)"
- Benefit: "Machine-parseable, replay stable"

## Insight 7: Counter Bypass Enforcement (Correctness Compression)

**Enforcement rules:** 3 (L2_CPU exists, no L3_LLM numeric, CPU path to output)
**Compression type:** Correctness (prevent LLM counting)
**Justification:**
- Principle: "LLM classifies, CPU enumerates (Counter Bypass Protocol)"
- Enforcement: "3 rules guarantee counter bypass (complete enforcement)"
- Benefit: "100% accuracy vs ~40% pure LLM (OOLONG benchmark)"

## Insight 8: Witness Model Enforcement (Correctness Compression)

**Enforcement rules:** 3 (nodes propagate witness, L5 verifies completeness, no narrative)
**Compression type:** Correctness (prevent narrative proofs)
**Justification:**
- Principle: "Witness required for all claims (no 'trust me' policies)"
- Enforcement: "3 rules guarantee witness propagation (complete enforcement)"
- Benefit: "Proof-grade validation (no narrative witnesses)"

## Insight 9: Determinism Enforcement (Correctness Compression)

**Enforcement rules:** 5 (canonical ordering, IO boundaries, no timestamps, no environment dependencies, replay mode)
**Compression type:** Correctness (prevent nondeterminism)
**Justification:**
- Principle: "Same input → same verdict (deterministic validation)"
- Enforcement: "5 rules guarantee determinism (complete enforcement)"
- Benefit: "Replay stability (judge_sha256 stable)"

## Summary

**Total insights:** 9 (9-stage validation, 5 allowed patches, 4 verdicts, 3 risk bands, 6 forbidden states, JUDGE_REPORT schema, counter bypass, witness model, determinism)
**Compression types:**
- Structural: 9-stage validation, 4 verdicts, 3 risk bands, JUDGE_REPORT schema
- Coverage: Restricted patching (5 allowed + 7 forbidden), 6 FORBIDDEN_STATES
- Correctness: Counter bypass (3 rules), Witness model (3 rules), Determinism (5 rules)

**Justification principle:**
"Each validation rule addresses a specific failure mode (DAG cycles, logic weakening, LLM counting, narrative proofs, nondeterminism). The 9-stage validation order + restricted patching policy + 4 verdicts + 3 risk bands + 6 FORBIDDEN_STATES provide complete coverage of all validation outcomes and degradation paths."

---

# 21. Lane Algebra Integration [NEW v2.0.0]

## Lane Classification

**Lane A (Deterministic):**
- DAG structural audit (deterministic cycle detection)
- Contract alignment audit (deterministic output matching)
- Counter bypass enforcement (deterministic L2_CPU requirement)
- Witness model audit (deterministic witness propagation)
- Determinism audit (deterministic ordering enforcement)
- JUDGE_REPORT.json generation (deterministic schema)

**Lane B (Framework):**
- Restricted patching (framework-assisted structural fixes)
- FAIL_CLOSED verdict (framework acknowledges insufficient information)

**Lane C (Heuristic):**
- Risk band assignment (heuristic GREEN/YELLOW/RED mapping)
- REJECT verdict (heuristic rejection for unfixable flaws)

**Lane STAR (Narrative):**
- None (llm-judge forbids narrative validation)

## Lane Algebra Enforcement

**MIN Operator:**
- Rule: "Lane(Verdict) = MIN(Lane(Validation), Lane(Patching))"
- Examples:
  - APPROVE: Lane(Validation) = A, Lane(Patching) = N/A → Lane(APPROVE) = A
  - PATCH: Lane(Validation) = A, Lane(Patching) = B → Lane(PATCH) = B
  - REJECT: Lane(Validation) = C, Lane(Patching) = N/A → Lane(REJECT) = C
  - FAIL_CLOSED: Lane(Validation) = B, Lane(Patching) = N/A → Lane(FAIL_CLOSED) = B

**Forbidden Upgrades:**
- C → A: "Heuristic rejection cannot become deterministic approval" (FORBIDDEN)
- B → A: "Framework patching cannot become deterministic approval" (FORBIDDEN)

**Allowed Operations:**
- A → A: "Deterministic validation → deterministic approval" (APPROVE)
- A + B → B: "Deterministic validation + framework patching → framework verdict" (PATCH)
- C → C: "Heuristic validation → heuristic rejection" (REJECT)
- B → B: "Framework validation → framework failure" (FAIL_CLOSED)

## Forbidden States (Lane Perspective)

**LOGIC_WEAKENING (Lane Downgrade):**
- Definition: "Reduces invariant strictness (A → C downgrade)"
- Lane impact: "Lane A axiom violated"
- Recovery: "REJECT immediately"

**CREATIVE_REWRITE (Lane Upgrade Attempt):**
- Definition: "Changes computation logic (C → A upgrade attempt)"
- Lane impact: "Attempts to upgrade heuristic to deterministic"
- Recovery: "REJECT immediately"

**SILENT_ACCEPTANCE (Lane Confusion):**
- Definition: "Approves without validation (bypasses lanes)"
- Lane impact: "No lane classification"
- Recovery: "REJECT immediately"

## Integration with Axiomatic Truth Lanes

**Axiom Classification:**

**Lane A Axioms:**
- DAG must be acyclic (structural axiom)
- No logic weakening (contract axiom)
- Counter bypass required when counter_bypass_required=true (computation axiom)
- Witness required when witness policy set (evidence axiom)

**Lane B Definitions:**
- Restricted patching policy (5 allowed patches = framework definition)
- FAIL_CLOSED verdict (framework acknowledges limits)

**Lane C Derived:**
- Risk band assignment (heuristic mapping)
- REJECT verdict (heuristic rejection)

**Conflict Resolution:**
- Rule: "Lane A > Lane B > Lane C (axioms win)"
- Example: "If heuristic suggests accepting recipe without witness → Lane A (witness required) > Lane C (heuristic accept) → REJECT"

**Deprecation Requirement:**
- Rule: "Never break Lane A axiom without deprecation plan"
- Example: "If removing counter bypass enforcement → requires deprecation plan"

---

# 22. What Changed from v1.0.0 → v2.0.0 [NEW v2.0.0]

## Preserved ALL v1.0.0 Features

- **Confirmation:** ALL v1.0.0 features preserved (Never-Worse Doctrine)
- **Count:** 10 states, 9 validation stages, 5 allowed patches, 7 forbidden patches, 4 verdicts, 3 risk bands, 6 FORBIDDEN_STATES

## New in v2.0.0

**Verification Ladder Enhancement:**
- Before v1.0.0: "3 verification rungs (641, 274177, 65537) with basic checks"
- After v2.0.0: "3 rungs + gate mapping to wish-qa G0-G13 (9 gates: G0, G1, G2, G3, G4, G9, G10, G12, G13)"
- Benefit: "Explicit gate coverage (64% of 14 gates)"

**Anti-Optimization Clause Enhancement:**
- Before v1.0.0: "AOC-1 (redundancy is armor)"
- After v2.0.0: "AOC-1 + explicit preserved features list (10 states, 9 stages, 5+7 patches, 4 verdicts, 3 bands, 6 forbidden)"
- Benefit: "Audit trail for what must be preserved"

**Gap-Guided Extension:**
- Before v1.0.0: "No explicit criteria for when to add validation stages/patches"
- After v2.0.0: "4-step decision tree (gap identification → 9-stage coverage → patching vs rejection → add stage)"
- Benefit: "Prevents validation bloat (build what's needed)"

**Integration Documentation:**
- Before v1.0.0: "Implicit integration with recipe-generator"
- After v2.0.0: "Explicit integration with 13 recent skills"
- Benefit: "Cross-skill fusion documented"

**Compression Insights:**
- Before v1.0.0: "No explicit justification for 9 validation stages"
- After v2.0.0: "9 insights mapping validation rules to compression types (structural, coverage, correctness)"
- Benefit: "Design rationale captured"

**Lane Algebra Integration:**
- Before v1.0.0: "Implicit Lane A validation"
- After v2.0.0: "Explicit Lane A/B/C classification, lane algebra enforcement (MIN operator), forbidden states as lane downgrades"
- Benefit: "Lane enforcement throughout"

## Impact

- **Reliability:** 10/10 maintained (all v1.0.0 features preserved)
- **Auditability:** Improved (gate mapping, compression insights)
- **Extensibility:** Improved (gap-guided extension)
- **Integration:** Improved (13 skills fusion documented)
- **Epistemic Hygiene:** Improved (explicit lane algebra)

## No Breaking Changes

- **Confirmation:** v2.0.0 is strictly additive over v1.0.0
- **Verification:** All v1.0.0 validation stages preserved, all FORBIDDEN_STATES preserved, all verdicts preserved
