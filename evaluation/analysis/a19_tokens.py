"""A19. Tokens per model and experiment, and a check of the prices of tab:models against the stored costs.

Sums the input, output and reasoning tokens of every stored LLM call of the paper: the extraction grid, every
generation and repair of E1-E7 and R3, and every judgment. The calls follow the cost accounting of
make_paper_tables._cost: the generations of the E3 bank were produced before this study and are
not counted. Calls that failed or were lost before being stored are not in the results.

Price check: tokens x the registry price (core/models.py, the price column of tab:models) against the cost that
OpenRouter returned for the same calls. Output tokens include the reasoning tokens (OpenRouter bills them as output).

    python -m evaluation.analysis.a19_tokens
"""

from __future__ import annotations

import pandas as pd

from core.config import RESULTS_DIR
from core.models import SUPPORTED_MODELS
from evaluation.analysis.common import fmt, jsonl, md_table, model_sort, out_dir, write_long_table, write_md

TOK = ["input_tokens", "output_tokens", "reasoning_tokens"]
# phase directory -> (experiment, results CSV or None)
PHASES = {"pipeline": ("E1", "pipeline_results.csv"), "ablation": ("E2", "ablation_results.csv"),
          "ablation_stress": ("E3", "ablation_results.csv"), "ablation_stress_revision": ("E3", "ablation_results.csv"),
          "c0_minimal_prompt": ("E4", "pipeline_results.csv"), "jwst_c0_bank": ("E4", "pipeline_results.csv"),
          "jwst_pipeline": ("E5", "pipeline_results.csv"), "jwst_v1_bank": ("E6", "pipeline_results.csv"),
          "jwst_v1_bank_flashlite": ("E6", "pipeline_results.csv"), "input_control_sol": ("R3", "pipeline_results.csv")}
OLD_BANKS = ("ablation_stress", "ablation_stress_revision", "jwst_v1_bank", "jwst_v1_bank_flashlite")
JUDGE_EXPERIMENT = {"nodoc_control/pipeline_c4": "E1", "second_judge/pipeline_c4": "E1",
                    "nodoc_control/jwst_pipeline_c4": "E5", "nodoc_control/c0_minimal_prompt": "E4",
                    "pilot_repair/nodoc": "E7"}


def usage_row(experiment: str, component: str, llm: str, u: dict) -> dict:
    return {"experiment": experiment, "component": component, "llm": llm, "calls": u.get("llm_calls", 1),
            **{k: u[k] for k in TOK}, "cost_usd": u["cost_usd"]}


def calls() -> pd.DataFrame:
    rows = []
    ext = pd.read_csv(RESULTS_DIR / "extraction" / "extraction_results.csv")
    for r in ext.itertuples():
        rows.append(usage_row("Extraction", "extraction", r.llm, {"llm_calls": r.llm_calls, "input_tokens": r.input_tokens,
                              "output_tokens": r.output_tokens, "reasoning_tokens": r.reasoning_tokens,
                              "cost_usd": r.cost_usd}))
    for phase, (exp, results) in PHASES.items():
        gens = jsonl(RESULTS_DIR / phase / "generations.jsonl")
        gen_usage = {}
        for g in gens:
            gen_usage[(g["llm"], g["run"], g["category"])] = g["usage"]
            if phase not in OLD_BANKS or "git_commit" in g:
                rows.append(usage_row(exp, "generation", g["llm"], g["usage"]))
        df = pd.read_csv(RESULTS_DIR / phase / results)
        for r in df.itertuples():  # a results row = shared generation + the repair calls of its condition
            g = gen_usage[(r.llm, r.run, r.category)]
            rep = {k: getattr(r, k) - g[k] for k in TOK + ["cost_usd"]}
            rep["llm_calls"] = r.llm_calls - g["llm_calls"]
            if rep["llm_calls"] > 0:
                rows.append(usage_row(exp, "repair", r.llm, rep))
    pr = pd.read_csv(RESULTS_DIR / "pilot_repair" / "pilot_repair_results.csv")
    for r in pr[pr.llm_calls > 0].itertuples():
        rows.append(usage_row("E7", "repair", r.llm, {"llm_calls": r.llm_calls, "input_tokens": r.input_tokens,
                              "output_tokens": r.output_tokens, "reasoning_tokens": r.reasoning_tokens,
                              "cost_usd": r.cost_usd}))
    for path in sorted(RESULTS_DIR.rglob("ljs/*/judgments.jsonl")):
        rel = path.parent.parent.parent.relative_to(RESULTS_DIR).as_posix()
        exp = JUDGE_EXPERIMENT.get(rel) or PHASES[rel][0]
        for j in jsonl(path):
            rows.append(usage_row(exp, "judge", j["judge"], j["usage"]))
    return pd.DataFrame(rows)


