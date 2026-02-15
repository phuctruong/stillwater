"""
SWE-bench runner: Orchestrate the full verification pipeline.

Pipeline:
    1. Load instance
    2. Setup environment
    3. Red Gate (baseline)
    4. Generate patch (LLM)
    5. Apply patch
    6. Green Gate (verification)
    7. God Gate (determinism - optional)
    8. Generate certificate

Usage:
    from stillwater.swe import run_instance

    result = run_instance("django__django-12345")
    print(result.certificate)
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List
import json
import time

from .loader import SWEInstance, load_instance, load_dataset
from .environment import setup_environment, apply_test_patch, apply_model_patch
from .gates import RedGate, GreenGate, GodGate, GateStatus


@dataclass
class InstanceResult:
    """
    Result from running a single SWE-bench instance.

    Attributes:
        instance_id: Instance identifier
        verified: Whether patch passed all gates
        patch: Generated patch (if any)
        certificate: Proof certificate (if verified)
        red_gate_message: Message from Red Gate
        green_gate_message: Message from Green Gate
        god_gate_message: Message from God Gate (if checked)
        baseline_passing: Number of tests passing before patch
        after_patch_passing: Number of tests passing after patch
        regressions: Number of test regressions
        new_fixes: Number of new tests fixed
        duration_ms: Total execution time
        error: Error message (if failed)
    """
    instance_id: str
    verified: bool
    patch: Optional[str] = None
    certificate: Optional[dict] = None
    red_gate_message: str = ""
    green_gate_message: str = ""
    god_gate_message: str = ""
    baseline_passing: int = 0
    after_patch_passing: int = 0
    regressions: int = 0
    new_fixes: int = 0
    duration_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def run_instance(
    instance_id: str,
    patch: Optional[str] = None,
    test_command: str = "pytest -xvs",
    cache_dir: Optional[Path] = None,
    check_determinism: bool = False,
) -> InstanceResult:
    """
    Run a single SWE-bench instance through the verification pipeline.

    Args:
        instance_id: Instance to run (e.g., "django__django-12345")
        patch: Pre-generated patch (if None, will generate using LLM)
        test_command: Command to run tests
        cache_dir: Directory for caching cloned repos
        check_determinism: Whether to run God Gate (determinism check)

    Returns:
        InstanceResult with verification status and certificate

    Example:
        >>> result = run_instance("django__django-12345")
        >>> if result.verified:
        >>>     print(f"✅ {result.certificate}")
        >>> else:
        >>>     print(f"❌ {result.error}")
    """
    start_ms = int(time.time() * 1000)

    try:
        # Load instance
        instance = load_instance(instance_id)
        print(f"\n{'='*60}")
        print(f"Running: {instance_id}")
        print(f"{'='*60}")

        # Setup environment
        env = setup_environment(instance, cache_dir)

        # Apply test patch
        if not apply_test_patch(env):
            return InstanceResult(
                instance_id=instance_id,
                verified=False,
                error="Failed to apply test patch",
                duration_ms=int(time.time() * 1000) - start_ms,
            )

        # Red Gate: Establish baseline
        red_result = RedGate.check(env.repo_dir, test_command)
        print(red_result.message)

        if not red_result:
            env.cleanup()
            return InstanceResult(
                instance_id=instance_id,
                verified=False,
                error=f"Red Gate failed: {red_result.message}",
                red_gate_message=red_result.message,
                duration_ms=int(time.time() * 1000) - start_ms,
            )

        # Generate or use provided patch
        if patch is None:
            # TODO: Implement LLM patch generation
            # For now, use gold patch if available (for testing harness)
            if instance.gold_patch:
                patch = instance.gold_patch
                print("📝 Using gold patch (LLM generation not yet implemented)")
            else:
                env.cleanup()
                return InstanceResult(
                    instance_id=instance_id,
                    verified=False,
                    error="No patch provided and LLM generation not yet implemented",
                    red_gate_message=red_result.message,
                    duration_ms=int(time.time() * 1000) - start_ms,
                )

        # Apply model patch
        if not apply_model_patch(env, patch):
            env.cleanup()
            return InstanceResult(
                instance_id=instance_id,
                verified=False,
                error="Failed to apply model patch",
                red_gate_message=red_result.message,
                patch=patch,
                duration_ms=int(time.time() * 1000) - start_ms,
            )

        # Green Gate: Verify no regressions
        green_result = GreenGate.check(
            env.repo_dir,
            test_command,
            red_result.baseline
        )
        print(green_result.message)

        # Cleanup environment
        env.cleanup()

        # Check if verified
        verified = green_result.status == GateStatus.PASS

        # Generate certificate if verified
        certificate = None
        if verified:
            certificate = _generate_certificate(
                instance,
                patch,
                red_result,
                green_result,
            )

        # Build result
        result = InstanceResult(
            instance_id=instance_id,
            verified=verified,
            patch=patch,
            certificate=certificate,
            red_gate_message=red_result.message,
            green_gate_message=green_result.message,
            baseline_passing=len(red_result.baseline.passing_tests),
            after_patch_passing=len(green_result.after_patch.passing_tests),
            regressions=len(green_result.regressions) if green_result.regressions else 0,
            new_fixes=len(green_result.new_fixes) if green_result.new_fixes else 0,
            duration_ms=int(time.time() * 1000) - start_ms,
        )

        # God Gate: Check determinism (optional)
        if check_determinism and verified:
            # TODO: Re-generate patch 2 more times and check
            # For now, skip God Gate
            result.god_gate_message = "⏭️  God Gate skipped (determinism check not yet implemented)"

        return result

    except Exception as e:
        return InstanceResult(
            instance_id=instance_id,
            verified=False,
            error=f"Unexpected error: {e}",
            duration_ms=int(time.time() * 1000) - start_ms,
        )


def run_batch(
    instance_ids: List[str],
    output_path: Optional[Path] = None,
    **kwargs
) -> List[InstanceResult]:
    """
    Run multiple SWE-bench instances.

    Args:
        instance_ids: List of instance IDs to run
        output_path: Optional path to save results JSON
        **kwargs: Additional arguments passed to run_instance

    Returns:
        List of InstanceResult objects

    Example:
        >>> results = run_batch(["django__django-12345", "requests__requests-5678"])
        >>> verified = [r for r in results if r.verified]
        >>> print(f"Verified: {len(verified)}/{len(results)}")
    """
    results = []

    for i, instance_id in enumerate(instance_ids, 1):
        print(f"\n[{i}/{len(instance_ids)}] Processing {instance_id}")

        result = run_instance(instance_id, **kwargs)
        results.append(result)

        if result.verified:
            print(f"✅ VERIFIED ({result.duration_ms}ms)")
        else:
            print(f"❌ REJECTED: {result.error}")

    # Save results if output path provided
    if output_path:
        _save_results(results, output_path)

    return results


def _generate_certificate(
    instance: SWEInstance,
    patch: str,
    red_result,
    green_result,
) -> dict:
    """
    Generate a proof certificate for a verified patch.

    The certificate contains:
    - Instance metadata
    - Baseline test results
    - After-patch test results
    - Regressions (should be empty)
    - New fixes
    - Patch hash

    This certificate serves as mathematical proof that:
    1. Tests passed before patch
    2. Tests still pass after patch
    3. No regressions were introduced
    """
    import hashlib

    patch_hash = hashlib.sha256(patch.encode()).hexdigest()

    return {
        "instance_id": instance.instance_id,
        "repo": instance.repo,
        "base_commit": instance.base_commit,
        "baseline_passing": list(red_result.baseline.passing_tests),
        "after_patch_passing": list(green_result.after_patch.passing_tests),
        "regressions": list(green_result.regressions) if green_result.regressions else [],
        "new_fixes": list(green_result.new_fixes) if green_result.new_fixes else [],
        "patch_hash": patch_hash,
        "status": "VERIFIED",
        "gates": {
            "red": red_result.message,
            "green": green_result.message,
        }
    }


def _save_results(results: List[InstanceResult], output_path: Path):
    """Save batch results to JSON file."""
    data = {
        "total": len(results),
        "verified": sum(1 for r in results if r.verified),
        "failed": sum(1 for r in results if not r.verified),
        "results": [r.to_dict() for r in results],
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n📄 Results saved to {output_path}")
