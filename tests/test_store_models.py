"""
tests/test_store_models.py — Unit tests for store/models.py Pydantic models.

PERSONA-BASED QA: Naval Ravikant (investor/philosopher)
"The model contract IS the product. Every validator is leverage — one line of
 code prevents a class of bugs forever. Don't test what you wish were true;
 test what the contract actually guarantees."

Covers:
  - SkillStatus enum values
  - ContentType enum values (all 6)
  - APIKey creation, required fields, defaults
  - SkillSubmission valid/invalid creation, rung gate, kebab-case gate
  - ReviewRecord creation and defaults
  - SkillListing creation
  - InstallRequest defaults
  - InstallResult creation
  - PaginatedSkillList creation
  - Model serialization round-trip

Rung target: 641 (local correctness, pure unit tests, no I/O)
Network: OFF — no HTTP calls, no external services
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import List

import pytest
from pydantic import ValidationError

# Ensure store package is importable from project root
sys.path.insert(0, "/home/phuc/projects/stillwater")

from store.models import (
    APIKey,
    ContentType,
    InstallRequest,
    InstallResult,
    PaginatedSkillList,
    ReviewRecord,
    SkillListing,
    SkillStatus,
    SkillSubmission,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _valid_submission(**overrides) -> SkillSubmission:
    """Factory for a minimal valid SkillSubmission."""
    defaults = dict(
        skill_name="prime-coder",
        skill_content="# prime-coder skill content here",
        author="phuc",
        rung_claimed=641,
    )
    defaults.update(overrides)
    return SkillSubmission(**defaults)


def _valid_api_key(**overrides) -> APIKey:
    """Factory for a minimal valid APIKey."""
    defaults = dict(
        key_id="acct_deadbeef",
        key_hash="hmac_sha256_placeholder_not_real",
        name="phuc-dev",
        created_at=_now(),
    )
    defaults.update(overrides)
    return APIKey(**defaults)


def _valid_review_record(**overrides) -> ReviewRecord:
    """Factory for a minimal valid ReviewRecord."""
    defaults = dict(
        skill_id="550e8400-e29b-41d4-a716-446655440000",
        skill_name="prime-coder",
        content_type=ContentType.skill,
        author="phuc",
        key_id="acct_deadbeef",
        rung_claimed=641,
        skill_content="# prime-coder content for review",
        submitted_at=_now(),
    )
    defaults.update(overrides)
    return ReviewRecord(**defaults)


# ===========================================================================
# SkillStatus enum
# ===========================================================================
# Naval: "Enums are contracts written in code. Each value is a promise that
#  downstream consumers can rely on. If a value is missing or misspelled, the
#  system silently breaks — and you pay the debugging tax forever."


class TestSkillStatusEnum:
    """SkillStatus — three states, no more, no less."""

    def test_pending_value(self):
        """SkillStatus.pending must have string value 'pending'."""
        assert SkillStatus.pending == "pending"
        assert SkillStatus.pending.value == "pending"

    def test_accepted_value(self):
        """SkillStatus.accepted must have string value 'accepted'."""
        assert SkillStatus.accepted == "accepted"
        assert SkillStatus.accepted.value == "accepted"

    def test_rejected_value(self):
        """SkillStatus.rejected must have string value 'rejected'."""
        assert SkillStatus.rejected == "rejected"
        assert SkillStatus.rejected.value == "rejected"

    def test_exactly_three_members(self):
        """SkillStatus must have exactly 3 members — no accidental extras."""
        assert len(SkillStatus) == 3

    def test_is_str_enum(self):
        """SkillStatus members must behave as strings (str subclass)."""
        assert isinstance(SkillStatus.pending, str)
        assert isinstance(SkillStatus.accepted, str)
        assert isinstance(SkillStatus.rejected, str)


# ===========================================================================
# ContentType enum
# ===========================================================================
# Naval: "The taxonomy of what you accept is a strategic decision. Six content
#  types means six leverage points. Each one governed by a single enum value
#  forces consistency across the entire API surface."


class TestContentTypeEnum:
    """ContentType — six accepted content types, kebab-case values where applicable."""

    def test_skill_value(self):
        """ContentType.skill must have value 'skill'."""
        assert ContentType.skill == "skill"
        assert ContentType.skill.value == "skill"

    def test_recipe_value(self):
        """ContentType.recipe must have value 'recipe'."""
        assert ContentType.recipe == "recipe"
        assert ContentType.recipe.value == "recipe"

    def test_swarm_value(self):
        """ContentType.swarm must have value 'swarm'."""
        assert ContentType.swarm == "swarm"
        assert ContentType.swarm.value == "swarm"

    def test_prime_wiki_value(self):
        """ContentType.prime_wiki must have kebab-case value 'prime-wiki'."""
        assert ContentType.prime_wiki == "prime-wiki"
        assert ContentType.prime_wiki.value == "prime-wiki"

    def test_prime_mermaid_value(self):
        """ContentType.prime_mermaid must have kebab-case value 'prime-mermaid'."""
        assert ContentType.prime_mermaid == "prime-mermaid"
        assert ContentType.prime_mermaid.value == "prime-mermaid"

    def test_bugfix_value(self):
        """ContentType.bugfix must have value 'bugfix'."""
        assert ContentType.bugfix == "bugfix"
        assert ContentType.bugfix.value == "bugfix"

    def test_exactly_six_members(self):
        """ContentType must have exactly 6 members."""
        assert len(ContentType) == 6

    def test_is_str_enum(self):
        """ContentType members must behave as strings."""
        for member in ContentType:
            assert isinstance(member, str), f"{member!r} is not a str"


# ===========================================================================
# APIKey model
# ===========================================================================
# Naval: "Trust is a function of track record. reputation=0.0 is honest
#  about a new account: you haven't earned it yet. The default speaks the
#  truth before a single action has been taken."


class TestAPIKeyCreation:
    """APIKey — creation with required fields and enforcement of defaults."""

    def test_create_with_required_fields(self):
        """APIKey must be constructable with only key_id, key_hash, name, created_at."""
        key = _valid_api_key()
        assert key.key_id == "acct_deadbeef"
        assert key.key_hash == "hmac_sha256_placeholder_not_real"
        assert key.name == "phuc-dev"
        assert isinstance(key.created_at, datetime)

    def test_default_account_type_is_human(self):
        """account_type must default to 'human'."""
        key = _valid_api_key()
        assert key.account_type == "human"

    def test_default_description_is_empty_string(self):
        """description must default to empty string, not None."""
        key = _valid_api_key()
        assert key.description == ""
        assert key.description is not None  # null != empty string

    def test_default_reputation_is_zero_float(self):
        """reputation must default to 0.0 (float, not int, not None)."""
        key = _valid_api_key()
        assert key.reputation == 0.0
        assert isinstance(key.reputation, float)

    def test_default_submission_count_is_zero(self):
        """submission_count must default to 0."""
        key = _valid_api_key()
        assert key.submission_count == 0

    def test_default_accepted_count_is_zero(self):
        """accepted_count must default to 0."""
        key = _valid_api_key()
        assert key.accepted_count == 0

    def test_default_rejected_count_is_zero(self):
        """rejected_count must default to 0."""
        key = _valid_api_key()
        assert key.rejected_count == 0

    def test_default_status_is_active(self):
        """status must default to 'active', not None."""
        key = _valid_api_key()
        assert key.status == "active"

    def test_default_recent_submission_timestamps_is_empty_list(self):
        """recent_submission_timestamps must default to [] (not None, not shared mutable)."""
        key1 = _valid_api_key()
        key2 = _valid_api_key()
        assert key1.recent_submission_timestamps == []
        assert key2.recent_submission_timestamps == []
        # Mutable default isolation: modifying one must not affect the other
        key1.recent_submission_timestamps.append("2026-01-01T00:00:00Z")
        assert key2.recent_submission_timestamps == [], (
            "Default list must be isolated — shared mutable default detected"
        )

    def test_override_account_type_bot(self):
        """account_type can be set to 'bot'."""
        key = _valid_api_key(account_type="bot")
        assert key.account_type == "bot"

    def test_override_reputation(self):
        """reputation can be set to a positive float."""
        key = _valid_api_key(reputation=3.5)
        assert key.reputation == 3.5


# ===========================================================================
# SkillSubmission valid creation
# ===========================================================================
# Naval: "A validator is the cheapest form of quality control. Every invalid
#  state that cannot be constructed is a bug that can never exist in
#  production. The constraint IS the value."


class TestSkillSubmissionValid:
    """SkillSubmission — valid creation and field contracts."""

    def test_create_minimal_valid(self):
        """SkillSubmission must be constructable with four required fields."""
        sub = _valid_submission()
        assert sub.skill_name == "prime-coder"
        assert sub.skill_content == "# prime-coder skill content here"
        assert sub.author == "phuc"
        assert sub.rung_claimed == 641

    def test_default_content_type_is_skill(self):
        """content_type must default to ContentType.skill."""
        sub = _valid_submission()
        assert sub.content_type == ContentType.skill

    def test_default_description_is_empty_string(self):
        """description must default to empty string."""
        sub = _valid_submission()
        assert sub.description == ""

    def test_default_tags_is_empty_list(self):
        """tags must default to []."""
        sub = _valid_submission()
        assert sub.tags == []

    def test_default_source_context_is_empty_string(self):
        """source_context must default to empty string."""
        sub = _valid_submission()
        assert sub.source_context == ""

    def test_override_content_type_recipe(self):
        """content_type can be explicitly set to ContentType.recipe."""
        sub = _valid_submission(content_type=ContentType.recipe)
        assert sub.content_type == ContentType.recipe

    def test_override_content_type_bugfix(self):
        """content_type can be explicitly set to ContentType.bugfix."""
        sub = _valid_submission(content_type=ContentType.bugfix)
        assert sub.content_type == ContentType.bugfix

    def test_tags_list_is_stored(self):
        """tags list is stored as provided."""
        sub = _valid_submission(tags=["ai", "coder", "prime"])
        assert sub.tags == ["ai", "coder", "prime"]


# ===========================================================================
# SkillSubmission rung_must_be_valid validator
# ===========================================================================
# Naval: "641, 274177, 65537 — these aren't arbitrary numbers. They are the
#  rungs of a verification ladder. Any other number is not a mistake; it is a
#  lie about the quality of the work."


class TestSkillSubmissionRungValidator:
    """rung_must_be_valid — gate on the three valid rung values."""

    def test_rung_641_accepted(self):
        """rung_claimed=641 (local correctness rung) must be accepted."""
        sub = _valid_submission(rung_claimed=641)
        assert sub.rung_claimed == 641

    def test_rung_274177_accepted(self):
        """rung_claimed=274177 (irreversible / 3-seed consensus rung) must be accepted."""
        sub = _valid_submission(rung_claimed=274177)
        assert sub.rung_claimed == 274177

    def test_rung_65537_accepted(self):
        """rung_claimed=65537 (production/security rung) must be accepted."""
        sub = _valid_submission(rung_claimed=65537)
        assert sub.rung_claimed == 65537

    def test_rung_zero_rejected(self):
        """rung_claimed=0 must raise ValidationError (not a valid rung)."""
        with pytest.raises(ValidationError):
            _valid_submission(rung_claimed=0)

    def test_rung_one_rejected(self):
        """rung_claimed=1 must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(rung_claimed=1)

    def test_rung_999_rejected(self):
        """rung_claimed=999 must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(rung_claimed=999)

    def test_rung_negative_rejected(self):
        """rung_claimed=-1 must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(rung_claimed=-1)

    def test_rung_274176_off_by_one_rejected(self):
        """rung_claimed=274176 (off-by-one from valid rung) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(rung_claimed=274176)


# ===========================================================================
# SkillSubmission name_must_be_kebab validator
# ===========================================================================
# Naval: "Naming is a public API. kebab-case is the law of the store. One
#  unconventional name pollutes every consumer that depends on predictable
#  filesystem paths and URL segments."


class TestSkillSubmissionKebabValidator:
    """name_must_be_kebab — gate on lowercase kebab-case skill names."""

    def test_kebab_prime_coder_accepted(self):
        """'prime-coder' is valid kebab-case and must be accepted."""
        sub = _valid_submission(skill_name="prime-coder")
        assert sub.skill_name == "prime-coder"

    def test_kebab_my_skill_v2_accepted(self):
        """'my-skill-v2' is valid kebab-case and must be accepted."""
        sub = _valid_submission(skill_name="my-skill-v2")
        assert sub.skill_name == "my-skill-v2"

    def test_kebab_simple_word_accepted(self):
        """'forecaster' (single word, no hyphens) must be accepted."""
        sub = _valid_submission(skill_name="forecaster")
        assert sub.skill_name == "forecaster"

    def test_kebab_alphanumeric_accepted(self):
        """'skill123' (alphanumeric, no hyphens) must be accepted."""
        sub = _valid_submission(skill_name="skill123")
        assert sub.skill_name == "skill123"

    def test_uppercase_rejected(self):
        """'UPPERCASE' must raise ValidationError (not kebab-case)."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="UPPERCASE")

    def test_pascal_case_rejected(self):
        """'PrimeCoder' must raise ValidationError (PascalCase is not kebab-case)."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="PrimeCoder")

    def test_spaces_rejected(self):
        """'my skill' (space-separated) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="my skill")

    def test_underscore_rejected(self):
        """'my_skill' (underscore) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="my_skill")

    def test_too_short_two_chars_rejected(self):
        """skill_name='ab' (2 chars, below min_length=3) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="ab")

    def test_too_short_one_char_rejected(self):
        """skill_name='a' (1 char) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="a")

    def test_leading_hyphen_rejected(self):
        """'-skill' (leading hyphen) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="-skill")

    def test_trailing_hyphen_rejected(self):
        """'skill-' (trailing hyphen) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_name="skill-")


# ===========================================================================
# SkillSubmission field-level constraints
# ===========================================================================


class TestSkillSubmissionFieldConstraints:
    """Field-level min/max length constraints on SkillSubmission."""

    def test_skill_content_too_short_rejected(self):
        """skill_content with fewer than 10 chars must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(skill_content="short")

    def test_skill_content_exactly_10_chars_accepted(self):
        """skill_content with exactly 10 chars must be accepted."""
        sub = _valid_submission(skill_content="1234567890")
        assert sub.skill_content == "1234567890"

    def test_description_max_512_accepted(self):
        """description up to 512 chars must be accepted."""
        long_desc = "x" * 512
        sub = _valid_submission(description=long_desc)
        assert len(sub.description) == 512

    def test_description_over_512_rejected(self):
        """description exceeding 512 chars must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(description="x" * 513)

    def test_source_context_max_1024_accepted(self):
        """source_context up to 1024 chars must be accepted."""
        ctx = "y" * 1024
        sub = _valid_submission(source_context=ctx)
        assert len(sub.source_context) == 1024

    def test_source_context_over_1024_rejected(self):
        """source_context exceeding 1024 chars must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(source_context="y" * 1025)

    def test_author_empty_string_rejected(self):
        """author='' (empty string, below min_length=1) must raise ValidationError."""
        with pytest.raises(ValidationError):
            _valid_submission(author="")


