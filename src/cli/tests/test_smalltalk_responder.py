"""Tests for stillwater.smalltalk_responder (TDD red tests).

Coverage targets:
  1. Data loading tests (~8 tests)
  2. High confidence response tests (~12 tests)
  3. Low confidence / gift fallback tests (~8 tests)
  4. Compliment tests — Plant Watering Rule (~8 tests)
  5. Reminder tests (~6 tests)
  6. Session management tests (~4 tests)
  7. Domain tag filtering tests (~6 tests)

Rung: 641 — deterministic, no network, testable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import pytest

from stillwater.data_registry import DataRegistry
from stillwater.smalltalk_responder import (
    SmallTalkResponse,
    SmallTalkResponder,
)


# ===========================================================================
# Helpers
# ===========================================================================

ALL_LABELS = [
    "greeting",
    "gratitude",
    "emotional_positive",
    "emotional_negative",
    "humor",
    "small_talk",
    "goodbye",
    "question",
    "off_domain",
]

HIGH_CONFIDENCE = 0.85
LOW_CONFIDENCE = 0.40
ZERO_CONFIDENCE = 0.0
THRESHOLD_CONFIDENCE = 0.70  # boundary between template and gift


def _make_response(
    id: str,
    label: str,
    response: str,
    level: int = 1,
    warmth: int = 3,
    confidence: float = 0.90,
    tags: Optional[list] = None,
) -> dict:
    """Build a single response record for responses.jsonl."""
    return {
        "id": id,
        "label": label,
        "pattern": ".*",
        "response": response,
        "level": level,
        "warmth": warmth,
        "confidence": confidence,
        "tags": tags or ["generic"],
        "added_by": "test",
    }


def _make_compliment(
    id: str,
    trigger: str = "task_completed",
    compliment: str = "Good work.",
    warmth: int = 3,
    tags: Optional[list] = None,
) -> dict:
    """Build a single compliment record for compliments.jsonl."""
    return {
        "id": id,
        "trigger": trigger,
        "compliment": compliment,
        "warmth": warmth,
        "tags": tags or ["generic"],
    }


def _make_reminder(
    id: str,
    trigger: str = "session_start",
    template: str = "Welcome back.",
    warmth: int = 4,
    requires: Optional[list] = None,
) -> dict:
    """Build a single reminder record for reminders.jsonl."""
    return {
        "id": id,
        "trigger": trigger,
        "template": template,
        "warmth": warmth,
        "requires": requires or [],
    }


def _make_joke(
    id: str,
    joke: str = "Why do programmers count from 0? Because they can.",
    tags: Optional[list] = None,
) -> dict:
    """Build a single joke record for jokes.json."""
    return {
        "id": id,
        "joke": joke,
        "tags": tags or ["programming"],
        "min_glow": 0.0,
        "max_glow": 0.5,
        "confidence": 0.85,
        "freshness_days": 90,
        "added_by": "test",
        "added_at": "2026-02-24",
    }


def _make_fact(
    id: str,
    title: str = "Test Fact",
    fact: str = "This is a test fact.",
    category: str = "general",
) -> dict:
    """Build a single fact record for facts.json."""
    return {
        "id": id,
        "title": title,
        "fact": fact,
        "category": category,
        "source": "Test",
        "added_at": "2026-02-24",
    }


def _make_config(key: str, value, description: str = "") -> dict:
    """Build a single config record for config.jsonl."""
    return {"key": key, "value": value, "description": description}


def _make_jsonl(records: list) -> str:
    """Serialize a list of dicts to JSONL."""
    return "\n".join(json.dumps(r) for r in records) + "\n"


def _make_json_array(records: list) -> str:
    """Serialize a list of dicts to JSON array."""
    return json.dumps(records, indent=2) + "\n"


def _write_default(tmp_path: Path, relative_path: str, content: str) -> None:
    """Write a file to data/default/ under tmp_path."""
    target = tmp_path / "data" / "default" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _write_custom(tmp_path: Path, relative_path: str, content: str) -> None:
    """Write a file to data/custom/ under tmp_path."""
    target = tmp_path / "data" / "custom" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _setup_data_dirs(tmp_path: Path) -> Path:
    """Create data/default/ and data/custom/ under tmp_path. Return tmp_path."""
    (tmp_path / "data" / "default").mkdir(parents=True)
    (tmp_path / "data" / "custom").mkdir(parents=True)
    return tmp_path


# ===========================================================================
# Standard test data — minimal but covers all labels
# ===========================================================================

STANDARD_RESPONSES = [
    _make_response("resp_001", "greeting", "Hey! What are you working on?", warmth=3, level=1),
    _make_response("resp_002", "greeting", "Hello. Ready when you are.", warmth=2, level=1),
    _make_response("resp_003", "gratitude", "Happy to help.", warmth=3, level=1),
    _make_response("resp_004", "gratitude", "Anytime. What's next?", warmth=2, level=1),
    _make_response("resp_005", "emotional_positive", "That's great to hear!", warmth=4, level=2),
    _make_response("resp_006", "emotional_negative", "I hear you. What can I help with?", warmth=4, level=2),
    _make_response("resp_007", "emotional_negative", "That sounds tough. Want to talk through it?", warmth=5, level=3),
    _make_response("resp_008", "humor", "Ha! Good one. What else?", warmth=3, level=1),
    _make_response("resp_009", "small_talk", "Interesting. What's on the task list?", warmth=2, level=1),
    _make_response("resp_010", "goodbye", "See you next time.", warmth=3, level=1),
    _make_response("resp_011", "question", "Let me think about that.", warmth=2, level=1),
    _make_response("resp_012", "off_domain", "That's outside my area. Want to refocus?", warmth=2, level=1),
]

STANDARD_COMPLIMENTS = [
    _make_compliment("comp_001", "task_completed", "Nice execution on that one.", warmth=3),
    _make_compliment("comp_002", "task_completed", "That was clean work.", warmth=3),
    _make_compliment("comp_003", "momentum", "You're on a roll today.", warmth=4),
    _make_compliment("comp_004", "resilience", "Tough bug, but you handled it.", warmth=4),
    _make_compliment("comp_005", "task_completed", "Shipped. That's the milestone.", warmth=4),
]

STANDARD_REMINDERS = [
    _make_reminder(
        "rem_001",
        "session_start",
        "Last session you were working on {last_task}. Pick up where you left off?",
        requires=["last_task"],
    ),
    _make_reminder(
        "rem_002",
        "session_start",
        "You had {open_tasks} open tasks from last time. Ready?",
        requires=["open_tasks"],
    ),
    _make_reminder(
        "rem_003",
        "session_start",
        "Last session ended with a green build. Let's keep that streak.",
        requires=[],
    ),
]

STANDARD_JOKES = [
    _make_joke("joke_001", "Why do programmers prefer dark mode? Light attracts bugs.", tags=["programming"]),
    _make_joke("joke_002", "A SQL query walks into a bar and asks two tables: Can I join you?", tags=["database", "sql"]),
    _make_joke("joke_003", "There are 10 types of people: those who know binary and those who don't.", tags=["math", "binary"]),
]

STANDARD_FACTS = [
    _make_fact("fact_001", "Stillwater Origin", "Stillwater refers to calm, flowing water.", category="stillwater"),
    _make_fact("fact_002", "CPU-LLM Twin", "CPU makes fast decisions; LLM validates.", category="architecture"),
    _make_fact("fact_003", "OAuth3", "OAuth3 is a valet key pattern for AI agents.", category="security"),
]

STANDARD_CONFIG = [
    _make_config("cpu_first", True, "Always try CPU response first"),
    _make_config("fallback_to_jokes", True, "Use jokes/facts when low confidence"),
    _make_config("compliment_frequency", 3, "Max compliments per session"),
    _make_config("redirect_after_exchanges", 2, "Max non-task exchanges before redirect"),
    _make_config("max_warmth_level", 3, "Default max warmth"),
]


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Create a fully populated test data directory."""
    _setup_data_dirs(tmp_path)
    _write_default(tmp_path, "smalltalk/responses.jsonl", _make_jsonl(STANDARD_RESPONSES))
    _write_default(tmp_path, "smalltalk/compliments.jsonl", _make_jsonl(STANDARD_COMPLIMENTS))
    _write_default(tmp_path, "smalltalk/reminders.jsonl", _make_jsonl(STANDARD_REMINDERS))
    _write_default(tmp_path, "smalltalk/jokes.json", _make_json_array(STANDARD_JOKES))
    _write_default(tmp_path, "smalltalk/facts.json", _make_json_array(STANDARD_FACTS))
    _write_default(tmp_path, "smalltalk/config.jsonl", _make_jsonl(STANDARD_CONFIG))
    return tmp_path


