#!/usr/bin/env python3
"""
Test a single Django instance with verbose output.
"""

from pathlib import Path
from stillwater.swe import run_instance

# Test a single Django instance
INSTANCE_ID = "django__django-11019"
CACHE_DIR = Path("/tmp/stillwater-swe-single-test")

def main():
    print("=" * 60)
    print(f"Testing single instance: {INSTANCE_ID}")
    print("=" * 60)
    print()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    result = run_instance(
        instance_id=INSTANCE_ID,
        cache_dir=CACHE_DIR,
    )

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Verified: {result.verified}")
    print(f"Error: {result.error}")
    print(f"Red Gate: {result.red_gate_message}")
    print(f"Baseline passing: {result.baseline_passing}")
    print("=" * 60)

if __name__ == "__main__":
    main()
