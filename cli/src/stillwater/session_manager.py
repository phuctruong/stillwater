"""
Stillwater Session Manager
Version: 1.0.0 | Auth: 641 | Status: STABLE

Tracks active LLM sessions with skill packs, evidence dirs, and expiry.

A Session represents a single interactive context window (e.g. a phuc-swarm run
or a CLI session). Sessions are stored in memory only — they are ephemeral and
do not persist across process restarts. For persistent session logging see
~/.stillwater/llm_calls.jsonl.

Usage:
    from stillwater.session_manager import SessionManager

    mgr = SessionManager()
    session = mgr.create_session(skill_pack=["prime-safety", "prime-coder"])
    print(session.session_id)  # UUID string
    print(session.is_expired())  # False (just created)

    found = mgr.get_session(session.session_id)  # returns Session or None
    mgr.close_session(session.session_id)         # marks closed, cleans up
    active = mgr.list_active()                    # [Session, ...]

Session expiry:
    Default TTL: 86400 seconds (24h).
    Expired sessions are returned as None by get_session().
    close_session() is idempotent for already-closed sessions (no-op).

Null safety:
    - get_session on unknown ID → None (not an error)
    - close_session on unknown ID → no-op (not an error)
    - list_active() never raises; returns []
    - All timestamps are int (UNIX seconds) — never float in comparisons
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_TTL_SECONDS: int = 86400  # 24 hours


# ---------------------------------------------------------------------------
# Session dataclass
# ---------------------------------------------------------------------------


@dataclass
class Session:
    """A single LLM session context.

    Fields:
        session_id:   UUID4 string — primary key.
        skill_pack:   List of skill names loaded into this session.
        active_task:  Short description of the current task (or None).
        evidence_dir: Path string where evidence is stored (or None).
        created_at:   UNIX timestamp (int) of creation.
        expires_at:   UNIX timestamp (int) after which the session is expired.
        closed:       True iff the session was explicitly closed.
    """

    session_id: str
    skill_pack: list[str]
    active_task: Optional[str]
    evidence_dir: Optional[str]
    created_at: int
    expires_at: int
    closed: bool = field(default=False)

    def is_expired(self) -> bool:
        """Return True iff the session has expired (expires_at <= now) or is closed."""
        if self.closed:
            return True
        now_int = int(time.time())
        return now_int >= self.expires_at

    def is_active(self) -> bool:
        """Return True iff the session is not expired and not closed."""
        return not self.is_expired()

    def ttl_remaining_seconds(self) -> int:
        """Return seconds remaining until expiry. Returns 0 if already expired."""
        now_int = int(time.time())
        remaining = self.expires_at - now_int
        return max(0, remaining)

    def to_dict(self) -> dict:
        """Serialize to a plain dict (for JSON logging / debugging)."""
        return {
            "session_id": self.session_id,
            "skill_pack": list(self.skill_pack),
            "active_task": self.active_task,
            "evidence_dir": self.evidence_dir,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "closed": self.closed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Session":
        """Reconstruct a Session from a plain dict.

        Null safety: missing optional fields default to None/False.
        """
        return cls(
            session_id=d["session_id"],
            skill_pack=list(d.get("skill_pack", [])),
            active_task=d.get("active_task"),
            evidence_dir=d.get("evidence_dir"),
            created_at=int(d["created_at"]),
            expires_at=int(d["expires_at"]),
            closed=bool(d.get("closed", False)),
        )


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------


class SessionManager:
    """In-memory session registry with TTL-based expiry.

    Thread-safe: all mutations are protected by a single lock.

    Args:
        default_ttl_seconds: Default session lifetime in seconds (default: 86400 = 24h).
    """

    def __init__(self, default_ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> None:
        if default_ttl_seconds <= 0:
            raise ValueError(
                f"default_ttl_seconds must be positive, got {default_ttl_seconds}"
            )
        self._ttl_seconds: int = default_ttl_seconds
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def create_session(
        self,
        skill_pack: list[str],
        active_task: Optional[str] = None,
        evidence_dir: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Session:
        """Create and register a new session.

        Args:
            skill_pack:   List of skill names to load (e.g. ['prime-safety', 'prime-coder']).
            active_task:  Optional short description of the current task.
            evidence_dir: Optional path to the evidence directory for this session.
            ttl_seconds:  Session lifetime in seconds (default: manager default_ttl_seconds).

        Returns:
            The newly created Session.

        Raises:
            ValueError: if skill_pack is not a list.
        """
        if not isinstance(skill_pack, list):
            raise ValueError(f"skill_pack must be a list, got {type(skill_pack).__name__}")

        ttl = ttl_seconds if ttl_seconds is not None else self._ttl_seconds
        now_int = int(time.time())

        session = Session(
            session_id=str(uuid.uuid4()),
            skill_pack=list(skill_pack),
            active_task=active_task,
            evidence_dir=evidence_dir,
            created_at=now_int,
            expires_at=now_int + ttl,
            closed=False,
        )

        with self._lock:
            self._sessions[session.session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Return the session for the given ID, or None if not found or expired.

        Expired sessions are treated as absent — returns None.

        Args:
            session_id: UUID string of the session.

        Returns:
            Session if found and active; None otherwise.
        """
        with self._lock:
            session = self._sessions.get(session_id)

        if session is None:
            return None

        # Return None for expired sessions (expired = not found)
        if session.is_expired():
            return None

        return session

    def close_session(self, session_id: str) -> None:
        """Close (terminate) a session and clean up its resources.

        Idempotent: calling on an unknown or already-closed session is a no-op.

        Args:
            session_id: UUID string of the session to close.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                session.closed = True

    def list_active(self) -> list[Session]:
        """Return all active (non-expired, non-closed) sessions.

        Returns:
            List of Session objects sorted by created_at ascending.
        """
        with self._lock:
            sessions = list(self._sessions.values())

        active = [s for s in sessions if s.is_active()]
        active.sort(key=lambda s: s.created_at)
        return active

    def list_all(self) -> list[Session]:
        """Return all sessions including expired and closed ones.

        Returns:
            List of Session objects sorted by created_at ascending.
        """
        with self._lock:
            sessions = list(self._sessions.values())

        sessions.sort(key=lambda s: s.created_at)
        return sessions

    def purge_expired(self) -> int:
        """Remove expired and closed sessions from memory.

        Returns:
            Number of sessions removed.
        """
        with self._lock:
            expired_ids = [
                sid for sid, s in self._sessions.items() if s.is_expired()
            ]
            for sid in expired_ids:
                del self._sessions[sid]

        return len(expired_ids)

    def session_count(self) -> int:
        """Return total number of sessions (including expired/closed) in memory."""
        with self._lock:
            return len(self._sessions)
