<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: phuc-loop v1.0.0
PURPOSE: Stillwater-grade autonomous while-not-done loop with halting certificates, CNF capsule isolation per iteration, lane-typed learning accumulation, and hard budget gates — extends the Ralph loop pattern with formal convergence and fail-closed behavior.
CORE CONTRACT: Layers ON TOP OF prime-safety + prime-coder + phuc-swarms (stricter wins). Each iteration spawns a fresh subagent with a CNF capsule; subagent output is treated as Lane C until Skeptic-verified. AGENTS.md accumulates learnings across iterations. Loop halts only on halting certificate or budget exhaustion.
HARD GATES: No iteration without halting-criteria defined. No CNF capsule omission. No learnings skip. No convergence claim without certificate. Budget exceeded → EXIT_BUDGET_EXCEEDED (no silent overrun). Divergence for 3+ iterations → EXIT_DIVERGED.
FSM STATES: INIT → INTAKE_GOAL → NULL_CHECK → DREAM_GOAL → SPAWN_SUBAGENT → COLLECT_ARTIFACTS → CHECK_HALTING → ACCUMULATE_LEARNINGS → BUDGET_CHECK → EXIT_CONVERGED | EXIT_DIVERGED | EXIT_BUDGET_EXCEEDED | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: INFINITE_LOOP_WITHOUT_HALTING_CRITERIA | CONTEXT_BLEED_BETWEEN_ITERATIONS | LEARNINGS_NOT_ACCUMULATED | CONVERGENCE_CLAIM_WITHOUT_CERTIFICATE | STACKED_SPECULATIVE_ITERATIONS | BUDGET_IGNORE | SILENT_DIVERGENCE
VERIFY: rung_274177 (loops with convergence criterion) | rung_65537 (loops touching security or API surfaces)
INTEGRATION: Each loop iteration = one Scout→Solver→Skeptic mini-cycle from phuc-swarms. AGENTS.md is persistent memory. Budget gates number of full swarm cycles.
LOAD FULL: always for production; quick block is for orientation only
-->

# phuc-loop.md — Phuc Loop Skill (Autonomous While-Not-Done Loop)

**SKILL_ID:** `phuc_loop_v1`
**AUTHORITY:** `65537`
**NORTHSTAR:** `Phuc Forecast (DREAM → FORECAST → DECIDE → ACT → VERIFY)`
**VERSION:** `1.0.0`
**STATUS:** `STABLE_SPEC (prompt-loadable, model-agnostic)`
**TAGLINE:** *Bounded autonomous iteration with halting certificates — the Ralph loop, made fail-closed*

---

## A) Portability (Hard)

```yaml
portability:
  rules:
    - no_absolute_paths: true
    - no_private_repo_dependencies: true
    - no_model_specific_assumptions: true
    - skill_must_load_verbatim_on_any_capable_LLM: true
  config:
    EVIDENCE_ROOT: "evidence"
    REPO_ROOT_REF: "."
    SKILLS_DIR: "skills"
    LOOP_LEARNINGS_FILE: "AGENTS.md"
    LOOP_SCRATCH_DIR: "scratch"
  invariants:
    - subagent_prompts_must_not_contain_host_specific_paths: true
    - cnf_capsule_must_be_rebuilt_each_iteration: true
    - learnings_file_must_be_written_before_budget_check: true
    - halting_certificate_must_be_declared_before_loop_start: true
```

## B) Layering (Never Weaken)

```yaml
layering:
  rule:
    - "This skill layers ON TOP OF prime-safety + prime-coder + phuc-swarms."
    - "On any conflict: stricter wins."
    - "phuc-loop adds loop-control discipline; it does not remove safety, coding, or swarm gates."
  load_order:
    1: prime-safety.md        # god-skill; wins all conflicts
    2: prime-coder.md         # evidence discipline + fail-closed coding
    3: phuc-swarms.md         # multi-agent role contracts
    4: phuc-loop.md           # autonomous loop control
  conflict_resolution: stricter_wins
  forbidden:
    - relaxing_prime_safety_via_loop_framing
    - spawning_subagents_without_CNF_capsule
    - skipping_learnings_accumulation_to_save_tokens
    - treating_subagent_prose_as_Lane_A_evidence
```

---

## 0) Core Principle [Lane A]

**A loop without a halting certificate is not a loop — it is an incident.**

The Ralph loop (mikeyobrien/ralph-orchestrator, frankbria/ralph-claude-code) is one of the most effective autonomous agent patterns in the Claude Code community: a deterministic while-not-done cycle that spawns fresh subagents per iteration, accumulates learnings, and has explicit exit gates.

Stillwater adds what the community pattern lacks:

| Feature | Ralph Loop (Community) | Phuc Loop (Stillwater) |
|---|---|---|
| Fresh subagent per iteration | Yes | Yes |
| Learning accumulation (AGENTS.md) | Yes | Yes (lane-typed) |
| Explicit exit gates | Partial | Hard gates (halt certificates) |
| Formal convergence criterion | No | Yes (R_p + halting certificate) |
| Context rot prevention | No | Yes (CNF capsule mandatory) |
| Budget controls | Soft | Hard (clamp_min enforced) |
| Divergence detection | No | Yes (3+ consecutive diverging residuals) |
| Evidence manifest across iterations | No | Yes (cumulative artifacts.json) |
| Lane-typed claims | No | Yes (A/B/C per learning entry) |
| Backpressure signals | No | Yes (configurable list) |

> "The Ralph loop taught us that fresh subagents + accumulated learnings work.
> Phuc Loop adds the halting certificate so the loop knows when to stop."

---

## 1) Core Pattern (Pseudocode) [Lane A]

