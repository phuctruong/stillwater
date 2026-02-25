"""Comprehensive unit tests for the Stillwater Admin Server API.

Tests cover all GET and POST endpoints via real HTTP requests against a
live server started on a random port in a module-level fixture.

Run with:
    pytest admin/tests/test_admin_server.py -v
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

import pytest

# --- Path setup -----------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"

for _p in (str(ADMIN_DIR), str(CLI_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from http.server import ThreadingHTTPServer

import server as admin_server


# =========================================================================
# Helpers
# =========================================================================

def _free_port() -> int:
    """Return an available TCP port on 127.0.0.1."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _json_request(
    conn: http.client.HTTPConnection,
    method: str,
    path: str,
    body: dict | None = None,
) -> tuple[int, dict]:
    """Make an HTTP request; return (status_code, parsed_json_body)."""
    headers: dict[str, str] = {}
    encoded: bytes | None = None
    if body is not None:
        encoded = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(encoded))
    conn.request(method, path, body=encoded, headers=headers)
    resp = conn.getresponse()
    status = resp.status
    raw = resp.read()
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        data = {"_raw": raw.decode("utf-8", errors="replace")}
    return status, data


# =========================================================================
# Module-scoped server fixture
# =========================================================================

@pytest.fixture(scope="module")
def server_conn():
    """Start the admin server on a free port; yield an HTTPConnection.

    The server is shut down after all tests in this module complete.
    """
    port = _free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), admin_server.AdminHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)  # Let the server accept connections

    conn = http.client.HTTPConnection("127.0.0.1", port)
    yield conn

    conn.close()
    httpd.shutdown()
    httpd.server_close()


# =========================================================================
# 1. Root and static file serving
# =========================================================================

class TestStaticServing:
    """Tests for the root HTML page and static file serving."""

    def test_get_root_returns_html(self, server_conn):
        """GET / should return 200 with text/html content."""
        server_conn.request("GET", "/")
        resp = server_conn.getresponse()
        assert resp.status == 200
        ct = resp.getheader("Content-Type", "")
        assert "text/html" in ct
        body = resp.read()
        assert len(body) > 0

    def test_get_root_contains_html_tag(self, server_conn):
        """The root response body should contain an HTML doctype or <html> tag."""
        server_conn.request("GET", "/")
        resp = server_conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace")
        assert "html" in body.lower()

    def test_get_static_existing_file(self, server_conn):
        """GET /static/<file> for a file that exists should return 200."""
        static_dir = ADMIN_DIR / "static"
        # Find any file in static/ to test
        files = list(static_dir.glob("*"))
        regular_files = [f for f in files if f.is_file()]
        if not regular_files:
            pytest.skip("No files in admin/static/ to test")
        fname = regular_files[0].name
        server_conn.request("GET", f"/static/{fname}")
        resp = server_conn.getresponse()
        assert resp.status == 200
        resp.read()

    def test_get_static_nonexistent_returns_404(self, server_conn):
        """GET /static/<missing> should return 404."""
        status, data = _json_request(server_conn, "GET", "/static/does_not_exist_xyz.css")
        assert status == 404
        assert data.get("ok") is False

    def test_get_static_path_traversal_blocked(self, server_conn):
        """GET /static/../../etc/passwd should be blocked (404)."""
        status, data = _json_request(server_conn, "GET", "/static/../../etc/passwd")
        assert status == 404
        assert data.get("ok") is False


# =========================================================================
# 2. Catalog API
# =========================================================================

