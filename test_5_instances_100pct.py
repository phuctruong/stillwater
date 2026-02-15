#!/usr/bin/env python3
"""
Test Phase: 5 Instances - Verify 100% success
Expected time: ~10 minutes
Target: 5/5 = 100%
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

def main():
    print("=" * 70)
    print("PHASE: 5 Instances (100% target)")
    print("=" * 70)
    print("\nExpected: ~10 minutes")
    print("Target: 5/5 = 100%\n")

    # Load dataset
    dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    all_instances = [_parse_instance(dict(item)) for item in dataset]

    # Select 5 diverse instances
    indices = [13, 50, 100, 150, 200]  # Spread across dataset
    instances = [all_instances[i] for i in indices if i < len(all_instances)]

    print(f"Testing {len(instances)} instances:\n")
    for i, inst in enumerate(instances, 1):
        print(f"  {i}. {inst.instance_id}")

    print()

    results = []
    verified_count = 0
    phase_start = time()

    for idx, instance in enumerate(instances, 1):
        print(f"\n[{idx}/{len(instances)}] {instance.instance_id}...", end=" ", flush=True)

        try:
            start = time()
            result = run_instance(instance.instance_id)
            duration = time() - start

            if result.verified:
                verified_count += 1
                print(f"✅ ({duration:.1f}s)")
            else:
                print(f"❌ ({duration:.1f}s)")

            results.append({
                'instance_id': instance.instance_id,
                'verified': result.verified,
                'duration_seconds': duration,
                'error': result.error[:100] if result.error else None,
            })

        except Exception as e:
            print(f"❌ Exception")
            results.append({
                'instance_id': instance.instance_id,
                'verified': False,
                'duration_seconds': 0,
                'error': str(e)[:100],
            })

    phase_duration = time() - phase_start
    success_rate = verified_count / len(instances)

    print(f"\n{'='*70}")
    print(f"Result: {verified_count}/{len(instances)} = {success_rate:.0%}")
    print(f"Time: {phase_duration:.1f}s total ({phase_duration/len(instances):.1f}s/instance)")

    # Save result
    with open('phase_5_instances.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'phase': '5_instances',
            'verified': verified_count,
            'total': len(instances),
            'success_rate': success_rate,
            'duration_seconds': phase_duration,
            'results': results,
        }, f, indent=2)

    if success_rate == 1.0:
        print(f"\n✅ SUCCESS - Ready for Phase: 10 Instances")
        return True
    else:
        print(f"\n❌ FAILED - Need to debug before advancing")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