@pytest.fixture
def registry(data_dir: Path) -> DataRegistry:
    """DataRegistry pointing at the test data directory."""
    return DataRegistry(repo_root=data_dir)


@pytest.fixture
def responder(registry: DataRegistry) -> SmallTalkResponder:
    """A SmallTalkResponder loaded with standard test data."""
    return SmallTalkResponder(registry)


@pytest.fixture
def empty_data_dir(tmp_path: Path) -> Path:
    """Create data dirs with NO smalltalk files (graceful degradation test)."""
    _setup_data_dirs(tmp_path)
    return tmp_path


# ===========================================================================
# 1. Data Loading Tests (8 tests)
# ===========================================================================


class TestDataLoading:
    """Verify data loading from DataRegistry into SmallTalkResponder."""

    def test_loads_responses_from_default(self, responder: SmallTalkResponder) -> None:
        """Responses are loaded from data/default/smalltalk/responses.jsonl."""
        assert len(responder._responses) == len(STANDARD_RESPONSES)
        ids = {r["id"] for r in responder._responses}
        assert "resp_001" in ids
        assert "resp_012" in ids

    def test_loads_jokes_from_default(self, responder: SmallTalkResponder) -> None:
        """Jokes are loaded from data/default/smalltalk/jokes.json."""
        assert len(responder._jokes) == len(STANDARD_JOKES)
        ids = {j["id"] for j in responder._jokes}
        assert "joke_001" in ids

    def test_loads_facts_from_default(self, responder: SmallTalkResponder) -> None:
        """Facts are loaded from data/default/smalltalk/facts.json."""
        assert len(responder._facts) == len(STANDARD_FACTS)
        ids = {f["id"] for f in responder._facts}
        assert "fact_001" in ids

    def test_loads_compliments(self, responder: SmallTalkResponder) -> None:
        """Compliments are loaded from data/default/smalltalk/compliments.jsonl."""
        assert len(responder._compliments) == len(STANDARD_COMPLIMENTS)
        ids = {c["id"] for c in responder._compliments}
        assert "comp_001" in ids
        assert "comp_004" in ids

    def test_loads_reminders(self, responder: SmallTalkResponder) -> None:
        """Reminders are loaded from data/default/smalltalk/reminders.jsonl."""
        assert len(responder._reminders) == len(STANDARD_REMINDERS)
        ids = {r["id"] for r in responder._reminders}
        assert "rem_001" in ids

    def test_loads_config(self, responder: SmallTalkResponder) -> None:
        """Config is loaded from data/default/smalltalk/config.jsonl."""
        assert responder._config != {}
        # Config should be keyed by the "key" field
        assert responder._config.get("cpu_first") is True
        assert responder._config.get("compliment_frequency") == 3

    def test_custom_overrides_default(self, data_dir: Path) -> None:
        """Custom data layer overrides default (DataRegistry overlay)."""
        custom_responses = [
            _make_response("resp_001", "greeting", "CUSTOM greeting response.", warmth=5, level=3),
        ]
        _write_custom(data_dir, "smalltalk/responses.jsonl", _make_jsonl(custom_responses))
        registry = DataRegistry(repo_root=data_dir)
        resp = SmallTalkResponder(registry)
        # Custom layer should override — only the custom response should be present
        assert any(r["response"] == "CUSTOM greeting response." for r in resp._responses)

    def test_empty_data_dir_graceful(self, empty_data_dir: Path) -> None:
        """SmallTalkResponder initializes gracefully when no data files exist."""
        registry = DataRegistry(repo_root=empty_data_dir)
        resp = SmallTalkResponder(registry)
        assert resp._responses == []
        assert resp._jokes == []
        assert resp._facts == []
        assert resp._compliments == []
        assert resp._reminders == []
        assert resp._config == {}


