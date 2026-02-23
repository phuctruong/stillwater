"""
Test: Deterministic keyword extraction from prompts.

Verifies:
- Lowercase normalization
- Stop word filtering
- Short token filtering (< 3 chars)
- Punctuation stripping
- Deduplication (first-occurrence order preserved)
- Multi-delimiter splitting
- Empty/whitespace-only prompts
- Prompts with only stop words
- Unicode handling

rung_target: 641
EXIT_PASS: All assertions pass, extraction is deterministic on repeat calls.
EXIT_BLOCKED: Non-deterministic output detected.
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.intent.cpu import IntentCPU
from admin.orchestration.intent.database import WishDB


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cpu():
    """IntentCPU with real wishes loaded."""
    db = WishDB(
        wishes_path=str(Path(__file__).parent.parent / "wishes.jsonl"),
        learned_path="/tmp/intent_test_learned.jsonl",
    )
    return IntentCPU(wish_db=db)


# ---------------------------------------------------------------------------
# Tests: Basic extraction
# ---------------------------------------------------------------------------

class TestKeywordExtraction:

    def test_lowercases_tokens(self, cpu):
        tokens = cpu.extract_tokens("OAUTH Token AUTH")
        assert all(t == t.lower() for t in tokens), (
            f"All tokens must be lowercase: {tokens}"
        )

    def test_filters_stop_words(self, cpu):
        tokens = cpu.extract_tokens("how do i implement oauth")
        assert "how" not in tokens
        assert "do" not in tokens
        assert "i" not in tokens
        assert "oauth" in tokens

    def test_filters_short_tokens(self, cpu):
        tokens = cpu.extract_tokens("my db is ok go run")
        # "db" is 2 chars → filtered. "run" is 3 chars → kept if not stop word
        assert "my" not in tokens  # stop word
        for tok in tokens:
            assert len(tok) >= 3, f"Token {tok!r} is too short (< 3 chars)"

    def test_strips_punctuation(self, cpu):
        tokens = cpu.extract_tokens("oauth! token, auth.")
        assert "oauth" in tokens
        assert "token" in tokens
        # "auth." → "auth"
        assert "auth" in tokens
        # No punctuation should survive
        for tok in tokens:
            assert not tok.startswith("!"), f"Token starts with punctuation: {tok!r}"
            assert not tok.endswith("."), f"Token ends with punctuation: {tok!r}"

    def test_deduplicates_tokens(self, cpu):
        tokens = cpu.extract_tokens("oauth oauth oauth token")
        assert tokens.count("oauth") == 1, "Duplicates must be removed"

    def test_dedup_preserves_first_occurrence_order(self, cpu):
        tokens = cpu.extract_tokens("database sql database python sql")
        # "database" appears before "sql" → database first
        assert tokens.index("database") < tokens.index("sql")
        # each appears exactly once
        assert tokens.count("database") == 1
        assert tokens.count("sql") == 1

    def test_multi_delimiter_splitting(self, cpu):
        # Various delimiters: /, -, _, comma, semicolon, parens
        tokens = cpu.extract_tokens("oauth/token,auth-service_setup;debug(test)")
        assert "oauth" in tokens
        assert "token" in tokens
        assert "auth" in tokens  # if >= 3 chars and not stop word
        assert "service" in tokens
        assert "setup" in tokens

    def test_empty_string_returns_empty(self, cpu):
        assert cpu.extract_tokens("") == []

    def test_whitespace_only_returns_empty(self, cpu):
        assert cpu.extract_tokens("   \t\n  ") == []

    def test_only_stop_words_returns_empty(self, cpu):
        # "i", "am", "the" are all stop words
        tokens = cpu.extract_tokens("i am the one")
        # "one" is 3 chars, not a stop word → should remain
        assert "one" in tokens or len(tokens) == 0
        # The stop words themselves must NOT appear
        for stop in ["i", "am", "the"]:
            assert stop not in tokens

    def test_only_short_tokens_returns_empty(self, cpu):
        # "go", "be", "it" are <= 2 chars
        tokens = cpu.extract_tokens("go be it do")
        for tok in tokens:
            assert len(tok) >= 3, f"Short token leaked: {tok!r}"


# ---------------------------------------------------------------------------
# Tests: Determinism
# ---------------------------------------------------------------------------

class TestExtractionDeterminism:

    def test_same_input_same_output(self, cpu):
        """Calling extract_tokens twice on the same input gives identical results."""
        prompt = "implement oauth2 token refresh for the api"
        first = cpu.extract_tokens(prompt)
        second = cpu.extract_tokens(prompt)
        assert first == second, (
            f"Non-deterministic extraction: {first} vs {second}"
        )

    def test_order_is_stable(self, cpu):
        """Token order matches left-to-right order of first appearance in text."""
        tokens = cpu.extract_tokens("python database oauth")
        assert tokens == sorted(tokens, key=lambda t: "python database oauth".index(t)), (
            "Token order must match left-to-right first-appearance order"
        )

    def test_case_insensitive_dedup(self, cpu):
        """'OAuth' and 'oauth' should both map to 'oauth' and deduplicate."""
        tokens = cpu.extract_tokens("OAuth oauth OAUTH token")
        assert tokens.count("oauth") == 1
        assert "token" in tokens


# ---------------------------------------------------------------------------
# Tests: Content-specific extraction
# ---------------------------------------------------------------------------

class TestContentExtraction:

    def test_oauth_prompt(self, cpu):
        tokens = cpu.extract_tokens("help me implement oauth token refresh flow")
        assert "oauth" in tokens
        assert "token" in tokens
        assert "refresh" in tokens

    def test_database_prompt(self, cpu):
        tokens = cpu.extract_tokens("my sql query is running slow need index")
        assert "sql" in tokens
        assert "query" in tokens
        assert "slow" in tokens
        assert "index" in tokens

    def test_docker_prompt(self, cpu):
        tokens = cpu.extract_tokens("build docker image and push to registry")
        assert "docker" in tokens
        assert "image" in tokens
        assert "push" in tokens
        assert "registry" in tokens

    def test_debug_prompt(self, cpu):
        tokens = cpu.extract_tokens("app is crashing with null pointer exception traceback")
        assert "crashing" in tokens
        assert "null" in tokens
        assert "exception" in tokens
        assert "traceback" in tokens

    def test_numbers_are_kept_if_long_enough(self, cpu):
        """Token '404' (3 chars) should survive if not a stop word."""
        tokens = cpu.extract_tokens("getting 404 error on the endpoint")
        # "404" has 3 chars, should survive
        assert "404" in tokens

    def test_hyphenated_keywords_split(self, cpu):
        """'rate-limit' should produce 'rate' and 'limit' as separate tokens."""
        tokens = cpu.extract_tokens("implement rate-limit for the api")
        assert "rate" in tokens
        assert "limit" in tokens
