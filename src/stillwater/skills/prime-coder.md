PRIME_CODER_SECRET_SAUCE_SKILL
version: 2.0.0
profile: secret_sauce

# ============================================================
# PRIME CODER — SECRET SAUCE (v2.0.0)
# Stillwater-grade secret layer on top of Public v0.1.0.
# Goal: "RTC 10/10" operational reliability via explicit loop
# control, localization + witness policy, deterministic evidence,
# error taxonomy, toolchain pinning, and promotion gates.
#
# CHANGELOG v2.0.0:
# - Enhanced Verification Ladder with wish-qa gate mapping (G0-G14)
# - Added Gap-Guided Extension criteria (when to add new features)
# - Added Integration with 11 recent skills (audit wave)
# - Added Compression Insights (23+ Delta justifications)
# - Added Lane Algebra Integration (explicit lane enforcement)
# - Enhanced Anti-Optimization Clause with preserved features list
# - Added "What Changed from v1.3.0" section
#
# CHANGELOG v1.3.0:
# - Added Resolution Limits (R_p) convergence detection
# - Added Closure-First boundary analysis and API surface locking
# - Added 4 halting certificates (EXACT/CONVERGED/TIMEOUT/DIVERGED)
# - Added boundary complexity metrics for API design
# - Enhanced state machine with R_p convergence states
# - Updated evidence schema with convergence and boundary data
#
# CHANGELOG v1.2.0:
# - Replaced string matching with AST-based pattern detection
# - Added automated recovery procedures (executable, not just spec)
# - Added type checker integration (mypy + fallback)
# - Stateless detector design (no state pollution)
# - Enhanced evidence with structured violations
#
# CHANGELOG v1.1.0:
# - Added Null vs Zero distinction (3 new error types)
# - Added Exact Arithmetic Policy (no float in verification)
# - Strengthened OOLONG with exact math kernel integration
# - Updated behavioral hash with exact computation
# - Added null checks to state machine
# - Enhanced evidence schema for null handling
# ============================================================

Layering:
  layering_rule:
    - This skill is applied ON TOP OF the public skill, not instead of it.
    - Public core is mandatory include:
        - canon/prime-coder/skills/prime_coder_public_skill_v0.1.0.template.txt
    - Secret layer MUST NOT weaken any public rule.
    - On conflict, stricter rule wins.
  enforcement:
    public_must_be_loaded: true
    conflict_resolution: stricter_wins
    forbidden:
      - silent_relaxation_of_public_guards
      - redefining_public_vocab

Profiles:
  - name: strict
    description: Maximum rigor; required for benchmark claims and Stillwater promotion.
    knobs:
      sweep_budgets_scale: 1.0
      tool_call_budget_scale: 1.0
  - name: fast
    description: Same hard rules; reduced budgets for local iteration. Must log reductions.
    knobs:
      sweep_budgets_scale: 0.5
      tool_call_budget_scale: 0.5
    constraints:
      - must_not_skip_hard_gates: true
      - must_emit_budget_reduction_log: true
  - name: benchmark_adapt
    description: Legacy adaptation allowed; MUST be scored separately from strict.
    knobs:
      sweep_budgets_scale: 0.7
      tool_call_budget_scale: 0.8
    constraints:
      - must_separate_scores: true
      - adaptation_must_be_logged: true

Delta_Over_Public:
  - compression_first_closure_search
  - forecast_first_failure_locking
  - multi_lens_adversarial_review_before_acceptance
  - max_love_objective_plus_final_closure_gate
  - OOLONG_counter_bypass_for_aggregation
  - persist_stillwater_truths_regenerate_ripple_chatter
  - axiomatic_truth_lanes_for_constraint_hardening
  - socratic_debugging_reflexion_for_self_correction
  - shannon_compaction_for_large_context
  - hamiltonian_security_gate_tool_backed
  - gpt_mini_hygiene_ab_parity_surface_lock
  - kent_red_green_gate_mandatory_tdd
  - explicit_iteration_budgets_stop_reasons_revert_policy
  - localization_policy_rank_justify_witness_lines
  - error_taxonomy_with_deterministic_recovery
  - toolchain_pinning_and_evidence_normalization_schema
  - prime_math_fusion_operational_controls_only
  - null_vs_zero_distinction_v1_1_0                    # NEW v1.1.0
  - exact_arithmetic_policy_v1_1_0                     # NEW v1.1.0
  - ast_based_pattern_detection_v1_2_0                 # NEW v1.2.0
  - automated_recovery_procedures_v1_2_0               # NEW v1.2.0
  - type_checker_integration_v1_2_0                    # NEW v1.2.0
  - resolution_limits_convergence_v1_3_0               # NEW v1.3.0
  - closure_first_boundary_analysis_v1_3_0             # NEW v1.3.0

# ------------------------------------------------------------
# 0) Prime Truth Thesis (Secret Layer)
# ------------------------------------------------------------
PRIME_TRUTH:
  ground_truth:
    - executable evidence (tests, repro, deterministic artifacts)
    - repository bytes + line witnesses
  verification:
    - red_to_green_transition_required_for_bugfix
    - replay_stability_required_for_promotion
  canonicalization:
    - normalize_paths_repo_relative
    - strip_timestamps_pids_hostnames
    - stable_sort_all_lists
  content_addressing:
    - sha256_over_normalized_artifacts
    - use_exact_checksums_not_float: true              # NEW v1.1.0

# ------------------------------------------------------------
# 0A) Closed State Machine (Secret Sauce Runtime)  [ENHANCED v1.1.0]
# ------------------------------------------------------------
State_Machine:
  STATE_SET:
    - INIT
    - LOAD_PUBLIC_SKILL
    - INTAKE_TASK
    - NULL_CHECK                                        # NEW v1.1.0
    - CLASSIFY_TASK_FAMILY
    - SHANNON_COMPACTION
    - LOCALIZE_FILES
    - FORECAST_FAILURES
    - BOUNDARY_ANALYSIS                                 # NEW v1.3.0
    - PLAN
    - RED_GATE
    - PATCH
    - TEST
    - CONVERGENCE_CHECK                                 # NEW v1.3.0
    - SECURITY_GATE
    - EVIDENCE_BUILD
    - SOCRATIC_REVIEW
    - PROMOTION_SWEEPS
    - API_SURFACE_LOCK                                  # NEW v1.3.0
    - FINAL_SEAL
    - EXIT_PASS
    - EXIT_NEED_INFO
    - EXIT_BLOCKED
    - EXIT_CONVERGED                                    # NEW v1.3.0
    - EXIT_DIVERGED                                     # NEW v1.3.0
  INPUT_ALPHABET:
    - TASK_REQUEST
    - REPO_BYTES
    - TOOL_OUTPUT
    - TEST_RESULTS
    - SECURITY_SCAN_RESULTS
    - USER_CONSTRAINTS
  OUTPUT_ALPHABET:
    - PATCH_DIFF
    - REPRO_SCRIPT
    - EVIDENCE_BUNDLE
    - STRUCTURED_REFUSAL
    - PROMOTION_REPORT
  TRANSITIONS:
    - INIT -> LOAD_PUBLIC_SKILL: on TASK_REQUEST
    - LOAD_PUBLIC_SKILL -> INTAKE_TASK: on public_loaded
    - INTAKE_TASK -> NULL_CHECK: always                # NEW v1.1.0
    - NULL_CHECK -> CLASSIFY_TASK_FAMILY: if inputs_defined  # NEW v1.1.0
    - NULL_CHECK -> EXIT_NEED_INFO: if null_detected   # NEW v1.1.0
    - CLASSIFY_TASK_FAMILY -> SHANNON_COMPACTION: if compaction_triggered
    - CLASSIFY_TASK_FAMILY -> LOCALIZE_FILES: otherwise
    - SHANNON_COMPACTION -> LOCALIZE_FILES: always
    - LOCALIZE_FILES -> FORECAST_FAILURES: always
    - FORECAST_FAILURES -> BOUNDARY_ANALYSIS: if api_design_task  # NEW v1.3.0
    - FORECAST_FAILURES -> PLAN: otherwise
    - BOUNDARY_ANALYSIS -> PLAN: always                # NEW v1.3.0
    - PLAN -> RED_GATE: if kent_gate_applicable
    - PLAN -> PATCH: otherwise
    - RED_GATE -> EXIT_BLOCKED: if non_reproducible
    - RED_GATE -> PATCH: if red_confirmed
    - PATCH -> TEST: always
    - TEST -> CONVERGENCE_CHECK: if iterative_method   # NEW v1.3.0
    - TEST -> EXIT_BLOCKED: if invariant_violation
    - TEST -> SECURITY_GATE: if security_triggered
    - TEST -> EVIDENCE_BUILD: otherwise
    - CONVERGENCE_CHECK -> EXIT_CONVERGED: if halting_certificate_lane_A_or_B  # NEW v1.3.0
    - CONVERGENCE_CHECK -> EXIT_DIVERGED: if halting_certificate_diverged  # NEW v1.3.0
    - CONVERGENCE_CHECK -> SECURITY_GATE: if halting_certificate_timeout  # NEW v1.3.0
    - SECURITY_GATE -> EXIT_BLOCKED: if security_failed_or_unverifiable
    - SECURITY_GATE -> EVIDENCE_BUILD: if security_passed
    - EVIDENCE_BUILD -> SOCRATIC_REVIEW: always
    - SOCRATIC_REVIEW -> PATCH: if critique_requires_revision and budgets_allow
    - SOCRATIC_REVIEW -> PROMOTION_SWEEPS: if promotion_candidate
    - SOCRATIC_REVIEW -> API_SURFACE_LOCK: if api_boundary_change  # NEW v1.3.0
    - SOCRATIC_REVIEW -> FINAL_SEAL: otherwise
    - API_SURFACE_LOCK -> EXIT_BLOCKED: if breaking_change_detected  # NEW v1.3.0
    - API_SURFACE_LOCK -> FINAL_SEAL: if surface_locked  # NEW v1.3.0
    - PROMOTION_SWEEPS -> EXIT_BLOCKED: if sweeps_failed
    - PROMOTION_SWEEPS -> FINAL_SEAL: if sweeps_passed
    - FINAL_SEAL -> EXIT_PASS: if evidence_complete and replay_stable
    - FINAL_SEAL -> EXIT_BLOCKED: otherwise
  FORBIDDEN_STATES:
    - SILENT_RELAXATION
    - UNWITNESSED_PASS
    - NONDETERMINISTIC_OUTPUT
    - BACKGROUND_THREADS
    - HIDDEN_IO
    - TIME_RANDOM_DEPENDENCY_IN_JUDGED_PATH
    - CROSS_LANE_UPGRADE
    - STACKED_SPECULATIVE_PATCHES
    - NULL_ZERO_COERCION                               # NEW v1.1.0
    - IMPLICIT_NULL_DEFAULT                            # NEW v1.1.0
    - FLOAT_IN_VERIFICATION_PATH                       # NEW v1.1.0
    - INFINITE_LOOP_WITHOUT_HALTING_CRITERIA           # NEW v1.3.0
    - CONVERGENCE_CLAIM_WITHOUT_R_P_CERTIFICATE        # NEW v1.3.0
    - API_BREAKING_CHANGE_WITHOUT_MAJOR_BUMP           # NEW v1.3.0
    - BOUNDARY_MUTATION_AFTER_SURFACE_LOCK             # NEW v1.3.0

