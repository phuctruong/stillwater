#!/usr/bin/env python3
"""
extract_seeds.py -- Extract top-N entries from simulation learned_*.jsonl files
to create production seed files for stillwater data/default/seeds/.

Usage:
    python src/scripts/extract_seeds.py scratch/learned_small_talk.jsonl --max 10 --min-count 20 --min-confidence 0.90
    python src/scripts/extract_seeds.py scratch/learned_intents.jsonl --max 10 --min-count 20 --min-confidence 0.85
    python src/scripts/extract_seeds.py scratch/learned_combos.jsonl --max 5 --min-count 20 --min-confidence 0.90

Output goes to stdout (JSONL format). Redirect to create seed files:
    python src/scripts/extract_seeds.py learned_small_talk.jsonl --max 10 > data/default/seeds/small-talk-seeds.jsonl

stdlib only -- no dependencies.
"""

import argparse
import json
import sys


def confidence_from_count(count: int) -> float:
    """Calculate confidence using the standard formula: 1 - 1/(1 + 0.3 * count)"""
    return 1.0 - 1.0 / (1.0 + 0.3 * count)


def load_jsonl(filepath: str) -> list:
    """Load a JSONL file, return list of dicts."""
    records = []
    with open(filepath) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARNING: Skipping line {line_num}: {e}", file=sys.stderr)
    return records


def extract_seeds(
    records: list,
    max_entries: int = 10,
    min_count: int = 20,
    min_confidence: float = 0.90,
    recalculate: bool = False,
) -> list:
    """
    Filter and sort records to extract the best seeds.

    Args:
        records: list of dicts from JSONL
        max_entries: maximum number of seeds to output
        min_count: minimum observation count to qualify
        min_confidence: minimum confidence to qualify
        recalculate: if True, recalculate confidence from count instead of using stored value

    Returns:
        list of seed records (sorted by confidence descending)
    """
    seeds = []
    for record in records:
        count = record.get("count", 0)
        if count < min_count:
            continue

        if recalculate:
            conf = confidence_from_count(count)
        else:
            conf = record.get("confidence", 0.0)

        if conf < min_confidence:
            continue

        seed = {
            "keyword": record["keyword"],
            "label": record["label"],
            "count": count,
            "confidence": round(conf if recalculate else conf, 4),
            "examples": record.get("examples", [])[:2],  # Keep max 2 examples for seeds
            "phase": record.get("phase", "unknown"),
        }
        seeds.append(seed)

    # Sort by confidence descending, then by count descending
    seeds.sort(key=lambda s: (s["confidence"], s["count"]), reverse=True)

    # Take top N
    return seeds[:max_entries]


def main():
    parser = argparse.ArgumentParser(
        description="Extract top-N entries from simulation JSONL to create production seeds."
    )
    parser.add_argument(
        "input_file",
        help="Path to the learned_*.jsonl file from simulation",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=10,
        dest="max_entries",
        help="Maximum number of seed entries to extract (default: 10)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=20,
        help="Minimum observation count to qualify as a seed (default: 20)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.90,
        help="Minimum confidence to qualify as a seed (default: 0.90)",
    )
    parser.add_argument(
        "--recalculate",
        action="store_true",
        help="Recalculate confidence from count instead of using stored value",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    # Load input
    records = load_jsonl(args.input_file)
    print(f"Loaded {len(records)} records from {args.input_file}", file=sys.stderr)

    # Extract seeds
    seeds = extract_seeds(
        records,
        max_entries=args.max_entries,
        min_count=args.min_count,
        min_confidence=args.min_confidence,
        recalculate=args.recalculate,
    )
    print(f"Extracted {len(seeds)} seeds (max={args.max_entries}, min_count={args.min_count}, min_confidence={args.min_confidence})", file=sys.stderr)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            for seed in seeds:
                f.write(json.dumps(seed) + "\n")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        for seed in seeds:
            print(json.dumps(seed))


if __name__ == "__main__":
    main()
