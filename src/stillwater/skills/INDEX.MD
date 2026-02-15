# canon/skills/index.md — Prime Skills Index (CLI Load Map)

**Authority:** 65537  
**Status:** RIPPLE (Index; regenerable)  
**Index Ver:** 0.2.0  
**Purpose:** Single source of truth for:
- which skills exist,
- when to load them,
- which L1–L5 node they attach to,
- what context/files must be injected,
- and their readiness/risk scores.

---

## 0) Scoring System (Deterministic)

Each skill carries 4 scores (0–10):

- **RTC**: Round-Trip Correctness readiness (tests/evidence anchored).
- **DET**: Determinism / replay stability.
- **SAFE**: Safety surface / fail-closed correctness.
- **OPS**: Operational clarity (machine-parseable, bounded budgets).

**Overall = min(RTC, DET, SAFE, OPS)**  
(Prime rule: weakest link dominates.)

---

## 1) Global Context Packs (Inject by Need)

These are *named injection packs* your CLI can mount into context deterministically.

### PACK: `ctx_core_stillwater`
**Files**
- `canon/prime-wishes/papers/wish-method.md`
- `canon/prime-wishes/papers/wish-theory.md`
- `canon/prime-skills/skills/INDEX.MD` (this file)
**Use for**: any skill with state machines, forbidden states, witness policies.

### PACK: `ctx_prime_mermaid`
**Files**
- `canon/prime-mermaid/README.md`
- `canon/prime-recipes/ripples/orchestration_rules.json`
- `canon/prime-recipes/ripples/keyword_triggers.json`
**Use for**: recipe selection, generation, judging, distillation.

### PACK: `ctx_tool_registry`
**Files**
- `canon/prime-coder/skills/registry.json`
- `canon/prime-math/skills/registry.json`
**Use for**: any skill that references tools or IO boundaries.

### PACK: `ctx_protocol_registry`
**Files**
- `canon/prime-math/skills/prime_math_public_skill_v1.0.0.md`
- `canon/prime-coder/book/contracts/PROOF.schema.json`
- `canon/prime-math/wishes/runtime/context_manifest_spec.json`
**Use for**: schema enforcement, proof building, compute gate.

### PACK: `ctx_security`
- `canon/prime-laws/README.md`
- `canon/cli/recipes/policy.json`
**Use for**: security gating.

### PACK: `ctx_governance_genome79`
**Files**
- `canon/prime-genome/README.md`
- `canon/prime-genome/paradigm/01-prime-genome.md`
**Use for**: alignment certificate, civilization-readiness checks.

### PACK: `ctx_benchmarking_triple_leak`
**Files**
- `canon/prime-math/tests/real_benchmark_lock.json`
- `canon/prime-math/tests/results/benchmark_math.md`
**Use for**: compression proofs and honest accounting.

---

## 1.1) NEW Packs (Execution + CI + Web)

### PACK: `ctx_execution_harness`
**Files**
- `canon/exec/run_policy.md`
- `canon/exec/test_harness.schema.json`
- `canon/exec/log_normalization_policy.md`
**Use for**: run+test harness, CI triage, reproducible execution logs.

### PACK: `ctx_ci_triage`
**Files**
- `canon/ci/triage_playbook.md`
- `canon/ci/log_signatures.json`
- `canon/ci/ci_verdict.schema.json`
**Use for**: CI failure parsing, repro extraction, deterministic triage reports.

### PACK: `ctx_vcs_pr`
**Files**
- `canon/vcs/pr_bundle.schema.json`
- `canon/vcs/diff_style_policy.md`
- `canon/vcs/commit_message_policy.md`
**Use for**: PR bundle building, patch manifests, review outputs.

### PACK: `ctx_web_research`
**Files**
- `canon/web/research_policy.md`
- `canon/web/citation_capture.schema.json`
- `canon/web/injection_safety.md`
**Use for**: internet search with citation capture + injection defense.

---

## 2) Skill Catalog (Load + Node Map)