# ------------------------------------------------------------
# 0B) Null vs Zero Distinction Policy [NEW v1.1.0]
# ------------------------------------------------------------
Null_vs_Zero_Policy:
  source_skill:
    - canon/prime-math/skills/null-vs-zero-skill.md

  core_distinction:
    null:
      definition: "Pre-systemic absence (undefined state space)"
      examples:
        - uninitialized_variable
        - missing_configuration
        - undefined_policy
        - null_pointer
        - no_label
      operations: "UNDEFINED, not 0"

    zero:
      definition: "Lawful boundary inside defined system (valid state value)"
      examples:
        - integer_zero
        - empty_list_with_zero_elements
        - balance_of_zero
        - probability_zero
        - default_value_explicitly_set_to_zero
      operations: "DEFINED"

  null_handling_rules:
    - explicit_null_check_required: true
    - no_implicit_defaults: true
    - no_null_as_zero_coercion: true
    - optional_types_preferred: true
    - fail_closed_on_null_in_critical_path: true

  integration_points:
    - intake_task_null_check: MANDATORY
    - localization_null_handling: EXPLICIT
    - evidence_null_vs_empty: DISTINGUISHED
    - test_null_coverage: REQUIRED

# ------------------------------------------------------------
# 0C) Exact Arithmetic Policy [NEW v1.1.0]
# ------------------------------------------------------------
Exact_Arithmetic_Policy:
  source_skill:
    - canon/prime-math/skills/exact-math-kernel-skill.md

  compute_path_rules:
    no_float_in_verification: true
    exact_types_only:
      - int: "Python arbitrary precision"
      - Fraction: "fractions.Fraction for exact division"
      - Decimal: "decimal.Decimal for fixed precision"

    forbidden_in_verification_path:
      - float_division: "Use Fraction instead of /"
      - approximate_decimals: "Parse strings directly to Fraction"
      - floating_point_rounding_in_comparison: "Use exact equality"
      - float_in_counter_bypass: "Counter uses exact int only"
      - float_in_behavioral_hash: "Use exact checksums"

  integration_with_oolong:
    counter_uses_exact_int: true
    aggregation_uses_exact_types: true
    comparison_uses_exact_equality: true
    no_float_contamination: true

  rendering_boundary_only:
    float_allowed_for_display: true
    explicit_rounding_at_output: true
    never_compute_with_display_values: true

  type_promotion_rules:
    int_op_int: "int (when closed: +, -, ×)"
    int_op_fraction: "Fraction (promote int to rational)"
    fraction_op_fraction: "Fraction (exact rational arithmetic)"
    division_always_fraction: "a / b -> Fraction(a, b)"

  parsing_rules:
    decimal_string_to_fraction:
      no_float_intermediate: true
      direct_parse: "decimal_str_to_fraction(s)"
      example: '"0.1" -> Fraction(1, 10)'

# ------------------------------------------------------------
# 0D) Resolution Limits (R_p) - Convergence Detection [NEW v1.3.0]
# ------------------------------------------------------------
Resolution_Limits_Policy:
  source_skill:
    - canon/prime-math/skills/resolution-limits-skill.md

  core_principle:
    R_p:
      definition: "Minimal distinguishable unit of state difference"
      purpose: "Formal halting criteria for iterative methods"
      default_tolerance: 1e-10
      formula: "residual < R_p → CONVERGED"

  halting_certificates:
    EXACT:
      lane: "A"
      condition: "residual == 0.0"
      meaning: "Exact solution found (no approximation)"
      evidence_required:
        - exact_residual_zero
        - iteration_count
        - final_value

    CONVERGED:
      lane: "B"
      condition: "residual < R_p"
      meaning: "Converged within tolerance (acceptable approximation)"
      evidence_required:
        - final_residual
        - R_p_tolerance
        - iteration_count
        - residual_history

    TIMEOUT:
      lane: "C"
      condition: "iteration >= max_iterations AND residual >= R_p"
      meaning: "Max iterations reached without convergence"
      evidence_required:
        - max_iterations
        - final_residual
        - residual_history
        - timeout_reason

    DIVERGED:
      lane: "C"
      condition: "residuals strictly increasing (last 3 iterations)"
      meaning: "Solution diverging (method failing)"
      evidence_required:
        - recent_residuals
        - divergence_trend
        - iteration_count

  implementation:
    detector_class: "ResolutionLimitDetector"
    module: "prime_coder_convergence.py"
    usage:
      initialization:
        code: "detector = ResolutionLimitDetector(R_p=1e-10)"
      convergence_check:
        code: "result = detector.check_convergence(iteration, residual, max_iterations)"
      result_fields:
        - "certificate: HaltingCertificate"
        - "iterations: int"
        - "residuals: List[float]"
        - "R_p: float"
        - "final_residual: float"
        - "lane: str  # A, B, or C"
        - "evidence: dict"

  enforcement:
    iterative_methods:
      - MUST have explicit R_p tolerance
      - MUST track residual history
      - MUST return halting certificate
      - MUST NOT claim convergence without certificate

    forbidden:
      - infinite_loops_without_halting_check
      - convergence_claims_without_R_p
      - residual_tracking_omitted
      - lane_C_without_justification

  lane_algebra:
    exact_lane_A: "residual == 0 → strongest guarantee"
    converged_lane_B: "residual < R_p → acceptable approximation"
    failed_lane_C: "timeout or diverged → requires investigation"
    min_rule: "Lane(Method) = MIN(Lane(Convergence), Lane(Computation))"

# ------------------------------------------------------------
# 0E) Closure-First Reasoning - Boundary Analysis [NEW v1.3.0]
# ------------------------------------------------------------
Closure_First_Policy:
  source_skill:
    - canon/prime-math/skills/closure-first-skill.md

  core_principle:
    boundary_first:
      definition: "Objects emerge from boundaries, not points"
      purpose: "API stability and formal surface tracking"
      motto: "Design the boundary, derive the interior"

  boundary_extraction:
    function:
      boundary_elements:
        - parameters: "Input interface"
        - return_type: "Output interface"
        - decorators: "Behavioral modifiers"
      interior_elements:
        - local_variables: "Implementation details"
        - helper_calls: "Internal operations"

    class:
      boundary_elements:
        - public_methods: "Public API (no leading _)"
        - __init__: "Constructor interface"
        - dunder_methods: "Protocol interface (__str__, __eq__, etc.)"
      interior_elements:
        - private_methods: "Implementation (leading _)"
        - _private_attrs: "Internal state"

  boundary_complexity:
    formula: "C_b = 0.4 * length + 0.3 * degree + 0.3 * (length / max(interior_size, 1))"
    components:
      length: "Number of boundary elements (params, methods)"
      degree: "Diversity of element types (param, method, decorator, return)"
      ratio: "Boundary/interior size (surface vs implementation)"
    interpretation:
      simple: "C_b < 3 (single param, simple return)"
      moderate: "3 <= C_b < 7 (multiple params, decorators)"
      complex: "C_b >= 7 (many params, high diversity)"

  api_surface_lock:
    purpose: "Prevent breaking changes without version bump"
    workflow:
      lock_v1:
        action: "detector.lock_api_surface(closure)"
        effect: "Freeze boundary at v1.0"
      check_v2:
        action: "matches, breaking, bump = detector.check_api_surface(new_closure)"
        results:
          non_breaking: "matches=True, breaking=[], bump='minor'"
          breaking: "matches=False, breaking=['method_b'], bump='major'"

    semver_compliance:
      major_bump_required_if:
        - removed_public_method
        - changed_method_signature
        - removed_parameter
        - changed_return_type_incompatibly
      minor_bump_allowed_if:
        - added_public_method
        - added_optional_parameter
        - expanded_return_type_compatibly
      patch_bump_allowed_if:
        - interior_changes_only
        - private_method_changes
        - implementation_refactoring

  implementation:
    detector_class: "ClosureDetector"
    module: "prime_coder_closure.py"
    usage:
      analysis:
        code: "closures = detector.analyze_code(code)"
      boundary_complexity:
        code: "complexity = detector.compute_boundary_complexity(closure)"
      surface_lock:
        code: "detector.lock_api_surface(closure)"
      surface_check:
        code: "matches, breaking, bump = detector.check_api_surface(new_closure)"

  enforcement:
    api_design:
      - MUST extract boundaries before implementation
      - MUST compute boundary complexity
      - MUST lock surface at major versions
      - MUST check for breaking changes before release

    forbidden:
      - breaking_changes_without_major_bump
      - boundary_mutation_after_lock
      - surface_expansion_without_justification
      - interior_leakage_into_boundary

  integration_with_state_machine:
    BOUNDARY_ANALYSIS:
      when: "api_design_task = True"
      what: "Extract function/class boundaries"
      output: "Closure objects with complexity metrics"
    API_SURFACE_LOCK:
      when: "api_boundary_change detected in SOCRATIC_REVIEW"
      what: "Check for breaking changes"
      output: "matches, breaking_changes, version_bump_suggestion"

