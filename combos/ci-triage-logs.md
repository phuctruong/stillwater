# ✅ Combo 3 — CI Triage (Logs → Repro → Fix)

This combo turns “CI failed” into a deterministic pipeline: **ingest logs → localize failure → produce minimal repro → propose fix plan (or patch) → verify via Run+Test Harness**.

It composes directly on:

* **Combo 1** Plan→Execute split
* **Combo 2** Run + Test Harness

---

# W_CI_TRIAGE — Deterministic CI Failure Triage

**WISH_ID:** `wish_ci_triage`
**PRIORITY:** CRITICAL
**CLASS:** maintenance
**DEPENDS_ON:** `wish_plan_execute_split`, `wish_run_test_harness`

---

## 🎯 Goal

Given CI artifacts (logs + failing command + repo commit), the system must:

1. extract the **failure signature** deterministically,
2. localize likely files/modules,
3. produce a **minimal repro script or command** (`repro.py` or equivalent),
4. produce an actionable **FixPlan.json** (Plan Mode) *or* an implementation patch (Execute Mode),
5. re-run the same gate command locally using the Run+Test Harness.

---

## 🔐 Invariants

1. **No hallucinated stack traces**: only use provided logs or locally reproduced logs.
2. **Repro-first**: triage must attempt to reproduce the failure before proposing a code change.
3. **Deterministic extraction**:

   * stable parsing rules
   * stable ordering of extracted errors
4. **Single primary failure**:

   * pick one “root candidate” deterministically (highest-confidence signature)
   * list secondary failures separately (do not mix)
5. **Evidence required**:

   * CI log pointer + extracted signature
   * repro command/script + exit code
   * mapping from signature → touched files justification

---

## 🚫 Forbidden States

* `FIX_WITHOUT_REPRO`
* `PATCH_WITHOUT_FAILING_GATE_COMMAND`
* `AMBIGUOUS_ROOT_CAUSE_WITHOUT_BRANCHING`
* `RANDOM_FILE_TOUCHING` (touching files without evidence-based justification)

---

## 🧪 Acceptance Tests

1. **Signature extraction**

   * Input: CI log snippet with traceback
   * Output: stable `FailureSignature.json`:

     * `error_type`, `message`, `top_frame`, `failing_test`, `command`

2. **Repro contract**

   * Must produce either:

     * `repro.py` (assert fails) **or**
     * `repro_cmd` (shell) that fails deterministically

3. **Localization policy**

   * Must emit ranked file list with deterministic scoring (your Localization policy)

4. **Plan/Execute compliance**

   * Plan Mode: only emits FixPlan + repro + localization (no patch)
   * Execute Mode: patch allowed, but must pass Run+Test Harness gates

---

## 📦 Required Artifacts

* `FailureSignature.json`
* `LocalizationReport.json`
* `repro.py` **or** `ReproCommand.txt`
* `FixPlan.json` (Plan Mode) **or** `PATCH_BUNDLE` (Execute Mode)
* Evidence:

  * `evidence/ci_log_ref.json`
  * `evidence/repro_red.log`
  * `evidence/tests.json` (post-fix)

---

# R_CI_TRIAGE — CI Failure Triage Recipe

**RECIPE_ID:** `recipe_ci_triage_v1`
**SATISFIES:** `wish_ci_triage`

---

## 🧠 Node Graph (L1–L5)

### Node 1 — L1 CPU: Parse CI Inputs → FailureSignature

Inputs:

* `CI_LOG` (text or file ref)
* `CI_COMMAND` (if available)
* `COMMIT_SHA`
* optional: `FAIL_URL`

Algorithm (deterministic):

* extract:

  * last N lines window around “FAIL”, “Traceback”, “AssertionError”
  * topmost traceback frame in repo paths
  * failing test name if present (`::test_`)
* produce `FailureSignature.json` sorted keys

Outputs:

* `FailureSignature.json`
* `evidence/ci_log_ref.json` (pointer + hash if file)

Fail-closed if no recognizable failure signature.

---

### Node 2 — L1 CPU: Localization (Rank → Justify → Witness Lines)

Inputs:

* FailureSignature.json
* repo tree index (or ripgrep index if available)

Actions:

* score candidate files with fixed scoring:

  * contains_error_string +5
  * referenced_in_trace +6
  * matches failing_test module +4
  * imports related module +3
* select top K

Outputs:

* `LocalizationReport.json`:

  * `ranked_files[]`
  * `justifications[]`
  * `witness_lines[]` (only minimal chunks)
  * compaction log line: `[COMPACTION] Distilled X → Y`

Fail-closed if repo paths not found.

---

### Node 3 — L3 LLM: Repro Constructor (Minimal)

Inputs:

* FailureSignature + witness lines
* mode flags (offline/tools)

Rules:

* produce minimal repro that fails **before fix**:

  * prefer `pytest -q <test>` if test exists
  * else `python repro.py` with assertion
* must specify:

  * command(s)
  * expected exit (nonzero)

Outputs:

* `repro.py` or `ReproCommand.txt`

If cannot construct repro: `FixPlan.json` must return `NEED_INFO` with what’s missing (e.g., missing CI artifacts).

---

### Node 4 — L4 Tool: Repro Red Run (Mandatory)

Uses **Run + Test Harness** (Combo 2) as a sub-recipe:

* run repro command
* record:

  * `evidence/repro_red.log`
  * exit code

Fail if repro passes initially → stop_reason `NON_REPRODUCIBLE`.

---

### Node 5 — Branch by Mode

#### Plan Mode branch (no patch)

**L3 LLM → FixPlan.json**

* root cause hypotheses (ranked)
* minimal fix candidates
* exact files to touch (≤3 ideally)
* verification plan (exact gate commands)

Outputs:

* `FixPlan.json` (machine-checkable)

#### Execute Mode branch (patch allowed)

**L3 LLM → Patch Proposal**

* emit patch bundle candidate (diff)
* must justify each file touched from localization evidence

Then:

* call Run+Test Harness again to turn repro green and run CI gate command.

---

### Node 6 — L5 Judge: Triage Closure Gate

Rules:

* must have:

  * FailureSignature
  * LocalizationReport
  * Repro red evidence
* Execute Mode: must also have Green run evidence
* if multiple plausible roots: must either

  * branch explicitly, or
  * downgrade to `NEED_INFO`

Outputs:

* `TriageVerdict.json`:

  * `status: PASS|BLOCKED|NEED_INFO`
  * `stop_reason`
  * `root_cause_summary`
  * `replay_commands`

---

## 🔁 Replay ABI (CI ↔ Local)

The recipe must output a stable “replay capsule”:

```json
{
  "ci_commit": "...",
  "repro": {"type": "cmd", "value": "pytest -q tests/test_x.py::test_y"},
  "expected_red_exit": 1,
  "green_gate_commands": ["pytest -q"]
}
```

---

## 🎛️ Context Injection (Minimal)

* L1 CPU: CI logs + repo index
* L3 LLM: witness lines + FailureSignature + triage policy (no full canon)
* L4 Tool: only RunManifest + commands
* L5 Judge: required artifacts list + invariants + forbidden states

---

## Why This Combo Is Critical

It prevents the classic agent failure mode:

> “Looks like X, I changed Y.”

Instead you get:

**Logs → deterministic signature → repro → fix → proof via gates.**

---

Say **“next”** for:

**Combo 4 — Bugfix→PR (Red→Green mandatory)**.
