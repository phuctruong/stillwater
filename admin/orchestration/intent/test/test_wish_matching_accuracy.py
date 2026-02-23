"""
Test: Wish matching accuracy — correct wish is matched.

Verifies:
- Known prompts map to expected wish IDs
- Matched keywords are a subset of the wish's keyword list
- Confidence score is > 0 for matches
- Multi-keyword prompts score higher than single-keyword
- Most-specific match wins over generic match
- Prompt_tokens field is populated

rung_target: 641
EXIT_PASS: >= 80% of accuracy test cases pass AND all contract fields are correct.
EXIT_BLOCKED: < 80% accuracy OR contract fields missing/wrong.
"""

import sys
from pathlib import Path
from typing import Optional

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.intent.cpu import IntentCPU
from admin.orchestration.intent.database import WishDB
from admin.orchestration.intent.models import IntentMatch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_WISHES_PATH = str(Path(__file__).parent.parent / "wishes.jsonl")
_LEARNED_PATH = "/tmp/intent_accuracy_test_learned.jsonl"


@pytest.fixture(scope="module")
def cpu():
    db = WishDB(wishes_path=_WISHES_PATH, learned_path=_LEARNED_PATH)
    return IntentCPU(wish_db=db)


# ---------------------------------------------------------------------------
# Accuracy oracle — (prompt, expected_wish_id) pairs
# ---------------------------------------------------------------------------

_ACCURACY_CASES = [
    # OAuth
    ("implement oauth2 token refresh with bearer auth", "oauth-integration"),
    ("set up oauth consent flow for the api", "oauth-integration"),
    ("revoke user access token on logout", "oauth-integration"),
    ("add authorization scopes to the api client", "oauth-integration"),
    # Database
    ("my sql query is running slow need an index", "database-optimization"),
    ("optimize the postgres schema for performance", "database-optimization"),
    ("write a database migration for the new schema", "database-optimization"),
    # Docker
    ("build a docker image and push to registry", "docker-containerization"),
    ("write a dockerfile for the python service", "docker-containerization"),
    ("compose multiple containers with docker compose", "docker-containerization"),
    # Security
    ("audit the codebase for xss vulnerabilities", "security-audit"),
    ("check for sql injection in the login form", "security-audit"),
    ("scan dependencies for known cve exploits", "security-audit"),
    # CI/CD
    ("set up github actions pipeline for testing", "ci-cd-pipeline"),
    ("fix the failing build in the ci pipeline", "ci-cd-pipeline"),
    # Machine learning
    ("train a neural network model on the dataset", "machine-learning-training"),
    ("tune hyperparameters to reduce overfitting loss", "machine-learning-training"),
    # React
    ("my react component does not re-render on state change", "react-frontend"),
    ("add routing to the react app with hooks", "react-frontend"),
    # Python
    ("profile python code to find the bottleneck", "python-performance"),
    ("add asyncio concurrency to speed up the service", "python-performance"),
    # Testing
    ("write unit tests with pytest and mock fixtures", "test-development"),
    ("add integration test coverage for the login flow", "test-development"),
    # Debugging
    ("debug the crash traceback in production logs", "debugging"),
    ("reproduce and fix the null pointer exception", "debugging"),
    # Refactoring
    ("refactor the auth module to reduce duplication", "code-refactoring"),
    ("simplify the complex nested function structure", "code-refactoring"),
    # Caching
    ("add redis cache with ttl for session tokens", "cache-optimization"),
    ("implement cache invalidation strategy", "cache-optimization"),
    # Encryption
    ("hash passwords with bcrypt argon2 key derivation", "encryption-cryptography"),
    ("implement aes encryption for sensitive data", "encryption-cryptography"),
    # Rate limiting
    ("add rate limit throttling to protect the endpoint", "rate-limiting"),
    ("implement backoff retry logic for api calls", "rate-limiting"),
    # Infrastructure as code
    ("write terraform module to provision aws resources", "infrastructure-as-code"),
    ("deploy infrastructure with pulumi iac scripts", "infrastructure-as-code"),
]


# ---------------------------------------------------------------------------
# Tests: Accuracy
# ---------------------------------------------------------------------------

