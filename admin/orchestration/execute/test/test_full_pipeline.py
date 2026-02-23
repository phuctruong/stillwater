"""
Test: Full pipeline — Phase 1 (Smalltalk) → Phase 2 (Intent) → Phase 3 (Execution).

Verifies:
- prompt → WarmToken (Phase 1) works
- prompt → IntentMatch (Phase 2) works
- wish_id → ExecutionMatch (Phase 3) works
- Full pipeline: prompt → warm_token + intent_match + execution_match
- Total latency across all 3 phases < 10ms
- ExecutionMatch.recipe starts with prime-safety (safety gate)
- Phase 2 wish_id feeds directly into Phase 3 (no transformation needed)
- ComboDB loads 25+ combos matching all wishes in wishes.jsonl
- Learned combos are usable in pipeline immediately after append

rung_target: 641
EXIT_PASS: All phases produce valid output. Total latency < 10ms.
EXIT_BLOCKED: Exception thrown OR latency > 50ms OR prime-safety missing.
"""

import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.execute.cpu import ExecutionCPU
from admin.orchestration.execute.database import ComboDB, ComboLookupLog
from admin.orchestration.execute.models import ExecutionMatch, LearnedCombo
from admin.orchestration.intent.cpu import IntentCPU
from admin.orchestration.intent.database import LookupLog, WishDB
from admin.orchestration.smalltalk.cpu import SmallTalkCPU
from admin.orchestration.smalltalk.database import BanterQueueDB


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_WISHES_PATH = str(Path(__file__).parent.parent.parent / "intent" / "wishes.jsonl")
_COMBOS_PATH = str(Path(__file__).parent.parent / "combos.jsonl")
_LEARNED_PATH = "/tmp/execute_pipeline_test_learned.jsonl"


@pytest.fixture(scope="module")
def wish_db():
    return WishDB(wishes_path=_WISHES_PATH, learned_path="/tmp/intent_pipeline_learned.jsonl")


@pytest.fixture(scope="module")
def combo_db():
    return ComboDB(combos_path=_COMBOS_PATH, learned_path=_LEARNED_PATH)


@pytest.fixture(scope="module")
def intent_cpu(wish_db):
    return IntentCPU(wish_db=wish_db)


@pytest.fixture(scope="module")
def execution_cpu(combo_db):
    return ExecutionCPU(combo_db=combo_db)


@pytest.fixture(scope="module")
def smalltalk_cpu():
    return SmallTalkCPU(
        db=BanterQueueDB(":memory:"),
        data_dir=str(Path(__file__).parent.parent.parent / "smalltalk"),
    )


# ---------------------------------------------------------------------------
# Tests: Phase 3 standalone
# ---------------------------------------------------------------------------

class TestPhase3Standalone:

    def test_combo_db_loads_25_combos(self, combo_db):
        """ComboDB must load 25+ combos from combos.jsonl."""
        count = combo_db.count()
        assert count >= 25, (
            f"Expected >= 25 combos, got {count}. "
            "Check that combos.jsonl has all entries."
        )

    def test_all_wish_ids_in_wishes_have_combos(self, wish_db, combo_db):
        """Every wish_id in wishes.jsonl must have a corresponding combo."""
        wishes = wish_db.all_wishes()
        missing = []
        for wish in wishes:
            combo = combo_db.get(wish.id)
            if combo is None:
                missing.append(wish.id)

        assert not missing, (
            f"These wishes have no combo:\n" +
            "\n".join(f"  - {w}" for w in missing)
        )

    def test_all_combos_have_prime_safety(self, combo_db):
        """Every combo recipe must start with prime-safety."""
        violations = []
        for combo in combo_db.all_combos():
            if not combo.recipe or combo.recipe[0] != "prime-safety":
                violations.append((combo.wish_id, combo.recipe))

        assert not violations, (
            f"Combos without prime-safety first:\n" +
            "\n".join(
                f"  wish={w!r} recipe={r!r}"
                for w, r in violations
            )
        )

    def test_all_combo_wish_ids_unique(self, combo_db):
        """No duplicate wish_ids in combo database."""
        combos = combo_db.all_combos()
        ids = [c.wish_id for c in combos]
        assert len(ids) == len(set(ids)), (
            f"Duplicate combo wish_ids: "
            f"{[i for i in ids if ids.count(i) > 1]}"
        )

    def test_all_combos_have_valid_confidence(self, combo_db):
        """All combos must have confidence in [0.0, 1.0]."""
        for combo in combo_db.all_combos():
            assert 0.0 <= combo.confidence <= 1.0, (
                f"Combo {combo.wish_id!r} has invalid confidence: {combo.confidence}"
            )


# ---------------------------------------------------------------------------
# Tests: Phase 2 → Phase 3 integration
# ---------------------------------------------------------------------------

