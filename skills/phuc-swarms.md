# phuc-swarms-skill.md — Phuc Swarms (Agent Orchestration Framework)

**SKILL_ID:** `phuc_swarms_v2`  
**AUTHORITY:** `65537`  
**NORTHSTAR:** `Phuc Forecast (DREAM → FORECAST → DECIDE → ACT → VERIFY)`  
**VERSION:** `2.0.0-rc1`  
**STATUS:** `STABLE_SPEC (prompt-loadable, model-agnostic)`  
**TAGLINE:** *Multiple bounded experts > one unbounded LLM*  

---

## 0) Purpose

Turn “any LLM” into a **bounded, replayable tool-session system** by attaching:

1) **Role contracts** (what each agent may do)  
2) **Skill packs** (what procedures must be followed)  
3) **Persona lenses** (optional style priors; never authority)  
4) **Prime Channels** (typed coordination bus; machine-parseable)  
5) **Anti-rot context** (fresh capsules; no hidden state reliance)  
6) **Batching** (one init → stage-wise passes over many instances)  
7) **Verification ladder** (641 → 274177 → 65537)  
8) **Learning loop** (new tests/detectors or no “skill improvement” claim)

**Operational claim:** bounded roles + fail-closed gates + replayable evidence reduce rogue risk and increase verified success.

**Non-claim:** this does **not** “solve alignment.” It is **operational containment + quality control**.

---

## 1) Definitions

