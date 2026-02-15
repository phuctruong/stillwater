#!/usr/bin/env python3
"""
Run SWE-bench Lite (300 instances) with Stillwater + Prime Skills + Ollama 8B.
"""

import json
import sys
from pathlib import Path
from datasets import load_dataset as hf_load_dataset

from stillwater.swe.loader import _parse_instance
from stillwater.swe import run_instance

# Configuration
OUTPUT_FILE = Path("stillwater-swe-lite-predictions.jsonl")
RESULTS_FILE = Path("stillwater-swe-lite-results.json")
PROGRESS_FILE = Path("stillwater-swe-lite-progress.json")
MODEL = "qwen2.5-coder:7b"  # Switched from llama3.1:8b for better patch generation
# TEST_COMMAND will auto-detect based on repo
CACHE_DIR = Path("/tmp/stillwater-swe-cache")

def load_progress():
    """Load progress from previous run."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": [], "results": []}

def save_progress(progress):
    """Save progress."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def main():
    print("=" * 60)
    print("Stillwater SWE-bench Lite Runner (300 instances)")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Skills: 51 Prime Skills loaded")
    print(f"Verification: Red-Green-God gates")
    print("=" * 60)
    print()

    # Load dataset
    print("📦 Loading SWE-bench Lite...")
    dataset = hf_load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    instances = [_parse_instance(dict(item)) for item in dataset]
    print(f"✅ Loaded {len(instances)} instances")
    print()

    # Load progress
    progress = load_progress()
    completed_ids = set(progress.get("completed", []))

    # Create cache dir
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Process instances
    results = progress.get("results", [])
    
    for i, instance in enumerate(instances, 1):
        if instance.instance_id in completed_ids:
            print(f"[{i}/{len(instances)}] ⏭️  Skipping {instance.instance_id} (already done)")
            continue

        print(f"\n{'='*60}")
        print(f"[{i}/{len(instances)}] Processing {instance.instance_id}")
        print(f"{'='*60}")

        try:
            result = run_instance(
                instance_id=instance.instance_id,
                cache_dir=CACHE_DIR,
                # Model comes from config file: stillwater.toml
            )

            # Save result
            results.append(result.to_dict())
            completed_ids.add(instance.instance_id)
            
            # Update progress
            progress["completed"] = list(completed_ids)
            progress["results"] = results
            save_progress(progress)

            # Print status
            if result.verified:
                print(f"✅ VERIFIED ({result.duration_ms}ms)")
            else:
                print(f"❌ FAILED: {result.error}")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "instance_id": instance.instance_id,
                "verified": False,
                "error": str(e),
            })
            progress["results"] = results
            save_progress(progress)

    # Generate predictions file
    print("\n📝 Generating predictions file...")
    with open(OUTPUT_FILE, "w") as f:
        for result in results:
            if isinstance(result, dict) and result.get("patch"):
                prediction = {
                    "instance_id": result["instance_id"],
                    "model_name_or_path": f"stillwater-{MODEL}-prime-skills",
                    "model_patch": result["patch"],
                }
                f.write(json.dumps(prediction) + "\n")

    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "total": len(instances),
            "completed": len(results),
            "verified": sum(1 for r in results if isinstance(r, dict) and r.get("verified", False)),
            "results": results,
        }, f, indent=2)

    # Print summary
    verified = sum(1 for r in results if isinstance(r, dict) and r.get("verified", False))
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total: {len(instances)}")
    print(f"Completed: {len(results)}")
    print(f"Verified: {verified}/{len(results)} ({verified/len(results)*100:.1f}%)")
    print(f"\nResults: {RESULTS_FILE}")
    print(f"Predictions: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
