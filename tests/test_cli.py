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


# TC6 — Bench subcommand help works
def test_bench_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "bench", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "bench" in result.stdout.lower()


# TC7 — Bench unknown benchmark name exits 1
def test_bench_unknown_benchmark() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "bench", "nonexistent"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Unknown benchmark" in result.stdout


# TC8 — Help mentions bench subcommand
def test_help_mentions_bench() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "bench" in result.stdout.lower()


# TC9 — Connect subcommand help works
def test_connect_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "connect", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "connect" in result.stdout.lower()


# TC10 — Chat subcommand help works
def test_chat_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "chat", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "chat" in result.stdout.lower()


# TC11 — Help mentions connect and chat subcommands
def test_help_mentions_connect_and_chat() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "stillwater.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "connect" in result.stdout.lower()
    assert "chat" in result.stdout.lower()