# ===========================================================================
# ReviewRecord model
# ===========================================================================
# Naval: "The ReviewRecord is the audit trail. An audit trail without
#  defaults is an audit trail that can be silently corrupted. status=pending
#  and rung_verified=None are the only honest starting states."


class TestReviewRecord:
    """ReviewRecord — creation, defaults, and optional fields."""

    def test_create_with_required_fields(self):
        """ReviewRecord must be constructable with all required fields."""
        rec = _valid_review_record()
        assert rec.skill_id == "550e8400-e29b-41d4-a716-446655440000"
        assert rec.skill_name == "prime-coder"
        assert rec.content_type == ContentType.skill
        assert rec.author == "phuc"
        assert rec.key_id == "acct_deadbeef"
        assert rec.rung_claimed == 641
        assert rec.skill_content == "# prime-coder content for review"
        assert isinstance(rec.submitted_at, datetime)

    def test_default_status_is_pending(self):
        """status must default to SkillStatus.pending."""
        rec = _valid_review_record()
        assert rec.status == SkillStatus.pending

    def test_default_rung_verified_is_none(self):
        """rung_verified must default to None (not 0, not the claimed rung)."""
        rec = _valid_review_record()
        assert rec.rung_verified is None

    def test_default_reviewed_at_is_none(self):
        """reviewed_at must default to None before any review has occurred."""
        rec = _valid_review_record()
        assert rec.reviewed_at is None

    def test_default_review_notes_is_none(self):
        """review_notes must default to None."""
        rec = _valid_review_record()
        assert rec.review_notes is None

    def test_default_behavior_hash_is_none(self):
        """behavior_hash must default to None before rung_validator runs."""
        rec = _valid_review_record()
        assert rec.behavior_hash is None

    def test_default_description_is_empty_string(self):
        """description must default to empty string."""
        rec = _valid_review_record()
        assert rec.description == ""

    def test_default_tags_is_empty_list(self):
        """tags must default to []."""
        rec = _valid_review_record()
        assert rec.tags == []

    def test_default_source_context_is_empty_string(self):
        """source_context must default to empty string."""
        rec = _valid_review_record()
        assert rec.source_context == ""

    def test_accepted_status_can_be_set(self):
        """status can be set to SkillStatus.accepted."""
        rec = _valid_review_record(status=SkillStatus.accepted)
        assert rec.status == SkillStatus.accepted

    def test_rung_verified_can_be_set(self):
        """rung_verified can be explicitly set after validation."""
        rec = _valid_review_record(rung_verified=641)
        assert rec.rung_verified == 641

    def test_content_type_recipe_accepted(self):
        """content_type can be ContentType.recipe."""
        rec = _valid_review_record(content_type=ContentType.recipe)
        assert rec.content_type == ContentType.recipe


