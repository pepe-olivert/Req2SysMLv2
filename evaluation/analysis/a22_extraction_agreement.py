"""A22. Agreement between the two annotators of the manual validation of the extraction (no LLM calls).

Reads every block of the second annotator (results/extraction/second_annotator/annotation_sheet_*.xlsx) and joins it,
by the requirement text, with the first annotator (results/extraction/manual_validation_sample_completed.csv). A new
block only has to be dropped in that folder; running this again updates every figure.

Writes results/analysis/a22_extraction_agreement/: paired_annotations.csv, disagreements.csv, agreement.csv,
tab_extraction_agreement.tex and summary.md.

    python -m evaluation.analysis.a22_extraction_agreement
"""

from __future__ import annotations

import pandas as pd
from scipy.stats import fisher_exact
from core.config import RESULTS_DIR
from evaluation.analysis.common import fmt, md_table, out_dir, write_md, write_paper_table
from evaluation.revision_summary import cohen_kappa

EX = RESULTS_DIR / "extraction"
ITEMS = [("exists", "Exists in the document"), ("faithful", "Faithful")]
SUBSETS = [("all", "All"), ("input_random", "Input"), ("reference_only", "Reference-only")]


def second_annotator() -> pd.DataFrame:
    blocks = [pd.read_excel(path, sheet_name="annotation").assign(block=path.stem)
              for path in sorted((EX / "second_annotator").glob("annotation_sheet_*.xlsx"))]
    df = pd.concat(blocks, ignore_index=True)
    if df.requirement.duplicated().any():
        raise SystemExit(f"Requirement annotated twice: {df.requirement[df.requirement.duplicated()].tolist()}")
    return df


def paired() -> pd.DataFrame:
    a = pd.read_csv(EX / "manual_validation_sample_completed.csv")
    b = second_annotator()
    df = b.merge(a, on="requirement", how="left", suffixes=("_B", "_A"), validate="one_to_one")
    if df.sample_id.isna().any():
        raise SystemExit(f"Not in the first annotator's sample: {df.requirement[df.sample_id.isna()].tolist()}")
    clean = lambda s: s.str.strip().str.lower()  # noqa: E731
    return pd.DataFrame({
        "sample_id": df.sample_id, "set": df.set, "category": df.category_A, "requirement": df.requirement,
        "block": df.block, "exists_A": clean(df.exists_in_document_annotation),
        "exists_B": clean(df.exists_in_document), "faithful_A": clean(df.faithful_annotation),
        "faithful_B": clean(df.faithful), "pdf_page_A": df.pdf_page_A, "pdf_page_B": df.pdf_page_B,
        "comment_B": df.comment_B}).sort_values("sample_id", ignore_index=True)


def agreement(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for item, _ in ITEMS:
        for subset, _ in SUBSETS:
            g = df if subset == "all" else df[df.set == subset]
            a, b = g[f"{item}_A"], g[f"{item}_B"]
            rows.append({"item": item, "set": subset, "n": len(g), "agreement": (a == b).mean() * 100,
                         "kappa": cohen_kappa(a, b), "yes_A": (a == "yes").mean() * 100,
                         "yes_B": (b == "yes").mean() * 100})
    return pd.DataFrame(rows)


def fisher(df: pd.DataFrame, annotator: str) -> tuple[int, int, int, int, float]:
    col = f"faithful_{annotator}"
    i, r = df[df.set == "input_random"][col], df[df.set == "reference_only"][col]
    table = [[(i == "yes").sum(), (i != "yes").sum()], [(r == "yes").sum(), (r != "yes").sum()]]
    return (*map(int, (table[0][0], len(i), table[1][0], len(r))), float(fisher_exact(table).pvalue))


def main() -> None:
    out = out_dir("a22_extraction_agreement")
    df = paired()
    ag = agreement(df)
    disagree = df[(df.exists_A != df.exists_B) | (df.faithful_A != df.faithful_B)]
    df.to_csv(out / "paired_annotations.csv", index=False)
    disagree.to_csv(out / "disagreements.csv", index=False)
    ag.to_csv(out / "agreement.csv", index=False)

    items, subsets, rows = dict(ITEMS), dict(SUBSETS), []
    for i, r in enumerate(ag.itertuples()):
        if i and i % len(SUBSETS) == 0:
            rows.append(["\\midrule"])
        rows.append([items[r.item], subsets[r.set], str(r.n), fmt(r.agreement), fmt(r.kappa, 2).replace("-", "$-$"), fmt(r.yes_A),
                     fmt(r.yes_B)])
    write_paper_table(out / "tab_extraction_agreement.tex",
                      f"Agreement between the two annotators of the manual validation of the extraction, on the "
                      f"{len(df)} requirements labelled by both: raw agreement, Cohen's $\\kappa$ and share labelled "
                      f"\\textit{{yes}} by each annotator (A, first annotator, I1 of the paper; B, second annotator, I2).",
                      "tab:extraction_agreement",
                      ["Item", "Set", "n", "Agreement \\%", "$\\kappa$", "Yes A \\%", "Yes B \\%"], "llrrrrr", rows)

    tests = pd.DataFrame([dict(zip(("annotator", "input_faithful", "input_n", "reference_faithful", "reference_n", "p"),
                                   (who, *fisher(df, who)))) for who in "AB"])
    crosstabs = [f"### {item}\n\n" + md_table(pd.crosstab(df[f"{item}_A"], df[f"{item}_B"]).reset_index())
                 for item, _ in ITEMS]
    write_md(out / "summary.md", "A22. Agreement between the annotators of the extraction validation",
             [f"{len(df)} requirements labelled by both annotators; blocks: {sorted(df.block.unique())}. "
              f"{len(disagree)} differ in at least one item (`disagreements.csv`).", md_table(ag), *crosstabs,
              "## Faithfulness, input vs reference-only, on the doubly labelled requirements (Fisher's exact test)",
              md_table(tests)])
    print(f"  wrote {out} ({len(df)} requirements, {len(disagree)} with a disagreement)")


if __name__ == "__main__":
    main()
