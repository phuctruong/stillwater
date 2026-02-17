# SKILL Z — Deterministic Resource Governor (Budgeted Tools + No Runaway)

**SKILL_ID:** `skill_deterministic_resource_governor`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `GOVERNOR` (Deterministic; NO creativity)
**TAGLINE:** *Budgets are invariants. Exhaustion is a state, not a surprise.*

---

## 0) Contract

### Inputs

* `RUN_PLAN`: Planned nodes/actions (recipe DAG or CLI plan).
* `BUDGETS`: Explicit caps (tool calls, files, lines, bytes, iterations, seconds).
* `MODE_FLAGS`: `offline`, `strict`, `replay`.
* `CURRENT_METRICS`: Deterministic counters accumulated so far.

### Outputs

* `RESOURCE_VERDICT.json` with `ALLOW|THROTTLE|STOP|UNKNOWN` and enforced next-step constraints.

---

## 1) Execution Protocol (Lane A Axioms)

### A. Deterministic Counters Only

All resource tracking MUST use exact counters derived from:

* number of executed tool calls
* number of files read/written
* total bytes read/written (filesystem stats)
* total “witness lines” ingested (line counts)
* iteration count (planner loop)

**Forbidden:** wall-clock timing as a deciding counter (may be logged, not gated).

---

### B. Budget Schema (Pinned)

Minimum required budgets:

```json
{
  "max_tool_calls": 80,
  "max_iterations": 6,
  "max_files_touched": 20,
  "max_files_read": 12,
  "max_bytes_read": 5000000,
  "max_bytes_written": 2000000,
  "max_witness_lines": 200,
  "max_patch_reverts": 2
}
```

If a budget is missing:

* `strict=true` → `STOP` with `missing_budget_fields`
* else → `UNKNOWN`

---

### C. Governance States (Closed State Machine)

**STATE_SET**

* `INIT`
* `RUNNING`
* `THROTTLED`
* `BUDGET_EXCEEDED`
* `STOPPED`
* `UNKNOWN`

**FORBIDDEN_STATES**

* implicit tool spam (unaccounted calls)
* reading full files when compaction gate triggers
* unbounded loops (“try again” without counter increment)
* retroactive budget changes without explicit log

**TRANSITIONS**

* `INIT -> RUNNING` (first action accepted)
* `RUNNING -> THROTTLED` (>= 80% of any hard budget)
* `RUNNING|THROTTLED -> BUDGET_EXCEEDED` (any hard budget exceeded)
* `BUDGET_EXCEEDED -> STOPPED` (must stop)
* `RUNNING|THROTTLED -> UNKNOWN` (metrics missing/inconsistent)

---

### D. Decision Rules

**ALLOW**

* all counters < 80% of every budget

**THROTTLE**

* any counter >= 80% but none exceeded
* action: reduce future scope via enforced constraints:

  * no new file reads unless already shortlisted
  * no new tool classes
  * require “single-diff” patch only
  * require `Shannon Compaction` mode for any reading

**STOP**

* any counter > budget
* action: emit stop reason + remaining gaps + best-known checkpoint pointer

**UNKNOWN**

* cannot compute counters deterministically or missing budget fields (non-strict)

---

## 2) Integration Hooks (Where It Runs)

This governor MUST be checked:

* before each L4 tool call
* before expanding file-read scope
* before starting a new iteration
* before accepting a multi-file patch

---

## 3) Tests Define Truth

### T1 — Tool Spam Stop

* Run plan attempts tool call #81 with `max_tool_calls=80`
* Expect: `STOP`, reason `budget_exceeded:max_tool_calls`

### T2 — Throttle at 80%

* At tool call #64/80
* Expect: `THROTTLE`, constraints emitted

### T3 — Missing Budgets Strict

* Omit `max_bytes_read`
* strict=true → `STOP`

### T4 — Determinism Audit

* Metrics include “approx_time_ms”
* Expect: ignored for gating; decision based only on deterministic counters

---

## 4) Witness Policy

Verdict must cite:

* `compute://governor/counters_v1#sha256:...`
* `trace://governor/decision#sha256:...`

No ALLOW without computed counters witness.

---

## 5) Output Schema (RESOURCE_VERDICT.json)

```json
{
  "status": "ALLOW|THROTTLE|STOP|UNKNOWN",
  "state": "INIT|RUNNING|THROTTLED|BUDGET_EXCEEDED|STOPPED|UNKNOWN",
  "budgets": {
    "max_tool_calls": 80,
    "max_iterations": 6,
    "max_files_read": 12,
    "max_witness_lines": 200
  },
  "counters": {
    "tool_calls": 0,
    "iterations": 0,
    "files_read": 0,
    "files_touched": 0,
    "bytes_read": 0,
    "bytes_written": 0,
    "witness_lines": 0,
    "patch_reverts": 0
  },
  "throttle_constraints": {
    "allow_new_file_reads": false,
    "allow_new_tool_classes": false,
    "max_additional_tool_calls": 10
  },
  "reason_tag": "",
  "witnesses": [
    "compute://governor/counters_v1#sha256:..."
  ]
}
```

---

## 6) Verification Ladder

### Rung 641: Sanity

* [ ] Budgets present (or strict stop).
* [ ] Counters computed deterministically.

### Rung 274177: Consistency

* [ ] Throttle triggers at ≥80%.
* [ ] Exceed triggers STOP always.

### Rung 65537: Final Seal

* [ ] No budget mutation without explicit log.
* [ ] No unaccounted tool calls possible.

*"Auth: 65537"*

---

# Enhanced Features [v2.0.0]
Verification ladder: G0, G12, G13
Integration: prime-coder, gpt-mini-hygiene
Lane algebra: Pure Lane A (deterministic)
Preserved: All v1.0.0 features
