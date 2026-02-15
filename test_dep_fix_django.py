#!/usr/bin/env python3
"""
Test the dependency installation fix on Django instances.
"""

import json
import sys
from pathlib import Path
from datasets import load_dataset as hf_load_dataset

from stillwater.swe.loader import _parse_instance
from stillwater.swe import run_instance

# Test on 5 Django instances
NUM_TEST_INSTANCES = 5
CACHE_DIR = Path("/tmp/stillwater-swe-cache-test-django")
# TEST_COMMAND will auto-detect from repo
OUTPUT_FILE = Path("test-dep-fix-django-results.json")

def main():
    print("=" * 60)
    print("Testing Dependency Installation Fix (Django)")
    print("=" * 60)
    print(f"Testing on {NUM_TEST_INSTANCES} Django instances")
    print()

    # Load dataset
    print("📦 Loading SWE-bench Lite...")
    dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    instances = [_parse_instance(dict(item)) for item in dataset]

    # Filter for Django instances only
    django_instances = [inst for inst in instances if inst.repo == "django/django"]
    test_instances = django_instances[:NUM_TEST_INSTANCES]

    print(f"✅ Found {len(django_instances)} Django instances")
    print(f"   Testing on first {len(test_instances)}")
    print()

    # Create cache dir
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Process instances
    results = []

    for i, instance in enumerate(test_instances, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(test_instances)}] Processing {instance.instance_id}")
        print(f"{'='*60}")

        try:
            result = run_instance(
                instance_id=instance.instance_id,
                cache_dir=CACHE_DIR,
                # test_command will auto-detect from repo
            )

            # Save result
            results.append(result.to_dict())

            # Print status
            if result.verified:
                print(f"✅ VERIFIED ({result.duration_ms}ms)")
            else:
                print(f"❌ FAILED: {result.error}")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "instance_id": instance.instance_id,
                "verified": False,
                "error": str(e),
            })

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "total": len(test_instances),
            "verified": sum(1 for r in results if isinstance(r, dict) and r.get("verified", False)),
            "failed": sum(1 for r in results if not (isinstance(r, dict) and r.get("verified", False))),
            "results": results,
        }, f, indent=2)

    # Print summary
    verified = sum(1 for r in results if isinstance(r, dict) and r.get("verified", False))
    print("\n" + "=" * 60)
    print("TEST RESULTS (Django)")
    print("=" * 60)
    print(f"Total: {len(test_instances)}")
    print(f"Verified: {verified}/{len(test_instances)} ({verified/len(test_instances)*100:.1f}%)")
    print(f"Failed: {len(test_instances) - verified}")
    print(f"\nResults saved to: {OUTPUT_FILE}")

    if verified > 0:
        print("\n✅ FIX WORKS! At least some instances passed Red Gate")
        print("   Ready to proceed with full run")
    else:
        print("\n❌ FIX DIDN'T WORK! All instances still failing")
        print("   Need to investigate further")
    print("=" * 60)

if __name__ == "__main__":
    main()
