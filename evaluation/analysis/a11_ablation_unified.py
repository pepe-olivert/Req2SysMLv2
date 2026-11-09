"""A11. Unified ablation tables over the four error banks.

Banks: E3 (EIRENE, v1 prompt) with gpt-6-luna and gemini-3.5-flash-lite, and the out-of-sample JWST bank
(v1 prompt) with the same two models. Conditions C2, C2KB, C3 (not run on JWST flash-lite), C4 and FULLREV;
all repair the same stored generations (paired). E3 C2/C3/C4 come from results/ablation_stress and C2KB/FULLREV
from results/ablation_stress_revision (same bank, copied byte for byte).

- Body table: rescue, iterations, repair calls and repair cost per invalid generation.
- Appendix table: paired tests A -> B (exact McNemar on rescue, Wilcoxon signed-rank on the rest), with
  better/worse/tie counts for the condition after the arrow; Holm over each bank's family of tests.

    python -m evaluation.analysis.a11_ablation_unified
"""

from __future__ import annotations

import pandas as pd

from evaluation.analysis.common import fmt, fmt_p, load_results, md_table, out_dir, tex, write_long_table, write_md, write_paper_table
from evaluation.make_paper_artifacts import holm, mcnemar_exact, mcnemar_odds_ratio, rank_biserial, wilcoxon_p

BANKS = [("E3 (EIRENE)", "gpt-6-luna", ["E3", "E3rev"]), ("E3 (EIRENE)", "gemini-3.5-flash-lite", ["E3", "E3rev"]),
         ("JWST", "gpt-6-luna", ["R9"]), ("JWST", "gemini-3.5-flash-lite", ["R9b"])]
# Bank label in the LaTeX tables (the CSVs keep the short name).
BANK_LABEL = {"JWST": "E6 (JWST)"}
CONDITIONS = ["C2", "C2KB", "C3", "C4", "FULLREV"]
PAIRS = [("C2", "C2KB"), ("C2", "C3"), ("C2", "C4"), ("C2", "FULLREV"), ("C2KB", "C4"), ("C3", "C4"),
         ("C2KB", "FULLREV"), ("C4", "FULLREV")]
METRICS = [("converged", "Rescued (\\%)", 100.0, 1), ("iterations", "Iterations", 1.0, 2),
           ("repair_calls", "Repair calls", 1.0, 2), ("repair_cost", "Repair cost (USD)", 1.0, 4)]


def effect_cell(r) -> str:
    if pd.isna(r.effect):
        return "--"
    return f"{r.effect:.2f}" if r.metric.startswith("Rescued") else f"{r.effect:+.2f}"


def bank_rows(sets: list[str], llm: str) -> pd.DataFrame:
    df = pd.concat([load_results(s) for s in sets])
    df = df[(df.llm == llm) & (df.initial_errors > 0) & df.condition.isin(CONDITIONS)]
    return df.drop_duplicates(["llm", "condition", "run", "category"], keep="last")