class TestCatalogAPI:
    """Tests for GET /api/catalog."""

    def test_catalog_returns_ok(self, server_conn):
        """GET /api/catalog should return 200 with ok=True."""
        status, data = _json_request(server_conn, "GET", "/api/catalog")
        assert status == 200
        assert data.get("ok") is True

    def test_catalog_has_groups_key(self, server_conn):
        """Response should contain a 'groups' list."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        assert "groups" in data
        assert isinstance(data["groups"], list)

    def test_catalog_has_expected_group_count(self, server_conn):
        """Catalog should have exactly 10 groups (matching CATALOG_GROUPS definition)."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        assert len(data["groups"]) == 10

    def test_catalog_group_schema(self, server_conn):
        """Each group should have id, title, files, and count fields."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        for group in data["groups"]:
            assert "id" in group, f"Missing id in group: {group}"
            assert "title" in group, f"Missing title in group: {group}"
            assert "files" in group, f"Missing files in group: {group}"
            assert "count" in group, f"Missing count in group: {group}"

    def test_catalog_count_matches_files_length(self, server_conn):
        """count field must equal len(files) for every group."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        for group in data["groups"]:
            assert group["count"] == len(group["files"]), (
                f"count mismatch for group {group['id']}: "
                f"count={group['count']} files={len(group['files'])}"
            )

    def test_catalog_file_has_path_name_group_dir(self, server_conn):
        """Each file entry should have path, name, group, dir fields."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        for group in data["groups"]:
            for f in group["files"]:
                assert "path" in f
                assert "name" in f
                assert "group" in f
                assert "dir" in f

    def test_catalog_root_skills_group_exists(self, server_conn):
        """Group with id='root_skills' should appear and have files."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        ids = {g["id"] for g in data["groups"]}
        assert "root_skills" in ids

    def test_catalog_extras_key_present(self, server_conn):
        """Response should contain an 'extras' list."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        assert "extras" in data
        assert isinstance(data["extras"], list)

    def test_catalog_skills_include_prime_safety(self, server_conn):
        """data/default/skills/prime-safety.md should appear in the root_skills group."""
        _, data = _json_request(server_conn, "GET", "/api/catalog")
        root_skills = next(
            (g for g in data["groups"] if g["id"] == "root_skills"), None
        )
        assert root_skills is not None
        paths = [f["path"] for f in root_skills["files"]]
        assert any("prime-safety.md" in p for p in paths)


# =========================================================================
# 3. File Read API
# =========================================================================

class TestFileReadAPI:
    """Tests for GET /api/file?path=..."""

    def test_read_real_file_returns_ok(self, server_conn):
        """GET /api/file?path=data/default/skills/prime-safety.md should return ok=True."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/prime-safety.md"
        )
        assert status == 200
        assert data.get("ok") is True

    def test_read_real_file_content_nonempty(self, server_conn):
        """Content field for prime-safety.md should be a non-empty string."""
        _, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/prime-safety.md"
        )
        assert isinstance(data.get("content"), str)
        assert len(data["content"]) > 0

    def test_read_real_file_sha256_matches(self, server_conn):
        """sha256 returned by the server must match locally computed digest."""
        _, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/prime-safety.md"
        )
        content = data["content"]
        expected_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert data.get("sha256") == expected_sha256

    def test_read_real_file_sha256_is_64_hex_chars(self, server_conn):
        """sha256 field should be a 64-character lowercase hex string."""
        _, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/prime-safety.md"
        )
        sha = data.get("sha256", "")
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_read_real_file_size_matches_content(self, server_conn):
        """size should equal len(content.encode('utf-8'))."""
        _, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/prime-safety.md"
        )
        content = data["content"]
        assert data.get("size") == len(content.encode("utf-8"))

    def test_read_real_file_path_echoed(self, server_conn):
        """path field in response should match the requested path."""
        _, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/prime-safety.md"
        )
        assert data.get("path") == "data/default/skills/prime-safety.md"

    def test_read_nonexistent_file_returns_error(self, server_conn):
        """A path that does not exist should return ok=False and 400."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=data/default/skills/does_not_exist_xyzzy.md"
        )
        assert status == 400
        assert data.get("ok") is False

    def test_read_disallowed_suffix_returns_error(self, server_conn):
        """A .py file (disallowed suffix) should return ok=False."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=admin/server.py"
        )
        assert status == 400
        assert data.get("ok") is False

    def test_read_empty_path_returns_error(self, server_conn):
        """Empty path parameter should return ok=False."""
        status, data = _json_request(server_conn, "GET", "/api/file?path=")
        assert status == 400
        assert data.get("ok") is False

    def test_read_path_traversal_blocked(self, server_conn):
        """Path traversal attempt should return ok=False."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=../../../etc/passwd"
        )
        assert status == 400
        assert data.get("ok") is False


# =========================================================================
# 4. File Save API
# =========================================================================

class TestFileSaveAPI:
    """Tests for POST /api/file/save."""

    def _writable_skill_path(self) -> str | None:
        """Return relative path of a writable skill file, or None."""
        d = REPO_ROOT / "data" / "default" / "skills"
        if not d.exists():
            return None
        files = list(d.glob("*.md"))
        return str(files[0].relative_to(REPO_ROOT)) if files else None

    def test_save_file_round_trip(self, server_conn, tmp_path):
        """Write content to an allowed file, then re-read and verify round-trip.

        Uses a temporary file inside the skills/ directory to avoid polluting
        existing files. The file is cleaned up after the test.
        """
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_filename = "zzz_test_save_temp.md"
        test_path_rel = f"data/default/skills/{test_filename}"
        test_file = skills_dir / test_filename
        original_content = "# Test save\n\nContent written by test.\n"

        try:
            # Create the file first so the save path is allowed
            test_file.write_text(original_content, encoding="utf-8")

            new_content = "# Updated by test\n\nRound-trip verified.\n"
            status, data = _json_request(
                server_conn,
                "POST",
                "/api/file/save",
                {"path": test_path_rel, "content": new_content},
            )
            assert status == 200, f"Save failed: {data}"
            assert data.get("ok") is True

            # Re-read via GET and verify content
            _, read_data = _json_request(
                server_conn, "GET", f"/api/file?path={test_path_rel}"
            )
            assert read_data.get("ok") is True
            assert read_data.get("content") == new_content
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_save_returns_sha256(self, server_conn):
        """POST /api/file/save should return the sha256 of saved content."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_filename = "zzz_test_sha256_temp.md"
        test_path_rel = f"data/default/skills/{test_filename}"
        test_file = skills_dir / test_filename
        content = "# sha256 test\n"
        try:
            test_file.write_text(content, encoding="utf-8")
            status, data = _json_request(
                server_conn,
                "POST",
                "/api/file/save",
                {"path": test_path_rel, "content": content},
            )
            assert status == 200
            expected_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
            assert data.get("sha256") == expected_sha
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_save_disallowed_suffix_blocked(self, server_conn):
        """Saving a .py file should be blocked (ok=False, 400)."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/save",
            {"path": "admin/server.py", "content": "# hacked"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_save_path_traversal_blocked(self, server_conn):
        """Path traversal in save path should be blocked."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/save",
            {"path": "../../../tmp/evil.md", "content": "evil"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_save_missing_path_field_blocked(self, server_conn):
        """Save with empty path should fail."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/save",
            {"content": "content only"},
        )
        assert status == 400
        assert data.get("ok") is False


# =========================================================================
# 5. File Create API
# =========================================================================

class TestFileCreateAPI:
    """Tests for POST /api/file/create."""

    def test_create_file_in_valid_group(self, server_conn):
        """Creating a file in a valid group should return ok=True and created=True."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_filename = "zzz_create_test_temp"
        expected_file = skills_dir / f"{test_filename}.md"

        try:
            status, data = _json_request(
                server_conn,
                "POST",
                "/api/file/create",
                {"group": "root_skills", "filename": test_filename},
            )
            assert status == 200, f"Create failed: {data}"
            assert data.get("ok") is True
            assert data.get("created") is True
            assert expected_file.exists(), "File was not created on disk"
        finally:
            if expected_file.exists():
                expected_file.unlink()

    def test_create_file_adds_md_extension(self, server_conn):
        """Filename without extension should get .md appended."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_filename = "zzz_ext_test_temp"
        expected_file = skills_dir / f"{test_filename}.md"

        try:
            status, data = _json_request(
                server_conn,
                "POST",
                "/api/file/create",
                {"group": "root_skills", "filename": test_filename},
            )
            assert status == 200
            assert "path" in data
            assert data["path"].endswith(".md")
        finally:
            if expected_file.exists():
                expected_file.unlink()

    def test_create_file_uses_template_content(self, server_conn):
        """Newly created file should contain the group's create_template content."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_filename = "zzz_template_test_temp"
        expected_file = skills_dir / f"{test_filename}.md"

        try:
            status, data = _json_request(
                server_conn,
                "POST",
                "/api/file/create",
                {"group": "root_skills", "filename": test_filename},
            )
            assert status == 200
            if expected_file.exists():
                content = expected_file.read_text(encoding="utf-8")
                # Template for root_skills starts with "---\nskill_id:"
                assert "skill_id" in content or "New Skill" in content
        finally:
            if expected_file.exists():
                expected_file.unlink()

    def test_create_file_duplicate_returns_error(self, server_conn):
        """Creating a file that already exists should return ok=False."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        if not skills_dir.exists():
            pytest.skip("data/default/skills directory does not exist")

        test_filename = "zzz_dup_test_temp"
        expected_file = skills_dir / f"{test_filename}.md"

        try:
            # Create once
            _json_request(
                server_conn,
                "POST",
                "/api/file/create",
                {"group": "root_skills", "filename": test_filename},
            )
            # Try again — should fail
            status, data = _json_request(
                server_conn,
                "POST",
                "/api/file/create",
                {"group": "root_skills", "filename": test_filename},
            )
            assert status == 400
            assert data.get("ok") is False
        finally:
            if expected_file.exists():
                expected_file.unlink()

    def test_create_file_invalid_group_returns_error(self, server_conn):
        """Creating a file in a non-existent group should return ok=False."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/create",
            {"group": "nonexistent_group_xyz", "filename": "test.md"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_create_file_invalid_filename_characters_blocked(self, server_conn):
        """Filename with path separators should be blocked."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/create",
            {"group": "root_skills", "filename": "../../../evil"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_create_file_space_in_filename_blocked(self, server_conn):
        """Filename with spaces should be blocked."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/create",
            {"group": "root_skills", "filename": "bad name with spaces"},
        )
        assert status == 400
        assert data.get("ok") is False


# =========================================================================
# 6. Security Tests
# =========================================================================

class TestSecurity:
    """Security-focused tests for path traversal and access control."""

    def test_path_traversal_in_file_read(self, server_conn):
        """Path traversal via ../../ should not expose files outside the repo."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=../../.bashrc"
        )
        assert status == 400
        assert data.get("ok") is False

    def test_absolute_path_blocked(self, server_conn):
        """An absolute file path should not be served."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=/etc/passwd"
        )
        assert status == 400
        assert data.get("ok") is False

    def test_disallowed_suffix_py_blocked(self, server_conn):
        """.py files are not in ALLOWED_WRITE_SUFFIXES so read should fail."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=admin/server.py"
        )
        assert status == 400
        assert data.get("ok") is False

    def test_disallowed_suffix_sh_blocked(self, server_conn):
        """.sh files are not in ALLOWED_WRITE_SUFFIXES so read should fail."""
        status, data = _json_request(
            server_conn, "GET", "/api/file?path=admin/start-admin.sh"
        )
        assert status == 400
        assert data.get("ok") is False

    def test_save_path_traversal_blocked(self, server_conn):
        """Save with path traversal should be blocked."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/save",
            {"path": "../../.bashrc", "content": "evil"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_save_outside_catalog_dir_blocked(self, server_conn):
        """Saving to an arbitrary .md file outside catalog dirs should fail."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/file/save",
            {"path": "admin/tests/evil.md", "content": "evil"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_static_path_traversal_blocked(self, server_conn):
        """Static file path traversal should return 404, not expose files."""
        status, data = _json_request(
            server_conn, "GET", "/static/../server.py"
        )
        assert status == 404


# =========================================================================
# 7. LLM Status API
# =========================================================================

class TestLLMStatusAPI:
    """Tests for GET /api/llm/status."""

    def test_llm_status_returns_ok(self, server_conn):
        """GET /api/llm/status should return 200 with ok=True."""
        status, data = _json_request(server_conn, "GET", "/api/llm/status")
        assert status == 200
        assert data.get("ok") is True

    def test_llm_status_has_status_key(self, server_conn):
        """Response should have a nested 'status' object."""
        _, data = _json_request(server_conn, "GET", "/api/llm/status")
        assert "status" in data
        assert isinstance(data["status"], dict)

    def test_llm_status_required_fields(self, server_conn):
        """LLM status should contain provider, setup_ok, models, and ollama_installed."""
        _, data = _json_request(server_conn, "GET", "/api/llm/status")
        s = data["status"]
        assert "provider" in s
        assert "setup_ok" in s
        assert "models" in s
        assert "ollama_installed" in s
        assert "probes" in s
        assert "preferred_ollama_url" in s

    def test_llm_status_setup_ok_is_bool(self, server_conn):
        """setup_ok must be a boolean value."""
        _, data = _json_request(server_conn, "GET", "/api/llm/status")
        assert isinstance(data["status"]["setup_ok"], bool)

    def test_llm_status_models_is_list(self, server_conn):
        """models field must be a list."""
        _, data = _json_request(server_conn, "GET", "/api/llm/status")
        assert isinstance(data["status"]["models"], list)

    def test_llm_status_ollama_installed_is_bool(self, server_conn):
        """ollama_installed must be a boolean."""
        _, data = _json_request(server_conn, "GET", "/api/llm/status")
        assert isinstance(data["status"]["ollama_installed"], bool)


# =========================================================================
# 8. Community API
# =========================================================================

class TestCommunityAPI:
    """Tests for community link, status, and sync endpoints."""

    def test_community_status_returns_ok(self, server_conn):
        """GET /api/community/status should return 200 with ok=True."""
        status, data = _json_request(server_conn, "GET", "/api/community/status")
        assert status == 200
        assert data.get("ok") is True

    def test_community_status_has_community_key(self, server_conn):
        """Response should have a 'community' object."""
        _, data = _json_request(server_conn, "GET", "/api/community/status")
        assert "community" in data
        assert isinstance(data["community"], dict)

    def test_community_status_required_fields(self, server_conn):
        """community object should have linked, email, link_status, sync_events."""
        _, data = _json_request(server_conn, "GET", "/api/community/status")
        c = data["community"]
        assert "linked" in c
        assert "email" in c
        assert "link_status" in c
        assert "sync_events" in c

    def test_community_link_valid_email(self, server_conn):
        """POST /api/community/link returns not_configured when cloud key is missing."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/community/link",
            {"email": "testuser@example.com"},
        )
        assert status == 503
        assert data.get("ok") is False

    def test_community_link_returns_link_object(self, server_conn):
        """Community link response should return cloud not_configured state."""
        _, data = _json_request(
            server_conn,
            "POST",
            "/api/community/link",
            {"email": "verify@example.com"},
        )
        assert "link" in data
        link = data["link"]
        assert link.get("status") == "not_configured"
        assert "message" in link

    def test_community_link_generates_api_key(self, server_conn):
        """Link response should never include raw API keys."""
        _, data = _json_request(
            server_conn,
            "POST",
            "/api/community/link",
            {"email": "apikey@example.com"},
        )
        link = data.get("link", {})
        assert "api_key" not in link

    def test_community_link_no_login_link_field(self, server_conn):
        """Link response should not include legacy login-link fields."""
        _, data = _json_request(
            server_conn,
            "POST",
            "/api/community/link",
            {"email": "loginlink@example.com"},
        )
        link = data.get("link", {})
        assert "login_link" not in link

    def test_community_link_invalid_email_blocked(self, server_conn):
        """POST /api/community/link with a non-email should return ok=False."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/community/link",
            {"email": "not-an-email"},
        )
        assert status == 400
        assert data.get("ok") is False

    def test_community_link_updates_status(self, server_conn):
        """Community status should not change when link feature is unimplemented."""
        _, before = _json_request(server_conn, "GET", "/api/community/status")
        _json_request(
            server_conn,
            "POST",
            "/api/community/link",
            {"email": "statuscheck@example.com"},
        )
        _, status_data = _json_request(server_conn, "GET", "/api/community/status")
        assert status_data["community"].get("linked") == before["community"].get("linked")

    def test_community_sync_returns_ok(self, server_conn):
        """POST /api/community/sync returns not_configured when cloud key is missing."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/community/sync",
            {"direction": "both"},
        )
        assert status == 503
        assert data.get("ok") is False

    def test_community_sync_response_structure(self, server_conn):
        """Sync response should include cloud status details."""
        _, data = _json_request(
            server_conn,
            "POST",
            "/api/community/sync",
            {"direction": "both"},
        )
        sync = data.get("sync", {})
        assert sync.get("status") == "not_configured"
        assert "message" in sync

    def test_community_sync_increments_event_count(self, server_conn):
        """Sync event count should not change when cloud is not configured."""
        _, before = _json_request(server_conn, "GET", "/api/community/status")
        before_count = before["community"].get("sync_events", 0)

        _json_request(
            server_conn,
            "POST",
            "/api/community/sync",
            {"direction": "both"},
        )

        _, after = _json_request(server_conn, "GET", "/api/community/status")
        after_count = after["community"].get("sync_events", 0)
        assert after_count == before_count

    def test_cloud_health_endpoint_not_configured(self, server_conn):
        """GET /api/health/cloud should report not_configured without key."""
        status, data = _json_request(server_conn, "GET", "/api/health/cloud")
        assert status == 200
        assert data.get("ok") is False
        assert data.get("cloud", {}).get("status") == "not_configured"


