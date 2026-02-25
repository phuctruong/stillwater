from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from stillwater.connectors.gmail import GmailConnector, ScopeDeniedError


def _future_iso(hours: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def test_connect_requires_scopes_list() -> None:
    c = GmailConnector(request_fn=lambda *_: {})
    with pytest.raises(ValueError):
        c.connect({"scopes": "gmail.read.inbox"})


def test_connect_rejects_expired_token() -> None:
    c = GmailConnector(request_fn=lambda *_: {})
    expires = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    with pytest.raises(ScopeDeniedError):
        c.connect({"scopes": ["gmail.read.inbox"], "expires_at": expires})


def test_fetch_unread_calls_request_fn() -> None:
    calls = []

    def _req(method, path, payload):
        calls.append((method, path, payload))
        return {"messages": [{"id": "m1"}]}

    c = GmailConnector(request_fn=_req)
    c.connect({"scopes": ["gmail.read.inbox"], "expires_at": _future_iso()})
    rows = c.fetch_unread(max_results=25)
    assert rows == [{"id": "m1"}]
    assert calls[0][0] == "GET"
    assert calls[0][1] == "/gmail/messages"
    assert calls[0][2]["max_results"] == 25


def test_apply_label_requires_scope() -> None:
    c = GmailConnector(request_fn=lambda *_: {"ok": True})
    c.connect({"scopes": ["gmail.read.inbox"], "expires_at": _future_iso()})
    with pytest.raises(ScopeDeniedError):
        c.apply_label("abc", "important")


def test_archive_requires_scope() -> None:
    c = GmailConnector(request_fn=lambda *_: {"ok": True})
    c.connect({"scopes": ["gmail.modify.label"], "expires_at": _future_iso()})
    with pytest.raises(ScopeDeniedError):
        c.archive("abc")


def test_health_check_reports_connection() -> None:
    c = GmailConnector(request_fn=lambda *_: {"ok": True})
    c.connect({"scopes": ["gmail.read.inbox"], "expires_at": _future_iso()})
    health = c.health_check()
    assert health["ok"] is True
    assert health["connector"] == "gmail"
    assert "gmail.read.inbox" in health["scopes"]

