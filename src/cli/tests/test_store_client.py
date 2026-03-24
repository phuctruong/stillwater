from __future__ import annotations

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from stillwater import store_client


class _Response:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_list_apps_parses_payload_and_sends_auth_header() -> None:
    seen: dict[str, str] = {}

    def _fake_urlopen(request, timeout=10.0):  # noqa: ARG001
        seen["url"] = request.full_url
        seen["auth"] = request.get_header("Authorization")
        return _Response({"items": [{"app_id": "gmail-inbox-triage"}], "total": 1})

    with patch("urllib.request.urlopen", _fake_urlopen):
        data = store_client.list_apps(base_url="http://127.0.0.1:8090", token="sw_sk_test")

    assert data["total"] == 1
    assert data["items"][0]["app_id"] == "gmail-inbox-triage"
    assert seen["url"] == "http://127.0.0.1:8090/api/v1/store/apps"
    assert seen["auth"] == "Bearer sw_sk_test"


def test_install_app_posts_optional_scopes() -> None:
    seen: dict[str, object] = {}

    def _fake_urlopen(request, timeout=10.0):  # noqa: ARG001
        seen["method"] = request.get_method()
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"app_id": "gmail-inbox-triage", "status": "installed"})

    with patch("urllib.request.urlopen", _fake_urlopen):
        data = store_client.install_app(
            "gmail-inbox-triage",
            optional_scopes_enabled=["gmail.send.email"],
            base_url="http://127.0.0.1:8090",
        )

    assert data["status"] == "installed"
    assert seen["method"] == "POST"
    assert seen["body"] == {"optional_scopes_enabled": ["gmail.send.email"]}


def test_request_json_raises_clean_error_on_http_failure() -> None:
    error = urllib.error.HTTPError(
        url="http://127.0.0.1:8090/api/v1/store/apps/gmail-inbox-triage/install",
        code=403,
        msg="Forbidden",
        hdrs=None,
        fp=io.BytesIO(b'{\"detail\":\"Requires Pro membership ($8/month)\"}'),
    )

    def _fake_urlopen(request, timeout=10.0):  # noqa: ARG001
        raise error

    with patch("urllib.request.urlopen", _fake_urlopen):
        with pytest.raises(store_client.StoreClientError) as excinfo:
            store_client.install_app("linkedin-outreach", base_url="http://127.0.0.1:8090")

    assert excinfo.value.status_code == 403
    assert "Requires Pro membership" in str(excinfo.value)