def main() -> None:
    out = out_dir("a19_tokens")
    df = calls()
    by_exp = df.groupby(["experiment", "component", "llm"], as_index=False)[["calls", *TOK, "cost_usd"]].sum()
    by_exp.to_csv(out / "tokens_by_experiment.csv", index=False)
    by_model = df.groupby("llm", as_index=False)[["calls", *TOK, "cost_usd"]].sum()
    check = []
    for r in by_model.itertuples():
        s = SUPPORTED_MODELS[r.llm]
        priced = (r.input_tokens * s.input_usd_per_m + r.output_tokens * s.output_usd_per_m) / 1e6
        check.append({"price_in": s.input_usd_per_m, "price_out": s.output_usd_per_m, "cost_from_prices": priced,
                      "cost_ratio": r.cost_usd / priced})
    by_model = pd.concat([by_model, pd.DataFrame(check)], axis=1)
    by_model.to_csv(out / "tokens_by_model.csv", index=False)
    order = ["Extraction", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "R3"]
    comp = ["extraction", "generation", "repair", "judge"]
    rows = []
    for exp in order:
        sub = by_exp[by_exp.experiment == exp]
        for c in comp:
            for llm in [x for x in model_sort(sub.llm) if x in set(sub[sub.component == c].llm)] + \
                    sorted(set(sub[sub.component == c].llm) - set(model_sort(sub.llm))):
                r = sub[(sub.component == c) & (sub.llm == llm)].iloc[0]
                rows.append([exp, c, f"\\llm{{{llm}}}", f"{int(r.calls):,}".replace(",", "{,}"),
                             fmt(r.input_tokens / 1e6, 2), fmt(r.output_tokens / 1e6, 2),
                             fmt(r.reasoning_tokens / 1e6, 2), fmt(r.cost_usd, 2)])
    write_long_table(
        out / "tab_sup_tokens.tex",
        "Tokens and cost of every stored LLM call, per experiment, component and model. Tokens in millions; output "
        "includes reasoning. Cost: USD returned by OpenRouter. E3: the bank generations predate the study and are not "
        "counted. Calls that failed or were not stored are not included.",
        "tab:sup_tokens", ["Exp.", "Component", "Model", "Calls", "Input (M)", "Output (M)", "Reasoning (M)", "Cost"],
        "lllrrrrr", rows)
    write_md(out / "summary.md", "A19. Tokens per model and experiment",
             ["Every stored call of the paper (extraction, generation, repair, judges). Output tokens include "
              "reasoning tokens. cost_ratio = cost returned by OpenRouter / (tokens x registry price).",
              md_table(by_model), "## By experiment", md_table(by_exp)])
    for r in by_model.itertuples():
        print(f"  {r.llm:24s} in {r.input_tokens / 1e6:8.2f}M out {r.output_tokens / 1e6:7.2f}M "
              f"cost {fmt(r.cost_usd, 2):>6s} ratio {r.cost_ratio:.3f}")


if __name__ == "__main__":
    main()
