"""Phase 3: repair-loop ablation (C1-C4) for one model, on the best requirements JSON.

    Condition  Repair?  Routing+priority?  Category KB?
    C1         no       -                  -            (generate + validate)
    C2         yes      no                 no           (blind repair, parser order)
    C3         yes      yes                no           (+ routing)
    C4         yes      yes                yes          (+ knowledge base = full framework)

Same input contract and outputs as the pipeline (never extracts):

    python -m evaluation.run_ablation --model gpt-6-luna --runs 3
"""

from __future__ import annotations

import argparse

from core.agents.agent2.logic import CONDITIONS

from evaluation.common import ABLATION_DIR, parse_models, setup_logging
from evaluation.run_pipeline import add_common_args, run_phase, validate_common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="gpt-6-luna", help="Model alias for generation and repair.")
    parser.add_argument("--conditions", nargs="+", choices=list(CONDITIONS), default=list(CONDITIONS))
    add_common_args(parser)
    args = parser.parse_args()
    models = parse_models(parser, [args.model])
    validate_common(parser, args)
    setup_logging(args.verbose)

    run_phase(
        out_dir=ABLATION_DIR, results_name="ablation_results.csv", requirements_path=args.requirements,
        models=models, conditions=args.conditions, runs=args.runs, max_iterations=args.max_iterations,
        max_categories=args.max_categories, workers=args.workers,
        budget_usd=args.budget_usd, dry_run=args.dry_run, max_rpm=args.max_rpm,
    )


if __name__ == "__main__":
    main()