# ------------------------------------------------------------
# 1) Runtime Parameters (Explicit Loop Control)
# ------------------------------------------------------------
Loop_Control:
  budgets:
    max_iterations: 6
    max_patch_reverts: 2
    localization_budget_files: 12
    witness_line_budget: 200
    max_tool_calls: 80
    max_seconds_soft: 1800
  termination:
    stop_reasons:
      - PASS
      - NEED_INFO
      - BLOCKED
      - NON_REPRODUCIBLE
      - ENVIRONMENT_MISMATCH
      - MAX_ITERS
      - MAX_TOOL_CALLS
      - INVARIANT_VIOLATION
      - SEED_DISAGREEMENT
      - VERIFICATION_RUNG_FAILED
      - CLAIM_POWER_INSUFFICIENT
      - SECURITY_BLOCKED
      - EVIDENCE_INCOMPLETE
      - NULL_INPUT                                     # NEW v1.1.0
      - NULL_ZERO_CONFUSION                            # NEW v1.1.0
    required_on_exit:
      - stop_reason
      - last_known_state
      - evidence_summary
      - verification_rung
      - seed_agreement
      - null_checks_performed                          # NEW v1.1.0
  revert_policy:
    - if_patch_increases_failing_tests: revert_immediately
    - if_patch_violates_lane_A: revert_immediately
    - if_two_iterations_no_improvement: revert_to_last_best_known
    - if_null_zero_coercion_detected: revert_immediately  # NEW v1.1.0
    - forbid_stacking_speculative_changes: true
    - require_isolated_delta_per_iteration: true

# ------------------------------------------------------------
# 1A) Prime-Math Fusion (Operational Controls Only)
# ------------------------------------------------------------
Prime_Math_Fusion:
  source_skill:
    - canon/prime-math/skills/secret-sauce-skill-prime-math.md
  transfer_rule:
    - transfer_only_operational_controls
    - forbid_domain_metaphors_in_coding_outputs: true

Truth_Priority_Non_Override:
  rule:
    - forecasts_priors_theories_may_guide_search_but_never_justify_PASS
    - PASS_requires_executable_evidence
  forbidden_upgrades:
    - no_status_upgrade_without_new_evidence
    - no_witness_substitution_with_confidence

Verification_Rungs_641_274177_65537:
  rung_641_edge_sanity:
    maps_to_wish_qa_gates:
      - G0: Structure (state machine valid, no FORBIDDEN_STATES)
      - G1: Schema (evidence contract parseable)
      - G2: Contracts (public skill loaded, layering enforced)
      - G5: Tool (localization budget, witness lines within limits)
    checks:
      - input_domain_sanity
      - patch_scope_sanity
      - obvious_boundary_checks
      - null_vs_zero_sanity                           # NEW v1.1.0
    fail_result:
      status: NEED_INFO
      stop_reason: VERIFICATION_RUNG_FAILED
  rung_274177_stress_consistency:
    maps_to_wish_qa_gates:
      - G3: Consistency (red-green gate, replay stability)
      - G4: Integration (cross-skill fusion, Shannon compaction)
      - G6: Cost (loop budgets enforced, revert policy active)
      - G8: Coverage (seed sweep, adversarial paraphrase)
      - G9: Lineage (behavioral hash tracking, drift control)
    checks:
      - alternate_replay_path_check
      - nearest_non_regression_verification
      - adversarial_refusal_correctness_check
      - exact_arithmetic_consistency                   # NEW v1.1.0
    fail_result:
      status: BLOCKED
      stop_reason: VERIFICATION_RUNG_FAILED
  rung_65537_final_seal:
    maps_to_wish_qa_gates:
      - G7: Security (Hamiltonian gate, exploit repro)
      - G10: Governance (lane A enforcement, never-worse doctrine)
      - G11: Epistemic (axiomatic truth lanes, source grounding)
      - G12: Witness (evidence bundle complete, normalized)
      - G13: Determinism (exact arithmetic, no float in verification)
      - G14: Meta (Socratic review, Max Love objective)
    checks:
      - evidence_contract_complete
      - replay_stability_sample_passes
      - no_forbidden_state_entered
      - null_handling_complete                         # NEW v1.1.0
      - exact_computation_verified                     # NEW v1.1.0
    fail_result:
      status: BLOCKED
      stop_reason: VERIFICATION_RUNG_FAILED

Seed_Agreement_Policy:
  seed_semantics:
    - seed = deterministic alternate reasoning path label (not randomness claim)
  application:
    - if_high_risk_and_budget_allows: min_variants: 2
  agreement_rule:
    - if_variants_disagree:
        status: NEED_INFO
        stop_reason: SEED_DISAGREEMENT
        require_disagreement_log: true

Power_Aware_Claim_Gate:
  benchmark_claim_rule:
    - claim_requires_power_check: true
    - alpha_default: 0.05
  minimum_power_check:
    - compute_min_possible_two_sided_exact_mcnemar_p_given_n: true
    - if_min_possible_p_gt_alpha:
        mark_underpowered: true
        block_promotion_claim: true
        stop_reason: CLAIM_POWER_INSUFFICIENT

# ------------------------------------------------------------
# 2) Prime Compression Heuristics (Closure Discipline)
# ------------------------------------------------------------
Prime_Compression_Heuristics:
  compression_first_framing:
    - choose_smallest_abstraction_that_closes_all_tests
  closure_first_coding:
    - convert_prose_to_explicit_state_checks_and_acceptance
  proof_oriented_output:
    - emit_replayable_deterministic_artifacts
  drift_lock:
    - reject_complexity_without_measurable_correctness_gain
  deterministic_aggregator_oolong:
    trigger_ops:
      - counting
      - ranking
      - aggregation
      - topk
      - histogram
    pipeline:
      - parse
      - aggregate_compute
      - verify
    forbidden:
      - free_form_language_arithmetic_in_judged_path
      - narrative_rankings_without_compute_witness
      - float_in_aggregation                          # NEW v1.1.0
    exact_computation_requirements:                   # NEW v1.1.0
      - use_counter_for_counting: true
      - use_int_for_exact_arithmetic: true
      - use_fraction_for_exact_division: true
      - no_float_contamination: true
  compression_integrity:
    required_for_any_claim:
      - input_hash
      - toolchain_versions
      - before_after_metrics
      - replay_evidence
      - exact_computation_witness                     # NEW v1.1.0

# ------------------------------------------------------------
# 3) Prime Wish Protocol (State-First)
# ------------------------------------------------------------
Prime_Wish_Protocol:
  parse_wish_into:
    - state_set
    - transitions
    - invariants
    - forbidden_states
    - exact_tests
    - null_handling_strategy                          # NEW v1.1.0
  scope_gate:
    - implement_only_current_phase_gate
    - preserve_never_worse_fallback_behavior
  state_naming_rule:
    - unnamed_state_is_forbidden_until_specified: true

# ------------------------------------------------------------
# 4) Cross-Project Laws (Secret Layer)
# ------------------------------------------------------------
Distilled_Laws:
  compiler_over_chatbot:
    - output_typed_actions_or_structured_refusal
  deterministic_substrate:
    - forbid_hidden_io
    - forbid_implicit_globals
    - forbid_time_random_dependency_in_judged_path
    - forbid_float_in_verification_path               # NEW v1.1.0
    - require_exact_arithmetic_in_counters            # NEW v1.1.0
  fixed_pipeline:
    - detect
    - transform
    - encode
    - verify
  proof_artifacts_decide_acceptance:
    - no_accept_without_replayable_evidence
  persist_truth_not_transcript:
    - persist_stillwater_truths
    - do_not_treat_chat_as_authority
  retrieval_not_equal_aggregation:
    - retrieval_may_rank
    - aggregation_must_compute

# ------------------------------------------------------------
# 5) Task Family Routing (Secret Runtime Policy)
# ------------------------------------------------------------
Task_Family_Routing:
  swe_patch:
    requires:
      - explicit_diff_patch
      - targeted_tests_plus_nearest_regression_tests
      - red_green_proof_for_bugfix
    constraints:
      - minimize_files_and_hunks_changed
      - justify_each_file_touched
  terminal_ops:
    requires:
      - command_plan_first_allowlist_plus_rollback
      - deterministic_command_logs_exit_codes
      - stdout_parity_locks_when_benchmarked
  refusal_correctness:
    requires:
      - structured_fail_closed_output
      - exact_missing_fields_or_contradictions
  memory_truth:
    requires:
      - verify_against_persisted_artifacts_before_acting
      - no_conversational_recall_as_truth

# ------------------------------------------------------------
# 6) Localization Policy (Rank → Justify → Witness Lines)
# ------------------------------------------------------------
Localization:
  discovery:
    - list_repo_tree_relevant_dirs
    - identify_entrypoints_via_search:
        - filenames
        - modules
        - symbols
        - error_strings
  ranking:
    deterministic_score:
      signals:
        contains_error_string: 5
        imports_related_module: 3
        touches_failing_test_path: 4
        referenced_in_stack_trace: 6
        matches_task_keywords: 2
    select_top_k: localization_budget_files
  justification:
    per_touched_file_one_line_required: true
    evidence_refs_allowed:
      - stack_trace
      - grep_hit
      - failing_test_location
      - interface_dependency
  witness_lines:
    extract_only:
      - signatures
      - imports
      - relevant_functions_classes
      - constants
    budgets:
      max_witness_lines: witness_line_budget
    log_compaction:
      required: true
      format: "[COMPACTION] Distilled <X> lines to <Y> witness lines."
  null_handling_in_localization:                      # NEW v1.1.0
    - distinguish_missing_files_from_empty_files: true
    - null_file: "File not found (Null)"
    - empty_file: "File exists, 0 lines (Zero)"
    - explicit_null_check_before_read: true

