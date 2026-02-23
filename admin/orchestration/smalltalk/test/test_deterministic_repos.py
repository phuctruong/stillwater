"""
Test: Deterministic repos (jokes.jsonl, weather_banter.py, tech_facts.jsonl).

Verifies:
- jokes.jsonl loads correctly (10+ entries)
- tech_facts.jsonl loads correctly (10+ entries)
- JokeRepo.find() is deterministic (same input → same output always)
- TechFactRepo.find() is deterministic
- weather_banter.generate_weather_banter() is deterministic and covers all rule branches
- Tag matching logic works correctly
- GLOW range filtering works correctly
- No randomness: calling find() twice returns identical result

rung_target: 641
EXIT_PASS: All repos load, all lookups deterministic, all rule branches covered
EXIT_BLOCKED: Non-determinism detected (same input, different output)
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.database import JokeRepo, TechFactRepo
from admin.orchestration.smalltalk.models import JokeEntry, TechFactEntry, WeatherContext
from admin.orchestration.smalltalk.weather_banter import generate_weather_banter

# Data directory (contains the real jokes.jsonl and tech_facts.jsonl)
_DATA_DIR = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_jokes():
    repo = JokeRepo()
    repo.load_jsonl(str(_DATA_DIR / "jokes.jsonl"))
    return repo


@pytest.fixture(scope="module")
def real_facts():
    repo = TechFactRepo()
    repo.load_jsonl(str(_DATA_DIR / "tech_facts.jsonl"))
    return repo


# ---------------------------------------------------------------------------
# Joke repo tests
# ---------------------------------------------------------------------------

class TestJokeRepo:

    def test_jokes_load_minimum_count(self, real_jokes):
        """jokes.jsonl must have at least 10 entries."""
        count = real_jokes.count()
        assert count >= 10, f"Expected >= 10 jokes, got {count}"

    def test_joke_find_is_deterministic(self, real_jokes):
        """Same tags + glow → same joke every call."""
        result_1 = real_jokes.find(tags=["programming"], glow=0.2)
        result_2 = real_jokes.find(tags=["programming"], glow=0.2)
        assert result_1 is not None
        assert result_2 is not None
        assert result_1.id == result_2.id, (
            f"Non-deterministic: first={result_1.id}, second={result_2.id}"
        )

    def test_joke_glow_range_filter(self, real_jokes):
        """Jokes outside GLOW range should not be returned for that GLOW."""
        # Jokes have max_glow typically 0.4-0.5
        # High GLOW (0.9) should not match most jokes
        result_high_glow = real_jokes.find(tags=["general"], glow=0.9)
        if result_high_glow:
            assert result_high_glow.min_glow <= 0.9 <= result_high_glow.max_glow, (
                f"Returned joke outside GLOW range: "
                f"min={result_high_glow.min_glow}, max={result_high_glow.max_glow}"
            )

    def test_joke_tag_matching(self, real_jokes):
        """Tag-matched jokes should have the requested tag."""
        result = real_jokes.find(tags=["sql"], glow=0.2)
        assert result is not None, "Should find a SQL-tagged joke"
        assert "sql" in result.tags, (
            f"Returned joke has tags {result.tags}, expected 'sql'"
        )

    def test_joke_empty_tags_returns_any(self, real_jokes):
        """Empty tag list → return any GLOW-matching joke."""
        result = real_jokes.find(tags=[], glow=0.2)
        assert result is not None, "Should return a joke for empty tags"

    def test_jokes_all_have_required_fields(self, real_jokes):
        """All jokes must have id, joke text, tags, confidence."""
        for joke in real_jokes.all():
            assert joke.id, f"Joke missing id: {joke}"
            assert joke.joke, f"Joke missing text: {joke.id}"
            assert isinstance(joke.tags, list), f"Joke {joke.id} tags must be list"
            assert 0.0 <= joke.confidence <= 1.0, (
                f"Joke {joke.id} confidence out of range: {joke.confidence}"
            )
            assert joke.min_glow <= joke.max_glow, (
                f"Joke {joke.id} min_glow > max_glow"
            )

    def test_joke_python_tag_match(self, real_jokes):
        """Should find a joke tagged 'python'."""
        result = real_jokes.find(tags=["python"], glow=0.2)
        assert result is not None, "Expected a Python-tagged joke"

    def test_joke_git_tag_match(self, real_jokes):
        """Should find a joke tagged 'git'."""
        result = real_jokes.find(tags=["git"], glow=0.2)
        assert result is not None, "Expected a git-tagged joke"


# ---------------------------------------------------------------------------
# Tech fact repo tests
# ---------------------------------------------------------------------------

class TestTechFactRepo:

    def test_facts_load_minimum_count(self, real_facts):
        """tech_facts.jsonl must have at least 10 entries."""
        count = real_facts.count()
        assert count >= 10, f"Expected >= 10 facts, got {count}"

    def test_fact_find_is_deterministic(self, real_facts):
        """Same tags → same fact every call."""
        result_1 = real_facts.find(tags=["oauth"])
        result_2 = real_facts.find(tags=["oauth"])
        assert result_1 is not None
        assert result_2 is not None
        assert result_1.id == result_2.id, (
            f"Non-deterministic: first={result_1.id}, second={result_2.id}"
        )

    def test_fact_tag_matching(self, real_facts):
        """Tag-matched fact should have the requested tag."""
        result = real_facts.find(tags=["python"])
        assert result is not None
        assert "python" in result.tags

    def test_fact_empty_tags_returns_first(self, real_facts):
        """Empty tags → returns first fact in file order."""
        result = real_facts.find(tags=[])
        assert result is not None

    def test_facts_all_have_required_fields(self, real_facts):
        """All facts must have id, fact text, tags, confidence."""
        for fact in real_facts.all():
            assert fact.id, f"Fact missing id: {fact}"
            assert fact.fact, f"Fact missing text: {fact.id}"
            assert isinstance(fact.tags, list)
            assert 0.0 <= fact.confidence <= 1.0

    def test_fact_oauth_match(self, real_facts):
        """Should find OAuth-tagged fact."""
        result = real_facts.find(tags=["oauth"])
        assert result is not None
        assert "oauth" in result.fact.lower() or "token" in result.fact.lower()

    def test_fact_security_match(self, real_facts):
        """Should find security-tagged fact."""
        result = real_facts.find(tags=["security"])
        assert result is not None

    def test_fact_database_match(self, real_facts):
        """Should find database-tagged fact."""
        result = real_facts.find(tags=["database"])
        assert result is not None


# ---------------------------------------------------------------------------
# Weather banter tests
# ---------------------------------------------------------------------------

class TestWeatherBanter:

    def test_rain_detected(self):
        """Raining weather produces rain-themed banter."""
        w = WeatherContext(is_raining=True)
        result = generate_weather_banter(weather=w)
        assert result, "Must return non-empty string"
        assert "rain" in result.lower() or "focus" in result.lower()

    def test_snow_detected(self):
        """Snowing weather produces snow-themed banter."""
        w = WeatherContext(is_snowing=True)
        result = generate_weather_banter(weather=w)
        assert "snow" in result.lower() or "warm" in result.lower() or "cozy" in result.lower()

    def test_high_temperature(self):
        """Very hot (>= 90F) produces hot-themed banter."""
        w = WeatherContext(temp_f=95.0)
        result = generate_weather_banter(weather=w)
        assert result, "Must return non-empty"
        assert "hot" in result.lower() or "hydrat" in result.lower() or "ac" in result.lower()

    def test_freezing_temperature(self):
        """Sub-freezing (<20F) produces freezing-themed banter."""
        w = WeatherContext(temp_f=5.0)
        result = generate_weather_banter(weather=w)
        assert "freez" in result.lower() or "cpu" in result.lower() or "warm" in result.lower()

    def test_location_override_sf(self):
        """San Francisco location triggers specific banter."""
        w = WeatherContext(location="San Francisco")
        result = generate_weather_banter(weather=w)
        assert "sf" in result.lower() or "golden gate" in result.lower() or "san francisco" in result.lower()

    def test_location_override_seattle(self):
        """Seattle location triggers specific banter."""
        w = WeatherContext(location="Seattle")
        result = generate_weather_banter(weather=w)
        assert "seattle" in result.lower() or "rain" in result.lower()

    def test_time_morning(self):
        """Morning hour (6-9) produces morning-themed banter."""
        result = generate_weather_banter(local_hour=7)
        assert result
        assert "morning" in result.lower() or "coffee" in result.lower() or "early" in result.lower()

    def test_time_evening(self):
        """Evening hour (17-20) produces evening-themed banter."""
        result = generate_weather_banter(local_hour=18)
        assert result
        assert "evening" in result.lower() or "dinner" in result.lower() or "feature" in result.lower()

    def test_time_midnight(self):
        """Midnight hour (0-5) produces night-themed banter."""
        result = generate_weather_banter(local_hour=2)
        assert result
        assert "midnight" in result.lower() or "night" in result.lower() or "commit" in result.lower()

    def test_none_weather_none_hour_returns_fallback(self):
        """No weather + no hour produces the generic fallback."""
        result = generate_weather_banter(weather=None, local_hour=None)
        assert result, "Must return non-empty fallback string"

    def test_deterministic_same_input(self):
        """Same input always produces the same output."""
        w = WeatherContext(is_raining=True, location="Seattle")
        r1 = generate_weather_banter(weather=w, local_hour=14)
        r2 = generate_weather_banter(weather=w, local_hour=14)
        assert r1 == r2, f"Non-deterministic: '{r1}' != '{r2}'"

    def test_condition_string_cloudy(self):
        """condition='cloudy' triggers cloudy banter."""
        w = WeatherContext(condition="cloudy")
        result = generate_weather_banter(weather=w)
        assert result
        # Should match the cloudy rule
        assert "cloud" in result.lower() or "focus" in result.lower() or "clarity" in result.lower()
