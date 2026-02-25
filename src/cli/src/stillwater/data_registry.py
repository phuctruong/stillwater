"""DataRegistry — layered data overlay system for stillwater.

Provides a read-write overlay where:
  - data/default/  is the canonical, git-tracked read-only layer
  - data/custom/   is the user's local layer (gitignored, never committed)

Rules enforced by this module:
  1. Reads: custom/ wins, default/ is the fallback
  2. Writes: always go to custom/ — NEVER to default/
  3. data/default/ is NEVER written by application code

Rung: 641 — deterministic, no network, testable.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Optional


def _find_repo_root() -> Path:
    """Walk up from this file's location until we find the repo root.

    The repo root is identified by the presence of ``pyproject.toml``
    (or ``.git``).  This is repo-relative so no absolute paths are
    hard-coded anywhere in the module.
    """
    candidate = Path(__file__).resolve()
    for _ in range(10):  # bounded ascent — never infinite
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    # Fallback: cwd (useful in tests that temporarily chdir)
    return Path.cwd()


class DataRegistry:
    """Layered data overlay — custom/ wins over default/.

    Parameters
    ----------
    repo_root:
        Path to the repository root.  Defaults to auto-detection via
        ``_find_repo_root()``.  Pass an explicit path in tests so the
        registry points at a temporary directory instead of the real repo.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        if repo_root is None:
            repo_root = _find_repo_root()
        self._root = Path(repo_root)
        self._default_dir = self._root / "data" / "default"
        self._custom_dir = self._root / "data" / "custom"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_data_file(self, relative_path: str) -> Optional[str]:
        """Return the content of *relative_path*, custom/ wins over default/.

        Parameters
        ----------
        relative_path:
            Path relative to either ``data/default/`` or ``data/custom/``,
            e.g. ``"jokes.json"`` or ``"templates/joke.json.template"``.

        Returns
        -------
        str | None
            The raw text content, or ``None`` if the file does not exist in
            either layer.  Malformed files (e.g. permission errors) are
            skipped gracefully and the next layer is tried.
        """
        custom_path = self._custom_dir / relative_path
        default_path = self._default_dir / relative_path

        for path in (custom_path, default_path):
            content = self._read_safe(path)
            if content is not None:
                return content

        return None

    def save_data_file(self, relative_path: str, content: str) -> None:
        """Write *content* to ``data/custom/<relative_path>``.

        Writes are NEVER sent to ``data/default/``.  The write is atomic:
        content is written to a sibling temp file, then renamed into place.

        Parameters
        ----------
        relative_path:
            Destination path relative to ``data/custom/``.
        content:
            Text to write.

        Raises
        ------
        ValueError
            If *relative_path* would escape the custom directory (path
            traversal guard).
        """
        target = self._custom_dir / relative_path

        # Path traversal guard: resolved target must live inside custom_dir
        resolved_target = target.resolve()
        resolved_custom = self._custom_dir.resolve()
        try:
            resolved_target.relative_to(resolved_custom)
        except ValueError:
            raise ValueError(
                f"Path traversal detected: {relative_path!r} escapes custom directory"
            )

        # Ensure parent directories exist
        target.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: temp file → rename
        fd, tmp_path = tempfile.mkstemp(dir=target.parent, prefix=".tmp_")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(content)
            os.replace(tmp_path, target)
        except Exception:
            # Clean up temp file on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def load_all_data(self) -> dict:
        """Walk default/ then overlay custom/ — returns unified registry.

        The returned dict maps ``relative_path`` (str) → file content (str).
        Custom versions silently overwrite default versions for the same key.
        The ``.gitkeep`` sentinel is excluded from the result.

        Returns
        -------
        dict[str, str]
            Mapping of ``relative_path`` → content.  Malformed or unreadable
            files are skipped.
        """
        registry: dict = {}

        # Step 1: Walk default/ — canonical baseline
        if self._default_dir.exists():
            for abs_path in sorted(self._default_dir.rglob("*")):
                if abs_path.is_file():
                    rel = abs_path.relative_to(self._default_dir).as_posix()
                    content = self._read_safe(abs_path)
                    if content is not None:
                        registry[rel] = content

        # Step 2: Walk custom/ — overwrite with user versions
        if self._custom_dir.exists():
            for abs_path in sorted(self._custom_dir.rglob("*")):
                if abs_path.is_file():
                    rel = abs_path.relative_to(self._custom_dir).as_posix()
                    if rel == ".gitkeep":
                        continue  # sentinel — never surfaced to callers
                    content = self._read_safe(abs_path)
                    if content is not None:
                        registry[rel] = content

        return registry

    def get_file_source(self, relative_path: str) -> str:
        """Return which layer owns *relative_path*.

        Returns
        -------
        str
            ``"custom"``  — file exists in data/custom/
            ``"default"`` — file exists in data/default/ (not in custom/)
            ``"missing"`` — file exists in neither layer
        """
        if (self._custom_dir / relative_path).exists():
            return "custom"
        if (self._default_dir / relative_path).exists():
            return "default"
        return "missing"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_safe(self, path: Path) -> Optional[str]:
        """Read *path* as UTF-8 text; return None on any failure."""
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    # ------------------------------------------------------------------
    # Convenience: never-write-to-default guard (callable from tests)
    # ------------------------------------------------------------------

    def _assert_default_untouched(self) -> None:
        """Raise AssertionError if any default file was modified since the
        registry was created.  Not called by production code; available for
        test assertions."""
        # We do not snapshot mtimes at __init__ time because that would be
        # expensive.  Tests that need this guarantee should simply stat the
        # files before and after the code-under-test runs.
        raise NotImplementedError(
            "Use direct Path.stat() comparisons in tests — this guard is for documentation only."
        )