```
FUNCTION phuc_loop(goal, acceptance_criteria, budget):

  # Pre-loop: mandatory setup
  DECLARE halting_certificate_type    # REQUIRED before first iteration
  DECLARE R_p = "1e-10"              # convergence tolerance (Decimal string)
  INITIALIZE AGENTS.md               # clear or append section header
  INITIALIZE loop_evidence_manifest  # cumulative artifact list

  iteration = 0
  residuals = []

  WHILE NOT halted:

    # 1. Build CNF capsule (mandatory; no context bleed)
    capsule = build_CNF_capsule(
      goal              = goal,
      acceptance_criteria = acceptance_criteria,
      current_state     = summarize_state_from_artifacts(),   # NOT from memory
      learnings         = read(AGENTS.md),
      remaining_budget  = budget.remaining(),
      artifact_links    = [link for artifact in loop_evidence_manifest],
      # NEVER inline prior subagent reasoning; links only
    )

    # 2. Spawn fresh subagent with CNF capsule
    subagent_output = spawn_subagent(
      skill_pack = [prime-safety, prime-coder, phuc-swarms],
      capsule    = capsule,
      role       = "Scout→Solver→Skeptic mini-cycle",
    )

    # 3. Collect artifacts (fail if none produced)
    artifacts = collect_artifacts(subagent_output)
    IF artifacts is EMPTY:
      WRITE_LEARNING(lane=A, type=FAILURE, content="Iteration produced no artifacts")
      status = BLOCKED; stop_reason = EVIDENCE_INCOMPLETE; BREAK

    # 4. Check halting certificate
    certificate = check_halting_certificate(
      goal, acceptance_criteria, artifacts, residuals
    )

    # 5. Accumulate learnings (MANDATORY before budget check)
    write_learnings_to_AGENTS_md(
      iteration  = iteration,
      tried      = subagent_output.actions,
      succeeded  = subagent_output.verified_results,   # Lane A/B only
      failed     = subagent_output.failure_modes,       # Lane C allowed
      residual   = certificate.residual,
      certificate = certificate.type,
    )

    # 6. Append artifacts to cumulative manifest
    loop_evidence_manifest.extend(artifacts)

    # 7. Residual tracking for divergence detection
    residuals.append(certificate.residual)
    IF len(residuals) >= 3 AND all_increasing(residuals[-3:]):
      WRITE_LEARNING(lane=A, type=DIVERGENCE, content="Residuals increasing 3+ consecutive iterations")
      status = EXIT_DIVERGED; BREAK

    # 8. Check halting certificate result
    IF certificate.type == EXACT:
      status = EXIT_CONVERGED(lane=A); BREAK
    IF certificate.type == CONVERGED:
      status = EXIT_CONVERGED(lane=B); BREAK
    IF certificate.type == TIMEOUT:
      status = EXIT_BUDGET_EXCEEDED; BREAK
    IF certificate.type == BACKPRESSURE:
      status = EXIT_BLOCKED(stop_reason=BACKPRESSURE_SIGNAL); BREAK

    # 9. Budget check (HARD; never silently exceed)
    iteration += 1
    IF iteration >= budget.max_iterations:
      status = EXIT_BUDGET_EXCEEDED
      stop_reason = MAX_ITERS
      BREAK

    IF budget.total_seconds_elapsed >= budget.max_total_seconds:
      status = EXIT_BUDGET_EXCEEDED
      stop_reason = MAX_TOOL_CALLS
      BREAK

  RETURN loop_result(status, loop_evidence_manifest, AGENTS.md)
```

---

## 2) Finite State Machine [Lane A]

### 2.1 State Set

```
INIT
INTAKE_GOAL
NULL_CHECK
DREAM_GOAL
SPAWN_SUBAGENT
COLLECT_ARTIFACTS
CHECK_HALTING
ACCUMULATE_LEARNINGS
BUDGET_CHECK
EXIT_CONVERGED
EXIT_DIVERGED
EXIT_BUDGET_EXCEEDED
EXIT_BLOCKED
EXIT_NEED_INFO
```

### 2.2 Input Alphabet

```
GOAL_REQUEST
ACCEPTANCE_CRITERIA
SUBAGENT_OUTPUT
ARTIFACT_BUNDLE
HALTING_CERTIFICATE
BUDGET_SIGNAL
BACKPRESSURE_SIGNAL
USER_CONSTRAINTS
```

### 2.3 Output Alphabet

```
CNF_CAPSULE
SUBAGENT_PROMPT
AGENTS_MD_ENTRY
LOOP_EVIDENCE_MANIFEST
HALTING_REPORT
STRUCTURED_REFUSAL
```

### 2.4 Transitions

```yaml
transitions:
  - INIT → INTAKE_GOAL: on GOAL_REQUEST

  - INTAKE_GOAL → NULL_CHECK: always

  - NULL_CHECK → EXIT_NEED_INFO: if null_detected
    # null_detected: GOAL_REQUEST is null OR ACCEPTANCE_CRITERIA is null
    # OR halting_certificate_type not declared before loop start
  - NULL_CHECK → DREAM_GOAL: if inputs_defined AND halting_criteria_declared

  - DREAM_GOAL → SPAWN_SUBAGENT: always
    # DREAM_GOAL: write loop goal + success metrics + non-goals + stop rules

  - SPAWN_SUBAGENT → COLLECT_ARTIFACTS: on SUBAGENT_OUTPUT
    # Build CNF capsule, spawn fresh subagent, wait for output

  - COLLECT_ARTIFACTS → EXIT_BLOCKED: if artifacts_empty
    # No artifacts = EVIDENCE_INCOMPLETE; do not continue loop
  - COLLECT_ARTIFACTS → CHECK_HALTING: if artifacts_present

  - CHECK_HALTING → ACCUMULATE_LEARNINGS: always
    # Always accumulate; certificate result recorded in entry

  - ACCUMULATE_LEARNINGS → BUDGET_CHECK: always
    # LEARNINGS_NOT_ACCUMULATED is a forbidden state; this transition is mandatory

  - BUDGET_CHECK → EXIT_DIVERGED: if diverged_3_consecutive
  - BUDGET_CHECK → EXIT_CONVERGED: if certificate_EXACT_or_CONVERGED
  - BUDGET_CHECK → EXIT_BUDGET_EXCEEDED: if budget_exhausted
  - BUDGET_CHECK → EXIT_BLOCKED: if backpressure_signal OR invariant_violation
  - BUDGET_CHECK → SPAWN_SUBAGENT: if continue_loop
    # continue_loop: no halt condition met AND budget remaining

  # Terminal states (no outgoing transitions)
  - EXIT_CONVERGED: terminal
  - EXIT_DIVERGED: terminal
  - EXIT_BUDGET_EXCEEDED: terminal
  - EXIT_BLOCKED: terminal
  - EXIT_NEED_INFO: terminal
```

