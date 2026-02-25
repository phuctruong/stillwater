"""
tests/test_admin_server.py — Security Auditor tests for admin/server.py

Persona: Security Auditor
Focus: path traversal prevention, command injection, input validation,
       JSON I/O correctness, allowlist enforcement, size limits.

Rung target: 65537 (security-sensitive module)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import target module
# ---------------------------------------------------------------------------
sys.path.insert(0, "/home/phuc/projects/stillwater")
sys.path.insert(0, "/home/phuc/projects/stillwater/src/cli/src")

from admin.server import (  # noqa: E402
    ALLOWED_WRITE_SUFFIXES,
    REPO_ROOT,
    SAFE_CLI_COMMANDS,
    _append_jsonl,
    _catalog,
    _community_link,
    _community_sync,
    _create_file,
    _is_allowed_edit_path,
    _load_json,
    _run_cli_command,
    _safe_resolve_repo_path,
    _utc_now,
    _write_json,
)


# ===========================================================================
# 1. _utc_now()
# ===========================================================================


class TestUtcNow:
    def test_returns_string(self):
        result = _utc_now()
        assert isinstance(result, str)

    def test_matches_iso8601_utc_format(self):
        result = _utc_now()
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", result), (
            f"_utc_now() returned unexpected format: {result!r}"
        )

    def test_ends_with_Z(self):
        """Confirms UTC designator 'Z' is always present, not +00:00."""
        assert _utc_now().endswith("Z")


# ===========================================================================
# 2. _load_json / _write_json round-trip
# ===========================================================================


class TestJsonIo:
    def test_write_then_load_roundtrip(self, tmp_path: Path):
        data = {"key": "value", "num": 42, "nested": {"a": 1}}
        target = tmp_path / "test.json"
        _write_json(target, data)
        loaded = _load_json(target)
        assert loaded == data

    def test_write_creates_parent_dirs(self, tmp_path: Path):
        target = tmp_path / "deep" / "nested" / "file.json"
        assert not target.parent.exists()
        _write_json(target, {"x": 1})
        assert target.exists()

    def test_write_output_ends_with_newline(self, tmp_path: Path):
        target = tmp_path / "test.json"
        _write_json(target, {"a": 1})
        raw = target.read_text(encoding="utf-8")
        assert raw.endswith("\n"), "JSON file should end with a trailing newline"

    def test_write_sorts_keys(self, tmp_path: Path):
        target = tmp_path / "sorted.json"
        _write_json(target, {"z": 1, "a": 2, "m": 3})
        raw = target.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        keys = list(parsed.keys())
        assert keys == sorted(keys), "Keys must be sorted (sort_keys=True)"

    def test_load_missing_file_raises(self, tmp_path: Path):
        missing = tmp_path / "does_not_exist.json"
        with pytest.raises(FileNotFoundError):
            _load_json(missing)


# ===========================================================================
# 3. _append_jsonl
# ===========================================================================


class TestAppendJsonl:
    def test_creates_file_on_first_write(self, tmp_path: Path):
        log = tmp_path / "events.jsonl"
        assert not log.exists()
        _append_jsonl(log, {"event": "init"})
        assert log.exists()

    def test_creates_parent_dirs(self, tmp_path: Path):
        log = tmp_path / "sub" / "dir" / "events.jsonl"
        assert not log.parent.exists()
        _append_jsonl(log, {"x": 1})
        assert log.exists()

    def test_multiple_rows_are_separate_lines(self, tmp_path: Path):
        log = tmp_path / "multi.jsonl"
        _append_jsonl(log, {"event": "one", "val": 1})
        _append_jsonl(log, {"event": "two", "val": 2})
        _append_jsonl(log, {"event": "three", "val": 3})
        lines = [ln for ln in log.read_text(encoding="utf-8").strip().split("\n") if ln]
        assert len(lines) == 3

    def test_each_line_is_valid_json(self, tmp_path: Path):
        log = tmp_path / "valid.jsonl"
        rows = [{"a": i, "b": f"val{i}"} for i in range(5)]
        for row in rows:
            _append_jsonl(log, row)
        lines = log.read_text(encoding="utf-8").strip().split("\n")
        for line in lines:
            parsed = json.loads(line)
            assert isinstance(parsed, dict)

    def test_appended_rows_preserve_data(self, tmp_path: Path):
        log = tmp_path / "data.jsonl"
        _append_jsonl(log, {"event": "alpha", "val": 99})
        _append_jsonl(log, {"event": "beta", "val": 100})
        lines = log.read_text(encoding="utf-8").strip().split("\n")
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["event"] == "alpha" and first["val"] == 99
        assert second["event"] == "beta" and second["val"] == 100

    def test_keys_are_sorted(self, tmp_path: Path):
        log = tmp_path / "sorted.jsonl"
        _append_jsonl(log, {"z": 1, "a": 2, "m": 3})
        line = log.read_text(encoding="utf-8").strip()
        parsed = json.loads(line)
        assert list(parsed.keys()) == sorted(parsed.keys())


# ===========================================================================
# 4. _safe_resolve_repo_path — path traversal prevention
# ===========================================================================


class TestSafeResolveRepoPath:
    def test_normal_path_resolves_inside_repo(self):
        result = _safe_resolve_repo_path("data/default/skills/prime-docker.md")
        assert str(result).startswith(str(REPO_ROOT))

    def test_dotdot_traversal_raises_value_error(self):
        with pytest.raises(ValueError, match="path escapes repo"):
            _safe_resolve_repo_path("../../etc/passwd")

    def test_deep_dotdot_traversal_raises_value_error(self):
        with pytest.raises(ValueError, match="path escapes repo"):
            _safe_resolve_repo_path("../../../tmp/evil")

    def test_dotdot_inside_path_raises_value_error(self):
        """Traversal hidden inside a plausible subdirectory prefix."""
        with pytest.raises(ValueError, match="path escapes repo"):
            _safe_resolve_repo_path("data/default/skills/../../../../../etc/passwd")

    def test_absolute_outside_repo_raises_value_error(self):
        with pytest.raises(ValueError, match="path escapes repo"):
            _safe_resolve_repo_path("/etc/passwd")

    def test_result_type_is_path(self):
        result = _safe_resolve_repo_path("data/default/skills/prime-docker.md")
        assert isinstance(result, Path)

    def test_nested_valid_path_resolves(self):
        result = _safe_resolve_repo_path("src/cli/recipes")
        assert str(result).startswith(str(REPO_ROOT))


# ===========================================================================
# 5. _is_allowed_edit_path
# ===========================================================================


class TestIsAllowedEditPath:
    def test_md_file_in_skills_is_allowed(self):
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        first_skill = next(skills_dir.glob("*.md"), None)
        assert first_skill is not None, "skills/ directory must contain at least one .md"
        assert _is_allowed_edit_path(first_skill) is True

    def test_py_file_in_skills_dir_is_disallowed(self):
        """Python files must never be editable via the admin UI."""
        fake_py = REPO_ROOT / "data" / "default" / "skills" / "injected.py"
        assert _is_allowed_edit_path(fake_py) is False

    def test_sh_file_is_disallowed(self):
        """Shell scripts must never be editable via the admin UI."""
        fake_sh = REPO_ROOT / "data" / "default" / "skills" / "inject.sh"
        assert _is_allowed_edit_path(fake_sh) is False

    def test_md_outside_any_allowed_dir_is_disallowed(self):
        """A Markdown file in /tmp is not in any allowlisted directory."""
        outside = Path("/tmp/evil.md")
        assert _is_allowed_edit_path(outside) is False

    def test_md_in_non_catalog_repo_dir_is_disallowed(self):
        """scratch/ is in the repo but not in any catalog dir or EXTRA_EDITABLE_FILES."""
        scratch_md = REPO_ROOT / "scratch" / "test.md"
        assert _is_allowed_edit_path(scratch_md) is False

    def test_extra_editable_file_llm_config_is_allowed(self):
        """llm_config.yaml is in EXTRA_EDITABLE_FILES and should be allowed."""
        llm_config = REPO_ROOT / "llm_config.yaml"
        if llm_config.exists():
            assert _is_allowed_edit_path(llm_config) is True

    def test_swarms_md_is_allowed(self):
        swarms_dir = REPO_ROOT / "data" / "default" / "swarms"
        first_swarm = next(
            (p for p in swarms_dir.rglob("*.md") if not p.name.startswith("README")),
            None,
        )
        assert first_swarm is not None, "swarms/ directory must contain at least one .md"
        assert _is_allowed_edit_path(first_swarm) is True


# ===========================================================================
# 6. _catalog
# ===========================================================================


class TestCatalog:
    def test_returns_dict_with_groups_and_extras(self):
        result = _catalog()
        assert isinstance(result, dict)
        assert "groups" in result
        assert "extras" in result

    def test_groups_is_list(self):
        result = _catalog()
        assert isinstance(result["groups"], list)

    def test_each_group_has_required_fields(self):
        result = _catalog()
        required = {"id", "title", "files", "count"}
        for group in result["groups"]:
            missing = required - set(group.keys())
            assert not missing, f"Group {group.get('id')!r} missing fields: {missing}"

    def test_count_matches_files_length(self):
        result = _catalog()
        for group in result["groups"]:
            assert group["count"] == len(group["files"]), (
                f"Group {group['id']!r}: count={group['count']} "
                f"but len(files)={len(group['files'])}"
            )

    def test_file_entries_have_required_fields(self):
        result = _catalog()
        required_file_fields = {"path", "name", "group", "dir"}
        for group in result["groups"]:
            for f in group["files"]:
                missing = required_file_fields - set(f.keys())
                assert not missing, f"File entry missing fields: {missing} in group {group['id']!r}"

    def test_root_skills_group_has_files(self):
        """The root_skills group (data/default/skills/*.md) should have at least one file."""
        result = _catalog()
        root_skills = next((g for g in result["groups"] if g["id"] == "root_skills"), None)
        assert root_skills is not None
        assert root_skills["count"] > 0, "root_skills group must have at least one skill file"

    def test_no_file_path_escapes_repo(self):
        """Every file path in the catalog must resolve inside REPO_ROOT."""
        result = _catalog()
        repo_str = str(REPO_ROOT.resolve())
        for group in result["groups"]:
            for f in group["files"]:
                resolved = str((REPO_ROOT / f["path"]).resolve())
                assert resolved.startswith(repo_str), (
                    f"Catalog entry {f['path']!r} resolves outside REPO_ROOT!"
                )


# ===========================================================================
# 7. _create_file — filename validation and group lookup
# ===========================================================================


class TestCreateFile:
    def test_invalid_filename_with_slash_raises_value_error(self):
        with pytest.raises(ValueError, match=r"\[A-Za-z0-9"):
            _create_file("root_skills", "path/traversal.md")

    def test_invalid_filename_with_spaces_raises_value_error(self):
        with pytest.raises(ValueError, match=r"\[A-Za-z0-9"):
            _create_file("root_skills", "my file name.md")

    def test_invalid_filename_with_special_chars_raises_value_error(self):
        with pytest.raises(ValueError, match=r"\[A-Za-z0-9"):
            _create_file("root_skills", "evil$(rm -rf /).md")

    def test_unknown_group_raises_value_error(self):
        with pytest.raises(ValueError, match="unknown group"):
            _create_file("nonexistent_group", "valid.md")

    def test_existing_filename_raises_file_exists_error(self):
        """Creating a file that already exists must raise FileExistsError."""
        skills_dir = REPO_ROOT / "data" / "default" / "skills"
        existing = next(skills_dir.glob("*.md"), None)
        assert existing is not None
        with pytest.raises(FileExistsError):
            _create_file("root_skills", existing.name)

    def test_valid_create_returns_dict_with_path_and_created(self, tmp_path: Path, monkeypatch):
        """
        Monkeypatch REPO_ROOT inside admin.server so create_file writes to tmp_path
        without touching the real repo.
        """
        import admin.server as srv

        fake_root = tmp_path
        (fake_root / "data" / "default" / "skills").mkdir(parents=True)

        original_root = srv.REPO_ROOT
        monkeypatch.setattr(srv, "REPO_ROOT", fake_root)

        try:
            result = srv._create_file("root_skills", "test-skill-new.md")
            assert result["created"] is True
            assert "path" in result
            assert result["path"].endswith("test-skill-new.md")
        finally:
            monkeypatch.setattr(srv, "REPO_ROOT", original_root)

    def test_filename_without_extension_gets_md_appended(self, tmp_path: Path, monkeypatch):
        """A filename without a dot should get .md appended automatically."""
        import admin.server as srv

        fake_root = tmp_path
        (fake_root / "data" / "default" / "skills").mkdir(parents=True)

        original_root = srv.REPO_ROOT
        monkeypatch.setattr(srv, "REPO_ROOT", fake_root)

        try:
            result = srv._create_file("root_skills", "my-new-skill")
            assert result["path"].endswith(".md")
        finally:
            monkeypatch.setattr(srv, "REPO_ROOT", original_root)


# ===========================================================================
# 8. _run_cli_command — allowlist enforcement (command injection prevention)
# ===========================================================================


class TestRunCliCommand:
    def test_disallowed_command_raises_value_error(self):
        with pytest.raises(ValueError, match="command not allowed"):
            _run_cli_command("rm -rf /")

    def test_shell_injection_attempt_raises_value_error(self):
        with pytest.raises(ValueError, match="command not allowed"):
            _run_cli_command("version; rm -rf /")

    def test_semicolon_injection_raises_value_error(self):
        with pytest.raises(ValueError, match="command not allowed"):
            _run_cli_command("doctor; cat /etc/shadow")

    def test_empty_command_raises_value_error(self):
        with pytest.raises(ValueError, match="command not allowed"):
            _run_cli_command("")

    def test_allowed_version_command_returns_expected_keys(self):
        result = _run_cli_command("version")
        assert set(result.keys()) >= {"command", "cmd", "returncode", "stdout", "stderr", "ok"}

    def test_allowed_version_command_field_is_correct(self):
        result = _run_cli_command("version")
        assert result["command"] == "version"

    def test_ok_field_is_boolean(self):
        result = _run_cli_command("version")
        assert isinstance(result["ok"], bool)

    def test_cmd_is_list_not_string(self):
        """Commands must be lists to prevent shell=True injection vectors."""
        result = _run_cli_command("version")
        assert isinstance(result["cmd"], list)


# ===========================================================================
# 9. _community_link — email validation
# ===========================================================================


class TestCommunityLink:
    def test_valid_email_returns_payload_dict(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._write_json", lambda *_args, **_kwargs: None)
        result = _community_link("user@example.com")
        assert isinstance(result, dict)

    def test_valid_email_is_normalized_lowercase(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._write_json", lambda *_args, **_kwargs: None)
        result = _community_link("User@Example.COM")
        assert result["email"] == "user@example.com"

    def test_valid_email_status_is_linked(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._write_json", lambda *_args, **_kwargs: None)
        result = _community_link("user@example.com")
        assert result["status"] == "linked"

    def test_cloud_not_configured_passes_through(self, monkeypatch):
        monkeypatch.setattr(
            "admin.server._cloud_health",
            lambda: {"status": "not_configured", "message": "configure key"},
        )
        result = _community_link("user@example.com")
        assert result["status"] == "not_configured"

    def test_invalid_email_no_at_raises_value_error(self):
        with pytest.raises(ValueError, match="valid email required"):
            _community_link("notanemail")

    def test_invalid_email_no_dot_raises_value_error(self):
        with pytest.raises(ValueError, match="valid email required"):
            _community_link("user@nodot")

    def test_invalid_email_empty_raises_value_error(self):
        with pytest.raises(ValueError, match="valid email required"):
            _community_link("")

    def test_invalid_email_spaces_raises_value_error(self):
        with pytest.raises(ValueError, match="valid email required"):
            _community_link("user @example.com")

# ===========================================================================
# 10. _community_sync — counts local recipes/skills
# ===========================================================================


class TestCommunitySync:
    def test_sync_returns_required_keys(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._append_jsonl", lambda *_args, **_kwargs: None)
        result = _community_sync("both")
        required = {"status", "direction", "synced_at", "response"}
        assert required <= set(result.keys())

    def test_sync_status_is_ok(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._append_jsonl", lambda *_args, **_kwargs: None)
        result = _community_sync("both")
        assert result["status"] == "ok"

    def test_empty_direction_normalizes_to_both(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._append_jsonl", lambda *_args, **_kwargs: None)
        result = _community_sync("")
        assert result["direction"] == "both"

    def test_up_direction_preserved(self, monkeypatch):
        monkeypatch.setattr("admin.server._cloud_health", lambda: {"status": "ok", "tier": "yellow"})
        monkeypatch.setattr(
            "admin.server._load_cloud_config",
            lambda: {"enabled": True, "api_key": "k", "api_url": "https://example.com"},
        )
        monkeypatch.setattr("admin.server._request_cloud", lambda *_args, **_kwargs: (200, {"ok": True}, None))
        monkeypatch.setattr("admin.server._append_jsonl", lambda *_args, **_kwargs: None)
        result = _community_sync("up")
        assert result["direction"] == "up"

    def test_invalid_direction_raises_value_error(self):
        with pytest.raises(ValueError, match="direction must be one of"):
            _community_sync("upload")


# ===========================================================================
# 11. SAFE_CLI_COMMANDS allowlist
# ===========================================================================


class TestSafeCliCommands:
    def test_allowlist_is_dict(self):
        assert isinstance(SAFE_CLI_COMMANDS, dict)

    def test_allowlist_contains_only_safe_commands(self):
        """Verify the exact set of allowed commands — never grow it silently."""
        expected_keys = {"version", "doctor", "llm-status"}
        assert set(SAFE_CLI_COMMANDS.keys()) == expected_keys

    def test_all_commands_are_lists(self):
        """All commands must be lists (no shell=True style strings)."""
        for key, cmd in SAFE_CLI_COMMANDS.items():
            assert isinstance(cmd, list), (
                f"Command {key!r} must be a list, got {type(cmd).__name__}"
            )

    def test_no_shell_metacharacters_in_commands(self):
        """No command token should contain shell metacharacters."""
        dangerous_chars = set(";|&`$><\\!")
        for key, cmd in SAFE_CLI_COMMANDS.items():
            for token in cmd:
                overlap = dangerous_chars & set(token)
                assert not overlap, (
                    f"Command {key!r} token {token!r} contains dangerous chars: {overlap}"
                )

    def test_rm_not_in_allowlist(self):
        assert "rm" not in SAFE_CLI_COMMANDS
        assert "rm -rf /" not in SAFE_CLI_COMMANDS

    def test_bash_not_in_allowlist(self):
        assert "bash" not in SAFE_CLI_COMMANDS

    def test_sh_not_in_allowlist(self):
        assert "sh" not in SAFE_CLI_COMMANDS


# ===========================================================================
# 12. ALLOWED_WRITE_SUFFIXES — no executable types
# ===========================================================================


class TestAllowedWriteSuffixes:
    def test_is_set(self):
        assert isinstance(ALLOWED_WRITE_SUFFIXES, set)

    def test_md_is_allowed(self):
        assert ".md" in ALLOWED_WRITE_SUFFIXES

    def test_txt_is_allowed(self):
        assert ".txt" in ALLOWED_WRITE_SUFFIXES

    def test_yaml_is_allowed(self):
        assert ".yaml" in ALLOWED_WRITE_SUFFIXES

    def test_yml_is_allowed(self):
        assert ".yml" in ALLOWED_WRITE_SUFFIXES

    def test_json_is_allowed(self):
        assert ".json" in ALLOWED_WRITE_SUFFIXES

    def test_py_not_allowed(self):
        """Python files must never be writable via admin UI."""
        assert ".py" not in ALLOWED_WRITE_SUFFIXES

    def test_sh_not_allowed(self):
        """Shell scripts must never be writable via admin UI."""
        assert ".sh" not in ALLOWED_WRITE_SUFFIXES

    def test_exe_not_allowed(self):
        assert ".exe" not in ALLOWED_WRITE_SUFFIXES

    def test_js_not_allowed(self):
        assert ".js" not in ALLOWED_WRITE_SUFFIXES

    def test_html_not_allowed(self):
        assert ".html" not in ALLOWED_WRITE_SUFFIXES
