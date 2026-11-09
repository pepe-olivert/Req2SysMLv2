"""A21. Conclusion validity: inventory of the hypothesis tests and a category-level sensitivity check of the
paired repair tests. No LLM calls.

1. Inventory: number of tests per family and the multiplicity correction applied to each, from the stored test
   tables (a04 between-model tests, a11 repair conditions on the banks, E2 repair conditions, and the paired LJS
   change of tab:repair_semantics).
2. Sensitivity: the paired repair tests of a11 treat each invalid generation (run, category) as a unit, but the
   runs of one category share the category's requirements. Here every metric is first averaged over the runs of a
   category (rescue as the share of rescued runs), and the comparison is repeated with a Wilcoxon signed-rank test
   on the category means, Holm-adjusted over the same family. The output lists where significance at 0.05 after
   Holm changes.

    python -m evaluation.analysis.a21_conclusion_validity
"""

from __future__ import annotations

import re

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.a11_ablation_unified import BANKS, METRICS, PAIRS, bank_rows
from evaluation.analysis.common import ANALYSIS_DIR, md_table, out_dir, write_md
from evaluation.make_paper_artifacts import holm, rank_biserial, wilcoxon_p

ALPHA = 0.05


def inventory() -> pd.DataFrame:
    rows = []
    a04 = pd.read_csv(ANALYSIS_DIR / "a04_cluster_stats" / "pairwise_tests.csv")
    for method, col in (("block test", "p_block"), ("cluster bootstrap", "p_cluster"), ("mixed model", "p_mixed")):
        sub = a04.dropna(subset=[col])
        fams = sub.groupby(["document", "metric"]).size()
        rows.append({"analysis": f"between models ({method})", "families": len(fams), "tests": int(fams.sum()),
                     "correction": "Holm per document and metric",
                     "significant_after_correction": int((sub[f"{col}_holm"] < ALPHA).sum())})
    a11 = pd.read_csv(ANALYSIS_DIR / "a11_ablation_unified" / "ablation_unified_tests.csv")
    rows.append({"analysis": "repair conditions, four banks (E3, E6)", "families": a11.groupby(["bank", "llm"]).ngroups,
                 "tests": len(a11), "correction": "Holm per bank and model",
                 "significant_after_correction": int((a11.p_holm < ALPHA).sum())})
    e2 = (RESULTS_DIR / "ablation" / "tables" / "tab_ablation_tests.tex").read_text(encoding="utf-8")
    e2_rows = [r for r in e2.splitlines() if "rightarrow" in r and "&" in r]
    rows.append({"analysis": "repair conditions, E2", "families": 1, "tests": len(e2_rows),
                 "correction": "Holm over the family",
                 "significant_after_correction": sum(float(r.split("&")[-1].strip(" \\")) < ALPHA
                                                     for r in e2_rows if "$<$" not in r.split("&")[-1])})
    rs = (RESULTS_DIR / "paper_tables" / "tab_repair_semantics.tex").read_text(encoding="utf-8")
    ps = [r.split("&")[-1].strip(" \\") for r in rs.splitlines() if r.startswith(("grammar", "reference"))]
    ps = [p for p in ps if p != "--"]
    rows.append({"analysis": "LJS change after repair (tab:repair_semantics)", "families": 1, "tests": len(ps),
                 "correction": "none (Holm across the table reported in the text)",
                 "significant_after_correction": sum(p != "$<$0.001" and float(p) < ALPHA for p in ps)})
    return pd.DataFrame(rows)


def sensitivity() -> pd.DataFrame:
    original = pd.read_csv(ANALYSIS_DIR / "a11_ablation_unified" / "ablation_unified_tests.csv")
    rows = []
    for bank, llm, sets in BANKS:
        df = bank_rows(sets, llm)
        df["converged"] = df.converged.astype(float)
        fam = []
        for a, b in PAIRS:
            if not {a, b} <= set(df.condition):
                continue
            for metric, name, *_ in METRICS:
                wide = df.pivot_table(index=["run", "category"], columns="condition", values=metric)[[a, b]].dropna()
                cat = wide.groupby(level="category").mean()
                fam.append({"bank": bank, "llm": llm, "metric": name, "comparison": f"{a} -> {b}",
                            "n_generations": len(wide), "n_categories": len(cat),
                            "p_category": wilcoxon_p(cat[a], cat[b]),
                            "r_category": rank_biserial(cat[a], cat[b])})
        for r, ph in zip(fam, holm([r["p_category"] for r in fam])):
            r["p_category_holm"] = ph
        rows += fam
    sens = pd.DataFrame(rows).merge(original[["bank", "llm", "metric", "comparison", "p_holm"]],
                                    on=["bank", "llm", "metric", "comparison"])
    sens["significant_generation"] = sens.p_holm < ALPHA
    sens["significant_category"] = sens.p_category_holm < ALPHA
    return sens


def main() -> None:
    out = out_dir("a21_conclusion_validity")
    inv = inventory()
    inv.to_csv(out / "test_inventory.csv", index=False)
    sens = sensitivity()
    sens.to_csv(out / "category_sensitivity.csv", index=False)
    changed = sens[sens.significant_generation != sens.significant_category]
    agg = (sens.groupby(["bank", "llm"], as_index=False)
           .agg(tests=("metric", "size"), significant_generation=("significant_generation", "sum"),
                significant_category=("significant_category", "sum"), n_categories=("n_categories", "max"),
                n_generations=("n_generations", "max")))
    agg.to_csv(out / "category_sensitivity_summary.csv", index=False)
    write_md(out / "summary.md", "A21. Conclusion validity",
             ["## Tests per family", md_table(inv),
              "## Category-level sensitivity of the bank tests",
              "Unit = category (metrics averaged over its runs) instead of invalid generation; Wilcoxon signed-rank, "
              "Holm per bank and model.", md_table(agg),
              "### Comparisons whose significance changes", md_table(changed)])
    print(inv.to_string(index=False))
    print(agg.to_string(index=False))
    print(f"  significance changes in {len(changed)} of {len(sens)} bank tests")


if __name__ == "__main__":
    main()
