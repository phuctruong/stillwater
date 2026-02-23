"""
Test: Fallback hierarchy — queue miss → CPU → repos.

Verifies the full fallback chain:
  1. Queue hit path (source == queue_hit)
  2. CPU high-GLOW path (source == cpu_glow)
  3. CPU repo path: joke (source == cpu_repo)
  4. CPU repo path: weather banter (source == cpu_repo)
  5. CPU repo path: tech fact (source == cpu_repo)
  6. Last-resort fallback (source == fallback or cpu_repo with no repos)

rung_target: 641
EXIT_PASS: All source types verified, correct priority ordering confirmed
EXIT_BLOCKED: Incorrect source labeling or wrong path taken
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.cpu import SmallTalkCPU
from admin.orchestration.smalltalk.database import (
    BanterQueueDB,
    JokeRepo,
    TechFactRepo,
)
from admin.orchestration.smalltalk.models import (
    BanterQueueEntry,
    JokeEntry,
    TechFactEntry,
    WeatherContext,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_with_one_entry():
    """DB containing exactly one entry for user_alice."""
    db = BanterQueueDB(":memory:")
    db.insert(BanterQueueEntry(
        id="q_one",
        user_id="user_alice",
        session_id="s1",
        banter="Queue banter for Alice.",
        source="job",
        tags=["general"],
        confidence=0.9,
    ))
    return db


@pytest.fixture
def db_empty():
    return BanterQueueDB(":memory:")


@pytest.fixture
def joke_repo_with_one():
    """JokeRepo pre-loaded with a single joke."""
    repo = JokeRepo()
    repo._jokes.append(JokeEntry(
        id="j001",
        joke="Why do programmers prefer dark mode? Because light attracts bugs.",
        tags=["programming", "general"],
        min_glow=0.0,
        max_glow=0.6,
        confidence=0.9,
    ))
    return repo


@pytest.fixture
def fact_repo_with_one():
    """TechFactRepo pre-loaded with a single fact."""
    repo = TechFactRepo()
    repo._facts.append(TechFactEntry(
        id="f001",
        fact="A database index is like a book's table of contents.",
        tags=["database", "general"],
        confidence=0.95,
    ))
    return repo


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFallbackHierarchy:

    def test_queue_hit_takes_priority(self, db_with_one_entry, joke_repo_with_one, fact_repo_with_one):
        """Queue hit is always preferred over CPU fallback."""
        cpu = SmallTalkCPU(
            db=db_with_one_entry,
            joke_repo=joke_repo_with_one,
            fact_repo=fact_repo_with_one,
        )
        token = cpu.generate(
            user_id="user_alice",
            session_id="s1",
            prompt="hi",
        )
        assert token.source == "queue_hit", (
            f"Expected queue_hit, got '{token.source}'. Response: {token.response!r}"
        )
        assert token.response == "Queue banter for Alice."

    def test_high_glow_after_queue_miss(self, db_empty, joke_repo_with_one):
        """High-GLOW CPU path taken when queue is empty and GLOW > 0.6."""
        cpu = SmallTalkCPU(
            db=db_empty,
            joke_repo=joke_repo_with_one,
            fact_repo=TechFactRepo(),
        )
        # This prompt should produce GLOW > 0.6
        token = cpu.generate(
            user_id="user_x",
            session_id="s1",
            prompt="I just SHIPPED it!! AMAZING!! We won the hackathon!!",
        )
        assert token.source == "cpu_glow", (
            f"Expected cpu_glow, got '{token.source}'. GLOW={token.glow_score}"
        )
        assert token.glow_score > 0.6

    def test_joke_fallback_when_low_glow(self, db_empty, joke_repo_with_one):
        """Joke repo is used when queue miss + low GLOW + joke available."""
        cpu = SmallTalkCPU(
            db=db_empty,
            joke_repo=joke_repo_with_one,
            fact_repo=TechFactRepo(),
        )
        # Low-GLOW prompt
        token = cpu.generate(
            user_id="user_x",
            session_id="s1",
            prompt="working on python today",
        )
        assert token.source == "cpu_repo", (
            f"Expected cpu_repo, got '{token.source}'"
        )
        assert token.glow_score <= 0.6
        # Response should contain the joke text
        assert "dark mode" in token.response.lower() or "bug" in token.response.lower(), (
            f"Expected joke content, got: {token.response!r}"
        )

    def test_weather_banter_when_no_joke_match(self, db_empty):
        """Weather banter is used when queue miss + no joke match + weather provided."""
        cpu = SmallTalkCPU(
            db=db_empty,
            joke_repo=JokeRepo(),     # empty jokes
            fact_repo=TechFactRepo(),  # empty facts
        )
        weather = WeatherContext(is_raining=True)
        token = cpu.generate(
            user_id="user_x",
            session_id="s1",
            prompt="hey",
            weather=weather,
        )
        assert token.source == "cpu_repo", (
            f"Expected cpu_repo for weather banter, got '{token.source}'"
        )
        assert "rain" in token.response.lower() or "focus" in token.response.lower(), (
            f"Expected weather-themed response, got: {token.response!r}"
        )

    def test_tech_fact_when_no_joke_no_weather(self, db_empty, fact_repo_with_one):
        """Tech fact is used when queue miss + no joke match + no weather."""
        cpu = SmallTalkCPU(
            db=db_empty,
            joke_repo=JokeRepo(),      # empty jokes
            fact_repo=fact_repo_with_one,
        )
        token = cpu.generate(
            user_id="user_x",
            session_id="s1",
            prompt="working on database queries",
        )
        assert token.source == "cpu_repo"
        assert "database" in token.response.lower() or "index" in token.response.lower(), (
            f"Expected fact content, got: {token.response!r}"
        )

    def test_last_resort_fallback_non_empty(self, db_empty):
        """Last-resort fallback must always return a non-empty string."""
        cpu = SmallTalkCPU(
            db=db_empty,
            joke_repo=JokeRepo(),      # empty
            fact_repo=TechFactRepo(),  # empty
        )
        # No weather, no local_hour — forces last-resort
        token = cpu.generate(
            user_id="user_last",
            session_id="s_last",
            prompt="hello",
        )
        assert token.response, "Last-resort fallback must produce non-empty string"

    def test_second_call_gets_second_queue_entry(self, db_with_one_entry):
        """After consuming one queue entry, second call gets CPU fallback."""
        cpu = SmallTalkCPU(
            db=db_with_one_entry,
            joke_repo=JokeRepo(),
            fact_repo=TechFactRepo(),
        )
        # First call: queue hit
        token1 = cpu.generate(
            user_id="user_alice",
            session_id="s1",
            prompt="hi",
            local_hour=9,
        )
        assert token1.source == "queue_hit"

        # Second call: queue exhausted → CPU fallback
        token2 = cpu.generate(
            user_id="user_alice",
            session_id="s1",
            prompt="hi again",
            local_hour=9,
        )
        assert token2.source in ("cpu_glow", "cpu_repo", "fallback"), (
            f"Expected CPU fallback, got '{token2.source}'"
        )
