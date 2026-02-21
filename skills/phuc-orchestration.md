# phuc-orchestration.md — Phuc Orchestration Skill

**Skill ID:** phuc-orchestration
**Version:** 1.0.0
**Authority:** 65537
**Status:** SEALED (10/10 target)
**Role:** Main-session context governor + skilled sub-agent dispatcher
**Tags:** orchestration, context-protection, dispatch, anti-rot, skill-injection, minimal-context, swarms

---

## A) Portability (Hard)

```yaml
portability:
  rules:
    - no_absolute_paths: true
    - no_private_repo_dependencies: true
    - skill_must_load_verbatim_on_any_capable_LLM: true
  config:
    EVIDENCE_ROOT: "evidence"
    REPO_ROOT_REF: "."
    SKILLS_DIR: "skills"
  invariants:
    - sub_agent_prompts_must_not_contain_host_specific_paths: true
    - skill_packs_referenced_by_relative_path_only: true
    - cnf_capsule_paths_must_be_repo_relative: true
```

## B) Layering (Never Weaken)

```yaml
layering:
  rule:
    - "This skill layers ON TOP OF prime-safety + prime-coder."
    - "On any conflict: stricter wins."
    - "phuc-orchestration adds dispatch discipline; it does not remove safety or coding gates."
  conflict_resolution: stricter_wins
  load_order:
    1: prime-safety.md         # god-skill; wins all conflicts
    2: prime-coder.md          # evidence discipline + fail-closed coding
    3: phuc-orchestration.md   # dispatch + context protection
  forbidden:
    - relaxing_prime_safety_via_orchestration_framing
    - spawning_sub_agents_without_safety_skill_in_their_pack
    - treating_sub_agent_prose_output_as_Lane_A_evidence
```

---

## 0) Core Principle

**The main session is the orchestrator. Sub-agents are the domain experts.**

Context is finite and expensive. Skill files are large (10K–60K bytes each).
Loading all skills into the main session wastes context on capabilities not needed
for the immediate task and causes context rot within ~10 turns.

Instead:
- **Main session** stays lean: `prime-safety` + `prime-coder` + `phuc-orchestration`
- **Sub-agents** receive exactly the skills they need for their role (pasted inline)
- **Artifacts** flow back to main session (JSON/diff/log — not prose summaries)
- **Context rot** is prevented by rebuilding the CNF capsule from artifacts, not memory

> "Context is scarce. Sub-agents are cheap. Load skills where they're used."

### Mechanics of Context Rot Prevention

The main session MUST:
1. **Never rely on prior hidden state** — treat each dispatch cycle as a fresh capsule
2. **Rebuild capsule from artifacts** — not from "what we discussed"
3. **Emit [COMPACTION] log** when context exceeds budget (see §5)
4. **Inject full context** into each sub-agent (no references to "earlier", "recall that")

---

## 1) Main Session Budget (Hard Limits)

```yaml
main_session_budget:
  max_always_loaded_skills: 3
    # prime-safety + prime-coder + phuc-orchestration
    # phuc-forecast may also be loaded if planning-heavy session
  max_inline_lines_before_dispatch: 100
    # If the task requires >100 lines of specialized work → dispatch
  compaction_trigger_lines: 800
    # When main context exceeds 800 lines: emit [COMPACTION] log + rebuild capsule
  compaction_log_format: "[COMPACTION] Distilled <X> lines to <Y> capsule fields."
  max_dispatch_rounds_per_task: 6
    # Bounded; if not resolved in 6 rounds: EXIT_BLOCKED, stop_reason=MAX_ITERS
```

The main session is **PERMITTED** to:
- Dispatch sub-agents with CNF capsules + skill packs
- Read skill files to construct sub-agent prompts
- Integrate artifact outputs from sub-agents
- Make coordination decisions (PASS/BLOCKED/NEED_INFO)
- Handle trivial tasks inline (<50 lines, no domain expertise needed)