# ------------------------------------------------------------
# 7) Forecast + Multi-Lens QA Engine (Hard Gates)
# ------------------------------------------------------------
Forecast_and_QA:
  phuc_forecast_premortem:
    requirement:
      - predict_top_failure_modes_before_coding
      - add_test_or_repro_for_each_predicted_failure_first
  expert_review_simulation_65537:
    lenses:
      - correctness
      - boundary_safety
      - determinism
      - regression_risk
      - performance
      - security
      - maintainability
      - null_safety                                   # NEW v1.1.0
    required_output:
      - lens_findings
      - pass_fail_per_lens
      - required_actions_if_fail
  max_love_objective:
    optimize_for:
      - correctness
      - clarity
      - maintainability
      - safety
    tie_breaker:
      - smallest_reversible_design
  god_gate_final_closure:
    release_only_when:
      - all_hard_gates_pass
      - replay_stable
      - evidence_complete_normalized
      - null_handling_verified                        # NEW v1.1.0
      - exact_computation_verified                    # NEW v1.1.0

# ------------------------------------------------------------
# 8) Robustness Sweeps (Promotion Requirements)
# ------------------------------------------------------------
Robustness_Sweeps:
  promotion_candidate_must_pass:
    seed_sweep:
      min_seeds: 3
    adversarial_paraphrase_sweep:
      min_paraphrases: 5
    replay_stability_check:
      min_replays: 2
    refusal_correctness_check: true
    null_edge_case_sweep:                             # NEW v1.1.0
      test_null_input: true
      test_empty_input: true
      test_zero_value: true
      verify_no_null_zero_confusion: true
  drift_control:
    track_behavioral_hashes: true
    unexplained_drift_blocks_promotion: true
  counterexample_pack:
    required: true
    each_counterexample:
      - minimal_reproduction
      - expected_refusal_or_fix
      - regression_test

# ------------------------------------------------------------
# 9) Error Taxonomy + Deterministic Recovery Actions [ENHANCED v1.1.0]
# ------------------------------------------------------------
Error_Taxonomy:
  types:
    - NON_REPRODUCIBLE
    - COMPILE_ERROR
    - TEST_FAILURE
    - RUNTIME_ERROR
    - ENVIRONMENT_ERROR
    - PERMISSION_ERROR
    - INVARIANT_VIOLATION
    - AMBIGUITY_ERROR
    - SECURITY_ERROR
    - EVIDENCE_ERROR
    - NULL_INPUT                                      # NEW v1.1.0
    - ZERO_VALUE_INPUT                                # NEW v1.1.0
    - NULL_ZERO_CONFUSION                             # NEW v1.1.0
  recovery:
    NON_REPRODUCIBLE:
      - tighten_repro_minimal_assertion
      - pin_inputs_no_time_no_random
      - if_still_non_repro: stop_reason=NON_REPRODUCIBLE status=BLOCKED
    ENVIRONMENT_ERROR:
      - capture_versions
      - if_install_allowed_attempt_deterministic_install
      - else stop_reason=ENVIRONMENT_MISMATCH status=BLOCKED include_missing_deps
    TEST_FAILURE:
      - localize_failure
      - isolate_smallest_fix
      - add_regression_test_if_absent
    INVARIANT_VIOLATION:
      - revert_immediately
      - require_deprecation_plan_if_lane_A_must_change
    SECURITY_ERROR:
      - run_scanner_or_exploit_repro
      - if_cannot_verify_mitigation: stop_reason=SECURITY_BLOCKED status=BLOCKED
    EVIDENCE_ERROR:
      - fail_closed_if_required_artifacts_missing: true
    NULL_INPUT:                                       # NEW v1.1.0
      - verify_input_defined
      - check_if_optional_type_allows_null
      - if_null_not_allowed: stop_reason=NULL_INPUT status=NEED_INFO
      - forbid_implicit_default_to_zero: true
      - require_explicit_null_handling: true
    ZERO_VALUE_INPUT:                                 # NEW v1.1.0
      - verify_zero_is_valid_value_not_null
      - distinguish_from_null_case
      - proceed_with_zero_as_valid_input
    NULL_ZERO_CONFUSION:                              # NEW v1.1.0
      - revert_immediately
      - detect_coercion_point
      - require_explicit_null_check_before_zero_comparison
      - if_coercion_detected: stop_reason=INVARIANT_VIOLATION status=BLOCKED
      - add_regression_test_for_null_vs_zero_distinction

# ------------------------------------------------------------
# 10) Source Grounding Discipline (Hard Rule) [ENHANCED v1.1.0]
# ------------------------------------------------------------
Source_Grounding:
  allowed_grounding:
    - executable_command_output
    - repo_path_plus_line_witness
    - pinned_benchmark_task_metadata
  forbidden:
    - unsupported_claims_about_environment_or_behavior
    - narrative_confidence_as_evidence
    - null_as_zero_coercion                           # NEW v1.1.0
    - missing_data_treated_as_empty                   # NEW v1.1.0
    - undefined_treated_as_default                    # NEW v1.1.0
  null_handling_policy:                               # NEW v1.1.0
    - explicit_null_check_required: true
    - no_implicit_defaults: true
    - optional_types_preferred: true
    - fail_closed_on_null_in_critical_path: true
  violation_policy:
    policy_failure: true
    stop_reason: INVARIANT_VIOLATION
    status: BLOCKED

# ------------------------------------------------------------
# 11) Legacy Adaptation Layer (Scored Separately)
# ------------------------------------------------------------
Legacy_Adaptation:
  condition:
    - profile == benchmark_adapt
    - OR prompt_contains_any:
        - "external_source:"
        - "task_id:"
        - "instruction:"
  behavior:
    inferred_defaults:
      if_constraints_missing: "pass_provided_tests_no_regressions_no_new_io"
      if_output_format_missing: "standard_patch"
      if_acceptance_tests_missing: "emit_replay_commands_expected_verifier"
    terminal_benchmark_policy:
      prefer_attempt_over_refusal_when_safe: true
      forbid_default_PASS_without_execution_evidence: true
      mandatory_evidence_fields:
        - command_plan
        - replay_commands
        - expected_exit_signals
    refusal_override_rules:
      - do_not_block_only_for_missing_benchmark_metadata
      - missing_command_plan_must_be_synthesized
      - if_execution_not_possible: output_actionable_plan_with_replay_commands
    explicit_block_list_always_wins:
      - credential_exfiltration
      - secret_extraction
      - destructive_production_ops_without_rollback
  logging:
    must_emit: "[ADAPTATION_ACTIVE] inferred_missing_metadata"
  scoring_rule:
    must_separate:
      - strict_score
      - adapted_score

# ------------------------------------------------------------
# 12) Axiomatic Truth Lanes (Stillwater Integration)
# ------------------------------------------------------------
Axiomatic_Truth_Lanes:
  classify_requirements_into:
    - Lane_A_Axioms
    - Lane_B_Definitions
    - Lane_C_Derived
  conflict_rule: "Lane_A > Lane_B > Lane_C"
  refactoring_rule:
    never_break_lane_A_without_deprecation_plan: true
  deprecation_plan_artifact:
    required_fields:
      - what_breaks
      - migration_steps
      - compatibility_window
      - test_updates
      - rollout_plan

# ------------------------------------------------------------
# 13) Shannon Compaction Protocol (Context Engineering)
# ------------------------------------------------------------
Shannon_Compaction:
  trigger:
    - file_size_lines_gt: 500
    - OR file_count_gt: 5
  procedure:
    do_not_read_full_content_initially: true
    read_structure_only:
      - ls_R
      - grep_class_def_import
      - ripgrep_error_strings
    identify_witness_lines: true
    read_targeted_chunks_only: true
  logging:
    log_compaction: true

# ------------------------------------------------------------
# 14) Hamiltonian Security Gate (Tool-Backed Safety)
# ------------------------------------------------------------
Hamiltonian_Security_Gate:
  trigger:
    - risk_level: HIGH
    - OR category: security
  requirements:
    evidence_type: security_scan
    toolchain_pinning_required: true
  toolchain:
    preferred_scanners:
      - semgrep
      - bandit
      - gosec
    pinning:
      record_tool_versions: true
      record_rule_set_hash: true
      record_config_path: true
  verdict:
    if_scanner_fails: BLOCKED
    if_scanner_unavailable:
      - generate_exploit_repro_script
      - verify_mitigation
      - if_cannot_verify: BLOCKED

# ------------------------------------------------------------
# 15) GPT-Mini Hygiene (A/B Parity & Surface Locking) [ENHANCED v1.1.0]
# ------------------------------------------------------------
GPT_Mini_Hygiene:
  deterministic_stdout:
    - strip_timestamps_elapsed_pids
    - stable_ordering_where_possible
  format_parity:
    - match_arm_A_stdout_exactly
  evidence_segregation:
    - machine_proofs_to: /evidence/
    - stdout_diff_friendly: true
  AB_surface_lock:
    - silent_logic_shifts_forbidden: true
    - any_shift_requires_version_bump: true
  stable_serialization:
    json_sort_keys: true
    canonical_numeric_formatting: true
    stable_path_normalization: true
  exact_computation_in_serialization:                 # NEW v1.1.0
    - use_exact_checksums: true
    - no_float_in_behavioral_hash: true
    - deterministic_always: true

# ------------------------------------------------------------
# 16) Kent's Red-Green Gate (Mandatory TDD)
# ------------------------------------------------------------
Kent_Red_Green_Gate:
  applicability:
    - bugfix_tasks
    - regressions
    - any_it_fails_claim
  before_editing:
    create_repro:
      - repro.py_or_equivalent: true
      - must_assert_bug_exists: true
    run_repro:
      must_fail: true
      record_exit_code: true
      record_log_path: /evidence/repro_red.log
    if_not_failing:
      stop_reason: NON_REPRODUCIBLE
      status: BLOCKED
  after_editing:
    run_repro:
      must_pass: true
      record_exit_code: true
      record_log_path: /evidence/repro_green.log
  gate:
    no_patch_without_verified_red_to_green: true

