from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from services.key_manager import KeyManager


def test_corrupt_override_file_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    override = repo / "data" / "custom" / "swarm-model-overrides.json"
    override.parent.mkdir(parents=True, exist_ok=True)
    override.write_text("{not-json", encoding="utf-8")

    km = KeyManager(repo_root=repo)
    with pytest.raises(RuntimeError, match="swarm model overrides file is corrupt"):
        km.set_swarm_model("coder", "sonnet")


def test_corrupt_override_file_logs_warning(tmp_path: Path, caplog) -> None:
    repo = tmp_path / "repo"
    override = repo / "data" / "custom" / "swarm-model-overrides.json"
    override.parent.mkdir(parents=True, exist_ok=True)
    override.write_text("{not-json", encoding="utf-8")

    km = KeyManager(repo_root=repo)
    with caplog.at_level("WARNING"):
        model = km.get_swarm_model("coder", "haiku")
    assert model == "haiku"
    assert any("swarm model overrides file is corrupt" in rec.getMessage() for rec in caplog.records)


def test_gemini_api_env_key_supported(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    km = KeyManager(repo_root=repo)
    monkeypatch.setenv("GEMINI_API_KEY", "g-123")
    key, source = km.get_provider_key("gemini-api")
    assert key == "g-123"
    assert source == "env"
