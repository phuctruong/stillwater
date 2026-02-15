"""
Tests for SWE-bench harness.

Tests the Red-Green-God verification gates and infrastructure.
"""

import pytest
from pathlib import Path
from stillwater.swe.loader import SWEInstance, _parse_instance
from stillwater.swe.gates import RedGate, GreenGate, GodGate, TestResult, GateStatus
from stillwater.swe.certificate import generate_certificate


class TestLoader:
    """Test SWE-bench dataset loading."""

    def test_parse_instance(self):
        """Test parsing raw data into SWEInstance."""
        data = {
            "instance_id": "django__django-12345",
            "problem_statement": "Fix the bug",
            "repo": "django/django",
            "base_commit": "abc123",
            "test_patch": "diff --git a/test.py",
            "patch": "diff --git a/fix.py",
        }

        instance = _parse_instance(data)

        assert instance.instance_id == "django__django-12345"
        assert instance.problem_statement == "Fix the bug"
        assert instance.repo == "django/django"
        assert instance.base_commit == "abc123"
        assert instance.test_patch == "diff --git a/test.py"
        assert instance.gold_patch == "diff --git a/fix.py"

    def test_parse_instance_minimal(self):
        """Test parsing with only required fields."""
        data = {
            "instance_id": "test-1",
            "problem_statement": "",
            "repo": "",
            "base_commit": "",
            "test_patch": "",
        }

        instance = _parse_instance(data)

        assert instance.instance_id == "test-1"
        assert instance.gold_patch is None


class TestGates:
    """Test Red-Green-God verification gates."""

    def test_test_result_all_passed(self):
        """Test TestResult.all_passed property."""
        result = TestResult(
            passing_tests={"test_1", "test_2"},
            failing_tests=set(),
            total_tests=2,
            exit_code=0,
            stdout="",
            stderr="",
            duration_ms=100,
        )

        assert result.all_passed is True
        assert result.pass_rate == 1.0

    def test_test_result_some_failed(self):
        """Test TestResult with failures."""
        result = TestResult(
            passing_tests={"test_1"},
            failing_tests={"test_2", "test_3"},
            total_tests=3,
            exit_code=1,
            stdout="",
            stderr="",
            duration_ms=100,
        )

        assert result.all_passed is False
        assert result.pass_rate == pytest.approx(0.333, 0.01)

    def test_green_gate_no_regressions(self):
        """Test Green Gate passes when no regressions."""
        baseline = TestResult(
            passing_tests={"test_1", "test_2"},
            failing_tests={"test_3"},
            total_tests=3,
            exit_code=1,
            stdout="",
            stderr="",
            duration_ms=100,
        )

        after_patch = TestResult(
            passing_tests={"test_1", "test_2", "test_3"},  # test_3 now passes
            failing_tests=set(),
            total_tests=3,
            exit_code=0,
            stdout="",
            stderr="",
            duration_ms=100,
        )

        # Mock Green Gate check (without actual subprocess)
        regressions = baseline.passing_tests - after_patch.passing_tests
        new_fixes = after_patch.passing_tests - baseline.passing_tests

        assert len(regressions) == 0
        assert new_fixes == {"test_3"}

    def test_green_gate_with_regressions(self):
        """Test Green Gate fails when regressions detected."""
        baseline = TestResult(
            passing_tests={"test_1", "test_2"},
            failing_tests={"test_3"},
            total_tests=3,
            exit_code=1,
            stdout="",
            stderr="",
            duration_ms=100,
        )

        after_patch = TestResult(
            passing_tests={"test_1"},  # test_2 now fails!
            failing_tests={"test_2", "test_3"},
            total_tests=3,
            exit_code=1,
            stdout="",
            stderr="",
            duration_ms=100,
        )

        regressions = baseline.passing_tests - after_patch.passing_tests

        assert regressions == {"test_2"}

    def test_god_gate_deterministic(self):
        """Test God Gate passes for identical patches."""
        patch = "diff --git a/file.py\n+print('hello')"
        patches = [patch, patch, patch]

        result = GodGate.check(patches)

        assert result.status == GateStatus.PASS
        assert "Deterministic" in result.message

    def test_god_gate_non_deterministic(self):
        """Test God Gate fails for different patches."""
        patches = [
            "diff --git a/file.py\n+print('hello')",
            "diff --git a/file.py\n+print('world')",
            "diff --git a/file.py\n+print('hello')",
        ]

        result = GodGate.check(patches)

        assert result.status == GateStatus.FAIL
        assert "Non-deterministic" in result.message

    def test_god_gate_insufficient_patches(self):
        """Test God Gate errors with < 2 patches."""
        result = GodGate.check(["single patch"])

        assert result.status == GateStatus.ERROR


class TestCertificate:
    """Test proof certificate generation."""

    def test_generate_certificate_verified(self):
        """Test certificate generation for verified patch."""
        cert = generate_certificate(
            instance_id="test-1",
            patch="diff --git a/fix.py",
            baseline_tests={"test_1", "test_2"},
            after_patch_tests={"test_1", "test_2", "test_3"},
            deterministic=True,
        )

        assert cert["instance_id"] == "test-1"
        assert cert["status"] == "VERIFIED"
        assert cert["baseline_passing"] == ["test_1", "test_2"]
        assert cert["after_patch_passing"] == ["test_1", "test_2", "test_3"]
        assert cert["regressions"] == []
        assert cert["new_fixes"] == ["test_3"]
        assert cert["determinism_verified"] is True
        assert cert["patch_hash"].startswith("sha256:")

    def test_generate_certificate_with_regressions(self):
        """Test certificate shows REJECTED when regressions exist."""
        cert = generate_certificate(
            instance_id="test-2",
            patch="diff --git a/bad.py",
            baseline_tests={"test_1", "test_2"},
            after_patch_tests={"test_1"},  # test_2 regressed!
            deterministic=False,
        )

        assert cert["status"] == "REJECTED"
        assert cert["regressions"] == ["test_2"]
        assert cert["new_fixes"] == []

    def test_certificate_hash_changes_with_patch(self):
        """Test patch hash is unique per patch."""
        cert1 = generate_certificate(
            "test", "patch1", set(), set()
        )
        cert2 = generate_certificate(
            "test", "patch2", set(), set()
        )

        assert cert1["patch_hash"] != cert2["patch_hash"]


class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_swe_instance_dataclass(self):
        """Test SWEInstance dataclass creation."""
        instance = SWEInstance(
            instance_id="test-1",
            problem_statement="Fix bug",
            repo="test/repo",
            base_commit="abc",
            test_patch="",
        )

        assert str(instance) == "SWEInstance(test-1)"

    def test_gate_result_bool_conversion(self):
        """Test GateResult can be used as boolean."""
        from stillwater.swe.gates import GateResult, GateStatus

        pass_result = GateResult(
            status=GateStatus.PASS,
            message="OK"
        )
        fail_result = GateResult(
            status=GateStatus.FAIL,
            message="Failed"
        )

        assert bool(pass_result) is True
        assert bool(fail_result) is False
