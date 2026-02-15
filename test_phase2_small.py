#!/usr/bin/env python3
"""
Phase 2 Small Batch: 10 instances to measure scaling
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


def test_phase_2_small():
    """Run Phase 2: 10 diverse instances"""

    print("=" * 70)
    print("PHASE 2: SMALL BATCH (10 Instances)")
    print("=" * 70)
    print("\nGoal: Measure scaling, identify patterns")
    print("Model: llama 8B")
    print("Approach: Direct edits + Feedback loop (up to 6 attempts)")
    print("Expected: 30-50% success (improvement from Phase 1's 20%)")
    print()

    # Load dataset
    print("📦 Loading SWE-bench Lite dataset...")
    try:
        dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
        instances_list = [_parse_instance(dict(item)) for item in dataset]
        print(f"✅ Loaded {len(instances_list)} instances")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return False

    # Select 10 diverse instances
    indices = [
        0,
        len(instances_list) // 9,
        len(instances_list) // 4,
        3 * len(instances_list) // 9,
        len(instances_list) // 2,
        5 * len(instances_list) // 9,
        2 * len(instances_list) // 3,
        7 * len(instances_list) // 9,
        8 * len(instances_list) // 9,
        -1,
    ]
    selected_instances = [instances_list[i] for i in indices if i < len(instances_list)]
    if len(selected_instances) < 10:
        selected_instances = instances_list[:10]

    instance_ids = [inst.instance_id for inst in selected_instances]

    print(f"Selected {len(instance_ids)} instances:")
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
    print("PHASE 2 RESULTS")
    print(f"{'='*70}\n")

    verified_count = sum(1 for r in results if r['verified'])
    success_rate = verified_count / len(instance_ids) if instance_ids else 0
    avg_duration = sum(r['duration_seconds'] for r in results) / len(results) if results else 0

    print(f"Total:           {len(instance_ids)} instances")
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
    if success_rate < 0.2:
        print("  🛑 Regressed - investigate why")
        print("     Review Phase 1 vs Phase 2 differences")
    elif success_rate < 0.3:
        print("  ⚠️  Scaling slowly, continue with improvements")
        print("     Try better file context or error feedback")
    elif success_rate < 0.5:
        print("  ✅ Good progress - proceed to Phase 3")
        print("     Improvements are working")
    else:
        print("  🎉 Excellent - likely on track for 100%")
        print("     Continue to Phase 3 and beyond")

    print()

    # Save for A/B notebook
    phase_2_data = {
        'phase': 2,
        'timestamp': datetime.now().isoformat(),
        'config': {
            'model': 'llama3.1:8b',
            'approach': 'direct_edits_plus_feedback_loop',
            'attempts_max': 6,
            'files_context': 'full',
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

    output_path = Path('phase_2_results.json')
    with open(output_path, 'w') as f:
        json.dump(phase_2_data, f, indent=2)

    print(f"✅ Results saved to: {output_path}")
    print(f"   (For A/B Jupyter notebook later)")
    print()

    return success_rate >= 0.2


if __name__ == '__main__':
    success = test_phase_2_small()

    if success:
        print("Phase 2 passed! Ready for Phase 3.")
        sys.exit(0)
    else:
        print("Phase 2 needs debugging before Phase 3.")
        sys.exit(1)
