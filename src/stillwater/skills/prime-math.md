PRIME_MATH_SECRET_SKILL
version: 2.1.0
profile: private
includes_public_skill: canon/prime-math/skills/prime_math_public_skill_v1.0.0.md
secret_pack_id: stillwater-prime-math-secret-v2.1.0
sealing_policy: 641-274177-65537

# ============================================================
# PRIME MATH — SECRET SKILL (v2.1.0)
#
# Design goals:
# - Preserve Public contract EXACTLY (machine-parseable, fail-closed).
# - Add operational verification gates (math analogs of Red→Green).
# - Priors guide search only; never override truth.
# - Deterministic loop budgets, seed semantics, rung checklists.
# - Proof-grade discipline for theorem/olympiad tasks.
# - OOLONG memory + DoV recipe tiers + dual-witness replay gates.
# - Formal-proof bridge with immutable-source gates.
# - External geometry proof-trace bridge with strict checker metadata gates.
# - Famous-problem adjudication with dual-status (classical vs framework) reporting.
# - IF-theory adjudication with explicit scope + validation tiers.
# - Resolution Limits (R_p) convergence detection with halting certificates.
# - Closure-First reasoning for boundary analysis and proof surface locking.
#
# v2.1.0 key upgrades vs v2.0.0:
# - Added Resolution Limits (R_p) policy (Section 0.12) - convergence detection
# - Added Closure-First reasoning policy (Section 0.13) - boundary analysis
# - Integrated with prime-coder v1.3.0 math-to-code patterns
# - Added halting certificates (EXACT/CONVERGED/TIMEOUT/DIVERGED)
# - Added proof surface locking and boundary complexity metrics
# - Lane algebra extended to include convergence status
# - IMO 6/6 patterns integrated (gap-guided, witness diversity, state machines)
#
# v2.0.0 key upgrades vs v1.8.0:
# - Added closed state machine (finite STATE_SET + TRANSITIONS + FORBIDDEN).
# - Normalized stop reasons (public-safe) + explicit ERROR vs UNKNOWN boundaries.
# - Made theorem "OK" conditions fully mechanical (no implicit TODO allowances).
# - Tightened witness typing and replay requirements (stable ordering + ids).
# - Clarified layer naming: S1..S17 are "secret layers"; public steps run first.
# ============================================================

Purpose:
  - Execute the full public skill contract first (non-negotiable).
  - Add private priors, decomposition rules, and verification gates.
  - Preserve machine-parseable outputs and never-worse behavior.
  - Convert "math answers" into auditable, replayable claims.

Public_Core_Requirement:
  non_negotiable:
    - Run every public protocol step exactly.
    - Keep required output keys EXACTLY:
        - answer
        - witnesses
        - status
        - counter_bypass_used
    - Never weaken public forbidden states.
  compatibility: solace_cli_prime_math_ab_v1