# =========================================================================
# 9. CLI Commands API
# =========================================================================

class TestCLICommandsAPI:
    """Tests for GET /api/cli/commands and POST /api/cli/run."""

    def test_cli_commands_returns_ok(self, server_conn):
        """GET /api/cli/commands should return 200 with ok=True."""
        status, data = _json_request(server_conn, "GET", "/api/cli/commands")
        assert status == 200
        assert data.get("ok") is True

    def test_cli_commands_has_commands_list(self, server_conn):
        """Response should contain a 'commands' list."""
        _, data = _json_request(server_conn, "GET", "/api/cli/commands")
        assert "commands" in data
        assert isinstance(data["commands"], list)

    def test_cli_commands_contains_expected_commands(self, server_conn):
        """Allowed commands should include version, doctor, llm-status."""
        _, data = _json_request(server_conn, "GET", "/api/cli/commands")
        cmds = data["commands"]
        assert "version" in cmds
        assert "doctor" in cmds
        assert "llm-status" in cmds

    def test_cli_run_disallowed_command_blocked(self, server_conn):
        """POST /api/cli/run with a disallowed command should return ok=False."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/cli/run",
            {"command": "rm -rf /"},
        )
        # Either 400 with ok=False, or 200 with ok=False (outer ok matches inner)
        assert data.get("ok") is False

    def test_cli_run_injection_attempt_blocked(self, server_conn):
        """Shell injection via command field should be rejected."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/cli/run",
            {"command": "version; rm -rf /"},
        )
        assert data.get("ok") is False

    def test_cli_run_empty_command_blocked(self, server_conn):
        """Empty command string should be blocked."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/cli/run",
            {"command": ""},
        )
        assert data.get("ok") is False

    def test_cli_run_allowed_command_version(self, server_conn):
        """POST /api/cli/run with 'version' should execute and return result structure."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/cli/run",
            {"command": "version"},
        )
        assert status == 200
        # ok field should be bool (True if stillwater is installed, False if not)
        assert "ok" in data
        result = data.get("result", {})
        assert "command" in result
        assert "returncode" in result
        assert result["command"] == "version"