def main() -> None:
    out = out_dir("a11_ablation_unified")
    stats, tests = [], []
    for bank, llm, sets in BANKS:
        df = bank_rows(sets, llm)
        wide = {m: df.pivot_table(index=["run", "category"], columns="condition", values=m, aggfunc="first")
                for m, *_ in METRICS}
        for c in [c for c in CONDITIONS if c in wide["converged"]]:
            col = {m: wide[m][c].dropna() for m, *_ in METRICS}
            stats.append({"bank": bank, "llm": llm, "condition": c, "n_invalid": len(col["converged"]),
                          "rescued": col["converged"].astype(float).mean() * 100, "iterations": col["iterations"].mean(),
                          "repair_calls": col["repair_calls"].mean(), "repair_cost": col["repair_cost"].mean()})
        rows = []
        for a, b in PAIRS:
            if a not in wide["converged"] or b not in wide["converged"]:
                continue
            for metric, name, scale, digits in METRICS:
                pair = wide[metric][[a, b]].dropna()
                if metric == "converged":
                    x, y = pair[a].astype(bool), pair[b].astype(bool)
                    p = mcnemar_exact(x, y)
                    better, worse = int((~x & y).sum()), int((x & ~y).sum())
                    effect = mcnemar_odds_ratio(better, worse)
                else:
                    diff = pair[b] - pair[a]
                    p = wilcoxon_p(pair[a], pair[b])
                    better, worse = int((diff < 0).sum()), int((diff > 0).sum())
                    effect = rank_biserial(pair[b], pair[a])  # positive when the condition after the arrow is lower
                rows.append({"bank": bank, "llm": llm, "metric": name, "comparison": f"{a} -> {b}", "n": len(pair),
                             "mean_from": pair[a].astype(float).mean() * scale,
                             "mean_to": pair[b].astype(float).mean() * scale, "digits": digits,
                             "better_worse_tie": f"{better}/{worse}/{len(pair) - better - worse}", "effect": effect,
                             "p": p})
        for r, ph in zip(rows, holm([r["p"] for r in rows])):
            r["p_holm"] = ph
        tests += rows
    st, ts = pd.DataFrame(stats), pd.DataFrame(tests)
    st.to_csv(out / "ablation_unified.csv", index=False)
    ts.to_csv(out / "ablation_unified_tests.csv", index=False)

    body = []
    for bank, llm, _ in BANKS:
        sub = st[(st.bank == bank) & (st.llm == llm)]
        if body:
            body.append(["\\midrule"])
        for i, r in enumerate(sub.itertuples()):
            body.append([tex(BANK_LABEL.get(bank, bank)) if i == 0 else "", tex(llm) if i == 0 else "",
                         str(r.n_invalid) if i == 0 else "", r.condition, fmt(r.rescued, 1), fmt(r.iterations, 2),
                         fmt(r.repair_calls, 2), fmt(r.repair_cost, 4)])
    write_paper_table(
        out / "tab_ablation_unified.tex",
        "Repair conditions on the four error banks (paired design: every condition repairs the same stored invalid "
        "generations of the bank). E3: EIRENE; E6 (JWST): out-of-sample bank built the same way (earlier generation "
        "prompt). C2KB: C2 plus the knowledge base of the current diagnostic (router used only to pick it); "
        "FULLREV: whole-file revision from the full diagnostic list (no router, no knowledge base). C3 was not run "
        "on the JWST bank of gemini-3.5-flash-lite. Means per invalid generation; repair cost in USD.",
        "tab:ablation_unified", ["Bank", "Model", "Invalid", "Cond.", "Rescued (\\%)", "Iterations", "Repair calls",
                                 "Repair cost"], "lllcrrrr", body, wide=True)

    app = []
    for bank, llm, _ in BANKS:
        sub = ts[(ts.bank == bank) & (ts.llm == llm)]
        if app:
            app.append(["\\midrule"])
        app.append([f"\\multicolumn{{9}}{{l}}{{\\textit{{{tex(BANK_LABEL.get(bank, bank))}, \\llm{{{llm}}}}}}} \\\\"])
        for r in sub.itertuples():
            app.append([r.metric, r.comparison.replace("->", "$\\rightarrow$"), str(r.n), fmt(r.mean_from, r.digits),
                        fmt(r.mean_to, r.digits), r.better_worse_tie, effect_cell(r), fmt_p(r.p), fmt_p(r.p_holm)])
    write_long_table(
        out / "tab_ablation_unified_tests.tex",
        "Paired comparison of the repair conditions on the invalid generations of each bank. Comparison A "
        "$\\rightarrow$ B: From: mean under A; To: mean under B. B/W/T (better/worse/tie): generations in which the "
        "condition after the arrow is better (rescues a generation the other does not, or needs fewer iterations, "
        "calls or cost), worse, or equal. Effect: for rescue, odds ratio of the discordant pairs (B/W, with 0.5 added to "
        "both when one is zero; above 1 favours the condition after the arrow); for the other metrics, matched-pairs "
        "rank-biserial correlation (from $-1$ to 1; positive when the condition after the arrow needs less). Rescue: "
        "exact McNemar test; other metrics: Wilcoxon signed-rank test. $p_{\\mathrm{Holm}}$: Holm-adjusted over each "
        "bank's family of tests.",
        "tab:ablation_unified_tests", ["Metric", "Comparison", "n", "From", "To", "B/W/T", "Effect", "$p$",
                                       "$p_{\\mathrm{Holm}}$"], "llrrrrrrr", app)
    write_md(out / "summary.md", "A11. Unified ablation over the four banks",
             [md_table(st), "## Paired tests", md_table(ts.drop(columns=["digits"]))])


if __name__ == "__main__":
    main()
