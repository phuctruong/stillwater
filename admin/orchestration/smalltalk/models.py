"""
Pydantic models for Queue-First Small Talk Twin.

All models are deterministic, offline-safe, and serializable to JSON.
No ML, no network, no randomness.

rung_target: 641 (deterministic, testable, no ML, offline-first)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# LearnedSmallTalk — new learned pattern (Phase 1 persistence equivalent)
# ---------------------------------------------------------------------------

class LearnedSmallTalk(BaseModel):
    """
    A new banter pattern discovered by the LLM and persisted.

    Stored as JSONL in ~/stillwater/data/smalltalk/learned_smalltalk.jsonl.
    Merged into the in-memory PatternRepo at startup.

    Symmetric to LearnedWish (intent/models.py) and LearnedCombo (execute/models.py).

    Sync fields (added here, as in LearnedWish and LearnedCombo):
      synced_to_firestore  — True once the Firestore write succeeds
      sync_timestamp       — UTC ISO timestamp of successful Firestore sync
      sync_attempt_count   — Number of sync attempts (capped at 5)
    """

    pattern_id: str
    """Stable identifier for this banter pattern, e.g. 'joke_016'."""

    response_template: str
    """Template string for the banter response. May contain {placeholders}."""

    keywords: List[str] = Field(default_factory=list)
    """Trigger keywords for CPU matching. Always lowercase."""

    tags: List[str] = Field(default_factory=list)
    """Category tags, e.g. ['support', 'encouragement']."""

    min_glow: float = Field(default=0.0, ge=0.0, le=1.0)
    """Minimum GLOW score for this pattern to be applicable."""

    max_glow: float = Field(default=1.0, ge=0.0, le=1.0)
    """Maximum GLOW score for this pattern to be applicable."""

    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    """Confidence in this learned pattern."""

    source: Literal["llm", "manual"] = "llm"
    """Who generated this entry."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    """
    When this entry was created locally.
    Immutable: set once, never overwritten (conflict-resolution key).
    """

    session_id: str = ""
    """Session that generated this entry."""

    # --- Sync fields (3 fields, same pattern as LearnedWish / LearnedCombo) ---

    synced_to_firestore: bool = False
    """True once successfully synced to Firestore."""

    sync_timestamp: Optional[str] = None
    """UTC ISO timestamp of the successful Firestore write. None = not yet synced."""

    sync_attempt_count: int = 0
    """Number of Firestore sync attempts. Capped at 5 by the sync worker."""

    @field_validator("keywords", mode="before")
    @classmethod
    def normalize_keywords(cls, v: List[str]) -> List[str]:
        """Force all keywords to lowercase and strip whitespace."""
        return [kw.lower().strip() for kw in v if kw.strip()]


# ---------------------------------------------------------------------------
# Register Profile — user's communication register
# ---------------------------------------------------------------------------

class RegisterProfile(BaseModel):
    """
    Captures the user's current communication register (style).

    Detected via keyword/regex matching on prompt + recent history.
    No ML involved — purely rule-based signals.
    """

    formality: Literal["formal", "casual"] = "casual"
    length: Literal["terse", "verbose"] = "terse"
    urgency: Literal["urgent", "reflective"] = "reflective"
    energy: Literal["low", "medium", "high"] = "medium"

    @property
    def glow_score(self) -> float:
        """
        Derive GLOW score from energy level.

        GLOW = emotional/communicative intensity signal.
        high   → 0.8
        medium → 0.5
        low    → 0.2
        """
        return {"low": 0.2, "medium": 0.5, "high": 0.8}[self.energy]


# ---------------------------------------------------------------------------
# Small Talk Pattern — a single banter template entry
# ---------------------------------------------------------------------------

class SmallTalkPattern(BaseModel):
    """
    One row in the in-memory pattern database.

    Loaded from patterns.jsonl at startup; never touched on hot path.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    keywords: List[str] = Field(default_factory=list)
    response_template: str
    priority: int = Field(default=2, ge=1, le=3)
    """Priority 1=always, 2=context-dependent, 3=trust-required."""

    freshness_days: int = Field(default=90, ge=1)
    min_glow: float = Field(default=0.0, ge=0.0, le=1.0)
    max_glow: float = Field(default=1.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)

    # Register filtering — None means "matches all"
    formality: Optional[Literal["formal", "casual"]] = None
    response_type: str = "warm"
    """warm, humor, affirmation, compassion, fact, celebration"""

    @field_validator("max_glow")
    @classmethod
    def max_glow_gte_min(cls, v: float, info) -> float:
        min_g = info.data.get("min_glow", 0.0)
        if v < min_g:
            raise ValueError(f"max_glow ({v}) must be >= min_glow ({min_g})")
        return v

    def matches_glow(self, glow: float) -> bool:
        return self.min_glow <= glow <= self.max_glow

    def matches_register(self, register: RegisterProfile) -> bool:
        if self.formality is not None and self.formality != register.formality:
            return False
        return True


