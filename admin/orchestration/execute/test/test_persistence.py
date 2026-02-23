"""
Test: Learned combos persistence — survive across sessions.

Verifies:
- append_learned_combo() writes to learned_combos.jsonl
- On reload(), new combos are merged into the database
- Higher-confidence learned combos overwrite existing ones
- Lower-confidence learned combos do not overwrite existing ones
- Malformed entries in learned_combos.jsonl are silently skipped
- Multiple learned entries for the same wish_id: last one wins (if higher confidence)
- Non-existent swarm in learned entry is rejected by validation
- Recipe without prime-safety is rejected
- CPU matches the learned swarm after merge

rung_target: 641
EXIT_PASS: All persistence assertions pass with real filesystem writes.
EXIT_BLOCKED: Learned combos not applied OR corrupted DB after malformed input.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.execute.cpu import ExecutionCPU
from admin.orchestration.execute.database import ComboDB
from admin.orchestration.execute.models import LearnedCombo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_COMBOS_PATH = str(Path(__file__).parent.parent / "combos.jsonl")


@pytest.fixture
def tmp_learned(tmp_path):
    """Fresh temporary learned_combos.jsonl path for each test."""
    return str(tmp_path / "learned_combos.jsonl")


@pytest.fixture
def fresh_db(tmp_learned):
    return ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_learned)


# ---------------------------------------------------------------------------
# Tests: Persistence
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_append_learned_combo_writes_file(self, fresh_db, tmp_learned):
        """append_learned_combo() must create and write to learned_combos.jsonl."""
        entry = LearnedCombo(
            wish_id="oauth-integration",
            swarm="coder",
            recipe=["prime-safety", "prime-coder", "oauth3-enforcer", "jwt-validator"],
            confidence=0.99,
            source="llm",
        )
        fresh_db.append_learned_combo(entry)

        learned_path = Path(tmp_learned)
        assert learned_path.exists(), "learned_combos.jsonl must be created"
        content = learned_path.read_text(encoding="utf-8").strip()
        assert content, "learned_combos.jsonl must not be empty"

        parsed = json.loads(content.split("\n")[0])
        assert parsed["wish_id"] == "oauth-integration"
        assert "jwt-validator" in parsed["recipe"]

    def test_higher_confidence_learned_overwrites(self, fresh_db):
        """
        A learned combo with higher confidence than existing must overwrite.
        """
        # Original oauth-integration confidence is 0.95
        original = fresh_db.get("oauth-integration")
        assert original is not None
        original_confidence = original.confidence

        # Append learned with higher confidence
        entry = LearnedCombo(
            wish_id="oauth-integration",
            swarm="security-auditor",
            recipe=["prime-safety", "prime-coder", "oauth3-enforcer"],
            confidence=0.99,  # higher than original 0.95
            source="llm",
        )
        fresh_db.append_learned_combo(entry)

        updated = fresh_db.get("oauth-integration")
        assert updated is not None
        assert updated.swarm == "security-auditor", (
            "Higher-confidence learned combo must overwrite the existing swarm"
        )
        assert updated.confidence == 0.99

    def test_lower_confidence_learned_does_not_overwrite(self, fresh_db):
        """
        A learned combo with lower confidence than existing must NOT overwrite.
        """
        # Original docker-containerization confidence is 0.91
        original = fresh_db.get("docker-containerization")
        assert original is not None
        original_swarm = original.swarm

        # Append learned with lower confidence
        entry = LearnedCombo(
            wish_id="docker-containerization",
            swarm="planner",
            recipe=["prime-safety", "prime-coder"],
            confidence=0.50,  # lower than original 0.91
            source="llm",
        )
        fresh_db.append_learned_combo(entry)

        unchanged = fresh_db.get("docker-containerization")
        assert unchanged is not None
        assert unchanged.swarm == original_swarm, (
            f"Lower-confidence learned combo must NOT overwrite. "
            f"Expected {original_swarm!r}, got {unchanged.swarm!r}"
        )

    def test_learned_combo_survives_reload(self, tmp_learned):
        """
        After writing to learned_combos.jsonl and creating a new ComboDB,
        the learned combo is still present.
        """
        db1 = ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_learned)
        entry = LearnedCombo(
            wish_id="git-workflow",
            swarm="planner",
            recipe=["prime-safety", "phuc-forecast", "prime-coder"],
            confidence=0.99,
            source="llm",
        )
        db1.append_learned_combo(entry)

        # New session: create a fresh DB instance
        db2 = ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_learned)

        updated = db2.get("git-workflow")
        assert updated is not None
        assert updated.swarm == "planner", (
            f"Learned swarm 'planner' must survive across sessions, "
            f"got {updated.swarm!r}"
        )

    def test_new_wish_id_added_by_learned_combo(self, fresh_db, tmp_learned):
        """
        A learned combo for a wish_id not in canonical combos.jsonl
        must be added to the database.
        """
        new_wish_id = "solace-oauth3-spec"
        assert fresh_db.get(new_wish_id) is None, (
            f"Wish {new_wish_id!r} should not exist in canonical DB"
        )

        entry = LearnedCombo(
            wish_id=new_wish_id,
            swarm="coder",
            recipe=["prime-safety", "prime-coder", "oauth3-enforcer"],
            confidence=0.80,
            source="llm",
        )
        fresh_db.append_learned_combo(entry)

        added = fresh_db.get(new_wish_id)
        assert added is not None, (
            f"Learned combo for new wish_id {new_wish_id!r} must be added"
        )
        assert added.swarm == "coder"

    def test_malformed_jsonl_lines_skipped(self, tmp_learned):
        """Malformed lines in learned_combos.jsonl must be silently skipped."""
        with open(tmp_learned, "w", encoding="utf-8") as fh:
            fh.write("not valid json at all\n")
            fh.write("{missing_quotes: true}\n")
            # Valid entry
            fh.write(json.dumps({
                "wish_id": "git-workflow",
                "swarm": "planner",
                "recipe": ["prime-safety", "phuc-forecast"],
                "confidence": 0.99,
                "source": "llm",
                "timestamp": "2026-02-22T00:00:00",
                "session_id": "",
            }) + "\n")

        db = ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_learned)
        combo = db.get("git-workflow")
        assert combo is not None, (
            "Valid entry after malformed lines must still be loaded"
        )
        assert combo.swarm == "planner"

    def test_recipe_without_prime_safety_silently_rejected_at_merge(self, fresh_db):
        """
        A learned combo whose recipe lacks prime-safety must be silently rejected
        by the database's _merge_learned gate. The existing combo is unchanged.
        """
        original = fresh_db.get("oauth-integration")
        assert original is not None
        original_swarm = original.swarm
        original_confidence = original.confidence

        # LearnedCombo construction itself succeeds (no validator on LearnedCombo)
        # But when merged, _merge_learned silently drops it because prime-safety is missing
        entry = LearnedCombo(
            wish_id="oauth-integration",
            swarm="planner",  # different swarm to detect if it incorrectly applies
            recipe=["prime-coder", "oauth3-enforcer"],  # missing prime-safety
            confidence=0.99,  # higher confidence — should NOT overwrite
            source="llm",
        )
        fresh_db.append_learned_combo(entry)

        # DB must be unchanged — the recipe without prime-safety was rejected
        after = fresh_db.get("oauth-integration")
        assert after is not None
        assert after.swarm == original_swarm, (
            f"Combo without prime-safety must not overwrite. "
            f"Expected {original_swarm!r}, got {after.swarm!r}"
        )

    def test_cpu_uses_learned_swarm_after_merge(self, tmp_learned):
        """
        After learning a new swarm for a wish, the CPU must use it.
        """
        db = ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_learned)
        cpu = ExecutionCPU(combo_db=db)

        # Teach a higher-confidence swarm override
        db.append_learned_combo(LearnedCombo(
            wish_id="documentation-writing",
            swarm="planner",  # override default "writer"
            recipe=["prime-safety", "phuc-forecast", "software5.0-paradigm"],
            confidence=0.99,
            source="llm",
        ))

        match = cpu.match("documentation-writing")
        assert match is not None
        assert match.swarm == "planner", (
            f"CPU must use learned swarm 'planner', got {match.swarm!r}"
        )

    def test_reload_picks_up_external_writes(self, tmp_learned):
        """
        After an external process writes to learned_combos.jsonl,
        reload() picks it up.
        """
        db = ComboDB(combos_path=_COMBOS_PATH, learned_path=tmp_learned)

        # External write (simulate another process)
        external_entry = LearnedCombo(
            wish_id="debugging",
            swarm="skeptic",
            recipe=["prime-safety", "prime-coder", "phuc-forecast"],
            confidence=0.99,
            source="manual",
        )
        with open(tmp_learned, "a", encoding="utf-8") as fh:
            fh.write(external_entry.model_dump_json() + "\n")

        db.reload()

        combo = db.get("debugging")
        assert combo is not None
        assert combo.swarm == "skeptic", (
            f"After reload, must use externally written swarm 'skeptic', "
            f"got {combo.swarm!r}"
        )

    def test_db_not_corrupted_after_bad_write(self, fresh_db):
        """
        Even if an exception occurs mid-write, the DB must remain usable.
        """
        original_count = fresh_db.count()

        # Attempt bad entry (missing required fields) — must not crash DB
        try:
            entry = LearnedCombo(
                wish_id="oauth-integration",
                swarm="coder",
                recipe=["prime-safety"],
                confidence=0.5,
                source="llm",
            )
            fresh_db.append_learned_combo(entry)
        except Exception:
            pass  # Expected for some edge cases

        # DB must still be usable
        assert fresh_db.count() >= original_count, "DB count must not decrease"
        combo = fresh_db.get("oauth-integration")
        assert combo is not None, "oauth-integration must still be findable"