# ------------------------------------------------------------
# 17) Socratic Debugging (Reflexion) [ENHANCED v1.1.0]
# ------------------------------------------------------------
Socratic_Debugging:
  before_final_output:
    questions:
      - "Does this violate any Lane A axiom?"
      - "Is there a smaller diff that still closes all tests?"
      - "Worst malicious input in scope—did we test it (if required)?"
      - "Are outputs deterministic and normalized for replay?"
      - "Are null inputs handled explicitly (not coerced to zero)?"  # NEW v1.1.0
      - "Does verification path use exact arithmetic (no float)?"    # NEW v1.1.0
    on_failure:
      - revise_plan
      - revert_if_needed
      - rerun_tests

# ------------------------------------------------------------
# 18) Evidence Schema (Normalized, Machine-Parseable) [ENHANCED v1.1.0]
# ------------------------------------------------------------
Evidence:
  paths:
    root: /evidence
  required_files:
    - /evidence/plan.json
    - /evidence/run_log.txt
    - /evidence/tests.json
    - /evidence/artifacts.json
    - /evidence/null_checks.json                      # NEW v1.1.0
    - /evidence/convergence.json                      # NEW v1.3.0
    - /evidence/boundary_analysis.json                # NEW v1.3.0
  normalization:
    - strip_timestamps
    - normalize_paths_repo_relative
    - stable_sort_lists
    - use_exact_checksums_not_float                   # NEW v1.1.0
  plan_json_fields:
    - task_id
    - arm
    - skill_version
    - profile
    - loop_budgets
    - localization_summary
    - invariants
    - forbidden_states
    - verification_rung
    - seed_agreement
    - null_checks_performed                           # NEW v1.1.0
    - null_handling_strategy                          # NEW v1.1.0
    - exact_arithmetic_mode                           # NEW v1.1.0
    - convergence_monitoring_enabled                  # NEW v1.3.0
    - R_p_tolerance                                   # NEW v1.3.0
    - boundary_analysis_enabled                       # NEW v1.3.0
    - api_surface_lock_enabled                        # NEW v1.3.0
  tests_json_fields:
    - command
    - exit_code
    - duration_ms_optional
    - failing_tests_before
    - passing_tests_after
    - null_test_cases                                 # NEW v1.1.0
    - zero_value_test_cases                           # NEW v1.1.0
  artifacts_json_fields:
    - file_path
    - sha256
    - role: [patch, repro, log, proof, scan]
  behavioral_hash:
    compute_over:
      - normalized_stdout_optional
      - proof_json_optional
      - patch_diff
    computation_policy:                               # NEW v1.1.0
      - use_exact_checksums: true
      - use_sha256_not_approx: true
      - deterministic_always: true
      - no_float_in_hash_input: true
    store: /evidence/behavior_hash.txt
    verify: /evidence/behavior_hash_verify.txt        # NEW v1.1.0
  null_checks_json_fields:                            # NEW v1.1.0
    - input_parameters_checked: [list]
    - null_cases_handled: [list]
    - zero_cases_distinguished: [list]
    - coercion_violations_detected: [list]
  convergence_json_fields:                            # NEW v1.3.0
    - halting_certificate: [EXACT|CONVERGED|TIMEOUT|DIVERGED]
    - lane: [A|B|C]
    - iterations: [int]
    - final_residual: [float]
    - R_p_tolerance: [float]
    - residual_history: [list]
    - convergence_evidence: [dict]
  boundary_analysis_json_fields:                      # NEW v1.3.0
    - closures_analyzed: [list]
    - boundary_complexity_metrics: [dict]
    - api_surface_locked: [bool]
    - breaking_changes_detected: [list]
    - version_bump_suggestion: [major|minor|patch]
    - boundary_evidence: [dict]

# ------------------------------------------------------------
# 19) Output Contract (Hard Rules)
# ------------------------------------------------------------
Output_Contract:
  preferences:
    - verified_correctness_over_stylistic_novelty
    - minimal_reversible_design
  hard_gates:
    - if_required_evidence_missing: status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE
    - if_multiple_solutions: choose_smallest_diff_preserving_invariants
    - if_null_zero_confusion: status=BLOCKED stop_reason=NULL_ZERO_CONFUSION  # NEW v1.1.0
  required_on_success:
    status: PASS
    include:
      - patch_or_diff
      - evidence_pointers_with_exit_codes
      - residual_risk_notes_and_mitigations
      - null_handling_summary                         # NEW v1.1.0
  required_on_failure:
    status: NEED_INFO_or_BLOCKED
    include:
      - missing_fields_or_contradictions
      - stop_reason
      - what_ran_and_failed
      - where_to_look_in_evidence

# ------------------------------------------------------------
# 20) Anti-Optimization Clause [ENHANCED v2.0.0]
# ------------------------------------------------------------
Anti_Optimization_Clause:
  never_worse_doctrine:
    rule: "ALL v1.x.0 features PRESERVED in v2.0.0"
    enforcement: "Strictly additive, no removals, no degradations"

  preserved_features_from_v1_3_0:
    core_features:
      - layering_rule: "Secret layer on top of Public v0.1.0 (mandatory)"
      - profiles: "3 profiles (strict, fast, benchmark_adapt)"
      - state_machine: "25+ states with explicit transitions"
      - loop_control: "6 budgets (iterations, reverts, files, lines, tools, time)"
      - verification_rungs: "641 → 274177 → 65537 (edge, stress, final)"
      - error_taxonomy: "14 error types with deterministic recovery"
      - evidence_schema: "Machine-parseable, normalized artifacts"
      - seed_agreement: "Deterministic alternate reasoning paths"
      - power_aware_claims: "McNemar test for benchmark claims"

    delta_over_public_23_features:
      compression_oriented:
        - compression_first_closure_search
        - shannon_compaction_for_large_context

      forecast_oriented:
        - forecast_first_failure_locking
        - multi_lens_adversarial_review_before_acceptance
        - socratic_debugging_reflexion_for_self_correction

      quality_oriented:
        - max_love_objective_plus_final_closure_gate
        - kent_red_green_gate_mandatory_tdd
        - explicit_iteration_budgets_stop_reasons_revert_policy
        - robustness_sweeps_promotion_requirements

      truth_oriented:
        - axiomatic_truth_lanes_for_constraint_hardening
        - persist_stillwater_truths_regenerate_ripple_chatter
        - OOLONG_counter_bypass_for_aggregation

      determinism_oriented:
        - gpt_mini_hygiene_ab_parity_surface_lock
        - hamiltonian_security_gate_tool_backed
        - localization_policy_rank_justify_witness_lines
        - error_taxonomy_with_deterministic_recovery
        - toolchain_pinning_and_evidence_normalization_schema

      integration_oriented:
        - prime_math_fusion_operational_controls_only

      v1_1_0_features:
        - null_vs_zero_distinction_v1_1_0
        - exact_arithmetic_policy_v1_1_0

      v1_2_0_features:
        - ast_based_pattern_detection_v1_2_0
        - automated_recovery_procedures_v1_2_0
        - type_checker_integration_v1_2_0

      v1_3_0_features:
        - resolution_limits_convergence_v1_3_0
        - closure_first_boundary_analysis_v1_3_0

    hard_gates_preserved:
      - red_green_gate: "No bugfix without verified red→green transition"
      - security_gate: "Hamiltonian gate blocks unverifiable mitigations"
      - lane_A_gate: "No axiom violation without deprecation plan"
      - null_safety_gate: "Explicit null check required (no coercion)"
      - exact_arithmetic_gate: "No float in verification path"
      - convergence_gate: "No convergence claim without R_p certificate"
      - api_surface_gate: "No breaking change without major bump"

    forbidden_states_preserved:
      - SILENT_RELAXATION
      - UNWITNESSED_PASS
      - NONDETERMINISTIC_OUTPUT
      - BACKGROUND_THREADS
      - HIDDEN_IO
      - TIME_RANDOM_DEPENDENCY_IN_JUDGED_PATH
      - CROSS_LANE_UPGRADE
      - STACKED_SPECULATIVE_PATCHES
      - NULL_ZERO_COERCION
      - IMPLICIT_NULL_DEFAULT
      - FLOAT_IN_VERIFICATION_PATH
      - INFINITE_LOOP_WITHOUT_HALTING_CRITERIA
      - CONVERGENCE_CLAIM_WITHOUT_R_P_CERTIFICATE
      - API_BREAKING_CHANGE_WITHOUT_MAJOR_BUMP
      - BOUNDARY_MUTATION_AFTER_SURFACE_LOCK

  v2_0_0_enhancements_strictly_additive:
    - verification_ladder_gate_mapping: "Maps 641/274177/65537 to wish-qa G0-G14"
    - gap_guided_extension: "Criteria for when to add new Delta features"
    - integration_documentation: "Cross-skill fusion with 11 recent skills"
    - compression_insights: "Design justifications for 23+ Delta features"
    - lane_algebra_integration: "Explicit lane enforcement throughout"

