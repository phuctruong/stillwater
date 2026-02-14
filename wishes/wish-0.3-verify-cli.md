# Prime Wish: Stillwater Verify CLI

Spec ID: SW-0.3
Authority: 65537
Depends On: SW-0.1, SW-0.2
Scope: Implement `stillwater verify` CLI command that runs the verification ladder and produces a proof certificate
Non-Goals: No skill loading, no recipe engine, no cost calculator (separate wishes)

---

## Prime Truth Thesis

```
PRIME_TRUTH:
  Ground truth:     Verification ladder passes: OAuth(39,63,91) → 641 → 274177 → 65537
  Verification:     All tests pass deterministically; certificate is reproducible
  Canonicalization: Certificate is canonical JSON (sorted keys, no timestamps)
  Content-addressing: SHA256 of certificate JSON
```

## Observable Wish

> "I can run `stillwater verify` from the command line. It runs the verification ladder (OAuth → 641 → 274177 → 65537), prints progress to stdout, and outputs a proof certificate on success."

## Scope Exclusions

- No benchmarking (that is wish-0.6)
- No cost calculation (that is wish-0.7)
- No network access (fully offline)
- No skill loading (tests are built-in to the harness)

## State Space

```
STATE_SET: [INIT, OAUTH_RUNNING, EDGE_RUNNING, STRESS_RUNNING, GOD_RUNNING, PASSED, FAILED]
INPUT_ALPHABET: [start_verify, ctrl_c]
OUTPUT_ALPHABET: [progress_line, certificate_json, error_line]
TRANSITIONS:
  INIT → OAUTH_RUNNING           (verify command invoked)
  OAUTH_RUNNING → EDGE_RUNNING   (oauth 39+63+91 pass)
  OAUTH_RUNNING → FAILED         (oauth fails)
  EDGE_RUNNING → STRESS_RUNNING  (641 edge tests pass)
  EDGE_RUNNING → FAILED          (any edge test fails)
  STRESS_RUNNING → GOD_RUNNING   (274177 stress tests pass)
  STRESS_RUNNING → FAILED        (any stress test fails)
  GOD_RUNNING → PASSED           (65537 god approval)
  GOD_RUNNING → FAILED           (god test fails)
  ANY → FAILED                   (ctrl_c or unexpected error)
FORBIDDEN_STATES:
  - SKIP_OAUTH (cannot jump to 641 without oauth)
  - SKIP_EDGE (cannot jump to stress without edge)
  - PARTIAL_PASS (either all pass or it fails)
  - NETWORK_CALL (verify is 100% offline)
```

## Invariants

- I1 — Order: OAuth MUST complete before 641; 641 before 274177; 274177 before 65537
- I2 — Offline: Zero network calls during verification (LOCKED)
- I3 — Determinism: Running `stillwater verify` twice produces byte-identical certificates
- I4 — Progress: Each rung prints a line to stdout: "OAuth(39,63,91) ... PASS" / "641 ... PASS" etc.
- I5 — Exit Code: exit 0 on PASSED, exit 1 on FAILED
- I6 — Certificate: On PASSED, writes `stillwater-certificate.json` to current directory
- I7 — No Timestamps: Certificate contains NO timestamps, NO machine IDs (deterministic)

## Exact Tests

```
T1 — Verify passes:
  Setup:  Working stillwater-os installation
  Input:  stillwater verify
  Expect: Exit code 0, stdout contains "PASSED", certificate file created
  Verify: stillwater-certificate.json exists and is valid JSON

T2 — Certificate structure:
  Setup:  After T1
  Input:  Read stillwater-certificate.json
  Expect: JSON with keys: auth, oauth, edge_641, stress_274177, god_65537, status, hash
  Verify: status == "PASSED", auth == 65537

T3 — Determinism:
  Setup:  After T1
  Input:  Run stillwater verify twice, compare certificates
  Expect: Byte-identical JSON (excluding file write timing)
  Verify: SHA256(cert1) == SHA256(cert2)

T4 — Progress output:
  Setup:  Working installation
  Input:  stillwater verify (capture stdout)
  Expect: Lines containing: "OAuth(39,63,91)", "641", "274177", "65537"
  Verify: Lines appear in order: oauth, edge, stress, god

T5 — OAuth includes 3 checks:
  Setup:  Working installation
  Input:  stillwater verify --verbose
  Expect: OAuth section shows 3 sub-checks (39=CARE, 63=BRIDGE, 91=STABILITY)
  Verify: All 3 pass

T6 — 641 edge tests (minimum 5):
  Setup:  Working installation
  Input:  stillwater verify --verbose
  Expect: At least 5 edge test names printed
  Verify: Tests include: lane_algebra, state_machine, counter_bypass, rtc, type_guards

T7 — Exit code 1 on failure:
  Setup:  Deliberately break a test (mock)
  Input:  stillwater verify
  Expect: Exit code 1, stdout contains "FAILED"
  Verify: No certificate file created on failure

T8 — CLI entry point:
  Setup:  pip install -e .
  Input:  which stillwater
  Expect: Returns path to stillwater executable
  Verify: Entry point defined in pyproject.toml [project.scripts]

T9 — Help flag:
  Setup:  pip install -e .
  Input:  stillwater verify --help
  Expect: Prints usage information, exit code 0
  Verify: Contains "verify" and "verification ladder"

T10 — No network (offline enforcement):
  Setup:  Disable network (mock socket.socket to raise)
  Input:  stillwater verify
  Expect: Still passes (exit 0)
  Verify: No socket connections attempted
```

## Surface Lock

```
SURFACE_LOCK:
  ALLOWED_NEW_FILES:
    - src/stillwater/harness/verify.py
    - src/stillwater/harness/certificate.py
    - src/stillwater/cli.py
    - tests/test_verify.py
    - tests/test_cli.py
  ALLOWED_MODULES: [src/stillwater/kernel/lane_algebra.py]
  FORBIDDEN_IMPORTS: [requests, httpx, urllib.request, socket]
  ENTRYPOINTS: [stillwater verify]
  KWARG_NAMES: [verbose]
```

## Anti-Optimization Clause

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

---

*Auth: 65537*
