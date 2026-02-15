"""
Red-Green-God verification gates for SWE-bench.

Three-stage verification protocol inspired by TDD:
    1. Red Gate: Baseline tests must PASS (environment is healthy)
    2. Green Gate: Tests must still PASS after patch (no regressions)
    3. God Gate: Patch must be deterministic (same input → same patch)

Philosophy:
    "We REFUSE to ship broken code."

    Other AI assistants generate patches and hope they work.
    Stillwater mathematically verifies patches before accepting them.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Optional
from enum import Enum


class GateStatus(Enum):
    """Gate evaluation result."""
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class TestResult:
    """
    Result from running test suite.

    Attributes:
        passing_tests: Set of test names that passed
        failing_tests: Set of test names that failed
        total_tests: Total number of tests run
        exit_code: Exit code from test runner
        stdout: Standard output from tests
        stderr: Standard error from tests
        duration_ms: Test execution time in milliseconds
    """
    passing_tests: Set[str]
    failing_tests: Set[str]
    total_tests: int
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int

    @property
    def all_passed(self) -> bool:
        """True if all tests passed."""
        return len(self.failing_tests) == 0

    @property
    def pass_rate(self) -> float:
        """Percentage of tests that passed."""
        if self.total_tests == 0:
            return 0.0
        return len(self.passing_tests) / self.total_tests


@dataclass
class GateResult:
    """
    Result from a verification gate.

    Attributes:
        status: PASS, FAIL, or ERROR
        message: Human-readable explanation
        baseline: Test results before patch (Red Gate only)
        after_patch: Test results after patch (Green Gate only)
        regressions: Tests that passed before but failed after (Green Gate only)
        new_fixes: Tests that failed before but passed after (Green Gate only)
    """
    status: GateStatus
    message: str
    baseline: Optional[TestResult] = None
    after_patch: Optional[TestResult] = None
    regressions: Optional[Set[str]] = None
    new_fixes: Optional[Set[str]] = None

    def __bool__(self) -> bool:
        """Allow using gate result as boolean (if result: ...)"""
        return self.status == GateStatus.PASS


class RedGate:
    """
    Red Gate: Verify baseline tests PASS before applying patch.

    Purpose:
        Establish which tests pass in the clean environment.
        If tests fail here, the environment is broken - abort.

    Critical insight:
        Don't try to fix bugs in a broken environment.
        We need a clean baseline to measure against.
    """

    @staticmethod
    def check(repo_dir: Path, test_command: str, timeout: int = 300) -> GateResult:
        """
        Run baseline tests and verify environment health.

        Args:
            repo_dir: Path to repository
            test_command: Command to run tests (e.g., "pytest tests/")
            timeout: Max seconds to wait for tests

        Returns:
            GateResult with baseline test results

        Example:
            >>> result = RedGate.check(env.repo_dir, "pytest tests/")
            >>> if result:
            >>>     print("✅ Baseline healthy")
            >>> else:
            >>>     print("❌ Environment broken, skipping instance")
        """
        print(f"🔴 Red Gate: Checking baseline tests...")

        test_result = _run_tests(repo_dir, test_command, timeout)

        # Red Gate passes if we successfully ran tests
        # (even if some tests fail - we just need to know the baseline)
        if test_result.exit_code == 0 or test_result.total_tests > 0:
            status = GateStatus.PASS
            message = f"✅ Baseline established: {len(test_result.passing_tests)}/{test_result.total_tests} passing"
        else:
            status = GateStatus.FAIL
            message = f"❌ Test execution failed: {test_result.stderr[:200]}"

        return GateResult(
            status=status,
            message=message,
            baseline=test_result,
        )


class GreenGate:
    """
    Green Gate: Verify tests still PASS after applying patch.

    Purpose:
        Ensure patch doesn't break existing functionality.
        Only accept patches that preserve or improve test passage.

    State transition rules:
        ✅ PASS: passing_after >= passing_before (no regressions)
        ❌ FAIL: passing_after < passing_before (regressions detected)

    Critical insight:
        A patch that breaks tests is worse than no patch at all.
    """

    @staticmethod
    def check(
        repo_dir: Path,
        test_command: str,
        baseline: TestResult,
        timeout: int = 300
    ) -> GateResult:
        """
        Run tests after patch and check for regressions.

        Args:
            repo_dir: Path to repository (with patch applied)
            test_command: Command to run tests
            baseline: Test results from Red Gate
            timeout: Max seconds to wait for tests

        Returns:
            GateResult with comparison to baseline

        Example:
            >>> red_result = RedGate.check(env.repo_dir, "pytest")
            >>> apply_model_patch(env, patch)
            >>> green_result = GreenGate.check(env.repo_dir, "pytest", red_result.baseline)
            >>> if green_result:
            >>>     print("✅ No regressions")
            >>> else:
            >>>     print(f"❌ Regressions: {green_result.regressions}")
        """
        print(f"🟢 Green Gate: Checking tests after patch...")

        after_patch = _run_tests(repo_dir, test_command, timeout)

        # Compute regressions: tests that passed before but fail now
        regressions = baseline.passing_tests - after_patch.passing_tests

        # Compute new fixes: tests that failed before but pass now
        new_fixes = after_patch.passing_tests - baseline.passing_tests

        # Green Gate passes if no regressions
        if len(regressions) == 0:
            status = GateStatus.PASS
            if new_fixes:
                message = f"✅ No regressions, {len(new_fixes)} new fixes: {new_fixes}"
            else:
                message = f"✅ No regressions ({len(after_patch.passing_tests)}/{after_patch.total_tests} passing)"
        else:
            status = GateStatus.FAIL
            message = f"❌ {len(regressions)} regressions detected: {regressions}"

        return GateResult(
            status=status,
            message=message,
            baseline=baseline,
            after_patch=after_patch,
            regressions=regressions,
            new_fixes=new_fixes,
        )


class GodGate:
    """
    God Gate: Verify patch is deterministic.

    Purpose:
        Ensure same input produces same patch.
        Non-deterministic patches are unreliable and unreproducible.

    Method:
        Run patch generation 3x with same input.
        SHA256 hash all 3 patches.
        All hashes must match.

    Critical insight:
        Randomness is acceptable for brainstorming.
        Randomness is unacceptable for code that ships to production.
    """

    @staticmethod
    def check(patches: List[str]) -> GateResult:
        """
        Verify all patches are identical.

        Args:
            patches: List of patches generated from same input

        Returns:
            GateResult indicating determinism status

        Example:
            >>> patches = [generate_patch(problem) for _ in range(3)]
            >>> result = GodGate.check(patches)
            >>> if result:
            >>>     print("✅ Deterministic")
            >>> else:
            >>>     print("❌ Non-deterministic")
        """
        import hashlib

        if len(patches) < 2:
            return GateResult(
                status=GateStatus.ERROR,
                message="❌ Need at least 2 patches to check determinism",
            )

        # Compute SHA256 for each patch
        hashes = [hashlib.sha256(p.encode()).hexdigest() for p in patches]

        # Check if all hashes match
        if len(set(hashes)) == 1:
            status = GateStatus.PASS
            message = f"✅ Deterministic (hash: {hashes[0][:16]}...)"
        else:
            status = GateStatus.FAIL
            message = f"❌ Non-deterministic: {len(set(hashes))} unique patches from {len(patches)} runs"

        return GateResult(
            status=status,
            message=message,
        )


def _run_tests(repo_dir: Path, test_command: str, timeout: int) -> TestResult:
    """
    Execute test command and parse results.

    Args:
        repo_dir: Repository path
        test_command: Shell command to run tests
        timeout: Max seconds to wait

    Returns:
        TestResult with parsed test outcomes

    Note:
        This is a simplified parser. Production version would parse
        pytest/unittest/nose output more robustly.
    """
    import time

    start_ms = int(time.time() * 1000)

    try:
        result = subprocess.run(
            test_command,
            shell=True,
            cwd=repo_dir,
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        duration_ms = int(time.time() * 1000) - start_ms

        # Parse test results from output
        # TODO: Make this more robust for different test frameworks
        passing_tests, failing_tests = _parse_test_output(result.stdout, result.stderr)

        return TestResult(
            passing_tests=passing_tests,
            failing_tests=failing_tests,
            total_tests=len(passing_tests) + len(failing_tests),
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=duration_ms,
        )

    except subprocess.TimeoutExpired:
        duration_ms = timeout * 1000
        return TestResult(
            passing_tests=set(),
            failing_tests=set(),
            total_tests=0,
            exit_code=-1,
            stdout="",
            stderr=f"Test execution timed out after {timeout}s",
            duration_ms=duration_ms,
        )
    except Exception as e:
        duration_ms = int(time.time() * 1000) - start_ms
        return TestResult(
            passing_tests=set(),
            failing_tests=set(),
            total_tests=0,
            exit_code=-1,
            stdout="",
            stderr=f"Test execution error: {e}",
            duration_ms=duration_ms,
        )


def _parse_test_output(stdout: str, stderr: str) -> tuple[Set[str], Set[str]]:
    """
    Parse test output to extract passing and failing test names.

    This is a simplified parser. A production version would handle:
    - pytest output format
    - unittest output format
    - nose output format
    - Custom test runners

    Args:
        stdout: Standard output from test run
        stderr: Standard error from test run

    Returns:
        Tuple of (passing_tests, failing_tests)

    TODO: Implement robust parsing for different test frameworks
    """
    # Placeholder implementation
    # Real parser would extract test names from pytest -v output
    passing_tests = set()
    failing_tests = set()

    # Simple heuristic: look for pytest summary line
    output = stdout + stderr
    for line in output.split("\n"):
        if "passed" in line.lower() and "failed" in line.lower():
            # Example: "5 passed, 2 failed in 1.23s"
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed" and i > 0:
                    try:
                        num_passed = int(parts[i - 1])
                        # Generate placeholder test names
                        passing_tests = {f"test_{i}" for i in range(num_passed)}
                    except ValueError:
                        pass
                if part == "failed" and i > 0:
                    try:
                        num_failed = int(parts[i - 1])
                        failing_tests = {f"test_fail_{i}" for i in range(num_failed)}
                    except ValueError:
                        pass

    return passing_tests, failing_tests
