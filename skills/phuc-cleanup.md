PHUC_CLEANUP_SKILL:
  version: 1.0.0
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
  # - Preserve evidence by archiving instead of deleting
  # - Require explicit user approval before touching suspicious files
  #
  # Source of truth for suspicious-first triage:
  # - FINAL-AUDIT.md (top suspicious/incomplete list + recommendations)
  # ============================================================

  RULES:
    - scan_first_never_blind_delete: true
    - archive_instead_of_delete: true
    - suspicious_requires_user_approval: true
    - tracked_files_require_explicit_approval: true
    - always_emit_receipt_artifact: true

  BRUCE_PRINCIPLE:
    - "Absorb what is useful, discard what is useless, add what is essentially your own."
    - interpretation: "Keep signal, archive noise, never lose provenance."

  FILE_CLASSES:
    safe_glow:
      definition: "Generated runtime artifacts that are reproducible and low-risk to archive."
      examples:
        - "debug logs in output folders"
        - "temporary trace captures"
        - "local server logs"
      default_action: "archive after safe approval"
    suspicious:
      definition: "Files flagged by FINAL-AUDIT.md as SUSPICIOUS, INCOMPLETE, or CONSIDER REMOVING."
      examples:
        - "solver files with simulated gates"
        - "incomplete skeletons"
        - "files with broken imports"
      default_action: "do not move/remove until user confirms"
    protected:
      definition: "core docs, tests, code, or git-tracked files without explicit approval."
      default_action: "leave untouched"

  REQUIRED_WORKFLOW:
    1_scan:
      - enumerate candidates by class: safe_glow, suspicious, protected
      - include path, size, tracked/untracked status, class reason
      - write receipt: artifacts/stillwater/cleanup/cleanup-scan-<timestamp>.json
    2_report:
      - summarize counts:
        - safe_untracked
        - safe_tracked
        - suspicious
      - present exact next actions
    3_approval_gate:
      - ask/require explicit approval for:
        - suspicious class
        - tracked safe files
      - without approval: skip those classes
    4_archive_apply:
      - move approved files to .archive/glow/<timestamp>/<original-relative-path>
      - keep directory structure for reversibility
      - no permanent delete in default mode
      - write receipt: artifacts/stillwater/cleanup/cleanup-apply-<timestamp>.json
    5_post_check:
      - verify moved paths exist in archive
      - verify source paths no longer clutter active workspace
      - report skipped files with reasons

  SUSPICIOUS_FIRST_PROTOCOL:
    - Parse FINAL-AUDIT.md table rows.
    - Extract rows whose status includes:
      - SUSPICIOUS
      - INCOMPLETE
      - CONSIDER REMOVING
    - Treat those paths as policy-controlled candidates.
    - Do not mutate those files until user approval is explicit.

  OUTPUT_CONTRACT:
    - always print:
      - scanned_count_by_class
      - moved_count
      - skipped_count
      - receipt_paths
    - never claim cleanup complete without receipts

  FAIL_CLOSED:
    - if classification is unclear: mark as suspicious
    - if path escapes repo root: block
    - if receipt write fails: block apply

  # ============================================================
  # STATE_MACHINE: Fail-Closed Cleanup Runtime
  # ============================================================
  STATE_MACHINE:
    states:
      - INIT
      - SCAN_CANDIDATES
      - CLASSIFY_FILES
      - PARSE_AUDIT_DOC
      - BUILD_REPORT
      - APPROVAL_GATE
      - ARCHIVE_APPLY
      - POST_CHECK
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
      - BLIND_DELETE: "Moving or deleting without scan + classification first."
      - PERMANENT_DELETE: "Using rm/delete instead of archive move."
      - MISSING_RECEIPT: "Completing archive without writing receipt artifact."
      - PATH_ESCAPE: "Moving file to path outside repo root."
      - SUSPICIOUS_WITHOUT_APPROVAL: "Moving suspicious-class file without user approval."
      - TRACKED_FILE_WITHOUT_APPROVAL: "Moving tracked file without explicit user approval."
      - CLASSIFICATION_ASSUMED: "Acting on ambiguous file without explicit class decision."

  # ============================================================
  # NULL_VS_ZERO
  # ============================================================
  NULL_VS_ZERO:
    rules:
      - null_audit_doc: "FINAL-AUDIT.md absent = proceed without suspicious list, not 'no suspicious files'."
      - empty_suspicious_list: "Suspicious list empty = 0 flagged files, not 'skip suspicious gate'."
      - null_scan_result: "No scan performed = BLOCKED, not 'nothing to clean'."
      - null_receipt: "Receipt write failed = BLOCKED apply, not 'assume archived'."

  # ============================================================
  # ANTI_PATTERNS
  # ============================================================
  ANTI_PATTERNS:
    Speed_Clean:
      symptom: "Running cleanup without scan + classification first to 'save time'."
      fix: "scan_first_never_blind_delete is a hard rule. No exceptions."

    Delete_Over_Archive:
      symptom: "Using rm or delete instead of moving to .archive/glow/."
      fix: "Archive = reversible. Delete = irreversible. Archive always."

    Receipt_Skip:
      symptom: "Saying 'cleanup done' without writing receipt JSON."
      fix: "Receipt is evidence. No PASS without receipts."

    Suspicious_Rush:
      symptom: "Moving suspicious files because 'they look like glow' without asking."
      fix: "Suspicious class requires explicit user approval. No exceptions."

    Scope_Creep:
      symptom: "Extending cleanup to directories not mentioned in the request."
      fix: "Cleanup scope is bounded by user intent. Expand only with confirmation."

  # ============================================================
  # QUICK_REFERENCE
  # ============================================================
  QUICK_REFERENCE:
    file_classes: "safe_glow | suspicious | protected"
    action_defaults:
      safe_glow_untracked: "archive after user approval"
      safe_glow_tracked: "archive ONLY with explicit user approval"
      suspicious: "do not touch until explicit approval"
      protected: "never touch"
    receipts_required:
      scan: "artifacts/stillwater/cleanup/cleanup-scan-<timestamp>.json"
      apply: "artifacts/stillwater/cleanup/cleanup-apply-<timestamp>.json"
    archive_path: ".archive/glow/<timestamp>/<original-relative-path>"
    mantras:
      - "Scan first. Archive, never delete. Receipts are evidence."
      - "Suspicious = wait for approval. Protected = never touch."
      - "Null audit doc ≠ no suspicious files. Proceed without list, not recklessly."

