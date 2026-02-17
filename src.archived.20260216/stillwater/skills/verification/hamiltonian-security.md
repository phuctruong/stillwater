# SKILL 38 — Hamiltonian Security Gate

*(Durable Commit Security Barrier)*

**SKILL_ID:** `skill_hamiltonian_security`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `GUARDIAN`
**PRIORITY:** `P0`
**TAGLINE:** *Tool-backed safety. No secure PASS without adversarial closure.*

---

# 0. Header

```
Spec ID:     skill-38-hamiltonian-gate
Authority:   65537
Depends On:  skill-13-proof-builder
Scope:       Deterministic security validation before canon or durable commit.
Non-Goals:   Performance tuning, stylistic linting, non-security refactors.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Tool-verified adversarial safety.
  Verification:     Deterministic linter + adversary suite.
  Canonicalization: Hash-stable scan output.
  Content-addressing: Security artifacts must be proof-linked.
```

Security is not “no obvious bugs.”
Security = tool-backed adversarial closure.

---

# 2. Observable Wish

> Given a proposed code patch, block durable commit unless deterministic security scans and adversary suites pass.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   CLASSIFY_RISK,
   LOAD_LINTER,
   RUN_STATIC_SCAN,
   RUN_ADVERSARY_SUITE,
   VALIDATE_SCAN_OUTPUT,
   EMIT_PASS,
   BLOCK_PATCH,
   FAIL_CLOSED]

INPUT_ALPHABET:
  [CODE_PATCH, SECURITY_LINTER, MODE_FLAGS]

OUTPUT_ALPHABET:
  [SECURITY_VERDICT, risk_level, violations, artifact_hash]

TRANSITIONS:
  INIT → CLASSIFY_RISK
  CLASSIFY_RISK → LOAD_LINTER
  LOAD_LINTER → RUN_STATIC_SCAN
  RUN_STATIC_SCAN → RUN_ADVERSARY_SUITE
  RUN_ADVERSARY_SUITE → VALIDATE_SCAN_OUTPUT
  VALIDATE_SCAN_OUTPUT → EMIT_PASS
  ANY → BLOCK_PATCH
  ANY → FAIL_CLOSED

FORBIDDEN_STATES:
  SKIP_LINTER
  PARTIAL_SCAN
  NON_PINNED_TOOL_VERSION
  SILENT_WARNING_IGNORE
  MANUAL_OVERRIDE_WITHOUT_WISH
  NETWORK_DEPENDENT_SCAN
