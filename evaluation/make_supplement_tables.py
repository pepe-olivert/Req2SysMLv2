"""Tables and case listings of the Supplementary Material (paper/supplementary.tex), from stored results only.

Writes results/paper_tables/supplement/*.tex. Tables already written in their final format by the phase-3
analyses (results/analysis/aNN_*/tab_*.tex) are \\input directly by supplementary.tex and are not duplicated here.

    python -m evaluation.make_supplement_tables
"""

from __future__ import annotations

import re

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.common import IEEE, fmt, load_ljs, model_sort, tex, write_paper_table

OUT = RESULTS_DIR / "paper_tables" / "supplement"
A = RESULTS_DIR / "analysis"
EX = RESULTS_DIR / "extraction"


def esc(text) -> str:
    """Full LaTeX escape for free text and code shown inline (braces, backslashes, tildes, carets too)."""
    s = str(text).replace("\\", "\x00").replace("{", "\\{").replace("}", "\\}")
    s = tex(s).replace("~", "\\textasciitilde{}").replace("^", "\\^{}").replace("$", "\\$")
    return s.replace("\x00", "\\textbackslash{}")


def code(text) -> str:
    """Inline code that may break after ::, dots, commas, semicolons and parentheses (long identifiers)."""
    return "\\texttt{" + re.sub(r"(::|[.,;(])", r"\1\\allowbreak{}", esc(text)) + "}"


def m(llm: str) -> str:
    return f"\\llm{{{llm}}}"


def sup_extraction() -> None:
    df = pd.read_csv(EX / "extraction_results.csv")
    agg = df.groupby(["pdf", "strategy", "llm"]).agg(ncat=("num_categories", "mean"), req=("num_requirements", "mean"),
                                                     calls=("llm_calls", "mean"), cost=("cost_usd", "mean"),
                                                     lat=("latency_s", "mean")).reset_index()
    rows = []
    for doc in ("eirene", "jwst"):
        rows.append([f"\\multicolumn{{7}}{{l}}{{\\textbf{{{doc.upper()}}}}} \\\\"])
        for strategy in ("raw", "sliding_window"):
            sub = agg[(agg.pdf == doc) & (agg.strategy == strategy)]
            for llm in model_sort(sub.llm):
                r = sub[sub.llm == llm].iloc[0]
                rows.append([strategy.replace("_", " "), m(llm), fmt(r.ncat, 1), fmt(r.req, 1), fmt(r.calls, 1),
                             fmt(r.cost, 4), fmt(r.lat, 1)])
    write_paper_table(OUT / "sup_extraction.tex",
                      "Requirement extraction by document, strategy and model (means over three runs; cost in USD, "
                      "latency in s).", "tab:sup_extraction",
                      ["Strategy", "Model", "\\#Cat", "\\#Req", "Calls", "Cost", "Lat."], "llrrrrr", rows,
                      placement="h")
    ag = pd.read_csv(EX / "extraction_agreement.csv").groupby(["pdf", "llm"]).jaccard_similarity.mean().reset_index()
    rows = [[r.pdf.upper(), m(r.llm), fmt(r.jaccard_similarity, 3)] for d in ("eirene", "jwst")
            for r in ag[ag.pdf == d].set_index("llm").loc[model_sort(ag[ag.pdf == d].llm)].reset_index().itertuples()]
    write_paper_table(OUT / "sup_jaccard.tex", "Agreement between raw and sliding-window extraction (fuzzy Jaccard, "
                      "cosine $\\geq$ 0.85; mean over runs).", "tab:sup_jaccard", ["Document", "Model", "Jaccard"],
                      "llr", rows, placement="h")
    cov = pd.read_csv(EX / "input_coverage.csv")
    rows = [[fmt(r.threshold, 2), fmt(r.reference_with_counterpart_pct, 1), fmt(r.reference_covered_one_to_one_pct, 1),
             fmt(r.selected_in_reference_pct, 1)] for r in cov.itertuples()]
    write_paper_table(OUT / "sup_input_coverage.tex",
                      f"Semantic coverage of the EIRENE input ({int(cov.selected_n.iloc[0])} distinct requirements) "
                      f"with respect to the most exhaustive extraction ({int(cov.reference_n.iloc[0])} distinct "
                      "requirements, \\llm{gpt-6.1-sol}). Cosine similarity of all-MiniLM-L6-v2 embeddings.",
                      "tab:sup_input_coverage", ["Cosine $\\geq$", "Ref.\\ with counterpart \\%", "Ref.\\ matched 1:1 \\%",
                                                 "Input found in ref.\\ \\%"], "rrrr", rows, placement="h")