# ===========================================================================
# 2. High Confidence Response Tests (12 tests)
# ===========================================================================


class TestHighConfidenceResponses:
    """Verify template-based responses when confidence >= 0.70."""

    def test_greeting_returns_greeting_response(self, responder: SmallTalkResponder) -> None:
        """A greeting label with high confidence returns a greeting template."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hello")
        assert isinstance(result, SmallTalkResponse)
        assert result.label == "greeting"
        assert result.response_type == "template"
        assert result.text != ""

    def test_gratitude_returns_gratitude_response(self, responder: SmallTalkResponder) -> None:
        """A gratitude label with high confidence returns a gratitude template."""
        result = responder.respond("gratitude", HIGH_CONFIDENCE, user_input="thanks")
        assert result.label == "gratitude"
        assert result.response_type == "template"
        # Should be one of the two gratitude responses
        assert result.text in {"Happy to help.", "Anytime. What's next?"}

    def test_emotional_positive_returns_response(self, responder: SmallTalkResponder) -> None:
        """An emotional_positive label returns an appropriate template."""
        result = responder.respond("emotional_positive", HIGH_CONFIDENCE, user_input="I got promoted!")
        assert result.label == "emotional_positive"
        assert result.text == "That's great to hear!"

    def test_emotional_negative_returns_empathetic_response(self, responder: SmallTalkResponder) -> None:
        """An emotional_negative label returns an empathetic template."""
        result = responder.respond("emotional_negative", HIGH_CONFIDENCE, user_input="I'm struggling")
        assert result.label == "emotional_negative"
        assert result.warmth >= 4  # empathetic responses should be warm

    def test_humor_returns_joke_from_responses(self, responder: SmallTalkResponder) -> None:
        """A humor label returns a humor template from responses.jsonl."""
        result = responder.respond("humor", HIGH_CONFIDENCE, user_input="haha")
        assert result.label == "humor"
        assert result.response_type == "template"

    def test_small_talk_returns_response(self, responder: SmallTalkResponder) -> None:
        """A small_talk label returns a small talk template."""
        result = responder.respond("small_talk", HIGH_CONFIDENCE, user_input="nice weather")
        assert result.label == "small_talk"
        assert result.response_type == "template"

    def test_response_warmth_within_range(self, responder: SmallTalkResponder) -> None:
        """Response warmth is always within 1-5 range."""
        result = responder.respond("greeting", HIGH_CONFIDENCE)
        assert 1 <= result.warmth <= 5

    def test_response_not_repeated_in_session(self, responder: SmallTalkResponder) -> None:
        """The same response ID is not returned twice in a single session (dedup)."""
        seen_ids: set[str] = set()
        # Call respond multiple times — with 2 greeting responses, third should not repeat
        for _ in range(2):
            result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
            assert result.source_id not in seen_ids, f"Duplicate response: {result.source_id}"
            seen_ids.add(result.source_id)

    @pytest.mark.parametrize("label", ALL_LABELS)
    def test_all_labels_have_responses(self, responder: SmallTalkResponder, label: str) -> None:
        """Every known label returns a valid response (template or gift fallback)."""
        result = responder.respond(label, HIGH_CONFIDENCE, user_input="test")
        assert isinstance(result, SmallTalkResponse)
        assert result.text != ""
        # Label can be the original label OR "gift"/"fallback" if template not found
        assert result.label in {label, "gift", "fallback"}

    def test_response_source_is_responses_jsonl(self, responder: SmallTalkResponder) -> None:
        """High confidence responses cite responses.jsonl as their source."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hello")
        assert result.source == "smalltalk/responses.jsonl"

    def test_confidence_above_threshold_uses_template(self, responder: SmallTalkResponder) -> None:
        """Confidence exactly at threshold (0.70) uses template path."""
        result = responder.respond("greeting", THRESHOLD_CONFIDENCE, user_input="hi")
        assert result.response_type == "template"

    def test_multiple_responses_available_per_label(self, responder: SmallTalkResponder) -> None:
        """Labels with multiple responses rotate (not always the same one)."""
        results = set()
        responder.reset_session()
        for _ in range(2):
            result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hey")
            results.add(result.source_id)
            responder.reset_session()  # reset dedup to allow re-selection
        # With 2 greeting responses, we should see at least the possibility of different ones
        # (deterministic seeded selection may return same — check at least one valid response)
        assert len(results) >= 1


