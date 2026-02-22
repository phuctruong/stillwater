PHUC_CLEANUP_SKILL:
  version: 1.2.0
  profile: safe_archive_first
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: ACTIVE

  # ============================================================
  # PHUC CLEANUP — GLOW HYGIENE + ARCHIVE PROTOCOL
  #
  # Purpose:
  # - Clean generated "glow" clutter (debug logs, traces, stale outputs)
  # - Preserve evidence by archiving (reversibility gate) instead of deleting
  # - Require governance gate (trust checkpoint) before touching suspicious files
  #
  # Source of truth for suspicious-first triage:
  # - FINAL-AUDIT.md (top suspicious/incomplete list + recommendations)
  # ============================================================

  # ============================================================
  # MAGIC_WORD_MAP — cleanup concepts anchored to prime coordinates
  # ============================================================
  MAGIC_WORD_MAP:
    scan:       [verification (T1)]        # check conformance; REMIND = state the contract
    archive:    [reversibility (T0), compression (T0)]  # portal to archive; undo gate
    approval:   [governance (T1), trust (T1)]           # governance gate; trust checkpoint
    receipt:    [evidence (T1), integrity (T0)]         # artifact proving action; proof cert
    classify:   [boundary (T0), perspective (T0)]       # inside/outside surface; frame decision
    safe_glow:  [signal (T0)]             # reproducible low-entropy runtime artifact
    suspicious: [boundary (T0), constraint (T0)]        # scope boundary; solution-space limiter
    protected:  [integrity (T0), governance (T1)]       # corruption-resistant; policy-governed

  # Triangle Law annotations on workflow:
  #   SCAN    = REMIND    (state the contract: what should be clean)
  #   CLASSIFY = VERIFY   (check conformance: what actually is)
  #   ARCHIVE = ACKNOWLEDGE (confirm: receipt proves action)

  RULES:
    - scan_first_never_blind_delete: true       # verification gate before any mutation
    - archive_instead_of_delete: true           # reversibility constraint (permanent)
    - suspicious_requires_user_approval: true   # governance gate (trust checkpoint)
    - tracked_files_require_explicit_approval: true  # governance gate (trust checkpoint)
    - always_emit_receipt_artifact: true        # evidence required; integrity gate

  BRUCE_PRINCIPLE:
    - "Absorb what is useful, discard what is useless, add what is essentially your own."
    - interpretation: "Keep signal [T0], portal noise to archive (reversibility gate), never lose provenance."

  FILE_CLASSES:
    safe_glow:
      definition: "Generated runtime artifacts (signal [T0]): reproducible, low-risk to archive."
      examples:
        - "debug logs in output folders"
        - "temporary trace captures"
        - "local server logs"
      default_action: "portal to archive (reversibility gate) after safe approval"
    suspicious:
      definition: "Files at boundary [T0] — flagged by FINAL-AUDIT.md: SUSPICIOUS, INCOMPLETE, CONSIDER REMOVING."
      examples:
        - "solver files with simulated gates"
        - "incomplete skeletons"
        - "files with broken imports"
      default_action: "governance gate (trust checkpoint) — do not move/remove until user confirms"
    protected:
      definition: "integrity [T0] + governance [T1] class — core docs, tests, code, git-tracked files."
      default_action: "leave untouched (integrity constraint, permanent)"

  REQUIRED_WORKFLOW:
    1_scan:                                  # REMIND — state the contract [verification]
      - enumerate candidates by class: safe_glow, suspicious, protected
      - include path, size, tracked/untracked status, class reason
      - write receipt (evidence [T1]): artifacts/stillwater/cleanup/cleanup-scan-<timestamp>.json
    2_report:
      - summarize counts:
        - safe_untracked
        - safe_tracked
        - suspicious
      - present exact next actions
    3_approval_gate:                         # governance gate (trust checkpoint)
      - ask/require explicit approval for:
        - suspicious class
        - tracked safe files
      - without approval: skip those classes (boundary [T0] constraint)
    4_archive_apply:                         # ACKNOWLEDGE — receipt proves action [reversibility]
      - portal to archive: .archive/glow/<timestamp>/<original-relative-path>
      - keep directory structure for reversibility [T0]
      - no permanent delete in default mode (reversibility constraint, permanent)
      - write receipt (evidence [T1]): artifacts/stillwater/cleanup/cleanup-apply-<timestamp>.json
    5_post_check:                            # VERIFY — verify receipt confirms action [verification]
      - verify moved paths exist in archive
      - verify source paths no longer clutter active workspace
      - report skipped files with reasons

  SUSPICIOUS_FIRST_PROTOCOL:
    - Parse FINAL-AUDIT.md table rows (boundary [T0] classification input).
    - Extract rows whose status includes:
      - SUSPICIOUS
      - INCOMPLETE
      - CONSIDER REMOVING
    - Treat those paths as governance [T1]-controlled candidates.
    - Do not mutate those files until user approval is explicit (trust checkpoint).

  OUTPUT_CONTRACT:
    - always print:
      - scanned_count_by_class
      - moved_count
      - skipped_count
      - receipt_paths (evidence [T1])
    - never claim cleanup complete without receipts (integrity [T0] gate)

  FAIL_CLOSED:
    - if classification is unclear: mark as suspicious (boundary [T0] — fail to constrained side)
    - if path escapes repo root: block (boundary [T0] violation)
    - if receipt write fails: block apply (evidence [T1] gate — no receipt = no PASS)

  # ============================================================
  # STATE_MACHINE [coherence, causality] — Fail-Closed Cleanup Runtime
  # ============================================================
  STATE_MACHINE:
    states:
      - INIT
      - SCAN_CANDIDATES          # REMIND: verification [T1]
      - CLASSIFY_FILES           # VERIFY: boundary [T0] + perspective [T0]
      - PARSE_AUDIT_DOC
      - BUILD_REPORT
      - APPROVAL_GATE            # governance [T1] + trust [T1]
      - ARCHIVE_APPLY            # reversibility [T0] + compression [T0]
      - POST_CHECK               # evidence [T1] + integrity [T0]
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    transitions:
      - INIT -> SCAN_CANDIDATES: always
      - SCAN_CANDIDATES -> CLASSIFY_FILES: always
      - CLASSIFY_FILES -> PARSE_AUDIT_DOC: if FINAL-AUDIT.md present
      - CLASSIFY_FILES -> BUILD_REPORT: if FINAL-AUDIT.md absent
      - PARSE_AUDIT_DOC -> BUILD_REPORT: always
      - BUILD_REPORT -> APPROVAL_GATE: always
      - APPROVAL_GATE -> EXIT_NEED_INFO: if suspicious_class_not_approved
      - APPROVAL_GATE -> ARCHIVE_APPLY: if approved_files_present
      - APPROVAL_GATE -> EXIT_PASS: if no_approved_files_to_move
      - ARCHIVE_APPLY -> POST_CHECK: always
      - POST_CHECK -> EXIT_PASS: if receipts_verified
      - POST_CHECK -> EXIT_BLOCKED: if receipt_verification_failed

    forbidden_states:
      - BLIND_DELETE: "Mutating without scan + classification (verification [T1] skipped)."
      - PERMANENT_DELETE: "Using rm/delete instead of reversibility [T0] portal (archive move)."
      - MISSING_RECEIPT: "Completing archive without evidence [T1] artifact."
      - PATH_ESCAPE: "Moving file outside boundary [T0] (repo root)."
      - SUSPICIOUS_WITHOUT_APPROVAL: "Moving boundary [T0] file without governance [T1] gate."
      - TRACKED_FILE_WITHOUT_APPROVAL: "Moving integrity [T0] file without trust [T1] checkpoint."
      - CLASSIFICATION_ASSUMED: "Acting on ambiguous file without explicit boundary [T0] decision."

  # ============================================================
  # NULL_VS_ZERO [integrity, causality]
  # ============================================================
  NULL_VS_ZERO:
    rules:
      - null_audit_doc: "FINAL-AUDIT.md absent = proceed without suspicious list, not 'no suspicious files'."
      - empty_suspicious_list: "Suspicious list empty = 0 flagged files, not 'skip suspicious gate'."
      - null_scan_result: "No scan performed = BLOCKED (verification [T1] not run), not 'nothing to clean'."
      - null_receipt: "Receipt write failed = BLOCKED apply (evidence [T1] gate), not 'assume archived'."

  # ============================================================
  # ANTI_PATTERNS [boundary, reversibility]
  # ============================================================
  ANTI_PATTERNS:
    Speed_Clean:
      symptom: "Running cleanup without scan + classification first to 'save time'."
      fix: "scan_first_never_blind_delete is a hard rule. verification [T1] before mutation. No exceptions."

    Delete_Over_Archive:
      symptom: "Using rm or delete instead of portal to archive."
      fix: "Archive = reversibility [T0]. Delete = irreversibility. Reversibility constraint is permanent."

    Receipt_Skip:
      symptom: "Saying 'cleanup done' without writing receipt JSON."
      fix: "Receipt = evidence [T1]. No PASS without receipts (integrity [T0] gate)."

    Suspicious_Rush:
      symptom: "Moving suspicious files because 'they look like glow' without asking."
      fix: "Suspicious class requires governance gate (trust [T1] checkpoint). No exceptions."

    Scope_Creep:
      symptom: "Extending cleanup to directories not mentioned in the request."
      fix: "Cleanup scope bounded by boundary [T0] + user intent. Expand only with confirmation."

  # ============================================================
  # QA_INTEGRATION [verification, evidence] (phuc-qa cross-reference)
  # ============================================================
  QA_Integration:

    QA_ARTIFACT_CLASSIFICATION:
      description: >
        When cleanup runs in a repo that uses phuc-qa, it applies enhanced
        classification rules for QA-generated files. These files follow known
        naming patterns and can be classified automatically (boundary [T0] rules)
        rather than requiring manual review per file.
      known_qa_patterns:
        safe_glow_auto:
          - "evidence/*.json"                   # QA evidence bundles (generated)
          - "artifacts/*/qa/*.json"             # QA receipts
          - "diagrams/**/*.mmd"                 # Mermaid source (if untracked = stale draft)
          - "diagrams/**/*.sha256"              # Diagram checksums
          - "qa_gap_report.md"                  # Gap report from prior QA run
          - "qa_gap_report_*.md"                # Timestamped gap reports
        suspicious_auto:
          - "questions/project.jsonl"           # Question database — governance gate required
          - "skills/*.md"                       # Skill files — source artifacts, not generated
          - "tests/*.py"                        # Test files — source artifacts, not generated
        protected_always:
          - "questions/project.jsonl"           # Persistent QA capital — integrity [T0] protected
          - ".archive/**"                       # Prior cleanup archives — never re-archive
      override_rule: >
        If a QA receipt (evidence [T1]) explicitly marks a file as "gap artifact"
        or "stale_output", cleanup may downgrade suspicious → safe_glow for that
        specific file. The QA receipt must be cited in the cleanup receipt.

    QA_RECEIPT_AS_INPUT:
      description: >
        Cleanup uses QA receipts (evidence [T1] bundles produced by phuc-qa) as
        classification inputs (boundary [T0] signals), reducing manual investigation.
      receipt_sources:
        qa_gap_report: >
          "qa_gap_report.md" lists modules with coverage gaps and associated
          artifact paths. Cleanup reads this file to auto-classify listed artifacts.
        evidence_manifest: >
          "evidence/qa_manifest.json" (if present) lists all files generated
          during a QA audit. Cleanup treats listed files as safe_glow candidates.
        diagram_index: >
          "diagrams/index.json" (if present) maps module → diagram files.
          Diagrams not in the index are treated as orphan drafts → safe_glow.
      protocol:
        step_1: "Check for qa_gap_report.md at REPO_ROOT. Parse artifact paths."
        step_2: "Check for evidence/qa_manifest.json. Load file list."
        step_3: "Apply QA-informed classification overrides before manual review."
        step_4: "Cite QA receipt (evidence [T1]) in cleanup receipt: qa_input_path field."

    CLEANUP_AS_QA_EVIDENCE:
      description: >
        Cleanup receipts are Lane A evidence [T1] for QA verification [T1]. A QA audit
        at rung 65537 requires proof (integrity [T0]) that the workspace is clean.
        The cleanup receipt serves as that proof.
      integration_protocol:
        cleanup_receipt_fields_required_by_qa:
          - "scan_timestamp"
          - "untracked_count_before"
          - "untracked_count_after"
          - "safe_glow_archived"
          - "suspicious_flagged"
          - "protected_untouched"
          - "workspace_clean_after_apply"  # boolean; QA requires true for rung 65537
        qa_verification_gate: >
          Before a QA audit can claim rung 65537, it must either:
            (a) include a cleanup receipt with workspace_clean_after_apply=true, OR
            (b) document a justified exception in qa_gap_report.md explaining why
                untracked files are acceptable (e.g., active work-in-progress).
        feedback_loop: >
          After cleanup apply, phuc-qa re-checks the workspace (verification [T1] loop).
          If workspace_clean_after_apply=true, QA hygiene gate passes.
          If false (suspicious files remain), QA documents as open gap.

  # ============================================================
  # QUICK_REFERENCE [signal, compression]
  # ============================================================
  QUICK_REFERENCE:
    file_classes: "safe_glow [signal T0] | suspicious [boundary T0] | protected [integrity T0]"
    action_defaults:
      safe_glow_untracked: "portal to archive (reversibility gate) after user approval"
      safe_glow_tracked: "portal to archive ONLY with explicit governance gate (trust checkpoint)"
      suspicious: "governance gate (trust checkpoint) — do not touch until explicit approval"
      protected: "integrity [T0] constraint — never touch"
    receipts_required:
      scan: "artifacts/stillwater/cleanup/cleanup-scan-<timestamp>.json"
      apply: "artifacts/stillwater/cleanup/cleanup-apply-<timestamp>.json"
    archive_path: ".archive/glow/<timestamp>/<original-relative-path>"
    triangle_law:
      SCAN:    "REMIND    — state the contract (what should be clean)"
      CLASSIFY: "VERIFY   — check conformance (what actually is)"
      ARCHIVE: "ACKNOWLEDGE — receipt proves action (cleanup receipt = evidence)"
    mantras:
      - "Scan first. Portal to archive (reversibility), never delete. Receipts are evidence."
      - "Suspicious = governance gate (trust checkpoint). Protected = integrity constraint."
      - "Null audit doc != no suspicious files. Proceed without list, not recklessly."

