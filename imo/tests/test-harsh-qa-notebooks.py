#!/usr/bin/env python3
"""
HARSH QA NOTEBOOK RUNNER (Stillwater, 2026-02-19)

Goals:
1) Ensure key notebooks exist and have no committed error outputs.
2) Execute PHUC-SKILLS-SECRET-SAUCE.ipynb in deterministic mock mode.
3) Verify A/B/AB/ABC move matrix artifacts are emitted.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_notebook(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def notebook_has_error_outputs(path: Path) -> bool:
    nb = load_notebook(path)
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                return True
    return False


def check_notebook_exists(path: Path) -> bool:
    ok = path.exists()
    print(f"  {'PASS' if ok else 'FAIL'} exists: {path.name}")
    return ok


def check_notebook_clean(path: Path) -> bool:
    if not path.exists():
        print(f"  FAIL clean-check skipped (missing): {path.name}")
        return False
    ok = not notebook_has_error_outputs(path)
    print(f"  {'PASS' if ok else 'FAIL'} no committed error outputs: {path.name}")
    return ok


def run_skills_notebook_mock(root: Path) -> tuple[bool, str]:
    nb = root / "PHUC-SKILLS-SECRET-SAUCE.ipynb"
    if not nb.exists():
        return False, "missing PHUC-SKILLS-SECRET-SAUCE.ipynb"

    env = os.environ.copy()
    env["STILLWATER_AB_BACKEND"] = "mock"
    env["STILLWATER_AB_CACHE"] = "0"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    cmd = [
        sys.executable,
        "-m",
        "nbconvert",
        "--execute",
        "--to",
        "notebook",
        "--inplace",
        str(nb),
    ]
    p = subprocess.run(
        cmd,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if p.returncode != 0:
        msg = (p.stdout or "") + "\n" + (p.stderr or "")
        return False, msg[-2000:]
    return True, "ok"


def check_skills_artifacts(root: Path) -> tuple[bool, str]:
    results_path = root / "artifacts" / "skills_ab" / "results.json"
    report_path = root / "artifacts" / "skills_ab" / "report.md"

    if not results_path.exists():
        return False, f"missing results artifact: {results_path}"
    if not report_path.exists():
        return False, f"missing report artifact: {report_path}"

    data = json.loads(results_path.read_text(encoding="utf-8"))
    scenario_variants = data.get("scenario_variants", {})
    summary = data.get("summary", {})
    runs = data.get("runs", [])

    required_arms = {
        "A_baseline_white_belt",
        "AB_guarded_coder",
        "ABC_master_stack",
    }
    seen_arms = set()
    for arms in scenario_variants.values():
        if isinstance(arms, list):
            seen_arms.update(arms)

    if not required_arms.issubset(seen_arms):
        return False, f"missing required arms in scenario_variants: {sorted(required_arms - seen_arms)}"

    required_scenarios = {"swarms_scout", "forecast_plan", "micro_swe_config"}
    if not required_scenarios.issubset(set(summary.keys())):
        return False, f"missing scenarios in summary: {sorted(required_scenarios - set(summary.keys()))}"

    if not runs:
        return False, "runs list is empty"

    report_text = report_path.read_text(encoding="utf-8")
    if "Kung-Fu Move Cards" not in report_text:
        return False, "report missing 'Kung-Fu Move Cards' section"

    return True, "artifacts verified"


def main() -> int:
    root = repo_root()
    notebooks = [
        root / "HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb",
        root / "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        root / "HOW-TO-CRUSH-SWE-BENCHMARK.ipynb",
        root / "PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb",
        root / "PHUC-SKILLS-SECRET-SAUCE.ipynb",
    ]

    print("=" * 72)
    print("STILLWATER HARSH QA NOTEBOOK RUNNER")
    print("=" * 72)

    ok = True
    print("\n[1] Existence checks")
    for nb in notebooks:
        ok = check_notebook_exists(nb) and ok

    print("\n[2] Committed notebook cleanliness")
    for nb in notebooks:
        ok = check_notebook_clean(nb) and ok

    print("\n[3] Execute PHUC-SKILLS notebook in mock mode")
    exec_ok, exec_msg = run_skills_notebook_mock(root)
    print(f"  {'PASS' if exec_ok else 'FAIL'} mock execution")
    if not exec_ok:
        print(exec_msg)
        ok = False

    print("\n[4] Validate emitted artifacts and move matrix")
    art_ok, art_msg = check_skills_artifacts(root)
    print(f"  {'PASS' if art_ok else 'FAIL'} {art_msg}")
    ok = ok and art_ok

    print("\n" + "=" * 72)
    if ok:
        print("ALL HARSH QA CHECKS PASSED")
        return 0
    print("HARSH QA FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
