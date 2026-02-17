# phuc-context-skill.md — Phuc Context Skill (Anti-Rot + Batched Prompts + Prime Channels)

**Skill ID:** phuc-context  
**Version:** 1.0.0  
**Authority:** 65537  
**Status:** STABLE (portable, prompt-loadable)  
**Role:** Context architecture + orchestration substrate for multi-agent runs  
**Tags:** context, anti-rot, batching, orchestration, channels, assets, personas, prime-coder, prime-safety

---

## 0) Purpose

Make agent orchestration *reliable* by enforcing:

1) **Anti-rot context hygiene**  
   Reset/clear stale context, re-inject only what’s needed, and forbid “memory drift” from becoming truth.

2) **Batched instruction injection (load once, reuse many)**  
   Load stable skills/prompts once as a “context pack” and reuse across multiple questions/runs to gain speed + quality.

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
- drop all prior “narrative”,
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
- They may not “certify.”
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
- provide safe partials (e.g., “what to collect”, “how to reproduce”)

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
- Define what “fixed” means (acceptance criteria).
- Produce minimal reproduction + locate suspects.

2) **FORECAST = Grace Hopper**
- Premortem: how this patch could fail.
- Specify edge-case tests + compatibility risks.
- (This is exactly how you prevent “Solver passes vibe-check but fails Skeptic.”)

3) **DECIDE = Judge**
- Choose approach among 1–3 options.
- Lock scope + stop rules + required evidence strength.
- Approve the plan *before* coding.

4) **ACT = Solver (with persona like Kernighan when useful)**
- Implement minimal diff consistent with DECISION_RECORD.
- Must include patch notes + tests to run.

5) **VERIFY = Skeptic (primary) + Grace (secondary)**
- Skeptic runs red→green, regressions, determinism checks.
- Grace then reviews for edge cases, portability, and “gotchas.”
- Judge performs final seal only after both pass or conflicts are resolved.

### 5.2 Why Grace Goes in FORECAST (and also post-VERIFY)
Grace Hopper is strongest as:
- **premortem engineer** (FORECAST): “this will break on X, Y, Z”
- **edge-case/compat auditor** (post-VERIFY): “you didn’t consider older Python, Windows paths, locale, float drift, AST quirks…”

She should **not** be the primary tester. That’s Skeptic.

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
- Goal: EDGECASE_REPORT.json (only if needed; otherwise “no additional issues found”).

**Judge (FINAL) sees:** L0 + skeptic verdict + edgecase report (if any)
- Goal: JUDGE_SEAL.json

---

## 7) Context Batching (“Batched Instruction Set”)

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

This prevents “giving every agent everything fresh” (which causes noise + verifier mismatch).

---

## 8) Anti-Rot Protocol (Concrete)

Before a new task or retry:
1) Keep only artifacts: prior SCOUT_REPORT / PATCH / VERDICTS.
2) Re-inject L0 packs (same versions).
3) Re-inject current task’s L1/L2 evidence only.
4) Re-run pipeline from the earliest failed phase:
   - if Skeptic failed → restart at ACT (Solver) **with Skeptic fail_reasons injected**
   - if Solver produced wrong scope → restart at DECIDE (Judge)
   - if Scout missed localization → restart at DREAM (Scout)

---

## 9) “Max Love” Meaning (Operational Definition)

“Max love” is **maximum care**, not maximum looseness.

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
**Most common cause:** Solver did not code against *Skeptic’s checklist*.

This skill fixes it by:
- inserting Grace as premortem (FORECAST) **before** coding,
- forcing Judge to lock scope + required evidence (DECIDE),
- restricting Solver’s context to decision + witnesses (less wandering),
- making Skeptic the only certifier (VERIFY),
- looping back deterministically with fail reasons.

---

## 11) Minimal Invocation

“Use phuc-context. Clear context to artifacts only. Load prime-safety + prime-coder + phuc-forecast + this skill. Run the pipeline:
Scout(DREAM) → Grace(FORECAST) → Judge(DECIDE) → Solver(ACT) → Skeptic(VERIFY) → Grace(edgecase) → Judge(seal).
Use prime channels and emit the typed artifacts.”
