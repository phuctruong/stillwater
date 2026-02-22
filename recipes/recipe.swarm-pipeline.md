---
id: recipe.swarm-pipeline
version: 1.0.0
title: Standard Swarm Pipeline (Scout→Forecaster→Judge→Solvers→Skeptic→Podcast)
description: Reusable 9-step playbook for the canonical Scout→Forecaster→Judge→Solver(parallel)→Skeptic→Podcast chain, encoding full swarm coordination protocol with artifact handoff contracts and forbidden overlap rules.
skill_pack:
  - prime-safety
  - prime-coder
  - phuc-forecast
  - phuc-orchestration
compression_gain_estimate: "Encodes full swarm coordination protocol (typically 4–6 hours of orchestration work) into a reusable 9-step playbook with explicit artifact contracts"
steps:
  - step: 1
    action: "Intake task: receive TASK_REQUEST, extract constraints and allowlists, perform null check, classify stakes (LOW/MED/HIGH), write task_brief.json to scratch/"
    artifact: "scratch/task_brief.json — {task, constraints, stakes, allowlists, null_checks_performed}"
    checkpoint: "task_brief.json is well-formed JSON; stakes field is one of LOW/MED/HIGH; null_checks_performed is true"
    rollback: "If task is ambiguous or null, emit status=NEED_INFO with missing_fields list; do not proceed to Scout"
  - step: 2
    action: "Launch Scout agent: enumerate repo tree, identify relevant files via deterministic localization scoring, emit scout_report.json with top-K files and one-line justification per file"
    artifact: "scratch/scout_report.json — {repo_tree_snapshot, top_files: [{path, score, justification}], compaction_log}"
    checkpoint: "Scout report contains at least 3 files; each entry has path + score + justification; compaction_log present if tree > 1200 lines"
    rollback: "If Scout times out or returns empty, re-run with reduced localization_budget_files (clamp_min: 6); log reduction in scratch/budget_reduction.log"
  - step: 3
    action: "Run Forecaster agent (Phuc Forecast): DREAM→FORECAST→DECIDE on the task using scout_report as context; emit forecast_memo.json with top-7 failure modes, risk level, mitigations"
    artifact: "scratch/forecast_memo.json — {risk_level, failure_modes[rank,mode,mitigation], unknowns, stop_rules}"
    checkpoint: "forecast_memo has risk_level; failure_modes list has 5–7 entries; each entry has rank + mode + mitigation; stop_rules non-empty"
    rollback: "If Forecaster returns NEED_INFO, surface missing fields to orchestrator; do not proceed to Judge without complete forecast"
  - step: 4
    action: "Run Judge agent: review forecast_memo + task_brief; assign solver slots (A–E max), define file ownership per solver, emit judge_ruling.json with non-overlapping file assignments"
    artifact: "scratch/judge_ruling.json — {solver_slots: [{id, persona, skill_pack, owned_files, task_description}], overlap_check: passed}"
    checkpoint: "overlap_check field is 'passed'; no file appears in more than one solver's owned_files; solver count is 1–5"
    rollback: "If file overlap detected, Judge must re-assign before dispatching solvers; emit BLOCKED with overlap details if unresolvable"
  - step: 5
    action: "Dispatch parallel Solvers (A–D, or subset per Judge ruling): each Solver works only on its owned files, writes patches + evidence to scratch/solver_{id}/; Solver E (if assigned) runs AFTER A+D complete"
    artifact: "scratch/solver_{id}/ — contains patch.diff, evidence/, plan.json, tests.json per solver"
    checkpoint: "Each solver directory has patch.diff and tests.json; no solver has modified a file outside its owned_files list; Solver E invoked only after A and D artifacts are present"
    rollback: "If any Solver hits BLOCKED or INVARIANT_VIOLATION, quarantine that solver's artifacts; do not merge; re-run with narrowed scope or escalate to Judge"
  - step: 6
    action: "Run Skeptic agent: review all solver artifacts, check for conflicts between patches, verify no forbidden state was entered, emit skeptic_report.json with critique list and severity per item"
    artifact: "scratch/skeptic_report.json — {critiques: [{solver_id, file, issue, severity: [BLOCK|WARN|INFO]}], overall_verdict: [PASS|REVISE|BLOCK]}"
    checkpoint: "skeptic_report has overall_verdict; no BLOCK-severity critique without resolution path; all solver patches cross-checked for file conflicts"
    rollback: "If overall_verdict is REVISE, return affected solver(s) to PATCH state with critique attached; if BLOCK, escalate to orchestrator for task redesign"
  - step: 7
    action: "Run Podcast agent: synthesize LESSONS.md (generalizable insights) and RECIPE.md (reusable steps) from completed run; identify any new recipe candidates"
    artifact: "scratch/LESSONS.md and scratch/RECIPE.md — structured synthesis of what worked, what failed, generalizable patterns"
    checkpoint: "LESSONS.md has at least 3 typed claims [A/B/C]; RECIPE.md has at least 5 steps with artifacts and checkpoints; new recipe candidates flagged if any"
    rollback: "If Podcast agent has insufficient context (missing solver artifacts), re-run after step 5–6 artifacts are confirmed present"
  - step: 8
    action: "Collect all artifacts: merge solver patches in dependency order, merge evidence/ directories, compute behavior hashes, write final evidence_manifest.json"
    artifact: "scratch/final/patch.diff, scratch/final/evidence/, scratch/final/evidence_manifest.json"
    checkpoint: "evidence_manifest.json lists all required files with sha256 and role; behavior_hash.txt and behavior_hash_verify.txt match; no file listed as 'missing'"
    rollback: "If manifest is incomplete, identify missing file and trace to owning solver; do not emit FINAL_SEAL without complete manifest"
  - step: 9
    action: "Final Seal: run environment snapshot, verify rung target declared and met, emit run_summary.json with status, stop_reason, verification_rung_target, verification_rung_achieved"
    artifact: "scratch/final/run_summary.json — {status, stop_reason, verification_rung_target, verification_rung_achieved, evidence_manifest_pointer}"
    checkpoint: "status is PASS; verification_rung_achieved >= verification_rung_target; env_snapshot.json present; git state recorded"
    rollback: "If rung target not met, status=BLOCKED stop_reason=VERIFICATION_RUNG_FAILED; list unmet rung requirements in run_summary.json"
