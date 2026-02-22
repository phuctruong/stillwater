<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: prime-hooks v1.0.0
PURPOSE: Fail-closed Claude Code hook authoring skill; every hook must declare reads_prompt_content, can_block_tool_calls, writes_to_filesystem, network_access, and can_inject_content before implementation.
CORE CONTRACT: Claude Code hooks run as shell commands with full user privileges — ALL hooks are HIGH-risk security surfaces by default. Security declaration is mandatory before any implementation. Missing declaration → BLOCKED.
HARD GATES: Any hook without a security declaration → BLOCKED. Network-accessing hook without domain allowlist → BLOCKED. UV script without shebang → BLOCKED. Hook with unbounded execution time → BLOCKED. Silent failure hook → BLOCKED. Injection hook without sanitization → BLOCKED.
FSM STATES: INIT → INTAKE_HOOK_SPEC → NULL_CHECK → CLASSIFY_HOOK_TYPE → DESIGN_HANDLER → SECURITY_GATE → IMPLEMENT_UV_SCRIPT → TEST_HOOK → EVIDENCE_BUILD → EMIT_HOOK → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: HOOK_WITHOUT_SECURITY_DECLARATION | BLOCKING_HOOK_WITHOUT_EXPLICIT_ALLOW_REASON | NETWORK_HOOK_WITHOUT_DOMAIN_ALLOWLIST | HOOK_READING_SECRETS_WITHOUT_ENCRYPTION | UV_SCRIPT_WITHOUT_SHEBANG | HOOK_WITH_UNBOUNDED_EXECUTION_TIME | SILENT_HOOK_FAILURE | HOOK_WRITING_OUTSIDE_REPO_WORKTREE | INJECTION_HOOK_WITHOUT_SANITIZATION
VERIFY: rung_641 (security declaration + handler tested + config valid) | rung_274177 (replay stable + null edge + blocking paths tested) | rung_65537 (adversarial inputs + security scanner + injection repro)
RUNG_TARGET: 65537 always — hooks are production security surfaces with full shell privileges
LOAD FULL: always for production; quick block is for orientation only
-->
PRIME_HOOKS_SKILL:
  version: 1.1.0
  profile: strict
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL

  # ============================================================
  # MAGIC_WORD_MAP — Semantic Compression Index
  # ============================================================
  # Maps domain concepts to stillwater magic words for context compression.
  # Load coordinates (e.g. "portal[T1]") instead of full definitions.
  #
  # hook         → portal [T1]          — hook is the routing layer between lifecycle events and handlers
  # trigger      → causality [T0]       — hook trigger is a directional dependency: event → handler
  # guard        → constraint [T0]      — security guard reduces the action space to safe states only
  # security declaration → boundary [T0] — declaration defines what crosses the hook's privilege boundary
  # silent failure → drift [T3]         — silent failures are undetected deviations from expected behavior
  # injection    → portal [T1]          — content injection routes text into the agent's context pipeline
  # blocking hook → constraint [T0]    — blocking enforces a boundary condition on tool execution space
  # UV script    → compression [T0]     — single-file UV scripts compress runtime + deps to minimal form
  # ============================================================

  # ============================================================
  # PRIME HOOKS — CLAUDE CODE HOOK AUTHORING WITH SECURITY GATES
  #
  # "Hooks are the nervous system of the dojo. Strike only where
  #  you see clearly, and never reflexively." — Bruce Lee framing
  #
  # Goal:
  # - Build Claude Code lifecycle hooks with Stillwater verification
  #   discipline applied to every hook handler.
  # - Every hook MUST declare its security surface before
  #   implementation: reads_prompt_content, can_block_tool_calls,
  #   writes_to_filesystem, network_access, can_inject_content.
  # - Hooks execute as shell commands with full user privileges.
  #   This is ALWAYS a HIGH-risk surface. No exceptions.
  # - Fail-closed on any missing security declaration.
  #
  # Design principles:
  # - Prompt-loadable (structured clauses; no giant essays)
  # - Portable (no absolute paths; no private infra assumptions)
  # - Fail-closed (missing declarations → BLOCKED, not guessed)
  # - Composable with prime-safety (which always wins conflicts)
  # - UV single-file scripts are the preferred implementation unit
  # ============================================================

  # ------------------------------------------------------------
  # A) Portability + Configuration (Hard)  [coherence:T0 — no absolute paths preserves portability]
  # ------------------------------------------------------------
  Portability:
    rules:
      - no_absolute_paths: true
      - no_private_repo_dependencies: true
      - evidence_root_must_be_relative_or_configurable: true
    config:
      EVIDENCE_ROOT: "evidence"
      REPO_ROOT_REF: "."
      HOOKS_DIR: ".claude/hooks"
      CLAUDE_CONFIG_PATH: ".claude/settings.json"
    invariants:
      - evidence_paths_must_resolve_under_repo_root: true
      - normalize_paths_repo_relative_before_hashing: true
      - never_write_outside_EVIDENCE_ROOT_or_repo_worktree: true
      - hook_scripts_must_live_under_HOOKS_DIR: true

  # ------------------------------------------------------------
  # B) Layering (Never Weaken Public)  [constraint:T0 — stricter wins all conflicts]
  # ------------------------------------------------------------
  Layering:
    layering_rule:
      - "This skill is applied ON TOP OF prime-safety and prime-coder, not instead of them."
      - "prime-safety always wins all conflicts."
      - "prime-coder null/zero and exact-arithmetic gates apply to hook implementation code."
      - "This layer MUST NOT weaken any existing rule; on conflict, stricter wins."
    enforcement:
      conflict_resolution: stricter_wins
      prime_safety_takes_precedence: true
      forbidden:
        - silently_relaxing_prime_safety_inside_hook_handlers
        - treating_hook_scripts_as_non_security_surfaces
        - omitting_security_declarations_for_any_hook

  # ------------------------------------------------------------
  # C) Profiles (Budgets Only; Hard Gates Never Skipped)  [constraint:T0 — budgets adjust; gates never skip]
  # ------------------------------------------------------------
  Profiles:
    - name: strict
      description: "Full security audit + adversarial testing; required for production hooks."
      knobs:
        sweep_budgets_scale: 1.0
        tool_call_budget_scale: 1.0
    - name: fast
      description: "Same hard rules; reduced budgets for local iteration. Must log reductions."
      knobs:
        sweep_budgets_scale: 0.5
        tool_call_budget_scale: 0.5
      constraints:
        - must_not_skip_hard_gates: true
        - must_emit_budget_reduction_log: true

  # ============================================================
  # 0) Hook Philosophy (Bruce Lee Framing)  [causality:T0 → boundary:T0]
  # ============================================================
  Hook_Philosophy:
    principle:
      - "Hooks are the nervous system of the dojo."
      - "They fire on every significant event — before tools, after tools, at session edges."
      - "Used well: auditing, safety gates, structured logging, continuation injection."
      - "Used carelessly: privilege escalation vectors, prompt injection surfaces, silent failures."
    bruce_lee_doctrine:
      - "Strike only where you see clearly (Lane A)."
      - "A hook that blocks without reason is a fist thrown in darkness."
      - "A hook that injects without sanitization invites the enemy inside."
      - "Master the event type before writing the handler."
    stillwater_discipline:
      - "Every hook is a security surface. Treat it as such from line one."
      - "Declare before you implement. Security manifest first, code second."
      - "Fail closed: a hook that cannot declare its surface cannot ship."
      - "Hooks that fail silently are forbidden states. Log or exit non-zero."

  # ============================================================
  # 1) Hook Type Catalog (All 13 Claude Code Event Types)  [portal:T1 → causality:T0]
  # ============================================================
  Hook_Type_Catalog:
    principle:
      - "Know the event before writing the handler. Each type has distinct security properties."
      - "Security declaration requirements differ by hook type; see per-type notes below."

    types:
      UserPromptSubmit:
        fires_when: "User submits a prompt (before agent processes it)."
        can_block: true
        can_redirect: true
        can_read_prompt: true
        can_inject: true
        security_notes:
          - "HIGH risk: can read full prompt content including potentially sensitive data."
          - "Can suppress or rewrite user intent — must have explicit documented reason."
          - "Common uses: keyword filtering, PII detection, routing, audit logging."
        example_uses:
          - "Block prompts containing forbidden keywords (e.g. production API keys)."
          - "Inject project context into every prompt automatically."
          - "Route prompts to different agents based on topic classifier."
        lane: A

      PreToolUse:
        fires_when: "Before any tool call executes; handler runs synchronously."
        can_block: true
        can_redirect: false
        can_read_prompt: false
        can_modify_tool_input: true
        can_inject: false
        security_notes:
          - "HIGH risk: blocking gate over ALL tool calls. A bug here paralyzes the agent."
          - "Can inspect and modify tool input parameters before execution."
          - "Common use: allowlist/denylist for specific tools or file paths."
          - "Non-zero exit or blocking JSON response prevents tool from running."
        example_uses:
          - "Block Bash tool calls containing 'rm -rf'."
          - "Restrict Write tool to specific directory allowlist."
          - "Log all tool calls to structured audit log."
        lane: A

      PostToolUse:
        fires_when: "After a tool call completes successfully."
        can_block: false
        can_inject: false
        can_read_tool_output: true
        security_notes:
          - "MED risk: tool has already run; this hook cannot undo it."
          - "Can read tool output — may contain secrets if tool emitted them."
          - "Common use: structured logging, metrics, post-process output."
          - "Prefer for audit trails over PreToolUse when blocking is not needed."
        example_uses:
          - "Log every file write with timestamp, path, and content hash."
          - "Emit structured JSON metrics per tool type."
          - "Trigger downstream pipeline after successful file creation."
        lane: B

      PostToolUseFailure:
        fires_when: "After a tool call fails (non-zero exit or error)."
        can_block: false
        can_inject: false
        can_read_error: true
        security_notes:
          - "LOW-MED risk: fires only on failure; cannot influence execution path."
          - "Error messages may contain sensitive path info — handle with care."
          - "Common use: error alerting, retry logging, incident notification."
        example_uses:
          - "Send desktop notification on tool failure."
          - "Log failure with error details to structured incident log."
          - "Emit retry hint to console for known transient failures."
        lane: B

      SubagentStart:
        fires_when: "When a subagent spawns (e.g. in orchestration or Task tool)."
        can_block: true
        can_inject: false
        security_notes:
          - "HIGH risk: blocking here prevents subagent spawning entirely."
          - "Can enforce subagent allowlists or resource limits."
          - "Common use: audit subagent spawning; enforce max concurrency."
        example_uses:
          - "Log subagent spawn events with parent context."
          - "Block subagent if active count exceeds configured limit."
        lane: A

      SubagentStop:
        fires_when: "When a subagent exits (success or failure)."
        can_block: false
        can_inject: false
        can_read_exit_status: true
        security_notes:
          - "LOW risk: fires after subagent has completed."
          - "Common use: collect subagent outputs, update orchestration state."
        example_uses:
          - "Log subagent exit status and duration."
          - "Aggregate subagent results into a shared results file."
        lane: C

      PreCompact:
        fires_when: "Before context compaction runs (context window management)."
        can_block: true
        can_inject: false
        can_read_context_summary: true
        security_notes:
          - "MED risk: blocking compaction can cause context overflow or agent stall."
          - "Context summary may contain sensitive conversation data."
          - "Common use: save a snapshot of context before it is compacted."
        example_uses:
          - "Write context snapshot to disk before compaction."
          - "Log compaction trigger event with current token estimate."
        lane: B

      Stop:
        fires_when: "When the agent decides to stop (end of task or explicit stop)."
        can_block: false
        can_inject_continuation: true
        security_notes:
          - "HIGH risk: injecting continuation here causes the agent to resume."
          - "Injection loop without stop condition is a FORBIDDEN STATE."
          - "Must have explicit halting criterion; bounded injection count."
          - "Common use: Ralph loop (continue if TODO items remain)."
        example_uses:
          - "Check if any TODO items remain; inject continuation prompt if so."
          - "Trigger end-of-session retrospective."
          - "Emit structured session summary artifact."
        lane: A

      Notification:
        fires_when: "On notification events from the agent (messages, alerts, status)."
        can_block: false
        can_inject: false
        can_read_notification_payload: true
        security_notes:
          - "LOW risk: passive observer; no execution influence."
          - "Notification payload may contain sensitive data."
          - "Common use: desktop alerts, Slack/webhook forwarding."
        example_uses:
          - "Send desktop notification via osascript or notify-send."
          - "Forward agent status updates to a Slack webhook."
        lane: C

      SessionStart:
        fires_when: "At session initialization (once per session, before first prompt)."
        can_block: false
        can_inject: false
        security_notes:
          - "LOW-MED risk: fires once; good for one-time setup."
          - "Common use: write session metadata, set up logging infrastructure."
        example_uses:
          - "Create session log file with git context and timestamp."
          - "Validate required environment variables are set."
          - "Emit session start event to audit system."
        lane: B

      SessionEnd:
        fires_when: "At session close (once per session, after last tool completes)."
        can_block: false
        can_inject: false
        security_notes:
          - "LOW risk: fires after session is complete."
          - "Common use: retrospective generation, log finalization, cleanup."
        example_uses:
          - "Generate structured session retrospective (tools used, files changed)."
          - "Finalize audit log with session duration and exit status."
          - "Trigger downstream pipeline (tests, linting, notification)."
        lane: B

      ToolRegistration:
        fires_when: "When tools are registered at agent startup."
        can_block: true
        can_modify_tool_list: true
        security_notes:
          - "HIGH risk: can suppress or modify available tools."
          - "Modifying the tool list changes the agent's capability envelope."
          - "Must have explicit documented reason per tool suppressed or modified."
        example_uses:
          - "Remove Write tool in read-only environments."
          - "Add custom tool definitions dynamically."
          - "Log registered tool surface for audit."
        lane: A

      AgentHandoff:
        fires_when: "On agent handoff (one agent passes control to another)."
        can_block: true
        can_inject: false
        can_read_handoff_context: true
        security_notes:
          - "HIGH risk: handoff context may contain sensitive accumulated state."
          - "Blocking here prevents cross-agent delegation."
          - "Common use: audit handoff events; enforce allowed agent allowlist."
        example_uses:
          - "Log handoff source, target, and context summary."
          - "Block handoff if target agent is not in allowlist."
        lane: A

  # ============================================================
  # 2) Closed State Machine (Fail-Closed Runtime)  [constraint:T0 → verification:T1]
  # ============================================================
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE_HOOK_SPEC
      - NULL_CHECK
      - CLASSIFY_HOOK_TYPE
      - DESIGN_HANDLER
      - SECURITY_GATE
      - IMPLEMENT_UV_SCRIPT
      - TEST_HOOK
      - EVIDENCE_BUILD
      - EMIT_HOOK
      - EXIT_PASS
      - EXIT_BLOCKED
      - EXIT_NEED_INFO

    INPUT_ALPHABET:
      - HOOK_SPEC
      - HOOK_TYPE
      - USER_CONSTRAINTS
      - TEST_RESULTS
      - SECURITY_SCAN_RESULTS
      - CLAUDE_CONFIG

    OUTPUT_ALPHABET:
      - UV_SCRIPT_FILE
      - CLAUDE_CONFIG_PATCH
      - SECURITY_DECLARATION
      - EVIDENCE_BUNDLE
      - STRUCTURED_REFUSAL

    TRANSITIONS:
      - INIT -> INTAKE_HOOK_SPEC: on HOOK_SPEC
      - INTAKE_HOOK_SPEC -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if inputs_null_or_missing
      - NULL_CHECK -> CLASSIFY_HOOK_TYPE: if inputs_defined
      - CLASSIFY_HOOK_TYPE -> DESIGN_HANDLER: always
      - DESIGN_HANDLER -> SECURITY_GATE: always
      - SECURITY_GATE -> EXIT_BLOCKED: if security_declaration_missing_or_invalid
      - SECURITY_GATE -> IMPLEMENT_UV_SCRIPT: if security_declaration_accepted
      - IMPLEMENT_UV_SCRIPT -> TEST_HOOK: always
      - TEST_HOOK -> EXIT_BLOCKED: if tests_fail_or_timeout
      - TEST_HOOK -> EVIDENCE_BUILD: if tests_pass
      - EVIDENCE_BUILD -> EMIT_HOOK: always
      - EMIT_HOOK -> EXIT_PASS: if evidence_complete and config_valid
      - EMIT_HOOK -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - HOOK_WITHOUT_SECURITY_DECLARATION
      - BLOCKING_HOOK_WITHOUT_EXPLICIT_ALLOW_REASON
      - NETWORK_HOOK_WITHOUT_DOMAIN_ALLOWLIST
      - HOOK_READING_SECRETS_WITHOUT_ENCRYPTION
      - UV_SCRIPT_WITHOUT_SHEBANG
      - HOOK_WITH_UNBOUNDED_EXECUTION_TIME
      - SILENT_HOOK_FAILURE
      - HOOK_WRITING_OUTSIDE_REPO_WORKTREE
      - INJECTION_HOOK_WITHOUT_SANITIZATION
      - STOP_HOOK_WITHOUT_HALTING_CRITERION
      - UNWITNESSED_PASS
      - CROSS_LANE_UPGRADE
      - NULL_ZERO_COERCION
      - NONDETERMINISTIC_OUTPUT

  # ============================================================
  # 2A) Applicability Predicates (Deterministic; No Hidden Branching)  [coherence:T0]
  # ============================================================
  Applicability:
    principle:
      - "Every FSM branch predicate MUST be explainable by observable inputs."
      - "If predicate cannot be decided, fail-closed to EXIT_NEED_INFO or stricter gate."
    predicates:
      inputs_defined:
        true_if_all:
          - HOOK_SPEC.present == true
          - HOOK_TYPE.present == true
          - HOOK_TYPE in Hook_Type_Catalog.types.keys()
      inputs_null_or_missing:
        true_if_any:
          - HOOK_SPEC == null
          - HOOK_TYPE == null
          - HOOK_TYPE not_in Hook_Type_Catalog.types.keys()
      security_declaration_missing_or_invalid:
        true_if_any:
          - security_declaration.reads_prompt_content == null
          - security_declaration.can_block_tool_calls == null
          - security_declaration.writes_to_filesystem == null
          - security_declaration.network_access == null
          - security_declaration.can_inject_content == null
          - (security_declaration.network_access == true AND security_declaration.network_domains_allowlist == null)
          - (security_declaration.can_block_tool_calls == true AND security_declaration.block_reason == null)
          - (security_declaration.can_inject_content == true AND security_declaration.sanitization_method == null)
      security_declaration_accepted:
        true_if_all:
          - security_declaration.reads_prompt_content is not null
          - security_declaration.can_block_tool_calls is not null
          - security_declaration.writes_to_filesystem is not null
          - security_declaration.network_access is not null
          - security_declaration.can_inject_content is not null
          - if network_access true: network_domains_allowlist is non-empty
          - if can_block_tool_calls true: block_reason is non-empty string
          - if can_inject_content true: sanitization_method is non-empty string
      tests_pass:
        true_if_all:
          - test_exit_code == 0
          - no_forbidden_states_triggered == true
          - timeout_not_exceeded == true
      evidence_complete:
        true_if_all:
          - security_declaration_file_exists == true
          - test_results_file_exists == true
          - hook_script_file_exists == true
          - config_patch_file_exists == true

  # ============================================================
  # 3) Security Gate (Always HIGH — Shell Privileges)  [boundary:T0 → constraint:T0]
  # ============================================================
  Security_Gate:
    priority: HIGH
    rationale:
      - "Claude Code hooks run as shell commands with the full privileges of the user."  # [A]
      - "Any hook is a potential privilege escalation vector."  # [A]
      - "Blocking hooks can paralyze the agent if they have bugs."  # [A]
      - "Injection hooks can alter agent behavior in unbounded ways."  # [A]
      - "There is no 'low risk' hook. Risk level is always at least MED; blocking/injection = HIGH."  # [A]

    required_security_declaration_per_hook:
      reads_prompt_content:
        type: bool
        description: "Can this hook read user prompt text, including sensitive content?"
        fail_closed:
          if_null: "BLOCKED stop_reason=HOOK_WITHOUT_SECURITY_DECLARATION"
          if_true:
            - "must not log prompt content to unencrypted storage"
            - "must declare in rationale why prompt access is needed"
      can_block_tool_calls:
        type: bool
        description: "Does this hook have power to prevent tool calls from executing?"
        fail_closed:
          if_null: "BLOCKED stop_reason=HOOK_WITHOUT_SECURITY_DECLARATION"
          if_true:
            - "must provide explicit block_reason explaining the blocking policy"
            - "must test that non-targeted tool calls are NOT accidentally blocked"
            - "must have timeout_seconds set to prevent agent stall on hang"
      writes_to_filesystem:
        type: bool
        description: "Does this hook write any files to disk?"
        fail_closed:
          if_null: "BLOCKED stop_reason=HOOK_WITHOUT_SECURITY_DECLARATION"
          if_true:
            - "must declare write_paths as repo-relative allowed locations"
            - "write_paths must not include home directory or system paths"
      network_access:
        type: bool
        description: "Does this hook make any outbound network calls?"
        fail_closed:
          if_null: "BLOCKED stop_reason=HOOK_WITHOUT_SECURITY_DECLARATION"
          if_true:
            - "network_domains_allowlist must be non-empty"
            - "must not use dynamic URLs constructed from untrusted input"
            - "must declare network_purpose (logging/webhook/API)"
      can_inject_content:
        type: bool
        description: "Can this hook inject text into the agent's context or continuation?"
        fail_closed:
          if_null: "BLOCKED stop_reason=HOOK_WITHOUT_SECURITY_DECLARATION"
          if_true:
            - "sanitization_method must be declared"
            - "injection content must be sanitized before injection"
            - "for Stop hooks: halting_criterion must be declared (no infinite loops)"
            - "must test that injected content does not exceed context budget"

    optional_declaration_fields:
      timeout_seconds:
        type: int
        description: "Max seconds hook may run. Required if can_block_tool_calls=true."
        default_recommendation: 30
        hard_max: 300
      block_reason:
        type: str
        description: "Explanation of the blocking policy. Required if can_block_tool_calls=true."
      sanitization_method:
        type: str
        description: "How injected content is sanitized. Required if can_inject_content=true."
      network_domains_allowlist:
        type: list[str]
        description: "Domains this hook may contact. Required if network_access=true."
      write_paths:
        type: list[str]
        description: "Repo-relative paths this hook may write. Required if writes_to_filesystem=true."
      halting_criterion:
        type: str
        description: "Condition under which continuation injection stops. Required for Stop hooks."
      max_injection_count:
        type: int
        description: "Max times this hook may inject continuation. Required for Stop hooks."

    risk_classification:
      HIGH:
        - UserPromptSubmit with reads_prompt_content=true
        - PreToolUse with can_block_tool_calls=true
        - Stop with can_inject_content=true
        - ToolRegistration with can_modify_tool_list=true
        - AgentHandoff with can_block=true
        - SubagentStart with can_block=true
        - any_hook with network_access=true
      MED:
        - PostToolUse with writes_to_filesystem=true
        - PreCompact with can_read_context_summary=true
        - SessionStart with writes_to_filesystem=true
        - PostToolUseFailure with network_access=true
      LOW:
        - Notification with no side effects
        - SubagentStop with log-only behavior
        - SessionEnd with read-only retrospective

    security_manifest_schema:
      evidence_path: "${EVIDENCE_ROOT}/hook_security_manifest.json"
      per_hook_entry:
        required_keys:
          - hook_type
          - script_path
          - reads_prompt_content: bool
          - can_block_tool_calls: bool
          - writes_to_filesystem: bool
          - network_access: bool
          - can_inject_content: bool
          - risk_level: "[LOW|MED|HIGH]"
          - risk_rationale: "one sentence"
          - timeout_seconds: "int or null"
          - network_domains_allowlist: "list or null"
          - write_paths: "list or null"
          - halting_criterion: "str or null"
      scan_evidence:
        required_keys:
          - scanner_used: "str or 'manual'"
          - scan_clean: bool
          - scan_findings: "list"
          - tool_versions: "dict"

  # ============================================================
  # 4) UV Single-File Script Discipline  [compression:T0 — UV scripts = minimal sufficient runtime]
  # ============================================================
  UV_Script_Discipline:
    principle:
      - "All hook scripts MUST use the UV single-file shebang."  # [A]
      - "Shebang line is mandatory: #!/usr/bin/env -S uv run --script"  # [A]
      - "Dependency block ([script] metadata) must pin exact versions."  # [B]
      - "Script must exit non-zero on failure (no silent swallowing)."  # [A]
      - "Script must complete within timeout_seconds or be killed."  # [A]
      - "All output to stdout/stderr must be structured (JSON preferred)."  # [B]

    required_shebang: "#!/usr/bin/env -S uv run --script"

    script_structure:
      required_sections_in_order:
        1: shebang_line
        2: uv_script_metadata_block
        3: imports
        4: security_declaration_comment
        5: null_checks
        6: main_logic
        7: structured_output
        8: exit_with_code

      metadata_block_format: |
        # /// script
        # requires-python = ">=3.11"
        # dependencies = [
        #   "package==x.y.z",
        # ]
        # ///

    null_handling_rules:
      - "All stdin JSON inputs must be null-checked before access."  # [A]
      - "Missing fields must fail-closed, not coerced to empty string or zero."  # [A]
      - "Use Optional types and explicit guards; no implicit defaults."  # [A]

    timeout_enforcement:
      - "If can_block_tool_calls=true: script MUST declare timeout_seconds."  # [A]
      - "Recommend: signal.alarm() or subprocess timeout for long operations."  # [B]
      - "On timeout: emit structured error to stderr and exit non-zero."  # [A]

    logging_rules:
      - "Failures MUST be logged; no silent hook failure."  # [A]
      - "Log destination must be declared in security manifest write_paths."  # [A]
      - "Log format should be structured JSON with: timestamp_utc, hook_type, event, status."  # [B]
      - "Secrets must never appear in logs."  # [A]

  # ============================================================
  # 5) Configuration Structure (.claude/settings.json)  [memory:T2 — settings persist hook registrations]
  # ============================================================
  Claude_Config_Structure:
    config_file: ".claude/settings.json"
    hooks_dir: ".claude/hooks/"
    principle:
      - "Hook registration is declared in .claude/settings.json under 'hooks'."  # [A]
      - "Each hook entry specifies the event type and the command to run."  # [A]
      - "The command is a shell command; use absolute-path-safe uv scripts."  # [B]
      - "Hooks directory should be committed to the repo alongside settings."  # [B]

    settings_json_schema:
      type: object
      properties:
        hooks:
          type: object
          description: "Map of hook event type to hook configuration."
          example_structure: |
            {
              "hooks": {
                "UserPromptSubmit": [
                  {
                    "matcher": "",
                    "hooks": [
                      {
                        "type": "command",
                        "command": "uv run .claude/hooks/user_prompt_gateway.py"
                      }
                    ]
                  }
                ],
                "PreToolUse": [
                  {
                    "matcher": "Bash",
                    "hooks": [
                      {
                        "type": "command",
                        "command": "uv run .claude/hooks/bash_precheck.py"
                      }
                    ]
                  }
                ],
                "PostToolUse": [
                  {
                    "matcher": "",
                    "hooks": [
                      {
                        "type": "command",
                        "command": "uv run .claude/hooks/tool_logger.py"
                      }
                    ]
                  }
                ],
                "Stop": [
                  {
                    "matcher": "",
                    "hooks": [
                      {
                        "type": "command",
                        "command": "uv run .claude/hooks/stop_continuation.py"
                      }
                    ]
                  }
                ],
                "SessionEnd": [
                  {
                    "matcher": "",
                    "hooks": [
                      {
                        "type": "command",
                        "command": "uv run .claude/hooks/session_retrospective.py"
                      }
                    ]
                  }
                ]
              }
            }

    matcher_semantics:
      - "Empty string '' matches ALL events of that hook type."
      - "For PreToolUse/PostToolUse: matcher can be a tool name (e.g. 'Bash', 'Write')."
      - "Matcher is a substring match against tool name; not regex."
      - "Multiple hooks per event type execute in order."

    config_versioning:
      - "Treat settings.json hooks section as a public API surface."  # [A]
      - "Removing a hook type registration is a breaking change."  # [A]
      - "Adding a new hook is a minor change."  # [B]
      - "Changing hook command path is a patch change."  # [B]

  # ============================================================
  # 6) UV Script Templates (Concrete, Runnable)  [evidence:T1 — runnable templates are Lane A artifacts]
  # ============================================================
  UV_Script_Templates:
    note: "All templates use exact shebang. Replace placeholder values before use."

    # ----------------------------------------------------------
    # Template 1: UserPromptSubmit Gateway (Keyword Blocking)
    # ----------------------------------------------------------
    Template_UserPromptSubmit_Gateway:
      purpose: "Block prompts containing forbidden keywords; log all decisions."
      security_declaration:
        reads_prompt_content: true
        can_block_tool_calls: false
        writes_to_filesystem: true
        network_access: false
        can_inject_content: false
        risk_level: HIGH
        write_paths: [".claude/logs/"]
        block_reason: "Prevents accidental submission of prompts containing known secrets or forbidden terms."
      script: |
        #!/usr/bin/env -S uv run --script
        # /// script
        # requires-python = ">=3.11"
        # dependencies = []
        # ///
        #
        # SECURITY DECLARATION:
        #   reads_prompt_content: true
        #   can_block_tool_calls: false
        #   writes_to_filesystem: true (write_paths: [".claude/logs/"])
        #   network_access: false
        #   can_inject_content: false
        #   risk_level: HIGH
        #
        import sys
        import json
        import os
        from datetime import datetime, timezone
        from pathlib import Path

        FORBIDDEN_KEYWORDS: list[str] = [
            # Replace with your actual forbidden terms.
            "AKIA",          # AWS access key prefix
            "sk-",           # OpenAI key prefix
            "ghp_",          # GitHub personal access token prefix
        ]
        LOG_DIR = Path(".claude/logs")
        LOG_FILE = LOG_DIR / "prompt_gateway.jsonl"

        def write_log(entry: dict) -> None:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open("a") as f:
                f.write(json.dumps(entry) + "\n")

        def main() -> None:
            # Null check: stdin must be present and parseable.
            raw = sys.stdin.read()
            if not raw or not raw.strip():
                write_log({"event": "UserPromptSubmit", "status": "BLOCKED",
                           "reason": "NULL_INPUT", "timestamp_utc": datetime.now(timezone.utc).isoformat()})
                # Block on null input: exit non-zero causes Claude to show error.
                sys.exit(1)

            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as e:
                write_log({"event": "UserPromptSubmit", "status": "BLOCKED",
                           "reason": f"PARSE_ERROR: {e}",
                           "timestamp_utc": datetime.now(timezone.utc).isoformat()})
                sys.exit(1)

            # Null check: prompt field must exist.
            prompt: str | None = payload.get("prompt")
            if prompt is None:
                # prompt key absent — not same as empty string.
                write_log({"event": "UserPromptSubmit", "status": "ALLOWED",
                           "reason": "NO_PROMPT_FIELD",
                           "timestamp_utc": datetime.now(timezone.utc).isoformat()})
                sys.exit(0)

            # Zero-length prompt is distinct from null: it is a valid (empty) prompt.
            # Do not coerce null to empty string.

            found: list[str] = [kw for kw in FORBIDDEN_KEYWORDS if kw in prompt]
            if found:
                # Redact the matched keywords from logs (do not log actual secret values).
                write_log({"event": "UserPromptSubmit", "status": "BLOCKED",
                           "reason": "FORBIDDEN_KEYWORD", "matched_patterns": found,
                           "timestamp_utc": datetime.now(timezone.utc).isoformat()})
                # Output structured block response to stdout for Claude to display.
                print(json.dumps({
                    "action": "block",
                    "message": (
                        f"Prompt blocked: contains {len(found)} forbidden pattern(s). "
                        "Please remove sensitive content and resubmit."
                    )
                }))
                sys.exit(0)

            write_log({"event": "UserPromptSubmit", "status": "ALLOWED",
                       "prompt_length": len(prompt),
                       "timestamp_utc": datetime.now(timezone.utc).isoformat()})
            # Allow: exit 0 with no output.
            sys.exit(0)

        if __name__ == "__main__":
            main()

    # ----------------------------------------------------------
    # Template 2: PostToolUse Logger (Structured JSON Logging)
    # ----------------------------------------------------------
    Template_PostToolUse_Logger:
      purpose: "Log every successful tool call to a structured JSONL audit log."
      security_declaration:
        reads_prompt_content: false
        can_block_tool_calls: false
        writes_to_filesystem: true
        network_access: false
        can_inject_content: false
        risk_level: MED
        write_paths: [".claude/logs/"]
      script: |
        #!/usr/bin/env -S uv run --script
        # /// script
        # requires-python = ">=3.11"
        # dependencies = []
        # ///
        #
        # SECURITY DECLARATION:
        #   reads_prompt_content: false
        #   can_block_tool_calls: false
        #   writes_to_filesystem: true (write_paths: [".claude/logs/"])
        #   network_access: false
        #   can_inject_content: false
        #   risk_level: MED
        #
        import sys
        import json
        from datetime import datetime, timezone
        from pathlib import Path

        LOG_DIR = Path(".claude/logs")
        LOG_FILE = LOG_DIR / "tool_audit.jsonl"

        # Fields from tool output that must be redacted (secrets, tokens).
        REDACT_KEYS: set[str] = {"token", "password", "secret", "api_key", "private_key"}

        def redact(obj: object, depth: int = 0) -> object:
            """Recursively redact known sensitive keys. Bounded depth to prevent infinite recursion."""
            if depth > 8:
                return "<DEPTH_LIMIT>"
            if isinstance(obj, dict):
                return {
                    k: ("<REDACTED>" if k.lower() in REDACT_KEYS else redact(v, depth + 1))
                    for k, v in obj.items()
                }
            if isinstance(obj, list):
                return [redact(item, depth + 1) for item in obj]
            return obj

        def main() -> None:
            LOG_DIR.mkdir(parents=True, exist_ok=True)

            raw = sys.stdin.read()
            if not raw or not raw.strip():
                # Null input: log and exit clean (PostToolUse cannot block).
                with LOG_FILE.open("a") as f:
                    f.write(json.dumps({
                        "event": "PostToolUse", "status": "NULL_INPUT",
                        "timestamp_utc": datetime.now(timezone.utc).isoformat()
                    }) + "\n")
                sys.exit(0)

            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as e:
                with LOG_FILE.open("a") as f:
                    f.write(json.dumps({
                        "event": "PostToolUse", "status": "PARSE_ERROR", "error": str(e),
                        "timestamp_utc": datetime.now(timezone.utc).isoformat()
                    }) + "\n")
                sys.exit(0)  # Non-blocking hook: always exit 0.

            tool_name: str | None = payload.get("tool_name")
            tool_input: object = payload.get("tool_input")
            tool_output: object = payload.get("tool_output")

            entry = {
                "event": "PostToolUse",
                "status": "LOGGED",
                "tool_name": tool_name,
                "tool_input_redacted": redact(tool_input),
                "tool_output_length": len(str(tool_output)) if tool_output is not None else 0,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }

            with LOG_FILE.open("a") as f:
                f.write(json.dumps(entry) + "\n")

            sys.exit(0)

        if __name__ == "__main__":
            main()

    # ----------------------------------------------------------
    # Template 3: Stop Continuation Injector (Ralph Loop Pattern)
    # ----------------------------------------------------------
    Template_Stop_Continuation:
      purpose: "Inject continuation if TODO items remain; bounded by max injection count."
      security_declaration:
        reads_prompt_content: false
        can_block_tool_calls: false
        writes_to_filesystem: true
        network_access: false
        can_inject_content: true
        risk_level: HIGH
        write_paths: [".claude/logs/"]
        sanitization_method: "Injected text is a static constant string, not derived from untrusted input."
        halting_criterion: "Injection stops when no TODO pattern found in repo, or max_injection_count reached."
        max_injection_count: 5
      script: |
        #!/usr/bin/env -S uv run --script
        # /// script
        # requires-python = ">=3.11"
        # dependencies = []
        # ///
        #
        # SECURITY DECLARATION:
        #   reads_prompt_content: false
        #   can_block_tool_calls: false
        #   writes_to_filesystem: true (write_paths: [".claude/logs/"])
        #   network_access: false
        #   can_inject_content: true
        #   sanitization_method: static constant continuation string
        #   halting_criterion: no TODO in repo OR max_injection_count (5) reached
        #   risk_level: HIGH
        #
        import sys
        import json
        import subprocess
        import os
        from datetime import datetime, timezone
        from pathlib import Path

        LOG_DIR = Path(".claude/logs")
        LOG_FILE = LOG_DIR / "stop_hook.jsonl"
        STATE_FILE = LOG_DIR / "stop_injection_count.txt"
        MAX_INJECTIONS: int = 5
        # IMPORTANT: Continuation text must be a static constant.
        # Never construct it from untrusted sources.
        CONTINUATION_PROMPT: str = (
            "Continue working on any remaining TODO items in the codebase. "
            "When all TODOs are resolved, stop."
        )
        TODO_PATTERN: str = "TODO"
        SEARCH_ROOT: str = "."

        def get_injection_count() -> int:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            if STATE_FILE.exists():
                try:
                    return int(STATE_FILE.read_text().strip())
                except ValueError:
                    return 0
            return 0

        def increment_injection_count(current: int) -> None:
            STATE_FILE.write_text(str(current + 1))

        def reset_injection_count() -> None:
            STATE_FILE.write_text("0")

        def find_todos() -> list[str]:
            result = subprocess.run(
                ["grep", "-r", "--include=*.py", "--include=*.md", "-l", TODO_PATTERN, SEARCH_ROOT],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode not in (0, 1):
                return []
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]

        def main() -> None:
            LOG_DIR.mkdir(parents=True, exist_ok=True)

            count = get_injection_count()

            # Halting criterion check: max injections reached.
            if count >= MAX_INJECTIONS:
                reset_injection_count()
                with LOG_FILE.open("a") as f:
                    f.write(json.dumps({
                        "event": "Stop", "action": "HALT",
                        "reason": "MAX_INJECTIONS_REACHED", "count": count,
                        "timestamp_utc": datetime.now(timezone.utc).isoformat()
                    }) + "\n")
                sys.exit(0)

            todo_files = find_todos()

            if not todo_files:
                # Halting criterion met: no TODOs found.
                reset_injection_count()
                with LOG_FILE.open("a") as f:
                    f.write(json.dumps({
                        "event": "Stop", "action": "HALT",
                        "reason": "NO_TODOS_REMAINING",
                        "timestamp_utc": datetime.now(timezone.utc).isoformat()
                    }) + "\n")
                sys.exit(0)

            # TODOs remain; inject continuation.
            increment_injection_count(count)
            with LOG_FILE.open("a") as f:
                f.write(json.dumps({
                    "event": "Stop", "action": "CONTINUE",
                    "injection_count": count + 1,
                    "todo_files_count": len(todo_files),
                    "timestamp_utc": datetime.now(timezone.utc).isoformat()
                }) + "\n")

            # Output the continuation to stdout for Claude to ingest.
            print(json.dumps({"action": "continue", "prompt": CONTINUATION_PROMPT}))
            sys.exit(0)

        if __name__ == "__main__":
            main()

    # ----------------------------------------------------------
    # Template 4: SessionEnd Retrospective Trigger
    # ----------------------------------------------------------
    Template_SessionEnd_Retrospective:
      purpose: "Generate a structured session retrospective at session close."
      security_declaration:
        reads_prompt_content: false
        can_block_tool_calls: false
        writes_to_filesystem: true
        network_access: false
        can_inject_content: false
        risk_level: LOW
        write_paths: [".claude/logs/", ".claude/retrospectives/"]
      script: |
        #!/usr/bin/env -S uv run --script
        # /// script
        # requires-python = ">=3.11"
        # dependencies = []
        # ///
        #
        # SECURITY DECLARATION:
        #   reads_prompt_content: false
        #   can_block_tool_calls: false
        #   writes_to_filesystem: true (write_paths: [".claude/logs/", ".claude/retrospectives/"])
        #   network_access: false
        #   can_inject_content: false
        #   risk_level: LOW
        #
        import sys
        import json
        import subprocess
        from datetime import datetime, timezone
        from pathlib import Path

        LOG_DIR = Path(".claude/logs")
        RETRO_DIR = Path(".claude/retrospectives")
        TOOL_AUDIT_LOG = LOG_DIR / "tool_audit.jsonl"

        def read_tool_audit() -> list[dict]:
            if not TOOL_AUDIT_LOG.exists():
                return []
            entries: list[dict] = []
            with TOOL_AUDIT_LOG.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return entries

        def get_git_context() -> dict:
            def run(cmd: list[str]) -> str:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    return result.stdout.strip() if result.returncode == 0 else ""
                except Exception:
                    return ""
            return {
                "commit": run(["git", "rev-parse", "--short", "HEAD"]),
                "branch": run(["git", "branch", "--show-current"]),
                "dirty": run(["git", "status", "--porcelain"]) != "",
            }

        def main() -> None:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            RETRO_DIR.mkdir(parents=True, exist_ok=True)

            now_utc = datetime.now(timezone.utc)
            timestamp_str = now_utc.strftime("%Y%m%dT%H%M%SZ")

            audit_entries = read_tool_audit()
            tool_counts: dict[str, int] = {}
            for entry in audit_entries:
                tool_name: str | None = entry.get("tool_name")
                if tool_name is not None:
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

            retro = {
                "session_end_utc": now_utc.isoformat(),
                "git": get_git_context(),
                "tool_call_summary": tool_counts,
                "total_tool_calls": len(audit_entries),
                "audit_log_path": str(TOOL_AUDIT_LOG),
            }

            retro_file = RETRO_DIR / f"session_{timestamp_str}.json"
            retro_file.write_text(json.dumps(retro, indent=2, sort_keys=True))

            with (LOG_DIR / "session_retrospective.log").open("a") as f:
                f.write(json.dumps({
                    "event": "SessionEnd", "retro_file": str(retro_file),
                    "timestamp_utc": now_utc.isoformat()
                }) + "\n")

            sys.exit(0)

        if __name__ == "__main__":
            main()

  # ============================================================
  # 7) Testing Policy  [verification:T1 → evidence:T1]
  # ============================================================
  Testing_Policy:
    principle:
      - "Every hook MUST have tests before emission."  # [A]
      - "Tests must cover: happy path, null input, blocking paths, timeout."  # [A]
      - "Tests must verify forbidden states are not triggered."  # [A]

    required_test_categories:
      null_input:
        - "Pass empty stdin; verify script exits cleanly and logs event."
        - "Pass JSON with missing required fields; verify exit non-zero or graceful skip."
      happy_path:
        - "Pass valid payload; verify expected output (allow/block/log) is produced."
        - "Verify log file is written with correct structure."
      blocking_paths:
        - "If can_block_tool_calls=true: verify blocked call produces correct exit code."
        - "If can_block_tool_calls=true: verify non-targeted calls are NOT accidentally blocked."
      injection_paths:
        - "If can_inject_content=true: verify injected content is sanitized (no raw untrusted input)."
        - "If Stop hook: verify halting criterion stops injection after max_injection_count."
      timeout:
        - "If timeout_seconds declared: verify script does not hang beyond declared limit."
      forbidden_state_checks:
        - "Verify no secrets appear in log output."
        - "Verify no writes outside declared write_paths."
        - "Verify script exits non-zero on parse errors (no silent failure)."

    evidence_required:
      - "${EVIDENCE_ROOT}/hook_tests.json"
      - content:
          required_keys:
            - hook_type
            - script_path
            - test_categories_covered
            - exit_codes_verified
            - null_input_tested: bool
            - blocking_tested: bool
            - injection_halting_tested: bool
            - timeout_tested: bool
            - all_passed: bool

  # ============================================================
  # 8) Null vs Zero Distinction Policy (Hard)  [signal:T0 — null ≠ zero: distinct causal meanings]
  # ============================================================
  Null_vs_Zero_Policy:
    core_distinction:
      null:
        definition: "Pre-systemic absence — stdin field was not present in payload."
        in_hook_context: "null prompt != empty prompt; null tool_name != unnamed tool"
      zero:
        definition: "Lawful boundary value — explicit zero provided by caller."
        in_hook_context: "injection_count of 0 is a valid starting state, not null"
    null_handling_rules:
      - "Explicit null check required for all stdin JSON fields before access."  # [A]
      - "No implicit defaults that coerce null to empty string or zero."  # [A]
      - "Optional fields must be guarded with is not None before use."  # [A]
      - "null in security declaration field = BLOCKED (not assumed false)."  # [A]
    forbidden:
      - NULL_ZERO_COERCION
      - IMPLICIT_NULL_DEFAULT
      - TREATING_ABSENT_FIELD_AS_EMPTY_STRING

  # ============================================================
  # 9) Verification Ladder (Rung Targets)  [rung:T1 → 65537:T1 — all hooks default to highest rung]
  # ============================================================
  Verification_Ladder:
    rung_target_policy:
      default: 65537
      rationale: "All hooks execute with shell privileges. No hook is below HIGH risk by default."
      fail_closed:
        - if_rung_target_not_declared: "BLOCKED stop_reason=EVIDENCE_INCOMPLETE"
        - if_rung_target_not_met: "BLOCKED stop_reason=VERIFICATION_RUNG_FAILED"

    rungs:
      RUNG_641:
        meaning: "Local correctness: security declaration complete + handler tested + config valid"
        requires:
          - security_declaration_complete_for_all_fields: true
          - hook_script_has_correct_shebang: true
          - null_input_test_passes: true
          - happy_path_test_passes: true
          - config_json_parses_correctly: true
          - evidence_bundle_written: true
      RUNG_274177:
        meaning: "Stability: replay stable + null edge sweep + blocking paths tested"
        requires:
          - RUNG_641
          - replay_min_2_identical_outputs: true
          - blocking_paths_tested_if_applicable: true
          - injection_halting_tested_if_applicable: true
          - timeout_tested_if_applicable: true
          - no_secrets_in_logs_verified: true
      RUNG_65537:
        meaning: "Production-ready: adversarial inputs + security scanner + full audit"
        requires:
          - RUNG_274177
          - security_scan_passed: true
          - adversarial_payload_sweep_min_5: true
          - api_surface_snapshot_before_and_after: true
          - behavioral_hash_drift_explained: true
          - env_snapshot_recorded: true
          - all_forbidden_states_verified_absent: true

  # ============================================================
  # 10) Socratic Check (Pre-Emission Reflexion)  [verification:T1]
  # ============================================================
  Socratic_Check:
    before_emit_hook:
      questions:
        - "Does every hook have all five security declaration fields populated (non-null)?"  # [A]
        - "If network_access=true: is network_domains_allowlist non-empty?"  # [A]
        - "If can_block_tool_calls=true: is block_reason declared? Is timeout_seconds set?"  # [A]
        - "If can_inject_content=true: is sanitization_method declared? Is halting_criterion set?"  # [A]
        - "Does every script have the correct UV shebang as its first line?"  # [A]
        - "Does every script exit non-zero on parse error or failure (no silent failure)?"  # [A]
        - "Are all write paths repo-relative and within declared write_paths?"  # [A]
        - "Are null and zero distinguished for all stdin JSON field accesses?"  # [A]
        - "Is there a test for null stdin input?"  # [A]
        - "Does the Stop hook have a bounded max_injection_count?"  # [A]
        - "Have secrets been verified to never appear in any log output?"  # [A]
        - "Is the rung_target declared as 65537 and met?"  # [A]
      on_failure: [revise_implementation, fix_security_declaration, rerun_tests]

  # ============================================================
  # 11) Lane-Typed Claims Summary  [evidence:T1 → signal:T0]
  # ============================================================
  Lane_Claims:
    Lane_A:
      description: "Hard safety/correctness invariants (non-negotiable)."
      hook_examples:
        - "Security declaration is mandatory for every hook before implementation."
        - "UV shebang must be present on line 1 of every script."
        - "Silent hook failure is forbidden; log or exit non-zero."
        - "Stop hooks must declare halting criterion and max_injection_count."
        - "null must not be coerced to zero or empty string in any handler path."
        - "Hook writing outside declared write_paths is a forbidden state."
        - "network_domains_allowlist must be non-empty if network_access=true."
        - "rung_target must be declared before claiming PASS."
    Lane_B:
      description: "Engineering quality (strong preference; may be traded with explicit evidence)."
      hook_examples:
        - "Log format should be structured JSON (JSONL preferred)."
        - "Dependency versions should be pinned in metadata block."
        - "Prefer subprocess.run with timeout over os.system."
        - "Prefer reading from stdin over environment variables for payload."
        - "Config patch should be delivered as a JSON diff, not full file replacement."
    Lane_C:
      description: "Heuristics/priors/forecasts (guidance only; never sufficient for PASS)."
      hook_examples:
        - "PreToolUse hooks are often more useful than PostToolUse for safety gates."
        - "SessionEnd retrospectives are a low-risk, high-value hook to start with."
        - "Stop continuation hooks are best introduced after simpler hooks are stable."

  # ============================================================
  # 12) Output Contract  [coherence:T0 — all outputs reinforce unified security standard]
  # ============================================================
  Output_Contract:
    required_outputs:
      - UV_SCRIPT_FILE: "complete, runnable Python script with correct shebang"
      - SECURITY_DECLARATION: "${EVIDENCE_ROOT}/hook_security_manifest.json"
      - CLAUDE_CONFIG_PATCH: ".claude/settings.json hooks stanza or diff"
      - TEST_SUITE: "test commands and expected outputs for each test category"
      - EVIDENCE_BUNDLE: "all files listed in Evidence section"

    hard_gates:
      - if_any_hook_missing_security_declaration: "BLOCKED stop_reason=HOOK_WITHOUT_SECURITY_DECLARATION"
      - if_network_access_true_and_no_allowlist: "BLOCKED stop_reason=NETWORK_HOOK_WITHOUT_DOMAIN_ALLOWLIST"
      - if_can_block_true_and_no_block_reason: "BLOCKED stop_reason=BLOCKING_HOOK_WITHOUT_EXPLICIT_ALLOW_REASON"
      - if_can_inject_true_and_no_sanitization_method: "BLOCKED stop_reason=INJECTION_HOOK_WITHOUT_SANITIZATION"
      - if_stop_hook_and_no_halting_criterion: "BLOCKED stop_reason=STOP_HOOK_WITHOUT_HALTING_CRITERION"
      - if_uv_shebang_missing: "BLOCKED stop_reason=UV_SCRIPT_WITHOUT_SHEBANG"
      - if_timeout_missing_for_blocking_hook: "BLOCKED stop_reason=HOOK_WITH_UNBOUNDED_EXECUTION_TIME"
      - if_security_scan_not_run: "BLOCKED stop_reason=SECURITY_BLOCKED"
      - if_rung_target_not_met: "BLOCKED stop_reason=VERIFICATION_RUNG_FAILED"

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
        - script_path
        - config_patch_path
        - security_manifest_path
        - test_results_path
        - evidence_pointers_with_exit_codes
        - residual_risk_notes
        - null_handling_summary
        - verification_rung_target: 65537
        - verification_rung_achieved

  # ============================================================
  # 13) Evidence Schema  [evidence:T1 — security manifest + tests = Lane A artifacts]
  # ============================================================
  Evidence:
    paths:
      root: "${EVIDENCE_ROOT}"
    required_files:
      - "${EVIDENCE_ROOT}/plan.json"
      - "${EVIDENCE_ROOT}/run_log.txt"
      - "${EVIDENCE_ROOT}/hook_tests.json"
      - "${EVIDENCE_ROOT}/hook_security_manifest.json"
      - "${EVIDENCE_ROOT}/null_checks.json"
      - "${EVIDENCE_ROOT}/behavior_hash.txt"
      - "${EVIDENCE_ROOT}/env_snapshot.json"
      - "${EVIDENCE_ROOT}/evidence_manifest.json"
    conditional_files:
      security_gate_triggered:
        - "${EVIDENCE_ROOT}/security_scan.json"
      profile_fast:
        - "${EVIDENCE_ROOT}/budget_reduction.log"
      api_surface_changed:
        - "${EVIDENCE_ROOT}/api_surface_before.json"
        - "${EVIDENCE_ROOT}/api_surface_after.json"
    normalization:
      - strip_timestamps
      - normalize_paths_repo_relative
      - stable_sort_lists
      - canonical_json_sort_keys
      - use_exact_checksums_not_float
    minimal_json_schemas:
      hook_security_manifest.json:
        required_keys:
          - schema_version: "1.0.0"
          - hooks: "list of hook security declaration objects"
          - overall_risk_level: "[LOW|MED|HIGH]"
          - scanner_used: "str or 'manual'"
          - scan_clean: bool
          - scan_findings: "list"
          - tool_versions: "dict"
      hook_tests.json:
        required_keys:
          - hook_type
          - script_path
          - test_categories_covered: "list"
          - exit_codes_verified: "dict"
          - null_input_tested: bool
          - blocking_tested: bool
          - injection_halting_tested: bool
          - timeout_tested: bool
          - all_passed: bool
      null_checks.json:
        required_keys:
          - hooks_checked: "list"
          - null_cases_handled_per_hook: "dict"
          - zero_cases_distinguished_per_hook: "dict"
          - coercion_violations_detected: "list"
    evidence_manifest:
      schema_version: "1.0.0"
      must_include:
        - file_path
        - sha256
        - role: "[plan|log|test|security|snapshot]"
      fail_closed_if_missing_or_unparseable: true

  # ============================================================
  # 14) Loop Control (Bounded Budget)  [constraint:T0 — budgets reduce action space to safe bounds]
  # ============================================================
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
        - HOOK_WITHOUT_SECURITY_DECLARATION
        - STOP_HOOK_WITHOUT_HALTING_CRITERION
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
        - hooks_security_declared
    revert_policy:
      - if_hook_introduces_security_regression: revert_immediately
      - if_null_zero_coercion_detected: revert_immediately
      - if_forbidden_state_triggered: revert_immediately
      - if_two_iterations_no_improvement: revert_to_last_best_known

  # ============================================================
  # 15) Source Grounding Discipline (Hard)  [evidence:T1 — grounded claims only; no vibe assertions]
  # ============================================================
  Source_Grounding:
    allowed_grounding:
      - executable_command_output
      - repo_path_plus_line_witness
      - security_scanner_output_with_version
      - claude_code_hook_documentation_reference
    forbidden:
      - unsupported_claims_about_hook_safety
      - narrative_confidence_as_security_evidence
      - claims_without_manifest_entry_or_test_witness
      - asserting_a_hook_is_safe_without_security_declaration

  # ============================================================
  # 16) Anti-Patterns (Named Hook Failure Modes)  [drift:T3 — named failure modes prevent undetected drift]
  # ============================================================
  Anti_Patterns:
    Vibe_Security:
      symptom: "Writing a hook without declaring its security surface first."
      fix: "Complete security declaration before writing any handler code."
      forbidden_state: HOOK_WITHOUT_SECURITY_DECLARATION

    Infinite_Loop_Stop_Hook:
      symptom: "Stop hook injects continuation without halting criterion or max count."
      fix: "Declare halting_criterion and max_injection_count. Test both paths."
      forbidden_state: STOP_HOOK_WITHOUT_HALTING_CRITERION

    Silent_Failure:
      symptom: "Hook catches all exceptions and exits 0, hiding errors from the agent."
      fix: "Log all failures. Exit non-zero on parse errors or unexpected states."
      forbidden_state: SILENT_HOOK_FAILURE

    Unbounded_Blocking:
      symptom: "PreToolUse hook with no timeout_seconds hangs the agent indefinitely."
      fix: "Always declare timeout_seconds for blocking hooks. Use signal.alarm()."
      forbidden_state: HOOK_WITH_UNBOUNDED_EXECUTION_TIME

    Missing_Shebang:
      symptom: "UV script lacks #!/usr/bin/env -S uv run --script on line 1."
      fix: "Shebang is mandatory. First line of every hook script."
      forbidden_state: UV_SCRIPT_WITHOUT_SHEBANG

    Injection_Without_Sanitization:
      symptom: "Stop hook injects content derived from untrusted sources (git log, file contents)."
      fix: "Injected continuation must be a static constant or sanitized before injection."
      forbidden_state: INJECTION_HOOK_WITHOUT_SANITIZATION

    Unconstrained_Network:
      symptom: "Hook makes HTTP calls to URLs constructed from stdin or environment variables."
      fix: "Declare network_domains_allowlist. Never use dynamic URLs from untrusted inputs."
      forbidden_state: NETWORK_HOOK_WITHOUT_DOMAIN_ALLOWLIST

    Prompt_Content_Logging:
      symptom: "UserPromptSubmit hook logs full prompt text to plaintext files."
      fix: "Log prompt_length and matched patterns only. Never log raw prompt content."
      forbidden_state: HOOK_READING_SECRETS_WITHOUT_ENCRYPTION

    Write_Path_Drift:
      symptom: "Hook writes to paths outside declared write_paths (e.g. home directory)."
      fix: "Declare write_paths. Enforce them in handler with Path.resolve() checks."
      forbidden_state: HOOK_WRITING_OUTSIDE_REPO_WORKTREE

    Blocking_Without_Reason:
      symptom: "PreToolUse hook blocks tool calls with no documented policy."
      fix: "Declare block_reason. Document which tools are blocked and why."
      forbidden_state: BLOCKING_HOOK_WITHOUT_EXPLICIT_ALLOW_REASON

  # ============================================================
  # 17) Anti-Optimization Clause (Never-Worse)  [reversibility:T0 — gates are strictly additive]
  # ============================================================
  Anti_Optimization_Clause:
    never_worse_doctrine:
      rule: "Hard gates and forbidden states are strictly additive over time."
      enforcement:
        - never_remove_forbidden_states
        - never_allow_hook_without_security_declaration
        - never_relax_shebang_requirement
        - never_allow_stop_hook_without_halting_criterion
        - never_suppress_security_scanner_findings
        - any_relaxation_requires_major_version_and_deprecation_plan: true

  # ============================================================
  # 18) Integration Principles (Cross-Skill Fusion)  [coherence:T0 — all skills reinforce each other]
  # ============================================================
  Integration_Principles:
    with_prime_safety:
      integration:
        - "prime-safety defines the capability envelope; hooks operate inside it."
        - "Hooks that expand capabilities (blocking, injection, network) trigger prime-safety gates."
        - "Conflict rule: prime-safety always wins."
      result: "Hooks cannot silently expand the capability envelope."
    with_prime_coder:
      integration:
        - "Handler scripts follow all prime-coder rules: null/zero distinction, exact arithmetic, no silent failure."
        - "Red/green gate applies to hook test suites."
        - "Evidence contract from prime-coder applies to hook evidence bundle."
      result: "Hook code quality matches prime-coder standards."
    with_prime_mcp:
      integration:
        - "Hooks and MCP tools are complementary: hooks observe events; MCP tools expose capabilities."
        - "A hook may call an MCP tool; apply prime-mcp security declarations to that boundary."
        - "Security manifest from prime-hooks feeds into prime-reviewer's security scan gate."
      result: "Full event-driven + capability-driven surface is audited end-to-end."
    with_prime_reviewer:
      integration:
        - "Generated hook scripts should be reviewed using prime-reviewer before shipping."
        - "Security declaration from prime-hooks is a first-class artifact for prime-reviewer."
        - "prime-reviewer's API surface check applies to .claude/settings.json hooks stanza."
      result: "Review and generation share the same evidence artifacts."