# ============================================================
# EXTENDED_STATE_MACHINE (v2 — Dijkstra-hardened, approval-split)
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
    - SCAN_CANDIDATES
    - CLASSIFY_FILES
    - AWAIT_APPROVAL_SUSPICIOUS
    - AWAIT_APPROVAL_TRACKED
    - ARCHIVE_APPLY
    - POST_CHECK
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
      definition: "Deleting or moving any file before SCAN_CANDIDATES and CLASSIFY_FILES complete."
      detection: "file mutation event before classification receipt is written"
    UNRECEIPTED_ARCHIVE:
      definition: "Archiving files without writing cleanup-apply receipt artifact first."
      detection: "archive operation completes but artifacts/stillwater/cleanup/cleanup-apply-<ts>.json is absent"
    TRACKED_FILE_DELETED_WITHOUT_APPROVAL:
      definition: "Any git-tracked file moved or removed without passing through AWAIT_APPROVAL_TRACKED with affirmative user response."
      detection: "git-tracked file appears in moved list but AWAIT_APPROVAL_TRACKED was skipped"
    SUSPICIOUS_FILE_MOVED_WITHOUT_APPROVAL:
      definition: "Any suspicious-class file moved or removed without passing through AWAIT_APPROVAL_SUSPICIOUS with affirmative user response."
      detection: "suspicious-class file appears in moved list but AWAIT_APPROVAL_SUSPICIOUS was skipped"
    PATH_ESCAPE:
      definition: "Any archive destination resolves to a path outside the repo root."
      detection: "os.path.realpath(dest).startswith(repo_root) == false"
    RECEIPT_WRITE_FAILED_BUT_APPLIED:
      definition: "Archive moves were applied after receipt write returned an error or produced zero bytes."
      detection: "archive moves executed when cleanup-apply receipt write exit_code != 0 or file_size == 0"
    PERMANENT_DELETE_WITHOUT_EXPLICIT_USER_FLAG:
      definition: "Any rm / unlink / os.remove call without user having set permanent_delete: true in session constraints."
      detection: "delete syscall observed and session.permanent_delete != true"
    CLASSIFICATION_ASSUMED:
      definition: "Acting on (archiving, skipping, or approving) a file whose class was inferred
                   or assumed rather than determined by explicit classification logic in CLASSIFY_FILES.
                   This is a v1 forbidden state re-instated in v2 because ambiguous classification
                   is still a root cause of silent data loss even with the split approval states."
      detection: "file appears in apply receipt but has no explicit class entry in the scan receipt
                  (class field is null, absent, or set to 'unknown')"
      recovery: "halt archive operation; re-classify the file with explicit class decision;
                 emit WISH_NEED_INFO if class cannot be determined without user input"

