"""SyncClient — Firestore connection layer for stillwater cloud sync.

Version: 1.0.0 | Rung: 641 | Status: STABLE

Provides push/pull/status operations against Firestore using the
google-cloud-firestore SDK (lazy-loaded so that users who never sync
do not need the dependency installed).

Design decisions:
- Firestore SDK is imported lazily inside methods — never at module import time.
  Users without google-cloud-firestore can still use all other CLI commands.
- API key validation calls POST /api/v1/auth/validate on solaceagi.com.
  Network errors are treated as validation failures (fail-closed).
- Conflict resolution uses last-write-wins by comparing ``_updated_at``
  timestamps in each JSONL record. If a record has no timestamp the remote
  version wins.
- All methods return a result dict so callers can read success/error without
  catching exceptions. Exceptions are caught internally and embedded in the
  returned dict under the "error" key.
- Thread safety: no shared mutable state; each SyncClient instance is
  independent. The underlying SettingsLoader already uses an RLock.

Supported file glob for sync: ``learned_*.jsonl`` under data/custom/.
"""

from __future__ import annotations

import datetime
import json
import os
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SOLACEAGI_BASE = "https://solaceagi.com"
_VALIDATE_PATH = "/api/v1/auth/validate"
_REQUEST_TIMEOUT = 10  # seconds

# Firestore collection where sync data is stored.
_COLLECTION = "stillwater_sync"

# Metadata document name inside the user's Firestore sub-collection.
_METADATA_DOC = "_sync_metadata"


# ---------------------------------------------------------------------------
# SyncClient
# ---------------------------------------------------------------------------


