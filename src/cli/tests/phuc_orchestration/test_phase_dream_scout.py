#!/usr/bin/env python3
"""
UNIT TEST: DREAM Phase (Scout)

Using phuc-forecast.md: Scout defines what "fixed" means
Using prime-coder.md: Evidence required, red-green gate
Using phuc-context.md: Full context, anti-rot

Scout MUST emit valid JSON with these keys:
- task_summary
- repro_command
- failing_tests
- suspect_files
- acceptance_criteria
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
WORK_DIR = Path("/tmp/swe-test-dream")
WORK_DIR.mkdir(exist_ok=True)


def load_test_instance():
    """Load one real SWE-bench instance"""
    lite_file = DATA_DIR / "SWE-bench_Lite-test.jsonl"
    if lite_file.exists():
        with open(lite_file) as f:
            return json.loads(f.readline())
    return None


def setup_test_repo() -> tuple:
    """Clone and setup test repo - returns (iid, repo_dir, problem, error, source)"""
    inst = load_test_instance()
    if not inst:
        return None, None, None, None, None

    iid = inst['instance_id']
    repo_url = f"https://github.com/{inst.get('repo')}.git"
    repo_dir = WORK_DIR / iid.replace("/", "_")

    if not repo_dir.exists():
        try:
            subprocess.run(
                ["git", "clone", "--quiet", "--depth=1", repo_url, str(repo_dir)],
                capture_output=True, timeout=60, cwd=str(WORK_DIR)
            )
            subprocess.run(
                ["git", "-C", str(repo_dir), "checkout", inst.get("base_commit")],
                capture_output=True, timeout=30
            )
        except Exception:
            return None, None, None, None, None

    # Get full context
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-xvs", "--tb=short"],
            capture_output=True, text=True, timeout=60, cwd=str(repo_dir)
        )
        error = result.stdout + result.stderr

        py_files = [f for f in repo_dir.glob("**/*.py")
                   if not any(x in f.name for x in ['setup', '__init__', 'conftest', 'config'])]
        if not py_files:
            return None, None, None, None, None

        source = open(py_files[0]).read()
        problem = inst.get('problem_statement', '')

        return iid, repo_dir, problem, error, source

    except Exception:
        return None, None, None, None, None


def scout_analyze_with_improved_prompt(problem: str, error: str, source: str) -> Optional[Dict]:
    """
    Scout analyzes problem and emits JSON.

    DREAM Phase Requirements (from phuc-forecast.md):
    - Define what "fixed" means
    - Identify acceptance criteria
    - Locate suspect files
    - Provide minimal reproduction

    Red-Green Gate (from prime-coder.md):
    - Must identify FAILING test (RED)
    - Must identify what would make it PASS (GREEN)

    Context (from phuc-context.md):
    - FULL problem statement (no truncation)
    - FULL error output (no truncation)
    - FULL source code (no truncation)
    """

    # IMPROVED PROMPT (using all 3 skills) - FAIL-CLOSED VERSION
    system = """AUTHORITY: 65537 (Phuc Forecast + Prime Coder + Phuc Context)

TASK: Analyze SWE-bench bug and emit SCOUT_REPORT.json

YOU MUST OUTPUT VALID JSON. NO QUESTIONS, NO CLARIFICATIONS, NO ESCAPE HATCHES.

REQUIRED JSON SCHEMA:
{
  "task_summary": "one sentence: what's broken?",
  "repro_command": "exact pytest command to reproduce (parse from error output if needed)",
  "failing_tests": ["list of test names from error output"],
  "suspect_files": ["files mentioned in problem or error, highest priority first"],
  "acceptance_criteria": ["test passes without failure", "no regressions"]
}

RULES:
1. Infer missing information from provided context (problem + error + source)
2. Extract test command from pytest error traceback
3. Extract test names from failure messages
4. Extract file paths from error output and source code
5. DO NOT ask for clarification - USE WHAT YOU HAVE
6. Output ONLY valid JSON, no text before or after
7. All five keys are required in output
"""

    prompt = f"""REAL SWE-BENCH INSTANCE:

