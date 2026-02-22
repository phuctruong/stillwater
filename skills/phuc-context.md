# phuc-context-skill.md — Phuc Context Skill (Anti-Rot + Batched Prompts + Prime Channels)

**Skill ID:** phuc-context
**Version:** 1.3.0
**Authority:** 65537
**Status:** STABLE (portable, prompt-loadable)
**Role:** Context architecture + orchestration substrate for multi-agent runs
**Tags:** context, anti-rot, batching, orchestration, channels, assets, personas, prime-coder, prime-safety

---

## MW) MAGIC_WORD_MAP — Prime Factorization Map for phuc-context
Navigation anchors for 97% context compression via phuc-magic-words

```yaml
MAGIC_WORD_MAP:
  # TRUNK (Tier 0) — universal coordinates anchoring this skill
  primary_trunk_words:
    integrity:      "Context = program not conversation — any state not in the artifact bundle is not truth (→ §1.1 Core Principles)"
    boundary:       "Context partitioning L0-L5: each agent sees only what it needs for its role (→ §6 Context Partitioning)"
    alignment:      "Every agent has one role, one artifact, one channel — no God Agents (→ §14 anti-patterns)"
    constraint:     "Required assets gate: if missing → NEED_INFO; pipeline cannot proceed (→ §3 Assets Policy)"

  # BRANCH (Tier 1) — structural concepts
  branch_words:
    context:        "versioned artifact bundle: stable_rules + task_facts + evidence + witnesses + candidate_artifacts (→ §1.1)"
    compaction:     "anti-rot: clear to artifacts only before each run, re-inject packs + evidence (→ §8 Anti-Rot Protocol)"
    memory:         "only explicit artifacts are truth; conversation recall is forbidden as truth source (→ §1.2 Clear-to-Compute)"
    capsule:        "CNF capsule = L0+L1+L2 re-injected each run from artifact bundle (→ §7 Context Batching)"
    swarm:          "5-6 agent pipeline: Scout→Forecaster→Judge→Solver→Skeptic→[Grace]→Judge(seal) (→ §5.1)"
    evidence:       "typed artifacts: SCOUT_REPORT | FORECAST_MEMO | DECISION_RECORD | PATCH_PROPOSAL | SKEPTIC_VERDICT | JUDGE_SEAL"
    governance:     "prime channels only — no freestyle chat between agents; typed JSON artifacts (→ §4 Prime Channels)"

  # CONCEPT (Tier 2) — operational nodes
  concept_words:
    artifact:       "all inter-agent communication is typed JSON artifacts via Prime Channels (→ §4)"
    dispatch:       "Scout→Forecaster→Judge→Solver→Skeptic sequence; each agent dispatched with its layer only"
    persona:        "style heuristic only (Kernighan, Hopper) — NEVER certifies PASS; only Skeptic+evidence certifies"
    drift:          "Context Rot anti-pattern: agent acts on stale narrative from prior turns (→ §14 anti-patterns)"
    state_machine:  "INIT→LOAD_PACKS→BUILD_CAPSULE→ASSET_GATE→...→FINAL_SEAL (→ §12 State Machine)"
    skill:          "L0 = always-loaded packs: prime-safety + prime-coder + phuc-context (→ §2 Required Packs)"
    overflow:       "Context Overload anti-pattern: every agent receives full repo + all logs (→ §14 anti-patterns)"

  # LEAF (Tier 3) — domain-specific
  leaf_words:
    context_rot:    "FORBIDDEN_STATE: agent acting on stale hidden narrative rather than explicit capsule"
    missing_grace:  "Anti-pattern: pipeline skips FORECAST (Grace Hopper) — means no premortem, no stop rules"
    chatty_channel: "Anti-pattern: agents exchange prose instead of typed JSON artifacts"
    god_agent:      "Anti-pattern: one agent (Solver) does Scout+Forecast+Decide+Code+Verify all at once"
    reluctant_judge: "Anti-pattern: Judge approves everything without documenting alternatives considered"
    l0_layers:      "L0=rules(prime-safety+prime-coder+phuc-context) | L1=task | L2=evidence | L3=witnesses | L4=patch | L5=verdicts"

  # PRIME FACTORIZATIONS of key context concepts
  prime_factorizations:
    anti_rot_protocol:    "integrity × compaction × memory — clear to artifacts, re-inject packs, rebuild capsule fresh"
    context_as_program:   "integrity × boundary × alignment — versioned bundle; nothing outside it is truth"
    context_partitioning: "boundary × alignment × constraint — L0-L5 layers; each agent sees only its required layers"
    prime_channels:       "governance × integrity × boundary — typed artifacts only; no freestyle prose between agents"
    capsule_rebuild:      "integrity × compression × causality — artifacts only; drop all prior narrative prose"
    asset_gate:           "constraint × integrity × causality — missing asset = NEED_INFO; never assume empty = OK"
    agent_role_contract:  "alignment × boundary × governance — one role, one artifact, one lane per agent"

  # TRIANGLE LAW ANNOTATIONS (REMIND/VERIFY/ACKNOWLEDGE)
  triangle_law:
    before_pipeline_run:
      REMIND:      "Clear to artifacts: drop all prior narrative; keep only explicit artifact bundles"
      VERIFY:      "All required assets present? (SCOUT_REPORT, repro logs, acceptance criteria)"
      ACKNOWLEDGE: "Re-inject L0 packs + current L1/L2 → proceed from earliest failed phase"
    on_context_drift:
      REMIND:      "Is agent acting on recalled narrative or explicit capsule?"
      VERIFY:      "Check: was context rebuilt from artifacts this iteration? (not from 'what we discussed')"
      ACKNOWLEDGE: "If drift detected → emit CONTEXT_ROT; clear to artifacts; re-inject"
    on_persona_certifying:
      REMIND:      "Personas are style only — Kernighan, Hopper, etc. cannot certify PASS"
      VERIFY:      "Is the PASS claim coming from Skeptic with executed evidence, or from a persona?"
      ACKNOWLEDGE: "If persona is certifying → PERSONA_CERTIFYING forbidden state → require Skeptic verification"
```

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

