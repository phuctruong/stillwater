from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import llm_portal_v3


def test_recipe_execute_returns_not_implemented(monkeypatch) -> None:
    monkeypatch.setattr(
        llm_portal_v3.recipe_executor,
        "execute",
        lambda recipe_name, task, context: llm_portal_v3.RecipeResponse(
            success=False,
            result={"status": "not_implemented", "error": "recipe execution not yet implemented"},
            error="recipe execution not yet implemented",
            recipe=recipe_name,
            timestamp=datetime.now().isoformat(),
        ),
    )

    with TestClient(llm_portal_v3.app) as client:
        res = client.post(
            "/v1/recipe/execute",
            json={"recipe_name": "demo", "task": "do thing", "context": {}},
        )

    assert res.status_code == 501
