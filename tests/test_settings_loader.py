#!/usr/bin/env python3
"""
Stillwater SettingsLoader — Test Suite
Version: 1.0.0 | Rung: 641 | Persona: Skeptic Auditor

Skeptic mandate: Assume the implementation is wrong until proven correct.
Challenge every contract claim: YAML parsing, defaults, null safety, format
validation, thread isolation, and atomic write correctness.
No prose confidence — every claim backed by assertion.

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_settings_loader.py -v --tb=short
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import path setup — must resolve before any stillwater imports
# ---------------------------------------------------------------------------

CLI_SRC = Path(__file__).resolve().parent.parent / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))

from stillwater.settings_loader import (  # noqa: E402
    SettingsLoader,
    _coerce_yaml_scalar,
    _parse_yaml_frontmatter,
    _rebuild_file,
    _serialize_yaml_scalar,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_VALID_SETTINGS_CONTENT = """\
---
api_key: sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011
firestore_project: my-project
cloud_sync: true
sync_interval_seconds: 60
last_sync_timestamp: 2026-01-01T00:00:00Z
last_sync_status: ok
---

# Data Settings

Some body text here.
"""

_NO_API_KEY_CONTENT = """\
---
api_key: null
firestore_project: stillwater-prod
cloud_sync: false
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---
"""

_PLACEHOLDER_API_KEY_CONTENT = """\
---
api_key: sw_sk_[24_random_bytes]
firestore_project: stillwater-prod
cloud_sync: false
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---
"""

_MINIMAL_CONTENT = """\
---
---
"""


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ===========================================================================
# Group 1: YAML front-matter parser unit tests
# ===========================================================================


class TestParseYamlFrontmatter:
    """Tests for the internal _parse_yaml_frontmatter helper."""

    def test_valid_full_frontmatter(self) -> None:
        parsed = _parse_yaml_frontmatter(_VALID_SETTINGS_CONTENT)
        assert parsed["api_key"] == "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"
        assert parsed["firestore_project"] == "my-project"
        assert parsed["cloud_sync"] is True
        assert parsed["sync_interval_seconds"] == 60
        assert parsed["last_sync_timestamp"] == "2026-01-01T00:00:00Z"
        assert parsed["last_sync_status"] == "ok"

    def test_null_values_parse_to_none(self) -> None:
        parsed = _parse_yaml_frontmatter(_NO_API_KEY_CONTENT)
        assert parsed["api_key"] is None
        assert parsed["last_sync_timestamp"] is None

    def test_boolean_false_parses_correctly(self) -> None:
        parsed = _parse_yaml_frontmatter(_NO_API_KEY_CONTENT)
        assert parsed["cloud_sync"] is False

    def test_integer_values_parse_correctly(self) -> None:
        parsed = _parse_yaml_frontmatter(_VALID_SETTINGS_CONTENT)
        assert isinstance(parsed["sync_interval_seconds"], int)
        assert parsed["sync_interval_seconds"] == 60

    def test_no_frontmatter_returns_empty_dict(self) -> None:
        content = "# Just a markdown file\n\nNo front-matter here.\n"
        parsed = _parse_yaml_frontmatter(content)
        assert parsed == {}

    def test_empty_string_returns_empty_dict(self) -> None:
        assert _parse_yaml_frontmatter("") == {}

    def test_unclosed_frontmatter_raises_value_error(self) -> None:
        content = "---\napi_key: somekey\n"  # no closing ---
        with pytest.raises(ValueError, match="not closed"):
            _parse_yaml_frontmatter(content)

    def test_malformed_line_without_colon_raises(self) -> None:
        content = "---\nbadline\n---\n"
        with pytest.raises(ValueError, match="no colon"):
            _parse_yaml_frontmatter(content)

    def test_minimal_empty_frontmatter(self) -> None:
        parsed = _parse_yaml_frontmatter(_MINIMAL_CONTENT)
        assert parsed == {}

    def test_body_content_not_parsed(self) -> None:
        # The body should not affect front-matter parsing
        parsed = _parse_yaml_frontmatter(_VALID_SETTINGS_CONTENT)
        assert "Some body text here" not in parsed


class TestCoerceYamlScalar:
    """Tests for the internal scalar coercion helper."""

    def test_null_variants(self) -> None:
        assert _coerce_yaml_scalar("null") is None
        assert _coerce_yaml_scalar("~") is None
        assert _coerce_yaml_scalar("") is None

    def test_true_variants(self) -> None:
        assert _coerce_yaml_scalar("true") is True
        assert _coerce_yaml_scalar("True") is True
        assert _coerce_yaml_scalar("yes") is True
        assert _coerce_yaml_scalar("on") is True

    def test_false_variants(self) -> None:
        assert _coerce_yaml_scalar("false") is False
        assert _coerce_yaml_scalar("False") is False
        assert _coerce_yaml_scalar("no") is False
        assert _coerce_yaml_scalar("off") is False

    def test_integer_coercion(self) -> None:
        assert _coerce_yaml_scalar("300") == 300
        assert isinstance(_coerce_yaml_scalar("300"), int)

    def test_string_passthrough(self) -> None:
        assert _coerce_yaml_scalar("stillwater-prod") == "stillwater-prod"
        assert _coerce_yaml_scalar("2026-01-01T00:00:00Z") == "2026-01-01T00:00:00Z"


# ===========================================================================
# Group 2: SettingsLoader initialization and defaults
# ===========================================================================


class TestSettingsLoaderDefaults:
    """Tests for behaviour when settings.md is absent or minimal."""

    def test_missing_file_returns_defaults_no_error(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "nonexistent.md"))
        assert loader.file_loaded is False
        settings = loader.parse_settings()
        assert settings["cloud_sync"] is False
        assert settings["sync_interval_seconds"] == 300
        assert settings["last_sync_status"] == "pending"

    def test_missing_file_get_api_key_returns_none(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "nonexistent.md"))
        assert loader.get_api_key() is None

    def test_missing_file_is_sync_enabled_returns_false(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "nonexistent.md"))
        assert loader.is_sync_enabled() is False

    def test_defaults_all_keys_present(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "nonexistent.md"))
        settings = loader.parse_settings()
        expected_keys = {
            "api_key",
            "cloud_sync",
            "sync_interval_seconds",
            "last_sync_timestamp",
            "last_sync_status",
        }
        assert expected_keys.issubset(set(settings.keys()))

    def test_parse_settings_returns_shallow_copy(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "nonexistent.md"))
        s1 = loader.parse_settings()
        s2 = loader.parse_settings()
        # Mutating one copy does not affect the other or the loader's internal state
        s1["cloud_sync"] = True
        assert loader.parse_settings()["cloud_sync"] is False


# ===========================================================================
# Group 3: SettingsLoader with valid file
# ===========================================================================


class TestSettingsLoaderValidFile:
    """Tests for parsing a correctly formatted settings.md."""

    def test_file_loaded_flag_true(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.file_loaded is True

    def test_parse_settings_returns_all_values(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        s = loader.parse_settings()
        assert s["api_key"] == "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"
        assert s["firestore_project"] == "my-project"
        assert s["cloud_sync"] is True
        assert s["sync_interval_seconds"] == 60
        assert s["last_sync_timestamp"] == "2026-01-01T00:00:00Z"
        assert s["last_sync_status"] == "ok"

    def test_get_api_key_returns_string(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        key = loader.get_api_key()
        assert isinstance(key, str)
        assert key == "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"

    def test_is_sync_enabled_true_when_enabled_and_key_present(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.is_sync_enabled() is True

    def test_get_convenience_accessor(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.get("sync_interval_seconds") == 60
        assert loader.get("nonexistent_key", "fallback") == "fallback"


# ===========================================================================
# Group 4: API key validation
# ===========================================================================


class TestApiKeyValidation:
    """Tests for validate_api_key format checks."""

    def test_valid_key_passes(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        loader._settings = {}
        loader._path = Path("nonexistent")
        loader._loaded = False
        key = "sw_sk_" + "a" * 48
        assert loader.validate_api_key(key) is True

    def test_valid_key_with_mixed_hex(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        key = "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"
        assert loader.validate_api_key(key) is True

    def test_wrong_prefix_fails(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        key = "sk_" + "a" * 48
        assert loader.validate_api_key(key) is False

    def test_too_short_hex_fails(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        key = "sw_sk_" + "a" * 47
        assert loader.validate_api_key(key) is False

    def test_too_long_hex_fails(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        key = "sw_sk_" + "a" * 49
        assert loader.validate_api_key(key) is False

    def test_non_hex_chars_fail(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        key = "sw_sk_" + "g" * 48  # 'g' is not hex
        assert loader.validate_api_key(key) is False

    def test_uppercase_hex_fails(self) -> None:
        # Pattern requires lowercase hex
        loader = SettingsLoader.__new__(SettingsLoader)
        key = "sw_sk_" + "A" * 48
        assert loader.validate_api_key(key) is False

    def test_non_string_input_fails(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        assert loader.validate_api_key(None) is False  # type: ignore[arg-type]
        assert loader.validate_api_key(12345) is False  # type: ignore[arg-type]

    def test_empty_string_fails(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        assert loader.validate_api_key("") is False

    def test_placeholder_value_fails(self) -> None:
        loader = SettingsLoader.__new__(SettingsLoader)
        assert loader.validate_api_key("sw_sk_[24_random_bytes]") is False


# ===========================================================================
# Group 5: get_api_key null safety
# ===========================================================================


class TestGetApiKeyNullSafety:
    """Tests confirming get_api_key returns None gracefully, never raising."""

    def test_null_value_in_file_returns_none(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.get_api_key() is None

    def test_placeholder_in_file_returns_none(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _PLACEHOLDER_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.get_api_key() is None

    def test_missing_file_returns_none_not_error(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "missing.md"))
        result = loader.get_api_key()  # must not raise
        assert result is None

    def test_key_present_returns_string_not_none(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        result = loader.get_api_key()
        assert result is not None
        assert isinstance(result, str)


# ===========================================================================
# Group 6: is_sync_enabled
# ===========================================================================


class TestIsSyncEnabled:
    """Tests for is_sync_enabled logic."""

    def test_enabled_with_valid_key_returns_true(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.is_sync_enabled() is True

    def test_enabled_false_in_file_returns_false(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.is_sync_enabled() is False

    def test_enabled_true_but_no_api_key_returns_false(self, tmp_path: Path) -> None:
        content = """\