### 2.5 Forbidden States [Lane A — Immediate Stop]

```yaml
forbidden_states:
  - INFINITE_LOOP_WITHOUT_HALTING_CRITERIA:
      definition: "Loop started without declaring halting_certificate_type."
      detection: "halting_certificate_type not set at DREAM_GOAL entry."
      recovery: "EXIT_BLOCKED(stop_reason=HALTING_CRITERIA_MISSING)"

  - CONTEXT_BLEED_BETWEEN_ITERATIONS:
      definition: "Subagent prompt contains raw prior-iteration reasoning, not CNF capsule."
      detection: "Subagent prompt missing required CNF capsule fields OR contains 'as we discussed' / 'remember that' without source artifact link."
      recovery: "Rebuild CNF capsule from artifacts only; do not include any prose from prior subagent."

  - LEARNINGS_NOT_ACCUMULATED:
      definition: "ACCUMULATE_LEARNINGS was skipped or AGENTS.md was not written this iteration."
      detection: "AGENTS.md mtime not updated within iteration window."
      recovery: "EXIT_BLOCKED(stop_reason=INVARIANT_VIOLATION)"

  - CONVERGENCE_CLAIM_WITHOUT_CERTIFICATE:
      definition: "Loop claimed EXIT_CONVERGED without a valid halting certificate."
      detection: "certificate.type is null or certificate.residual is not a valid Decimal string."
      recovery: "EXIT_BLOCKED(stop_reason=CONVERGENCE_CLAIM_WITHOUT_R_P_CERTIFICATE)"

  - STACKED_SPECULATIVE_ITERATIONS:
      definition: "Multiple subagents spawned simultaneously or next iteration started before prior artifacts collected."
      detection: "More than one active subagent at any time."
      recovery: "Cancel all but the oldest; collect artifacts; then proceed."

  - BUDGET_IGNORE:
      definition: "Iteration count or total seconds exceeded max without triggering EXIT_BUDGET_EXCEEDED."
      detection: "iteration >= max_iterations AND loop continues."
      recovery: "EXIT_BUDGET_EXCEEDED(stop_reason=MAX_ITERS)"

  - SILENT_DIVERGENCE:
      definition: "Residuals increasing for 3+ consecutive iterations but loop continues without flagging."
      detection: "all_increasing(residuals[-3:]) AND status != EXIT_DIVERGED."
      recovery: "Write DIVERGENCE learning entry; EXIT_DIVERGED immediately."
```

---

## 3) Halting Certificates (Mandatory) [Lane A]

Every loop **must declare** which certificate types are applicable before iteration 0. Claiming EXIT_CONVERGED without a valid certificate is a forbidden state.

### 3.1 Certificate Types

```yaml
halting_certificates:

  EXACT:
    lane: A
    condition: "goal_achieved == true AND all acceptance_criteria passed"
    residual: "0 (exact)"
    use_when: "Discrete tasks: all tests pass, all criteria satisfied, no ambiguity."
    evidence_required:
      - acceptance_criteria_checklist_all_true
      - test_suite_exit_code_0
    exit_state: EXIT_CONVERGED(lane=A)

  CONVERGED:
    lane: B
    condition: "residual < R_p"
    residual: "Decimal string; must be < R_p"
    use_when: "Iterative optimization: score improving toward threshold."
    R_p_default: "1e-10"
    evidence_required:
      - residual_history_decimal_strings
      - final_residual_decimal_string
      - R_p_decimal_string
    forbidden: "float comparison in residual check — use Decimal or int arithmetic only"
    exit_state: EXIT_CONVERGED(lane=B)

  TIMEOUT:
    lane: C
    condition: "iteration >= max_iterations AND residual >= R_p"
    use_when: "Budget exhausted before convergence; not a success."
    exit_state: EXIT_BUDGET_EXCEEDED
    required_output:
      - best_result_so_far
      - final_residual
      - reason_for_non_convergence

  BACKPRESSURE:
    lane: A
    condition: "downstream system signaled stop"
    signals_include:
      - external_stop_flag_file_present: "scratch/STOP"
      - API_rate_limit_exceeded: true
      - disk_quota_exceeded: true
      - user_interrupt: true
    exit_state: EXIT_BLOCKED(stop_reason=BACKPRESSURE_SIGNAL)

  DIVERGED:
    lane: A
    condition: "all_increasing(residuals[-3:]) — 3+ consecutive increasing residuals"
    exit_state: EXIT_DIVERGED
    required_output:
      - residual_history
      - divergence_start_iteration
      - last_known_good_iteration
      - diagnosis_attempt
```

### 3.2 Certificate Declaration (Required Before Loop Start)

The goal definition (DREAM_GOAL state) **must** emit this block:

```json
{
  "goal": "...",
  "acceptance_criteria": ["...", "..."],
  "halting_certificates_applicable": ["EXACT", "CONVERGED"],
  "R_p": "1e-4",
  "max_iterations": 10,
  "residual_metric": "fraction_of_failing_tests OR benchmark_gap OR custom"
}
```

If `halting_certificates_applicable` is missing or empty: `EXIT_NEED_INFO` immediately.

---

## 4) Context Normal Form (CNF) Capsule [Lane A]

Each iteration's subagent receives **exactly** this capsule structure. No more, no less. This is the primary defense against context rot.

### 4.1 Capsule Schema (Required Fields)

