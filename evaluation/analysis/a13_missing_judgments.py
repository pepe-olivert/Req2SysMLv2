"""A13. Sensitivity of the LJS results to the judgments that are missing.

The answers rejected by the strict parser of the SemanticJudge were not stored (evaluator/semantic_judge.py keeps
only accepted judgments; the logs keep the reason, not the answer), so they cannot be re-parsed. This is a bounds
analysis instead: every missing (model, run, category) row is imputed with the worst (LJS = 0) and the best
(LJS = 1) possible value, and, for each pair of models, adversarially (worst for the model that leads the pair,
best for the other). For each scenario: model means, ranking, and the paired Wilcoxon block tests (run,
category) with Holm over the six pairs, compared with the judged-only result. Agreement between judges (kappa) is
only defined on the requirements both judges labelled, so it is reported on that intersection (A13 does not
change it).

    python -m evaluation.analysis.a13_missing_judgments
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from evaluation.analysis.common import (KEYS, MODEL_ORDER, fmt, fmt_p, jsonl, load_ljs, md_table, out_dir, tex,
                                        write_md, write_paper_table)
from evaluation.make_paper_artifacts import holm, wilcoxon_p
from core.config import RESULTS_DIR

SETS = [  # (label, models file, conditions, judge dir)
    ("E1 C4, claude-haiku-5.5", "pipeline/sysml_models.jsonl", ["C4"], "second_judge/pipeline_c4/ljs/claude-haiku-5.5"),
    ("E1 C4 no-doc, claude-haiku-5.5", "nodoc_control/pipeline_c4/sysml_models.jsonl", ["C4"],
     "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5"),
    ("E5 C4, gpt-4o-mini", "jwst_pipeline/sysml_models.jsonl", ["C4"], "jwst_pipeline/ljs/gpt-4o-mini"),
    ("E5 C4 no-doc, gpt-4o-mini", "nodoc_control/jwst_pipeline_c4/sysml_models.jsonl", ["C4"],
     "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini"),
    ("E5 C4 no-doc, claude-haiku-5.5", "nodoc_control/jwst_pipeline_c4/sysml_models.jsonl", ["C4"],
     "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"),
]
# Sets with missing judgments but no model ranking (one candidate): only their n is reported.
COUNT_ONLY = [
    ("R4 C0 no-doc, claude-haiku-5.5", "nodoc_control/c0_minimal_prompt/sysml_models.jsonl", ["C1", "C4"],
     "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5"),
    ("R9 JWST bank (luna), gpt-4o-mini", "jwst_v1_bank/sysml_models.jsonl",
     ["C1", "C2", "C2KB", "C3", "C4", "FULLREV"], "jwst_v1_bank/ljs/gpt-4o-mini"),
]


def table(models_file: str, conditions: list[str], judge_dir: str) -> pd.DataFrame:
    rows = {}
    for r in jsonl(RESULTS_DIR / models_file):
        if r["condition"] in conditions:
            rows[(r["pdf"], r["llm"], r["condition"], int(r["run"]), r["category"])] = None
    keys = pd.DataFrame(list(rows), columns=KEYS)
    lj = load_ljs(judge_dir)
    lj = lj[lj.condition.isin(conditions)]
    return keys.merge(lj[KEYS + ["ljs"]], on=KEYS, how="left")


def analyse(df: pd.DataFrame) -> tuple[dict, list[dict]]:
    models = [m for m in MODEL_ORDER if m in set(df.llm)]
    means = df.groupby("llm").ljs.mean().reindex(models)
    wide = df.pivot_table(index=["run", "category"], columns="llm", values="ljs", aggfunc="first")
    tests = []
    for a, b in itertools.combinations(models, 2):
        pair = wide[[a, b]].dropna()
        tests.append({"a": a, "b": b, "diff": pair[a].mean() - pair[b].mean(), "p": wilcoxon_p(pair[a], pair[b])})
    for t, ph in zip(tests, holm([t["p"] for t in tests])):
        t["p_holm"] = ph
    return means.to_dict(), tests


def main() -> None:
    out = out_dir("a13_missing_judgments")
    rows, test_rows, n_rows = [], [], []
    for label, models_file, conds, judge_dir in SETS:
        df = table(models_file, conds, judge_dir)
        missing = df[df.ljs.isna()]
        n_rows.append({"set": label, "rows": len(df), "judged": int(df.ljs.notna().sum()), "missing": len(missing),
                       **{f"missing_{m}": int((missing.llm == m).sum()) for m in MODEL_ORDER}})
        if missing.empty:
            continue
        observed_means, observed_tests = analyse(df.dropna(subset=["ljs"]))
        order_obs = sorted(observed_means, key=observed_means.get, reverse=True)
        scenarios = {"judged only": df.dropna(subset=["ljs"]), "missing = 0": df.fillna({"ljs": 0.0}),
                     "missing = 1": df.fillna({"ljs": 1.0})}
        for (a, b) in itertools.combinations(order_obs, 2):  # a leads b in the judged-only ranking
            adv = df.copy()
            adv.loc[adv.ljs.isna() & (adv.llm == a), "ljs"] = 0.0
            adv.loc[adv.ljs.isna() & (adv.llm == b), "ljs"] = 1.0
            adv.loc[adv.ljs.isna(), "ljs"] = np.nan
            scenarios[f"adversarial {a} < {b}"] = adv.dropna(subset=["ljs"])
        sig_obs = {(t["a"], t["b"]): t["p_holm"] < 0.05 for t in observed_tests}
        for name, d in scenarios.items():
            means, tests = analyse(d)
            order = sorted(means, key=means.get, reverse=True)
            changed = [f"{t['a']}-{t['b']}" for t in tests if (t["p_holm"] < 0.05) != sig_obs[(t["a"], t["b"])]]
            rows.append({"set": label, "scenario": name, **{m: means.get(m) for m in MODEL_ORDER},
                         "ranking": " > ".join(order), "ranking_changes": order != order_obs,
                         "significance_changes": ", ".join(changed)})
            for t in tests:
                test_rows.append({"set": label, "scenario": name, **t})
    for label, models_file, conds, judge_dir in COUNT_ONLY:
        df = table(models_file, conds, judge_dir)
        missing = df[df.ljs.isna()]
        n_rows.append({"set": label, "rows": len(df), "judged": int(df.ljs.notna().sum()), "missing": len(missing),
                       **{f"missing_{m}": int((missing.llm == m).sum()) for m in MODEL_ORDER}})
    n_df, sc, ts = pd.DataFrame(n_rows), pd.DataFrame(rows), pd.DataFrame(test_rows)
    n_df.to_csv(out / "judged_n.csv", index=False)
    sc.to_csv(out / "bounds.csv", index=False)
    ts.to_csv(out / "bounds_tests.csv", index=False)

    keep = sc[sc.scenario.isin(["judged only", "missing = 0", "missing = 1"]) | sc.ranking_changes
              | (sc.significance_changes != "")]
    trows = [[tex(r.set), tex(r.scenario)] + [fmt(r[3 + i], 3) for i in range(4)]
             + ["yes" if r.ranking_changes else "no", tex(r.significance_changes) or "none"] for r in keep.itertuples()]
    write_paper_table(
        out / "tab_missing_bounds.tex",
        "Sensitivity of the LJS to the missing judgments (answers rejected by the strict parser after three "
        "attempts, not stored). Missing rows imputed with the worst (0) or best (1) LJS, or adversarially for a "
        "pair (worst for the leader, best for the other; listed only if they change the ranking or a test). "
        "Ranking: whether the order of the four models changes; Significance: pairs whose Holm-adjusted Wilcoxon "
        "test changes at 0.05.",
        "tab:missing_bounds", ["Set", "Scenario", *[tex(m) for m in MODEL_ORDER], "Ranking", "Significance"],
        "llrrrrll", trows, wide=True)

    # Sentence for the paper.
    judged = {r.set: (r.judged, r.rows) for r in n_df.itertuples()}
    any_rank = bool(sc.ranking_changes.any())
    any_sig = bool((sc.significance_changes != "").any())
    e1h, e1hn = judged["E1 C4, claude-haiku-5.5"], judged["E1 C4 no-doc, claude-haiku-5.5"]
    e5h = judged["E5 C4 no-doc, claude-haiku-5.5"]
    e5o, e5on = judged["E5 C4, gpt-4o-mini"], judged["E5 C4 no-doc, gpt-4o-mini"]
    sentence = (
        f"The judges returned a valid verdict for {e1h[0]} of {e1h[1]} E1 models with claude-haiku-5.5 "
        f"({e1hn[0]}/{e1hn[1]} without doc comments), {e5h[0]}/{e5h[1]} E5 models without doc comments with "
        f"claude-haiku-5.5, and {e5o[0]}/{e5o[1]} ({e5on[0]}/{e5on[1]} without doc comments) E5 models with "
        f"gpt-4o-mini; {judged['R4 C0 no-doc, claude-haiku-5.5'][0]}/{judged['R4 C0 no-doc, claude-haiku-5.5'][1]} "
        f"rows of the C0 models without doc comments with claude-haiku-5.5 and "
        f"{judged['R9 JWST bank (luna), gpt-4o-mini'][0]}/{judged['R9 JWST bank (luna), gpt-4o-mini'][1]} rows of "
        "the JWST error bank of gpt-6-luna with gpt-4o-mini; every other set was judged completely. The missing "
        "verdicts are answers rejected by the strict parser "
        "after three attempts and are left out. In the model comparisons, imputing them with the worst or the best possible LJS "
        + ("does not change" if not any_rank else "changes") + " the ranking of the models"
        + (" and does not change the significance of any pairwise test." if not any_sig else
           "; the pairwise tests that change significance are listed in Table~\\ref{tab:missing_bounds}."))
    (out / "paper_sentence.txt").write_text(sentence + "\n", encoding="utf-8")
    write_md(out / "summary.md", "A13. Sensitivity to the missing judgments",
             ["The rejected answers were not stored, so they cannot be re-parsed with a tolerant parser; bounds "
              "analysis instead.", md_table(n_df), md_table(sc), "## Sentence for the paper", sentence])


if __name__ == "__main__":
    main()