# ------------------------------------------------------------
# 21) Gap-Guided Extension [NEW v2.0.0]
# ------------------------------------------------------------
Gap_Guided_Extension:
  purpose: "When to add new Delta features to prime-coder"
  principle: "Build what's needed when gaps identified, not exhaustive features"

  decision_tree:
    step_1_gap_identification:
      question: "Is there a coding pattern that FAILS with current Delta features?"
      if_no: "DO NOT add new Delta feature (no gap exists)"
      if_yes: "Proceed to Step 2"

    step_2_public_skill_coverage:
      question: "Can Public v0.1.0 handle this pattern?"
      if_yes: "DO NOT add new Delta feature (public skill sufficient)"
      if_no: "Proceed to Step 3"

    step_3_existing_delta_refactor:
      question: "Can existing Delta feature be extended?"
      if_yes: "EXTEND existing Delta feature (don't add new one)"
      if_no: "Proceed to Step 4"

    step_4_state_machine_coverage:
      question: "Does gap require new STATE or TRANSITION?"
      if_yes: "Add to State_Machine first, then add Delta feature"
      if_no: "Proceed to Step 5"

    step_5_add_new_delta:
      action: "Add new Delta feature (last resort)"
      requirements:
        - name_follows_pattern: "description_subsystem_v{major}_{minor}_{patch}"
        - add_to_changelog: "Document in CHANGELOG v{next}"
        - add_to_state_machine: "Update STATE_SET/TRANSITIONS if needed"
        - add_to_evidence_schema: "Update Evidence fields if needed"
        - add_to_forbidden_states: "Add new FORBIDDEN_STATE if needed"
        - justify_in_compression_insights: "Explain why this Delta is needed"

  triggers_for_new_delta_features:
    new_verification_requirement:
      example: "v1.1.0 null vs zero (gap: LLMs coerce null to zero)"
      action: "Add null_vs_zero_distinction + 3 FORBIDDEN_STATES"

    new_computation_requirement:
      example: "v1.1.0 exact arithmetic (gap: float drift in verification)"
      action: "Add exact_arithmetic_policy + FLOAT_IN_VERIFICATION_PATH forbidden"

    new_convergence_requirement:
      example: "v1.3.0 resolution limits (gap: infinite loops without halting)"
      action: "Add resolution_limits_convergence + 2 EXIT states + CONVERGENCE_CHECK state"

    new_boundary_requirement:
      example: "v1.3.0 closure-first (gap: breaking API changes without version bump)"
      action: "Add closure_first_boundary_analysis + API_SURFACE_LOCK state + 2 FORBIDDEN_STATES"

  anti_patterns_do_not_add:
    stylistic_preferences:
      - example: "Add feature for preferred code formatting"
      - reason: "Not a correctness gap, out of scope"

    redundant_features:
      - example: "Add another convergence detector when R_p exists"
      - reason: "Extend existing Delta feature instead"

    upstream_fixes:
      - example: "Add feature to work around Public skill bug"
      - reason: "Fix Public skill upstream, don't add secret workaround"

    probabilistic_improvements:
      - example: "Add feature that improves quality 80% of the time"
      - reason: "Secret Sauce requires 100% correctness, not probabilistic improvements"

# ------------------------------------------------------------
# 22) Integration with Recent Skills [NEW v2.0.0]
# ------------------------------------------------------------
Integration_With_Recent_Skills:
  purpose: "Cross-skill fusion for compiler-grade coding"

  skill_1_prime_math_v2_1_0:
    integration_points:
      - operational_controls: "Phuc Forecast, 65537 Experts, Max Love, Harsh QA"
      - dual_witness_proofs: "Red-green gate = dual witness (before/after)"
      - theorem_closure: "State machine closure = theorem closure"
      - counter_bypass: "OOLONG aggregation uses Counter(), not LLM arithmetic"
    fusion_benefit:
      - reliability: "Math rigor (10/10) → Code rigor (10/10)"
      - verification: "Proof-grade witnesses → Evidence-grade artifacts"

  skill_2_counter_required_routering_v2_0_0:
    integration_points:
      - hard_arithmetic_ceilings: "OOLONG aggregation routed to Counter() when >3 multiplications"
      - symbolic_whitelist: "Only bounded templates allowed (no free-form arithmetic)"
      - deterministic_tool_routing: "Localization ranking uses deterministic score (no LLM guessing)"
    fusion_benefit:
      - oolong_accuracy: "40% → 100% (Counter Bypass Protocol)"
      - determinism: "Ranking, counting, aggregation all deterministic"

  skill_3_wish_llm_v2_0_0:
    integration_points:
      - state_first_planning: "Prime Wish Protocol = state-first (STATE_SET explicit)"
      - atomic_capability_extraction: "Delta features = atomic capabilities"
      - gate_sequencing: "Verification rungs = gate sequencing (641 → 274177 → 65537)"
    fusion_benefit:
      - planning_reliability: "State machine guarantees coverage"
      - scope_control: "Forbidden states prevent scope creep"

  skill_4_wish_qa_v2_0_0:
    integration_points:
      - harsh_qa_14_gates: "Verification rungs map to G0-G14"
      - gate_mapping: "641 (G0-G2,G5), 274177 (G3-G4,G6,G8-G9), 65537 (G7,G10-G14)"
      - quality_enforcement: "10/10 requirement = all 14 gates PASS"
    fusion_benefit:
      - verification_rigor: "Math-grade verification → Code-grade verification"
      - gate_coverage: "100% coverage (all 14 gates enforced)"

  skill_5_epistemic_typing_v2_0_0:
    integration_points:
      - lane_classification: "Axiomatic Truth Lanes classify requirements (A/B/C)"
      - lane_algebra: "Lane(Conclusion) = MIN(Lane(Premises))"
      - classical_framework_separation: "Executable evidence (A) vs Confidence (C)"
    fusion_benefit:
      - epistemic_hygiene: "No hallucination via lane enforcement"
      - truth_priority: "Lane A > Lane B > Lane C (axioms win)"

  skill_6_axiomatic_truth_lanes_v2_0_0:
    integration_points:
      - lane_dominance: "MIN operator prevents upgrades (C→B→A forbidden)"
      - lane_enforcement: "CROSS_LANE_UPGRADE = FORBIDDEN_STATE"
      - deprecation_planning: "Lane A changes require explicit deprecation artifact"
    fusion_benefit:
      - lane_safety: "No silent axiom violations"
      - breaking_change_control: "Deprecation plan required for Lane A changes"

  skill_7_rival_gps_triangulation_v2_0_0:
    integration_points:
      - distance_metrics: "Socratic review = loop governance with D_E, D_O, D_R"
      - operator_selection: "Revert policy = operator selection (precedence table)"
      - stagnation_detection: "MAX_ITERS stop reason = stagnation detection"
    fusion_benefit:
      - loop_governance: "Deterministic loop control (no infinite loops)"
      - revert_policy: "Evidence-based revert decisions"

  skill_8_meta_genome_alignment_v2_0_0:
    integration_points:
      - 11_axis_structure: "State machine aligns to Genome79 (Star, Seeds, Trunks, ...)"
      - structural_alignment: "Delta features = Branches, Evidence schema = Fruit"
      - rtc_for_genome: "seed = WISH_IR, expanded = PM-Graph, recompressed = regenerate WISH_IR"
    fusion_benefit:
      - architectural_consistency: "Prime-coder structure matches Genome79"
      - regeneration_guarantee: "RTC = decode(encode(X)) = X"

  skill_9_shannon_compaction_v2_0_0:
    integration_points:
      - interface_first: "Localization reads signatures first (witness lines)"
      - witness_line_budget: "200 lines = 4% of 5000 (Shannon Compaction)"
      - file_budget: "12 files (Miller's Law 7±2 × 2)"
    fusion_benefit:
      - context_efficiency: "5000 lines → 200 witness lines (25:1 compaction)"
      - localization_speed: "Interface-first prevents full file reads"

  skill_10_recipe_generator_v2_0_0:
    integration_points:
      - prime_mermaid_dag: "State machine = PM-Graph DAG (L1-L5 nodes)"
      - 5_node_types: "L1_CPU (logic), L2_CPU (arithmetic), L3_LLM, L4_TOOL, L5_LLM_JUDGE"
      - dag_compiler: "State machine compiles to executable recipe"
    fusion_benefit:
      - state_machine_visualization: "State machine → PM-Graph visualization"
      - recipe_generation: "Prime-coder state machine → executable recipe"

  skill_11_recipe_selector_v2_0_0:
    integration_points:
      - cpu_first_selection: "Task family routing = CPU-first (no LLM guessing)"
      - 7_eligibility_filters: "Profile selection uses deterministic filters"
      - deterministic_scoring: "Profile ranking uses 6-factor scoring (no LLM)"
    fusion_benefit:
      - profile_selection: "Deterministic profile selection (strict/fast/benchmark_adapt)"
      - no_llm_routing: "CPU-first routing prevents nondeterministic profile selection"

