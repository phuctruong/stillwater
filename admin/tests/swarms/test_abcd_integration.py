#!/usr/bin/env python3
"""
ABCD Integration Test — Admin Server CLI Endpoint Evaluation

Demonstrates the ABCDHarness running a real evaluation against a live
admin server. Starts a ThreadingHTTPServer on a free port, evaluates
three CLI command variants (version, doctor, llm-status) across three
tasks, and writes JSON + Markdown reports.

Run with:
    pytest admin/tests/swarms/test_abcd_integration.py -v

rung_target: 641
"""

from __future__ import annotations

import http.client
import json
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup — same pattern as test_admin_server.py
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
ADMIN_DIR = REPO_ROOT / "admin"
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"
SWARMS_DIR = ADMIN_DIR / "tests" / "swarms"

for _p in (str(ADMIN_DIR), str(CLI_SRC), str(SWARMS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from http.server import ThreadingHTTPServer

import server as admin_server
from abcd_harness import ABCDHarness, Task, Variant


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _free_port() -> int:
    """Return an available TCP port on 127.0.0.1."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Module-scoped server fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def server_port():
    """Start the admin server on a free port; yield the port number.

    The server is shut down after all tests in this module complete.
    """
    port = _free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), admin_server.AdminHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)  # Let the server accept connections

    yield port

    httpd.shutdown()
    httpd.server_close()


# ---------------------------------------------------------------------------
# Variant + Task definitions
# ---------------------------------------------------------------------------

def _make_variants(port: int) -> list[Variant]:
    """Return 3 variants — each runs a different CLI command via /api/cli/run."""
    base_url = f"http://127.0.0.1:{port}/api/cli/run"
    return [
        Variant(
            id="A",
            name="version-command",
            config={"command": "version", "endpoint": base_url},
        ),
        Variant(
            id="B",
            name="doctor-command",
            config={"command": "doctor", "endpoint": base_url},
        ),
        Variant(
            id="C",
            name="llm-status-command",
            config={"command": "llm-status", "endpoint": base_url},
        ),
    ]


def _make_tasks() -> list[Task]:
    """Return 3 tasks that exercise the CLI commands."""
    return [
        Task(
            id="t1",
            prompt="Check system health",
            tags=["health"],
        ),
        Task(
            id="t2",
            prompt="Verify installation",
            tags=["installation"],
        ),
        Task(
            id="t3",
            prompt="List capabilities",
            tags=["capabilities"],
        ),
    ]


# ---------------------------------------------------------------------------
# run_variant_fn
# ---------------------------------------------------------------------------

def _make_run_variant_fn():
    """
    Return a run_variant_fn that:
      - Takes (variant_config, task)
      - Makes HTTP POST to /api/cli/run with the variant's command
      - Returns {output: str, tokens: int, cost_usd: float}

    The output is the JSON-serialised full server response so the scorer
    can inspect ok=True/False and the presence of stdout.
    """
    import urllib.request
    import urllib.error

    def run_variant(config: dict, task: Task) -> dict:
        endpoint = config["endpoint"]
        command = config["command"]
        body = json.dumps({"command": command}).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # Serialise the full response as output so the scorer can parse it
                return {
                    "output": json.dumps(data),
                    "tokens": 0,
                    "cost_usd": 0.0,
                }
        except urllib.error.URLError as exc:
            raise RuntimeError(f"CLI endpoint unreachable: {exc}") from exc

    return run_variant


# ---------------------------------------------------------------------------
# scorer_fn
# ---------------------------------------------------------------------------

def _scorer_fn(output: str, task: Task, config: dict) -> float:
    """
    Score a single CLI command response.

    Scoring rules:
      1.0  — ok=True  AND non-empty stdout (command ran and produced output)
      0.5  — ok=True  BUT stdout is empty (command ran but produced no output)
      0.0  — ok=False (command failed or was rejected)
      0.0  — output is not parseable JSON (unexpected error)
    """
    try:
        data = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        return 0.0

    outer_ok = data.get("ok", False)
    if not outer_ok:
        return 0.0

    result = data.get("result", {})
    stdout = result.get("stdout", "") or ""
    stderr = result.get("stderr", "") or ""

    # Non-empty stdout means the command produced real output
    if stdout.strip():
        return 1.0
    # ok=True but no stdout (some commands might write only to stderr)
    return 0.5


# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------

class TestABCDIntegration:
    """Integration test: ABCD harness against a live admin server."""

    def test_abcd_integration_runs_and_produces_report(self, server_port, tmp_path):
        """
        Full ABCD integration test:
          1. Start real server (via fixture)
          2. Register 3 variants and 3 tasks
          3. Run harness with repeats=3
          4. Save report to admin/tests/swarms/
          5. Assert report structure is valid
        """
        # --- Build harness ---
        harness = ABCDHarness(
            run_variant_fn=_make_run_variant_fn(),
            scorer_fn=_scorer_fn,
            seed=641,
        )

        for variant in _make_variants(server_port):
            harness.add_variant(variant)

        for task in _make_tasks():
            harness.add_task(task)

        # --- Run with repeats=3 ---
        results = harness.run(repeats=3)

        # Sanity: 3 variants x 3 tasks x 3 repeats = 27 results
        assert len(results) == 27, (
            f"Expected 27 results, got {len(results)}"
        )

        # All results should succeed (no errors from the HTTP call itself)
        errors = [r for r in results if r.error is not None]
        # Errors are allowed (command may not be installed), but record them
        # We only require that the harness completes the full matrix
        # (individual CLI commands may fail if stillwater is not installed)

        # --- Generate report ---
        report = harness.report()

        # --- Verify report structure ---
        assert "variants" in report
        assert "tasks" in report
        assert "summary" in report
        assert "pairwise" in report
        assert "bonferroni" in report
        assert "winner" in report
        assert "raw_results" in report

        assert len(report["variants"]) == 3
        assert len(report["tasks"]) == 3
        assert len(report["raw_results"]) == 27

        # Summary has entries for each variant
        for vid in ("A", "B", "C"):
            assert vid in report["summary"]
            s = report["summary"][vid]
            assert "n_total" in s
            assert "n_success" in s
            assert "success_rate" in s
            assert "mean_latency_ms" in s
            assert s["n_total"] == 9  # 3 tasks x 3 repeats

        # Pairwise section has all 3 pairs
        assert "A_vs_B" in report["pairwise"]
        assert "A_vs_C" in report["pairwise"]
        assert "B_vs_C" in report["pairwise"]

        # Bonferroni section is present
        bonf = report["bonferroni"]
        assert "pairs" in bonf
        assert "num_tests" in bonf
        assert bonf["num_tests"] == 3

        # --- Save reports ---
        report_json_path = SWARMS_DIR / "abcd_demo_report.json"
        harness.save_report(str(report_json_path))

        # Verify JSON file was written
        assert report_json_path.exists(), f"Report JSON not found at {report_json_path}"
        with report_json_path.open("r", encoding="utf-8") as fh:
            saved = json.load(fh)

        # Verify saved JSON has expected top-level keys
        for key in ("variants", "tasks", "summary", "pairwise", "bonferroni", "winner", "raw_results"):
            assert key in saved, f"Missing key in saved report: {key!r}"

        # Verify markdown file was written alongside
        report_md_path = report_json_path.with_suffix(".md")
        assert report_md_path.exists(), f"Report markdown not found at {report_md_path}"
        md_content = report_md_path.read_text(encoding="utf-8")
        assert "ABCD Test Report" in md_content
        assert "Summary" in md_content

    def test_abcd_scorer_logic(self):
        """Unit test the scorer_fn in isolation."""
        from abcd_harness import Task as HarnessTask

        dummy_task = HarnessTask(id="t1", prompt="test")
        dummy_config = {"command": "version"}

        # ok=True + non-empty stdout → 1.0
        response = json.dumps({"ok": True, "result": {"stdout": "stillwater 1.2.3", "stderr": ""}})
        assert _scorer_fn(response, dummy_task, dummy_config) == 1.0

        # ok=True + empty stdout → 0.5
        response_empty = json.dumps({"ok": True, "result": {"stdout": "", "stderr": ""}})
        assert _scorer_fn(response_empty, dummy_task, dummy_config) == 0.5

        # ok=False → 0.0
        response_fail = json.dumps({"ok": False, "result": {}})
        assert _scorer_fn(response_fail, dummy_task, dummy_config) == 0.0

        # Non-JSON output → 0.0
        assert _scorer_fn("not json at all", dummy_task, dummy_config) == 0.0

        # ok=True + stderr-only output (no stdout) → 0.5
        response_stderr = json.dumps({"ok": True, "result": {"stdout": "", "stderr": "some warning"}})
        assert _scorer_fn(response_stderr, dummy_task, dummy_config) == 0.5

    def test_abcd_report_is_valid_json_on_disk(self, server_port):
        """Verify the report file written by the integration test is valid JSON."""
        report_json_path = SWARMS_DIR / "abcd_demo_report.json"
        if not report_json_path.exists():
            pytest.skip("Report not yet generated — run test_abcd_integration_runs_and_produces_report first")

        with report_json_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        # Top-level structure
        assert isinstance(data, dict)
        assert isinstance(data.get("variants"), list)
        assert isinstance(data.get("tasks"), list)
        assert isinstance(data.get("summary"), dict)
        assert isinstance(data.get("pairwise"), dict)
        assert isinstance(data.get("raw_results"), list)

        # Each raw result has expected fields
        for raw in data["raw_results"]:
            assert "variant_id" in raw
            assert "task_id" in raw
            assert "repeat_index" in raw
            assert "output" in raw
            assert "latency_ms" in raw
            assert "quality_score" in raw

    def test_abcd_variant_ids_in_report(self, server_port):
        """Verify all three variant IDs appear in the saved report."""
        report_json_path = SWARMS_DIR / "abcd_demo_report.json"
        if not report_json_path.exists():
            pytest.skip("Report not yet generated")

        with report_json_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        variant_ids = {v["id"] for v in data["variants"]}
        assert "A" in variant_ids
        assert "B" in variant_ids
        assert "C" in variant_ids

        # Check summary keys too
        assert "A" in data["summary"]
        assert "B" in data["summary"]
        assert "C" in data["summary"]
