"""A10. Variability between E1 and E2 (gpt-6-luna, same guided prompt, same input, independent generations).

E1 and E2 each generated the 77 categories x 3 runs with gpt-6-luna under identical settings. Compared:
- share of invalid generations (Fisher's exact test);
- diagnostics per invalid generation (distribution and Mann-Whitney U test; the generations are independent);
- router categories of the diagnostics (Fisher-Freeman-Halton is not available, so a chi-square test on the
  categories with expected count >= 1, and the exact counts);
- paired view: (run, category) blocks invalid in one experiment and valid in the other (McNemar).

    python -m evaluation.analysis.a10_e1_e2_variability
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu

from core.config import RESULTS_DIR
from evaluation.analysis.common import fmt, fmt_p, load_results, md_table, out_dir, write_md, write_paper_table
from evaluation.make_paper_artifacts import mcnemar_exact

MODEL = "gpt-6-luna"


def initial_errors(phase: str) -> pd.DataFrame:
    e = pd.read_csv(RESULTS_DIR / phase / "errors.csv")
    e = e[(e.llm == MODEL) & (e.iteration == 0)]
    return e.drop_duplicates(["llm", "run", "category", "line", "column", "message"])


def main() -> None:
    out = out_dir("a10_e1_e2_variability")
    gens = {}
    for name in ("E1", "E2"):
        r = load_results(name)
        gens[name] = r[(r.llm == MODEL) & (r.condition == "C1")].set_index(["run", "category"]).initial_errors
    e1, e2 = gens["E1"], gens["E2"]
    inv1, inv2 = e1[e1 > 0], e2[e2 > 0]
    _, p_fisher = fisher_exact([[len(inv1), len(e1) - len(inv1)], [len(inv2), len(e2) - len(inv2)]])
    p_mw = mannwhitneyu(inv1, inv2, alternative="two-sided").pvalue
    both = pd.concat([e1.rename("E1"), e2.rename("E2")], axis=1).dropna()
    p_mcnemar = mcnemar_exact(both.E1 > 0, both.E2 > 0)
    overlap = int(((both.E1 > 0) & (both.E2 > 0)).sum())

    cats = pd.concat([initial_errors("pipeline").groupby("error_category").size().rename("E1"),
                      initial_errors("ablation").groupby("error_category").size().rename("E2")], axis=1).fillna(0)
    chi = chi2_contingency(cats.values.T) if len(cats) > 1 else (np.nan, np.nan)
    dist = pd.DataFrame({"experiment": ["E1", "E2"], "generations": [len(e1), len(e2)],
                         "invalid": [len(inv1), len(inv2)],
                         "invalid_pct": [len(inv1) / len(e1) * 100, len(inv2) / len(e2) * 100],
                         "diag_mean": [inv1.mean(), inv2.mean()], "diag_median": [inv1.median(), inv2.median()],
                         "diag_p90": [np.percentile(inv1, 90), np.percentile(inv2, 90)],
                         "diag_max": [inv1.max(), inv2.max()], "diag_total": [inv1.sum(), inv2.sum()]})
    dist.to_csv(out / "e1_e2_diagnostics.csv", index=False)
    cats.reset_index().to_csv(out / "e1_e2_router_categories.csv", index=False)
    pd.DataFrame({"E1": inv1.value_counts().sort_index(), "E2": inv2.value_counts().sort_index()}).fillna(0).astype(
        int).rename_axis("diagnostics").reset_index().to_csv(out / "e1_e2_histogram.csv", index=False)
    tests = pd.DataFrame([
        {"test": "invalid share, Fisher exact", "p": p_fisher},
        {"test": "diagnostics per invalid generation, Mann-Whitney U", "p": p_mw},
        {"test": "(run, category) invalid in one and valid in the other, exact McNemar", "p": p_mcnemar},
        {"test": "router categories of the diagnostics, chi-square", "p": chi[1]},
    ])
    tests.to_csv(out / "e1_e2_tests.csv", index=False)

    rows = [[r.experiment, str(r.generations), f"{r.invalid} ({fmt(r.invalid_pct, 1)}\\%)", fmt(r.diag_mean, 2),
             fmt(r.diag_median, 0), fmt(r.diag_p90, 1), str(int(r.diag_max)), str(int(r.diag_total))]
            for r in dist.itertuples()]
    rows.append([f"\\multicolumn{{8}}{{l}}{{Invalid share: Fisher $p$ = {fmt_p(p_fisher)}; diagnostics per invalid "
                 f"generation: Mann-Whitney $p$ = {fmt_p(p_mw)}; blocks invalid in both: {overlap}; McNemar $p$ = "
                 f"{fmt_p(p_mcnemar)}}} \\\\"])
    write_paper_table(
        out / "tab_e1_e2_variability.tex",
        "Variability between two independent generations of the same specification with the same model and "
        "prompt (gpt-6-luna, E1 and E2): invalid generations and diagnostics per invalid generation.",
        "tab:e1_e2_variability", ["Exp.", "Generations", "Invalid", "Diag. mean", "Median", "P90", "Max", "Total"],
        "lrrrrrrr", rows)
    write_md(out / "summary.md", "A10. Variability between E1 and E2 (gpt-6-luna)",
             [md_table(dist), md_table(tests), f"Blocks invalid in both experiments: {overlap}.",
              "## Router categories", md_table(cats.reset_index())])


if __name__ == "__main__":
    main()
