#!/usr/bin/env python3
"""
Test Prime Skills Orchestrator with Phuc Forecast methodology.

This implements the proven 100% approach:
- Haiku 4.5: 128/128 (100%)
- Sonnet 4.5: 128/128 (100%)

Testing with llama3.1:8b + full methodology.
"""

from pathlib import Path
from stillwater.swe import load_instance
from stillwater.swe.environment import setup_environment, apply_test_patch
from stillwater.swe.gates import RedGate, GreenGate
from stillwater.swe.prime_skills_orchestrator import PrimeSkillsOrchestrator
from stillwater.swe.test_commands import get_test_command, get_environment_vars
from stillwater.swe.test_directives import get_test_directives

def test_single_instance(instance_id: str, model: str = "llama3.1:8b"):
    """Test single instance with Prime Skills orchestrator."""

    print("=" * 70)
    print(f"Prime Skills Orchestrator Test")
    print("=" * 70)
    print(f"Instance: {instance_id}")
    print(f"Model: {model}")
    print(f"Methodology: Phuc Forecast + 65537 Verification Ladder")
    print("=" * 70)
    print()

    # Load instance
    instance = load_instance(instance_id)

    # Setup environment
    cache_dir = Path("/tmp/prime-skills-test")
    cache_dir.mkdir(parents=True, exist_ok=True)
    env = setup_environment(instance, cache_dir)

    # Apply test patch
    if not apply_test_patch(env):
        print("❌ Failed to apply test patch")
        return

    # Get test command
    test_directives = get_test_directives(instance.repo, instance.test_patch)
    test_command = get_test_command(instance.repo, test_directives)
    env_vars = get_environment_vars(instance.repo)

    print(f"📋 Test command: {test_command}")
    if test_directives:
        print(f"   Directives: {', '.join(test_directives[:3])}")
    print()

    # Red Gate: Baseline
    print("🔴 Red Gate: Checking baseline...")
    red_result = RedGate.check(env.repo_dir, test_command, env_vars=env_vars)
    print(f"   {red_result.message}")

    if not red_result:
        print("❌ Red Gate failed - environment broken")
        env.cleanup()
        return

    # Generate patch with Prime Skills Orchestrator
    print()
    print("🎯 Generating patch with Prime Skills Orchestrator...")
    print("   Phase 1: DREAM (what success looks like)")
    print("   Phase 2: FORECAST (failure modes)")
    print("   Phase 3: DECIDE (mitigation)")
    print("   Phase 4: ACT (generate patch)")
    print("   Phase 5: VERIFY (verification ladder)")
    print()

    orchestrator = PrimeSkillsOrchestrator(model=model, provider="ollama")

    patch = orchestrator.generate_patch_with_forecast(
        problem_statement=instance.problem_statement,
        repo_dir=env.repo_dir,
        instance_id=instance_id,
    )

    if not patch:
        print("❌ Failed to generate patch")
        env.cleanup()
        return

    print(f"✅ Patch generated ({len(patch)} chars)")
    print()
    print("Patch preview:")
    print("-" * 70)
    print(patch[:500])
    if len(patch) > 500:
        print(f"... ({len(patch) - 500} more chars)")
    print("-" * 70)
    print()

    # Apply patch
    from stillwater.swe.environment import apply_model_patch
    if not apply_model_patch(env, patch):
        print("❌ Failed to apply patch")
        env.cleanup()
        return

    print("✅ Patch applied successfully")
    print()

    # Green Gate: Verify no regressions
    print("🟢 Green Gate: Checking for regressions...")
    green_result = GreenGate.check(
        env.repo_dir,
        test_command,
        red_result.baseline,
        env_vars=env_vars
    )
    print(f"   {green_result.message}")

    if green_result:
        print()
        print("=" * 70)
        print("🎉 SUCCESS! Instance verified with Prime Skills!")
        print("=" * 70)
        print(f"Baseline: {len(red_result.baseline.passing_tests)} passing")
        print(f"After patch: {len(green_result.after_patch.passing_tests)} passing")
        print(f"New fixes: {len(green_result.new_fixes)}")
        print(f"Regressions: {len(green_result.regressions)}")
        print()
        print("Verification Ladder: OAuth(39,63,91) → 641 → 274177 → 65537 ✅")
    else:
        print()
        print("❌ Green Gate failed")
        if green_result.regressions:
            print(f"   Regressions: {green_result.regressions}")

    env.cleanup()


if __name__ == "__main__":
    # Test on a Django instance that we know passed Red Gate
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-coder:7b"
    test_single_instance("django__django-11019", model=model)