## 0) Purpose [context × integrity × boundary × alignment]

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

## 1) Core Principles [context × integrity × boundary × memory]

### 1.1 Context = A Program, Not a Conversation [integrity × boundary × memory]
Treat context as a **versioned bundle**:
- stable rules (skills, invariants),
- task facts (ticket, constraints),
- evidence (logs/tests),
- witnesses (localized code),
- candidate artifacts (patch).

Anything not in the bundle is **not truth**.

### 1.2 Clear-to-Compute (Anti-Rot) [compaction × integrity × memory]
<!-- TRIANGLE: REMIND(prior narrative) → VERIFY(artifacts only kept) → ACKNOWLEDGE(re-inject packs + evidence) -->
Before each run:
- drop all prior “narrative”,
- keep only explicit artifacts (files, diffs, logs, prior verdict JSON),
- re-inject stable packs + current evidence.

### 1.3 Minimal Context Per Agent [boundary × alignment × constraint]
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

## 3) Assets Policy (Fail-Closed) [constraint × integrity × boundary]

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

## 4) Prime Channels (Typed Coordination) [governance × boundary × integrity × evidence]

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

## 5) Orchestration: Exact Sequence (Recommended Default) [swarm × alignment × boundary × dispatch]

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

## 6) What Each Agent Should See (Context Partitioning) [boundary × alignment × constraint]
<!-- L0=rules | L1=task | L2=evidence | L3=witnesses | L4=patch | L5=verdicts — each agent gets only its layers -->

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

## 7) Context Batching (“Batched Instruction Set”) [capsule × compaction × memory]

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

## 8) Anti-Rot Protocol (Concrete) [compaction × integrity × memory × boundary]
<!-- TRIANGLE: REMIND(artifacts only) → VERIFY(L0 packs re-injected) → ACKNOWLEDGE(restart from earliest failed phase) -->

Before a new task or retry:
1) Keep only artifacts: prior SCOUT_REPORT / PATCH / VERDICTS.
2) Re-inject L0 packs (same versions).
3) Re-inject current task’s L1/L2 evidence only.
4) Re-run pipeline from the earliest failed phase:
   - if Skeptic failed → restart at ACT (Solver) **with Skeptic fail_reasons injected**
   - if Solver produced wrong scope → restart at DECIDE (Judge)
   - if Scout missed localization → restart at DREAM (Scout)