# ===========================================================================
# SkillListing model
# ===========================================================================
# Naval: "The public API is a promise. SkillListing is what you show the
#  world. It strips internal state and presents only what the consumer needs.
#  Optional[str] = None means 'not yet reviewed' — an honest signal."


class TestSkillListing:
    """SkillListing — public-facing skill entry."""

    def test_create_full_listing(self):
        """SkillListing must be constructable with all fields provided."""
        now = _now()
        listing = SkillListing(
            skill_id="skill_abc123",
            skill_name="prime-coder",
            content_type=ContentType.skill,
            author="phuc",
            rung_claimed=641,
            rung_verified=641,
            description="A production-grade coder skill",
            tags=["coder", "prime"],
            submitted_at=now,
            reviewed_at=now,
            review_notes="Rung 641 verified. Evidence complete.",
            behavior_hash="a" * 64,
        )
        assert listing.skill_id == "skill_abc123"
        assert listing.skill_name == "prime-coder"
        assert listing.rung_claimed == 641
        assert listing.rung_verified == 641
        assert listing.skill_content is None  # not included in list endpoint

    def test_skill_content_optional_default_none(self):
        """skill_content must default to None in list response."""
        now = _now()
        listing = SkillListing(
            skill_id="skill_xyz",
            skill_name="my-skill",
            content_type=ContentType.swarm,
            author="author",
            rung_claimed=274177,
            rung_verified=None,
            description="",
            tags=[],
            submitted_at=now,
            reviewed_at=None,
            review_notes=None,
            behavior_hash=None,
        )
        assert listing.skill_content is None

    def test_skill_content_included_for_single_fetch(self):
        """skill_content can be explicitly set for single-skill fetch response."""
        now = _now()
        listing = SkillListing(
            skill_id="skill_single",
            skill_name="prime-math",
            content_type=ContentType.skill,
            author="phuc",
            rung_claimed=65537,
            rung_verified=65537,
            description="Math skill",
            tags=[],
            submitted_at=now,
            reviewed_at=now,
            review_notes=None,
            behavior_hash="b" * 64,
            skill_content="# prime-math full content here",
        )
        assert listing.skill_content == "# prime-math full content here"


