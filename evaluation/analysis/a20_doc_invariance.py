"""A20. Does grammar-stage repair change the text that the no-doc control removes?

The grammar-stage pairs of tab:repair_semantics (C1 vs the repaired model) were judged with the doc comments. If
repair leaves the copied requirement text unchanged, both sides of each pair carry the same copied text, and the
paired change reflects only edits to the rest of the model. For every repaired model of E1, E5 and the four banks,
this compares the text removed by the no-doc control (evaluation.nodoc_control: every doc comment, and every other
comment or note with requirement text) before and after repair. No LLM calls.

    python -m evaluation.analysis.a20_doc_invariance
"""

from __future__ import annotations

import re

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.common import SETS, jsonl, md_table, model_sort, out_dir, write_md
from evaluation.nodoc_control import (_BLOCK_RE, _COMMENT_RE, _DOC_RE, _NOTE_BLOCK_RE, _NOTE_LINE_RE, leaks,
                                      requirement_ngrams, words)

GROUPS = [("E1", ["E1"]), ("E5", ["E5"]), ("E3", ["E3", "E3rev"]), ("E6", ["R9", "R9b"])]


def removed_text(code: str, requirements: list[str]) -> list[str]:
    """The segments that strip_requirement_text removes, in the same order, whitespace-normalised."""
    grams = requirement_ngrams(requirements)
    removed = []

    def keep_if_clean(m: re.Match) -> str:
        if leaks(words(m.group(0)), grams):
            removed.append(" ".join(m.group(0).split()))
            return ""
        return m.group(0)

    def drop(m: re.Match) -> str:
        removed.append(" ".join(m.group(0).split()))
        return ""

    code = _NOTE_BLOCK_RE.sub(keep_if_clean, code)
    code = _DOC_RE.sub(drop, code)
    code = _COMMENT_RE.sub(keep_if_clean, code)
    code = _BLOCK_RE.sub(keep_if_clean, code)
    _NOTE_LINE_RE.sub(keep_if_clean, code)
    return removed


def main() -> None:
    out = out_dir("a20_doc_invariance")
    rows = []
    for group, names in GROUPS:
        models = {}
        for name in names:
            for r in jsonl(RESULTS_DIR / SETS[name].phase_dir / "sysml_models.jsonl"):
                models[(r["llm"], r["run"], r["category"], r["condition"])] = r
        for (llm, run, cat, cond), r in models.items():
            base = models.get((llm, run, cat, "C1"))
            if cond == "C1" or base is None or base["sysml_code"] == r["sysml_code"]:
                continue
            before = removed_text(base["sysml_code"], base["requirements"])
            after = removed_text(r["sysml_code"], r["requirements"])
            rows.append({"set": group, "llm": llm, "condition": cond, "run": run, "category": cat,
                         "segments_before": len(before), "segments_after": len(after),
                         "identical": before == after})
    df = pd.DataFrame(rows)
    df[~df.identical].to_csv(out / "changed_cases.csv", index=False)
    summary = (df.groupby(["set", "llm", "condition"], as_index=False)
               .agg(repaired=("identical", "size"), identical=("identical", "sum")))
    summary["llm_order"] = summary.llm.map({m: i for i, m in enumerate(model_sort(summary.llm))})
    summary = summary.sort_values(["set", "llm_order", "condition"]).drop(columns="llm_order")
    total = pd.DataFrame([{"set": "all", "llm": "all", "condition": "all", "repaired": len(df),
                           "identical": int(df.identical.sum())}])
    summary = pd.concat([summary, total], ignore_index=True)
    summary.to_csv(out / "doc_invariance.csv", index=False)
    write_md(out / "summary.md", "A20. Copied requirement text before and after grammar-stage repair",
             ["Repaired models (code changed) of E1, E5 and the four banks; identical: the text removed by the no-doc "
              "control is the same, segment by segment, before and after repair.", md_table(summary),
              "## Models where it changed", md_table(df[~df.identical])])
    print(f"  identical removed text in {int(df.identical.sum())} of {len(df)} repaired models")


if __name__ == "__main__":
    main()
