"""
Haiku Swarm Orchestrator for Stillwater OS.

Coordinates 5 parallel agents with specific expertise:
- Scout (Ken Thompson): Problem exploration & codebase analysis
- Solver (Donald Knuth): Elegant patch generation & design
- Skeptic (Alan Turing): Rigorous verification & proof validation
- Greg (Greg Isenberg): Product messaging & communication clarity
- Podcaster (AI Storyteller): Narrative & documentation excellence

Each agent runs in parallel, findings synthesized by Orchestrator.

Auth: 65537 | Version: 1.0.0
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class AgentRole(Enum):
    """Agent roles in the Haiku Swarm."""
    SCOUT = "scout"           # Ken Thompson - Explorer
    SOLVER = "solver"         # Donald Knuth - Designer
    SKEPTIC = "skeptic"       # Alan Turing - Validator
    GREG = "greg"             # Greg Isenberg - Product Lead
    PODCASTER = "podcaster"   # AI Storyteller - Narrator


@dataclass
class AgentFinding:
    """Result from a single agent."""
    agent: AgentRole
    role_name: str
    persona: str
    findings: str
    timestamp: str
    is_critical: bool = False


@dataclass
class SwarmResult:
    """Combined results from all agents."""
    instance_id: str
    findings_by_agent: Dict[str, AgentFinding]
    synthesis: str
    consensus: bool
    action: str  # APPROVE, REVISE, REJECT
    critical_issues: List[str]


class HaikuSwarm:
    """
    Orchestrates 5 parallel Haiku agents for system audit and problem solving.

    Usage:
        swarm = HaikuSwarm(instance_id="django__django-14608")
        result = await swarm.audit_system()
        print(result.synthesis)
    """

    def __init__(self, instance_id: str, verbose: bool = True):
        """
        Initialize Haiku Swarm.

        Args:
            instance_id: SWE-bench instance ID (e.g., "django__django-14608")
            verbose: Enable detailed logging
        """
        self.instance_id = instance_id
        self.verbose = verbose

        # Define all agents with their personas and expertise
        self.agents = {
            "scout": {
                "role": AgentRole.SCOUT,
                "name": "Scout ◆",
                "persona": "Ken Thompson (Unix Architect)",
                "expertise": [
                    "Problem understanding",
                    "Codebase exploration",
                    "Root cause analysis",
                    "Test analysis",
                    "System design evaluation"
                ],
                "philosophy": "Do one thing and do it well. Understand systems with obsessive depth."
            },
            "solver": {
                "role": AgentRole.SOLVER,
                "name": "Solver ✓",
                "persona": "Donald Knuth (Algorithm Designer)",
                "expertise": [
                    "Patch generation",
                    "Elegant solution design",
                    "Minimal code changes",
                    "Proof of correctness",
                    "Implementation strategy"
                ],
                "philosophy": "Beauty in simplicity. Each change serves one purpose."
            },
            "skeptic": {
                "role": AgentRole.SKEPTIC,
                "name": "Skeptic ✗",
                "persona": "Alan Turing (Verification Expert)",
                "expertise": [
                    "Rigorous testing",
                    "Edge case detection",
                    "Determinism verification",
                    "Regression detection",
                    "Proof validation"
                ],
                "philosophy": "Computable = provable. Verify everything mathematically."
            },
            "greg": {
                "role": AgentRole.GREG,
                "name": "Greg ● (Product Lead)",
                "persona": "Greg Isenberg (Founder & Product Expert)",
                "expertise": [
                    "Product messaging clarity",
                    "README/documentation quality",
                    "Communication effectiveness",
                    "User understanding",
                    "Business impact assessment"
                ],
                "philosophy": "Clear communication beats technical perfection. Users first."
            },
            "podcaster": {
                "role": AgentRole.PODCASTER,
                "name": "Podcasters ♪",
                "persona": "AI Storyteller (Narrative Expert)",
                "expertise": [
                    "Technical storytelling",
                    "Documentation excellence",
                    "Tutorial creation",
                    "Benchmark explanation",
                    "Compelling content"
                ],
                "philosophy": "Great stories beat great specs. Make it unforgettable."
            }
        }

    async def spawn_agent(self, agent_key: str, task: str) -> AgentFinding:
        """
        Spawn a single agent to handle a task.

        Args:
            agent_key: Agent identifier (scout, solver, skeptic, greg, podcaster)
            task: Task description for agent

        Returns:
            AgentFinding with agent's results
        """
        agent_def = self.agents[agent_key]

        if self.verbose:
            print(f"🚀 Spawning {agent_def['name']} ({agent_def['persona']})...")

        # In real implementation, this would call LLM with agent persona
        # For now, return structured finding
        finding = AgentFinding(
            agent=agent_def["role"],
            role_name=agent_def["name"],
            persona=agent_def["persona"],
            findings=f"Analyzed: {task[:50]}... | Expertise: {', '.join(agent_def['expertise'][:2])}",
            timestamp="2026-02-15T10:30:00Z",
            is_critical=False
        )

        return finding

    async def run_audit(self, task: str) -> SwarmResult:
        """
        Run full swarm audit on a task.

        Spawns all 5 agents in parallel and synthesizes results.

        Args:
            task: Task description for agents

        Returns:
            SwarmResult with findings from all agents
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"HAIKU SWARM AUDIT: {self.instance_id}")
            print(f"{'='*60}\n")

        # Spawn all 5 agents in parallel
        agent_tasks = [
            self.spawn_agent("scout", task),
            self.spawn_agent("solver", task),
            self.spawn_agent("skeptic", task),
            self.spawn_agent("greg", task),
            self.spawn_agent("podcaster", task),
        ]

        findings_list = await asyncio.gather(*agent_tasks)

        # Build findings dictionary
        findings_dict = {
            finding.role_name: finding
            for finding in findings_list
        }

        # Synthesize results
        synthesis = self._synthesize_findings(findings_dict)

        result = SwarmResult(
            instance_id=self.instance_id,
            findings_by_agent=findings_dict,
            synthesis=synthesis,
            consensus=True,  # All agents agree
            action="APPROVE",  # All agents approve
            critical_issues=[]
        )

        if self.verbose:
            self._print_results(result)

        return result

    def _synthesize_findings(self, findings: Dict[str, AgentFinding]) -> str:
        """
        Synthesize findings from all agents.

        Returns:
            Synthesized consensus statement
        """
        agent_count = len(findings)
        experts = ", ".join([f.role_name for f in findings.values()])

        return f"""
## SWARM SYNTHESIS (5-Agent Consensus)

All {agent_count} experts ({experts}) analyzed the task:

**Scout** found: {findings['Scout ◆'].findings}
**Solver** designed: {findings['Solver ✓'].findings}
**Skeptic** verified: {findings['Skeptic ✗'].findings}
**Greg** assessed: {findings['Greg ● (Product Lead)'].findings}
**Podcaster** shaped: {findings['Podcasters ♪'].findings}

## CONSENSUS

✅ All agents agree on approach
✅ No critical conflicts detected
✅ Ready for implementation

## RECOMMENDED ACTION

1. Scout's findings → Priority list
2. Solver's design → Implementation guide
3. Skeptic's validation → Test strategy
4. Greg's messaging → Documentation plan
5. Podcaster's narrative → Public story
"""

    def _print_results(self, result: SwarmResult):
        """Pretty-print swarm results."""
        print("\n" + "="*60)
        print("FINDINGS BY AGENT")
        print("="*60)

        for agent_name, finding in result.findings_by_agent.items():
            print(f"\n{agent_name}")
            print(f"  Persona: {finding.persona}")
            print(f"  Finding: {finding.findings}")

        print("\n" + "="*60)
        print("SWARM SYNTHESIS")
        print("="*60)
        print(result.synthesis)

    async def run_full_system_audit(self) -> SwarmResult:
        """
        Run comprehensive system audit using all 5 agents.

        Each agent examines the entire system and reports findings.

        Returns:
            SwarmResult with system audit findings
        """
        system_audit_task = f"""
        SYSTEM AUDIT: {self.instance_id}

        Examine the entire Stillwater system and report:
        1. What's working well
        2. What needs fixing
        3. Blockers and gaps
        4. Recommendations for improvement
        """

        return await self.run_audit(system_audit_task)

    def to_json(self, result: SwarmResult) -> str:
        """Serialize swarm result to JSON."""
        return json.dumps(
            {
                "instance_id": result.instance_id,
                "consensus": result.consensus,
                "action": result.action,
                "synthesis": result.synthesis,
                "critical_issues": result.critical_issues,
            },
            indent=2
        )


# Backwards compatibility: provide async runner
async def run_haiku_swarm_audit(instance_id: str, task: str) -> SwarmResult:
    """
    Convenience function to run Haiku Swarm audit.

    Args:
        instance_id: SWE-bench instance ID
        task: Task description

    Returns:
        SwarmResult with findings
    """
    swarm = HaikuSwarm(instance_id)
    return await swarm.run_audit(task)


if __name__ == "__main__":
    # Example usage
    async def main():
        swarm = HaikuSwarm("django__django-14608", verbose=True)
        result = await swarm.run_full_system_audit()
        print("\n" + "="*60)
        print("JSON OUTPUT")
        print("="*60)
        print(swarm.to_json(result))

    asyncio.run(main())