---

## 9) “Max Love” Meaning (Operational Definition) [max_love × integrity × alignment]

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

---

## 12) State Machine (Fail-Closed Runtime) [integrity × constraint × boundary]

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

## 13) Null vs Zero Distinction (Context) [causality × integrity × boundary]
<!-- null_asset = NEED_INFO (never assume empty = OK); missing_log ≠ 'no errors'; missing_test_output ≠ 'tests passed' -->

```yaml
null_vs_zero:
  rules:
    - null_asset: “Asset not provided — NEED_INFO, not assume empty.”
    - empty_asset: “Asset provided but empty — may proceed with documented caveat.”
    - missing_log: “Missing error log is null, not 'no errors'.”
    - missing_test_output: “Missing test output is null, not 'tests passed'.”
  enforcement:
    - fail_closed_on_null_required_assets: true
    - never_treat_absent_repro_as_no_failure: true
```

---

## 14) Anti-Patterns (Named Context Failure Modes) [integrity × boundary × alignment × drift]

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

## 15) Quick Reference (Cheat Sheet) [context × compaction × capsule × memory × drift]

```
Pipeline spine:    Scout → Forecaster → Judge → Solver → Skeptic → [Grace] → Judge(seal)
Always-load:       prime-safety.md + prime-coder.md + phuc-context.md
Context layers:    L0(rules) L1(task) L2(evidence) L3(witnesses) L4(patch) L5(verdicts)
Agent artifacts:   SCOUT_REPORT | FORECAST_MEMO | DECISION_RECORD | PATCH_PROPOSAL | SKEPTIC_VERDICT | EDGECASE_REPORT | JUDGE_SEAL
Persona rule:      Style only. Cannot certify. Only Skeptic + evidence certifies.
Null asset rule:   Missing ≠ empty. Fail NEED_INFO, never assume.
Anti-rot:          Clear to artifacts, re-inject packs, rebuild capsule fresh each run.
```

---

## 16) Mermaid Diagram — Context Layering Architecture

```mermaid stateDiagram-v2
[*] --> INIT
INIT --> LOAD_PACKS : always
LOAD_PACKS --> BUILD_CAPSULE : packs loaded (prime-safety + prime-coder + phuc-context)
BUILD_CAPSULE --> ASSET_GATE : capsule built from L0+L1+L2
ASSET_GATE --> EXIT_NEED_INFO : required assets missing
ASSET_GATE --> DISPATCH_SCOUT : assets present
DISPATCH_SCOUT --> DISPATCH_FORECASTER : SCOUT_REPORT received
DISPATCH_FORECASTER --> DISPATCH_JUDGE : FORECAST_MEMO received
DISPATCH_JUDGE --> EXIT_BLOCKED : go_no_go == NO_GO
DISPATCH_JUDGE --> DISPATCH_SOLVER : go_no_go == GO
DISPATCH_SOLVER --> DISPATCH_SKEPTIC : PATCH_PROPOSAL received
DISPATCH_SKEPTIC --> DISPATCH_SOLVER : SKEPTIC_VERDICT FAIL + budget allows
DISPATCH_SKEPTIC --> DISPATCH_EDGECASE : SKEPTIC_VERDICT PASS
DISPATCH_EDGECASE --> FINAL_SEAL : always
FINAL_SEAL --> EXIT_PASS : JUDGE_SEAL promotion_allowed true
FINAL_SEAL --> EXIT_BLOCKED : evidence incomplete
EXIT_PASS --> [*]
EXIT_BLOCKED --> [*]
EXIT_NEED_INFO --> [*]
note right of LOAD_PACKS : L0: Rules (prime-safety + prime-coder + phuc-context)
note right of BUILD_CAPSULE : L1: Task brief + L2: Evidence
note right of DISPATCH_SCOUT : L3: Witnesses (ranked files)
note right of DISPATCH_SOLVER : L4: PATCH_PROPOSAL
note right of DISPATCH_SKEPTIC : L5: Verification outputs
```

