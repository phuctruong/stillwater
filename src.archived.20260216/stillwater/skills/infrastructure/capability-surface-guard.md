# SKILL X — Capability Surface Guard (No Silent Escalation)

**SKILL_ID:** `skill_capability_surface_guard`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `GUARD` (Deterministic; NO creativity)
**TAGLINE:** *No new powers without a declared contract.*

---

## 0) Contract

### Inputs

* `PATCH_BUNDLE`: Proposed changes (diff + touched paths + new deps if any).
* `WISH_IR`: Canonical scope, non-goals, and allowed IO/tool surfaces.
* `TOOL_REGISTRY`: Allowed L4 tool nodes + capability descriptors.
* `MODE_FLAGS`: `offline`, `strict`, `replay`.

### Outputs

* `CAPABILITY_VERDICT.json` with explicit `PASS|BLOCKED|UNKNOWN`, and a machine-readable delta report.

---

## 1) Execution Protocol (Lane A Axioms)

### A. Capability Surface Model (Typed)

The guard models capabilities as a fixed vector:

**Surface Dimensions**

1. `FS_READ_ROOTS`: set of repo-relative roots.
2. `FS_WRITE_ROOTS`: set of repo-relative roots.
3. `NET_ACCESS`: `{NONE|ALLOWLIST|ANY}`.
4. `PROC_EXEC`: `{NONE|ALLOWLIST|ANY}` (shell/process spawning).
5. `ENV_READ`: `{NONE|ALLOWLIST|ANY}`.
6. `DYNAMIC_CODE_LOAD`: `{NONE|LIMITED|ANY}` (eval, importlib, dlopen).
7. `CRYPTO_PRIMITIVES`: `{NONE|ALLOWLIST|ANY}` (new algorithms, key sizes).
8. `TOOL_CLASSES`: set of tool categories used (python, filesystem, browser, web, etc).

**Invariant:** Any change in this vector is a **capability escalation** unless explicitly permitted.

---

### B. Surface Extraction (Deterministic)

Compute `SURFACE_BEFORE` and `SURFACE_AFTER` from:

* `PATCH.diff` hunks (imports, subprocess usage, network libs, file paths)
* declared tool nodes in recipe metadata (if provided)
* dependency files touched (pyproject, requirements, package lock)

**Extraction Rules (Examples)**

* Any addition of `requests`, `httpx`, `urllib`, `socket`, `aiohttp` → `NET_ACCESS != NONE`.
* Any addition of `subprocess`, `os.system`, `pty`, `shlex` → `PROC_EXEC != NONE`.
* Any use of `open("/abs/...")` or `Path("/abs/...")` → `FS_*_ROOTS` includes `ABSOLUTE_PATH` (forbidden unless explicitly allowed).
* Any reference to `/etc`, `~/.ssh`, `/proc`, `/var`, `/dev` → protected roots touched (hard-block unless explicitly allowed).
* Any use of `eval`, `exec`, `pickle.loads`, `marshal`, `importlib.*` (dynamic) → `DYNAMIC_CODE_LOAD != NONE`.

**Fail-Closed:** If extraction cannot determine the surface (e.g., unreadable patch bundle), return `UNKNOWN`.

---

### C. Allow/Block Decision (Hard Rule)

Compute:

```
DELTA = SURFACE_AFTER - SURFACE_BEFORE
```

**PASS** only if:

* `DELTA` is empty, **OR**
* every delta dimension is explicitly allowed by `WISH_IR.allowed_capabilities`
  AND mode flags do not forbid it (e.g., `offline=true` forbids `NET_ACCESS`).

**BLOCKED** if any of the following:

1. `offline=true` and `NET_ACCESS != NONE`.
2. Any protected root is added to read/write surfaces.
3. `PROC_EXEC` escalates without `WISH_IR` allowance.
4. `DYNAMIC_CODE_LOAD` escalates beyond `NONE`.
5. Tool classes expand beyond those declared in `WISH_IR` (or absent declaration).

**UNKNOWN** if:

