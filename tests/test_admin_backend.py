"""
tests/test_admin_backend.py — Admin backend FastAPI server tests

Rung target: 641
Focus: endpoint routing, data CRUD, cloud proxy 503 handling,
       auth header validation, settings exposure.

All cloud-proxy tests use httpx mocking to avoid real network calls.
DataRegistry tests use a temp directory to avoid touching real data.
"""

from __future__ import annotations

import json
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — ensure admin.backend.app is importable
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "cli" / "src"))

# Import the app — this must succeed before any test runs
from admin.backend.app import app  # noqa: E402
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path):
    """Test client with DataRegistry + SettingsLoader pointed at tmp_path."""
    from stillwater.data_registry import DataRegistry
    from stillwater.settings_loader import SettingsLoader

    # Patch registry and settings to use temp dirs so no real data is touched
    test_registry = DataRegistry(repo_root=tmp_path)
    test_settings = SettingsLoader(str(tmp_path / "data" / "settings.md"))

    with patch("admin.backend.app.registry", test_registry), \
         patch("admin.backend.app.settings", test_settings):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c, test_registry, test_settings


# ---------------------------------------------------------------------------
# 1. Health endpoint
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health_returns_ok(self, client):
        c, _, _ = client
        resp = c.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"

    def test_health_has_version(self, client):
        c, _, _ = client
        resp = c.get("/health")
        assert "version" in resp.json()
        assert resp.json()["version"] == "1.0.0"

    def test_health_has_firestore_enabled_field(self, client):
        c, _, _ = client
        resp = c.get("/health")
        assert "firestore_enabled" in resp.json()

    def test_health_firestore_false_by_default(self, client):
        c, _, _ = client
        resp = c.get("/health")
        assert resp.json()["firestore_enabled"] is False


# ---------------------------------------------------------------------------
# 2. Jokes endpoints
# ---------------------------------------------------------------------------


class TestJokes:
    def test_get_jokes_empty_by_default(self, client):
        c, _, _ = client
        resp = c.get("/api/data/jokes")
        assert resp.status_code == 200
        assert resp.json()["jokes"] == []

    def test_get_jokes_returns_list_key(self, client):
        c, _, _ = client
        body = c.get("/api/data/jokes").json()
        assert "jokes" in body

    def test_post_joke_returns_added(self, client):
        c, _, _ = client
        joke = {"text": "Why did the AI cross the road?", "author": "phuc"}
        resp = c.post("/api/data/jokes", json=joke)
        assert resp.status_code == 200
        assert resp.json()["added"]["text"] == joke["text"]

    def test_post_joke_persists_to_registry(self, client):
        c, reg, _ = client
        joke = {"text": "Persistent joke", "author": "test"}
        c.post("/api/data/jokes", json=joke)
        saved = reg.load_data_file("jokes.json")
        assert saved is not None
        data = json.loads(saved)
        assert any(j["text"] == "Persistent joke" for j in data["jokes"])

    def test_post_multiple_jokes_accumulate(self, client):
        c, reg, _ = client
        c.post("/api/data/jokes", json={"text": "Joke A"})
        c.post("/api/data/jokes", json={"text": "Joke B"})
        saved = json.loads(reg.load_data_file("jokes.json"))
        texts = [j["text"] for j in saved["jokes"]]
        assert "Joke A" in texts
        assert "Joke B" in texts


# ---------------------------------------------------------------------------
# 3. Settings endpoint
# ---------------------------------------------------------------------------


class TestSettings:
    def test_get_settings_has_firestore_enabled(self, client):
        c, _, _ = client
        resp = c.get("/api/data/settings")
        assert resp.status_code == 200
        assert "firestore_enabled" in resp.json()

    def test_get_settings_firestore_false_no_key(self, client):
        c, _, _ = client
        resp = c.get("/api/data/settings")
        assert resp.json()["firestore_enabled"] is False

    def test_get_settings_api_key_not_configured_by_default(self, client):
        c, _, _ = client
        resp = c.get("/api/data/settings")
        assert resp.json()["api_key_configured"] is False

    def test_get_settings_api_key_preview_null_when_no_key(self, client):
        c, _, _ = client
        resp = c.get("/api/data/settings")
        assert resp.json()["api_key_preview"] is None

    def test_get_settings_api_key_preview_masked_when_key_present(self, tmp_path):
        """When a valid API key is in settings.md, preview is masked."""
        from stillwater.data_registry import DataRegistry
        from stillwater.settings_loader import SettingsLoader

        # Write a settings.md with a valid API key
        settings_path = tmp_path / "data" / "settings.md"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        fake_key = "sw_sk_" + "a" * 48
        settings_path.write_text(
            f"---\napi_key: {fake_key}\nfirestore_enabled: false\n---\n"
        )
        test_registry = DataRegistry(repo_root=tmp_path)
        test_settings = SettingsLoader(str(settings_path))

        with patch("admin.backend.app.registry", test_registry), \
             patch("admin.backend.app.settings", test_settings):
            with TestClient(app) as c:
                resp = c.get("/api/data/settings")
                assert resp.json()["api_key_configured"] is True
                preview = resp.json()["api_key_preview"]
                assert preview is not None
                assert "..." in preview