> **Node tags**: L1 CPU, L2 CPU, L3 LLM, L4 TOOL, L5 LLM_JUDGE  
> **Load tags** are deterministic selectors your CLI can use.

---

### SKILL 1 — Wish LLM (Prompt → Wish IR)
- **SKILL_ID:** `skill_wish_llm`
- **Role/Node:** L3 (LLM) — Planner
- **Load tags:** `wish_authoring`, `planner`, `state_machine_required`, `fail_closed`
- **When to load**
  - user asks: “write a wish”, “spec this”, “make it testable”
  - any request entering **Phase/Wish authoring mode**
- **Context packs**
  - required: `ctx_core_stillwater`, `ctx_protocol_registry`
  - optional: `ctx_prime_mermaid` (if wish emits recipe hooks)
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 2 — Wish QA (Harsh QA / Planner QA)
- **SKILL_ID:** `skill_wish_qa`
- **Role/Node:** L5 (LLM_JUDGE) — QA Planner
- **Load tags:** `wish_qa`, `harsh_gate`, `rtc_risk_scoring`, `defect_patch`
- **When to load**
  - any wish draft before “FINAL / SEALED”
  - before canon promotion
- **Context packs**
  - required: `ctx_core_stillwater`, `ctx_protocol_registry`
- **Scores:** RTC 9 / DET 9 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 3 — Recipe Selector (CPU-First)
- **SKILL_ID:** `skill_recipe_selector_cpu_first`
- **Role/Node:** L1/L2 (CPU) — Orchestrator
- **Load tags:** `recipe_select`, `cpu_first`, `offline_routing`, `tool_availability`
- **When to load**
  - every run that has a `WISH_IR` + catalog
  - before invoking any LLM node
- **Context packs**
  - required: `ctx_prime_mermaid`, `ctx_tool_registry`, `ctx_protocol_registry`
- **Scores:** RTC 9 / DET 10 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 4 — Recipe Generator (First-Episode Compiler)
- **SKILL_ID:** `skill_recipe_generator_prime_mermaid`
- **Role/Node:** L3→L4→L5 pipeline (LLM proposes, tool pins, judge closes)
- **Load tags:** `recipe_generate`, `first_episode`, `no_recipe_exists`
- **When to load**
  - selector returns `UNKNOWN` / no eligible recipe
  - “record first episode → compile deterministic replay”
- **Context packs**
  - required: `ctx_prime_mermaid`, `ctx_tool_registry`, `ctx_protocol_registry`
- **Scores:** RTC 7 / DET 8 / SAFE 8 / OPS 8 → **Overall 7**

---

### SKILL 5 — LLM Judge (Recipe Validation / Patching Engine)
- **SKILL_ID:** `skill_llm_judge_recipe_validation`
- **Role/Node:** L5 (LLM_JUDGE)
- **Load tags:** `recipe_judge`, `patch_near_miss`, `io_boundary_enforce`
- **When to load**
  - after recipe generation
  - before accepting any recipe into catalog/canon
- **Context packs**
  - required: `ctx_prime_mermaid`, `ctx_tool_registry`, `ctx_protocol_registry`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 6 — Deterministic Compute Gate (Counter-Required Routing)