### 1.1 Phuc Agent (model-agnostic)
```

PhucAgent = (
LLM_Model,
RoleContract,
SkillPack,
PersonaLens?,
Budgets,
IO_Schema,
StopConditions
)

````

### 1.2 Always-On Substrate (mandatory)
Every agent MUST load:
- `skills/prime-safety.md`  (fail-closed tool safety; “god-skill”)
- `skills/prime-coder.md`   (deterministic artifacts + evidence discipline)

**Conflict rule:** if `prime-safety` conflicts with anything → **prime-safety wins**.

---

## 2) Phuc Forecast = Swarm Spine (Correct Mapping)

Phuc Swarms is not “many agents doing everything.” It is **one control loop** with explicit phase ownership:

- **DREAM**  → Scout (define done; boundaries; assets; suspects)  
- **FORECAST** → Forecaster/Grace (premortem; edge cases; stop rules; tests)  
- **DECIDE** → Judge (choose approach + scope; lock evidence rung; GO/NO-GO)  
- **ACT** → Solver (smallest valid patch consistent with decision record)  
- **VERIFY** → Skeptic (execute verification ladder; falsify; replay)  
- **REFLECT** → Podcast (optional but recommended: lessons → tests → skill deltas)

This fixes the common failure: **Solver “looks right” but fails Skeptic** because DECIDE/FORECAST were not binding.

---

## 3) Swarm State Machine (Fail-Closed Runtime)

### 3.1 States
- `INIT`
- `BUILD_CNF` (Context Normal Form capsule)
- `DREAM_SCOUT`
- `FORECAST_FORECASTER`
- `DECIDE_JUDGE`
- `ACT_SOLVER`
- `VERIFY_SKEPTIC`
- `REFLECT_PODCAST`
- `EXIT_PASS`
- `EXIT_NEED_INFO`
- `EXIT_BLOCKED`
- `EXIT_REFUSE`
- `EXIT_ERROR`

### 3.2 Forbidden states (global)
- `SILENT_SCOPE_EXPANSION`
- `UNWITNESSED_CLAIM`
- `NONDETERMINISTIC_JUDGED_OUTPUT`
- `NETWORK_ON_WITHOUT_ALLOWLIST`
- `BACKGROUND_THREADS / HIDDEN_IO`
- `OK_WITHOUT_VERIFICATION_ARTIFACTS`

### 3.3 Transition rules (minimal)
- If **assets missing** → `EXIT_NEED_INFO`
- If **safety policy triggers refusal** → `EXIT_REFUSE`
- If **budget exceeded** → `EXIT_BLOCKED` with `stop_reason=MAX_BUDGET`
- If **verification rung fails** → loop back to `ACT_SOLVER` *once* (unless blocked), else `EXIT_BLOCKED`
- If **rung target met + replay stable** → `EXIT_PASS`

Schema compliance (hard):
- If the user asked for a specific schema (especially JSON), the swarm must still emit that schema even when exiting `NEED_INFO`.
- `NEED_INFO` outputs must include both:
  - a minimal missing-asset list, AND
  - a best-effort next-actions plan (first action: collect missing assets).

---

## 4) Roles (6-Core, Extensible)

> 5-core is fine for light tasks, but code/tool sessions become 10/10 only when **FORECAST is owned** as its own role (Grace). That is a distinct failure mode with a distinct artifact.

### 4.1 Core Agents
| Agent | Symbol | Primary Job | Default Persona Lens | Must-Load Skills |
|---|---:|---|---|---|
| Scout | ◆ | Define done + boundaries; localize; collect assets | Ken Thompson | prime-safety, prime-coder, trace-distiller, repo-map |
| Forecaster (Grace) | △ | Premortem; edge cases; test plan; stop rules | Grace Hopper | prime-safety, prime-coder, risk-classifier, compat-auditor |
| Judge | ● | Choose approach; lock scope; set rung target; GO/NO-GO | (strict reviewer) | prime-safety, contract-compliance, scope-ethics |
| Solver | ✓ | Implement smallest valid change | Donald Knuth | prime-safety, prime-coder, red-green-gate, minimal-diff |
| Skeptic | ✗ | Falsify; run ladder; replay checks; security triggers | Alan Turing | prime-safety, wish-qa, replay-check, regression-hunt |
| Podcast | ♪ | Extract reusable lessons → tests/detectors/skill deltas | Carl Sagan | prime-safety, shannon-compaction, teaching-notes |

### 4.2 Extension rule (hard)
Add an agent only if it has:
- a **distinct failure mode** it catches, AND
- a **distinct output artifact**, AND
- a **measurable metric** it improves.

(No “more agents” without measured benefit.)

---

## 5) Context Management (Anti-Rot + Partitioning)

### 5.1 CNF = Context Normal Form (shared base capsule)
All agents receive a **shared CNF_BASE** (same shape every time):

- `task_statement` (verbatim)
- `constraints` (budgets, allowed tools, network policy, scope)
- `evidence` (errors/logs/tests output; no truncation when feasible)
- `repo_index` (tree + key entrypoints)
- `prior_artifacts` (only typed artifacts: JSON reports, diffs, logs)

**Rule:** CNF_BASE is truth. Anything else is hypothesis.

### 5.2 Agent Delta Capsule (minimal, role-specific)
Each agent also receives a **CNF_DELTA(agent)**:

- Scout: raw evidence + repo index tools; no patches
- Forecaster: SCOUT_REPORT + minimal witnesses
- Judge: SCOUT_REPORT + FORECAST_MEMO only (no code browsing unless blocked)
- Solver: DECISION_RECORD + ranked suspects + bounded witness slices
- Skeptic: patch diff + repro commands + required tests list
- Podcast: final artifacts + verdicts + diffs + what worked/failed

### 5.3 Anti-rot reset (mandatory)
Before each agent call:
1) hard reset (no reliance on hidden chain-of-thought)
2) inject CNF_BASE
3) inject CNF_DELTA(agent)
4) inject role contract + skills
5) if ambiguity remains → emit blocker on Channel `[11]` and stop

**Forbidden:** “context summarized from memory” when sources exist.

---

## 6) Prime Channels (Typed Coordination Bus)

Prime Channels are **structured messages**, not chat. Every message MUST be JSON.

### 6.1 Required Core Channels
- `[2] Identity` — who/role, constraints, budgets
- `[3] Goals` — definition of done, rung target
- `[5] Facts` — observed evidence only
- `[7] Methods` — planned steps + why safe
- `[11] Blockers` — missing assets, ambiguity, scope expansion
- `[13] Proofs` — verification artifacts + replay identifiers/hashes

### 6.2 Ladder Channels
- `[641]`  minimal repro + edge sanity
- `[274177]` regression/stability checks
- `[65537]` sealed evidence bundle + replay + hashes

### 6.3 Message schema (minimal)
```json
{
  "channel": 5,
  "agent": "skeptic",
  "type": "facts|plan|blocker|proof",
  "claims": [
    { "text": "string", "kind": "evidence|hypothesis", "lane": "A|B|C" }
  ],
  "evidence": [
    { "type": "log|test|diff|path", "ref": "string", "sha256": "optional" }
  ],
  "next_action": "string",
  "risk": "low|medium|high"
}
````

