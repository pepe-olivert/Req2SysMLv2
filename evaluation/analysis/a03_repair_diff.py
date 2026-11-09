"""A3. Changes introduced by the repair: line diff between the generated and the repaired model.

For every repaired row (generation with at least one initial diagnostic, repair condition), the generated code
(after clean_sysml, the text the parser saw) is compared line by line with the final code (difflib opcodes):
added and deleted lines, modified lines (a replaced block counts min(old, new) modified lines and the rest as
added or deleted) and the share of generated lines kept unchanged. Median, P90 and maximum per bank, model and
condition (FULLREV included). E1 and E5 C4 are included as the pipeline setting.

    python -m evaluation.analysis.a03_repair_diff
"""

from __future__ import annotations

import difflib

import numpy as np
import pandas as pd

from core.agents.agent2.logic import SysMLAgent
from evaluation.analysis.common import (CONDITION_ORDER, fmt, load_models, md_table, model_sort, out_dir, tex,
                                        write_md, write_paper_table)

BANKS = {"E1": "E1 (EIRENE)", "E5": "E5 (JWST)", "E3": "E3 bank", "E3rev": "E3 bank", "R9": "JWST bank",
         "R9b": "JWST bank"}


def line_diff(before: str, after: str) -> dict:
    a, b = before.splitlines(), after.splitlines()
    added = deleted = modified = equal = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            equal += i2 - i1
        elif tag == "insert":
            added += j2 - j1
        elif tag == "delete":
            deleted += i2 - i1
        else:
            k = min(i2 - i1, j2 - j1)
            modified += k
            added += (j2 - j1) - k
            deleted += (i2 - i1) - k
    return {"lines_before": len(a), "added": added, "deleted": deleted, "modified": modified,
            "unchanged_pct": 100.0 * equal / len(a) if a else np.nan}


def main() -> None:
    out = out_dir("a03_repair_diff")
    rows = []
    for name, bank in BANKS.items():
        m = load_models(name)
        m = m[(m.condition != "C1") & (m.initial_errors.fillna(0) > 0)]
        for r in m.itertuples():
            d = line_diff(SysMLAgent.clean_sysml(r.generated_code), r.sysml_code)
            rows.append({"bank": bank, "set": name, "llm": r.llm, "condition": r.condition, "run": r.run,
                         "category": r.category, "valid": r.valid, **d})
    df = pd.DataFrame(rows)
    df["changed_lines"] = df.added + df.deleted + df.modified
    df.to_csv(out / "repair_diff_per_model.csv", index=False)

    def q(s, p):
        return float(np.percentile(s, p))
    agg = (df.groupby(["bank", "llm", "condition"])
           .agg(n=("changed_lines", "size"),
                changed_median=("changed_lines", "median"), changed_p90=("changed_lines", lambda s: q(s, 90)),
                changed_max=("changed_lines", "max"),
                added_median=("added", "median"), deleted_median=("deleted", "median"),
                modified_median=("modified", "median"),
                unchanged_median=("unchanged_pct", "median"), unchanged_p10=("unchanged_pct", lambda s: q(s, 10)),
                unchanged_min=("unchanged_pct", "min"))
           .reset_index())
    agg.to_csv(out / "repair_diff_summary.csv", index=False)

    order = ["E1 (EIRENE)", "E5 (JWST)", "E3 bank", "JWST bank"]
    trows = []
    for bank in order:
        sub = agg[agg.bank == bank]
        for llm in model_sort(sub.llm):
            for c in [c for c in CONDITION_ORDER if c in set(sub[sub.llm == llm].condition)]:
                a = sub[(sub.llm == llm) & (sub.condition == c)].iloc[0]
                trows.append([tex(bank), tex(llm), c, str(int(a.n)), fmt(a.changed_median, 0), fmt(a.changed_p90, 0),
                              str(int(a.changed_max)), fmt(a.unchanged_median, 1), fmt(a.unchanged_p10, 1),
                              fmt(a.unchanged_min, 1)])
    write_paper_table(
        out / "tab_repair_diff.tex",
        "Lines changed by the repair (line diff between the generated and the final model of each repaired "
        "generation): added + deleted + modified lines (median, 90th percentile and maximum) and share of the "
        "generated lines kept unchanged (median, 10th percentile and minimum, \\%).",
        "tab:repair_diff", ["Setting", "Model", "Cond.", "n", "Changed med.", "P90", "Max", "Unchanged med.",
                            "P10", "Min"], "lllrrrrrrr", trows, wide=True)
    write_md(out / "summary.md", "A3. Changes introduced by the repair", [md_table(agg)])


if __name__ == "__main__":
    main()