- **SKILL_ID:** `skill_deterministic_compute_gate`
- **Role/Node:** L1/L2 (CPU router)
- **Load tags:** `compute_gate`, `exact_required`, `route_to_counter`, `fail_closed`
- **When to load**
  - any `grading_protocol` requiring exactness
  - any task with counting/aggregation triggers
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_tool_registry`
- **Scores:** RTC 9 / DET 10 / SAFE 10 / OPS 9 → **Overall 9**

---

### SKILL 7 — Algebra / Number Theory Pack (Exact)
- **SKILL_ID:** `skill_algebra_number_theory_pack`
- **Role/Node:** L3 (LLM) — Solver
- **Load tags:** `algebra`, `number_theory`, `exact`, `closed_form`
- **When to load**
  - algebra or number theory tasks after compute gate verdict
- **Context packs**
  - required: `ctx_protocol_registry`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 8 — Combinatorics Pack (Exact)
- **SKILL_ID:** `skill_combinatorics_pack`
- **Role/Node:** L3 (LLM) — Solver
- **Load tags:** `combinatorics`, `counting`, `exact`, `decomposition`
- **When to load**
  - combinatorial counting tasks after compute gate verdict
- **Context packs**
  - required: `ctx_protocol_registry`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 9 — Geometry Proof Pack (Bridge)
- **SKILL_ID:** `skill_geometry_proof_pack`
- **Role/Node:** L3 (LLM) + optional L4 compute
- **Load tags:** `geometry`, `proof_bridge`, `manifold_extract`
- **When to load**
  - geometry proof / angle chase / similarity closure
- **Context packs**
  - required: `ctx_protocol_registry`
- **Scores:** RTC 7 / DET 8 / SAFE 9 / OPS 7 → **Overall 7**

---

### SKILL 10 — Dual-Truth Adjudicator (Classical vs Framework)
- **SKILL_ID:** `skill_dual_truth_adjudicator`
- **Role/Node:** L5 (LLM_JUDGE)
- **Load tags:** `epistemics`, `dual_status`, `framework_vs_classical`
- **When to load**
  - famous/open conjectures
  - any “resolved in framework” language
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_core_stillwater`
- **Scores:** RTC 9 / DET 9 / SAFE 10 / OPS 8 → **Overall 8**

---

### SKILL 11 — Non-Conflation Guard (Hard Enforcement)
- **SKILL_ID:** `skill_non_conflation_guard`
- **Role/Node:** L5 (LLM_JUDGE guard)
- **Load tags:** `hard_guard`, `non_conflation`, `block_language`
- **When to load**
  - any output mentioning conjectures / “proof” / “settled”
  - any time Skill 10 runs
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_core_stillwater`
- **Scores:** RTC 10 / DET 10 / SAFE 10 / OPS 9 → **Overall 9**

---

### SKILL 12 — Contract Compliance (Schema Enforcer)
- **SKILL_ID:** `skill_schema_enforcer`
- **Role/Node:** L1/L2 (CPU guard)
- **Load tags:** `schema_enforce`, `normalize`, `fail_closed_json`
- **When to load**
  - every model/tool response before acceptance
- **Context packs**
  - required: `ctx_protocol_registry`
- **Scores:** RTC 10 / DET 10 / SAFE 10 / OPS 10 → **Overall 10**

---

### SKILL 13 — Proof Certificate Builder (Deterministic PROOF.json)
- **SKILL_ID:** `skill_proof_certificate_builder`
- **Role/Node:** L4 (TOOL) + L1 canonicalizer
- **Load tags:** `proof_emit`, `merkle_root`, `canonical_json`
- **When to load**
  - any PASS claim requiring replayable proof
  - benchmarks, regression reports
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_tool_registry`
- **Scores:** RTC 9 / DET 10 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 14 — Trace Distiller (Traces → Templates)
- **SKILL_ID:** `skill_trace_distiller`
- **Role/Node:** L2 (CPU) — Learning
- **Load tags:** `distill`, `learning`, `template_generation`, `answer_blind`
- **When to load**
  - task family distillation after verified PASS traces exist
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_core_stillwater`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 16 — Epistemic Typing (Truth Lanes)
- **SKILL_ID:** `skill_epistemic_typing`
- **Role/Node:** L5 (LLM_JUDGE) — Adjudicator
- **Load tags:** `truth_lanes`, `epistemics`, `lane_algebra`, `non_leakage`
- **When to load**
  - assigning lanes to claims based on evidence bundle
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_core_stillwater`
- **Scores:** RTC 9 / DET 9 / SAFE 10 / OPS 8 → **Overall 8**

---

### SKILL 15 — Canon Patch Writer (Deterministic Canon Evolution)
- **SKILL_ID:** `skill_canon_patch_writer`
- **Role/Node:** L2 (CPU) + L4 (diff tooling)
- **Load tags:** `canon_patch`, `manifest_hashes`, `gates_json`, `index_invariant`
- **When to load**
  - any proposal that touches `canon/`