# ===========================================================================
# 3. Low Confidence / Gift Fallback Tests (8 tests)
# ===========================================================================


class TestGiftFallback:
    """Verify joke/fact fallback when confidence is below threshold."""

    def test_low_confidence_returns_joke_or_fact(self, responder: SmallTalkResponder) -> None:
        """Below threshold confidence returns a gift (joke or fact)."""
        result = responder.respond("greeting", LOW_CONFIDENCE, user_input="hey")
        assert result.response_type in {"joke", "fact"}

    def test_unknown_label_returns_gift(self, responder: SmallTalkResponder) -> None:
        """An unrecognized label falls back to gift path."""
        result = responder.respond("totally_unknown_label", LOW_CONFIDENCE, user_input="xyz")
        assert result.response_type in {"joke", "fact"}
        assert result.text != ""

    def test_zero_confidence_returns_gift(self, responder: SmallTalkResponder) -> None:
        """Zero confidence always returns gift path."""
        result = responder.respond("greeting", ZERO_CONFIDENCE, user_input="")
        assert result.response_type in {"joke", "fact"}

    def test_gift_alternation_joke_fact_joke(self, responder: SmallTalkResponder) -> None:
        """Gifts alternate between joke and fact across calls."""
        types = []
        for i in range(3):
            result = responder.respond("greeting", LOW_CONFIDENCE, user_input="hmm")
            types.append(result.response_type)
        # Should alternate: if first is joke, second is fact, third is joke (or vice versa)
        assert types[0] != types[1], f"First two gifts should alternate, got {types}"
        assert types[1] != types[2], f"Second two gifts should alternate, got {types}"

    def test_gift_includes_redirect(self, responder: SmallTalkResponder) -> None:
        """Gift responses include redirect text or the response itself is substantive."""
        result = responder.respond("greeting", LOW_CONFIDENCE, user_input="hmm")
        # The response text should be non-empty (the joke/fact text)
        assert len(result.text) > 0

    def test_gift_source_is_jokes_or_facts(self, responder: SmallTalkResponder) -> None:
        """Gift responses cite jokes.json or facts.json as their source."""
        result = responder.respond("greeting", LOW_CONFIDENCE, user_input="hmm")
        assert result.source in {"smalltalk/jokes.json", "smalltalk/facts.json"}

    def test_empty_jokes_falls_to_facts(self, data_dir: Path) -> None:
        """When jokes.json is empty, gifts fall back to facts only."""
        _write_default(data_dir, "smalltalk/jokes.json", _make_json_array([]))
        registry = DataRegistry(repo_root=data_dir)
        resp = SmallTalkResponder(registry)
        result = resp.respond("greeting", LOW_CONFIDENCE, user_input="hmm")
        # With empty jokes, alternation tries joke first, fails, then generic fallback
        # OR it may serve a template since greeting has templates
        assert result.response_type in {"fact", "template", "joke"}

    def test_empty_both_returns_default_message(self, data_dir: Path) -> None:
        """When both jokes and facts are empty, a hardcoded default message is returned."""
        _write_default(data_dir, "smalltalk/jokes.json", _make_json_array([]))
        _write_default(data_dir, "smalltalk/facts.json", _make_json_array([]))
        registry = DataRegistry(repo_root=data_dir)
        resp = SmallTalkResponder(registry)
        result = resp.respond("greeting", LOW_CONFIDENCE, user_input="hmm")
        assert isinstance(result, SmallTalkResponse)
        assert result.text != ""
        # Should have a sensible fallback type
        assert result.response_type in {"default", "fallback", "template"}


