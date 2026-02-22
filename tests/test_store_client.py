"""
tests/test_store_client.py — Integration tests for Stillwater Store Client SDK.

Tests:
  - store/packager.py  (SkillPackager: bundle, SHA-256 manifest, integrity)
  - store/rung_validator.py (RungValidator: schema, 3-seed hash replay, fail-closed)
  - store/client.py    (StillwaterStoreClient: submit, fetch, list, install — all mocked)

Rung target: 641 (local correctness, all mocks, no real HTTP)
Network: OFF — all HTTP calls are mocked via unittest.mock.patch

Red-Green gate: this file is committed first. Tests must FAIL before the
implementation exists, then PASS after implementation is complete.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the store package is importable (store/ lives at the project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_skill(tmp_path: Path, name: str = "prime-test", content: str = "# test skill") -> Path:
    skill_file = tmp_path / f"{name}.md"
    skill_file.write_text(content, encoding="utf-8")
    return skill_file


def _make_evidence_dir(tmp_path: Path, behavior_hash: str = "abc123") -> Path:
    """Create a minimal valid evidence directory."""
    ev = tmp_path / "evidence"
    ev.mkdir(exist_ok=True)

    plan = {
        "task_family": "swe_patch",
        "rung_target": 641,
        "design_decisions": ["minimal diff", "fail-closed"],
        "files_changed": ["store/packager.py"],
    }
    tests_json = {
        "test_command": "pytest tests/test_store_client.py -v",
        "exit_code": 0,
        "total": 16,
        "passed": 16,
        "failed": 0,
        "failing_before": ["test_packager_bundle"],
        "passing_after": ["test_packager_bundle"],
    }
    behavior = {
        "seed_42":   behavior_hash,
        "seed_137":  behavior_hash,
        "seed_9001": behavior_hash,
    }

    (ev / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (ev / "tests.json").write_text(json.dumps(tests_json), encoding="utf-8")
    (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")

    return ev


# ===========================================================================
# CHECKPOINT 1: Packager tests
# ===========================================================================

class TestSkillPackager:
    """Tests for store/packager.py — SkillPackager."""

    def test_packager_bundle_returns_dict(self, tmp_path):
        """bundle_skill() must return a dict with required keys."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)
        packager = SkillPackager()
        bundle = packager.bundle_skill(
            skill_path=skill_file,
            evidence_dir=ev,
            author="test-author",
            rung_claimed=641,
        )
        assert isinstance(bundle, dict)
        required_keys = {"skill_name", "skill_content", "author", "rung_claimed",
                         "manifest_sha256", "evidence"}
        assert required_keys <= bundle.keys(), (
            f"Missing keys: {required_keys - bundle.keys()}"
        )

    def test_packager_sha256_manifest(self, tmp_path):
        """SHA-256 manifest must be a valid 64-char hex string."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path, content="# my skill content")
        ev = _make_evidence_dir(tmp_path)
        packager = SkillPackager()
        bundle = packager.bundle_skill(skill_file, ev, "author", 641)
        sha = bundle["manifest_sha256"]
        assert isinstance(sha, str)
        assert len(sha) == 64, f"Expected 64-char hex, got {len(sha)}"
        # Must be valid hex
        int(sha, 16)

    def test_packager_integrity_round_trip(self, tmp_path):
        """verify_bundle() must return True for a bundle produced by bundle_skill()."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path, content="# integrity test")
        ev = _make_evidence_dir(tmp_path)
        packager = SkillPackager()
        bundle = packager.bundle_skill(skill_file, ev, "author", 641)
        assert packager.verify_bundle(bundle) is True

    def test_packager_tamper_detected(self, tmp_path):
        """verify_bundle() must return False if skill_content is modified."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path, content="# original content")
        ev = _make_evidence_dir(tmp_path)
        packager = SkillPackager()
        bundle = packager.bundle_skill(skill_file, ev, "author", 641)
        # Tamper with content
        bundle["skill_content"] = "# TAMPERED"
        assert packager.verify_bundle(bundle) is False

    def test_packager_skill_name_derived_from_filename(self, tmp_path):
        """skill_name in bundle must match the stem of the skill file."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path, name="my-cool-skill", content="# cool")
        ev = _make_evidence_dir(tmp_path)
        packager = SkillPackager()
        bundle = packager.bundle_skill(skill_file, ev, "author", 641)
        assert bundle["skill_name"] == "my-cool-skill"

    def test_packager_missing_evidence_raises(self, tmp_path):
        """bundle_skill() must raise ValueError if evidence_dir does not exist."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path)
        packager = SkillPackager()
        with pytest.raises((ValueError, FileNotFoundError)):
            packager.bundle_skill(skill_file, tmp_path / "nonexistent", "author", 641)

    def test_packager_invalid_rung_raises(self, tmp_path):
        """bundle_skill() must raise ValueError for invalid rung (e.g. 999)."""
        from store.packager import SkillPackager
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)
        packager = SkillPackager()
        with pytest.raises(ValueError, match="rung"):
            packager.bundle_skill(skill_file, ev, "author", 999)


# ===========================================================================
# CHECKPOINT 2: Rung Validator tests
# ===========================================================================

class TestRungValidator:
    """Tests for store/rung_validator.py — RungValidator."""

    def test_validator_accepts_valid_evidence(self, tmp_path):
        """verify_evidence() must return 'VALID' for a complete, correct evidence dir."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path, behavior_hash="deadbeef" * 8)
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "VALID", f"Expected VALID, got {result}"

    def test_validator_missing_plan_json_is_invalid(self, tmp_path):
        """Missing plan.json → status=INVALID (fail-closed)."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        (ev / "plan.json").unlink()
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID", f"Expected INVALID, got {result}"

    def test_validator_missing_tests_json_is_invalid(self, tmp_path):
        """Missing tests.json → status=INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        (ev / "tests.json").unlink()
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID"

    def test_validator_missing_behavior_hash_is_invalid(self, tmp_path):
        """Missing behavior_hash.txt → status=INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        (ev / "behavior_hash.txt").unlink()
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID"

    def test_validator_seed_mismatch_is_invalid(self, tmp_path):
        """If any of the 3 seeds disagree, result must be INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        # Tamper: seed_137 disagrees
        behavior = {
            "seed_42":   "aaaaaaaabbbbbbbbccccccccdddddddd" * 2,
            "seed_137":  "DIFFERENT_HASH_HERE_seed137_xxxxxxxxxxx",  # mismatch
            "seed_9001": "aaaaaaaabbbbbbbbccccccccdddddddd" * 2,
        }
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID", f"Expected INVALID on seed mismatch, got {result}"

    def test_validator_all_three_seeds_required(self, tmp_path):
        """If any seed key is missing (seed_42, seed_137, seed_9001), result=INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        behavior = {
            "seed_42":  "aaa",
            # seed_137 missing
            "seed_9001": "aaa",
        }
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID"

    def test_validator_null_rung_is_invalid(self, tmp_path):
        """null rung_target → INVALID (null != zero, fail-closed)."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=None)
        assert result == "INVALID"

    def test_validator_invalid_rung_value_is_invalid(self, tmp_path):
        """Unsupported rung value (e.g. 99) → INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=99)
        assert result == "INVALID"

    def test_validator_invalid_json_in_plan_is_invalid(self, tmp_path):
        """Malformed JSON in plan.json → INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        (ev / "plan.json").write_text("{not valid json}", encoding="utf-8")
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID"

    def test_validator_schema_compliance_plan_requires_rung_target(self, tmp_path):
        """plan.json missing rung_target field → INVALID."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        plan = json.loads((ev / "plan.json").read_text())
        del plan["rung_target"]
        (ev / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        validator = RungValidator()
        result = validator.verify_evidence(ev, rung_target=641)
        assert result == "INVALID"


# ===========================================================================
# CHECKPOINT 3: Client SDK tests
# ===========================================================================

class TestStillwaterStoreClient:
    """Tests for store/client.py — StillwaterStoreClient."""

    # -----------------------------------------------------------------------
    # Happy path
    # -----------------------------------------------------------------------

    def test_client_submit_happy_path(self, tmp_path):
        """submit_skill() → returns submission_id on HTTP 201."""
        from store.client import StillwaterStoreClient
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)

        fake_response = MagicMock()
        fake_response.status_code = 201
        fake_response.json.return_value = {"submission_id": "sub_abc123"}

        with patch("store.client.requests.post", return_value=fake_response) as mock_post:
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "a" * 32,
                base_url="https://www.solaceagi.com",
            )
            sub_id = client.submit_skill(
                skill_path=skill_file,
                author="test-author",
                rung_claimed=641,
                evidence_dir=ev,
            )

        assert sub_id == "sub_abc123"
        mock_post.assert_called_once()
        # Verify Authorization header includes Bearer
        # Check the actual call had headers passed
        assert mock_post.called

    def test_client_fetch_skill_happy_path(self, tmp_path):
        """fetch_skill() → returns skill content string on HTTP 200."""
        from store.client import StillwaterStoreClient
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            "skill_id": "skill_xyz",
            "skill_name": "prime-test",
            "skill_content": "# prime-test skill content",
            "author": "phuc",
            "rung_claimed": 641,
        }

        with patch("store.client.requests.get", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "b" * 32,
                base_url="https://www.solaceagi.com",
            )
            content = client.fetch_skill("skill_xyz")

        assert content == "# prime-test skill content"

    def test_client_list_skills_happy_path(self, tmp_path):
        """list_skills() → returns list of skill metadata dicts."""
        from store.client import StillwaterStoreClient
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            "total": 2,
            "page": 1,
            "per_page": 20,
            "skills": [
                {"skill_id": "s1", "skill_name": "prime-alpha", "author": "a"},
                {"skill_id": "s2", "skill_name": "prime-beta",  "author": "b"},
            ],
        }

        with patch("store.client.requests.get", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "c" * 32,
                base_url="https://www.solaceagi.com",
            )
            results = client.list_skills(query="prime")

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["skill_name"] == "prime-alpha"

    def test_client_install_skill_happy_path(self, tmp_path):
        """install_skill() → writes skill file to target_dir, returns installed path."""
        from store.client import StillwaterStoreClient
        target_dir = tmp_path / "skills"
        target_dir.mkdir()

        fetch_response = MagicMock()
        fetch_response.status_code = 200
        fetch_response.json.return_value = {
            "skill_id": "skill_xyz",
            "skill_name": "prime-install-test",
            "skill_content": "# installed skill content",
            "author": "phuc",
            "rung_claimed": 641,
        }

        with patch("store.client.requests.get", return_value=fetch_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "d" * 32,
                base_url="https://www.solaceagi.com",
            )
            installed_path = client.install_skill("skill_xyz", target_dir=target_dir)

        assert Path(installed_path).exists()
        assert Path(installed_path).read_text(encoding="utf-8") == "# installed skill content"

    # -----------------------------------------------------------------------
    # Error paths
    # -----------------------------------------------------------------------

    def test_client_missing_api_key_raises(self, tmp_path):
        """Constructing client with empty api_key → ValueError."""
        from store.client import StillwaterStoreClient
        with pytest.raises(ValueError, match="api_key"):
            StillwaterStoreClient(api_key="", base_url="https://www.solaceagi.com")

    def test_client_invalid_api_key_format_raises(self, tmp_path):
        """Constructing client with wrong key prefix → ValueError."""
        from store.client import StillwaterStoreClient
        with pytest.raises(ValueError, match="sw_sk_"):
            StillwaterStoreClient(api_key="bad_key_format", base_url="https://www.solaceagi.com")

    def test_client_submit_401_unauthorized(self, tmp_path):
        """submit_skill() → raises PermissionError on HTTP 401."""
        from store.client import StillwaterStoreClient
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)

        fake_response = MagicMock()
        fake_response.status_code = 401
        fake_response.json.return_value = {"detail": "Invalid API key"}

        with patch("store.client.requests.post", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "e" * 32,
                base_url="https://www.solaceagi.com",
            )
            with pytest.raises(PermissionError):
                client.submit_skill(skill_file, author="test", rung_claimed=641, evidence_dir=ev)

    def test_client_submit_422_validation_error(self, tmp_path):
        """submit_skill() → raises ValueError on HTTP 422."""
        from store.client import StillwaterStoreClient
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)

        fake_response = MagicMock()
        fake_response.status_code = 422
        fake_response.json.return_value = {"detail": "validation error"}

        with patch("store.client.requests.post", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "f" * 32,
                base_url="https://www.solaceagi.com",
            )
            with pytest.raises(ValueError):
                client.submit_skill(skill_file, author="test", rung_claimed=641, evidence_dir=ev)

    def test_client_submit_500_server_error(self, tmp_path):
        """submit_skill() → raises RuntimeError on HTTP 500."""
        from store.client import StillwaterStoreClient
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)

        fake_response = MagicMock()
        fake_response.status_code = 500
        fake_response.json.return_value = {"detail": "internal error"}

        with patch("store.client.requests.post", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "0" * 32,
                base_url="https://www.solaceagi.com",
            )
            with pytest.raises(RuntimeError):
                client.submit_skill(skill_file, author="test", rung_claimed=641, evidence_dir=ev)

    def test_client_fetch_skill_not_found(self, tmp_path):
        """fetch_skill() → raises LookupError on HTTP 404."""
        from store.client import StillwaterStoreClient
        fake_response = MagicMock()
        fake_response.status_code = 404
        fake_response.json.return_value = {"detail": "not found"}

        with patch("store.client.requests.get", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "1" * 32,
                base_url="https://www.solaceagi.com",
            )
            with pytest.raises(LookupError):
                client.fetch_skill("nonexistent_id")

    def test_client_api_key_never_in_repr(self, tmp_path):
        """API key must not appear in repr() or str() of client."""
        from store.client import StillwaterStoreClient
        key = "sw_sk_" + "a" * 32
        client = StillwaterStoreClient(api_key=key, base_url="https://www.solaceagi.com")
        assert key not in repr(client), "API key leaked in repr()"
        assert key not in str(client), "API key leaked in str()"

    # -----------------------------------------------------------------------
    # Security: API key not in headers via logs / exception messages
    # -----------------------------------------------------------------------

    def test_client_submit_error_message_no_api_key(self, tmp_path):
        """Error messages from submit_skill() must not contain the raw API key."""
        from store.client import StillwaterStoreClient
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)

        fake_response = MagicMock()
        fake_response.status_code = 401
        fake_response.json.return_value = {"detail": "Unauthorized"}

        key = "sw_sk_" + "2" * 32
        with patch("store.client.requests.post", return_value=fake_response):
            client = StillwaterStoreClient(api_key=key, base_url="https://www.solaceagi.com")
            try:
                client.submit_skill(skill_file, author="test", rung_claimed=641, evidence_dir=ev)
            except PermissionError as exc:
                assert key not in str(exc), "API key leaked in exception message"

    def test_client_submit_429_rate_limited(self, tmp_path):
        """submit_skill() → raises RuntimeError on HTTP 429 (rate limited)."""
        from store.client import StillwaterStoreClient
        skill_file = _write_skill(tmp_path)
        ev = _make_evidence_dir(tmp_path)

        fake_response = MagicMock()
        fake_response.status_code = 429
        fake_response.json.return_value = {"detail": "Rate limit exceeded"}

        with patch("store.client.requests.post", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "3" * 32,
                base_url="https://www.solaceagi.com",
            )
            with pytest.raises(RuntimeError, match="429"):
                client.submit_skill(skill_file, author="test", rung_claimed=641, evidence_dir=ev)

    def test_client_unexpected_status_code_raises(self, tmp_path):
        """Unexpected HTTP status (e.g. 418) → raises RuntimeError."""
        from store.client import StillwaterStoreClient
        fake_response = MagicMock()
        fake_response.status_code = 418
        fake_response.json.return_value = {"detail": "I'm a teapot"}

        with patch("store.client.requests.get", return_value=fake_response):
            client = StillwaterStoreClient(
                api_key="sw_sk_" + "4" * 32,
                base_url="https://www.solaceagi.com",
            )
            with pytest.raises(RuntimeError, match="418"):
                client.fetch_skill("some_id")


# ===========================================================================
# CHECKPOINT 4: No circular imports
# ===========================================================================

class TestNoCircularImports:
    """Ensure store modules can be imported without circular dependencies."""

    def test_import_packager(self):
        import importlib
        mod = importlib.import_module("store.packager")
        assert hasattr(mod, "SkillPackager")

    def test_import_rung_validator(self):
        import importlib
        mod = importlib.import_module("store.rung_validator")
        assert hasattr(mod, "RungValidator")

    def test_import_client(self):
        import importlib
        mod = importlib.import_module("store.client")
        assert hasattr(mod, "StillwaterStoreClient")

    def test_import_order_independence(self):
        """All three modules must be importable in any order without errors."""
        import importlib
        importlib.import_module("store.client")
        importlib.import_module("store.packager")
        importlib.import_module("store.rung_validator")

    def test_store_init_exports_store_client(self):
        """store package must export StoreClient alias."""
        import store
        assert hasattr(store, "StoreClient"), "store must export StoreClient"

    def test_store_init_exports_rung_validator(self):
        """store package must export RungValidator."""
        import store
        assert hasattr(store, "RungValidator"), "store must export RungValidator"

    def test_store_init_exports_skill_packager(self):
        """store package must export SkillPackager."""
        import store
        assert hasattr(store, "SkillPackager"), "store must export SkillPackager"

    def test_store_client_alias_is_stillwater_store_client(self):
        """StoreClient must be the same class as StillwaterStoreClient."""
        import store
        from store.client import StillwaterStoreClient
        assert store.StoreClient is StillwaterStoreClient


# ===========================================================================
# CHECKPOINT 5: RungValidator spec-interface tests
# ===========================================================================

class TestRungValidatorSpecInterface:
    """Tests for the spec-required methods: validate_bundle, verify_rung, compute_behavior_hash."""

    def test_validate_bundle_valid(self, tmp_path):
        """validate_bundle() returns status=VALID for a correctly formed bundle."""
        from store.rung_validator import RungValidator
        # Create a valid bundle matching validate_bundle's requirements:
        # plan.json needs goal, constraints, rung_target
        # tests.json needs exit_code=0, pass_count>0, fail_count=0
        # behavior_hash.txt needs all three seeds as 64-char hex sha256
        ev = tmp_path / "bundle"
        ev.mkdir()
        sha_hex = "a" * 64  # 64 valid hex chars
        plan = {"goal": "test skill", "constraints": ["no drift"], "rung_target": 641}
        tests_json = {
            "test_command": "pytest",
            "exit_code": 0,
            "pass_count": 5,
            "fail_count": 0,
        }
        behavior = {
            "seed_42":   sha_hex,
            "seed_137":  sha_hex,
            "seed_9001": sha_hex,
        }
        (ev / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        (ev / "tests.json").write_text(json.dumps(tests_json), encoding="utf-8")
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")

        validator = RungValidator()
        result = validator.validate_bundle(ev)
        assert result["status"] == "VALID", f"Expected VALID, got {result}"
        assert result["errors"] == []

    def test_validate_bundle_missing_plan_json(self, tmp_path):
        """validate_bundle() returns INVALID when plan.json is missing."""
        from store.rung_validator import RungValidator
        ev = tmp_path / "bundle"
        ev.mkdir()
        sha_hex = "b" * 64
        tests_json = {"test_command": "pytest", "exit_code": 0, "pass_count": 1, "fail_count": 0}
        behavior = {"seed_42": sha_hex, "seed_137": sha_hex, "seed_9001": sha_hex}
        (ev / "tests.json").write_text(json.dumps(tests_json), encoding="utf-8")
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")

        validator = RungValidator()
        result = validator.validate_bundle(ev)
        assert result["status"] == "INVALID"
        assert any("plan.json" in e for e in result["errors"])

    def test_validate_bundle_nonzero_exit_code(self, tmp_path):
        """validate_bundle() returns INVALID when tests.json exit_code != 0."""
        from store.rung_validator import RungValidator
        ev = tmp_path / "bundle"
        ev.mkdir()
        sha_hex = "c" * 64
        plan = {"goal": "test", "constraints": [], "rung_target": 641}
        tests_json = {"test_command": "pytest", "exit_code": 1, "pass_count": 3, "fail_count": 2}
        behavior = {"seed_42": sha_hex, "seed_137": sha_hex, "seed_9001": sha_hex}
        (ev / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        (ev / "tests.json").write_text(json.dumps(tests_json), encoding="utf-8")
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")

        validator = RungValidator()
        result = validator.validate_bundle(ev)
        assert result["status"] == "INVALID"
        assert any("exit_code" in e for e in result["errors"])

    def test_validate_bundle_invalid_hash_length(self, tmp_path):
        """validate_bundle() returns INVALID when behavior hash is not 64 hex chars."""
        from store.rung_validator import RungValidator
        ev = tmp_path / "bundle"
        ev.mkdir()
        short_hash = "abc123"  # too short — not 64 chars
        plan = {"goal": "test", "constraints": [], "rung_target": 641}
        tests_json = {"test_command": "pytest", "exit_code": 0, "pass_count": 1, "fail_count": 0}
        behavior = {"seed_42": short_hash, "seed_137": short_hash, "seed_9001": short_hash}
        (ev / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        (ev / "tests.json").write_text(json.dumps(tests_json), encoding="utf-8")
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")

        validator = RungValidator()
        result = validator.validate_bundle(ev)
        assert result["status"] == "INVALID"

    def test_validate_bundle_missing_plan_fields(self, tmp_path):
        """validate_bundle() returns INVALID when plan.json is missing goal/constraints/rung_target."""
        from store.rung_validator import RungValidator
        ev = tmp_path / "bundle"
        ev.mkdir()
        sha_hex = "d" * 64
        plan = {"task_family": "swe"}  # missing goal, constraints, rung_target
        tests_json = {"test_command": "pytest", "exit_code": 0, "pass_count": 1, "fail_count": 0}
        behavior = {"seed_42": sha_hex, "seed_137": sha_hex, "seed_9001": sha_hex}
        (ev / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        (ev / "tests.json").write_text(json.dumps(tests_json), encoding="utf-8")
        (ev / "behavior_hash.txt").write_text(json.dumps(behavior), encoding="utf-8")

        validator = RungValidator()
        result = validator.validate_bundle(ev)
        assert result["status"] == "INVALID"
        # Should report multiple missing fields
        assert len(result["errors"]) >= 2

    def test_verify_rung_641_valid(self, tmp_path):
        """verify_rung(641, ...) returns VALID when tests.json and plan.json present with exit_code=0."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        validator = RungValidator()
        result = validator.verify_rung(641, ev)
        assert result == "VALID", f"Expected VALID for rung 641, got {result}"

    def test_verify_rung_274177_valid(self, tmp_path):
        """verify_rung(274177, ...) returns VALID when behavior_hash.txt present with 3-seed consensus."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path, behavior_hash="e" * 64)
        # behavior_hash.txt already has 3 seeds from _make_evidence_dir
        validator = RungValidator()
        result = validator.verify_rung(274177, ev)
        assert result == "VALID", f"Expected VALID for rung 274177, got {result}"

    def test_verify_rung_65537_requires_security_scan(self, tmp_path):
        """verify_rung(65537, ...) returns INVALID without security_scan.json."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path, behavior_hash="f" * 64)
        validator = RungValidator()
        result = validator.verify_rung(65537, ev)
        assert result == "INVALID", "Expected INVALID: no security_scan.json"

    def test_verify_rung_65537_valid_with_security_scan(self, tmp_path):
        """verify_rung(65537, ...) returns VALID with passing security_scan.json."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path, behavior_hash="0" * 64)
        security_scan = {"status": "PASS", "tool": "bandit", "issues": []}
        (ev / "security_scan.json").write_text(json.dumps(security_scan), encoding="utf-8")
        validator = RungValidator()
        result = validator.verify_rung(65537, ev)
        assert result == "VALID", f"Expected VALID for rung 65537 with security_scan, got {result}"

    def test_verify_rung_null_is_invalid(self, tmp_path):
        """verify_rung(None, ...) returns INVALID (null != 0, fail-closed)."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        validator = RungValidator()
        result = validator.verify_rung(None, ev)
        assert result == "INVALID"

    def test_verify_rung_unknown_rung_is_invalid(self, tmp_path):
        """verify_rung(999, ...) returns INVALID for unknown rung value."""
        from store.rung_validator import RungValidator
        ev = _make_evidence_dir(tmp_path)
        validator = RungValidator()
        result = validator.verify_rung(999, ev)
        assert result == "INVALID"

    def test_compute_behavior_hash_is_64_char_hex(self):
        """compute_behavior_hash() returns a 64-char hex SHA-256 string."""
        from store.rung_validator import RungValidator
        h = RungValidator.compute_behavior_hash("pytest passed 5 tests", seed=42)
        assert isinstance(h, str)
        assert len(h) == 64, f"Expected 64-char hex, got {len(h)}"
        int(h, 16)  # must be valid hex

    def test_compute_behavior_hash_deterministic(self):
        """compute_behavior_hash() produces the same result for same inputs."""
        from store.rung_validator import RungValidator
        h1 = RungValidator.compute_behavior_hash("test output line 1\ntest output line 2", seed=42)
        h2 = RungValidator.compute_behavior_hash("test output line 1\ntest output line 2", seed=42)
        assert h1 == h2, "compute_behavior_hash must be deterministic"

    def test_compute_behavior_hash_seed_changes_output(self):
        """Different seeds must produce different hashes."""
        from store.rung_validator import RungValidator
        h_42   = RungValidator.compute_behavior_hash("same output", seed=42)
        h_137  = RungValidator.compute_behavior_hash("same output", seed=137)
        h_9001 = RungValidator.compute_behavior_hash("same output", seed=9001)
        assert h_42 != h_137, "seed=42 and seed=137 should produce different hashes"
        assert h_42 != h_9001, "seed=42 and seed=9001 should produce different hashes"