---
api_key: null
firestore_project: stillwater-prod
cloud_sync: true
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---
"""
        p = _write(tmp_path, "settings.md", content)
        loader = SettingsLoader(str(p))
        # No key → sync cannot proceed
        assert loader.is_sync_enabled() is False

    def test_missing_file_returns_false(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "missing.md"))
        assert loader.is_sync_enabled() is False


# ===========================================================================
# Group 7: update_sync_metadata
# ===========================================================================


class TestUpdateSyncMetadata:
    """Tests for update_sync_metadata write-back and atomic write."""

    def test_update_creates_file_if_missing(self, tmp_path: Path) -> None:
        p = tmp_path / "settings.md"
        loader = SettingsLoader(str(p))
        loader.update_sync_metadata("2026-02-01T12:00:00Z", "ok")
        assert p.exists()

    def test_update_writes_timestamp_and_status(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        loader.update_sync_metadata("2026-02-23T00:00:00Z", "ok")

        text = p.read_text(encoding="utf-8")
        assert "2026-02-23T00:00:00Z" in text
        assert "last_sync_status: ok" in text

    def test_update_reflects_in_parse_settings(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        loader.update_sync_metadata("2026-02-23T00:00:00Z", "error")
        s = loader.parse_settings()
        assert s["last_sync_timestamp"] == "2026-02-23T00:00:00Z"
        assert s["last_sync_status"] == "error"

    def test_update_preserves_body_content(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        loader.update_sync_metadata("2026-02-23T00:00:00Z", "ok")
        text = p.read_text(encoding="utf-8")
        assert "Some body text here." in text

    def test_update_invalid_timestamp_raises(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        with pytest.raises(ValueError, match="timestamp"):
            loader.update_sync_metadata("", "ok")

    def test_update_invalid_status_raises(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        with pytest.raises(ValueError, match="status"):
            loader.update_sync_metadata("2026-02-23T00:00:00Z", "")

    def test_atomic_write_no_tmp_left_behind(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        loader.update_sync_metadata("2026-02-23T00:00:00Z", "ok")
        tmp = p.with_suffix(".md.tmp")
        assert not tmp.exists(), "Temp file must be cleaned up after atomic write"

    def test_multiple_updates_accumulate_correctly(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        loader.update_sync_metadata("2026-02-01T00:00:00Z", "ok")
        loader.update_sync_metadata("2026-02-23T12:30:00Z", "error")
        s = loader.parse_settings()
        assert s["last_sync_timestamp"] == "2026-02-23T12:30:00Z"
        assert s["last_sync_status"] == "error"


# ===========================================================================
# Group 8: Thread safety
# ===========================================================================


class TestThreadSafety:
    """Tests for concurrent read correctness under load."""

    def test_concurrent_reads_return_consistent_results(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _VALID_SETTINGS_CONTENT)
        loader = SettingsLoader(str(p))
        results: list[Optional[str]] = []
        errors: list[Exception] = []

        def read_key() -> None:
            try:
                results.append(loader.get_api_key())
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=read_key) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert not errors, f"Thread errors: {errors}"
        assert all(r == "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011" for r in results)

    def test_concurrent_reads_and_writes_no_crash(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        errors: list[Exception] = []

        def do_read() -> None:
            for _ in range(10):
                try:
                    loader.is_sync_enabled()
                    loader.get_api_key()
                    loader.parse_settings()
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        def do_write() -> None:
            for i in range(5):
                try:
                    loader.update_sync_metadata(f"2026-02-{i+1:02d}T00:00:00Z", "ok")
                    time.sleep(0.001)
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        readers = [threading.Thread(target=do_read) for _ in range(10)]
        writer = threading.Thread(target=do_write)

        for t in readers:
            t.start()
        writer.start()

        for t in readers:
            t.join(timeout=10)
        writer.join(timeout=10)

        assert not errors, f"Concurrent read/write errors: {errors}"


# ===========================================================================
# Group 9: Rebuild file helper
# ===========================================================================


class TestRebuildFile:
    """Tests for the internal _rebuild_file helper."""

    def test_rebuild_updates_fields(self) -> None:
        original = _VALID_SETTINGS_CONTENT
        updated = {
            "api_key": "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011",
            "firestore_project": "my-project",
            "cloud_sync": True,
            "sync_interval_seconds": 60,
            "last_sync_timestamp": "2026-02-23T00:00:00Z",
            "last_sync_status": "error",
        }
        result = _rebuild_file(original, updated)
        assert "last_sync_status: error" in result
        assert "last_sync_timestamp: 2026-02-23T00:00:00Z" in result

    def test_rebuild_preserves_body(self) -> None:
        original = _VALID_SETTINGS_CONTENT
        updated = {"api_key": None}
        result = _rebuild_file(original, updated)
        assert "Some body text here." in result

    def test_rebuild_starts_with_frontmatter_delimiter(self) -> None:
        result = _rebuild_file(_NO_API_KEY_CONTENT, {"api_key": None})
        assert result.startswith("---\n")


# ===========================================================================
# Group 10: Serialize YAML scalar helper
# ===========================================================================


class TestSerializeYamlScalar:
    """Tests for the internal _serialize_yaml_scalar helper."""

    def test_none_serializes_to_null(self) -> None:
        assert _serialize_yaml_scalar(None) == "null"

    def test_true_serializes_correctly(self) -> None:
        assert _serialize_yaml_scalar(True) == "true"

    def test_false_serializes_correctly(self) -> None:
        assert _serialize_yaml_scalar(False) == "false"

    def test_int_serializes_correctly(self) -> None:
        assert _serialize_yaml_scalar(300) == "300"

    def test_string_passthrough(self) -> None:
        assert _serialize_yaml_scalar("ok") == "ok"
        assert _serialize_yaml_scalar("2026-02-23T00:00:00Z") == "2026-02-23T00:00:00Z"


# ===========================================================================
# Group 11: Edge cases and null safety contracts
# ===========================================================================


class TestEdgeCases:
    """Miscellaneous edge cases and contract verification."""

    def test_path_property_accessible(self, tmp_path: Path) -> None:
        p = tmp_path / "settings.md"
        loader = SettingsLoader(str(p))
        assert loader.path == p

    def test_minimal_frontmatter_file_uses_defaults(self, tmp_path: Path) -> None:
        p = _write(tmp_path, "settings.md", _MINIMAL_CONTENT)
        loader = SettingsLoader(str(p))
        s = loader.parse_settings()
        # All defaults should be present since front-matter is empty
        assert s["cloud_sync"] is False
        assert s["sync_interval_seconds"] == 300

    def test_settings_with_extra_unknown_keys(self, tmp_path: Path) -> None:
        content = """\