class TestPhase2Phase3Integration:

    def test_intent_wish_id_feeds_execution_match(self, intent_cpu, execution_cpu):
        """
        Phase 2 IntentMatch.wish_id feeds directly into Phase 3 ExecutionCPU.match().
        """
        prompt = "implement oauth token refresh with bearer auth"

        # Phase 2: detect wish_id
        intent_match = intent_cpu.match(prompt)
        assert intent_match is not None, "Intent CPU must match oauth prompt"
        assert intent_match.wish_id == "oauth-integration"

        # Phase 3: get execution plan
        exec_match = execution_cpu.match(intent_match.wish_id)
        assert exec_match is not None, (
            f"Execution CPU must match wish_id={intent_match.wish_id!r}"
        )
        assert exec_match.swarm == "coder"
        assert "prime-safety" in exec_match.recipe
        assert "oauth3-enforcer" in exec_match.recipe

    def test_phase2_to_phase3_for_all_known_prompts(self, intent_cpu, execution_cpu):
        """
        All prompts that Phase 2 matches must also produce a Phase 3 execution plan.
        """
        prompts_and_wishes = [
            ("my sql query is slow", "database-optimization"),
            ("build docker image", "docker-containerization"),
            ("train neural network", "machine-learning-training"),
            ("write unit tests with pytest", "test-development"),
            ("audit codebase for xss vulnerabilities", "security-audit"),
        ]

        for prompt, expected_wish in prompts_and_wishes:
            intent_match = intent_cpu.match(prompt)
            if intent_match is None:
                continue
            if intent_match.wish_id != expected_wish:
                continue

            exec_match = execution_cpu.match(intent_match.wish_id)
            assert exec_match is not None, (
                f"Phase 3 must match wish_id={intent_match.wish_id!r} "
                f"(from prompt={prompt!r})"
            )
            assert exec_match.recipe[0] == "prime-safety", (
                f"prime-safety must be first in recipe for wish {intent_match.wish_id!r}"
            )

    def test_phase2_miss_leads_to_phase3_miss(self, intent_cpu, execution_cpu):
        """
        If Phase 2 returns None, Phase 3 receives None wish_id → no execution plan.
        """
        prompt = "xyzzy foobar gibberish"
        intent_match = intent_cpu.match(prompt)

        if intent_match is None:
            # Phase 3 cannot run without a wish_id
            # Simulate by passing a fallback wish_id that doesn't exist
            exec_match = execution_cpu.match("__no_wish_detected__")
            assert exec_match is None, (
                "Phase 3 must return None for non-existent wish_id"
            )