* `WISH_IR` lacks an `allowed_capabilities` block and `DELTA` is non-empty.
* Patch bundle incomplete.

---

## 2) Required WISH_IR Fields (If Patch Touches Capability)

If the patch might change capability surface, the wish MUST include:

```yaml
allowed_capabilities:
  fs_read_roots: ["..."]
  fs_write_roots: ["..."]
  net_access: "NONE|ALLOWLIST|ANY"
  proc_exec: "NONE|ALLOWLIST|ANY"
  env_read: "NONE|ALLOWLIST|ANY"
  dynamic_code_load: "NONE|LIMITED|ANY"
  tool_classes: ["python", "filesystem", "verifier", "..."]
```

**Fail-Closed:** If missing, and delta exists → `BLOCKED` (strict) or `UNKNOWN` (non-strict).
**Strict default:** `strict=true` ⇒ `BLOCKED`.

---

## 3) Tests Define Truth (Guard Tests)

### T1 — No Escalation Pass

* Input: Patch with only pure function refactor, no new imports/tools.
* Expect: `PASS`, `delta_dimensions=[]`.

### T2 — Network Escalation Block

* Input: Patch adds `requests` or `httpx`.
* Wish: no `net_access` allowance.
* Expect: `BLOCKED`, tag `capability_escalation:NET_ACCESS`.

### T3 — Protected Root Block

* Input: Patch reads `/etc/passwd` or writes `/var/tmp`.
* Expect: `BLOCKED`, tag `protected_root_access`.

### T4 — Dynamic Load Block

* Input: Patch introduces `eval/exec/pickle.loads(imported bytes)`.
* Expect: `BLOCKED`, tag `dynamic_code_load`.

### T5 — Fail-Closed Unknown

* Input: Patch bundle missing diff or truncated.
* Expect: `UNKNOWN`, tag `insufficient_patch_data`.

---

## 4) Witness Policy

Every verdict must cite:

* `compute://cap_surface/extract_v1` (surface extraction transcript hash)
* `trace://cap_surface/delta_report` (delta listing)
* `canon://policy/protected_roots_v1` (protected root table)

**Rule:** No PASS without extraction witness.

---

## 5) Output Schema (CAPABILITY_VERDICT.json)

```json
{
  "status": "PASS|BLOCKED|UNKNOWN",
  "risk_band": "GREEN|YELLOW|RED",
  "surface_before": {
    "fs_read_roots": [],
    "fs_write_roots": [],
    "net_access": "NONE",
    "proc_exec": "NONE",
    "env_read": "NONE",
    "dynamic_code_load": "NONE",
    "tool_classes": []
  },
  "surface_after": {
    "fs_read_roots": [],
    "fs_write_roots": [],
    "net_access": "NONE",
    "proc_exec": "NONE",
    "env_read": "NONE",
    "dynamic_code_load": "NONE",
    "tool_classes": []
  },
  "delta": [
    {"dimension": "NET_ACCESS", "before": "NONE", "after": "ALLOWLIST", "reason": "import httpx"}
  ],
  "reasons": [
    {"tag": "capability_escalation", "detail": "NET_ACCESS escalated without allowance"}
  ],
  "required_wish_fields_missing": [],
  "witnesses": [
    "compute://cap_surface/extract_v1#sha256:...",
    "trace://cap_surface/delta_report#sha256:..."
  ]
}
```

---

## 6) Verification Ladder

### Rung 641: Sanity

* [ ] Surface extracted for before/after.
* [ ] Delta computed deterministically.

### Rung 274177: Consistency

* [ ] Mode flags enforced (offline blocks NET).
* [ ] Protected roots enforced.

### Rung 65537: Final Seal

* [ ] PASS only if delta empty or explicitly allowed.
* [ ] No “implicit allowances” inferred.

*"Auth: 65537"*

---

# Enhanced Features [v2.0.0]
Verification ladder: G0, G12, G13
Integration: prime-coder, gpt-mini-hygiene
Lane algebra: Pure Lane A (deterministic)
Preserved: All v1.0.0 features