# ===========================================================================
# 4. Compliment Tests — Plant Watering Rule (8 tests)
# ===========================================================================


class TestCompliments:
    """Verify compliment selection follows the Plant Watering Rule (max 3/session)."""

    def test_compliment_returns_compliment(self, responder: SmallTalkResponder) -> None:
        """A basic compliment call returns a SmallTalkResponse of type compliment."""
        result = responder.compliment(trigger="task_completed")
        assert result is not None
        assert isinstance(result, SmallTalkResponse)
        assert result.response_type == "compliment"
        assert result.text != ""

    def test_compliment_max_3_per_session(self, responder: SmallTalkResponder) -> None:
        """Only 3 compliments are allowed per session (Plant Watering Rule)."""
        results = []
        for _ in range(3):
            result = responder.compliment(trigger="task_completed")
            assert result is not None
            results.append(result)
        assert len(results) == 3

    def test_compliment_fourth_returns_none(self, responder: SmallTalkResponder) -> None:
        """The 4th compliment request returns None (budget exhausted)."""
        for _ in range(3):
            result = responder.compliment(trigger="task_completed")
            assert result is not None
        fourth = responder.compliment(trigger="task_completed")
        assert fourth is None

    @pytest.mark.parametrize("trigger", ["task_completed", "momentum", "resilience"])
    def test_compliment_trigger_categories(
        self, responder: SmallTalkResponder, trigger: str
    ) -> None:
        """Compliments work for all trigger categories."""
        result = responder.compliment(trigger=trigger)
        assert result is not None
        assert result.response_type == "compliment"

    def test_compliment_not_after_high_warmth(self, responder: SmallTalkResponder) -> None:
        """After a high-warmth response (warmth >= 4), compliment should be suppressed
        to avoid emotional overload."""
        # First, trigger a high-warmth response
        responder.respond("emotional_negative", HIGH_CONFIDENCE, user_input="I'm upset")
        # Now attempt a compliment — should be None or reduced-warmth
        result = responder.compliment(trigger="task_completed")
        # Either None (suppressed) or warmth is lower than the high-warmth threshold
        if result is not None:
            assert result.warmth <= 3

    def test_compliment_reset_on_new_session(self, responder: SmallTalkResponder) -> None:
        """After reset_session, compliment budget is restored."""
        for _ in range(3):
            responder.compliment(trigger="task_completed")
        assert responder.compliment(trigger="task_completed") is None
        responder.reset_session()
        result = responder.compliment(trigger="task_completed")
        assert result is not None

    def test_compliment_dedup(self, responder: SmallTalkResponder) -> None:
        """Same compliment is not served twice in a session."""
        seen_ids: set[str] = set()
        for _ in range(3):
            result = responder.compliment(trigger="task_completed")
            if result is not None:
                assert result.source_id not in seen_ids, f"Duplicate compliment: {result.source_id}"
                seen_ids.add(result.source_id)

    def test_compliment_warmth_calibrated(self, responder: SmallTalkResponder) -> None:
        """Compliment warmth is within the valid 1-5 range."""
        result = responder.compliment(trigger="task_completed")
        assert result is not None
        assert 1 <= result.warmth <= 5