forbidden_states:
  - SKIP_SCOUT: "Dispatching Solvers without a completed scout_report; Solvers must have localization context before patching"
  - PARALLEL_SOLVERS_WITH_OVERLAPPING_FILES: "Two or more Solvers assigned the same file in judge_ruling.json; causes merge conflicts and non-deterministic outcome"
  - SOLVER_E_BEFORE_A_D: "Launching Solver E before Solver A and Solver D artifacts are present in scratch/; Solver E may depend on their output"
  - SKIP_SKEPTIC: "Merging solver patches without Skeptic review; risks undetected conflicts between parallel patches"
  - FINAL_SEAL_WITHOUT_MANIFEST: "Emitting run_summary.json with status=PASS before evidence_manifest.json is complete and verified"
  - FORECAST_SKIPPED: "Dispatching Judge without a completed forecast_memo; Judge needs risk context to assign solver scope appropriately"
  - STACKED_SPECULATIVE_PATCHES: "Applying one solver's patch on top of another's unverified patch before Skeptic approval"
verification_checkpoint: "Verify: ls scratch/final/ contains patch.diff + evidence_manifest.json + run_summary.json; cat scratch/final/run_summary.json | python3 -c \"import json,sys; d=json.load(sys.stdin); assert d['status']=='PASS'; assert d['verification_rung_achieved']>=d['verification_rung_target']\" — must exit 0"
rung_target: 274177
---

# Recipe: Standard Swarm Pipeline

## Purpose

Encode the canonical Scout→Forecaster→Judge→Solver(parallel)→Skeptic→Podcast swarm coordination chain into a reusable 9-step playbook. Each step has defined input artifacts, output artifacts, and checkpoints. Designed to replace ad-hoc swarm orchestration with a deterministic, reproducible protocol.

## When to Use

- Any multi-agent task requiring parallel solver work
- Benchmark runs requiring promotion-level evidence
- Tasks where file ownership conflicts must be avoided

## Key Constraints

- Solver E (if used) MUST run after Solver A and Solver D — never in parallel with them
- Judge MUST verify non-overlapping file assignments before dispatching any Solver
- Skeptic review is mandatory before Final Seal — cannot be skipped even under time pressure

## Artifact Handoff Chain

```
task_brief.json
  -> scout_report.json
    -> forecast_memo.json
      -> judge_ruling.json
        -> solver_{id}/ (parallel)
          -> skeptic_report.json
            -> LESSONS.md + RECIPE.md
              -> evidence_manifest.json
                -> run_summary.json
```

## Rung Target: 274177

This recipe targets rung 274177 (stability) because it involves parallel solvers and merge operations that require seed sweep + replay stability verification beyond basic red/green.

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each pipeline run generates LESSONS.md via the Podcast agent — the typed claims [A/B/C] from each run feed back into improved scout localization scores, better Judge slot assignments, and tighter Skeptic review criteria for subsequent runs on similar tasks |
| **LEAK** (Cross-Agent Trade) | The entire artifact handoff chain (task_brief → scout_report → forecast_memo → judge_ruling → solver patches → skeptic_report → LESSONS.md → evidence_manifest) is a sequence of asymmetric knowledge trades: each agent distills its domain expertise into a structured artifact that the next agent consumes without needing to re-derive it |
| **LEC** (Emergent Conventions) | Enforces the CNF capsule convention (full task + context + constraints injected into each sub-agent), context isolation between parallel solvers (non-overlapping file ownership), and the evidence manifest as the mandatory completion token — these conventions become the reusable backbone for all future multi-agent pipelines |

