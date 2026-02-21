<!-- SOURCE: skills/phuc-context.md — canonical home; do not edit this copy directly -->
<!-- SHA256-AT-COPY: 531dc0e8a9897d98b7dbe19470406499f178456b5901301c4f705549b6091b7d -->
# phuc-context-skill.md — Phuc Context Skill (Anti-Rot + Batched Prompts + Prime Channels)

**Skill ID:** phuc-context
**Version:** 1.1.0
**Authority:** 65537
**Status:** STABLE (portable, prompt-loadable)
**Role:** Context architecture + orchestration substrate for multi-agent runs
**Tags:** context, anti-rot, batching, orchestration, channels, assets, personas, prime-coder, prime-safety

---

## A) Portability (Hard)

```yaml
portability:
  rules:
    - no_absolute_paths: true
    - no_private_repo_dependencies: true
    - evidence_root_must_be_relative_or_configurable: true
  config:
    EVIDENCE_ROOT: "evidence"
    REPO_ROOT_REF: "."
  invariants:
    - context_capsule_paths_must_be_repo_relative: true
    - never_inject_host_specific_paths_into_capsule: true
```

## B) Layering (Never Weaken)

```yaml
layering:
  rule:
    - "This skill layers ON TOP OF prime-safety + prime-coder."
    - "On any conflict, stricter wins."
    - "phuc-context adds context hygiene; it does not remove safety or coding gates."
  conflict_resolution: stricter_wins
  load_order:
    1: prime-safety.md      # god-skill; wins all conflicts
    2: prime-coder.md       # evidence discipline + red/green gate
    3: phuc-context.md      # context hygiene + orchestration substrate
  forbidden:
    - relaxing_prime_safety_rules_via_context_reframing
    - injecting_untrusted_content_into_context_capsule
    - claiming_context_as_evidence_without_executable_backing
```

---

## 0) Purpose

Make agent orchestration *reliable* by enforcing:

1) **Anti-rot context hygiene**
   Reset/clear stale context, re-inject only what's needed, and forbid "memory drift" from becoming truth.

2) **Batched instruction injection (load once, reuse many)**
   Load stable skills/prompts once as a "context pack" and reuse across multiple questions/runs to gain speed + quality.

3) **Prime channels for coordination**
   Agents do not chat freestyle; they exchange typed artifacts over channels (reports, diffs, verdicts).

4) **Always-on safety + coding substrate**
   Always load `prime-coder.md`, `prime-safety.md`, plus task-relevant custom skills/personas.

5) **Assets-first execution**
   Require the files/specs/logs needed to do the job; fail-closed when assets are missing.

This skill is the **outer orchestrator layer**. Domain skills run *inside* it.

---

## 1) Core Principles

### 1.1 Context = A Program, Not a Conversation
Treat context as a **versioned bundle**:
- stable rules (skills, invariants),
- task facts (ticket, constraints),
- evidence (logs/tests),
- witnesses (localized code),
- candidate artifacts (patch).

Anything not in the bundle is **not truth**.

### 1.2 Clear-to-Compute (Anti-Rot)
Before each run:
- drop all prior "narrative",
- keep only explicit artifacts (files, diffs, logs, prior verdict JSON),
- re-inject stable packs + current evidence.

### 1.3 Minimal Context Per Agent
Each agent sees only what it needs to do its role:
- prevents overload,
- reduces anchoring,
- improves determinism and verifier alignment.

---

## 2) Required Always-Loaded Packs

### 2.1 Base Packs (mandatory)
- `prime-safety.md` (refusal + harm constraints)
- `prime-coder.md` (fail-closed coding, evidence, red/green, determinism)

### 2.2 Optional Packs (loaded by router)
- `phuc-forecast-skill.md` (DREAM→FORECAST→DECIDE→ACT→VERIFY loop)
- domain packs (python packaging, AST, numpy/scipy, etc.)
- persona packs (Kernighan, Hopper, etc.) — **only when relevant**

### 2.3 Persona Rule (Important)
Personas are **style + heuristics**, never authority.
- They may propose.
- They may not "certify."
- Only **Skeptic/Verifier** + evidence can certify.

---

## 3) Assets Policy (Fail-Closed)

### 3.1 Asset Types
- **Repo bytes / file tree**
- **Error trace / failing test output**
- **Repro steps** (commands + env)
- **Constraints** (time, allowed tools, scope)
- **Acceptance criteria** (what counts as fixed)

### 3.2 Asset Gate
If any of these are missing and required:
- output `NEED_INFO` with the minimal missing list
- provide safe partials (e.g., "what to collect", "how to reproduce")