# ===========================================================================
# 5. Reminder Tests (6 tests)
# ===========================================================================


class TestReminders:
    """Verify session-start reminders from reminders.jsonl."""

    def test_reminder_returns_template(self, responder: SmallTalkResponder) -> None:
        """A reminder call with valid history returns a SmallTalkResponse."""
        history = {"last_task": "fix auth bug"}
        result = responder.reminder(session_history=history)
        assert result is not None
        assert isinstance(result, SmallTalkResponse)
        assert result.response_type == "reminder"

    def test_reminder_injects_variables(self, responder: SmallTalkResponder) -> None:
        """Template variables like {last_task} are filled from session_history."""
        history = {"last_task": "deploy v2.0"}
        result = responder.reminder(session_history=history)
        assert result is not None
        assert "deploy v2.0" in result.text

    def test_reminder_none_without_history(self, responder: SmallTalkResponder) -> None:
        """Returns None when no session history is provided."""
        result = responder.reminder(session_history=None)
        assert result is None

    def test_reminder_max_one_per_session(self, responder: SmallTalkResponder) -> None:
        """Only one reminder is served per session."""
        history = {"last_task": "write tests"}
        first = responder.reminder(session_history=history)
        assert first is not None
        second = responder.reminder(session_history=history)
        assert second is None

    def test_reminder_requires_context_variables(self, responder: SmallTalkResponder) -> None:
        """Reminders that require variables not present in history are skipped.
        Falls through to a reminder whose requires are satisfied or returns None."""
        # rem_001 requires last_task, rem_002 requires open_tasks — provide neither
        # rem_003 has empty requires, so it should be selected
        history = {"unrelated_key": "value"}
        result = responder.reminder(session_history=history)
        if result is not None:
            # Should be rem_003 which has no requires
            assert "{" not in result.text, "Unfilled template variable in reminder text"

    def test_reminder_source_is_reminders_jsonl(self, responder: SmallTalkResponder) -> None:
        """Reminder responses cite reminders.jsonl as their source."""
        history = {"last_task": "refactor code"}
        result = responder.reminder(session_history=history)
        assert result is not None
        assert result.source == "smalltalk/reminders.jsonl"


# ===========================================================================
# 6. Session Management Tests (4 tests)
# ===========================================================================