PROBLEM STATEMENT:
{problem}

PYTEST ERROR OUTPUT (contains test command, test names, file paths):
{error}

SOURCE CODE CONTEXT:
{source}

SCOUT TASK: Analyze this bug based on provided context. Extract all information from error output and problem statement. Emit valid JSON:
"""

    payload = {
        "system": system,
        "prompt": prompt,
        "model": "haiku",
        "stream": False
    }

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:8080/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            return None

        response = json.loads(result.stdout).get('response', '')

        # Try to extract JSON (handle response wrapped in explanation)
        # Look for complete JSON object
        match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response, re.DOTALL)
        if not match:
            print(f"DEBUG: No JSON found. Response:\n{response[:300]}")
            return None

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse error: {e}")
            print(f"DEBUG: Extracted: {match.group(0)[:200]}")
            return None

    except subprocess.TimeoutExpired:
        print("DEBUG: API timeout")
        return None
    except Exception as e:
        print(f"DEBUG: Exception: {e}")
        return None


def test_dream_scout_json():
    """
    Test: Scout emits valid JSON with required schema
    RED: Haiku asks questions or outputs invalid JSON
    GREEN: Haiku outputs valid JSON with all required keys
    """
    print("\n" + "="*70)
    print("TEST: DREAM Phase - Scout JSON Output")
    print("="*70)

    iid, repo_dir, problem, error, source = setup_test_repo()
    if not iid:
        print("❌ SETUP FAILED - could not load/clone test instance")
        return False

    print(f"Instance: {iid}")
    print(f"Problem chars: {len(problem)}")
    print(f"Error chars: {len(error)}")
    print(f"Source chars: {len(source)}")

    print("\nCalling Scout with improved prompt...")
    scout_report = scout_analyze_with_improved_prompt(problem, error, source)

    if scout_report is None:
        print("❌ Scout returned None (JSON parse failed)")
        return False

    # Check if it's a NEED_INFO response
    if scout_report.get("status") == "NEED_INFO":
        print(f"⚠️  Scout returned NEED_INFO: {scout_report.get('missing')}")
        return False

    # Validate schema
    required_keys = ['task_summary', 'repro_command', 'failing_tests', 'suspect_files', 'acceptance_criteria']
    missing = [k for k in required_keys if k not in scout_report]

    if missing:
        print(f"❌ Missing keys: {missing}")
        print(f"   Keys present: {list(scout_report.keys())}")
        return False

    print("✅ JSON schema valid (all required keys present)")

    # Validate key types
    if not isinstance(scout_report['failing_tests'], list):
        print(f"❌ failing_tests must be list, got {type(scout_report['failing_tests'])}")
        return False

    if not isinstance(scout_report['suspect_files'], list):
        print(f"❌ suspect_files must be list, got {type(scout_report['suspect_files'])}")
        return False

    print("✅ Field types valid")

    # Validate non-empty
    if not scout_report['task_summary']:
        print("❌ task_summary is empty")
        return False

    if not scout_report['suspect_files']:
        print("❌ suspect_files is empty (must identify files to change)")
        return False

    print("✅ Required fields populated")

    # Print output
    print("\nScout Report:")
    print(f"  Summary: {scout_report['task_summary'][:60]}")
    print(f"  Repro: {scout_report['repro_command'][:60]}")
    print(f"  Failing tests: {scout_report['failing_tests'][:2]}")
    print(f"  Suspect files: {scout_report['suspect_files'][:2]}")
    print(f"  Acceptance: {scout_report['acceptance_criteria'][:2]}")

    print("\n✅ DREAM Phase Test PASSED")
    return True


if __name__ == "__main__":
    import sys
    success = test_dream_scout_json()
    sys.exit(0 if success else 1)