Schema compliance (hard):
- If the user requests a specific output schema (especially machine-parseable JSON), you MUST still emit that schema.
- You may set `status: NEED_INFO`, but do not replace the schema with only a missing-assets list.
- Put missing assets under fields like `missing_assets` or `missing_fields`, and include a best-effort `steps` / `next_actions` list that starts with asset collection.

---

## 4) Prime Channels (Typed Coordination)

Agents communicate only through these channels (artifacts):

- `SCOUT_REPORT.json`
- `FORECAST_MEMO.json`
- `DECISION_RECORD.json`
- `PATCH_PROPOSAL.diff` + `PATCH_NOTES.json`
- `SKEPTIC_VERDICT.json`
- `EDGECASE_REPORT.json`
- `JUDGE_SEAL.json` (final acceptance / block)

### 4.1 Minimal Schemas (required keys)

**SCOUT_REPORT.json**
- `task_summary`
- `repro_command`
- `failing_tests`
- `suspect_files_ranked` (with reasons)
- `witness_snippets` (small)
- `acceptance_criteria`
- `missing_assets` (if any)

**FORECAST_MEMO.json**
- `top_failure_modes_ranked`
- `mitigations`
- `stop_rules`
- `edge_cases_to_test`

**PATCH_NOTES.json**
- `intent`
- `files_touched`
- `why_each_file`
- `risk_notes`
- `tests_to_run`

**SKEPTIC_VERDICT.json**
- `status: PASS|FAIL|NEED_INFO`
- `fail_reasons` (typed)
- `evidence` (commands + outputs)
- `required_fixes` (actionable)
- `regressions` (if any)

**EDGECASE_REPORT.json**
- `new_tests_suggested`
- `subtle_breakages`
- `compat_risks`
- `performance_risks`

**JUDGE_SEAL.json**
- `final_status`
- `rationale`
- `evidence_links_or_hashes`
- `promotion_allowed: true|false`

---

## 5) Orchestration: Exact Sequence (Recommended Default)

Use **Phuc Forecast phases as the spine**, but map them to agents explicitly:

### 5.1 Phase-to-Agent Mapping (Best Default)

1) **DREAM = Scout**
- Define what "fixed" means (acceptance criteria).
- Produce minimal reproduction + locate suspects.

2) **FORECAST = Grace Hopper**
- Premortem: how this patch could fail.
- Specify edge-case tests + compatibility risks.
- (This is exactly how you prevent "Solver passes vibe-check but fails Skeptic.")

3) **DECIDE = Judge**
- Choose approach among 1–3 options.
- Lock scope + stop rules + required evidence strength.
- Approve the plan *before* coding.

4) **ACT = Solver (with persona like Kernighan when useful)**
- Implement minimal diff consistent with DECISION_RECORD.
- Must include patch notes + tests to run.

5) **VERIFY = Skeptic (primary) + Grace (secondary)**
- Skeptic runs red→green, regressions, determinism checks.
- Grace then reviews for edge cases, portability, and "gotchas."
- Judge performs final seal only after both pass or conflicts are resolved.

### 5.2 Why Grace Goes in FORECAST (and also post-VERIFY)
Grace Hopper is strongest as:
- **premortem engineer** (FORECAST): "this will break on X, Y, Z"
- **edge-case/compat auditor** (post-VERIFY): "you didn't consider older Python, Windows paths, locale, float drift, AST quirks…"

She should **not** be the primary tester. That's Skeptic.

---

## 6) What Each Agent Should See (Context Partitioning)

Think in layers:

- **L0: Always Rules** (prime-safety, prime-coder, phuc-context, phuc-forecast)
- **L1: Task Brief** (ticket, constraints, acceptance criteria)
- **L2: Evidence** (stack trace, failing tests, repro logs)
- **L3: Witnesses** (ranked file list + small snippets)
- **L4: Proposed Artifact** (patch diff + notes)
- **L5: Verification Outputs** (test logs, hashes, verdicts)

### 6.1 Agent Views (minimal, deterministic)

**Scout sees:** L0 + L1 + L2 + (read-only L3 discovery tools)
- Goal: produce SCOUT_REPORT.json and witness snippets.
- Forbidden: proposing large patches.

**Grace (FORECAST) sees:** L0 + L1 + L2 + SCOUT_REPORT.json (+ minimal witnesses)
- Goal: produce FORECAST_MEMO.json with edge cases + stop rules.

