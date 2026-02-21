<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: prime-data v1.0.0
PURPOSE: Fail-closed data pipeline design agent (ETL/ELT). Enforces null handling, schema validation, idempotency, exact arithmetic for financial aggregations, and schema versioning.
CORE CONTRACT: Every pipeline PASS requires: idempotency key on every write, schema version tracked, null semantics documented per field, no float in financial aggregations, and schema validation at every ingestion boundary.
HARD GATES: Float gate blocks float types in any financial aggregation path. Idempotency gate blocks pipelines without idempotency key or upsert semantics. Schema version gate blocks pipelines without declared schema version. Null gate blocks pipelines that silently drop or coerce nulls in financial data.
FSM STATES: INIT → INTAKE → NULL_CHECK → CLASSIFY_PIPELINE → SCHEMA_LOAD → NULL_ANALYSIS → IDEMPOTENCY_AUDIT → FINANCIAL_GATE → SCHEMA_VERSION_GATE → PIPELINE_DRAFT → TEST_PIPELINE → EVIDENCE_BUILD → SOCRATIC_REVIEW → FINAL_SEAL → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: FLOAT_IN_FINANCIAL_AGGREGATION | NO_IDEMPOTENCY_KEY | NO_SCHEMA_VERSION | SILENT_NULL_DROP | SCHEMA_DRIFT_WITHOUT_MIGRATION | UNVALIDATED_INGESTION | DUPLICATE_RECORD_WITHOUT_DEDUP_STRATEGY
VERIFY: rung_641 (schema valid + idempotency test + null coverage + financial types clean) | rung_274177 (replay idempotency: run pipeline twice, assert identical output)
LANE TYPES: [A] no float in finance, idempotency key required, schema version required | [B] schema registry, partitioning strategy, watermark policy | [C] performance hints, partition sizing, backfill heuristics
LOAD FULL: always for production; quick block is for orientation only
-->