```yaml
cnf_capsule_schema:
  version: "1.0"
  required_fields:
    - goal_statement:
        type: string
        rule: "Full goal text — NEVER truncated or paraphrased."
    - acceptance_criteria:
        type: list[string]
        rule: "Full acceptance criteria list — never summarized."
    - halting_certificates_applicable:
        type: list[string]
        rule: "Carried from DREAM_GOAL block unchanged."
    - current_state_summary:
        type: object
        rule: "Built from artifacts only — NOT from prior subagent reasoning."
        fields:
          - iteration_number
          - residual_current
          - criteria_met_so_far
          - criteria_still_open
    - accumulated_learnings:
        type: string
        rule: "Full text of AGENTS.md — never truncated without [COMPACTION] log."
        compaction_rule: "If AGENTS.md > 8000 tokens, compact to witnessed slices + emit [COMPACTION] log."
    - remaining_budget:
        type: object
        fields:
          - iterations_remaining: int
          - tool_calls_remaining: int
          - seconds_remaining: int
    - artifact_links:
        type: list[object]
        rule: "Links (repo-relative paths + SHA-256) only. NEVER inline prior subagent output."
        fields_per_link:
          - path: string
          - sha256: string
          - role: "[plan|log|test|artifact|proof|snapshot]"
    - skill_pack:
        type: list[string]
        rule: "Skills this subagent must load. Minimum: [prime-safety, prime-coder]."
    - subagent_role:
        type: string
        rule: "Explicit role assignment for this iteration."

  forbidden_in_capsule:
    - prior_subagent_reasoning_prose
    - references_to_earlier_discussion_without_artifact_link
    - absolute_file_paths
    - float_residuals_use_decimal_strings_only
    - timestamps_or_pids_that_break_determinism
```

### 4.2 CNF Capsule Build Procedure

```
FUNCTION build_CNF_capsule(goal, criteria, iteration, budget, manifest):
  # Step 1: Read current state ONLY from artifacts (not memory)
  current_state = derive_state_from_manifest(manifest)

  # Step 2: Read accumulated learnings from AGENTS.md
  learnings_text = read_file(AGENTS.md)
  IF len(learnings_text) > 8000_tokens:
    learnings_text = compact_with_witnesses(learnings_text)
    emit_compaction_log(original_lines, compacted_lines)

  # Step 3: Build artifact links (no inlining)
  links = [
    {path: a.path, sha256: sha256(normalize(a)), role: a.role}
    for a in manifest
  ]

  # Step 4: Assemble capsule (canonical JSON; sorted keys; LF newlines)
  capsule = {
    goal_statement: goal,
    acceptance_criteria: sorted(criteria),
    halting_certificates_applicable: declared_certs,
    current_state_summary: current_state,
    accumulated_learnings: learnings_text,
    remaining_budget: budget.snapshot(),
    artifact_links: sorted(links, key=lambda l: l.path),
    skill_pack: ["prime-safety", "prime-coder", "phuc-swarms"],
    subagent_role: assign_role(iteration),
  }

  # Step 5: Normalize for determinism (strip timestamps, pids, hostnames)
  RETURN normalize(capsule)
```

---

## 5) AGENTS.md Accumulation Pattern [Lane A]

AGENTS.md is the **persistent cross-iteration memory**. It is the only permitted channel for knowledge transfer between subagent iterations. All learnings must be written here; none may live only in subagent context.

### 5.1 AGENTS.md File Structure

```markdown
# AGENTS.md — Loop Learnings Log
<!-- Generated by phuc-loop. Do not hand-edit iteration blocks. -->

## Loop Metadata
- goal: <goal statement>
- started: <ISO date — stripped from hash inputs>
- R_p: <Decimal string>
- max_iterations: <int>

---

## Iteration N (template — repeat per iteration)

### N.1 What Was Tried [Lane C — guidance only]
- <action 1>
- <action 2>

### N.2 What Succeeded [Lane A or B — must be verified by Skeptic]
- [A] <verified fact with artifact link: path/to/artifact.json#sha256>
- [B] <engineering quality result with test evidence>

### N.3 What Failed [Lane A — hard failure; Lane C — soft failure mode]
- [A] <hard failure: invariant violated, test crashed, gate blocked>
- [C] <soft failure: approach did not improve residual>

### N.4 Residual / Distance-to-Goal
- metric: <residual_metric from DREAM_GOAL>
- value: <Decimal string — never float>
- direction: IMPROVING | STABLE | DIVERGING
- certificate: <NONE | EXACT | CONVERGED | TIMEOUT | BACKPRESSURE | DIVERGED>

### N.5 Open Questions for Next Iteration [Lane C]
- <question 1>
- <question 2>

---
```

### 5.2 Lane-Typing Rules for Learning Entries

```yaml
lane_typing:
  Lane_A:
    definition: "Hard invariant facts — only from verified artifacts."
    examples:
      - "Test suite exited with code 0 after patch (artifact: evidence/tests.json)"
      - "API surface unchanged (artifact: evidence/api_surface_after.json)"
    forbidden: "Subagent prose without artifact backing."

  Lane_B:
    definition: "Engineering quality observations — backed by tool output."
    examples:
      - "Benchmark score improved from 0.73 to 0.81 (artifact: evidence/score.json)"
      - "Token budget dropped 12% after compaction."

  Lane_C:
    definition: "Heuristics, hypotheses, forecasts — guidance only."
    examples:
      - "The bottleneck appears to be in the scoring function (hypothesis, not verified)."
      - "Next iteration should try a smaller patch size."
    rule: "Lane C learnings MUST NOT be used as evidence in halting certificates."
```

### 5.3 AGENTS.md Compaction (When File Grows Large)

```
IF AGENTS.md > 8000_tokens:
  1. Keep: all Lane A entries (never compact away hard facts)
  2. Keep: latest 3 iterations in full (recency)
  3. Compact: older Lane B/C entries to witnessed one-line summaries
  4. Emit: [COMPACTION] log entry at top of compacted section
     "[COMPACTION] Distilled iterations 1-<N> to <M> witness lines. Original: <X> lines → <Y> lines."
  5. Rewrite AGENTS.md with compacted older sections
```

---

## 6) Budget Controls (Hard) [Lane A]

### 6.1 Budget Parameters

