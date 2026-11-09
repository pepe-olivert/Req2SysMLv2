"""Cost ledger and key figures of the JSS-revision runs (R1-R6). Reads stored results only; no LLM calls.

Writes results/revision_summary/:
    costs.csv            real cost per run and component (sum of the cost returned by OpenRouter per call)
    key_figures.md       the figures of each run, as markdown tables
    *.csv                one CSV per key-figure table

Only records written by the revision (they carry `git_commit`) are counted as cost: the E3 bank copied
into results/ablation_stress_revision and the input copies keep the usage of its original v1 generation, which is not paid again.

    python -m evaluation.revision_summary
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from core.config import RESULTS_DIR
from evaluation import require_study_results
from evaluation.make_paper_artifacts import bootstrap_ci, holm, mcnemar_exact, model_order, wilcoxon_p

OUT = RESULTS_DIR / "revision_summary"
KEYS = ["pdf", "llm", "condition", "run", "category"]
IEEE = ["correctness", "completeness", "unambiguity", "verifiability", "traceability"]
STATUSES = ["satisfied", "partial", "missing", "not_applicable"]

# Run -> (phase directories with generations/repairs, judgment directories)
RUNS = {
    "R1 JWST end-to-end (E5)": (["jwst_pipeline"], ["jwst_pipeline/ljs/gpt-4o-mini"]),
    "R2+R8 C2+KB and FULLREV on the E3 bank": (["ablation_stress_revision"],
                                               ["ablation_stress_revision/ljs/gpt-4o-mini"]),
    "R3 input control (sol extraction)": (["input_control_sol"], ["input_control_sol/ljs/gpt-4o-mini"]),
    "R4 C0 minimal prompt (E4)": (["c0_minimal_prompt"], [
        "c0_minimal_prompt/ljs/gpt-4o-mini", "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini"]),
    "R5 no-doc control (gpt-4o-mini)": ([], ["nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
                                             "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini"]),
    "R6 second judge (claude-haiku-5.5)": ([], ["second_judge/pipeline_c4/ljs/claude-haiku-5.5",
                                                "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5",
                                                "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5",
                                                "second_judge/jwst_pipeline_c4/ljs/claude-haiku-5.5",
                                                "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"]),
    # R9: C0 on JWST gave only 8 invalid generations, so (authors' decision) the out-of-sample bank was built
    # like E3, with the v1 prompt, on JWST and gpt-6-luna only. The C0 generations are kept as data.
    "R9 out-of-sample error bank (JWST) + R8 on it": (["jwst_c0_bank", "jwst_v1_bank"],
                                                      ["jwst_v1_bank/ljs/gpt-4o-mini"]),
    "R11 repair with the Pilot Implementation as validator (C4P)": (
        ["pilot_repair"], ["pilot_repair/nodoc/ljs/gpt-4o-mini", "pilot_repair/nodoc/ljs/claude-haiku-5.5"]),
    "R9b out-of-sample bank (JWST, v1 prompt) with flash-lite, no C3": (
        ["jwst_v1_bank_flashlite"], ["jwst_v1_bank_flashlite/ljs/gpt-4o-mini"]),
}

# Router categories whose knowledge base was created or substantively rewritten after examining
# the EIRENE v1 errors (lines changed: CONSTRAINT_EXPR +142 new, DECLARATION_FORM +77/-4, LITERALS_STRINGS
# +29/-4, DOC_COMMENT +24/-20, QUALIFICATION +12/-2). The other KBs (ALT_NO_VIABLE, LEXER, UNKNOWN +7;
# DELIMITERS +11/-4) only gained the "return the complete file" instruction and placeholder fixes in their
# examples. Their earlier history is unknown.
EIRENE_TUNED_KBS = {"CONSTRAINT_EXPR", "DECLARATION_FORM", "LITERALS_STRINGS", "DOC_COMMENT", "QUALIFICATION"}


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def results_csv(phase_dir: Path) -> pd.DataFrame | None:
    for name in ("pipeline_results.csv", "ablation_results.csv"):
        if (phase_dir / name).exists():
            df = pd.read_csv(phase_dir / name)
            df["converged"] = df["converged"].astype(str).str.lower() == "true"
            df["repair_calls"] = df["llm_calls"] - 1
            df["repair_cost"] = df["cost_usd"] - df["generation_cost_usd"]
            return df
    return None


def ljs(judge_dir: Path) -> pd.DataFrame | None:
    path = judge_dir / "ljs_results.csv"
    return pd.read_csv(path) if path.exists() else None


# ---------------------------------------------------------------------------
# Costs
# ---------------------------------------------------------------------------
def costs() -> pd.DataFrame:
    rows = []
    for run, (phases, judges) in RUNS.items():
        for phase in phases:
            d = RESULTS_DIR / phase
            gens = [g for g in jsonl(d / "generations.jsonl") if "git_commit" in g]
            rows.append({"run": run, "component": f"{phase}: generation", "calls": sum(g["usage"]["llm_calls"] for g in gens),
                         "cost_usd": sum(g["usage"]["cost_usd"] for g in gens)})
            if (d / "pilot_repair_results.csv").exists():  # R11: repair calls only (no generation)
                pr = pd.read_csv(d / "pilot_repair_results.csv")
                rows.append({"run": run, "component": f"{phase}: repair", "calls": int(pr.llm_calls.sum()),
                             "cost_usd": float(pr.cost_usd.sum())})
                continue
            df = results_csv(d)
            if df is not None:
                rows.append({"run": run, "component": f"{phase}: repair", "calls": int(df.repair_calls.sum()),
                             "cost_usd": float(df.repair_cost.sum())})
        for judge in judges:
            js = jsonl(RESULTS_DIR / judge / "judgments.jsonl")
            if js:
                rows.append({"run": run, "component": f"{judge}", "calls": sum(j["usage"]["llm_calls"] for j in js),
                             "cost_usd": sum(j["usage"]["cost_usd"] for j in js)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Key figures
# ---------------------------------------------------------------------------
def mean_ci(values) -> str:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return "--"
    lo, hi = bootstrap_ci(v)
    return f"{v.mean():.3f} [{lo:.3f}, {hi:.3f}]"


def pipeline_figures(phase: str, judge_dir: str) -> pd.DataFrame | None:
    df = results_csv(RESULTS_DIR / phase)
    if df is None:
        return None
    lj = ljs(RESULTS_DIR / judge_dir)
    if lj is not None:
        df = df.merge(lj[KEYS + ["ljs"]], on=KEYS, how="left")
    else:
        df["ljs"] = np.nan
    rows = []
    for m in model_order(df.llm):
        row = {"model": m}
        for c in sorted(df.condition.unique()):
            sub = df[(df.llm == m) & (df.condition == c)]
            row[f"conv_{c}_%"] = round(sub.converged.mean() * 100, 1)
            row[f"invalid_{c}"] = int((sub.initial_errors > 0).sum())
            judged = sub.ljs.notna().sum()
            row[f"LJS_{c}"] = mean_ci(sub.ljs) if judged == len(sub) else f"-- ({judged}/{len(sub)} judged)"
        row["n"] = int((df.llm == m).sum() / df.condition.nunique())
        rows.append(row)
    return pd.DataFrame(rows)


def bank_figures(frames: list[pd.DataFrame], new_conditions=("C2KB", "FULLREV"),
                 conditions=("C2", "C2KB", "C3", "C4", "FULLREV")) -> pd.DataFrame | None:
    """Repair conditions on the invalid generations of a bank (paired by run and category), with tests of
    C2KB against C2 and C4 and of FULLREV against C2, C2KB and C4 (McNemar on rescue, Wilcoxon on the rest;
    Holm over each model's family of tests)."""
    frames = [f for f in frames if f is not None]
    if not frames:
        return None
    df = pd.concat(frames)
    df = df[(df.initial_errors > 0) & df.condition.isin(conditions)]
    rows = []
    for m in model_order(df.llm):
        sub = df[df.llm == m]
        wide = {metric: sub.pivot_table(index=["run", "category"], columns="condition", values=metric, aggfunc="first")
                for metric in ("converged", "iterations", "repair_calls", "repair_cost")}
        for c in conditions:
            if c not in wide["converged"]:
                continue
            rows.append({"model": m, "condition": c, "n_invalid": int(wide["converged"][c].notna().sum()),
                         "rescued_%": round(wide["converged"][c].astype(float).mean() * 100, 1),
                         "iterations": round(wide["iterations"][c].mean(), 2),
                         "repair_calls": round(wide["repair_calls"][c].mean(), 2),
                         "repair_cost_usd": round(wide["repair_cost"][c].mean(), 4)})
        tests, ps = [], []
        for new in new_conditions:
            # FULLREV is also compared with C2KB; Holm runs over the whole family of the model.
            for ref in ("C2", "C2KB", "C4") if new == "FULLREV" else ("C2", "C4"):
                if new not in wide["converged"] or ref not in wide["converged"]:
                    continue
                for metric in ("converged", "iterations", "repair_calls", "repair_cost"):
                    pair = wide[metric][[ref, new]].dropna()
                    p = (mcnemar_exact(pair[ref].astype(bool), pair[new].astype(bool)) if metric == "converged"
                         else wilcoxon_p(pair[ref], pair[new]))
                    tests.append(f"{ref}->{new} {metric}")
                    ps.append(p)
        for name, p, ph in zip(tests, ps, holm(ps)):
            rows.append({"model": m, "condition": f"test {name}", "p": p, "p_holm": ph})
    return pd.DataFrame(rows)


def tuned_split(errors_csv: Path, llm: str) -> dict | None:
    """Initial diagnostics in categories with an EIRENE-tuned KB vs the other categories."""
    if not errors_csv.exists():
        return None
    e = pd.read_csv(errors_csv)
    e = e[(e.iteration == 0) & (e.llm == llm)].drop_duplicates(["llm", "run", "category", "line", "column", "message"])
    tuned = int(e.error_category.isin(EIRENE_TUNED_KBS).sum())
    return {"n_diagnostics": len(e), "in_EIRENE_tuned_KBs": tuned, "in_other_KBs": len(e) - tuned,
            "tuned_%": round(tuned / len(e) * 100, 1) if len(e) else np.nan}


def category_profile(errors_csv: Path, llm: str) -> pd.Series | None:
    if not errors_csv.exists():
        return None
    e = pd.read_csv(errors_csv)
    e = e[(e.iteration == 0) & (e.llm == llm)].drop_duplicates(["llm", "run", "category", "line", "column", "message"])
    return (e.groupby("error_category").size() / len(e) * 100).round(1) if len(e) else None


def c0_figures() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    df = results_csv(RESULTS_DIR / "c0_minimal_prompt")
    if df is None:
        return None, None
    lj = ljs(RESULTS_DIR / "c0_minimal_prompt/ljs/gpt-4o-mini")
    e1 = results_csv(RESULTS_DIR / "pipeline")
    e1 = e1[e1.llm == "gpt-6-luna"]
    e1_ljs = ljs(RESULTS_DIR / "pipeline/ljs/gpt-4o-mini")
    rows = []
    for label, d, l in (("C0 (minimal prompt)", df, lj), ("E1 guided prompt", e1, e1_ljs)):
        if l is not None:
            d = d.merge(l[KEYS + ["ljs"]], on=KEYS, how="left")
        for c in ("C1", "C4"):
            sub = d[d.condition == c]
            rows.append({"setting": label, "condition": c, "n": len(sub),
                         "conv_%": round(sub.converged.mean() * 100, 1),
                         "invalid": int((sub.initial_errors > 0).sum()),
                         "initial_errors_mean": round(sub.initial_errors.mean(), 2),
                         "initial_errors_mean_invalid": round(sub[sub.initial_errors > 0].initial_errors.mean(), 2),
                         "LJS": mean_ci(sub.ljs) if "ljs" in sub and sub.ljs.notna().all() else "--"})
    profiles = {
        "C0 luna": category_profile(RESULTS_DIR / "c0_minimal_prompt/errors.csv", "gpt-6-luna"),
        "E1 luna": category_profile(RESULTS_DIR / "pipeline/errors.csv", "gpt-6-luna"),
        "E3 bank luna": category_profile(RESULTS_DIR / "ablation_stress/errors.csv", "gpt-6-luna"),
        "E3 bank flash-lite": category_profile(RESULTS_DIR / "ablation_stress/errors.csv", "gemini-3.5-flash-lite"),
    }
    prof = pd.DataFrame({k: v for k, v in profiles.items() if v is not None}).fillna(0.0)
    return pd.DataFrame(rows), prof


def judgment_table(judge_dir: Path, models_path: Path | None = None) -> pd.DataFrame | None:
    """One row per (row key, requirement): status and the five attributes of one judge."""
    lj = ljs(judge_dir)
    js = {j["judgment_key"]: j for j in jsonl(judge_dir / "judgments.jsonl")}
    if lj is None or not js:
        return None
    rows = []
    for r in lj.itertuples():
        for v in js[r.judgment_key]["per_requirement"]:
            rows.append({"llm": r.llm, "condition": r.condition, "run": r.run, "category": r.category,
                         "req_id": v["req_id"], "status": v["status"], **{a: v["ieee830"][a] for a in IEEE}})
    return pd.DataFrame(rows)


def cohen_kappa(a, b) -> float:
    a, b = np.asarray(a, dtype=object), np.asarray(b, dtype=object)
    labels = sorted(set(a) | set(b), key=str)
    po = float(np.mean(a == b))
    pe = sum(float(np.mean(a == lab)) * float(np.mean(b == lab)) for lab in labels)
    return np.nan if pe == 1 else (po - pe) / (1 - pe)


def nodoc_figures(original: str, nodoc: str, judge: str, conditions=("C4",)) -> pd.DataFrame | None:
    o, n = ljs(RESULTS_DIR / original), ljs(RESULTS_DIR / nodoc)
    if o is None or n is None:
        return None
    o = o[o.condition.isin(conditions)]
    cols = ["ljs"] + [f"ieee_{a}" for a in IEEE]
    m = o.merge(n[KEYS + cols], on=KEYS, suffixes=("_orig", "_nodoc"))
    rows = []
    for model in model_order(m.llm):
        sub = m[m.llm == model]
        row = {"judge": judge, "model": model, "n_pairs": len(sub)}
        for c in cols:
            row[f"{c}_orig"] = round(sub[f"{c}_orig"].mean(), 3)
            row[f"{c}_nodoc"] = round(sub[f"{c}_nodoc"].mean(), 3)
        row["p_ljs"] = wilcoxon_p(sub["ljs_orig"], sub["ljs_nodoc"])
        rows.append(row)
    return pd.DataFrame(rows)


def kappa_figures(dir_a: str, dir_b: str, label: str) -> pd.DataFrame | None:
    a, b = judgment_table(RESULTS_DIR / dir_a), judgment_table(RESULTS_DIR / dir_b)
    if a is None or b is None:
        return None
    key = ["llm", "condition", "run", "category", "req_id"]
    m = a.merge(b, on=key, suffixes=("_a", "_b"))
    rows = [{"set": label, "item": "status (4 classes)", "n": len(m),
             "agreement_%": round(float(np.mean(m.status_a == m.status_b)) * 100, 1),
             "kappa": round(cohen_kappa(m.status_a, m.status_b), 3)}]
    for attr in IEEE:
        sub = m.dropna(subset=[f"{attr}_a", f"{attr}_b"])
        rows.append({"set": label, "item": attr, "n": len(sub),
                     "agreement_%": round(float(np.mean(sub[f"{attr}_a"] == sub[f"{attr}_b"])) * 100, 1),
                     "kappa": round(cohen_kappa(sub[f"{attr}_a"].astype(bool), sub[f"{attr}_b"].astype(bool)), 3)})
    return pd.DataFrame(rows)


def ranking(dirs: dict[str, str], conditions=("C4",)) -> pd.DataFrame | None:
    out = []
    for judge, d in dirs.items():
        lj = ljs(RESULTS_DIR / d)
        if lj is None:
            return None
        lj = lj[lj.condition.isin(conditions)]
        for model in model_order(lj.llm):
            out.append({"judge": judge, "model": model, "n": int((lj.llm == model).sum()),
                        "LJS": mean_ci(lj[lj.llm == model].ljs), "mean": lj[lj.llm == model].ljs.mean()})
    df = pd.DataFrame(out)
    df["rank"] = df.groupby("judge")["mean"].rank(ascending=False).astype(int)
    return df.drop(columns="mean")


def c0_vs_e1_nodoc(judge: str) -> pd.DataFrame | None:
    """C0 (minimal prompt) vs the E1 guided prompt for gpt-6-luna, both without doc comments, one judge.

    Paired by (run, category): same requirements, different generated models. C0 C1 and C4 are the same code
    (no invalid generation), and E1 C4 is the code the no-doc control was built from.
    """
    c0 = ljs(RESULTS_DIR / f"nodoc_control/c0_minimal_prompt/ljs/{judge}")
    e1 = ljs(RESULTS_DIR / f"nodoc_control/pipeline_c4/ljs/{judge}")
    if c0 is None or e1 is None:
        return None
    cols = ["ljs", "ljs_strict", "ieee_completeness"]
    a = c0[c0.condition == "C1"][["run", "category"] + cols]
    b = e1[(e1.llm == "gpt-6-luna") & (e1.condition == "C4")][["run", "category"] + cols]
    m = a.merge(b, on=["run", "category"], suffixes=("_c0", "_e1"))
    rows = []
    for c in cols:
        pair = m[[f"{c}_c0", f"{c}_e1"]].dropna()
        rows.append({"judge": judge, "metric": c, "n_pairs": len(pair), "C0_no_doc": round(pair[f"{c}_c0"].mean(), 3),
                     "E1_luna_no_doc": round(pair[f"{c}_e1"].mean(), 3),
                     "diff": round((pair[f"{c}_c0"] - pair[f"{c}_e1"]).mean(), 3),
                     "p_wilcoxon": wilcoxon_p(pair[f"{c}_c0"], pair[f"{c}_e1"])})
    return pd.DataFrame(rows)


# (experiment, judge, models file, conditions or None, repaired only, judge directory)
JUDGED_SETS = [
    ("E1", "gpt-4o-mini", "pipeline/sysml_models.jsonl", None, False, "pipeline/ljs/gpt-4o-mini"),
    ("E1 no-doc", "gpt-4o-mini", "nodoc_control/pipeline_c4/sysml_models.jsonl", None, False,
     "nodoc_control/pipeline_c4/ljs/gpt-4o-mini"),
    ("E1 C4", "claude-haiku-5.5", "pipeline/sysml_models.jsonl", ["C4"], False,
     "second_judge/pipeline_c4/ljs/claude-haiku-5.5"),
    ("E1 no-doc", "claude-haiku-5.5", "nodoc_control/pipeline_c4/sysml_models.jsonl", None, False,
     "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5"),
    ("E5", "gpt-4o-mini", "jwst_pipeline/sysml_models.jsonl", None, False, "jwst_pipeline/ljs/gpt-4o-mini"),
    ("E5 no-doc", "gpt-4o-mini", "nodoc_control/jwst_pipeline_c4/sysml_models.jsonl", None, False,
     "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini"),
    ("E5 no-doc", "claude-haiku-5.5", "nodoc_control/jwst_pipeline_c4/sysml_models.jsonl", None, False,
     "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"),
    ("R4 C0", "gpt-4o-mini", "c0_minimal_prompt/sysml_models.jsonl", None, False, "c0_minimal_prompt/ljs/gpt-4o-mini"),
    ("R4 C0 no-doc", "gpt-4o-mini", "nodoc_control/c0_minimal_prompt/sysml_models.jsonl", None, False,
     "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini"),
    ("R4 C0 no-doc", "claude-haiku-5.5", "nodoc_control/c0_minimal_prompt/sysml_models.jsonl", None, False,
     "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5"),
    ("R9 (luna)", "gpt-4o-mini", "jwst_v1_bank/sysml_models.jsonl", None, False, "jwst_v1_bank/ljs/gpt-4o-mini"),
    ("R9b (flash-lite)", "gpt-4o-mini", "jwst_v1_bank_flashlite/sysml_models.jsonl", None, False,
     "jwst_v1_bank_flashlite/ljs/gpt-4o-mini"),
]


def stored_models(models_file: str, conditions) -> pd.DataFrame:
    from evaluator.__main__ import judgment_key

    rows = {}
    for r in jsonl(RESULTS_DIR / models_file):
        if conditions is None or r["condition"] in conditions:
            rows[tuple(str(r[k]) for k in KEYS)] = {**{k: r[k] for k in KEYS},
                                                   "judgment_key": judgment_key(r["requirements"], r["sysml_code"])}
    df = pd.DataFrame(list(rows.values()))
    df["run"] = df["run"].astype(int)
    return df


def missing_judgments() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Rows and distinct models left without a judgment, per experiment and judge (never filled)."""
    out, missing = [], {}
    for exp, judge, models_file, conditions, _, judge_dir in JUDGED_SETS:
        models = stored_models(models_file, conditions)
        done = {j["judgment_key"] for j in jsonl(RESULTS_DIR / judge_dir / "judgments.jsonl")}
        miss = models[~models.judgment_key.isin(done)]
        missing[(exp, judge)] = miss
        out.append({"experiment": exp, "judge": judge, "rows": len(models), "rows_missing": len(miss),
                    "models": models.judgment_key.nunique(), "models_missing": miss.judgment_key.nunique()})
    # haiku on E1: same (model, run, category) in the original and the no-doc version?
    a = missing[("E1 C4", "claude-haiku-5.5")]
    b = missing[("E1 no-doc", "claude-haiku-5.5")]
    ka = set(map(tuple, a[["llm", "run", "category"]].values))
    kb = set(map(tuple, b[["llm", "run", "category"]].values))
    overlap = pd.DataFrame([{"original_missing": len(ka), "no_doc_missing": len(kb), "in_both": len(ka & kb),
                             "union": len(ka | kb)}])
    both = pd.concat([a.assign(version="original"), b.assign(version="no-doc")])
    detail = both.groupby(["version", "llm", "category"]).size().rename("missing").reset_index()
    return pd.DataFrame(out), overlap, detail


def analysis_sections() -> list[str]:
    """Key figures of the phase-3 analyses (results/analysis/aNN_*), read from their CSV outputs."""
    a = RESULTS_DIR / "analysis"
    csv = lambda rel: pd.read_csv(a / rel) if (a / rel).exists() else None  # noqa: E731
    first_line = lambda rel: next((l for l in (a / rel).read_text(encoding="utf-8").splitlines()  # noqa: E731
                                   if l and not l.startswith("#")), "") if (a / rel).exists() else ""
    out = ["", "# Phase 3: analyses without LLM calls (results/analysis/)"]
    acc = csv("a01_tool_acceptance/acceptance.csv")
    if acc is not None:
        final = acc[((acc.condition == "C4") & acc.set.isin(["E1", "E5", "E3", "R9", "R9b"]))
                    | (acc.set.isin(["E4", "E5C0"]) & (acc.condition == "C1"))]
        out += ["## A1 Pilot Implementation acceptance (final models, %)", md(final)]
        sat = csv("a01_tool_acceptance/satisfy_resolution.csv")
        out += ["### satisfy relations that resolve (models without syntax errors)", md(sat)]
    acc_b = csv("a01b_boilerplate/acceptance.csv")
    if acc_b is not None:
        fb = acc_b[((acc_b.condition == "C4") & acc_b.set.isin(["E1", "E5", "E3", "R9", "R9b"]))
                   | (acc_b.set.isin(["E4", "E5C0"]) & (acc_b.condition == "C1"))]
        piv = fb.pivot_table(index=["set", "llm"], columns=["release", "variant"], values="accepted").round(1)
        piv.columns = [f"{r} {v}" for r, v in piv.columns]
        out += ["## A1b Acceptance with the deterministic fixes ((a) imports, (b) connector ends A::p -> A.p)",
                md(piv.reset_index())]
        types = csv("a01b_boilerplate/remaining_error_types.csv")
        if types is not None:
            out += ["### A1b Remaining error types with (a)+(b), 2024-04.1 (ANTLR-valid models)",
                    md(types[types.release == "2024-04.1"].head(12)[["type", "statements", "models", "issues",
                                                                    "example_code"]])]
        ex = csv("a01b_boilerplate/prompt_kb_examples.csv")
        if ex is not None:
            out += ["### A1b Code examples of the frozen prompt and KBs (intended valid), by status",
                    md(ex[ex.intended == "valid"].groupby(["release", "source", "status"]).size()
                       .rename("examples").reset_index())]
    r11 = csv("r11_pilot_repair/summary_by_model.csv")
    if r11 is not None:
        out += ["## R11 Repair with the Pilot as validator (C4P)", md(r11),
                "### R11 Elements before/after (sums)", md(csv("r11_pilot_repair/elements.csv")),
                "### R11 LJS without doc, before/after", md(csv("r11_pilot_repair/ljs_before_after.csv")),
                "### R11 Errors with 2026-08 after the loop and (b)",
                md(csv("r11_pilot_repair/remaining_2026_after_b.csv"))]
    for title, rel in (("## A14 ANTLR error types of the answers the R11 guard rejected", "a14_guard_rejections/antlr_error_types.csv"),
                       ("### A14 Stagnation in R11 (old: diagnostics unchanged; new: diagnostics and model unchanged)",
                        "a14_guard_rejections/stagnation_frequency.csv"),
                       ("## A15 Acceptance after R11 with the extended rewriting A::x -> A.x", "a15_extended_b/acceptance.csv"),
                       ("### A15 Remaining errors with 2026-08 and the extended rewriting", "a15_extended_b/remaining_2026_b_extended.csv")):
        df = csv(rel)
        if df is not None:
            out += [title, md(df.groupby("llm").head(6) if "llm" in df and "remaining" in rel else df)]
    for title, rel in (("## A2 Richness per model (means per category)", "a02_richness/richness_by_model.csv"),
                       ("### A2 Spearman: structure per requirement vs LJS", "a02_richness/richness_ljs_correlation.csv"),
                       ("## A3 Lines changed by the repair", "a03_repair_diff/repair_diff_summary.csv"),
                       ("## A5 Not applicable, by judge", "a05_not_applicable/not_applicable_by_judge.csv"),
                       ("## A6 Extraction output vs limits", "a06_extraction_truncation/truncation_summary.csv"),
                       ("## A7 Answers to CONSTRAINT_EXPR diagnostics (% of calls)",
                        "a07_c3_vs_c2/constraint_expr_answers.csv"),
                       ("## A8 Single-line blocks by router category", "a08_block_localisation/block_localisation_by_category.csv"),
                       ("## A10 E1 vs E2 (gpt-6-luna)", "a10_e1_e2_variability/e1_e2_diagnostics.csv"),
                       ("### A10 tests", "a10_e1_e2_variability/e1_e2_tests.csv"),
                       ("## A11 Unified ablation", "a11_ablation_unified/ablation_unified.csv"),
                       ("## A13 Judged n per set", "a13_missing_judgments/judged_n.csv")):
        df = csv(rel)
        if df is not None:
            out += [title, md(df)]
    pairs = csv("a04_cluster_stats/pairwise_tests.csv")
    if pairs is not None:
        ch = pairs[pairs.conclusion_changes][["document", "metric", "a", "b", "diff", "p_block_holm",
                                               "p_cluster_holm", "p_mixed_holm"]]
        out += ["## A4 Pairs whose conclusion changes with cluster bootstrap or mixed model", md(ch)]
    out += ["## A6 " + first_line("a06_extraction_truncation/summary.md"),
            "## A8 " + first_line("a08_block_localisation/summary.md"),
            "## A9 " + " ".join(l for l in (a / "a09_input_duplicates/summary.md").read_text(encoding="utf-8")
                                .splitlines() if l.startswith("Entries"))
            if (a / "a09_input_duplicates/summary.md").exists() else "",
            "## A12 Examples: results/analysis/a12_paper_examples/ (fig_repair_example.tex, fig_richness_example.tex)",
            "## A13 Sentence for the paper", (a / "a13_missing_judgments/paper_sentence.txt").read_text(encoding="utf-8")
            if (a / "a13_missing_judgments/paper_sentence.txt").exists() else ""]
    return out


def md(df: pd.DataFrame | None) -> str:
    """Markdown table (no tabulate dependency); missing values are left empty."""
    if df is None or df.empty:
        return "_(not available yet)_"
    cell = lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) else (  # noqa: E731
        f"{v:.4g}" if isinstance(v, float) else str(v))
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def main() -> None:
    require_study_results()
    OUT.mkdir(parents=True, exist_ok=True)
    sections = []
    c = costs()
    c.to_csv(OUT / "costs.csv", index=False)
    per_run = c.groupby("run", sort=False)[["calls", "cost_usd"]].sum().reset_index()
    per_run["cumulative_usd"] = per_run.cost_usd.cumsum()
    sections += ["## Real cost per run (USD, cost returned by OpenRouter)", md(per_run), "", md(c)]

    tables = {
        "jwst_pipeline": ("## R1 JWST end-to-end (E5): convergence and LJS (gpt-4o-mini, mean [95% bootstrap CI])",
                          pipeline_figures("jwst_pipeline", "jwst_pipeline/ljs/gpt-4o-mini")),
        "e1_reference": ("### E1 (EIRENE) for reference", pipeline_figures("pipeline", "pipeline/ljs/gpt-4o-mini")),
        "bank_e3": ("## R2/R8 C2+KB and FULLREV on the E3 bank (invalid generations; C2/C3/C4 from "
                    "results/ablation_stress)", bank_figures([
                        (lambda d: d[d.condition.isin(["C2", "C3", "C4"])] if d is not None else None)(
                            results_csv(RESULTS_DIR / "ablation_stress")),
                        results_csv(RESULTS_DIR / "ablation_stress_revision")])),
        "bank_jwst": ("## R9 out-of-sample bank (JWST, v1 prompt, gpt-6-luna): repair conditions on the invalid "
                      "generations", bank_figures([results_csv(RESULTS_DIR / "jwst_v1_bank"),
                                                   results_csv(RESULTS_DIR / "jwst_v1_bank_flashlite")])),
        "input_control": ("## R3 input control (gpt-6.1-sol extraction, C1, 1 run)",
                          pipeline_figures("input_control_sol", "input_control_sol/ljs/gpt-4o-mini")),
    }
    c0, profile = c0_figures()
    tables["c0"] = ("## R4 C0 minimal prompt (gpt-6-luna) vs E1 guided prompt", c0)
    jwst_profile = {
        "R9 JWST v1 luna": category_profile(RESULTS_DIR / "jwst_v1_bank/errors.csv", "gpt-6-luna"),
        "R9b JWST v1 flash-lite": category_profile(RESULTS_DIR / "jwst_v1_bank_flashlite/errors.csv",
                                                   "gemini-3.5-flash-lite"),
        "JWST C0 luna": category_profile(RESULTS_DIR / "jwst_c0_bank/errors.csv", "gpt-6-luna"),
        "E3 bank luna": category_profile(RESULTS_DIR / "ablation_stress/errors.csv", "gpt-6-luna"),
        "E3 bank flash-lite": category_profile(RESULTS_DIR / "ablation_stress/errors.csv", "gemini-3.5-flash-lite"),
        "R4 EIRENE C0 luna": category_profile(RESULTS_DIR / "c0_minimal_prompt/errors.csv", "gpt-6-luna"),
    }
    jp = pd.DataFrame({k: v for k, v in jwst_profile.items() if v is not None}).fillna(0.0)
    tables["bank_jwst_profile"] = ("### R9 initial diagnostics per router category (%), vs the E3 bank",
                                   jp.reset_index().rename(columns={"index": "category"}) if not jp.empty else None)
    split = {k: tuned_split(RESULTS_DIR / d, llm) for k, (d, llm) in {
        "R9 JWST v1 luna": ("jwst_v1_bank/errors.csv", "gpt-6-luna"),
        "R9b JWST v1 flash-lite": ("jwst_v1_bank_flashlite/errors.csv", "gemini-3.5-flash-lite"),
        "JWST C0 luna": ("jwst_c0_bank/errors.csv", "gpt-6-luna"),
        "E3 bank luna": ("ablation_stress/errors.csv", "gpt-6-luna"),
        "E3 bank flash-lite": ("ablation_stress/errors.csv", "gemini-3.5-flash-lite"),
        "R4 EIRENE C0 luna": ("c0_minimal_prompt/errors.csv", "gpt-6-luna")}.items()}
    split_df = pd.DataFrame([{"set": k, **v} for k, v in split.items() if v is not None])
    tables["kb_tuned_split"] = (
        "### Diagnostics in categories whose KB was written/rewritten after examining EIRENE "
        f"({', '.join(sorted(EIRENE_TUNED_KBS))}) vs the others", split_df if not split_df.empty else None)
    tables["c0_profile"] = ("### Initial diagnostics per router category (% of each set's diagnostics)",
                            profile.reset_index().rename(columns={"index": "category"}) if profile is not None else None)
    tables["nodoc_e1_4omini"] = ("## R5 no-doc control: E1 C4, gpt-4o-mini",
                                 nodoc_figures("pipeline/ljs/gpt-4o-mini", "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
                                               "gpt-4o-mini"))
    tables["nodoc_e5_4omini"] = ("### E5 (JWST) C4, gpt-4o-mini",
                                 nodoc_figures("jwst_pipeline/ljs/gpt-4o-mini",
                                               "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini", "gpt-4o-mini"))
    tables["nodoc_e1_haiku"] = ("### E1 C4, claude-haiku-5.5",
                                nodoc_figures("second_judge/pipeline_c4/ljs/claude-haiku-5.5",
                                              "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5", "claude-haiku-5.5"))
    tables["nodoc_c0_4omini"] = ("### C0 (gpt-6-luna), gpt-4o-mini, C1 and C4",
                                 pd.concat([x for x in (
                                     nodoc_figures("c0_minimal_prompt/ljs/gpt-4o-mini",
                                                   "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini", f"gpt-4o-mini {c}",
                                                   (c,)) for c in ("C1", "C4")) if x is not None] or [pd.DataFrame()]))
    tables["kappa"] = ("## R6 agreement gpt-4o-mini vs claude-haiku-5.5 (per requirement; rows judged by both)",
                       pd.concat([x for x in (
                           kappa_figures("pipeline/ljs/gpt-4o-mini", "second_judge/pipeline_c4/ljs/claude-haiku-5.5",
                                         "E1 C4 original"),
                           kappa_figures("nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
                                         "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5", "E1 C4 no-doc"),
                           kappa_figures("nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
                                         "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5", "E5 C4 no-doc"))
                           if x is not None] or [pd.DataFrame()]))
    tables["ranking"] = ("### Model ranking by LJS (E1 C4)", ranking({
        "gpt-4o-mini": "pipeline/ljs/gpt-4o-mini", "claude-haiku-5.5": "second_judge/pipeline_c4/ljs/claude-haiku-5.5",
        "gpt-4o-mini no-doc": "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
        "claude-haiku-5.5 no-doc": "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5"}))
    tables["ranking_e5"] = ("### Model ranking by LJS (E5 JWST C4)", ranking({
        "gpt-4o-mini": "jwst_pipeline/ljs/gpt-4o-mini",
        "gpt-4o-mini no-doc": "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
        "claude-haiku-5.5 no-doc": "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"}))
    tables["c0_vs_e1_nodoc_haiku"] = ("### C0 vs E1 (gpt-6-luna), both without doc, claude-haiku-5.5 "
                                      "(paired by run and category; Wilcoxon)", c0_vs_e1_nodoc("claude-haiku-5.5"))
    tables["c0_vs_e1_nodoc_4omini"] = ("### Same comparison with gpt-4o-mini", c0_vs_e1_nodoc("gpt-4o-mini"))
    missing, overlap, detail = missing_judgments()
    tables["missing_judgments"] = ("## Judgments missing per experiment and judge (failed the strict parse after 3 "
                                   "attempts; left out, never filled)", missing)
    tables["missing_haiku_e1_overlap"] = ("### claude-haiku-5.5 on E1: same (model, run, category) missing in the "
                                          "original and the no-doc version?", overlap)
    tables["missing_haiku_e1_detail"] = ("### claude-haiku-5.5 on E1: missing rows per model and category", detail)
    for name, (title, df) in tables.items():
        if df is not None and not df.empty:
            df.to_csv(OUT / f"{name}.csv", index=False)
        sections += ["", title, md(df)]

    leaks = []
    for d in sorted((RESULTS_DIR / "nodoc_control").glob("*/requirement_text_leaks.csv")):
        lk = pd.read_csv(d)
        g = lk.groupby("llm")[["n_requirement_names", "n_names_with_text", "n_strings", "n_strings_with_text"]].sum()
        g.insert(0, "set", d.parent.name)
        leaks.append(g.reset_index())
        ex = pd.read_csv(d.parent / "exclusions.csv")
        sections += ["", f"- {d.parent.name}: {len(ex)} models excluded after stripping"
                     + (f" ({ex.reason.value_counts().to_dict()})" if len(ex) else "")]
    if leaks:
        leak_df = pd.concat(leaks)
        leak_df.to_csv(OUT / "requirement_text_leaks.csv", index=False)
        sections += ["", "### Requirement names / string literals with >= 5 consecutive words of the requirement",
                     md(leak_df)]
    sections += analysis_sections()
    (OUT / "key_figures.md").write_text("# JSS revision: key figures\n\n" + "\n".join(sections) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}/key_figures.md")
    print(per_run.to_string(index=False))


if __name__ == "__main__":
    main()