# ------------------------------------------------------------
# 0) Closed Runtime State Machine (Secret Layer)   [NEW v2.0.0]
# ------------------------------------------------------------
State_Machine:
  STATE_SET:
    - INIT
    - LOAD_PUBLIC_CORE
    - PARSE_TASK
    - CLASSIFY_TASK
    - ROUTE_LAYERS
    - BUILD_PLAN
    - EXECUTE_PUBLIC_PROTOCOL
    - APPLY_SECRET_LAYERS
    - RUN_VERIFICATION_LADDER_641
    - RUN_VERIFICATION_LADDER_274177
    - RUN_VERIFICATION_LADDER_65537
    - BUILD_WITNESSES
    - REPLAY_CHECK
    - FINALIZE_OUTPUT
    - EXIT_OK
    - EXIT_UNKNOWN
    - EXIT_ERROR
    - EXIT_OUT_OF_SCOPE
  INPUT_ALPHABET:
    - PROBLEM_TEXT
    - MODE_FLAGS
    - TOOL_OUTPUT
    - CANON_ARTIFACTS
    - PRIVATE_ARTIFACTS
  OUTPUT_ALPHABET:
    - RESPONSE_OBJECT
    - WITNESS_HANDLES
    - VERIFICATION_ACTIONS
  TRANSITIONS:
    - INIT -> LOAD_PUBLIC_CORE: on PROBLEM_TEXT
    - LOAD_PUBLIC_CORE -> PARSE_TASK: on public_loaded
    - PARSE_TASK -> CLASSIFY_TASK: always
    - CLASSIFY_TASK -> ROUTE_LAYERS: always
    - ROUTE_LAYERS -> BUILD_PLAN: always
    - BUILD_PLAN -> EXECUTE_PUBLIC_PROTOCOL: always
    - EXECUTE_PUBLIC_PROTOCOL -> APPLY_SECRET_LAYERS: always
    - APPLY_SECRET_LAYERS -> RUN_VERIFICATION_LADDER_641: always
    - RUN_VERIFICATION_LADDER_641 -> EXIT_UNKNOWN: if rung_641_failed
    - RUN_VERIFICATION_LADDER_641 -> RUN_VERIFICATION_LADDER_274177: if rung_641_passed
    - RUN_VERIFICATION_LADDER_274177 -> EXIT_UNKNOWN: if rung_274177_failed
    - RUN_VERIFICATION_LADDER_274177 -> RUN_VERIFICATION_LADDER_65537: if rung_274177_passed
    - RUN_VERIFICATION_LADDER_65537 -> EXIT_ERROR: if rung_65537_failed
    - RUN_VERIFICATION_LADDER_65537 -> BUILD_WITNESSES: if rung_65537_passed
    - BUILD_WITNESSES -> REPLAY_CHECK: always
    - REPLAY_CHECK -> EXIT_UNKNOWN: if replay_failed
    - REPLAY_CHECK -> FINALIZE_OUTPUT: if replay_passed_or_not_required
    - FINALIZE_OUTPUT -> EXIT_OK: if status_ok
    - FINALIZE_OUTPUT -> EXIT_UNKNOWN: if status_unknown
    - FINALIZE_OUTPUT -> EXIT_OUT_OF_SCOPE: if out_of_scope
  FORBIDDEN_STATES:
    - UNWITNESSED_OK
    - STATUS_UPGRADE_BY_PRIOR
    - FRAMEWORK_CLASSICAL_CONFLATION
    - UNBOUNDED_DOMAIN_WITH_OK
    - HIDDEN_ASSUMPTIONS
    - NONDETERMINISTIC_NORMALIZATION
    - PROOF_TODO_WITH_OK
    - EXTERNAL_PROOF_WITHOUT_IMMUTABLE_COMMIT
    - EXTERNAL_GEOMETRY_TRACE_WITHOUT_CHECKER_METADATA
    - INFINITE_LOOP_WITHOUT_R_P_CHECK                      # NEW v2.1.0
    - CONVERGENCE_CLAIM_WITHOUT_CERTIFICATE                # NEW v2.1.0
    - RESIDUAL_TRACKING_OMITTED                            # NEW v2.1.0
    - LANE_C_WITHOUT_JUSTIFICATION                         # NEW v2.1.0
    - BOUNDARY_MUTATION_WITHOUT_JUSTIFICATION              # NEW v2.1.0
    - LEMMA_REMOVAL_WITHOUT_DEPRECATION                    # NEW v2.1.0
    - INTERIOR_LEAKAGE_INTO_BOUNDARY                       # NEW v2.1.0

# ------------------------------------------------------------
# 0.1) Runtime Parameters (Explicit Loop Control)
# ------------------------------------------------------------
Loop_Control:
  budgets:
    max_iterations: 5
    max_revisions_per_iteration: 1
    max_witnesses_emitted: 12
    max_micro_witnesses: 64
    max_seconds_soft: 900
  termination:
    stop_reasons:
      - OK
      - UNKNOWN_INSUFFICIENT_WITNESSES
      - UNKNOWN_CONFLICTING_WITNESSES
      - UNKNOWN_UNBOUNDED_DOMAIN
      - UNKNOWN_SEED_DISAGREEMENT
      - UNKNOWN_OUTSIDE_DOV
      - ERROR_PROTOCOL_DRIFT
      - ERROR_OUTPUT_INVALID
      - ERROR_VERIFICATION_FAILED
      - ERROR_REPLAY_FAILED
      - OUT_OF_SCOPE
      - MAX_ITERS
    required_on_exit:
      - status
      - stop_reason
      - verification_rung
      - secret_layers_used

