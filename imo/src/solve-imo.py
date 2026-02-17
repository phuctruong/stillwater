#!/usr/bin/env python3
"""IMO runner (repo-local).

This repository includes an executable demo solver and a notebook.

Paths:
- Demo solver: `imo/src/imo_2024_solver_proper.py`

Claim hygiene:
- This runner does not claim official IMO grading or a formal proof assistant.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    here = Path(__file__).resolve().parent
    return subprocess.call([sys.executable, str(here / "imo_2024_solver_proper.py")])


if __name__ == "__main__":
    raise SystemExit(main())
