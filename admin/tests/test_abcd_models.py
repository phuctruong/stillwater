from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = REPO_ROOT / "scratch" / "abcd-results.jsonl"
SUMMARY_PATH = REPO_ROOT / "scratch" / "abcd-summary.json"

MODELS: dict[str, dict[str, object]] = {
    "A_haiku": {
        "cmd": ["claude", "--print", "--model", "haiku"],
        "name": "haiku",
        "cost_class": "low",
    },
    "B_sonnet": {
        "cmd": ["claude", "--print", "--model", "sonnet"],
        "name": "sonnet",
        "cost_class": "medium",
    },
    "C_opus": {
        "cmd": ["claude", "--print", "--model", "opus"],
        "name": "opus",
        "cost_class": "high",
    },
}

if os.getenv("ABCD_INCLUDE_GEMINI", "").strip().lower() in {"1", "true", "yes", "on"}:
    MODELS["D_gemini"] = {
        "cmd": ["gemini", "-m", "gemini-3-flash-preview", "-p"],
        "name": "gemini-3-flash-preview",
        "cost_class": "low",
    }

SWARM_PROMPTS: dict[str, str] = {
    "coder": "Fix this Python function that has an off-by-one error: def sum_range(n): total=0; for i in range(n): total+=i; return total",
    "planner": "Design the architecture for a microservice that handles OAuth3 tokens with grant, revoke, and scope verification",
    "skeptic": "Review this code for bugs: def divide(a,b): return a/b",
    "scout": "What are the main components of a typical FastAPI web application?",
    "mathematician": "Prove that the square root of 2 is irrational. Be rigorous.",
    "graph-designer": "Create a Mermaid flowchart showing user authentication flow with OAuth3",
    "security-auditor": "What are the top 3 security risks of storing API keys in environment variables?",
    "portal-engineer": "Write a Python function that calls an LLM API with retry logic and timeout",
    "janitor": "Simplify this: x = []; for i in range(10): if i % 2 == 0: x.append(i*i)",
    "content-writer": "Write a 3-sentence summary of why deterministic AI verification matters",
}


def _approx_quality_score(output: str) -> int:
    text = output.strip().lower()
    if not text:
        return 1
    if any(marker in text for marker in ("i can't", "i cannot", "unable", "sorry")):
        return 2
    words = len(text.split())
    if words < 25:
        return 2
    if words < 60:
        return 3
    if words < 140:
        return 4
    return 5


def _append_result(row: dict[str, object]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _run_model(model_key: str, swarm_type: str) -> dict[str, object]:
    model = MODELS[model_key]
    cmd = list(model["cmd"]) + [SWARM_PROMPTS[swarm_type]]

    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        latency_ms = int((time.time() - started) * 1000)
        output = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        ok = proc.returncode == 0 and bool(output)
        error = None if ok else (err or f"exit {proc.returncode}")
    except subprocess.TimeoutExpired:
        latency_ms = int((time.time() - started) * 1000)
        output = ""
        ok = False
        error = "timeout"
    except Exception as exc:  # pragma: no cover
        latency_ms = int((time.time() - started) * 1000)
        output = ""
        ok = False
        error = str(exc)

    row: dict[str, object] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model_key": model_key,
        "model": model["name"],
        "swarm_type": swarm_type,
        "prompt": SWARM_PROMPTS[swarm_type],
        "latency_ms": latency_ms,
        "output_length": len(output),
        "quality_score": _approx_quality_score(output),
        "cost_estimate": model["cost_class"],
        "ok": ok,
        "error": error,
    }
    _append_result(row)
    return row


@pytest.mark.real_llm
@pytest.mark.parametrize("model_key", list(MODELS.keys()))
@pytest.mark.parametrize("swarm_type", list(SWARM_PROMPTS.keys()))
def test_abcd(model_key: str, swarm_type: str) -> None:
    row = _run_model(model_key, swarm_type)
    if os.getenv("ABCD_STRICT", "").strip().lower() in {"1", "true", "yes", "on"}:
        assert row["ok"] is True, f"{model_key} failed on {swarm_type}: {row['error']}"


@pytest.mark.real_llm
def test_generate_abcd_summary() -> None:
    if not RESULTS_PATH.exists():
        pytest.skip("no results file yet")

    rows = [
        json.loads(line)
        for line in RESULTS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        pytest.skip("results file is empty")

    target_models = {str(v["name"]) for v in MODELS.values()}
    rows = [r for r in rows if str(r.get("model")) in target_models]

    by_swarm: dict[str, list[dict[str, object]]] = {}
    by_model: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_swarm.setdefault(str(row["swarm_type"]), []).append(row)
        by_model.setdefault(str(row["model"]), []).append(row)

    def _avg(items: list[dict[str, object]], key: str) -> float:
        values = [float(i.get(key, 0)) for i in items if i.get(key) is not None]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    model_metrics: dict[str, dict[str, object]] = {}
    for model, items in by_model.items():
        ok_count = sum(1 for i in items if i.get("ok") is True)
        model_metrics[model] = {
            "count": len(items),
            "ok_count": ok_count,
            "ok_rate": round(ok_count / len(items), 4) if items else 0.0,
            "avg_latency_ms": _avg(items, "latency_ms"),
            "avg_output_length": _avg(items, "output_length"),
            "avg_quality_score": _avg(items, "quality_score"),
        }

    swarm_best_model: dict[str, str] = {}
    for swarm, items in by_swarm.items():
        ok_items = [i for i in items if i.get("ok") is True]
        if not ok_items:
            swarm_best_model[swarm] = "none"
            continue
        ranked = sorted(
            ok_items,
            key=lambda x: (
                -float(x.get("quality_score", 0)),
                float(x.get("latency_ms", 10**9)),
                -float(x.get("output_length", 0)),
            ),
        )
        swarm_best_model[swarm] = str(ranked[0]["model"])

    summary = {
        "models_tested": sorted(target_models),
        "rows": len(rows),
        "ok_rows": sum(1 for row in rows if row.get("ok") is True),
        "failed_rows": sum(1 for row in rows if row.get("ok") is not True),
        "by_model": model_metrics,
        "best_model_by_swarm": swarm_best_model,
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    assert summary["rows"] >= len(target_models)
