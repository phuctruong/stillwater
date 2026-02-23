"""
SaveHandler — unified save entry point for all learned entities.

Routes writes to the appropriate backend (LocalStore or HybridStore)
based on runtime configuration. Returns a status dict for every save.

Status dict contract:
  {
    "success": bool,   # True if local write succeeded (local must always succeed)
    "synced":  bool,   # True if also written to remote (Firestore) synchronously
    "error":   str|None  # Error message on failure, None on success
  }

Rules:
  - Local write MUST succeed; any local failure → success=False
  - Firestore failure is non-fatal → success=True, synced=False
  - HybridStore enqueues Firestore writes asynchronously → synced=False at return time
    (synced becomes True only when the background worker confirms the write)

Rung: 641
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from admin.orchestration.intent.models import LearnedWish
from admin.orchestration.execute.models import LearnedCombo
from admin.orchestration.smalltalk.models import LearnedSmallTalk
from admin.orchestration.storage.backend import HybridStore, LocalStore, StorageBackend

logger = logging.getLogger(__name__)


class SaveHandler:
    """
    Detects storage mode at runtime and routes saves accordingly.

    Instantiation:
      # Local-only mode (OSS default):
      handler = SaveHandler(local_store=LocalStore(base_dir="~/stillwater/data/"))

      # Hybrid mode (Firestore enabled):
      handler = SaveHandler(
          local_store=LocalStore(...),
          hybrid_store=HybridStore(local=..., remote=FirestoreStore(...)),
      )

    When hybrid_store is supplied, all saves go through HybridStore.
    When only local_store is supplied, all saves go through LocalStore directly.

    The caller never needs to know which backend is active — just call save_*().
    """

    def __init__(
        self,
        local_store: LocalStore,
        hybrid_store: Optional[HybridStore] = None,
    ) -> None:
        """
        Args:
            local_store:  LocalStore instance (always required).
            hybrid_store: HybridStore instance (optional; activates Firestore backup).
        """
        self._local = local_store
        self._hybrid = hybrid_store
        self._backend: StorageBackend = hybrid_store if hybrid_store is not None else local_store

    # ------------------------------------------------------------------ #
    # Public save API
    # ------------------------------------------------------------------ #

    def save_learned_wish(self, entry: LearnedWish) -> Dict[str, Any]:
        """
        Persist a LearnedWish.

        Returns:
            {"success": bool, "synced": bool, "error": str|None}
        """
        return self._save("save_learned_wish", entry)

    def save_learned_combo(self, entry: LearnedCombo) -> Dict[str, Any]:
        """
        Persist a LearnedCombo.

        Returns:
            {"success": bool, "synced": bool, "error": str|None}
        """
        return self._save("save_learned_combo", entry)

    def save_learned_smalltalk(self, entry: LearnedSmallTalk) -> Dict[str, Any]:
        """
        Persist a LearnedSmallTalk.

        Returns:
            {"success": bool, "synced": bool, "error": str|None}
        """
        return self._save("save_learned_smalltalk", entry)

    # ------------------------------------------------------------------ #
    # Private
    # ------------------------------------------------------------------ #

    def _save(self, method_name: str, entry: Any) -> Dict[str, Any]:
        """
        Call the appropriate save method on the active backend.

        Always catches exceptions and returns a structured status dict.
        Never raises.
        """
        try:
            method = getattr(self._backend, method_name)
            method(entry)
            return {"success": True, "synced": False, "error": None}
        except Exception as exc:
            logger.error("SaveHandler.%s failed: %s", method_name, exc)
            return {"success": False, "synced": False, "error": str(exc)}

    # ------------------------------------------------------------------ #
    # Inspection helpers
    # ------------------------------------------------------------------ #

    @property
    def is_hybrid(self) -> bool:
        """True if using HybridStore (Firestore backup active)."""
        return self._hybrid is not None

    @property
    def backend(self) -> StorageBackend:
        """The active StorageBackend instance."""
        return self._backend
