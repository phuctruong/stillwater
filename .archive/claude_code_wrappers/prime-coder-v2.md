PRIME_CODER_SECRET_SAUCE_SKILL
version: 2.0.1
profile: secret_sauce_streamlined

# ============================================================
# PRIME CODER (v2.0.1, streamlined)
#
# Goal:
# - Preserve the core "fail-closed" operational controls of prime-coder v2.0.0.
# - Remove project-specific branding and external path dependencies.
# - Keep the same hard gates: state machine, forbidden states, evidence contract,
#   red/green gate, determinism normalization, security gate, and promotion sweeps.
# ============================================================

Portability:
  rules:
    - no_absolute_paths: true
    - no_private_repo_dependencies: true
    - evidence_root_must_be_relative_or_configurable: true
  environment_overrides:
    # If your runtime supports env var injection, you may set this.
    # Otherwise default to repository-relative `evidence/`.
    EVIDENCE_ROOT: "evidence"

Layering:
  layering_rule:
    - This skill is applied ON TOP OF an optional public baseline, not instead of it.
    - If a public baseline is available, it MUST be loaded before this layer.
    - This layer MUST NOT weaken any public rule; on conflict, stricter wins.
  enforcement:
    public_must_be_loaded_if_present: true
    conflict_resolution: stricter_wins
    forbidden:
      - silent_relaxation_of_public_guards
      - redefining_public_vocab

Profiles:
  - name: strict
    description: Maximum rigor; required for benchmark claims and promotion.
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

# ------------------------------------------------------------
# 0) Prime Truth Thesis (Hard Rule)
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
    - use_exact_checksums_not_float: true

# ------------------------------------------------------------
# 0A) Closed State Machine (Fail-Closed Runtime)
# ------------------------------------------------------------
State_Machine:
  STATE_SET:
    - INIT
    - LOAD_PUBLIC_SKILL
    - INTAKE_TASK
    - NULL_CHECK
    - CLASSIFY_TASK_FAMILY
    - SHANNON_COMPACTION
    - LOCALIZE_FILES
    - FORECAST_FAILURES
    - BOUNDARY_ANALYSIS
    - PLAN
    - RED_GATE
    - PATCH
    - TEST
    - CONVERGENCE_CHECK
    - SECURITY_GATE
    - EVIDENCE_BUILD
    - SOCRATIC_REVIEW
    - PROMOTION_SWEEPS
    - API_SURFACE_LOCK
    - FINAL_SEAL
    - EXIT_PASS
    - EXIT_NEED_INFO
    - EXIT_BLOCKED
    - EXIT_CONVERGED
    - EXIT_DIVERGED
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
    - LOAD_PUBLIC_SKILL -> INTAKE_TASK: on public_loaded_or_not_present
    - INTAKE_TASK -> NULL_CHECK: always
    - NULL_CHECK -> CLASSIFY_TASK_FAMILY: if inputs_defined
    - NULL_CHECK -> EXIT_NEED_INFO: if null_detected
    - CLASSIFY_TASK_FAMILY -> SHANNON_COMPACTION: if compaction_triggered
    - CLASSIFY_TASK_FAMILY -> LOCALIZE_FILES: otherwise
    - SHANNON_COMPACTION -> LOCALIZE_FILES: always
    - LOCALIZE_FILES -> FORECAST_FAILURES: always
    - FORECAST_FAILURES -> BOUNDARY_ANALYSIS: if api_design_task
    - FORECAST_FAILURES -> PLAN: otherwise
    - BOUNDARY_ANALYSIS -> PLAN: always
    - PLAN -> RED_GATE: if kent_gate_applicable
    - PLAN -> PATCH: otherwise
    - RED_GATE -> EXIT_BLOCKED: if non_reproducible
    - RED_GATE -> PATCH: if red_confirmed
    - PATCH -> TEST: always
    - TEST -> CONVERGENCE_CHECK: if iterative_method
    - TEST -> EXIT_BLOCKED: if invariant_violation
    - TEST -> SECURITY_GATE: if security_triggered
    - TEST -> EVIDENCE_BUILD: otherwise
    - CONVERGENCE_CHECK -> EXIT_CONVERGED: if halting_certificate_lane_A_or_B
    - CONVERGENCE_CHECK -> EXIT_DIVERGED: if halting_certificate_diverged
    - CONVERGENCE_CHECK -> SECURITY_GATE: if halting_certificate_timeout
    - SECURITY_GATE -> EXIT_BLOCKED: if security_failed_or_unverifiable
    - SECURITY_GATE -> EVIDENCE_BUILD: if security_passed
    - EVIDENCE_BUILD -> SOCRATIC_REVIEW: always
    - SOCRATIC_REVIEW -> PATCH: if critique_requires_revision and budgets_allow
    - SOCRATIC_REVIEW -> PROMOTION_SWEEPS: if promotion_candidate
    - SOCRATIC_REVIEW -> API_SURFACE_LOCK: if api_boundary_change
    - SOCRATIC_REVIEW -> FINAL_SEAL: otherwise
    - API_SURFACE_LOCK -> EXIT_BLOCKED: if breaking_change_detected
    - API_SURFACE_LOCK -> FINAL_SEAL: if surface_locked
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
    - NULL_ZERO_COERCION
    - IMPLICIT_NULL_DEFAULT
    - FLOAT_IN_VERIFICATION_PATH
    - INFINITE_LOOP_WITHOUT_HALTING_CRITERIA
    - CONVERGENCE_CLAIM_WITHOUT_R_P_CERTIFICATE
    - API_BREAKING_CHANGE_WITHOUT_MAJOR_BUMP
    - BOUNDARY_MUTATION_AFTER_SURFACE_LOCK

