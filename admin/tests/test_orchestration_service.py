"""Unit tests for admin/services/orchestration_service.py."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"
for _path in (str(REPO_ROOT), str(CLI_SRC)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from admin.services.orchestration_service import OrchestrationService


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"

    # Minimal data/default structure.
    (repo / "data" / "default" / "cpu-nodes").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "default" / "seeds").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "default" / "smalltalk").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "custom").mkdir(parents=True, exist_ok=True)

    # Phase contracts (frontmatter parser in triple_twin expects inline lists).
    (repo / "data" / "default" / "cpu-nodes" / "phase1.md").write_text(
        """---
phase: 1
name: phase1-smalltalk
validator_model: haiku
labels: [greeting, task, question]
learnings_file: learned_phase1.jsonl
---
# phase1
""",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "cpu-nodes" / "phase2.md").write_text(
        """---
phase: 2
name: phase2-intent
validator_model: sonnet
labels: [bugfix, research]
learnings_file: learned_phase2.jsonl
---
# phase2
""",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "cpu-nodes" / "phase3.md").write_text(
        """---
phase: 3
name: phase3-exec
validator_model: sonnet
labels: [bugfix-combo, default-combo]
learnings_file: learned_phase3.jsonl
---
# phase3
""",
        encoding="utf-8",
    )

    phase1_seeds = [
        {"keyword": "hello", "label": "greeting", "count": 30, "examples": [], "phase": "phase1"},
        {"keyword": "fix", "label": "task", "count": 30, "examples": [], "phase": "phase1"},
    ]
    phase2_seeds = [
        {"keyword": "login", "label": "bugfix", "count": 30, "examples": [], "phase": "phase2"},
        {"keyword": "bug", "label": "bugfix", "count": 30, "examples": [], "phase": "phase2"},
    ]
    phase3_seeds = [
        {"keyword": "login", "label": "bugfix-combo", "count": 40, "examples": [], "phase": "phase3"},
        {"keyword": "bug", "label": "bugfix-combo", "count": 40, "examples": [], "phase": "phase3"},
    ]

    (repo / "data" / "default" / "seeds" / "phase1.jsonl").write_text(
        "\n".join(json.dumps(x) for x in phase1_seeds) + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "seeds" / "phase2.jsonl").write_text(
        "\n".join(json.dumps(x) for x in phase2_seeds) + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "seeds" / "phase3.jsonl").write_text(
        "\n".join(json.dumps(x) for x in phase3_seeds) + "\n",
        encoding="utf-8",
    )

    # Smalltalk data required for response_text generation.
    (repo / "data" / "default" / "smalltalk" / "responses.jsonl").write_text(
        json.dumps(
            {
                "id": "resp-001",
                "label": "greeting",
                "response": "Hey there. Nice to see you.",
                "warmth": 3,
                "level": 1,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "smalltalk" / "compliments.jsonl").write_text("", encoding="utf-8")
    (repo / "data" / "default" / "smalltalk" / "reminders.jsonl").write_text("", encoding="utf-8")
    (repo / "data" / "default" / "smalltalk" / "config.jsonl").write_text(
        json.dumps({"key": "cpu_first", "value": True}) + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "smalltalk" / "jokes.json").write_text("[]\n", encoding="utf-8")
    (repo / "data" / "default" / "smalltalk" / "facts.json").write_text("[]\n", encoding="utf-8")

    # Catalog files.
    for dirname, filename in [
        ("swarms", "coder.md"),
        ("combos", "bugfix.md"),
        ("skills", "prime-safety.md"),
        ("recipes", "recipe.bugfix.md"),
    ]:
        (repo / "data" / "default" / dirname).mkdir(parents=True, exist_ok=True)
        (repo / "data" / "default" / dirname / filename).write_text(
            """---
id: demo
name: demo
---
# demo
""",
            encoding="utf-8",
        )

    (repo / "data" / "default" / "personas" / "eq").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "default" / "personas" / "eq" / "bruce.md").write_text(
        """---
