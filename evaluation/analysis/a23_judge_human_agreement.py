"""A23. Human evaluation of the LJS judges on the sample of data/h_e_judge_sample (no LLM calls).

Reads the two filled annotation sheets of that folder and joins them by case with both judges' verdicts
(key/sample_key.csv). The sheets are not edited: a status left empty is derived from the attributes with the rule of
the judge prompt, and `status_rule` applies that rule to every case as a sensitivity check. The evidence column of
annotator 2 opens with the candidate model and run of the case, which is reported as `evidence_names_key_fields`.

Writes results/analysis/a23_judge_human_agreement/: paired_annotations.csv, inconsistent_cases.csv, agreement.csv,
scores.csv, tab_judge_human.tex and summary.md.

    python -m evaluation.analysis.a23_judge_human_agreement
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from core.config import DATA_DIR
from evaluation.analysis.common import IEEE, fmt, md_table, out_dir, write_md, write_paper_table
from evaluation.make_paper_artifacts import holm, rank_biserial
from evaluation.revision_summary import cohen_kappa

SAMPLE = DATA_DIR / "h_e_judge_sample"
JUDGES = ["gpt-4o-mini", "claude-haiku-5.5"]
SCORE = {"satisfied": 1.0, "partial": 0.5, "missing": 0.0}
STATUSES = list(SCORE)
SHEETS = {"annotator 1": "annotation_sheet_LLM_blockB.xlsx", "annotator 2": "annotation_sheet_A.xlsm"}
RESAMPLES = 5000
SEED = 0


def rule(row: pd.Series, prefix: str) -> str:
    yes = sum(row[f"{prefix}{a}"] == "yes" for a in IEEE)
    return "satisfied" if yes == len(IEEE) else "missing" if yes == 0 else "partial"


def annotators() -> dict[str, pd.DataFrame]:
    sample = pd.read_csv(SAMPLE / "annotation_sheet.csv")
    found = {}
    for name, file in SHEETS.items():
        df = pd.read_excel(SAMPLE / file, sheet_name="annotation", keep_default_na=False, engine="openpyxl")
        if not (df.case.equals(sample.case) and df.requirement.equals(sample.requirement)):
            raise SystemExit(f"{file} does not follow the sample")
        found[name] = df
    return found


def paired() -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(SAMPLE / "key" / "sample_key.csv")
    for judge in JUDGES:
        df[judge] = df[f"{judge}_status"]
        for a in IEEE:
            df[f"{judge}_{a}"] = df[f"{judge}_{a}"].map({True: "yes", False: "no"})
    names = []
    for name, sheet in annotators().items():
        names.append(name)
        for a in IEEE:
            df[f"{name}_{a}"] = sheet[a].str.strip().str.lower()
        df[f"{name}_status_rule"] = df.apply(rule, axis=1, prefix=f"{name}_")
        given = sheet.status.str.strip().str.lower()
        df[name] = given.where(given != "", df[f"{name}_status_rule"])
        df[f"{name}_status_given"] = given
        df[f"{name}_evidence"] = sheet.evidence
        df[f"{name}_comment"] = sheet.comment
    return df, names


def kappa_ci(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    rng = np.random.default_rng(SEED)
    x, y = a.to_numpy(object), b.to_numpy(object)
    values = [cohen_kappa(x[i], y[i]) for i in rng.integers(0, len(x), (RESAMPLES, len(x)))]
    return tuple(np.nanquantile(values, [0.025, 0.975]))


def compare(df: pd.DataFrame, a: str, b: str, kind: str) -> list[dict]:
    low, high = kappa_ci(df[a], df[b])
    rows = [{"kind": kind, "a": a, "b": b, "item": "status", "n": len(df), "agreement": (df[a] == df[b]).mean() * 100,
             "kappa": cohen_kappa(df[a], df[b]), "kappa_low": low, "kappa_high": high}]
    for attr in IEEE:
        x, y = df[f"{a}_{attr}"], df[f"{b}_{attr}"]
        rows.append({"kind": kind, "a": a, "b": b, "item": attr, "n": len(df), "agreement": (x == y).mean() * 100,
                     "kappa": cohen_kappa(x, y)})
    return rows


def scores(df: pd.DataFrame, humans: list[str]) -> pd.DataFrame:
    rows = []
    for doc, g in [("All", df), *df.groupby("document")]:
        for r in [*humans, *JUDGES]:
            s = g[r].map(SCORE)
            row = {"document": doc, "rater": r, "n": len(g), "score": s.mean(),
                   **{st: int((g[r] == st).sum()) for st in STATUSES},
                   **{a: (g[f"{r}_{a}"] == "yes").mean() * 100 for a in IEEE}}
            for h in humans:
                if r != h:
                    d = s - g[h].map(SCORE)
                    row[f"diff_vs_{h}"], row[f"r_vs_{h}"] = d.mean(), rank_biserial(g[h].map(SCORE), s)
                    row[f"p_vs_{h}"] = wilcoxon(d).pvalue if d.any() else np.nan
            rows.append(row)
    out = pd.DataFrame(rows)
    for h in humans:
        tested = out[(out.document == "All") & out.rater.isin(JUDGES)].index
        out.loc[tested, f"p_holm_vs_{h}"] = holm(out.loc[tested, f"p_vs_{h}"].tolist())
    return out


def consensus(df: pd.DataFrame, humans: list[str]) -> pd.DataFrame:
    """Judges against the status of the cases on which both annotators agree."""
    a, b = humans
    g = df[df[a] == df[b]]
    return pd.DataFrame([{"judge": j, "n": len(g), "agreement": (g[j] == g[a]).mean() * 100,
                          "kappa": cohen_kappa(g[j], g[a]), "score_judge": g[j].map(SCORE).mean(),
                          "score_annotators": g[a].map(SCORE).mean()} for j in JUDGES])


def main() -> None:
    out = out_dir("a23_judge_human_agreement")
    df, humans = paired()
    pairs = [c for h in humans for j in JUDGES for c in compare(df, h, j, "annotator-judge")]
    pairs += compare(df, *JUDGES, "judge-judge")
    pairs += compare(df, *humans, "annotator-annotator")
    ag = pd.DataFrame(pairs)
    sc = scores(df, humans)
    cons = consensus(df, humans)
    keep = ["case", "document", "category", "req_id", *JUDGES]
    bad = pd.concat([df.loc[(df[h] != df[f"{h}_status_rule"]) | (df[f"{h}_status_given"] == ""),
                            keep + [f"{h}_status_given", f"{h}_status_rule", f"{h}_comment"]]
                     .rename(columns=lambda c: c.replace(f"{h}_", "")).assign(annotator=h) for h in humans])
    bad.to_csv(out / "inconsistent_cases.csv", index=False)
    named = sum(e.startswith(f"{r.document}, {r.llm}, {r.condition}, run {r.run}, {r.category}, {r.req_id}.")
                for r, e in zip(df.itertuples(), df[f"{humans[1]}_evidence"]))
    df.to_csv(out / "paired_annotations.csv", index=False)
    ag.to_csv(out / "agreement.csv", index=False)
    sc.to_csv(out / "scores.csv", index=False)
    cons.to_csv(out / "consensus.csv", index=False)

    rows = []
    for r in ag.itertuples():
        if r.item == "status":
            if rows:
                rows.append(["\\midrule"])
            label = (f"\\llm{{{r.b}}} vs {r.a}" if r.kind == "annotator-judge" else
                     f"\\llm{{{r.a}}} vs \\llm{{{r.b}}}" if r.kind == "judge-judge" else "Annotator 1 vs annotator 2")
        ci = f" [{fmt(r.kappa_low, 2)}, {fmt(r.kappa_high, 2)}]" if r.item == "status" else ""
        rows.append([label if r.item == "status" else "", r.item, fmt(r.agreement),
                     (fmt(r.kappa, 2) + ci).replace("-", "$-$")])
    all_docs = sc[sc.document == "All"].set_index("rater")
    counts = "; ".join(f"{r}, " + "/".join(str(all_docs.loc[r, s]) for s in STATUSES) for r in all_docs.index)
    write_paper_table(out / "tab_judge_human.tex",
                      f"Agreement per requirement among the two human annotators and the two judges on the {len(df)} "
                      f"sampled requirements of the final C4 models without doc comments: raw agreement and Cohen's "
                      f"$\\kappa$ (for the status, with a bootstrap 95\\% confidence interval). Annotators 1 and 2 are H1 and H2 "
                      f"of the paper (H1 is I2 and H2 is I1 of the input validation). "
                      f"Satisfied/partial/missing: {tex_llm(counts)}.",
                      "tab:judge_human", ["Pair", "Item", "Agreement \\%", "$\\kappa$"], "llrl", rows)

    crosstabs = [f"### {a} (rows) vs {b} (columns)\n\n"
                 + md_table(pd.crosstab(df[a], df[b]).reindex(index=STATUSES, columns=STATUSES, fill_value=0)
                            .reset_index()) for a, b in [(*humans,), *((j, h) for j in JUDGES for h in humans)]]
    sensitivity = pd.DataFrame([{"a": a, "b": b, "agreement": (df[f"{a}_status_rule"] == df[b]).mean() * 100,
                                 "kappa": cohen_kappa(df[f"{a}_status_rule"], df[b])}
                                for a in humans for b in [*JUDGES, *(h for h in humans if h != a)]])
    write_md(out / "summary.md", "A23. Human evaluation of the LJS judges",
             [f"Annotators: {SHEETS}. Evidence of {humans[1]} opening with the document, candidate model, condition, "
              f"run, category and requirement of the key: {named} of {len(df)}. Cases whose status is empty or does "
              "not follow the rule are in `inconsistent_cases.csv`: "
              + "; ".join(f"{h}: {g.case.tolist()}" for h, g in bad.groupby("annotator")) + ".",
              "## Agreement", md_table(ag), "## Judges on the cases where both annotators agree", md_table(cons),
              "## Scores (satisfied = 1, partial = 0.5, missing = 0)", md_table(sc), *crosstabs,
              "## Sensitivity: status of the annotator derived from the attributes in every case",
              md_table(sensitivity),
              "p: Wilcoxon signed-rank of the paired score against each annotator (r, rank-biserial of rater minus "
              "annotator; p_holm over the two judges, All only)."])
    print(f"  wrote {out} ({len(df)} cases; annotators: {humans}; {named} evidence cells name the key fields)")


def tex_llm(text: str) -> str:
    for judge in JUDGES:
        text = text.replace(judge, f"\\llm{{{judge}}}")
    return text


if __name__ == "__main__":
    main()
