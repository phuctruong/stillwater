"""
Storage layer for stillwater learned entities.

Public exports:
  StorageBackend  — abstract base class
  LocalStore      — JSONL file backend (OSS default, zero network)
  FirestoreStore  — Cloud Firestore backend (lazy-imported, opt-in)
  HybridStore     — local-first + async Firestore backup
  SaveHandler     — unified save entry point (detects mode at runtime)

Usage (local-only / OSS):
  from admin.orchestration.storage import LocalStore, SaveHandler

  store = LocalStore(base_dir="~/stillwater/data/")
  handler = SaveHandler(local_store=store)
  result = handler.save_learned_wish(entry)
  # → {"success": True, "synced": False, "error": None}

Usage (hybrid / Firestore enabled):
  from admin.orchestration.storage import (
      LocalStore, FirestoreStore, HybridStore, SaveHandler
  )

  local = LocalStore(base_dir="~/stillwater/data/")
  remote = FirestoreStore(project="stillwater-prod", user_id="user_phuc")
  hybrid = HybridStore(local=local, remote=remote)
  handler = SaveHandler(local_store=local, hybrid_store=hybrid)
"""

from admin.orchestration.storage.backend import (
    FirestoreStore,
    HybridStore,
    LocalStore,
    StorageBackend,
)
from admin.orchestration.storage.save_handler import SaveHandler

__all__ = [
    "StorageBackend",
    "LocalStore",
    "FirestoreStore",
    "HybridStore",
    "SaveHandler",
]
