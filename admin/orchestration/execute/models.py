"""
Pydantic models for Execution Twin (Phase 3).

Maps wish IDs (from Phase 2 Intent Twin) to concrete swarm+recipe execution
plans using a deterministic in-memory combo database.

All models are offline-safe, serializable to JSON, no ML, no network.

Architecture (from SMALLTALK_TWIN_BRAINSTORM.md Phase 3):
  wish_id → CPU combo lookup (< 1ms) → {swarm, recipe} → execute

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Combo — a wish_id → {swarm, recipe} mapping
# ---------------------------------------------------------------------------

class Combo(BaseModel):
    """
    Maps a wish_id to a concrete execution plan (swarm + recipe).

    Loaded from combos.jsonl at startup.
    Immutable on hot path.
    """

    wish_id: str
    """Stable identifier matching a Wish in the Intent Twin, e.g. 'oauth-integration'."""

    swarm: Literal["coder", "mathematician", "writer", "planner", "skeptic",
                   "scout", "janitor", "test-developer", "graph-designer",
                   "security-auditor", "northstar-navigator", "portal-engineer"]
    """
    The sub-agent role to dispatch.
    Matches swarms/ directory agent type names.
    """

    recipe: List[str] = Field(default_factory=list)
    """
    Ordered list of skill names to load into the sub-agent's skill pack.
    Always starts with 'prime-safety'.
    Example: ['prime-safety', 'prime-coder', 'oauth3-enforcer']
    """

    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    """
    Prior confidence that this combo is the correct mapping for the wish.
    Higher = more reliable pairing.
    """

    description: str = ""
    """Human-readable description of what this combo accomplishes."""

    category: str = "general"
    """
    Grouping tag for filtering, e.g. 'security', 'performance', 'devops'.
    Mirrors the Wish.category for cross-reference.
    """

    @field_validator("wish_id")
    @classmethod
    def wish_id_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError(f"Combo wish_id must not contain spaces: {v!r}")
        return v.lower()

    @field_validator("recipe", mode="before")
    @classmethod
    def recipe_must_have_prime_safety(cls, v: List[str]) -> List[str]:
        """Ensure prime-safety is in the recipe (safety gate)."""
        if v and "prime-safety" not in v:
            raise ValueError(
                f"Recipe must include 'prime-safety'. Got: {v!r}"
            )
        return v


# ---------------------------------------------------------------------------
# ExecutionMatch — result of a CPU or LLM execution match
# ---------------------------------------------------------------------------

class ExecutionMatch(BaseModel):
    """
    The result of matching a wish_id to an execution plan.

    Produced by ExecutionCPU.match() or LLM validation layer.
    """

    wish_id: str
    """The wish ID that was matched."""

    swarm: str
    """The sub-agent role to dispatch (e.g. 'coder', 'mathematician')."""

    recipe: List[str] = Field(default_factory=list)
    """Ordered skill pack for the sub-agent (prime-safety always first)."""

    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    """
    How confident the match is.
    CPU: combo.confidence (direct lookup)
    LLM: model-returned confidence
    """

    source: Literal["cpu", "llm"] = "cpu"
    """Which path produced this match."""

    latency_ms: float = 0.0
    """Time taken to produce this match (wall clock ms)."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# ComboDatabase — in-memory dict of wish_id → Combo
# ---------------------------------------------------------------------------

class ComboDatabase(BaseModel):
    """
    In-memory container for all loaded combos.

    Supports O(1) lookup by wish_id.
    Loaded at startup from combos.jsonl + learned_combos.jsonl.
    """

    combos: Dict[str, Combo] = Field(default_factory=dict)
    """Primary store: wish_id → Combo."""

    model_config = {"arbitrary_types_allowed": True}

    def add(self, combo: Combo) -> None:
        """Add a combo (or overwrite existing) by wish_id."""
        self.combos[combo.wish_id] = combo

    def get(self, wish_id: str) -> Optional[Combo]:
        """Look up a combo by wish_id. Returns None if not found."""
        return self.combos.get(wish_id)

    def count(self) -> int:
        return len(self.combos)

    def all_combos(self) -> List[Combo]:
        return list(self.combos.values())

    def combos_by_swarm(self, swarm: str) -> List[Combo]:
        """Return all combos that target a specific swarm agent."""
        return [c for c in self.combos.values() if c.swarm == swarm]


# ---------------------------------------------------------------------------
# LookupEntry — records a single CPU match event for LLM learning
# ---------------------------------------------------------------------------

class ComboLookupEntry(BaseModel):
    """
    Records a single CPU combo lookup event.

    Stored in memory so the LLM feedback loop can confirm or correct
    CPU matches and generate new learned_combos.jsonl entries.
    """

    wish_id: str
    """The wish_id that was looked up."""

    cpu_match: Optional[str] = None
    """Wish ID the CPU matched (None = CPU miss)."""

    cpu_swarm: Optional[str] = None
    """Swarm the CPU matched."""

    cpu_recipe: List[str] = Field(default_factory=list)
    """Recipe the CPU matched."""

    cpu_confidence: float = 0.0
    """CPU match confidence."""

    llm_confirmed: Optional[bool] = None
    """None = not yet validated. True = LLM confirmed. False = LLM corrected."""

    llm_swarm: Optional[str] = None
    """Swarm the LLM determined (may differ from CPU on correction)."""

    llm_recipe: List[str] = Field(default_factory=list)
    """Recipe the LLM determined."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session_id: str = ""


# ---------------------------------------------------------------------------
# LearnedCombo — an entry added to learned_combos.jsonl
# ---------------------------------------------------------------------------

class LearnedCombo(BaseModel):
    """
    A new wish_id→{swarm, recipe} mapping discovered by the LLM and persisted.

    Stored as JSONL in learned_combos.jsonl.
    Loaded and merged into ComboDatabase on startup.
    """

    wish_id: str
    """Which wish this combo covers."""

    swarm: str
    """The swarm agent role."""

    recipe: List[str] = Field(default_factory=list)
    """Skill pack for the sub-agent."""

    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    """Confidence in the learned mapping."""

    source: Literal["llm", "manual"] = "llm"
    """Who generated this entry."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session_id: str = ""

    @field_validator("wish_id")
    @classmethod
    def wish_id_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError(f"LearnedCombo wish_id must not contain spaces: {v!r}")
        return v.lower()
