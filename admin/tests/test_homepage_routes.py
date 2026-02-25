from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from backend.homepage_routes import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_list_endpoints_return_payloads() -> None:
    endpoints = [
        "/api/skills/list",
        "/api/recipes/list",
        "/api/swarms/list",
        "/api/personas/list",
    ]
    with _client() as client:
        for endpoint in endpoints:
            res = client.get(endpoint)
            assert res.status_code == 200
            payload = res.json()
            assert "count" in payload
            assert "skills" in payload
            assert payload["count"] == len(payload["skills"])


def test_stubbed_demo_endpoints_return_501() -> None:
    endpoints = [
        "/api/skills/demo",
        "/api/recipes/demo",
    ]
    with _client() as client:
        for endpoint in endpoints:
            res = client.get(endpoint)
            assert res.status_code == 501
            detail = res.json()["detail"]
            assert detail["error"] == "not implemented"
            assert "endpoint" in detail


def test_mermaid_endpoints_return_graph_payload() -> None:
    endpoints = [
        "/api/mermaid/orchestration",
        "/api/mermaid/skills",
        "/api/mermaid/recipes",
        "/api/mermaid/swarms",
        "/api/mermaid/personas",
    ]

    with _client() as client:
        for endpoint in endpoints:
            res = client.get(endpoint)
            assert res.status_code == 200
            payload = res.json()
            assert "graph_syntax" in payload
            assert payload["graph_syntax"]
            assert "generated_at" in payload