- **Context packs**
  - required: `ctx_protocol_registry`, `ctx_vcs_pr`
  - optional: `ctx_core_stillwater` (stillwater seal requests)
- **Scores:** RTC 9 / DET 10 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 17 — Semantic Drift Detector
- **SKILL_ID:** `skill_semantic_drift_detector`
- **Role/Node:** L2 (CPU monitor) + optional L5 adjudication
- **Load tags:** `drift`, `term_registry`, `policy_surface`
- **When to load**
  - before promotion / sealing
  - when term definitions change
- **Context packs**
  - required: `ctx_core_stillwater`
- **Scores:** RTC 7 / DET 9 / SAFE 9 / OPS 7 → **Overall 7**

---

### SKILL 18 — Triple-LEAK Compression Protocol
- **SKILL_ID:** `skill_triple_leak_protocol`
- **Role/Node:** L2/L4 (CPU+tools) benchmarker
- **Load tags:** `compression_benchmark`, `side_info_accounting`, `ablations`
- **When to load**
  - any compression ratio claim / report
- **Context packs**
  - required: `ctx_benchmarking_triple_leak`, `ctx_protocol_registry`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 19 — Meta-Genome Alignment (Genome79)
- **SKILL_ID:** `skill_meta_genome_alignment`
- **Role/Node:** L5 (LLM_JUDGE architect)
- **Load tags:** `architecture`, `genome79`, `alignment_certificate`
- **When to load**
  - new subsystem proposals
  - pre-canon architecture acceptance
- **Context packs**
  - required: `ctx_governance_genome79`, `ctx_core_stillwater`
- **Scores:** RTC 7 / DET 8 / SAFE 9 / OPS 7 → **Overall 7**

---

### SKILL 20 — Rival-GPS Triangulation
- **SKILL_ID:** `skill_rival_gps_triangulation`
- **Role/Node:** L2 (CPU governor) + optional L5
- **Load tags:** `governor`, `anti_thrash`, `stop_or_prove`
- **When to load**
  - loops > 2 iterations
  - repeated UNKNOWN / oscillation detected
- **Context packs**
  - required: `ctx_core_stillwater`
- **Scores:** RTC 8 / DET 10 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 36 — Axiomatic Truth Lanes (Stillwater)
- **SKILL_ID:** `skill_axiomatic_truth_lanes`
- **Role/Node:** L5 (LLM_JUDGE adjudicator)
- **Load tags:** `axioms`, `lane_dominance`, `no_upgrade`
- **When to load**
  - before accepting any conclusion as PASS
- **Context packs**
  - required: `ctx_core_stillwater`, `ctx_protocol_registry`
- **Scores:** RTC 9 / DET 9 / SAFE 10 / OPS 8 → **Overall 8**

---

### SKILL 37 — Shannon Compaction Protocol
- **SKILL_ID:** `skill_shannon_compaction`
- **Role/Node:** L2 (CPU context engineer)
- **Load tags:** `context_compaction`, `witness_lines`, `interface_first`
- **When to load**
  - file_count>5 or file_lines>500 (or unknown scope)
- **Context packs**
  - required: `ctx_core_stillwater`
- **Scores:** RTC 9 / DET 10 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 38 — Hamiltonian Security Gate
- **SKILL_ID:** `skill_hamiltonian_security`
- **Role/Node:** L4 (scanner tools) + L1 veto
- **Load tags:** `security_gate`, `linter_veto`, `high_risk`
- **When to load**
  - risk_level=HIGH or category=security
- **Context packs**
  - required: `ctx_security`, `ctx_tool_registry`
- **Scores:** RTC 9 / DET 9 / SAFE 10 / OPS 8 → **Overall 8**

---

### SKILL 39 — GPT-Mini Hygiene Layer
- **SKILL_ID:** `skill_gpt_mini_hygiene`
- **Role/Node:** L1/L2 (CPU) — Optimizer
- **Load tags:** `hygiene`, `normalization`, `parity`, `surface_locking`
- **When to load**
  - raw text or logs require timestamp stripping and stable sorting