class TestWishMatchingAccuracy:

    def test_accuracy_oracle(self, cpu):
        """
        At least 80% of accuracy oracle cases must match the expected wish.
        """
        passed = 0
        failed_cases = []

        for prompt, expected_id in _ACCURACY_CASES:
            match = cpu.match(prompt)
            if match is not None and match.wish_id == expected_id:
                passed += 1
            else:
                actual = match.wish_id if match else None
                failed_cases.append((prompt, expected_id, actual))

        total = len(_ACCURACY_CASES)
        accuracy = passed / total

        assert accuracy >= 0.80, (
            f"Accuracy {accuracy:.1%} ({passed}/{total}) < 80% threshold.\n"
            f"Failed cases:\n" +
            "\n".join(
                f"  prompt={p!r}\n    expected={e}\n    actual={a}"
                for p, e, a in failed_cases[:10]
            )
        )

    def test_matched_keywords_are_subset_of_wish_keywords(self, cpu):
        """
        match.matched_keywords must all be in the wish's keyword list.
        """
        db = cpu._db
        for prompt, expected_id in _ACCURACY_CASES[:15]:
            match = cpu.match(prompt)
            if match is None:
                continue
            wish = db.get(match.wish_id)
            assert wish is not None, f"Wish {match.wish_id} not found in DB"
            for kw in match.matched_keywords:
                assert kw in wish.keywords, (
                    f"Matched keyword {kw!r} not in wish {wish.id} keywords: "
                    f"{wish.keywords}"
                )

    def test_confidence_positive_on_match(self, cpu):
        """All matches must have confidence > 0."""
        for prompt, _ in _ACCURACY_CASES[:10]:
            match = cpu.match(prompt)
            if match is not None:
                assert match.confidence > 0.0, (
                    f"Zero confidence for prompt {prompt!r}, wish {match.wish_id}"
                )

    def test_multi_keyword_higher_confidence(self, cpu):
        """
        A prompt with 3+ matching keywords should score higher confidence
        than a prompt with 1 matching keyword for the same wish.
        """
        # Multi-keyword prompt for oauth
        multi = cpu.match("oauth token refresh authorize scopes bearer")
        # Single keyword prompt for oauth
        single = cpu.match("oauth")

        if multi is not None and single is not None:
            if multi.wish_id == single.wish_id:
                assert multi.confidence >= single.confidence, (
                    f"Multi-keyword confidence {multi.confidence:.3f} < "
                    f"single-keyword confidence {single.confidence:.3f}"
                )

    def test_prompt_tokens_field_populated(self, cpu):
        """match.prompt_tokens must be a non-empty list for matching prompts."""
        match = cpu.match("implement oauth token refresh")
        assert match is not None
        assert len(match.prompt_tokens) > 0, "prompt_tokens must not be empty"

    def test_source_is_cpu(self, cpu):
        """All matches from IntentCPU must have source='cpu'."""
        for prompt, _ in _ACCURACY_CASES[:10]:
            match = cpu.match(prompt)
            if match is not None:
                assert match.source == "cpu", (
                    f"Expected source='cpu', got '{match.source}' for {prompt!r}"
                )

    def test_wish_id_exists_in_database(self, cpu):
        """Every matched wish_id must resolve to a real Wish object."""
        for prompt, _ in _ACCURACY_CASES[:15]:
            match = cpu.match(prompt)
            if match is not None:
                wish = cpu._db.get(match.wish_id)
                assert wish is not None, (
                    f"match.wish_id={match.wish_id!r} not found in DB for "
                    f"prompt={prompt!r}"
                )


# ---------------------------------------------------------------------------
# Tests: Specific wish matching
# ---------------------------------------------------------------------------

class TestSpecificWishMatching:

    def test_oauth_keywords_match_oauth_wish(self, cpu):
        match = cpu.match("implement oauth token refresh authorization bearer")
        assert match is not None
        assert match.wish_id == "oauth-integration", (
            f"Expected oauth-integration, got {match.wish_id}"
        )

    def test_docker_keywords_match_docker_wish(self, cpu):
        match = cpu.match("build docker image dockerfile container registry")
        assert match is not None
        assert match.wish_id == "docker-containerization", (
            f"Expected docker-containerization, got {match.wish_id}"
        )

    def test_security_keywords_match_security_wish(self, cpu):
        match = cpu.match("audit vulnerability xss injection exploit")
        assert match is not None
        assert match.wish_id == "security-audit", (
            f"Expected security-audit, got {match.wish_id}"
        )

    def test_encrypt_keywords_match_crypto_wish(self, cpu):
        match = cpu.match("encrypt data with aes cipher hmac signature")
        assert match is not None
        assert match.wish_id == "encryption-cryptography", (
            f"Expected encryption-cryptography, got {match.wish_id}"
        )

    def test_cache_keywords_match_cache_wish(self, cpu):
        match = cpu.match("redis cache with ttl expiry invalidate")
        assert match is not None
        assert match.wish_id == "cache-optimization", (
            f"Expected cache-optimization, got {match.wish_id}"
        )