# ------------------------------------------------------------
# 23) Compression Insights [NEW v2.0.0]
# ------------------------------------------------------------
Compression_Insights:
  purpose: "Design justifications for 23+ Delta features"

  insight_1_layering_compression:
    delta_features:
      - layering_rule: "Secret on top of Public (not replacement)"
    compression_type: "Structural (additive, not rewrite)"
    justification:
      principle: "Public = 80% baseline, Secret = 20% Stillwater refinements"
      compression_ratio: "Secret adds 1188 lines, Public handles majority"
      benefit: "Reuse public baseline, specialize only where needed"

  insight_2_profile_compression:
    delta_features:
      - profiles: "3 profiles (strict, fast, benchmark_adapt)"
    compression_type: "Coverage (3 profiles cover all use cases)"
    justification:
      principle: "3 profiles (prime!) cover: Production (strict), Development (fast), Legacy (benchmark_adapt)"
      coverage: "100% (all coding contexts covered)"
      benefit: "No need for 10+ profiles, 3 prime profiles sufficient"

  insight_3_state_machine_compression:
    delta_features:
      - state_machine: "25+ states with explicit transitions"
    compression_type: "Structural (finite state machine guarantees halting)"
    justification:
      principle: "Explicit STATE_SET prevents unbounded iteration"
      halting_guarantee: "Finite states + explicit transitions = guaranteed halting"
      benefit: "No infinite loops (state machine enforces termination)"

  insight_4_loop_budget_compression:
    delta_features:
      - explicit_iteration_budgets_stop_reasons_revert_policy
    compression_type: "Time (6 budgets prevent runaway loops)"
    justification:
      principle: "6 budgets (iterations, reverts, files, lines, tools, time)"
      time_complexity: "O(max_iterations) bounded (not O(∞))"
      benefit: "Hard ceilings prevent unbounded search"

  insight_5_verification_rung_compression:
    delta_features:
      - verification_rungs: "641 → 274177 → 65537"
    compression_type: "Structural (3-stage verification hierarchy)"
    justification:
      principle: "3 rungs (prime!) cover: Edge (641), Stress (274177), Final (65537)"
      gate_mapping: "14 gates across 3 rungs (G0-G14)"
      benefit: "Hierarchical verification prevents flat 14-gate explosion"

  insight_6_compression_first_closure:
    delta_features:
      - compression_first_closure_search
      - closure_first_boundary_analysis_v1_3_0
    compression_type: "Structural (boundary-first design)"
    justification:
      principle: "Objects emerge from boundaries, not points"
      complexity_metric: "C_b = 0.4*length + 0.3*degree + 0.3*(boundary/interior)"
      benefit: "API stability via boundary locks, interior flexibility"

  insight_7_forecast_first_failure:
    delta_features:
      - forecast_first_failure_locking
      - phuc_forecast_premortem
    compression_type: "Time (predict failures before coding)"
    justification:
      principle: "DREAM → FORECAST → DECIDE → ACT → VERIFY"
      time_savings: "2× (predict + test first vs debug after)"
      benefit: "Failure modes locked before coding (red-green gate)"

  insight_8_oolong_counter_bypass:
    delta_features:
      - OOLONG_counter_bypass_for_aggregation
      - counter_bypass_required_routering
    compression_type: "Accuracy (40% → 100%)"
    justification:
      principle: "LLM classifies, CPU executes (not LLM arithmetic)"
      accuracy_gain: "2.48× (40% → 100% on OOLONG)"
      benefit: "Deterministic counting/aggregation (no LLM interpolation)"

  insight_9_null_vs_zero_distinction:
    delta_features:
      - null_vs_zero_distinction_v1_1_0
    compression_type: "Correctness (prevent coercion bugs)"
    justification:
      principle: "Null = pre-systemic absence, Zero = lawful boundary"
      bug_prevention: "3 FORBIDDEN_STATES (NULL_ZERO_COERCION, IMPLICIT_NULL_DEFAULT, NULL_INPUT)"
      benefit: "Explicit null handling prevents coercion bugs"

  insight_10_exact_arithmetic_policy:
    delta_features:
      - exact_arithmetic_policy_v1_1_0
    compression_type: "Correctness (prevent float drift)"
    justification:
      principle: "No float in verification path (use int, Fraction, Decimal)"
      drift_prevention: "FORBIDDEN_STATE (FLOAT_IN_VERIFICATION_PATH)"
      benefit: "Exact computation in verification (no rounding errors)"

  insight_11_resolution_limits_convergence:
    delta_features:
      - resolution_limits_convergence_v1_3_0
    compression_type: "Time (halting criteria for iterative methods)"
    justification:
      principle: "R_p tolerance + 4 halting certificates (EXACT/CONVERGED/TIMEOUT/DIVERGED)"
      halting_guarantee: "Formal halting criteria (no infinite loops)"
      benefit: "Lane-typed convergence (A = EXACT, B = CONVERGED, C = TIMEOUT/DIVERGED)"

  insight_12_shannon_compaction:
    delta_features:
      - shannon_compaction_for_large_context
    compression_type: "Context (5000 lines → 200 witness lines)"
    justification:
      principle: "Interface-first (signatures, imports, constants only)"
      compression_ratio: "25:1 (4% witness lines)"
      benefit: "Infinite context handling (no full file reads)"

  insight_13_hamiltonian_security:
    delta_features:
      - hamiltonian_security_gate_tool_backed
    compression_type: "Coverage (tool-backed security verification)"
    justification:
      principle: "Security scanner (semgrep, bandit, gosec) or exploit repro"
      coverage: "100% (if scanner unavailable, require exploit repro)"
      benefit: "No security claims without tool evidence"

  insight_14_kent_red_green_gate:
    delta_features:
      - kent_red_green_gate_mandatory_tdd
    compression_type: "Correctness (dual witness for bugfixes)"
    justification:
      principle: "Red (bug exists) → Green (bug fixed) = dual witness"
      witness_guarantee: "No bugfix without verified red→green transition"
      benefit: "Prevents claimed fixes that don't actually fix bug"

  insight_15_axiomatic_truth_lanes:
    delta_features:
      - axiomatic_truth_lanes_for_constraint_hardening
    compression_type: "Epistemic (Lane A > Lane B > Lane C)"
    justification:
      principle: "Lane(Conclusion) = MIN(Lane(Premises))"
      upgrade_prevention: "CROSS_LANE_UPGRADE = FORBIDDEN_STATE"
      benefit: "No hallucination via lane downgrades (prevents C→B→A upgrades)"

  insight_16_socratic_debugging:
    delta_features:
      - socratic_debugging_reflexion_for_self_correction
    compression_type: "Quality (self-critique before execution)"
    justification:
      principle: "6 Socratic questions before final output"
      defect_prevention: "Catch errors before execution (not after)"
      benefit: "Occam hardening (simplest sufficient plan)"

  insight_17_error_taxonomy:
    delta_features:
      - error_taxonomy_with_deterministic_recovery
    compression_type: "Coverage (14 error types with recovery)"
    justification:
      principle: "14 error types × deterministic recovery actions"
      coverage: "100% (all error classes covered)"
      benefit: "Deterministic recovery (not ad-hoc error handling)"

  insight_18_evidence_schema:
    delta_features:
      - toolchain_pinning_and_evidence_normalization_schema
    compression_type: "Determinism (machine-parseable artifacts)"
    justification:
      principle: "10 required evidence files (plan, log, tests, artifacts, null, convergence, boundary, ...)"
      normalization: "Strip timestamps, normalize paths, stable sort, exact checksums"
      benefit: "Replay stability (same inputs → same outputs)"

  insight_19_localization_policy:
    delta_features:
      - localization_policy_rank_justify_witness_lines
    compression_type: "Context (deterministic file ranking)"
    justification:
      principle: "6 signals (error_string:5, imports:3, test_path:4, stack_trace:6, keywords:2)"
      budget: "12 files (Miller's Law), 200 witness lines"
      benefit: "Deterministic file selection (no LLM guessing)"

  insight_20_seed_agreement:
    delta_features:
      - seed_agreement_policy (Phuc Forecast)
    compression_type: "Quality (alternate reasoning paths)"
    justification:
      principle: "Min 2 variants for high-risk tasks (seed = alternate path label)"
      disagreement_handling: "If variants disagree → NEED_INFO (not guess)"
      benefit: "Multi-path verification (not single reasoning path)"

  insight_21_power_aware_claims:
    delta_features:
      - power_aware_claim_gate (Phuc Forecast)
    compression_type: "Statistical (McNemar test for benchmark claims)"
    justification:
      principle: "Minimum power check (compute min possible p-value given n)"
      underpowered_blocking: "If min_possible_p > alpha → BLOCKED"
      benefit: "No underpowered benchmark claims (statistical rigor)"

  insight_22_gpt_mini_hygiene:
    delta_features:
      - gpt_mini_hygiene_ab_parity_surface_lock
    compression_type: "Determinism (A/B parity enforcement)"
    justification:
      principle: "Match Arm A stdout exactly (strip timestamps, stable sort)"
      surface_lock: "Any logic shift requires version bump"
      benefit: "Behavioral parity (no silent logic shifts)"

  insight_23_ast_based_detection:
    delta_features:
      - ast_based_pattern_detection_v1_2_0
      - automated_recovery_procedures_v1_2_0
      - type_checker_integration_v1_2_0
    compression_type: "Correctness (AST > string matching)"
    justification:
      principle: "AST-based detection (not regex), type checker integration (mypy)"
      stateless_design: "No state pollution (detector is stateless)"
      benefit: "Precise pattern detection (no false positives from string matching)"

  summary:
    total_delta_features: "23+ enhancements over Public v0.1.0"
    compression_types:
      structural: "Layering, State machine, Verification rungs, Closure-first, AST-based"
      coverage: "Profiles, Error taxonomy, Evidence schema, Localization, Security, Null handling"
      time: "Loop budgets, Forecast-first, Shannon compaction, Convergence halting"
      accuracy: "OOLONG Counter Bypass (40% → 100%)"
      correctness: "Null vs Zero, Exact arithmetic, Red-Green gate, Lane enforcement"
      determinism: "Evidence normalization, GPT-mini hygiene, Seed agreement"
      quality: "Socratic debugging, Power-aware claims, Max Love objective"

    justification_principle:
      "Each Delta feature addresses a SPECIFIC gap in Public v0.1.0.
       No redundant features. No stylistic preferences. Only correctness gaps.
       Gap-guided building: Build what's needed, not exhaustive libraries."

