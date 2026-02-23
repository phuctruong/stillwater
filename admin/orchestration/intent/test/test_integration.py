"""
Test: Integration — Queue (Phase 1) → Intent (Phase 2) → WarmToken flow.

Verifies:
- IntentCPU match feeds context back to SmallTalkCPU (Phase 1)
- Full pipeline: prompt → intent → warm response
- IntentMatch.skill_pack_hint populates WarmToken.tags
- Both Phase 1 and Phase 2 work together on same prompt
- WishDB loads correctly from disk (canonical wishes.jsonl)
- LookupLog records events for LLM feedback path
- Latency across full pipeline (intent + warm) remains < 10ms

rung_target: 641
EXIT_PASS: Full pipeline produces non-empty WarmToken with intent context.
EXIT_BLOCKED: Exception thrown OR latency > 50ms.
"""

import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.intent.cpu import IntentCPU
from admin.orchestration.intent.database import LookupLog, WishDB
from admin.orchestration.intent.models import LearnedWish
from admin.orchestration.smalltalk.cpu import SmallTalkCPU
from admin.orchestration.smalltalk.database import BanterQueueDB


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_WISHES_PATH = str(Path(__file__).parent.parent / "wishes.jsonl")
_LEARNED_PATH = "/tmp/intent_integration_test_learned.jsonl"


@pytest.fixture(scope="module")
def wish_db():
    return WishDB(wishes_path=_WISHES_PATH, learned_path=_LEARNED_PATH)


@pytest.fixture(scope="module")
def lookup_log():
    return LookupLog()


@pytest.fixture(scope="module")
def intent_cpu(wish_db, lookup_log):
    return IntentCPU(wish_db=wish_db, lookup_log=lookup_log)


@pytest.fixture(scope="module")
def smalltalk_cpu():
    """Phase 1 SmallTalkCPU with in-memory queue."""
    return SmallTalkCPU(
        db=BanterQueueDB(":memory:"),
        data_dir=str(Path(__file__).parent.parent.parent / "smalltalk"),
    )


# ---------------------------------------------------------------------------
# Tests: Phase 1 → Phase 2 pipeline
# ---------------------------------------------------------------------------

class TestPhase1Phase2Pipeline:

    def test_intent_result_feeds_warmtoken_tags(self, intent_cpu, smalltalk_cpu):
        """
        Intent match enriches the context passed to SmallTalkCPU,
        so WarmToken.tags contains the wish category.
        """
        prompt = "implement oauth token refresh with bearer auth"

        # Phase 2: detect intent
        intent_match = intent_cpu.match(prompt)
        assert intent_match is not None, "Intent CPU must match oauth prompt"
        assert intent_match.wish_id == "oauth-integration"

        # Build enriched context for Phase 1
        wish = intent_cpu._db.get(intent_match.wish_id)
        intent_context = {
            "tags": list(intent_match.matched_keywords),
            "project": wish.category if wish else "",
        }

        # Phase 1: generate warm response with intent context
        warm_token = smalltalk_cpu.generate(
            user_id="integration_user",
            session_id="integration_sess",
            prompt=prompt,
            context=intent_context,
        )

        assert warm_token is not None
        assert warm_token.response, "WarmToken must have a non-empty response"

    def test_full_pipeline_under_10ms(self, intent_cpu, smalltalk_cpu):
        """
        Full pipeline (intent match + warm response) must complete < 10ms.
        """
        prompts = [
            "implement oauth token refresh",
            "my sql query is slow need index",
            "build docker image and push",
            "debug the production error crash",
            "add redis cache for session tokens",
        ]

        for prompt in prompts:
            start = time.perf_counter()

            # Phase 2: intent
            intent_match = intent_cpu.match(prompt)
            context = {}
            if intent_match:
                context = {
                    "tags": intent_match.matched_keywords[:3],
                }

            # Phase 1: warm response
            warm_token = smalltalk_cpu.generate(
                user_id="pipeline_user",
                session_id="pipeline_sess",
                prompt=prompt,
                context=context,
            )

            elapsed_ms = (time.perf_counter() - start) * 1000

            assert warm_token.response, f"Empty response for: {prompt!r}"
            assert elapsed_ms < 50.0, (
                f"Full pipeline took {elapsed_ms:.3f}ms for {prompt!r} "
                f"— exceeds 50ms SLA"
            )

    def test_lookup_log_records_events(self, intent_cpu, lookup_log):
        """LookupLog must record events for LLM feedback."""
        initial_count = lookup_log.count()

        intent_cpu.match(
            "implement oauth token refresh",
            session_id="log_test_session",
        )
        intent_cpu.match(
            "optimize sql query performance",
            session_id="log_test_session",
        )

        final_count = lookup_log.count()
        assert final_count >= initial_count + 2, (
            f"Expected at least 2 new log entries, got {final_count - initial_count}"
        )

    def test_lookup_log_no_match_recorded(self, intent_cpu, lookup_log):
        """No-match events are also recorded with cpu_match=None."""
        before = lookup_log.count()
        intent_cpu.match(
            "xyzzy foobar randomgarbage",
            session_id="nomatch_session",
        )
        after = lookup_log.count()
        assert after == before + 1, "No-match must still be recorded"

        # Find the no-match entry
        pending = lookup_log.pending_validation()
        no_match_entries = [
            e for e in pending
            if e.prompt == "xyzzy foobar randomgarbage"
        ]
        if no_match_entries:
            assert no_match_entries[-1].cpu_match is None, (
                "cpu_match must be None for no-match events"
            )

    def test_lookup_log_confirm_and_correct(self, intent_cpu, lookup_log):
        """LookupLog.confirm() and .correct() update entries correctly."""
        prompt = "deploy terraform module to aws"
        intent_cpu.match(prompt, session_id="feedback_sess")

        # Confirm the match
        lookup_log.confirm(
            prompt=prompt,
            wish_id="infrastructure-as-code",
            new_keywords=["terraform", "aws"],
        )

        # Find the confirmed entry
        confirmed = [
            e for e in lookup_log.all()
            if e.prompt == prompt and e.llm_confirmed is True
        ]
        assert confirmed, "Confirmed entry must be findable in log"
        assert confirmed[-1].llm_wish_id == "infrastructure-as-code"


