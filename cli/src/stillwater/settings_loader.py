"""
Stillwater Settings Loader
Version: 1.0.0 | Rung: 641 | Status: STABLE

Parses YAML front-matter from data/settings.md and exposes typed accessors
for API key, Firestore config, and sync metadata.

File format (YAML front-matter + Markdown body):

    ---
    api_key: sw_sk_<48 hex chars>
    firestore_project: stillwater-prod
    firestore_enabled: false
    sync_interval_seconds: 300
    last_sync_timestamp: null
    last_sync_status: pending
    ---

    # Data Settings
    ...

Design decisions:
- YAML front-matter only (no full Mermaid/Markdown body parsing).
- If settings.md is missing, all methods return defaults (no error raised).
- Thread-safe concurrent reads via a module-level RLock.
- Atomic writes: write to <file>.tmp then os.replace to the final path.
- API key validation: format only (sw_sk_ prefix + 48 hex chars), no remote call.
- Null != default: missing keys and null values both return None explicitly.

Usage:
    from stillwater.settings_loader import SettingsLoader

    loader = SettingsLoader()                 # uses data/settings.md relative to CWD
    loader = SettingsLoader("data/settings.md")

    key = loader.get_api_key()               # str or None
    ok  = loader.validate_api_key(key)       # bool (format check)
    enabled = loader.is_sync_enabled()       # bool
    loader.update_sync_metadata("2026-01-01T00:00:00Z", "ok")
"""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_API_KEY_PATTERN = re.compile(r"^sw_sk_[0-9a-f]{48}$")

_DEFAULTS: dict[str, Any] = {
    "api_key": None,
    "firestore_project": "stillwater-prod",
    "firestore_enabled": False,
    "sync_interval_seconds": 300,
    "last_sync_timestamp": None,
    "last_sync_status": "pending",
}

# Module-level reentrant lock for thread-safe reads/writes across instances.
_FILE_LOCK = threading.RLock()


# ---------------------------------------------------------------------------
# Internal YAML front-matter parser
# ---------------------------------------------------------------------------


def _parse_yaml_frontmatter(text: str) -> dict[str, Any]:
    """Parse minimal YAML front-matter from a Markdown string.

    Expects the text to start with ``---``, followed by simple ``key: value``
    lines, and closed by a second ``---`` line. Only scalar values are
    supported (strings, booleans, integers, null). No lists or nested maps.

    Args:
        text: Full text content of the settings file.

    Returns:
        Dict of parsed key-value pairs. Returns {} if no front-matter found.

    Raises:
        ValueError: if the front-matter block is malformed (e.g. duplicate
            ``---`` delimiters missing or unparseable value).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm_lines: list[str] = []
    closed = False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        fm_lines.append(line)

    if not closed:
        raise ValueError("YAML front-matter block is not closed (missing closing '---')")

    result: dict[str, Any] = {}
    for raw_line in fm_lines:
        # Skip blank lines and comment lines
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if ":" not in stripped:
            raise ValueError(f"Malformed YAML front-matter line (no colon): {raw_line!r}")

        key, _, raw_value = stripped.partition(":")
        key = key.strip()
        if not key:
            raise ValueError(f"Malformed YAML front-matter line (empty key): {raw_line!r}")

        value = _coerce_yaml_scalar(raw_value.strip())
        result[key] = value

    return result


def _coerce_yaml_scalar(raw: str) -> Any:
    """Convert a raw YAML scalar string to a Python value.

    Supported types: null, bool, int, str.

    Args:
        raw: The raw string after the colon in a YAML front-matter line.

    Returns:
        Python-typed value.
    """
    if raw in ("null", "~", ""):
        return None
    if raw.lower() in ("true", "yes", "on"):
        return True
    if raw.lower() in ("false", "no", "off"):
        return False
    # Try integer
    try:
        return int(raw)
    except ValueError:
        pass
    # Strip surrounding quotes (single or double)
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        return raw[1:-1]
    return raw


def _rebuild_file(original_text: str, updated_settings: dict[str, Any]) -> str:
    """Rebuild the settings file text with updated front-matter.

    The Markdown body (everything after the closing ``---``) is preserved
    unchanged. The front-matter is rebuilt from ``updated_settings`` in the
    original key order, with any extra original keys also preserved.

    Args:
        original_text: Current content of the settings file.
        updated_settings: The full settings dict to serialize.

    Returns:
        New file content as a string.
    """
    lines = original_text.splitlines(keepends=True)
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = i + 1
                break

    body = "".join(lines[body_start:])

    fm_lines = ["---\n"]
    for key, value in updated_settings.items():
        fm_lines.append(f"{key}: {_serialize_yaml_scalar(value)}\n")
    fm_lines.append("---\n")

    return "".join(fm_lines) + body


def _serialize_yaml_scalar(value: Any) -> str:
    """Serialize a Python value to a YAML scalar string.

    Args:
        value: Python value to serialize.

    Returns:
        YAML scalar representation.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


# ---------------------------------------------------------------------------
# SettingsLoader
# ---------------------------------------------------------------------------