def sup_attributes() -> None:
    sets = [("E1", "with doc", "gpt-4o-mini", "pipeline/ljs/gpt-4o-mini", "C4"),
            ("E1", "no doc", "gpt-4o-mini", "nodoc_control/pipeline_c4/ljs/gpt-4o-mini", "C4"),
            ("E1", "with doc", "haiku-5.5", "second_judge/pipeline_c4/ljs/claude-haiku-5.5", "C4"),
            ("E1", "no doc", "haiku-5.5", "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5", "C4"),
            ("E5", "with doc", "gpt-4o-mini", "jwst_pipeline/ljs/gpt-4o-mini", "C4"),
            ("E5", "no doc", "gpt-4o-mini", "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini", "C4"),
            ("E5", "no doc", "haiku-5.5", "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5", "C4"),
            ("C0", "with doc", "gpt-4o-mini", "c0_minimal_prompt/ljs/gpt-4o-mini", "C1"),
            ("C0", "no doc", "gpt-4o-mini", "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini", "C1"),
            ("C0", "no doc", "haiku-5.5", "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5", "C1")]
    rows = []
    for exp, doc, judge, d, cond in sets:
        lj = load_ljs(d)
        lj = lj[lj.condition == cond]
        for llm in model_sort(lj.llm):
            g = lj[lj.llm == llm]
            rows.append([exp, doc, judge, m(llm), fmt(g.ljs.mean(), 3), fmt(g.ljs_strict.mean(), 3),
                         fmt(g.ljs_lenient.mean(), 3)] + [fmt(g[f"ieee_{a}"].mean() * 100, 1) for a in IEEE])
    write_paper_table(OUT / "sup_attributes.tex",
                      "LJS and ISO/IEC/IEEE 29148 quality attributes per experiment, version of the models (with or "
                      "without doc comments), judge and model (C4; C1 for C0). Attributes: \\% of applicable "
                      "requirements with the attribute met.", "tab:sup_attributes",
                      ["Exp.", "Doc", "Judge", "Model", "LJS", "Strict", "Lenient", "Corr.", "Compl.", "Unamb.",
                       "Verif.", "Trace."], "llllrrrrrrrr", rows, wide=True, placement="p")


def sup_kappa() -> None:
    k = pd.read_csv(RESULTS_DIR / "revision_summary" / "kappa.csv")
    rows = [[r.set, r.item, str(int(r.n)), fmt(r._4, 1), fmt(r.kappa, 3)] for r in k.itertuples()]
    write_paper_table(OUT / "sup_kappa.tex", "Agreement between \\llm{gpt-4o-mini} and \\llm{claude-haiku-5.5} per "
                      "requirement (models judged by both): raw agreement and Cohen's $\\kappa$, for the status "
                      "(satisfied, partial, missing, not applicable) and each quality attribute.", "tab:sup_kappa",
                      ["Set", "Item", "n", "Agreement \\%", "$\\kappa$"], "llrrr", rows, placement="h")


def _short(text: str, n: int) -> str:
    text = str(text)
    return text if len(text) <= n else text[: n - 1] + "…"


