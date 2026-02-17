"""
Gamification System for Stillwater OS SWE-bench

Tracks XP, achievements, and agent performance across all benchmarks.
Used by Haiku Swarms (Scout, Solver, Skeptic) to:
  1. Track progress toward SWE-bench Phase 3 (40%+ target)
  2. Compete and collaborate via shared scoreboard
  3. Gain achievements for milestones (First Patch, 10 Patches, etc.)
  4. Level up roles (Initiate → Apprentice → Master)
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class Achievement:
    """Single achievement unlock."""
    id: str                           # e.g., "first_patch", "10_patches"
    name: str                         # e.g., "First Patch"
    description: str                  # e.g., "Generated first verified patch"
    xp_reward: int                    # XP gained
    requirement: str                  # e.g., "1 verified patch"
    unlocked: bool = False
    unlock_date: Optional[str] = None


@dataclass
class AgentStats:
    """Performance stats for a single Haiku agent."""
    name: str                         # "Scout", "Solver", "Skeptic"
    role_level: str = "Initiate"     # Initiate → Apprentice → Master
    total_xp: int = 0
    instances_attempted: int = 0
    instances_succeeded: int = 0
    patches_generated: int = 0
    patches_verified: int = 0
    tests_run: int = 0
    failures_caught: int = 0         # For Skeptic
    achievements: List[Achievement] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Percentage of successful instances."""
        if self.instances_attempted == 0:
            return 0.0
        return (self.instances_succeeded / self.instances_attempted) * 100

    @property
    def next_level_xp(self) -> int:
        """XP needed for next level."""
        levels = {
            "Initiate": 1000,
            "Apprentice": 3000,
            "Master": 10000,
        }
        return levels.get(self.role_level, 0)

    @property
    def xp_to_next(self) -> int:
        """XP remaining for next level."""
        return max(0, self.next_level_xp - self.total_xp)

    def level_up(self) -> bool:
        """Attempt to level up agent."""
        if self.total_xp >= self.next_level_xp:
            levels = ["Initiate", "Apprentice", "Master"]
            current_idx = levels.index(self.role_level)
            if current_idx < len(levels) - 1:
                self.role_level = levels[current_idx + 1]
                return True
        return False


@dataclass
class BenchmarkStats:
    """Statistics for each benchmark."""
    name: str                         # "OOLONG", "SWE Phase 2", "SWE Phase 3"
    target: float                     # 99.8%, 100%, 40%
    current: float = 0.0
    instances_total: int = 0
    instances_passed: int = 0
    xp_base: int = 0                  # Base XP for completion
    xp_milestone_50: int = 0          # XP at 50% completion
    xp_milestone_100: int = 0         # XP at 100% completion (bonus)