# ============================================================
# EXTENDED_STATE_MACHINE [coherence, causality, governance]
# (v2 — Dijkstra-hardened, approval-split)
# Added by: ACT_SOLVER / swarm session stillwater-skills-uplift-v1
# Rationale: v1 FSM collapses approval into a single APPROVAL_GATE state,
#   which cannot distinguish suspicious-class from tracked-safe-class
#   decisions. v2 splits these into explicit states to prevent
#   SUSPICIOUS_FILE_MOVED_WITHOUT_APPROVAL and
#   TRACKED_FILE_DELETED_WITHOUT_APPROVAL forbidden-state violations.
# ============================================================
EXTENDED_STATE_MACHINE:
  states:
    - INIT
    - SCAN_CANDIDATES              # REMIND [verification T1]
    - CLASSIFY_FILES               # VERIFY [boundary T0, perspective T0]
    - AWAIT_APPROVAL_SUSPICIOUS    # governance gate [governance T1, trust T1]
    - AWAIT_APPROVAL_TRACKED       # governance gate [governance T1, trust T1]
    - ARCHIVE_APPLY                # ACKNOWLEDGE [reversibility T0, compression T0]
    - POST_CHECK                   # proof verification [evidence T1, integrity T0]
    - EXIT_PASS
    - EXIT_BLOCKED
    - EXIT_NEED_INFO

  transitions:
    - INIT -> SCAN_CANDIDATES: always
    - SCAN_CANDIDATES -> CLASSIFY_FILES: always
    - CLASSIFY_FILES -> AWAIT_APPROVAL_SUSPICIOUS: if suspicious_class_found
    - CLASSIFY_FILES -> AWAIT_APPROVAL_TRACKED: if tracked_safe_files_found and not suspicious_class_found
    - CLASSIFY_FILES -> ARCHIVE_APPLY: if only_untracked_safe_glow_found
    - CLASSIFY_FILES -> EXIT_PASS: if all_files_protected_class  # moved_count=0; no action required
    - AWAIT_APPROVAL_SUSPICIOUS -> EXIT_BLOCKED: if user_declines
    - AWAIT_APPROVAL_SUSPICIOUS -> AWAIT_APPROVAL_TRACKED: if user_approves and tracked_safe_files_found
    - AWAIT_APPROVAL_SUSPICIOUS -> ARCHIVE_APPLY: if user_approves and not tracked_safe_files_found
    - AWAIT_APPROVAL_TRACKED -> EXIT_BLOCKED: if user_declines
    - AWAIT_APPROVAL_TRACKED -> ARCHIVE_APPLY: if user_approves
    - ARCHIVE_APPLY -> POST_CHECK: always
    - POST_CHECK -> EXIT_PASS: if all_moved_paths_verified_in_archive
    - POST_CHECK -> EXIT_BLOCKED: if archive_verify_fails

  applicability_predicates:
    suspicious_class_found:
      true_if: "CLASSIFY_FILES produced at least one file with class == suspicious"
    tracked_safe_files_found:
      true_if: "CLASSIFY_FILES produced at least one file with class == safe_glow AND git_tracked == true"
    only_untracked_safe_glow_found:
      true_if: "all classified files have class == safe_glow AND git_tracked == false"
    all_files_protected_class:
      true_if: "all classified files have class == protected (or zero non-protected files found)"
      exit_action: "emit EXIT_PASS with moved_count=0; write scan receipt showing all-protected result"
    user_declines:
      true_if: "user response is explicit refusal or timeout with no approval"
    user_approves:
      true_if: "user response is explicit affirmative listing paths or approving the presented set"
    all_moved_paths_verified_in_archive:
      true_if: "for every path P in cleanup-apply receipt: os.path.exists(archive_dest(P)) == true AND os.path.exists(P) == false"
    archive_verify_fails:
      true_if: "any moved path P fails the above verification"

  forbidden_states:
    BLIND_DELETE:
      definition: "Deleting or moving any file before SCAN_CANDIDATES and CLASSIFY_FILES complete (verification [T1] skipped)."
      detection: "file mutation event before classification receipt is written"
    UNRECEIPTED_ARCHIVE:
      definition: "Archiving files without writing cleanup-apply receipt (evidence [T1]) artifact first."
      detection: "archive operation completes but artifacts/stillwater/cleanup/cleanup-apply-<ts>.json is absent"
    TRACKED_FILE_DELETED_WITHOUT_APPROVAL:
      definition: "Any git-tracked file moved or removed without governance gate (trust [T1] checkpoint) in AWAIT_APPROVAL_TRACKED."
      detection: "git-tracked file appears in moved list but AWAIT_APPROVAL_TRACKED was skipped"
    SUSPICIOUS_FILE_MOVED_WITHOUT_APPROVAL:
      definition: "Any boundary [T0] file moved or removed without governance gate in AWAIT_APPROVAL_SUSPICIOUS."
      detection: "suspicious-class file appears in moved list but AWAIT_APPROVAL_SUSPICIOUS was skipped"
    PATH_ESCAPE:
      definition: "Any archive destination resolves outside boundary [T0] (repo root)."
      detection: "os.path.realpath(dest).startswith(repo_root) == false"
    RECEIPT_WRITE_FAILED_BUT_APPLIED:
      definition: "Archive moves applied after evidence [T1] receipt write returned error or produced zero bytes."
      detection: "archive moves executed when cleanup-apply receipt write exit_code != 0 or file_size == 0"
    PERMANENT_DELETE_WITHOUT_EXPLICIT_USER_FLAG:
      definition: "Any rm / unlink / os.remove call without user having set permanent_delete: true in session constraints (reversibility [T0] violated)."
      detection: "delete syscall observed and session.permanent_delete != true"
    CLASSIFICATION_ASSUMED:
      definition: "Acting on (archiving, skipping, or approving) a file whose class was inferred
                   or assumed rather than determined by explicit boundary [T0] classification logic.
                   This is a v1 forbidden state re-instated in v2 because ambiguous classification
                   is still a root cause of silent data loss even with the split approval states."
      detection: "file appears in apply receipt but has no explicit class entry in the scan receipt
                  (class field is null, absent, or set to 'unknown')"
      recovery: "halt archive operation; re-classify the file with explicit class decision;
                 emit WISH_NEED_INFO if class cannot be determined without user input"