id: bruce
---
# Bruce
""",
        encoding="utf-8",
    )

    return repo


@pytest.fixture()
def service_and_client(temp_repo: Path):
    service = OrchestrationService(temp_repo)
    app = service.create_app()
    with TestClient(app) as client:
        yield service, client


# 1) Service lifecycle (3 tests)

def test_service_creates_with_valid_repo_root(temp_repo: Path):
    service = OrchestrationService(temp_repo)
    assert service.repo_root == temp_repo
    assert service.engine is not None


def test_service_registers_with_admin_mock(monkeypatch, temp_repo: Path):
    called = {"value": False}

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _fake_urlopen(req, timeout=2):
        del req, timeout
        called["value"] = True
        return _Resp()

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    service = OrchestrationService(temp_repo)
    app = service.create_app()
    with TestClient(app):
        pass
    assert called["value"] is True


def test_health_endpoint_returns_200(service_and_client):
    _, client = service_and_client
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


# 2) Core orchestration (8 tests)

def test_process_greeting_returns_phase1_greeting_and_response(service_and_client):
    _, client = service_and_client
    res = client.post("/api/orchestrate/process", json={"text": "hello friend"})
    payload = res.json()["result"]
    assert payload["phase1"]["label"] == "greeting"
    assert isinstance(payload["response_text"], str) and payload["response_text"]


def test_process_task_runs_all_three_phases(service_and_client):
    _, client = service_and_client
    res = client.post("/api/orchestrate/process", json={"text": "fix login bug"})
    payload = res.json()["result"]
    assert payload["phase1"]["label"] == "task"
    assert payload["phase2"]["label"] == "bugfix"
    assert payload["phase3"]["label"] == "bugfix-combo"


def test_process_empty_string_returns_result_object(service_and_client):
    _, client = service_and_client
    res = client.post("/api/orchestrate/process", json={"text": ""})
    assert res.status_code == 200
    payload = res.json()["result"]
    assert "phase1" in payload


def test_phase1_only_returns_phase1(service_and_client):
    _, client = service_and_client
    res = client.post("/api/orchestrate/phase1", json={"text": "hello"})
    payload = res.json()
    assert payload["phase1"]["label"] == "greeting"


def test_phase2_with_context_returns_phase2(service_and_client):
    _, client = service_and_client
    res = client.post(
        "/api/orchestrate/phase2",
        json={"text": "fix login bug", "context": {"phase1_label": "task"}},
    )
    payload = res.json()
    assert payload["phase2"]["label"] == "bugfix"


def test_phase3_with_context_returns_phase3(service_and_client):
    _, client = service_and_client
    res = client.post(
        "/api/orchestrate/phase3",
        json={"text": "fix login bug", "context": {"phase2_label": "bugfix"}},
    )
    payload = res.json()
    assert payload["phase3"]["label"] == "bugfix-combo"


def test_stats_endpoint_returns_expected_counters(service_and_client):
    _, client = service_and_client
    client.post("/api/orchestrate/process", json={"text": "fix login bug"})
    client.post("/api/orchestrate/process", json={"text": "hello"})
    res = client.get("/api/orchestrate/stats")
    stats = res.json()["stats"]
    assert stats["total_processed"] >= 2
    assert "cpu_hits" in stats
    assert "cpu_hit_rate" in stats


def test_phases_endpoint_lists_three_phases(service_and_client):
    _, client = service_and_client
    res = client.get("/api/orchestrate/phases")
    phases = res.json()["phases"]
    names = {p["phase"] for p in phases}
    assert names == {"phase1", "phase2", "phase3"}


# 3) Customization (6 tests)

def test_get_phase_seeds_returns_seed_list(service_and_client):
    _, client = service_and_client
    res = client.get("/api/phases/1/seeds")
    payload = res.json()
    assert payload["phase"] == "phase1"
    assert len(payload["seeds"]) >= 1


def test_post_phase_seeds_writes_custom_overlay_file(service_and_client):
    service, client = service_and_client
    res = client.post(
        "/api/phases/1/seeds",
        json={"seeds": [{"keyword": "yo", "label": "greeting", "count": 35}]},
    )
    assert res.status_code == 200
    custom_file = service.repo_root / "data" / "custom" / "seeds" / "phase1_custom.jsonl"
    assert custom_file.exists()


def test_post_phase_seed_affects_next_process_call(service_and_client):
    _, client = service_and_client
    client.post(
        "/api/phases/1/seeds",
        json={"seeds": [{"keyword": "sup", "label": "greeting", "count": 35}]},
    )
    res = client.post("/api/orchestrate/process", json={"text": "sup there"})
    assert res.json()["result"]["phase1"]["label"] == "greeting"


def test_get_phase_config_returns_threshold_and_labels(service_and_client):
    _, client = service_and_client
    res = client.get("/api/phases/1/config")
    config = res.json()["config"]
    assert "labels" in config


def test_put_phase_config_updates_threshold_in_custom_overlay(service_and_client):
    service, client = service_and_client
    res = client.put("/api/phases/1/config", json={"threshold": 0.95})
    assert res.status_code == 200
    custom_cfg = service.repo_root / "data" / "custom" / "cpu-nodes" / "phase1.md"
    assert custom_cfg.exists()
    assert "threshold: 0.95" in custom_cfg.read_text(encoding="utf-8")


def test_customization_never_modifies_data_default_files(service_and_client):
    service, client = service_and_client
    default_cfg = service.repo_root / "data" / "default" / "cpu-nodes" / "phase1.md"
    before = hashlib.sha256(default_cfg.read_bytes()).hexdigest()

    client.put("/api/phases/1/config", json={"threshold": 0.91})
    client.post(
        "/api/phases/1/seeds",
        json={"seeds": [{"keyword": "hiya", "label": "greeting", "count": 20}]},
    )

    after = hashlib.sha256(default_cfg.read_bytes()).hexdigest()
    assert before == after


# 4) Catalog endpoints (5 tests)

def test_catalog_swarms_returns_frontmatter_items(service_and_client):
    _, client = service_and_client
    res = client.get("/api/swarms")
    swarms = res.json()["swarms"]
    assert len(swarms) >= 1
    assert "frontmatter" in swarms[0]


def test_catalog_combos_returns_items(service_and_client):
    _, client = service_and_client
    res = client.get("/api/combos")
    assert len(res.json()["combos"]) >= 1


def test_catalog_skills_returns_items(service_and_client):
    _, client = service_and_client
    res = client.get("/api/skills")
    assert len(res.json()["skills"]) >= 1


def test_catalog_recipes_returns_items(service_and_client):
    _, client = service_and_client
    res = client.get("/api/recipes")
    assert len(res.json()["recipes"]) >= 1


def test_catalog_personas_supports_nested_directories(service_and_client):
    _, client = service_and_client
    res = client.get("/api/personas")
    assert len(res.json()["personas"]) >= 1


# 5) Evidence integration (3 tests)

def test_process_produces_audit_log_entry(service_and_client):
    service, client = service_and_client
    client.post("/api/orchestrate/process", json={"text": "fix login bug"})
    entries = service.audit_logger.read_all_log_files()
    assert len(entries) >= 1


def test_audit_entry_contains_label_and_session_id(service_and_client):
    service, client = service_and_client
    client.post("/api/orchestrate/process", json={"text": "fix login bug"})
    entry = service.audit_logger.read_all_log_files()[-1]
    assert entry["metadata"].get("prediction_label") in {"task", "bugfix", "bugfix-combo", "greeting"}
    assert isinstance(entry["actor"].get("session_id"), str)


def test_hash_chain_intact_after_ten_process_calls(service_and_client):
    service, client = service_and_client
    for i in range(10):
        client.post("/api/orchestrate/process", json={"text": f"fix login bug {i}"})

    log_files = sorted((service.repo_root / "data" / "logs").glob("audit-*.jsonl"))
    assert log_files, "expected at least one audit file"
    assert service.audit_logger.verify_chain(log_files[-1]) is True