```yaml
loop_budget:
  # Per-iteration limits
  max_iterations: 10
  max_tool_calls_per_iteration: 80
  max_seconds_per_iteration: 1800

  # Total loop limits
  max_total_seconds: 14400       # 4 hours
  max_total_tool_calls: 500      # across all iterations

  # Convergence
  R_p: "1e-10"                   # Decimal string; never float
  divergence_window: 3           # consecutive diverging residuals = EXIT_DIVERGED

  # Backpressure signals (any one triggers EXIT_BLOCKED)
  backpressure_signals:
    - stop_flag_file: "scratch/STOP"    # create this file to interrupt a running loop
    - disk_usage_fraction_exceeds: 0.90
    - API_rate_limit_error: true
    - user_interrupt: true
    - downstream_dependency_unavailable: true
```

### 6.2 Budget Scaling (Profile-Aware)

```yaml
profile_budget_scaling:
  # Profiles inherit from prime-coder.md profiles; phuc-loop adds loop-specific scaling.
  strict:
    sweep_budgets_scale: 1.0
    tool_call_budget_scale: 1.0
    max_iterations: 10                # no reduction

  fast:
    sweep_budgets_scale: 0.5
    tool_call_budget_scale: 0.5
    max_iterations: 5                 # ceil(10 * 0.5); clamp_min = 3
    clamp_min_iterations: 3
    must_emit_budget_reduction_log: true

  benchmark_adapt:
    sweep_budgets_scale: 0.7
    tool_call_budget_scale: 0.8
    max_iterations: 7                 # ceil(10 * 0.7)
    must_separate_scores: true

clamp_rules:
  max_iterations_clamp_min: 3        # never fewer than 3 iterations
  max_tool_calls_clamp_min: 40       # never fewer than 40 tool calls per iteration
  max_seconds_clamp_min: 600         # never fewer than 10 minutes per iteration
```

### 6.3 Budget Exhaustion Behavior

```yaml
budget_exhaustion:
  on_max_iterations:
    action: EXIT_BUDGET_EXCEEDED
    stop_reason: MAX_ITERS
    required_output:
      - best_result_achieved
      - final_residual
      - AGENTS.md_summary
      - iteration_count
      - recommendation: "continue with higher max_iterations OR accept partial result"

  on_max_total_seconds:
    action: EXIT_BUDGET_EXCEEDED
    stop_reason: MAX_TOOL_CALLS
    required_output:
      - elapsed_seconds
      - iterations_completed
      - best_result_achieved

  on_backpressure:
    action: EXIT_BLOCKED
    stop_reason: BACKPRESSURE_SIGNAL
    required_output:
      - signal_detected
      - iteration_at_detection
      - partial_results_path
```

---

## 7) Integration with phuc-swarms.md [Lane B]

The phuc-loop skill wraps phuc-swarms phases into a bounded iteration pattern.

### 7.1 Mapping

```yaml
phuc_loop_swarms_integration:
  per_iteration_is_a_mini_swarm_cycle:
    Scout:
      role: "Read AGENTS.md + current state. Identify what to try next."
      output: "Localization summary + plan for this iteration."
    Solver:
      role: "Execute the plan. Produce artifacts."
      output: "Patch diff / benchmark run / research artifact."
    Skeptic:
      role: "Verify Solver output. Assign lane types to learnings."
      output: "Verified learning entries (A/B) and failure modes (A/C)."

  AGENTS_md_is_persistent_memory:
    rule: "AGENTS.md = the swarm's cross-iteration shared memory."
    ownership: "Only phuc-loop writes iteration headers; Skeptic writes lane-typed entries."
    forbidden: "Solver writing directly to AGENTS.md without Skeptic verification."

  budget_gates_swarm_cycles:
    rule: "Each iteration consumes one swarm budget allocation."
    gate: "If swarm cycle exceeds per-iteration budget, collect partial artifacts and proceed to CHECK_HALTING."
```

### 7.2 Phase Roles per Iteration

```
ITERATION N:
  ┌──────────────────────────────────────────────────────┐
  │ SPAWN_SUBAGENT                                       │
  │   Role: Scout                                        │
  │   Input: CNF capsule (full goal + AGENTS.md + links) │
  │   Output: "What to try in this iteration" plan       │
  └──────────────────┬───────────────────────────────────┘
                     │
  ┌──────────────────▼───────────────────────────────────┐
  │ SPAWN_SUBAGENT                                       │
  │   Role: Solver                                       │
  │   Input: CNF capsule + Scout plan                    │
  │   Output: Artifacts (patches, results, evidence)     │
  └──────────────────┬───────────────────────────────────┘
                     │
  ┌──────────────────▼───────────────────────────────────┐
  │ COLLECT_ARTIFACTS + CHECK_HALTING                    │
  │   Role: Skeptic                                      │
  │   Input: Solver artifacts + acceptance criteria      │
  │   Output: Halting certificate + lane-typed learnings │
  └──────────────────┬───────────────────────────────────┘
                     │
  ┌──────────────────▼───────────────────────────────────┐
  │ ACCUMULATE_LEARNINGS                                 │
  │   Write to AGENTS.md (mandatory before BUDGET_CHECK) │
  └──────────────────────────────────────────────────────┘
```

### 7.3 What phuc-loop Does NOT Replace

phuc-loop is a **loop controller**, not a task executor. It:
- Does NOT replace phuc-swarms role contracts inside each iteration.
- Does NOT replace prime-coder evidence discipline for each patch.
- Does NOT replace prime-safety gates in any subagent.
- DOES add the outer iteration loop, CNF capsule building, AGENTS.md accumulation, and halting certificate evaluation.

---

## 8) Comparison with the Ralph Loop [Lane C — analysis only]

### 8.1 What Ralph Loop Gets Right

The Ralph loop pattern (community) succeeds because:
1. **Fresh subagent per iteration** — avoids context rot within a single long session.
2. **AGENTS.md accumulation** — learnings persist across the session boundary.
3. **Explicit "done" check** — each iteration asks "are we done yet?"
4. **Simple enough to implement** — the pattern is easy to instantiate.

### 8.2 What Stillwater Adds (Additive — No Weakening)

