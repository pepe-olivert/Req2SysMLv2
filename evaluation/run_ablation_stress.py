"""Phase 3b: repair-loop ablation (C1-C4) on a fixed bank of real invalid generations.

With the corrected generation prompt the candidate models rarely produce invalid models, so the
regular ablation (run_ablation) has too few errors to compare the repair conditions. This phase
repairs a fixed bank of generations produced by the same models on the same requirements with
the ORIGINAL generation prompt (before the prompt fix), which contain
many naturally occurring errors. Nothing is generated: every condition repairs the stored code
with the current repair loop (paired design, as in run_phase).

    python -m evaluation.run_ablation_stress --seed-from <generations.jsonl of the earlier prompt> \\
        --models gpt-6-luna gemini-3.5-flash-lite --runs 3 --workers 8 --max-rpm 18 --budget-usd 8

The seeded generations are written once to results/ablation_stress/generations.jsonl, so the
bank is part of the results and later runs only need --models.

New conditions on the same bank go to a new directory, seeded from the stored bank, so they stay
paired with C1-C4 (same generations) and results/ablation_stress is never extended:

    python -m evaluation.run_ablation_stress --out-dir results/ablation_stress_c2kb \\
        --seed-from results/ablation_stress/generations.jsonl --conditions C1 C2KB --runs 3 --workers 8 --max-rpm 18
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.agents.agent2.logic import CONDITIONS

from evaluation.common import ABLATION_STRESS_DIR, load_best_requirements, parse_models, setup_logging
from evaluation.run_pipeline import add_common_args, run_phase, validate_common

def seed_bank(source: Path, models: list[str], sha256: str, out_dir: Path) -> None:
    """Copies the source generations of `models` (same requirements) into the phase directory once."""
    generations_path = out_dir / "generations.jsonl"
    if generations_path.exists():
        print(f"Bank already seeded: {generations_path}")
        return
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = [r for r in records if r["llm"] in models and r.get("requirements_sha256") == sha256]
    generations_path.parent.mkdir(parents=True, exist_ok=True)
    generations_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected), encoding="utf-8")
    print(f"Seeded {len(selected)} generations from {source} into {generations_path}")


def summarize_source(source: Path, sha256: str) -> None:
    """Validity of every source generation (all models) with the current validator.

    Written to results/ablation_stress/source_validity.csv: it documents why the bank uses the
    models it uses (the ones with the most invalid generations under the earlier prompt).
    """
    from core.agents.agent2.logic import SysMLAgent
    from evaluation.common import write_csv

    agent = SysMLAgent.__new__(SysMLAgent)  # validation only: no LLM client is needed
    rows = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("requirements_sha256") != sha256:
            continue
        errors = agent.validate_sysml(r["raw_output"])
        rows.append({"llm": r["llm"], "run": r["run"], "category": r["category"],
                     "valid": not errors, "errors": len(errors)})
    path = ABLATION_STRESS_DIR / "source_validity.csv"
    write_csv(path, ["llm", "run", "category", "valid", "errors"], rows)
    print(f"Wrote {path}: {len(rows)} source generations")


def check_bank(models: list[str], runs: int, categories: list[str], sha256: str, out_dir: Path) -> None:
    """Refuses to run if any (model, run, category) is missing: run_phase would generate it with the new prompt."""
    generations_path = out_dir / "generations.jsonl"
    have = set()
    if generations_path.exists():
        for line in generations_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("requirements_sha256") == sha256:
                    have.add((r["llm"], int(r["run"]), r["category"]))
    missing = [(m, run, c) for m in models for run in range(1, runs + 1) for c in categories
               if (m, run, c) not in have]
    if missing:
        raise SystemExit(f"{len(missing)} generations missing from the bank (e.g. {missing[0]}); "
                         f"seed it with --seed-from. Nothing was run.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=["gpt-6-luna", "gemini-3.5-flash-lite"])
    parser.add_argument("--conditions", nargs="+", choices=list(CONDITIONS), default=list(CONDITIONS))
    parser.add_argument("--out-dir", type=Path, default=ABLATION_STRESS_DIR,
                        help="Phase directory (default: results/ablation_stress).")
    parser.add_argument("--seed-from", type=Path, default=None,
                        help="generations.jsonl to build the bank from (only used if the bank does not exist).")
    parser.add_argument("--summarize-source", type=Path, default=None,
                        help="Write source_validity.csv for every model of this generations.jsonl and exit.")
    add_common_args(parser)
    args = parser.parse_args()
    models = parse_models(parser, args.models)
    validate_common(parser, args)
    setup_logging(args.verbose)

    best = load_best_requirements(args.requirements)
    categories = list(best["requirements"])[:args.max_categories] if args.max_categories else list(best["requirements"])
    if args.summarize_source:
        summarize_source(args.summarize_source, best["sha256"])
        return
    if args.seed_from:
        seed_bank(args.seed_from, models, best["sha256"], args.out_dir)
    check_bank(models, args.runs, categories, best["sha256"], args.out_dir)

    run_phase(
        out_dir=args.out_dir, results_name="ablation_results.csv", requirements_path=args.requirements,
        models=models, conditions=args.conditions, runs=args.runs, max_iterations=args.max_iterations,
        max_categories=args.max_categories, workers=args.workers,
        budget_usd=args.budget_usd, dry_run=args.dry_run, max_rpm=args.max_rpm,
    )


if __name__ == "__main__":
    main()