The main session is **FORBIDDEN** from:
- Doing deep coding without red-green gate (dispatch to Coder with `prime-coder`)
- Doing mathematical proofs (dispatch to Mathematician with `prime-math`)
- Building Mermaid state graphs (dispatch to Graph Designer with `prime-mermaid`)
- Running multi-agent swarm design inline (dispatch to Swarm Orchestrator with `phuc-swarms`)
- Writing long-form papers (dispatch to Writer with `software5.0-paradigm`)

---

## 2) Dispatch Decision Matrix

| Task Type | Dispatch? | Agent Role | Skill Pack |
|---|---|---|---|
| Bugfix, feature, refactor | YES | Coder | `prime-safety` + `prime-coder` |
| Planning, premortem, risk analysis | YES | Planner | `prime-safety` + `phuc-forecast` |
| Mathematical proof, exact computation | YES | Mathematician | `prime-safety` + `prime-math` |
| State machine, workflow graph | YES | Graph Designer | `prime-safety` + `prime-mermaid` |
| Multi-agent swarm design/execution | YES | Swarm Orchestrator | `prime-safety` + `phuc-swarms` + `phuc-context` |
| Technical paper, book, long-form report | YES | Writer | `prime-safety` + `software5.0-paradigm` |
| Workspace cleanup, archival | YES | Janitor | `prime-safety` + `phuc-cleanup` |
| Wish contract, backlog management | YES | Wish Manager | `prime-safety` + `prime-wishes` + `prime-mermaid` |
| Adversarial review, verification | YES | Skeptic | `prime-safety` + `prime-coder` + `phuc-forecast` |
| Context-heavy multi-turn session | YES | Context Manager | `prime-safety` + `phuc-context` |
| Simple single-step (<50 lines) | NO | — | Handle inline |
| Quick lookup, trivial edit, short answer | NO | — | Handle inline |

**Dispatch threshold:** Any task requiring >100 lines of specialized reasoning → dispatch.

---

## 3) Canonical Skill Packs

```yaml
skill_packs:

  coder:
    skills: [prime-safety, prime-coder]
    model_preferred: haiku (volume) | sonnet (complex logic) | opus (promotion gate)
    rung_default: 641
    artifacts: [PATCH_DIFF, repro_red.log, repro_green.log, tests.json, evidence/plan.json]

  planner:
    skills: [prime-safety, phuc-forecast]
    model_preferred: sonnet
    rung_default: 641
    artifacts: [FORECAST_MEMO.json, DECISION_RECORD.json]

  mathematician:
    skills: [prime-safety, prime-math]
    model_preferred: sonnet | opus (olympiad/proof)
    rung_default: 274177
    artifacts: [PROOF.md, convergence.json (if iterative), halting_certificate]

  graph_designer:
    skills: [prime-safety, prime-mermaid]
    model_preferred: haiku | sonnet
    rung_default: 641
    artifacts: [state.prime-mermaid.md, state.mmd, state.sha256]

  swarm_orchestrator:
    skills: [prime-safety, phuc-swarms, phuc-context]
    model_preferred: sonnet | opus
    rung_default: 274177
    artifacts: [SWARM_PLAN.json, swarm-activity.log, per-role CNF capsules]

  writer:
    skills: [prime-safety, software5.0-paradigm, phuc-context]
    model_preferred: sonnet
    rung_default: 641
    artifacts: [DRAFT.md with typed claims [A/B/C], RECIPE.md (if extractable)]

  skeptic:
    skills: [prime-safety, prime-coder, phuc-forecast]
    model_preferred: sonnet | opus
    rung_default: 274177
    artifacts: [SKEPTIC_VERDICT.json, falsifiers_list.md]

  janitor:
    skills: [prime-safety, phuc-cleanup]
    model_preferred: haiku
    rung_default: 641
    artifacts: [cleanup-scan-{ts}.json, cleanup-apply-{ts}.json]

  wish_manager:
    skills: [prime-safety, prime-wishes, prime-mermaid]
    model_preferred: sonnet
    rung_default: 641
    artifacts: [wish.{id}.md, state.mmd, state.sha256, belt_promotion_receipt.json]

  context_manager:
    skills: [prime-safety, phuc-context]
    model_preferred: sonnet
    rung_default: 641
    artifacts: [context_capsule.json, compaction_log.txt]
```