---
api_key: null
custom_field: hello
cloud_sync: false
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
firestore_project: stillwater-prod
---
"""
        p = _write(tmp_path, "settings.md", content)
        loader = SettingsLoader(str(p))
        # Known fields still parse correctly
        assert loader.get_api_key() is None
        assert loader.is_sync_enabled() is False
        # Extra key is available via get()
        assert loader.get("custom_field") == "hello"

    def test_default_path_string_used_when_no_arg(self) -> None:
        # Just verifies the default path is set (file likely doesn't exist)
        loader = SettingsLoader()
        assert str(loader.path) == "data/settings.md"
        assert loader.file_loaded is False  # won't exist in test runner cwd

    def test_get_returns_default_for_unknown_key(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "missing.md"))
        assert loader.get("nonexistent") is None
        assert loader.get("nonexistent", "sentinel") == "sentinel"

    def test_is_sync_enabled_returns_bool_type(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "missing.md"))
        result = loader.is_sync_enabled()
        assert isinstance(result, bool)

    def test_validate_api_key_returns_bool_type(self, tmp_path: Path) -> None:
        loader = SettingsLoader(str(tmp_path / "missing.md"))
        assert isinstance(loader.validate_api_key("sw_sk_" + "a" * 48), bool)
        assert isinstance(loader.validate_api_key("bad"), bool)

    def test_frontmatter_with_comment_and_blank_lines_parses_cleanly(self, tmp_path: Path) -> None:
        """Cover the blank/comment-line skip branch in _parse_yaml_frontmatter."""
        content = """\
