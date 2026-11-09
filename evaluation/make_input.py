"""Builds a requirements input file (same format and dedup as best_requirements.json) from one extraction run.

Used by the runs that need an input other than the EIRENE one of E1-E3 (JWST end-to-end, input control).
No LLM calls; writes only the requested file, inside the new phase directory.

    python -m evaluation.make_input --run-file jwst_sliding_window_gpt-6-luna_run1.json \\
        --out results/jwst_pipeline/input_requirements.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from evaluation.common import EXTRACTION_DIR, read_json, write_json
from evaluation.run_extraction import select_best


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-file", required=True, help="Name of a file in results/extraction/runs/.")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    path = EXTRACTION_DIR / "runs" / args.run_file
    payload = read_json(path)
    best = select_best([(path, payload)], payload["metadata"]["doc"], best_file=args.run_file)
    if args.out.exists():
        existing = read_json(args.out)
        if existing.get("sha256") != best["sha256"]:
            raise SystemExit(f"{args.out} exists with another sha256 ({existing.get('sha256')}); not overwritten.")
        print(f"{args.out} already up to date")
    else:
        write_json(args.out, best)
    s = best["source"]
    print(f"{args.out}: {s['file']} -> {s['n_requirements']} requirements in {s['n_categories']} categories "
          f"after dedup (raw run: {payload['metadata']['n_requirements']}), sha256 {best['sha256']}")


if __name__ == "__main__":
    main()