---

## 4) Sub-Agent Prompt Template (CNF Anti-Rot)

Every sub-agent dispatch MUST follow this template.
**Paste skill file content inline** — never assume the sub-agent has loaded skills from environment.

```
You are a [ROLE] agent with persona [PERSONA].

## Loaded Skills
<BEGIN_SKILL name="prime-safety">
[PASTE full content of skills/prime-safety.md here]
</BEGIN_SKILL>

<BEGIN_SKILL name="[domain-skill]">
[PASTE full content of skills/[domain-skill].md here]
</BEGIN_SKILL>

## Task (CNF Capsule)
- task_id: [UNIQUE_ID]
- task_request: [FULL TASK TEXT — no references to "what we discussed" or "earlier"]
- constraints: [TIME/BUDGET/SCOPE/SAFETY LIMITS — explicit]
- context: [FULL CONTEXT — repo tree, error logs, failing tests, prior artifacts — no summaries]
- allowed_tools: [EXPLICIT ALLOWLIST]
- rung_target: [641 | 274177 | 65537]

## Expected Artifacts
[EXACT JSON schema of what the agent must emit]

## Stop Rules
- EXIT_PASS if: [concrete conditions]
- EXIT_BLOCKED if: [concrete conditions]
- EXIT_NEED_INFO if: [concrete conditions]
```

**Key constraint:** Never write "as discussed", "as before", "recall that we...",
"from our earlier conversation", "you know the context" in sub-agent prompts.
Every sub-agent starts fresh. Every sub-agent gets a complete CNF capsule.

---

## 5) Context Anti-Rot Protocol (Main Session)

```yaml
anti_rot_protocol:
  hard_rule: |
    Main session context MUST be rebuilt (not relied on from memory) before each dispatch round.

  rebuild_trigger:
    - main_context_exceeds_800_lines: true
    - before_each_new_dispatch_round: true
    - before_integrating_artifacts_from_multiple_agents: true

  capsule_required_fields:
    - current_task_full_text: "always include verbatim"
    - explicit_constraints: "budget, scope, safety"
    - artifacts_received:
        format: "links or inline JSON (not prose summaries)"
        rule: "artifacts are evidence; summaries are Lane C only"
    - repo_state: "git hash or tree summary"
    - prior_agent_verdicts:
        include: "PASS|BLOCKED|NEED_INFO + stop_reason"
        exclude: "agent's reasoning, forecasts, prose"

  compaction_rule:
    trigger: "main context exceeds 800 lines"
    action:
      - emit: "[COMPACTION] Distilled <X> lines to <Y> capsule fields."
      - rebuild: "capsule from artifacts only"
      - drop: "all prior reasoning and conversation prose"

  forbidden:
    - treating_agent_prose_as_capsule_content
    - referencing_prior_state_without_rebuilding_capsule
    - skipping_compaction_log_when_triggered
    - injecting_untrusted_content_into_capsule
```

---

## 6) State Machine