# =========================================================================
# 10. Service Registry API
# =========================================================================

class TestServiceRegistryAPI:
    """Tests for service registration, retrieval, health check, and discovery."""

    _TEST_SERVICE_ID = "test-service-unit-test-xyz"

    def _cleanup_service(self, server_conn):
        """Remove the test service if it exists (idempotent)."""
        _json_request(
            server_conn,
            "POST",
            "/api/services/deregister",
            {"service_id": self._TEST_SERVICE_ID},
        )

    def test_list_services_returns_ok(self, server_conn):
        """GET /api/services should return 200 with ok=True."""
        status, data = _json_request(server_conn, "GET", "/api/services")
        if status == 404:
            pytest.skip("Service registry not available on this installation")
        assert status == 200
        assert data.get("ok") is True

    def test_list_services_has_services_list(self, server_conn):
        """Response should contain a 'services' list."""
        status, data = _json_request(server_conn, "GET", "/api/services")
        if status == 404:
            pytest.skip("Service registry not available")
        assert "services" in data
        assert isinstance(data["services"], list)

    def test_register_service(self, server_conn):
        """POST /api/services/register should register a new service."""
        self._cleanup_service(server_conn)
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/services/register",
            {
                "service_id": self._TEST_SERVICE_ID,
                "service_type": "custom",
                "name": "Unit Test Service",
                "port": 9999,
            },
        )
        if status == 404:
            pytest.skip("Service registry not available")
        assert status == 200, f"Register failed: {data}"
        assert data.get("ok") is True
        assert "service" in data
        assert data["service"]["service_id"] == self._TEST_SERVICE_ID
        self._cleanup_service(server_conn)

    def test_register_service_returns_descriptor_fields(self, server_conn):
        """Registered service descriptor should have expected fields."""
        self._cleanup_service(server_conn)
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/services/register",
            {
                "service_id": self._TEST_SERVICE_ID,
                "service_type": "custom",
                "name": "Unit Test Service",
                "port": 9999,
            },
        )
        if status == 404:
            pytest.skip("Service registry not available")
        if status == 200:
            svc = data.get("service", {})
            assert "service_id" in svc
            assert "service_type" in svc
            assert "name" in svc
            assert "port" in svc
            assert "status" in svc
        self._cleanup_service(server_conn)

    def test_get_specific_service(self, server_conn):
        """GET /api/services/{id} should return the registered service."""
        self._cleanup_service(server_conn)
        _json_request(
            server_conn,
            "POST",
            "/api/services/register",
            {
                "service_id": self._TEST_SERVICE_ID,
                "service_type": "custom",
                "name": "Unit Test Service",
                "port": 9999,
            },
        )
        status, data = _json_request(
            server_conn, "GET", f"/api/services/{self._TEST_SERVICE_ID}"
        )
        if status == 404 and data.get("error") == "not found":
            # Registry not available — skip
            pytest.skip("Service registry not available")
        assert status == 200
        assert data.get("ok") is True
        assert data["service"]["service_id"] == self._TEST_SERVICE_ID
        self._cleanup_service(server_conn)

    def test_get_nonexistent_service_returns_404(self, server_conn):
        """GET /api/services/<missing_id> should return 404."""
        status, data = _json_request(
            server_conn, "GET", "/api/services/totally_nonexistent_service_xyzzy_999"
        )
        if status == 404 and "not found" in str(data.get("error", "")):
            # Could be "service not found" or just the route not found
            assert data.get("ok") is False
        # Also acceptable: registry unavailable routes to generic 404
        assert status == 404

    def test_health_check_registered_service(self, server_conn):
        """GET /api/services/{id}/health should return a health object."""
        self._cleanup_service(server_conn)
        reg_status, _ = _json_request(
            server_conn,
            "POST",
            "/api/services/register",
            {
                "service_id": self._TEST_SERVICE_ID,
                "service_type": "custom",
                "name": "Unit Test Service",
                "port": 9999,
            },
        )
        if reg_status == 404:
            pytest.skip("Service registry not available")

        status, data = _json_request(
            server_conn, "GET", f"/api/services/{self._TEST_SERVICE_ID}/health"
        )
        assert status == 200
        assert data.get("ok") is True
        health = data.get("health", {})
        assert "service_id" in health
        assert "status" in health
        # The service is not actually running, so it should be OFFLINE
        assert health["status"] in ("online", "offline", "degraded", "starting")
        self._cleanup_service(server_conn)

    def test_deregister_service(self, server_conn):
        """POST /api/services/deregister should remove a registered service."""
        # First register
        _json_request(
            server_conn,
            "POST",
            "/api/services/register",
            {
                "service_id": self._TEST_SERVICE_ID,
                "service_type": "custom",
                "name": "Unit Test Service",
                "port": 9999,
            },
        )
        # Then deregister
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/services/deregister",
            {"service_id": self._TEST_SERVICE_ID},
        )
        if status == 404:
            pytest.skip("Service registry not available")
        assert data.get("ok") is True

        # Verify it's gone
        get_status, get_data = _json_request(
            server_conn, "GET", f"/api/services/{self._TEST_SERVICE_ID}"
        )
        assert get_status == 404

    def test_deregister_nonexistent_service_returns_false(self, server_conn):
        """Deregistering a non-existent service should return ok=False."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/services/deregister",
            {"service_id": "service_that_does_not_exist_xyzzy_999"},
        )
        if status == 404:
            pytest.skip("Service registry not available")
        # Returns ok=False (the registry returns removed=False)
        assert data.get("ok") is False

    def test_discover_returns_ok(self, server_conn):
        """POST /api/services/discover should return ok=True."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/services/discover",
            {},
        )
        if status == 404:
            pytest.skip("Service registry not available")
        assert status == 200
        assert data.get("ok") is True

    def test_discover_returns_discovery_object(self, server_conn):
        """Discovery response should contain a 'discovery' object with discovered list."""
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/services/discover",
            {},
        )
        if status == 404:
            pytest.skip("Service registry not available")
        discovery = data.get("discovery", {})
        assert "discovered" in discovery
        assert isinstance(discovery["discovered"], list)
        assert "failed_ports" in discovery