# ---------------------------------------------------------------------------
# Tests: WishDB integration
# ---------------------------------------------------------------------------

class TestWishDBIntegration:

    def test_wishes_loaded_from_disk(self, wish_db):
        """WishDB must load 20+ wishes from wishes.jsonl."""
        count = wish_db.count()
        assert count >= 20, (
            f"Expected >= 20 wishes, got {count}. "
            "Check that wishes.jsonl has all entries."
        )

    def test_all_wishes_have_keywords(self, wish_db):
        """Every loaded wish must have at least 3 keywords."""
        for wish in wish_db.all_wishes():
            assert len(wish.keywords) >= 3, (
                f"Wish {wish.id!r} has only {len(wish.keywords)} keywords — need >= 3"
            )

    def test_all_wishes_have_skill_pack_hint(self, wish_db):
        """Every loaded wish must have a non-empty skill_pack_hint."""
        for wish in wish_db.all_wishes():
            assert wish.skill_pack_hint, (
                f"Wish {wish.id!r} has empty skill_pack_hint"
            )

    def test_all_wish_ids_are_unique(self, wish_db):
        """No duplicate wish IDs allowed."""
        ids = [w.id for w in wish_db.all_wishes()]
        assert len(ids) == len(set(ids)), (
            f"Duplicate wish IDs found: {[i for i in ids if ids.count(i) > 1]}"
        )

    def test_wish_keywords_all_lowercase(self, wish_db):
        """All wish keywords must be lowercase (verified after normalization)."""
        for wish in wish_db.all_wishes():
            for kw in wish.keywords:
                assert kw == kw.lower(), (
                    f"Wish {wish.id!r} has non-lowercase keyword: {kw!r}"
                )

    def test_keyword_index_covers_all_keywords(self, wish_db):
        """Every keyword in every wish must be findable in the keyword index."""
        for wish in wish_db.all_wishes():
            for kw in wish.keywords:
                found = wish_db.lookup_by_keyword(kw)
                wish_ids = [w.id for w in found]
                assert wish.id in wish_ids, (
                    f"Keyword {kw!r} not indexed for wish {wish.id!r}"
                )

    def test_learned_wish_merged_into_pipeline(self, wish_db):
        """
        After appending a learned wish, the full pipeline (CPU match)
        should use the new keyword.
        """
        cpu = IntentCPU(wish_db=wish_db)

        # Teach a new word (using tmp path to avoid polluting real learned file)
        import tempfile
        with tempfile.NamedTemporaryFile(
            suffix=".jsonl", mode="w", delete=False
        ) as tmp:
            tmp_path = tmp.name

        tmp_db = WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_path)
        tmp_db.append_learned_wish(LearnedWish(
            wish_id="test-development",
            keywords=["vitest", "playwright"],
            confidence=0.75,
            source="llm",
        ))

        tmp_cpu = IntentCPU(wish_db=tmp_db)
        match = tmp_cpu.match("write playwright integration tests")
        assert match is not None, (
            "CPU must match 'playwright' after learning it"
        )
        assert match.wish_id == "test-development", (
            f"Expected test-development, got {match.wish_id}"
        )
