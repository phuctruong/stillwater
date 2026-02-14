"""Tests for the verification ladder (harness/verify.py)."""

from __future__ import annotations

import json
import os
import tempfile
from unittest import mock

import pytest

from stillwater.harness.verify import (
    VerifyResult,
    build_certificate,
    run_274177_stress_tests,
    run_641_edge_tests,
    run_65537_god_test,
    run_oauth_checks,
    run_verification,
)


# T1 — Verify passes: run_verification returns True, stdout has "PASSED", cert created
def test_verify_passes(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
    workdir = str(tmp_path)
    monkeypatch.chdir(workdir)
    passed, cert = run_verification(verbose=False)
    assert passed is True
    assert cert["status"] == "PASSED"


# T2 — Certificate structure: JSON with required keys
def test_certificate_structure() -> None:
    oauth = run_oauth_checks()
    edge = run_641_edge_tests()
    stress = run_274177_stress_tests()
    god = run_65537_god_test(oauth, edge, stress)
    cert = build_certificate(oauth, edge, stress, god)

    required_keys = {"auth", "oauth", "edge_641", "stress_274177", "god_65537", "status", "hash"}
    assert set(cert.keys()) == required_keys
    assert cert["auth"] == 65537
    assert cert["status"] == "PASSED"
    assert isinstance(cert["hash"], str)
    assert len(cert["hash"]) == 64  # SHA-256 hex


# T3 — Determinism: run twice -> byte-identical certs (SHA256 match)
def test_determinism() -> None:
    _, cert1 = run_verification(verbose=False)
    _, cert2 = run_verification(verbose=False)
    assert cert1["hash"] == cert2["hash"]
    # Full structural equality
    assert json.dumps(cert1, sort_keys=True) == json.dumps(cert2, sort_keys=True)


# T4 — Progress output: stdout has "OAuth(39,63,91)", "641", "274177", "65537" in order
def test_progress_output(capsys: pytest.CaptureFixture[str]) -> None:
    run_verification(verbose=False)
    output = capsys.readouterr().out
    # Check all four rungs appear
    assert "OAuth(39,63,91)" in output
    assert "641" in output
    assert "274177" in output
    assert "65537" in output
    # Check order: OAuth before 641 before 274177 before 65537
    i_oauth = output.index("OAuth(39,63,91)")
    i_641 = output.index("641 ...")
    i_274177 = output.index("274177 ...")
    i_65537 = output.index("65537 ...")
    assert i_oauth < i_641 < i_274177 < i_65537


# T5 — OAuth includes 3 checks: verbose shows CARE, BRIDGE, STABILITY
def test_oauth_verbose(capsys: pytest.CaptureFixture[str]) -> None:
    run_verification(verbose=True)
    output = capsys.readouterr().out
    assert "CARE" in output
    assert "BRIDGE" in output
    assert "STABILITY" in output


# T6 — 641 edge tests minimum 5: verbose shows required names
def test_641_edge_minimum_five(capsys: pytest.CaptureFixture[str]) -> None:
    run_verification(verbose=True)
    output = capsys.readouterr().out
    assert "641_lane_algebra" in output
    assert "641_state_machine" in output
    assert "641_counter_bypass" in output
    assert "641_rtc" in output
    assert "641_type_guards" in output


# T7 — Exit code 1 on failure: mock a failing test, verify result is False
def test_failure_mode() -> None:
    oauth = [VerifyResult("OAuth(39)_CARE", False, "forced failure")]
    edge = run_641_edge_tests()
    stress = run_274177_stress_tests()
    god = run_65537_god_test(oauth, edge, stress)
    assert god.passed is False
    cert = build_certificate(oauth, edge, stress, god)
    assert cert["status"] == "FAILED"


# T8 — OAuth has exactly 3 checks
def test_oauth_has_three_checks() -> None:
    results = run_oauth_checks()
    assert len(results) == 3
    assert all(r.passed for r in results)


# T9 — 641 has at least 5 checks
def test_641_has_five_checks() -> None:
    results = run_641_edge_tests()
    assert len(results) >= 5
    assert all(r.passed for r in results)


# T10 — No network: mock socket.socket to raise, verify still passes
def test_no_network() -> None:
    import socket

    original_socket = socket.socket

    def blocked_socket(*args, **kwargs):
        raise OSError("Network blocked for testing")

    with mock.patch.object(socket, "socket", blocked_socket):
        passed, cert = run_verification(verbose=False)
    assert passed is True
    assert cert["status"] == "PASSED"