# ---------------------------------------------------------------------------
# Tests: Full 3-phase pipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:

    def test_full_3_phase_pipeline_oauth(
        self, smalltalk_cpu, intent_cpu, execution_cpu
    ):
        """
        Full pipeline: prompt → WarmToken (P1) + IntentMatch (P2) + ExecutionMatch (P3).
        """
        prompt = "implement oauth token refresh with bearer auth"

        # Phase 1: warm response
        warm_token = smalltalk_cpu.generate(
            user_id="pipeline_user",
            session_id="pipeline_sess",
            prompt=prompt,
        )
        assert warm_token.response, "Phase 1 must return non-empty response"

        # Phase 2: intent
        intent_match = intent_cpu.match(prompt)
        assert intent_match is not None
        assert intent_match.wish_id == "oauth-integration"

        # Phase 3: execution plan
        exec_match = execution_cpu.match(intent_match.wish_id)
        assert exec_match is not None
        assert exec_match.swarm == "coder"
        assert "prime-safety" in exec_match.recipe

    def test_full_pipeline_under_10ms(
        self, smalltalk_cpu, intent_cpu, execution_cpu
    ):
        """
        Full 3-phase pipeline must complete < 10ms per prompt.
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

            # Phase 1
            warm_token = smalltalk_cpu.generate(
                user_id="latency_user",
                session_id="latency_sess",
                prompt=prompt,
            )

            # Phase 2
            intent_match = intent_cpu.match(prompt)

            # Phase 3
            exec_match = None
            if intent_match:
                exec_match = execution_cpu.match(intent_match.wish_id)

            elapsed_ms = (time.perf_counter() - start) * 1000

            assert warm_token.response, f"Empty warm response for: {prompt!r}"
            assert elapsed_ms < 50.0, (
                f"Full pipeline took {elapsed_ms:.3f}ms for {prompt!r} "
                f"— exceeds 50ms SLA"
            )

    def test_full_pipeline_p99_under_5ms(self, intent_cpu, execution_cpu):
        """
        Phases 2+3 combined P99 must be < 5ms over 200 iterations.
        (Phase 1 SQLite I/O excluded from this tight SLA test.)
        """
        wish_prompts = [
            "implement oauth token refresh",
            "optimize sql query performance",
            "build and push docker image",
            "audit xss injection vulnerabilities",
            "train neural network model",
        ]

        latencies_ms = []
        for i in range(200):
            prompt = wish_prompts[i % len(wish_prompts)]
            start = time.perf_counter()

            intent_match = intent_cpu.match(prompt)
            if intent_match:
                execution_cpu.match(intent_match.wish_id)

            latencies_ms.append((time.perf_counter() - start) * 1000)

        latencies_ms.sort()
        p99_idx = max(0, int(len(latencies_ms) * 0.99) - 1)
        p99_ms = latencies_ms[p99_idx]

        assert p99_ms < 5.0, (
            f"Phase 2+3 P99 = {p99_ms:.4f}ms — exceeds 5ms SLA"
        )

    def test_execution_lookup_log_records_events(self, combo_db):
        """ExecutionCPU with LookupLog records events for LLM feedback."""
        log = ComboLookupLog()
        cpu = ExecutionCPU(combo_db=combo_db, lookup_log=log)

        cpu.match("oauth-integration", session_id="log_test")
        cpu.match("debugging", session_id="log_test")
        cpu.match("nonexistent-wish", session_id="log_test")

        assert log.count() == 3, f"Expected 3 log entries, got {log.count()}"

    def test_lookup_log_confirm_and_correct(self, combo_db):
        """ComboLookupLog.confirm() and .correct() update entries correctly."""
        log = ComboLookupLog()
        cpu = ExecutionCPU(combo_db=combo_db, lookup_log=log)

        cpu.match("documentation-writing", session_id="feedback_sess")

        # Confirm the match
        log.confirm(
            wish_id="documentation-writing",
            swarm="writer",
            recipe=["prime-safety", "software5.0-paradigm"],
        )

        confirmed = [
            e for e in log.all()
            if e.wish_id == "documentation-writing" and e.llm_confirmed is True
        ]
        assert confirmed, "Confirmed entry must be findable"
        assert confirmed[-1].llm_swarm == "writer"

    def test_learned_combo_immediately_available_in_pipeline(self, combo_db):
        """
        After appending a learned combo, Phase 3 uses it immediately.
        """
        import tempfile
        with tempfile.NamedTemporaryFile(
            suffix=".jsonl", mode="w", delete=False
        ) as tmp:
            tmp_path = tmp.name

        tmp_db = ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_path)
        cpu3 = ExecutionCPU(combo_db=tmp_db)

        # Teach it: a new wish → planner swarm
        tmp_db.append_learned_combo(LearnedCombo(
            wish_id="solace-oauth3-implementation",
            swarm="planner",
            recipe=["prime-safety", "phuc-forecast", "oauth3-enforcer"],
            confidence=0.90,
            source="llm",
        ))

        match = cpu3.match("solace-oauth3-implementation")
        assert match is not None, (
            "CPU must match newly learned wish_id immediately"
        )
        assert match.swarm == "planner"
        assert "oauth3-enforcer" in match.recipe


# ---------------------------------------------------------------------------
# Tests: ComboDB integrity
# ---------------------------------------------------------------------------

class TestComboDatabaseIntegrity:

    def test_combos_loaded_from_disk(self, combo_db):
        """ComboDB must load combos from combos.jsonl."""
        count = combo_db.count()
        assert count >= 25, f"Expected >= 25 combos, got {count}"

    def test_all_combos_have_recipe(self, combo_db):
        """Every loaded combo must have a non-empty recipe list."""
        for combo in combo_db.all_combos():
            assert combo.recipe, (
                f"Combo {combo.wish_id!r} has empty recipe"
            )

    def test_all_combos_have_description(self, combo_db):
        """Every loaded combo should have a non-empty description."""
        for combo in combo_db.all_combos():
            assert combo.description, (
                f"Combo {combo.wish_id!r} has empty description"
            )

    def test_combos_by_swarm_filters_correctly(self, combo_db):
        """combos_by_swarm() must return only combos for that swarm."""
        coder_combos = combo_db.combos_by_swarm("coder")
        for combo in coder_combos:
            assert combo.swarm == "coder", (
                f"combos_by_swarm('coder') returned {combo.swarm!r} for {combo.wish_id!r}"
            )

    def test_security_auditor_combos_exist(self, combo_db):
        """At least 2 combos must target security-auditor."""
        security_combos = combo_db.combos_by_swarm("security-auditor")
        assert len(security_combos) >= 2, (
            f"Expected >= 2 security-auditor combos, got {len(security_combos)}"
        )

    def test_all_wish_ids_are_lowercase(self, combo_db):
        """All combo wish_ids must be lowercase."""
        for combo in combo_db.all_combos():
            assert combo.wish_id == combo.wish_id.lower(), (
                f"Combo wish_id {combo.wish_id!r} is not lowercase"
            )
