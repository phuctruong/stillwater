<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: prime-sql v1.0.0
PURPOSE: Fail-closed SQL query design agent with null-safety, index analysis, explain plan interpretation, and financial arithmetic discipline.
CORE CONTRACT: Every query PASS requires explain plan evidence, null-coverage proof, and no float in financial paths. Cartesian joins require explicit documented intent. SELECT * is never acceptable in production.
HARD GATES: Index gate blocks queries lacking index coverage on large tables. Null gate blocks queries that coerce NULL to zero or empty. Financial gate blocks float arithmetic in any aggregation path. Explain gate requires EXPLAIN ANALYZE output for any query touching >1000 estimated rows.
FSM STATES: INIT → INTAKE → NULL_CHECK → CLASSIFY_QUERY → SCHEMA_LOAD → NULL_ANALYSIS → INDEX_ANALYSIS → QUERY_DRAFT → EXPLAIN_GATE → FINANCIAL_GATE → TEST_QUERY → EVIDENCE_BUILD → SOCRATIC_REVIEW → FINAL_SEAL → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: CARTESIAN_JOIN_WITHOUT_INTENT | SELECT_STAR_IN_PRODUCTION | FLOAT_IN_FINANCIAL_PATH | NULL_COERCED_TO_ZERO | INDEX_IGNORED_ON_LARGE_TABLE | UNWITNESSED_EXPLAIN_PLAN | IMPLICIT_TYPE_COERCION
VERIFY: rung_641 (explain plan + null coverage + no regressions) | rung_274177 (stability: seed data sweep + replay + edge cases) | rung_65537 (promotion: adversarial input + injection check + performance regression)
LANE TYPES: [A] null-safety, no float in finance, no cartesian join | [B] index preference, query style | [C] heuristics, optimization hints
LOAD FULL: always for production; quick block is for orientation only
-->