---
# This is a comment
api_key: null

cloud_sync: false
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
firestore_project: stillwater-prod
---
"""
        p = _write(tmp_path, "settings.md", content)
        loader = SettingsLoader(str(p))
        assert loader.get_api_key() is None
        assert loader.is_sync_enabled() is False

    def test_frontmatter_empty_key_raises(self) -> None:
        """Cover the empty-key error path in _parse_yaml_frontmatter."""
        content = "---\n: bad_value\n---\n"
        with pytest.raises(ValueError, match="empty key"):
            _parse_yaml_frontmatter(content)

    def test_quoted_string_scalar_parses_correctly(self) -> None:
        """Cover the quoted-string branch in _coerce_yaml_scalar."""
        assert _coerce_yaml_scalar('"hello world"') == "hello world"
        assert _coerce_yaml_scalar("'single quoted'") == "single quoted"

    def test_reload_rereads_file(self, tmp_path: Path) -> None:
        """Cover the _reload() helper method."""
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        assert loader.get_api_key() is None
        # Modify the file externally
        new_content = _NO_API_KEY_CONTENT.replace(
            "api_key: null",
            "api_key: sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011",
        )
        p.write_text(new_content, encoding="utf-8")
        loader._reload()
        assert loader.get_api_key() == "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"

    def test_get_api_key_non_string_value_returns_none(self, tmp_path: Path) -> None:
        """Cover the non-string api_key guard in get_api_key()."""
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        # Directly inject a non-string to exercise the isinstance branch
        loader._settings["api_key"] = 12345
        assert loader.get_api_key() is None

    def test_is_sync_enabled_non_bool_enabled_coerced(self, tmp_path: Path) -> None:
        """Cover the non-bool enabled coercion branch in is_sync_enabled()."""
        p = _write(tmp_path, "settings.md", _NO_API_KEY_CONTENT)
        loader = SettingsLoader(str(p))
        # Inject a truthy non-bool value — should coerce to True, but still
        # return False because no api_key is present.
        loader._settings["cloud_sync"] = 1
        assert loader.is_sync_enabled() is False
        # Now also add a key to confirm coercion path goes all the way to key check
        loader._settings["api_key"] = "sw_sk_aabbccddeeff00112233445566778899aabbccddeeff0011"
        assert loader.is_sync_enabled() is True


# ---------------------------------------------------------------------------
# Type annotation for thread test
# ---------------------------------------------------------------------------
from typing import Optional  # noqa: E402 (used above)
