"""
Pydantic models for Intent Twin (Phase 2).

Maps user prompts to "wishes" (intent/task categories) using
deterministic keyword-based CPU matching.

All models are offline-safe, serializable to JSON, no ML, no network.

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Wish — a named intent category with keyword hints
# ---------------------------------------------------------------------------

class Wish(BaseModel):
    """
    A named intent/task category that the user might be requesting.

    Loaded from wishes.jsonl at startup.
    Immutable on hot path.
    """

    id: str
    """Stable identifier, e.g. 'oauth-integration', 'database-optimization'."""

    name: str
    """Human-readable name, e.g. 'OAuth Integration'."""

    description: str = ""
    """Optional description of what this wish covers."""

    keywords: List[str] = Field(default_factory=list)
    """
    Trigger keywords for CPU matching.
    All lowercase. Matched case-insensitively against extracted prompt tokens.
    """

    skill_pack_hint: str = ""
    """
    Comma-separated skill pack suggestion, e.g. 'coder+security'.
    Used to warm-cache the right skill pack for this wish.
    """

    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    """
    Prior confidence that this wish is correctly defined.
    Higher = more reliable keyword set.
    """

    category: str = "general"
    """
    Grouping tag for filtering, e.g. 'security', 'performance', 'devops'.
    """

    @field_validator("keywords", mode="before")
    @classmethod
    def normalize_keywords(cls, v: List[str]) -> List[str]:
        """Ensure all keywords are lowercase and stripped."""
        return [kw.lower().strip() for kw in v if kw.strip()]

    @field_validator("id")
    @classmethod
    def id_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError(f"Wish id must not contain spaces: {v!r}")
        return v.lower()


# ---------------------------------------------------------------------------
# IntentMatch — result of a CPU or LLM match attempt
# ---------------------------------------------------------------------------

class IntentMatch(BaseModel):
    """
    The result of matching a user prompt to a wish.

    Produced by IntentCPU.match() or LLM validation layer.
    """

    wish_id: str
    """ID of the matched Wish."""

    matched_keywords: List[str] = Field(default_factory=list)
    """Which keywords from the wish's keyword list were found in the prompt."""

    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    """
    How confident the match is.
    CPU: keyword overlap ratio * wish.confidence
    LLM: model-returned confidence
    """

    source: Literal["cpu", "llm"] = "cpu"
    """Which path produced this match."""

    latency_ms: float = 0.0
    """Time taken to produce this match (wall clock ms)."""

    prompt_tokens: List[str] = Field(default_factory=list)
    """Extracted tokens from the prompt used for matching."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# WishDatabase — in-memory dict of id → Wish
# ---------------------------------------------------------------------------

class WishDatabase(BaseModel):
    """
    In-memory container for all loaded wishes.

    Supports O(1) lookup by id and keyword-indexed search.
    Loaded at startup from wishes.jsonl + learned_wishes.jsonl.
    """

    wishes: Dict[str, Wish] = Field(default_factory=dict)
    """Primary store: wish_id → Wish."""

    # Keyword index: keyword → list of wish_ids (built at load time)
    _keyword_index: Dict[str, List[str]] = {}

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context) -> None:
        """Build keyword index after construction."""
        self._keyword_index = {}
        for wish in self.wishes.values():
            for kw in wish.keywords:
                if kw not in self._keyword_index:
                    self._keyword_index[kw] = []
                self._keyword_index[kw].append(wish.id)

    def add(self, wish: Wish) -> None:
        """Add a wish and update the keyword index."""
        self.wishes[wish.id] = wish
        for kw in wish.keywords:
            if kw not in self._keyword_index:
                self._keyword_index[kw] = []
            if wish.id not in self._keyword_index[kw]:
                self._keyword_index[kw].append(wish.id)

    def get(self, wish_id: str) -> Optional[Wish]:
        """Look up a wish by id. Returns None if not found."""
        return self.wishes.get(wish_id)

    def lookup_by_keyword(self, keyword: str) -> List[Wish]:
        """
        Return all wishes that have this keyword.

        Deterministic: returns wishes in insertion order of their ids.
        """
        ids = self._keyword_index.get(keyword.lower(), [])
        return [self.wishes[wid] for wid in ids if wid in self.wishes]

    def count(self) -> int:
        return len(self.wishes)

    def all_wishes(self) -> List[Wish]:
        return list(self.wishes.values())


# ---------------------------------------------------------------------------
# LookupEntry — tracks a single CPU match event for LLM learning
# ---------------------------------------------------------------------------

class LookupEntry(BaseModel):
    """
    Records a single CPU lookup event.

    Stored in the lookup log so the LLM feedback loop can confirm or
    correct CPU matches and generate new learned_wishes.
    """

    prompt: str
    """The original user prompt."""

    prompt_tokens: List[str] = Field(default_factory=list)
    """Extracted tokens from the prompt."""

    cpu_match: Optional[str] = None
    """Wish ID the CPU matched (None = CPU miss)."""

    cpu_confidence: float = 0.0
    """CPU match confidence."""

    llm_confirmed: Optional[bool] = None
    """None = not yet validated. True = LLM confirmed. False = LLM corrected."""

    llm_wish_id: Optional[str] = None
    """Wish ID the LLM determined (may differ from cpu_match on correction)."""

    llm_new_keywords: List[str] = Field(default_factory=list)
    """New keywords the LLM suggests adding to the matched wish."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session_id: str = ""


# ---------------------------------------------------------------------------
# LearnedWish — an entry added to learned_wishes.jsonl
# ---------------------------------------------------------------------------

class LearnedWish(BaseModel):
    """
    A new keyword→wish_id mapping discovered by the LLM and persisted.

    Stored as JSONL in learned_wishes.jsonl.
    Merged into the main WishDatabase on startup.

    Sync fields (backward-compatible: optional on deserialization from old JSONL):
      synced_to_firestore  — True once the Firestore write succeeds
      sync_timestamp       — UTC ISO timestamp of successful sync (None = not yet synced)
      sync_attempt_count   — Number of sync attempts (capped at 5 by sync worker)
    """

    wish_id: str
    """Which wish these keywords belong to."""

    keywords: List[str] = Field(default_factory=list)
    """New keywords to add to the wish."""

    skill_pack_hint: str = ""
    """Updated skill pack hint (may extend the existing one)."""

    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    """Confidence in the learned mapping."""

    source: Literal["llm", "manual"] = "llm"
    """Who generated this entry."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session_id: str = ""

    # --- Sync fields (optional; default to unsynced for backward compat) ---

    synced_to_firestore: bool = False
    """True once successfully synced to Firestore."""

    sync_timestamp: Optional[str] = None
    """UTC ISO timestamp of the successful Firestore write. None = not yet synced."""

    sync_attempt_count: int = 0
    """Number of Firestore sync attempts. Capped at 5 by the sync worker."""

    @field_validator("keywords", mode="before")
    @classmethod
    def normalize_keywords(cls, v: List[str]) -> List[str]:
        return [kw.lower().strip() for kw in v if kw.strip()]