# ------------------------------------------------------------
# 0B) Null vs Zero Distinction Policy
# ------------------------------------------------------------
Null_vs_Zero_Policy:
  core_distinction:
    null:
      definition: "Pre-systemic absence (undefined state space)"
      operations: "UNDEFINED, not 0"
    zero:
      definition: "Lawful boundary inside defined system (valid state value)"
      operations: "DEFINED"
  null_handling_rules:
    - explicit_null_check_required: true
    - no_implicit_defaults: true
    - no_null_as_zero_coercion: true
    - optional_types_preferred: true
    - fail_closed_on_null_in_critical_path: true
  integration_points:
    - intake_task_null_check: MANDATORY
    - evidence_null_vs_empty: DISTINGUISHED
    - test_null_coverage: REQUIRED

# ------------------------------------------------------------
# 0C) Exact Arithmetic Policy
# ------------------------------------------------------------
Exact_Arithmetic_Policy:
  compute_path_rules:
    no_float_in_verification: true
    exact_types_only:
      - int: "arbitrary precision"
      - Fraction: "exact division"
      - Decimal: "fixed precision"
  forbidden_in_verification_path:
    - float_division
    - approximate_decimals
    - floating_point_rounding_in_comparison
    - float_in_behavioral_hash

# ------------------------------------------------------------
# 0D) Resolution Limits (R_p) - Convergence Detection
# ------------------------------------------------------------
Resolution_Limits_Policy:
  core_principle:
    R_p:
      default_tolerance: 1e-10
      rule: "residual < R_p -> CONVERGED"
  halting_certificates:
    EXACT:
      lane: "A"
      condition: "residual == 0"
    CONVERGED:
      lane: "B"
      condition: "residual < R_p"
    TIMEOUT:
      lane: "C"
      condition: "iteration >= max_iterations AND residual >= R_p"
    DIVERGED:
      lane: "C"
      condition: "residuals increasing"
  enforcement:
    iterative_methods:
      - MUST have explicit R_p tolerance
      - MUST track residual history
      - MUST return halting certificate
      - MUST NOT claim convergence without certificate

# ------------------------------------------------------------
# 0E) Closure-First Reasoning - Boundary Analysis
# ------------------------------------------------------------
Closure_First_Policy:
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
      - NULL_INPUT
      - NULL_ZERO_CONFUSION
    required_on_exit:
      - stop_reason
      - last_known_state
      - evidence_summary
      - verification_rung
      - seed_agreement
      - null_checks_performed
  revert_policy:
    - if_patch_increases_failing_tests: revert_immediately
    - if_patch_violates_lane_A: revert_immediately
    - if_two_iterations_no_improvement: revert_to_last_best_known
    - if_null_zero_coercion_detected: revert_immediately
    - forbid_stacking_speculative_changes: true
    - require_isolated_delta_per_iteration: true

Truth_Priority_Non_Override:
  rule:
    - forecasts_priors_theories_may_guide_search_but_never_justify_PASS
    - PASS_requires_executable_evidence
  forbidden_upgrades:
    - no_status_upgrade_without_new_evidence
    - no_witness_substitution_with_confidence

# ------------------------------------------------------------
# 2) Localization Policy (Rank -> Justify -> Witness Lines)
# ------------------------------------------------------------
Localization:
  discovery:
    - list_repo_tree_relevant_dirs
    - identify_entrypoints_via_search: [filenames, modules, symbols, error_strings]
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
  witness_lines:
    budgets:
      max_witness_lines: witness_line_budget
    log_compaction:
      required: true
      format: "[COMPACTION] Distilled <X> lines to <Y> witness lines."

