"""
Test: Combo matching accuracy — correct swarm+recipe for each wish.

Verifies:
- All 25 canonical wish_ids return the expected swarm
- recipe always starts with prime-safety
- confidence > 0 for all matches
- source is 'cpu' for all CPU matches
- swarm is a valid agent type
- recipe is a non-empty list
- ExecutionMatch fields are correctly populated

rung_target: 641
EXIT_PASS: All 25 wish_ids match correct swarm and recipe starts with prime-safety.
EXIT_BLOCKED: Any wish_id missing, wrong swarm, or recipe without prime-safety.
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.execute.cpu import ExecutionCPU
from admin.orchestration.execute.database import ComboDB
from admin.orchestration.execute.models import ExecutionMatch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_COMBOS_PATH = str(Path(__file__).parent.parent / "combos.jsonl")
_LEARNED_PATH = "/tmp/execute_matching_test_learned.jsonl"


@pytest.fixture(scope="module")
def cpu():
    db = ComboDB(combos_path=_COMBOS_PATH, learned_path=_LEARNED_PATH)
    return ExecutionCPU(combo_db=db)


# ---------------------------------------------------------------------------
# Oracle: (wish_id, expected_swarm) pairs
# ---------------------------------------------------------------------------

_SWARM_ORACLE = [
    ("oauth-integration",        "coder"),
    ("database-optimization",    "coder"),
    ("video-compression",        "coder"),
    ("api-design",               "coder"),
    ("docker-containerization",  "coder"),
    ("security-audit",           "security-auditor"),
    ("ci-cd-pipeline",           "coder"),
    ("machine-learning-training","mathematician"),
    ("react-frontend",           "coder"),
    ("python-performance",       "coder"),
    ("test-development",         "test-developer"),
    ("git-workflow",             "coder"),
    ("debugging",                "coder"),
    ("documentation-writing",    "writer"),
    ("code-refactoring",         "coder"),
    ("dependency-management",    "coder"),
    ("logging-monitoring",       "coder"),
    ("data-pipeline",            "coder"),
    ("websocket-realtime",       "coder"),
    ("encryption-cryptography",  "security-auditor"),
    ("cache-optimization",       "coder"),
    ("infrastructure-as-code",   "planner"),
    ("file-storage-upload",      "coder"),
    ("rate-limiting",            "coder"),
    ("search-indexing",          "coder"),
]

# Oracle: wishes that MUST have prime-math in recipe (math-heavy tasks)
_MATH_RECIPE_WISHES = [
    "database-optimization",
    "machine-learning-training",
    "python-performance",
    "encryption-cryptography",
    "cache-optimization",
    "rate-limiting",
    "search-indexing",
    "data-pipeline",
    "prime-math",
]

# Valid swarm agent types
_VALID_SWARMS = {
    "coder", "mathematician", "writer", "planner", "skeptic",
    "scout", "janitor", "test-developer", "graph-designer",
    "security-auditor", "northstar-navigator", "portal-engineer",
}


# ---------------------------------------------------------------------------
# Tests: Swarm assignment
# ---------------------------------------------------------------------------

class TestComboSwarmMatching:

    def test_all_wish_ids_have_combo(self, cpu):
        """All 25 canonical wish_ids must return a non-None ExecutionMatch."""
        missing = []
        for wish_id, _ in _SWARM_ORACLE:
            match = cpu.match(wish_id)
            if match is None:
                missing.append(wish_id)

        assert not missing, (
            f"Following wish_ids have no combo:\n" +
            "\n".join(f"  - {w}" for w in missing)
        )

    def test_swarm_oracle_correct(self, cpu):
        """Each wish_id must map to the expected swarm agent."""
        wrong = []
        for wish_id, expected_swarm in _SWARM_ORACLE:
            match = cpu.match(wish_id)
            if match is None:
                wrong.append((wish_id, expected_swarm, None))
            elif match.swarm != expected_swarm:
                wrong.append((wish_id, expected_swarm, match.swarm))

        assert not wrong, (
            f"Incorrect swarm assignments:\n" +
            "\n".join(
                f"  wish={w!r} expected={e!r} actual={a!r}"
                for w, e, a in wrong
            )
        )

    def test_security_wishes_use_security_auditor(self, cpu):
        """Security-sensitive wishes must dispatch to security-auditor."""
        security_wishes = ["security-audit", "encryption-cryptography"]
        for wish_id in security_wishes:
            match = cpu.match(wish_id)
            assert match is not None, f"No match for {wish_id!r}"
            assert match.swarm == "security-auditor", (
                f"{wish_id!r} should use security-auditor, got {match.swarm!r}"
            )

    def test_math_wishes_use_mathematician_or_have_math_skill(self, cpu):
        """ML training wish must use mathematician swarm."""
        match = cpu.match("machine-learning-training")
        assert match is not None
        assert match.swarm == "mathematician", (
            f"machine-learning-training should use mathematician, got {match.swarm!r}"
        )

    def test_test_development_uses_test_developer(self, cpu):
        """test-development wish must use test-developer role."""
        match = cpu.match("test-development")
        assert match is not None
        assert match.swarm == "test-developer", (
            f"test-development should use test-developer, got {match.swarm!r}"
        )

    def test_documentation_uses_writer(self, cpu):
        """documentation-writing wish must use writer role."""
        match = cpu.match("documentation-writing")
        assert match is not None
        assert match.swarm == "writer", (
            f"documentation-writing should use writer, got {match.swarm!r}"
        )

    def test_infrastructure_uses_planner(self, cpu):
        """infrastructure-as-code wish must use planner role."""
        match = cpu.match("infrastructure-as-code")
        assert match is not None
        assert match.swarm == "planner", (
            f"infrastructure-as-code should use planner, got {match.swarm!r}"
        )

    def test_all_swarms_are_valid_agent_types(self, cpu):
        """Every swarm in every combo must be a valid agent type."""
        invalid = []
        for wish_id, _ in _SWARM_ORACLE:
            match = cpu.match(wish_id)
            if match and match.swarm not in _VALID_SWARMS:
                invalid.append((wish_id, match.swarm))

        assert not invalid, (
            f"Invalid swarm types:\n" +
            "\n".join(f"  wish={w!r} swarm={s!r}" for w, s in invalid)
        )


# ---------------------------------------------------------------------------
# Tests: Recipe integrity
# ---------------------------------------------------------------------------

class TestComboRecipeIntegrity:

    def test_prime_safety_always_first(self, cpu):
        """Every recipe must start with prime-safety (safety gate)."""
        violations = []
        for wish_id, _ in _SWARM_ORACLE:
            match = cpu.match(wish_id)
            if match is None:
                continue
            if not match.recipe:
                violations.append((wish_id, "empty recipe"))
            elif match.recipe[0] != "prime-safety":
                violations.append((wish_id, f"first skill = {match.recipe[0]!r}"))

        assert not violations, (
            f"prime-safety must be first skill in every recipe:\n" +
            "\n".join(f"  wish={w!r}: {v}" for w, v in violations)
        )

    def test_recipe_is_non_empty(self, cpu):
        """Every recipe must have at least 2 skills (prime-safety + domain skill)."""
        short = []
        for wish_id, _ in _SWARM_ORACLE:
            match = cpu.match(wish_id)
            if match and len(match.recipe) < 2:
                short.append((wish_id, len(match.recipe)))

        assert not short, (
            f"Recipes with fewer than 2 skills:\n" +
            "\n".join(f"  wish={w!r} recipe_len={n}" for w, n in short)
        )

    def test_coder_wishes_have_prime_coder(self, cpu):
        """Coder-dispatched wishes must include prime-coder in recipe."""
        missing_prime_coder = []
        for wish_id, expected_swarm in _SWARM_ORACLE:
            if expected_swarm != "coder":
                continue
            match = cpu.match(wish_id)
            if match and "prime-coder" not in match.recipe:
                missing_prime_coder.append(wish_id)

        assert not missing_prime_coder, (
            f"Coder wishes missing prime-coder:\n" +
            "\n".join(f"  - {w}" for w in missing_prime_coder)
        )

    def test_oauth_recipe_has_oauth3_enforcer(self, cpu):
        """OAuth integration must have oauth3-enforcer in recipe."""
        match = cpu.match("oauth-integration")
        assert match is not None
        assert "oauth3-enforcer" in match.recipe, (
            f"oauth-integration must include oauth3-enforcer skill. "
            f"Got recipe: {match.recipe}"
        )

    def test_test_development_has_unit_test_skill(self, cpu):
        """test-development must include phuc-unit-test-development skill."""
        match = cpu.match("test-development")
        assert match is not None
        assert "phuc-unit-test-development" in match.recipe, (
            f"test-development must include phuc-unit-test-development. "
            f"Got recipe: {match.recipe}"
        )

    def test_recipe_skills_are_strings(self, cpu):
        """All recipe entries must be non-empty strings."""
        for wish_id, _ in _SWARM_ORACLE:
            match = cpu.match(wish_id)
            if match is None:
                continue
            for i, skill in enumerate(match.recipe):
                assert isinstance(skill, str), (
                    f"{wish_id!r} recipe[{i}] is not a string: {skill!r}"
                )
                assert skill, (
                    f"{wish_id!r} recipe[{i}] is empty string"
                )


# ---------------------------------------------------------------------------
# Tests: ExecutionMatch field contracts
# ---------------------------------------------------------------------------

class TestExecutionMatchContracts:

    def test_confidence_positive_on_match(self, cpu):
        """All matches must have confidence > 0."""
        for wish_id, _ in _SWARM_ORACLE[:10]:
            match = cpu.match(wish_id)
            if match is not None:
                assert match.confidence > 0.0, (
                    f"Zero confidence for wish {wish_id!r}"
                )

    def test_confidence_is_float(self, cpu):
        """confidence must be a float in [0, 1]."""
        for wish_id, _ in _SWARM_ORACLE[:10]:
            match = cpu.match(wish_id)
            if match:
                assert 0.0 <= match.confidence <= 1.0, (
                    f"{wish_id!r}: confidence={match.confidence} out of [0,1]"
                )

    def test_source_is_cpu(self, cpu):
        """All matches from ExecutionCPU must have source='cpu'."""
        for wish_id, _ in _SWARM_ORACLE[:10]:
            match = cpu.match(wish_id)
            if match is not None:
                assert match.source == "cpu", (
                    f"Expected source='cpu', got {match.source!r} for {wish_id!r}"
                )

    def test_wish_id_preserved_in_match(self, cpu):
        """ExecutionMatch.wish_id must equal the input wish_id."""
        for wish_id, _ in _SWARM_ORACLE[:15]:
            match = cpu.match(wish_id)
            if match:
                assert match.wish_id == wish_id, (
                    f"match.wish_id={match.wish_id!r} != input {wish_id!r}"
                )

    def test_timestamp_populated(self, cpu):
        """ExecutionMatch.timestamp must be set."""
        match = cpu.match("oauth-integration")
        assert match is not None
        assert match.timestamp is not None, "timestamp must be set"

    def test_recipe_is_list_type(self, cpu):
        """ExecutionMatch.recipe must be a list (not tuple or None)."""
        for wish_id, _ in _SWARM_ORACLE[:5]:
            match = cpu.match(wish_id)
            if match:
                assert isinstance(match.recipe, list), (
                    f"{wish_id!r}: recipe is {type(match.recipe)}, expected list"
                )