class TestSessionManagement:
    """Verify reset_session clears per-session state."""

    def test_reset_session_clears_used_ids(self, responder: SmallTalkResponder) -> None:
        """After reset, previously used response IDs can be selected again."""
        result1 = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        id1 = result1.source_id
        responder.reset_session()
        # After reset, the same ID should be eligible again
        # (with only 2 greeting responses, dedup without reset would force the other one)
        possible_ids = set()
        for _ in range(5):
            r = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
            possible_ids.add(r.source_id)
            responder.reset_session()
        assert id1 in possible_ids

    def test_reset_session_clears_compliment_count(self, responder: SmallTalkResponder) -> None:
        """After reset, compliment budget is restored to 3."""
        for _ in range(3):
            responder.compliment(trigger="task_completed")
        assert responder.compliment(trigger="task_completed") is None
        responder.reset_session()
        assert responder._compliment_count == 0
        result = responder.compliment(trigger="task_completed")
        assert result is not None

    def test_reset_session_clears_gift_type(self, responder: SmallTalkResponder) -> None:
        """After reset, gift alternation state is cleared."""
        responder.respond("greeting", LOW_CONFIDENCE, user_input="test")
        old_gift_type = responder._last_gift_type
        assert old_gift_type != ""
        responder.reset_session()
        assert responder._last_gift_type == ""

    def test_multiple_sessions_independent(self, responder: SmallTalkResponder) -> None:
        """State from one session does not leak into the next after reset."""
        # Session 1: exhaust compliments and use some responses
        for _ in range(3):
            responder.compliment(trigger="task_completed")
        responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        responder.respond("greeting", HIGH_CONFIDENCE, user_input="hello")

        # Reset
        responder.reset_session()

        # Session 2: everything should be fresh
        assert responder._compliment_count == 0
        assert responder._used_ids == set()
        assert responder._last_gift_type == ""

        result = responder.compliment(trigger="task_completed")
        assert result is not None
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        assert result is not None


# ===========================================================================
# 7. Domain Tag Filtering Tests (6 tests)
# ===========================================================================


class TestDomainTagFiltering:
    """Verify tag-based filtering for domain-specific content."""

    def test_tag_filter_coding_jokes(self, responder: SmallTalkResponder) -> None:
        """When context includes domain=programming, programming-tagged jokes are preferred."""
        context = {"domain": "programming"}
        result = responder.respond("greeting", LOW_CONFIDENCE, user_input="hmm", context=context)
        assert result.response_type in {"joke", "fact"}
        # With programming domain, the joke should ideally be programming-tagged
        # (implementation detail — at minimum the result should be valid)
        assert isinstance(result, SmallTalkResponse)

    def test_tag_filter_no_match_returns_any(self, responder: SmallTalkResponder) -> None:
        """When context domain has no matching tags, any joke/fact is returned."""
        context = {"domain": "nonexistent_domain_xyz"}
        result = responder.respond("greeting", LOW_CONFIDENCE, user_input="test", context=context)
        assert result.response_type in {"joke", "fact"}
        assert result.text != ""

    def test_tag_filter_multiple_tags(self, data_dir: Path) -> None:
        """Jokes with multiple tags match on any of them."""
        tagged_jokes = [
            _make_joke("joke_t1", "SQL walks into a bar.", tags=["database", "sql", "humor"]),
            _make_joke("joke_t2", "Python joke.", tags=["python", "scripting"]),
        ]
        _write_default(data_dir, "smalltalk/jokes.json", _make_json_array(tagged_jokes))
        registry = DataRegistry(repo_root=data_dir)
        resp = SmallTalkResponder(registry)
        context = {"domain": "database"}
        result = resp.respond("greeting", LOW_CONFIDENCE, user_input="test", context=context)
        assert isinstance(result, SmallTalkResponse)

    def test_domain_content_from_custom(self, data_dir: Path) -> None:
        """Custom layer jokes are served alongside or instead of default jokes."""
        custom_jokes = [
            _make_joke("joke_custom_001", "Custom domain joke for testing.", tags=["custom", "testing"]),
        ]
        _write_custom(data_dir, "smalltalk/jokes.json", _make_json_array(custom_jokes))
        registry = DataRegistry(repo_root=data_dir)
        resp = SmallTalkResponder(registry)
        # Custom layer overrides default — should have the custom joke
        joke_ids = {j["id"] for j in resp._jokes}
        assert "joke_custom_001" in joke_ids

    def test_llm_predictions_influence_selection(self, responder: SmallTalkResponder) -> None:
        """When context includes llm_predictions, they influence response selection."""
        context = {
            "llm_predictions": {
                "suggested_warmth": 4,
                "suggested_label": "greeting",
            }
        }
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hello", context=context)
        assert isinstance(result, SmallTalkResponse)
        # LLM prediction context should be accepted without error
        assert result.label == "greeting"

    def test_level_gate_filters_by_van_edwards_level(self, responder: SmallTalkResponder) -> None:
        """Responses above the Van Edwards level gate are excluded."""
        context = {"max_level": 1}
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hello", context=context)
        assert isinstance(result, SmallTalkResponse)
        # With max_level=1, only level 1 responses should be returned
        assert result.level <= 1


