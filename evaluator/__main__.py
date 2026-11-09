"""LJS over the SysML v2 models stored by a phase (no generation or repair is re-run).

Reads results/<phase>/sysml_models.jsonl, judges every distinct (requirements, code) once and writes
results/<phase>/ljs/<judge>/:
    judgments.jsonl   one record per judged model (per-requirement verdicts, scores, usage); resume marker
    ljs_results.csv   one row per (pdf, llm, condition, run, category); rebuilt from judgments.jsonl

    python -m evaluator --phase pipeline --dry-run
    python -m evaluator --phase pipeline --sample 30 --workers 4 --max-rpm 18 --budget-usd 1   # pilot
    python -m evaluator --phase pipeline --workers 8 --max-rpm 18 --budget-usd 10
    python -m evaluator --input other/sysml_models.jsonl --out-dir other/ljs/deepseek-v4-pro --judge deepseek-v4-pro
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core.models import get_model, judge_aliases

from evaluation.common import (ABLATION_DIR, ABLATION_STRESS_DIR, PIPELINE_DIR, Budget, JsonlAppender, provenance,
                               setup_logging, write_csv, write_run_manifest)

from . import DEFAULT_JUDGE
from .prompts import IEEE830_ATTRIBUTES, STATUSES
from .scoring import score
from .semantic_judge import build_messages, judge


logger = logging.getLogger(__name__)

PHASE_DIRS = {"pipeline": PIPELINE_DIR, "ablation": ABLATION_DIR, "ablation_stress": ABLATION_STRESS_DIR}
KEY_COLUMNS = ("pdf", "llm", "condition", "run", "category")
SCORE_COLUMNS = ("ljs", "ljs_strict", "ljs_lenient", "n_requirements", *(f"n_{s}" for s in STATUSES),
                 *(f"ieee_{a}" for a in IEEE830_ATTRIBUTES))
# judge_cost_usd is the cost of the judgment the row points to; rows with the same judgment_key share it.
RESULT_COLUMNS = (*KEY_COLUMNS, "judge", "judgment_key", "requirements_sha256", *SCORE_COLUMNS, "judge_cost_usd")

# Dry-run token profile when nothing has been judged yet (output includes reasoning tokens).
_PROFILE_OUTPUT_BASE = 800
_PROFILE_OUTPUT_PER_REQUIREMENT = 250


def judgment_key(requirements: list[str], sysml_code: str) -> str:
    """Identity of what the judge sees: identical (requirements, code) pairs are judged once."""
    canonical = json.dumps({"requirements": requirements, "sysml_code": sysml_code},
                           ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_models(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"Models file not found: {path}")
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            record["judgment_key"] = judgment_key(record["requirements"], record["sysml_code"])
            rows[tuple(str(record[c]) for c in KEY_COLUMNS)] = record  # last record of a key wins
    return list(rows.values())


def load_judgments(path: Path, judge_alias: str) -> dict[str, dict]:
    judgments = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                if record["judge"] == judge_alias:
                    judgments[record["judgment_key"]] = record
    return judgments


def write_results(path: Path, models: list[dict], judgments: dict[str, dict], judge_alias: str) -> int:
    rows = []
    for record in models:
        judgment = judgments.get(record["judgment_key"])
        if judgment is None:
            continue  # not judged yet: left out, never filled
        rows.append({
            **{c: record[c] for c in KEY_COLUMNS},
            "judge": judge_alias, "judgment_key": record["judgment_key"],
            "requirements_sha256": record.get("requirements_sha256", ""),
            **{c: judgment["scores"][c] for c in SCORE_COLUMNS},
            "judge_cost_usd": judgment["usage"]["cost_usd"],
        })
    write_csv(path, RESULT_COLUMNS, rows)
    return len(rows)


def print_estimate(pending: list[dict], judge_alias: str, judgments: dict[str, dict]) -> None:
    n_requirements = sum(len(r["requirements"]) for r in pending)
    observed = [j["usage"]["cost_usd"] / len(j["per_requirement"]) for j in judgments.values() if j["per_requirement"]]
    if observed:
        cost = n_requirements * sum(observed) / len(observed)
        basis = f"observed cost per requirement (n={len(observed)} judgments)"
    else:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        spec = get_model(judge_alias)
        cost = 0.0
        for r in pending:
            tokens_in = sum(len(enc.encode(m["content"])) for m in build_messages(r["requirements"], r["sysml_code"]))
            tokens_out = _PROFILE_OUTPUT_BASE + _PROFILE_OUTPUT_PER_REQUIREMENT * len(r["requirements"])
            cost += (tokens_in * spec.input_usd_per_m + tokens_out * spec.output_usd_per_m) / 1e6
        basis = "token profile (rough: reasoning length is unknown until a pilot runs)"
    print(f"Estimated cost for {len(pending)} judgments ({n_requirements} requirements): ${cost:.4f} [{basis}]")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--phase", choices=list(PHASE_DIRS), help="Judge results/<phase>/sysml_models.jsonl.")
    source.add_argument("--input", type=Path, help="Any sysml_models.jsonl (needs --out-dir).")
    parser.add_argument("--out-dir", type=Path, default=None, help="Default: results/<phase>/ljs/<judge>.")
    parser.add_argument("--judge", default=DEFAULT_JUDGE, choices=judge_aliases(),
                        help=f"Judge model alias from core/models.py (default: {DEFAULT_JUDGE}).")
    parser.add_argument("--conditions", nargs="+", default=None, help="Only rows of these conditions.")
    parser.add_argument("--models", nargs="+", default=None, help="Only rows of these candidate models.")
    parser.add_argument("--repaired-only", action="store_true",
                        help="Only rows whose generation was invalid (initial_errors > 0), i.e. repaired code.")
    parser.add_argument("--sample", type=int, default=None,
                        help="Judge only N random pending models (pilot). Re-running without it completes the rest.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-rpm", type=float, default=None,
                        help="Max requests per minute to the judge (e.g. 18 for OpenRouter's 20 rpm limit).")
    parser.add_argument("--budget-usd", type=float, default=None,
                        help="Stop submitting new judgments once this much is spent.")
    parser.add_argument("--dry-run", action="store_true", help="Print pending judgments and estimated cost, then exit.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.input and not args.out_dir:
        parser.error("--input needs --out-dir")
    setup_logging(args.verbose)

    models_path = args.input or PHASE_DIRS[args.phase] / "sysml_models.jsonl"
    out_dir = args.out_dir or PHASE_DIRS[args.phase] / "ljs" / args.judge
    judgments_path = out_dir / "judgments.jsonl"
    results_path = out_dir / "ljs_results.csv"

    models = [r for r in load_models(models_path)
              if (args.conditions is None or r["condition"] in args.conditions)
              and (args.models is None or r["llm"] in args.models)
              and (not args.repaired_only or int(r.get("initial_errors") or 0) > 0)]
    judgments = load_judgments(judgments_path, args.judge)
    unique = {r["judgment_key"]: r for r in models}
    pending = [r for key, r in unique.items() if key not in judgments]
    if args.sample is not None:
        pending = random.Random(args.seed).sample(pending, min(args.sample, len(pending)))
    print(f"Models: {models_path} ({len(models)} rows, {len(unique)} distinct requirements+code)\n"
          f"Judge: {args.judge} ({get_model(args.judge).openrouter_id}) -> {out_dir}\n"
          f"Judgments: {len(judgments)} stored, {len(pending)} to run now")

    if args.dry_run:
        print_estimate(pending, args.judge, judgments)
        return

    if pending:
        from core.llm_client import create_client

        client = create_client(args.judge, max_rpm=args.max_rpm)
        write_run_manifest(out_dir, models_path=str(models_path), judge=args.judge, judge_model=client.model,
                           judge_provider=client.spec.provider, judge_reasoning_effort=client.spec.reasoning_effort,
                           requirements_sha256=sorted({r.get("requirements_sha256", "") for r in pending}),
                           n_pending=len(pending), budget_usd=args.budget_usd)
        appender = JsonlAppender(judgments_path)
        budget = Budget(args.budget_usd)
        counter = {"n": 0}
        lock = threading.Lock()

        def work(record: dict) -> None:
            if budget.exceeded:
                return
            tag = f"[{record['llm']}][{record['condition']}][run {record['run']}] {record['category'][:60]}"
            try:
                result = judge(record["requirements"], record["sysml_code"], client)
            except Exception as exc:
                budget.add(getattr(exc, "usage", {}).get("cost_usd", 0.0))
                logger.exception("Judgment failed for %s", tag)
                message = f"FAILED ({type(exc).__name__}; retried on resume)"
            else:
                judgment = {
                    "judgment_key": record["judgment_key"], "judge": args.judge,
                    "judge_model": client.model, "judge_provider": client.spec.provider,
                    **provenance(client.model, record.get("requirements_sha256", "")),
                    "judge_reasoning_effort": client.spec.reasoning_effort,
                    **result, "scores": score(result["per_requirement"]),
                }
                appender.append_many([judgment])
                with lock:
                    judgments[record["judgment_key"]] = judgment
                budget.add(result["usage"]["cost_usd"])
                s = judgment["scores"]
                ljs = "n/a" if s["ljs"] is None else f"{s['ljs']:.3f}"
                message = (f"LJS {ljs} (sat/part/miss/na {s['n_satisfied']}/{s['n_partial']}/{s['n_missing']}/"
                           f"{s['n_not_applicable']}) ${result['usage']['cost_usd']:.4f}")
            with lock:
                counter["n"] += 1
                print(f"[{counter['n']}/{len(pending)}] {tag}: {message}")

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            list(executor.map(work, pending))
        print(f"\nSpent in this invocation: ${budget.spent_usd:.4f}")
        if budget.exceeded:
            print(f"Budget of ${args.budget_usd:.2f} reached; re-run the same command to continue.")

    n_rows = write_results(results_path, models, judgments, args.judge)
    print(f"Wrote {results_path}: {n_rows}/{len(models)} rows judged")


if __name__ == "__main__":
    main()
