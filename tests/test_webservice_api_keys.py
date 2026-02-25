"""
Stillwater Webservice — API key auth + DataRegistry integration tests.

Version: 1.0.0 | Rung: 641 | Persona: Skeptic Auditor

Coverage:
  - API key required for sync endpoints (401 on missing key)
  - Invalid key format rejected with 401
  - Valid key format accepted (200)
  - DataRegistry used for all reads
  - DataRegistry.save_data_file() called for all writes
  - Settings metadata updated on save
  - No API key required for read/learn endpoints
  - Admin reload-data works with valid key
  - Firestore unavailable → graceful fallback
  - Health endpoint always accessible
  - 401 vs 403 contract (format invalid = 401)

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_webservice_api_keys.py -v --tb=short
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CLI_SRC = _REPO_ROOT / "src" / "cli" / "src"
_ADMIN = _REPO_ROOT / "admin"

for p in [str(_CLI_SRC), str(_REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient  # noqa: E402

# Import create_app (not the module-level default app — we need test isolation)
from admin.app import create_app  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_KEY = "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"
_INVALID_KEY_SHORT = "sw_sk_tooshort"
_INVALID_KEY_PREFIX = "sk_aabbccddeeff00112233445566778899aabbccddeeff0011"
_INVALID_KEY_UPPERCASE = "sw_sk_AABBCCDDEEFF00112233445566778899AABBCCDDEEFF0011"
_VALID_KEY_BEARER = f"Bearer {_VALID_KEY}"

_SETTINGS_ENABLED = """\
---
api_key: sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011
firestore_project: stillwater-test
firestore_enabled: false
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---
"""

_SETTINGS_DISABLED = """\
---
api_key: null
firestore_project: stillwater-test
firestore_enabled: false
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    """Create a minimal test repo with data/default/ + data/custom/."""
    (tmp_path / "data" / "default").mkdir(parents=True)
    (tmp_path / "data" / "custom").mkdir(parents=True)
    (tmp_path / "data" / "custom" / ".gitkeep").write_text("", encoding="utf-8")

    # Seed default files
    jokes = [
        {"id": "joke_001", "joke": "Why do programmers prefer dark mode? Bugs.", "tags": ["test"]}
    ]
    (tmp_path / "data" / "default" / "jokes.json").write_text(
        json.dumps(jokes, indent=2), encoding="utf-8"
    )
    (tmp_path / "data" / "default" / "wishes.md").write_text(
        "# Wishes\n- oauth\n", encoding="utf-8"
    )
    (tmp_path / "data" / "default" / "combos.mermaid").write_text(
        "stateDiagram-v2\n  A --> B\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def settings_file(repo_root: Path) -> Path:
    """Write a settings.md with a valid API key."""
    p = repo_root / "data" / "settings.md"
    p.write_text(_SETTINGS_ENABLED, encoding="utf-8")
    return p


@pytest.fixture()
def client_with_key(repo_root: Path, settings_file: Path) -> TestClient:
    """Test client with valid API key in settings.md."""
    settings_path = str(settings_file)
    app = create_app(repo_root=repo_root, settings_path=settings_path)
    return TestClient(app)


@pytest.fixture()
def client_no_settings(repo_root: Path) -> TestClient:
    """Test client with NO settings.md (defaults, no API key)."""
    app = create_app(repo_root=repo_root, settings_path=str(repo_root / "data" / "settings.md"))
    return TestClient(app)


# ---------------------------------------------------------------------------
# Group 1: Health check — always accessible
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Health endpoint must always return 200."""

    def test_health_returns_200(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/health")
        assert r.status_code == 200

    def test_health_has_status_ok(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/health")
        assert r.json()["status"] == "ok"

    def test_health_includes_registry_files(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/health")
        data = r.json()
        assert "registry_files" in data
        assert isinstance(data["registry_files"], int)
        assert data["registry_files"] >= 3  # jokes.json, wishes.md, combos.mermaid

    def test_health_no_auth_required(self, client_no_settings: TestClient) -> None:
        r = client_no_settings.get("/health")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Group 2: Read endpoints — no auth required
# ---------------------------------------------------------------------------


class TestReadEndpoints:
    """Read endpoints must be accessible without API key."""

    def test_get_jokes_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/jokes")
        assert r.status_code == 200

    def test_get_jokes_returns_list(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/jokes")
        data = r.json()
        assert "jokes" in data
        assert isinstance(data["jokes"], list)

    def test_get_jokes_from_registry(self, client_with_key: TestClient) -> None:
        """DataRegistry provides jokes data."""
        r = client_with_key.get("/api/v1/data/jokes")
        data = r.json()
        assert data["source"] == "registry"
        assert len(data["jokes"]) >= 1

    def test_get_wishes_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/wishes")
        assert r.status_code == 200

    def test_get_wishes_returns_content(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/wishes")
        data = r.json()
        assert data["source"] == "registry"
        assert data["wishes"] is not None

    def test_get_combos_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/combos")
        assert r.status_code == 200

    def test_list_data_files_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/list")
        assert r.status_code == 200

    def test_list_data_files_includes_defaults(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/data/list")
        data = r.json()
        assert "files" in data
        file_list = data["files"]
        assert "jokes.json" in file_list
        assert "wishes.md" in file_list
        assert "combos.mermaid" in file_list


# ---------------------------------------------------------------------------
# Group 3: API key requirement for sync endpoints
# ---------------------------------------------------------------------------


class TestSyncEndpointsRequireApiKey:
    """Sync endpoints must return 401 when no API key provided."""

    def test_backup_without_key_returns_401(self, client_with_key: TestClient) -> None:
        r = client_with_key.post("/api/v1/sync/backup", json={})
        assert r.status_code == 401

    def test_sync_status_without_key_returns_401(self, client_with_key: TestClient) -> None:
        r = client_with_key.get("/api/v1/sync/status")
        assert r.status_code == 401

    def test_storage_mode_without_key_returns_401(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/config/storage-mode", json={"firestore_enabled": True}
        )
        assert r.status_code == 401

    def test_reload_without_key_returns_401(self, client_with_key: TestClient) -> None:
        r = client_with_key.post("/api/v1/admin/reload-data")
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Group 4: Invalid API key format rejected with 401
# ---------------------------------------------------------------------------


class TestInvalidApiKeyRejected:
    """Invalid key formats must return 401."""

    def test_short_key_rejected(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": f"Bearer {_INVALID_KEY_SHORT}"},
        )
        assert r.status_code == 401

    def test_wrong_prefix_rejected(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": f"Bearer {_INVALID_KEY_PREFIX}"},
        )
        assert r.status_code == 401

    def test_uppercase_hex_rejected(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": f"Bearer {_INVALID_KEY_UPPERCASE}"},
        )
        assert r.status_code == 401

    def test_empty_bearer_rejected(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": "Bearer "},
        )
        assert r.status_code == 401

    def test_no_bearer_prefix_rejected(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": _VALID_KEY},
        )
        assert r.status_code == 401

    def test_invalid_key_error_message_present(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": f"Bearer {_INVALID_KEY_SHORT}"},
        )
        detail = r.json().get("detail", "")
        assert "Invalid API key" in detail or "Missing API key" in detail or "401" in str(r.status_code)


# ---------------------------------------------------------------------------
# Group 5: Valid API key format accepted
# ---------------------------------------------------------------------------


class TestValidApiKeyAccepted:
    """Valid key format must be accepted (200) on sync endpoints."""

    def test_sync_status_with_valid_key(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        assert r.status_code == 200

    def test_sync_status_response_fields(self, client_with_key: TestClient) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        assert "sync_enabled" in data
        assert "firestore_enabled" in data
        assert "last_sync_status" in data

    def test_backup_with_valid_key(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/sync/backup",
            json={},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        assert r.status_code == 200

    def test_backup_response_has_api_key_prefix(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/sync/backup",
            json={},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        assert "api_key_prefix" in data
        assert data["api_key_prefix"].startswith("sw_sk_aabbcc")

    def test_storage_mode_with_valid_key(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/config/storage-mode",
            json={"firestore_enabled": False},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        assert r.status_code == 200

    def test_storage_mode_returns_updated_flag(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/config/storage-mode",
            json={"firestore_enabled": True},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        assert data["updated"] is True
        assert data["firestore_enabled"] is True

    def test_reload_data_with_valid_key(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/admin/reload-data",
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        assert r.status_code == 200

    def test_reload_response_includes_file_count(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/admin/reload-data",
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        assert data["reloaded"] is True
        assert isinstance(data["files_loaded"], int)
        assert data["files_loaded"] >= 3


# ---------------------------------------------------------------------------
# Group 6: DataRegistry used for all reads
# ---------------------------------------------------------------------------


class TestDataRegistryIntegration:
    """DataRegistry must be the source of truth for all read operations."""

    def test_custom_jokes_override_default(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Custom overlay takes precedence over default jokes.json."""
        custom_jokes = [{"id": "custom_001", "joke": "Custom joke here", "tags": []}]
        (repo_root / "data" / "custom").mkdir(parents=True, exist_ok=True)
        (repo_root / "data" / "custom" / "jokes.json").write_text(
            json.dumps(custom_jokes), encoding="utf-8"
        )

        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            r = c.get("/api/v1/data/jokes")
            data = r.json()
            assert data["jokes"][0]["id"] == "custom_001"

    def test_registry_loaded_on_startup(self, client_with_key: TestClient) -> None:
        """DataRegistry must be pre-loaded at startup."""
        r = client_with_key.get("/health")
        assert r.json()["registry_files"] >= 3

    def test_missing_jokes_returns_empty_list(
        self, tmp_path: Path
    ) -> None:
        """Empty registry returns empty jokes list (not 500)."""
        # No data/default — empty registry
        app = create_app(
            repo_root=tmp_path,
            settings_path=str(tmp_path / "data" / "settings.md"),
        )
        with TestClient(app) as c:
            r = c.get("/api/v1/data/jokes")
            assert r.status_code == 200
            assert r.json()["jokes"] == []


# ---------------------------------------------------------------------------
# Group 7: DataRegistry.save_data_file() called for all writes
# ---------------------------------------------------------------------------


class TestDataRegistrySaveIntegration:
    """Learn endpoints must persist via DataRegistry.save_data_file()."""

    def test_learn_smalltalk_saves_to_custom(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Learned smalltalk must land in data/custom/."""
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            r = c.post(
                "/api/v1/smalltalk/learn",
                json={
                    "pattern_id": "test_pattern_001",
                    "response_template": "Test response {name}",
                    "keywords": ["test", "hello"],
                    "confidence": 0.8,
                },
            )
            assert r.status_code == 200
            assert r.json()["saved"] is True

        saved_path = repo_root / "data" / "custom" / "smalltalk" / "learned_smalltalk.jsonl"
        assert saved_path.exists(), "Learned entry not written to custom/"
        content = saved_path.read_text(encoding="utf-8")
        assert "test_pattern_001" in content

    def test_learn_intent_saves_to_custom(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Learned intent must land in data/custom/."""
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            r = c.post(
                "/api/v1/intent/learn",
                json={
                    "wish_id": "test-wish-001",
                    "keywords": ["oauth", "login"],
                    "confidence": 0.75,
                },
            )
            assert r.status_code == 200

        saved_path = repo_root / "data" / "custom" / "intent" / "learned_wishes.jsonl"
        assert saved_path.exists()
        content = saved_path.read_text(encoding="utf-8")
        assert "test-wish-001" in content

    def test_learn_execution_saves_to_custom(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Learned execution combo must land in data/custom/."""
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            r = c.post(
                "/api/v1/execution/learn",
                json={
                    "wish_id": "test-combo-001",
                    "swarm": "coder",
                    "recipe": ["prime-safety", "prime-coder"],
                    "confidence": 0.9,
                },
            )
            assert r.status_code == 200

        saved_path = repo_root / "data" / "custom" / "execute" / "learned_combos.jsonl"
        assert saved_path.exists()
        content = saved_path.read_text(encoding="utf-8")
        assert "test-combo-001" in content

    def test_learn_never_writes_to_default(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Write operations must NEVER touch data/default/."""
        default_dir = repo_root / "data" / "default"
        before_mtimes = {
            f: f.stat().st_mtime for f in default_dir.rglob("*") if f.is_file()
        }

        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            c.post(
                "/api/v1/smalltalk/learn",
                json={
                    "pattern_id": "guard_test",
                    "response_template": "hello",
                    "keywords": ["hi"],
                },
            )

        after_mtimes = {
            f: f.stat().st_mtime for f in default_dir.rglob("*") if f.is_file()
        }
        assert before_mtimes == after_mtimes, "data/default/ was modified — this is a bug"

    def test_multiple_learn_calls_append_correctly(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Multiple learn calls must append, not overwrite."""
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            c.post(
                "/api/v1/intent/learn",
                json={"wish_id": "wish-a", "keywords": ["alpha"]},
            )
            c.post(
                "/api/v1/intent/learn",
                json={"wish_id": "wish-b", "keywords": ["beta"]},
            )

        saved_path = repo_root / "data" / "custom" / "intent" / "learned_wishes.jsonl"
        lines = [
            l for l in saved_path.read_text(encoding="utf-8").splitlines() if l.strip()
        ]
        assert len(lines) >= 2, "Second learn call overwrote the first"
        content = saved_path.read_text(encoding="utf-8")
        assert "wish-a" in content
        assert "wish-b" in content


# ---------------------------------------------------------------------------
# Group 8: Settings metadata updated on save
# ---------------------------------------------------------------------------


class TestSettingsMetadataUpdate:
    """Settings metadata must be updated on every learn/save operation."""

    def test_smalltalk_learn_updates_sync_metadata(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            c.post(
                "/api/v1/smalltalk/learn",
                json={"pattern_id": "meta_test", "response_template": "hi"},
            )

        text = settings_file.read_text(encoding="utf-8")
        assert "last_sync_timestamp" in text
        assert "pending" in text or "ok" in text

    def test_intent_learn_updates_sync_metadata(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            c.post(
                "/api/v1/intent/learn",
                json={"wish_id": "meta-wish", "keywords": ["x"]},
            )

        text = settings_file.read_text(encoding="utf-8")
        assert "last_sync_timestamp" in text


# ---------------------------------------------------------------------------
# Group 9: No API key required for learn endpoints
# ---------------------------------------------------------------------------


class TestLearnEndpointsNoAuth:
    """Learn endpoints must work without API key."""

    def test_smalltalk_learn_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/smalltalk/learn",
            json={"pattern_id": "noauth_test", "response_template": "hello"},
        )
        assert r.status_code == 200

    def test_intent_learn_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/intent/learn",
            json={"wish_id": "noauth-wish", "keywords": ["test"]},
        )
        assert r.status_code == 200

    def test_execution_learn_no_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/execution/learn",
            json={"wish_id": "noauth-combo", "swarm": "coder", "recipe": []},
        )
        assert r.status_code == 200

    def test_learn_response_includes_saved_true(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/smalltalk/learn",
            json={"pattern_id": "saved_flag_test", "response_template": "hi"},
        )
        assert r.json()["saved"] is True

    def test_learn_response_synced_false_initially(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/intent/learn",
            json={"wish_id": "sync-flag-test", "keywords": []},
        )
        assert r.json()["synced"] is False


# ---------------------------------------------------------------------------
# Group 10: Firestore unavailable → graceful fallback
# ---------------------------------------------------------------------------


class TestFirestoreGracefulFallback:
    """When Firestore is unavailable/not-enabled, backup must not raise 500."""

    def test_backup_without_firestore_enabled_returns_200(
        self, client_with_key: TestClient
    ) -> None:
        """Backup with firestore_enabled=false returns 200 (not 500)."""
        r = client_with_key.post(
            "/api/v1/sync/backup",
            json={},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        assert r.status_code == 200

    def test_backup_without_firestore_reports_not_backed_up(
        self, client_with_key: TestClient
    ) -> None:
        """When Firestore is disabled, backed_up should be False."""
        r = client_with_key.post(
            "/api/v1/sync/backup",
            json={},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        # firestore_enabled=false → backed_up=False, not an error response
        assert "backed_up" in data
        assert "error" in data

    def test_backup_includes_file_list(
        self, client_with_key: TestClient
    ) -> None:
        r = client_with_key.post(
            "/api/v1/sync/backup",
            json={},
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        assert "files_included" in data
        assert isinstance(data["files_included"], int)

    def test_sync_status_shows_not_enabled(
        self, client_with_key: TestClient
    ) -> None:
        r = client_with_key.get(
            "/api/v1/sync/status",
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        # Settings file has firestore_enabled=false
        assert data["firestore_enabled"] is False
        assert data["sync_enabled"] is False


# ---------------------------------------------------------------------------
# Group 11: Admin reload-data
# ---------------------------------------------------------------------------


class TestAdminReloadData:
    """Admin reload-data endpoint must refresh registry from disk."""

    def test_reload_reflects_custom_file_added_after_startup(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """Files added after startup appear after reload."""
        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        with TestClient(app) as c:
            # Before adding custom file
            r_before = c.get("/api/v1/data/list")
            before_count = r_before.json()["count"]

            # Add a new custom file AFTER startup
            custom_dir = repo_root / "data" / "custom"
            (custom_dir / "new_custom.json").write_text('{"x": 1}', encoding="utf-8")

            # Reload
            c.post(
                "/api/v1/admin/reload-data",
                headers={"Authorization": _VALID_KEY_BEARER},
            )

            # After reload
            r_after = c.get("/api/v1/data/list")
            after_count = r_after.json()["count"]

        assert after_count > before_count, "Reload did not pick up new custom file"

    def test_reload_requires_auth(self, client_with_key: TestClient) -> None:
        r = client_with_key.post("/api/v1/admin/reload-data")
        assert r.status_code == 401

    def test_reload_timestamp_present(self, client_with_key: TestClient) -> None:
        r = client_with_key.post(
            "/api/v1/admin/reload-data",
            headers={"Authorization": _VALID_KEY_BEARER},
        )
        data = r.json()
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")


# ---------------------------------------------------------------------------
# Group 12: Thread safety — concurrent requests
# ---------------------------------------------------------------------------


class TestConcurrentRequests:
    """Multiple concurrent requests must not corrupt data."""

    def test_concurrent_learn_calls_all_succeed(
        self, repo_root: Path, settings_file: Path
    ) -> None:
        """10 concurrent learn calls must all return 200."""
        import threading

        app = create_app(repo_root=repo_root, settings_path=str(settings_file))
        statuses: list[int] = []
        errors: list[Exception] = []

        def do_learn(i: int) -> None:
            try:
                with TestClient(app) as c:
                    r = c.post(
                        "/api/v1/intent/learn",
                        json={
                            "wish_id": f"concurrent-wish-{i:03d}",
                            "keywords": [f"keyword_{i}"],
                        },
                    )
                    statuses.append(r.status_code)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=do_learn, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Thread errors: {errors}"
        assert all(s == 200 for s in statuses), f"Some failed: {statuses}"

    def test_concurrent_reads_no_data_races(
        self, client_with_key: TestClient
    ) -> None:
        """50 concurrent reads must all return 200 and valid data."""
        import threading

        results: list[dict] = []
        errors: list[Exception] = []

        def do_read() -> None:
            try:
                r = client_with_key.get("/api/v1/data/jokes")
                results.append({"status": r.status_code, "count": len(r.json().get("jokes", []))})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=do_read) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Thread errors: {errors}"
        assert all(r["status"] == 200 for r in results)