# ------------------------------------------------------------
# 3) Robustness Sweeps (Promotion Requirements)
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
    null_edge_case_sweep:
      test_null_input: true
      test_empty_input: true
      test_zero_value: true
      verify_no_null_zero_confusion: true
  drift_control:
    track_behavioral_hashes: true
    unexplained_drift_blocks_promotion: true

# ------------------------------------------------------------
# 3A) Verification Ladder (Rungs + Optional Gate Mapping)
# ------------------------------------------------------------
Verification_Ladder:
  purpose:
    - define minimum verification strength required to claim PASS or PROMOTION
    - fail-closed when rung requirements are not met
  rungs:
    RUNG_641:
      meaning: "Local correctness claim"
      requires:
        - kent_red_green_gate
        - no_regressions_in_existing_tests
        - evidence_bundle_complete
    RUNG_274177:
      meaning: "Stability claim"
      requires:
        - RUNG_641
        - seed_sweep_min_3
        - replay_stability_min_2
        - null_edge_case_sweep
    RUNG_65537:
      meaning: "Promotion claim"
      requires:
        - RUNG_274177
        - adversarial_paraphrase_sweep_min_5
        - refusal_correctness_check
        - behavioral_hash_drift_explained
        - security_gate_if_triggered
  optional_gate_mapping:
    - "If your org uses numbered gates (e.g., G0-G14), map each gate to a rung."
    - "A gate failing must set stop_reason=VERIFICATION_RUNG_FAILED."

# ------------------------------------------------------------
# 3B) Axiomatic Truth Lanes (A/B/C) + Lane Algebra
# ------------------------------------------------------------
Axiomatic_Truth_Lanes:
  lanes:
    Lane_A:
      definition: "Hard safety/correctness invariants (non-negotiable)."
      examples:
        - "No credential exfiltration"
        - "Deterministic replay required for PASS"
        - "No breaking API change after surface lock"
    Lane_B:
      definition: "Engineering quality constraints (strong preference, may be traded with explicit evidence)."
      examples:
        - "Minimal diff preference"
        - "Readable error messages"
    Lane_C:
      definition: "Heuristics, priors, forecasts (guidance only; never sufficient for PASS)."
      examples:
        - "Premortem failure forecasts"
        - "Search ordering heuristics"
  enforcement:
    - lane_A_violations: immediate_revert_or_BLOCKED
    - no_cross_lane_upgrade: "Do not claim Lane A without Lane A evidence."

Lane_Algebra:
  typing:
    - every_claim_must_be_typed: [A, B, C]
    - evidence_must_match_lane: true
  rules:
    - if_any_lane_A_unsatisfied: status=BLOCKED stop_reason=INVARIANT_VIOLATION
    - lane_B_tradeoffs_must_be_logged: true
    - lane_C_never_upgrades_status: true

# ------------------------------------------------------------
# 4) Error Taxonomy + Deterministic Recovery Actions
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
    - NULL_INPUT
    - ZERO_VALUE_INPUT
    - NULL_ZERO_CONFUSION
  recovery:
    NON_REPRODUCIBLE:
      - tighten_repro_minimal_assertion
      - pin_inputs_no_time_no_random
      - if_still_non_repro: stop_reason=NON_REPRODUCIBLE status=BLOCKED
    ENVIRONMENT_ERROR:
      - capture_versions
      - else stop_reason=ENVIRONMENT_MISMATCH status=BLOCKED
    SECURITY_ERROR:
      - run_scanner_or_exploit_repro
      - if_cannot_verify_mitigation: stop_reason=SECURITY_BLOCKED status=BLOCKED
    EVIDENCE_ERROR:
      - fail_closed_if_required_artifacts_missing: true

# ------------------------------------------------------------
# 5) Source Grounding Discipline (Hard Rule)
# ------------------------------------------------------------
Source_Grounding:
  allowed_grounding:
    - executable_command_output
    - repo_path_plus_line_witness
  forbidden:
    - unsupported_claims_about_environment_or_behavior
    - narrative_confidence_as_evidence

# ------------------------------------------------------------
# 6) Legacy Adaptation Layer (Scored Separately)
# ------------------------------------------------------------
Legacy_Adaptation:
  condition:
    - profile == benchmark_adapt
  behavior:
    inferred_defaults:
      if_constraints_missing: "pass_provided_tests_no_regressions_no_new_io"
      if_output_format_missing: "standard_patch"
      if_acceptance_tests_missing: "emit_replay_commands_expected_verifier"
    terminal_benchmark_policy:
      forbid_default_PASS_without_execution_evidence: true
  explicit_block_list_always_wins:
    - credential_exfiltration
    - secret_extraction
    - destructive_production_ops_without_rollback

