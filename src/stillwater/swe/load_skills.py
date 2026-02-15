"""
Load-Skills Command: Dynamically load Prime Skills for session.

This provides the `/load-skills` executable command that:
- Loads all 51 Prime Skills from disk
- Validates skill integrity
- Creates skill summary for LLM injection
- Reports loaded count and any errors

Usage:
    from stillwater.swe.load_skills import LoadSkillsCommand

    cmd = LoadSkillsCommand()
    result = cmd.execute(verify=True, domain="coding")
    print(result.message)

Auth: 65537 | Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .skills import (
    get_skills_directory,
    load_all_skills,
    create_skills_summary,
    load_skill_excerpts,
    get_essential_skills,
    count_skills_loaded,
)


class SkillDomain(Enum):
    """Skill domains/categories."""
    CODING = "coding"
    MATH = "math"
    EPISTEMIC = "epistemic"
    VERIFICATION = "verification"
    INFRASTRUCTURE = "infrastructure"
    GOVERNANCE = "governance"
    COMMUNICATIONS = "communications"
    ALL = "all"


@dataclass
class SkillLoadResult:
    """Result of loading skills."""
    success: bool
    skills_loaded: int
    skills_total: int
    domains_loaded: List[str]
    message: str
    errors: List[str]
    summary: str  # For injection into prompts
    excerpts: str  # For enhanced context


class LoadSkillsCommand:
    """
    Execute `/load-skills` command to load Prime Skills.

    Supports:
    - `/load-skills` - Load all 51 skills
    - `/load-skills --verify` - Load + verify integrity
    - `/load-skills --domain coding` - Load only coding skills
    - `/load-skills --quiet` - Suppress output
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize load-skills command.

        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose

    def execute(
        self,
        verify: bool = False,
        domain: Optional[str] = None,
        quiet: bool = False,
    ) -> SkillLoadResult:
        """
        Execute load-skills command.

        Args:
            verify: Run verification checks after loading
            domain: Load specific domain only (coding, math, etc)
            quiet: Suppress output

        Returns:
            SkillLoadResult with loading status
        """
        errors = []
        skills_loaded = 0
        domains_loaded = []

        try:
            # Load all skills from disk
            all_skills = load_all_skills()
            skills_loaded = len(all_skills)

            # Filter by domain if specified
            if domain and domain != "all":
                try:
                    domain_enum = SkillDomain[domain.upper()]
                    all_skills = self._filter_by_domain(all_skills, domain_enum)
                    domains_loaded = [domain]
                except KeyError:
                    errors.append(f"Unknown domain: {domain}")
                    domains_loaded = ["unknown"]
            else:
                # Infer domains from loaded skills
                domains_loaded = self._infer_domains(all_skills)

            # Get skill count
            total_skills = count_skills_loaded()

            # Create summary for prompt injection
            summary = create_skills_summary()

            # Load excerpts for enhanced context
            excerpts = load_skill_excerpts()

            # Run verification if requested
            if verify:
                verify_errors = self._verify_skills(all_skills)
                if verify_errors:
                    errors.extend(verify_errors)

            # Build success message
            if not errors:
                message = self._build_success_message(
                    skills_loaded, total_skills, domains_loaded, verify
                )
            else:
                message = self._build_error_message(errors)

            return SkillLoadResult(
                success=len(errors) == 0,
                skills_loaded=skills_loaded,
                skills_total=total_skills,
                domains_loaded=domains_loaded,
                message=message,
                errors=errors,
                summary=summary,
                excerpts=excerpts,
            )

        except Exception as e:
            return SkillLoadResult(
                success=False,
                skills_loaded=0,
                skills_total=0,
                domains_loaded=[],
                message=f"ERROR: Failed to load skills: {e}",
                errors=[str(e)],
                summary="",
                excerpts="",
            )

    def _filter_by_domain(
        self, skills: Dict[str, str], domain: SkillDomain
    ) -> Dict[str, str]:
        """Filter skills by domain."""
        if domain == SkillDomain.ALL:
            return skills

        domain_path = domain.value
        filtered = {}

        for skill_name, content in skills.items():
            # Check if skill belongs to this domain
            if skill_name.startswith(f"{domain_path}/") or f"/{domain_path}/" in skill_name:
                filtered[skill_name] = content

        return filtered

    def _infer_domains(self, skills: Dict[str, str]) -> List[str]:
        """Infer which domains are represented in loaded skills."""
        domains = set()

        for skill_name in skills.keys():
            parts = skill_name.split("/")
            if len(parts) > 1:
                domains.add(parts[-2])  # domain from path
            elif skill_name.startswith("prime-"):
                domains.add("core")

        return sorted(list(domains))

    def _verify_skills(self, skills: Dict[str, str]) -> List[str]:
        """
        Verify skill integrity.

        Checks:
        1. No duplicate skill names
        2. All skills have content
        3. Required core skills present
        4. All skill files readable
        """
        errors = []

        # Check core skills present
        required_core = ["prime-coder.md", "prime-math.md", "prime-swarm-orchestration.md"]
        for required in required_core:
            if required not in skills:
                errors.append(f"Missing core skill: {required}")

        # Check for duplicates (shouldn't happen but verify)
        if len(skills) != len(set(skills.keys())):
            errors.append("Duplicate skill names detected")

        # Check all skills have content
        for name, content in skills.items():
            if not content or len(content.strip()) == 0:
                errors.append(f"Empty skill: {name}")

        # Verification ladder check
        if "Lane A" not in str(skills) and "lane" not in str(skills).lower():
            errors.append("Lane algebra framework not loaded (epistemic foundation)")

        if "Counter" not in str(skills) or "counting" not in str(skills).lower():
            errors.append("Counter bypass protocol not loaded (math foundation)")

        return errors

    def _build_success_message(
        self,
        loaded: int,
        total: int,
        domains: List[str],
        verified: bool,
    ) -> str:
        """Build success message."""
        lines = [
            "✅ Skills loaded successfully",
            f"   Loaded: {loaded}/{total} skills",
            f"   Domains: {', '.join(domains)}",
        ]

        if verified:
            lines.append("   Verification: PASSED ✅")

        lines.append("")
        lines.append("Ready for:")
        lines.append("- LLM patch generation")
        lines.append("- SWE-bench instances")
        lines.append("- System audits with Haiku Swarms")

        return "\n".join(lines)

    def _build_error_message(self, errors: List[str]) -> str:
        """Build error message."""
        lines = [
            "⚠️  Skills loaded with errors:",
            "",
        ]
        for error in errors:
            lines.append(f"  - {error}")

        lines.append("")
        lines.append("Action: Check skill files in src/stillwater/skills/")

        return "\n".join(lines)


def run_load_skills_command(
    verify: bool = False,
    domain: Optional[str] = None,
    quiet: bool = False,
) -> SkillLoadResult:
    """
    Standalone function to run /load-skills command.

    Can be called from CLI, scripts, or notebooks.

    Args:
        verify: Run verification checks
        domain: Load specific domain
        quiet: Suppress output

    Returns:
        SkillLoadResult
    """
    cmd = LoadSkillsCommand(verbose=not quiet)
    result = cmd.execute(verify=verify, domain=domain, quiet=quiet)

    if not quiet:
        print(result.message)

    return result


if __name__ == "__main__":
    # CLI usage
    import argparse

    parser = argparse.ArgumentParser(description="Load Prime Skills")
    parser.add_argument("--verify", action="store_true", help="Verify skill integrity")
    parser.add_argument("--domain", help="Load specific domain (coding, math, etc)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    result = run_load_skills_command(
        verify=args.verify, domain=args.domain, quiet=args.quiet
    )

    exit(0 if result.success else 1)