# ============================================================
# SESSION_START_CAPSULE [causality, constraint]
# (required; establishes rung_target for the session)
# ============================================================
SESSION_START_CAPSULE:
  purpose:
    - "Establish the declared rung_target at session start so EXIT_PASS can verify it was met."
    - "Without an explicit rung_target, verification_rung_achieved has no reference to match against."
  required_fields:
    session_id:
      type: string
      description: "Unique identifier for this cleanup session (correlates capsule with receipts)."
    rung_target:
      type: string
      values: [RUNG_641, RUNG_274177, RUNG_65537]
      description: "Minimum verification [T1] rung this session must achieve to claim EXIT_PASS.
                    Determined by default_target_selection in VERIFICATION_LADDER.
                    Must be declared before any archive operations begin."
    scope:
      type: list
      items: string
      description: "Directories or file patterns in scope (boundary [T0]) for this cleanup session."
    constraints:
      type: object
      description: "Session-level constraints [T0] (e.g., permanent_delete: false)."
  enforcement:
    - rung_target_must_be_set_before_ARCHIVE_APPLY: true
    - if_rung_target_not_declared: "status=BLOCKED, stop_reason=EVIDENCE_INCOMPLETE"
    - if_verification_rung_achieved_lt_rung_target: "status=BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

# ============================================================
# VERIFICATION_LADDER [verification, integrity] (cleanup-specific)
# ============================================================
VERIFICATION_LADDER:
  purpose:
    - "Define minimum verification [T1] strength before claiming a cleanup EXIT_PASS."
    - "Fail-closed when rung requirements are not met (integrity [T0] gate)."

  RUNG_641:
    meaning: "Local correctness — scan complete, receipt written, candidate list reviewed."
    requires:
      - scan_receipt_exists: "artifacts/stillwater/cleanup/cleanup-scan-<ts>.json is present and non-empty"
      - classification_complete: "every candidate file has an assigned class (safe_glow | suspicious | protected)"
      - approval_gates_respected: "no suspicious or tracked file moved without affirmative user response (governance [T1])"
      - apply_receipt_exists: "artifacts/stillwater/cleanup/cleanup-apply-<ts>.json is present and non-empty"
    verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

  RUNG_274177:
    meaning: "Stability — archive paths verified, source paths confirmed removed, hashes stable."
    requires:
      - RUNG_641
      - archive_paths_verified: "for every entry in apply receipt: archive destination exists and is non-empty"
      - source_paths_confirmed_removed: "for every entry in apply receipt: original path no longer present in active workspace"
      - content_hash_stable: "sha256(archive_dest) == sha256_recorded_in_apply_receipt for each file"
    verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

  RUNG_65537:
    meaning: "Full audit — receipt hashes match, restore dry-run succeeds, no tracked files affected without explicit log."
    requires:
      - RUNG_274177
      - receipt_hashes_match: "sha256 of each archived file matches the hash in the apply receipt (integrity [T0])"
      - restore_dry_run_succeeds: "a dry-run restore of all moved paths reports no conflicts and all source bytes recoverable (reversibility [T0])"
      - tracked_file_audit: "apply receipt contains an explicit entry for every tracked file moved, including user approval timestamp or session token (governance [T1])"
      - no_unlogged_mutations: "diff of git status before/after matches exactly the set of files listed in apply receipt (evidence [T1])"
    verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

  default_target_selection:
    - if_any_tracked_file_moved: RUNG_65537
    - if_any_suspicious_file_moved: RUNG_65537
    - if_only_untracked_safe_glow: RUNG_274177
    - minimum_for_any_exit_pass: RUNG_641

