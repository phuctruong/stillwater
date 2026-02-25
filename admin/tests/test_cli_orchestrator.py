from __future__ import annotations

import sys
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import cli_orchestrator


def test_check_portal_health_request_error_returns_false(monkeypatch) -> None:
    def _boom(*args, **kwargs):
        del args, kwargs
        raise requests.exceptions.ConnectionError("down")

    monkeypatch.setattr(cli_orchestrator.requests, "get", _boom)
    assert cli_orchestrator.check_portal_health() is False


def test_check_portal_health_keyboardinterrupt_propagates(monkeypatch) -> None:
    def _interrupt(*args, **kwargs):
        del args, kwargs
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli_orchestrator.requests, "get", _interrupt)
    with pytest.raises(KeyboardInterrupt):
        cli_orchestrator.check_portal_health()
