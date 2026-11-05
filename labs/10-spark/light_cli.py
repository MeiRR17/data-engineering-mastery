"""Print a deterministic Stage 10 light MapReduce result using only stdlib."""
import argparse
import json
from pathlib import Path
from instructor.reference import run_light

LAB = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=LAB / "data/synthetic_events.jsonl")
    parser.add_argument("--partitions", type=int, default=2)
    args = parser.parse_args()
    print(json.dumps(run_light(args.input, args.partitions), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