# ---------------------------------------------------------------------------
# 4. Wishes endpoint
# ---------------------------------------------------------------------------


class TestWishes:
    def test_get_wishes_returns_content_key(self, client):
        c, _, _ = client
        resp = c.get("/api/data/wishes")
        assert resp.status_code == 200
        assert "content" in resp.json()

    def test_get_wishes_empty_string_by_default(self, client):
        c, _, _ = client
        resp = c.get("/api/data/wishes")
        assert resp.json()["content"] == ""

    def test_post_wish_returns_added(self, client):
        c, _, _ = client
        wish = {"title": "Build OAuth3 core", "priority": "HIGH"}
        resp = c.post("/api/data/wishes", json=wish)
        assert resp.status_code == 200
        assert resp.json()["added"]["title"] == wish["title"]


# ---------------------------------------------------------------------------
# 5. Learned endpoint
# ---------------------------------------------------------------------------


class TestLearned:
    def test_get_learned_returns_list(self, client):
        c, _, _ = client
        resp = c.get("/api/data/learned")
        assert resp.status_code == 200
        assert "learned" in resp.json()
        assert isinstance(resp.json()["learned"], list)

    def test_get_learned_empty_by_default(self, client):
        c, _, _ = client
        resp = c.get("/api/data/learned")
        assert resp.json()["learned"] == []


# ---------------------------------------------------------------------------
# 6. Auth proxy endpoints — 503 on connection error
# ---------------------------------------------------------------------------


class TestAuthProxy:
    def test_verify_token_missing_id_token_returns_400(self, client):
        c, _, _ = client
        resp = c.post("/api/auth/verify-token", json={})
        assert resp.status_code == 400

    def test_verify_token_connection_error_returns_503(self, client):
        c, _, _ = client
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("connection refused")
            # We need to patch at the right level — use ConnectError
            import httpx as _httpx

            mock_post.side_effect = _httpx.ConnectError("connection refused")
            resp = c.post("/api/auth/verify-token", json={"id_token": "fake-token"})
            assert resp.status_code == 503

    def test_get_user_missing_auth_header_returns_401(self, client):
        c, _, _ = client
        resp = c.get("/api/auth/user")
        assert resp.status_code == 401

    def test_get_user_malformed_auth_header_returns_401(self, client):
        c, _, _ = client
        resp = c.get("/api/auth/user", headers={"Authorization": "notbearer abc"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 7. Verification proxy endpoints — 503 on connection error
# ---------------------------------------------------------------------------


class TestVerifyProxy:
    def test_verify_social_no_auth_returns_401(self, client):
        c, _, _ = client
        resp = c.post("/api/verify/social", json={"url": "https://example.com"})
        assert resp.status_code == 401

    def test_verify_status_no_auth_returns_401(self, client):
        c, _, _ = client
        resp = c.get("/api/verify/status")
        assert resp.status_code == 401

    def test_verify_social_cloud_unavailable_returns_503(self, client):
        c, _, _ = client
        import httpx as _httpx
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = _httpx.ConnectError("cloud down")
            resp = c.post(
                "/api/verify/social",
                json={"url": "https://x.com/user/status/123"},
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp.status_code == 503

    def test_verify_status_cloud_unavailable_returns_503(self, client):
        c, _, _ = client
        import httpx as _httpx
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = _httpx.ConnectError("cloud down")
            resp = c.get(
                "/api/verify/status",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 8. API key proxy endpoints — 503 + 401
# ---------------------------------------------------------------------------


class TestApiKeyProxy:
    def test_generate_key_no_auth_returns_401(self, client):
        c, _, _ = client
        resp = c.post("/api/keys/generate")
        assert resp.status_code == 401

    def test_list_keys_no_auth_returns_401(self, client):
        c, _, _ = client
        resp = c.get("/api/keys/list")
        assert resp.status_code == 401

    def test_generate_key_cloud_unavailable_returns_503(self, client):
        c, _, _ = client
        import httpx as _httpx
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = _httpx.ConnectError("cloud down")
            resp = c.post(
                "/api/keys/generate",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp.status_code == 503

    def test_list_keys_cloud_unavailable_returns_503(self, client):
        c, _, _ = client
        import httpx as _httpx
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = _httpx.ConnectError("cloud down")
            resp = c.get(
                "/api/keys/list",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 9. Static file serving
# ---------------------------------------------------------------------------


class TestStaticServing:
    def test_root_returns_200_when_index_exists(self, client):
        """GET / returns 200 because admin/static/index.html exists in real repo."""
        c, _, _ = client
        resp = c.get("/")
        # Index exists in the real repo — should return 200
        assert resp.status_code == 200

    def test_root_returns_html_content_type(self, client):
        c, _, _ = client
        resp = c.get("/")
        assert "text/html" in resp.headers.get("content-type", "")