class SettingsLoader:
    """Load, query, and update data/settings.md configuration.

    Thread safety:
        All reads and writes are protected by a module-level RLock so that
        concurrent reads are safe. Writes use atomic temp-file → rename to
        avoid partial writes being observed by concurrent readers.

    Args:
        settings_path: Path to the settings.md file. May be relative to CWD
            or absolute. Defaults to ``"data/settings.md"``.

    Raises:
        ValueError: Only on explicit parse errors (malformed YAML), not on
            missing files (missing → defaults returned).
    """

    def __init__(self, settings_path: str = "data/settings.md") -> None:
        self._path = Path(settings_path)
        self._settings: dict[str, Any] = {}
        self._loaded = False
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load and parse the settings file.

        If the file does not exist, self._settings stays as defaults.
        If the file exists but has no front-matter, defaults are used.
        Raises ValueError for malformed front-matter.
        """
        with _FILE_LOCK:
            if not self._path.exists():
                self._settings = dict(_DEFAULTS)
                self._loaded = False
                return

            text = self._path.read_text(encoding="utf-8")
            parsed = _parse_yaml_frontmatter(text)

            # Merge: start from defaults, overlay with file values.
            merged: dict[str, Any] = dict(_DEFAULTS)
            merged.update(parsed)
            self._settings = merged
            self._loaded = True

    def _reload(self) -> None:
        """Re-read the file from disk (for use after external modifications)."""
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_settings(self) -> dict[str, Any]:
        """Return the parsed settings dict.

        Keys present in _DEFAULTS are always present. Values come from the
        settings file when available; defaults otherwise.

        Returns:
            A shallow copy of the current settings dict.
        """
        with _FILE_LOCK:
            return dict(self._settings)

    def get_api_key(self) -> Optional[str]:
        """Return the configured API key, or None if not set.

        A key is considered absent when the ``api_key`` field is null,
        missing, or set to the placeholder ``sw_sk_[24_random_bytes]``.

        Returns:
            API key string or None.
        """
        with _FILE_LOCK:
            value = self._settings.get("api_key")

        if value is None:
            return None
        if not isinstance(value, str):
            return None
        # Reject the placeholder value from the template
        if value == "sw_sk_[24_random_bytes]":
            return None
        return value

    def validate_api_key(self, key: str) -> bool:
        """Check whether a key string matches the expected format.

        Format: ``sw_sk_`` prefix followed by exactly 48 lowercase hex characters
        (representing 24 random bytes).

        This is a format-only check — no remote verification is performed.

        Args:
            key: The key string to validate.

        Returns:
            True iff the key matches the required format.
        """
        if not isinstance(key, str):
            return False
        return bool(_API_KEY_PATTERN.match(key))

    def is_sync_enabled(self) -> bool:
        """Return True iff Firestore sync is enabled.

        Sync is considered enabled only when both:
        - ``firestore_enabled`` is ``True`` in the settings, AND
        - a valid (non-None) API key is present.

        Returns:
            bool — whether sync should be active.
        """
        with _FILE_LOCK:
            enabled = self._settings.get("firestore_enabled", False)

        if not isinstance(enabled, bool):
            enabled = bool(enabled)

        if not enabled:
            return False

        # Sync requires a key to be present (format-valid or not — presence check)
        return self.get_api_key() is not None

    def update_sync_metadata(self, timestamp: str, status: str) -> None:
        """Update last_sync_timestamp and last_sync_status and write back to disk.

        Uses atomic write (temp file → os.replace) to avoid partial writes.
        If the settings file does not exist, creates it with default content
        plus the updated metadata fields.

        Args:
            timestamp: ISO-8601 UTC timestamp string (e.g. "2026-01-01T00:00:00Z").
            status:    Sync status string — typically "ok", "error", or "pending".

        Raises:
            ValueError: if timestamp or status is not a non-empty string.
        """
        if not isinstance(timestamp, str) or not timestamp:
            raise ValueError(f"timestamp must be a non-empty string, got {timestamp!r}")
        if not isinstance(status, str) or not status:
            raise ValueError(f"status must be a non-empty string, got {status!r}")

        with _FILE_LOCK:
            self._settings["last_sync_timestamp"] = timestamp
            self._settings["last_sync_status"] = status

            if self._path.exists():
                original_text = self._path.read_text(encoding="utf-8")
            else:
                # Build a minimal default front-matter if the file doesn't exist yet.
                original_text = _rebuild_file("---\n---\n", dict(_DEFAULTS))

            new_text = _rebuild_file(original_text, self._settings)
            self._atomic_write(new_text)

    def _atomic_write(self, content: str) -> None:
        """Write content to the settings file atomically.

        Writes to a .tmp sibling file then calls os.replace() so readers
        always see either the old or the new complete file.

        Args:
            content: Full file content to write.
        """
        tmp_path = self._path.with_suffix(".md.tmp")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(str(tmp_path), str(self._path))

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def path(self) -> Path:
        """The resolved Path of the settings file."""
        return self._path

    @property
    def file_loaded(self) -> bool:
        """True iff the settings file existed and was successfully read."""
        return self._loaded

    def get(self, key: str, default: Any = None) -> Any:
        """Generic accessor for any settings key.

        Args:
            key: Settings key name.
            default: Value to return if the key is absent.

        Returns:
            Value from settings or ``default``.
        """
        with _FILE_LOCK:
            return self._settings.get(key, default)
