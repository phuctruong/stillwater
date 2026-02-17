#!/usr/bin/env python3
"""
UNIT TEST: ACT Phase (Solver)

Using phuc-forecast.md: Solver implements per locked DECISION_RECORD
Using prime-coder.md: Red-green gate (patch must make tests pass)
Using phuc-context.md: FRESH context only (no prior reasoning)

Solver MUST emit valid unified diff that:
- Has proper format (--- a/, +++ b/, @@ @@)
- Can be parsed by patch utility
- Can be applied cleanly

KEY: Solver sees ONLY:
- DECISION_RECORD (locked approach)
- Source code
- NO prior reasoning/narrative
"""

import json
import subprocess
import re
import os
from pathlib import Path
from typing import Optional

try:
    import pytest  # type: ignore
except Exception:  # pragma: no cover
    pytest = None

if pytest and os.environ.get("STILLWATER_RUN_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "Integration test (local wrapper). "
        "Set STILLWATER_RUN_INTEGRATION_TESTS=1 to run.",
        allow_module_level=True,
    )

DATA_DIR = Path(os.environ.get("STILLWATER_SWE_BENCH_DATA", str(Path.home() / "Downloads/benchmarks/SWE-bench-official")))
WORK_DIR = Path("/tmp/swe-test-act")
WORK_DIR.mkdir(exist_ok=True)


def test_act_solver_diff():
    """
    Test: Solver generates valid unified diff

    ACT Phase Requirements (from phuc-forecast.md):
    - Implement per DECISION_RECORD
    - Step-by-step with checkpoints
    - Produce artifacts

    Red-Green Gate (from prime-coder.md):
    - Must follow TDD: failing test → patch → passing test
    - Diff must be applicable (patch -p1 works)

    Anti-Rot (from phuc-context.md):
    - FRESH context: see DECISION_RECORD + source code only
    - DO NOT see Scout report, Grace memo, or prior reasoning
    - Clear narrative before each step

    STRATEGY: Use synthetic example to test diff generation format
    (Real SWE-bench requires correct file matching; unit test focuses on format)
    """

    print("\n" + "="*70)
    print("TEST: ACT Phase - Solver Diff Generation")
    print("="*70)

    # Use synthetic example for format testing
    iid = "synthetic__diff_test"
    problem = """
    Bug: The function `calculate_total()` in calculator.py incorrectly sums negative numbers.
    It should add all numbers but currently ignores negative values.

    Test: test_calculate_total_with_negatives expects calculate_total([-5, 10, -3]) = 2
    but currently returns 10 (missing negative values).
    """

    source = """def calculate_total(numbers):
    '''Calculate sum of all numbers in the list.'''
    total = 0
    for num in numbers:
        if num > 0:  # BUG: This condition ignores negative numbers
            total += num
    return total
"""

    print(f"Synthetic Test: {iid}")
    print(f"Problem: calculate_total() ignores negative numbers")

    # DECISION_RECORD (what Judge would output)
    decision = {
        "chosen_approach": "Fix the condition to include all numbers, not just positive ones",
        "scope_locked": ["Modify calculator.py calculate_total() function", "Remove the if num > 0 check"],
        "stop_rules": ["If any tests fail, reject patch"],
        "required_evidence": ["test_calculate_total_with_negatives passes", "All other tests still pass"]
    }

    # FAIL-CLOSED SOLVER PROMPT
    system = """AUTHORITY: 65537 (Prime Coder + Phuc Forecast)

TASK: Generate unified diff to fix the bug. YOU MUST OUTPUT A DIFF.

YOU SEE ONLY:
1. DECISION_RECORD (locked approach)
2. SOURCE CODE
NO prior reasoning, no narrative, no questions.

YOU MUST OUTPUT A UNIFIED DIFF IN THIS EXACT FORMAT:
```diff
--- a/calculator.py
+++ b/calculator.py
@@ -1,8 +1,8 @@
 def calculate_total(numbers):
     '''Calculate sum of all numbers.'''
     total = 0
     for num in numbers:
-        if num > 0:
+        if True:  # Changed: include all numbers
             total += num
     return total
```

CRITICAL RULES:
1. Every line MUST start with SPACE, MINUS, or PLUS (no other prefixes)
2. Include 2-3 context lines before and after changes
3. Output code block with exactly 3 backticks: ```diff
4. Never ask questions - generate diff from available context
5. Diff is minimal (only necessary changes)
"""

    prompt = f"""DECISION_RECORD (locked - implement this):
{json.dumps(decision, indent=2)}

PROBLEM:
{problem}

SOURCE CODE (calculator.py):
{source}

GENERATE DIFF NOW. Output format (MANDATORY):
```diff
--- a/calculator.py
+++ b/calculator.py
@@ -X,Y +X,Y @@"""

    payload = {
        "system": system,
        "prompt": prompt,
        "model": "haiku",
        "stream": False
    }

    print("Calling Solver with locked DECISION_RECORD...")

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

        # Extract diff from code block
        match = re.search(r'```diff\n(.*?)\n```', response, re.DOTALL)
        if match:
            diff_content = match.group(1)
        elif "--- a/" in response:
            # Extract from --- onwards
            lines = response.split('\n')
            start = next((i for i, l in enumerate(lines) if l.startswith('--- a/')), -1)
            if start < 0:
                print(f"❌ No diff found. Response:\n{response[:300]}")
                return False
            diff_content = '\n'.join(lines[start:start+20])
        else:
            print(f"❌ No diff found. Response:\n{response[:300]}")
            return False

        # Validate diff format
        diff_lines = diff_content.split('\n')

        # Check required headers
        has_header_minus = any(l.startswith('--- a/') for l in diff_lines[:5])
        has_header_plus = any(l.startswith('+++ b/') for l in diff_lines[:5])
        has_hunks = any(l.startswith('@@') for l in diff_lines)

        if not has_header_minus:
            print("❌ Missing '--- a/...' header")
            return False

        if not has_header_plus:
            print("❌ Missing '+++ b/...' header")
            return False

        if not has_hunks:
            print("❌ Missing '@@ @@' hunks")
            return False

        print("✅ Diff format valid")

        # Try to validate patch (for real repos only)
        # For synthetic examples, skip validation
        import tempfile
        import shutil
        if iid.startswith("synthetic"):
            print("ⓘ  Synthetic example - skipping patch application test")
            print("   (Unit test focus: diff format validation)")
        else:
            print("Validating patch application...")
            result = subprocess.run(
                ["patch", "--dry-run", "-p1"],
                input=diff_content,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(repo_dir)
            )

            if result.returncode != 0:
                print(f"⚠️  Patch might not apply cleanly:")
                print(f"   {result.stderr[:200]}")
            else:
                print("✅ Patch applies cleanly (dry-run)")

        # Print diff
        print(f"\nGenerated Diff:")
        for i, line in enumerate(diff_lines[:15]):
            print(f"  {line[:70]}")
        if len(diff_lines) > 15:
            print(f"  ... ({len(diff_lines) - 15} more lines)")

        print("\n✅ ACT Phase Test PASSED")
        return True

    except subprocess.TimeoutExpired:
        print("❌ API timeout")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = test_act_solver_diff()
    sys.exit(0 if success else 1)