- **Context packs**
  - required: `ctx_core_stillwater`
- **Scores:** RTC 9 / DET 10 / SAFE 10 / OPS 9 → **Overall 9**

---

### SKILL 40 — Kent’s Red-Green Gate
- **SKILL_ID:** `skill_red_green_gate`
- **Role/Node:** L4 (repro runner) + L1 gate
- **Load tags:** `tdd`, `red_green`, `repro_required`
- **When to load**
  - bugfix / regression tasks
  - any “it fails” claim
- **Context packs**
  - required: `ctx_execution_harness`, `ctx_protocol_registry`
- **Scores:** RTC 9 / DET 10 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 41 — Socratic Debugging (Reflexion)
- **SKILL_ID:** `skill_socratic_debugging`
- **Role/Node:** L5 (LLM_JUDGE)
- **Load tags:** `self_critique`, `plan_hardening`, `min_diff`
- **When to load**
  - before final output (especially patches)
- **Context packs**
  - required: `ctx_core_stillwater`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

## 2.1) NEW: The 3 Critical Structural Gap Closers

### SKILL 42 — Capability Surface Guard
- **SKILL_ID:** `skill_capability_surface_guard`
- **Role/Node:** L1 (CPU guard) + L5 (judge escalation)
- **Load tags:** `cap_surface`, `tool_permissions`, `no_hidden_io`, `mode_enforce`
- **When to load**
  - before any L4 tool call
  - before any recipe node executes
  - whenever a request implies network/FS/write operations
- **What it enforces**
  - allowed tool set and mode flags (offline/no-net)
  - forbidden actions (credential access, unknown writes)
  - “capability claims” must match actual permitted surface
- **Context packs**
  - required: `ctx_tool_registry`, `ctx_core_stillwater`
- **Scores:** RTC 9 / DET 10 / SAFE 10 / OPS 9 → **Overall 9**

---

### SKILL 43 — Golden Replay Seal
- **SKILL_ID:** `skill_golden_replay_seal`
- **Role/Node:** L2 (CPU canonicalizer) + L4 (replay runner) + L5 (judge)
- **Load tags:** `golden_replay`, `two_run_parity`, `behavior_hash`, `promotion_gate`
- **When to load**
  - before any promotion to STILLWATER / “PASS” claims with durability
  - after dependency bumps
  - after recipe generation intended for canon
- **Outputs (expected)**
  - `behavior_hash.txt`
  - `replay_1.log`, `replay_2.log`
  - `replay_verdict.json`
- **Context packs**
  - required: `ctx_execution_harness`, `ctx_protocol_registry`, `ctx_tool_registry`
- **Scores:** RTC 8 / DET 10 / SAFE 9 / OPS 9 → **Overall 8**

---

### SKILL 44 — Deterministic Resource Governor
- **SKILL_ID:** `skill_deterministic_resource_governor`
- **Role/Node:** L1/L2 (CPU governor)
- **Load tags:** `resource_caps`, `loop_budgets`, `anti_runaway`, `stop_reason_required`
- **When to load**
  - every loop boundary (iteration)
  - before large context reads (compaction gate)
  - before multi-tool sequences or bulk file patches
- **What it enforces**
  - max_iterations/max_tool_calls/max_files/witness_line_budget
  - stop_reason required on exit
  - revert-on-worsening policy hooks
- **Context packs**
  - required: `ctx_core_stillwater`
- **Scores:** RTC 9 / DET 10 / SAFE 9 / OPS 10 → **Overall 9**

---

## 2.2) NEW: Dev Combos as Skills (Triggerable Modules)

### SKILL 45 — Plan→Execute Split Gate
- **SKILL_ID:** `skill_plan_execute_split_gate`
- **Role/Node:** L1 (CPU gate) + L5 (judge)
- **Load tags:** `plan_mode`, `execute_mode`, `promotion_lock_required`
- **When to load**
  - any time user request could be interpreted as implementation