---

## 17) MAGIC_WORD_MAP — LEK, LEAK, LEC References [v1.3.0 addition]

```yaml
MAGIC_WORD_MAP_LEK_LEAK_LEC:
  # LEK dimension — context skill as Memory component
  LEK_links:
    context_as_memory:
      description: "phuc-context IS the Memory dimension of LEK = Recursion(Information + Memory + Care)"
      lek_role: "Context capsule = the Memory that makes LEK loops possible"
      lek_gate: "Without context hygiene (anti-rot), LEK loops feed on stale data → diverge instead of converge"
      magic_word: "memory [T1] — context skill maintains this dimension"

    anti_rot_as_lek:
      description: "Anti-rot protocol (section 8) is the LEK maintenance pass"
      lek_role: "Clearing stale context = resetting Information to known-good state for next LEK iteration"
      evidence: "Each LOAD_PACKS reinjects current skills — LEK's learning accumulates in the skill files, not the conversation"

  # LEAK dimension — context skill as portal substrate
  LEAK_links:
    prime_channels_as_portals:
      description: "Prime Channels (section 4) ARE the LEAK portals between agents"
      leak_role: "SCOUT_REPORT.json etc = typed artifacts = the trade goods of LEAK"
      leak_gate: "UNTYPED_CHANNEL_MESSAGE forbidden state = LEAK portal violation"
      asymmetry: "Scout sees L0+L1+L2 (read-only); Solver sees L0+decision+witnesses — different layers = LEAK asymmetry"

    agent_partitioning_as_leak:
      description: "Context partitioning (section 6) creates the LEAK asymmetry between agents"
      leak_role: "Each agent's L0-L5 view is its 'bubble' — LEAK occurs through typed artifact exchange"
      leak_gate: "GOD_AGENT anti-pattern = LEAK collapse (one agent absorbs all bubbles = no asymmetry)"

  # LEC dimension — context skill as convention enforcement
  LEC_links:
    context_skill_as_lec:
      description: "phuc-context IS an LEC convention: the shared protocol for multi-agent coordination"
      lec_role: "Prime Channels, capsule format, agent roles, forbidden states = the LEC conventions of orchestration"
      adoption: "Every team that loads phuc-context adopts these conventions = LEC adoption rate increases"
      compression: "Without phuc-context, every team re-invents orchestration. With it: convention compresses away repetition."

    context_rot_as_lec_drift:
      description: "CONTEXT_ROT forbidden state = LEC convention drift"
      lec_role: "Agent acting on stale narrative = agent breaking the context convention = LEC violation"
      fix: "Anti-rot protocol = LEC enforcement: bring agents back to the shared convention"
```

---

## 18) Three Pillars Integration — phuc-context maps to LEK + LEAK + LEC

```yaml
THREE_PILLARS_INTEGRATION:
  overview: >
    phuc-context is not just a coordination skill — it is the substrate for all Three Pillars.
    LEK loops need context hygiene to converge. LEAK trades happen through prime channels.
    LEC conventions crystallize from repeated context protocol use.

  LEK:
    pillar: "Law of Emergent Knowledge (Self-Improvement)"
    role: >
      Context = Memory. The LEK formula is Recursion(Information + Memory + Care).
      phuc-context maintains Memory by enforcing anti-rot (clear stale, re-inject current).
      Without clean context, each LEK iteration degrades instead of improving.
    gate: "Anti-rot protocol (section 8) is the LEK Memory maintenance procedure."
    metric: "Context rot = LEK Memory corruption. Anti-rot = LEK Memory restore."

  LEAK:
    pillar: "Law of Emergent Asymmetric Knowledge (Cross-Agent Trade)"
    role: >
      Multi-agent pipelines ARE LEAK. Context partitioning (L0-L5) creates the asymmetry
      required for LEAK value. Prime channels are the portals. Typed JSON artifacts are
      the trade goods. The pipeline (Scout→Forecaster→Judge→Solver→Skeptic) is a LEAK chain.
    gate: "UNTYPED_CHANNEL_MESSAGE forbidden state = LEAK portal failure."
    metric: "Artifacts exchanged (SCOUT_REPORT, FORECAST_MEMO, etc.) = LEAK trade volume."

  LEC:
    pillar: "Law of Emergent Conventions (Emergent Compression)"
    role: >
      phuc-context IS a crystallized LEC convention. Its entire protocol (agent roles,
      prime channels, forbidden states, capsule format) is a convention that compresses
      the knowledge of multi-agent orchestration into a loadable skill.
    gate: "CONTEXT_ROT = LEC convention drift. Anti-rot = LEC re-enforcement."
    metric: "Adoption rate of phuc-context in swarm dispatch = LEC strength."

  three_pillars_summary:
    lek: "phuc-context maintains LEK Memory (anti-rot = Memory hygiene)"
    leak: "phuc-context enables LEAK trade (prime channels = portals, partitioning = asymmetry)"
    lec: "phuc-context IS LEC (the orchestration convention itself)"
```