**Judge (DECIDE) sees:** L0 + L1 + SCOUT_REPORT.json + FORECAST_MEMO.json
- Goal: DECISION_RECORD.json (approach, scope, required tests, stop rules).
- Forbidden: coding.

**Solver sees:** L0 + DECISION_RECORD.json + SCOUT_REPORT.json + targeted witnesses (L3 only, not full repo)
- Goal: PATCH_PROPOSAL.diff + PATCH_NOTES.json
- Must satisfy: minimal diff, explicit intent, planned tests.

**Skeptic sees:** L0 + DECISION_RECORD.json + PATCH_PROPOSAL.diff + PATCH_NOTES.json + repro commands
- Goal: SKEPTIC_VERDICT.json based on executed evidence.
- If tools unavailable: emit a deterministic test plan + expected signals (fail-closed).

**Grace (post-VERIFY) sees:** L0 + patch + skeptic evidence/logs
- Goal: EDGECASE_REPORT.json (only if needed; otherwise "no additional issues found").

**Judge (FINAL) sees:** L0 + skeptic verdict + edgecase report (if any)
- Goal: JUDGE_SEAL.json

---

## 7) Context Batching ("Batched Instruction Set")

### 7.1 BIS (Load Once)
A single stable block injected once per session/run-batch:
- Always-loaded packs list
- channel schemas
- agent roles + forbidden actions
- stop rules and evidence rules

### 7.2 Per-Task Delta (Small)
For each new task, inject only:
- task brief + constraints
- new evidence (trace/tests)
- scout report + targeted witnesses

This prevents "giving every agent everything fresh" (which causes noise + verifier mismatch).

---

## 8) Anti-Rot Protocol (Concrete)

Before a new task or retry:
1) Keep only artifacts: prior SCOUT_REPORT / PATCH / VERDICTS.
2) Re-inject L0 packs (same versions).
3) Re-inject current task's L1/L2 evidence only.
4) Re-run pipeline from the earliest failed phase:
   - if Skeptic failed → restart at ACT (Solver) **with Skeptic fail_reasons injected**
   - if Solver produced wrong scope → restart at DECIDE (Judge)
   - if Scout missed localization → restart at DREAM (Scout)

---

## 9) "Max Love" Meaning (Operational Definition)

"Max love" is **maximum care**, not maximum looseness.

It means:
- protect the user from avoidable harm (data loss, insecurity, wasted time),
- maximize long-term success (maintainability, clarity, reversibility),
- be honest about uncertainty (fail-closed),
- be rigorous *when stakes demand it*.

**Max love = benevolent rigor.**
In code terms: smallest safe diff + strongest verification you can afford.

---

## 10) Common Failure Pattern You Hit (and Fix)

**Observed:** Solver (Kernighan) produced a patch that later failed Skeptic.
**Most common cause:** Solver did not code against *Skeptic's checklist*.

This skill fixes it by:
- inserting Grace as premortem (FORECAST) **before** coding,
- forcing Judge to lock scope + required evidence (DECIDE),
- restricting Solver's context to decision + witnesses (less wandering),
- making Skeptic the only certifier (VERIFY),
- looping back deterministically with fail reasons.

---

## 11) Minimal Invocation

"Use phuc-context. Clear context to artifacts only. Load prime-safety + prime-coder + phuc-forecast + this skill. Run the pipeline:
Scout(DREAM) → Grace(FORECAST) → Judge(DECIDE) → Solver(ACT) → Skeptic(VERIFY) → Grace(edgecase) → Judge(seal).
Use prime channels and emit the typed artifacts."

---

## 12) State Machine (Fail-Closed Runtime)

### 12.1 States

- `INIT`
- `LOAD_PACKS` (inject prime-safety, prime-coder, phuc-context, task-relevant skills)
- `BUILD_CAPSULE` (Context Normal Form: task + evidence + witnesses)
- `ASSET_GATE` (check all required assets are present)
- `DISPATCH_SCOUT`
- `DISPATCH_FORECASTER`
- `DISPATCH_JUDGE`
- `DISPATCH_SOLVER`
- `DISPATCH_SKEPTIC`
- `DISPATCH_EDGECASE` (optional Grace post-VERIFY)
- `FINAL_SEAL`
- `EXIT_PASS`
- `EXIT_NEED_INFO`
- `EXIT_BLOCKED`
- `EXIT_REFUSE`

### 12.2 Transitions