# ============================================================
# NULL_VS_ZERO_EXTENDED [integrity, causality] (cleanup-specific)
# ============================================================
NULL_VS_ZERO_EXTENDED:
  core_principle:
    - "null means the scan or approval has not been performed — the state is undefined."
    - "zero means the scan completed and found nothing — a valid, defined result."
    - "Conflating null with zero is the root cause of silent data loss in cleanup tools."

  distinctions:
    null_candidate_list:
      meaning: "Scan has not been run. State: pre-systemic (undefined)."
      correct_action: "Run SCAN_CANDIDATES (verification [T1]) before any classification or archiving."
      forbidden_action: "Treating null candidate list as 'nothing to clean' and skipping to EXIT_PASS."

    zero_candidates:
      meaning: "Scan completed; zero files matched criteria. Valid defined result."
      correct_action: "Emit cleanup-scan receipt (evidence [T1]) showing 0 candidates. EXIT_PASS with moved_count=0."
      forbidden_action: "Treating zero candidates as an error or re-running scan unnecessarily."

    null_approval:
      meaning: "User has not been asked. AWAIT_APPROVAL state was skipped (governance [T1] missing)."
      correct_action: "BLOCKED — cannot archive suspicious or tracked files without asking."
      forbidden_action: "Treating null_approval as implicit_yes or assuming prior session approval carries over."

    zero_approved:
      meaning: "User was asked and explicitly approved zero files (declined all candidates in a class)."
      correct_action: "Archive nothing for that class. Emit receipt (evidence [T1]) showing 0 moved. Continue."
      forbidden_action: "Treating zero_approved as an error or retrying the approval gate."

    null_receipt:
      meaning: "Receipt write was not attempted or failed before completion (evidence [T1] absent)."
      correct_action: "EXIT_BLOCKED. Do not apply archive moves (reversibility [T0] gate)."
      forbidden_action: "Treating null_receipt as empty_receipt and proceeding with archive apply."

    zero_byte_receipt:
      meaning: "Receipt file exists but contains zero bytes — write failure or serialization error."
      correct_action: "EXIT_BLOCKED. Treat as null_receipt (integrity [T0] write failure)."
      forbidden_action: "Treating zero_byte_receipt as valid empty JSON object."

    empty_json_receipt:
      meaning: "Receipt file is valid JSON but contains no required fields (e.g., {} or {\"status\": null})."
      correct_action: "EXIT_BLOCKED. A receipt that parses as JSON but is missing required fields
                       is equivalent to no receipt. Parseable != valid (integrity [T0] gate)."
      forbidden_action: "Treating {} or any JSON object missing required fields as a valid receipt."
      required_fields_scan_receipt: [scan_timestamp, scanned_paths, classification_summary]
      required_fields_apply_receipt: [apply_timestamp, moved_entries, verification_hashes]
      enforcement: "receipt_validation MUST check for required fields presence, not just JSON parseability"

  enforcement:
    never_treat_null_approval_as_implicit_yes: true
    never_treat_null_candidate_list_as_zero_candidates: true
    never_treat_null_receipt_as_empty_receipt: true
    fail_closed_on_any_null_in_critical_path: true