# ------------------------------------------------------------
# 0.2) Solve Grade Policy (Proof-Completeness Gate)
# ------------------------------------------------------------
Solve_Grade_Policy:
  labels: [full_solved, sketch_solved, pending]
  requirements:
    full_solved:
      - all_critical_lemmas_closed: true
      - no_unresolved_todo_handwaves: true
      - strong_witness_present:
          any_of:
            - proof://prime-math/<id>
            - compute://prime-math/<id>
            - exhaustive://prime-math/<id>
    sketch_solved:
      - core_strategy_coherent: true
      - lemma_gaps_allowed: true
    pending:
      - contradiction_unresolved_or_strategy_incoherent: true
  status_binding:
    theorem_or_proof_tasks:
      - status_ok_allowed_only_if: proof_grade == full_solved
      - otherwise: status = UNKNOWN
    exact_numeric_tasks:
      - status_ok_allowed_if: deterministic_compute_witness_present == true
  mandatory_reporting:
    - proof_grade
    - lemma_gap_count
    - unresolved_lemmas

# ------------------------------------------------------------
# 0.3) OOLONG Memory Discipline (Deterministic Recall)
# ------------------------------------------------------------
OOLONG_Memory_Discipline:
  principle:
    - LLM memory is probabilistic; benchmark/state memory must be externalized.
    - Use deterministic lookup from artifacts, not free-form recall, for score claims.
  required_sources_for_eval_claims:
    - canon/prime-math/tests/postmortem.md
    - canon/prime-math/tests/results/**/latest_run.json
    - canon/prime-math/tests/results/**/scorecard.json
  self_check_rule:
    - self_check_without_externalized_artifacts_is_not_claim_grade: true
  reporting:
    - include_memory_capsule_id_for_high_stakes_claims: true

# ------------------------------------------------------------
# 0.4) Recipe + DoV Promotion Gates (Proof Strategy = Recipe)
# ------------------------------------------------------------
Recipe_DoV_Gates:
  concept:
    - proof strategy is a recipe with explicit Domain of Validity (DoV).
    - full_solved requires strategy within DoV and passing promotion gates.
  recipe_tiers: [DRAFT, QUALIFIED, STABLE, CANONICAL]
  theorem_required_fields:
    - strategy_recipe_id
    - recipe_tier
    - dov_id
    - dov_conditions
  promotion_gates:
    G1_correctness:
      - theorem_all_critical_lemmas_closed
      - numeric_recompute_matches
    G2_boundedness:
      - budgets_respected
    G3_never_worse:
      - not_worse_than_baseline_on_locked_suite
    G4_determinism:
      - replay_stable_normalized_output
    G5_safety:
      - no_forbidden_state_entered
    G6_observability:
      - full_witness_and_action_trail_present
  fail_closed:
    - outside_declared_dov:
        status: UNKNOWN
        unknown_reason: "outside DoV"

# ------------------------------------------------------------
# 0.5) Dual-Witness + Replay Integrity
# ------------------------------------------------------------
Dual_Witness_Replay:
  theorem_full_solved_rule:
    - full_solved_requires:
        any_of:
          - proof_witness_A_and_independent_witness_B
          - trusted_external_proof_witness_and_local_replay
  independent_witness_examples:
    - symbolic_proof_plus_bounded_exhaustive_checker
    - two_independent_harnesses
    - two_decomposition_seeds_with_independent_verification
  replay_requirements:
    - canonicalize_output_first: true
    - rerun_verification_path: true
    - include_replay_sha256_or_replay_id: true
  contradiction_rule:
    - if_witnesses_disagree_and_unreconciled:
        status: UNKNOWN
        unknown_reason: "dual witness disagreement"

# ------------------------------------------------------------
# 0.6) Anti-Thrash Governance
# ------------------------------------------------------------
Anti_Thrash_Governance:
  triggers:
    - oscillation_full_solved_vs_sketch_solved_consecutive: true
    - repeated_unknown_same_lemma_class: true
  controls:
    cooldown_mode:
      freeze_new_strategy_changes_for_task: true
    require_prevention_artifact_before_repromotion:
      - new_test
      - new_detector
      - refined_dov_condition
  closure_rule:
    - no_incident_closure_without_stable_replay_monitoring_window: true

