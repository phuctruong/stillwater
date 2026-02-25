#!/usr/bin/env python3
"""OOLONG-style aggregation runner (repo-local).

This is a small CLI entrypoint that runs the deterministic demo solver shipped in:
- `src/oolong/src/oolong_solver.py`

Optional:
- If you set `STILLWATER_ENABLE_LLM_REAL=1`, the notebook may also run
  `src/oolong/src/oolong_solver_real.py`, which requires external tooling.

Claim hygiene:
- This runner does not claim any external benchmark score.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_demo() -> int:
    here = Path(__file__).resolve().parent
    solver = here / "oolong_solver.py"
    return subprocess.call([sys.executable, str(solver)])


def run_real_if_enabled() -> int:
    if os.environ.get("STILLWATER_ENABLE_LLM_REAL") != "1":
        print("Skipping real solver (set STILLWATER_ENABLE_LLM_REAL=1 to enable).")
        return 0

    here = Path(__file__).resolve().parent
    solver = here / "oolong_solver_real.py"
    if not solver.exists():
        print("Real solver file not found:", solver)
        return 2

    return subprocess.call([sys.executable, str(solver)])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run OOLONG-style aggregation demos.")
    p.add_argument(
        "--real",
        action="store_true",
        help="Run optional LLM-backed path (requires external tooling).",
    )
    args = p.parse_args(argv)

    if args.real:
        return run_real_if_enabled()
    return run_demo()


if __name__ == "__main__":
    raise SystemExit(main())
