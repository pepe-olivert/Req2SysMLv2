"""Phase 1: requirement extraction (docs x strategies x models x runs) and best-JSON selection.

    python -m evaluation.run_extraction --models all --runs 3
    python -m evaluation.run_extraction --select-best-only
    python -m evaluation.run_extraction --select-best-only --best-file eirene_sliding_window_gpt-6-luna_run1.json
"""

from __future__ import annotations

import argparse
import logging
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.config import DOCUMENTS, document_path, openrouter_api_key
from core.extraction import STRATEGIES
from core.llm_client import UsageTracker, create_client
from core.models import get_model

from evaluation.common import (
    BEST_REQUIREMENTS_PATH,
    EXTRACTION_DIR,
    Budget,
    add_models_arg,
    count_requirements,
    normalize_requirements,
    parse_models,
    read_json,
    requirements_sha256,
    setup_logging,
    write_csv,
    write_json,
)


logger = logging.getLogger(__name__)

RUNS_DIR = EXTRACTION_DIR / "runs"
MAX_RPM: dict[str, float | None] = {"value": None}  # set from --max-rpm
RESULTS_PATH = EXTRACTION_DIR / "extraction_results.csv"
AGREEMENT_PATH = EXTRACTION_DIR / "extraction_agreement.csv"

RESULT_COLUMNS = (
    "pdf", "strategy", "llm", "run", "num_categories", "num_requirements", "avg_req_per_cat",
    "input_tokens", "output_tokens", "reasoning_tokens", "llm_calls", "latency_s", "cost_usd",
)
AGREEMENT_COLUMNS = ("pdf", "llm", "run", "strategy_a", "strategy_b", "jaccard_similarity")
FUZZY_MATCH_THRESHOLD = 0.85
BEST_CRITERION = (
    "max number of requirements after dedup among all successful (strategy, model, run) "
    "extractions of the document; ties broken by lowest extraction cost"
)


def run_file(doc: str, strategy: str, model: str, run: int) -> Path:
    return RUNS_DIR / f"{doc}_{strategy}_{model}_run{run}.json"


def load_run(path: Path) -> dict | None:
    """Return the run payload if the file is a complete, successful run; else None."""
    try:
        payload = read_json(path)
    except (OSError, ValueError):
        return None
    if isinstance(payload, dict) and isinstance(payload.get("requirements"), dict) \
            and isinstance(payload.get("metadata"), dict):
        return payload
    return None