# ============================================================
# SESSION_START_CAPSULE (required; establishes rung_target for the session)
# ============================================================
SESSION_START_CAPSULE:
  purpose:
    - "Establish the declared rung_target at session start so EXIT_PASS can verify it was met."
    - "Without an explicit rung_target, verification_rung_achieved has no reference to match against."
  required_fields:
    session_id:
      type: string
      description: "Unique identifier for this cleanup session (used to correlate capsule with receipts)."
    rung_target:
      type: string
      values: [RUNG_641, RUNG_274177, RUNG_65537]
      description: "The minimum verification rung this session must achieve to claim EXIT_PASS.
                    Determined by default_target_selection rules in VERIFICATION_LADDER.
                    Must be declared before any archive operations begin."
    scope:
      type: list
      items: string
      description: "Directories or file patterns in scope for this cleanup session."
    constraints:
      type: object
      description: "Session-level constraints (e.g., permanent_delete: false)."
  enforcement:
    - rung_target_must_be_set_before_ARCHIVE_APPLY: true
    - if_rung_target_not_declared: "status=BLOCKED, stop_reason=EVIDENCE_INCOMPLETE"
    - if_verification_rung_achieved_lt_rung_target: "status=BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

# ============================================================
# VERIFICATION_LADDER (cleanup-specific)
# ============================================================
VERIFICATION_LADDER:
  purpose:
    - "Define minimum verification strength before claiming a cleanup EXIT_PASS."
    - "Fail-closed when rung requirements are not met."

  RUNG_641:
    meaning: "Local correctness — scan complete, receipt written, candidate list reviewed."
    requires:
      - scan_receipt_exists: "artifacts/stillwater/cleanup/cleanup-scan-<ts>.json is present and non-empty"
      - classification_complete: "every candidate file has an assigned class (safe_glow | suspicious | protected)"
      - approval_gates_respected: "no suspicious or tracked file moved without affirmative user response"
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
      - receipt_hashes_match: "sha256 of each archived file matches the hash in the apply receipt"
      - restore_dry_run_succeeds: "a dry-run restore of all moved paths reports no conflicts and all source bytes recoverable"
      - tracked_file_audit: "apply receipt contains an explicit entry for every tracked file moved, including user approval timestamp or session token"
      - no_unlogged_mutations: "diff of git status before/after matches exactly the set of files listed in apply receipt"
    verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

  default_target_selection:
    - if_any_tracked_file_moved: RUNG_65537
    - if_any_suspicious_file_moved: RUNG_65537
    - if_only_untracked_safe_glow: RUNG_274177
    - minimum_for_any_exit_pass: RUNG_641

