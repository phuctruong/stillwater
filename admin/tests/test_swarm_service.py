from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"
for _path in (str(REPO_ROOT), str(ADMIN_DIR), str(CLI_SRC)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from services.swarm_service import _FrontmatterParser, SwarmService


def test_frontmatter_strips_inline_comments() -> None:
    text = (REPO_ROOT / "data" / "default" / "swarms" / "coding" / "coder.md").read_text(encoding="utf-8")
    fm = _FrontmatterParser.parse(text)
    assert fm["skill_pack"][0] == "prime-safety"
    assert all("#" not in s for s in fm["skill_pack"])


def test_persona_primary_extracted() -> None:
    service = SwarmService(REPO_ROOT)
    swarm = service._load_swarm("coder")
    assert swarm["persona_primary"] == "Donald Knuth"


def test_all_swarms_parse_without_corruption() -> None:
    for path in sorted((REPO_ROOT / "data" / "default" / "swarms").rglob("*.md")):
        if path.name.startswith("README"):
            continue
        fm = _FrontmatterParser.parse(path.read_text(encoding="utf-8"))
        for skill in fm.get("skill_pack", []):
            assert "#" not in skill


def test_audit_failure_logged_not_silenced(monkeypatch, caplog) -> None:
    service = SwarmService(REPO_ROOT)

    class BrokenAuditLogger:
        def log_llm_call(self, **kwargs):  # pragma: no cover - exercised via dispatch
            del kwargs
            raise RuntimeError("audit backend unavailable")

    service.audit_logger = BrokenAuditLogger()
    monkeypatch.setattr(
        service.llm,
        "complete",
        lambda **kwargs: {"ok": True, "provider": "claude-code", "completion": "ok"},
    )

    app = service.create_app()
    with TestClient(app) as client:
        with caplog.at_level("ERROR"):
            res = client.post("/api/swarms/coder/dispatch", json={"task": "run", "context": {}})

    assert res.status_code == 200
    assert any("audit log failed" in rec.getMessage() for rec in caplog.records)
