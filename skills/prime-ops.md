<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: prime-ops v1.0.0
PURPOSE: Fail-closed production operations agent. Runbooks, incident response, on-call discipline, canary deploy strategy, and rollback verification.
CORE CONTRACT: Every ops PASS requires: rollback procedure tested before deploy, every alert linked to a runbook, every deploy uses canary or equivalent staged rollout, and every incident has a written timeline and action items within 48 hours.
HARD GATES: Rollback gate blocks deploy without tested rollback procedure. Runbook gate blocks alert rule creation without linked runbook. Canary gate blocks production deploy without staged rollout plan. PIR gate blocks incident close without post-incident review artifact.
FSM STATES: INIT → INTAKE → NULL_CHECK → CLASSIFY_OPS_TASK → ROLLBACK_GATE → RUNBOOK_AUDIT → CANARY_PLAN → DEPLOY_EXECUTE → MONITOR_GATE → INCIDENT_GATE → EVIDENCE_BUILD → SOCRATIC_REVIEW → FINAL_SEAL → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: ROLLBACK_WITHOUT_TESTED_PROCEDURE | ALERT_WITHOUT_RUNBOOK | DEPLOY_WITHOUT_CANARY | INCIDENT_CLOSED_WITHOUT_PIR | HOTFIX_WITHOUT_REVIEW | MANUAL_PROD_CHANGE_WITHOUT_TICKET | SILENT_ROLLBACK
VERIFY: rung_641 (rollback tested + runbook linked + canary plan present) | rung_65537 (security: auth audit on prod access + blast radius documented + data loss risk assessed)
LANE TYPES: [A] rollback tested before deploy, alert has runbook, no silent rollback | [B] canary percentage ramp strategy, monitoring coverage | [C] on-call scheduling heuristics, tooling preferences
LOAD FULL: always for production; quick block is for orientation only
-->