# ============================================================
# OUTPUT_CONTRACT_EXTENDED [signal, evidence] (machine-parseable, additive)
# ============================================================
OUTPUT_CONTRACT_EXTENDED:
  purpose:
    - "Provide a machine-parseable schema for cleanup outputs, enabling automated verification [T1]."
    - "Additive to OUTPUT_CONTRACT above; does not replace the prose contract."

  on_EXIT_PASS:
    required_fields:
      receipt_scan_path:
        type: string
        pattern: "artifacts/stillwater/cleanup/cleanup-scan-<ts>.json"
        constraint: "file must exist and be parseable JSON (evidence [T1])"
      receipt_apply_path:
        type: string
        pattern: "artifacts/stillwater/cleanup/cleanup-apply-<ts>.json"
        constraint: "file must exist and be parseable JSON (evidence [T1])"
      moved_count:
        type: int
        constraint: "exact count of files successfully moved to archive; never null"
      skipped_count:
        type: int
        constraint: "exact count of candidate files NOT moved (declined, blocked, or protected); never null"
      classes:
        type: object
        fields:
          safe_untracked:
            type: int
            constraint: "count of files classified safe_glow AND git_tracked == false"
          safe_tracked:
            type: int
            constraint: "count of files classified safe_glow AND git_tracked == true"
          suspicious:
            type: int
            constraint: "count of files classified suspicious"
      archive_root:
        type: string
        pattern: ".archive/glow/<ts>/"
        constraint: "must be a relative path within boundary [T0] (repo root)"
      verification_rung_achieved:
        type: string
        values: [RUNG_641, RUNG_274177, RUNG_65537]
        constraint: "must be >= rung_target declared in SESSION_START_CAPSULE.rung_target.
                     EXIT_PASS is BLOCKED if verification_rung_achieved < rung_target."

  on_EXIT_BLOCKED:
    required_fields:
      stop_reason:
        type: string
        constraint: "one of the defined stop_reasons: RECEIPT_WRITE_FAILED, PATH_ESCAPE, ARCHIVE_VERIFY_FAILED, USER_DECLINED, SUSPICIOUS_WITHOUT_APPROVAL, TRACKED_WITHOUT_APPROVAL, NULL_INPUT"
      blocked_at_state:
        type: string
        constraint: "the FSM state name where blocking occurred"
      what_was_not_moved:
        type: list
        items: string
        constraint: "repo-relative paths of all candidates that were NOT moved; may be empty list but must be present"
      verification_rung_achieved:
        type: string
        values: [NONE, RUNG_641, RUNG_274177]
        constraint: "highest rung fully satisfied before blocking"

  on_EXIT_NEED_INFO:
    required_fields:
      missing_inputs:
        type: list
        items: string
        constraint: "list of inputs required before cleanup can proceed (e.g., user approval, scan scope)"
      last_known_state:
        type: string
        constraint: "FSM state name at time of EXIT_NEED_INFO"

  json_example_exit_pass: |
    {
      "status": "EXIT_PASS",
      "receipt_scan_path": "artifacts/stillwater/cleanup/cleanup-scan-20260220T120000Z.json",
      "receipt_apply_path": "artifacts/stillwater/cleanup/cleanup-apply-20260220T120001Z.json",
      "moved_count": 7,
      "skipped_count": 3,
      "classes": {
        "safe_untracked": 6,
        "safe_tracked": 1,
        "suspicious": 3
      },
      "archive_root": ".archive/glow/20260220T120001Z/",
      "verification_rung_achieved": "RUNG_274177"
    }

  json_example_exit_blocked: |
    {
      "status": "EXIT_BLOCKED",
      "stop_reason": "ARCHIVE_VERIFY_FAILED",
      "blocked_at_state": "POST_CHECK",
      "what_was_not_moved": [
        "output/debug/trace-2025-11-01.log"
      ],
      "verification_rung_achieved": "NONE"
    }