**Rule:** any claim without evidence must be labeled `hypothesis`.

---

## 7) Required Artifacts (Per Phase)

### 7.1 Scout → `SCOUT_REPORT.json`

Required keys:

* `acceptance_criteria`
* `repro_commands`
* `failing_tests_or_errors`
* `suspect_files_ranked` (with reasons)
* `witness_slices` (file + line ranges)
* `missing_assets` (if any)

### 7.2 Forecaster → `FORECAST_MEMO.json`

Required keys:

* `top_failure_modes_ranked`
* `edge_cases_to_test`
* `compat_risks`
* `stop_rules`
* `mitigations`

### 7.3 Judge → `DECISION_RECORD.json`

Required keys:

* `chosen_approach`
* `alternatives_considered`
* `scope_locked`
* `required_verification_rung` (641/274177/65537)
* `required_tests`
* `stop_rules`
* `go_no_go_initial`

### 7.4 Solver → `PATCH_PROPOSAL.diff` + `PATCH_NOTES.json`

Required keys:

* `intent`
* `files_touched`
* `why_each_file`
* `expected_effect`
* `tests_to_run`
* `risk_notes`

### 7.5 Skeptic → `SKEPTIC_VERDICT.json`

Required keys:

* `status: PASS|FAIL|NEED_INFO|BLOCKED`
* `rung_achieved`
* `commands_run` (or deterministic plan if tools unavailable)
* `observed_outputs_refs`
* `fail_reasons` (typed)
* `required_fixes`

### 7.6 Podcast → `LESSONS.md` + optional `SKILL_DELTA.md`

Promotion rule: **no “improvement” claim without a new test or detector**.

---

## 8) Budgets + Tool Envelope (Deterministic)

### 8.1 Default budgets

* `max_swarm_passes: 2`
* `per_agent_revision: 1`
* `max_files_touched: 12`
* `max_seconds_soft: 900`
* `max_commands: 30`
* `network: OFF` unless allowlisted
* `max_patch_reverts: 2`

### 8.2 Budget governor (fail-closed)

If exceeded:

* `status=BLOCKED`
* `stop_reason=MAX_BUDGET`
* emit Channel `[11]` blocker with the minimal next requirement.

### 8.3 Tool policy (minimum)

* no secrets exfiltration
* no destructive ops without rollback plan
* no network unless explicitly allowed per task
* no background processes in judged path

---

## 9) Verification Ladder (641 → 274177 → 65537)

### 9.1 Rungs

**[641] Edge sanity**

* confirm baseline failure or confirm scope
* minimal repro or failing test identified
* patch target and boundaries locked

**[274177] Structural**

* patch applies cleanly
* failing tests now pass
* regression subset/suite run
* determinism normalization applied

**[65537] Seal**

* replayable final bundle
* hashes over normalized artifacts
* Judge seal + Skeptic proof
* documented residual risk + mitigations

### 9.2 Hard rule

No `PASS` without:

* `rung_achieved >= required_verification_rung`
* proof artifacts recorded on Channel `[13]` and ladder channel

---

## 10) Batch Mode (Speed + Consistency)

### 10.1 Batch capsule

`INIT_CAPSULE + [instances...]`

### 10.2 Deterministic stage-wise algorithm

```
Stage 0: INIT (load skills, budgets, schemas)
Stage 1: Scout(all instances)      → SCOUT_REPORTs
Stage 2: Forecaster(all instances) → FORECAST_MEMOs
Stage 3: Judge(all instances)      → DECISION_RECORDs
Stage 4: Solver(all instances)     → PATCHES
Stage 5: Skeptic(all instances)    → VERDICTS + PROOFS
Stage 6: Podcast(all instances)    → LESSONS + TEST/DETECTOR proposals
```