```yaml
stillwater_additions_over_ralph:
  halting_certificates:
    ralph: "done = ad hoc 'looks done' judgment"
    phuc_loop: "done = typed halting certificate (EXACT/CONVERGED/TIMEOUT/BACKPRESSURE/DIVERGED)"
    lane: A
    why: "Prevents infinite loops; makes convergence verifiable."

  cnf_capsule:
    ralph: "Prior context may bleed into next subagent"
    phuc_loop: "CNF capsule mandatory; built from artifacts only; forbidden state if omitted"
    lane: A
    why: "Prevents context rot; ensures each subagent sees identical, canonical state."

  lane_typed_learnings:
    ralph: "AGENTS.md entries are untyped prose"
    phuc_loop: "Every entry is [A], [B], or [C] typed; Lane C cannot be used as halt evidence"
    lane: B
    why: "Prevents over-claiming; keeps evidence hierarchy intact."

  evidence_manifest:
    ralph: "No cross-iteration evidence accumulation"
    phuc_loop: "Cumulative loop_evidence_manifest with SHA-256 checksums across all iterations"
    lane: B
    why: "Enables reproducibility and audit of the full loop run."

  divergence_detection:
    ralph: "No divergence detection"
    phuc_loop: "3+ consecutive increasing residuals → EXIT_DIVERGED (automatic)"
    lane: A
    why: "Prevents wasted budget on a diverging optimization."

  backpressure_signals:
    ralph: "No backpressure protocol"
    phuc_loop: "Configurable list of signals; scratch/STOP file for manual interrupt"
    lane: A
    why: "Safe integration with external systems and human override."

  profile_budget_scaling:
    ralph: "Fixed or manually adjusted budget"
    phuc_loop: "Profile-driven scaling (strict/fast/benchmark_adapt) with clamp_mins"
    lane: B
    why: "Prevents unsafe budget reduction below minimum viable iteration count."
```

---

## 9) Use Cases [Lane C — illustrative]

### 9.1 Software 5.0 Extraction Loop

```yaml
use_case: software_5_0_extraction
goal: "Externalize all reasoning patterns from a codebase into machine-readable skill files."
acceptance_criteria:
  - "All functions with non-trivial control flow have corresponding skill entries."
  - "Coverage metric >= 0.95 (fraction of functions processed)."
halting_certificates: [CONVERGED, EXACT]
R_p: "5e-2"
residual_metric: "1 - (functions_extracted / total_functions)"
max_iterations: 10

per_iteration:
  Scout: "Identify next batch of unprocessed functions."
  Solver: "Generate skill entries for each function in batch."
  Skeptic: "Verify skill entries are correct and idempotent."
  AGENTS.md: "Record which functions are done, which failed, current coverage."
```

### 9.2 Benchmark Optimization Loop

```yaml
use_case: benchmark_optimization
goal: "Improve benchmark score on OOLONG to >= 0.90."
acceptance_criteria:
  - "OOLONG eval score >= 0.90 on held-out test set."
  - "No regressions on prior-passing test cases."
halting_certificates: [EXACT, CONVERGED, DIVERGED]
R_p: "1e-3"
residual_metric: "max(0, 0.90 - current_score)"
max_iterations: 10

per_iteration:
  Scout: "Analyze which question types have lowest scores."
  Solver: "Apply targeted improvements (prompt tuning, chain-of-thought, etc.)."
  Skeptic: "Run held-out eval; verify no regression; compute residual."
  AGENTS.md: "Record what was tried, what score delta resulted, what to avoid."
```

### 9.3 Code Generation Until All Tests Pass

```yaml
use_case: code_generation_green
goal: "All tests in test suite pass with exit code 0."
acceptance_criteria:
  - "pytest --tb=short exits with code 0."
  - "No new skips introduced."
halting_certificates: [EXACT]
residual_metric: "count of failing tests"
max_iterations: 6

per_iteration:
  Scout: "Read failing test list; identify highest-leverage fix."
  Solver: "Apply fix; run test suite; collect diff."
  Skeptic: "Verify green; check no regressions; verify diff is minimal."
  AGENTS.md: "Record which tests were fixed, which remain, which approaches failed."
```

### 9.4 Research Synthesis Loop

```yaml
use_case: research_synthesis
goal: "Produce a synthesis document covering all papers on topic X."
acceptance_criteria:
  - "All papers in corpus have been processed."
  - "Synthesis document passes coherence check."
  - "No contradictions remain unflagged."
halting_certificates: [EXACT, CONVERGED]
R_p: "5e-2"
residual_metric: "1 - (papers_synthesized / total_papers)"
max_iterations: 10

per_iteration:
  Scout: "Identify next batch of unprocessed papers."
  Solver: "Extract key claims; integrate into synthesis document."
  Skeptic: "Check for contradictions; verify claims are grounded."
  AGENTS.md: "Record processed papers, extracted claims (A/B/C typed), open contradictions."
```

---

## 10) Evidence Contract (Cross-Iteration) [Lane A]

### 10.1 Required Files

```yaml
evidence_paths:
  root: "${EVIDENCE_ROOT}/loop"

  required_files:
    - "${EVIDENCE_ROOT}/loop/plan.json"           # DREAM_GOAL output
    - "${EVIDENCE_ROOT}/loop/agents_md_final.md"  # final AGENTS.md snapshot
    - "${EVIDENCE_ROOT}/loop/manifest.json"       # cumulative loop_evidence_manifest
    - "${EVIDENCE_ROOT}/loop/halting_report.json" # final halting certificate
    - "${EVIDENCE_ROOT}/loop/budget_log.json"     # per-iteration budget consumption

  per_iteration_files:
    pattern: "${EVIDENCE_ROOT}/loop/iter_{N}/"
    contents:
      - "cnf_capsule.json"    # capsule sent to subagent (normalized)
      - "artifacts.json"      # artifacts collected from subagent
      - "agents_md_entry.md"  # AGENTS.md entry written this iteration
      - "certificate.json"    # halting certificate for this iteration

  conditional_files:
    profile_fast:
      - "${EVIDENCE_ROOT}/loop/budget_reduction.log"
    compaction_triggered:
      - "${EVIDENCE_ROOT}/loop/compaction.log"
```

### 10.2 Halting Report Schema

