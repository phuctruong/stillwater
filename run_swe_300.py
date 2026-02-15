#!/usr/bin/env python3
"""
Run all 300 SWE-bench instances with Stillwater + Prime Skills + Ollama 8B.

Target: 100% accuracy using llama3.1:8b + Prime Skills v1.0.0+
"""

import json
import sys
from pathlib import Path

from stillwater.swe import load_dataset, run_batch

# Configuration
OUTPUT_FILE = Path("stillwater-swe-300-predictions.jsonl")
RESULTS_FILE = Path("stillwater-swe-300-results.json")
MODEL = "llama3.1:8b"
TEST_COMMAND = "pytest -xvs"
CACHE_DIR = Path("/tmp/stillwater-swe-cache")


def main():
    print("=" * 60)
    print("Stillwater SWE-bench 300-Instance Runner")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Prime Skills: Loaded (51 skills)")
    print(f"Verification: Red-Green-God gates")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)
    print()

    # Load dataset
    print("📦 Loading SWE-bench Lite dataset...")
    try:
        dataset = load_dataset()
        instance_ids = [inst.instance_id for inst in dataset]
        print(f"✅ Loaded {len(instance_ids)} instances")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        print("Install with: pip install datasets")
        sys.exit(1)

    # Create cache directory
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Run all instances
    print()
    print("🚀 Starting batch processing...")
    print()

    results = run_batch(
        instance_ids=instance_ids,
        output_path=RESULTS_FILE,
        test_command=TEST_COMMAND,
        cache_dir=CACHE_DIR,
    )

    # Generate predictions file (SWE-bench format)
    print()
    print("📝 Generating predictions file...")

    with open(OUTPUT_FILE, "w") as f:
        for result in results:
            if result.patch:
                prediction = {
                    "instance_id": result.instance_id,
                    "model_name_or_path": f"stillwater-{MODEL}-prime-skills-v1.0.0",
                    "model_patch": result.patch,
                }
                f.write(json.dumps(prediction) + "\n")

    # Print summary
    verified = sum(1 for r in results if r.verified)
    generated = sum(1 for r in results if r.patch)

    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total instances: {len(results)}")
    print(f"Patches generated: {generated}/{len(results)} ({generated/len(results):.1%})")
    print(f"Patches verified: {verified}/{len(results)} ({verified/len(results):.1%})")
    print()
    print(f"Results: {RESULTS_FILE}")
    print(f"Predictions: {OUTPUT_FILE}")
    print("=" * 60)

    # Exit code
    if verified == len(results):
        print("✅ 100% SUCCESS!")
        sys.exit(0)
    else:
        print(f"⚠️  {len(results) - verified} instances failed verification")
        sys.exit(1)


if __name__ == "__main__":
    main()