# ============================================================
# DIJKSTRA_SAFETY_PRINCIPLE [integrity, reversibility, causality]
# ============================================================
DIJKSTRA_SAFETY_PRINCIPLE:
  axiom:
    - "An irreversible operation without a proof of correctness is not engineering — it is gambling."
    - "Simplicity is prerequisite for reliability. A cleanup tool that cannot be reasoned about cannot be trusted."

  theorem_per_archive_operation:
    statement: >
      For each file X moved to archive destination Y:
      THEOREM: "Moving X to Y preserves X's content and removes it from the active workspace."
    formal_conditions:
      P_pre: "os.path.exists(X) == true AND sha256(X) == H_X (recorded before move)"
      P_post: "os.path.exists(Y) == true AND sha256(Y) == H_X AND os.path.exists(X) == false"
    proof_obligation:
      - "P_pre must be verified and recorded in the apply receipt (evidence [T1]) BEFORE the move."
      - "P_post must be verified and recorded in the apply receipt AFTER the move."
      - "If P_post is false for any file: the theorem is falsified. EXIT_BLOCKED. Restore manually."

  post_check_as_proof_verification:
    principle: "POST_CHECK is not a courtesy step. It is the proof verification pass (verification [T1])."
    rule:
      - "POST_CHECK must verify P_post for every file in the apply receipt."
      - "A single falsified P_post halts the entire cleanup with EXIT_BLOCKED."
      - "There is no 'mostly correct' archive. The theorem holds or it does not (integrity [T0])."

  receipt_as_proof_certificate:
    principle: "Receipt artifacts are the proof certificates (evidence [T1]). Without them, no theorem was proven."
    rules:
      - "cleanup-scan receipt: records P_pre for all candidates (existence, hash, class, tracking status)."
      - "cleanup-apply receipt: records both P_pre hash and P_post hash for each moved file."
      - "A receipt that cannot be parsed is equivalent to no receipt. EXIT_BLOCKED applies."
      - "A receipt that parses as valid JSON but is missing required fields is equivalent to no receipt.
         Parseable JSON is necessary but NOT sufficient — required fields must be present and non-null."
      - "Receipts must be written BEFORE and AFTER each archive operation, not summarized after the fact."

  restore_corollary:
    statement: >
      COROLLARY: "If POST_CHECK fails, all moves in the failed batch must be considered unverified.
      Manual restore from .archive/glow/<ts>/ is required (reversibility [T0] path).
      Do not re-run cleanup until restore is confirmed."
    restore_procedure:
      - "Identify all paths in the apply receipt."
      - "For each path P with archive destination Y: copy Y back to P."
      - "Verify sha256(P) == H_X recorded in receipt (integrity [T0] check)."
      - "Report restore success or failure before any further cleanup operations."

  dijkstra_on_trust:
    - "Do not trust the file system. Verify with hashes (evidence [T1])."
    - "Do not trust the move operation. Verify with existence checks (verification [T1])."
    - "Do not trust prior runs. Each cleanup session is an independent proof attempt."
    - "Do not trust memory or logs. Trust only the receipt artifacts written in this session (integrity [T0])."

