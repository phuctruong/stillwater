"""
Test: Learned wishes persistence — survive across sessions.

Verifies:
- append_learned_wish() writes to learned_wishes.jsonl
- On reload(), new keywords are merged into the wish
- Merged keywords appear in CPU match results
- Duplicate keywords are not duplicated in the wish
- Malformed entries in learned_wishes.jsonl are silently skipped
- Multiple learned entries for the same wish are all applied
- Non-existent wish_id in learned entry is silently dropped

rung_target: 641
EXIT_PASS: All persistence assertions pass with real filesystem writes.
EXIT_BLOCKED: Learned keywords not found in DB after reload OR duplicate keywords.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.intent.cpu import IntentCPU
from admin.orchestration.intent.database import WishDB
from admin.orchestration.intent.models import LearnedWish


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_WISHES_PATH = str(Path(__file__).parent.parent / "wishes.jsonl")


@pytest.fixture
def tmp_learned(tmp_path):
    """Fresh temporary learned_wishes.jsonl path for each test."""
    return str(tmp_path / "learned_wishes.jsonl")


@pytest.fixture
def fresh_db(tmp_learned):
    return WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_learned)


# ---------------------------------------------------------------------------
# Tests: Persistence
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_append_learned_wish_writes_file(self, fresh_db, tmp_learned):
        """append_learned_wish() must create and write to learned_wishes.jsonl."""
        entry = LearnedWish(
            wish_id="oauth-integration",
            keywords=["jwt", "jsonwebtoken"],
            skill_pack_hint="coder+security",
            confidence=0.75,
            source="llm",
        )
        fresh_db.append_learned_wish(entry)

        learned_path = Path(tmp_learned)
        assert learned_path.exists(), "learned_wishes.jsonl must be created"
        content = learned_path.read_text(encoding="utf-8").strip()
        assert content, "learned_wishes.jsonl must not be empty"

        # Verify it's valid JSON
        parsed = json.loads(content.split("\n")[0])
        assert parsed["wish_id"] == "oauth-integration"
        assert "jwt" in parsed["keywords"]

    def test_learned_keywords_appear_in_live_db(self, fresh_db):
        """After append_learned_wish(), new keywords are immediately searchable."""
        entry = LearnedWish(
            wish_id="oauth-integration",
            keywords=["jwt", "jsonwebtoken"],
            confidence=0.75,
            source="llm",
        )
        fresh_db.append_learned_wish(entry)

        # Immediately check live DB
        wishes = fresh_db.lookup_by_keyword("jwt")
        wish_ids = [w.id for w in wishes]
        assert "oauth-integration" in wish_ids, (
            "jwt keyword must map to oauth-integration in live DB"
        )

    def test_learned_keywords_survive_reload(self, tmp_learned):
        """
        After writing to learned_wishes.jsonl and reloading,
        the new keywords are still present.
        """
        # Write a learned entry
        db1 = WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_learned)
        entry = LearnedWish(
            wish_id="docker-containerization",
            keywords=["podman", "containerd"],
            confidence=0.70,
            source="llm",
        )
        db1.append_learned_wish(entry)

        # Create a fresh DB instance (simulating new session)
        db2 = WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_learned)

        # New keywords must be present
        wishes = db2.lookup_by_keyword("podman")
        wish_ids = [w.id for w in wishes]
        assert "docker-containerization" in wish_ids, (
            "Learned keyword 'podman' must survive across sessions"
        )

    def test_duplicate_keywords_not_added_twice(self, fresh_db):
        """
        Appending a keyword that already exists in the wish must not duplicate it.
        """
        # "oauth" is already in oauth-integration keywords
        entry = LearnedWish(
            wish_id="oauth-integration",
            keywords=["oauth", "token"],  # both already exist
            confidence=0.75,
            source="llm",
        )
        fresh_db.append_learned_wish(entry)

        wish = fresh_db.get("oauth-integration")
        assert wish is not None
        oauth_count = wish.keywords.count("oauth")
        assert oauth_count == 1, (
            f"'oauth' appears {oauth_count} times — duplicates must be prevented"
        )

    def test_malformed_jsonl_lines_skipped(self, tmp_learned):
        """Malformed lines in learned_wishes.jsonl must be silently skipped."""
        # Manually write malformed content to learned file
        with open(tmp_learned, "w", encoding="utf-8") as fh:
            fh.write("not valid json at all\n")
            fh.write("{missing_quotes: true}\n")
            # Valid entry
            fh.write(json.dumps({
                "wish_id": "oauth-integration",
                "keywords": ["jwtauth"],
                "confidence": 0.7,
                "source": "llm",
                "timestamp": "2026-02-22T00:00:00",
                "session_id": "",
                "skill_pack_hint": "",
            }) + "\n")

        db = WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_learned)
        # Should load without exception
        wishes = db.lookup_by_keyword("jwtauth")
        wish_ids = [w.id for w in wishes]
        assert "oauth-integration" in wish_ids, (
            "Valid entry after malformed lines must still be loaded"
        )

    def test_multiple_learned_entries_same_wish_all_applied(self, tmp_learned):
        """Multiple learned entries for the same wish should all add their keywords."""
        db = WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_learned)

        db.append_learned_wish(LearnedWish(
            wish_id="database-optimization",
            keywords=["aurora", "cockroachdb"],
            confidence=0.7,
            source="llm",
        ))
        db.append_learned_wish(LearnedWish(
            wish_id="database-optimization",
            keywords=["tidb", "planetscale"],
            confidence=0.65,
            source="llm",
        ))

        wish = db.get("database-optimization")
        assert wish is not None
        assert "aurora" in wish.keywords, "'aurora' must be in db keywords"
        assert "tidb" in wish.keywords, "'tidb' must be in db keywords"

    def test_unknown_wish_id_silently_dropped(self, fresh_db):
        """
        An entry with a wish_id that doesn't exist must not crash or corrupt DB.
        """
        entry = LearnedWish(
            wish_id="nonexistent-wish-xyz",
            keywords=["someword"],
            confidence=0.5,
            source="llm",
        )
        try:
            fresh_db.append_learned_wish(entry)
        except Exception as exc:
            pytest.fail(f"append_learned_wish raised on unknown wish_id: {exc}")

        # Verify DB is not corrupted
        assert fresh_db.count() > 0, "DB should still have canonical wishes"

    def test_cpu_matches_learned_keywords_after_merge(self, tmp_learned):
        """
        After learning a new keyword, the CPU should match using it.
        """
        db = WishDB(wishes_path=_WISHES_PATH, learned_path=tmp_learned)
        cpu = IntentCPU(wish_db=db)

        # Verify the word "paseto" doesn't match anything initially
        before_match = cpu.match("implement paseto token authentication")
        # (may or may not match — depends on keyword overlap)

        # Teach it: "paseto" maps to oauth-integration
        db.append_learned_wish(LearnedWish(
            wish_id="oauth-integration",
            keywords=["paseto"],
            confidence=0.8,
            source="llm",
        ))

        # Now it must match
        after_match = cpu.match("implement paseto token authentication")
        assert after_match is not None, (
            "CPU must match 'paseto' after it was learned"
        )
        assert after_match.wish_id == "oauth-integration", (
            f"Expected oauth-integration, got {after_match.wish_id}"
        )