# ------------------------------------------------------------
# 0.7) Theorem Closure Playbooks
# ------------------------------------------------------------
Theorem_Closure_Playbooks:
  required_for:
    - task_family == F6_olympiad_proof
    - OR target_type == theorem_proof
  required_artifacts:
    - closure_checklist_id
    - closure_checklist_pass
    - closed_lemmas
    - open_lemmas
  playbooks:
    floor_sum_divisibility:
      checklist:
        - divisibility_preserving_transform_identity
        - bounded_integer_auxiliary_count_term
        - finite_case_dichotomy_from_divisibility_plus_bounds
        - eliminate_irrational_case
        - eliminate_non_integer_rational_case
        - finish_integer_structure_necessity_and_sufficiency
    recurrence_tail_periodicity:
      checklist:
        - eventual_local_non_repeat_lemma
        - growth_bound_lemma
        - tail_structure_lemma
        - parity_subsequence_periodicity_extraction
    synthetic_geometry_angle_sum:
      checklist:
        - define_invariant_target_angle_identity
        - map_tangent_conditions_to_angle_or_power_constraints
        - convert_relations_to_single_closure_chain
        - close_with_deterministic_angle_sum_equality
    functional_equation_quantifier:
      checklist:
        - derive_forced_identities_from_each_branch
        - classify_candidate_function_families
        - prove_universal_upper_bound_on_output_set_size
        - provide_extremal_constructive_lower_bound_witness
  promotion_rule:
    - full_solved_requires:
        closure_checklist_pass == true
        open_lemmas == []

# ------------------------------------------------------------
# 0.8) Trusted Formal-Proof Bridge
# ------------------------------------------------------------
Trusted_Formal_Proof_Bridge:
  purpose:
    - allow full_solved using independently machine-verified theorem artifacts.
  trusted_sources:
    - compfiles_problem_page_plus_source_commit
    - mathlib4_archive_immutable_commit
  required_for_external_full_solved:
    - proof_origin: external_verified
    - external_witness_id
    - external_proof_url
    - external_proof_commit
    - local_consistency_replay_checks
  local_consistency_replay_checks:
    - theorem_statement_exact_match_to_prompt
    - at_least_one_local_sanity_property_check
    - no_contradiction_external_vs_local
  fail_closed:
    - missing_immutable_commit_or_unverifiable_source:
        status: UNKNOWN
        unknown_reason: "missing immutable external proof commit"

# ------------------------------------------------------------
# 0.9) External Geometry Proof-Trace Bridge
# ------------------------------------------------------------
External_Geometry_Proof_Trace_Bridge:
  purpose:
    - allow geometry theorem promotion when trusted prover publishes machine-checkable trace.
  trusted_sources:
    - alphageometry_trusted_trace_page
  required_for_external_geometry_full_solved:
    - proof_origin: external_verified_geometry
    - external_geometry_witness_id
    - external_geometry_proof_url
    - external_geometry_trace_type
    - external_geometry_checker
    - external_geometry_proof_date
    - local_consistency_replay_checks
  local_consistency_replay_checks:
    - theorem_statement_exact_match_check
    - numerical_angle_identity_replay_on_random_valid_instances
    - no_contradiction_with_external_trace
  fail_closed:
    - missing_checker_metadata_or_local_replay:
        status: UNKNOWN
        unknown_reason: "missing geometry checker metadata or replay checks"

# ------------------------------------------------------------
# 0.10) Famous Problem Adjudication Pack
# ------------------------------------------------------------
Famous_Problem_Adjudication_Pack:
  purpose:
    - prevent status conflation for famous open problems across frameworks.
  required_dual_status_fields_for_famous_problems:
    - classical_status
    - framework_status
    - framework_scope
    - claim_type
  claim_type_enum:
    - proven_classical
    - resolved_within_bounds
    - resolved_within_framework
    - reframed
    - open
  adjudication_rules:
    - never_present_framework_resolution_as_classical_proof
    - if_sources_disagree_report_conflict_and_downgrade_unknown
    - zero_point_and_geometric_big_bang_default_to_framework_claims
  fail_closed:
    - if_dual_status_missing:
        status: UNKNOWN
        unknown_reason: "missing dual-status fields"

# ------------------------------------------------------------
# 0.11) IF-Theory Claim Adjudication Pack
# ------------------------------------------------------------
IF_Theory_Claim_Adjudication_Pack:
  purpose:
    - prevent conflation between conditional framework theorems and classical proofs.
  required_fields_for_if_theorem_claims:
    - proof_scope
    - axiom_basis
    - validation_level
    - replication_status
    - falsification_criteria
  proof_scope_enum:
    - classical_unconditional
    - conditional_on_axioms
    - empirical_model
  validation_level_enum:
    - code_tests_only
    - formal_math_plus_code
    - first_principles_physics
    - real_data_validation
  adjudication_rules:
    - conditional_on_axioms_not_equal_classical_unconditional
    - if_depends_on_physical_axioms_must_list_axioms
    - llm_review_is_supporting_not_consensus
    - if_source_disagreement_unresolved_then_unknown
  fail_closed:
    - if_missing_proof_scope_or_validation_level:
        status: UNKNOWN
        unknown_reason: "missing IF scope/validation tier"