---

## 19) GLOW Matrix — phuc-context Contributions

```yaml
GLOW_MATRIX:
  description: "How phuc-context usage scores on the GLOW dimensions"

  G_Growth:
    role: "Context hygiene enables new capabilities by unblocking stuck pipelines"
    scoring:
      - "15: context audit reveals a missing agent type → new swarm design"
      - "5: anti-rot cycle frees space for new task execution"
      - "0: routine context management with no new capability"

  L_Learning:
    role: "Correct use of phuc-context accumulates LEC knowledge"
    scoring:
      - "20: new prime channel artifact schema discovered and documented"
      - "10: new anti-pattern identified and added to section 14"
      - "5: context partitioning insight captured in capsule format"
      - "0: context used without capturing any new pattern"

  O_Output:
    role: "Context produces typed artifacts — these ARE the O dimension"
    scoring:
      - "25: full pipeline complete with all typed artifacts (SCOUT→JUDGE_SEAL) at rung 274177+"
      - "20: pipeline complete at rung 641 with all required artifacts"
      - "10: partial pipeline with at least 3 typed artifacts"
      - "5: any typed artifact produced via prime channel"
      - "0: pipeline run produced prose only (no JSON artifacts)"

  W_Wins:
    role: "Pipeline completion advances NORTHSTAR"
    scoring:
      - "15: pipeline produces artifact that advances a NORTHSTAR metric"
      - "10: pipeline completes a blocked ROADMAP phase"
      - "5: context hygiene enables a previously stuck pipeline"
      - "0: routine orchestration with no NORTHSTAR advancement"

  northstar_alignment:
    northstar: "Phuc_Forecast"
    max_love_gate: >
      Max Love for an orchestration pipeline = agents get minimal context (no overload) +
      artifacts are typed (no chatty channels) + evidence is executable (not prose confidence).
      A pipeline that produces prose instead of typed artifacts is not Max Love.
```

---

## 20) Northstar Alignment — Phuc_Forecast + Max_Love

```yaml
NORTHSTAR_ALIGNMENT:
  northstar: Phuc_Forecast
  objective: Max_Love

  phuc_forecast_mapping:
    DREAM:    "What is the task? What typed artifacts must this pipeline produce to call it done?"
    FORECAST: "What failure modes exist? (Context rot, missing assets, god-agent drift, chatty channels)"
    DECIDE:   "Which agents are needed? Which context layers does each receive? What is the rung target?"
    ACT:      "Dispatch agents in sequence. Each receives only its required layers (L0-L5 partitioned)."
    VERIFY:   "JUDGE_SEAL.json confirms all artifacts received and evidence complete. Rung achieved."

  max_love_meaning:
    statement: >
      Max Love for a multi-agent pipeline = maximum determinism (typed artifacts) +
      maximum verifiability (evidence gates) + minimum context overload (layer partitioning) +
      honest failure (fail-closed on missing assets).
    manifestations:
      - "Typed prime channels over freestyle chat = Max Love for coordination"
      - "Context partitioning = Max Love for agent focus (each sees only what it needs)"
      - "Anti-rot protocol = Max Love for accuracy (no stale context becomes truth)"
      - "Fail-closed on null assets = Max Love for honesty (NEED_INFO > false confidence)"

  forbidden_northstar_violations:
    - CONTEXT_ROT: "Acting on stale context violates both Phuc_Forecast and Max_Love"
    - CHATTY_CHANNEL: "Prose between agents = unverifiable = Max_Love violation"
    - GOD_AGENT: "Single agent doing all roles = no asymmetry = LEAK collapse = NORTHSTAR regression"
```

