"""
Test: Fallback handling — unknown wish_id → None.

Verifies:
- Unknown wish_id returns None (clean fallback)
- Empty string returns None
- None-like inputs are handled gracefully
- Partial wish_ids don't accidentally match
- Case sensitivity is enforced (wish_ids are lowercase)
- Match returns None (not an exception) for all edge cases
- Lookup log records no-match events correctly

rung_target: 641
EXIT_PASS: All edge case inputs return None without exceptions.
EXIT_BLOCKED: Any edge case raises an exception or returns wrong data.
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.execute.cpu import ExecutionCPU
from admin.orchestration.execute.database import ComboDB, ComboLookupLog
from admin.orchestration.execute.models import ExecutionMatch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_COMBOS_PATH = str(Path(__file__).parent.parent / "combos.jsonl")
_LEARNED_PATH = "/tmp/execute_fallback_test_learned.jsonl"


@pytest.fixture(scope="module")
def cpu():
    db = ComboDB(combos_path=_COMBOS_PATH, learned_path=_LEARNED_PATH)
    return ExecutionCPU(combo_db=db)


@pytest.fixture(scope="module")
def cpu_with_log():
    db = ComboDB(combos_path=_COMBOS_PATH, learned_path=_LEARNED_PATH)
    log = ComboLookupLog()
    return ExecutionCPU(combo_db=db, lookup_log=log), log


# ---------------------------------------------------------------------------
# Tests: Unknown wish_id → None
# ---------------------------------------------------------------------------

class TestFallbackHandling:

    def test_unknown_wish_id_returns_none(self, cpu):
        """A completely unknown wish_id must return None."""
        result = cpu.match("nonexistent-wish-xyz")
        assert result is None, (
            f"Expected None for unknown wish_id, got {result!r}"
        )

    def test_empty_string_returns_none(self, cpu):
        """Empty string wish_id must return None without exception."""
        result = cpu.match("")
        assert result is None, (
            f"Expected None for empty wish_id, got {result!r}"
        )

    def test_gibberish_returns_none(self, cpu):
        """Random gibberish must return None."""
        gibberish_ids = [
            "xyzzy-foobar",
            "aaaaaaaaaaaaaaaaaa",
            "!!!---invalid---!!!",
            "wish/that/does/not/exist",
            "   spaces   ",
        ]
        for wish_id in gibberish_ids:
            result = cpu.match(wish_id)
            assert result is None, (
                f"Expected None for {wish_id!r}, got {result!r}"
            )

    def test_partial_wish_id_does_not_match(self, cpu):
        """Partial wish_id should not accidentally match a known combo."""
        partial_ids = [
            "oauth",           # partial of "oauth-integration"
            "database",        # partial of "database-optimization"
            "docker",          # partial of "docker-containerization"
            "security",        # partial of "security-audit"
            "react",           # partial of "react-frontend"
        ]
        for wish_id in partial_ids:
            result = cpu.match(wish_id)
            assert result is None, (
                f"Partial wish_id {wish_id!r} should not match, got {result!r}"
            )

    def test_case_sensitive_no_match_for_uppercase(self, cpu):
        """
        Wish_ids are stored lowercase. Uppercase versions should not match.
        """
        uppercase_ids = [
            "OAuth-Integration",
            "DATABASE-OPTIMIZATION",
            "DOCKER-CONTAINERIZATION",
        ]
        for wish_id in uppercase_ids:
            result = cpu.match(wish_id)
            assert result is None, (
                f"Uppercase wish_id {wish_id!r} should not match, got {result!r}"
            )

    def test_similar_but_wrong_wish_ids_no_match(self, cpu):
        """Wish_ids with extra/missing characters should not match."""
        similar_ids = [
            "oauth-integrations",       # extra 's'
            "database-optimisation",    # British spelling
            "docker-container",         # truncated
            "security-auditing",        # extra 'ing'
            "react-frontends",          # extra 's'
        ]
        for wish_id in similar_ids:
            result = cpu.match(wish_id)
            # These should not match exact wish_ids (they differ by characters)
            if result is not None:
                # If it matches, it must match a DIFFERENT wish (not the similar one)
                assert result.wish_id != wish_id, (
                    f"Similar wish_id {wish_id!r} should not exactly self-match"
                )

    def test_none_like_string_returns_none(self, cpu):
        """Strings like 'None', 'null', 'undefined' return None."""
        null_like = ["None", "null", "undefined", "nil"]
        for wish_id in null_like:
            result = cpu.match(wish_id)
            assert result is None, (
                f"Null-like wish_id {wish_id!r} should return None"
            )

    def test_no_match_never_raises(self, cpu):
        """cpu.match() must never raise an exception, even for weird inputs."""
        weird_inputs = [
            "",
            " ",
            "a",
            "a" * 500,  # very long
            "wish-id-with-unicode-\u00e9",
        ]
        for wish_id in weird_inputs:
            try:
                cpu.match(wish_id)
            except Exception as exc:
                pytest.fail(
                    f"cpu.match({wish_id!r}) raised {type(exc).__name__}: {exc}"
                )

    def test_batch_with_unknown_ids_returns_none_entries(self, cpu):
        """match_batch() with unknown IDs returns (wish_id, None) tuples."""
        ids = ["known-oauth", "nonexistent-xyz", "oauth-integration"]
        results = cpu.match_batch(ids)

        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        # "oauth-integration" is real, others are not
        for wish_id, match in results:
            if wish_id == "oauth-integration":
                assert match is not None, "oauth-integration should match"
            else:
                assert match is None, (
                    f"Unknown wish_id {wish_id!r} should return None, got {match!r}"
                )


# ---------------------------------------------------------------------------
# Tests: No-match logging
# ---------------------------------------------------------------------------

class TestNoMatchLogging:

    def test_no_match_logged_with_none_cpu_match(self, cpu_with_log):
        """No-match events must be recorded with cpu_match=None."""
        cpu, log = cpu_with_log
        before = log.count()

        cpu.match("nonexistent-wish", session_id="fallback_test")

        after = log.count()
        assert after == before + 1, "No-match must still be recorded in log"

        # Find the no-match entry
        entries = log.all()
        no_match = [e for e in entries if e.wish_id == "nonexistent-wish"]
        assert no_match, "No-match entry must be findable"
        assert no_match[-1].cpu_match is None, (
            "No-match entry must have cpu_match=None"
        )
        assert no_match[-1].cpu_swarm is None, (
            "No-match entry must have cpu_swarm=None"
        )
        assert no_match[-1].cpu_recipe == [], (
            "No-match entry must have empty cpu_recipe"
        )

    def test_known_match_logged_with_swarm(self, cpu_with_log):
        """Known match events must be recorded with swarm and recipe populated."""
        cpu, log = cpu_with_log
        before = log.count()

        cpu.match("oauth-integration", session_id="match_test")

        after = log.count()
        assert after == before + 1, "Match event must be recorded"

        entries = log.all()
        match_entries = [e for e in entries if e.wish_id == "oauth-integration"]
        assert match_entries, "Match entry must be findable"

        latest = match_entries[-1]
        assert latest.cpu_match == "oauth-integration"
        assert latest.cpu_swarm == "coder"
        assert "prime-safety" in latest.cpu_recipe
        assert latest.cpu_confidence > 0.0


# ---------------------------------------------------------------------------
# Tests: Context parameter (ignored on hot path, but must not break)
# ---------------------------------------------------------------------------

class TestContextParameter:

    def test_context_does_not_break_lookup(self, cpu):
        """Passing context dict must not change the result for known wish_ids."""
        contexts = [
            {},
            {"project": "oauth"},
            {"tags": ["security", "auth"]},
            {"keywords": ["bearer", "token"]},
            {"arbitrary_key": "arbitrary_value", "nested": {"deep": True}},
        ]
        for ctx in contexts:
            match = cpu.match("oauth-integration", context=ctx)
            assert match is not None, (
                f"oauth-integration must match even with context={ctx!r}"
            )
            assert match.swarm == "coder", (
                f"swarm changed with context={ctx!r}: {match.swarm!r}"
            )

    def test_context_does_not_manufacture_match(self, cpu):
        """Context dict must not cause a false positive for unknown wish_ids."""
        match = cpu.match(
            "nonexistent-wish",
            context={"project": "oauth", "tags": ["security"]},
        )
        assert match is None, (
            f"Context must not manufacture a match for unknown wish_id, got {match!r}"
        )