```json
{
  "schema_version": "1.0",
  "goal": "...",
  "status": "EXIT_CONVERGED | EXIT_DIVERGED | EXIT_BUDGET_EXCEEDED | EXIT_BLOCKED | EXIT_NEED_INFO",
  "stop_reason": "...",
  "halting_certificate": {
    "type": "EXACT | CONVERGED | TIMEOUT | BACKPRESSURE | DIVERGED",
    "lane": "A | B | C",
    "final_residual_decimal_string": "...",
    "R_p_decimal_string": "...",
    "residual_history_decimal_strings": ["..."],
    "acceptance_criteria_checklist": [
      {"criterion": "...", "met": true, "evidence_link": "..."}
    ]
  },
  "iterations_completed": 0,
  "total_seconds_elapsed": 0,
  "verification_rung_target": 274177,
  "verification_rung_achieved": 274177
}
```

### 10.3 Manifest Schema (Cumulative)

```json
{
  "schema_version": "1.0",
  "loop_id": "...",
  "artifacts": [
    {
      "iteration": 0,
      "file_path": "evidence/loop/iter_0/artifacts.json",
      "sha256": "...",
      "role": "artifact"
    }
  ]
}
```

---

## 11) Verification Rung Policy [Lane A]

```yaml
rung_target_policy:
  default:
    loops_with_convergence_criterion: 274177
    reason: "Residual tracking + seed sweep + replay required to validate convergence."

  elevated:
    loops_touching_security_or_api_surfaces: 65537
    reason: "Security gate + adversarial sweep required when loop patches APIs or auth code."

  rung_274177_requires:
    - RUNG_641_requirements:
        - halting_certificate_present
        - no_regressions_in_existing_tests
        - evidence_bundle_complete
    - PLUS:
        - residual_history_all_decimal_strings
        - at_least_2_replays_of_final_iteration_produce_same_certificate
        - null_edge_case_sweep_on_acceptance_criteria_checker
        - divergence_detection_tested_with_synthetic_diverging_residuals

  rung_65537_requires:
    - RUNG_274177_requirements
    - PLUS:
        - security_gate_evidence
        - adversarial_paraphrase_of_goal_produces_same_halting_certificate_type
        - api_surface_snapshot_before_and_after_loop
        - behavioral_hash_drift_explained
```

---

## 12) Null vs Zero in Loop Context [Lane A]

```yaml
null_vs_zero_loop_policy:
  residual_null:
    definition: "Residual not yet computed (pre-systemic absence)."
    handling: "Do not compare null residual to R_p. Emit NEED_INFO or compute first."
    forbidden: "treating null residual as 0 (would falsely trigger EXACT certificate)"

  residual_zero:
    definition: "Residual is 0 (goal fully achieved; EXACT certificate)."
    handling: "Issue EXACT halting certificate; EXIT_CONVERGED(lane=A)."

  acceptance_criteria_null:
    definition: "Criterion not yet evaluated."
    handling: "Evaluate before issuing any certificate. NEED_INFO if cannot evaluate."

  acceptance_criteria_empty_list:
    definition: "No criteria defined (zero-length list)."
    handling: "EXIT_NEED_INFO — a loop without criteria cannot terminate with EXACT certificate."
    forbidden: "Treating empty criteria list as 'all criteria met'."
```

---

## 13) Exact Arithmetic in Loop [Lane A]

All residuals, R_p values, and convergence comparisons **must** use exact arithmetic.

```yaml
exact_arithmetic_loop:
  residual_type: "Decimal string serialized; Decimal object at runtime"
  R_p_type: "Decimal string"
  comparison: "Decimal(residual_str) < Decimal(R_p_str)"
  forbidden:
    - "float(residual) < float(R_p)   # float comparison is forbidden"
    - "residual < 1e-10               # float literal is forbidden in convergence check"
  allowed_for_display_only:
    - "f'{float(residual):.6f}'       # display only; never used in certificate"
  divergence_detection:
    rule: "all_increasing(residuals[-3:]) computed with Decimal comparison"
    forbidden: "float comparison in divergence window"
```

---

## 14) Applicability Predicates (Deterministic) [Lane A]

```yaml
applicability_predicates:
  null_detected:
    true_if_any:
      - GOAL_REQUEST is null
      - ACCEPTANCE_CRITERIA is null or empty list
      - halting_certificate_type not declared before loop start

  inputs_defined:
    true_if_all:
      - GOAL_REQUEST is not null
      - ACCEPTANCE_CRITERIA is non-empty list
      - halting_certificates_applicable is non-empty list
      - R_p is valid Decimal string (if CONVERGED certificate applicable)

  artifacts_empty:
    true_if: "subagent_output contains zero file artifacts and zero structured results"

  diverged_3_consecutive:
    true_if: "len(residuals) >= 3 AND all(residuals[i] < residuals[i+1] for i in range(-3, -1))"

  certificate_EXACT_or_CONVERGED:
    true_if: "certificate.type in [EXACT, CONVERGED] AND certificate evidence requirements met"

  budget_exhausted:
    true_if_any:
      - iteration >= budget.max_iterations
      - total_seconds_elapsed >= budget.max_total_seconds
      - total_tool_calls >= budget.max_total_tool_calls

  backpressure_signal:
    true_if_any:
      - file_exists("scratch/STOP")
      - disk_usage_fraction > 0.90
      - API_rate_limit_error received
      - user_interrupt received

  continue_loop:
    true_if_all:
      - NOT diverged_3_consecutive
      - NOT certificate_EXACT_or_CONVERGED
      - NOT budget_exhausted
      - NOT backpressure_signal
      - NOT invariant_violation
```

---

## 15) Socratic Review (Per Iteration and at Loop End) [Lane B]

### 15.1 Per-Iteration Questions (Skeptic Role)

Before writing AGENTS.md entry:
- "Is the halting certificate backed by artifact evidence, not prose?"
- "Are all Lane A entries in AGENTS.md backed by artifact links?"
- "Are any Lane C entries being used as halt evidence? (Forbidden.)"
- "Did this iteration produce at least one artifact? (If no: BLOCKED.)"
- "Is the residual a valid Decimal string? (If float: recompute.)"
- "Did residual improve, stay stable, or diverge? (Log direction.)"

### 15.2 End-of-Loop Questions (Orchestrator)