PRIME_SQL_SKILL:
  version: 1.0.0
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL
  quote: "A query that returns wrong nulls is not a query — it is a trap. — adapted from C.J. Date"

  # ============================================================
  # PRIME SQL — Fail-Closed SQL Design Skill  [10/10]
  #
  # Goal: Author, review, and optimize SQL queries with:
  # - Explicit null handling (never coerce NULL to 0 or '')
  # - Index coverage analysis before execution on large tables
  # - EXPLAIN plan verification for non-trivial queries
  # - Exact arithmetic (NUMERIC/DECIMAL) for all financial paths
  # - No cartesian joins unless explicitly documented as intent
  # - No SELECT * in production queries
  # ============================================================

  # ------------------------------------------------------------
  # A) Configuration
  # ------------------------------------------------------------
  Config:
    EVIDENCE_ROOT: "evidence"
    LARGE_TABLE_THRESHOLD_ROWS: 1000
    FINANCIAL_TYPES_FORBIDDEN: [float, double, real, float4, float8]
    FINANCIAL_TYPES_REQUIRED: [numeric, decimal]
    NULL_COERCION_PATTERNS_FORBIDDEN:
      - "COALESCE(x, 0) in financial aggregation"
      - "ISNULL(x, 0) applied to currency columns"
      - "NVL(x, 0) applied to quantity columns"

  # ------------------------------------------------------------
  # B) State Machine
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE
      - NULL_CHECK
      - CLASSIFY_QUERY
      - SCHEMA_LOAD
      - NULL_ANALYSIS
      - INDEX_ANALYSIS
      - QUERY_DRAFT
      - EXPLAIN_GATE
      - FINANCIAL_GATE
      - TEST_QUERY
      - EVIDENCE_BUILD
      - SOCRATIC_REVIEW
      - FINAL_SEAL
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    TRANSITIONS:
      - INIT -> INTAKE: on TASK_REQUEST
      - INTAKE -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if schema_or_task_missing
      - NULL_CHECK -> CLASSIFY_QUERY: otherwise
      - CLASSIFY_QUERY -> SCHEMA_LOAD: always
      - SCHEMA_LOAD -> NULL_ANALYSIS: always
      - NULL_ANALYSIS -> INDEX_ANALYSIS: always
      - INDEX_ANALYSIS -> QUERY_DRAFT: always
      - QUERY_DRAFT -> EXPLAIN_GATE: if estimated_rows > LARGE_TABLE_THRESHOLD_ROWS
      - QUERY_DRAFT -> FINANCIAL_GATE: if query_touches_financial_columns
      - QUERY_DRAFT -> TEST_QUERY: otherwise
      - EXPLAIN_GATE -> EXIT_BLOCKED: if explain_plan_missing_or_unacceptable
      - EXPLAIN_GATE -> FINANCIAL_GATE: if query_touches_financial_columns
      - EXPLAIN_GATE -> TEST_QUERY: otherwise
      - FINANCIAL_GATE -> EXIT_BLOCKED: if float_detected_in_financial_path
      - FINANCIAL_GATE -> TEST_QUERY: if exact_types_confirmed
      - TEST_QUERY -> EVIDENCE_BUILD: if tests_pass
      - TEST_QUERY -> EXIT_BLOCKED: if tests_fail_or_cartesian_detected
      - EVIDENCE_BUILD -> SOCRATIC_REVIEW: always
      - SOCRATIC_REVIEW -> QUERY_DRAFT: if critique_requires_revision and budgets_allow
      - SOCRATIC_REVIEW -> FINAL_SEAL: otherwise
      - FINAL_SEAL -> EXIT_PASS: if evidence_complete
      - FINAL_SEAL -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - CARTESIAN_JOIN_WITHOUT_INTENT
      - SELECT_STAR_IN_PRODUCTION
      - FLOAT_IN_FINANCIAL_PATH
      - NULL_COERCED_TO_ZERO
      - INDEX_IGNORED_ON_LARGE_TABLE
      - UNWITNESSED_EXPLAIN_PLAN
      - IMPLICIT_TYPE_COERCION
      - UNPARAMETERIZED_USER_INPUT
      - SILENT_NULL_DROP_IN_AGGREGATION
      - NONDETERMINISTIC_ORDER_WITHOUT_TIEBREAKER

  # ------------------------------------------------------------
  # C) Hard Gates (Domain-Specific)
  # ------------------------------------------------------------
  Hard_Gates:

    Cartesian_Join_Gate:
      trigger: any JOIN without explicit ON clause or CROSS JOIN without comment
      action: EXIT_BLOCKED
      exception:
        - requires_explicit_comment: "-- INTENT: cartesian product for <reason>"
        - evidence_file: "${EVIDENCE_ROOT}/cartesian_intent.txt"
      lane: A

    Select_Star_Gate:
      trigger: SELECT * in any query marked for production use
      action: EXIT_BLOCKED
      rationale: "Schema changes silently break downstream consumers."
      allowed_exceptions:
        - exploratory queries labeled [EXPLORE] not promoted to production
      lane: A

    Float_Financial_Gate:
      trigger: any float/double/real column in SUM, AVG, or comparison on financial data
      action: EXIT_BLOCKED
      required_replacement: NUMERIC or DECIMAL with explicit precision and scale
      lane: A

    Null_Safety_Gate:
      trigger:
        - COUNT(*) vs COUNT(column) conflation without documentation
        - AVG() on nullable column without IS NOT NULL filter documented
        - COALESCE(financial_col, 0) in aggregation without business-rule citation
      action: EXIT_BLOCKED
      rationale: "Silent null drops change business semantics without error."
      lane: A

    Index_Coverage_Gate:
      trigger: estimated_rows > LARGE_TABLE_THRESHOLD_ROWS AND no index on WHERE/JOIN columns
      action: EXIT_BLOCKED unless index_recommendation documented
      evidence_required: "${EVIDENCE_ROOT}/index_analysis.txt"
      lane: B

    Explain_Plan_Gate:
      trigger: estimated_rows > LARGE_TABLE_THRESHOLD_ROWS
      required: EXPLAIN ANALYZE output captured and interpreted
      forbidden_plan_nodes:
        - Seq Scan on table with >10000 rows unless justified
        - Nested Loop with large outer set unless justified
      evidence_required: "${EVIDENCE_ROOT}/explain_plan.txt"
      lane: B

    SQL_Injection_Gate:
      trigger: any user-controlled input concatenated into SQL string
      action: EXIT_BLOCKED
      required: parameterized queries or prepared statements only
      lane: A

  # ------------------------------------------------------------
  # D) Null Analysis Protocol
  # ------------------------------------------------------------
  Null_Analysis:
    per_column_required:
      - is_nullable: bool
      - null_semantic: "missing | inapplicable | unknown | error"
      - aggregation_behavior: "COUNT(*) vs COUNT(col) documented"
      - join_behavior: "inner vs outer join null semantics documented"
    forbidden_patterns:
      - treating_null_as_zero: true
      - treating_null_as_empty_string: true
      - equality_check_null_eq_null: "use IS NULL not = NULL"

  # ------------------------------------------------------------
  # E) Index Analysis Protocol
  # ------------------------------------------------------------
  Index_Analysis:
    steps:
      1: list_all_where_clause_columns
      2: list_all_join_columns
      3: list_all_order_by_columns_if_large_result
      4: check_existing_indexes_against_above
      5: compute_selectivity_estimate_if_stats_available
      6: recommend_composite_index_if_multi_column_filter
    output:
      - covered_columns: list
      - missing_index_columns: list
      - recommendation: text
    evidence_file: "${EVIDENCE_ROOT}/index_analysis.txt"

  # ------------------------------------------------------------
  # F) Financial Arithmetic Policy
  # ------------------------------------------------------------
  Financial_Arithmetic:
    allowed_types: [NUMERIC, DECIMAL]
    forbidden_types: [FLOAT, DOUBLE PRECISION, REAL]
    precision_rule:
      - monetary_values: "NUMERIC(19, 4) minimum"
      - rate_values: "NUMERIC(10, 6) minimum"
    rounding_rule:
      - always_explicit: true
      - use_ROUND_with_explicit_scale: true
      - never_rely_on_implicit_cast: true

  # ------------------------------------------------------------
  # G) Lane-Typed Claims
  # ------------------------------------------------------------
  Lane_Claims:
    Lane_A:
      - no_cartesian_join_without_documented_intent
      - no_select_star_in_production
      - no_float_in_financial_path
      - no_null_coercion_to_zero_in_financial_aggregation
      - no_unparameterized_user_input
    Lane_B:
      - index_coverage_on_large_tables_preferred
      - explain_plan_verified_for_large_queries
      - explicit_ORDER_BY_tiebreaker_for_determinism
    Lane_C:
      - query_style_preferences
      - CTE_vs_subquery_heuristics
      - denormalization_hints

  # ------------------------------------------------------------
  # H) Verification Rung Target
  # ------------------------------------------------------------
  Verification_Rung:
    default_target: 641
    security_queries_target: 65537
    rung_641_requires:
      - explain_plan_captured_if_large
      - null_analysis_documented
      - financial_type_check_passed
      - no_forbidden_states_triggered
      - test_query_executed_with_sample_data
    rung_65537_requires:
      - rung_641
      - sql_injection_adversarial_sweep
      - privilege_escalation_check
      - data_exposure_audit

  # ------------------------------------------------------------
  # I) Socratic Review Questions (SQL-Specific)
  # ------------------------------------------------------------
  Socratic_Review:
    questions:
      - "Does every JOIN have an explicit, correct ON clause?"
      - "Are all nullable columns in aggregations explicitly handled?"
      - "Is there a FLOAT type anywhere in a financial calculation?"
      - "Does the explain plan show any unexpected sequential scans?"
      - "Is user input parameterized or validated before injection into SQL?"
      - "Does COUNT(*) vs COUNT(column) reflect the intended business logic?"
      - "Are results deterministic — is there an explicit ORDER BY with tiebreaker?"
    on_failure: revise_query and recheck

  # ------------------------------------------------------------
  # J) Evidence Schema
  # ------------------------------------------------------------
  Evidence:
    required_files:
      - "${EVIDENCE_ROOT}/query.sql"
      - "${EVIDENCE_ROOT}/null_analysis.txt"
      - "${EVIDENCE_ROOT}/index_analysis.txt"
      - "${EVIDENCE_ROOT}/test_results.txt"
    conditional_files:
      large_table_query:
        - "${EVIDENCE_ROOT}/explain_plan.txt"
      financial_query:
        - "${EVIDENCE_ROOT}/financial_type_check.txt"
      cartesian_join_present:
        - "${EVIDENCE_ROOT}/cartesian_intent.txt"
      user_input_present:
        - "${EVIDENCE_ROOT}/parameterization_proof.txt"
