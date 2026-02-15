#!/usr/bin/env python3
"""
Find instances with healthy test environments (Red Gate passes baseline).
These are the only instances we can actually solve.
"""

import sys
from pathlib import Path
from datasets import load_dataset as hf_load_dataset
import json
from time import time

sys.path.insert(0, str(Path.cwd() / "src"))

from stillwater.swe.loader import _parse_instance
from stillwater.swe.environment import setup_environment
from stillwater.swe.gates import RedGate, GateStatus

def check_red_gate(instance_id, repo, base_commit):
    """Check if Red Gate baseline passes (test environment is healthy)"""
    try:
        env = setup_environment(repo, base_commit)
        gate = RedGate()
        result = gate.check(env)

        # Check if it actually passed
        if result.status == GateStatus.PASS:
            return True, "✅ Baseline passes"
        else:
            # Check what kind of failure
            msg = str(result.message)
            if "PluggyTeardownRaisedWarning" in msg or "plugin" in msg.lower():
                return False, "❌ Pytest plugin issue"
            elif "import" in msg.lower() and "error" in msg.lower():
                return False, "❌ Import error"
            elif "not found" in msg.lower():
                return False, "❌ Missing dependency"
            else:
                return False, f"❌ Test failure: {msg[:60]}"
    except Exception as e:
        return False, f"❌ Exception: {str(e)[:60]}"

def main():
    print("=" * 70)
    print("FINDING HEALTHY INSTANCES (Red Gate Baseline Passes)")
    print("=" * 70)
    print("\nLoading dataset...")

    dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    instances_list = [_parse_instance(dict(item)) for item in dataset]
    print(f"Loaded {len(instances_list)} instances")

    print("\nScanning for healthy instances...")
    print("(This will take a few minutes)\n")

    healthy = []
    unhealthy = {}
    checked = 0

    # Sample across the dataset
    sample_size = min(100, len(instances_list))
    step = len(instances_list) // sample_size

    for idx in range(0, len(instances_list), step):
        if idx >= len(instances_list):
            break

        instance = instances_list[idx]
        checked += 1

        print(f"[{checked}] {instance.instance_id}...", end=" ", flush=True)
        start = time()

        ok, msg = check_red_gate(instance.instance_id, instance.repo, instance.base_commit)
        elapsed = time() - start

        if ok:
            print(f"✅ {elapsed:.1f}s")
            healthy.append(instance.instance_id)
        else:
            print(f"{msg} {elapsed:.1f}s")
            reason = msg.split(":")[0]
            unhealthy[reason] = unhealthy.get(reason, 0) + 1

        # Stop early if we have enough
        if len(healthy) >= 50:
            break

    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: Found {len(healthy)} healthy instances out of {checked} checked")
    print("=" * 70)

    print(f"\n✅ HEALTHY INSTANCES ({len(healthy)}):")
    for iid in healthy:
        print(f"   {iid}")

    print(f"\n❌ FAILURE REASONS:")
    for reason, count in sorted(unhealthy.items(), key=lambda x: x[1], reverse=True):
        print(f"   {reason}: {count}")

    # Save for next phase
    data = {
        'checked': checked,
        'healthy_count': len(healthy),
        'healthy_instances': healthy,
        'failure_reasons': unhealthy,
    }

    with open('healthy_instances.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved {len(healthy)} healthy instances to: healthy_instances.json")

    if len(healthy) >= 10:
        print(f"\n🎯 Next: Run Phase 2.3 on these {len(healthy)} healthy instances")
        print(f"   Target: 100% success on instances with working test environments")
    else:
        print(f"\n⚠️  Only found {len(healthy)} healthy instances")
        print(f"   This explains why we can't get 100% - most test environments are broken")

if __name__ == '__main__':
    main()
