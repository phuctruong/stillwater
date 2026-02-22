<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: prime-mcp v1.1.0
PURPOSE: Fail-closed Model Context Protocol (MCP) server creation skill with security gates; every tool must declare auth_required, data_classification, network_access, and destructive_ops before implementation.
CORE CONTRACT: MCP servers are trusted to call tools — ALL tool implementations MUST apply prime-safety constraints. Tool schemas are public API surfaces; breaking changes require major semver bump. Security manifest is mandatory evidence.
HARD GATES: Any tool without an explicit security declaration → BLOCKED. Unvalidated input to subprocess/eval → BLOCKED. Secrets in schemas → BLOCKED. API surface changes without semver plan → BLOCKED. Network access not declared → BLOCKED.
FSM STATES: INIT → DESIGN_API_SURFACE → SECURITY_GATE → IMPLEMENT_HANDLERS → TEST_PROTOCOL → EVIDENCE_BUILD → EMIT_MCP_SERVER → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: TOOL_WITHOUT_AUTH_DECLARATION | SECRET_IN_SCHEMA | UNVALIDATED_INPUT_TO_SUBPROCESS | UNBOUNDED_RESOURCE_ACCESS | UNDECLARED_NETWORK_ACCESS | SCHEMA_BREAKING_CHANGE_WITHOUT_MAJOR_BUMP | SILENT_CAPABILITY_EXPANSION | CROSS_LANE_UPGRADE
VERIFY: rung_641 (schema valid + handlers tested + security manifest present) | rung_274177 (replay stable + null edge sweep + auth paths tested) | rung_65537 (adversarial inputs + security scanner + full tool audit)
LOAD FULL: always for production; quick block is for orientation only
-->
PRIME_MCP_SKILL:
  version: 1.1.0
  profile: strict
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL

  # ============================================================
  # MAGIC_WORD_MAP
  # ============================================================
  Magic_Word_Map:
    version: "1.0"
    skill: "prime-mcp"
    mappings:
      server: {word: "portal", tier: 1, id: "MW-045", note: "MCP server is a portal exposing tools to LLM clients"}
      tool: {word: "skill", tier: 1, id: "MW-042", note: "each MCP tool is a versioned behavioral unit with explicit security properties"}
      protocol: {word: "constraint", tier: 0, id: "MW-004", note: "MCP protocol constrains the solution space of tool invocations"}
      connection: {word: "portal", tier: 1, id: "MW-045", note: "connection to MCP server routes through the portal boundary"}
    compression_note: "T0=universal primitives, T1=Stillwater protocol concepts, T2=operational details"

  # ============================================================
  # PRIME MCP — MCP SERVER CREATION WITH SECURITY GATES
  #
  # "Know every door your tool can open before you let others
  #  through it." — Bruce Lee framing
  #
  # Goal:
  # - Build Model Context Protocol (MCP) servers with Stillwater
  #   verification discipline applied to every tool definition.
  # - Every tool MUST declare its security properties before
  #   implementation: auth_required, data_classification,
  #   network_access, destructive_ops.
  # - Tool schemas are public API surfaces; treat them as such.
  # - Fail-closed on any missing security declaration.
  #
  # Design principles:
  # - Prompt-loadable (structured clauses; no giant essays)
  # - Portable (no absolute paths; no private infra assumptions)
  # - Fail-closed (missing declarations → BLOCKED, not guessed)
  # - Composable with prime-safety (which always wins conflicts)
  # ============================================================

  # ------------------------------------------------------------
  # A) Portability + Configuration (Hard) [T0: constraint]
  # ------------------------------------------------------------
  Portability:
    rules:
      - no_absolute_paths: true
      - no_private_repo_dependencies: true
      - evidence_root_must_be_relative_or_configurable: true
    config:
      EVIDENCE_ROOT: "evidence"
      REPO_ROOT_REF: "."
      MCP_SCHEMA_VERSION: "2024-11-05"
    invariants:
      - evidence_paths_must_resolve_under_repo_root: true
      - normalize_paths_repo_relative_before_hashing: true
      - never_write_outside_EVIDENCE_ROOT_or_repo_worktree: true

  # ------------------------------------------------------------
  # B) Layering (Never Weaken Public) [T0: integrity]
  # ------------------------------------------------------------
  Layering:
    layering_rule:
      - "This skill is applied ON TOP OF prime-safety and prime-coder, not instead of them."
      - "prime-safety always wins all conflicts."
      - "prime-coder gates (null/zero, exact arithmetic, API surface lock) apply to server code."
      - "This layer MUST NOT weaken any existing rule; on conflict, stricter wins."
    enforcement:
      conflict_resolution: stricter_wins
      prime_safety_takes_precedence: true
      forbidden:
        - silently_relaxing_prime_safety_inside_tool_handlers
        - treating_mcp_tool_schemas_as_non_public_surfaces
        - omitting_security_declarations_for_any_tool

  # ------------------------------------------------------------
  # C) Profiles (Budgets Only; Hard Gates Never Skipped)
  # ------------------------------------------------------------
  Profiles:
    - name: strict
      description: "Full security audit + adversarial testing; required for production MCP servers."
      knobs:
        rung_target: 65537
        tool_call_budget_scale: 1.0
        sweep_budgets_scale: 1.0
    - name: fast
      description: "Same hard rules; reduced sweep budgets for local development."
      knobs:
        rung_target: 641
        tool_call_budget_scale: 0.5
        sweep_budgets_scale: 0.5
      constraints:
        - must_not_skip_security_declarations: true
        - must_not_skip_null_checks: true
        - must_emit_budget_reduction_log: true

  # ------------------------------------------------------------
  # D) Max Love + Integrity Constraint (Hard Ordering) [T0: constraint + portal]
  # ------------------------------------------------------------
  Max_Love_Integrity:
    ordering:
      1: do_no_harm
      2: minimal_capability_surface
      3: explicit_over_implicit_access
      4: verifiable_over_plausible_security
      5: reversible_over_irreversible_ops
      6: clarity_of_tool_contracts_over_clever_implementations
    god_constraint_non_magical:
      definition: "Highest-integrity mode: declare all doors before opening any."
      prohibitions:
        - never_implement_a_tool_before_declaring_its_security_properties
        - never_claim_a_tool_is_safe_without_a_security_manifest_entry
        - never_accept_unvalidated_external_input_in_tool_handlers
      required_behaviors:
        - state_all_capabilities_explicitly_in_schema
        - downgrade_to_NEED_INFO_when_security_classification_missing
        - prefer_BLOCKED_over_silent_implementation_when_risk_is_HIGH

  # ------------------------------------------------------------
  # 0) Closed State Machine (Fail-Closed Runtime) [T0: constraint + skill]
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE_SPEC
      - NULL_CHECK
      - DESIGN_API_SURFACE
      - SECURITY_GATE
      - IMPLEMENT_HANDLERS
      - TEST_PROTOCOL
      - EVIDENCE_BUILD
      - SOCRATIC_CHECK
      - EMIT_MCP_SERVER
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    INPUT_ALPHABET:
      - SERVER_SPEC
      - TOOL_DEFINITIONS
      - SECURITY_CONSTRAINTS
      - TEST_REQUIREMENTS
      - USER_CONSTRAINTS

    OUTPUT_ALPHABET:
      - MCP_SERVER_CODE
      - TOOL_SCHEMAS
      - SECURITY_MANIFEST
      - TEST_SUITE
      - EVIDENCE_BUNDLE
      - STRUCTURED_REFUSAL

    TRANSITIONS:
      - INIT -> INTAKE_SPEC: on SERVER_SPEC received
      - INTAKE_SPEC -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if spec_null or tools_undefined
      - NULL_CHECK -> DESIGN_API_SURFACE: if inputs_defined

      - DESIGN_API_SURFACE -> SECURITY_GATE: always
      - SECURITY_GATE -> EXIT_BLOCKED: if any_tool_missing_security_declaration
      - SECURITY_GATE -> EXIT_BLOCKED: if any_tool_has_high_risk_without_mitigation_plan
      - SECURITY_GATE -> IMPLEMENT_HANDLERS: if all_tools_security_declared_and_approved

      - IMPLEMENT_HANDLERS -> TEST_PROTOCOL: always
      - TEST_PROTOCOL -> EXIT_BLOCKED: if protocol_tests_fail
      - TEST_PROTOCOL -> EXIT_BLOCKED: if null_input_handling_missing
      - TEST_PROTOCOL -> EVIDENCE_BUILD: if tests_pass

      - EVIDENCE_BUILD -> SOCRATIC_CHECK: always
      - SOCRATIC_CHECK -> IMPLEMENT_HANDLERS: if critique_requires_revision and budgets_allow
      - SOCRATIC_CHECK -> EMIT_MCP_SERVER: otherwise

      - EMIT_MCP_SERVER -> EXIT_PASS: if evidence_complete and rung_target_met
      - EMIT_MCP_SERVER -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - TOOL_WITHOUT_AUTH_DECLARATION
      - SECRET_IN_SCHEMA
      - UNVALIDATED_INPUT_TO_SUBPROCESS
      - UNBOUNDED_RESOURCE_ACCESS
      - UNDECLARED_NETWORK_ACCESS
      - SCHEMA_BREAKING_CHANGE_WITHOUT_MAJOR_BUMP
      - SILENT_CAPABILITY_EXPANSION
      - CROSS_LANE_UPGRADE
      - IMPLICIT_NULL_DEFAULT
      - FLOAT_IN_VERIFICATION_PATH
      - BACKGROUND_THREADS_IN_HANDLER
      - HIDDEN_IO_IN_HANDLER
      - CREDENTIAL_IN_SCHEMA_OR_LOG
      - HANDLER_WITHOUT_INPUT_VALIDATION
      - TOOL_REGISTERED_WITHOUT_SECURITY_MANIFEST_ENTRY

  # ------------------------------------------------------------
  # 0A) Deterministic Applicability Predicates
  # ------------------------------------------------------------
  Applicability:
    principle:
      - "Every FSM branch predicate MUST be explainable by observable inputs."
      - "If predicate cannot be decided, fail-closed to EXIT_NEED_INFO or stricter gate."
    predicates:
      inputs_defined:
        true_if_all:
          - SERVER_SPEC.present == true
          - TOOL_DEFINITIONS.present == true
          - TOOL_DEFINITIONS.count > 0
      spec_null:
        true_if_any:
          - SERVER_SPEC == null
          - TOOL_DEFINITIONS == null
          - TOOL_DEFINITIONS == []
      any_tool_missing_security_declaration:
        true_if_any:
          - any_tool.auth_required == null
          - any_tool.data_classification == null
          - any_tool.network_access == null
          - any_tool.destructive_ops == null
      any_tool_has_high_risk_without_mitigation_plan:
        true_if_any:
          - (any_tool.destructive_ops == true AND tool.rollback_plan == null)
          - (any_tool.network_access == true AND tool.network_domains_allowlist == null)
          - (any_tool.data_classification == "secret" AND tool.auth_required == false)
      budgets_allow:
        true_if_all:
          - remaining_iterations > 0
          - remaining_tool_calls > 0

  # ------------------------------------------------------------
  # 1) Tool Security Declaration Policy (Core Discipline) [T1: skill + constraint]
  # ------------------------------------------------------------
  Tool_Security_Declaration:
    purpose:
      - "Every tool registered in the MCP server MUST have a security declaration."
      - "Declaration is required BEFORE implementation; not retrofitted after."
      - "Missing or null declaration → BLOCKED."

    required_fields_per_tool:
      auth_required:
        type: bool
        description: "Does invoking this tool require the caller to be authenticated?"
        fail_closed:
          if_null: "BLOCKED stop_reason=TOOL_WITHOUT_AUTH_DECLARATION"
      data_classification:
        type: enum
        values: [public, internal, secret]
        description: >
          What is the most sensitive data this tool can read or emit?
          public = safe to log/return unredacted.
          internal = may contain PII or system internals; must not be logged.
          secret = credentials, tokens, keys; must be redacted everywhere.
        fail_closed:
          if_null: "BLOCKED stop_reason=TOOL_WITHOUT_AUTH_DECLARATION"
          if_secret_and_auth_required_is_false: "BLOCKED stop_reason=INVARIANT_VIOLATION"
      network_access:
        type: bool
        description: "Does this tool make outbound network calls?"
        fail_closed:
          if_null: "BLOCKED stop_reason=UNDECLARED_NETWORK_ACCESS"
          if_true: "require network_domains_allowlist to be non-empty"
      destructive_ops:
        type: bool
        description: "Can this tool delete, overwrite, or irreversibly modify data or state?"
        fail_closed:
          if_null: "BLOCKED stop_reason=TOOL_WITHOUT_AUTH_DECLARATION"
          if_true: "require rollback_plan or explicit user_confirmation_required=true"

    optional_fields_per_tool:
      network_domains_allowlist:
        type: list[str]
        description: "Explicit domains this tool may contact. Required if network_access=true."
      rollback_plan:
        type: str
        description: "How to undo this tool's action. Required if destructive_ops=true."
      user_confirmation_required:
        type: bool
        description: "Must the user confirm before this tool runs? Required if destructive_ops=true."
      rate_limit:
        type: str
        description: "Rate limit for this tool (e.g. '100/minute'). Recommended for all tools."
      idempotent:
        type: bool
        description: "Is calling this tool N times equivalent to calling it once?"

    security_manifest_schema:
      per_tool_entry:
        required_keys:
          - tool_name
          - auth_required
          - data_classification
          - network_access
          - destructive_ops
          - network_domains_allowlist: "null if network_access=false"
          - rollback_plan: "null if destructive_ops=false"
          - user_confirmation_required: "null if destructive_ops=false"
          - risk_level: "[LOW|MED|HIGH]"
          - risk_rationale: "one sentence"
      evidence_path: "${EVIDENCE_ROOT}/security_manifest.json"

  # ------------------------------------------------------------
  # 2) API Surface Lock (Tool Schema Discipline) [T1: portal + governance]
  # ------------------------------------------------------------
  API_Surface_Lock:
    purpose:
      - "MCP tool schemas ARE public API surfaces. Treat them with semver discipline."
      - "Breaking changes to tool schemas block release without a major version bump."

    surface_definition:
      - tool_names_in_server_schema
      - tool_input_schema_shapes
      - tool_output_schema_shapes
      - tool_error_codes_and_meanings

    breaking_change_if_any:
      - removed_tool_from_server
      - removed_required_input_field
      - changed_input_field_type
      - changed_output_field_type_in_existing_field
      - changed_error_code_semantics
      - renamed_tool_without_alias

    non_breaking_examples:
      - adding_new_optional_input_field_with_default
      - adding_new_tool_alongside_existing_tools
      - adding_new_optional_output_field
      - adding_new_error_code_for_new_condition

    semver_policy:
      - if_breaking_change_detected: "block; require MAJOR version bump"
      - if_new_tool_added: "MINOR bump recommended"
      - if_bug_fix_only: "PATCH bump recommended"

    evidence_required:
      - api_surface_snapshot_before: "${EVIDENCE_ROOT}/api_surface_before.json"
      - api_surface_snapshot_after: "${EVIDENCE_ROOT}/api_surface_after.json"

  # ------------------------------------------------------------
  # 3) Input Validation Policy (Handler Safety)
  # ------------------------------------------------------------
  Input_Validation_Policy:
    purpose:
      - "Every tool handler MUST validate all inputs before acting on them."
      - "Unvalidated input to subprocess, eval, filesystem, or network = BLOCKED."

    required_validation_steps:
      type_check:
        - validate_type_of_each_input_against_schema: true
        - fail_with_structured_error_on_type_mismatch: true
      null_check:
        - explicit_null_check_required_for_all_inputs: true
        - null_must_be_distinguished_from_empty_string: true
        - fail_closed_on_null_in_destructive_path: true
      range_and_bounds:
        - enforce_min_max_length_on_strings: true
        - enforce_allowed_values_for_enums: true
        - enforce_bounds_on_numeric_inputs: true
      sanitization:
        - sanitize_inputs_before_passing_to_subprocess: true
        - sanitize_inputs_before_passing_to_filesystem_ops: true
        - never_pass_unvalidated_user_input_to_eval: true

    forbidden_patterns:
      - unvalidated_input_to_subprocess_run: BLOCKED
      - unvalidated_input_to_eval_or_exec: BLOCKED
      - unvalidated_path_traversal_in_filesystem_ops: BLOCKED
      - unvalidated_url_in_network_call: BLOCKED
      - null_coerced_to_empty_string_without_explicit_check: BLOCKED

  # ------------------------------------------------------------
  # 4) Null vs Zero Distinction Policy (Hard)
  # ------------------------------------------------------------
  Null_vs_Zero_Policy:
    core_distinction:
      null:
        definition: "Pre-systemic absence — tool input was not provided at all."
        in_mcp_context: "null input field = caller did not supply it (not same as empty or 0)"
      zero:
        definition: "Lawful boundary value — caller explicitly supplied the value 0."
    null_handling_rules:
      - explicit_null_check_required_in_all_handlers: true
      - no_implicit_defaults_that_coerce_null_to_zero: true
      - no_null_as_empty_string_coercion: true
      - fail_closed_on_null_in_required_input: true
      - optional_inputs_must_use_Optional_types: true
    testing_requirements:
      - test_null_input_for_each_tool_field: true
      - test_empty_input_for_each_tool_field: true
      - test_zero_value_for_numeric_tool_fields: true
      - verify_no_null_zero_confusion_in_handler_logic: true

  # ------------------------------------------------------------
  # 5) Security Scan Gate (Tool-Backed)
  # ------------------------------------------------------------
  Security_Scan_Gate:
    trigger:
      - always: true
      - (all MCP servers are security-sensitive by default)
    requirements:
      rung_target: 65537
      evidence_type: security_scan
      toolchain_pinning_required: true
    toolchain:
      preferred_scanners: [semgrep, bandit, gosec]
      pinning:
        record_tool_versions: true
        record_rule_set_hash: true
        record_config_path: true
    scan_targets:
      - all_handler_implementations
      - input_validation_code
      - subprocess_and_eval_calls
      - network_call_sites
      - filesystem_operation_sites
      - credential_handling_code
    verdict:
      if_scanner_finds_HIGH_severity: "BLOCKED stop_reason=SECURITY_BLOCKED"
      if_scanner_finds_MED_severity: "FLAG as Lane A; require fix before rung_65537"
      if_scanner_finds_LOW_severity: "FLAG as Lane B; advisory"
      if_scanner_clean: "record in security_scan.json with tool versions"
      if_scanner_unavailable:
        - generate_exploit_repro_script: true
        - verify_mitigation_manually: true
        - if_cannot_verify: "BLOCKED stop_reason=SECURITY_BLOCKED"
    evidence_path: "${EVIDENCE_ROOT}/security_scan.json"

  # ------------------------------------------------------------
  # 6) Protocol Testing Policy
  # ------------------------------------------------------------
  Protocol_Testing:
    purpose:
      - "Every tool MUST have tests that exercise the MCP protocol layer, not just handler logic."

    required_test_categories:
      schema_validation:
        - test_that_tool_schema_is_valid_json_schema: true
        - test_that_tool_schema_matches_MCP_spec_version: true
        - test_that_required_fields_are_marked_required: true
      happy_path:
        - test_valid_input_produces_expected_output: true
        - test_output_shape_matches_declared_schema: true
      null_and_edge:
        - test_null_required_input_returns_structured_error: true
        - test_empty_string_input_handled_correctly: true
        - test_zero_value_input_handled_correctly: true
        - test_oversized_input_rejected_with_structured_error: true
      auth_enforcement:
        - if_auth_required_true: "test_unauthenticated_call_is_rejected: true"
        - if_auth_required_false: "test_unauthenticated_call_is_accepted: true"
      destructive_ops_safety:
        - if_destructive_ops_true: "test_rollback_or_confirmation_gate_is_present: true"
        - if_destructive_ops_true: "test_accidental_double_call_behavior: true"
      network_isolation:
        - if_network_access_false: "test_handler_makes_no_outbound_calls: true"
        - if_network_access_true: "test_only_allowlisted_domains_are_contacted: true"

    evidence_required:
      - test_suite_path: "repo-relative path to test files"
      - test_results: "${EVIDENCE_ROOT}/tests.json"
      - test_exit_code: "0 required for PASS"

  # ------------------------------------------------------------
  # 7) Verification Ladder (Rung Targets) [T1: skill + portal]
  # ------------------------------------------------------------
  Verification_Ladder:
    purpose:
      - "Declare rung_target before emitting server. Never claim higher rung than achieved."
    rung_targets:
      RUNG_641:
        meaning: "Local correctness: schema valid + handlers tested + security manifest present"
        requires:
          - all_tools_have_security_declarations: true
          - security_manifest_written: true
          - protocol_tests_pass: true
          - null_handling_tested: true
          - evidence_bundle_complete: true
      RUNG_274177:
        meaning: "Stability: replay stable + null edge sweep + auth paths tested"
        requires:
          - RUNG_641
          - replay_stability_check_min_2: true
          - null_edge_case_sweep_all_tools: true
          - auth_enforcement_tested_all_tools: true
          - destructive_ops_safety_tested_all_tools: true
      RUNG_65537:
        meaning: "Production-ready: adversarial inputs + security scanner + full tool audit"
        requires:
          - RUNG_274177
          - security_scan_passed: true
          - adversarial_input_sweep_min_5_per_tool: true
          - api_surface_lock_confirmed: true
          - behavioral_hash_drift_explained: true
          - env_snapshot_recorded: true
    default_selection:
      - always: 65537
      - (MCP servers are always production-security concerns)
    fail_closed:
      - if_target_not_declared: "status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE"
      - if_target_declared_but_not_met: "status=BLOCKED stop_reason=VERIFICATION_RUNG_FAILED"

  # ------------------------------------------------------------
  # 8) Socratic Check (Pre-Emission Reflexion)
  # ------------------------------------------------------------
  Socratic_Check:
    before_emit_mcp_server:
      questions:
        - "Does every tool have a security declaration (auth_required, data_classification, network_access, destructive_ops)?"
        - "Is every secret-classified tool protected by auth_required=true?"
        - "Is every destructive_ops=true tool protected by rollback_plan or user_confirmation_required=true?"
        - "Is every network_access=true tool limited to an explicit allowlist of domains?"
        - "Are all inputs validated before reaching subprocess, eval, filesystem, or network?"
        - "Are null and zero distinguished in all handler paths?"
        - "Is the security manifest written and complete?"
        - "Is the API surface snapshotted before and after for semver tracking?"
        - "Does the rung_target (65537) meet all its requirements?"
        - "Have I run the security scanner or blocked with SECURITY_BLOCKED?"
      on_failure: [revise_implementation, fix_security_declaration, rerun_tests]

  # ------------------------------------------------------------
  # 9) Output Contract
  # ------------------------------------------------------------
  Output_Contract:
    required_outputs:
      - MCP_SERVER_CODE: "complete, runnable server implementation"
      - TOOL_SCHEMAS: "JSON Schema objects for all tools, valid against MCP spec"
      - SECURITY_MANIFEST: "${EVIDENCE_ROOT}/security_manifest.json"
      - TEST_SUITE: "test files covering all required test categories"
      - EVIDENCE_BUNDLE: "all files listed in Evidence section"

    hard_gates:
      - if_any_tool_missing_security_declaration: "BLOCKED"
      - if_secret_in_any_schema_or_log: "BLOCKED"
      - if_unvalidated_input_to_subprocess_or_eval: "BLOCKED"
      - if_security_scan_not_run_or_failed: "BLOCKED"
      - if_rung_target_not_met: "BLOCKED stop_reason=VERIFICATION_RUNG_FAILED"
      - if_api_surface_not_snapshotted_on_change: "BLOCKED stop_reason=EVIDENCE_INCOMPLETE"

    structured_refusal_format:
      required_keys:
        - status: "[NEED_INFO|BLOCKED]"
        - stop_reason
        - last_known_state
        - missing_fields_or_contradictions
        - what_was_attempted
        - next_actions
        - evidence_pointers

    required_on_success:
      status: PASS
      include:
        - server_code_path
        - tool_schemas_path
        - security_manifest_path
        - test_suite_path
        - evidence_pointers_with_exit_codes
        - residual_risk_notes
        - null_handling_summary
        - verification_rung_target
        - verification_rung_achieved

  # ------------------------------------------------------------
  # 10) Loop Control (Bounded Budget)
  # ------------------------------------------------------------
  Loop_Control:
    budgets:
      max_iterations: 6
      max_patch_reverts: 2
      max_tool_calls: 80
      max_seconds_soft: 1800
    termination:
      stop_reasons:
        - PASS
        - NEED_INFO
        - BLOCKED
        - SECURITY_BLOCKED
        - VERIFICATION_RUNG_FAILED
        - EVIDENCE_INCOMPLETE
        - NULL_INPUT
        - INVARIANT_VIOLATION
        - MAX_TOOL_CALLS
        - MAX_ITERS
      required_on_exit:
        - stop_reason
        - last_known_state
        - rung_target
        - rung_achieved
        - security_gate_status
        - tools_security_declared
    revert_policy:
      - if_implementation_introduces_security_regression: revert_immediately
      - if_null_zero_coercion_detected: revert_immediately
      - if_two_iterations_no_improvement: revert_to_last_best_known

  # ------------------------------------------------------------
  # 11) Evidence Schema
  # ------------------------------------------------------------
  Evidence:
    paths:
      root: "${EVIDENCE_ROOT}"
    required_files:
      - "${EVIDENCE_ROOT}/plan.json"
      - "${EVIDENCE_ROOT}/run_log.txt"
      - "${EVIDENCE_ROOT}/tests.json"
      - "${EVIDENCE_ROOT}/security_manifest.json"
      - "${EVIDENCE_ROOT}/security_scan.json"
      - "${EVIDENCE_ROOT}/null_checks.json"
      - "${EVIDENCE_ROOT}/behavior_hash.txt"
      - "${EVIDENCE_ROOT}/env_snapshot.json"
      - "${EVIDENCE_ROOT}/evidence_manifest.json"
    conditional_files:
      api_surface_changed:
        - "${EVIDENCE_ROOT}/api_surface_before.json"
        - "${EVIDENCE_ROOT}/api_surface_after.json"
      profile_fast:
        - "${EVIDENCE_ROOT}/budget_reduction.log"
    normalization:
      - strip_timestamps
      - normalize_paths_repo_relative
      - stable_sort_lists
      - canonical_json_sort_keys
      - use_exact_checksums_not_float
    minimal_json_schemas:
      security_manifest.json:
        required_keys:
          - schema_version
          - tools: "list of tool security declaration objects"
          - overall_risk_level: "[LOW|MED|HIGH]"
          - scanner_used
          - scan_clean: bool
      null_checks.json:
        required_keys:
          - tools_checked
          - null_cases_handled_per_tool
          - zero_cases_distinguished_per_tool
          - coercion_violations_detected
      env_snapshot.json:
        required_keys:
          - git_commit
          - git_dirty
          - repo_root
          - os
          - arch
          - language_runtimes
          - tool_versions
          - timezone
          - locale
    evidence_manifest:
      schema_version: "1.0.0"
      must_include:
        - file_path
        - sha256
        - role: "[plan|log|test|security|api_surface|snapshot]"
      fail_closed_if_missing_or_unparseable: true

  # ------------------------------------------------------------
  # 12) Source Grounding Discipline (Hard)
  # ------------------------------------------------------------
  Source_Grounding:
    allowed_grounding:
      - executable_command_output
      - repo_path_plus_line_witness
      - security_scanner_output_with_version
      - MCP_spec_section_reference
    forbidden:
      - unsupported_claims_about_tool_safety
      - narrative_confidence_as_security_evidence
      - claims_without_manifest_entry_or_test_witness
      - asserting_a_tool_is_safe_without_scan_result

  # ------------------------------------------------------------
  # 13) Anti-Optimization Clause (Never-Worse)
  # ------------------------------------------------------------
  Anti_Optimization_Clause:
    never_worse_doctrine:
      rule: "Hard gates and forbidden states are strictly additive over time."
      enforcement:
        - never_remove_forbidden_states
        - never_allow_tool_without_security_declaration
        - never_relax_input_validation_requirements
        - never_suppress_security_scanner_findings
        - any_relaxation_requires_major_version_and_deprecation_plan: true

  # ------------------------------------------------------------
  # 14) Integration Principles (Cross-Skill Fusion)
  # ------------------------------------------------------------
  Integration_Principles:
    with_prime_safety:
      integration:
        - "prime-safety defines the capability envelope; prime-mcp operates inside it."
        - "MCP tool schemas are treated as a capability expansion surface; prime-safety guards."
        - "Conflict rule: prime-safety always wins."
      result: "MCP servers cannot silently expand capability beyond the prime-safety envelope."
    with_prime_coder:
      integration:
        - "Handler implementations follow all prime-coder rules: null/zero, exact arithmetic, API lock."
        - "Red/green gate applies to handler test suites."
        - "Evidence contract from prime-coder applies to MCP evidence bundle."
      result: "Handler code quality matches prime-coder standards."
    with_prime_reviewer:
      integration:
        - "Generated MCP server code should be reviewed using prime-reviewer before shipping."
        - "API surface snapshots from prime-mcp feed directly into prime-reviewer's API surface check."
        - "Security manifest from prime-mcp is a first-class artifact for prime-reviewer's security scan gate."
      result: "Review and generation share the same evidence artifacts."
    with_phuc_forecast:
      integration:
        - "Phuc Forecast DREAM→FORECAST→DECIDE→ACT→VERIFY spine applies to MCP server design."
        - "FORECAST step must enumerate: what tools can be abused, how, and mitigations."
        - "Forecast is Lane C guidance only; security_manifest is Lane A evidence."
      result: "Security risks predicted before implementation, not discovered in production."
    conflict_rule:
      ordering: "prime-safety > prime-mcp > prime-coder > phuc-* skills"
      resolution: "stricter wins on any gate conflict"
