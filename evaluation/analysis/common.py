"""Shared helpers of the phase-3 analyses (no LLM calls): model sets, loaders and final-format LaTeX tables.

Every analysis writes to results/analysis/<name>/ (CSV, markdown, and LaTeX tables ready for \\input in main.tex).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from core.config import RESULTS_DIR

ANALYSIS_DIR = RESULTS_DIR / "analysis"
KEYS = ["pdf", "llm", "condition", "run", "category"]
MODEL_ORDER = ["gpt-6.1-sol", "gpt-6-luna", "gemini-3.7-flash", "gemini-3.5-flash-lite"]
CONDITION_ORDER = ["C1", "C2", "C2KB", "C3", "C4", "FULLREV"]
IEEE = ["correctness", "completeness", "unambiguity", "verifiability", "traceability"]


@dataclass(frozen=True)
class ModelSet:
    name: str        # short id used in tables
    document: str    # EIRENE | JWST
    experiment: str  # E1, E5, E3 bank, ...
    prompt: str      # guided | c0_minimal | v1
    phase_dir: str   # under results/
    results: str     # results CSV name


# Every stored set of SysML models of the paper and of the revision.
MODEL_SETS = [
    ModelSet("E1", "EIRENE", "E1", "guided", "pipeline", "pipeline_results.csv"),
    ModelSet("E2", "EIRENE", "E2", "guided", "ablation", "ablation_results.csv"),
    ModelSet("E3", "EIRENE", "E3 bank", "v1", "ablation_stress", "ablation_results.csv"),
    ModelSet("E3rev", "EIRENE", "E3 bank", "v1", "ablation_stress_revision", "ablation_results.csv"),
    ModelSet("E4", "EIRENE", "E4 (C0)", "c0_minimal", "c0_minimal_prompt", "pipeline_results.csv"),
    ModelSet("R3", "EIRENE", "R3 (sol input)", "guided", "input_control_sol", "pipeline_results.csv"),
    ModelSet("E5", "JWST", "E5", "guided", "jwst_pipeline", "pipeline_results.csv"),
    ModelSet("E5C0", "JWST", "C0", "c0_minimal", "jwst_c0_bank", "pipeline_results.csv"),
    ModelSet("R9", "JWST", "R9 bank", "v1", "jwst_v1_bank", "pipeline_results.csv"),
    ModelSet("R9b", "JWST", "R9b bank", "v1", "jwst_v1_bank_flashlite", "pipeline_results.csv"),
]
SETS = {s.name: s for s in MODEL_SETS}


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_results(name: str) -> pd.DataFrame:
    s = SETS[name]
    df = pd.read_csv(RESULTS_DIR / s.phase_dir / s.results)
    df["converged"] = df["converged"].astype(str).str.lower() == "true"
    df["repair_calls"] = df["llm_calls"] - 1
    df["repair_cost"] = df["cost_usd"] - df["generation_cost_usd"]
    return df.assign(set=name, document=s.document, prompt=s.prompt)


def load_models(name: str) -> pd.DataFrame:
    """Final SysML code of every row (last record of a key wins, as in the evaluator) plus the generated code."""
    s = SETS[name]
    rows = {}
    for r in jsonl(RESULTS_DIR / s.phase_dir / "sysml_models.jsonl"):
        rows[tuple(str(r[k]) for k in KEYS)] = r
    gens = {(g["llm"], str(g["run"]), g["category"]): g["raw_output"]
            for g in jsonl(RESULTS_DIR / s.phase_dir / "generations.jsonl")}
    out = []
    for r in rows.values():
        out.append({**{k: r[k] for k in KEYS}, "run": int(r["run"]), "requirements": r["requirements"],
                    "sysml_code": r["sysml_code"], "valid": r.get("valid"), "initial_errors": r.get("initial_errors"),
                    "generated_code": gens.get((r["llm"], str(r["run"]), r["category"]))})
    return pd.DataFrame(out).assign(set=name, document=s.document, prompt=s.prompt)


def load_ljs(judge_dir: str) -> pd.DataFrame | None:
    path = RESULTS_DIR / judge_dir / "ljs_results.csv"
    return pd.read_csv(path) if path.exists() else None


def model_sort(names) -> list[str]:
    names = list(dict.fromkeys(names))
    return [m for m in MODEL_ORDER if m in names] + [m for m in names if m not in MODEL_ORDER]


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def out_dir(name: str) -> Path:
    d = ANALYSIS_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def tex(text) -> str:
    return str(text).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")


def fmt(value, digits: int = 1) -> str:
    """Formatted number; missing values are left empty (never filled)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return f"{value:.{digits}f}"


def fmt_p(p) -> str:
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "--"
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def write_paper_table(path: Path, caption: str, label: str, columns: list[str], align: str,
                      rows: list[list[str]], wide: bool = False, placement: str = "t",
                      header: list[str] | None = None) -> None:
    """LaTeX table in its final format (caption, label, adjustbox), ready for \\input in main.tex.

    A row with a single cell is written as a raw LaTeX line (e.g. \\midrule). `header`: raw LaTeX lines written
    between \\toprule and the column names (multi-level headers).
    """
    env = "table*" if wide else "table"
    width = r"\textwidth" if wide else r"\columnwidth"
    lines = [f"\\begin{{{env}}}[{placement}]", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}",
             f"\\begin{{adjustbox}}{{max width={width}}}", f"\\begin{{tabular}}{{{align}}}", "\\toprule",
             *(header or []), " & ".join(columns) + r" \\", "\\midrule"]
    for row in rows:
        lines.append(row[0] if len(row) == 1 else " & ".join(row) + r" \\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", f"\\end{{{env}}}", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote {path}")


def write_long_table(path: Path, caption: str, label: str, columns: list[str], align: str,
                     rows: list[list[str]]) -> None:
    """Multi-page table (longtable, footnotesize) with the header repeated on every page; same row rules as
    write_paper_table. Needs \\usepackage{longtable} in the document."""
    head = ["\\toprule", " & ".join(columns) + r" \\", "\\midrule"]
    lines = ["{\\footnotesize\\setlength{\\tabcolsep}{4pt}", f"\\begin{{longtable}}{{{align}}}",
             f"\\caption{{{caption}}}\\label{{{label}}} \\\\", *head, "\\endfirsthead",
             f"\\multicolumn{{{len(columns)}}}{{l}}{{\\textit{{(continued)}}}} \\\\", *head, "\\endhead",
             "\\bottomrule", "\\endlastfoot"]
    for row in rows:
        lines.append(row[0] if len(row) == 1 else " & ".join(row) + r" \\")
    lines += ["\\end{longtable}", "}", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote {path}")


def write_md(path: Path, title: str, sections: list[str]) -> None:
    path.write_text(f"# {title}\n\n" + "\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"  wrote {path}")


def md_table(df: pd.DataFrame | None, digits: int = 3) -> str:
    if df is None or df.empty:
        return "_(no data)_"
    cell = lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) else (  # noqa: E731
        f"{v:.{digits}g}" if isinstance(v, float) and abs(v) < 1e-3 and v != 0 else
        (f"{v:.{digits}f}" if isinstance(v, float) else str(v)))
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)
