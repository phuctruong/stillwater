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