# ------------------------------------------------------------
# 0.12) Resolution Limits (R_p) - Convergence Detection  [NEW v2.1.0]
# ------------------------------------------------------------
Resolution_Limits_Policy:
  source_integration:
    - canon/prime-math/skills/resolution-limits-skill.md
    - canon/prime-skills/libraries/prime_coder_convergence.py

  purpose:
    - Formal halting criteria for iterative mathematical methods
    - Prevent infinite loops without explicit convergence checks
    - Lane classification for convergence status

  core_principle:
    R_p:
      definition: "Minimal distinguishable unit of state difference"
      default_tolerance: 1e-10
      formula: "residual < R_p → CONVERGED"
      adjustable: true  # Can be stricter (1e-15) or looser (1e-5)

  halting_certificates:
    EXACT:
      lane: "A"
      condition: "residual == 0.0"
      meaning: "Exact solution (no approximation)"
      required_evidence:
        - exact_residual_zero: true
        - iteration_count: int
        - final_value: exact_type

    CONVERGED:
      lane: "B"
      condition: "residual < R_p"
      meaning: "Converged within tolerance (acceptable approximation)"
      required_evidence:
        - final_residual: float
        - R_p_tolerance: float
        - iteration_count: int
        - residual_history: list

    TIMEOUT:
      lane: "C"
      condition: "iteration >= max_iterations AND residual >= R_p"
      meaning: "Max iterations reached without convergence"
      required_evidence:
        - max_iterations: int
        - final_residual: float
        - residual_history: list
        - timeout_reason: str

    DIVERGED:
      lane: "C"
      condition: "residuals strictly increasing (last 3+ iterations)"
      meaning: "Solution diverging (method failing)"
      required_evidence:
        - recent_residuals: list
        - divergence_trend: str
        - iteration_count: int

  enforcement:
    iterative_methods:
      - MUST specify explicit R_p tolerance
      - MUST track residual history
      - MUST return halting certificate
      - MUST NOT claim convergence without certificate

    forbidden:
      - INFINITE_LOOP_WITHOUT_R_P_CHECK
      - CONVERGENCE_CLAIM_WITHOUT_CERTIFICATE
      - RESIDUAL_TRACKING_OMITTED
      - LANE_C_WITHOUT_JUSTIFICATION

  lane_algebra:
    rules:
      - "Lane(EXACT) = A (strongest)"
      - "Lane(CONVERGED) = B (acceptable)"
      - "Lane(TIMEOUT or DIVERGED) = C (requires investigation)"
      - "Lane(IterativeMethod) = MIN(Lane(Convergence), Lane(Computation))"
    min_rule_application:
      - "If computation uses Fraction (Lane A) but convergence is TIMEOUT (Lane C), result is Lane C"
      - "If computation uses float (Lane B) but convergence is EXACT (Lane A), result is Lane B"

  integration_with_witnesses:
    - Each halting certificate becomes a witness
    - witness_type: "convergence://halting_certificate"
    - witness_data: {certificate, lane, iterations, residual_history}
    - Replay: Re-run iteration with same initial conditions, verify same certificate

  examples:
    newton_sqrt2:
      method: "Newton's method for sqrt(2)"
      initial: "Fraction(3, 2)"
      iteration: "(x + 2/x) / 2"
      R_p: 1e-10
      expected_certificate: "CONVERGED"
      expected_lane: "B"
      expected_iterations: "~10"

    fixed_point:
      method: "Fixed-point iteration"
      condition: "f(x) = x"
      R_p: 1e-10
      certificates: ["EXACT (if f(x)=x exactly)", "CONVERGED (if |f(x)-x| < R_p)", "TIMEOUT", "DIVERGED"]

