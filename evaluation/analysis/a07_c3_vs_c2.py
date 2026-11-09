"""A7. Why C3 (router order + label, no KB) is worse than C2 (blind repair) on the E3 bank.

Dumps about ten cases of the E3 bank (gemini-3.5-flash-lite) to results/analysis/a07_c3_vs_c2/c3_vs_c2_cases.md:
the seven generations that C2 rescues and C3 does not, plus the three where both converge and C3 needs the most
extra iterations. For every repair call of C2 and C3: chosen diagnostic (line, column, message, router category),
its code block, the lines the answer changed, and the number of diagnostics before and after.

It also classifies every repair call on a CONSTRAINT_EXPR diagnostic (E3 bank and the revision conditions) by
what the answer did on the offending `assert` line:
- drops the `assert` keyword and keeps the expression (the fix the CONSTRAINT_EXPR KB prescribes: inside a
  constraint body the expression stands alone);
- wraps the expression in `assert constraint { ... }` / `constraint { ... }`;
- keeps the bare `assert` and edits the expression (operator, qualification, parentheses);
- deletes the statement; no change; other.

    python -m evaluation.analysis.a07_c3_vs_c2
"""

from __future__ import annotations

import difflib
import re
from collections import Counter

import pandas as pd

from core.agents.agent2.error_router import ErrorRouter
from core.agents.agent2.logic import SysMLAgent
from core.config import RESULTS_DIR
from evaluation.analysis.common import fmt, jsonl, md_table, out_dir, write_md, write_paper_table

MODEL = "gemini-3.5-flash-lite"
_OPERATOR_RE = re.compile(r"==|!=|<=|>=|<|>|\band\b|\bor\b|\bnot\b")


