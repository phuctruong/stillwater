#!/usr/bin/env python3
"""SWE runner (repo-local).

This is a small CLI entrypoint for SWE-related demos in this repository.

Paths:
- Demo / educational scaffold: `swe/src/swe_solver.py`
- Optional "real" path (requires external data + tooling): `swe/src/swe_solver_real.py`

Claim hygiene:
- This runner does not claim reproduced SWE-bench success rates.
"""

from __future__ import annotations

import argparse
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
        return _run(here / "swe_solver_real.py")
    return _run(here / "swe_solver.py")


if __name__ == "__main__":
    raise SystemExit(main())