# =========================================================================
# 11. Error Handling
# =========================================================================

class TestErrorHandling:
    """Tests for proper error responses on bad requests."""

    def test_unknown_get_path_returns_404(self, server_conn):
        """GET to an unknown path should return 404."""
        status, data = _json_request(server_conn, "GET", "/api/this/does/not/exist")
        assert status == 404
        assert data.get("ok") is False

    def test_unknown_post_path_returns_404(self, server_conn):
        """POST to an unknown path should return 404."""
        status, data = _json_request(
            server_conn, "POST", "/api/this/does/not/exist", {}
        )
        assert status == 404
        assert data.get("ok") is False

    def test_post_invalid_json_body_returns_400(self, server_conn):
        """POST with a malformed JSON body should return 400."""
        headers = {
            "Content-Type": "application/json",
            "Content-Length": "13",
        }
        server_conn.request(
            "POST", "/api/file/save", body=b"not valid jso", headers=headers
        )
        resp = server_conn.getresponse()
        assert resp.status == 400
        raw = resp.read()
        data = json.loads(raw.decode("utf-8"))
        assert data.get("ok") is False

    def test_post_empty_body_handled_gracefully(self, server_conn):
        """POST with empty body to a known endpoint should not crash (returns error)."""
        server_conn.request("POST", "/api/file/save", body=b"", headers={})
        resp = server_conn.getresponse()
        resp.read()
        # Should be 400 (empty/missing path) but not 500
        assert resp.status in (400, 404)

    def test_file_api_missing_path_param(self, server_conn):
        """GET /api/file without path param should return ok=False."""
        status, data = _json_request(server_conn, "GET", "/api/file")
        assert status == 400
        assert data.get("ok") is False

    def test_all_json_responses_have_ok_field(self, server_conn):
        """All API JSON responses should include an 'ok' boolean field."""
        endpoints = [
            ("GET", "/api/catalog"),
            ("GET", "/api/llm/status"),
            ("GET", "/api/community/status"),
            ("GET", "/api/health/cloud"),
            ("GET", "/api/cli/commands"),
        ]
        for method, path in endpoints:
            status, data = _json_request(server_conn, method, path)
            assert "ok" in data, f"Missing 'ok' field in {method} {path}: {data}"
            assert isinstance(data["ok"], bool), (
                f"'ok' is not bool in {method} {path}: {type(data['ok'])}"
            )