PRIME_OPS_SKILL:
  version: 1.0.0
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL
  quote: "Hope is not a strategy. Runbooks are. — Site Reliability Engineering, Google"

  # ============================================================
  # PRIME OPS — Fail-Closed Production Operations Skill  [10/10]
  #
  # Goal: Operate production systems with:
  # - Rollback procedure tested before every production deploy
  # - Every alert rule linked to an actionable runbook
  # - Canary or staged rollout for every production change
  # - Post-incident review (PIR) required within 48 hours of any SEV1/SEV2
  # - No silent rollbacks — every rollback is logged and communicated
  # - No manual production changes without change ticket
  # ============================================================

  # ------------------------------------------------------------
  # A) Configuration
  # ------------------------------------------------------------
  Config:
    EVIDENCE_ROOT: "evidence"
    SEVERITY_LEVELS:
      SEV1: "Service down or major data loss; all hands"
      SEV2: "Significant degradation; on-call + lead"
      SEV3: "Minor degradation; on-call handles"
      SEV4: "No user impact; tracked async"
    PIR_REQUIRED_SEVS: [SEV1, SEV2]
    PIR_DEADLINE_HOURS: 48
    CANARY_MINIMUM_PERCENT: 5
    CANARY_BAKE_TIME_MINIMUM_MINUTES: 15
    ROLLBACK_TEST_REQUIRED_ENVIRONMENTS: [production, staging]
    ALERT_RUNBOOK_LINK_REQUIRED: true
    CHANGE_TICKET_REQUIRED_FOR_PROD: true

  # ------------------------------------------------------------
  # B) State Machine
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE
      - NULL_CHECK
      - CLASSIFY_OPS_TASK
      - ROLLBACK_GATE
      - RUNBOOK_AUDIT
      - CANARY_PLAN
      - DEPLOY_EXECUTE
      - MONITOR_GATE
      - INCIDENT_GATE
      - PIR_GATE
      - EVIDENCE_BUILD
      - SOCRATIC_REVIEW
      - FINAL_SEAL
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    TRANSITIONS:
      - INIT -> INTAKE: on TASK_REQUEST
      - INTAKE -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if service_or_change_type_missing
      - NULL_CHECK -> CLASSIFY_OPS_TASK: otherwise
      - CLASSIFY_OPS_TASK -> ROLLBACK_GATE: if deploy_task
      - CLASSIFY_OPS_TASK -> RUNBOOK_AUDIT: if alert_task
      - CLASSIFY_OPS_TASK -> INCIDENT_GATE: if incident_task
      - ROLLBACK_GATE -> EXIT_BLOCKED: if rollback_procedure_untested
      - ROLLBACK_GATE -> RUNBOOK_AUDIT: if rollback_tested
      - RUNBOOK_AUDIT -> EXIT_BLOCKED: if alert_without_runbook_link
      - RUNBOOK_AUDIT -> CANARY_PLAN: otherwise
      - CANARY_PLAN -> EXIT_BLOCKED: if no_staged_rollout_plan
      - CANARY_PLAN -> DEPLOY_EXECUTE: if canary_plan_present
      - DEPLOY_EXECUTE -> MONITOR_GATE: always
      - MONITOR_GATE -> EXIT_BLOCKED: if monitoring_coverage_insufficient
      - MONITOR_GATE -> EVIDENCE_BUILD: if monitoring_confirmed
      - INCIDENT_GATE -> PIR_GATE: if sev_requires_pir
      - PIR_GATE -> EXIT_BLOCKED: if incident_closed_without_pir
      - PIR_GATE -> EVIDENCE_BUILD: if pir_complete
      - EVIDENCE_BUILD -> SOCRATIC_REVIEW: always
      - SOCRATIC_REVIEW -> ROLLBACK_GATE: if critique_requires_revision and budgets_allow
      - SOCRATIC_REVIEW -> FINAL_SEAL: otherwise
      - FINAL_SEAL -> EXIT_PASS: if evidence_complete
      - FINAL_SEAL -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - ROLLBACK_WITHOUT_TESTED_PROCEDURE
      - ALERT_WITHOUT_RUNBOOK
      - DEPLOY_WITHOUT_CANARY_OR_STAGED_ROLLOUT
      - INCIDENT_CLOSED_WITHOUT_PIR_FOR_SEV1_SEV2
      - HOTFIX_WITHOUT_CHANGE_TICKET
      - MANUAL_PROD_CHANGE_WITHOUT_TICKET
      - SILENT_ROLLBACK_WITHOUT_COMMUNICATION
      - ROLLBACK_THAT_CAUSES_DATA_LOSS_WITHOUT_BACKUP_VERIFIED
      - ALERT_THAT_FIRES_WITHOUT_SEVERITY_CLASSIFICATION
      - ON_CALL_WITHOUT_DEFINED_ESCALATION_PATH

  # ------------------------------------------------------------
  # C) Hard Gates (Domain-Specific)
  # ------------------------------------------------------------
  Hard_Gates:

    Rollback_Gate:
      trigger: production deploy without tested rollback procedure
      action: EXIT_BLOCKED
      required:
        - rollback_steps documented in runbook
        - rollback tested in staging within last 30 days
        - rollback RTO (recovery time objective) documented
        - data migration rollback plan if schema changes included
      evidence_file: "${EVIDENCE_ROOT}/rollback_test.txt"
      lane: A

    Runbook_Gate:
      trigger: alert rule created or modified without runbook link in alert annotation
      action: EXIT_BLOCKED
      required_runbook_sections:
        - alert_description: what the alert means
        - impact: what users experience
        - investigation_steps: numbered, active voice
        - escalation_path: who to page if stuck
        - rollback_or_mitigation: how to stop the bleeding
      lane: A

    Canary_Gate:
      trigger: production deploy targeting > CANARY_MINIMUM_PERCENT of traffic without staged rollout
      action: EXIT_BLOCKED
      required:
        - initial canary percentage: >= CANARY_MINIMUM_PERCENT
        - bake time: >= CANARY_BAKE_TIME_MINIMUM_MINUTES
        - success criteria: defined (error rate, latency, etc.)
        - automatic rollback trigger: defined
      evidence_file: "${EVIDENCE_ROOT}/canary_plan.txt"
      lane: A

    PIR_Gate:
      trigger: SEV1 or SEV2 incident closed without post-incident review document
      action: EXIT_BLOCKED
      required_pir_sections:
        - timeline: chronological sequence of events
        - contributing_factors: root causes (not people)
        - impact: user-facing duration and scope
        - action_items: specific, assigned, with due dates
        - what_went_well: (optional but encouraged)
      deadline_hours: PIR_DEADLINE_HOURS
      lane: A

    Change_Ticket_Gate:
      trigger: any production change without associated change ticket
      action: EXIT_BLOCKED
      exception: "emergency hotfix allowed with ticket created post-facto within 2 hours"
      lane: A

    Monitoring_Coverage_Gate:
      trigger: service deployed without monitoring on at minimum [latency, error_rate, saturation]
      action: EXIT_BLOCKED
      required_golden_signals:
        - latency: p95 and p99 per endpoint
        - error_rate: HTTP 5xx rate per endpoint
        - saturation: CPU and memory utilization
        - traffic: requests per second
      lane: B

  # ------------------------------------------------------------
  # D) Runbook Template
  # ------------------------------------------------------------
  Runbook_Template:
    required_sections:
      title: "Alert: <alert_name>"
      severity: "SEV1 | SEV2 | SEV3 | SEV4"
      alert_description: "What does this alert fire for?"
      impact: "What are users experiencing?"
      investigation_steps:
        format: "numbered list, active imperative voice"
        example:
          - "1. Check the service error rate in Grafana: <link>"
          - "2. Run: kubectl logs -n <namespace> <pod> --tail=100"
          - "3. Look for errors matching pattern X in the logs."
      escalation_path:
        - primary_on_call: "PagerDuty policy: <link>"
        - secondary: "Team lead: <name or role>"
        - third: "Incident commander: <name or role>"
      rollback_or_mitigation:
        steps: "numbered, tested procedure"
        rto: "estimated time to mitigate"
      runbook_owner: "team name"
      last_tested_date: "YYYY-MM-DD"

  # ------------------------------------------------------------
  # E) Incident Response Protocol
  # ------------------------------------------------------------
  Incident_Response:
    roles:
      incident_commander: "coordinates response; owns communication"
      technical_lead: "drives investigation and fix"
      communications_lead: "updates status page; notifies stakeholders"
    communication_cadence:
      SEV1: "update every 15 minutes"
      SEV2: "update every 30 minutes"
    status_page_required: true
    blameless_principle:
      - focus_on_systems_and_processes_not_individuals: true
      - no_naming_individuals_in_PIR_for_blame: true
    timeline_format:
      - "HH:MM UTC: <observed fact or action taken>"
      - example: "14:23 UTC: Alert fired. On-call paged."
      - example: "14:31 UTC: Identified spike in DB connection pool exhaustion."
      - example: "14:45 UTC: Rolled back deploy. Error rate returned to baseline."

  # ------------------------------------------------------------
  # F) Canary Deploy Protocol
  # ------------------------------------------------------------
  Canary_Deploy:
    stages:
      - name: canary
        traffic_percent: 5
        bake_time_minutes: 15
        success_criteria:
          - error_rate_delta: "< 0.1%"
          - p95_latency_delta: "< 10%"
      - name: partial
        traffic_percent: 25
        bake_time_minutes: 15
        success_criteria: same_as_canary
      - name: full
        traffic_percent: 100
        bake_time_minutes: 30
        success_criteria: same_as_canary
    automatic_rollback_trigger:
      - error_rate_delta: "> 1%"
      - p95_latency_delta: "> 25%"
    manual_override_requires:
      - incident_commander_approval
      - documented_justification

  # ------------------------------------------------------------
  # G) Lane-Typed Claims
  # ------------------------------------------------------------
  Lane_Claims:
    Lane_A:
      - rollback_procedure_tested_before_production_deploy
      - every_alert_has_runbook_link
      - no_silent_rollback_all_rollbacks_communicated
      - pir_required_for_sev1_and_sev2_within_48_hours
      - no_production_change_without_change_ticket
    Lane_B:
      - canary_or_staged_rollout_for_every_production_deploy
      - golden_signals_monitored_for_every_service
      - on_call_rotation_has_documented_escalation_path
    Lane_C:
      - on_call_scheduling_preferences
      - observability_tooling_recommendations
      - runbook_documentation_style_hints

  # ------------------------------------------------------------
  # H) Verification Rung Target
  # ------------------------------------------------------------
  Verification_Rung:
    default_target: 65537
    rationale: "Production operations touch live user data and uptime. Security and blast radius must be verified."
    rung_641_requires:
      - rollback_procedure_tested
      - runbook_linked_to_alert
      - canary_plan_documented
      - change_ticket_present
    rung_65537_requires:
      - rung_641
      - prod_access_auth_audit
      - blast_radius_analysis
      - data_loss_risk_assessment
      - pir_complete_for_any_incidents_in_scope

  # ------------------------------------------------------------
  # I) Socratic Review Questions (Ops-Specific)
  # ------------------------------------------------------------
  Socratic_Review:
    questions:
      - "Has the rollback procedure been tested in staging recently?"
      - "Does every new alert rule link to a runbook?"
      - "Is there a canary plan with defined success criteria and automatic rollback triggers?"
      - "What is the blast radius of this change if it goes wrong?"
      - "Is there a change ticket linked to this production change?"
      - "For any incident involved: is the PIR complete with timeline and action items?"
      - "Are the four golden signals (latency, errors, saturation, traffic) all monitored?"
    on_failure: revise_ops_plan and recheck

  # ------------------------------------------------------------
  # J) Evidence Schema
  # ------------------------------------------------------------
  Evidence:
    required_files:
      - "${EVIDENCE_ROOT}/change_ticket.txt"
      - "${EVIDENCE_ROOT}/rollback_test.txt"
      - "${EVIDENCE_ROOT}/runbook_audit.txt"
    conditional_files:
      deploy_task:
        - "${EVIDENCE_ROOT}/canary_plan.txt"
        - "${EVIDENCE_ROOT}/monitoring_coverage.txt"
      incident_task:
        - "${EVIDENCE_ROOT}/incident_timeline.txt"
        - "${EVIDENCE_ROOT}/pir.md"
      security_gate_triggered:
        - "${EVIDENCE_ROOT}/prod_access_audit.txt"
        - "${EVIDENCE_ROOT}/blast_radius.txt"
