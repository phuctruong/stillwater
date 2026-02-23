"""
ExecutionCPU — CPU-side execution matcher for the Execution Twin (Phase 3).

Architecture (from SMALLTALK_TWIN_BRAINSTORM.md Phase 3):

  wish_id (from Phase 2 Intent Twin)
    |
    v
  1. Direct wish_id lookup in combo database (< 0.1ms)
     O(1) dict lookup → {swarm, recipe, confidence}
    |
    v
  2. Return ExecutionMatch or None (if no combo found)
     Falls back to None if wish_id not in database
    |
    v
  ExecutionMatch(wish_id, swarm, recipe, confidence, source="cpu")

No network. No ML. No randomness. All deterministic.
Dict lookups are O(1) — fastest possible hot path.

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

import time
from typing import Optional

from .database import ComboDB, ComboLookupLog
from .models import ComboLookupEntry, ExecutionMatch


# ---------------------------------------------------------------------------
# ExecutionCPU
# ---------------------------------------------------------------------------

class ExecutionCPU:
    """
    CPU-side execution matcher.

    Instantiate once with a loaded ComboDB.
    Call match() with a wish_id from the Intent Twin (Phase 2).

    Hot path budget: < 1ms total (O(1) dict lookup).

    Thread-safe (read-only access to ComboDB after init).
    """

    def __init__(
        self,
        combo_db: ComboDB,
        lookup_log: Optional[ComboLookupLog] = None,
    ) -> None:
        """
        Args:
            combo_db:   Loaded ComboDB (must be pre-loaded before calling match()).
            lookup_log: Optional log for CPU match events (for LLM feedback).
        """
        self._db = combo_db
        self._log = lookup_log

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        wish_id: str,
        context: Optional[dict] = None,
        session_id: str = "",
    ) -> Optional[ExecutionMatch]:
        """
        Match a wish_id to a concrete execution plan.

        Args:
            wish_id:    The wish ID from Phase 2 Intent Twin.
            context:    Optional dict with extra hints (currently unused on hot path).
            session_id: Session identifier (for lookup log).

        Returns:
            ExecutionMatch if a combo was found, None otherwise.

        Performance:
            O(1) dict lookup. P99 target: < 1ms.
        """
        context = context or {}
        t_start = time.perf_counter()

        # O(1) direct lookup
        combo = self._db.get(wish_id)

        latency_ms = (time.perf_counter() - t_start) * 1000

        # Log event (for LLM feedback loop)
        if self._log is not None:
            log_entry = ComboLookupEntry(
                wish_id=wish_id,
                cpu_match=combo.wish_id if combo else None,
                cpu_swarm=combo.swarm if combo else None,
                cpu_recipe=list(combo.recipe) if combo else [],
                cpu_confidence=combo.confidence if combo else 0.0,
                session_id=session_id,
            )
            self._log.record(log_entry)

        if combo is None:
            return None

        return ExecutionMatch(
            wish_id=combo.wish_id,
            swarm=combo.swarm,
            recipe=list(combo.recipe),
            confidence=combo.confidence,
            source="cpu",
            latency_ms=latency_ms,
        )

    def match_batch(
        self,
        wish_ids: list,
        session_id: str = "",
    ) -> list:
        """
        Match multiple wish_ids in a single call.

        Args:
            wish_ids:   List of wish IDs to match.
            session_id: Session identifier (for lookup log).

        Returns:
            List of (wish_id, ExecutionMatch | None) tuples.

        Useful for pipeline pre-warming or batch execution planning.
        """
        return [
            (wid, self.match(wid, session_id=session_id))
            for wid in wish_ids
        ]