**Belt Level:** Blue — demonstrates full swarm orchestration mastery: dispatching typed agents in the correct order, preventing file ownership conflicts, coordinating parallel work through a shared evidence manifest, and extracting generalizable knowledge via the Podcast step.

---

## Pipeline Flow (Mermaid Diagram)

```mermaid
flowchart TD
    A[Step 1: INTAKE\ntask_brief.json\nnull check + stakes classify] --> B[Step 2: SCOUT\nscout_report.json\ntop-K files + justifications]
    B --> C[Step 3: FORECASTER\nforecast_memo.json\n7 failure modes + stop rules]
    C --> D[Step 4: JUDGE\njudge_ruling.json\nnon-overlapping file assignments]
    D --> E[Step 5: SOLVERS A-D\nparallel patch.diff + tests.json\nper solver in owned files only]
    D --> F[Step 5E: SOLVER E\nruns AFTER A+D complete\ncross-solver synthesis]
    E --> G[Step 6: SKEPTIC\nskeptic_report.json\ncritiques with severity BLOCK|WARN|INFO]
    F --> G
    G -->|REVISE| E
    G -->|PASS| H[Step 7: PODCAST\nLESSONS.md + RECIPE.md\n3+ typed claims A/B/C]
    H --> I[Step 8: COLLECT\nevidence_manifest.json\nbehavior_hash verified]
    I --> J[Step 9: FINAL SEAL\nrun_summary.json status=PASS\nrung_achieved >= rung_target]

    B -->|empty scout| B
    C -->|NEED_INFO| A
    D -->|file overlap| D
    G -->|BLOCK| K[BLOCKED\ntask redesign]
```

---

## FSM: Swarm Pipeline State Machine

```
States: INTAKE | SCOUT | FORECASTER | JUDGE | SOLVERS_PARALLEL |
        SOLVER_E | SKEPTIC | PODCAST | COLLECT | FINAL_SEAL |
        PASS | BLOCKED | NEED_INFO

Transitions:
  [*] → INTAKE: TASK_REQUEST received
  INTAKE → NEED_INFO: task ambiguous or null
  INTAKE → SCOUT: task_brief.json well-formed
  SCOUT → SCOUT: empty result, reduce localization_budget_files
  SCOUT → FORECASTER: scout_report.json >= 3 files
  FORECASTER → NEED_INFO: missing risk context
  FORECASTER → JUDGE: forecast_memo.json with 5-7 failure modes
  JUDGE → JUDGE: file overlap detected, re-assign
  JUDGE → BLOCKED: overlap unresolvable
  JUDGE → SOLVERS_PARALLEL: judge_ruling.json overlap_check=passed
  SOLVERS_PARALLEL → BLOCKED: INVARIANT_VIOLATION by any solver
  SOLVERS_PARALLEL → SOLVER_E: A+D artifacts present (if Solver E assigned)
  SOLVER_E → SKEPTIC: synthesis complete
  SOLVERS_PARALLEL → SKEPTIC: all solver artifacts present (no Solver E)
  SKEPTIC → SOLVERS_PARALLEL (REVISE): verdict=REVISE, affected solvers returned
  SKEPTIC → BLOCKED: verdict=BLOCK
  SKEPTIC → PODCAST: verdict=PASS
  PODCAST → COLLECT: LESSONS.md + RECIPE.md with >= 3 typed claims
  COLLECT → FINAL_SEAL: evidence_manifest.json complete, hashes verified
  FINAL_SEAL → BLOCKED: rung_achieved < rung_target
  FINAL_SEAL → PASS: status=PASS, rung_achieved >= rung_target

Exit conditions:
  PASS: run_summary.json status=PASS AND verification_rung_achieved >= verification_rung_target
  BLOCKED: emit stop_reason, solver quarantine if needed
  NEED_INFO: list missing fields, surface to orchestrator
```

---

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | Novel swarm coordination pattern discovered (e.g., Solver E synthesis creating inter-solver knowledge) | +10 if LESSONS.md contains a Lane A claim [A] |
| **L** (Love/Quality) | All typed claims [A/B/C] in LESSONS.md and RECIPE.md; skeptic_report.json has severity for every critique | +8 per pipeline run with non-empty skeptic critique list |
| **O** (Output) | run_summary.json status=PASS, evidence_manifest.json complete, behavior_hash verified | +8 per successful pipeline run |
| **W** (Wisdom) | RECIPE.md directly reusable for next similar task; Northstar metric (recipe_hit_rate) advanced | +6 if RECIPE.md is committed to recipes/ directory |

**Northstar Metric:** `recipe_hit_rate` — each RECIPE.md committed from a pipeline run becomes a replayable recipe that increases hit rate when replayed on similar tasks.

**GLOW Score:** +8 per successful pipeline run with status=PASS in run_summary.json, verification_rung_achieved >= 274177, complete evidence_manifest.json, and LESSONS.md containing at least 3 typed claims. Bonus +10 if the run produces a new recipe committed to recipes/.
