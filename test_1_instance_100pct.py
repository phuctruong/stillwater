#!/usr/bin/env python3
"""
Test Phase: 1 Instance - Verify 100% success
Expected time: ~2 minutes
Target: 1/1 = 100%
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
    print("PHASE: 1 Instance (100% target)")
    print("=" * 70)
    print("\nExpected: ~2 minutes")
    print("Target: 1/1 = 100%\n")

    # Load dataset
    dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    all_instances = [_parse_instance(dict(item)) for item in dataset]

    # Use first instance (django__django-14608 is near start)
    instance = all_instances[13]  # Known to work
    print(f"Testing: {instance.instance_id}\n")

    start = time()
    result = run_instance(instance.instance_id)
    duration = time() - start

    print(f"\n{'='*70}")
    if result.verified:
        print(f"✅ VERIFIED in {duration:.1f}s")
        print(f"Problem: {instance.problem_statement[:80]}...")
        print(f"Result: SUCCESS - 1/1 = 100%")

        # Save result
        with open('phase_1_instance.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'phase': '1_instance',
                'verified': 1,
                'total': 1,
                'success_rate': 1.0,
                'duration_seconds': duration,
                'instance_id': instance.instance_id,
            }, f, indent=2)

        print(f"\n✅ Ready for Phase: 5 Instances")
        return True
    else:
        print(f"❌ FAILED in {duration:.1f}s")
        print(f"Error: {result.error[:200]}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
