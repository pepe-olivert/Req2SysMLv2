"""R11: repair loop with the SysML v2 Pilot Implementation (2024-04.1) as validator (condition C4P).

Input: the final C4 models of E1 (results/pipeline) and E5 (results/jwst_pipeline) of gpt-6-luna and
gemini-3.5-flash-lite, valid for our ANTLR validator, after the deterministic import normalisation (a) of A1b
(connector ends are NOT rewritten: the repair has to fix them). The same model that generated a model repairs
it, with core/agents/agent2/pilot_repair.py (one Pilot diagnostic per call, no router, no knowledge base, guard
on content and on ANTLR validity, N = 10). Writes results/pilot_repair/ (resumable; provenance in every record).

    python -m evaluation.run_pilot_repair --sets E5 --models gpt-6-luna --limit 20 --dry-run
    python -m evaluation.run_pilot_repair --sets E5 --models gpt-6-luna --limit 20 --workers 6 --max-rpm 18 --budget-usd 1
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core.agents.agent2.logic import SysMLAgent
from core.agents.agent2.pilot_repair import FIX_PILOT_SYSTEM_PROMPT, run_pilot_repair
from core.config import RESULTS_DIR
from evaluation.analysis.a01b_boilerplate import fix_imports
from evaluation.common import (Budget, CsvAppender, JsonlAppender, provenance, read_csv_keys, setup_logging,
                               text_sha256, write_run_manifest)

logger = logging.getLogger(__name__)
OUT = RESULTS_DIR / "pilot_repair"
SOURCES = {"E1": RESULTS_DIR / "pipeline" / "sysml_models.jsonl", "E5": RESULTS_DIR / "jwst_pipeline" / "sysml_models.jsonl"}
KEYS = ("set", "pdf", "llm", "run", "category")
COLUMNS = (*KEYS, "condition", "num_requirements", "pilot_initial_errors", "pilot_final_errors", "converged",
           "iterations", "stagnation", "guard_retries_content", "guard_retries_antlr", "guard_rejections_content",
           "guard_rejections_antlr", "llm_calls", "input_tokens", "output_tokens", "reasoning_tokens", "latency_s",
           "cost_usd", "requirements_sha256")


def load_inputs(sets: list[str], models: list[str]) -> list[dict]:
    rows = []
    for s in sets:
        last = {}
        for line in SOURCES[s].read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r["condition"] == "C4" and r["llm"] in models:
                    last[(r["llm"], int(r["run"]), r["category"])] = r
        for r in last.values():
            if r.get("valid"):
                rows.append({**r, "set": s, "run": int(r["run"]), "input_code": fix_imports(r["sysml_code"])})
    # Interleave models: the rate limit is per model, so both models are repaired at the same time.
    rows.sort(key=lambda r: (r["run"], r["category"], r["set"], r["llm"]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sets", nargs="+", choices=list(SOURCES), default=list(SOURCES))
    parser.add_argument("--models", nargs="+", default=["gpt-6-luna", "gemini-3.5-flash-lite"])
    parser.add_argument("--limit", type=int, default=None, help="Only the first N inputs per (set, model) (pilot).")
    parser.add_argument("--pilot-release", type=Path, default=Path.home() / "tools" / "pilot" / "2024-04.1")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--workers", type=int, default=6, help="Models repaired in parallel (= Pilot JVMs).")
    parser.add_argument("--max-rpm", type=float, default=None)
    parser.add_argument("--budget-usd", type=float, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    setup_logging(args.verbose)

    inputs = load_inputs(args.sets, args.models)
    if args.limit:
        picked, count = [], {}
        for r in inputs:
            k = (r["set"], r["llm"])
            if count.get(k, 0) < args.limit:
                picked.append(r)
                count[k] = count.get(k, 0) + 1
        inputs = picked
    done = read_csv_keys(OUT / "pilot_repair_results.csv", KEYS)
    pending = [r for r in inputs if (r["set"], r["pdf"], r["llm"], str(r["run"]), r["category"]) not in done]
    print(f"Inputs: {len(inputs)} ({len(inputs) - len(pending)} done, {len(pending)} pending); sets {args.sets}; "
          f"models {args.models}; Pilot {args.pilot_release.name}")
    if args.dry_run or not pending:
        return

    from core.llm_client import create_client
    from core.validate.pilot import PilotValidator

    pilot = PilotValidator(args.pilot_release, size=args.workers)
    lock = threading.RLock()
    results = CsvAppender(OUT / "pilot_repair_results.csv", COLUMNS, lock)
    repairs = JsonlAppender(OUT / "repairs.jsonl", lock)
    models_out = JsonlAppender(OUT / "sysml_models.jsonl", lock)
    traces = JsonlAppender(OUT / "iteration_trace.jsonl", lock)
    clients = {m: create_client(m, max_rpm=args.max_rpm) for m in args.models}
    write_run_manifest(OUT, sets=args.sets, models={m: c.model for m, c in clients.items()},
                       reasoning_effort={m: c.spec.reasoning_effort for m, c in clients.items()},
                       pilot_release=args.pilot_release.name, max_iterations=args.max_iterations,
                       system_prompt_sha256=text_sha256(FIX_PILOT_SYSTEM_PROMPT), n_pending=len(pending),
                       budget_usd=args.budget_usd, limit=args.limit)
    budget = Budget(args.budget_usd)
    counter = {"n": 0}

    def work(r: dict) -> None:
        if budget.exceeded:
            return
        tag = f"[{r['set']}][{r['llm']}][run {r['run']}] {r['category'][:50]}"
        try:
            agent = SysMLAgent(clients[r["llm"]])
            res = run_pilot_repair(agent, pilot, r["input_code"], args.max_iterations)
        except Exception:
            logger.exception("C4P failed for %s", tag)
            print(f"{tag}: FAILED (retried on resume)")
            return
        u = res["usage"]
        budget.add(u["cost_usd"])
        key = {"set": r["set"], "pdf": r["pdf"], "llm": r["llm"], "run": r["run"], "category": r["category"]}
        prov = provenance(clients[r["llm"]].model, r["requirements_sha256"])
        g = res["guard"]
        row = {**key, "condition": "C4P", "num_requirements": len(r["requirements"]),
               "pilot_initial_errors": res["initial_error_count"], "pilot_final_errors": res["final_error_count"],
               "converged": res["converged"], "iterations": res["iterations_used"],
               "stagnation": res["stagnation_detected"], "guard_retries_content": g["retries_content"],
               "guard_retries_antlr": g["retries_antlr"], "guard_rejections_content": g["rejections_content"],
               "guard_rejections_antlr": g["rejections_antlr"], **{k: u[k] for k in (
                   "llm_calls", "input_tokens", "output_tokens", "reasoning_tokens", "latency_s", "cost_usd")},
               "requirements_sha256": r["requirements_sha256"]}
        with lock:
            repairs.append_many([{**key, **prov, **x} for x in res["repairs"]])
            traces.append_many([{**key, **t} for t in res["trace"]])
            models_out.append_many([{**key, "condition": "C4P", **prov, "requirements": r["requirements"],
                                     "input_code": r["input_code"], "sysml_code": res["sysml_code"],
                                     "valid": True, "initial_errors": res["initial_error_count"],
                                     "pilot_final_errors": res["final_errors"]}])
            results.append(row)
            counter["n"] += 1
            print(f"[{counter['n']}/{len(pending)}] {tag}: Pilot errors {res['initial_error_count']} -> "
                  f"{res['final_error_count']} iters={res['iterations_used']} calls={u['llm_calls']} "
                  f"${u['cost_usd']:.4f}", flush=True)

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            list(ex.map(work, pending))
    finally:
        pilot.close()
    print(f"\nSpent in this invocation: ${budget.spent_usd:.4f}")


if __name__ == "__main__":
    main()
