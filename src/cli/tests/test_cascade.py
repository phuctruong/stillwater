"""Tests for stillwater.cascade.CascadeResolver.

Coverage targets:
  1. Combo discovery (~10 tests)
  2. Wish parsing (~8 tests)
  3. Resolution (~12 tests)
  4. Listing + stats (~5 tests)

Rung: 641 — deterministic, no network, testable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest

from stillwater.cascade import CascadeResolver, ComboEntry, ExecutionPlan, WishEntry
from stillwater.data_registry import DataRegistry


# ===========================================================================
# Helpers
# ===========================================================================


def _setup_data_dirs(tmp_path: Path) -> Path:
    """Create data/default/ and data/custom/ under tmp_path. Return tmp_path."""
    (tmp_path / "data" / "default").mkdir(parents=True)
    (tmp_path / "data" / "custom").mkdir(parents=True)
    return tmp_path


def _write_default(tmp_path: Path, relative_path: str, content: str) -> None:
    """Write a file to data/default/ under tmp_path."""
    target = tmp_path / "data" / "default" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _write_custom(tmp_path: Path, relative_path: str, content: str) -> None:
    """Write a file to data/custom/ under tmp_path."""
    target = tmp_path / "data" / "custom" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _make_combo_md(
    combo_id: str,
    wish: str,
    agents: Optional[list] = None,
    skills: Optional[list] = None,
    rung_target: int = 641,
    model_tier: str = "sonnet",
    description: str = "",
) -> str:
    """Generate a combo .md file with YAML frontmatter."""
    if agents is None:
        agents = ["coder"]
    if skills is None:
        skills = ["prime-safety", "prime-coder"]
    agents_str = ", ".join(agents)
    skills_str = ", ".join(skills)
    return (
        f"---\n"
        f"id: {combo_id}\n"
        f"type: combo\n"
        f"wish: {wish}\n"
        f"agents: [{agents_str}]\n"
        f"skills: [{skills_str}]\n"
        f"rung_target: {rung_target}\n"
        f"model_tier: {model_tier}\n"
        f'description: "{description}"\n'
        f"---\n\n"
        f"# {combo_id}\n\nCombo description.\n"
    )


def _make_wishes_md(rows: Optional[list] = None) -> str:
    """Generate a wishes.md file with a markdown table.

    Each row in *rows* is a tuple:
        (wish_id, name, category, swarm, skill_pack_hint, confidence)
    """
    if rows is None:
        rows = [
            ("bugfix", "Bug Fixing", "quality", "coder", "coder", "0.90"),
            ("feature", "New Feature", "development", "coder", "coder", "0.88"),
            ("deploy", "Deployment", "devops", "coder", "coder+devops", "0.91"),
        ]
    header = "| wish_id | name | category | swarm | skill_pack_hint | confidence |"
    separator = "|---------|------|----------|-------|-----------------|------------|"
    data_lines = []
    for row in rows:
        data_lines.append("| " + " | ".join(row) + " |")

    lines = [
        "---",
        "id: wishes-test-v1",
        "format: mermaid-statechart",
        "---",
        "",
        "## Wish Catalog",
        "",
        header,
        separator,
    ] + data_lines

    return "\n".join(lines) + "\n"


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    """Create a minimal repo-root layout with wishes + combos."""
    root = _setup_data_dirs(tmp_path)
    _write_default(root, "wishes.md", _make_wishes_md())
    _write_default(root, "combos/bugfix-combo.md", _make_combo_md(
        "bugfix-combo", "bugfix", ["coder", "skeptic"],
        ["prime-safety", "prime-coder"], 641, "sonnet",
        "Systematic bug fixing with red/green test gate",
    ))
    _write_default(root, "combos/feature-combo.md", _make_combo_md(
        "feature-combo", "feature", ["coder"],
        ["prime-safety", "prime-coder"], 641, "sonnet",
        "New feature development with test coverage",
    ))
    _write_default(root, "combos/deploy-combo.md", _make_combo_md(
        "deploy-combo", "deploy", ["coder"],
        ["prime-safety", "prime-coder", "devops"], 641, "sonnet",
        "Deployment with rollback plan",
    ))
    return root


@pytest.fixture()
def resolver(repo_root: Path) -> CascadeResolver:
    """Return a CascadeResolver with wishes + 3 combos."""
    reg = DataRegistry(repo_root=repo_root)
    return CascadeResolver(registry=reg)


# ===========================================================================
# 1. Combo discovery (~10 tests)
# ===========================================================================


class TestComboDiscovery:
    """Tests for combo discovery from combos/*.md."""

    def test_discovers_combos_from_default(self, resolver: CascadeResolver) -> None:
        """Combos in data/default/combos/ are discovered."""
        assert "bugfix-combo" in resolver._combos
        assert "feature-combo" in resolver._combos
        assert "deploy-combo" in resolver._combos

    def test_combo_count(self, resolver: CascadeResolver) -> None:
        """Exactly 3 combos from the fixture."""
        assert len(resolver._combos) == 3

    def test_combo_agents_parsed(self, resolver: CascadeResolver) -> None:
        """Combo agents list is correctly parsed from frontmatter."""
        combo = resolver._combos["bugfix-combo"]
        assert combo.agents == ["coder", "skeptic"]

    def test_combo_skills_parsed(self, resolver: CascadeResolver) -> None:
        """Combo skills list is correctly parsed."""
        combo = resolver._combos["bugfix-combo"]
        assert combo.skills == ["prime-safety", "prime-coder"]

    def test_combo_rung_target_parsed(self, resolver: CascadeResolver) -> None:
        """Combo rung_target is an integer from frontmatter."""
        combo = resolver._combos["bugfix-combo"]
        assert combo.rung_target == 641
        assert isinstance(combo.rung_target, int)

    def test_combo_model_tier_parsed(self, resolver: CascadeResolver) -> None:
        """Combo model_tier is a string from frontmatter."""
        combo = resolver._combos["bugfix-combo"]
        assert combo.model_tier == "sonnet"

    def test_combo_description_parsed(self, resolver: CascadeResolver) -> None:
        """Combo description is parsed from frontmatter."""
        combo = resolver._combos["bugfix-combo"]
        assert "bug fixing" in combo.description.lower()

    def test_custom_combo_overrides_default(self, tmp_path: Path) -> None:
        """Custom combo wins over default for same combo ID."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "wishes.md", _make_wishes_md())
        _write_default(root, "combos/bugfix-combo.md", _make_combo_md(
            "bugfix-combo", "bugfix", ["coder"], ["prime-safety"], 641, "sonnet",
            "Default bugfix",
        ))
        _write_custom(root, "combos/bugfix-combo.md", _make_combo_md(
            "bugfix-combo", "bugfix", ["coder", "skeptic", "auditor"],
            ["prime-safety", "prime-coder", "security"], 65537, "opus",
            "Custom bugfix with extra agents",
        ))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        combo = resolver._combos["bugfix-combo"]
        assert combo.agents == ["coder", "skeptic", "auditor"]
        assert combo.rung_target == 65537
        assert combo.model_tier == "opus"

    def test_missing_combos_dir_gives_empty(self, tmp_path: Path) -> None:
        """No combos/ directory → empty combos dict."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "wishes.md", _make_wishes_md())
        # No combos/ directory created

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert resolver._combos == {}

    def test_invalid_md_file_skipped(self, tmp_path: Path) -> None:
        """Combo .md with no valid frontmatter is skipped."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "wishes.md", _make_wishes_md())
        _write_default(root, "combos/bad.md", "# No frontmatter\nJust content.\n")
        _write_default(root, "combos/bugfix-combo.md", _make_combo_md(
            "bugfix-combo", "bugfix",
        ))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        # bad.md skipped, bugfix-combo.md loaded
        assert len(resolver._combos) == 1
        assert "bugfix-combo" in resolver._combos

    def test_combo_without_id_skipped(self, tmp_path: Path) -> None:
        """Combo .md with frontmatter but no 'id' field is skipped."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "wishes.md", _make_wishes_md())
        _write_default(root, "combos/no-id.md", (
            "---\n"
            "type: combo\n"
            "wish: bugfix\n"
            "agents: [coder]\n"
            "---\n\n"
            "# Missing ID combo\n"
        ))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert len(resolver._combos) == 0

    def test_non_md_files_in_combos_ignored(self, tmp_path: Path) -> None:
        """Non-.md files in combos/ directory are ignored."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "wishes.md", _make_wishes_md())
        _write_default(root, "combos/readme.txt", "Not a combo")
        _write_default(root, "combos/data.json", '{"not": "a combo"}')

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert resolver._combos == {}


# ===========================================================================
# 2. Wish parsing (~8 tests)
# ===========================================================================


class TestWishParsing:
    """Tests for parsing wishes.md table."""

    def test_parses_wishes_from_table(self, resolver: CascadeResolver) -> None:
        """Wishes are parsed from the markdown table in wishes.md."""
        assert "bugfix" in resolver._wishes
        assert "feature" in resolver._wishes
        assert "deploy" in resolver._wishes

    def test_wish_count(self, resolver: CascadeResolver) -> None:
        """Correct number of wishes parsed."""
        assert len(resolver._wishes) == 3

    def test_wish_name_parsed(self, resolver: CascadeResolver) -> None:
        """Wish name (description) is correctly parsed."""
        wish = resolver._wishes["bugfix"]
        assert wish.name == "Bug Fixing"

    def test_wish_category_parsed(self, resolver: CascadeResolver) -> None:
        """Wish category is correctly parsed."""
        wish = resolver._wishes["bugfix"]
        assert wish.category == "quality"

    def test_wish_swarm_parsed(self, resolver: CascadeResolver) -> None:
        """Wish swarm is correctly parsed."""
        wish = resolver._wishes["deploy"]
        assert wish.swarm == "coder"

    def test_wish_skill_pack_parsed(self, resolver: CascadeResolver) -> None:
        """Wish skill_pack is correctly parsed."""
        wish = resolver._wishes["deploy"]
        assert wish.skill_pack == "coder+devops"

    def test_wish_confidence_parsed(self, resolver: CascadeResolver) -> None:
        """Wish confidence is a float from the table."""
        wish = resolver._wishes["bugfix"]
        assert wish.confidence == 0.90
        assert isinstance(wish.confidence, float)

    def test_missing_wishes_md_graceful(self, tmp_path: Path) -> None:
        """Missing wishes.md → empty wishes dict, no crash."""
        root = _setup_data_dirs(tmp_path)
        # No wishes.md written

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert resolver._wishes == {}

    def test_empty_wishes_table(self, tmp_path: Path) -> None:
        """wishes.md with header but no data rows → empty wishes."""
        root = _setup_data_dirs(tmp_path)
        content = (
            "---\nid: wishes-test\n---\n\n"
            "## Wish Catalog\n\n"
            "| wish_id | name | category | swarm | skill_pack_hint | confidence |\n"
            "|---------|------|----------|-------|-----------------|------------|\n"
        )
        _write_default(root, "wishes.md", content)

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert resolver._wishes == {}

    def test_wishes_with_extra_columns(self, tmp_path: Path) -> None:
        """Table rows with extra columns are parsed without error."""
        root = _setup_data_dirs(tmp_path)
        rows = [
            ("test-wish", "Test", "quality", "coder", "coder", "0.85"),
        ]
        _write_default(root, "wishes.md", _make_wishes_md(rows))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert "test-wish" in resolver._wishes

    def test_wishes_with_minimal_columns(self, tmp_path: Path) -> None:
        """Table rows with only wish_id and name still parse."""
        root = _setup_data_dirs(tmp_path)
        content = (
            "---\nid: wishes-test\n---\n\n"
            "## Wish Catalog\n\n"
            "| wish_id | name |\n"
            "|---------|------|\n"
            "| minimal-wish | Minimal Wish |\n"
        )
        _write_default(root, "wishes.md", content)

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert "minimal-wish" in resolver._wishes
        wish = resolver._wishes["minimal-wish"]
        assert wish.name == "Minimal Wish"
        assert wish.category == ""
        assert wish.confidence == 0.0

    def test_wishes_invalid_confidence_defaults_zero(self, tmp_path: Path) -> None:
        """Non-numeric confidence column defaults to 0.0."""
        root = _setup_data_dirs(tmp_path)
        rows = [
            ("bad-conf", "Bad Confidence", "quality", "coder", "coder", "not-a-number"),
        ]
        _write_default(root, "wishes.md", _make_wishes_md(rows))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        assert resolver._wishes["bad-conf"].confidence == 0.0


# ===========================================================================
# 3. Resolution (~12 tests)
# ===========================================================================


class TestResolution:
    """Tests for resolve() — wish → combo → execution plan."""

    def test_resolve_bugfix(self, resolver: CascadeResolver) -> None:
        """resolve('bugfix') → bugfix-combo with correct agents/skills."""
        plan = resolver.resolve("bugfix")
        assert plan.wish is not None
        assert plan.wish.wish_id == "bugfix"
        assert plan.combo is not None
        assert plan.combo.combo_id == "bugfix-combo"
        assert plan.agents == ["coder", "skeptic"]
        assert plan.skills == ["prime-safety", "prime-coder"]

    def test_resolve_feature(self, resolver: CascadeResolver) -> None:
        """resolve('feature') → feature-combo."""
        plan = resolver.resolve("feature")
        assert plan.combo is not None
        assert plan.combo.combo_id == "feature-combo"
        assert plan.agents == ["coder"]

    def test_resolve_deploy(self, resolver: CascadeResolver) -> None:
        """resolve('deploy') → deploy-combo."""
        plan = resolver.resolve("deploy")
        assert plan.combo is not None
        assert plan.combo.combo_id == "deploy-combo"
        assert "devops" in plan.skills

    def test_resolve_unknown_returns_error(self, resolver: CascadeResolver) -> None:
        """resolve('unknown') → error with fallback defaults."""
        plan = resolver.resolve("unknown")
        assert plan.error is not None
        assert "No combo found" in plan.error
        assert "unknown-combo" in plan.error
        assert plan.combo is None
        assert plan.agents == ["support"]
        assert plan.skills == ["prime-safety"]
        assert plan.model_tier == "haiku"
        assert plan.rung_target == 641

    def test_resolve_unknown_wish_still_has_none_wish(self, resolver: CascadeResolver) -> None:
        """Wish that doesn't exist in wishes.md → wish is None."""
        plan = resolver.resolve("nonexistent-wish")
        assert plan.wish is None
        assert plan.error is not None

    def test_resolve_convention_combo_id(self, resolver: CascadeResolver) -> None:
        """Convention: combo_id = '{wish_id}-combo'."""
        plan = resolver.resolve("bugfix")
        assert plan.combo.combo_id == "bugfix-combo"

    def test_resolve_propagates_rung_target(self, resolver: CascadeResolver) -> None:
        """ExecutionPlan.rung_target comes from the combo."""
        plan = resolver.resolve("bugfix")
        assert plan.rung_target == 641

    def test_resolve_propagates_model_tier(self, resolver: CascadeResolver) -> None:
        """ExecutionPlan.model_tier comes from the combo."""
        plan = resolver.resolve("bugfix")
        assert plan.model_tier == "sonnet"

    def test_resolve_returns_execution_plan(self, resolver: CascadeResolver) -> None:
        """resolve() always returns an ExecutionPlan instance."""
        assert isinstance(resolver.resolve("bugfix"), ExecutionPlan)
        assert isinstance(resolver.resolve("unknown"), ExecutionPlan)

    def test_resolve_no_error_on_success(self, resolver: CascadeResolver) -> None:
        """Successful resolution has error=None."""
        plan = resolver.resolve("bugfix")
        assert plan.error is None

    def test_resolve_wish_with_combo_but_no_wish_entry(self, tmp_path: Path) -> None:
        """Combo exists for a wish_id, but wish_id not in wishes.md → wish=None, combo=present."""
        root = _setup_data_dirs(tmp_path)
        # Empty wishes
        _write_default(root, "wishes.md", _make_wishes_md([]))
        _write_default(root, "combos/orphan-combo.md", _make_combo_md(
            "orphan-combo", "orphan",
        ))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        plan = resolver.resolve("orphan")
        assert plan.wish is None
        assert plan.combo is not None
        assert plan.combo.combo_id == "orphan-combo"
        assert plan.error is None

    def test_resolve_high_rung_combo(self, tmp_path: Path) -> None:
        """Security combo with rung_target 65537 propagates correctly."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "wishes.md", _make_wishes_md([
            ("security", "Security Audit", "security", "security-auditor", "coder+security", "0.93"),
        ]))
        _write_default(root, "combos/security-combo.md", _make_combo_md(
            "security-combo", "security", ["security-auditor"],
            ["prime-safety", "security"], 65537, "opus",
            "Security audit with vulnerability scanning",
        ))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        plan = resolver.resolve("security")
        assert plan.rung_target == 65537
        assert plan.model_tier == "opus"
        assert plan.agents == ["security-auditor"]

    def test_resolve_all_standard_combos(self, tmp_path: Path) -> None:
        """All 15 standard combos from the real data resolve correctly."""
        standard_combos = [
            "bugfix", "feature", "deploy", "test", "security",
            "perf", "docs", "refactor", "plan", "debug",
            "review", "research", "support", "design", "audit",
        ]
        root = _setup_data_dirs(tmp_path)
        wish_rows = [(c, c.title(), "cat", "coder", "coder", "0.90") for c in standard_combos]
        _write_default(root, "wishes.md", _make_wishes_md(wish_rows))
        for c in standard_combos:
            _write_default(root, f"combos/{c}-combo.md", _make_combo_md(
                f"{c}-combo", c,
            ))

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        for c in standard_combos:
            plan = resolver.resolve(c)
            assert plan.combo is not None, f"No combo found for wish '{c}'"
            assert plan.combo.combo_id == f"{c}-combo"
            assert plan.error is None


# ===========================================================================
# 4. Listing + stats (~5 tests)
# ===========================================================================


class TestListingAndStats:
    """Tests for list_wishes(), list_combos(), stats()."""

    def test_list_wishes_returns_sorted(self, resolver: CascadeResolver) -> None:
        """list_wishes() returns a sorted list of wish IDs."""
        wishes = resolver.list_wishes()
        assert wishes == sorted(wishes)
        assert "bugfix" in wishes
        assert "feature" in wishes
        assert "deploy" in wishes

    def test_list_combos_returns_sorted(self, resolver: CascadeResolver) -> None:
        """list_combos() returns a sorted list of combo IDs."""
        combos = resolver.list_combos()
        assert combos == sorted(combos)
        assert "bugfix-combo" in combos
        assert "feature-combo" in combos
        assert "deploy-combo" in combos

    def test_stats_total_wishes(self, resolver: CascadeResolver) -> None:
        """stats() reports correct total_wishes."""
        stats = resolver.stats()
        assert stats["total_wishes"] == 3

    def test_stats_total_combos(self, resolver: CascadeResolver) -> None:
        """stats() reports correct total_combos."""
        stats = resolver.stats()
        assert stats["total_combos"] == 3

    def test_stats_matched_pairs(self, resolver: CascadeResolver) -> None:
        """stats() reports correct matched_pairs count."""
        stats = resolver.stats()
        assert stats["matched_pairs"] == 3

    def test_stats_lists_match(self, resolver: CascadeResolver) -> None:
        """stats() wishes/combos lists match list_wishes()/list_combos()."""
        stats = resolver.stats()
        assert stats["wishes"] == resolver.list_wishes()
        assert stats["combos"] == resolver.list_combos()

    def test_empty_registry_stats(self, tmp_path: Path) -> None:
        """Empty registry → all counts zero."""
        root = _setup_data_dirs(tmp_path)

        reg = DataRegistry(repo_root=root)
        resolver = CascadeResolver(registry=reg)

        stats = resolver.stats()
        assert stats["total_wishes"] == 0
        assert stats["total_combos"] == 0
        assert stats["matched_pairs"] == 0
        assert stats["wishes"] == []
        assert stats["combos"] == []


# ===========================================================================
# 5. Integration: real data/default/ files (~5 tests)
# ===========================================================================


class TestIntegrationRealData:
    """Smoke tests against the real data/default/ directory."""

    def test_real_wishes_load(self) -> None:
        """Real wishes.md loads and has at least 20 entries."""
        reg = DataRegistry()
        resolver = CascadeResolver(registry=reg)
        assert len(resolver._wishes) >= 20

    def test_real_combos_load(self) -> None:
        """Real combos/ load and have at least 10 entries."""
        reg = DataRegistry()
        resolver = CascadeResolver(registry=reg)
        assert len(resolver._combos) >= 10

    def test_real_bugfix_resolves(self) -> None:
        """bugfix-combo resolves from real data."""
        reg = DataRegistry()
        resolver = CascadeResolver(registry=reg)
        plan = resolver.resolve("bugfix")
        assert plan.combo is not None
        assert plan.combo.combo_id == "bugfix-combo"
        assert "coder" in plan.agents
        assert plan.error is None

    def test_real_security_resolves(self) -> None:
        """security-combo resolves from real data with opus tier."""
        reg = DataRegistry()
        resolver = CascadeResolver(registry=reg)
        plan = resolver.resolve("security")
        assert plan.combo is not None
        assert plan.combo.combo_id == "security-combo"
        assert plan.rung_target == 65537
        assert plan.model_tier == "opus"

    def test_real_stats_consistency(self) -> None:
        """stats() counts are consistent with list lengths."""
        reg = DataRegistry()
        resolver = CascadeResolver(registry=reg)
        stats = resolver.stats()
        assert stats["total_wishes"] == len(resolver.list_wishes())
        assert stats["total_combos"] == len(resolver.list_combos())
        assert stats["matched_pairs"] <= min(stats["total_wishes"], stats["total_combos"])
