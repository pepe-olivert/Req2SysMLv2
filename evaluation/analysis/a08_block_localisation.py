"""A8. Contextual localisation: repair calls whose extracted code block is a single line.

The repair message of C2-C4 (and C2KB) carries the code block of the current error, extracted by indentation
from the reported line (SysMLAgent._extract_block_by_indent). The block is rebuilt here with the same function
from the stored code_before and error line of every repair call (FULLREV sends no block and is left out).
A single-line block gives the model no context beyond the line itself.

    python -m evaluation.analysis.a08_block_localisation
"""

from __future__ import annotations

import pandas as pd

from core.agents.agent2.logic import SysMLAgent
from core.config import RESULTS_DIR
from evaluation.analysis.common import (CONDITION_ORDER, fmt, jsonl, md_table, model_sort, out_dir, tex, write_md,
                                        write_paper_table)

PHASES = {"E1 (EIRENE)": ["pipeline"], "E2 (EIRENE)": ["ablation"], "E3 bank": ["ablation_stress", "ablation_stress_revision"],
          "E5 (JWST)": ["jwst_pipeline"], "JWST bank": ["jwst_v1_bank", "jwst_v1_bank_flashlite"]}


def main() -> None:
    out = out_dir("a08_block_localisation")
    agent = SysMLAgent.__new__(SysMLAgent)
    rows = []
    for setting, phases in PHASES.items():
        for phase in phases:
            for r in jsonl(RESULTS_DIR / phase / "repairs.jsonl"):
                if r["condition"] == "FULLREV":
                    continue
                line = r["current_error"].get("line")
                lines = SysMLAgent.clean_sysml(r["code_before"]).splitlines()
                block = agent._extract_block_by_indent(lines, line) if isinstance(line, int) else ""
                n = len([x for x in block.splitlines()]) if block else 0
                rows.append({"setting": setting, "llm": r["llm"], "condition": r["condition"],
                             "error_category": r["error_category"], "block_lines": n})
    df = pd.DataFrame(rows)
    df.to_csv(out / "block_lines_per_call.csv.gz", index=False, compression="gzip")
    agg = (df.groupby(["setting", "llm", "condition"])
           .agg(calls=("block_lines", "size"), single_line=("block_lines", lambda s: int((s == 1).sum())),
                empty=("block_lines", lambda s: int((s == 0).sum())), median_lines=("block_lines", "median"))
           .reset_index())
    agg["single_line_pct"] = (agg.single_line / agg.calls * 100).round(1)
    agg.to_csv(out / "block_localisation.csv", index=False)
    by_cat = df.groupby("error_category").agg(calls=("block_lines", "size"),
                                              single_line_pct=("block_lines", lambda s: round((s == 1).mean() * 100, 1)))
    by_cat.reset_index().to_csv(out / "block_localisation_by_category.csv", index=False)

    trows = []
    for setting in PHASES:
        sub = agg[agg.setting == setting]
        for llm in model_sort(sub.llm):
            for c in [c for c in CONDITION_ORDER if c in set(sub[sub.llm == llm].condition)]:
                r = sub[(sub.llm == llm) & (sub.condition == c)].iloc[0]
                trows.append([tex(setting), tex(llm), c, str(r.calls), str(r.single_line), fmt(r.single_line_pct, 1),
                              fmt(r.median_lines, 0)])
    total = df.block_lines.eq(1).mean() * 100
    write_paper_table(
        out / "tab_block_localisation.tex",
        f"Repair calls whose code block (extracted by indentation from the reported line) is a single line, per "
        f"setting, model and condition; overall {total:.1f}\\% of {len(df):,} calls. Median: lines of the block. "
        "FULLREV sends no block.".replace(",", "{,}"),
        "tab:block_localisation", ["Setting", "Model", "Cond.", "Calls", "Single line", "\\%", "Median"],
        "lllrrrr", trows)
    write_md(out / "summary.md", "A8. Single-line code blocks in the repair calls",
             [f"Calls: {len(df)}; single-line block: {int(df.block_lines.eq(1).sum())} ({total:.1f}%); "
              f"empty block (no line): {int(df.block_lines.eq(0).sum())}.", md_table(agg),
              "## By router category", md_table(by_cat.reset_index())])


if __name__ == "__main__":
    main()