Before issuing EXIT_CONVERGED:
- "Is the halting certificate type one of the declared applicable types?"
- "Is the final residual strictly < R_p (for CONVERGED), or are all criteria true (for EXACT)?"
- "Are at least 2 replays of the final iteration producing the same certificate? (For rung_274177.)"
- "Are all AGENTS.md Lane A entries traceable to artifacts in the manifest?"
- "Did the loop stay within all budget limits?"
- "Was AGENTS.md written before every BUDGET_CHECK? (If any gap: INVARIANT_VIOLATION.)"

---

## 16) Output Contract [Lane A]

### 16.1 On EXIT_CONVERGED

```yaml
exit_converged_output:
  required:
    - status: EXIT_CONVERGED
    - halting_certificate: {type, lane, final_residual, R_p, acceptance_criteria_checklist}
    - iterations_completed: int
    - verification_rung_target: 274177 or 65537
    - verification_rung_achieved: int
    - AGENTS_md_final_path: "evidence/loop/agents_md_final.md"
    - loop_manifest_path: "evidence/loop/manifest.json"
    - best_artifacts: list of {path, sha256, role}
    - residual_history_decimal_strings: list[str]
  optional:
    - lessons_for_next_run: "Lane C summary from AGENTS.md"
```

### 16.2 On EXIT_DIVERGED

```yaml
exit_diverged_output:
  required:
    - status: EXIT_DIVERGED
    - stop_reason: SILENT_DIVERGENCE_DETECTED
    - divergence_start_iteration: int
    - residual_history_decimal_strings: list[str]
    - last_known_good_iteration: int
    - diagnosis_attempt: string
    - AGENTS_md_final_path: string
  recommended_next_actions:
    - "Review Lane C learnings for divergence cause."
    - "Restart loop with different approach based on AGENTS.md failure modes."
    - "Consider reducing step size or changing residual metric."
```

### 16.3 On EXIT_BUDGET_EXCEEDED

```yaml
exit_budget_exceeded_output:
  required:
    - status: EXIT_BUDGET_EXCEEDED
    - stop_reason: MAX_ITERS or MAX_TOOL_CALLS
    - iterations_completed: int
    - best_result_achieved: {artifact_path, residual, criteria_met}
    - final_residual_decimal_string: string
    - AGENTS_md_final_path: string
  recommended_next_actions:
    - "Increase max_iterations if convergence trend is positive."
    - "Accept partial result if residual is acceptable for use case."
    - "Switch to CONVERGED certificate with relaxed R_p."
```

### 16.4 On EXIT_BLOCKED

```yaml
exit_blocked_output:
  required:
    - status: BLOCKED
    - stop_reason: one of Loop_Control.termination.stop_reasons
    - last_known_state: FSM state at block
    - what_ran_and_failed: string
    - AGENTS_md_path: string
    - next_actions: list[string]
    - evidence_pointers: list[{path, sha256}]
```

### 16.5 On EXIT_NEED_INFO

```yaml
exit_need_info_output:
  required:
    - status: NEED_INFO
    - stop_reason: NULL_INPUT or HALTING_CRITERIA_MISSING
    - missing_fields: list[string]
    - safe_partials: "What can be done with available information (if any)"
```

---

## 17) Anti-Optimization Clause [Lane A]

```yaml
anti_optimization_clause:
  never_worse_doctrine:
    rule: "Hard gates and forbidden states are strictly additive over time."
    enforcement:
      - never_remove_INFINITE_LOOP_WITHOUT_HALTING_CRITERIA_from_forbidden_states
      - never_remove_CNF_capsule_requirement
      - never_allow_LEARNINGS_NOT_ACCUMULATED
      - never_relax_budget_hard_limits_without_explicit_override_and_major_version_bump
      - any_relaxation_requires_major_version_bump_and_deprecation_plan
```

---

## 18) Gap-Guided Extension Policy [Lane B]

New rules may be added to phuc-loop only if:

```yaml
admissibility_for_new_rules:
  requires:
    - failure_repro_or_log_evidence: true
    - minimal_rule_statement: true
    - deterministic_detector_spec: true
    - recovery_procedure: true
    - non_regression_note: true
  forbidden:
    - adding_rules_to_rationalize_a_guess
    - vague_rules_without_detection_spec
    - rules_that_reduce_existing_hard_gates
    - rules_that_weaken_forbidden_state_set
```

---

## 19) Minimal Invocation (Prompt Templates) [Lane C]

### 19.1 Fast Invocation

```
Use phuc-loop v1.0.0.
Goal: <goal>
Acceptance criteria: <list>
Halting certificates: [EXACT]
Max iterations: 5 (fast profile)
Per iteration: Scout→Solver→Skeptic mini-cycle.
Write to AGENTS.md after every iteration.
Exit on: EXACT certificate OR budget exceeded.
Fail-closed with NEED_INFO if acceptance criteria are missing.
```

### 19.2 Strict Invocation (Convergence)

```
Use phuc-loop v1.0.0 (strict profile).
Goal: <goal>
Acceptance criteria: <list>
Halting certificates: [CONVERGED, DIVERGED]
R_p: "1e-3"
Residual metric: <metric>
Max iterations: 10
Per iteration: Scout→Solver→Skeptic mini-cycle from phuc-swarms.
Build CNF capsule from artifacts only (no context bleed).
Write lane-typed entries to AGENTS.md before every budget check.
Exit on: CONVERGED OR DIVERGED OR MAX_ITERS.
Verification rung target: 274177.
```

### 19.3 Security/API Loop Invocation

```
Use phuc-loop v1.0.0 (strict profile) + security gate active.
Goal: <goal touching API or auth>
Halting certificates: [EXACT]
Max iterations: 10
Verification rung target: 65537 (security gate required).
Per iteration: Scout→Solver→Skeptic with prime-safety enforced.
API surface snapshot required before and after loop.
Any breaking change detected → EXIT_BLOCKED.
```

---

*phuc-loop v1.0.0 — Bounded autonomous iteration with halting certificates.*
*Layers on prime-safety + prime-coder + phuc-swarms. Stricter always wins.*
*The Ralph loop made fail-closed.*