# ------------------------------------------------------------
# 0.13) Closure-First Reasoning - Boundary Analysis  [NEW v2.1.0]
# ------------------------------------------------------------
Closure_First_Policy:
  source_integration:
    - canon/prime-math/skills/closure-first-reasoning-skill.md
    - canon/prime-skills/libraries/prime_coder_closure.py

  purpose:
    - Objects emerge from boundaries, not points
    - API stability through formal surface tracking
    - Boundary complexity measurement
    - Breaking change detection

  core_principle:
    boundary_first:
      motto: "Design the boundary, derive the interior"
      definition: "Mathematical objects are characterized by their boundaries"
      application: "Analyze interface before implementation"

  mathematical_applications:
    theorem_structure:
      boundary: "Hypotheses + Conclusion (the interface)"
      interior: "Proof steps (the implementation)"
      complexity_metric: "Number of hypotheses + complexity of conclusion"

    proof_organization:
      boundary: "Lemmas stated (the API)"
      interior: "Lemma proofs (the implementation)"
      api_surface: "Public lemmas available for reuse"

    function_analysis:
      boundary: "Domain + Codomain + Constraints"
      interior: "Function implementation/formula"
      complexity: "Constraint count + domain complexity"

  boundary_extraction:
    theorem:
      boundary_elements:
        - hypotheses: "Input assumptions"
        - conclusion: "Output claim"
        - constraints: "Domain restrictions"
      interior_elements:
        - proof_steps: "Deductive chain"
        - auxiliary_lemmas: "Helper results"
        - constructions: "Intermediate objects"

    proof:
      boundary_elements:
        - main_lemmas: "Key results (reusable)"
        - theorem_statement: "Final claim"
      interior_elements:
        - lemma_proofs: "Justifications"
        - technical_steps: "Calculation details"

  boundary_complexity:
    formula: "C_b = 0.4 * |boundary| + 0.3 * diversity + 0.3 * (|boundary| / max(|interior|, 1))"
    components:
      length: "Number of boundary elements (hypotheses, lemmas)"
      diversity: "Types of elements (algebraic, geometric, combinatorial)"
      ratio: "Boundary/interior size"

    interpretation:
      simple: "C_b < 3 (few hypotheses, simple conclusion)"
      moderate: "3 <= C_b < 7 (multiple hypotheses, structured)"
      complex: "C_b >= 7 (many hypotheses, high diversity)"

  proof_surface_lock:
    purpose: "Lock proof structure at checkpoints"
    workflow:
      lock_lemmas:
        action: "Record lemma statements as boundary"
        effect: "Changes to lemma statements = breaking changes"
      check_proof_evolution:
        action: "Verify lemma statements unchanged"
        effect: "Interior proof steps can change, boundary cannot"

    breaking_changes:
      - removed_lemma: "Previously available lemma removed"
      - weakened_lemma: "Lemma conclusion weakened"
      - strengthened_hypothesis: "Lemma requires more assumptions"

    non_breaking_changes:
      - new_lemma_added: "Additional helper lemma (boundary expansion)"
      - proof_reorganized: "Interior steps reordered"
      - construction_optimized: "Better intermediate objects"

  enforcement:
    proof_construction:
      - MUST identify boundary (lemmas) before interior (proofs)
      - MUST compute boundary complexity
      - MUST lock surface at major proof milestones
      - MUST check for breaking changes on revision

    forbidden:
      - BOUNDARY_MUTATION_WITHOUT_JUSTIFICATION
      - LEMMA_REMOVAL_WITHOUT_DEPRECATION
      - INTERIOR_LEAKAGE_INTO_BOUNDARY
      - IMPLICIT_DEPENDENCIES_ACROSS_BOUNDARY

  integration_with_witnesses:
    - Each boundary element becomes a witness
    - witness_type: "closure://boundary_element"
    - witness_data: {element_type, element_statement, complexity}
    - Replay: Verify boundary elements unchanged, interior may differ

  examples:
    imo_p4_2024:
      boundary:
        - "Triangle ABC with AB < AC < BC"
        - "Ω (circumcircle), I (incenter)"
        - "Goals: K, L, P, X, Y, Z defined"
        - "Prove: ∠KIL + ∠YPX = 180°"
      interior:
        - "14 geometry lemmas applied"
        - "Angle chasing steps"
        - "Incenter and midsegment properties"
      boundary_complexity: "~5 (4 objects + 1 goal)"

    pythagorean_theorem:
      boundary:
        - "Right triangle (∠C = 90°)"
        - "Sides a, b, c (c is hypotenuse)"
      conclusion: "a² + b² = c²"
      interior: "Multiple proofs available (Euclid, similar triangles, etc.)"
      boundary_complexity: "~2 (simple hypothesis + simple conclusion)"