```yaml
state_machine:
  STATE_SET:
    - INIT
    - INTAKE_TASK
    - NULL_CHECK
    - BUDGET_CHECK
    - COMPACTION
    - DISPATCH_DECISION
    - BUILD_CNF_CAPSULE
    - SELECT_SKILL_PACK
    - LAUNCH_AGENT
    - AWAIT_ARTIFACTS
    - INTEGRATE_ARTIFACTS
    - VERIFY_INTEGRATION
    - FINAL_SEAL
    - INLINE_EXECUTE
    - EXIT_PASS
    - EXIT_NEED_INFO
    - EXIT_BLOCKED

  TRANSITIONS:
    - INIT → INTAKE_TASK: on task_received
    - INTAKE_TASK → NULL_CHECK: always
    - NULL_CHECK → EXIT_NEED_INFO: if task_null_or_ambiguous
    - NULL_CHECK → BUDGET_CHECK: otherwise
    - BUDGET_CHECK → COMPACTION: if main_context_lines > 800
    - BUDGET_CHECK → DISPATCH_DECISION: otherwise
    - COMPACTION → DISPATCH_DECISION: after_capsule_rebuild
    - DISPATCH_DECISION → BUILD_CNF_CAPSULE: if task_requires_dispatch
    - DISPATCH_DECISION → INLINE_EXECUTE: if trivial_task_le_50_lines
    - BUILD_CNF_CAPSULE → SELECT_SKILL_PACK: always
    - SELECT_SKILL_PACK → LAUNCH_AGENT: always
    - LAUNCH_AGENT → AWAIT_ARTIFACTS: always
    - AWAIT_ARTIFACTS → INTEGRATE_ARTIFACTS: on artifacts_received
    - AWAIT_ARTIFACTS → EXIT_BLOCKED: if agent_EXIT_BLOCKED
    - AWAIT_ARTIFACTS → EXIT_NEED_INFO: if agent_EXIT_NEED_INFO
    - INTEGRATE_ARTIFACTS → VERIFY_INTEGRATION: always
    - VERIFY_INTEGRATION → FINAL_SEAL: if integration_consistent and all_rounds_complete
    - VERIFY_INTEGRATION → BUILD_CNF_CAPSULE: if re_dispatch_needed and budgets_allow
    - VERIFY_INTEGRATION → EXIT_BLOCKED: if max_rounds_exceeded
    - INLINE_EXECUTE → FINAL_SEAL: always
    - FINAL_SEAL → EXIT_PASS: if evidence_complete and rung_target_met
    - FINAL_SEAL → EXIT_BLOCKED: otherwise

  FORBIDDEN_STATES:
    SKILL_LESS_DISPATCH:
      definition: "Sub-agent launched without skill pack pasted into prompt"
      detector: "sub-agent prompt missing <BEGIN_SKILL> block"
      recovery: "rebuild prompt with full skill content; re-dispatch"

    SUMMARY_AS_EVIDENCE:
      definition: "Main session uses agent prose summary as Lane A evidence"
      detector: "evidence reference is prose, not artifact path or JSON"
      recovery: "request artifact (tests.json, PATCH_DIFF) from agent; reject prose claim"

    CONTEXT_ACCUMULATION:
      definition: "Main context grows >800 lines without [COMPACTION] log"
      detector: "line count >800 and no COMPACTION entry in session"
      recovery: "emit [COMPACTION] log; rebuild capsule from artifacts"

    INLINE_DEEP_WORK:
      definition: "Main session doing specialized work (code/math/proof) without dispatch"
      detector: "main session output contains code diff or math proof >100 lines"
      recovery: "dispatch to appropriate role; do not continue inline"

    UNDECLARED_RUNG:
      definition: "Sub-agent launched without rung_target declared"
      detector: "prompt missing rung_target field"
      recovery: "add rung_target; default 641 if not promotion candidate"

    CROSS_LANE_UPGRADE:
      definition: "Agent Lane C forecast used to claim PASS"
      detector: "PASS status derived from forecast/plan, not executable artifact"
      recovery: "require artifact evidence; downgrade to NEED_INFO"

    FORGOTTEN_CAPSULE:
      definition: "Sub-agent prompt references 'earlier', 'as discussed', 'recall that'"
      detector: "regex match on forbidden phrases in sub-agent prompt"
      recovery: "rebuild capsule from scratch; remove all history references"

    PRIME_SAFETY_MISSING_FROM_PACK:
      definition: "Skill pack built without prime-safety as first skill"
      detector: "BEGIN_SKILL for prime-safety absent from sub-agent prompt"
      recovery: "add prime-safety as first BEGIN_SKILL block before dispatching"

    SILENT_CONTEXT_DROP:
      definition: "Context truncated without emitting [COMPACTION] log"
      detector: "context shortened by >200 lines without COMPACTION entry"
      recovery: "emit COMPACTION entry retroactively; document what was dropped"
```

---

## 7) Verification Ladder