PRIME_DATA_SKILL:
  version: 1.0.0
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL
  quote: "Data pipelines are contracts with the future. Break them silently and the future breaks loudly. — Data engineering wisdom"

  # ============================================================
  # PRIME DATA — Fail-Closed Data Pipeline Design Skill  [10/10]
  #
  # Goal: Design and review ETL/ELT pipelines with:
  # - Null semantics documented per field (missing vs unknown vs inapplicable)
  # - Schema validation at every ingestion boundary
  # - Idempotency key on every write (run-twice = same result)
  # - Exact arithmetic (NUMERIC/DECIMAL) for all financial paths
  # - Schema versioning with explicit migration strategy
  # - Deduplication strategy declared for all append-mode pipelines
  # ============================================================

  # ------------------------------------------------------------
  # A) Configuration
  # ------------------------------------------------------------
  Config:
    EVIDENCE_ROOT: "evidence"
    FINANCIAL_TYPES_FORBIDDEN: [float, double, float32, float64, Float]
    FINANCIAL_TYPES_REQUIRED: [Decimal, NUMERIC, DECIMAL, integer_cents]
    IDEMPOTENCY_STRATEGIES:
      - upsert_on_primary_key
      - insert_overwrite_partition
      - dedup_on_event_id_before_write
      - truncate_and_reload_with_transaction
    SCHEMA_REGISTRY_TOOLS: [confluent_schema_registry, glue_schema_registry, buf]
    NULL_SEMANTIC_VALUES:
      - missing: "data was not collected"
      - unknown: "data exists but was not determinable"
      - inapplicable: "concept does not apply to this record"
      - error: "data collection failed"

  # ------------------------------------------------------------
  # B) State Machine
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE
      - NULL_CHECK
      - CLASSIFY_PIPELINE
      - SCHEMA_LOAD
      - NULL_ANALYSIS
      - IDEMPOTENCY_AUDIT
      - FINANCIAL_GATE
      - SCHEMA_VERSION_GATE
      - PIPELINE_DRAFT
      - TEST_PIPELINE
      - EVIDENCE_BUILD
      - SOCRATIC_REVIEW
      - FINAL_SEAL
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    TRANSITIONS:
      - INIT -> INTAKE: on TASK_REQUEST
      - INTAKE -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if source_schema_or_pipeline_type_missing
      - NULL_CHECK -> CLASSIFY_PIPELINE: otherwise
      - CLASSIFY_PIPELINE -> SCHEMA_LOAD: always
      - SCHEMA_LOAD -> NULL_ANALYSIS: always
      - NULL_ANALYSIS -> IDEMPOTENCY_AUDIT: always
      - IDEMPOTENCY_AUDIT -> EXIT_BLOCKED: if no_idempotency_strategy_defined
      - IDEMPOTENCY_AUDIT -> FINANCIAL_GATE: always
      - FINANCIAL_GATE -> EXIT_BLOCKED: if float_in_financial_aggregation
      - FINANCIAL_GATE -> SCHEMA_VERSION_GATE: otherwise
      - SCHEMA_VERSION_GATE -> EXIT_BLOCKED: if schema_version_undeclared
      - SCHEMA_VERSION_GATE -> PIPELINE_DRAFT: otherwise
      - PIPELINE_DRAFT -> TEST_PIPELINE: always
      - TEST_PIPELINE -> EVIDENCE_BUILD: if tests_pass
      - TEST_PIPELINE -> EXIT_BLOCKED: if tests_fail
      - EVIDENCE_BUILD -> SOCRATIC_REVIEW: always
      - SOCRATIC_REVIEW -> PIPELINE_DRAFT: if critique_requires_revision and budgets_allow
      - SOCRATIC_REVIEW -> FINAL_SEAL: otherwise
      - FINAL_SEAL -> EXIT_PASS: if evidence_complete
      - FINAL_SEAL -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - FLOAT_IN_FINANCIAL_AGGREGATION
      - NO_IDEMPOTENCY_KEY
      - NO_SCHEMA_VERSION
      - SILENT_NULL_DROP
      - SILENT_NULL_COERCION_TO_ZERO
      - SCHEMA_DRIFT_WITHOUT_MIGRATION
      - UNVALIDATED_INGESTION_BOUNDARY
      - DUPLICATE_RECORD_WITHOUT_DEDUP_STRATEGY
      - UNBOUNDED_PIPELINE_WITHOUT_WATERMARK
      - BACKFILL_WITHOUT_IDEMPOTENCY_PROOF

  # ------------------------------------------------------------
  # C) Hard Gates (Domain-Specific)
  # ------------------------------------------------------------
  Hard_Gates:

    Float_Financial_Gate:
      trigger: float/double type used in SUM, AVG, or any financial aggregation
      action: EXIT_BLOCKED
      required_replacement:
        python: decimal.Decimal
        sql: NUMERIC(19,4)
        java_scala: java.math.BigDecimal
        spark: DecimalType(precision, scale)
      rationale: "IEEE 754 float addition is not associative. Financial totals drift."
      lane: A

    Idempotency_Gate:
      trigger: pipeline writes without declared idempotency strategy
      action: EXIT_BLOCKED
      required: one of IDEMPOTENCY_STRATEGIES must be declared and tested
      test: "run pipeline twice on same input; assert output is identical"
      evidence_file: "${EVIDENCE_ROOT}/idempotency_test.txt"
      lane: A

    Schema_Version_Gate:
      trigger: pipeline schema has no version field or migration path
      action: EXIT_BLOCKED
      required:
        - schema_version: semver or integer monotonic
        - migration_strategy: documented (forward-compatible, backward-compatible, or breaking)
      lane: A

    Null_Safety_Gate:
      trigger:
        - null records silently dropped without logging
        - null coerced to 0 in financial field without business-rule citation
        - null_count not tracked in pipeline metrics
      action: EXIT_BLOCKED
      required: explicit null handling per field with semantic documented
      lane: A

    Schema_Validation_Gate:
      trigger: ingestion reads from external source without schema validation step
      action: EXIT_BLOCKED
      required: validation against declared schema before any transformation
      tools: [great_expectations, pydantic, avro_schema, json_schema]
      lane: A

    Dedup_Strategy_Gate:
      trigger: append-mode pipeline without declared deduplication strategy
      action: EXIT_BLOCKED
      required: dedup_on field declared (event_id, idempotency_key, or composite key)
      lane: B

  # ------------------------------------------------------------
  # D) Null Analysis Protocol
  # ------------------------------------------------------------
  Null_Analysis:
    per_field_required:
      - is_nullable: bool
      - null_semantic: "missing | unknown | inapplicable | error"
      - null_handling: "drop | substitute | propagate | error_out"
      - null_count_metric: tracked in pipeline output stats
    financial_field_special_rule:
      - null_in_financial_field_must_not_be_silently_dropped: true
      - null_in_financial_field_must_not_be_coerced_to_zero: true
      - required: business rule citation for any null handling on financial data

  # ------------------------------------------------------------
  # E) Schema Evolution Protocol
  # ------------------------------------------------------------
  Schema_Evolution:
    compatibility_modes:
      - BACKWARD: new schema can read data written by old schema
      - FORWARD: old schema can read data written by new schema
      - FULL: both backward and forward compatible
    breaking_changes_require:
      - major version bump
      - migration script tested
      - downstream consumer notification
    non_breaking_additions:
      - adding optional field with default
      - adding new enum value (FORWARD compatible only)
    forbidden_without_major_bump:
      - removing field
      - renaming field without alias
      - changing field type incompatibly
      - making optional field required

  # ------------------------------------------------------------
  # F) Idempotency Testing Protocol
  # ------------------------------------------------------------
  Idempotency_Testing:
    test_procedure:
      1: "Run pipeline with input batch A; record output checksum"
      2: "Run pipeline again with identical input batch A; record output checksum"
      3: "Assert: checksum(run_1) == checksum(run_2)"
    edge_cases:
      - partial_failure_then_retry: "assert no duplicates after retry"
      - concurrent_runs: "assert locking or atomic upsert prevents double-write"
    evidence_file: "${EVIDENCE_ROOT}/idempotency_test.txt"

  # ------------------------------------------------------------
  # G) Lane-Typed Claims
  # ------------------------------------------------------------
  Lane_Claims:
    Lane_A:
      - no_float_in_any_financial_aggregation
      - idempotency_strategy_declared_and_tested
      - schema_version_tracked_with_migration_path
      - null_semantics_documented_per_field
      - schema_validation_at_every_ingestion_boundary
    Lane_B:
      - dedup_strategy_declared_for_append_pipelines
      - watermark_policy_declared_for_streaming
      - partition_strategy_documented
    Lane_C:
      - partition_sizing_hints
      - backfill_scheduling_heuristics
      - schema_registry_tooling_recommendations

  # ------------------------------------------------------------
  # H) Verification Rung Target
  # ------------------------------------------------------------
  Verification_Rung:
    default_target: 274177
    rationale: "Data pipelines require replay stability — run-twice idempotency is a hard requirement."
    rung_641_requires:
      - schema_validation_passes
      - financial_type_check_clean
      - idempotency_strategy_declared
      - null_analysis_documented
    rung_274177_requires:
      - rung_641
      - idempotency_test_run_twice_identical_output
      - null_edge_case_sweep
      - schema_evolution_backward_compatible_verified

  # ------------------------------------------------------------
  # I) Socratic Review Questions (Data-Specific)
  # ------------------------------------------------------------
  Socratic_Review:
    questions:
      - "Are any financial aggregations using float or double types?"
      - "Is the idempotency strategy tested — does running twice produce identical output?"
      - "What does NULL mean for each nullable field? Is it documented?"
      - "Is the schema version declared and is there a migration path?"
      - "Is schema validation performed before any transformation on ingested data?"
      - "For append-mode pipelines, what is the deduplication strategy?"
      - "Are null counts tracked in pipeline output metrics?"
    on_failure: revise_pipeline and recheck

  # ------------------------------------------------------------
  # J) Evidence Schema
  # ------------------------------------------------------------
  Evidence:
    required_files:
      - "${EVIDENCE_ROOT}/schema_definition.json"
      - "${EVIDENCE_ROOT}/null_analysis.txt"
      - "${EVIDENCE_ROOT}/idempotency_test.txt"
      - "${EVIDENCE_ROOT}/financial_type_check.txt"
    conditional_files:
      schema_evolution_involved:
        - "${EVIDENCE_ROOT}/migration_plan.txt"
        - "${EVIDENCE_ROOT}/compatibility_test.txt"
      streaming_pipeline:
        - "${EVIDENCE_ROOT}/watermark_policy.txt"