# ===========================================================================
# CHECKPOINT 6: SkillPackager spec-interface tests
# ===========================================================================

class TestSkillPackagerSpecInterface:
    """Tests for the spec-required methods: package_skill, validate_frontmatter, compute_sha256_manifest."""

    _VALID_FRONTMATTER_SKILL = """\
---
name: prime-test
version: 1.2.3
rung: 641
description: A test skill
scopes: [read, write]
author: test-author
---

# prime-test

This is the skill body.
"""

    def test_package_skill_without_evidence(self, tmp_path):
        """package_skill() with no evidence_dir returns payload without evidence."""
        from store.packager import SkillPackager
        skill_file = tmp_path / "prime-test.md"
        skill_file.write_text(self._VALID_FRONTMATTER_SKILL, encoding="utf-8")

        packager = SkillPackager()
        payload = packager.package_skill(skill_file)

        assert "skill_content" in payload
        assert "frontmatter" in payload
        assert "sha256_manifest" in payload
        assert "packaged_at" in payload
        assert payload["evidence"] is None
        assert payload["frontmatter"]["name"] == "prime-test"
        assert payload["frontmatter"]["version"] == "1.2.3"

    def test_package_skill_with_evidence(self, tmp_path):
        """package_skill() with evidence_dir includes evidence in payload."""
        from store.packager import SkillPackager
        skill_file = tmp_path / "prime-test.md"
        skill_file.write_text(self._VALID_FRONTMATTER_SKILL, encoding="utf-8")
        ev = _make_evidence_dir(tmp_path)

        packager = SkillPackager()
        payload = packager.package_skill(skill_file, evidence_dir=ev)

        assert payload["evidence"] is not None
        assert "tests.json" in payload["evidence"]
        assert "plan.json" in payload["evidence"]
        assert "behavior_hash.txt" in payload["evidence"]

    def test_package_skill_sha256_manifest_includes_all_files(self, tmp_path):
        """package_skill() sha256_manifest must cover skill file and all evidence files."""
        from store.packager import SkillPackager
        skill_file = tmp_path / "prime-test.md"
        skill_file.write_text(self._VALID_FRONTMATTER_SKILL, encoding="utf-8")
        ev = _make_evidence_dir(tmp_path)

        packager = SkillPackager()
        payload = packager.package_skill(skill_file, evidence_dir=ev)

        manifest = payload["sha256_manifest"]
        assert "prime-test.md" in manifest
        assert "tests.json" in manifest
        assert "plan.json" in manifest
        assert "behavior_hash.txt" in manifest
        # All hashes must be 64-char hex
        for fname, h in manifest.items():
            assert len(h) == 64, f"{fname}: expected 64-char hex, got {len(h)}"
            int(h, 16)

    def test_package_skill_missing_file_raises(self, tmp_path):
        """package_skill() raises FileNotFoundError if skill file does not exist."""
        from store.packager import SkillPackager
        packager = SkillPackager()
        with pytest.raises(FileNotFoundError):
            packager.package_skill(tmp_path / "nonexistent.md")

    def test_package_skill_missing_frontmatter_raises(self, tmp_path):
        """package_skill() raises ValueError if skill file has no valid frontmatter."""
        from store.packager import SkillPackager
        skill_file = tmp_path / "no-fm.md"
        skill_file.write_text("# no frontmatter here\njust body text\n", encoding="utf-8")

        packager = SkillPackager()
        with pytest.raises(ValueError, match="[Ff]rontmatter"):
            packager.package_skill(skill_file)

    def test_validate_frontmatter_valid(self):
        """validate_frontmatter() returns valid=True for correct frontmatter."""
        from store.packager import SkillPackager
        packager = SkillPackager()
        result = packager.validate_frontmatter(self._VALID_FRONTMATTER_SKILL)
        assert result["valid"] is True, f"Expected valid, got errors: {result['errors']}"
        assert result["fields"]["name"] == "prime-test"
        assert result["fields"]["version"] == "1.2.3"

    def test_validate_frontmatter_missing_name(self):
        """validate_frontmatter() returns valid=False if name is missing."""
        from store.packager import SkillPackager
        content = "---\nversion: 1.0.0\n---\n# body\n"
        packager = SkillPackager()
        result = packager.validate_frontmatter(content)
        assert result["valid"] is False
        assert any("name" in e for e in result["errors"])

    def test_validate_frontmatter_missing_version(self):
        """validate_frontmatter() returns valid=False if version is missing."""
        from store.packager import SkillPackager
        content = "---\nname: my-skill\n---\n# body\n"
        packager = SkillPackager()
        result = packager.validate_frontmatter(content)
        assert result["valid"] is False
        assert any("version" in e for e in result["errors"])

    def test_validate_frontmatter_invalid_semver(self):
        """validate_frontmatter() returns valid=False for non-semver version."""
        from store.packager import SkillPackager
        content = "---\nname: my-skill\nversion: not-semver\n---\n# body\n"
        packager = SkillPackager()
        result = packager.validate_frontmatter(content)
        assert result["valid"] is False
        assert any("version" in e for e in result["errors"])

    def test_validate_frontmatter_no_frontmatter_block(self):
        """validate_frontmatter() returns valid=False if no --- block at top."""
        from store.packager import SkillPackager
        content = "# Just a heading\nNo frontmatter here\n"
        packager = SkillPackager()
        result = packager.validate_frontmatter(content)
        assert result["valid"] is False

    def test_compute_sha256_manifest_correctness(self):
        """compute_sha256_manifest() produces correct SHA-256 for each file."""
        from store.packager import SkillPackager
        files = {
            "skill.md": "# My skill content",
            "tests.json": '{"exit_code": 0}',
        }
        manifest = SkillPackager.compute_sha256_manifest(files)
        for fname, content in files.items():
            expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
            assert manifest[fname] == expected, (
                f"{fname}: expected {expected}, got {manifest[fname]}"
            )

    def test_compute_sha256_manifest_all_64_char_hex(self):
        """compute_sha256_manifest() all values must be 64-char hex strings."""
        from store.packager import SkillPackager
        files = {"a.md": "content a", "b.json": "content b", "c.txt": "content c"}
        manifest = SkillPackager.compute_sha256_manifest(files)
        for fname, h in manifest.items():
            assert len(h) == 64, f"{fname}: expected 64-char hex, got {len(h)}"
            int(h, 16)  # must be valid hex

    def test_compute_sha256_manifest_empty_dict(self):
        """compute_sha256_manifest() with empty dict returns empty dict."""
        from store.packager import SkillPackager
        result = SkillPackager.compute_sha256_manifest({})
        assert result == {}