# ===========================================================================
# InstallRequest model
# ===========================================================================
# Naval: "dry_run=True as the default is a safety-first design decision.
#  Destructive operations require explicit opt-in. This is the only honest
#  default for an install operation."


class TestInstallRequest:
    """InstallRequest — payload defaults and required fields."""

    def test_create_with_required_fields(self):
        """InstallRequest must be constructable with skill_id and target_repo."""
        req = InstallRequest(
            skill_id="skill_abc123",
            target_repo="/home/phuc/projects/stillwater",
        )
        assert req.skill_id == "skill_abc123"
        assert req.target_repo == "/home/phuc/projects/stillwater"

    def test_default_dry_run_is_true(self):
        """dry_run must default to True — safe default, no destructive action."""
        req = InstallRequest(
            skill_id="skill_abc123",
            target_repo="/home/phuc/projects/stillwater",
        )
        assert req.dry_run is True

    def test_dry_run_can_be_set_false(self):
        """dry_run can be explicitly set to False for a real install."""
        req = InstallRequest(
            skill_id="skill_abc123",
            target_repo="/home/phuc/projects/stillwater",
            dry_run=False,
        )
        assert req.dry_run is False

    def test_empty_skill_id_rejected(self):
        """skill_id='' must raise ValidationError (min_length=1)."""
        with pytest.raises(ValidationError):
            InstallRequest(skill_id="", target_repo="/some/path")

    def test_empty_target_repo_rejected(self):
        """target_repo='' must raise ValidationError (min_length=1)."""
        with pytest.raises(ValidationError):
            InstallRequest(skill_id="skill_abc", target_repo="")

    def test_git_remote_url_accepted_as_target_repo(self):
        """target_repo accepts a git remote URL as well as a local path."""
        req = InstallRequest(
            skill_id="skill_abc",
            target_repo="https://github.com/phuc/my-project",
        )
        assert "github.com" in req.target_repo