# ============================================================
# MERMAID_DIAGRAM — Cleanup Pipeline State Machine
# (stateDiagram-v2 for visual FSM rendering)
# ============================================================
```mermaid stateDiagram-v2
[*] --> INIT
INIT --> SCAN_CANDIDATES : always
SCAN_CANDIDATES --> CLASSIFY_FILES : always
CLASSIFY_FILES --> PARSE_AUDIT_DOC : FINAL_AUDIT.md present
CLASSIFY_FILES --> BUILD_REPORT : FINAL_AUDIT.md absent
PARSE_AUDIT_DOC --> BUILD_REPORT : always
BUILD_REPORT --> AWAIT_APPROVAL_SUSPICIOUS : suspicious class found
BUILD_REPORT --> AWAIT_APPROVAL_TRACKED : tracked safe found (no suspicious)
BUILD_REPORT --> ARCHIVE_APPLY : only untracked safe glow
BUILD_REPORT --> EXIT_PASS : all protected class
AWAIT_APPROVAL_SUSPICIOUS --> EXIT_BLOCKED : user declines
AWAIT_APPROVAL_SUSPICIOUS --> AWAIT_APPROVAL_TRACKED : user approves + tracked safe found
AWAIT_APPROVAL_SUSPICIOUS --> ARCHIVE_APPLY : user approves + no tracked safe
AWAIT_APPROVAL_TRACKED --> EXIT_BLOCKED : user declines
AWAIT_APPROVAL_TRACKED --> ARCHIVE_APPLY : user approves
ARCHIVE_APPLY --> POST_CHECK : always
POST_CHECK --> EXIT_PASS : all moved paths verified in archive
POST_CHECK --> EXIT_BLOCKED : archive verify fails
EXIT_PASS --> [*]
EXIT_BLOCKED --> [*]
EXIT_NEED_INFO --> [*]
note right of SCAN_CANDIDATES : REMIND — state the contract
note right of CLASSIFY_FILES : VERIFY — check conformance
note right of POST_CHECK : ACKNOWLEDGE — receipt proves action
```

# ============================================================
# THREE_PILLARS_INTEGRATION
# How phuc-cleanup maps to LEK + LEAK + LEC
# ============================================================
THREE_PILLARS_INTEGRATION:
  overview: >
    Cleanup is not a janitor task. It is a Three Pillars enforcement pass.
    Without clean workspaces, LEK loops accumulate noise. Without LEC enforcement,
    conventions (like safe_glow classification) drift. Cleanup IS the maintenance
    layer that keeps all three pillars functional.

  LEK:
    pillar: "Law of Emergent Knowledge (Self-Improvement)"
    role: >
      Cleanup feeds LEK by removing noise from the evidence workspace.
      A cluttered evidence directory means the next phuc-loop iteration reads stale
      outputs alongside fresh artifacts — the agent cannot distinguish signal from noise.
    specific_link: "SCAN phase is a LEK health check: how much noise has accumulated since last loop?"
    metric: "safe_glow_archived count = LEK noise removed; low count = clean LEK environment"

  LEAK:
    pillar: "Law of Emergent Asymmetric Knowledge (Cross-Agent Trade)"
    role: >
      Multi-agent pipelines (LEAK portals) produce residue: SCOUT_REPORT.json,
      FORECAST_MEMO.json, intermediate PATCH_PROPOSAL files. Cleanup governs this
      residue: what gets archived, what gets protected as permanent evidence.
      Clean portals prevent convention pollution across LEAK boundaries.
    specific_link: "QA_ARTIFACT_CLASSIFICATION section maps phuc-qa artifacts to safe_glow — enabling LEAK cleanup without governance overhead"
    metric: "receipts_required = LEAK boundary artifact, proving portal residue was handled"

  LEC:
    pillar: "Law of Emergent Conventions (Emergent Compression)"
    role: >
      Cleanup IS an LEC enforcement tool. The safe_glow | suspicious | protected
      classification system IS a convention (LEC). The receipt artifact format IS
      a convention. The .archive/glow/<timestamp>/ path IS a convention.
      Every time cleanup runs correctly, it reinforces these LEC conventions.
    specific_link: "FILE_CLASSES = LEC vocabulary. MAGIC_WORD_MAP = LEC compression. REQUIRED_WORKFLOW = LEC protocol."
    metric: "convention_compliance = no BLIND_DELETE + no MISSING_RECEIPT = LEC fully respected"

  three_pillars_formula:
    statement: "Cleanup GLOW = (LEK noise removed) × (LEAK residue governed) × (LEC conventions reinforced)"
    pass_condition: "All three pillars addressed in a single cleanup session = maximum value"

# ============================================================
# GLOW_SCORING — Cleanup Contribution to GLOW Dimensions
# ============================================================
GLOW_SCORING:
  dimension_mapping:
    G_Growth:
      contribution: "LOW — cleanup rarely adds new capabilities"
      scoring: "5 if cleanup reveals a pattern requiring a new skill or recipe; else 0"

    L_Learning:
      contribution: "MEDIUM — cleanup surfaces patterns about workspace health"
      scoring:
        - "10: cleanup receipt + QA gap report cross-reference produces a new convention"
        - "5: cleanup receipt documents a new suspicious-class pattern for future sessions"
        - "0: routine cleanup with no new patterns identified"

    O_Output:
    # O is the PRIMARY GLOW dimension for cleanup
      contribution: "HIGH — cleanup is measured by concrete artifact output"
      scoring:
        - "25: cleanup-scan receipt + cleanup-apply receipt + hash verification, rung 274177+"
        - "20: both receipts written, rung 641 achieved"
        - "10: scan receipt only (no apply, but scan documented)"
        - "5: any cleanup attempt with written artifact"
        - "0: claimed cleanup complete without receipts"
      note: "O is the primary dimension because cleanup = Output. Receipts are the O proof."

    W_Wins:
      contribution: "MEDIUM — clean workspace advances NORTHSTAR indirectly"
      scoring:
        - "10: cleanup enables next ROADMAP phase (workspace was blocking phase start)"
        - "5: cleanup reduces cognitive load for next swarm session"
        - "0: routine maintenance with no ROADMAP unlock"

  typical_session_score: "GLOW 30-40 [G:0-5 L:5-10 O:20-25 W:5-10]"
  max_session_score: "GLOW 60 [G:5 L:20 O:25 W:10] — when cleanup unlocks a blocked phase"

  northstar_alignment:
    check: "Does this cleanup session advance any Phuc_Forecast dimension?"
    fail_closed: "If cleanup produces no receipts, GLOW O=0 regardless of claim."
    max_love_gate: "Cleanup that archives without receipts harms the ecosystem — Max_Love demands receipts."