```yaml
verification_ladder:
  RUNG_641:
    meaning: "Correct dispatch + artifact integration (local correctness)"
    requires:
      - task_dispatched_to_correct_agent_role
      - skill_pack_appropriate_for_task
      - prime_safety_in_every_pack
      - artifacts_received_and_format_verified
      - cnf_capsule_complete_no_history_references
      - rung_target_declared_in_dispatch

  RUNG_274177:
    meaning: "Stable orchestration (multi-round, no rot)"
    requires:
      - RUNG_641
      - compaction_log_emitted_when_triggered
      - context_rebuilt_from_artifacts_not_memory
      - multiple_dispatch_rounds_consistent
      - no_forbidden_states_entered_in_any_round
      - artifact_sha256_stable_across_rounds

  RUNG_65537:
    meaning: "Promotion-grade orchestration (adversarial + complete chain)"
    requires:
      - RUNG_274177
      - skeptic_agent_verified_all_solver_outputs
      - judge_reviewed_scope_compliance_of_all_agents
      - no_cross_lane_upgrades
      - rung_of_integration_is_MIN_of_all_agents
      - behavioral_hash_stable_across_3_seeds
```

---

## 8) Null vs Zero Distinction

```yaml
null_vs_zero_orchestration:
  null_task:
    definition: "No task provided — pre-systemic absence"
    handling: "EXIT_NEED_INFO immediately; do not invent task or constraints"

  empty_artifact_list:
    definition: "Sub-agent returned 0 artifacts but verdict=PASS (valid: no changes needed)"
    handling: "PASS if agent verdict=PASS AND stop_reason=NO_CHANGES_REQUIRED"
    never_confuse_with: "null artifacts (agent produced nothing = different from empty set)"

  null_skill_pack:
    definition: "No skills assigned to sub-agent"
    handling: "EXIT_BLOCKED stop_reason=SKILL_LESS_DISPATCH before launching"
    never_treat_as: "default empty pack or 'the agent already knows'"

  null_rung_target:
    definition: "No rung declared for dispatch"
    handling: "EXIT_BLOCKED stop_reason=UNDECLARED_RUNG before launching"
    never_treat_as: "rung=641 by default (must be explicit)"

  zero_dispatch_rounds:
    definition: "No agents dispatched (trivial inline task completed)"
    handling: "PASS with inline_execute=true artifact"
    never_confuse_with: "null dispatch (task exists but no dispatch decision made)"
```

---

## 9) Output Contract

```yaml
output_contract:
  on_DISPATCH:
    required:
      - agent_role: "[Coder|Planner|Mathematician|Graph_Designer|Swarm_Orchestrator|Writer|Skeptic|Janitor|Wish_Manager|Context_Manager]"
      - skill_pack_files: "list of skill files included"
      - rung_target: "[641|274177|65537]"
      - cnf_capsule_complete: true
      - expected_artifact_schema: "JSON schema"

  on_INTEGRATION:
    required:
      - artifacts_received: "list with sha256 or explicit review"
      - verdicts_per_agent: "PASS|BLOCKED|NEED_INFO per agent"
      - compaction_log_if_triggered: true

  on_EXIT_PASS:
    required:
      - integrated_artifact_summary: "artifact paths + sha256"
      - verification_rung_achieved: "[641|274177|65537]"
      - rung_calculation: "MIN(all agent rungs)"
      - all_agents_verdict: "PASS"
      - no_forbidden_states_entered: true

  on_EXIT_BLOCKED:
    required:
      - stop_reason
      - which_agent_blocked: "role + task"
      - what_was_attempted
      - artifacts_produced_so_far
      - next_actions

  on_EXIT_NEED_INFO:
    required:
      - missing_fields: "non-empty list"
      - safe_partial_if_available
```

---

## 10) Anti-Patterns (Named)

**AP-1: God Orchestrator**
- Symptom: Main session doing coding, proofs, or graph design inline (>100 lines)
- Fix: Dispatch to appropriate agent with correct skill pack
- Forbidden state: `INLINE_DEEP_WORK`

**AP-2: Skill Anemia**
- Symptom: Sub-agent launched with only a brief description of a skill, not its full content
- Fix: Paste entire skill file content into sub-agent prompt via `<BEGIN_SKILL>` blocks
- Forbidden state: `SKILL_LESS_DISPATCH`

