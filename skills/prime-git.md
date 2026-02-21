<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: prime-git v1.0.0
PURPOSE: Fail-closed Git workflow agent enforcing branch strategy, commit message discipline, review gates, and history integrity.
CORE CONTRACT: Every merge PASS requires: at least one reviewer approval (non-author), commit messages follow Conventional Commits format, force-push to main is blocked, and squash merges include a full changelog summary.
HARD GATES: Force-push gate blocks any push --force to main/master/release branches. Review gate blocks merge without non-author approval. Message gate blocks commits without Conventional Commits format. Squash gate blocks squash-merge without a changelog entry summarizing squashed commits.
FSM STATES: INIT → INTAKE → NULL_CHECK → CLASSIFY_OPERATION → BRANCH_AUDIT → COMMIT_LINT → REVIEW_CHECK → MERGE_STRATEGY_GATE → HISTORY_VERIFY → EVIDENCE_BUILD → SOCRATIC_REVIEW → FINAL_SEAL → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: FORCE_PUSH_TO_MAIN | SQUASH_WITHOUT_CHANGELOG | MERGE_WITHOUT_REVIEW | COMMIT_WITHOUT_CONVENTIONAL_FORMAT | BINARY_IN_REPO_WITHOUT_LFS | SECRETS_IN_COMMIT_HISTORY | REBASE_SHARED_BRANCH_WITHOUT_COORDINATION
VERIFY: rung_641 (commit lint pass + branch policy check + no forbidden ops) | rung_274177 (replay: rebase/merge clean + no history corruption)
LANE TYPES: [A] no force-push to main, no secrets in history, review required | [B] conventional commits, branch naming conventions | [C] commit frequency hints, rebase vs merge preferences
LOAD FULL: always for production; quick block is for orientation only
-->