# ---------------------------------------------------------------------------
# Banter Queue Entry — one item in the central SQLite queue
# ---------------------------------------------------------------------------

class BanterQueueEntry(BaseModel):
    """
    A single queued banter message, pre-computed and ready to serve.

    Schema mirrors the banter_queue table exactly.
    Sources:
      queue            — generic queued entry (backward-compat)
      cpu              — generated by SmallTalkCPU at fallback time
      job              — job completion webhook
      recipe           — recipe banter bank injection
      previous_session — prior session notes converted to banter
      llm_generated    — LLM background generation (future use)
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str

    banter: str
    """The ready-to-emit warm response text."""

    source: Literal[
        "queue", "cpu", "job", "recipe", "previous_session", "llm_generated"
    ] = "queue"
    source_id: Optional[str] = None
    """job_id, recipe_name, session_note_id, etc."""

    tags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    used: bool = False
    used_at: Optional[datetime] = None

    feedback_score: Optional[int] = Field(default=None, ge=1, le=5)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_available(self) -> bool:
        return (not self.used) and (not self.is_expired)


# ---------------------------------------------------------------------------
# Warm Token — the final output handed to the caller
# ---------------------------------------------------------------------------

class WarmToken(BaseModel):
    """
    The final, caller-facing response object.

    Contains the ready-to-display text plus provenance metadata
    so upstream systems (Portal, CLI, tests) can introspect where
    the response came from and how confident the system is.
    """

    response: str
    """The text to show the user."""

    source: Literal["queue_hit", "cpu_glow", "cpu_repo", "fallback"] = "fallback"
    """
    queue_hit  — came from the banter queue (<5ms SLA)
    cpu_glow   — CPU generated via GLOW + keyword template
    cpu_repo   — CPU pulled from deterministic repo (joke/weather/fact)
    fallback   — hardcoded last-resort string
    """

    pattern_id: Optional[str] = None
    queue_entry_id: Optional[str] = None

    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    latency_ms: float = 0.0
    glow_score: float = Field(default=0.5, ge=0.0, le=1.0)

    detected_register: Optional[RegisterProfile] = None
    tags: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Joke / Tech Fact repo entries (loaded from JSONL at startup)
# ---------------------------------------------------------------------------

class JokeEntry(BaseModel):
    """One row from jokes.jsonl."""

    id: str
    joke: str
    tags: List[str] = Field(default_factory=list)
    min_glow: float = Field(default=0.0, ge=0.0, le=1.0)
    max_glow: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    freshness_days: int = Field(default=30, ge=1)

    def matches_glow(self, glow: float) -> bool:
        return self.min_glow <= glow <= self.max_glow

    def matches_tags(self, query_tags: List[str]) -> bool:
        if not query_tags:
            return True
        return bool(set(self.tags) & set(query_tags))


class TechFactEntry(BaseModel):
    """One row from tech_facts.jsonl."""

    id: str
    fact: str
    tags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)

    def matches_tags(self, query_tags: List[str]) -> bool:
        if not query_tags:
            return True
        return bool(set(self.tags) & set(query_tags))


# ---------------------------------------------------------------------------
# Weather context (passed in from caller — no network here)
# ---------------------------------------------------------------------------

class WeatherContext(BaseModel):
    """
    Caller supplies weather context; we never fetch it ourselves.
    All fields optional — fallback to generic response if absent.
    """

    temp_f: Optional[float] = None
    is_raining: bool = False
    is_snowing: bool = False
    location: Optional[str] = None
    condition: Optional[str] = None
    """clear, cloudy, overcast, etc."""