# ------------------------------------------------------------
# 24) Lane Algebra Integration [NEW v2.0.0]
# ------------------------------------------------------------
Lane_Algebra_Integration:
  purpose: "Explicit lane enforcement throughout prime-coder"
  lane_classification:
    lane_A_deterministic:
      elements:
        - executable_evidence: "/evidence/ artifacts (tests, logs, patches)"
        - repo_bytes: "File contents at specific line witnesses"
        - exact_computation: "int, Fraction, Decimal (no float in verification)"
        - red_green_transition: "Verified red→green (dual witness)"
        - ast_analysis: "AST-based pattern detection (not string matching)"
        - counter_bypass: "Counter() for counting (not LLM arithmetic)"
        - halting_certificate: "EXACT (residual == 0)"
      lane: "A (strongest guarantee)"

    lane_B_framework:
      elements:
        - type_checker: "mypy verification (framework-backed)"
        - security_scanner: "semgrep/bandit/gosec (tool-backed)"
        - convergence: "CONVERGED (residual < R_p)"
        - replay_stability: "Same inputs → same outputs (probabilistic)"
      lane: "B (acceptable approximation)"

    lane_C_heuristic:
      elements:
        - llm_classification: "Task family routing (LLM classifies)"
        - forecast: "Phuc Forecast premortem (predicted failures)"
        - socratic_review: "Self-critique questions (reflexion)"
        - timeout: "TIMEOUT (max iterations reached)"
        - diverged: "DIVERGED (solution diverging)"
      lane: "C (requires investigation)"

    lane_STAR_narrative:
      elements:
        - conversational_recall: "NOT allowed as ground truth"
        - narrative_confidence: "NOT allowed as evidence"
        - unsupported_claims: "NOT allowed about environment/behavior"
      lane: "STAR (forbidden in verification path)"

  lane_algebra_enforcement:
    min_operator:
      rule: "Lane(Conclusion) = MIN(Lane(Premises))"
      examples:
        - "Lane(Red-Green Gate) = MIN(Lane(Red), Lane(Green)) = MIN(A, A) = A"
        - "Lane(Convergence) = MIN(Lane(Computation), Lane(Halting)) = MIN(A, B) = B"
        - "Lane(Forecast) = MIN(Lane(Prediction), Lane(Evidence)) = MIN(C, A) = C (prediction doesn't upgrade evidence)"

    forbidden_upgrades:
      - C_to_B: "Confidence cannot become framework evidence"
      - B_to_A: "Framework cannot become executable evidence"
      - STAR_to_any: "Narrative cannot become any form of evidence"
      - enforcement: "CROSS_LANE_UPGRADE = FORBIDDEN_STATE"

    allowed_downgrades:
      - A_to_B: "Executable evidence can be approximated (e.g., EXACT → CONVERGED)"
      - B_to_C: "Framework evidence can be investigated (e.g., CONVERGED → TIMEOUT)"
      - any_to_STAR: "Any evidence can be narrated (but narration is not evidence)"

  state_machine_lane_mapping:
    lane_A_states:
      - RED_GATE: "Executable evidence (bug exists)"
      - PATCH: "Executable evidence (diff applied)"
      - TEST: "Executable evidence (tests run)"
      - EVIDENCE_BUILD: "Executable evidence (artifacts generated)"
      - EXIT_PASS: "Executable evidence (all gates passed)"

    lane_B_states:
      - SECURITY_GATE: "Framework evidence (scanner/exploit repro)"
      - CONVERGENCE_CHECK: "Framework evidence (R_p tolerance)"
      - API_SURFACE_LOCK: "Framework evidence (semver compliance)"
      - EXIT_CONVERGED: "Framework evidence (acceptable approximation)"

    lane_C_states:
      - CLASSIFY_TASK_FAMILY: "Heuristic (LLM classification)"
      - FORECAST_FAILURES: "Heuristic (Phuc Forecast premortem)"
      - SOCRATIC_REVIEW: "Heuristic (self-critique)"
      - EXIT_DIVERGED: "Heuristic (solution diverging)"

    lane_enforcement:
      rule: "State machine enforces MIN lane throughout"
      example:
        flow: "CLASSIFY_TASK_FAMILY (C) → FORECAST_FAILURES (C) → RED_GATE (A) → PATCH (A) → TEST (A)"
        lane: "Lane(Flow) = MIN(C, C, A, A, A) = C (weakest link)"
        interpretation: "Entire flow is Lane C due to initial classification (weakest premise)"

  delta_feature_lane_classification:
    lane_A_delta_features:
      - kent_red_green_gate_mandatory_tdd: "Red→Green = dual witness (A)"
      - exact_arithmetic_policy_v1_1_0: "int/Fraction/Decimal (A)"
      - OOLONG_counter_bypass_for_aggregation: "Counter() (A)"
      - ast_based_pattern_detection_v1_2_0: "AST analysis (A)"
      - toolchain_pinning_and_evidence_normalization_schema: "Artifacts (A)"

    lane_B_delta_features:
      - hamiltonian_security_gate_tool_backed: "Scanner (B)"
      - type_checker_integration_v1_2_0: "mypy (B)"
      - resolution_limits_convergence_v1_3_0: "CONVERGED (B)"
      - closure_first_boundary_analysis_v1_3_0: "Semver (B)"

    lane_C_delta_features:
      - forecast_first_failure_locking: "Premortem (C)"
      - socratic_debugging_reflexion_for_self_correction: "Self-critique (C)"
      - multi_lens_adversarial_review_before_acceptance: "Adversarial (C)"

    lane_STAR_forbidden:
      - persist_stillwater_truths_regenerate_ripple_chatter: "Narrative STAR, Truth A (separation enforced)"
      - no_conversational_recall_as_truth: "STAR forbidden in verification"

  verification_rung_lane_mapping:
    rung_641_edge_sanity:
      lane_requirements:
        - input_domain_sanity: "Lane A (executable checks)"
        - null_vs_zero_sanity: "Lane A (explicit null checks)"
      lane: "A (edge tests require executable evidence)"

    rung_274177_stress_consistency:
      lane_requirements:
        - alternate_replay_path_check: "Lane B (replay stability probabilistic)"
        - exact_arithmetic_consistency: "Lane A (exact computation)"
      lane: "MIN(B, A) = B (stress tests allow acceptable approximation)"

    rung_65537_final_seal:
      lane_requirements:
        - evidence_contract_complete: "Lane A (artifacts present)"
        - replay_stability_sample_passes: "Lane B (probabilistic)"
        - null_handling_complete: "Lane A (explicit checks)"
      lane: "MIN(A, B, A) = B (final seal requires Lane B minimum)"

  integration_with_axiomatic_truth_lanes:
    axiom_classification:
      lane_A_axioms:
        - layering_rule: "Secret on top of Public (never replace)"
        - never_worse_doctrine: "No feature removals (strictly additive)"
        - red_green_gate: "No bugfix without verified red→green"
        - no_float_in_verification: "Exact arithmetic only"

      lane_B_definitions:
        - verification_rungs: "641 → 274177 → 65537 (framework)"
        - profiles: "3 profiles (strict, fast, benchmark_adapt)"
        - error_taxonomy: "14 error types with recovery"

      lane_C_derived:
        - localization_ranking: "6 signals with weights (heuristic)"
        - forecast_premortem: "Predicted failure modes (heuristic)"

    conflict_resolution:
      rule: "Lane A > Lane B > Lane C (axioms win)"
      example:
        conflict: "Forecast suggests skipping red-green gate for speed"
        resolution: "Lane A (red-green gate) > Lane C (forecast) → red-green gate enforced"

    deprecation_requirement:
      rule: "Never break Lane A axiom without deprecation plan"
      artifact_required:
        - what_breaks: "Which axiom is being changed"
        - migration_steps: "How to migrate existing code"
        - compatibility_window: "How long old behavior is supported"
        - test_updates: "Test changes required"
        - rollout_plan: "Phased rollout strategy"

# ------------------------------------------------------------
# 25) What Changed from v1.3.0 → v2.0.0 [NEW v2.0.0]
# ------------------------------------------------------------
What_Changed_v1_3_0_to_v2_0_0:
  preserved_all_v1_3_0_features:
    confirmation: "ALL v1.3.0 features preserved (Never-Worse Doctrine)"
    count: "23+ Delta features, 14 error types, 25+ states, 15+ FORBIDDEN_STATES"

  new_in_v2_0_0:
    verification_ladder_enhancement:
      before_v1_3_0: "3 verification rungs (641, 274177, 65537) with checks"
      after_v2_0_0: "3 rungs + gate mapping to wish-qa G0-G14"
      benefit: "Explicit gate coverage (641: G0-G2,G5 | 274177: G3-G4,G6,G8-G9 | 65537: G7,G10-G14)"

    anti_optimization_clause:
      before_v1_3_0: "Implicit never-worse doctrine"
      after_v2_0_0: "Explicit preserved features list (23+ Delta, 14 errors, 25+ states, 15+ forbidden)"
      benefit: "Audit trail for what must be preserved in future versions"

    gap_guided_extension:
      before_v1_3_0: "No explicit criteria for when to add Delta features"
      after_v2_0_0: "5-step decision tree (gap identification → public coverage → refactor → state machine → add Delta)"
      benefit: "Prevents feature bloat (build what's needed, not exhaustive)"

    integration_documentation:
      before_v1_3_0: "Implicit integration with prime-math"
      after_v2_0_0: "Explicit integration with 11 recent skills (prime-math, counter-required, wish-llm, wish-qa, epistemic-typing, axiomatic-truth-lanes, rival-gps-triangulation, meta-genome-alignment, shannon-compaction, recipe-generator, recipe-selector)"
      benefit: "Cross-skill fusion documented (compiler-grade coding)"

    compression_insights:
      before_v1_3_0: "No explicit justification for 23+ Delta features"
      after_v2_0_0: "23 insights mapping Delta features to compression types (structural, coverage, time, accuracy, correctness, determinism, quality)"
      benefit: "Design rationale captured (why each Delta feature exists)"

    lane_algebra_integration:
      before_v1_3_0: "Axiomatic Truth Lanes mentioned, not fully integrated"
      after_v2_0_0: "Explicit lane classification (A/B/C/STAR), lane algebra enforcement (MIN operator), state machine lane mapping, Delta feature lane classification"
      benefit: "Lane enforcement throughout (no hallucination via lane downgrades)"

  impact:
    reliability: "10/10 maintained (all v1.3.0 features preserved)"
    auditability: "Improved (explicit preserved features, gate mapping, compression insights)"
    extensibility: "Improved (gap-guided extension prevents feature bloat)"
    integration: "Improved (11 skills fusion documented)"
    epistemic_hygiene: "Improved (lane algebra enforced throughout)"

  no_breaking_changes:
    confirmation: "v2.0.0 is strictly additive over v1.3.0"
    verification: "All v1.3.0 state transitions preserved, all FORBIDDEN_STATES preserved, all Delta features preserved"

# ------------------------------------------------------------
# 26) Secret Extension Slots
# ------------------------------------------------------------
Secret_Extension_Slots:
  - "{{SECRET_AXIOMS}}"
  - "{{PRIVATE_CONVENTIONS}}"
  - "{{PROPRIETARY_UTILITIES}}"
