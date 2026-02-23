"""CLI sync subcommand module for stillwater data push/pull.

Version: 1.0.0 | Rung: 641 | Status: STABLE

Exposes four argparse-compatible handler functions (push, pull, status,
configure) that are wired into the main CLI via ``add_sync_subcommands()``.

Usage (after integration into cli.py):
    stillwater data sync push
    stillwater data sync pull
    stillwater data sync status
    stillwater data sync configure

Design decisions:
- Does NOT use click — the existing CLI uses argparse exclusively.
- tqdm is lazy-loaded (only when actually syncing) so offline users and
  test suites without tqdm installed are not affected.
- Offline / network errors are caught and reported as "pending" state
  with a clear, actionable message. No crash.
- API key is validated locally (format check) before attempting any
  remote call. This makes the common misconfiguration case instant.
- All output goes to stdout via print(); color via ANSI codes with a
  fallback if the terminal does not support color.

Colour helpers:
    _green(s)  -> ANSI green
    _red(s)    -> ANSI red
    _yellow(s) -> ANSI yellow
    _cyan(s)   -> ANSI cyan
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m" if _USE_COLOR else s


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m" if _USE_COLOR else s


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m" if _USE_COLOR else s


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m" if _USE_COLOR else s


# ---------------------------------------------------------------------------
# Progress bar helper (lazy tqdm)
# ---------------------------------------------------------------------------


def _progress(iterable: list, desc: str = "", unit: str = "file") -> Any:
    """Wrap iterable in tqdm if available, otherwise iterate plain."""
    try:
        from tqdm import tqdm  # type: ignore[import]
        return tqdm(iterable, desc=desc, unit=unit)
    except ImportError:
        # tqdm not installed — print a simple header and return iterable.
        if desc:
            print(f"  {desc}...")
        return iterable


# ---------------------------------------------------------------------------
# Settings + repo helpers
# ---------------------------------------------------------------------------


def _find_repo_root() -> Path:
    """Walk up from this file until we find pyproject.toml or .git."""
    candidate = Path(__file__).resolve()
    for _ in range(10):
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd()


def _load_settings(root: Path):  # noqa: ANN001
    """Return a SettingsLoader for data/settings.md relative to repo root."""
    from stillwater.settings_loader import SettingsLoader  # noqa: PLC0415
    settings_path = root / "data" / "settings.md"
    return SettingsLoader(str(settings_path))


def _custom_data_dir(root: Path) -> Path:
    return root / "data" / "custom"


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------


def add_sync_subcommands(sync_subparsers: argparse.Action) -> None:  # type: ignore[type-arg]
    """Register push/pull/status/configure sub-commands under a sync parser.

    Parameters
    ----------
    sync_subparsers:
        The ``add_subparsers()`` result from the parent ``sync`` parser.
    """
    # push
    p_push = sync_subparsers.add_parser(
        "push",
        help="Push local learned data to Firestore.",
    )
    p_push.add_argument(
        "--data-dir",
        default=None,
        help="Override path to data/custom/ (default: auto-detect from repo root).",
    )
    p_push.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without uploading.",
    )

    # pull
    p_pull = sync_subparsers.add_parser(
        "pull",
        help="Pull remote learned data from Firestore.",
    )
    p_pull.add_argument(
        "--data-dir",
        default=None,
        help="Override path to data/custom/ (default: auto-detect from repo root).",
    )
    p_pull.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading.",
    )

    # status
    sync_subparsers.add_parser(
        "status",
        help="Show sync status (last sync time, pending changes, API key).",
    )

    # configure
    sync_subparsers.add_parser(
        "configure",
        help="Interactive setup for cloud sync API key.",
    )


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def handle_sync(ns: argparse.Namespace) -> int:
    """Dispatch to the correct sync sub-command handler.

    Parameters
    ----------
    ns:
        Parsed argparse namespace.  Must have ``ns.sync_cmd`` set.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on error.
    """
    cmd = getattr(ns, "sync_cmd", None)
    if cmd == "push":
        return _handle_push(ns)
    if cmd == "pull":
        return _handle_pull(ns)
    if cmd == "status":
        return _handle_status(ns)
    if cmd == "configure":
        return _handle_configure(ns)

    print("Usage: stillwater data sync <push|pull|status|configure>")
    return 1


# ------------------------------------------------------------------
# push
# ------------------------------------------------------------------


def _handle_push(ns: argparse.Namespace) -> int:
    root = _find_repo_root()
    loader = _load_settings(root)

    api_key = loader.get_api_key()
    if api_key is None:
        print(
            _red("API key not configured.")
            + " Run: stillwater data sync configure"
        )
        return 1

    if not loader.validate_api_key(api_key):
        print(
            _red("API key format invalid.")
            + " Please generate a new one at https://solaceagi.com"
        )
        return 1

    data_dir = Path(ns.data_dir) if getattr(ns, "data_dir", None) else _custom_data_dir(root)

    if not data_dir.exists():
        print(
            _yellow("No local data directory found.")
            + f" (looked for: {data_dir})"
        )
        return 0  # nothing to push is not an error

    jsonl_files = sorted(data_dir.glob("learned_*.jsonl"))
    if not jsonl_files:
        print(_yellow("No learned_*.jsonl files found.") + " Nothing to push.")
        return 0

    print(f"Found {len(jsonl_files)} file(s) to push:")
    for f in _progress(jsonl_files, desc="Scanning", unit="file"):
        print(f"  {_cyan(f.name)}")

    if getattr(ns, "dry_run", False):
        print(_yellow("[dry-run] No files were uploaded."))
        return 0

    # Attempt push.
    from stillwater.sync_client import SyncClient  # noqa: PLC0415

    client = SyncClient(api_key=api_key)
    print("Validating API key...")
    if not client.validate_api_key():
        print(
            _red("API key invalid or revoked.")
            + " Please generate a new one at https://solaceagi.com"
        )
        return 1

    print("Uploading...")
    result = client.push_data(str(data_dir))

    if not result["success"]:
        err = result.get("error") or "unknown error"
        if _is_network_error(err):
            _queue_pending(root)
            print(
                _yellow("Network error. Offline? Changes queued for later.")
                + f"\n  detail: {err}"
            )
            return 1
        print(_red(f"Push failed: {err}"))
        return 1

    loader.update_sync_metadata(_utc_now(), "ok")
    print(
        _green("Synced")
        + f"  {result['uploaded_files']} file(s), "
        + f"{result['uploaded_records']} record(s) uploaded."
    )
    return 0


# ------------------------------------------------------------------
# pull
# ------------------------------------------------------------------


def _handle_pull(ns: argparse.Namespace) -> int:
    root = _find_repo_root()
    loader = _load_settings(root)

    api_key = loader.get_api_key()
    if api_key is None:
        print(
            _red("API key not configured.")
            + " Run: stillwater data sync configure"
        )
        return 1

    if not loader.validate_api_key(api_key):
        print(
            _red("API key format invalid.")
            + " Please generate a new one at https://solaceagi.com"
        )
        return 1

    data_dir = Path(ns.data_dir) if getattr(ns, "data_dir", None) else _custom_data_dir(root)

    if getattr(ns, "dry_run", False):
        print(_yellow("[dry-run] Pull skipped — no changes made."))
        return 0

    from stillwater.sync_client import SyncClient  # noqa: PLC0415

    client = SyncClient(api_key=api_key)
    print("Validating API key...")
    if not client.validate_api_key():
        print(
            _red("API key invalid or revoked.")
            + " Please generate a new one at https://solaceagi.com"
        )
        return 1

    print("Downloading...")
    result = client.pull_data(str(data_dir))

    if not result["success"]:
        err = result.get("error") or "unknown error"
        if _is_network_error(err):
            print(
                _yellow("Network error. Offline?")
                + " Local data unchanged.\n"
                + f"  detail: {err}"
            )
            return 1
        print(_red(f"Pull failed: {err}"))
        return 1

    loader.update_sync_metadata(_utc_now(), "ok")
    print(
        _green("Synced")
        + f"  {result['downloaded_files']} file(s), "
        + f"{result['downloaded_records']} record(s) downloaded."
    )
    if result["conflicts_resolved"]:
        print(
            f"  {_yellow('Conflicts resolved:')} {result['conflicts_resolved']}"
            + " (last-write-wins)"
        )
    return 0


# ------------------------------------------------------------------
# status
# ------------------------------------------------------------------


def _handle_status(_ns: argparse.Namespace) -> int:
    root = _find_repo_root()
    loader = _load_settings(root)

    api_key = loader.get_api_key()
    key_ok = api_key is not None and loader.validate_api_key(api_key)

    settings = loader.parse_settings()
    last_sync = settings.get("last_sync_timestamp")
    last_status = settings.get("last_sync_status", "pending")
    enabled = loader.is_sync_enabled()

    # API key display: show masked version.
    if api_key:
        key_display = f"{api_key[:10]}...{api_key[-6:]}" if len(api_key) > 16 else api_key
    else:
        key_display = "(not configured)"

    print("Sync Status")
    print("-----------")

    # API key line.
    if key_ok:
        print(f"  API key:       {_green(key_display)}")
    elif api_key:
        print(
            f"  API key:       {_red(key_display)}"
            + _red(" (invalid format)")
        )
    else:
        print(f"  API key:       {_red('not configured')}")
        print(
            "                 Run: "
            + _cyan("stillwater data sync configure")
        )

    # Enabled/disabled.
    if enabled:
        print(f"  Sync enabled:  {_green('yes')}")
    else:
        print(f"  Sync enabled:  {_yellow('no')}  (set firestore_enabled: true in data/settings.md)")

    # Last sync.
    if last_sync:
        print(f"  Last sync:     {last_sync}")
    else:
        print(f"  Last sync:     {_yellow('never')}")

    # Last status.
    if last_status == "ok":
        print(f"  Last status:   {_green('ok')}")
    elif last_status == "pending":
        print(f"  Last status:   {_yellow('pending')}")
    else:
        print(f"  Last status:   {_red(last_status)}")

    # Pending local changes.
    data_dir = _custom_data_dir(root)
    if data_dir.exists():
        pending_files = sorted(data_dir.glob("learned_*.jsonl"))
        if pending_files:
            print(f"  Local files:   {len(pending_files)} learned_*.jsonl file(s) ready to push")
        else:
            print("  Local files:   (none)")
    else:
        print("  Local files:   (data/custom/ not found)")

    return 0


# ------------------------------------------------------------------
# configure
# ------------------------------------------------------------------


def _handle_configure(_ns: argparse.Namespace) -> int:
    root = _find_repo_root()
    loader = _load_settings(root)

    print("Cloud Sync Configuration")
    print("------------------------")
    print(
        "Stillwater can back up your learned data to the cloud via Firestore.\n"
        "You need a free API key from https://solaceagi.com\n"
    )

    # Ask if user wants to enable.
    try:
        answer = input("Enable cloud sync? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 0

    if answer not in ("y", "yes"):
        print("Cloud sync not enabled. You can run this again later.")
        return 0

    # Prompt for API key.
    try:
        raw_key = input("Enter your API key (sw_sk_...): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 0

    if not raw_key:
        print(_red("No key entered. Aborted."))
        return 1

    if not loader.validate_api_key(raw_key):
        print(
            _red("Invalid key format.")
            + " Expected: sw_sk_ followed by 48 hex characters."
        )
        print(
            "Generate a key at: " + _cyan("https://solaceagi.com/settings/api-keys")
        )
        return 1

    # Optional connection test.
    try:
        test_answer = input("Test connection now? [Y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        test_answer = "n"

    if test_answer not in ("n", "no"):
        from stillwater.sync_client import SyncClient  # noqa: PLC0415
        print("Testing connection...")
        client = SyncClient(api_key=raw_key)
        ok = client.validate_api_key()
        if ok:
            print(_green("Connection OK — API key is valid."))
        else:
            print(
                _red("Connection failed.")
                + " Key not recognised. Check the key or your network."
            )
            try:
                proceed = input("Save the key anyway? [y/N]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                proceed = "n"
            if proceed not in ("y", "yes"):
                print("Key not saved. Aborted.")
                return 1

    # Persist to settings.md.
    _save_api_key(root, loader, raw_key)
    print(_green("API key saved to data/settings.md"))
    print("Run: " + _cyan("stillwater data sync push") + " to back up your data.")
    return 0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    import datetime  # noqa: PLC0415
    return datetime.datetime.now(tz=datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _is_network_error(msg: str) -> bool:
    """Return True if the error message looks like a network/connectivity issue."""
    keywords = (
        "urlopen error",
        "connection refused",
        "timed out",
        "network",
        "socket",
        "nodename",
        "no route",
        "name or service not known",
        "connectionreseterror",
        "remotedenied",
    )
    msg_lower = msg.lower()
    return any(kw in msg_lower for kw in keywords)


def _queue_pending(root: Path) -> None:
    """Write a .pending sentinel file so the user knows changes are queued."""
    pending_path = root / "data" / "custom" / ".sync_pending"
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        pending_path.write_text(f"pending since {_utc_now()}\n", encoding="utf-8")
    except OSError:
        pass  # best-effort


def _save_api_key(root: Path, loader: Any, api_key: str) -> None:
    """Persist the API key into data/settings.md."""
    settings_path = root / "data" / "settings.md"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    if settings_path.exists():
        text = settings_path.read_text(encoding="utf-8")
    else:
        text = (
            "---\n"
            "api_key: null\n"
            "firestore_project: stillwater-prod\n"
            "firestore_enabled: false\n"
            "sync_interval_seconds: 300\n"
            "last_sync_timestamp: null\n"
            "last_sync_status: pending\n"
            "---\n\n"
            "# Data Settings\n\n"
            "This file is managed by `stillwater data sync configure`.\n"
        )

    # Replace or insert api_key line in front-matter.
    lines = text.split("\n")
    new_lines: list[str] = []
    in_fm = False
    fm_closed = False
    key_written = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped == "---":
            in_fm = True
            new_lines.append(line)
            continue
        if in_fm and stripped == "---" and not fm_closed:
            fm_closed = True
            in_fm = False
            if not key_written:
                new_lines.append(f"api_key: {api_key}")
                key_written = True
            new_lines.append(line)
            continue
        if in_fm and stripped.startswith("api_key:"):
            new_lines.append(f"api_key: {api_key}")
            key_written = True
            continue
        new_lines.append(line)

    new_text = "\n".join(new_lines)

    # Also enable firestore.
    new_text = new_text.replace(
        "firestore_enabled: false", "firestore_enabled: true", 1
    )

    tmp_path = settings_path.with_suffix(".md.tmp")
    tmp_path.write_text(new_text, encoding="utf-8")
    import os  # noqa: PLC0415
    os.replace(str(tmp_path), str(settings_path))
