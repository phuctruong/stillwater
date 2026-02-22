PRIME_MATH_SECRET_SKILL:
  version: 2.3.0
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  profile: private
  includes_public_skill: canon/prime-math/skills/prime_math_public_skill_v1.0.0.md
  secret_pack_id: stillwater-prime-math-secret-v2.3.0
  sealing_policy: 641-274177-65537
  status: FINAL

  # ============================================================
  # MAGIC_WORD_MAP — prime-math concepts anchored to prime coordinates
  # ============================================================
  MAGIC_WORD_MAP:
    proof:      [verification (T1)]     # executable witness that claim holds; not prose confidence
    exact:      [integrity (T0)]        # no float in verification path; exact arithmetic preserves coherence
    fraction:   [compression (T0)]      # Fraction(1,3) = lossless rational; no precision lost
    witness:    [evidence (T1)]         # artifact proving mathematical claim; compute:// or proof:// handle
    counterexample: [constraint (T0)]   # reduces solution space; one disconfirming instance falsifies universal
    rung:       [rung (T1)]             # 641=local, 274177=stability, 65537=proof-grade promotion
    dual_witness: [coherence (T0)]      # two independent witnesses both pointing to same truth
    domain:     [boundary (T0)]         # over ℝ vs ℤ vs ℤ/pℤ; undeclared domain = UNKNOWN

  # ============================================================
  # PRIME MATH — SECRET SKILL (v2.2.0)  [10/10]
  #
  # Design goals (non-negotiable):
  # - Preserve Public contract EXACTLY (keys, semantics, fail-closed).
  # - Add mechanical verification gates (math analogs of Red→Green).
  # - Priors guide search only; never upgrade truth.
  # - Deterministic budgets, seed semantics, rung checklists.
  # - Proof-grade discipline for theorem/olympiad tasks.
  # - OOLONG memory discipline + DoV recipe tiers + dual-witness replay.
  # - Formal-proof bridge with immutable-source gates.
  # - Geometry proof-trace bridge with strict checker metadata gates.
  # - Famous-problem adjudication with dual-status reporting.
  # - IF-theory adjudication with explicit scope + validation tiers.
  # - Resolution Limits (R_p) convergence detection with halting certificates.
  # - Closure-First boundary analysis + proof surface locking.
  #
  # v2.2.0 additions (additive-only, never weakens v2.1.0):
  # - Added portability config block (no absolute paths)
  # - Added layering rule (never weaken public skill)
  # - Added IMO-style proof structure section (6-step proof discipline)
  # - Added Lemma Library Protocol (register, evolve, deprecate lemmas)
  # - Added Null/Zero distinction for math contexts
  # - Added anti-patterns section (named math failure modes)
  # - Added quick reference cheat sheet
  # - Added exact arithmetic policy reference (Fraction/Decimal, no float)
  # - Added proof surface locking with semver discipline
  # ============================================================

  # ------------------------------------------------------------
  # A) Portability (Hard)
  # ------------------------------------------------------------
  Portability:
    rules:
      - no_absolute_paths: true
      - no_private_repo_dependencies: true
      - evidence_root_must_be_relative_or_configurable: true
    config:
      EVIDENCE_ROOT: "evidence"
      REPO_ROOT_REF: "."
    invariants:
      - witness_paths_must_be_repo_relative_or_handle_prefixed: true
      - normalize_paths_before_hashing: true

  # ------------------------------------------------------------
  # B) Layering (Never Weaken Public)
  # ------------------------------------------------------------
  Layering:
    rule:
      - "This skill runs ON TOP OF the public prime-math skill."
      - "Public skill MUST be loaded first. This layer CANNOT weaken it."
      - "On conflict: stricter wins."
    conflict_resolution: stricter_wins
    forbidden:
      - removing_public_required_output_keys
      - relaxing_public_forbidden_states
      - downgrading_public_ok_conditions
    baseline_absent_policy:
      if_PUBLIC_BASELINE_REF_is_null: load_this_skill_standalone_without_error
      if_baseline_fails_to_load: log_warning_and_continue_with_this_layer_only

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
  # 0) Global Hard Rules (apply to every state) [integrity, verification]
  # ------------------------------------------------------------
  Global_Hard_Rules:
    truth_priority_non_override:
      rule:
        - priors_forecasts_style_may_guide_search_only
        - status_OK_requires_executable_or_checkable_witnesses
        - never_upgrade_status_or_lane_by_confidence
      forbidden:
        - STATUS_UPGRADE_BY_PRIOR
        - REPLACING_MISSING_WITNESSES_WITH_CONFIDENCE
        - INVENTING_EXTERNAL_FACTS
    format_integrity:
      - output_must_validate_against_public_schema: true
      - if_schema_invalid:
          status: ERROR
          stop_reason: ERROR_OUTPUT_INVALID
    determinism_normalization:
      - stable_sort_lists: true
      - canonicalize_symbol_names_when_generated: true
      - strip_nondeterministic_tokens: [timestamps, hostnames, pids]
      - stable_witness_ids: "sha256(normalized witness payload)"
    unknown_over_maybe:
      - if_any_critical_gap_unclosed: status=UNKNOWN
      - if_witness_conflict_unresolved: status=UNKNOWN
      - if_domain_unbounded_or_DoV_missing: status=UNKNOWN

  # ------------------------------------------------------------
  # 0.0) Task Family Classifier (binding routing + rung targets)
  # ------------------------------------------------------------
  Task_Family:
    enum:
      - F1_deterministic_math          # exact algebra/nt/combinatorics with finite closure
      - F2_resolution_bound            # numeric/iterative/approx methods needing R_p
      - F3_truth_lane                  # tasks about epistemics, certainty, correctness claims
      - F4_domain_validity             # “when does strategy work” / DoV / meta reasoning
      - F5_rival_witness               # “find counterexample” / adversarial falsification
      - F6_olympiad_proof              # proof-grade olympiad / theorem tasks
      - F7_famous_problem_adjudication # open problems / classical vs framework status
      - F8_if_theory_adjudication      # conditional frameworks / validation tiers
    classifier_rules:
      - if_problem_requests_exact_value_or_proof: include [F1 or F6]
      - if_requires_iteration_or_approx: include F2
      - if_requests_status_of_open_problem: include F7
      - if_mentions_if_theory_or_axioms_or_validation: include F8
      - if_asks_for_counterexample_or_falsify: include F5
    output_binding:
      - emit task_family: REQUIRED (secret optional key; must not break public)

  # ------------------------------------------------------------
  # 0.1) Closed Runtime State Machine (Secret Layer)
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - LOAD_PUBLIC_CORE
      - PARSE_TASK
      - CLASSIFY_TASK
      - ROUTE_LAYERS
      - SET_RUNG_TARGET
      - BUILD_PLAN
      - EXECUTE_PUBLIC_PROTOCOL
      - APPLY_SECRET_LAYERS
      - MATH_RED_GREEN_PROTOCOL
      - RUN_VERIFICATION_LADDER_641
      - RUN_VERIFICATION_LADDER_274177
      - RUN_VERIFICATION_LADDER_65537
      - BUILD_WITNESSES
      - REPLAY_CHECK
      - FINALIZE_OUTPUT
      - EXIT_OK
      - EXIT_NEED_INFO
      - EXIT_UNKNOWN
      - EXIT_ERROR
      - EXIT_OUT_OF_SCOPE

    INPUT_ALPHABET: [PROBLEM_TEXT, MODE_FLAGS, TOOL_OUTPUT, CANON_ARTIFACTS, PRIVATE_ARTIFACTS]
    OUTPUT_ALPHABET: [RESPONSE_OBJECT, WITNESS_HANDLES, VERIFICATION_ACTIONS]

    TRANSITIONS:
      - INIT -> LOAD_PUBLIC_CORE: on PROBLEM_TEXT
      - LOAD_PUBLIC_CORE -> PARSE_TASK: on public_loaded
      - PARSE_TASK -> EXIT_NEED_INFO: if task_request_null_or_required_inputs_missing
      - PARSE_TASK -> CLASSIFY_TASK: otherwise
      - CLASSIFY_TASK -> ROUTE_LAYERS: always
      - ROUTE_LAYERS -> SET_RUNG_TARGET: always
      - SET_RUNG_TARGET -> BUILD_PLAN: always
      - BUILD_PLAN -> EXECUTE_PUBLIC_PROTOCOL: always
      - EXECUTE_PUBLIC_PROTOCOL -> APPLY_SECRET_LAYERS: always
      - APPLY_SECRET_LAYERS -> MATH_RED_GREEN_PROTOCOL: always
      - MATH_RED_GREEN_PROTOCOL -> RUN_VERIFICATION_LADDER_641: always
      - RUN_VERIFICATION_LADDER_641 -> EXIT_UNKNOWN: if rung_641_failed
      - RUN_VERIFICATION_LADDER_641 -> RUN_VERIFICATION_LADDER_274177: if rung_641_passed_and_target_ge_274177
      - RUN_VERIFICATION_LADDER_641 -> BUILD_WITNESSES: if rung_641_passed_and_target_eq_641
      - RUN_VERIFICATION_LADDER_274177 -> EXIT_UNKNOWN: if rung_274177_failed
      - RUN_VERIFICATION_LADDER_274177 -> RUN_VERIFICATION_LADDER_65537: if rung_274177_passed_and_target_eq_65537
      - RUN_VERIFICATION_LADDER_274177 -> BUILD_WITNESSES: if rung_274177_passed_and_target_eq_274177
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
      - INFINITE_LOOP_WITHOUT_R_P_CHECK
      - CONVERGENCE_CLAIM_WITHOUT_CERTIFICATE
      - RESIDUAL_TRACKING_OMITTED
      - LANE_C_WITHOUT_JUSTIFICATION
      - BOUNDARY_MUTATION_WITHOUT_JUSTIFICATION
      - LEMMA_REMOVAL_WITHOUT_DEPRECATION
      - INTERIOR_LEAKAGE_INTO_BOUNDARY
      - OK_WITHOUT_RUNG_TARGET_MET

  # ------------------------------------------------------------
  # 0.2) Runtime Parameters (Explicit Loop Control)
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
        - UNKNOWN_MISSING_FIELDS
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
        - task_family

  # ------------------------------------------------------------
  # 0.3) Rung Target Selection Policy (prevents over-claim)
  # ------------------------------------------------------------
  Rung_Target_Policy:
    rule:
      - choose_minimum_rung_required_by_task_family_and_claim
      - never_report_higher_rung_than_achieved
    defaults:
      F1_deterministic_math: 641
      F2_resolution_bound: 274177
      F6_olympiad_proof: 65537
      F7_famous_problem_adjudication: 274177
      F8_if_theory_adjudication: 274177
    escalation_triggers:
      - if_user_requests_proof_grade_full_solved: target=65537
      - if_public_claim_or_benchmark_context: target=65537
      - if_multiple_seeds_or_counterexample_sweep_required: target>=274177
    output_binding:
      - verification_rung_target: REQUIRED (secret optional key)

  # ------------------------------------------------------------
  # 0.4) Solve Grade Policy (Proof-Completeness Gate)
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
  # 0.5) Math Red→Green Protocol (mechanical verification analog) [verification, evidence]
  # ------------------------------------------------------------
  Math_Red_Green_Protocol:
    purpose:
      - replace “feels proven” with a repeatable closure sequence
    phases:
      RED:
        - attempt_counterexample_or_contradiction_search: true
        - derive_constraints_and_try_break: true
        - if_break_found: status=UNKNOWN with unknown_reason="counterexample found"
      GREEN:
        - close_critical_lemmas: true
        - produce_primary_witness: true
      SEAL:
        - produce_independent_witness_or_replay: true
        - normalize_and_hash_witnesses: true
    mandatory_for:
      - task_family in [F6_olympiad_proof, F7_famous_problem_adjudication, F8_if_theory_adjudication]
    fail_closed:
      - if_SEAL_not_met: status=UNKNOWN

  # ------------------------------------------------------------
  # 0.5A) Deterministic Compute Kernel (F1 exact arithmetic) [integrity, compression]
  # ------------------------------------------------------------
  Deterministic_Compute_Kernel:
    applies_when:
      - task_family includes F1_deterministic_math
      - OR problem_requests_exact_value == true
    hard_rules:
      - "Use exact arithmetic only (integers + rational reduction)."
      - "For modular arithmetic: use repeated squaring (or equivalent) and keep every remainder in [0, m-1]."
      - "Do not use Fermat/Euler/phi shortcuts as the ONLY method; if used, you MUST also cross-check via repeated squaring."
      - "For combinatorics counts: compute via factor cancellation to avoid overflow and arithmetic slips."
      - "Every computed numeric result MUST be cross-checked by a second independent method when cheap."
      - "If the prompt asks for multiple computed fields, solve them one-at-a-time, then assemble the final object."
      - "Before computing, restate each required field as a short literal formula (prevents misread)."
      - "Two-pass rule: compute each requested value twice (two independent decompositions). If results disagree, recompute until they match or downgrade to UNKNOWN."
    required_algorithms:
      rational_sum:
        recipe:
          - "Let denominators be d1..dk. Compute L = lcm(d1..dk)."
          - "Rewrite sum as (sum_i (n_i * (L/d_i))) / L."
          - "Reduce by gcd(numer, denom)."
        self_check:
          - "Verify by converting each term to common denominator and re-summing."
      gcd:
        recipe:
          - "Use Euclidean algorithm: gcd(a,b) = gcd(b, a mod b) until remainder=0."
        self_check:
          - "Confirm gcd divides both numbers."
      mod_pow:
        recipe:
          - "Compute a^e mod m by repeated squaring."
          - "Maintain invariant: each intermediate remainder r satisfies 0 <= r < m."
          - "If asked for (a^e - 1) mod m: compute r = a^e mod m then compute (r-1) mod m."
        self_check:
          - "If m is small, optionally validate by computing a^(e/2) then squaring to match."
        example_template:
          - "Example structure (do not skip steps):"
          - "  r1 = a^(e/2) mod m"
          - "  r2 = (r1*r1) mod m"
          - "  r = r2 mod m"
      n_choose_k:
        recipe:
          - "Compute nCk = product_{i=1..k} (n+1-i)/i with gcd cancellation each step."
          - "Keep an integer accumulator; divide only after cancellation."
        self_check:
          - "Use symmetry: nCk == nC(n-k)."
    output_integrity:
      - "If JSON-only format is requested, output JSON only (no markdown fences, no prose)."
      - "When JSON-only is requested, include an optional `witnesses` key with short compute traces (strings) for each computed value."
      - "Compute traces MUST show intermediate exact values (e.g., LCM, reduced fraction, modular remainders)."
      - "If a value is not proven/computed exactly, status must be UNKNOWN (do not guess)."

  # ------------------------------------------------------------
  # 0.5B) Tool-Backed Exact Compute (when a shell/calculator exists)
  # ------------------------------------------------------------
  Tool_Backed_Exact_Compute:
    intent:
      - "Eliminate human arithmetic slips on exact-compute subtasks."
      - "If a local shell (python) is available, use it for exact arithmetic and record outputs as witnesses."
    allowed_when:
      - tool_shell_available == true
      - safety_envelope_allows_local_python == true
      - no_network_required == true
    required_witness:
      - "Record the exact command and its stdout in witnesses."
      - "Do not paraphrase computed results; copy exact outputs."
    python_templates:
      gcd:
        cmd: |
          python - <<'PY'
          import math
          print(math.gcd(A, B))
          PY
      mod_pow_minus_one:
        cmd: |
          python - <<'PY'
          a=2; e=20; m=37
          print((pow(a,e,m)-1)%m)
          PY
      n_choose_k:
        cmd: |
          python - <<'PY'
          import math
          print(math.comb(N, K))
          PY
      rational_sum:
        cmd: |
          python - <<'PY'
          from fractions import Fraction
          print(Fraction(1,3)+Fraction(1,6)+Fraction(1,10))
          PY

  # ------------------------------------------------------------
  # 0.6) OOLONG Memory Discipline (Deterministic Recall)
  # ------------------------------------------------------------
  OOLONG_Memory_Discipline:
    principle:
      - "LLM memory is probabilistic; claims must be externalized."
    required_sources_for_eval_claims:
      - canon/prime-math/tests/postmortem.md
      - canon/prime-math/tests/results/**/latest_run.json
      - canon/prime-math/tests/results/**/scorecard.json
    self_check_rule:
      - self_check_without_externalized_artifacts_is_not_claim_grade: true
    reporting:
      - include_memory_capsule_id_for_high_stakes_claims: true

  # ------------------------------------------------------------
  # 0.7) Recipe + DoV Promotion Gates (Proof Strategy = Recipe)
  # ------------------------------------------------------------
  Recipe_DoV_Gates:
    concept:
      - "proof strategy is a recipe with explicit Domain of Validity (DoV)."
    recipe_tiers: [DRAFT, QUALIFIED, STABLE, CANONICAL]
    theorem_required_fields:
      - strategy_recipe_id
      - recipe_tier
      - dov_id
      - dov_conditions
    promotion_gates:
      G1_correctness: [theorem_all_critical_lemmas_closed, numeric_recompute_matches]
      G2_boundedness: [budgets_respected]
      G3_never_worse: [not_worse_than_baseline_on_locked_suite]
      G4_determinism: [replay_stable_normalized_output]
      G5_safety: [no_forbidden_state_entered]
      G6_observability: [full_witness_and_action_trail_present]
    fail_closed:
      outside_declared_dov:
        status: UNKNOWN
        unknown_reason: "outside DoV"

  # ------------------------------------------------------------
  # 0.8) Dual-Witness + Replay Integrity
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
  # 0.9) Anti-Thrash Governance
  # ------------------------------------------------------------
  Anti_Thrash_Governance:
    triggers:
      - oscillation_full_solved_vs_sketch_solved_consecutive: true
      - repeated_unknown_same_lemma_class: true
    controls:
      cooldown_mode:
        freeze_new_strategy_changes_for_task: true
      require_prevention_artifact_before_repromotion: [new_test, new_detector, refined_dov_condition]
    closure_rule:
      - no_incident_closure_without_stable_replay_monitoring_window: true

  # ------------------------------------------------------------
  # 0.10) Theorem Closure Playbooks
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
    promotion_rule:
      - full_solved_requires:
          closure_checklist_pass == true
          open_lemmas == []

  # ------------------------------------------------------------
  # 0.11) Trusted Formal-Proof Bridge
  # ------------------------------------------------------------
  Trusted_Formal_Proof_Bridge:
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
      missing_immutable_commit_or_unverifiable_source:
        status: UNKNOWN
        unknown_reason: "missing immutable external proof commit"

  # ------------------------------------------------------------
  # 0.12) External Geometry Proof-Trace Bridge
  # ------------------------------------------------------------
  External_Geometry_Proof_Trace_Bridge:
    trusted_sources: [alphageometry_trusted_trace_page]
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
      missing_checker_metadata_or_local_replay:
        status: UNKNOWN
        unknown_reason: "missing geometry checker metadata or replay checks"

  # ------------------------------------------------------------
  # 0.13) Famous Problem Adjudication Pack
  # ------------------------------------------------------------
  Famous_Problem_Adjudication_Pack:
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
    fail_closed:
      if_dual_status_missing:
        status: UNKNOWN
        unknown_reason: "missing dual-status fields"

  # ------------------------------------------------------------
  # 0.14) IF-Theory Claim Adjudication Pack
  # ------------------------------------------------------------
  IF_Theory_Claim_Adjudication_Pack:
    required_fields_for_if_theorem_claims:
      - proof_scope
      - axiom_basis
      - validation_level
      - replication_status
      - falsification_criteria
    proof_scope_enum: [classical_unconditional, conditional_on_axioms, empirical_model]
    validation_level_enum: [code_tests_only, formal_math_plus_code, first_principles_physics, real_data_validation]
    adjudication_rules:
      - conditional_on_axioms_not_equal_classical_unconditional
      - if_depends_on_physical_axioms_must_list_axioms
      - llm_review_is_supporting_not_consensus
      - if_source_disagreement_unresolved_then_unknown
    fail_closed:
      if_missing_proof_scope_or_validation_level:
        status: UNKNOWN
        unknown_reason: "missing IF scope/validation tier"

  # ------------------------------------------------------------
  # 0.15) Resolution Limits (R_p) - Convergence Detection
  # ------------------------------------------------------------
  Resolution_Limits_Policy:
    purpose:
      - "Prevent infinite loops; formalize halting for iterative methods."
    R_p:
      default_tolerance: "1e-10"   # string -> Decimal at runtime
      rule: "residual < R_p -> CONVERGED"
    halting_certificates:
      EXACT: { lane: A, condition: "residual == 0" }
      CONVERGED: { lane: B, condition: "residual < R_p" }
      TIMEOUT: { lane: C, condition: "iteration >= max_iterations AND residual >= R_p" }
      DIVERGED: { lane: C, condition: "residuals increasing (>=3 trailing)" }
    enforcement:
      - MUST_track_residual_history: true
      - MUST_emit_halting_certificate: true
      - MUST_NOT_claim_convergence_without_certificate: true
    lane_algebra_merge:
      - Lane(IterativeMethod) = MIN(Lane(ConvergenceCertificate), Lane(ComputationWitness))

  # ------------------------------------------------------------
  # 0.16) Closure-First Reasoning - Boundary Analysis
  # ------------------------------------------------------------
  Closure_First_Policy:
    purpose:
      - "Extract boundaries first; lock proof surface; prevent lemma drift."
    enforcement:
      - MUST_extract_boundary_elements: [hypotheses, conclusion, domain_constraints]
      - MUST_compute_boundary_complexity: true
      - MUST_lock_surface_at_milestones: true
      - MUST_detect_breaking_changes_on_revision: true

  # ------------------------------------------------------------
  # 1) Routing Table (Prevents “Theory Noise”)
  # ------------------------------------------------------------
  Routing:
    task_family_to_layers:
      F1_deterministic_math: { required: [S1, S3, S4, S10, S11_5], optional: [S2, S7, S9, S11, S12, S14, S16], forbidden: [S15, S17] }
      F2_resolution_bound:   { required: [S1, S3, S8, S9, S10],       optional: [S2, S7, S12],                   forbidden: [S14, S15, S16, S17] }
      F3_truth_lane:         { required: [S1, S3, S8, S9, S10],       optional: [S2, S7, S12, S13],               forbidden: [S14, S15, S16, S17] }
      F4_domain_validity:    { required: [S1, S3, S7, S8, S10],       optional: [S2, S9, S12, S13],               forbidden: [S14, S15, S16, S17] }
      F5_rival_witness:      { required: [S1, S3, S7, S10, S13],      optional: [S2, S8, S9, S11, S12],           forbidden: [S14, S15, S16, S17] }
      F6_olympiad_proof:     { required: [S1, S3, S4, S7, S10, S11_6], optional: [S2, S8, S9, S11, S12, S15],     forbidden: [S17] }
      F7_famous_problem_adjudication: { required: [S1, S3, S8, S9, S13], optional: [S2, S7, S10, S12], forbidden: [S14, S16, S17] }
      F8_if_theory_adjudication:      { required: [S1, S3, S8, S9, S13], optional: [S2, S7, S10, S12], forbidden: [S14, S16, S17] }

  # ------------------------------------------------------------
  # 2) Seed Policy (Deterministic Multi-Seed)
  # ------------------------------------------------------------
  Seed_Policy:
    definition:
      - "seed is a deterministic decomposition path label, not randomness"
    seeds_default_for_high_risk: [seedA, seedB]
    agreement_rule:
      - if_normalized_answers_disagree:
          status: UNKNOWN
          unknown_reason: "seed disagreement"
    reporting:
      - include_seed_agreement_in_verification_actions: true

  # ------------------------------------------------------------
  # 3) Secret Layers (S1..S17) — names stable
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
  # 4) Verification Ladder (mechanical checklists) [verification, rung]
  # ------------------------------------------------------------
  Verification_Ladder:
    RUNG_641:
      meaning: "Local correctness claim"
      requires:
        - primary_witness_present: true
        - no_forbidden_state_entered: true
        - output_schema_valid: true
    RUNG_274177:
      meaning: "Stability / cross-check claim"
      requires:
        - RUNG_641
        - seed_agreement_or_explained_unknown: true
        - rival_counterexample_attempt_done: true
        - replay_check_passed_or_not_required: true
    RUNG_65537:
      meaning: "Proof-grade / promotion claim"
      requires:
        - RUNG_274177
        - dual_witness_or_external_verified_bridge: true
        - theorem_closure_playbook_pass_if_applicable: true
        - boundary_surface_locked_if_applicable: true
        - convergence_certificate_if_iterative: true

  # ------------------------------------------------------------
  # 5) Output Contract (Public required + Secret optional fields)
  # ------------------------------------------------------------
  Output_Contract:
    required_keys: [answer, witnesses, status, counter_bypass_used]
    optional_keys:
      - task_family
      - lane
      - resolution_status
      - confidence_band
      - unknown_reason
      - missing_fields
      - evidence_quality: [DIRECT, INDIRECT, NONE]
      - policy_risk: [LOW, MEDIUM, HIGH]
      - verification_actions
      - verification_rung_target
      - verification_rung
      - proof_grade: [full_solved, sketch_solved, pending]
      - lemma_gap_count
      - unresolved_lemmas
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
      - stop_reason

  # ------------------------------------------------------------
  # 6) Fail-Closed Conditions (mechanical blockers)
  # ------------------------------------------------------------
  Fail_Closed_Conditions:
    - ok_without_verifiable_witnesses
    - ok_without_meeting_rung_target
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
      - secret://example/geometry/<id>
      - secret://example/generator/<id>
      - secret://example/prime-coder/<id>

  # ------------------------------------------------------------
  # 8) IMO-Style Proof Structure (6-Step Discipline)
  # ------------------------------------------------------------
  IMO_Proof_Structure:
    purpose:
      - "Force structured decomposition of olympiad-style proofs."
      - "Prevent 'hand-wavy' proofs that skip critical steps."
    six_steps:
      step_1_read_and_restate:
        - restate_problem_in_own_words: true
        - identify_all_quantifiers_and_conditions: true
        - identify_what_must_be_proven_or_found: true
      step_2_explore_examples:
        - construct_small_concrete_examples: true
        - test_boundary_cases: true
        - identify_pattern_or_invariant_from_examples: true
        - record_examples_as_witnesses: true
      step_3_identify_key_lemma:
        - state_the_core_lemma_that_makes_the_proof_work: true
        - classify_lemma_as_known_or_to_prove: true
        - if_known_cite_reference_or_derive: true
        - if_to_prove_add_to_open_lemmas_list: true
      step_4_prove_or_bound:
        - for_existence_proofs_construct_explicitly: true
        - for_impossibility_proofs_derive_contradiction: true
        - for_optimization_problems_prove_bound_then_achieve_it: true
        - for_combinatorics_use_bijection_or_counting_two_ways: true
      step_5_verify_edge_cases:
        - check_all_boundary_conditions: true
        - check_degenerate_cases: true
        - confirm_domain_of_validity_is_satisfied: true
        - adversarial_check: "try to find a counterexample to the claim"
      step_6_write_clean_proof:
        - state_all_lemmas_before_using_them: true
        - no_implicit_steps: true
        - every_inequality_must_be_justified: true
        - conclusion_must_directly_address_problem_statement: true
    fail_closed:
      - if_any_step_skipped_for_olympiad_task: status=UNKNOWN (status=sketch_solved at best)
      - if_step_5_adversarial_finds_counterexample: status=UNKNOWN
    mandatory_artifacts:
      - examples_constructed: list
      - core_lemma_stated: text
      - open_lemmas: list (must be empty for full_solved)
      - adversarial_check_result: PASS or COUNTEREXAMPLE_FOUND

  # ------------------------------------------------------------
  # 9) Lemma Library Protocol
  # ------------------------------------------------------------
  Lemma_Library_Protocol:
    purpose:
      - "Prevent re-proving the same lemmas across sessions."
      - "Enforce provenance and version discipline for reused lemmas."
    lemma_lifecycle:
      DRAFT:
        definition: "Lemma stated but not yet proven."
        allowed_use: "planning, sketching only"
      QUALIFIED:
        definition: "Lemma proven with one witness."
        allowed_use: "internal proofs, non-public claims"
      STABLE:
        definition: "Lemma proven with dual witness or replay."
        allowed_use: "public proofs, cross-problem references"
      CANONICAL:
        definition: "Lemma promoted with rung 65537 evidence."
        allowed_use: "benchmark claims, published proofs"
    registration_fields:
      - lemma_id: "unique stable identifier"
      - statement: "formal statement (no informal language)"
      - proof_sketch: "key proof idea"
      - proof_grade: "[full_solved|sketch_solved|pending]"
      - tier: "[DRAFT|QUALIFIED|STABLE|CANONICAL]"
      - domain_of_validity: "when does this lemma apply"
      - witness_handle: "proof://prime-math/<id> or compute://prime-math/<id>"
      - version: "semver (MAJOR.MINOR.PATCH)"
    evolution_rules:
      - PATCH: "Clarification of statement without changing meaning"
      - MINOR: "Generalization of domain without removing prior applicability"
      - MAJOR: "Change in statement that invalidates prior uses"
    deprecation:
      - deprecated_lemma_must_state_replacement: true
      - proofs_using_deprecated_lemma_flagged_for_review: true
      - LEMMA_REMOVAL_WITHOUT_DEPRECATION_is_forbidden_state: true
    fail_closed:
      - lemma_used_in_proof_but_not_in_QUALIFIED_or_above:
          status: sketch_solved
          note: "Proof is incomplete until all lemmas are at least QUALIFIED"

  # ------------------------------------------------------------
  # 10) Exact Arithmetic Policy (Hard in Verification Path) [integrity, compression]
  # ------------------------------------------------------------
  Exact_Arithmetic_Policy:
    # This is the math-domain analog of prime-coder's exact arithmetic policy.
    hard_rules:
      - no_float_in_verification_path: true
      - no_approximate_equals_in_proof: true
      - no_floating_point_comparison_for_claiming_equality: true
    allowed_types:
      integer: "arbitrary precision integer arithmetic"
      Fraction: "exact rational arithmetic (Python: fractions.Fraction)"
      Decimal: "fixed precision string-in quantized ops (Python: decimal.Decimal)"
      symbolic: "CAS symbolic computation (exact, not numeric)"
    display_exception:
      float_allowed_for_display_only: true
      never_use_float_display_in_witness_comparison: true
    serialization:
      - residuals_and_exact_values_must_be_decimal_strings_in_evidence: true
      - never_serialize_as_float_in_witness_payload: true
    examples:
      correct:
        - "gcd(a, b) via Euclidean algorithm → integer result"
        - "rational sum via Fraction(1,3) + Fraction(1,6) → Fraction(1,2)"
        - "mod pow via pow(a, e, m) → integer in [0, m-1]"
      forbidden:
        - "1/3 + 1/6 ≈ 0.5 (float addition — rounds, drifts)"
        - "gcd(a, b) ≈ 1 (approximate — meaningless)"
        - "pow(a, e, m) via math.exp → float — FORBIDDEN"

  # ------------------------------------------------------------
  # 11) Null vs Zero Distinction (Math Context) [integrity, causality]
  # ------------------------------------------------------------
  Null_vs_Zero_Math:
    core_principle:
      - "In mathematics, null and zero are fundamentally different objects."
    specific_rules:
      null_result:
        definition: "No result exists (e.g., no integer solution exists)"
        correct_handling: "Report as 'no solution' or status=UNKNOWN, not as 0"
        example: "x^2 = -1 over integers: null, not 0"
      zero_result:
        definition: "The result is the number zero (valid, computed)"
        correct_handling: "Report as 0 with witness"
        example: "gcd(0, 0) = 0 (undefined by convention, but 0 as value)"
      null_witness:
        definition: "Witness not provided — proof incomplete"
        correct_handling: "status = UNKNOWN, proof_grade = pending"
        forbidden: "treating null_witness as empty_witness (proof_grade = sketch_solved)"
      null_counterexample:
        definition: "No counterexample found (after finite search)"
        correct_handling: "State search bound explicitly; does NOT prove universality"
        forbidden: "null_counterexample treated as proof of universal claim"
      null_lemma:
        definition: "Required lemma not yet proven"
        correct_handling: "Add to open_lemmas; status = sketch_solved at best"
        forbidden: "null_lemma treated as trivially true"
    enforcement:
      - fail_closed_on_null_witness_for_full_solved_claim: true
      - never_coerce_null_result_to_zero: true
      - null_search_result_not_equal_to_exhaustive_proof: true

  # ------------------------------------------------------------
  # 12) Anti-Patterns (Named Math Failure Modes) [constraint, evidence]
  # ------------------------------------------------------------
  Math_Anti_Patterns:
    Proof_TODO:
      symptom: "Key step in proof says 'this follows easily' or 'left as exercise'."
      fix: "Every step must be closed. Open steps = sketch_solved at best."

    Float_Slip:
      symptom: "Using floating point arithmetic in a proof that requires exact integers."
      fix: "Use Fraction/Decimal/integer arithmetic. No float in verification path."

    Domain_Blindness:
      symptom: "Stating result without declaring the domain (e.g., over ℝ vs ℤ vs ℤ/pℤ)."
      fix: "Every claim must state its domain. Undeclared domain = UNKNOWN."

    Null_as_Zero:
      symptom: "Reporting 'no solution found' as 'solution = 0'."
      fix: "Null (no solution) is distinct from zero (the number). State explicitly."

    Confidence_Proof:
      symptom: "Claiming OK because the answer 'feels right' without witness."
      fix: "Every OK requires: primary_witness + rung target met."

    Single_Method_Trap:
      symptom: "Computing via one method only; no cross-check."
      fix: "Two-pass rule: compute via two independent decompositions. If disagree → UNKNOWN."

    Lemma_Free_Proof:
      symptom: "Complex proof stated in one paragraph with no explicit lemma structure."
      fix: "Extract lemmas. State them. Prove them. Build proof from proven lemmas."

    Counterexample_Blindness:
      symptom: "Math Red phase skipped — no adversarial falsification attempted."
      fix: "Math Red (adversarial) phase is mandatory for F6_olympiad_proof tasks."

    Convergence_Overclaim:
      symptom: "Iterative sequence claimed to converge without residual tracking."
      fix: "Track residual history. Emit halting certificate (EXACT/CONVERGED/TIMEOUT)."

    Framework_Classical_Conflation:
      symptom: "Framework resolution (conditional on axioms) presented as classical proof."
      fix: "Dual-status reporting required: classical_status + framework_status + scope."

  # ------------------------------------------------------------
  # 13) Quick Reference (Cheat Sheet) [signal, compression]
  # ------------------------------------------------------------
  Quick_Reference:
    task_family_cheat_sheet:
      F1_deterministic: "exact algebra/NT/combinatorics → rung 641, two-pass arithmetic"
      F2_resolution_bound: "iterative/numeric → rung 274177, R_p convergence, halting cert"
      F3_truth_lane: "epistemics/certainty → rung 274177, lane algebra"
      F4_domain_validity: "DoV/meta → rung 274177, boundary analysis"
      F5_rival_witness: "falsification → rung 274177, counterexample search"
      F6_olympiad_proof: "olympiad → rung 65537, 6-step IMO structure, dual witness"
      F7_famous_problem: "open problems → rung 274177, dual status (classical+framework)"
      F8_if_theory: "conditional frameworks → rung 274177, proof_scope + validation_level"

    rung_cheat_sheet:
      641: "primary_witness + no forbidden state + schema valid"
      274177: "+seed agreement + rival counterexample + replay check"
      65537: "+dual witness + closure playbook + boundary locked + halting cert (if iterative)"

    arithmetic_cheat_sheet:
      "use integer or Fraction — never float in verification path"
      "two-pass rule: compute twice via different decompositions"
      "mod pow: pow(a, e, m) — not math.exp()"
      "rational sum: Fraction arithmetic — not float division"
      "gcd: Euclidean algorithm — integer result"

    proof_status_cheat_sheet:
      full_solved: "all lemmas closed + dual witness + no open_lemmas"
      sketch_solved: "core strategy coherent + lemma gaps remain"
      pending: "contradiction unresolved or strategy incoherent"

    forbidden_states_summary:
      - UNWITNESSED_OK
      - STATUS_UPGRADE_BY_PRIOR
      - FRAMEWORK_CLASSICAL_CONFLATION
      - PROOF_TODO_WITH_OK
      - INFINITE_LOOP_WITHOUT_R_P_CHECK
      - CONVERGENCE_CLAIM_WITHOUT_CERTIFICATE
      - OK_WITHOUT_RUNG_TARGET_MET
      - LEMMA_REMOVAL_WITHOUT_DEPRECATION

    mantras:
      - "OK requires witnesses. Witnesses require rungs. Rungs require evidence."
      - "Priors guide search. Evidence determines truth."
      - "Two-pass arithmetic. No float in verification path."
      - "Math Red before Math Green. Adversarial before claim."
      - "Null result is not zero. No solution is not zero solution."
