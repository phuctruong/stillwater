from __future__ import annotations

import json
from pathlib import Path

import pytest

from stillwater.recipe_executor import RecipeExecutionError, RecipeExecutor
from stillwater.recipe_router import MailRouter
from stillwater.recipe_safety import SafetyGate


class _FakeClient:
    def __init__(self, responses: dict[str, dict]) -> None:
        self.responses = responses

    def post_json(self, path: str, payload: dict | None = None) -> dict:
        return json.loads(json.dumps(self.responses.get(path, {"ok": True})))


def _write_recipe(path: Path, payload: dict) -> str:
    p = path / "recipe.json"
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(p)


def test_recipe_executor_rejects_unknown_action(tmp_path: Path) -> None:
    recipe_path = _write_recipe(tmp_path, {"id": "x", "steps": [{"action": "nope"}]})
    ex = RecipeExecutor(recipe_path, client=_FakeClient({}))
    with pytest.raises(RecipeExecutionError) as err:
        ex.execute()
    assert err.value.halt_code == "EXIT_UNKNOWN_ACTION"


def test_router_cpu_and_llm_paths() -> None:
    r = MailRouter(cpu_threshold=0.8)
    assert r.route({"subject": "urgent deploy", "sender": "ops@example.com"}).routed_to == "cpu_archive"

    r2 = MailRouter(cpu_threshold=0.99)
    assert r2.route({"subject": "hello", "sender": "friend@example.com"}).routed_to == "llm_validate"


def test_safety_scope_denied_without_validator(tmp_path: Path) -> None:
    gate = SafetyGate(session_id="s", budget_path=tmp_path / "budget.json", snapshot_dir=tmp_path / "snaps")
    ok, msg = gate.check_scope("tok", "gmail.archive")
    assert not ok
    assert msg == "EXIT_SCOPE_DENIED"


def test_safety_budget_and_snapshot(tmp_path: Path) -> None:
    gate = SafetyGate(session_id="s2", budget_path=tmp_path / "budget.json", snapshot_dir=tmp_path / "snaps")
    ok, _, remaining = gate.check_budget("archive", 2)
    assert ok and remaining == 2
    gate.consume_budget("archive", 2)
    ok2, msg2, remaining2 = gate.check_budget("archive", 2)
    assert not ok2 and msg2 == "EXIT_BUDGET_EXCEEDED" and remaining2 == 0

    snap_ok, snap_msg, snap_hash = gate.snapshot_pre_action({"ids": ["x"]})
    assert snap_ok and snap_msg == "OK" and snap_hash


def test_executor_reads_inbox_recipe_with_fake_snapshot(tmp_path: Path) -> None:
    recipe_path = _write_recipe(
        tmp_path,
        {"id": "read", "steps": [{"name": "extract", "action": "extract", "selector": "[role='row']"}]},
    )
    ex = RecipeExecutor(
        recipe_path,
        client=_FakeClient({"/api/snapshot": {"emails": [{"subject": "Urgent", "sender": "a@example.com"}]}}),
    )
    out = ex.execute()
    assert out["emails_processed"] == 1
    assert out["audit_events"] >= 3