# ===========================================================================
# InstallResult model
# ===========================================================================
# Naval: "The result model is the receipt. It records what actually happened —
#  not what was planned. installed=bool is unambiguous. message is the
#  human-readable audit note."


class TestInstallResult:
    """InstallResult — result model for the install operation."""

    def test_create_successful_install(self):
        """InstallResult must be constructable with all fields."""
        result = InstallResult(
            skill_id="skill_abc123",
            skill_name="prime-coder",
            target_repo="/home/phuc/projects/stillwater",
            dry_run=False,
            installed=True,
            message="Installed prime-coder to skills/prime-coder.md",
        )
        assert result.skill_id == "skill_abc123"
        assert result.skill_name == "prime-coder"
        assert result.installed is True
        assert result.dry_run is False

    def test_create_dry_run_result(self):
        """InstallResult can represent a dry-run (installed=False, dry_run=True)."""
        result = InstallResult(
            skill_id="skill_xyz",
            skill_name="my-skill",
            target_repo="/some/path",
            dry_run=True,
            installed=False,
            message="Dry run: would install my-skill to /some/path/skills/my-skill.md",
        )
        assert result.dry_run is True
        assert result.installed is False

    def test_create_failed_install(self):
        """InstallResult can represent a failed install (installed=False)."""
        result = InstallResult(
            skill_id="skill_abc",
            skill_name="prime-coder",
            target_repo="/bad/path",
            dry_run=False,
            installed=False,
            message="Error: target_repo does not exist",
        )
        assert result.installed is False
        assert "Error" in result.message


