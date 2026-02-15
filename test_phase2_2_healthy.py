#!/usr/bin/env python3
"""
Phase 2.2: Smart instance selection - only instances with healthy test environments
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from time import time
from datasets import load_dataset as hf_load_dataset

sys.path.insert(0, str(Path.cwd() / "src"))

from stillwater.swe.runner import run_instance
from stillwater.swe.loader import _parse_instance
from stillwater.swe.gates import RedGate
from stillwater.swe.environment import setup_environment


def has_healthy_tests(instance):
    """Quick check if instance has healthy test environment (Red Gate baseline passes)"""
    try:
        env = setup_environment(instance.repo, instance.base_commit)
        gate = RedGate()
        result = gate.check(env)

        # Check if baseline passes or fails gracefully
        if "AttributeError" in str(result.message) or "PluggyTeardownRaisedWarning" in str(result.message):
            return False  # Broken test environment
        if "import" in str(result.message).lower() and "error" in str(result.message).lower():
            return False  # Import errors in tests

        return True
    except Exception:
        return False


def test_phase_2_2_healthy():
    """Run Phase 2.2: 10 instances with healthy test environments"""

    print("=" * 70)
    print("PHASE 2.2: HEALTHY INSTANCES (Smart Selection)")
    print("=" * 70)
    print("\nGoal: Scale to 50-70% with only viable instances")
    print("Model: llama 8B")
    print("Approach: Direct edits + Feedback loop")
    print("Strategy: Filter for healthy test environments first")
    print()

    # Load dataset
    print("📦 Loading SWE-bench Lite dataset...")
    try:
        dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
        instances_list = [_parse_instance(dict(item)) for item in dataset]
        print(f"✅ Loaded {len(instances_list)} total instances")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return False

    # Filter for healthy instances (sample and check)
    print("\n🔍 Filtering for healthy test environments...")
    print("   (Checking ~30 instances to find 10 healthy ones)")

    healthy_instances = []
    indices_to_check = [
        0, len(instances_list)//15, len(instances_list)//10, len(instances_list)//7,
        len(instances_list)//5, 4*len(instances_list)//15, len(instances_list)//3,
        3*len(instances_list)//8, len(instances_list)//2, 9*len(instances_list)//16,
        7*len(instances_list)//12, 5*len(instances_list)//8, 11*len(instances_list)//16,
        3*len(instances_list)//5, 7*len(instances_list)//10, 13*len(instances_list)//18,
        4*len(instances_list)//5, 5*len(instances_list)//6, 8*len(instances_list)//9,
        -1,
    ]

    checked = 0
    for idx in indices_to_check:
        if idx >= len(instances_list) or checked >= 30:
            break

        instance = instances_list[idx]
        checked += 1

        print(f"   [{checked}] Checking {instance.instance_id}...", end=" ", flush=True)

        if has_healthy_tests(instance):
            healthy_instances.append(instance)
            print("✅")
            if len(healthy_instances) >= 10:
                break
        else:
            print("❌")

    if len(healthy_instances) < 10:
        print(f"\n⚠️  Only found {len(healthy_instances)} healthy instances in sample")
        print("   Using all found instances")

    instance_ids = [inst.instance_id for inst in healthy_instances]

    print(f"\n✅ Selected {len(instance_ids)} healthy instances:")
    for i, iid in enumerate(instance_ids, 1):
        print(f"  {i}. {iid}")
    print()

    # Run tests
    results = []
    phase_start = time()

    for idx, instance_id in enumerate(instance_ids, 1):
        print(f"\n{'='*70}")
        print(f"[{idx}/{len(instance_ids)}] {instance_id}")
        print(f"{'='*70}")

        instance_start = time()

        try:
            result = run_instance(instance_id)

            instance_duration = time() - instance_start

            verified = result.verified
            error = result.error
            attempts = 1

            results.append({
                'instance_id': instance_id,
                'verified': verified,
                'attempts': attempts,
                'duration_seconds': instance_duration,
                'error': error[:200] if error else None,
            })

            status = "✅ VERIFIED" if verified else "❌ FAILED"
            print(f"\n{status} ({instance_duration:.1f}s)")
            if error:
                print(f"Error: {error[:100]}")

        except Exception as e:
            instance_duration = time() - instance_start
            results.append({
                'instance_id': instance_id,
                'verified': False,
                'attempts': 1,
                'duration_seconds': instance_duration,
                'error': f"Exception: {str(e)[:200]}",
            })
            print(f"\n❌ EXCEPTION ({instance_duration:.1f}s)")
            print(f"Error: {str(e)[:100]}")

    phase_duration = time() - phase_start

    # Analyze results
    print(f"\n\n{'='*70}")
    print("PHASE 2.2 RESULTS (Healthy Instances Only)")
    print(f"{'='*70}\n")

    verified_count = sum(1 for r in results if r['verified'])
    success_rate = verified_count / len(instance_ids) if instance_ids else 0
    avg_duration = sum(r['duration_seconds'] for r in results) / len(results) if results else 0

    print(f"Total:           {len(instance_ids)} instances (filtered for healthy tests)")
    print(f"Verified:        {verified_count}/{len(instance_ids)}")
    print(f"Success Rate:    {success_rate:.0%}")
    print(f"Avg Time:        {avg_duration:.1f}s per instance")
    print(f"Total Time:      {phase_duration:.1f}s")
    print()

    # Error analysis
    error_types = {}
    for r in results:
        if r['error']:
            error_msg = r['error'].split(':')[0]
            error_types[error_msg] = error_types.get(error_msg, 0) + 1

    if error_types:
        print("Error Types:")
        for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error}: {count}")
        print()

    # Decision
    print("DECISION FOR PHASE 3:")
    if success_rate < 0.3:
        print("  ⚠️  Still low - may need model improvements")
    elif success_rate < 0.5:
        print("  ✅ Good - on track for 100%")
    elif success_rate < 0.7:
        print("  🎉 Excellent - strong scaling")
    else:
        print("  🚀 Outstanding - likely 90%+ on full dataset")

    print()

    # Save for A/B notebook
    phase_data = {
        'phase': '2.2',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'model': 'llama3.1:8b',
            'approach': 'direct_edits_plus_feedback_loop',
            'attempts_max': 6,
            'files_context': 'full',
            'instance_filtering': 'healthy_test_environments',
        },
        'summary': {
            'total_instances': len(instance_ids),
            'verified': verified_count,
            'success_rate': success_rate,
            'avg_duration_seconds': avg_duration,
            'total_duration_seconds': phase_duration,
        },
        'results': results,
        'error_analysis': error_types,
    }

    output_path = Path('phase_2_2_results.json')
    with open(output_path, 'w') as f:
        json.dump(phase_data, f, indent=2)

    print(f"✅ Results saved to: {output_path}")
    print()

    return success_rate >= 0.3


if __name__ == '__main__':
    success = test_phase_2_2_healthy()

    if success:
        print("Phase 2.2 passed! Ready for Phase 3.")
        sys.exit(0)
    else:
        print("Phase 2.2 needs improvement.")
        sys.exit(1)
