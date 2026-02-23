"""Tests for stillwater.data_registry.DataRegistry.

Coverage targets:
  - load_data_file: returns custom version when custom exists
  - load_data_file: falls back to default when custom missing
  - load_data_file: returns None when file exists in neither layer
  - save_data_file: creates data/custom/ directory when absent
  - save_data_file: writes to custom/, never touches default/
  - save_data_file: atomic (temp→rename); default/ not modified on error
  - load_all_data: custom overlay applies over default
  - load_all_data: .gitkeep sentinel excluded from result
  - load_all_data: returns empty dict when both dirs missing
  - get_file_source: returns "custom" when custom exists
  - get_file_source: returns "default" when only default exists
  - get_file_source: returns "missing" when file in neither layer
  - Determinism: repeated loads return identical results
  - Path traversal guard raises ValueError

Rung: 641 — deterministic, no network.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Optional

import pytest

from stillwater.data_registry import DataRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    """Create a minimal repo-root layout in a temp directory."""
    (tmp_path / "data" / "default").mkdir(parents=True)
    (tmp_path / "data" / "custom").mkdir(parents=True)
    (tmp_path / "data" / "custom" / ".gitkeep").write_text("", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def registry(repo_root: Path) -> DataRegistry:
    """Return a DataRegistry pointed at the temp repo_root."""
    return DataRegistry(repo_root=repo_root)


@pytest.fixture()
def default_dir(repo_root: Path) -> Path:
    return repo_root / "data" / "default"


@pytest.fixture()
def custom_dir(repo_root: Path) -> Path:
    return repo_root / "data" / "custom"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def write_default(default_dir: Path, filename: str, content: str) -> None:
    """Write a file into the default layer (test setup only)."""
    (default_dir / filename).parent.mkdir(parents=True, exist_ok=True)
    (default_dir / filename).write_text(content, encoding="utf-8")


def write_custom(custom_dir: Path, filename: str, content: str) -> None:
    """Write a file into the custom layer (test setup only)."""
    (custom_dir / filename).parent.mkdir(parents=True, exist_ok=True)
    (custom_dir / filename).write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: load_data_file returns custom version when custom exists
# ---------------------------------------------------------------------------


def test_load_prefers_custom_over_default(
    registry: DataRegistry, default_dir: Path, custom_dir: Path
) -> None:
    """Custom layer wins when both versions exist."""
    write_default(default_dir, "jokes.json", '["default joke"]')
    write_custom(custom_dir, "jokes.json", '["custom joke"]')

    result = registry.load_data_file("jokes.json")

    assert result == '["custom joke"]', "Expected custom content, got default"


# ---------------------------------------------------------------------------
# Test 2: load_data_file falls back to default when custom missing
# ---------------------------------------------------------------------------


def test_load_falls_back_to_default(
    registry: DataRegistry, default_dir: Path
) -> None:
    """Default layer is used when custom does not have the file."""
    write_default(default_dir, "wishes.md", "default wishes content")

    result = registry.load_data_file("wishes.md")

    assert result == "default wishes content"


# ---------------------------------------------------------------------------
# Test 3: load_data_file returns None when file exists in neither layer
# ---------------------------------------------------------------------------


def test_load_returns_none_for_missing_file(registry: DataRegistry) -> None:
    """None returned when file is absent from both layers."""
    result = registry.load_data_file("nonexistent.json")
    assert result is None


# ---------------------------------------------------------------------------
# Test 4: save_data_file creates data/custom/ when absent
# ---------------------------------------------------------------------------


def test_save_creates_custom_dir(tmp_path: Path) -> None:
    """save_data_file creates data/custom/ (and parents) if not present."""
    # Set up: default exists but custom does NOT
    (tmp_path / "data" / "default").mkdir(parents=True)
    # custom directory intentionally absent

    reg = DataRegistry(repo_root=tmp_path)
    reg.save_data_file("new_file.json", '{"key": "value"}')

    saved = tmp_path / "data" / "custom" / "new_file.json"
    assert saved.exists(), "save_data_file did not create the file"
    assert saved.read_text(encoding="utf-8") == '{"key": "value"}'


# ---------------------------------------------------------------------------
# Test 5: save_data_file writes to custom/, never touches default/
# ---------------------------------------------------------------------------


def test_save_never_writes_to_default(
    registry: DataRegistry, default_dir: Path, custom_dir: Path
) -> None:
    """Writes land in custom/ and default/ is completely untouched."""
    write_default(default_dir, "jokes.json", '["original"]')
    default_file = default_dir / "jokes.json"
    mtime_before = default_file.stat().st_mtime

    registry.save_data_file("jokes.json", '["new version"]')

    mtime_after = default_file.stat().st_mtime
    assert mtime_before == mtime_after, "default/ file was modified — this is a bug"

    # Custom should now have the new content
    custom_file = custom_dir / "jokes.json"
    assert custom_file.exists()
    assert custom_file.read_text(encoding="utf-8") == '["new version"]'


# ---------------------------------------------------------------------------
# Test 6: save_data_file is atomic (temp file then rename)
# ---------------------------------------------------------------------------


def test_save_creates_file_atomically(
    registry: DataRegistry, custom_dir: Path
) -> None:
    """After save completes, the file is fully written (no partial state)."""
    content = json.dumps({"id": "test", "value": "atomic write test"})
    registry.save_data_file("atomic_test.json", content)

    target = custom_dir / "atomic_test.json"
    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["id"] == "test"
    assert loaded["value"] == "atomic write test"

    # No lingering .tmp_ files
    tmp_files = list(custom_dir.glob(".tmp_*"))
    assert tmp_files == [], f"Temp files not cleaned up: {tmp_files}"


# ---------------------------------------------------------------------------
# Test 7: load_all_data overlay applies custom over default
# ---------------------------------------------------------------------------


def test_load_all_data_custom_overwrites_default(
    registry: DataRegistry, default_dir: Path, custom_dir: Path
) -> None:
    """load_all_data returns a dict where custom values overwrite defaults."""
    write_default(default_dir, "jokes.json", '["default"]')
    write_default(default_dir, "combos.mermaid", "default combos")
    write_custom(custom_dir, "jokes.json", '["custom"]')

    data = registry.load_all_data()

    # custom version of jokes.json
    assert data["jokes.json"] == '["custom"]', "Custom jokes not in overlay"
    # default version of combos.mermaid (no custom override)
    assert data["combos.mermaid"] == "default combos", "Default combos missing"


# ---------------------------------------------------------------------------
# Test 8: load_all_data excludes .gitkeep sentinel
# ---------------------------------------------------------------------------


def test_load_all_data_excludes_gitkeep(
    registry: DataRegistry, default_dir: Path, custom_dir: Path
) -> None:
    """The .gitkeep sentinel must NOT appear in the returned registry."""
    write_default(default_dir, "jokes.json", "[]")
    # .gitkeep already in custom_dir from fixture

    data = registry.load_all_data()

    assert ".gitkeep" not in data, ".gitkeep sentinel leaked into registry"


# ---------------------------------------------------------------------------
# Test 9: load_all_data returns empty dict when both dirs missing
# ---------------------------------------------------------------------------


def test_load_all_data_empty_when_dirs_missing(tmp_path: Path) -> None:
    """load_all_data does not raise when data/ dirs do not exist yet."""
    # Neither default/ nor custom/ is created
    reg = DataRegistry(repo_root=tmp_path)

    data = reg.load_all_data()

    assert data == {}, f"Expected empty dict, got {data}"


# ---------------------------------------------------------------------------
# Test 10: get_file_source returns "custom" when custom exists
# ---------------------------------------------------------------------------


def test_get_file_source_custom(
    registry: DataRegistry, default_dir: Path, custom_dir: Path
) -> None:
    write_default(default_dir, "jokes.json", "[]")
    write_custom(custom_dir, "jokes.json", "[]")

    assert registry.get_file_source("jokes.json") == "custom"


# ---------------------------------------------------------------------------
# Test 11: get_file_source returns "default" when only default exists
# ---------------------------------------------------------------------------


def test_get_file_source_default(
    registry: DataRegistry, default_dir: Path
) -> None:
    write_default(default_dir, "wishes.md", "wishes")

    assert registry.get_file_source("wishes.md") == "default"


# ---------------------------------------------------------------------------
# Test 12: get_file_source returns "missing" when file in neither layer
# ---------------------------------------------------------------------------


def test_get_file_source_missing(registry: DataRegistry) -> None:
    assert registry.get_file_source("does_not_exist.json") == "missing"


# ---------------------------------------------------------------------------
# Test 13: Determinism — repeated loads return identical results
# ---------------------------------------------------------------------------


def test_repeated_loads_are_deterministic(
    registry: DataRegistry, default_dir: Path, custom_dir: Path
) -> None:
    """Two successive load_all_data calls with no writes return identical dicts."""
    write_default(default_dir, "jokes.json", '["a"]')
    write_default(default_dir, "wishes.md", "wishes")
    write_custom(custom_dir, "jokes.json", '["a-custom"]')

    first = registry.load_all_data()
    second = registry.load_all_data()

    assert first == second, "load_all_data is non-deterministic"


# ---------------------------------------------------------------------------
# Test 14: Repeated load_data_file calls return identical result
# ---------------------------------------------------------------------------


def test_load_data_file_is_deterministic(
    registry: DataRegistry, default_dir: Path
) -> None:
    """load_data_file returns the same content on every call."""
    content = '{"stable": true}'
    write_default(default_dir, "stable.json", content)

    results = [registry.load_data_file("stable.json") for _ in range(5)]

    assert all(r == content for r in results), "load_data_file returned different values"


# ---------------------------------------------------------------------------
# Test 15: Path traversal guard raises ValueError
# ---------------------------------------------------------------------------


def test_save_rejects_path_traversal(registry: DataRegistry) -> None:
    """save_data_file must reject paths that escape the custom directory."""
    with pytest.raises(ValueError, match="Path traversal"):
        registry.save_data_file("../../etc/passwd", "evil content")


# ---------------------------------------------------------------------------
# Test 16: Subdirectory support — templates/ nested files work
# ---------------------------------------------------------------------------


def test_load_nested_file_in_subdirectory(
    registry: DataRegistry, default_dir: Path
) -> None:
    """load_data_file handles subdirectory paths (e.g. templates/)."""
    (default_dir / "templates").mkdir(parents=True, exist_ok=True)
    write_default(default_dir, "templates/joke.json.template", '{"template": true}')

    result = registry.load_data_file("templates/joke.json.template")

    assert result == '{"template": true}'


def test_save_nested_file_in_subdirectory(
    registry: DataRegistry, custom_dir: Path
) -> None:
    """save_data_file creates subdirectory hierarchy in custom/."""
    registry.save_data_file("subdir/nested/data.json", '{"nested": true}')

    target = custom_dir / "subdir" / "nested" / "data.json"
    assert target.exists()
    assert '{"nested": true}' in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 17: Real data/default/ files load correctly (integration smoke)
# ---------------------------------------------------------------------------


def test_real_default_files_exist_and_load() -> None:
    """Smoke test: jokes.json, wishes.md, combos.mermaid all exist and load."""
    # Use the real repo root (DataRegistry auto-detects it)
    reg = DataRegistry()

    jokes = reg.load_data_file("jokes.json")
    wishes = reg.load_data_file("wishes.md")
    combos = reg.load_data_file("combos.mermaid")

    assert jokes is not None, "data/default/jokes.json missing or unreadable"
    assert wishes is not None, "data/default/wishes.md missing or unreadable"
    assert combos is not None, "data/default/combos.mermaid missing or unreadable"

    # jokes.json must be valid JSON array
    parsed = json.loads(jokes)
    assert isinstance(parsed, list), "jokes.json is not a JSON array"
    assert len(parsed) > 0, "jokes.json is empty"


# ---------------------------------------------------------------------------
# Test 18: get_file_source on real default files returns "default"
# ---------------------------------------------------------------------------


def test_real_default_source_returns_default() -> None:
    """get_file_source for bundled default files returns 'default' in a clean repo."""
    reg = DataRegistry()
    # Only guaranteed if custom/ does not override jokes.json
    custom_jokes = reg._custom_dir / "jokes.json"
    if custom_jokes.exists():
        pytest.skip("Custom jokes.json present — skipping source check")

    source = reg.get_file_source("jokes.json")
    assert source == "default"