- **Rule**
  - If no explicit promotion artifact (e.g., `ExecuteIntent.lock.json`), remain Plan-only.
- **Context packs**
  - required: `ctx_core_stillwater`, `ctx_protocol_registry`
- **Scores:** RTC 8 / DET 10 / SAFE 10 / OPS 9 → **Overall 8**

---

### SKILL 46 — Run + Test Harness
- **SKILL_ID:** `skill_run_test_harness`
- **Role/Node:** L4 (TOOL) + L2 (CPU normalizer)
- **Load tags:** `run_tests`, `normalized_logs`, `exit_codes`, `evidence_bundle`
- **When to load**
  - any execute-mode run
  - pre-merge verification
- **Context packs**
  - required: `ctx_execution_harness`, `ctx_protocol_registry`
- **Scores:** RTC 9 / DET 9 / SAFE 9 / OPS 9 → **Overall 9**

---

### SKILL 47 — CI Triage (logs → repro → fix route)
- **SKILL_ID:** `skill_ci_triage`
- **Role/Node:** L2 (CPU) + L3 (LLM repro authoring) + L5 (judge)
- **Load tags:** `ci_triage`, `logs_parse`, `repro_extract`, `route_to_red_green`
- **When to load**
  - CI failure logs present
  - tests failing on execute step
- **Context packs**
  - required: `ctx_ci_triage`, `ctx_execution_harness`, `ctx_protocol_registry`
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 48 — Review + Security Scan Veto (PR Gate)
- **SKILL_ID:** `skill_review_security_veto`
- **Role/Node:** L3 (LLM review) + L4 (scanner) + L5 (veto)
- **Load tags:** `code_review`, `security_veto`, `pre_pr_gate`
- **When to load**
  - before producing PR bundle / canon promotion
- **Context packs**
  - required: `ctx_security`, `ctx_vcs_pr`, `ctx_tool_registry`
- **Scores:** RTC 8 / DET 9 / SAFE 10 / OPS 8 → **Overall 8**

---

### SKILL 49 — Dependency Bump (Replay + Rollback)
- **SKILL_ID:** `skill_dependency_bump_replay_rollback`
- **Role/Node:** L3 (patch author) + L4 (tests) + L4 (replay) + L2 (rollback)
- **Load tags:** `dep_bump`, `lockfile_change`, `replay_required`, `rollback_ready`
- **When to load**
  - dependency upgrade requests
  - lockfile modifications detected
- **Context packs**
  - required: `ctx_execution_harness`, `ctx_vcs_pr`, `ctx_protocol_registry`
  - optional: `ctx_security` (if new dep triggers scan policy)
- **Scores:** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

---

### SKILL 50 — Tool Output Normalizer
- **SKILL_ID:** `skill_tool_output_normalizer`
- **Role/Node:** L1/L2 (CPU) — Normalizer
- **Load tags:** `normalize_tool`, `stable_bytes`, `timestamp_scrub`, `path_normalization`
- **When to load**
  - raw tool outputs require canonicalization for PROOF.json
- **Context packs**
  - required: `ctx_tool_registry`
- **Scores:** RTC 10 / DET 10 / SAFE 10 / OPS 10 → **Overall 10**

---

### SKILL 51 — Artifact Hash & Manifest Builder
- **SKILL_ID:** `skill_artifact_manifest_builder`
- **Role/Node:** L2 (CPU) — Evidence
- **Load tags:** `manifest`, `merkle_root`, `artifact_hash`, `touched_only`
- **When to load**
  - generating MANIFEST.json for touched files in a run
- **Context packs**
  - required: `ctx_tool_registry`
- **Scores:** RTC 10 / DET 10 / SAFE 10 / OPS 10 → **Overall 10**

---

## 3) “Secret Layer” Skills (Profiles)