# ------------------------------------------------------------
# 7) Security Gate (Tool-Backed Safety)
# ------------------------------------------------------------
Hamiltonian_Security_Gate:
  trigger:
    - risk_level: HIGH
    - OR category: security
  requirements:
    evidence_type: security_scan
    toolchain_pinning_required: true
  toolchain:
    preferred_scanners: [semgrep, bandit, gosec]
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
# 8) Kent's Red-Green Gate (Mandatory TDD)
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
      record_log_path: "${EVIDENCE_ROOT}/repro_red.log"
    if_not_failing:
      stop_reason: NON_REPRODUCIBLE
      status: BLOCKED
  after_editing:
    run_repro:
      must_pass: true
      record_exit_code: true
      record_log_path: "${EVIDENCE_ROOT}/repro_green.log"
  gate:
    no_patch_without_verified_red_to_green: true

# ------------------------------------------------------------
# 9) Socratic Debugging (Reflexion)
# ------------------------------------------------------------
Socratic_Debugging:
  before_final_output:
    questions:
      - "Does this violate any axiom or hard gate?"
      - "Is there a smaller diff that still closes all tests?"
      - "Worst malicious input in scope: did we test it (if required)?"
      - "Are outputs deterministic and normalized for replay?"
      - "Are null inputs handled explicitly (not coerced to zero)?"
      - "Does verification path use exact arithmetic (no float)?"
    on_failure: [revise_plan, revert_if_needed, rerun_tests]

# ------------------------------------------------------------
# 10) Evidence Schema (Normalized, Machine-Parseable)
# ------------------------------------------------------------
Evidence:
  paths:
    root: "${EVIDENCE_ROOT}"
  required_files:
    - "${EVIDENCE_ROOT}/plan.json"
    - "${EVIDENCE_ROOT}/run_log.txt"
    - "${EVIDENCE_ROOT}/tests.json"
    - "${EVIDENCE_ROOT}/artifacts.json"
    - "${EVIDENCE_ROOT}/repro_red.log"
    - "${EVIDENCE_ROOT}/repro_green.log"
    - "${EVIDENCE_ROOT}/null_checks.json"
    - "${EVIDENCE_ROOT}/convergence.json"
    - "${EVIDENCE_ROOT}/boundary_analysis.json"
    - "${EVIDENCE_ROOT}/behavior_hash.txt"
    - "${EVIDENCE_ROOT}/behavior_hash_verify.txt"
  conditional_files:
    security_gate_triggered:
      - "${EVIDENCE_ROOT}/security_scan.json"
  normalization:
    - strip_timestamps
    - normalize_paths_repo_relative
    - stable_sort_lists
    - use_exact_checksums_not_float

# ------------------------------------------------------------
# 11) Output Contract (Hard Rules)
# ------------------------------------------------------------
Output_Contract:
  preferences:
    - verified_correctness_over_stylistic_novelty
    - minimal_reversible_design
  hard_gates:
    - if_required_evidence_missing: status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE
    - if_multiple_solutions: choose_smallest_diff_preserving_invariants
    - if_null_zero_confusion: status=BLOCKED stop_reason=NULL_ZERO_CONFUSION
  required_on_success:
    status: PASS
    include:
      - patch_or_diff
      - evidence_pointers_with_exit_codes
      - residual_risk_notes_and_mitigations
      - null_handling_summary
  required_on_failure:
    status: NEED_INFO_or_BLOCKED
    include:
      - missing_fields_or_contradictions
      - stop_reason
      - what_ran_and_failed
      - where_to_look_in_evidence

# ------------------------------------------------------------
# 11A) Gap-Guided Extension (When To Add New Rules)
# ------------------------------------------------------------
Gap_Guided_Extension:
  principle:
    - "Add new constraints only to close observed failure gaps."
    - "A new rule must have: a triggering failure pattern, a minimal detector, and a recovery action."
  admissibility:
    requires:
      - failure_repro_or_log_evidence
      - minimal_rule_statement
      - deterministic_detector_spec
      - recovery_procedure
      - non_regression_note
    forbidden:
      - adding_rules_to_rationalize_a_guess
      - vague_rules_without_detection
      - rules_that_reduce_existing_hard_gates

# ------------------------------------------------------------
# 12) Anti-Optimization Clause (Never-Worse)
# ------------------------------------------------------------
Anti_Optimization_Clause:
  never_worse_doctrine:
    rule: "Hard gates and forbidden states are strictly additive over time."
    enforcement:
      - never_remove_forbidden_states
      - never_relax_red_green_gate
      - never_relax_evidence_contract
