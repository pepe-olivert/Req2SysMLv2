"""A5. Requirements judged not applicable, per experiment, model, condition and judge.

A not_applicable requirement is left out of every LJS score, so a high share would inflate the LJS. Share =
not_applicable / requirements judged, over the judged rows of each judge directory (missing judgments left out).

    python -m evaluation.analysis.a05_not_applicable
"""

from __future__ import annotations

import pandas as pd

from evaluation.analysis.common import (CONDITION_ORDER, fmt, load_ljs, md_table, model_sort, out_dir, tex, write_md,
                                        write_long_table)

JUDGE_DIRS = [
    ("E1", "EIRENE", "gpt-4o-mini", "with doc", "pipeline/ljs/gpt-4o-mini"),
    ("E1", "EIRENE", "gpt-4o-mini", "no doc", "nodoc_control/pipeline_c4/ljs/gpt-4o-mini"),
    ("E1", "EIRENE", "claude-haiku-5.5", "with doc", "second_judge/pipeline_c4/ljs/claude-haiku-5.5"),
    ("E1", "EIRENE", "claude-haiku-5.5", "no doc", "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5"),
    ("E2", "EIRENE", "gpt-4o-mini", "with doc", "ablation/ljs/gpt-4o-mini"),
    ("E3 bank", "EIRENE", "gpt-4o-mini", "with doc", "ablation_stress/ljs/gpt-4o-mini"),
    ("E3 bank", "EIRENE", "gpt-4o-mini", "with doc", "ablation_stress_revision/ljs/gpt-4o-mini"),
    ("C0", "EIRENE", "gpt-4o-mini", "with doc", "c0_minimal_prompt/ljs/gpt-4o-mini"),
    ("C0", "EIRENE", "gpt-4o-mini", "no doc", "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini"),
    ("C0", "EIRENE", "claude-haiku-5.5", "no doc", "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5"),
    ("R3", "EIRENE", "gpt-4o-mini", "with doc", "input_control_sol/ljs/gpt-4o-mini"),
    ("E5", "JWST", "gpt-4o-mini", "with doc", "jwst_pipeline/ljs/gpt-4o-mini"),
    ("E5", "JWST", "gpt-4o-mini", "no doc", "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini"),
    ("E5", "JWST", "claude-haiku-5.5", "no doc", "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"),
    ("JWST bank", "JWST", "gpt-4o-mini", "with doc", "jwst_v1_bank/ljs/gpt-4o-mini"),
    ("JWST bank", "JWST", "gpt-4o-mini", "with doc", "jwst_v1_bank_flashlite/ljs/gpt-4o-mini"),
]


def main() -> None:
    out = out_dir("a05_not_applicable")
    frames = []
    for exp, doc, judge, docflag, d in JUDGE_DIRS:
        lj = load_ljs(d)
        if lj is not None:
            frames.append(lj.assign(experiment=exp, document=doc, judge=judge, doc=docflag))
    df = pd.concat(frames, ignore_index=True).drop_duplicates(["experiment", "judge", "doc", "pdf", "llm", "condition",
                                                               "run", "category"])
    agg = (df.groupby(["experiment", "document", "judge", "doc", "llm", "condition"])
           .agg(rows=("ljs", "size"), requirements=("n_requirements", "sum"), na=("n_not_applicable", "sum"),
                rows_with_na=("n_not_applicable", lambda s: (s > 0).sum()))
           .reset_index())
    agg["na_pct"] = (agg.na / agg.requirements * 100).round(2)
    agg.to_csv(out / "not_applicable.csv", index=False)
    by_judge = agg.groupby(["judge", "doc"]).agg(requirements=("requirements", "sum"), na=("na", "sum")).reset_index()
    by_judge["na_pct"] = (by_judge.na / by_judge.requirements * 100).round(2)
    by_judge.to_csv(out / "not_applicable_by_judge.csv", index=False)

    rows = []
    for exp in ["E1", "C0", "R3", "E5"]:
        sub = agg[(agg.experiment == exp) & agg.condition.isin(["C1", "C4"])]
        for (judge, docflag), g in sub.groupby(["judge", "doc"], sort=False):
            for llm in model_sort(g.llm):
                for c in [c for c in CONDITION_ORDER if c in set(g[g.llm == llm].condition)]:
                    r = g[(g.llm == llm) & (g.condition == c)].iloc[0]
                    rows.append([exp, tex(judge), docflag, tex(llm), c, str(int(r.requirements)), str(int(r.na)),
                                 fmt(r.na_pct, 2)])
    write_long_table(
        out / "tab_not_applicable.tex",
        "Requirements judged not applicable (excluded from the LJS), per experiment, judge, version of the "
        "models (with or without doc comments), model and condition: count and share of the judged requirements.",
        "tab:not_applicable", ["Exp.", "Judge", "Doc", "Model", "Cond.", "Req.", "N/A", "\\%"], "lllllrrr", rows)
    write_md(out / "summary.md", "A5. Requirements judged not applicable", [md_table(by_judge), md_table(agg)])


if __name__ == "__main__":
    main()
