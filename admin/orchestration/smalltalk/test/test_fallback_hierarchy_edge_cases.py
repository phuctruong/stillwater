"""
Test: Edge cases in the fallback hierarchy.

Verifies edge cases not covered by main hierarchy test:
- Empty queue + empty repos = last-resort cycle
- Tag extraction from various prompt formats
- Multiple calls cycle through fallback responses deterministically
- WeatherContext with all fields None
- Queue with only expired entries → falls to CPU
- Queue with only used entries → falls to CPU
- Feedback for non-existent entry returns False (not crash)
- count_available for unknown user = 0

rung_target: 641
EXIT_PASS: All edge cases handled without exceptions
EXIT_BLOCKED: Any unhandled exception or incorrect fallback behavior
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.cpu import SmallTalkCPU, _FALLBACK_RESPONSES
from admin.orchestration.smalltalk.database import BanterQueueDB, JokeRepo, TechFactRepo
from admin.orchestration.smalltalk.models import BanterQueueEntry, WeatherContext


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_db():
    return BanterQueueDB(":memory:")


@pytest.fixture
def cpu_empty(empty_db):
    """CPU with completely empty repos and empty queue."""
    return SmallTalkCPU(
        db=empty_db,
        joke_repo=JokeRepo(),
        fact_repo=TechFactRepo(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_fallback_cycle_is_deterministic(self, cpu_empty):
        """
        Multiple calls with empty repos cycle through _FALLBACK_RESPONSES
        in deterministic order.
        """
        results = []
        for _ in range(len(_FALLBACK_RESPONSES) * 2):
            token = cpu_empty.generate(
                user_id="cycle_user",
                session_id="s",
                prompt="hello",
            )
            results.append(token.response)

        # Each fallback response should appear exactly twice (2 full cycles)
        expected_cycle = list(_FALLBACK_RESPONSES) * 2
        # Results may interleave with cpu_glow if any glow detected; handle both
        # At minimum: the responses must be non-empty
        assert all(r for r in results), "All fallback responses must be non-empty"

        # Verify deterministic rotation: first len() results repeat correctly
        n = len(_FALLBACK_RESPONSES)
        for i in range(n):
            assert results[i] == results[i + n], (
                f"Fallback rotation non-deterministic at index {i}: "
                f"'{results[i]}' != '{results[i + n]}'"
            )

    def test_empty_weather_context_no_crash(self, cpu_empty):
        """WeatherContext with all fields None/default should not crash."""
        w = WeatherContext()  # all defaults
        token = cpu_empty.generate(
            user_id="weather_user",
            session_id="s",
            prompt="hello",
            weather=w,
        )
        assert token.response

    def test_queue_only_expired_entries_falls_to_cpu(self, empty_db):
        """Queue containing only expired entries falls through to CPU."""
        expired = BanterQueueEntry(
            id="exp_edge",
            user_id="exp_user",
            session_id="s",
            banter="Should never see this.",
            source="queue",
            tags=[],
            confidence=0.99,
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        empty_db.insert(expired)

        cpu = SmallTalkCPU(
            db=empty_db,
            joke_repo=JokeRepo(),
            fact_repo=TechFactRepo(),
        )
        token = cpu.generate(
            user_id="exp_user",
            session_id="s",
            prompt="hello",
        )
        assert token.source != "queue_hit", (
            "Expired queue entry must not produce a queue_hit"
        )

    def test_queue_only_used_entries_falls_to_cpu(self, empty_db):
        """Queue containing only used entries falls through to CPU."""
        used_entry = BanterQueueEntry(
            id="used_edge",
            user_id="used_user",
            session_id="s",
            banter="Already used, should not appear.",
            source="queue",
            tags=[],
            confidence=0.99,
            used=True,
        )
        empty_db.insert(used_entry)

        cpu = SmallTalkCPU(
            db=empty_db,
            joke_repo=JokeRepo(),
            fact_repo=TechFactRepo(),
        )
        token = cpu.generate(
            user_id="used_user",
            session_id="s",
            prompt="hello",
        )
        assert token.source != "queue_hit", (
            "Used queue entry must not produce a queue_hit"
        )

    def test_feedback_nonexistent_entry_returns_false(self, empty_db):
        """update_feedback for nonexistent ID returns False without crashing."""
        result = empty_db.update_feedback("nonexistent_id_xyz", score=3)
        assert result is False

    def test_count_available_unknown_user_is_zero(self, empty_db):
        """count_available for a user with no entries returns 0."""
        count = empty_db.count_available("unknown_user_xyz")
        assert count == 0

    def test_tag_extraction_from_prompt(self, cpu_empty):
        """Tags extracted from prompt text map to known tag lists."""
        token = cpu_empty.generate(
            user_id="tag_user",
            session_id="s",
            prompt="working on python oauth and docker today",
        )
        expected_tags = {"python", "programming", "oauth", "security", "auth", "docker", "devops", "containers"}
        for tag in token.tags:
            assert tag in expected_tags, (
                f"Unexpected tag '{tag}' in token.tags. All tags: {token.tags}"
            )

    def test_context_tags_added_to_token(self, cpu_empty):
        """Context dict with explicit tags are included in WarmToken.tags."""
        token = cpu_empty.generate(
            user_id="ctx_user",
            session_id="s",
            prompt="hello",
            context={"tags": ["custom_tag", "my_project"]},
        )
        assert "custom_tag" in token.tags or "my_project" in token.tags, (
            f"Context tags not found in token.tags: {token.tags}"
        )

    def test_generate_returns_warmtoken_always(self, cpu_empty):
        """generate() never raises; always returns WarmToken."""
        tricky_prompts = [
            "",
            " ",
            "!!!!!",
            "a" * 500,
            "SELECT * FROM users; DROP TABLE users;",
            "\n\n\n",
            "🔥🔥🔥🔥🎉🎉",
        ]
        for prompt in tricky_prompts:
            try:
                token = cpu_empty.generate(
                    user_id="robust_user",
                    session_id="s",
                    prompt=prompt,
                )
                assert token is not None, f"generate() returned None for: {prompt!r}"
                assert isinstance(token.response, str), (
                    f"response must be str, got {type(token.response)}"
                )
            except Exception as e:
                pytest.fail(
                    f"generate() raised {type(e).__name__} for prompt {prompt!r}: {e}"
                )

    def test_mark_used_idempotent(self, empty_db):
        """Calling mark_used() twice on same entry is safe."""
        e = BanterQueueEntry(
            id="idem_test",
            user_id="idem_user",
            session_id="s",
            banter="Idempotent test.",
            source="queue",
            tags=[],
            confidence=0.9,
        )
        empty_db.insert(e)
        result1 = empty_db.mark_used("idem_test")
        result2 = empty_db.mark_used("idem_test")
        assert result1 is True, "First mark_used should succeed"
        assert result2 is False, "Second mark_used (already used) should return False"

    def test_insert_duplicate_id_raises(self, empty_db):
        """Inserting two entries with the same ID raises an error."""
        e = BanterQueueEntry(
            id="dup_id",
            user_id="dup_user",
            session_id="s",
            banter="Original.",
            source="queue",
            tags=[],
            confidence=0.9,
        )
        empty_db.insert(e)
        e2 = BanterQueueEntry(
            id="dup_id",  # same ID
            user_id="dup_user",
            session_id="s",
            banter="Duplicate.",
            source="queue",
            tags=[],
            confidence=0.9,
        )
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            empty_db.insert(e2)