def sup_pilot_errors() -> None:
    t = pd.read_csv(A / "a01b_boilerplate" / "remaining_error_types.csv")
    rows = []
    for rel in ("2024-04.1", "2026-08"):
        sub = t[t.release == rel].head(10)
        rows.append([f"\\multicolumn{{4}}{{l}}{{\\textit{{Release {rel}, with imports and connector ends rewritten}}}} \\\\"])
        rows += [[esc(_short(r.type, 60)), str(int(r.models)), str(int(r.issues)),
                  f"\\texttt{{{esc(_short(r.example_code, 70))}}}"] for r in sub.itertuples()]
    write_paper_table(OUT / "sup_pilot_errors.tex", "Errors that remain in the final models (valid for our ANTLR "
                      "validator) after the deterministic fixes of the import normalisation and the rewriting of "
                      "connector ends, per Pilot release: type, models and issues affected, and an example line.",
                      "tab:sup_pilot_errors", ["Type", "Models", "Issues", "Example"], "lrrl", rows, wide=True,
                      placement="p")
    t2 = pd.read_csv(A / "a15_extended_b" / "remaining_2026_b_extended.csv")
    rows = [[m(r.llm), tex(r.code), str(int(r.models)), f"\\texttt{{{esc(_short(r.example_line, 75))}}}"]
            for r in t2.groupby("llm").head(6).itertuples()]
    write_paper_table(OUT / "sup_pilot_2026.tex", "Errors of release 2026-08 that remain after the reference stage "
                      "and the extended rewriting of references \\texttt{A::x} as \\texttt{A.x}, per model.",
                      "tab:sup_pilot_2026", ["Model", "Validation rule", "Models", "Example"], "llrl", rows,
                      wide=True, placement="h")
    t3 = pd.read_csv(A / "a14_guard_rejections" / "antlr_error_types.csv")
    rows = [[esc(_short(r.type, 70)), str(int(r.answers)), str(int(r.pilot_parses_line)),
             f"\\texttt{{{esc(_short(r.example_line, 60))}}}"] for r in t3.itertuples()]
    write_paper_table(OUT / "sup_guard_rejections.tex", "Answers of the reference stage rejected by the grammar guard "
                      "(our ANTLR validator): type of the first error, number of answers, answers whose offending line "
                      "the Pilot 2024-04.1 parses without a syntax error, and an example.", "tab:sup_guard_rejections",
                      ["Type", "Answers", "Pilot parses", "Example"], "lrrl", rows, wide=True, placement="h")
    ex = pd.read_csv(A / "a01b_boilerplate" / "prompt_kb_examples.csv")
    ex = ex[(ex.intended == "valid") & ex.status.isin(["syntax error", "validation error"])]
    rows = [[r.release, tex(r.source), esc(_short(r.where, 45)), r.status, esc(_short(r.reason, 80))]
            for r in ex.itertuples()]
    write_paper_table(OUT / "sup_prompt_kb_examples.tex", "Code examples of the frozen generation prompt and of the "
                      "knowledge bases, intended as valid, that the Pilot rejects for a reason other than names the "
                      "fragment does not declare (validated with the minimal library imports).",
                      "tab:sup_prompt_kb_examples", ["Release", "Source", "Where", "Status", "Reason"], "lllll", rows,
                      wide=True, placement="h")


def md_to_latex(md: str) -> str:
    """Minimal Markdown to LaTeX for the case files: headings, code fences, bullets, inline code, bold."""
    out, in_code, in_list = [], False, False

    def inline(s: str) -> str:
        res = []
        for p in re.split(r"(`[^`]*`)", s):
            if p.startswith("`") and p.endswith("`") and len(p) > 1:
                res.append(code(p[1:-1]))
            else:
                q = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", esc(p))
                res.append(q.replace("<->", "$\\leftrightarrow$").replace("->", "$\\rightarrow$").replace("—", "---"))
        return "".join(res)

    for line in md.splitlines():
        if line.startswith("```"):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            out.append("\\begin{lstlisting}[style=sysml]" if not in_code else "\\end{lstlisting}")
            in_code = not in_code
            continue
        if in_code:
            out.append(line)
            continue
        if line.startswith("# "):
            continue
        if line.startswith("### "):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            out.append("\\paragraph{" + inline(line[4:]) + "}")
            continue
        if line.startswith("## "):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            out.append("\\subsubsection*{" + inline(line[3:]) + "}")
            continue
        stripped = line.lstrip()
        if stripped.startswith("- "):
            if not in_list:
                out.append("\\begin{itemize}")
                in_list = True
            out.append("\\item " + inline(stripped[2:]))
            continue
        if in_list and not stripped:
            out.append("\\end{itemize}")
            in_list = False
        if stripped.startswith("|"):
            continue  # markdown tables are given as LaTeX tables elsewhere
        out.append(inline(line))
    if in_list:
        out.append("\\end{itemize}")
    if in_code:
        out.append("\\end{lstlisting}")
    return "\n".join(out) + "\n"