@dataclass
class Scoreboard:
    """Complete gamification scoreboard."""
    created_date: str
    last_updated: str

    # Benchmarks
    benchmarks: Dict[str, BenchmarkStats] = field(default_factory=dict)

    # Agents (Scout, Solver, Skeptic)
    agents: Dict[str, AgentStats] = field(default_factory=dict)

    # Global stats
    total_patches: int = 0
    total_xp_earned: int = 0
    current_phase: str = "Phase 3 (In Progress)"

    # Milestones
    milestones_achieved: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize default benchmarks and agents."""
        if not self.benchmarks:
            self._init_benchmarks()
        if not self.agents:
            self._init_agents()

    def _init_benchmarks(self):
        """Initialize all benchmarks."""
        self.benchmarks = {
            "OOLONG": BenchmarkStats(
                name="OOLONG",
                target=99.8,
                current=99.8,
                instances_total=1300,
                instances_passed=1300,
                xp_base=1500,
                xp_milestone_50=500,
                xp_milestone_100=500,
            ),
            "IMO 2024": BenchmarkStats(
                name="IMO 2024",
                target=6.0,
                current=6.0,
                instances_total=6,
                instances_passed=6,
                xp_base=2000,
                xp_milestone_50=750,
                xp_milestone_100=1000,
            ),
            "SWE Phase 2": BenchmarkStats(
                name="SWE Phase 2",
                target=100.0,
                current=100.0,
                instances_total=128,
                instances_passed=128,
                xp_base=1200,
                xp_milestone_50=400,
                xp_milestone_100=300,
            ),
            "SWE Phase 3": BenchmarkStats(
                name="SWE Phase 3",
                target=40.0,
                current=0.0,
                instances_total=300,
                instances_passed=0,
                xp_base=2000,
                xp_milestone_50=500,
                xp_milestone_100=1500,
            ),
        }

    def _init_agents(self):
        """Initialize all Haiku agents."""
        self.agents = {
            "Scout": AgentStats(
                name="Scout",
                role_level="Initiate",
                achievements=self._create_scout_achievements(),
            ),
            "Solver": AgentStats(
                name="Solver",
                role_level="Initiate",
                achievements=self._create_solver_achievements(),
            ),
            "Skeptic": AgentStats(
                name="Skeptic",
                role_level="Initiate",
                achievements=self._create_skeptic_achievements(),
            ),
        }

    def _create_scout_achievements(self) -> List[Achievement]:
        """Scout-specific achievements."""
        return [
            Achievement(
                id="first_analysis",
                name="🔍 First Analysis",
                description="Complete first codebase analysis",
                xp_reward=100,
                requirement="1 successful analysis",
            ),
            Achievement(
                id="ten_analyses",
                name="🔍 Detective",
                description="Complete 10 codebase analyses",
                xp_reward=300,
                requirement="10 successful analyses",
            ),
            Achievement(
                id="hundred_analyses",
                name="🔍 Master Detective",
                description="Complete 100 codebase analyses",
                xp_reward=1000,
                requirement="100 successful analyses",
            ),
            Achievement(
                id="root_cause_master",
                name="🎯 Root Cause Master",
                description="Find root cause in 95%+ of cases",
                xp_reward=500,
                requirement="95%+ success rate",
            ),
        ]

    def _create_solver_achievements(self) -> List[Achievement]:
        """Solver-specific achievements."""
        return [
            Achievement(
                id="first_patch",
                name="✨ First Patch",
                description="Generate first verified patch",
                xp_reward=150,
                requirement="1 verified patch",
            ),
            Achievement(
                id="ten_patches",
                name="✨ Patch Creator",
                description="Generate 10 verified patches",
                xp_reward=400,
                requirement="10 verified patches",
            ),
            Achievement(
                id="hundred_patches",
                name="✨ Patch Master",
                description="Generate 100 verified patches",
                xp_reward=2000,
                requirement="100 verified patches",
            ),
            Achievement(
                id="red_green_expert",
                name="🔴🟢 Red-Green Expert",
                description="100% RED→GREEN transition rate",
                xp_reward=500,
                requirement="Perfect RED→GREEN in 10+ patches",
            ),
        ]

    def _create_skeptic_achievements(self) -> List[Achievement]:
        """Skeptic-specific achievements."""
        return [
            Achievement(
                id="first_verification",
                name="✅ First Verification",
                description="Complete first verification run",
                xp_reward=100,
                requirement="1 verified patch",
            ),
            Achievement(
                id="ten_verifications",
                name="✅ Quality Assurance",
                description="Complete 10 verification runs",
                xp_reward=300,
                requirement="10 verifications",
            ),
            Achievement(
                id="zero_regressions",
                name="🛡️ Zero Regressions",
                description="Verify 50 patches with zero regressions",
                xp_reward=800,
                requirement="50 patches, 0 regressions",
            ),
            Achievement(
                id="ladder_complete",
                name="🪜 Verification Ladder Master",
                description="Pass all 3 rungs (641→274177→65537)",
                xp_reward=1000,
                requirement="100% ladder completion on 10+ patches",
            ),
        ]

    def add_xp(self, agent: str, amount: int, reason: str = ""):
        """Add XP to agent and check for level ups."""
        if agent not in self.agents:
            return

        self.agents[agent].total_xp += amount
        self.total_xp_earned += amount

        # Check for level up
        if self.agents[agent].level_up():
            print(f"🎉 {agent} leveled up to {self.agents[agent].role_level}!")

    def record_instance(self, agent: str, success: bool, xp: int = 0):
        """Record instance attempt for agent."""
        if agent not in self.agents:
            return

        self.agents[agent].instances_attempted += 1
        if success:
            self.agents[agent].instances_succeeded += 1
            self.add_xp(agent, xp, f"Success on instance")

    def record_patch(self, agent: str, verified: bool = False):
        """Record patch generation."""
        if agent not in self.agents:
            return

        self.agents[agent].patches_generated += 1
        self.total_patches += 1

        if verified:
            self.agents[agent].patches_verified += 1
            self.add_xp(agent, 150, "Patch verified")

    def record_test_run(self, agent: str, passed: int = 0, failed: int = 0):
        """Record test execution."""
        if agent not in self.agents:
            return

        self.agents[agent].tests_run += passed + failed
        if failed > 0 and agent == "Skeptic":
            self.agents[agent].failures_caught += failed

    def update_benchmark(self, benchmark_name: str, instances: int, passed: int):
        """Update benchmark progress."""
        if benchmark_name not in self.benchmarks:
            return

        bench = self.benchmarks[benchmark_name]
        bench.instances_total = instances
        bench.instances_passed = passed
        bench.current = (passed / instances * 100) if instances > 0 else 0.0

        # Award XP for milestones
        if bench.current >= 50.0 and f"{benchmark_name}_50" not in self.milestones_achieved:
            self._award_milestone_xp(benchmark_name, 50)

        if bench.current >= 100.0 and f"{benchmark_name}_100" not in self.milestones_achieved:
            self._award_milestone_xp(benchmark_name, 100)

    def _award_milestone_xp(self, benchmark_name: str, percent: int):
        """Award XP for reaching milestone."""
        bench = self.benchmarks[benchmark_name]
        milestone_key = f"{benchmark_name}_{percent}"

        if percent == 50:
            xp = bench.xp_milestone_50
        else:
            xp = bench.xp_milestone_100

        self.milestones_achieved.append(milestone_key)

        # Distribute XP to all agents
        per_agent = xp // 3
        for agent in self.agents.keys():
            self.add_xp(agent, per_agent, f"{benchmark_name} {percent}% milestone")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "benchmarks": {k: asdict(v) for k, v in self.benchmarks.items()},
            "agents": {k: asdict(v) for k, v in self.agents.items()},
            "total_patches": self.total_patches,
            "total_xp_earned": self.total_xp_earned,
            "current_phase": self.current_phase,
            "milestones_achieved": self.milestones_achieved,
        }

    def save(self, path: Path):
        """Save scoreboard to JSON."""
        self.last_updated = datetime.now().isoformat()
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @staticmethod
    def load(path: Path) -> "Scoreboard":
        """Load scoreboard from JSON."""
        data = json.loads(path.read_text())
        board = Scoreboard(
            created_date=data["created_date"],
            last_updated=data["last_updated"],
        )
        # Reconstruct from dict
        board.total_patches = data["total_patches"]
        board.total_xp_earned = data["total_xp_earned"]
        board.current_phase = data["current_phase"]
        board.milestones_achieved = data["milestones_achieved"]
        return board


def create_scoreboard() -> Scoreboard:
    """Create a new scoreboard."""
    return Scoreboard(
        created_date=datetime.now().isoformat(),
        last_updated=datetime.now().isoformat(),
    )


def print_scoreboard(board: Scoreboard) -> str:
    """Pretty-print scoreboard for display."""
    lines = []

    lines.append("=" * 80)
    lines.append("🏆 STILLWATER OS - SWE-BENCH GAMIFICATION SCOREBOARD")
    lines.append("=" * 80)

    # Global stats
    lines.append(f"\n📊 GLOBAL STATS")
    lines.append(f"  Total Patches Generated: {board.total_patches}")
    lines.append(f"  Total XP Earned: {board.total_xp_earned}")
    lines.append(f"  Current Phase: {board.current_phase}")

    # Benchmarks
    lines.append(f"\n📈 BENCHMARKS")
    for name, bench in board.benchmarks.items():
        pct = bench.current
        bar_length = 30
        filled = int(bar_length * pct / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        lines.append(f"  {name:20s} [{bar}] {pct:6.1f}% ({bench.instances_passed}/{bench.instances_total})")

    # Agent Stats
    lines.append(f"\n👥 HAIKU AGENTS")
    for agent_name, agent in board.agents.items():
        xp_bar_length = 20
        xp_pct = min(100, (agent.total_xp / agent.next_level_xp * 100) if agent.next_level_xp > 0 else 100)
        xp_filled = int(xp_bar_length * xp_pct / 100)
        xp_bar = "▓" * xp_filled + "░" * (xp_bar_length - xp_filled)

        lines.append(f"\n  {agent_name} (Role: {agent.role_level})")
        lines.append(f"    XP: {agent.total_xp:,} [{xp_bar}] {int(xp_pct)}%")
        lines.append(f"    Success Rate: {agent.success_rate:.1f}% ({agent.instances_succeeded}/{agent.instances_attempted})")

        if agent_name == "Solver":
            lines.append(f"    Patches Generated: {agent.patches_generated}")
            lines.append(f"    Patches Verified: {agent.patches_verified}")
        elif agent_name == "Skeptic":
            lines.append(f"    Tests Run: {agent.tests_run}")
            lines.append(f"    Failures Caught: {agent.failures_caught}")

        # Achievements
        unlocked = [a for a in agent.achievements if a.unlocked]
        if unlocked:
            lines.append(f"    Achievements: {len(unlocked)}/{len(agent.achievements)}")
            for achievement in unlocked:
                lines.append(f"      ✓ {achievement.name} ({achievement.xp_reward} XP)")

    lines.append("\n" + "=" * 80)

    return "\n".join(lines)
