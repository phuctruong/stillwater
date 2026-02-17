#!/usr/bin/env python3
"""
UNIT TEST: FORECAST Phase (Grace)

Using phuc-forecast.md: Grace identifies failure modes (premortem)
Using prime-coder.md: Evidence, determinism, red-green thinking
Using phuc-context.md: Fresh context, clear before each run

Grace MUST emit valid JSON with these keys:
- top_failure_modes_ranked
- edge_cases_to_test
- compatibility_risks
- stop_rules
"""

import json
import subprocess
import re
import os
from pathlib import Path
from typing import Optional, Dict

try:
    import pytest  # type: ignore
except Exception:  # pragma: no cover
    pytest = None

if pytest and os.environ.get("STILLWATER_RUN_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "Integration test (SWE-bench data + local wrapper). "
        "Set STILLWATER_RUN_INTEGRATION_TESTS=1 to run.",
        allow_module_level=True,
    )

DATA_DIR = Path(os.environ.get("STILLWATER_SWE_BENCH_DATA", str(Path.home() / "Downloads/benchmarks/SWE-bench-official")))
WORK_DIR = Path("/tmp/swe-test-forecast")
WORK_DIR.mkdir(exist_ok=True)


def test_forecast_grace_json():
    """
    Test: Grace emits valid JSON with failure mode analysis

    FORECAST Phase Requirements (from phuc-forecast.md):
    - Identify top 5 failure modes
    - Rank by severity
    - Specify edge cases
    - Identify compatibility risks
    - Set stop rules

    Anti-Rot (from phuc-context.md):
    - Grace sees FRESH context: problem + error + scout report
    - Grace does NOT see prior reasoning, only artifacts
    - Grace does NOT inherit narrative drift
    """

    print("\n" + "="*70)
    print("TEST: FORECAST Phase - Grace Failure Analysis")
    print("="*70)

    # Load test instance
    lite_file = DATA_DIR / "SWE-bench_Lite-test.jsonl"
    if not lite_file.exists():
        print("❌ No test data")
        return False

    with open(lite_file) as f:
        inst = json.loads(f.readline())

    iid = inst['instance_id']
    problem = inst.get('problem_statement', '')

    print(f"Instance: {iid}")
    print(f"Problem: {problem[:100]}...")

    # Fake Scout report (what Grace would receive)
    scout_report = {
        "task_summary": "Fix separability_matrix for nested CompoundModels",
        "repro_command": "pytest -xvs tests/modeling/test_compound.py",
        "failing_tests": ["test_nested_compound_separability"],
        "suspect_files": ["astropy/modeling/compound.py", "astropy/modeling/separable.py"],
        "acceptance_criteria": ["Test passes", "No regressions"]
    }

    # IMPROVED GRACE PROMPT (using phuc-context anti-rot principle)
    system = """AUTHORITY: 65537 (Phuc Forecast + Prime Coder)

TASK: Premortem analysis - how will a fix for this break things?

STRICT JSON SCHEMA (must include all keys):
{
  "top_failure_modes_ranked": [
    {"mode": "description", "risk_level": "HIGH|MED|LOW"}
  ],
  "edge_cases_to_test": ["specific test case", "..."],
  "compatibility_risks": ["backwards compat issue", "..."],
  "stop_rules": ["condition to abort", "..."]
}

OUTPUT REQUIREMENTS:
- Output ONLY valid JSON
- Rank failure modes by severity (HIGH first)
- Consider: Python versions, OS platforms, backwards compatibility
- If cannot analyze, output {"status": "NEED_INFO"}
"""

    prompt = f"""FRESH CONTEXT (Anti-Rot: no prior narrative):

SCOUT FOUND:
{json.dumps(scout_report, indent=2)}

PROBLEM CONTEXT:
{problem[:400]}

GRACE TASK (FORECAST Phase - Premortem):
Think adversarially: how will a patch for this BREAK other things?
- What Python versions might break?
- What edge cases might fail?
- What backwards compat risks?
- When should we stop and reject?

OUTPUT ONLY JSON (valid JSON, no text):"""

    payload = {
        "system": system,
        "prompt": prompt,
        "model": "haiku",
        "stream": False
    }

    print("Calling Grace with premortem prompt...")

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:8080/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            print("❌ API error")
            return False

        response = json.loads(result.stdout).get('response', '')

        # Extract JSON
        match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response, re.DOTALL)
        if not match:
            print(f"❌ No JSON found. Response:\n{response[:300]}")
            return False

        try:
            grace_memo = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return False

        # Check schema
        required_keys = ['top_failure_modes_ranked', 'edge_cases_to_test', 'compatibility_risks', 'stop_rules']
        missing = [k for k in required_keys if k not in grace_memo]

        if missing:
            print(f"❌ Missing keys: {missing}")
            return False

        print("✅ JSON schema valid")

        # Validate structure
        if not isinstance(grace_memo['top_failure_modes_ranked'], list):
            print(f"❌ top_failure_modes_ranked must be list")
            return False

        if len(grace_memo['top_failure_modes_ranked']) == 0:
            print("❌ top_failure_modes_ranked is empty")
            return False

        print("✅ Failure modes identified")

        # Print output
        print(f"\nGrace Forecast:")
        print(f"  Failure modes: {len(grace_memo['top_failure_modes_ranked'])}")
        for i, mode in enumerate(grace_memo['top_failure_modes_ranked'][:3], 1):
            print(f"    {i}. {mode.get('mode', '?')[:50]} ({mode.get('risk_level', '?')})")
        print(f"  Edge cases: {len(grace_memo['edge_cases_to_test'])}")
        print(f"  Compatibility risks: {len(grace_memo['compatibility_risks'])}")
        print(f"  Stop rules: {len(grace_memo['stop_rules'])}")

        print("\n✅ FORECAST Phase Test PASSED")
        return True

    except subprocess.TimeoutExpired:
        print("❌ API timeout")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = test_forecast_grace_json()
    sys.exit(0 if success else 1)