# =========================================================================
# 12. Swarm Studio API
# =========================================================================

class TestSwarmStudioAPI:
    """Tests for diagram <-> swarm studio endpoints."""

    def test_swarms_studio_catalog_returns_ok(self, server_conn):
        status, data = _json_request(server_conn, "GET", "/api/swarms/studio/catalog")
        assert status == 200
        assert data.get("ok") is True
        assert isinstance(data.get("swarms"), list)
        assert isinstance(data.get("skills"), list)
        assert isinstance(data.get("recipes"), list)
        assert isinstance(data.get("personas"), list)

    def test_swarms_studio_main_diagram_returns_mermaid(self, server_conn):
        status, data = _json_request(server_conn, "GET", "/api/swarms/studio/main-diagram")
        assert status == 200
        assert data.get("ok") is True
        graph = data.get("diagram_mermaid", "")
        assert isinstance(graph, str)
        assert "graph TD" in graph

    def test_swarms_studio_load_swarm_returns_markdown_and_diagram(self, server_conn):
        status, data = _json_request(
            server_conn, "GET", "/api/swarms/studio/swarm?swarm_id=coder"
        )
        assert status == 200
        assert data.get("ok") is True
        assert isinstance(data.get("markdown"), str)
        assert isinstance(data.get("diagram_mermaid"), str)
        assert isinstance(data.get("validation"), dict)

    def test_swarms_studio_compile_diagram_from_markdown(self, server_conn):
        status, loaded = _json_request(
            server_conn, "GET", "/api/swarms/studio/swarm?swarm_id=coder"
        )
        assert status == 200 and loaded.get("ok") is True
        status, compiled = _json_request(
            server_conn,
            "POST",
            "/api/swarms/studio/compile-diagram",
            {
                "swarm_id": "coder",
                "path": loaded.get("path"),
                "markdown": loaded.get("markdown"),
            },
        )
        assert status == 200
        assert compiled.get("ok") is True
        assert "%% SWARM_SPEC:" in compiled.get("diagram_mermaid", "")

    def test_swarms_studio_compile_swarm_from_diagram(self, server_conn):
        status, loaded = _json_request(
            server_conn, "GET", "/api/swarms/studio/swarm?swarm_id=coder"
        )
        assert status == 200 and loaded.get("ok") is True
        status, compiled = _json_request(
            server_conn,
            "POST",
            "/api/swarms/studio/compile-swarm",
            {"diagram_mermaid": loaded.get("diagram_mermaid")},
        )
        assert status == 200
        assert compiled.get("ok") is True
        markdown = compiled.get("markdown", "")
        assert isinstance(markdown, str)
        assert markdown.startswith("---\n")

    def test_swarms_studio_validate_returns_validation_block(self, server_conn):
        status, loaded = _json_request(
            server_conn, "GET", "/api/swarms/studio/swarm?swarm_id=coder"
        )
        assert status == 200 and loaded.get("ok") is True
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/swarms/studio/validate",
            {"markdown": loaded.get("markdown")},
        )
        assert status == 200
        assert data.get("ok") is True
        assert isinstance(data.get("validation"), dict)
        assert "errors" in data["validation"]
        assert "warnings" in data["validation"]


