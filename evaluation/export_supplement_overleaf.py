"""Copies the tables and figures of the Supplementary Material in the layout of the Overleaf project.

paper/supplementary.tex reads tables/<name>.tex and figures/<name>.png. This writes them, with
paper/supplementary.tex itself, to results/paper_tables/overleaf_supplement/. Every float is fixed where it is
\\input ([H] of the float package; one column, so table* becomes table). No LLM calls.

    python -m evaluation.export_supplement_overleaf
"""

from __future__ import annotations

import re
import shutil

from core.config import REPO_ROOT, RESULTS_DIR

OUT = RESULTS_DIR / "paper_tables" / "overleaf_supplement"
A = RESULTS_DIR / "analysis"
SUP = RESULTS_DIR / "paper_tables" / "supplement"

TABLES = [
    SUP / "sup_extraction.tex",
    SUP / "sup_jaccard.tex",
    A / "a06_extraction_truncation" / "tab_extraction_truncation.tex",
    SUP / "sup_input_coverage.tex",
    RESULTS_DIR / "extraction" / "tables" / "tab_manual_validation.tex",
    A / "a22_extraction_agreement" / "tab_extraction_agreement.tex",
    SUP / "sup_attributes.tex",
    SUP / "sup_kappa.tex",
    A / "a23_judge_human_agreement" / "tab_judge_human.tex",
    A / "a05_not_applicable" / "tab_not_applicable.tex",
    A / "a02_richness" / "tab_richness_ljs.tex",
    A / "a13_missing_judgments" / "tab_missing_bounds.tex",
    A / "a04_cluster_stats" / "tab_cluster_means.tex",
    A / "a04_cluster_stats" / "tab_cluster_tests.tex",
    A / "a10_e1_e2_variability" / "tab_e1_e2_variability.tex",
    RESULTS_DIR / "ablation" / "tables" / "tab_ablation_tests.tex",
    A / "a03_repair_diff" / "tab_repair_diff.tex",
    A / "a08_block_localisation" / "tab_block_localisation.tex",
    A / "a07_c3_vs_c2" / "tab_constraint_expr_answers.tex",
    SUP / "sup_c3_cases.tex",
    A / "a01b_boilerplate" / "tab_tool_acceptance.tex",
    SUP / "sup_pilot_errors.tex",
    SUP / "sup_prompt_kb_examples.tex",
    SUP / "sup_guard_rejections.tex",
    SUP / "sup_pilot_2026.tex",
    SUP / "sup_interface_cases.tex",
    SUP / "sup_ref_equivalence.tex",
    A / "a19_tokens" / "tab_sup_tokens.tex",
]
FIGURES = [RESULTS_DIR / "extraction" / "figures" / "fig_extraction_pareto.png"]


def fixed_floats(tex: str) -> str:
    tex = re.sub(r"\\begin\{table\*?\}(\[[^]]*\])?", r"\\begin{table}[H]", tex)
    return tex.replace("\\end{table*}", "\\end{table}")


def main() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    for src in TABLES:
        (OUT / "tables" / src.name).write_text(fixed_floats(src.read_text(encoding="utf-8")), encoding="utf-8")
    for src in FIGURES:
        shutil.copyfile(src, OUT / "figures" / src.name)
    shutil.copyfile(REPO_ROOT / "paper" / "supplementary.tex", OUT / "supplementary.tex")
    print(f"  wrote {len(TABLES)} tables, {len(FIGURES)} figures and supplementary.tex to {OUT}")


if __name__ == "__main__":
    main()
