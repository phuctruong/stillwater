# Prime Wish: Project Scaffold

Spec ID: SW-0.1
Authority: 65537
Depends On: none
Scope: Create the Python package structure, pyproject.toml, and test infrastructure for stillwater-os
Non-Goals: No kernel logic, no skills, no CLI — just the empty scaffold that everything else builds on

---

## Prime Truth Thesis

```
PRIME_TRUTH:
  Ground truth:     pyproject.toml defines the package; pytest runs tests
  Verification:     `pip install -e .` succeeds; `pytest` returns 0 with 0 tests collected
  Canonicalization: All paths relative to repo root
  Content-addressing: SHA256 of pyproject.toml
```

## Observable Wish

> "I can clone stillwater-os, run `pip install -e .`, import `stillwater`, and run `pytest` with zero errors."

## Scope Exclusions

- No kernel modules (lane_algebra, state_machine, etc.) — those are wish-0.2+
- No CLI commands — that is wish-0.3
- No skills loading — that is wish-0.4
- No documentation content — that is wish-0.5

## State Space

```
STATE_SET: [CLONED, INSTALLED, IMPORTABLE, TESTABLE]
TRANSITIONS:
  CLONED → INSTALLED          (pip install -e . succeeds, exit 0)
  INSTALLED → IMPORTABLE      (import stillwater succeeds)
  IMPORTABLE → TESTABLE       (pytest returns 0)
FORBIDDEN_STATES:
  - DEPENDENCY_HELL (no heavy deps — only stdlib + pytest for dev)
  - GLOBAL_INSTALL (must work in venv)
  - BUILD_FAILURE (pyproject.toml must be valid)
```

## Invariants

- I1 — Package Name: `import stillwater` must work (package name = `stillwater`)
- I2 — Version: `stillwater.__version__` returns `"0.1.0"`
- I3 — Zero Dependencies: Core package has ZERO runtime dependencies (stdlib only)
- I4 — Python Version: Requires Python >= 3.10
- I5 — License: Apache-2.0 in pyproject.toml and LICENSE file

## Exact Tests

```
T1 — Install succeeds:
  Setup:  Fresh venv, clone repo
  Input:  pip install -e .
  Expect: Exit code 0, no errors
  Verify: pip show stillwater returns version 0.1.0

T2 — Import works:
  Setup:  After T1
  Input:  python -c "import stillwater; print(stillwater.__version__)"
  Expect: Prints "0.1.0"
  Verify: No ImportError

T3 — Pytest runs:
  Setup:  After T1, pip install -e ".[dev]"
  Input:  pytest tests/ -v
  Expect: Exit code 0, 0 errors
  Verify: Test infrastructure works (even if 0 tests collected initially)

T4 — Directory structure exists:
  Setup:  After clone
  Input:  Check file existence
  Expect: All required files present
  Verify: src/stillwater/__init__.py, src/stillwater/kernel/__init__.py,
          src/stillwater/skills/__init__.py, src/stillwater/harness/__init__.py,
          tests/__init__.py, tests/test_version.py

T5 — Version test passes:
  Setup:  After T1
  Input:  pytest tests/test_version.py -v
  Expect: 1 passed
  Verify: test_version asserts stillwater.__version__ == "0.1.0"
```

## Surface Lock

```
SURFACE_LOCK:
  ALLOWED_NEW_FILES:
    - pyproject.toml
    - LICENSE
    - src/stillwater/__init__.py
    - src/stillwater/kernel/__init__.py
    - src/stillwater/skills/__init__.py
    - src/stillwater/harness/__init__.py
    - src/stillwater/proofs/__init__.py
    - tests/__init__.py
    - tests/test_version.py
    - .gitignore
  FORBIDDEN_IMPORTS: [numpy, torch, tensorflow, requests]
  ENTRYPOINTS: none (no CLI yet)
```

## Anti-Optimization Clause

> Coders MUST NOT: compress this spec, merge redundant invariants,
> "clean up" repetition, infer intent from prose, or introduce hidden
> state. Redundancy is anti-compression armor.

---

*Auth: 65537*