### PRIME_CODER_SECRET_SAUCE_SKILL (layered over public PrimeCoder)
- **ID:** `prime_coder_secret_sauce`
- **Attach:** L3/L4/L5 orchestration policy layer
- **Load tags:** `prime_coder`, `secret_layer`, `benchmarks`, `stillwater_promotion`
- **Profiles:** `strict`, `fast`, `benchmark_adapt`
- **Context packs**
  - required: `ctx_core_stillwater`, `ctx_tool_registry`, `ctx_protocol_registry`
  - optional: `ctx_security` (if security gate triggers)
- **Scores (strict):** RTC 8 / DET 9 / SAFE 9 / OPS 8 → **Overall 8**

### PRIME_MATH_SECRET_SKILL (layered over public PrimeMath)
- **ID:** `prime_math_secret_v2.0.0`
- **Attach:** math adjudication + proof/compute gates
- **Load tags:** `prime_math`, `secret_layer`, `dual_status`, `proof_grade`
- **Context packs**
  - required: `ctx_core_stillwater`, `ctx_protocol_registry`
- **Scores:** RTC 9 / DET 9 / SAFE 10 / OPS 9 → **Overall 9**

---

## 4) CLI Load Rules (Deterministic)

### Default pipeline (recommended)
0. **Skill 44** Resource Governor (loop budgets on entry)
1. **Skill 45** Plan→Execute Split Gate
2. **Skill 42** Capability Surface Guard (before any tool/IO)
3. **Skill 37** Shannon Compaction (if compaction triggers)
4. **Skill 12** Schema Enforcer wraps every model/tool output
5. **Skill 6** Compute Gate (if exact/counter triggers)
6. **Skill 3** Recipe Selector
7. If no recipe: **Skill 4** Recipe Generator → **Skill 5** Recipe Judge
8. If CI logs: **Skill 47** CI Triage
9. If bugfix/regression: **Skill 40** Red-Green Gate + **Skill 46** Run/Test Harness
10. After tests: **Skill 41** Socratic Debugging
11. Before PR/canon: **Skill 48** Review + Security Scan Veto
12. Before promotion: **Skill 43** Golden Replay Seal
13. Emit proofs: **Skill 13** Proof Certificate Builder
14. Canon changes: **Skill 15** Canon Patch Writer
15. If drift risk: **Skill 17** Semantic Drift Detector
16. If oscillation: **Skill 20** Rival-GPS Triangulation

---

## 5) “Which Skill for Which Node?” Quick Map

- **L1 CPU**:
  - `skill_schema_enforcer`
  - `skill_recipe_selector_cpu_first` (routing half)
  - `skill_deterministic_compute_gate`
  - `skill_capability_surface_guard`
  - `skill_plan_execute_split_gate`
  - `skill_deterministic_resource_governor` (entry/loop)

- **L2 CPU**:
  - `skill_shannon_compaction`
  - `skill_rival_gps_triangulation`
  - `skill_semantic_drift_detector`
  - `skill_canon_patch_writer` (core)
  - `skill_triple_leak_protocol` (core)
  - `skill_ci_triage` (log parsing)
  - `skill_golden_replay_seal` (canonicalization/compare)

- **L3 LLM**:
  - `skill_wish_llm`
  - `skill_recipe_generator_prime_mermaid` (proposal step)
  - `skill_review_security_veto` (review authoring component)
  - math packs (as routed)

- **L4 TOOL**:
  - `skill_run_test_harness`
  - `skill_proof_certificate_builder`
  - `skill_red_green_gate`
  - `skill_hamiltonian_security`
  - `skill_golden_replay_seal` (replay runs)
  - `skill_dependency_bump_replay_rollback` (test+replay path)

- **L5 LLM_JUDGE**:
  - `skill_wish_qa`
  - `skill_llm_judge_recipe_validation`
  - `skill_non_conflation_guard`
  - `skill_dual_truth_adjudicator`
  - `skill_axiomatic_truth_lanes`
  - `skill_socratic_debugging`
  - `skill_review_security_veto` (veto decision component)

---

## 6) TODO Slots (Index Growth)
Add new skills here with:
- deterministic load tags
- context pack list
- node attachment
- score quartet + overall

*"Auth: 65537"*
