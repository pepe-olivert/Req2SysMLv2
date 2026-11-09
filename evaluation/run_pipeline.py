"""Phase 2: SysML v2 generation + repair (C1 vs C4) for every model, on the best requirements JSON.

Never extracts: it reads results/extraction/best_requirements.json, so every model
is evaluated on exactly the same requirements.

    python -m evaluation.run_pipeline --models all --conditions C1 C4 --runs 3 --dry-run
    python -m evaluation.run_pipeline --models all --conditions C1 C4 --runs 3
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from core.agents.agent2.logic import CONDITIONS, SysMLAgent
from core.agents.agent2.generation_prompts import GENERATION_PROMPTS
from core.models import get_model

from evaluation.common import (
    ABLATION_DIR,
    ABLATION_STRESS_DIR,
    BEST_REQUIREMENTS_PATH,
    PIPELINE_DIR,
    Budget,
    CsvAppender,
    JsonlAppender,
    add_models_arg,
    load_best_requirements,
    parse_models,
    provenance,
    read_csv_keys,
    read_csv_rows,
    setup_logging,
    slugify,
    text_sha256,
    write_run_manifest,
)


logger = logging.getLogger(__name__)

RESULT_COLUMNS = (
    "pdf", "llm", "condition", "run", "category", "num_requirements",
    "converged", "iterations", "initial_errors", "final_errors", "error_reduction_pct", "stagnation", "guard_retries", "guard_rejections",
    "rcs", "srs",
    "llm_calls", "input_tokens", "output_tokens", "reasoning_tokens", "latency_s", "cost_usd",
    "generation_cost_usd", "requirements_sha256",
)
ERROR_COLUMNS = (
    "pdf", "llm", "condition", "run", "category", "iteration", "error_category", "priority",
    "line", "column", "message", "resolved_next_iteration",
)
TRACE_COLUMNS = ("llm", "condition", "run", "category", "iteration", "error_count")
KEY_COLUMNS = ("pdf", "llm", "condition", "run", "category")

# Published E1-E3 results: complete, never extended (new runs go to a new --out-dir).
FROZEN_RESULT_DIRS = {d.resolve() for d in (PIPELINE_DIR, ABLATION_DIR, ABLATION_STRESS_DIR)}
# SHA-256 of the requirements of E1-E3. Rows with it in those directories are the published results.
PUBLISHED_REQUIREMENTS_SHA256 = "b5da76f32ac036f465e56cfbd3733fcc642218c6f312aff3178fdbd15a8ab377"

# Default token profile for --dry-run when no observed results exist yet.
# Output tokens include reasoning tokens.
_PROFILE_GEN_OUTPUT = 4000
_PROFILE_BROKEN_SHARE = 0.15          # share of generations that fail validation
_PROFILE_REPAIR_CALLS_IF_BROKEN = 4.0  # repair calls for an invalid generation
_PROFILE_KB_TOKENS = 1500
_PROFILE_CODE_TOKENS = 1500


@dataclass
class PhaseOutputs:
    out_dir: Path
    results_name: str

    def __post_init__(self) -> None:
        lock = threading.RLock()  # one lock for every file: a category is written atomically
        self.results = CsvAppender(self.out_dir / self.results_name, RESULT_COLUMNS, lock)
        self.errors = CsvAppender(self.out_dir / "errors.csv", ERROR_COLUMNS, lock)
        self.trace = CsvAppender(self.out_dir / "iteration_trace.csv", TRACE_COLUMNS, lock)
        self.repairs = JsonlAppender(self.out_dir / "repairs.jsonl", lock)
        self.models = JsonlAppender(self.out_dir / "sysml_models.jsonl", lock)
        self.generations = JsonlAppender(self.out_dir / "generations.jsonl", lock)
        self.valid_dir = self.out_dir / "valid_models"
        self.lock = lock


# ---------------------------------------------------------------------------
# Rows
# ---------------------------------------------------------------------------
def _error_key(error: dict) -> tuple:
    return (error["line"], error["column"], error["message"])


def build_error_rows(base: dict, iteration_errors: list[dict]) -> list[dict]:
    rows = []
    for index, snapshot in enumerate(iteration_errors):
        nxt = iteration_errors[index + 1]["errors"] if index + 1 < len(iteration_errors) else None
        next_keys = {_error_key(e) for e in nxt} if nxt is not None else None
        for error in snapshot["errors"]:
            rows.append({
                **base,
                "iteration": snapshot["iteration"],
                "error_category": error["error_category"],
                "priority": error["priority"],
                "line": error["line"],
                "column": error["column"],
                "message": error["message"],
                "resolved_next_iteration": next_keys is not None and _error_key(error) not in next_keys,
            })
    return rows


def _metrics(semantic: dict) -> dict:
    return {
        "rcs": semantic["requirement_coverage"]["rcs"],
        "srs": semantic["structural_richness"]["srs"],
    }


def load_generations(path: Path, sha256: str) -> dict[tuple[str, str, str], dict]:
    generations: dict[tuple[str, str, str], dict] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                if record.get("requirements_sha256") == sha256:
                    generations[(record["llm"], str(record["run"]), record["category"])] = record
    return generations


def generate_once(*, client, model: str, run: int, category: str, requirements: list[str],
                  sha256: str, outputs: PhaseOutputs, generation_prompt: str = "guided") -> dict:
    """Shared first generation of a (model, run, category): every condition starts from this code."""
    from core.evaluation.semantic_eval import evaluate_model

    agent = SysMLAgent(client)
    raw_output = agent.generate_sysml(json.dumps({category: requirements}, ensure_ascii=False, indent=2),
                                      system_prompt=GENERATION_PROMPTS[generation_prompt])
    usage = agent.llm_client.snapshot()
    semantic = evaluate_model({category: requirements}, agent.clean_sysml(raw_output))
    record = {
        "llm": model, "run": run, "category": category, "requirements_sha256": sha256,
        "raw_output": raw_output, "usage": usage, "metrics": _metrics(semantic),
        **provenance(client.model, sha256),
        "generation_prompt": generation_prompt,
        "generation_prompt_sha256": text_sha256(GENERATION_PROMPTS[generation_prompt]),
    }
    outputs.generations.append_many([record])
    return record


def process_condition(*, client, generation: dict, pdf: str, model: str, condition: str,
                      run: int, category: str, requirements: list[str], sha256: str, max_iterations: int,
                      outputs: PhaseOutputs) -> dict:
    """Repairs the shared generation under one condition and writes every output of that row."""
    from core.evaluation.semantic_eval import evaluate_model

    agent = SysMLAgent(client)
    result = agent.run_category(category, requirements, CONDITIONS[condition], max_iterations,
                                initial_code=generation["raw_output"])
    repair_usage = result["usage"]
    spent = repair_usage["cost_usd"]
    if result["sysml_code"] == agent.clean_sysml(generation["raw_output"]):
        metrics = generation["metrics"]  # same code as the shared generation: reuse its scores
    else:
        metrics = _metrics(evaluate_model({category: requirements}, result["sysml_code"]))

    # Row usage = standalone cost of the condition: shared generation + its own repair calls.
    gen_usage = generation["usage"]
    usage = {k: gen_usage[k] + repair_usage[k] for k in gen_usage}
    key = {"pdf": pdf, "llm": model, "condition": condition, "run": run, "category": category}
    row = {
        **key,
        "num_requirements": len(requirements),
        "converged": result["converged"],
        "iterations": result["iterations_used"],
        "initial_errors": result["initial_error_count"],
        "final_errors": result["final_error_count"],
        "error_reduction_pct": result["error_reduction_pct"],
        "stagnation": result["stagnation_detected"],
        "guard_retries": result["guard_retries"],
        "guard_rejections": result["guard_rejections"],
        **metrics,
        "llm_calls": usage["llm_calls"],
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "reasoning_tokens": usage["reasoning_tokens"],
        "latency_s": usage["latency_s"],
        "cost_usd": usage["cost_usd"],
        "generation_cost_usd": gen_usage["cost_usd"],
        "requirements_sha256": sha256,
    }
    trace_rows = [
        {"llm": model, "condition": condition, "run": run, "category": category,
         "iteration": snap["iteration"], "error_count": len(snap["errors"])}
        for snap in result["iteration_errors"]
    ]
    model_record = {
        **key,
        **provenance(client.model, sha256),
        "requirements": requirements,
        "sysml_code": result["sysml_code"],
        "valid": result["final_error_count"] == 0,
        "final_errors": result["final_errors"],
        "initial_errors": result["initial_error_count"],
        "iterations": result["iterations_used"],
        **metrics,
    }

    with outputs.lock:
        # The results row goes last: its presence is the resume marker.
        outputs.errors.append_many(build_error_rows(key, result["iteration_errors"]))
        outputs.trace.append_many(trace_rows)
        outputs.repairs.append_many([{**key, **provenance(client.model, sha256, repair["timestamp_utc"]), **repair}
                                     for repair in result["repairs"]])
        outputs.models.append_many([model_record])
        if model_record["valid"]:
            path = outputs.valid_dir / model / condition / f"run{run}" / f"{slugify(category)}.sysml"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(result["sysml_code"], encoding="utf-8")
        outputs.results.append(row)

    return {"row": row, "spent": spent}


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------
def print_estimate(groups: dict[tuple, dict], generated: set, observed_rows: list[dict]) -> None:
    import tiktoken

    from core.agents.agent2.prompts import FIX_SYSTEM_PROMPT, GENERATE_SYSTEM_PROMPT

    enc = tiktoken.get_encoding("cl100k_base")
    n_tokens = lambda text: len(enc.encode(text))  # noqa: E731
    gen_prompt = n_tokens(GENERATE_SYSTEM_PROMPT) + 40
    fix_prompt = n_tokens(FIX_SYSTEM_PROMPT) + 60

    def mean(values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    obs_gen: dict[str, list[float]] = {}
    obs_repair: dict[tuple[str, str], list[float]] = {}
    for r in observed_rows:
        obs_gen.setdefault(r["llm"], []).append(float(r["generation_cost_usd"]))
        obs_repair.setdefault((r["llm"], r["condition"]), []).append(
            float(r["cost_usd"]) - float(r["generation_cost_usd"]))

    summary: dict[tuple[str, str], dict] = {}
    for (model, run, category), info in groups.items():
        spec = get_model(model)
        req_tokens = n_tokens(json.dumps({category: info["reqs"]}, ensure_ascii=False, indent=2))
        if (model, str(run), category) not in generated:
            s = summary.setdefault((model, "generation"), {"n": 0, "cost": 0.0, "basis": "profile"})
            s["n"] += 1
            observed = mean(obs_gen.get(model, []))
            if observed is not None:
                s["cost"] += observed
                s["basis"] = f"observed (n={len(obs_gen[model])})"
            else:
                s["cost"] += ((gen_prompt + req_tokens) * spec.input_usd_per_m
                              + _PROFILE_GEN_OUTPUT * spec.output_usd_per_m) / 1e6
        for condition in info["conditions"]:
            if not CONDITIONS[condition].do_repair:
                continue
            s = summary.setdefault((model, condition), {"n": 0, "cost": 0.0, "basis": "profile"})
            s["n"] += 1
            observed = mean(obs_repair.get((model, condition), []))
            if observed is not None:
                s["cost"] += observed
                s["basis"] = f"observed (n={len(obs_repair[(model, condition)])})"
                continue
            kb = _PROFILE_KB_TOKENS if CONDITIONS[condition].use_kb else 0
            calls = _PROFILE_BROKEN_SHARE * _PROFILE_REPAIR_CALLS_IF_BROKEN
            s["cost"] += calls * ((fix_prompt + kb + 2 * _PROFILE_CODE_TOKENS) * spec.input_usd_per_m
                                  + _PROFILE_GEN_OUTPUT * spec.output_usd_per_m) / 1e6

    print(f"\n{'model':<24}{'step':<12}{'tasks':>7}{'llm $':>10}  basis")
    total = 0.0
    for (model, step), s in summary.items():
        total += s["cost"]
        print(f"{model:<24}{step:<12}{s['n']:>7}{s['cost']:>10.4f}  {s['basis']}")
    print(f"\nEstimated total for pending work: ${total:.4f} (rough; repairs are only needed for invalid generations)")


# ---------------------------------------------------------------------------
# Engine (shared with run_ablation)
# ---------------------------------------------------------------------------
def run_phase(
    *,
    out_dir: Path,
    results_name: str,
    requirements_path: Path,
    models: list[str],
    conditions: list[str],
    runs: int,
    max_iterations: int,
    max_categories: int | None,
    workers: int,
    budget_usd: float | None,
    dry_run: bool,
    max_rpm: float | None = None,
    generation_prompt: str = "guided",
) -> None:
    """Paired design: each (model, run, category) is generated once and every condition repairs that same code."""
    from core.llm_client import create_client

    prompt_sha256 = text_sha256(GENERATION_PROMPTS[generation_prompt])

    best = load_best_requirements(requirements_path)
    requirements: dict[str, list[str]] = best["requirements"]
    sha256 = best["sha256"]
    pdf = best.get("source", {}).get("doc", "unknown")
    categories = list(requirements.items())[:max_categories] if max_categories else list(requirements.items())

    results_path = out_dir / results_name
    done = read_csv_keys(results_path, KEY_COLUMNS)
    generations = load_generations(out_dir / "generations.jsonl", sha256)
    groups: dict[tuple, dict] = {}
    total_tasks = 0
    # Models innermost: the rpm limit is per model, so interleaving keeps every model's limit busy at once.
    for run in range(1, runs + 1):
        for category, reqs in categories:
            for model in models:
                total_tasks += len(conditions)
                todo = [c for c in conditions if (pdf, model, c, str(run), category) not in done]
                if todo:
                    groups[(model, run, category)] = {"reqs": reqs, "conditions": todo}
    pending = sum(len(g["conditions"]) for g in groups.values())
    mixed = {g.get("generation_prompt_sha256") for g in generations.values()} - {None, prompt_sha256}
    if mixed:
        raise SystemExit(f"{out_dir}/generations.jsonl has generations from another prompt; "
                         f"use a new --out-dir for --generation-prompt {generation_prompt}. Nothing was run.")
    if (pending and Path(out_dir).resolve() in FROZEN_RESULT_DIRS
            and any(r.get("requirements_sha256") == PUBLISHED_REQUIREMENTS_SHA256 for r in read_csv_rows(results_path))):
        raise SystemExit(f"{out_dir} holds the published E1-E3 results and is frozen: "
                         f"write new runs to a new --out-dir. Nothing was run.")
    print(
        f"Requirements: {requirements_path} (doc={pdf}, sha256={sha256[:12]}..., "
        f"{len(categories)}/{len(requirements)} categories)\n"
        f"Models: {', '.join(models)} | conditions: {', '.join(conditions)} | runs: {runs} | "
        f"generation prompt: {generation_prompt} ({prompt_sha256[:12]}...)\n"
        f"Paired design: one generation per (model, run, category), repaired under every condition\n"
        f"Tasks: {total_tasks} total, {total_tasks - pending} already done, {pending} pending "
        f"({len(generations)} generations already stored)"
    )

    if dry_run:
        observed = [r for r in read_csv_rows(results_path) if r.get("requirements_sha256") == sha256]
        print_estimate(groups, set(generations), observed)
        return
    if not groups:
        return

    outputs = PhaseOutputs(out_dir, results_name)
    budget = Budget(budget_usd)
    clients = {model: create_client(model, max_rpm=max_rpm) for model in models}
    write_run_manifest(
        out_dir, requirements_path=str(requirements_path), requirements_sha256=sha256, pdf=pdf,
        n_categories=len(categories), n_requirements=sum(len(r) for _, r in categories),
        models={m: c.model for m, c in clients.items()},
        reasoning_effort={m: c.spec.reasoning_effort for m, c in clients.items()},
        conditions=conditions, runs=runs, max_iterations=max_iterations, budget_usd=budget_usd,
        generation_prompt=generation_prompt, generation_prompt_sha256=prompt_sha256,
    )
    counter = {"n": 0}
    counter_lock = threading.Lock()

    def report(tag: str, message: str) -> None:
        with counter_lock:
            counter["n"] += 1
            print(f"[{counter['n']}/{pending}] {tag}: {message}")

    def work(item: tuple) -> None:
        (model, run, category), info = item
        if budget.exceeded:
            return
        generation = generations.get((model, str(run), category))
        if generation is None:
            try:
                generation = generate_once(
                    client=clients[model], model=model, run=run, category=category,
                    requirements=info["reqs"], sha256=sha256, outputs=outputs,
                    generation_prompt=generation_prompt,
                )
            except Exception:
                logger.exception("Generation failed llm=%s run=%d cat=%s", model, run, category)
                for condition in info["conditions"]:
                    report(f"[{model}][{condition}][run {run}] {category[:60]}", "FAILED (generation; retried on resume)")
                return
            budget.add(generation["usage"]["cost_usd"])
        for condition in info["conditions"]:
            tag = f"[{model}][{condition}][run {run}] {category[:60]}"
            try:
                outcome = process_condition(
                    client=clients[model], generation=generation, pdf=pdf,
                    model=model, condition=condition, run=run, category=category, requirements=info["reqs"],
                    sha256=sha256, max_iterations=max_iterations, outputs=outputs,
                )
            except Exception:
                logger.exception("Repair/evaluation failed llm=%s cond=%s run=%d cat=%s", model, condition, run, category)
                report(tag, "FAILED (see log; will be retried on resume)")
                continue
            budget.add(outcome["spent"])
            r = outcome["row"]
            report(tag, f"conv={r['converged']} err {r['initial_errors']}->{r['final_errors']} iters={r['iterations']} "
                        f"spent ${outcome['spent']:.4f}")
        if budget.exceeded:
            print(f"Budget of ${budget_usd:.2f} reached; finishing in-flight categories and stopping.")

    def guarded(item: tuple) -> None:
        try:
            work(item)
        except Exception:
            logger.exception("Unexpected failure for %s", item[0])

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        list(executor.map(guarded, groups.items()))
    print(f"\nSpent in this invocation: ${budget.spent_usd:.4f} (generation+repair)")


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--requirements", type=Path, default=BEST_REQUIREMENTS_PATH)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--max-categories", type=int, default=None, help="Only the first N categories (smoke tests).")
    parser.add_argument("--workers", type=int, default=4, help="Categories processed in parallel.")
    parser.add_argument("--budget-usd", type=float, default=None,
                        help="Stop after the in-flight categories once this much (gen+repair) is spent.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned calls and estimated cost, then exit.")
    parser.add_argument("--max-rpm", type=float, default=None,
                        help="Max requests per minute per model (e.g. 18 for OpenRouter's 20 rpm new-account limit).")
    parser.add_argument("-v", "--verbose", action="store_true")


def validate_common(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.runs <= 0:
        parser.error("--runs must be > 0")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_models_arg(parser)
    parser.add_argument("--conditions", nargs="+", choices=list(CONDITIONS), default=["C1", "C4"])
    parser.add_argument("--out-dir", type=Path, default=PIPELINE_DIR,
                        help="Phase directory (default: results/pipeline).")
    parser.add_argument("--generation-prompt", choices=list(GENERATION_PROMPTS), default="guided")
    add_common_args(parser)
    args = parser.parse_args()
    models = parse_models(parser, args.models)
    validate_common(parser, args)
    setup_logging(args.verbose)

    run_phase(
        out_dir=args.out_dir, results_name="pipeline_results.csv", requirements_path=args.requirements,
        models=models, conditions=args.conditions, runs=args.runs, max_iterations=args.max_iterations,
        max_categories=args.max_categories, workers=args.workers,
        budget_usd=args.budget_usd, dry_run=args.dry_run, max_rpm=args.max_rpm,
        generation_prompt=args.generation_prompt,
    )


if __name__ == "__main__":
    main()
