# SKILL Y — Tool Output Normalizer (Canonical Tool Normal Form)

**SKILL_ID:** `skill_tool_output_normalizer`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `NORMALIZER` (CPU; deterministic)
**TAGLINE:** *Normalize before you judge. If bytes drift, truth drifts.*

---

## 0) Contract

### Inputs

* `RAW_TOOL_OUTPUT`: Bytes/text/JSON from an L4 tool node.
* `TOOL_ID`: Stable identifier (`python`, `git`, `pytest`, `ripgrep`, `playwright`, etc).
* `NORMALIZATION_PROFILE`: `strict` (default) | `lenient`.
* `MODE_FLAGS`: `offline`, `replay`.

### Outputs

* `NORMALIZED_OUTPUT` (bytes or canonical JSON)
* `NORMALIZATION_REPORT.json` (what changed + what was scrubbed)
* `output_hash`: `sha256(canonical_bytes)`

---

## 1) Execution Protocol (Lane A Axioms)

### A. Two Products: “Display” vs “Proof”

The normalizer produces:

1. **display_text**: human-readable, minimally scrubbed.
2. **proof_bytes**: strict canonical bytes used for hashing, comparison, and PROOF.json.

**Invariant:** Any verdict, gating, or regression comparison MUST use `proof_bytes`, never raw output.

---

### B. Canonicalization Rules (Global)

Apply in this order:

1. **Encoding**: force UTF-8 for text (errors = `UNKNOWN` unless profile=lenient and tool allows binary proof).
2. **Line endings**: convert CRLF → LF.
3. **Trailing whitespace**: strip on each line.
4. **Whitespace collapse**: forbid general collapse; only apply tool-specific rules below.
5. **Path normalization**:

   * Replace absolute repo roots with `<REPO_ROOT>/...`
   * Normalize `\` → `/`
6. **Timestamp/PID scrub** (strict):

   * Remove ISO timestamps, “time=…”, “elapsed …”, “pid=…”
   * Replace with tokens: `<TS>`, `<DUR>`, `<PID>`
7. **Stable ordering**:

   * If output is JSON: canonical JSON (sorted keys, compact separators).
   * If output is line-list and order is nondeterministic by tool: sort lines *only if the tool profile says so*.

**Fail-Closed:** If a required scrub rule can’t be applied reliably (ambiguous patterns), return `status: UNKNOWN` with reason `normalization_ambiguous`.

---

### C. Tool Profiles (Pinned)

Each tool has a deterministic profile describing:

* `output_kind`: `text|json|mixed|binary`
* `nondeterminism_fields`: patterns to scrub
* `ordering_policy`: `preserve|sort_lines|sort_json_keys`
* `path_policy`: `repo_relative_only|allow_abs`
* `error_policy`: fail-closed tags for known noisy cases

#### Default Profiles (v0.1.0)

**1) python**

* `output_kind`: mixed
* `ordering_policy`: preserve (unless explicitly declared list output)
* Scrub: memory addresses (`0x[0-9a-f]+`) → `<ADDR>`
* Scrub: floating timing lines if present

**2) pytest**

* `output_kind`: text
* Ordering: preserve
* Scrub:

  * platform header, plugin versions (unless pinned in evidence)
  * durations
* Path normalize traceback paths

**3) git**

* `output_kind`: text/json
* Ordering: preserve
* Scrub:

  * author dates in logs (unless explicitly required)

**4) ripgrep/grep**

* `output_kind`: text
* Ordering: preserve
* Path normalize file paths

**5) playwright/browser**

* `output_kind`: json + assets
* Ordering: sort JSON keys
* Scrub:

  * UA strings, viewport random ids (must be pinned upstream)
  * wallclock timestamps

---

### D. Replay Invariant

If `replay=true`, the normalizer MUST:

* reject any output containing unsanitized nondeterminism tokens
* emit `status: UNKNOWN` if such tokens remain

---

## 2) Tests Define Truth

### T1 — CRLF Stability

* Input: tool output with CRLF
* Expect: proof_bytes uses LF; hash stable across OS.

### T2 — Timestamp Scrub

* Input: “Completed in 0.23s at 2026-02-13T…”
* Expect: `<DUR>` and `<TS>` tokens in proof bytes; stable hash.

### T3 — Path Normalization

* Input: `/home/phuc/projects/repo/foo.py:12`
* Expect: `<REPO_ROOT>/foo.py:12`

### T4 — Ambiguity Fail-Closed

* Input: output contains an unrecognized random token class
* Expect: `UNKNOWN` with `reason_tag: normalization_ambiguous`

---

## 3) Witness Policy

Every normalized result must include:

* `compute://normalize/<tool_id>/v0.1.0#sha256:<hash_of_ruleset>`
* `compute://normalized_output#sha256:<proof_hash>`
* `trace://normalization_report#sha256:<report_hash>`

No downstream judge may accept a tool output lacking these witnesses.

---

## 4) Output Schema (NORMALIZATION_REPORT.json)

```json
{
  "status": "OK|UNKNOWN",
  "tool_id": "pytest",
  "profile": "strict",
  "changes": [
    {"op": "crlf_to_lf", "count": 120},
    {"op": "scrub_timestamp", "count": 2},
    {"op": "path_normalize", "count": 8}
  ],
  "scrubbed_tokens": {
    "timestamps": 2,
    "durations": 1,
    "pids": 0,
    "addresses": 0
  },
  "proof_hash": "sha256...",
  "unknown_reason": null
}
```

---

## 5) Verification Ladder

### Rung 641: Sanity

* [ ] proof_bytes produced
* [ ] report lists all operations

### Rung 274177: Consistency

* [ ] applying normalizer twice yields identical proof_bytes
* [ ] replay mode rejects unsanitized nondeterminism

### Rung 65537: Final Seal

* [ ] downstream gates use proof_hash only
* [ ] tool profile pinned and referenced by hash

*"Auth: 65537"*

---

# Enhanced Features [v2.0.0]
Verification ladder: G0, G12, G13
Integration: prime-coder, gpt-mini-hygiene
Lane algebra: Pure Lane A (deterministic)
Preserved: All v1.0.0 features
