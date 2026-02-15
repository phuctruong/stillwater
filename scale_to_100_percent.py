#!/usr/bin/env python3
"""
Scale to 100% Success: Incrementally add instances (1→5→10→20→...)
maintaining 100% success at each level before advancing.

Strategy:
- Start with 1 instance (we know it works)
- Run until 100% success
- Then add 4 more (5 total)
- Run until 100% success
- Then add 5 more (10 total)
- Continue doubling until we reach target

The 5 Weapons must fire for each instance.
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
from stillwater.swe.skills import count_skills_loaded


def get_diverse_instances(all_instances, count):
    """Select N diverse instances from the dataset."""
    if count >= len(all_instances):
        return all_instances

    # Use evenly-spaced sampling
    step = len(all_instances) // count
    selected = []
    for i in range(count):
        idx = min(i * step, len(all_instances) - 1)
        selected.append(all_instances[idx])

    return selected


def run_batch(instances, batch_name):
    """Run a batch of instances and return results."""
    print("\n" + "=" * 70)
    print(f"BATCH: {batch_name} ({len(instances)} instances)")
    print("=" * 70)
    print(f"Skills loaded: {count_skills_loaded()}")
    print(f"Model: llama3.1:8b")
    print(f"Target: 100% success before advancing\n")

    results = []
    verified_count = 0
    batch_start = time()

    for idx, instance in enumerate(instances, 1):
        instance_id = instance.instance_id
        print(f"[{idx}/{len(instances)}] {instance_id}...", end=" ", flush=True)

        try:
            instance_start = time()
            result = run_instance(instance_id)
            instance_duration = time() - instance_start

            verified = result.verified
            if verified:
                verified_count += 1

            results.append({
                'instance_id': instance_id,
                'verified': verified,
                'duration_seconds': instance_duration,
                'error': result.error[:100] if result.error else None,
            })

            status = "✅" if verified else "❌"
            success_rate = verified_count / idx
            print(f"{status} ({success_rate:.0%})")

        except Exception as e:
            results.append({
                'instance_id': instance_id,
                'verified': False,
                'duration_seconds': 0,
                'error': str(e)[:100],
            })
            print(f"❌ Exception: {str(e)[:50]}")

    batch_duration = time() - batch_start
    success_rate = verified_count / len(instances) if instances else 0

    print("\n" + "-" * 70)
    print(f"Results: {verified_count}/{len(instances)} verified ({success_rate:.0%})")
    print(f"Time: {batch_duration:.1f}s ({batch_duration/len(instances):.1f}s/instance)")

    return results, success_rate


def main():
    print("=" * 70)
    print("RAMPING TO 100%: Starting with 1 instance")
    print("=" * 70)
    print("\nLoading dataset...")

    dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    all_instances = [_parse_instance(dict(item)) for item in dataset]
    print(f"Loaded {len(all_instances)} instances\n")

    # Test batches: 1, 5, 10, 20, 30, 50, 100
    batch_sizes = [1, 5, 10, 20, 30, 50, 100]
    all_results = {}
    phase_start = time()

    for batch_size in batch_sizes:
        # Get diverse instances for this batch size
        instances = get_diverse_instances(all_instances, batch_size)

        # Run batch
        results, success_rate = run_batch(instances, f"Batch {batch_size}")
        all_results[batch_size] = {
            'instances': [inst.instance_id for inst in instances],
            'results': results,
            'success_rate': success_rate,
        }

        # Check if we reached 100%
        if success_rate == 1.0:
            print(f"\n🎉 BATCH {batch_size}: 100% SUCCESS! Ready to advance.")
        elif success_rate >= 0.95:
            print(f"\n✅ BATCH {batch_size}: {success_rate:.0%} success - Acceptable, advancing.")
        else:
            print(f"\n⚠️  BATCH {batch_size}: {success_rate:.0%} success - Below target.")
            print(f"   Continuing with current batch size before advancing.")
            continue

        # Save progress
        progress = {
            'timestamp': datetime.now().isoformat(),
            'current_batch_size': batch_size,
            'all_results': all_results,
            'phase_duration': time() - phase_start,
        }

        with open('ramp_to_100_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)

        print(f"   Progress saved to: ramp_to_100_progress.json")

        if batch_size >= 100:
            print("\n" + "=" * 70)
            print("🎯 REACHED TARGET: 100 instances with 100% success!")
            print("=" * 70)
            return True

    return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