**AP-3: Context Rot**
- Symptom: Main session references "earlier conversation"; sub-agent gets "as before" prompts
- Fix: Rebuild CNF capsule from artifacts; inject full context in each dispatch
- Forbidden state: `FORGOTTEN_CAPSULE`, `CONTEXT_ACCUMULATION`

**AP-4: Summary Theater**
- Symptom: Main session uses agent prose ("the coder agent said it works") as Lane A evidence
- Fix: Require artifacts (tests.json, PATCH_DIFF, convergence.json); prose is Lane C only
- Forbidden state: `SUMMARY_AS_EVIDENCE`

**AP-5: Rung Laundering**
- Symptom: Slowest sub-agent achieves rung 641; main session claims rung 65537
- Fix: Rung of integrated output = MIN(rung of all agents). Non-negotiable.
- Forbidden state: `CROSS_LANE_UPGRADE`

**AP-6: Skill Overload**
- Symptom: All 10 skills pasted into every sub-agent "to be safe" — bloats context, causes conflicts
- Fix: Load only the skills relevant to the agent's declared role (per §3 dispatch matrix)
- Rule: More skills ≠ better. Irrelevant skills waste sub-agent context window.

**AP-7: Safety Omission**
- Symptom: Skill pack built without prime-safety (e.g., coder agent gets only prime-coder)
- Fix: prime-safety ALWAYS the first `<BEGIN_SKILL>` block in every sub-agent prompt
- Forbidden state: `PRIME_SAFETY_MISSING_FROM_PACK`

**AP-8: Silent Truncation**
- Symptom: Main context is implicitly compressed by the system; no COMPACTION log emitted
- Fix: Proactively emit `[COMPACTION]` log before context hits limit; rebuild capsule
- Forbidden state: `SILENT_CONTEXT_DROP`

---

## 11) Integration with phuc-swarms

`phuc-orchestration` handles the main session. `phuc-swarms` handles multi-agent coordination
within a sub-agent context.

```yaml
integration:
  phuc_orchestration:
    scope: "Main session orchestration"
    responsibility: "Dispatch decision + skill pack assembly + CNF capsule + artifact integration"
    context: "Loaded in main session CLAUDE.md (always on)"

  phuc_swarms:
    scope: "Sub-agent swarm coordination"
    responsibility: "Scout→Forecast→Judge→Solve→Verify→Podcast chain within a sub-agent"
    context: "Loaded in Swarm Orchestrator sub-agent skill pack (on demand)"

  relationship: |
    When the main session needs multi-agent orchestration:
    1. Main session (phuc-orchestration) dispatches to Swarm Orchestrator agent
    2. Swarm Orchestrator (phuc-swarms + phuc-context) runs the swarm chain
    3. Swarm outputs (SCOUT_REPORT.json, FORECAST_MEMO.json, SOLUTION.diff, SKEPTIC_VERDICT.json)
       flow back as artifacts to the main session
    4. Main session integrates artifacts and updates its capsule
    5. Main session rung = MIN(main session rung, swarm rung)
```

---

## 12) Quick Reference (Cheat Sheet)

```
Main session loads: prime-safety + prime-coder + phuc-orchestration (always)
                    phuc-forecast (optional; add if planning-heavy session)

Dispatch threshold: >100 lines specialized work → dispatch to typed sub-agent

Skill pack rule:    prime-safety ALWAYS first; then domain skill (see §3 table)

CNF capsule rule:   Full task + context + constraints injected into each sub-agent
                    NEVER: "as discussed", "as before", "recall that", "you know the context"

Compaction trigger: Main context >800 lines → [COMPACTION] log → rebuild capsule from artifacts

Rung of output:     MIN(rung of all sub-agents that contributed)

Forbidden (hard):   SKILL_LESS_DISPATCH | CONTEXT_ACCUMULATION | SUMMARY_AS_EVIDENCE
                    INLINE_DEEP_WORK | PRIME_SAFETY_MISSING_FROM_PACK | FORGOTTEN_CAPSULE

Swarms:             When complex multi-agent work needed → dispatch Swarm Orchestrator
                    with phuc-swarms + phuc-context in skill pack (not inline)
```