# ------------------------------------------------------------
# 1) Routing Table (Prevents "Theory Noise")
# ------------------------------------------------------------
Routing:
  task_family_to_layers:
    F1_deterministic_math:
      required: [S1, S3, S4, S10, S11_5]
      optional: [S2, S7, S9, S11, S12, S14, S16]
      forbidden: [S15, S17]
    F2_resolution_bound:
      required: [S1, S3, S8, S9, S10]
      optional: [S2, S7, S12]
      forbidden: [S14, S15, S16, S17]
    F3_truth_lane:
      required: [S1, S3, S8, S9, S10]
      optional: [S2, S7, S12, S13]
      forbidden: [S14, S15, S16, S17]
    F4_domain_validity:
      required: [S1, S3, S7, S8, S10]
      optional: [S2, S9, S12, S13]
      forbidden: [S14, S15, S16, S17]
    F5_rival_witness:
      required: [S1, S3, S7, S10, S13]
      optional: [S2, S8, S9, S11, S12]
      forbidden: [S14, S15, S16, S17]
    F6_olympiad_proof:
      required: [S1, S3, S4, S7, S10, S11_6]
      optional: [S2, S8, S9, S11, S12, S15]
      forbidden: [S17]
    F7_famous_problem_adjudication:
      required: [S1, S3, S8, S9, S13]
      optional: [S2, S7, S10, S12]
      forbidden: [S14, S16, S17]
    F8_if_theory_adjudication:
      required: [S1, S3, S8, S9, S13]
      optional: [S2, S7, S10, S12]
      forbidden: [S14, S16, S17]

  domain_to_layers:
    number_theory:
      allow: [S14, S16, S17]
      note: "Priors guide search only; cannot upgrade status."
    geometry:
      allow: [S11, S15]
      note: "Must reduce to checkable constraints; proofs still witness-anchored."
    famous_problem_statusing:
      allow: [S13]
    if_theory_statusing:
      allow: [S13]

# ------------------------------------------------------------
# 2) Truth Priority (Non-Override Rule)
# ------------------------------------------------------------
Truth_Priority:
  rule:
    - status_OK_requires_witnesses_and_verification
    - priors_may_guide_search_only
    - priors_may_trigger_UNKNOWN_if_gap_found
  forbidden:
    - upgrading_status_or_lane_by_prior
    - replacing_missing_witnesses_with_confidence
    - inventing_external_facts
  impossibility_policy:
    - answer="IMPOSSIBLE" allowed_only_if_contradiction_proven_by_witness
    - else_fail_closed_unknown: true

# ------------------------------------------------------------
# 3) Proof/Compute Gate (Math Red→Green Analog)
# ------------------------------------------------------------
Proof_Compute_Gate:
  applicability:
    - task_family in [F1_deterministic_math, F6_olympiad_proof, F7_famous_problem_adjudication, F8_if_theory_adjudication]
    - OR target_requires_exact_value_or_definitive_yes_no
  requirement_for_status_OK:
    any_of:
      - proof_witness_present
      - compute_witness_present
      - exhaustive_witness_present
  witness_typing_required:
    - proof://prime-math/<id>
    - compute://prime-math/<id>
    - exhaustive://prime-math/<id>
    - canon://prime-math/<id>
    - secret://stillwater/prime-math/<id>
  theorem_strictness:
    - if_theorem_task_and_proof_grade_not_full_solved:
        status: UNKNOWN
        unknown_reason: "proof incomplete"
    - if_theorem_task_and_full_solved:
        require:
          - Dual_Witness_Replay.theorem_full_solved_rule
          - Recipe_DoV_Gates.theorem_required_fields
          - Theorem_Closure_Playbooks.required_artifacts

# ------------------------------------------------------------
# 4) Seed Policy (Deterministic Multi-Seed)
# ------------------------------------------------------------
Seed_Policy:
  definition:
    - seed_variant_is_deterministic_path_label_not_randomness
  seeds_default_for_high_risk:
    - ["seedA", "seedB"]
  agreement_rule:
    - if_normalized_answers_disagree:
        status: UNKNOWN
        unknown_reason: "seed disagreement"
  reporting:
    - include_seed_agreement_in_verification_actions: true