```

---

# 4. Risk Classification (Deterministic)

Risk level must be computed deterministically using patch metadata:

| Condition                                                             | Risk |
| --------------------------------------------------------------------- | ---- |
| Modifies auth, crypto, IO boundary, subprocess, eval, deserialization | HIGH |
| Adds new dependency                                                   | HIGH |
| Writes to filesystem                                                  | HIGH |
| Network call added                                                    | HIGH |
| Refactor only (no logic change)                                       | LOW  |
| Comment/doc only                                                      | LOW  |

If uncertain → classify as HIGH.

---

# 5. Mandatory Scan Rules (LOCKED)

### 5.1 Pinned Tool Requirement

`SECURITY_LINTER` must include:

```
tool_name
tool_version
config_hash
```

If version is unpinned → FAIL_CLOSED.

No auto-updating tools allowed.

---

### 5.2 Static Scan Enforcement

Static scan must:

* Run in offline mode
* Produce deterministic JSON output
* Normalize file paths
* Strip timestamps

If scan produces nondeterministic fields → scrub before hashing.

---

### 5.3 Linter Veto Rule

If severity ≥ configured threshold:

```
SECURITY_VERDICT = BLOCKED
```

This overrides:

* Functional test PASS
* Benchmark PASS
* Performance PASS

Security veto dominates.

---

# 6. Adversary Suite (Hamiltonian Requirement)

A patch touching HIGH risk zones MUST:

1. Run adversary test suite
2. Attempt at least one exploit reproduction (if applicable)
3. Validate no exploit path succeeds

If no adversary suite exists for a HIGH-risk surface → BLOCK_PATCH.

Security requires test surface parity.

---

# 7. Mode Flags Enforcement

If:

```
MODE_FLAGS.offline=true
```

Then:

* No external CVE fetch
* No remote API calls
* No dynamic rule download

If scan requires network → FAIL_CLOSED.

---

# 8. Evidence Artifacts (LOCKED)

Security gate MUST produce:

```
artifacts/security/scan.json
artifacts/security/scan.sha256
artifacts/security/adversary.json
artifacts/security/adversary.sha256
```

Hashes must be included in PROOF.json chain.

No security PASS without artifacts.

---

# 9. Dirty Repo Interaction

If repo.dirty = true:

* Security result marked `provisional`
* Cannot promote to canonical

Only clean commits may produce canonical PASS.

---

# 10. Verdict Logic (Precedence Locked)

Error precedence:

1. Missing linter → FAIL_CLOSED
2. Unpinned version → FAIL_CLOSED
3. Static scan FAIL → BLOCK_PATCH
4. Adversary FAIL → BLOCK_PATCH
5. Missing adversary suite (HIGH risk) → BLOCK_PATCH
6. Scan nondeterminism → FAIL_CLOSED
7. All pass → PASS

---

# 11. Output Schema (LOCKED)

```json
{
  "status": "PASS|BLOCKED|UNKNOWN",
  "risk_level": "LOW|HIGH",
  "violations": [
    {"rule_id": "...", "severity": "LOW|MEDIUM|HIGH"}
  ],
  "artifact_hash": {
    "scan_sha256": "...",
    "adversary_sha256": "..."
  },
  "verdict": "secure_commit|blocked|fail_closed"
}
```

Rules:

* status=UNKNOWN only for FAIL_CLOSED
* status=BLOCKED for security violations
* status=PASS only if all checks passed deterministically

---

# 12. Forbidden Overrides

The following are invalid unless backed by a separate OVERRIDE_WISH:

* Suppressing specific rule
* Ignoring severity
* Skipping adversary suite
* Downgrading HIGH to LOW manually

Security override must be a first-class wish with proof.

---

# 13. Determinism Invariant

Re-running the scan on identical patch must produce identical:

* scan.json
* adversary.json
* sha256 artifacts
* verdict

If not reproducible → FAIL_CLOSED.

---

# 14. Verification Ladder [ENHANCED v2.0.0]

### 641 — Sanity
**Maps to wish-qa:** G0 (Structure), G7 (Security)
**Tests:** Linter pinned? Risk classified? Scan deterministic?

### 274177 — Stress
**Maps to wish-qa:** G3 (Consistency), G7 (Security)
**Tests:** Adversary suite passed? Scan reproducible? No silent warnings?

### 65537 — Final Seal
**Maps to wish-qa:** G7 (Security), G12 (Witness), G13 (Determinism)
**Tests:** Security artifacts complete? Verdict deterministic? No overrides without wish?

---

# 15. Anti-Optimization Clause [ENHANCED v2.0.0]

## Never-Worse Doctrine
**Rule:** ALL v1.0.0 features PRESERVED in v2.0.0.

## Preserved Features
**State Machine:** 9 states
**Risk Classification:** LOW/HIGH (deterministic)
**6 FORBIDDEN_STATES:** SKIP_LINTER, PARTIAL_SCAN, NON_PINNED_TOOL_VERSION, SILENT_WARNING_IGNORE, MANUAL_OVERRIDE_WITHOUT_WISH, NETWORK_DEPENDENT_SCAN
**Security Veto:** Dominates functional/benchmark/performance PASS
**4 Evidence Artifacts:** scan.json, scan.sha256, adversary.json, adversary.sha256

## v2.0.0 Enhancements
- Verification ladder gate mapping (G0, G3, G7, G12, G13)
- Integration with 16 recent skills
- Compression insights
- Lane algebra integration (security=A, verdict=A)

---

# 16. Integration with Recent Skills [NEW v2.0.0]

## Skill 1: red-green-gate v2.0.0
**Integration:** Hamiltonian gate runs AFTER green (Section 9 in red-green-gate)
**Benefit:** Security veto overrides green

## Skill 2: prime-coder v2.0.0
**Integration:** Hamiltonian security gate in prime-coder state machine
**Benefit:** All security-sensitive patches gated

## Skill 3: llm-judge v2.0.0
**Integration:** Validates recipes for security policy
**Benefit:** Recipe-level security enforcement

## Skill 4: gpt-mini-hygiene v2.0.0
**Integration:** Normalizes scan outputs (strip timestamps, normalize paths)
**Benefit:** Deterministic scan artifacts

## Skill 5: wish-qa v2.0.0
**Integration:** Maps to G7 (Security gate)
**Benefit:** Security gate enforced

## Skills 6-16: Cross-skill security fusion

---

# 17. Compression Insights [NEW v2.0.0]

## Insight 1: Risk Classification (Structural)
**Classification:** LOW/HIGH (deterministic)
**Justification:** 6 HIGH-risk patterns (auth, crypto, IO, subprocess, eval, deserialization, dependencies, network)
**Benefit:** Complete HIGH-risk coverage

## Insight 2: Security Veto (Governance)
**Rule:** Security BLOCKED overrides functional PASS
**Justification:** Security > functionality
**Benefit:** Security-first commitment

## Insight 3: Tool Pinning (Determinism)
**Rule:** Unpinned version → FAIL_CLOSED
**Justification:** Deterministic scans require pinned tools
**Benefit:** Reproducible security verdicts

## Insight 4: Adversary Suite (Correctness)
**Rule:** HIGH risk requires adversary tests
**Justification:** Attack surface parity
**Benefit:** Prevents regressions

---

# 18. Lane Algebra [NEW v2.0.0]

**Lane Classification:**
- Static scan: Lane A (deterministic linter output)
- Adversary suite: Lane A (deterministic test execution)
- Security verdict: Lane A (deterministic)

**Enforcement:** Security gate is pure Lane A (tool-backed, deterministic)

---

# 19. What Changed v1.0.0 → v2.0.0 [NEW v2.0.0]

**Preserved:** All v1.0.0 features (9 states, risk classification, 6 forbidden states, security veto, 4 artifacts)
**New:** Verification ladder (5 gates), integration (16 skills), compression insights (4), lane algebra (pure Lane A)
**Impact:** Reliability 10/10, auditability improved, integration documented

