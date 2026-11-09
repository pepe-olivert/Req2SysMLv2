"""A14 (no LLM calls). R11 answers rejected by the guard because our ANTLR validator rejected them, and a stricter
definition of stagnation for R11.

1. Every repair answer of R11 that the guard finally rejected for breaking our ANTLR validity (stored in
   results/pilot_repair/repairs.jsonl as code_after of the retry; the first answers of accepted retries were not
   stored) is validated with the Pilot 2024-04.1 (official grammar): how many have no Pilot syntax error, the types
   of the ANTLR errors (message pattern and construct of the offending line) with an example, and, per type, how
   many of its answers the Pilot parses without a syntax error at that line (candidate constructs that the official
   grammar accepts and our ANTLR translation rejects; checked by hand in the summary).
2. Stagnation redefined: an iteration is stagnant when neither the diagnostics nor the model change during it (the
   loop's flag only compares diagnostics). Frequency per model and document.

    python -m evaluation.analysis.a14_guard_rejections
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from core.agents.agent2.logic import SysMLAgent
from core.config import RESULTS_DIR
from evaluation.analysis.a01_tool_acceptance import parse_issues
from evaluation.analysis.a01b_boilerplate import run_texts, sha20
from evaluation.analysis.common import fmt, jsonl, md_table, out_dir, write_md

SRC = RESULTS_DIR / "pilot_repair"
DOC = {"E1": "EIRENE", "E5": "JWST"}


def antlr_type(message: str, line_text: str) -> str:
    m = re.match(r"(mismatched input|extraneous input|no viable alternative at input|missing)\s+('(?:[^'\\]|\\.)*'|\S+)",
                 message)
    kind, token = (m.group(1), m.group(2)) if m else (message.split(" ")[0], "")
    kw = re.match(r"\s*((?:private\s+|public\s+)?\w+(?:\s+def)?)", line_text)
    return f"{kind} {token[:30]} | line starts with `{kw.group(1) if kw else '?'}`"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pilot-root", type=Path, default=Path.home() / "tools" / "pilot")
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work_a14")
    args = parser.parse_args()
    out = out_dir("a14_guard_rejections")
    agent = SysMLAgent.__new__(SysMLAgent)

    reps = jsonl(SRC / "repairs.jsonl")
    rejected = [r for r in reps if r.get("guard_rejected") == "antlr"]
    texts = {}
    rows = []
    for r in rejected:
        code = agent.clean_sysml(r["code_after"])
        texts[sha20(code)] = code
        errs = agent.validate_sysml(code)
        lines = code.splitlines()
        for k, e in enumerate(errs):
            ln = e.get("line")
            text = lines[ln - 1] if isinstance(ln, int) and 0 < ln <= len(lines) else ""
            rows.append({"set": r["set"], "llm": r["llm"], "run": r["run"], "category": r["category"],
                         "iteration": r["iteration"], "sha": sha20(code), "first_error": k == 0, "line": ln,
                         "message": e.get("error"), "line_text": text.strip()[:160],
                         "type": antlr_type(e.get("error") or "", text)})
    (args.work / "2024-04.1").mkdir(parents=True, exist_ok=True)
    (args.work / "2024-04.1" / "cache.tsv").touch()
    run_texts(args.pilot_root, "2024-04.1", args.work, texts, 4)
    issues = parse_issues(args.work / "2024-04.1" / "cache.tsv", set())
    issues = issues[issues.sha.isin(texts)]
    syntax = issues[issues.group == "syntax"]
    syntax_lines = syntax.groupby("sha").line.apply(set).to_dict()
    errors_any = set(issues[issues.group.isin(["syntax", "name_other", "name_library", "validation"])].sha)

    per_answer = pd.DataFrame([{"sha": s, "pilot_syntax_ok": s not in syntax_lines, "pilot_accepted": s not in errors_any}
                               for s in texts])
    err = pd.DataFrame(rows)
    err["pilot_syntax_error_on_line"] = err.apply(lambda r: r.line in syntax_lines.get(r.sha, set()), axis=1)
    err.to_csv(out / "antlr_errors_of_rejected_answers.csv", index=False)
    first = err[err.first_error]
    types = (first.groupby("type").agg(answers=("sha", "nunique"),
                                       pilot_parses_line=("pilot_syntax_error_on_line", lambda s: int((~s).sum())),
                                       example_line=("line_text", "first"), example_message=("message", "first"))
             .reset_index().sort_values("answers", ascending=False))
    types.to_csv(out / "antlr_error_types.csv", index=False)

    # Stagnation redefined: no change in the diagnostics AND no change in the model during the iteration.
    traces = {}
    for t in jsonl(SRC / "iteration_trace.jsonl"):
        traces.setdefault((t["set"], t["llm"], int(t["run"]), t["category"]), {})[int(t["iteration"])] = \
            sorted((e["line"], e["column"], e["error"]) for e in t["errors"])
    by_iter = {}
    for r in reps:
        key = (r["set"], r["llm"], int(r["run"]), r["category"])
        by_iter.setdefault(key, {}).setdefault(int(r["iteration"]), []).append(r)
    st_rows = []
    for key, its in by_iter.items():
        tr = traces.get(key, {})
        for it, calls in sorted(its.items()):
            start = agent.clean_sysml(calls[0]["code_before"])
            end = start
            for c in calls:
                if not c.get("guard_rejected"):
                    end = agent.clean_sysml(c["code_after"])
            same_diag = tr.get(it - 1) == tr.get(it)
            st_rows.append({"set": key[0], "llm": key[1], "run": key[2], "category": key[3], "iteration": it,
                            "same_diagnostics": same_diag, "same_model": start == end,
                            "stagnant_old": same_diag, "stagnant_new": same_diag and start == end})
    st = pd.DataFrame(st_rows)
    st["document"] = st.set.map(DOC)
    st.to_csv(out / "stagnation_per_iteration.csv", index=False)
    per_model = st.groupby(["document", "llm", "run", "category"]).agg(old=("stagnant_old", "any"),
                                                                       new=("stagnant_new", "any")).reset_index()
    freq = per_model.groupby(["document", "llm"]).agg(models_repaired=("old", "size"),
                                                      stagnant_models_old=("old", "sum"),
                                                      stagnant_models_new=("new", "sum")).reset_index()
    it_freq = st.groupby(["document", "llm"]).agg(iterations=("stagnant_old", "size"),
                                                  stagnant_iterations_old=("stagnant_old", "sum"),
                                                  stagnant_iterations_new=("stagnant_new", "sum")).reset_index()
    freq = freq.merge(it_freq, on=["document", "llm"])
    freq.to_csv(out / "stagnation_frequency.csv", index=False)

    n = len(texts)
    ok = int(per_answer.pilot_syntax_ok.sum())
    acc = int(per_answer.pilot_accepted.sum())
    write_md(out / "summary.md", "A14. Guard rejections for ANTLR validity, and stagnation in R11", [
        f"Answers finally rejected by the guard for breaking ANTLR validity: {len(rejected)} ({n} distinct). Pilot "
        f"2024-04.1: {ok} of them ({100 * ok / n:.1f}%) have no syntax error; {acc} are accepted with no error at "
        "all. Only the rejected (second) answers are stored; the first answers of retries that were then accepted "
        "were not.",
        "## ANTLR error types (first error of each answer)", md_table(types),
        "## Stagnation (old: diagnostics unchanged; new: diagnostics and model unchanged)", md_table(freq)])
    print(f"rejected {len(rejected)} ({n} distinct); Pilot syntax ok {ok}; accepted {acc}")


if __name__ == "__main__":
    main()
