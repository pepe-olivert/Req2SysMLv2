"""A2. Richness of the generated models and its relation with the LJS.

Per category model: non-empty lines and number of requirement, part, attribute, constraint and satisfy elements
(definitions and usages, comments and doc text excluded). Aggregated per model, prompt (C0 minimal vs guided)
and document. The relation with the LJS is the Spearman correlation, over category models, between the
structural elements per requirement ((part + attribute + constraint + satisfy) / requirements of the category)
and the LJS of each judge, with and without doc comments. Normalising by the requirements of the category avoids
a spurious size effect (bigger categories get bigger models and are judged on more requirements).

    python -m evaluation.analysis.a02_richness
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from evaluation.analysis.common import (KEYS, fmt, load_ljs, load_models, md_table, model_sort, out_dir, tex,
                                        write_md, write_paper_table)

ELEMENTS = ["requirement", "part", "attribute", "constraint", "satisfy"]
_COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.DOTALL)
_STRING_RE = re.compile(r"\"(?:[^\"\\]|\\.)*\"")
_PATTERNS = {e: re.compile(rf"\b{e}\b") for e in ELEMENTS}

# (set, condition of the final model) -> label
FINAL = {("E1", "C4"): "E1 guided", ("E4", "C1"): "C0 minimal", ("R3", "C1"): "R3 guided (sol input)",
         ("E5", "C4"): "E5 guided", ("E5C0", "C1"): "C0 minimal"}
# (set label, judge, doc) -> judge directory
JUDGES = {
    ("E1", "gpt-4o-mini", "with doc"): "pipeline/ljs/gpt-4o-mini",
    ("E1", "gpt-4o-mini", "no doc"): "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
    ("E1", "claude-haiku-5.5", "with doc"): "second_judge/pipeline_c4/ljs/claude-haiku-5.5",
    ("E1", "claude-haiku-5.5", "no doc"): "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5",
    ("E4", "gpt-4o-mini", "with doc"): "c0_minimal_prompt/ljs/gpt-4o-mini",
    ("E4", "gpt-4o-mini", "no doc"): "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini",
    ("E4", "claude-haiku-5.5", "no doc"): "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5",
    ("R3", "gpt-4o-mini", "with doc"): "input_control_sol/ljs/gpt-4o-mini",
    ("E5", "gpt-4o-mini", "with doc"): "jwst_pipeline/ljs/gpt-4o-mini",
    ("E5", "gpt-4o-mini", "no doc"): "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
    ("E5", "claude-haiku-5.5", "no doc"): "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5",
}


def richness(code: str) -> dict:
    body = _STRING_RE.sub('""', _COMMENT_RE.sub("", code))
    out = {"lines": sum(1 for line in code.splitlines() if line.strip())}
    out.update({e: len(_PATTERNS[e].findall(body)) for e in ELEMENTS})
    return out


def main() -> None:
    out = out_dir("a02_richness")
    frames = []
    for (name, cond), label in FINAL.items():
        m = load_models(name)
        m = m[m.condition == cond].copy()
        m["setting"] = label
        frames.append(m)
    models = pd.concat(frames, ignore_index=True)
    r = pd.DataFrame([richness(c) for c in models.sysml_code])
    models = pd.concat([models.reset_index(drop=True), r], axis=1)
    models["n_requirements"] = models.requirements.map(len)
    models["structure_per_req"] = models[["part", "attribute", "constraint", "satisfy"]].sum(axis=1) / models.n_requirements
    models.drop(columns=["requirements", "sysml_code", "generated_code"]).to_csv(out / "richness_per_category.csv",
                                                                                 index=False)

    agg = (models.groupby(["document", "setting", "prompt", "llm"])[["lines", *ELEMENTS, "structure_per_req"]]
           .mean().round(2).reset_index())
    agg["n"] = models.groupby(["document", "setting", "prompt", "llm"]).size().values
    agg.to_csv(out / "richness_by_model.csv", index=False)

    rows = []
    for doc in ("EIRENE", "JWST"):
        for setting in ["E1 guided", "R3 guided (sol input)", "C0 minimal"] if doc == "EIRENE" else ["E5 guided", "C0 minimal"]:
            sub = agg[(agg.document == doc) & (agg.setting == setting)]
            for llm in model_sort(sub.llm):
                a = sub[sub.llm == llm].iloc[0]
                rows.append([doc, tex(setting), tex(llm), str(int(a.n)), fmt(a.lines, 1)]
                            + [fmt(a[e], 1) for e in ELEMENTS] + [fmt(a.structure_per_req, 2)])
    write_paper_table(
        out / "tab_richness.tex",
        "Richness of the final models (means per category model). Lines: non-empty lines. Element columns: "
        "definitions and usages of each kind (comments and doc text excluded). Struct./req: (part + attribute + "
        "constraint + satisfy) per requirement of the category. C0: minimal generation prompt.",
        "tab:richness", ["Document", "Setting", "Model", "n", "Lines", "Req.", "Part", "Attr.", "Constr.",
                         "Satisfy", "Struct./req"], "llrrrrrrrrr", rows, wide=True)

    # Correlation with the LJS per judge, with and without doc.
    corr_rows = []
    set_of = {"E1 guided": "E1", "C0 minimal": None, "R3 guided (sol input)": "R3", "E5 guided": "E5"}
    for (name, judge, doc), judge_dir in JUDGES.items():
        lj = load_ljs(judge_dir)
        if lj is None:
            continue
        cond = "C1" if name in ("E4", "R3") else "C4"
        m = models[(models.set == name)][KEYS + ["structure_per_req", "lines", "n_requirements"]]
        lj = lj[lj.condition == cond]
        d = m.merge(lj[KEYS + ["ljs"]], on=KEYS).dropna(subset=["ljs"])
        if len(d) < 10:
            continue
        rho, p = spearmanr(d.structure_per_req, d.ljs)
        within = [spearmanr(g.structure_per_req, g.ljs)[0] for _, g in d.groupby("llm") if g.structure_per_req.nunique() > 1]
        corr_rows.append({"set": name, "judge": judge, "doc": doc, "n": len(d), "rho_pooled": round(rho, 3),
                          "p_pooled": p, "rho_within_model_mean": round(float(np.mean(within)), 3) if within else np.nan,
                          **{f"rho_{llm}": round(spearmanr(g.structure_per_req, g.ljs)[0], 3)
                             for llm, g in d.groupby("llm") if g.structure_per_req.nunique() > 1}})
    corr = pd.DataFrame(corr_rows)
    corr.to_csv(out / "richness_ljs_correlation.csv", index=False)
    labels = {"E1": "E1 (EIRENE, guided)", "E4": "C0 (EIRENE, minimal)", "R3": "R3 (EIRENE, sol input)",
              "E5": "E5 (JWST, guided)"}
    crow = [[tex(labels[r.set]), tex(r.judge), r.doc, str(r.n), fmt(r.rho_pooled, 3),
             ("$<$0.001" if r.p_pooled < 0.001 else f"{r.p_pooled:.3f}"), fmt(r.rho_within_model_mean, 3)]
            for r in corr.itertuples()]
    write_paper_table(
        out / "tab_richness_ljs.tex",
        "Spearman correlation between structural elements per requirement and the LJS of each category model, per "
        "judge, with the doc comments and without them (no-doc control). Pooled: all models of the set; Within: "
        "mean of the per-model correlations.",
        "tab:richness_ljs", ["Set", "Judge", "Doc", "n", "$\\rho$ pooled", "$p$", "$\\rho$ within"], "lllrrrr", crow)

    write_md(out / "summary.md", "A2. Richness of the models", [md_table(agg), "## Correlation with the LJS", md_table(corr)])


if __name__ == "__main__":
    main()
