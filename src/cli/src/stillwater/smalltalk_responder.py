"""smalltalk_responder.py — CPU-first small talk response selector.

Selects responses from the smalltalk database based on Phase 1 classification.
Part of the twin orchestration: CPU provides instant response, LLM enriches
the database for future turns (handled separately by the smalltalk-enricher swarm).

Architecture:
  High confidence (>=0.70): select template from responses.jsonl
  Low confidence (<0.70):  gift fallback (joke or fact, alternating)

Data sources (DataRegistry overlay — custom/ wins over default/):
  data/default/smalltalk/responses.jsonl   — 150+ response templates by label
  data/default/smalltalk/compliments.jsonl — 30 calibrated compliments
  data/default/smalltalk/reminders.jsonl   — 15 session-start callbacks
  data/default/smalltalk/config.jsonl      — system configuration
  data/default/smalltalk/jokes.json        — programming jokes (gift fallback)
  data/default/smalltalk/facts.json        — facts (gift fallback)

stdlib only: json, dataclasses, typing, random.
Rung: 641 — deterministic with seeded random, no network, no LLM.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Default thresholds
# ---------------------------------------------------------------------------

CONFIDENCE_THRESHOLD = 0.70
MAX_LEVEL_DEFAULT = 1  # Van Edwards Three Levels: start conservative


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SmallTalkResponse:
    """Response selected by the SmallTalkResponder."""

    text: str
    source: str  # e.g., "smalltalk/responses.jsonl"
    source_id: str  # e.g., "resp_001"
    label: str  # phase1 label
    warmth: int  # 1-5 (Cuddy warmth score)
    level: int  # 1-3 (Van Edwards Three Levels)
    response_type: str  # "template", "joke", "fact", "compliment", "reminder"


# ---------------------------------------------------------------------------
# SmallTalkResponder
# ---------------------------------------------------------------------------


class SmallTalkResponder:
    """CPU-first small talk response selector.

    Loads response templates, jokes, facts, compliments, and reminders from
    the DataRegistry overlay, then selects the best response for a given
    Phase 1 classification result.

    Parameters
    ----------
    registry:
        A ``DataRegistry`` instance for all file I/O.
    seed:
        Random seed for deterministic selection (default 42).
    """

    def __init__(self, registry: Any, seed: int = 42) -> None:
        self.registry = registry
        self._rng = random.Random(seed)

        # Data stores — populated by _load_data()
        self._responses: List[dict] = []
        self._jokes: List[dict] = []
        self._facts: List[dict] = []
        self._compliments: List[dict] = []
        self._reminders: List[dict] = []
        self._config: Dict[str, Any] = {}
        self._last_prediction: Optional[dict] = None
        self._domain_content: List[dict] = []

        # Session-scoped state
        self._used_ids: Set[str] = set()
        self._compliment_count: int = 0
        self._gift_is_joke: bool = True  # alternates: True=joke, False=fact
        self._last_gift_type: str = ""  # "joke" or "fact" (for test introspection)
        self._last_warmth: int = 0
        self._exchange_count: int = 0
        self._reminder_given: bool = False  # max 1 reminder per session

        # Load all data on construction
        self._load_data()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_data(self) -> None:
        """Load all smalltalk data files via DataRegistry."""
        # Load responses.jsonl (JSONL format — one JSON per line)
        raw = self.registry.load_data_file("smalltalk/responses.jsonl")
        if raw:
            self._responses = [
                json.loads(line)
                for line in raw.splitlines()
                if line.strip()
            ]

        # Load jokes.json (JSON array format)
        raw = self.registry.load_data_file("smalltalk/jokes.json")
        if raw:
            self._jokes = json.loads(raw)

        # Load facts.json (JSON array format)
        raw = self.registry.load_data_file("smalltalk/facts.json")
        if raw:
            self._facts = json.loads(raw)

        # Load compliments.jsonl
        raw = self.registry.load_data_file("smalltalk/compliments.jsonl")
        if raw:
            self._compliments = [
                json.loads(line)
                for line in raw.splitlines()
                if line.strip()
            ]

        # Load reminders.jsonl
        raw = self.registry.load_data_file("smalltalk/reminders.jsonl")
        if raw:
            self._reminders = [
                json.loads(line)
                for line in raw.splitlines()
                if line.strip()
            ]

        # Load config.jsonl
        raw = self.registry.load_data_file("smalltalk/config.jsonl")
        if raw:
            for line in raw.splitlines():
                if line.strip():
                    entry = json.loads(line)
                    self._config[entry.get("key", "")] = entry.get("value")

        # Also try to load LLM predictions from custom/
        raw = self.registry.load_data_file("smalltalk/llm-predictions.jsonl")
        if raw:
            lines = [line for line in raw.splitlines() if line.strip()]
            if lines:
                # Use the most recent prediction
                self._last_prediction = json.loads(lines[-1])

        # Load domain content from custom/
        raw = self.registry.load_data_file("smalltalk/domain-content.jsonl")
        if raw:
            self._domain_content = [
                json.loads(line)
                for line in raw.splitlines()
                if line.strip()
            ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def respond(
        self,
        label: str,
        confidence: float,
        user_input: str = "",
        context: Optional[dict] = None,
    ) -> SmallTalkResponse:
        """Select best response for a non-task classification.

        High confidence path (>=threshold):
          1. Filter responses by label
          2. Apply level gate (Van Edwards Three Levels)
          3. Apply tag filter (if domain tags from LLM prediction exist)
          4. Remove already-used IDs (session dedup)
          5. Select best match

        Low confidence / gift fallback path:
          1. Alternate between joke and fact
          2. Apply tag filter if domain detected
          3. Append redirect phrase
          4. Mark as used

        Parameters
        ----------
        label:
            Phase 1 classification label (e.g. ``"greeting"``, ``"farewell"``).
        confidence:
            Classification confidence (0.0 - 1.0).
        user_input:
            Original user text (for brevity matching).
        context:
            Optional context dict (e.g. domain tags, session state).

        Returns
        -------
        SmallTalkResponse
            The selected response with metadata.
        """
        self._exchange_count += 1
        threshold = self._config.get("cpu_first", True) and CONFIDENCE_THRESHOLD
        tags = self._extract_tags(context)

        # Determine the level gate from exchange count
        level = self._current_level()

        if confidence >= threshold and self._responses:
            result = self._select_template(label, tags, level)
            if result is not None:
                self._last_warmth = result.warmth
                return result

        # Fall through to gift fallback
        result = self._select_gift(tags)
        self._last_warmth = result.warmth
        return result

    def compliment(self, trigger: str = "task_completed") -> Optional[SmallTalkResponse]:
        """Select a calibrated compliment if budget allows.

        Plant Watering Rule:
        - Max 3 compliments per session
        - Only after task completion or achievement
        - Never after failure (patronizing)
        - Normal: warmth 3-4
        - Hard tasks: warmth 5
        - Skip if last response warmth >= 4 (over-watering)

        Parameters
        ----------
        trigger:
            The event that triggered the compliment (e.g. ``"task_completed"``).

        Returns
        -------
        SmallTalkResponse | None
            A compliment response, or ``None`` if the budget is exhausted or
            conditions are not met.
        """
        max_compliments = self._config.get("compliment_frequency", 3)
        if self._compliment_count >= max_compliments:
            return None

        # Over-watering guard: skip if last warmth was already high
        if self._last_warmth >= 4:
            return None

        candidates = [
            c for c in self._compliments
            if c.get("trigger") == trigger
            and c.get("id") not in self._used_ids
        ]

        if not candidates:
            return None

        selected = self._rng.choice(candidates)
        self._used_ids.add(selected["id"])
        self._compliment_count += 1

        return SmallTalkResponse(
            text=selected.get("compliment", ""),
            source="smalltalk/compliments.jsonl",
            source_id=selected["id"],
            label="compliment",
            warmth=selected.get("warmth", 3),
            level=selected.get("level", 1),
            response_type="compliment",
        )

    def reminder(
        self, session_history: Optional[dict] = None,
    ) -> Optional[SmallTalkResponse]:
        """Select a session-start reminder if one applies.

        Checks whether reminder_at_session_start is enabled in config,
        then finds a reminder whose ``requires`` fields are all present
        in the session history, fills in the template, and returns it.

        Parameters
        ----------
        session_history:
            Dict of session state keys (e.g. ``{"last_task": "fix CI",
            "open_tasks": 3}``).  Template placeholders like ``{last_task}``
            are substituted from this dict.

        Returns
        -------
        SmallTalkResponse | None
            A reminder response, or ``None`` if reminders are disabled,
            no history is available, or no reminder template matches.
        """
        if not self._config.get("reminder_at_session_start", True):
            return None

        # Max 1 reminder per session
        if self._reminder_given:
            return None

        if not session_history:
            return None

        available_keys = set(session_history.keys())

        candidates = [
            r for r in self._reminders
            if r.get("id") not in self._used_ids
            and set(r.get("requires", [])).issubset(available_keys)
        ]

        if not candidates:
            return None

        selected = self._rng.choice(candidates)
        self._used_ids.add(selected["id"])
        self._reminder_given = True

        # Fill template placeholders from session_history
        template = selected.get("template", "")
        try:
            text = template.format(**session_history)
        except (KeyError, IndexError):
            text = template

        return SmallTalkResponse(
            text=text,
            source="smalltalk/reminders.jsonl",
            source_id=selected["id"],
            label="reminder",
            warmth=selected.get("warmth", 3),
            level=2,  # reminders are personal — level 2
            response_type="reminder",
        )

    def reset_session(self) -> None:
        """Reset session-scoped state for a new conversation.

        Clears used IDs, compliment count, gift alternation, and exchange
        count.  Data files are NOT reloaded (call ``_load_data`` explicitly
        if data refresh is needed).
        """
        self._used_ids.clear()
        self._compliment_count = 0
        self._gift_is_joke = True
        self._last_gift_type = ""
        self._last_warmth = 0
        self._exchange_count = 0
        self._reminder_given = False

    def stats(self) -> dict:
        """Return responder statistics.

        Returns
        -------
        dict
            Keys: ``responses_loaded``, ``jokes_loaded``, ``facts_loaded``,
            ``compliments_loaded``, ``reminders_loaded``, ``used_ids``,
            ``compliment_count``, ``exchange_count``, ``gift_is_joke``.
        """
        return {
            "responses_loaded": len(self._responses),
            "jokes_loaded": len(self._jokes),
            "facts_loaded": len(self._facts),
            "compliments_loaded": len(self._compliments),
            "reminders_loaded": len(self._reminders),
            "used_ids": len(self._used_ids),
            "compliment_count": self._compliment_count,
            "exchange_count": self._exchange_count,
            "gift_is_joke": self._gift_is_joke,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _select_template(
        self, label: str, tags: List[str], level: int,
    ) -> Optional[SmallTalkResponse]:
        """Select a response template matching label, level gate, and tags.

        Filters by label, then by level (Van Edwards Three Levels — only
        responses at or below the current level are eligible), then by tags
        if any are available, then removes already-used IDs.  Picks one at
        random from the surviving candidates.

        Returns ``None`` if no candidate survives all filters.
        """
        # Step 1: filter by label
        candidates = [r for r in self._responses if r.get("label") == label]

        if not candidates:
            return None

        # Step 2: level gate — only responses at or below current level
        # Exception: emotional labels bypass the level gate (emotions happen
        # at any time — you don't need rapport level 2 to feel frustrated)
        _EMOTION_LABELS = {"emotional_positive", "emotional_negative"}
        if label not in _EMOTION_LABELS:
            candidates = [r for r in candidates if r.get("level", 1) <= level]

            if not candidates:
                # Relax to level 1 minimum so we always have something
                candidates = [
                    r for r in self._responses
                    if r.get("label") == label and r.get("level", 1) <= 1
                ]

        # Step 3: tag filter (if domain tags from LLM prediction exist)
        if tags:
            tagged = self._apply_tag_filter(candidates, tags)
            if tagged:
                candidates = tagged

        # Step 4: session dedup — remove already-used IDs
        fresh = [r for r in candidates if r.get("id") not in self._used_ids]
        if fresh:
            candidates = fresh

        if not candidates:
            return None

        selected = self._rng.choice(candidates)
        self._used_ids.add(selected.get("id", ""))

        return SmallTalkResponse(
            text=selected.get("response", ""),
            source="smalltalk/responses.jsonl",
            source_id=selected.get("id", ""),
            label=label,
            warmth=selected.get("warmth", 3),
            level=selected.get("level", 1),
            response_type="template",
        )

    def _select_gift(self, tags: List[str]) -> SmallTalkResponse:
        """Select a gift (joke or fact) using alternation.

        Alternates between joke and fact each time this is called.  Applies
        tag filtering if domain tags are available.  Falls back to a generic
        response if both pools are exhausted.

        Returns
        -------
        SmallTalkResponse
            Always returns a response (never None).
        """
        if self._gift_is_joke:
            result = self._pick_joke(tags)
            self._gift_is_joke = False
            if result is not None:
                self._last_gift_type = "joke"
                return result
        else:
            result = self._pick_fact(tags)
            self._gift_is_joke = True
            if result is not None:
                self._last_gift_type = "fact"
                return result

        # Both pools exhausted or empty — generic fallback
        return SmallTalkResponse(
            text="I'm here when you're ready to work on something.",
            source="smalltalk/fallback",
            source_id="fallback_001",
            label="fallback",
            warmth=2,
            level=1,
            response_type="template",
        )

    def _pick_joke(self, tags: List[str]) -> Optional[SmallTalkResponse]:
        """Pick a joke from the pool, respecting tags and dedup."""
        candidates = [j for j in self._jokes if j.get("id") not in self._used_ids]

        if tags:
            tagged = self._apply_tag_filter(candidates, tags)
            if tagged:
                candidates = tagged

        if not candidates:
            return None

        selected = self._rng.choice(candidates)
        self._used_ids.add(selected.get("id", ""))

        return SmallTalkResponse(
            text=selected.get("joke", ""),
            source="smalltalk/jokes.json",
            source_id=selected.get("id", ""),
            label="gift",
            warmth=3,
            level=1,
            response_type="joke",
        )

    def _pick_fact(self, tags: List[str]) -> Optional[SmallTalkResponse]:
        """Pick a fact from the pool, respecting tags and dedup."""
        candidates = [f for f in self._facts if f.get("id") not in self._used_ids]

        if tags:
            tagged = self._apply_tag_filter(candidates, tags)
            if tagged:
                candidates = tagged

        if not candidates:
            return None

        selected = self._rng.choice(candidates)
        self._used_ids.add(selected.get("id", ""))

        return SmallTalkResponse(
            text=selected.get("fact", ""),
            source="smalltalk/facts.json",
            source_id=selected.get("id", ""),
            label="gift",
            warmth=2,
            level=1,
            response_type="fact",
        )

    def _apply_tag_filter(
        self, items: List[dict], tags: List[str],
    ) -> List[dict]:
        """Filter items to those sharing at least one tag with *tags*.

        Parameters
        ----------
        items:
            List of dicts, each with an optional ``"tags"`` list.
        tags:
            Tags to match against.

        Returns
        -------
        list[dict]
            Items that have at least one overlapping tag, or an empty list
            if none match.
        """
        tag_set = set(tags)
        return [
            item for item in items
            if tag_set.intersection(set(item.get("tags", [])))
        ]

    def _extract_tags(self, context: Optional[dict]) -> List[str]:
        """Extract domain tags from context or last LLM prediction.

        Checks context dict first (key ``"tags"``), then falls back to
        the most recent LLM prediction stored in
        ``smalltalk/llm-predictions.jsonl``.
        """
        if context and "tags" in context:
            tags = context["tags"]
            if isinstance(tags, list):
                return tags

        if self._last_prediction and "tags" in self._last_prediction:
            tags = self._last_prediction["tags"]
            if isinstance(tags, list):
                return tags

        return []

    def _current_level(self) -> int:
        """Determine the Van Edwards Three Levels gate for this exchange.

        Level progression:
          - Exchanges 1-3:   Level 1 (general / safe topics)
          - Exchanges 4-8:   Level 2 (personal / specific topics)
          - Exchanges 9+:    Level 3 (vulnerability / deep topics)

        This mirrors natural conversation depth — start broad, go deeper
        as rapport builds.
        """
        if self._exchange_count <= 3:
            return 1
        if self._exchange_count <= 8:
            return 2
        return 3