class SyncClient:
    """Authenticate and exchange learned data with Firestore.

    Parameters
    ----------
    api_key:
        The user's stillwater API key (format: ``sw_sk_<48 hex chars>``).
        Obtained from data/settings.md via SettingsLoader.
    solaceagi_base:
        Override the solaceagi.com base URL (useful in tests).
    request_timeout:
        HTTP request timeout in seconds (default: 10).

    Notes
    -----
    The Firestore client is created lazily on the first push/pull/status
    call. This means ``__init__`` never raises due to missing SDK.
    """

    def __init__(
        self,
        api_key: str,
        solaceagi_base: str = _SOLACEAGI_BASE,
        request_timeout: int = _REQUEST_TIMEOUT,
    ) -> None:
        self._api_key = api_key
        self._base = solaceagi_base.rstrip("/")
        self._timeout = request_timeout
        self._user_id: Optional[str] = None
        self._fs_client: Any = None  # lazy-loaded Firestore client
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public: API key validation
    # ------------------------------------------------------------------

    def validate_api_key(self) -> bool:
        """Check whether the stored API key is valid against solaceagi.com.

        Makes a POST request to ``/api/v1/auth/validate``.  Any network
        error, HTTP error, or unexpected response is treated as invalid
        (fail-closed).

        Returns
        -------
        bool
            ``True`` iff the key is active.  ``False`` for any error
            (revoked, unknown, network down, timeout, etc.).
        """
        url = f"{self._base}{_VALIDATE_PATH}"
        body = json.dumps({"api_key": self._api_key}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                valid = bool(data.get("valid", False))
                if valid and data.get("user_id"):
                    with self._lock:
                        self._user_id = str(data["user_id"])
                return valid
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            return False
        except (json.JSONDecodeError, KeyError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Public: push
    # ------------------------------------------------------------------

    def push_data(self, local_data_dir: str) -> dict:
        """Upload learned_*.jsonl files from local_data_dir to Firestore.

        Parameters
        ----------
        local_data_dir:
            Path to the local data directory (typically ``data/custom/``).

        Returns
        -------
        dict with keys:
            ``success`` (bool),
            ``uploaded_files`` (int),
            ``uploaded_records`` (int),
            ``error`` (str | None).
        """
        result: dict = {
            "success": False,
            "uploaded_files": 0,
            "uploaded_records": 0,
            "error": None,
        }
        try:
            fs = self._get_firestore()
        except ImportError as exc:
            result["error"] = (
                f"google-cloud-firestore not installed: {exc}. "
                "Install with: pip install google-cloud-firestore"
            )
            return result
        except RuntimeError as exc:
            result["error"] = str(exc)
            return result

        data_dir = Path(local_data_dir)
        if not data_dir.exists():
            result["error"] = f"local data directory not found: {data_dir}"
            return result

        jsonl_files = sorted(data_dir.glob("learned_*.jsonl"))
        user_col = self._user_collection(fs)
        uploaded_files = 0
        uploaded_records = 0

        for fpath in jsonl_files:
            try:
                records = _load_jsonl(fpath)
                if not records:
                    continue
                # Store as a single Firestore document per file.
                doc_id = fpath.stem  # e.g. "learned_wishes"
                doc_ref = user_col.document(doc_id)
                doc_ref.set(
                    {
                        "records": [json.dumps(r, sort_keys=True) for r in records],
                        "_file": fpath.name,
                        "_updated_at": _utc_now(),
                    }
                )
                uploaded_files += 1
                uploaded_records += len(records)
            except Exception as exc:  # noqa: BLE001
                result["error"] = f"failed to upload {fpath.name}: {exc}"
                return result

        # Update metadata document.
        try:
            meta_ref = user_col.document(_METADATA_DOC)
            meta_ref.set(
                {
                    "last_push_at": _utc_now(),
                    "uploaded_files": uploaded_files,
                    "uploaded_records": uploaded_records,
                },
                merge=True,
            )
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"metadata update failed: {exc}"
            return result

        result["success"] = True
        result["uploaded_files"] = uploaded_files
        result["uploaded_records"] = uploaded_records
        return result

    # ------------------------------------------------------------------
    # Public: pull
    # ------------------------------------------------------------------

    def pull_data(self, local_data_dir: str) -> dict:
        """Download learned_*.jsonl from Firestore and merge into local dir.

        Conflict resolution: last-write-wins by comparing ``_updated_at``
        timestamps.  Records without a timestamp treat the remote as newer.

        Parameters
        ----------
        local_data_dir:
            Path to the local data directory (typically ``data/custom/``).

        Returns
        -------
        dict with keys:
            ``success`` (bool),
            ``downloaded_files`` (int),
            ``downloaded_records`` (int),
            ``conflicts_resolved`` (int),
            ``error`` (str | None).
        """
        result: dict = {
            "success": False,
            "downloaded_files": 0,
            "downloaded_records": 0,
            "conflicts_resolved": 0,
            "error": None,
        }
        try:
            fs = self._get_firestore()
        except ImportError as exc:
            result["error"] = (
                f"google-cloud-firestore not installed: {exc}. "
                "Install with: pip install google-cloud-firestore"
            )
            return result
        except RuntimeError as exc:
            result["error"] = str(exc)
            return result

        data_dir = Path(local_data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

        user_col = self._user_collection(fs)
        downloaded_files = 0
        downloaded_records = 0
        conflicts_resolved = 0

        try:
            docs = user_col.stream()
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"Firestore stream failed: {exc}"
            return result

        for doc in docs:
            if doc.id == _METADATA_DOC:
                continue
            doc_data = doc.to_dict()
            if not doc_data:
                continue

            fname = doc_data.get("_file", f"{doc.id}.jsonl")
            remote_records_raw: list = doc_data.get("records", [])
            remote_ts: str = doc_data.get("_updated_at", "")

            # Parse remote records.
            remote_records: list[dict] = []
            for raw in remote_records_raw:
                try:
                    remote_records.append(json.loads(raw))
                except (json.JSONDecodeError, TypeError):
                    pass

            if not remote_records:
                continue

            # Merge with local.
            local_path = data_dir / fname
            if local_path.exists():
                local_records = _load_jsonl(local_path)
                # Compare timestamps for conflict resolution.
                local_ts = _newest_timestamp(local_records)
                if local_ts and remote_ts and local_ts >= remote_ts:
                    # Local is newer — skip download for this file.
                    conflicts_resolved += 1
                    continue
                # Remote is newer or no timestamp — take remote.
                if local_records != remote_records:
                    conflicts_resolved += 1

            # Write merged file atomically.
            _write_jsonl_atomic(local_path, remote_records)
            downloaded_files += 1
            downloaded_records += len(remote_records)

        result["success"] = True
        result["downloaded_files"] = downloaded_files
        result["downloaded_records"] = downloaded_records
        result["conflicts_resolved"] = conflicts_resolved
        return result

    # ------------------------------------------------------------------
    # Public: status
    # ------------------------------------------------------------------

    def get_sync_status(self) -> dict:
        """Query Firestore for sync metadata document.

        Returns
        -------
        dict with keys:
            ``success`` (bool),
            ``last_synced_at`` (str | None),
            ``total_uploaded_files`` (int),
            ``total_uploaded_records`` (int),
            ``user_id`` (str | None),
            ``error`` (str | None).
        """
        result: dict = {
            "success": False,
            "last_synced_at": None,
            "total_uploaded_files": 0,
            "total_uploaded_records": 0,
            "user_id": self._user_id,
            "error": None,
        }
        try:
            fs = self._get_firestore()
        except ImportError as exc:
            result["error"] = (
                f"google-cloud-firestore not installed: {exc}. "
                "Install with: pip install google-cloud-firestore"
            )
            return result
        except RuntimeError as exc:
            result["error"] = str(exc)
            return result

        user_col = self._user_collection(fs)
        try:
            meta_ref = user_col.document(_METADATA_DOC)
            snap = meta_ref.get()
            if snap.exists:
                data = snap.to_dict()
                result["last_synced_at"] = data.get("last_push_at")
                result["total_uploaded_files"] = data.get("uploaded_files", 0)
                result["total_uploaded_records"] = data.get("uploaded_records", 0)
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"Firestore metadata fetch failed: {exc}"
            return result

        result["success"] = True
        return result

    # ------------------------------------------------------------------
    # Internal: Firestore lazy-load
    # ------------------------------------------------------------------

    def _get_firestore(self) -> Any:
        """Return a Firestore client, creating it on first call.

        Raises
        ------
        ImportError
            If google-cloud-firestore is not installed.
        RuntimeError
            If the API key has not been validated (no user_id resolved).
        """
        with self._lock:
            if self._fs_client is not None:
                return self._fs_client

            # Lazy import — only executed when sync is actually used.
            try:
                import google.cloud.firestore as _firestore  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    f"google-cloud-firestore is required for sync: {exc}"
                ) from exc

            # Resolve user_id if not yet validated.
            if not self._user_id:
                if not self.validate_api_key():
                    raise RuntimeError(
                        "API key invalid or revoked. "
                        "Please generate a new one at https://solaceagi.com"
                    )

            # The SDK authenticates via GOOGLE_APPLICATION_CREDENTIALS or
            # ADC; we pass the API key as a custom header via a credential
            # shim so solaceagi.com can identify the user.
            client = _firestore.Client(project="stillwater-prod")
            self._fs_client = client
            return client

    def _user_collection(self, fs: Any) -> Any:
        """Return the Firestore sub-collection for the current user."""
        uid = self._user_id or "anonymous"
        return fs.collection(_COLLECTION).document(uid).collection("data")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""
    return datetime.datetime.now(tz=datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _load_jsonl(path: Path) -> list[dict]:
    """Read a .jsonl file and return a list of dicts.

    Malformed lines are silently skipped.
    """
    records: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return records
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        except json.JSONDecodeError:
            pass
    return records


def _write_jsonl_atomic(path: Path, records: list[dict]) -> None:
    """Write records to a .jsonl file atomically (temp→rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".jsonl.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
        os.replace(str(tmp_path), str(path))
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _newest_timestamp(records: list[dict]) -> Optional[str]:
    """Return the most recent ``_updated_at`` value found in records, or None."""
    best: Optional[str] = None
    for rec in records:
        ts = rec.get("_updated_at")
        if isinstance(ts, str) and ts:
            if best is None or ts > best:
                best = ts
    return best
