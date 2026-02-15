# SKILL Z — Artifact Hash & Manifest Builder (Touched-Only Merkle)

**SKILL_ID:** `skill_artifact_manifest_builder`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `EVIDENCE_CPU` (deterministic; no creativity)
**TAGLINE:** *If it moved, hash it. If it matters, manifest it.*

---

## 0) Contract

### Inputs

* `WORKSPACE_ROOT`: Repo root (canonical).
* `TOUCHED_PATHS`: Ordered list of files produced/modified by the run (patches, logs, artifacts).
* `MODE_FLAGS`: `offline`, `replay`, `strict`.
* `HASH_POLICY`:

  * `algo`: `sha256`
  * `chunk_bytes`: default `1048576` (1 MiB)
  * `follow_symlinks`: `false`

### Outputs

* `MANIFEST.json` (canonical JSON)
* `MANIFEST.sha256` (hash of MANIFEST.json bytes)
* `TOUCHED_TREE.json` (optional: directory tree proof for touched paths)

---

## 1) Execution Protocol (Lane A Axioms)

### A. Touched-Only Rule (No Silent Expansion)

The manifest MUST include **only**:

* files in `TOUCHED_PATHS`, plus
* their parent directories (as structural context entries, not content-hashed), plus
* explicitly-declared “required context” files (if provided by caller)

**FORBIDDEN:** scanning the whole repo “just in case”.

---

### B. Path Canonicalization

For every entry:

* store `path` as repo-relative POSIX (`/`)
* reject `..` traversal
* reject absolute paths
* reject symlinks (unless policy allows; default forbids)

If any violation occurs: `status: UNKNOWN` with `reason_tag: invalid_path`.

---

### C. Hashing Method (Deterministic)

For each file:

1. read bytes as-is (no newline conversion)
2. compute `sha256(bytes)`
3. record:

   * `bytes`
   * `sha256`
   * `content_type_hint` (by extension only; no sniffing)
   * `role_tag` (caller-provided or inferred: `patch|log|proof|data|report|repro|config`)

**Chunking:** allowed for streaming, but final hash must be full-file sha256.

---

### D. Merkle Root (Touched Merkle)

Compute:

* `leaf_i = sha256(path + "\n" + sha256_file + "\n" + bytes_as_decimal)`
* `merkle_root = sha256(canon(sorted(leaf_i)))`

**Invariant:** Sorting is lexicographic by `path`. No timestamp input.

---

### E. Strict Replay Gate

If `replay=true`, also verify:

* every referenced path exists
* hashes recompute identically during the same run
* manifest canonical JSON bytes are stable

Failure => `UNKNOWN` with `reason_tag: replay_instability`.

---

## 2) Tests Define Truth

### T1 — Path Rejection

* Input: `../secrets.txt` in TOUCHED_PATHS
* Expect: `UNKNOWN` `invalid_path`

### T2 — Hash Stability

* Same file bytes hashed twice
* Expect: same sha256

### T3 — Merkle Stability Under Reordering

* Same TOUCHED_PATHS shuffled
* Expect: identical `merkle_root` (because sorting by path)

### T4 — Symlink Block

* Touched path is symlink
* Expect: `UNKNOWN` `symlink_forbidden`

---

## 3) Witness Policy

Every manifest emission MUST include:

* `compute://manifest_builder/v0.1.0`
* `compute://manifest#sha256:<MANIFEST.sha256>`
* `compute://touched_merkle_root#sha256:<merkle_root>`

Downstream PROOF.json builder MUST refuse any run lacking these witnesses.

---

## 4) Output Schema (MANIFEST.json)

```json
{
  "status": "OK|UNKNOWN",
  "manifest_version": "0.1.0",
  "hash_algo": "sha256",
  "workspace_root": "<REPO_ROOT>",
  "touched": [
    {
      "path": "evidence/run_log.txt",
      "bytes": 1234,
      "sha256": "sha256...",
      "content_type_hint": "text/plain",
      "role_tag": "log"
    }
  ],
  "merkle_root": "sha256...",
  "unknown_reason": null
}
```

---

## 5) Verification Ladder

### Rung 641: Sanity

* [ ] all touched paths are relative + normalized
* [ ] sha256 present for each file

### Rung 274177: Consistency

* [ ] merkle root stable under input list reorder
* [ ] replay mode recompute passes

### Rung 65537: Final Seal

* [ ] manifest JSON canonicalized (sorted keys, compact separators)
* [ ] no timestamps/hostnames/pids anywhere

*"Auth: 65537"*

---

# Enhanced Features [v2.0.0]
Verification ladder: G0, G12, G13
Integration: prime-coder, gpt-mini-hygiene
Lane algebra: Pure Lane A (deterministic)
Preserved: All v1.0.0 features