# ===========================================================================
# PaginatedSkillList model
# ===========================================================================
# Naval: "Pagination is the interface between infinite data and finite
#  attention. total + page + per_page gives the consumer everything needed
#  to navigate the store without over-fetching."


class TestPaginatedSkillList:
    """PaginatedSkillList — paginated response for GET /store/skills."""

    def _make_listing(self, skill_id: str, skill_name: str) -> SkillListing:
        now = _now()
        return SkillListing(
            skill_id=skill_id,
            skill_name=skill_name,
            content_type=ContentType.skill,
            author="phuc",
            rung_claimed=641,
            rung_verified=None,
            description="",
            tags=[],
            submitted_at=now,
            reviewed_at=None,
            review_notes=None,
            behavior_hash=None,
        )

    def test_create_empty_page(self):
        """PaginatedSkillList must be constructable with zero skills."""
        paginated = PaginatedSkillList(total=0, page=1, per_page=20, skills=[])
        assert paginated.total == 0
        assert paginated.skills == []

    def test_create_with_skills(self):
        """PaginatedSkillList must store a list of SkillListing objects."""
        listings = [
            self._make_listing("s1", "prime-alpha"),
            self._make_listing("s2", "prime-beta"),
        ]
        paginated = PaginatedSkillList(total=2, page=1, per_page=20, skills=listings)
        assert paginated.total == 2
        assert len(paginated.skills) == 2
        assert paginated.skills[0].skill_name == "prime-alpha"
        assert paginated.skills[1].skill_name == "prime-beta"

    def test_page_and_per_page_stored(self):
        """page and per_page must be stored as provided."""
        paginated = PaginatedSkillList(total=100, page=3, per_page=10, skills=[])
        assert paginated.page == 3
        assert paginated.per_page == 10
        assert paginated.total == 100


