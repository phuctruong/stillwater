"""Tests for the CLI entry point (cli.py)."""

from __future__ import annotations

import subprocess
import sys

import pytest


# TC1 — CLI help works
def test_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "stillwater" in result.stdout.lower()


# TC2 — Verify subcommand help works
def test_verify_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "verify", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "verify" in result.stdout.lower()
    assert "verification ladder" in result.stdout.lower()


# TC3 — Verify subcommand runs and passes
def test_verify_runs(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
    workdir = str(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "verify"],
        capture_output=True,
        text=True,
        cwd=workdir,
    )
    assert result.returncode == 0
    assert "PASSED" in result.stdout


# TC4 — Entry point defined in pyproject.toml
def test_entry_point_defined() -> None:
    import importlib.metadata

    eps = importlib.metadata.entry_points()
    # Filter for console_scripts group
    if hasattr(eps, "select"):
        # Python 3.12+
        console_scripts = eps.select(group="console_scripts")
    else:
        # Python 3.10-3.11
        console_scripts = eps.get("console_scripts", [])

    found = False
    for ep in console_scripts:
        if ep.name == "stillwater":
            assert ep.value == "stillwater.cli:main"
            found = True
            break
    assert found, "stillwater entry point not found in console_scripts"


# TC5 — No subcommand prints help
def test_no_subcommand_prints_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "stillwater" in result.stdout.lower()