def _with_review(md: str) -> str:
    """Replaces the 'to be judged by hand' line of each interface case by the answers of the human review."""
    review = pd.read_csv(A / "r11_interface_review" / "review_sheet_completed.csv").set_index("case")
    parts = re.split(r"(?m)^(?=## Case \d+:)", md)
    for i, part in enumerate(parts):
        hit = re.match(r"## Case (\d+):.*interface `([^`]+)`", part)
        if not hit:
            continue
        r = review.loc[int(hit.group(1))]
        assert r.interface == hit.group(2), (r.interface, hit.group(2))
        worse = r.Q3_requirement_worse + (f" ({r.Q3_requirements})" if isinstance(r.Q3_requirements, str) else "")
        parts[i] = re.sub(r"(?m)^Still models a connection.*$", lambda _: (
            f"**Manual review** ({r.reviewer}). Connection between identifiable parts before the repair: "
            f"{r.Q1_connection_before} ({r.Q1_parts}). The same connection after the repair: {r.Q2_connection_after}. "
            f"A requirement of the category represented worse after the repair: {worse}. {r.comment}"), part)
    return "".join(parts)


def sup_cases() -> None:
    (OUT / "sup_interface_cases.tex").write_text(
        md_to_latex(_with_review((A / "r11_pilot_repair" / "interface_def_cases.md").read_text(encoding="utf-8"))),
        encoding="utf-8")
    text = (A / "a07_c3_vs_c2" / "c3_vs_c2_cases.md").read_text(encoding="utf-8")
    text = re.sub(r"## Answers to CONSTRAINT_EXPR diagnostics \(% of calls\)\n\n(\|.*\n)+", "", text)
    (OUT / "sup_c3_cases.tex").write_text(md_to_latex(text), encoding="utf-8")
    print(f"  wrote {OUT / 'sup_interface_cases.tex'} and sup_c3_cases.tex")


def sup_ref_equivalence() -> None:
    r = pd.read_csv(A / "a17_ref_equivalence" / "references.csv")
    old, new = r[r.release == "2024-04.1"].reset_index(drop=True), r[r.release == "2026-08"].reset_index(drop=True)
    old = old.assign(chain_2026=new.target_after.notna() & (old.verdict == "same element"),
                     same_2026=new.target_after == old.target_before)
    rows = []
    for doc, llm in [(d, l) for d in sorted(old.document.unique()) for l in model_sort(old.llm)]:
        g = old[(old.document == doc) & (old.llm == llm)]
        rows.append([doc, m(llm), str(len(g)), str(int((g.verdict == "same element").sum())),
                     str(int((g.verdict == "different element").sum())),
                     str(int((g.verdict == "qualified name not resolved").sum())),
                     str(int(g.chain_2026.sum())), str(int((g.chain_2026 & g.same_2026).sum()))])
    write_paper_table(OUT / "sup_ref_equivalence.tex", "Rewriting (b) extended: does the feature chain \\texttt{A.x} "
                      "reach the element of the qualified name \\texttt{A::x}? Every reference rewritten in the final "
                      "models of the reference stage, linked by the Pilot Implementation before and after the rewriting. "
                      "2024-04.1: element of \\texttt{A::x} before against element reached by \\texttt{A.x} after (same, "
                      "different, or \\texttt{A::x} not resolved). 2026-08, where \\texttt{A::x} no longer resolves: "
                      "chains that resolve, and those that reach the element of \\texttt{A::x} in 2024-04.1.",
                      "tab:sup_ref_equivalence", ["Document", "Model", "Rewritten", "Same", "Different", "Unresolved",
                                                  "Resolved 26-08", "Same 26-08"], "llrrrrrr", rows, placement="h",
                      header=["& & & \\multicolumn{3}{c}{2024-04.1} & \\multicolumn{2}{c}{2026-08} \\\\ "
                              "\\cmidrule(lr){4-6}\\cmidrule(lr){7-8}"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sup_extraction()
    sup_attributes()
    sup_kappa()
    sup_pilot_errors()
    sup_ref_equivalence()
    sup_cases()


if __name__ == "__main__":
    main()