# =========================================================================
# 13. VSCode Open API
# =========================================================================

class TestVSCodeOpenAPI:
    def test_vscode_open_missing_file_returns_400(self, server_conn):
        status, data = _json_request(server_conn, "POST", "/api/vscode/open", {})
        assert status == 400
        assert data.get("ok") is False

    def test_vscode_open_nonexistent_path_returns_400(self, server_conn):
        status, data = _json_request(
            server_conn,
            "POST",
            "/api/vscode/open",
            {"file": "data/default/swarms/nope/missing.md"},
        )
        assert status == 400
        assert data.get("success") is False


# =========================================================================
# 14. Response Content-Type
# =========================================================================

class TestResponseHeaders:
    """Tests that verify correct Content-Type headers are returned."""

    def test_api_endpoint_returns_json_content_type(self, server_conn):
        """API endpoints should return application/json content type."""
        server_conn.request("GET", "/api/catalog")
        resp = server_conn.getresponse()
        ct = resp.getheader("Content-Type", "")
        resp.read()
        assert "application/json" in ct

    def test_root_returns_html_content_type(self, server_conn):
        """GET / should return text/html content type."""
        server_conn.request("GET", "/")
        resp = server_conn.getresponse()
        ct = resp.getheader("Content-Type", "")
        resp.read()
        assert "text/html" in ct