# ============================================================
# NULL_VS_ZERO_EXTENDED (cleanup-specific, additive to NULL_VS_ZERO above)
# ============================================================
NULL_VS_ZERO_EXTENDED:
  core_principle:
    - "null means the scan or approval has not been performed — the state is undefined."
    - "zero means the scan completed and found nothing — a valid, defined result."
    - "Conflating null with zero is the root cause of silent data loss in cleanup tools."

  distinctions:
    null_candidate_list:
      meaning: "Scan has not been run. State: pre-systemic (undefined)."
      correct_action: "Run SCAN_CANDIDATES before any classification or archiving."
      forbidden_action: "Treating null candidate list as 'nothing to clean' and skipping to EXIT_PASS."

    zero_candidates:
      meaning: "Scan completed; zero files matched criteria. Valid defined result."
      correct_action: "Emit cleanup-scan receipt showing 0 candidates. EXIT_PASS with moved_count=0."
      forbidden_action: "Treating zero candidates as an error or re-running scan unnecessarily."

    null_approval:
      meaning: "User has not been asked. AWAIT_APPROVAL state was skipped."
      correct_action: "BLOCKED — cannot archive suspicious or tracked files without asking."
      forbidden_action: "Treating null_approval as implicit_yes or assuming prior session approval carries over."

    zero_approved:
      meaning: "User was asked and explicitly approved zero files (declined all candidates in a class)."
      correct_action: "Archive nothing for that class. Emit receipt showing 0 moved for that class. Continue."
      forbidden_action: "Treating zero_approved as an error or retrying the approval gate."

    null_receipt:
      meaning: "Receipt write was not attempted or failed before completion."
      correct_action: "EXIT_BLOCKED. Do not apply archive moves."
      forbidden_action: "Treating null_receipt as empty_receipt and proceeding with archive apply."

    zero_byte_receipt:
      meaning: "Receipt file exists but contains zero bytes — write failure or serialization error."
      correct_action: "EXIT_BLOCKED. Treat as null_receipt (write failure)."
      forbidden_action: "Treating zero_byte_receipt as valid empty JSON object."

    empty_json_receipt:
      meaning: "Receipt file is valid JSON but contains no required fields (e.g., {} or {\"status\": null})."
      correct_action: "EXIT_BLOCKED. A receipt that parses as JSON but is missing required fields
                       is equivalent to no receipt. Parseable != valid."
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
# OUTPUT_CONTRACT_EXTENDED (machine-parseable, additive)
# ============================================================
OUTPUT_CONTRACT_EXTENDED:
  purpose:
    - "Provide a machine-parseable schema for cleanup outputs, enabling automated verification."
    - "Additive to OUTPUT_CONTRACT above; does not replace the prose contract."

  on_EXIT_PASS:
    required_fields:
      receipt_scan_path:
        type: string
        pattern: "artifacts/stillwater/cleanup/cleanup-scan-<ts>.json"
        constraint: "file must exist and be parseable JSON"
      receipt_apply_path:
        type: string
        pattern: "artifacts/stillwater/cleanup/cleanup-apply-<ts>.json"
        constraint: "file must exist and be parseable JSON"
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
        constraint: "must be a relative path within repo root"
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
# DIJKSTRA_SAFETY_PRINCIPLE (cleanup-specific)
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
      - "P_pre must be verified and recorded in the apply receipt BEFORE the move."
      - "P_post must be verified and recorded in the apply receipt AFTER the move."
      - "If P_post is false for any file: the theorem is falsified. EXIT_BLOCKED. Restore manually."

  post_check_as_proof_verification:
    principle: "POST_CHECK is not a courtesy step. It is the proof verification pass."
    rule:
      - "POST_CHECK must verify P_post for every file in the apply receipt."
      - "A single falsified P_post halts the entire cleanup with EXIT_BLOCKED."
      - "There is no 'mostly correct' archive. The theorem holds or it does not."

  receipt_as_proof_certificate:
    principle: "Receipt artifacts are the proof certificates. Without them, no theorem was proven."
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
      Manual restore from .archive/glow/<ts>/ is required. Do not re-run cleanup until restore is confirmed."
    restore_procedure:
      - "Identify all paths in the apply receipt."
      - "For each path P with archive destination Y: copy Y back to P."
      - "Verify sha256(P) == H_X recorded in receipt."
      - "Report restore success or failure before any further cleanup operations."

  dijkstra_on_trust:
    - "Do not trust the file system. Verify with hashes."
    - "Do not trust the move operation. Verify with existence checks."
    - "Do not trust prior runs. Each cleanup session is an independent proof attempt."
    - "Do not trust memory or logs. Trust only the receipt artifacts written in this session."