def successful_runs() -> list[tuple[Path, dict]]:
    if not RUNS_DIR.exists():
        return []
    runs = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        if path.name.endswith("_error.json"):
            continue
        payload = load_run(path)
        if payload is not None:
            runs.append((path, payload))
    return runs


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def extract_one(doc: str, strategy: str, model: str, run: int) -> dict:
    strategy_obj = STRATEGIES[strategy]()
    tracker = UsageTracker(create_client(model, max_rpm=MAX_RPM["value"]))
    spec = get_model(model)
    error_path = run_file(doc, strategy, model, run).with_name(
        f"{doc}_{strategy}_{model}_run{run}_error.json"
    )
    try:
        result = strategy_obj.extract(str(document_path(doc)), tracker)
    except Exception as exc:
        logger.exception("Extraction failed doc=%s strategy=%s model=%s run=%d", doc, strategy, model, run)
        write_json(error_path, {
            "doc": doc, "strategy": strategy, "model": model, "run": run,
            "error_type": type(exc).__name__, "error_message": str(exc),
            "traceback": traceback.format_exc(), "usage": tracker.snapshot(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return {"ok": False, "cost_usd": tracker.cost_usd}

    requirements = result["requirements"]
    normalized = normalize_requirements(requirements)
    usage = tracker.snapshot()
    payload = {
        "requirements": requirements,
        "metadata": {
            "doc": doc,
            "strategy": strategy,
            "model": model,
            "openrouter_id": spec.openrouter_id,
            "reasoning_effort": spec.reasoning_effort,
            "run": run,
            "n_categories": len(normalized),
            "n_requirements": count_requirements(normalized),
            **usage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_size": getattr(strategy_obj, "chunk_size_tokens", None),
            "overlap": getattr(strategy_obj, "overlap_tokens", None),
            "strategy_metadata": result.get("metadata", {}),
        },
    }
    write_json(run_file(doc, strategy, model, run), payload)
    error_path.unlink(missing_ok=True)
    return {"ok": True, "cost_usd": usage["cost_usd"]}


def rebuild_results_csv() -> None:
    rows = []
    for _, payload in successful_runs():
        m = payload["metadata"]
        rows.append({
            "pdf": m["doc"], "strategy": m["strategy"], "llm": m["model"], "run": m["run"],
            "num_categories": m["n_categories"], "num_requirements": m["n_requirements"],
            "avg_req_per_cat": m["n_requirements"] / m["n_categories"] if m["n_categories"] else 0.0,
            "input_tokens": m["input_tokens"], "output_tokens": m["output_tokens"],
            "reasoning_tokens": m["reasoning_tokens"], "llm_calls": m["llm_calls"],
            "latency_s": m["latency_s"], "cost_usd": m["cost_usd"],
        })
    rows.sort(key=lambda r: (r["pdf"], r["strategy"], r["llm"], int(r["run"])))
    write_csv(RESULTS_PATH, RESULT_COLUMNS, rows)


# ---------------------------------------------------------------------------
# Raw vs sliding-window agreement (fuzzy Jaccard)
# ---------------------------------------------------------------------------
def flatten_requirements(requirements: dict[str, list[str]]) -> list[str]:
    return list(dict.fromkeys(r for reqs in requirements.values() for r in reqs))


def fuzzy_jaccard_similarity(
    requirements_a: dict[str, list[str]],
    requirements_b: dict[str, list[str]],
    encode: Callable[[list[str]], Any],
) -> float:
    """Greedy one-to-one matching of requirements with cosine >= 0.85, then Jaccard."""
    items_a = flatten_requirements(requirements_a)
    items_b = flatten_requirements(requirements_b)

    if not items_a and not items_b:
        return 1.0
    if not items_a or not items_b:
        return 0.0

    similarities = encode(items_a) @ encode(items_b).T
    candidate_matches = sorted(
        (
            (float(similarities[i, j]), i, j)
            for i in range(len(items_a))
            for j in range(len(items_b))
            if similarities[i, j] >= FUZZY_MATCH_THRESHOLD
        ),
        reverse=True,
    )

    matched_a: set[int] = set()
    matched_b: set[int] = set()
    for _, index_a, index_b in candidate_matches:
        if index_a not in matched_a and index_b not in matched_b:
            matched_a.add(index_a)
            matched_b.add(index_b)

    intersection_size = len(matched_a)
    union_size = len(items_a) + len(items_b) - intersection_size
    return intersection_size / union_size


def rebuild_agreement_csv() -> None:
    from core.evaluation.semantic_eval import encode

    by_key: dict[tuple[str, str, int], dict[str, dict]] = {}
    for _, payload in successful_runs():
        m = payload["metadata"]
        by_key.setdefault((m["doc"], m["model"], m["run"]), {})[m["strategy"]] = \
            normalize_requirements(payload["requirements"])

    rows = []
    for (doc, model, run), by_strategy in sorted(by_key.items()):
        if "raw" in by_strategy and "sliding_window" in by_strategy:
            rows.append({
                "pdf": doc, "llm": model, "run": run,
                "strategy_a": "raw", "strategy_b": "sliding_window",
                "jaccard_similarity": fuzzy_jaccard_similarity(
                    by_strategy["raw"], by_strategy["sliding_window"], encode),
            })
    write_csv(AGREEMENT_PATH, AGREEMENT_COLUMNS, rows)


# ---------------------------------------------------------------------------
# Best selection
# ---------------------------------------------------------------------------
def _default_dedup(requirements: dict[str, list[str]]) -> dict[str, list[str]]:
    from core.extraction.dedup import deduplicate_requirements

    return deduplicate_requirements(requirements)[0]


def select_best(
    runs: list[tuple[Path, dict]],
    doc: str,
    dedup: Callable[[dict[str, list[str]]], dict[str, list[str]]] = _default_dedup,
    best_file: str | None = None,
) -> dict:
    """Pick the single requirements set consumed by the pipeline and the ablation.

    With `best_file`, that run is used instead of the automatic criterion (same dedup).
    """
    candidates = []
    for path, payload in runs:
        m = payload["metadata"]
        if m.get("doc") != doc or (best_file is not None and path.name != best_file):
            continue
        requirements = normalize_requirements(dedup(normalize_requirements(payload["requirements"])))
        if not requirements:
            continue
        candidates.append((path, m, requirements))
    if not candidates:
        if best_file is not None:
            raise ValueError(f"'{best_file}' is not a successful, non-empty extraction run of '{doc}'.")
        raise ValueError(f"No successful extraction runs for document '{doc}'.")

    path, m, requirements = min(
        candidates,
        key=lambda c: (-count_requirements(c[2]), float(c[1]["cost_usd"]),
                       c[1]["strategy"], c[1]["model"], int(c[1]["run"])),
    )
    return {
        "requirements": requirements,
        "source": {
            "doc": doc,
            "strategy": m["strategy"],
            "model": m["model"],
            "run": m["run"],
            "file": path.name,
            "n_categories": len(requirements),
            "n_requirements": count_requirements(requirements),
            "cost_usd": m["cost_usd"],
            "criterion": (f"manually selected run ({best_file}); requirements deduplicated as in the automatic criterion"
                          if best_file is not None else BEST_CRITERION),
            "n_candidates": len(candidates),
        },
        "sha256": requirements_sha256(requirements),
    }


def write_best(doc: str, best_file: str | None = None) -> dict:
    best = select_best(successful_runs(), doc, best_file=best_file)
    write_json(BEST_REQUIREMENTS_PATH, best)
    s = best["source"]
    print(
        f"\nBest requirements -> {BEST_REQUIREMENTS_PATH}\n"
        f"  chosen: {s['file']} (strategy={s['strategy']}, model={s['model']}, run={s['run']})\n"
        f"  {s['n_requirements']} requirements in {s['n_categories']} categories after dedup, "
        f"extraction cost ${s['cost_usd']:.4f}\n"
        f"  why: {s['criterion']} ({s['n_candidates']} candidates)\n"
        f"  sha256: {best['sha256']}"
    )
    return best


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs", nargs="+", choices=list(DOCUMENTS), default=list(DOCUMENTS))
    parser.add_argument("--strategies", nargs="+", choices=list(STRATEGIES), default=list(STRATEGIES))
    add_models_arg(parser)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--budget-usd", type=float, default=None,
                        help="Stop launching new extractions once this much has been spent.")
    parser.add_argument("--workers", type=int, default=4, help="Extraction runs executed in parallel.")
    parser.add_argument("--max-rpm", type=float, default=None,
                        help="Max requests per minute per model (e.g. 18 for OpenRouter's 20 rpm new-account limit).")
    parser.add_argument("--best-doc", choices=list(DOCUMENTS), default="eirene",
                        help="Document whose best extraction feeds the pipeline (default: eirene).")
    parser.add_argument("--best-file", default=None,
                        help="Use this run file (name in results/extraction/runs/) as the best JSON "
                             "instead of the automatic max-requirements criterion.")
    parser.add_argument("--select-best-only", action="store_true",
                        help="Only (re)select best_requirements.json from existing runs; no LLM calls.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.runs <= 0:
        parser.error("--runs must be > 0")
    return args, parse_models(parser, args.models)


def main() -> None:
    args, models = parse_args()
    setup_logging(args.verbose)
    MAX_RPM["value"] = args.max_rpm

    if not args.select_best_only:
        missing = [str(document_path(d)) for d in args.docs if not document_path(d).exists()]
        if missing:
            raise SystemExit(f"error: source documents not found: {', '.join(missing)}\n"
                             "They are not distributed (see Data availability in README.md). Nothing was run.")
        openrouter_api_key()
        budget = Budget(args.budget_usd)
        jobs = [(d, s, m, r) for d in args.docs for s in args.strategies for m in models
                for r in range(1, args.runs + 1)]
        pending = [job for job in jobs if load_run(run_file(*job)) is None]
        print(f"Extraction jobs: {len(jobs)} total, {len(jobs) - len(pending)} already done, "
              f"{len(pending)} pending, workers={args.workers}")
        # Longest jobs first (sliding window, larger document) to shorten the total wall time.
        pending.sort(key=lambda job: (job[1] != "sliding_window", job[0] != "jwst"))
        lock = threading.Lock()
        counter = {"n": 0}

        def work(job: tuple) -> None:
            doc, strategy, model, run = job
            tag = f"doc={doc} strategy={strategy} model={model} run={run}"
            if budget.exceeded:
                return
            print(f"{tag}: extracting...")
            try:
                outcome = extract_one(doc, strategy, model, run)
            except Exception:
                logger.exception("Unexpected failure for %s", tag)
                outcome = {"ok": False, "cost_usd": 0.0}
            budget.add(outcome["cost_usd"])
            with lock:
                counter["n"] += 1
                print(f"[{counter['n']}/{len(pending)}] {tag}: "
                      f"{'ok' if outcome['ok'] else 'FAILED'} (${outcome['cost_usd']:.4f})")
                rebuild_results_csv()
            if budget.exceeded:
                print(f"Budget of ${args.budget_usd:.2f} reached (spent ${budget.spent_usd:.4f}); "
                      "finishing in-flight extractions and stopping.")

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            list(executor.map(work, pending))
        rebuild_results_csv()
        rebuild_agreement_csv()
        print(f"\nSpent in this invocation: ${budget.spent_usd:.4f}")

    try:
        write_best(args.best_doc, args.best_file)
    except ValueError as exc:
        if args.select_best_only:
            raise SystemExit(str(exc))
        print(f"\nBest requirements not (re)selected: {exc}")


if __name__ == "__main__":
    main()