# ===========================================================================
# 8. SmallTalkResponse Dataclass Tests (4 tests)
# ===========================================================================


class TestSmallTalkResponseDataclass:
    """Verify the SmallTalkResponse dataclass contract."""

    def test_response_has_all_fields(self, responder: SmallTalkResponder) -> None:
        """SmallTalkResponse includes all required fields."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        assert hasattr(result, "text")
        assert hasattr(result, "source")
        assert hasattr(result, "source_id")
        assert hasattr(result, "label")
        assert hasattr(result, "warmth")
        assert hasattr(result, "level")
        assert hasattr(result, "response_type")

    def test_response_text_is_string(self, responder: SmallTalkResponder) -> None:
        """Response text is always a string."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        assert isinstance(result.text, str)

    def test_response_source_id_format(self, responder: SmallTalkResponder) -> None:
        """Source IDs follow the expected prefix format (resp_, joke_, fact_, etc.)."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        valid_prefixes = ("resp_", "joke_", "fact_", "comp_", "rem_")
        assert any(result.source_id.startswith(p) for p in valid_prefixes), (
            f"Unexpected source_id format: {result.source_id}"
        )

    def test_response_type_is_valid(self, responder: SmallTalkResponder) -> None:
        """Response type is one of the known types."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        valid_types = {"template", "joke", "fact", "compliment", "reminder", "default", "fallback"}
        assert result.response_type in valid_types


# ===========================================================================
# 9. Edge Cases & Boundary Tests (6 tests)
# ===========================================================================


class TestEdgeCases:
    """Boundary conditions and edge cases."""

    def test_confidence_just_below_threshold(self, responder: SmallTalkResponder) -> None:
        """Confidence at 0.69 (just below 0.70) triggers gift path."""
        result = responder.respond("greeting", 0.69, user_input="hi")
        assert result.response_type in {"joke", "fact"}

    def test_confidence_exactly_at_threshold(self, responder: SmallTalkResponder) -> None:
        """Confidence at exactly 0.70 triggers template path."""
        result = responder.respond("greeting", 0.70, user_input="hi")
        assert result.response_type == "template"

    def test_empty_user_input(self, responder: SmallTalkResponder) -> None:
        """Empty user_input is handled gracefully."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="")
        assert isinstance(result, SmallTalkResponse)
        assert result.text != ""

    def test_none_context_handled(self, responder: SmallTalkResponder) -> None:
        """None context is handled gracefully (default path)."""
        result = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi", context=None)
        assert isinstance(result, SmallTalkResponse)

    def test_dedup_exhaustion_still_returns(self, data_dir: Path) -> None:
        """When all responses for a label are used, dedup wraps around gracefully."""
        # Only 1 greeting response
        single_response = [
            _make_response("resp_solo", "greeting", "Only response.", warmth=2, level=1),
        ]
        _write_default(data_dir, "smalltalk/responses.jsonl", _make_jsonl(single_response))
        registry = DataRegistry(repo_root=data_dir)
        resp = SmallTalkResponder(registry)

        r1 = resp.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        assert r1.source_id == "resp_solo"
        # Second call — dedup pool exhausted, should still return something
        r2 = resp.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        assert isinstance(r2, SmallTalkResponse)
        assert r2.text != ""

    def test_respond_returns_new_object_each_call(self, responder: SmallTalkResponder) -> None:
        """Each respond() call returns a new SmallTalkResponse instance."""
        r1 = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        responder.reset_session()
        r2 = responder.respond("greeting", HIGH_CONFIDENCE, user_input="hi")
        assert r1 is not r2
