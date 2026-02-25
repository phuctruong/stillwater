"""cascade.py — Resolves wish → combo → execution plan.

Convention-over-configuration: combo_id = "{wish_id}-combo".
No mapping file needed. The naming convention IS the mapping.

Uses DataRegistry for all file I/O. stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Import parse_frontmatter from triple_twin
from stillwater.triple_twin import parse_frontmatter


@dataclass
class WishEntry:
    """A wish from wishes.md."""
    wish_id: str
    description: str
    name: str = ""
    category: str = ""
    swarm: str = ""
    skill_pack: str = ""
    confidence: float = 0.0


@dataclass
class ComboEntry:
    """A combo from combos/*.md."""
    combo_id: str
    wish: str
    agents: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    rung_target: int = 641
    model_tier: str = "sonnet"
    description: str = ""


@dataclass
class ExecutionPlan:
    """The result of resolving a wish through the cascade."""
    wish: Optional[WishEntry] = None
    combo: Optional[ComboEntry] = None
    agents: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    rung_target: int = 641
    model_tier: str = "sonnet"
    error: Optional[str] = None


class CascadeResolver:
    """Resolves wish → combo → execution plan via DataRegistry convention.

    Convention: combo_id = "{wish_id}-combo" (Rails-style naming).
    """

    def __init__(self, registry: Any):
        self.registry = registry
        self._wishes: Dict[str, WishEntry] = {}
        self._combos: Dict[str, ComboEntry] = {}
        self._discover()

    def _discover(self):
        """Discover wishes and combos from DataRegistry."""
        self._load_wishes()
        self._load_combos()

    def _load_wishes(self):
        """Parse wishes.md — extract wish IDs from the markdown table.

        Expected format (columns separated by ``|``):

            | wish_id | name | category | swarm | skill_pack_hint | confidence |
            |---------|------|----------|-------|-----------------|------------|
            | oauth-integration | OAuth Integration | security | coder | coder+security | 0.92 |

        The header row and separator row (containing ``---``) are skipped.
        """
        content = self.registry.load_data_file("wishes.md")
        if not content:
            return

        in_table = False
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # Detect table rows: must start and end with |
            if not stripped.startswith("|"):
                # If we were already in a table and hit a non-table line, stop
                if in_table:
                    break
                continue

            # Split on | and trim whitespace from each cell
            cells = [c.strip() for c in stripped.split("|")]
            # Leading/trailing split produces empty strings at edges
            # e.g. "| a | b |" → ["", "a", "b", ""]
            cells = [c for c in cells if c != ""]

            if not cells:
                continue

            # Skip separator row (e.g. "|---------|------|")
            if all(set(c) <= set("-: ") for c in cells):
                in_table = True
                continue

            # Skip header row: the first non-separator row with "wish_id" as first cell
            if cells[0].lower() == "wish_id":
                in_table = True
                continue

            if not in_table:
                # We haven't passed the header/separator yet
                # Check if this looks like a data row anyway
                # (for tables without explicit separator detection)
                in_table = True

            # Parse data row — expect at least wish_id and name
            if len(cells) < 2:
                continue

            wish_id = cells[0]
            name = cells[1] if len(cells) > 1 else ""
            category = cells[2] if len(cells) > 2 else ""
            swarm = cells[3] if len(cells) > 3 else ""
            skill_pack = cells[4] if len(cells) > 4 else ""

            # Parse confidence (float)
            confidence = 0.0
            if len(cells) > 5:
                try:
                    confidence = float(cells[5])
                except (ValueError, TypeError):
                    pass

            self._wishes[wish_id] = WishEntry(
                wish_id=wish_id,
                description=name,
                name=name,
                category=category,
                swarm=swarm,
                skill_pack=skill_pack,
                confidence=confidence,
            )

    def _load_combos(self):
        """Discover combos from combos/*.md using YAML frontmatter."""
        all_data = self.registry.load_all_data()
        for rel_path, content in sorted(all_data.items()):
            if not rel_path.startswith("combos/") or not rel_path.endswith(".md"):
                continue
            try:
                config = parse_frontmatter(content)
            except Exception:
                continue
            combo_id = config.get("id", "")
            if not combo_id:
                continue
            self._combos[combo_id] = ComboEntry(
                combo_id=combo_id,
                wish=config.get("wish", ""),
                agents=config.get("agents", []),
                skills=config.get("skills", []),
                rung_target=config.get("rung_target", 641),
                model_tier=config.get("model_tier", "sonnet"),
                description=config.get("description", ""),
            )

    def resolve(self, wish_id: str) -> ExecutionPlan:
        """Resolve a wish to an execution plan.

        Convention: combo_id = "{wish_id}-combo"
        """
        # 1. Look up wish
        wish = self._wishes.get(wish_id)

        # 2. Look up combo by convention
        combo_id = f"{wish_id}-combo"
        combo = self._combos.get(combo_id)

        if combo is None:
            # Fallback: return a default plan with error
            return ExecutionPlan(
                wish=wish,
                error=f"No combo found for wish '{wish_id}' (expected combos/{combo_id}.md)",
                agents=["support"],
                skills=["prime-safety"],
                rung_target=641,
                model_tier="haiku",
            )

        return ExecutionPlan(
            wish=wish,
            combo=combo,
            agents=combo.agents,
            skills=combo.skills,
            rung_target=combo.rung_target,
            model_tier=combo.model_tier,
        )

    def list_wishes(self) -> list:
        """Return all known wish IDs."""
        return sorted(self._wishes.keys())

    def list_combos(self) -> list:
        """Return all known combo IDs."""
        return sorted(self._combos.keys())

    def stats(self) -> dict:
        """Return cascade statistics."""
        matched = 0
        for wish_id in self._wishes:
            combo_id = f"{wish_id}-combo"
            if combo_id in self._combos:
                matched += 1

        return {
            "total_wishes": len(self._wishes),
            "total_combos": len(self._combos),
            "matched_pairs": matched,
            "wishes": self.list_wishes(),
            "combos": self.list_combos(),
        }
