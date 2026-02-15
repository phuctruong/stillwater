#!/usr/bin/env python3
"""
Phase 100%: Get 100% success on Django instances (known to work)
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


def test_100_percent():
    """Run on Django instances only (known to work) until 100% success"""

    print("=" * 70)
    print("PHASE 100%: Django Instances (Known to Work)")
    print("=" * 70)
    print("\nGoal: Get 100% success on instances with healthy test environments")
    print("Model: llama 8B")
    print("Focus: Django instances (proven to work)")
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

    # Filter for Django instances only
    django_instances = [
        inst for inst in instances_list
        if inst.instance_id.startswith('django__django')
    ]

    print(f"Found {len(django_instances)} Django instances")

    # Select a diverse subset of Django instances
    if len(django_instances) > 20:
        # Take evenly spaced django instances
        step = len(django_instances) // 20
        selected = [django_instances[i*step] for i in range(20)]
    else:
        selected = django_instances

    instance_ids = [inst.instance_id for inst in selected]

    print(f"\nSelected {len(instance_ids)} Django instances:")
    for i, iid in enumerate(instance_ids[:10], 1):
        print(f"  {i}. {iid}")
    if len(instance_ids) > 10:
        print(f"  ... and {len(instance_ids)-10} more")
    print()

    # Run tests
    results = []
    phase_start = time()
    verified_count = 0

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

            if verified:
                verified_count += 1

            status = "✅ VERIFIED" if verified else "❌ FAILED"
            print(f"\n{status} ({instance_duration:.1f}s)")
            if error:
                print(f"Error: {error[:100]}")

            # Print progress
            success_rate = verified_count / idx
            print(f"Progress: {verified_count}/{idx} = {success_rate:.0%}")

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

    # Results
    print(f"\n\n{'='*70}")
    print("PHASE 100% RESULTS")
    print(f"{'='*70}\n")

    verified_count = sum(1 for r in results if r['verified'])
    success_rate = verified_count / len(instance_ids) if instance_ids else 0
    avg_duration = sum(r['duration_seconds'] for r in results) / len(results) if results else 0

    print(f"Total:           {len(instance_ids)} Django instances")
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
    print("ASSESSMENT:")
    if success_rate == 1.0:
        print("  🎉 100% SUCCESS! Django instances all passed!")
    elif success_rate >= 0.9:
        print("  ✅ Excellent (90%+) - Ready to scale to all instances")
    elif success_rate >= 0.7:
        print("  ⚠️  Good progress (70%+) - Need to improve feedback loop")
    else:
        print("  🛑 Below 70% - Need to fix orchestration")

    print()

    # Save results
    phase_data = {
        'phase': '100%',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'model': 'llama3.1:8b',
            'approach': 'direct_edits_plus_feedback_loop',
            'attempts_max': 6,
            'instance_filter': 'django_instances_only',
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

    output_path = Path('phase_100_results.json')
    with open(output_path, 'w') as f:
        json.dump(phase_data, f, indent=2)

    print(f"✅ Results saved to: {output_path}")
    print()

    return success_rate >= 0.7


if __name__ == '__main__':
    success = test_100_percent()

    if success:
        print("✅ Django instances strong! Ready to scale.")
        sys.exit(0)
    else:
        print("❌ Need to improve.")
        sys.exit(1)