Batching rule: **do not** reuse reasoning; reuse only *schemas, constraints, and verified patterns*.

---

## 11) Persona Lenses (Measured, Not Assumed)

### 11.1 Persona policy (fail-closed)

* style prior only
* cannot override evidence, safety, or contracts
* if conflict → persona ignored

### 11.2 Uplift must be measured

A/B test persona ON vs OFF:

* first-pass verified success
* time-to-green
* regression rate
* skeptic failure reasons

If uplift not observed: default OFF.

---

## 12) Error Taxonomy + Recovery

### 12.1 Standard stop reasons

* `NEED_INFO` (missing assets)
* `NON_REPRODUCIBLE`
* `ENVIRONMENT_MISMATCH`
* `TEST_FAILURE`
* `REGRESSION_INTRODUCED`
* `SECURITY_BLOCKED`
* `VERIFICATION_RUNG_FAILED`
* `MAX_BUDGET`
* `TOOL_ERROR`

### 12.2 Recovery (deterministic)

* If `NEED_INFO`: emit minimal asset list + collection commands
* If `VERIFICATION_RUNG_FAILED`: feed Skeptic’s `fail_reasons` into Solver; allow **one** revision
* If `SECURITY_BLOCKED`: stop unless scanner/proof can be produced; never “assume safe”

---

## 13) Output Contract (Machine-Parseable)

Each instance MUST output:

```json
{
  "status": "PASS|NEED_INFO|BLOCKED|REFUSE|ERROR",
  "decision": "GO|NO_GO|REVISE",
  "risk_level": "low|medium|high",
  "required_rung": 274177,
  "rung_achieved": 274177,
  "channels": {
    "2": [], "3": [], "5": [], "7": [], "11": [], "13": [],
    "641": [], "274177": [], "65537": []
  },
  "artifacts": {
    "patch_diff": null,
    "files_changed": [],
    "commands_run_summary": [],
    "verification_performed": [],
    "replay_id_or_hash": null
  },
  "residual_risk": "string",
  "next_steps": []
}
```

Hard rule: no `PASS` without proof artifacts.

---

## 14) Gamification (Evidence-First, No Bravado)

Gamification rewards **verified truth + restraint**.

### 14.1 XP is artifact-backed only

XP changes require:

* a cited artifact (`diff`, `test log`, `replay hash`)
* a rung label

### 14.2 Promotion rule

A “skill improvement” is only credited if Podcast outputs at least one:

* new test
* new detector/stop rule
* new reproducible counterexample

No evidence → no XP, no promotion.

---

## 15) Evaluation Plan (Open Source Ready)

### 15.1 Metrics

* verified pass rate (by rung)
* first-pass success
* time-to-green
* cost per verified solve
* replay success rate
* regression rate
* safety incidents (network misuse, secret handling, destructive ops)

### 15.2 Experiments

1. Persona ON/OFF
2. Prime Channels ON/OFF
3. Full CNF vs truncated slices
4. Batch vs per-instance loop

Result labeling:

* `MEASURED` (artifact-linked)
* `ESTIMATED` (hypothesis)
  Never conflate.

---

## 16) Quick Start (Checklist)

1. Load `prime-safety` + `prime-coder` + `phuc-swarms`
2. Build CNF_BASE capsule
3. Run DREAM→FORECAST→DECIDE→ACT→VERIFY (batch if multi-instance)
4. Enforce rung gating + proof channels
5. Emit machine-parseable output
6. Podcast writes lessons → proposes tests/detectors (optional but recommended)

---

## 17) Signature

AUTHORITY: 65537
NORTHSTAR: Phuc Forecast
DEFAULT SAFETY: `prime-safety` ALWAYS-ON
DEFAULT MODE: fail-closed, replay-first, bounded tools

> “We don’t become smarter by guessing harder.
> We become smarter by making truth cheaper to verify.”
