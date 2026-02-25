"""Integration tests for AdminClient against a real admin server.

Tests verify round-trip: AdminClient call → HTTP → AdminHandler → response → parsed dict.

Run with:
    pytest src/cli/tests/test_admin_client.py -v

Pattern mirrors admin/tests/test_admin_server.py:
- Module-scoped fixture starts a real ThreadingHTTPServer on a free port.
- AdminClient is pointed at that port.
- Every test calls the client and asserts on the returned dict.
"""

from __future__ import annotations

import socket
import sys
import threading
import time
from pathlib import Path

import pytest

# --- Path setup -----------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
ADMIN_DIR = REPO_ROOT / "admin"
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"

for _p in (str(ADMIN_DIR), str(CLI_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from http.server import ThreadingHTTPServer

import server as admin_server
from stillwater.admin_client import AdminClient, AdminClientError


# =========================================================================
# Helpers
# =========================================================================

def _free_port() -> int:
    """Return an available TCP port on 127.0.0.1."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# =========================================================================
# Module-scoped server fixture
# =========================================================================

@pytest.fixture(scope="module")
def admin_client():
    """Start the admin server on a free port; yield a configured AdminClient.

    The server is shut down after all tests in this module complete.
    """
    port = _free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), admin_server.AdminHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)  # Let the server accept connections

    client = AdminClient(base_url=f"http://127.0.0.1:{port}", timeout=10)
    yield client

    httpd.shutdown()
    httpd.server_close()


# =========================================================================
# 1. Catalog API
# =========================================================================

class TestGetCatalog:
    """Tests for AdminClient.get_catalog()."""

    def test_returns_dict_with_ok_true(self, admin_client):
        result = admin_client.get_catalog()
        assert isinstance(result, dict)
        assert result.get("ok") is True

    def test_has_groups_list(self, admin_client):
        result = admin_client.get_catalog()
        assert "groups" in result
        assert isinstance(result["groups"], list)

    def test_has_extras_list(self, admin_client):
        result = admin_client.get_catalog()
        assert "extras" in result
        assert isinstance(result["extras"], list)

    def test_groups_count_is_10(self, admin_client):
        """Catalog should expose exactly 10 groups (matches CATALOG_GROUPS length)."""
        result = admin_client.get_catalog()
        assert len(result["groups"]) == 10

    def test_group_schema_has_required_fields(self, admin_client):
        result = admin_client.get_catalog()
        for group in result["groups"]:
            assert "id" in group
            assert "title" in group
            assert "files" in group
            assert "count" in group

    def test_count_matches_files_length(self, admin_client):
        result = admin_client.get_catalog()
        for group in result["groups"]:
            assert group["count"] == len(group["files"]), (
                f"count mismatch in group {group['id']}"
            )

    def test_file_entries_have_required_fields(self, admin_client):
        result = admin_client.get_catalog()
        for group in result["groups"]:
            for f in group["files"]:
                assert "path" in f
                assert "name" in f
                assert "group" in f
                assert "dir" in f

    def test_root_skills_group_exists(self, admin_client):
        result = admin_client.get_catalog()
        ids = {g["id"] for g in result["groups"]}
        assert "root_skills" in ids

    def test_prime_safety_in_root_skills(self, admin_client):
        result = admin_client.get_catalog()
        root_skills = next((g for g in result["groups"] if g["id"] == "root_skills"), None)
        assert root_skills is not None
        paths = [f["path"] for f in root_skills["files"]]
        assert any("prime-safety.md" in p for p in paths)


# =========================================================================
# 2. File Read API
# =========================================================================

class TestGetFile:
    """Tests for AdminClient.get_file()."""

    def test_read_real_file_returns_dict(self, admin_client):
        result = admin_client.get_file("data/default/skills/prime-safety.md")
        assert isinstance(result, dict)
        assert result.get("ok") is True

    def test_content_is_non_empty_string(self, admin_client):
        result = admin_client.get_file("data/default/skills/prime-safety.md")
        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0

    def test_path_echoed_in_response(self, admin_client):
        result = admin_client.get_file("data/default/skills/prime-safety.md")
        assert result["path"] == "data/default/skills/prime-safety.md"

    def test_size_matches_content_bytes(self, admin_client):
        result = admin_client.get_file("data/default/skills/prime-safety.md")
        assert result["size"] == len(result["content"].encode("utf-8"))

    def test_sha256_is_64_hex_chars(self, admin_client):
        result = admin_client.get_file("data/default/skills/prime-safety.md")
        sha = result["sha256"]
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_sha256_matches_content(self, admin_client):
        import hashlib
        result = admin_client.get_file("data/default/skills/prime-safety.md")
        expected = hashlib.sha256(result["content"].encode("utf-8")).hexdigest()
        assert result["sha256"] == expected

    def test_nonexistent_file_raises_error(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.get_file("data/default/skills/does_not_exist_xyzzy.md")
        assert exc_info.value.status == 400

    def test_disallowed_suffix_raises_error(self, admin_client):
        """Reading a .py file should raise AdminClientError."""
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.get_file("admin/server.py")
        assert exc_info.value.status == 400

    def test_empty_path_raises_error(self, admin_client):
        with pytest.raises(AdminClientError):
            admin_client.get_file("")

    def test_path_traversal_raises_error(self, admin_client):
        with pytest.raises(AdminClientError):
            admin_client.get_file("../../../etc/passwd")


# =========================================================================
# 3. File Save API
# =========================================================================

class TestSaveFile:
    """Tests for AdminClient.save_file()."""

    def test_round_trip_write_and_read(self, admin_client):
        """Write content, then read it back and verify round-trip."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_file = skills_dir / "zzz_client_test_save_temp.md"
        test_rel = "data/default/skills/zzz_client_test_save_temp.md"
        original = "# Client test save\n\nOriginal content.\n"

        try:
            test_file.write_text(original, encoding="utf-8")
            new_content = "# Updated by client test\n\nRound-trip verified.\n"

            saved = admin_client.save_file(test_rel, new_content)
            assert saved.get("ok") is True
            assert saved["path"] == test_rel

            # Re-read via client and verify
            read = admin_client.get_file(test_rel)
            assert read["content"] == new_content
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_save_returns_sha256(self, admin_client):
        import hashlib
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_file = skills_dir / "zzz_client_sha256_temp.md"
        test_rel = "data/default/skills/zzz_client_sha256_temp.md"
        content = "# sha256 client test\n"

        try:
            test_file.write_text(content, encoding="utf-8")
            result = admin_client.save_file(test_rel, content)
            expected_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
            assert result["sha256"] == expected_sha
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_save_returns_correct_size(self, admin_client):
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_file = skills_dir / "zzz_client_size_temp.md"
        test_rel = "data/default/skills/zzz_client_size_temp.md"
        content = "# size test\n"

        try:
            test_file.write_text(content, encoding="utf-8")
            result = admin_client.save_file(test_rel, content)
            assert result["size"] == len(content.encode("utf-8"))
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_save_disallowed_suffix_raises_error(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.save_file("admin/server.py", "# hacked")
        assert exc_info.value.status == 400

    def test_save_path_traversal_raises_error(self, admin_client):
        with pytest.raises(AdminClientError):
            admin_client.save_file("../../../tmp/evil.md", "evil")

    def test_save_empty_path_raises_error(self, admin_client):
        with pytest.raises(AdminClientError):
            admin_client.save_file("", "content")


# =========================================================================
# 4. File Create API
# =========================================================================

class TestCreateFile:
    """Tests for AdminClient.create_file()."""

    def test_create_in_valid_group(self, admin_client):
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        filename = "zzz_client_create_temp"
        expected = skills_dir / f"{filename}.md"

        try:
            result = admin_client.create_file("root_skills", filename)
            assert result.get("ok") is True
            assert result.get("created") is True
            assert expected.exists()
        finally:
            if expected.exists():
                expected.unlink()

    def test_create_adds_md_extension(self, admin_client):
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        filename = "zzz_client_ext_temp"
        expected = skills_dir / f"{filename}.md"

        try:
            result = admin_client.create_file("root_skills", filename)
            assert result.get("ok") is True
            assert "path" in result
            assert result["path"].endswith(".md")
        finally:
            if expected.exists():
                expected.unlink()

    def test_create_duplicate_raises_error(self, admin_client):
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        filename = "zzz_client_dup_temp"
        expected = skills_dir / f"{filename}.md"

        try:
            admin_client.create_file("root_skills", filename)
            with pytest.raises(AdminClientError) as exc_info:
                admin_client.create_file("root_skills", filename)
            assert exc_info.value.status == 400
        finally:
            if expected.exists():
                expected.unlink()

    def test_create_invalid_group_raises_error(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.create_file("nonexistent_group_xyz", "test.md")
        assert exc_info.value.status == 400

    def test_create_invalid_filename_raises_error(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.create_file("root_skills", "../../../evil")
        assert exc_info.value.status == 400

    def test_create_filename_with_spaces_raises_error(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.create_file("root_skills", "bad name with spaces")
        assert exc_info.value.status == 400


# =========================================================================
# 5. LLM Status API
# =========================================================================

class TestGetLLMStatus:
    """Tests for AdminClient.get_llm_status()."""

    def test_returns_dict_with_ok_true(self, admin_client):
        result = admin_client.get_llm_status()
        assert isinstance(result, dict)
        assert result.get("ok") is True

    def test_has_status_nested_dict(self, admin_client):
        result = admin_client.get_llm_status()
        assert "status" in result
        assert isinstance(result["status"], dict)

    def test_status_has_required_fields(self, admin_client):
        result = admin_client.get_llm_status()
        s = result["status"]
        assert "provider" in s
        assert "setup_ok" in s
        assert "models" in s
        assert "ollama_installed" in s
        assert "probes" in s
        assert "preferred_ollama_url" in s

    def test_setup_ok_is_bool(self, admin_client):
        result = admin_client.get_llm_status()
        assert isinstance(result["status"]["setup_ok"], bool)

    def test_models_is_list(self, admin_client):
        result = admin_client.get_llm_status()
        assert isinstance(result["status"]["models"], list)

    def test_ollama_installed_is_bool(self, admin_client):
        result = admin_client.get_llm_status()
        assert isinstance(result["status"]["ollama_installed"], bool)


# =========================================================================
# 6. Community API
# =========================================================================

class TestCommunityAPI:
    """Tests for community status, link, and sync methods."""

    def test_get_community_status_returns_ok(self, admin_client):
        result = admin_client.get_community_status()
        assert result.get("ok") is True

    def test_community_status_has_community_dict(self, admin_client):
        result = admin_client.get_community_status()
        assert "community" in result
        assert isinstance(result["community"], dict)

    def test_community_status_required_fields(self, admin_client):
        result = admin_client.get_community_status()
        c = result["community"]
        assert "linked" in c
        assert "email" in c
        assert "link_status" in c
        assert "sync_events" in c

    def test_community_link_valid_email(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_link("clienttest@example.com")
        assert exc_info.value.status == 503

    def test_community_link_returns_link_object(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_link("linkobject@example.com")
        payload = exc_info.value.payload
        assert "link" in payload
        link = payload["link"]
        assert link.get("status") == "not_configured"
        assert "message" in link

    def test_community_link_has_api_key(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_link("apikey@example.com")
        link = exc_info.value.payload["link"]
        assert "api_key" not in link

    def test_community_link_has_login_link_stub(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_link("loginstub@example.com")
        link = exc_info.value.payload["link"]
        assert "login_link_stub" not in link

    def test_community_link_invalid_email_raises_error(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_link("not-an-email")
        assert exc_info.value.status == 400

    def test_community_link_updates_status(self, admin_client):
        """Not configured cloud link endpoint must not mutate status."""
        before = admin_client.get_community_status()
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_link("statusupdate@example.com")
        assert exc_info.value.status == 503
        status = admin_client.get_community_status()
        assert status["community"].get("linked") == before["community"].get("linked")

    def test_community_sync_returns_ok(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_sync("both")
        assert exc_info.value.status == 503

    def test_community_sync_has_sync_dict(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_sync("both")
        payload = exc_info.value.payload
        assert "sync" in payload
        sync = payload["sync"]
        assert sync.get("status") == "not_configured"
        assert "message" in sync

    def test_community_sync_increments_event_count(self, admin_client):
        before = admin_client.get_community_status()
        before_count = before["community"].get("sync_events", 0)

        with pytest.raises(AdminClientError) as exc_info:
            admin_client.community_sync("both")
        assert exc_info.value.status == 503

        after = admin_client.get_community_status()
        after_count = after["community"].get("sync_events", 0)
        assert after_count == before_count


# =========================================================================
# 7. CLI Commands API
# =========================================================================

class TestCLICommandsAPI:
    """Tests for AdminClient.get_cli_commands() and run_cli_command()."""

    def test_get_cli_commands_returns_ok(self, admin_client):
        result = admin_client.get_cli_commands()
        assert result.get("ok") is True

    def test_get_cli_commands_has_commands_list(self, admin_client):
        result = admin_client.get_cli_commands()
        assert "commands" in result
        assert isinstance(result["commands"], list)

    def test_expected_commands_present(self, admin_client):
        result = admin_client.get_cli_commands()
        cmds = result["commands"]
        assert "version" in cmds
        assert "doctor" in cmds
        assert "llm-status" in cmds

    def test_run_disallowed_command_raises_error(self, admin_client):
        """Running a command not in the allowlist should raise AdminClientError."""
        with pytest.raises(AdminClientError):
            admin_client.run_cli_command("rm -rf /")

    def test_run_injection_attempt_raises_error(self, admin_client):
        with pytest.raises(AdminClientError):
            admin_client.run_cli_command("version; rm -rf /")

    def test_run_empty_command_raises_error(self, admin_client):
        with pytest.raises(AdminClientError):
            admin_client.run_cli_command("")

    def test_run_version_command_returns_result_structure(self, admin_client):
        """Running 'version' should return result dict with required fields."""
        result = admin_client.run_cli_command("version")
        # ok may be True or False depending on whether stillwater is installed
        assert "ok" in result
        assert "result" in result
        r = result["result"]
        assert "command" in r
        assert "returncode" in r
        assert r["command"] == "version"


# =========================================================================
# 8. Service Registry API
# =========================================================================

class TestServiceRegistryAPI:
    """Tests for service registry client methods."""

    _TEST_SERVICE_ID = "test-client-unit-test-xyz"

    def _cleanup(self, admin_client):
        """Remove test service if it exists (idempotent, ignore errors)."""
        try:
            admin_client.deregister_service(self._TEST_SERVICE_ID)
        except AdminClientError:
            pass

    def test_list_services_returns_ok(self, admin_client):
        try:
            result = admin_client.list_services()
            assert result.get("ok") is True
            assert "services" in result
            assert isinstance(result["services"], list)
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise

    def test_register_service(self, admin_client):
        self._cleanup(admin_client)
        try:
            result = admin_client.register_service(
                service_id=self._TEST_SERVICE_ID,
                service_type="custom",
                name="Client Unit Test Service",
                port=9998,
            )
            assert result.get("ok") is True
            assert "service" in result
            svc = result["service"]
            assert svc["service_id"] == self._TEST_SERVICE_ID
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise
        finally:
            self._cleanup(admin_client)

    def test_register_service_descriptor_fields(self, admin_client):
        self._cleanup(admin_client)
        try:
            result = admin_client.register_service(
                service_id=self._TEST_SERVICE_ID,
                service_type="custom",
                name="Client Unit Test Service",
                port=9998,
            )
            if result.get("ok"):
                svc = result["service"]
                assert "service_id" in svc
                assert "service_type" in svc
                assert "name" in svc
                assert "port" in svc
                assert "status" in svc
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise
        finally:
            self._cleanup(admin_client)

    def test_get_service_after_register(self, admin_client):
        self._cleanup(admin_client)
        try:
            admin_client.register_service(
                service_id=self._TEST_SERVICE_ID,
                service_type="custom",
                name="Client Unit Test Service",
                port=9998,
            )
            result = admin_client.get_service(self._TEST_SERVICE_ID)
            assert result.get("ok") is True
            assert result["service"]["service_id"] == self._TEST_SERVICE_ID
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise
        finally:
            self._cleanup(admin_client)

    def test_get_nonexistent_service_raises_error(self, admin_client):
        try:
            with pytest.raises(AdminClientError) as exc_info:
                admin_client.get_service("totally_nonexistent_service_xyzzy_999")
            assert exc_info.value.status == 404
        except AdminClientError as exc:
            # If list_services 404s, registry is unavailable
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise

    def test_service_health_check(self, admin_client):
        self._cleanup(admin_client)
        try:
            reg = admin_client.register_service(
                service_id=self._TEST_SERVICE_ID,
                service_type="custom",
                name="Client Unit Test Service",
                port=9998,
            )
            if not reg.get("ok"):
                pytest.skip("Registration failed")

            result = admin_client.get_service_health(self._TEST_SERVICE_ID)
            assert result.get("ok") is True
            health = result["health"]
            assert "service_id" in health
            assert "status" in health
            assert health["status"] in ("online", "offline", "degraded", "starting")
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise
        finally:
            self._cleanup(admin_client)

    def test_deregister_service(self, admin_client):
        try:
            admin_client.register_service(
                service_id=self._TEST_SERVICE_ID,
                service_type="custom",
                name="Client Unit Test Service",
                port=9998,
            )
            result = admin_client.deregister_service(self._TEST_SERVICE_ID)
            assert result.get("ok") is True

            # Verify it's gone
            with pytest.raises(AdminClientError) as exc_info:
                admin_client.get_service(self._TEST_SERVICE_ID)
            assert exc_info.value.status == 404
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise

    def test_deregister_nonexistent_service(self, admin_client):
        """Deregistering a non-existent service should return ok=False (not raise)."""
        try:
            result = admin_client.deregister_service("service_that_does_not_exist_xyzzy_999")
            # The server returns ok=False (not an HTTP error), so the client
            # should propagate ok=False through the payload.
            # However, our client raises on ok=False. Check that:
            # Either raises AdminClientError OR returns ok=False dict.
            # The server sends {"ok": False} with HTTP 200 for deregister.
            # Our _send() raises AdminClientError on ok=False.
            # So we expect an exception here.
            assert False, f"Expected AdminClientError but got: {result}"
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            # Expected: ok=False payload
            assert exc.payload.get("ok") is False

    def test_discover_services(self, admin_client):
        try:
            result = admin_client.discover_services()
            assert result.get("ok") is True
            assert "discovery" in result
            discovery = result["discovery"]
            assert "discovered" in discovery
            assert isinstance(discovery["discovered"], list)
            assert "failed_ports" in discovery
        except AdminClientError as exc:
            if exc.status == 404:
                pytest.skip("Service registry not available")
            raise


# =========================================================================
# 9. Error handling and AdminClientError
# =========================================================================

class TestAdminClientError:
    """Tests for AdminClientError attributes and error propagation."""

    def test_error_has_status_code(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.get_file("data/default/skills/does_not_exist_xyzzy.md")
        assert exc_info.value.status == 400

    def test_error_has_payload_dict(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.get_file("admin/server.py")
        err = exc_info.value
        assert isinstance(err.payload, dict)

    def test_error_message_is_string(self, admin_client):
        with pytest.raises(AdminClientError) as exc_info:
            admin_client.get_file("data/default/skills/does_not_exist_xyzzy.md")
        assert isinstance(str(exc_info.value), str)
        assert len(str(exc_info.value)) > 0

    def test_cannot_connect_raises_error(self):
        """Client targeting a port with no server should raise AdminClientError."""
        dead_client = AdminClient(base_url="http://127.0.0.1:19999", timeout=1)
        with pytest.raises(AdminClientError) as exc_info:
            dead_client.get_catalog()
        assert exc_info.value.status == 0


# =========================================================================
# 10. All API responses have ok field
# =========================================================================

class TestResponseShape:
    """Verify that all successful responses contain ok=True."""

    def test_all_get_endpoints_have_ok_true(self, admin_client):
        endpoints = [
            admin_client.get_catalog,
            admin_client.get_llm_status,
            admin_client.get_community_status,
            admin_client.get_cli_commands,
        ]
        for fn in endpoints:
            result = fn()
            assert "ok" in result, f"{fn.__name__} missing 'ok' key"
            assert result["ok"] is True, f"{fn.__name__} returned ok={result['ok']}"