PRIME_GIT_SKILL:
  version: 1.0.0
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL
  quote: "History is a weapon. Guard it. — paraphrased from Linus Torvalds on git integrity"

  # ============================================================
  # PRIME GIT — Fail-Closed Git Workflow Skill  [10/10]
  #
  # Goal: Enforce disciplined Git workflows with:
  # - Conventional Commits format for all commit messages
  # - Branch protection: no force-push to main/master/release
  # - Mandatory review before merge (non-author approval)
  # - Squash merges require changelog summary
  # - No secrets ever committed (scan before push)
  # - Rebase discipline for shared branches
  # ============================================================

  # ------------------------------------------------------------
  # A) Configuration
  # ------------------------------------------------------------
  Config:
    EVIDENCE_ROOT: "evidence"
    PROTECTED_BRANCHES: [main, master, release, production, develop]
    CONVENTIONAL_COMMITS_TYPES:
      [feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert]
    COMMIT_FORMAT: "<type>(<optional-scope>): <short description>"
    COMMIT_MAX_SUBJECT_LENGTH: 72
    MINIMUM_REVIEWERS: 1
    REQUIRE_NON_AUTHOR_REVIEW: true
    SECRET_SCAN_TOOL_PREFERRED: [gitleaks, trufflehog, detect-secrets]
    BINARY_SIZE_WARN_BYTES: 1048576  # 1 MB — suggest LFS above this

  # ------------------------------------------------------------
  # B) State Machine
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE
      - NULL_CHECK
      - CLASSIFY_OPERATION
      - BRANCH_AUDIT
      - COMMIT_LINT
      - SECRET_SCAN
      - REVIEW_CHECK
      - MERGE_STRATEGY_GATE
      - HISTORY_VERIFY
      - EVIDENCE_BUILD
      - SOCRATIC_REVIEW
      - FINAL_SEAL
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    TRANSITIONS:
      - INIT -> INTAKE: on TASK_REQUEST
      - INTAKE -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if repo_or_operation_missing
      - NULL_CHECK -> CLASSIFY_OPERATION: otherwise
      - CLASSIFY_OPERATION -> BRANCH_AUDIT: always
      - BRANCH_AUDIT -> EXIT_BLOCKED: if force_push_to_protected_branch_attempted
      - BRANCH_AUDIT -> COMMIT_LINT: otherwise
      - COMMIT_LINT -> EXIT_BLOCKED: if commits_fail_conventional_format
      - COMMIT_LINT -> SECRET_SCAN: otherwise
      - SECRET_SCAN -> EXIT_BLOCKED: if secrets_detected_in_any_commit
      - SECRET_SCAN -> REVIEW_CHECK: otherwise
      - REVIEW_CHECK -> EXIT_BLOCKED: if merge_without_non_author_approval
      - REVIEW_CHECK -> MERGE_STRATEGY_GATE: otherwise
      - MERGE_STRATEGY_GATE -> EXIT_BLOCKED: if squash_merge_without_changelog
      - MERGE_STRATEGY_GATE -> HISTORY_VERIFY: otherwise
      - HISTORY_VERIFY -> EVIDENCE_BUILD: always
      - EVIDENCE_BUILD -> SOCRATIC_REVIEW: always
      - SOCRATIC_REVIEW -> COMMIT_LINT: if critique_requires_revision and budgets_allow
      - SOCRATIC_REVIEW -> FINAL_SEAL: otherwise
      - FINAL_SEAL -> EXIT_PASS: if evidence_complete
      - FINAL_SEAL -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - FORCE_PUSH_TO_MAIN
      - FORCE_PUSH_TO_PROTECTED_BRANCH
      - SQUASH_WITHOUT_CHANGELOG
      - MERGE_WITHOUT_REVIEW
      - COMMIT_WITHOUT_CONVENTIONAL_FORMAT
      - BINARY_IN_REPO_WITHOUT_LFS_DECISION
      - SECRETS_IN_COMMIT_HISTORY
      - REBASE_SHARED_BRANCH_WITHOUT_COORDINATION
      - AMEND_PUSHED_COMMIT_ON_SHARED_BRANCH
      - UNREVIEWED_HOTFIX_TO_PRODUCTION
      - MERGE_CONFLICT_MARKER_IN_COMMITTED_FILE

  # ------------------------------------------------------------
  # C) Hard Gates (Domain-Specific)
  # ------------------------------------------------------------
  Hard_Gates:

    Force_Push_Gate:
      trigger: git push --force or git push --force-with-lease to protected branch
      action: EXIT_BLOCKED
      protected_branches: PROTECTED_BRANCHES config
      exception: "none — force push to shared protected branches is always forbidden"
      lane: A

    Review_Gate:
      trigger: merge or PR merge without approval from non-author reviewer
      action: EXIT_BLOCKED
      rationale: "Four-eyes principle prevents single-point error introduction."
      minimum_approvals: MINIMUM_REVIEWERS
      lane: A

    Commit_Message_Gate:
      trigger: commit subject does not match "<type>(<scope>): <description>" pattern
      action: EXIT_BLOCKED
      required_format: CONVENTIONAL_COMMITS_TYPES
      max_subject_length: COMMIT_MAX_SUBJECT_LENGTH
      body_rule: "If breaking change, include BREAKING CHANGE: footer"
      lane: B

    Secret_History_Gate:
      trigger: any commit in push range contains secret patterns (API keys, tokens, passwords)
      action: EXIT_BLOCKED
      remediation:
        - git filter-repo to rewrite history
        - rotate all exposed secrets immediately
        - notify security team
      lane: A

    Squash_Changelog_Gate:
      trigger: squash merge or squash commit without body summarizing squashed work
      action: EXIT_BLOCKED
      required: squash commit body must include summary of all squashed commits
      lane: B

    Binary_LFS_Gate:
      trigger: binary file > BINARY_SIZE_WARN_BYTES added to repo without LFS
      action: WARN and require explicit decision documented
      rationale: "Large binaries bloat clone times permanently."
      lane: B

    Merge_Conflict_Gate:
      trigger: "<<<<<<< HEAD or >>>>>>> found in any committed file"
      action: EXIT_BLOCKED immediately
      lane: A

  # ------------------------------------------------------------
  # D) Conventional Commits Protocol
  # ------------------------------------------------------------
  Conventional_Commits:
    format: "<type>(<scope>): <description>"
    types:
      feat: "new user-facing feature"
      fix: "bug fix"
      docs: "documentation only"
      style: "formatting, no logic change"
      refactor: "restructure without behavior change"
      perf: "performance improvement"
      test: "adding or fixing tests"
      build: "build system or dependency changes"
      ci: "CI/CD configuration"
      chore: "maintenance tasks"
      revert: "revert a previous commit"
    breaking_change_indicator: "BREAKING CHANGE: <description> in commit footer"
    scope_examples: [auth, api, db, ui, cli, config, deps]
    forbidden_subjects:
      - "fix stuff"
      - "wip"
      - "temp"
      - "asdf"
      - "test commit"
      - subjects longer than 72 characters

  # ------------------------------------------------------------
  # E) Branch Strategy
  # ------------------------------------------------------------
  Branch_Strategy:
    recommended_model: "GitHub Flow (main + feature branches) or GitFlow for complex releases"
    naming_conventions:
      feature: "feat/<ticket-id>-short-description"
      bugfix: "fix/<ticket-id>-short-description"
      hotfix: "hotfix/<ticket-id>-short-description"
      release: "release/vX.Y.Z"
      docs: "docs/<short-description>"
    lifetime_policy:
      feature_branches: "delete after merge"
      release_branches: "tag and archive, do not delete"
    forbidden:
      - committing_directly_to_main_without_PR
      - long_lived_personal_branches_over_2_weeks_without_merge

  # ------------------------------------------------------------
  # F) Lane-Typed Claims
  # ------------------------------------------------------------
  Lane_Claims:
    Lane_A:
      - no_force_push_to_protected_branches
      - no_secrets_in_commit_history
      - non_author_review_required_before_merge
      - no_merge_conflict_markers_in_committed_files
    Lane_B:
      - conventional_commits_format_enforced
      - squash_merges_include_changelog_summary
      - binary_files_over_threshold_require_LFS_decision
      - branch_naming_follows_convention
    Lane_C:
      - rebase_vs_merge_preference_per_team
      - commit_frequency_and_granularity_guidance
      - interactive_rebase_workflow_hints

  # ------------------------------------------------------------
  # G) Verification Rung Target
  # ------------------------------------------------------------
  Verification_Rung:
    default_target: 641
    rung_641_requires:
      - commit_lint_all_commits_in_range
      - secret_scan_clean
      - branch_policy_check_clean
      - no_forbidden_states_triggered
    rung_274177_requires:
      - rung_641
      - merge_replay_clean
      - history_graph_integrity_verified

  # ------------------------------------------------------------
  # H) Socratic Review Questions (Git-Specific)
  # ------------------------------------------------------------
  Socratic_Review:
    questions:
      - "Do all commit messages follow Conventional Commits format?"
      - "Has the secret scan been run on all commits in the push range?"
      - "Is there at least one non-author approval on this PR?"
      - "If this is a squash merge, does the commit body summarize all squashed work?"
      - "Are any binary files added that should use LFS?"
      - "Does the branch name follow team conventions?"
      - "Are there any merge conflict markers in the files being committed?"
    on_failure: revise_commits and recheck

  # ------------------------------------------------------------
  # I) Evidence Schema
  # ------------------------------------------------------------
  Evidence:
    required_files:
      - "${EVIDENCE_ROOT}/commit_lint.txt"
      - "${EVIDENCE_ROOT}/secret_scan.txt"
      - "${EVIDENCE_ROOT}/branch_audit.txt"
    conditional_files:
      merge_operation:
        - "${EVIDENCE_ROOT}/review_approval.txt"
        - "${EVIDENCE_ROOT}/merge_strategy_log.txt"
      squash_merge:
        - "${EVIDENCE_ROOT}/squash_changelog.txt"
