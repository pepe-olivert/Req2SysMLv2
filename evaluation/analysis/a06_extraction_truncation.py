"""A6. Truncation in the raw extraction.

The extraction runs do not store finish_reason (core/llm_client.py returns it, but run_extraction.py does not
write it), and no max_tokens is sent, so each model's own output limit applies. Truncation is therefore assessed
from what is stored:

- output tokens (reasoning included) of each run against the model's maximum completion tokens on OpenRouter
  (catalogue checked 2026-10-20; 128k for the GPT models, 65,536 for the Gemini models);
- retries: chat_json re-asks when the answer is not a parseable JSON object, which is what a truncated JSON
  answer produces, so llm_calls - chunks counts the unparseable answers of the run.

A run is counted as truncated when a call reaches 95% of the limit. A retry is reported separately: it shows an
unparseable answer (which a truncated JSON would produce), not that the answer was cut.

    python -m evaluation.analysis.a06_extraction_truncation
"""

from __future__ import annotations

import json

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.common import fmt, md_table, model_sort, out_dir, tex, write_md, write_paper_table

MAX_COMPLETION = {"gpt-6-luna": 128000, "gpt-6.1-sol": 128000, "gemini-3.5-flash-lite": 65536,
                  "gemini-3.7-flash": 65536}


def main() -> None:
    out = out_dir("a06_extraction_truncation")
    rows = []
    for f in sorted((RESULTS_DIR / "extraction" / "runs").glob("*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))["metadata"]
        chunks = m.get("strategy_metadata", {}).get("chunks", 1)
        rows.append({"doc": m["doc"], "strategy": m["strategy"], "llm": m["model"], "run": m["run"],
                     "requirements": m["n_requirements"], "chunks": chunks, "llm_calls": m["llm_calls"],
                     "retries": m["llm_calls"] - chunks, "output_tokens": m["output_tokens"],
                     "reasoning_tokens": m["reasoning_tokens"],
                     "output_per_call": m["output_tokens"] / m["llm_calls"],
                     "limit": MAX_COMPLETION[m["model"]]})
    df = pd.DataFrame(rows)
    df["pct_of_limit"] = df.output_per_call / df.limit * 100
    df["truncated"] = df.pct_of_limit >= 95
    df.to_csv(out / "extraction_runs.csv", index=False)
    agg = (df.groupby(["doc", "strategy", "llm"])
           .agg(runs=("run", "size"), requirements=("requirements", "mean"), out_mean=("output_per_call", "mean"),
                out_max=("output_per_call", "max"), pct_max=("pct_of_limit", "max"), retries=("retries", "sum"),
                truncated=("truncated", "sum"))
           .reset_index())
    agg.to_csv(out / "truncation_summary.csv", index=False)

    trows = []
    for doc in ("eirene", "jwst"):
        for strategy in ("raw", "sliding_window"):
            sub = agg[(agg.doc == doc) & (agg.strategy == strategy)]
            for llm in model_sort(sub.llm):
                r = sub[sub.llm == llm].iloc[0]
                trows.append([doc.upper(), tex(strategy.replace("_", " ")), tex(llm), str(int(r.runs)),
                              fmt(r.requirements, 0), fmt(r.out_mean, 0), fmt(r.out_max, 0),
                              f"{MAX_COMPLETION[llm]:,}".replace(",", "{,}"), fmt(r.pct_max, 1), str(int(r.retries)),
                              str(int(r.truncated))])
    write_paper_table(
        out / "tab_extraction_truncation.tex",
        "Output length of the extraction calls against each model's maximum completion tokens (OpenRouter). Out: "
        "output tokens per call, reasoning included (mean and maximum over the runs). Retries: answers that were "
        "not a parseable JSON object (re-asked). Truncated: runs with a call at 95\\% of the limit or more. "
        "finish\\_reason was not stored for the extraction calls.",
        "tab:extraction_truncation", ["Document", "Strategy", "Model", "Runs", "Req.", "Out mean", "Out max",
                                      "Limit", "Max \\% of limit", "Retries", "Truncated"], "lllrrrrrrrr", trows,
        wide=True)
    write_md(out / "summary.md", "A6. Truncation in the raw extraction",
             [f"Runs: {len(df)}; truncated (>= 95% of the limit): {int(df.truncated.sum())}; runs with a JSON retry: "
              f"{int((df.retries > 0).sum())}; highest share of the limit: {df.pct_of_limit.max():.1f}%. "
              "finish_reason is not stored for the extraction calls.", md_table(agg)])


if __name__ == "__main__":
    main()