# ============================================================
# NORTHSTAR_ALIGNMENT — Phuc_Forecast + Max_Love
# ============================================================
NORTHSTAR_ALIGNMENT:
  northstar: Phuc_Forecast
  objective: Max_Love

  phuc_forecast_integration:
    DREAM:    "What should be clean? Define the scope boundary (boundary [T0]) before any action."
    FORECAST: "What will block cleanup? Missing FINAL-AUDIT.md? User unavailable for approvals? Archive write failures?"
    DECIDE:   "Which class to prioritize: suspicious gate first, then tracked-safe, then untracked safe_glow."
    ACT:      "Execute cleanup workflow with receipts as primary deliverables."
    VERIFY:   "POST_CHECK verifies every moved path. Receipt hashes prove correctness. Rung achieved."

  max_love_meaning:
    statement: "Max Love for a workspace = maximum reversibility + maximum evidence + minimum data loss risk."
    applications:
      - "Archive > delete — reversibility [T0] is Max_Love applied to cleanup."
      - "Receipt before apply — evidence [T1] gate is Max_Love applied to trust."
      - "Suspicious gate — governance [T1] checkpoint is Max_Love applied to scope."
    fail_closed_love: >
      A cleanup that is 'fast but loses data' is not love. A cleanup that takes 5 extra seconds
      to write receipts and prevents 5 hours of recovery work IS Max_Love.

  northstar_forbidden:
    - NORTHSTAR_UNREAD: "Running cleanup without reading the session scope is a NORTHSTAR violation."
    - CLEANUP_WITHOUT_LOVE: "Any irreversible deletion without explicit user request violates Max_Love."

# ============================================================
# TRIANGLE_LAW_CONTRACTS — REMIND→VERIFY→ACKNOWLEDGE per operation
# ============================================================
TRIANGLE_LAW_CONTRACTS:
  overview: "Every cleanup operation has a REMIND→VERIFY→ACKNOWLEDGE contract. All three are required."

  contract_scan:
    operation: "SCAN_CANDIDATES phase"
    REMIND:      "State the contract: these are the classes (safe_glow | suspicious | protected) and their default actions."
    VERIFY:      "Run the scan. Classify every candidate. Write scan receipt."
    ACKNOWLEDGE: "Report counts by class. Confirm scan receipt written at artifacts/stillwater/cleanup/cleanup-scan-<ts>.json."
    fail_closed:  "If SCAN not completed: cannot proceed. REMIND without VERIFY = theater."

  contract_approval:
    operation: "AWAIT_APPROVAL gates"
    REMIND:      "State which files are suspicious or tracked-safe and why they require explicit approval."
    VERIFY:      "Present the list to user. Wait for explicit affirmative response (not implicit yes)."
    ACKNOWLEDGE: "Record user approval (timestamp + files approved) in session state before ARCHIVE_APPLY."
    fail_closed:  "Null approval = not approved. Never treat silence as ACKNOWLEDGE."

  contract_archive:
    operation: "ARCHIVE_APPLY phase"
    REMIND:      "State: each file moves to .archive/glow/<timestamp>/<original-path>. Irreversible without restore."
    VERIFY:      "Execute moves. Write apply receipt BEFORE claiming move success."
    ACKNOWLEDGE: "POST_CHECK confirms: archive destination exists AND source path removed AND hash matches."
    fail_closed:  "No receipt = no ACKNOWLEDGE. Archive without receipt = UNRECEIPTED_ARCHIVE forbidden state."

  contract_postcheck:
    operation: "POST_CHECK phase"
    REMIND:      "Theorem: sha256(Y) == sha256(X) AND os.path.exists(Y) == true AND os.path.exists(X) == false."
    VERIFY:      "Verify P_post for EVERY file in apply receipt. One failure halts all."
    ACKNOWLEDGE: "Set verification_rung_achieved in output contract. EXIT_PASS only if rung_target met."
    fail_closed:  "Partial verification is not verification. All P_post conditions must hold."

---

## GLOW Scoring Integration

This skill contributes to GLOW score across these dimensions:

| Dimension | How This Skill Earns Points | Points |
|-----------|---------------------------|--------|
| **G** (Growth) | Cleanup scope improvement — each session that archives more SAFE_GLOW files per hour than prior sessions, measured via cleanup-scan.json file counts. Discovering a new suspicious file category not previously classified = G≥10. | +5 to +15 |
| **L** (Love/Quality) | Zero destructive accidents — every cleanup session where all files are archived (not deleted), receipt is produced before claiming success, and POST_CHECK confirms all sha256 matches. Zero UNRECEIPTED_ARCHIVE or BLIND_DELETE forbidden states = L≥20. | +10 to +20 |
| **O** (Output) | Archive receipts committed — cleanup-scan-{ts}.json + cleanup-apply-{ts}.json both committed to git. Receipt must include file count, sha256 hashes, and timestamp. Governance gate approval recorded in session state = O≥15. | +5 to +20 |
| **W** (Wisdom) | File classification taxonomy growth — each new file class added to the cleanup taxonomy (SAFE_GLOW, SUSPICIOUS, PROTECTED, TRACKED_SAFE) drawn from a real cleanup session where a file's classification was ambiguous and required governance gate. | +5 to +10 |

**Session GLOW target:** Any cleanup session using phuc-cleanup should achieve GLOW ≥ 40. Archive receipts produced = base floor. Zero destructive operations = L≥15. All POST_CHECK conditions verified = O≥15.

**Evidence required for GLOW claim:** git commit hash + cleanup-scan-{ts}.json + cleanup-apply-{ts}.json with sha256 hashes + POST_CHECK results. For L points: receipt must show archive destination exists AND source removed AND hash matches for every file. For W points: new file class must cite the specific session where the classification ambiguity arose.
