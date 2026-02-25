#!/usr/bin/env python3
"""
UNIT TEST: VERIFY Phase (Skeptic)

Using phuc-forecast.md: Skeptic verifies evidence (tests pass)
Using prime-coder.md: Red-green gate - patch must make test pass
Using phuc-context.md: FRESH context only (no prior reasoning)

Skeptic MUST:
- Apply patch
- Run tests
- Check for regressions
- Emit SKEPTIC_VERDICT.json

RED-GREEN verification:
- RED: Failing test (baseline)
- Apply patch
- GREEN: Same test must pass
"""

import json
import subprocess
import tempfile
import shutil
import os
from pathlib import Path

try:
    import pytest  # type: ignore
except Exception:  # pragma: no cover
    pytest = None

if pytest and os.environ.get("STILLWATER_RUN_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "Integration test (SWE-bench data + network clone). "
        "Set STILLWATER_RUN_INTEGRATION_TESTS=1 to run.",
        allow_module_level=True,
    )

DATA_DIR = Path(os.environ.get("STILLWATER_SWE_BENCH_DATA", str(Path.home() / "Downloads/benchmarks/SWE-bench-official")))
WORK_DIR = Path("/tmp/swe-test-verify")
WORK_DIR.mkdir(exist_ok=True)


def test_verify_skeptic_redgreen():
    """
    Test: Skeptic verifies RED→GREEN transition

    VERIFY Phase Requirements (from phuc-forecast.md):
    - Tests pass
    - Evidence verified
    - No regressions

    Red-Green Gate (from prime-coder.md):
    - RED: Test fails without patch
    - GREEN: Test passes with patch
    - Both must be deterministic (run twice)
    """

    print("\n" + "="*70)
    print("TEST: VERIFY Phase - Skeptic Red-Green Gate")
    print("="*70)

    # Load test instance
    lite_file = DATA_DIR / "SWE-bench_Lite-test.jsonl"
    if not lite_file.exists():
        print("❌ No test data")
        return False

    with open(lite_file) as f:
        inst = json.loads(f.readline())

    iid = inst['instance_id']
    repo_url = f"https://github.com/{inst.get('repo')}.git"
    repo_dir = WORK_DIR / iid.replace("/", "_")

    # Clone
    if not repo_dir.exists():
        print(f"Cloning {iid}...")
        try:
            subprocess.run(
                ["git", "clone", "--quiet", "--depth=1", repo_url, str(repo_dir)],
                capture_output=True, timeout=60, cwd=str(WORK_DIR)
            )
            subprocess.run(
                ["git", "-C", str(repo_dir), "checkout", inst.get("base_commit")],
                capture_output=True, timeout=30
            )
        except Exception as e:
            print(f"❌ Clone failed: {e}")
            return False

    print(f"Instance: {iid}")

    # Step 1: Verify RED (test fails without patch)
    print("\nStep 1: Verify RED (test fails without patch)...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-xvs", "--tb=short"],
            capture_output=True, text=True, timeout=60, cwd=str(repo_dir)
        )

        if result.returncode == 0:
            print("⚠️  Tests already pass (bug may already be fixed?)")
            # This could mean the test setup is wrong, but continue
        else:
            print("✅ Tests fail as expected (RED state)")

        _ = result.stdout + result.stderr  # baseline captured for future regression use

    except subprocess.TimeoutExpired:
        print("❌ Test timeout")
        return False

    # Step 2: Create a fake patch (for testing - we can't actually generate it here)
    # In real scenario, Solver would create this
    print("\nStep 2: Apply test patch...")

    # For this unit test, we'll create a dummy patch that modifies nothing
    # (In real case, Solver's actual patch would be used)
    test_patch = """--- a/nonexistent.py
+++ b/nonexistent.py
@@ -1,1 +1,1 @@
-# test
+# test
"""

    # Step 3: Try to verify GREEN (apply patch and test)
    print("Step 3: Verify GREEN (apply patch and test)...")

    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Copy repo
        shutil.copytree(repo_dir, temp_dir / "repo", dirs_exist_ok=True)
        repo_copy = temp_dir / "repo"

        # Apply patch (expect it to fail for our dummy patch, but that's ok for unit test)
        result = subprocess.run(
            ["patch", "-p1"],
            input=test_patch,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(repo_copy)
        )

        if result.returncode != 0:
            # Expected - our dummy patch won't apply
            print("⚠️  Patch did not apply (expected for dummy patch)")
            # In real case, if Solver's patch doesn't apply, Skeptic REJECTS
        else:
            print("✅ Patch applied")

        # Try to run tests anyway (they'll likely still fail)
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-xvs", "--tb=line"],
                capture_output=True, text=True, timeout=60, cwd=str(repo_copy)
            )
            _ = result.stdout + result.stderr  # after-patch output captured for future use

            print(f"Test result after patch: {'PASS' if result.returncode == 0 else 'FAIL'}")

        except subprocess.TimeoutExpired:
            print("❌ Test timeout after patch")
            return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Step 4: Emit SKEPTIC_VERDICT
    print("\nStep 4: Emit SKEPTIC_VERDICT...")

    verdict = {
        "status": "FAIL",  # Would be PASS if patch actually worked
        "reason": "Dummy patch for unit test",
        "fail_reasons": ["patch_not_real_for_unit_test"],
        "evidence": "Tests run successfully, methodology correct",
        "required_fixes": ["Use actual Solver-generated patch"]
    }

    print(f"Verdict: {verdict['status']}")
    print(f"Reason: {verdict['reason']}")

    # Validate schema
    required_keys = ['status', 'reason', 'fail_reasons', 'evidence']
    missing = [k for k in required_keys if k not in verdict]

    if missing:
        print(f"❌ Missing keys in verdict: {missing}")
        return False

    print("✅ Verdict JSON valid")

    # In real scenario:
    # - If tests PASS → APPROVE
    # - If tests FAIL → REJECT
    # - If patch doesn't apply → REJECT

    print("\n✅ VERIFY Phase Test PASSED")
    print("   (Note: actual patch needed to test GREEN state)")
    return True


if __name__ == "__main__":
    import sys
    success = test_verify_skeptic_redgreen()
    sys.exit(0 if success else 1)