# ===========================================================================
# Model serialization round-trip
# ===========================================================================
# Naval: "A model that cannot survive serialization is not a model — it is a
#  temporary illusion. model_dump → model_validate must be an identity
#  transformation. Anything less is a broken contract."


class TestSerializationRoundTrip:
    """model_dump / model_validate round-trip for all models."""

    def test_skill_submission_round_trip(self):
        """SkillSubmission must survive model_dump → model_validate without data loss."""
        original = _valid_submission(
            tags=["ai", "coder"],
            description="A great skill",
            source_context="from swarms/coder.md",
        )
        data = original.model_dump()
        restored = SkillSubmission.model_validate(data)
        assert restored.skill_name == original.skill_name
        assert restored.rung_claimed == original.rung_claimed
        assert restored.tags == original.tags
        assert restored.content_type == original.content_type

    def test_api_key_round_trip(self):
        """APIKey must survive model_dump → model_validate."""
        original = _valid_api_key(
            reputation=2.5,
            submission_count=5,
            accepted_count=4,
            rejected_count=1,
            recent_submission_timestamps=["2026-01-01T00:00:00Z"],
        )
        data = original.model_dump()
        restored = APIKey.model_validate(data)
        assert restored.key_id == original.key_id
        assert restored.reputation == original.reputation
        assert restored.submission_count == original.submission_count
        assert restored.recent_submission_timestamps == original.recent_submission_timestamps

    def test_review_record_round_trip(self):
        """ReviewRecord must survive model_dump → model_validate."""
        now = _now()
        original = _valid_review_record(
            status=SkillStatus.accepted,
            rung_verified=641,
            reviewed_at=now,
            review_notes="Evidence verified. Rung 641 confirmed.",
            behavior_hash="c" * 64,
        )
        data = original.model_dump()
        restored = ReviewRecord.model_validate(data)
        assert restored.skill_id == original.skill_id
        assert restored.status == SkillStatus.accepted
        assert restored.rung_verified == 641
        assert restored.behavior_hash == "c" * 64
        assert restored.review_notes == "Evidence verified. Rung 641 confirmed."

    def test_install_request_round_trip(self):
        """InstallRequest must survive model_dump → model_validate."""
        original = InstallRequest(
            skill_id="skill_rt",
            target_repo="/home/phuc/projects/test",
            dry_run=False,
        )
        data = original.model_dump()
        restored = InstallRequest.model_validate(data)
        assert restored.skill_id == original.skill_id
        assert restored.target_repo == original.target_repo
        assert restored.dry_run is False

    def test_install_result_round_trip(self):
        """InstallResult must survive model_dump → model_validate."""
        original = InstallResult(
            skill_id="skill_rt",
            skill_name="prime-rt",
            target_repo="/home/phuc/projects/test",
            dry_run=True,
            installed=False,
            message="Dry run complete",
        )
        data = original.model_dump()
        restored = InstallResult.model_validate(data)
        assert restored.skill_id == original.skill_id
        assert restored.installed == original.installed
        assert restored.message == original.message

    def test_paginated_skill_list_round_trip(self):
        """PaginatedSkillList must survive model_dump → model_validate."""
        now = _now()
        listing = SkillListing(
            skill_id="s_rt",
            skill_name="prime-rt",
            content_type=ContentType.recipe,
            author="phuc",
            rung_claimed=274177,
            rung_verified=274177,
            description="RT skill",
            tags=["round-trip"],
            submitted_at=now,
            reviewed_at=now,
            review_notes=None,
            behavior_hash="d" * 64,
        )
        original = PaginatedSkillList(total=1, page=1, per_page=20, skills=[listing])
        data = original.model_dump()
        restored = PaginatedSkillList.model_validate(data)
        assert restored.total == 1
        assert len(restored.skills) == 1
        assert restored.skills[0].skill_name == "prime-rt"
        assert restored.skills[0].content_type == ContentType.recipe