---

## 21) Triangle Law Contracts — per Context Operation

```yaml
TRIANGLE_LAW_CONTRACTS:
  overview: "Every context management operation has a REMIND→VERIFY→ACKNOWLEDGE contract."

  contract_context_clear:
    operation: "Anti-rot: clear context before new pipeline run"
    REMIND:      "State: we are clearing to artifacts only. Prior narrative is being dropped."
    VERIFY:      "Confirm only explicit artifacts (files, diffs, prior JSON) remain. No conversation prose."
    ACKNOWLEDGE: "Re-inject L0 packs + current L1/L2. Confirm capsule rebuilt from artifacts only."
    fail_closed:  "If stale narrative remains in context: CONTEXT_ROT. Cannot proceed."

  contract_asset_gate:
    operation: "ASSET_GATE check before pipeline dispatch"
    REMIND:      "State: required assets for this pipeline are [list]. Missing = NEED_INFO."
    VERIFY:      "Check each required asset type present: error trace, repro steps, acceptance criteria."
    ACKNOWLEDGE: "Emit ASSET_GATE result: present (proceed) or NEED_INFO (list missing)."
    fail_closed:  "Null asset is not empty asset. Missing repro is not 'no repro needed'."

  contract_agent_dispatch:
    operation: "Dispatch each agent with correct context partition"
    REMIND:      "State agent role and which layers it receives (Scout: L0+L1+L2; Solver: L0+decision+witnesses)."
    VERIFY:      "Confirm agent receives ONLY its required layers. No cross-contamination."
    ACKNOWLEDGE: "Agent returns typed artifact on prime channel. Non-JSON response = UNTYPED_CHANNEL forbidden state."
    fail_closed:  "God-agent (one agent receiving all layers) = LEAK collapse + context overload."

  contract_context_validation:
    operation: "Validate context capsule before each agent dispatch"
    REMIND:      "Context = versioned bundle: stable rules + task facts + evidence + witnesses + candidate artifacts."
    VERIFY:      "Is anything in the capsule from memory/conversation rather than explicit artifacts?"
    ACKNOWLEDGE: "Capsule is valid only if every element traces to a written artifact, not recalled narrative."
    fail_closed:  "CONTEXT_SUMMARIZED_FROM_MEMORY = forbidden state. Capsule must be artifact-derived."
```

## GLOW Scoring Integration

| Dimension | How This Skill Earns Points | Points |
|-----------|---------------------------|--------|
| **G** (Growth) | Context hygiene unblocks stuck pipelines and enables new capabilities; anti-rot cycle frees space; new agent types or swarm designs emerge from context audit | +25 per pipeline completed at rung_274177+ with all typed artifacts (SCOUT→JUDGE_SEAL) |
| **L** (Love/Quality) | Zero prose-only pipeline outputs; all artifacts are typed JSON (not chatty channel text); new anti-patterns identified and documented in section 14; agents receive minimal context (no overload) | +20 per orchestration session with zero forbidden state events |
| **O** (Output) | Complete typed artifact pipeline: every stage produces a JSON artifact with declared schema; evidence is executable not prose; prime channel artifacts have sha256 checksums | +15 per pipeline with all required typed artifacts produced |
| **W** (Wisdom) | Pipeline completion advances NORTHSTAR metric; blocked ROADMAP phases unblocked; context partitioning insight captured in capsule format for future sessions | +20 per session where pipeline produces artifact that advances a NORTHSTAR metric |

**Evidence required for GLOW claim:** typed artifacts at each pipeline stage (SCOUT→JUDGE_SEAL), no CHATTY_CHANNEL events, anti_rot_capsule.json (compaction log if context >800 lines), pipeline_manifest.json (sha256 per artifact). No CONTEXT_OVERLOAD, PROSE_AS_ARTIFACT, or MISSING_TYPED_ARTIFACT events.