def changed(before: str, after: str) -> tuple[list[str], list[str]]:
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="", n=0))
    return ([l[1:] for l in diff if l.startswith("-") and not l.startswith("---")],
            [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")])


def classify(r: dict) -> str:
    removed, added = changed(r["code_before"], r["code_after"])
    if not removed and not added:
        return "no change"
    line = r["current_error"]["line"]
    lines = r["code_before"].splitlines()
    old = lines[line - 1] if line and line <= len(lines) else ""
    new = " ".join(added)
    if not re.search(r"\bassert\b", old):
        return "other"
    if re.search(r"\bconstraint\b", new) and "constraint" not in old:
        return "wraps in constraint"
    if not added:
        return "deletes the statement"
    if not re.search(r"\bassert\b", new):
        return "drops assert, keeps expression" if _OPERATOR_RE.search(new) or new.strip() else "deletes the statement"
    return "keeps bare assert, edits expression"


def block_of(agent: SysMLAgent, code: str, err: dict) -> str:
    for e in agent.validate_sysml(code):
        if e.get("line") == err["line"] and e.get("column") == err["column"]:
            return e.get("sysml_block") or ""
    return ""


def main() -> None:
    out = out_dir("a07_c3_vs_c2")
    agent = SysMLAgent.__new__(SysMLAgent)
    agent.router = ErrorRouter()
    res = pd.read_csv(RESULTS_DIR / "ablation_stress" / "ablation_results.csv")
    res = res[(res.llm == MODEL) & (res.initial_errors > 0)]
    w = res.pivot_table(index=["run", "category"], columns="condition", values=["converged", "iterations", "llm_calls"],
                        aggfunc="first")
    conv = w["converged"].astype(str) == "True"
    fails = w[(~conv["C3"]) & conv["C2"]].index.tolist()
    slower = w[conv["C3"] & conv["C2"]].assign(extra=lambda d: d["iterations"]["C3"] - d["iterations"]["C2"])
    slower = slower.sort_values("extra", ascending=False).head(3).index.tolist()
    reps = jsonl(RESULTS_DIR / "ablation_stress" / "repairs.jsonl")

    sections = []
    for kind, cases in (("C2 rescues, C3 does not", fails), ("both rescue, C3 needs the most extra iterations", slower)):
        for run, category in cases:
            sec = [f"## {category} (run {run}) — {kind}",
                   f"C2: converged={w.loc[(run, category), ('converged', 'C2')]}, "
                   f"iterations={w.loc[(run, category), ('iterations', 'C2')]}, "
                   f"calls={w.loc[(run, category), ('llm_calls', 'C2')] - 1}. "
                   f"C3: converged={w.loc[(run, category), ('converged', 'C3')]}, "
                   f"iterations={w.loc[(run, category), ('iterations', 'C3')]}, "
                   f"calls={w.loc[(run, category), ('llm_calls', 'C3')] - 1}."]
            for cond in ("C2", "C3"):
                seq = [r for r in reps if r["llm"] == MODEL and int(r["run"]) == int(run)
                       and r["category"] == category and r["condition"] == cond]
                sec.append(f"### {cond} ({len(seq)} calls; first 6 shown)")
                for r in seq[:6]:
                    e = r["current_error"]
                    removed, added = changed(r["code_before"], r["code_after"])
                    block = block_of(agent, r["code_before"], e).strip().splitlines()
                    sec.append(
                        f"- **iteration {r['iteration']}**, line {e['line']}, col {e['column']}, "
                        f"`{r['error_category']}`: {e['message'][:110]}\n"
                        f"  - block: `{' / '.join(x.strip() for x in block[:3])[:160]}`\n"
                        f"  - answer: " + ("; ".join(f"`-{x.strip()[:90]}`" for x in removed[:2])
                                           + " → " + "; ".join(f"`+{x.strip()[:90]}`" for x in added[:2])
                                           if removed or added else "no change") + "\n"
                        f"  - result: {len(r['errors_before'])} → {len(r['errors_after'])} diagnostics "
                        f"({classify(r) if r['error_category'] == 'CONSTRAINT_EXPR' else 'n/a'})")
            sections.append("\n".join(sec))

    # Classification of every CONSTRAINT_EXPR repair call.
    allreps = reps + jsonl(RESULTS_DIR / "ablation_stress_revision" / "repairs.jsonl")
    counts = {}
    for r in allreps:
        if r["error_category"] == "CONSTRAINT_EXPR":
            counts.setdefault((r["llm"], r["condition"]), Counter())[classify(r)] += 1
    kinds = ["drops assert, keeps expression", "wraps in constraint", "keeps bare assert, edits expression",
             "deletes the statement", "no change", "other"]
    rows = []
    for (llm, cond), c in sorted(counts.items()):
        n = sum(c.values())
        rows.append({"llm": llm, "condition": cond, "calls": n, **{k: round(100 * c[k] / n, 1) for k in kinds}})
    cls = pd.DataFrame(rows)
    cls.to_csv(out / "constraint_expr_answers.csv", index=False)
    order = ["C2", "C2KB", "C3", "C4", "FULLREV"]
    trows = []
    for llm in ["gpt-6-luna", "gemini-3.5-flash-lite"]:
        for cond in order:
            sel = cls[(cls.llm == llm) & (cls.condition == cond)]
            if sel.empty:
                continue
            r = sel.iloc[0]
            trows.append([llm.replace("_", r"\_"), cond, str(int(r.calls))] + [fmt(r[k], 1) for k in kinds[:4]])
    write_paper_table(
        out / "tab_constraint_expr_answers.tex",
        "What the repair answer did on the offending line of a \\textit{Constraint expr.} diagnostic (E3 bank, all "
        "repair calls on that category, \\%). Drops \\texttt{assert}: keeps the expression as the body of the "
        "enclosing constraint (the fix of the knowledge base). Keeps bare \\texttt{assert}: edits the operator, "
        "the qualification or the parentheses and keeps the invalid form.",
        "tab:constraint_expr_answers", ["Model", "Cond.", "Calls", "Drops assert", "Wraps in constraint",
                                        "Keeps bare assert", "Deletes"], "llrrrrr", trows)

    v = lambda llm, cond, k: cls[(cls.llm == llm) & (cls.condition == cond)][k].iloc[0]  # noqa: E731
    keep, drop = "keeps bare assert, edits expression", "drops assert, keeps expression"
    fl, lu = MODEL, "gpt-6-luna"
    hypothesis = (
        "## Hypothesis\n\n"
        "In these cases C2 and C3 mostly pick the same diagnostic on the same line (an `assert <expr>` that the "
        "grammar rejects; the router labels it CONSTRAINT_EXPR, priority 25), so the order is not what differs. "
        "What differs is the answer. With the label but without its knowledge base, flash-lite keeps the bare "
        "`assert` and edits the expression (`==` <-> `=`, `::` <-> `.`, parentheses), which leaves the statement "
        "invalid and often oscillates between two invalid forms until the iteration limit. Over all "
        f"CONSTRAINT_EXPR calls of the bank, flash-lite keeps the bare assert in {v(fl, 'C3', keep):.0f}% of the C3 "
        f"answers against {v(fl, 'C2', keep):.0f}% in C2, and drops the `assert` keyword (the fix) in "
        f"{v(fl, 'C3', drop):.0f}% against {v(fl, 'C2', drop):.0f}%. With the knowledge base it drops the keyword in "
        f"{v(fl, 'C2KB', drop):.0f}% (C2KB) and {v(fl, 'C4', drop):.0f}% (C4) of the answers. A plausible reading "
        "is that naming the category without its rule ('constraint expression') steers the model towards "
        "rewriting the expression instead of the statement around it. The pattern holds for flash-lite only: "
        f"gpt-6-luna keeps the bare assert in {v(lu, 'C2', keep):.0f}% (C2) and {v(lu, 'C3', keep):.0f}% (C3) of "
        "its answers, and C3 does not penalise luna. This is an observation on one model and one bank, not a "
        "tested mechanism.")
    write_md(out / "c3_vs_c2_cases.md", "A7. Why C3 is worse than C2 on the E3 bank (gemini-3.5-flash-lite)",
             [hypothesis, "## Answers to CONSTRAINT_EXPR diagnostics (% of calls)", md_table(cls)] + sections)


if __name__ == "__main__":
    main()
