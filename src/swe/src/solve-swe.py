#!/usr/bin/env python3
"""SWE runner (repo-local).

This is a small CLI entrypoint for SWE-related demos in this repository.

Paths:
- Demo / educational scaffold: `src/swe/src/swe_solver.py`
- Optional "real" path (requires external data + tooling; disabled by default): `src/swe/src/swe_solver_real.py`
  - Enable explicitly with: `STILLWATER_ENABLE_LEGACY_SOLVERS=1`

Claim hygiene:
- This runner does not claim reproduced SWE-bench success rates.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _run(path: Path) -> int:
    return subprocess.call([sys.executable, str(path)])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run SWE demos.")
    p.add_argument(
        "--real",
        action="store_true",
        help="Run optional real solver (requires external SWE-bench data + local tooling).",
    )
    args = p.parse_args(argv)

    here = Path(__file__).resolve().parent
    if args.real:
        if os.environ.get("STILLWATER_ENABLE_LEGACY_SOLVERS") != "1":
            print("❌ Refusing to run legacy/experimental solver by default.", file=sys.stderr)
            print("Enable explicitly with: export STILLWATER_ENABLE_LEGACY_SOLVERS=1", file=sys.stderr)
            return 2
        return _run(here / "swe_solver_real.py")
    return _run(here / "swe_solver.py")


if __name__ == "__main__":
    raise SystemExit(main())