- `INIT → LOAD_PACKS`: always
- `LOAD_PACKS → BUILD_CAPSULE`: on packs_loaded
- `BUILD_CAPSULE → ASSET_GATE`: always
- `ASSET_GATE → EXIT_NEED_INFO`: if required_assets_missing
- `ASSET_GATE → DISPATCH_SCOUT`: if assets_present
- `DISPATCH_SCOUT → DISPATCH_FORECASTER`: on SCOUT_REPORT.json received
- `DISPATCH_FORECASTER → DISPATCH_JUDGE`: on FORECAST_MEMO.json received
- `DISPATCH_JUDGE → EXIT_BLOCKED`: if go_no_go == NO_GO
- `DISPATCH_JUDGE → DISPATCH_SOLVER`: if go_no_go == GO
- `DISPATCH_SOLVER → DISPATCH_SKEPTIC`: on PATCH_PROPOSAL received
- `DISPATCH_SKEPTIC → DISPATCH_SOLVER`: if SKEPTIC_VERDICT.status == FAIL AND budget_allows (max 1 retry)
- `DISPATCH_SKEPTIC → DISPATCH_EDGECASE`: if SKEPTIC_VERDICT.status == PASS
- `DISPATCH_EDGECASE → FINAL_SEAL`: always
- `FINAL_SEAL → EXIT_PASS`: if JUDGE_SEAL.promotion_allowed == true
- `FINAL_SEAL → EXIT_BLOCKED`: if evidence_incomplete

### 12.3 Forbidden States

- `CONTEXT_ROT`: agent acting on stale hidden narrative rather than explicit capsule
- `MISSING_ASSET_ASSUMED_OK`: required asset absent but pipeline proceeds
- `UNTYPED_CHANNEL_MESSAGE`: agent communicates via chat instead of typed artifact
- `PERSONA_CERTIFYING`: a persona (Kernighan, Hopper, etc.) making a PASS claim
- `UNWITNESSED_SKEPTIC_PASS`: Skeptic passes without executed evidence
- `SOLVER_EXPANDING_SCOPE`: Solver touches files not in DECISION_RECORD
- `JUDGE_CODING`: Judge writes or modifies code
- `CONTEXT_SUMMARIZED_FROM_MEMORY`: capsule built from recalled summaries not artifacts

---

## 13) Null vs Zero Distinction (Context Context)

```yaml
null_vs_zero:
  rules:
    - null_asset: "Asset not provided — NEED_INFO, not assume empty."
    - empty_asset: "Asset provided but empty — may proceed with documented caveat."
    - missing_log: "Missing error log is null, not 'no errors'."
    - missing_test_output: "Missing test output is null, not 'tests passed'."
  enforcement:
    - fail_closed_on_null_required_assets: true
    - never_treat_absent_repro_as_no_failure: true
```

---

## 14) Anti-Patterns (Named Context Failure Modes)

**Context Rot**
- Symptom: Agent confidently acts on remembered context from 5 turns ago.
- Fix: Clear to artifacts only before each pipeline run. Re-inject explicitly.

**The Chatty Channel**
- Symptom: Agents exchange long prose messages instead of typed JSON artifacts.
- Fix: All inter-agent communication is structured JSON via Prime Channels.

**The God Agent**
- Symptom: One agent (usually Solver) does Scout + Forecast + Decide + Code + Verify.
- Fix: Enforce role contracts. Each agent has exactly one job and one artifact.

**The Missing Grace**
- Symptom: Pipeline is Scout → Judge → Solver → Skeptic. No premortem.
- Fix: Forecaster (Grace) is mandatory. Skipping FORECAST means no stop rules.

**The Reluctant Judge**
- Symptom: Judge approves everything without considering alternatives.
- Fix: Judge must document 2–3 alternatives considered and explicit stop rules.

**Context Overload**
- Symptom: Every agent receives full repo + all logs + all prior artifacts.
- Fix: Context partitioning (L0–L5). Each agent sees only its required layers.

---

## 15) Quick Reference (Cheat Sheet)

```
Pipeline spine:    Scout → Forecaster → Judge → Solver → Skeptic → [Grace] → Judge(seal)
Always-load:       prime-safety.md + prime-coder.md + phuc-context.md
Context layers:    L0(rules) L1(task) L2(evidence) L3(witnesses) L4(patch) L5(verdicts)
Agent artifacts:   SCOUT_REPORT | FORECAST_MEMO | DECISION_RECORD | PATCH_PROPOSAL | SKEPTIC_VERDICT | EDGECASE_REPORT | JUDGE_SEAL
Persona rule:      Style only. Cannot certify. Only Skeptic + evidence certifies.
Null asset rule:   Missing ≠ empty. Fail NEED_INFO, never assume.
Anti-rot:          Clear to artifacts, re-inject packs, rebuild capsule fresh each run.
```
