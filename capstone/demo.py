
"""Run an end-to-end synthetic capstone and display a redacted evidence report."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from instructor.reference import run_pipeline


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace",type=Path,
                        help="Must not exist yet; artifacts saved here")
    args=parser.parse_args()
    if args.workspace:
        evidence=run_pipeline(args.workspace)
        print(json.dumps(evidence,ensure_ascii=False,indent=2))
        print("Local synthetic evidence saved to:",args.workspace/"evidence.json")
    else:
        with TemporaryDirectory(prefix="dem-capstone-") as folder:
            evidence=run_pipeline(Path(folder)/"exercise")
            print(json.dumps(evidence,ensure_ascii=False,indent=2))
            print("Temporary training files cleaned up after successful run.")


if __name__=="__main__":
    main()