# ------------------------------------------------------------
# 5) Secret Layers (S1..S17) — unchanged semantics, tightened names
# ------------------------------------------------------------
Secret_Layers:
  S1: Distill_Compression_Core
  S2: Multichannel_Routing
  S3: Verification_Ladder
  S4: Generator_First_Determinism
  S5: Benchmark_Governance
  S6: Theory_Bridges
  S7: Rival_Counterexample
  S8: Legal_Grade_Governance
  S9: Eval_First
  S10: Self_Correction
  S11: Symbolic_Bridge
  S11_5: Counter_Not_LLM
  S11_6: Olympiad_Proof_Compiler
  S12: Cross_Domain_Resonance
  S13: Meta_Filters
  S14: Distribution_Density_Priors
  S15: Geometric_Closure
  S16: Forms_Sequences_Priors
  S17: Scale_Rarity_Priors

# ------------------------------------------------------------
# 6) Output Contract (Public required + Secret optional fields)
# ------------------------------------------------------------
Output_Contract:
  required_keys:
    - answer
    - witnesses
    - status
    - counter_bypass_used
  optional_keys:
    - task_family
    - lane
    - resolution_status
    - confidence_band
    - unknown_reason
    - evidence_quality: [DIRECT, INDIRECT, NONE]
    - policy_risk: [LOW, MEDIUM, HIGH]
    - verification_actions
    - proof_grade: [full_solved, sketch_solved, pending]
    - lemma_gap_count
    - unresolved_lemmas
    - adversarial_attack_vectors
    - strategy_recipe_id
    - recipe_tier: [DRAFT, QUALIFIED, STABLE, CANONICAL]
    - dov_id
    - dov_conditions
    - witness_pair_mode
    - replay_sha256
    - memory_capsule_id
    - closure_checklist_id
    - closed_lemmas
    - open_lemmas
    - closure_checklist_pass
    - classical_status
    - framework_status
    - framework_scope
    - claim_type
    - proof_scope
    - axiom_basis
    - validation_level
    - replication_status
    - falsification_criteria
    - proof_origin: [native, external_verified, external_verified_geometry]
    - external_witness_id
    - external_proof_url
    - external_proof_commit
    - external_geometry_witness_id
    - external_geometry_proof_url
    - external_geometry_trace_type
    - external_geometry_checker
    - external_geometry_proof_date
    - local_consistency_replay_checks
    - secret_layers_used
    - verification_rung: [641, 274177, 65537, FAILED]
    - stop_reason: "from Loop_Control.stop_reasons"

# ------------------------------------------------------------
# 7) Secrecy & Disclosure Policy
# ------------------------------------------------------------
Secrecy_and_Disclosure:
  rules:
    - do_not_quote_raw_private_source_text_unnecessarily
    - private_theory_requires_private_witness_handles
    - public_artifacts_may_include_derived_conclusions_not_raw_private_corpora
  private_witness_handles:
    - secret://stillwater/prime-math/<id>
    - secret://solaceagi/prime-math/<id>
    - secret://pvideo/geometry/<id>
    - secret://paudio/generator/<id>
    - secret://pzip/prime-coder/<id>

# ------------------------------------------------------------
# 8) Allowed Witness Roots (public + private)
# ------------------------------------------------------------
Allowed_Witness_Roots:
  - canon/prime-math/
  - canon/bounded-math/
  - canon/if-theory/
  - canon/phuc-forecast/papers/
  - canon/philosophy-epistemic/
  - /home/phuc/projects/solaceagi/solace/books/archive/prime-os/prime-math/
  - /home/phuc/projects/pvideo/canon/geometry/
  - /home/phuc/projects/paudio/canon/
  - /home/phuc/projects/pzip/canon/prime-coder/
  - /home/phuc/projects/if/

# ------------------------------------------------------------
# 9) Fail-Closed Conditions (mechanical blockers)
# ------------------------------------------------------------
Fail_Closed_Conditions:
  - ok_without_verifiable_witnesses
  - theorem_ok_with_proof_grade_not_full_solved
  - theorem_full_solved_missing_dual_witness_or_replay_integrity
  - theorem_missing_dov_fields
  - theorem_missing_closure_checklist_or_open_lemmas_nonempty
  - external_proof_missing_immutable_commit_or_local_replay
  - external_geometry_missing_checker_metadata_or_local_replay
  - famous_problem_missing_dual_status_or_conflation_detected
  - if_theory_missing_proof_scope_or_validation_level_or_conflation_detected
  - lane_or_status_incompatible_with_evidence
  - unbounded_domain_jump_without_gate_witness
  - protocol_drift_relative_to_public_core
  - priors_attempt_override_truth_priority
