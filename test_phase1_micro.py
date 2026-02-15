#!/usr/bin/env python3
"""
Phase 1 Micro Test: 5 instances to verify orchestration works

This is the start of our ramp to 100% with llama 8B.
We'll measure everything and document for the A/B notebook.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from time import time

sys.path.insert(0, str(Path.cwd() / "src"))

from stillwater.swe.runner import run_instance
from stillwater.swe.loader import load_dataset, _parse_instance


def test_phase_1_micro():
    """Run Phase 1: 5 diverse instances"""

    print("=" * 70)
    print("PHASE 1: MICRO TEST (5 Instances)")
    print("=" * 70)
    print("\nGoal: Verify orchestration works, identify critical issues")
    print("Model: llama 8B")
    print("Approach: Direct edits + Feedback loop (up to 6 attempts)")
    print()

    # Select 5 diverse instances
    dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")

    # Pick diverse instances (different repos, different complexity)
    instance_indices = [0, 50, 100, 150, 200]  # Spread across dataset
    instances = [_parse_instance(dataset[i]) for i in instance_indices]

    print(f"Selected {len(instances)} instances:")
    for i, inst in enumerate(instances, 1):
        print(f"  {i}. {inst.instance_id:45s} ({inst.repo})")
    print()

    # Run tests
    results = []
    phase_start = time()

    for idx, instance in enumerate(instances, 1):
        print(f"\n{'='*70}")
        print(f"[{idx}/{len(instances)}] {instance.instance_id}")
        print(f"{'='*70}")

        instance_start = time()

        try:
            result = run_instance(instance.instance_id)

            instance_duration = time() - instance_start

            verified = result.verified
            error = result.error
            attempts = 1  # We can't track this yet, will improve

            results.append({
                'instance_id': instance.instance_id,
                'repo': instance.repo,
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
                'instance_id': instance.instance_id,
                'repo': instance.repo,
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
    print("PHASE 1 RESULTS")
    print(f"{'='*70}\n")

    verified_count = sum(1 for r in results if r['verified'])
    success_rate = verified_count / len(results)
    avg_duration = sum(r['duration_seconds'] for r in results) / len(results)

    print(f"Total:           {len(results)} instances")
    print(f"Verified:        {verified_count}/{len(results)}")
    print(f"Success Rate:    {success_rate:.0%}")
    print(f"Avg Time:        {avg_duration:.1f}s per instance")
    print(f"Total Time:      {phase_duration:.1f}s")
    print()

    # Error analysis
    error_types = {}
    for r in results:
        if r['error']:
            error_msg = r['error'].split(':')[0]  # Get first part
            error_types[error_msg] = error_types.get(error_msg, 0) + 1

    if error_types:
        print("Error Types:")
        for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error}: {count}")
        print()

    # Decision
    print("DECISION FOR PHASE 2:")
    if success_rate == 0:
        print("  🛑 STOP - Critical bug exists")
        print("     Debug failures before continuing")
    elif success_rate < 0.4:
        print("  ⚠️  Continue with caution")
        print("     Expect to improve in Phase 2")
    else:
        print("  ✅ Good baseline - proceed to Phase 2")

    print()

    # Save for A/B notebook
    phase_1_data = {
        'phase': 1,
        'timestamp': datetime.now().isoformat(),
        'config': {
            'model': 'llama3.1:8b',
            'approach': 'direct_edits_plus_feedback_loop',
            'attempts_max': 6,
            'files_context': 'full',
        },
        'summary': {
            'total_instances': len(results),
            'verified': verified_count,
            'success_rate': success_rate,
            'avg_duration_seconds': avg_duration,
            'total_duration_seconds': phase_duration,
        },
        'results': results,
        'error_analysis': error_types,
    }

    output_path = Path('phase_1_results.json')
    with open(output_path, 'w') as f:
        json.dump(phase_1_data, f, indent=2)

    print(f"✅ Results saved to: {output_path}")
    print(f"   (For A/B Jupyter notebook later)")
    print()

    return success_rate >= 0.2  # Return True if we should continue


if __name__ == '__main__':
    success = test_phase_1_micro()

    if success:
        print("Phase 1 passed! Ready for Phase 2.")
        sys.exit(0)
    else:
        print("Phase 1 needs debugging before Phase 2.")
        sys.exit(1)
