"""Tables of the revised paper (phase 4), in their final format, from stored results only (no LLM calls).

Writes results/paper_tables/*.tex, ready for \\input in paper/main.tex:
    tab_models.tex            candidate LLMs and judges (OpenRouter ids, prices of the registry)
    tab_experiments.tex       every experiment: purpose, models, conditions, n, cost, dates
    tab_validity.tex          RQ1: parseability, Pilot acceptance (2024-04.1 / 2026-08), satisfy resolution, richness
    tab_semantics.tex         RQ2: LJS without doc (two judges), LJS with doc (control), completeness
    tab_ranking.tex           RQ2: robustness of the model ranking (document, input, judge, doc, statistical model)
    tab_c4p.tex               RQ3: the reference stage (C4P): effort, guard, diff and elements before/after
    tab_cost.tex              RQ4: cost per specification and per stage, both documents
    tab_repair_semantics.tex  appendix: paired LJS before/after repair, every stage and bank
Every number comes from results/ (the CSV/JSONL of the runs and of results/analysis/).

    python -m evaluation.make_paper_tables
"""

from __future__ import annotations

import itertools
import json
import subprocess

import numpy as np
import pandas as pd

from core.config import REPO_ROOT, RESULTS_DIR
from core.models import SUPPORTED_MODELS
from evaluation.analysis.common import (KEYS, MODEL_ORDER, fmt, fmt_p, jsonl, load_ljs, load_results,
                                        model_sort, tex, write_paper_table)
from evaluation.make_paper_artifacts import holm, rank_biserial, wilcoxon_p

OUT = RESULTS_DIR / "paper_tables"
A = RESULTS_DIR / "analysis"
SHORT = {"gpt-6.1-sol": "sol", "gpt-6-luna": "luna", "gemini-3.7-flash": "flash", "gemini-3.5-flash-lite": "flash-lite"}
N_CAT = {"EIRENE": 77, "JWST": 86}


def csv(rel: str) -> pd.DataFrame:
    return pd.read_csv(A / rel)


def m(llm: str) -> str:
    return f"\\llm{{{llm}}}"


def pct(x) -> str:
    return fmt(x, 1)


# ---------------------------------------------------------------------------
def tab_models() -> None:
    tok = csv("a19_tokens/tokens_by_model.csv").set_index("llm")
    rows = []
    for alias in ("gpt-6.1-sol", "gpt-6-luna", "gemini-3.7-flash", "gemini-3.5-flash-lite", "gpt-4o-mini",
                  "claude-haiku-5.5"):
        s = SUPPORTED_MODELS[alias]
        role = "candidate" if s.role == "candidate" else ("judge (default)" if alias == "gpt-4o-mini" else "judge (second)")
        t = tok.loc[alias]
        rows.append([m(alias), f"\\texttt{{{tex(s.openrouter_id)}}}", role,
                     f"{s.input_usd_per_m:.2f} / {s.output_usd_per_m:.2f}",
                     f"{t.input_tokens / 1e6:.2f} / {t.output_tokens / 1e6:.2f}", fmt(t.cost_usd, 2)])
    sol = tok.loc["gpt-6.1-sol"].cost_ratio
    others = (tok.drop(index="gpt-6.1-sol").cost_ratio - 1).abs().max() * 100
    write_paper_table(
        OUT / "tab_models.tex",
        "LLMs (accessed through OpenRouter). Price: USD per million input/output tokens at the time of the "
        "experiments. Tokens: millions of input/output tokens (output includes reasoning) of every stored call of "
        "the study, extraction and judgements included; Cost: USD returned by the provider for those calls. Priced "
        "at the listed rates, the tokens reproduce the returned cost to within "
        f"{others:.1f}\\% for every model except \\llm{{gpt-6.1-sol}}, whose returned cost is {(1 - sol) * 100:.0f}\\% lower (cached input tokens were not "
        "recorded). Per-experiment tokens: Supplementary Material, Section~S8. Reasoning effort: medium for every model except "
        "\\llm{gpt-4o-mini}, which has none. \\llm{claude-haiku-5.5} is pinned to Anthropic's endpoint. Identifiers "
        "name a model, not a dated snapshot.",
        "tab:models", ["Model", "OpenRouter id", "Role", "Price in/out", "Tokens in/out (M)", "Cost"],
        "lllrrr", rows)


def _dates(phase: str) -> str:
    stamps = []
    for path in [RESULTS_DIR / phase / "run_manifest.jsonl", *(RESULTS_DIR / phase).rglob("ljs/*/run_manifest.jsonl")]:
        stamps += [r["timestamp_utc"][:10] for r in jsonl(path)]
    if not stamps:  # runs before the provenance fields: date of the commit that wrote the current results CSV
        for name in ("pipeline_results.csv", "ablation_results.csv"):
            if (RESULTS_DIR / phase / name).exists():
                out = subprocess.run(["git", "log", "--format=%ad", "--date=short", "--",
                                      f"results/{phase}/{name}"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.split()
                # the last commit that changed the rows (later commits only added columns or nothing)
                stamps = out[:1]
    if not stamps:
        return ""
    lo, hi = min(stamps), max(stamps)
    return lo if lo == hi else f"{lo}--{hi[5:]}"


def _cost(phase: str, results: str | None) -> tuple[float, float]:
    """(generation + repair cost of the new calls, judge cost) of a phase directory."""
    gen = sum(g["usage"]["cost_usd"] for g in jsonl(RESULTS_DIR / phase / "generations.jsonl")
              if phase not in ("ablation_stress", "ablation_stress_revision", "jwst_v1_bank", "jwst_v1_bank_flashlite")
              or "git_commit" in g)
    rep = 0.0
    if results and (RESULTS_DIR / phase / results).exists():
        df = pd.read_csv(RESULTS_DIR / phase / results)
        rep = float((df.cost_usd - df.get("generation_cost_usd", 0)).sum()) if "generation_cost_usd" in df else \
            float(df.cost_usd.sum())
    judge = sum(j["usage"]["cost_usd"] for p in (RESULTS_DIR / phase).rglob("ljs/*/judgments.jsonl") for j in jsonl(p))
    return gen + rep, judge


def tab_experiments() -> None:
    exps = [
        ("E1", "RQ1, RQ2, RQ4", "all four", "C1, C4", "pipeline", "pipeline_results.csv",
         "1{,}848 (231/model)", "EIRENE"),
        ("E2", "RQ3, few errors", m("gpt-6-luna"), "C1--C4", "ablation", "ablation_results.csv", "924", "EIRENE"),
        ("E3", "RQ3, frequent errors", "luna, flash-lite", "C1--C4, C2KB, FULLREV",
         "ablation_stress", "ablation_results.csv", "106 invalid of 462", "EIRENE (bank)"),
        ("E4", "RQ1, RQ2 (C0)", m("gpt-6-luna"), "C0 (C1, C4)", "c0_minimal_prompt", "pipeline_results.csv",
         "231 + 258", "EIRENE, JWST"),
        ("E5", "RQ1, RQ2, RQ4", "all four", "C1, C4", "jwst_pipeline", "pipeline_results.csv",
         "2{,}064 (258/model)", "JWST"),
        ("E6", "RQ3, out of sample", "luna, flash-lite", "C2, C2KB, C3$^a$, C4, FULLREV", "jwst_v1_bank",
         "pipeline_results.csv", "86 invalid of 516", "JWST (bank)"),
        ("E7", "RQ1--RQ4, reference stage", "luna, flash-lite", "C4P", "pilot_repair", "pilot_repair_results.csv",
         "627 repaired of 978", "EIRENE, JWST"),
        ("R3", "input control", "all four", "C1", "input_control_sol", "pipeline_results.csv", "608 (152/model)",
         "EIRENE (sol input)"),
    ]
    rows = []
    for exp, purpose, models, conds, phase, res, n, doc in exps:
        c, j = _cost(phase, res)
        extra = {"E3": ("ablation_stress_revision", "ablation_results.csv"),  # C2KB and FULLREV, same bank, later
                 "E4": ("jwst_c0_bank", "pipeline_results.csv"),              # C0 on JWST (C1 only)
                 "E6": ("jwst_v1_bank_flashlite", "pipeline_results.csv")}
        dates = _dates(phase)
        if exp in extra:
            c2, j2 = _cost(*extra[exp])
            c, j = c + c2, j + j2
            d2 = _dates(extra[exp][0])
            dates = dates if d2 == dates else f"{dates}, {d2}"
        rows.append([exp, purpose, doc, models, conds, n, fmt(c, 2), fmt(j, 2), dates])
    write_paper_table(
        OUT / "tab_experiments.tex",
        "Experiments. Every experiment uses three runs of every category, and all of them follow a paired design "
        "(each generation is shared by every condition). Banks: stored generations of an earlier generation prompt "
        "with real errors (E3: EIRENE, E6: JWST). Cost: LLM calls of generation and repair (USD); Judge: LJS "
        "judgments of the experiment. $^a$ C3 with \\llm{gpt-6-luna} only. The extraction of the inputs is "
        "reported in \\ref{app:extraction}.",
        "tab:experiments", ["Exp.", "Purpose", "Document", "Models", "Conditions", "n", "Cost", "Judge", "Dates"],
        "llllllrrl", rows, wide=True)


# ---------------------------------------------------------------------------
def tab_validity() -> None:
    blocks = [("EIRENE (E1)", "E1", "C4", "EIRENE"), ("JWST (E5)", "E5", "C4", "JWST"),
              ("C0, EIRENE (E4)", "E4", "C1", "EIRENE"), ("C0, JWST", "E5C0", "C1", "JWST")]
    a1b = csv("a01b_boilerplate/acceptance.csv")
    sat = csv("a01_tool_acceptance/satisfy_resolution.csv")
    r11 = csv("r11_pilot_repair/summary_by_model.csv")
    a15 = csv("a15_extended_b/acceptance.csv")
    rich = csv("a02_richness/richness_by_model.csv")
    rows = []
    for label, s, cond, doc in blocks:
        res = load_results(s)
        if rows:
            rows.append(["\\midrule"])
        rows.append([f"\\multicolumn{{11}}{{l}}{{\\textit{{{label}}}}} \\\\"])
        for llm in model_sort(res.llm):
            r = res[res.llm == llm]
            c1 = r[r.condition == "C1"].converged.mean() * 100
            c4 = r[r.condition == "C4"].converged.mean() * 100 if (r.condition == "C4").any() else np.nan
            ab = a1b[(a1b.set == s) & (a1b.llm == llm) & (a1b.condition == cond) & (a1b.release == "2024-04.1")]
            stored = ab[ab.variant == "as_stored"].accepted.iloc[0]
            imports = ab[ab.variant == "a"].accepted.iloc[0]
            rr = r11[(r11.document == doc) & (r11.llm == llm)] if s in ("E1", "E5") else r11.iloc[0:0]
            c4p = rr.accepted_2024_after.iloc[0] if len(rr) else np.nan
            aa = a15[(a15.document == doc) & (a15.llm == llm)] if s in ("E1", "E5") else a15.iloc[0:0]
            orig = aa["2026-08_b_original"].iloc[0] if len(aa) else np.nan
            ext = aa["2026-08_b_extended"].iloc[0] if len(aa) else np.nan
            ss = sat[(sat.set == s) & (sat.llm == llm) & (sat.condition == cond) & (sat.release == "2024-04.1")]
            sres = ss.resolved_pct.iloc[0] if len(ss) else np.nan
            setting = {"E1": "E1 guided", "E5": "E5 guided", "E4": "C0 minimal", "E5C0": "C0 minimal"}[s]
            rc = rich[(rich.setting == setting) & (rich.llm == llm) & (rich.document == doc)]
            rows.append([m(llm), pct(c1), pct(c4), pct(stored), pct(imports), pct(c4p), pct(orig), pct(ext), pct(sres),
                         fmt(rc.structure_per_req.iloc[0], 2) if len(rc) else "", fmt(rc.lines.iloc[0], 0) if len(rc) else ""])
    write_paper_table(
        OUT / "tab_validity.tex",
        "Validity and richness of the models (RQ1). Parseable: \\% of category models valid for the grammar "
        "(ANTLR) before repair (C1) and after the grammar stage (C4). Pilot 2024-04.1: \\% accepted by the reference "
        "implementation with name resolution and validation, for the final models as stored, after the deterministic "
        "import normalisation, and after the reference stage (C4P, run for \\llm{gpt-6-luna} and "
        "\\llm{gemini-3.5-flash-lite}). 2026-08: acceptance by the later release after C4P and rewriting (b) of the "
        "connector ends \\texttt{A::p} as \\texttt{A.p}; ext.: after the extended rewriting of every reference "
        "\\texttt{A::x} to a feature of a usage, designed after inspecting the 2026-08 results (post hoc). Satisfy: \\% of \\texttt{satisfy} "
        "relations whose references resolve (2024-04.1, models without syntax errors; the C0 models contain none). "
        "Struct./req: part, attribute, constraint and satisfy elements per requirement; Lines: non-empty lines per "
        "category model. C0: minimal generation prompt (C1 and C4 coincide on EIRENE; C4 was not run on JWST).",
        "tab:validity", ["Model", "Parse C1", "Parse C4", "As stored", "+imports", "+C4P", "+b", "+b ext.",
                         "Satisfy", "Struct./req", "Lines"],
        "lrrrrrrrrrr", rows, wide=True,
        header=["& \\multicolumn{2}{c}{Parseable \\%} & \\multicolumn{3}{c}{Pilot 2024-04.1 \\%} & \\multicolumn{2}{c}{2026-08 \\%} & "
                "\\multicolumn{3}{c}{} \\\\ \\cmidrule(lr){2-3}\\cmidrule(lr){4-6}\\cmidrule(lr){7-8}"])


# ---------------------------------------------------------------------------
def _ljs(judge_dir: str, cond: str) -> pd.DataFrame | None:
    lj = load_ljs(judge_dir)
    return lj[lj.condition == cond] if lj is not None else None


def tab_semantics() -> None:
    means = csv("a04_cluster_stats/model_means_cluster_ci.csv")
    sets = [("EIRENE (E1)", "EIRENE", "C4", {"nd4": "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
                                             "ndh": "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5",
                                             "d4": "pipeline/ljs/gpt-4o-mini",
                                             "dh": "second_judge/pipeline_c4/ljs/claude-haiku-5.5"}),
            ("JWST (E5)", "JWST", "C4", {"nd4": "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
                                         "ndh": "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5",
                                         "d4": "jwst_pipeline/ljs/gpt-4o-mini", "dh": None}),
            ("C0, EIRENE (E4)", "C0", "C1", {"nd4": "nodoc_control/c0_minimal_prompt/ljs/gpt-4o-mini",
                                             "ndh": "nodoc_control/c0_minimal_prompt/ljs/claude-haiku-5.5",
                                             "d4": "c0_minimal_prompt/ljs/gpt-4o-mini", "dh": None})]
    metric = {"nd4": "LJS gpt-4o-mini no-doc", "ndh": "LJS haiku-5.5 no-doc", "d4": "LJS gpt-4o-mini",
              "dh": "LJS haiku-5.5"}
    rows = []
    for label, doc, cond, dirs in sets:
        if rows:
            rows.append(["\\midrule"])
        rows.append([f"\\multicolumn{{7}}{{l}}{{\\textit{{{label}}}}} \\\\"])
        frames = {k: _ljs(v, cond) if v else None for k, v in dirs.items()}
        models = model_sort(frames["nd4"].llm)
        for llm in models:
            cells = []
            for k in ("nd4", "ndh", "d4", "dh"):
                f = frames[k]
                if f is None or not (f.llm == llm).any():
                    cells.append("")
                    continue
                mm = means[(means.document == doc) & (means.metric == metric[k]) & (means.llm == llm)]
                v = f[f.llm == llm].ljs.mean()
                cells.append(f"{fmt(v, 3)} [{fmt(mm.ci_low.iloc[0], 3)}, {fmt(mm.ci_high.iloc[0], 3)}]" if len(mm)
                             else fmt(v, 3))
            comp = [fmt(frames[k][frames[k].llm == llm].ieee_completeness.mean() * 100, 1)
                    if frames[k] is not None and (frames[k].llm == llm).any() else "" for k in ("nd4", "ndh")]
            rows.append([m(llm)] + cells + comp)
    write_paper_table(
        OUT / "tab_semantics.tex",
        "Semantic adequacy (RQ2): LLM-as-a-Judge Score of the final models without the doc comments that copy the "
        "requirement text (main measure), with two judges, and with the comments as a control; mean with 95\\% "
        "cluster-bootstrap confidence interval (categories resampled). Completeness: \\% of applicable requirements with the ISO/IEC/IEEE "
        "29148 completeness attribute met, without doc. \\llm{claude-haiku-5.5} judged 914/924 and 919/924 E1 "
        "models, 1{,}026/1{,}032 E5 models and 460/462 C0 rows (Section~\\ref{subsec:metrics}).",
        "tab:semantics", ["Model", "4o-mini", "haiku-5.5", "4o-mini", "haiku-5.5", "4o-mini", "haiku-5.5"],
        "lrrrrrr", rows, wide=True,
        header=["& \\multicolumn{2}{c}{LJS, no doc} & \\multicolumn{2}{c}{LJS, with doc} & "
                "\\multicolumn{2}{c}{Completeness \\%, no doc} \\\\ \\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}"])


def tab_ranking() -> None:
    settings = [("E1", "EIRENE", "LJS gpt-4o-mini", "pipeline/ljs/gpt-4o-mini", "C4"),
                ("E1 no doc", "EIRENE", "LJS gpt-4o-mini no-doc", "nodoc_control/pipeline_c4/ljs/gpt-4o-mini", "C4"),
                ("E1 haiku", "EIRENE", "LJS haiku-5.5", "second_judge/pipeline_c4/ljs/claude-haiku-5.5", "C4"),
                ("E1 haiku no doc", "EIRENE", "LJS haiku-5.5 no-doc",
                 "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5", "C4"),
                ("E5", "JWST", "LJS gpt-4o-mini", "jwst_pipeline/ljs/gpt-4o-mini", "C4"),
                ("E5 no doc", "JWST", "LJS gpt-4o-mini no-doc", "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini", "C4"),
                ("E5 haiku no doc", "JWST", "LJS haiku-5.5 no-doc",
                 "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5", "C4"),
                ("R3 (sol input)", "EIRENE", None, "input_control_sol/ljs/gpt-4o-mini", "C1")]
    pairs = csv("a04_cluster_stats/pairwise_tests.csv")
    rank_rows = {llm: [m(llm)] for llm in MODEL_ORDER}
    sig_rows = {}
    for label, doc, metric, d, cond in settings:
        lj = _ljs(d, cond)
        means = lj.groupby("llm").ljs.mean()
        order = means.sort_values(ascending=False).index.tolist()
        for llm in MODEL_ORDER:
            rank_rows[llm].append(str(order.index(llm) + 1) if llm in order else "")
        for a, b in itertools.combinations(MODEL_ORDER, 2):
            key = f"{SHORT[a]} -- {SHORT[b]}"
            if metric is not None:
                p = pairs[(pairs.document == doc) & (pairs.metric == metric) & (pairs.a == a) & (pairs.b == b)]
                flags = "".join(ch for ch, col in (("B", "p_block_holm"), ("C", "p_cluster_holm"), ("M", "p_mixed_holm"))
                                if len(p) and p[col].iloc[0] < 0.05)
            else:  # R3: one run, so only the paired test by category
                w = lj.pivot_table(index="category", columns="llm", values="ljs")
                ps = {(x, y): wilcoxon_p(w[x], w[y]) for x, y in itertools.combinations(MODEL_ORDER, 2)}
                adj = dict(zip(ps, holm(list(ps.values()))))
                flags = "B" if adj[(a, b)] < 0.05 else ""
            sig_rows.setdefault(key, [key]).append(flags or "--")
    title = ("Pairs with a significant difference (B: block test; C: cluster bootstrap; M: mixed model; Holm, "
             "$\\alpha=0.05$)")
    rows = list(rank_rows.values()) + [["\\midrule"],
                                       ["\\multicolumn{" + str(len(settings) + 1) + "}{l}{\\textit{" + title + "}} \\\\"]] \
        + list(sig_rows.values())
    write_paper_table(
        OUT / "tab_ranking.tex",
        "Robustness of the model ranking by LJS (RQ2). Upper block: rank of each model (1 = highest mean LJS) per "
        "document, judge and version of the models (with or without the doc comments); R3: the same models generated "
        "from another input extraction (\\llm{gpt-6.1-sol}, 152 categories, one run, without repair). Lower block: "
        "pairwise differences that are significant under the paired block test by (run, category), the cluster "
        "bootstrap of categories and the mixed model with a random intercept per category (R3: block test by "
        "category only).",
        "tab:ranking", ["Model"] + [s[0] for s in settings], "l" + "c" * len(settings), rows, wide=True)


# ---------------------------------------------------------------------------
def tab_c4p() -> None:
    s = csv("r11_pilot_repair/summary_by_model.csv")
    e = csv("r11_pilot_repair/elements.csv")
    st = csv("a14_guard_rejections/stagnation_frequency.csv")
    pm = csv("r11_pilot_repair/per_model.csv")
    needing = pm[pm.pilot_initial_errors > 0].groupby(["document", "llm"]).size()
    rows = []
    for doc in ("EIRENE", "JWST"):
        for llm in model_sort(s[s.document == doc].llm):
            r = s[(s.document == doc) & (s.llm == llm)].iloc[0]
            x = e[(e.document == doc) & (e.llm == llm)].iloc[0]
            g = st[(st.document == doc) & (st.llm == llm)].iloc[0]
            arrow = lambda k: f"{int(x[f'{k}_before'])}$\\rightarrow${int(x[f'{k}_after'])}"  # noqa: E731
            rows.append([doc, m(llm), f"{int(needing[(doc, llm)])}/{int(r.n)}", fmt(r.calls_per_repaired, 2),
                         fmt(r.iterations_per_repaired, 2), fmt(r.cost_per_repaired, 4),
                         f"{int(r.guard_retries_antlr)}/{int(r.guard_rejections_antlr)}",
                         f"{int(r.guard_retries_content)}/{int(r.guard_rejections_content)}",
                         str(int(g.stagnant_models_new)), fmt(r.changed_median, 0), fmt(r.unchanged_median, 1),
                         arrow("requirement"), arrow("satisfy"), arrow("constraint"), arrow("interface_usage"),
                         arrow("interface_def"), arrow("effective_connections")])
    write_paper_table(
        OUT / "tab_c4p.tex",
        "Reference stage (C4P, RQ1 and RQ2): repair with the Pilot Implementation 2024-04.1 as validator, on the final C4 "
        "models after the import normalisation. Repaired: models with at least one Pilot error (three of them, two of "
        "\\llm{gpt-6-luna} on EIRENE and one of \\llm{gemini-3.5-flash-lite} on JWST, were left unchanged). Calls, iterations "
        "and cost (USD): per repaired model. Guard: retries/rejections for breaking grammar validity (ANTLR) and "
        "for losing content. Stagn.: repaired models with an iteration in which neither the diagnostics nor the "
        "model changed. Changed: median lines changed; Unch.: median \\% of lines kept. Element counts summed over "
        "the models, before $\\rightarrow$ after; effective connections: interface usages with ends plus "
        "\\texttt{connect} statements.",
        "tab:c4p", ["Doc.", "Model", "Repaired", "Calls", "Iters", "Cost", "Guard ANTLR", "Guard content", "Stagn.",
                    "Changed", "Unch.\\%", "Requirement", "Satisfy", "Constraint", "Iface usage", "Iface def",
                    "Eff. conn."], "llrrrrrrrrrrrrrrr", rows, wide=True)


# ---------------------------------------------------------------------------
def tab_cost() -> None:
    r11 = pd.read_csv(RESULTS_DIR / "pilot_repair" / "pilot_repair_results.csv")
    extraction = {}
    for doc, f in (("EIRENE", "eirene_sliding_window_gpt-6-luna_run1.json"),
                   ("JWST", "jwst_sliding_window_gpt-6-luna_run1.json")):
        extraction[doc] = json.loads((RESULTS_DIR / "extraction" / "runs" / f).read_text())["metadata"]["cost_usd"]
    na = lambda v, d: "--" if np.isnan(v) else fmt(v, d)  # noqa: E731  stage not measured
    rows, shares = [], []
    for doc, s, set_id in (("EIRENE", "E1", "E1"), ("JWST", "E5", "E5")):
        res = load_results(s)
        c4 = res[res.condition == "C4"]
        for llm in model_sort(c4.llm):
            r = c4[c4.llm == llm]
            gen = r.generation_cost_usd.mean() * N_CAT[doc]
            rep = r.repair_cost.mean() * N_CAT[doc]
            x = r11[(r11.set == set_id) & (r11.llm == llm)]
            ref = x.cost_usd.sum() / 3 if len(x) else np.nan
            grammar_total = extraction[doc] + gen + rep
            total = grammar_total + ref  # NaN when the reference stage was not run
            rows.append([doc, m(llm), fmt(extraction[doc], 3), fmt(gen, 3), fmt(rep, 4), fmt(grammar_total, 2),
                         na(ref, 3), na(total, 2)])
            shares.append({"document": doc, "llm": llm, "extraction": extraction[doc], "generation": gen,
                           "grammar_repair": rep, "through_grammar": grammar_total, "reference": ref, "total": total,
                           "grammar_repair_pct_of_through_grammar": rep / grammar_total * 100,
                           "repair_pct_of_total": (rep + ref) / total * 100})
    pd.DataFrame(shares).to_csv(OUT / "tab_cost.csv", index=False)
    write_paper_table(
        OUT / "tab_cost.tex",
        "Cost per specification (RQ4), in USD, by stage: extraction of the input requirements (once, "
        "\\llm{gpt-6-luna}), generation and grammar-stage repair (C4) of every category, and the reference stage "
        "(C4P); means over the three runs (77 categories for EIRENE, 86 for JWST). Through grammar: extraction, "
        "generation and grammar repair, measured for the four generators. Reference and Total: only for the two "
        "generators run through C4P; -- marks a stage that was not measured. Judging is excluded: it is an "
        "evaluation instrument, not part of the pipeline.",
        "tab:cost", ["Doc.", "Model", "Extraction", "Generation", "Grammar", "Through grammar", "Reference", "Total"],
        "llrrrrrr", rows)


# ---------------------------------------------------------------------------
def rb(before, after) -> str:
    """Rank-biserial effect size of a paired before/after comparison, formatted ('--' when undefined)."""
    v = rank_biserial(before, after)
    return "--" if np.isnan(v) else f"{v:+.2f}"


def _c4p_ljs_pairs() -> pd.DataFrame:
    """LJS without doc before and after C4P of the models it changed (the pairs of r11_pilot_repair), per judge."""
    keys = ["pdf", "llm", "run", "category"]
    changed = pd.DataFrame([{"set": x["set"], "pdf": x["pdf"], "llm": x["llm"], "run": int(x["run"]),
                             "category": x["category"]}
                            for x in jsonl(RESULTS_DIR / "pilot_repair" / "sysml_models.jsonl")
                            if x["input_code"] != x["sysml_code"]])
    before = {("E1", "gpt-4o-mini"): "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
              ("E1", "claude-haiku-5.5"): "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5",
              ("E5", "gpt-4o-mini"): "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
              ("E5", "claude-haiku-5.5"): "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"}
    out = []
    for judge in ("gpt-4o-mini", "claude-haiku-5.5"):
        a = load_ljs(f"pilot_repair/nodoc/ljs/{judge}")
        for s, doc in (("E1", "EIRENE"), ("E5", "JWST")):
            b = load_ljs(before[(s, judge)])
            mm = (changed[changed.set == s][keys]
                  .merge(b[b.condition == "C4"][keys + ["ljs"]], on=keys)
                  .merge(a[keys + ["ljs"]], on=keys, suffixes=("_before", "_after")).dropna(subset=["ljs_before", "ljs_after"]))
            out.append(mm.assign(judge=judge, document=doc))
    return pd.concat(out)


def tab_repair_semantics() -> None:
    rows = []

    def paired(before: pd.DataFrame, after: pd.DataFrame, keys=("llm", "run", "category")):
        mm = before.merge(after, on=list(keys), suffixes=("_b", "_a")).dropna(subset=["ljs_b", "ljs_a"])
        return mm

    def add(stage, setting, llm, cond, judge, mm):
        if len(mm) == 0:
            return
        rows.append([stage, setting, m(llm), cond, judge, str(len(mm)), fmt(mm.ljs_b.mean(), 3), fmt(mm.ljs_a.mean(), 3),
                     f"{(mm.ljs_a - mm.ljs_b).mean():+.3f}", rb(mm.ljs_b, mm.ljs_a),
                     fmt_p(wilcoxon_p(mm.ljs_b, mm.ljs_a)) if len(mm) > 1 else "--"])

    for setting, s, judge_dir in (("E1", "E1", "pipeline/ljs/gpt-4o-mini"), ("E5", "E5", "jwst_pipeline/ljs/gpt-4o-mini")):
        res = load_results(s)
        lj = load_ljs(judge_dir)
        inv = res[(res.condition == "C1") & (res.initial_errors > 0)][["llm", "run", "category"]]
        b = lj[lj.condition == "C1"][["llm", "run", "category", "ljs"]].merge(inv)
        a = lj[lj.condition == "C4"][["llm", "run", "category", "ljs"]].merge(inv)
        for llm in model_sort(b.llm):
            add("grammar", setting, llm, "C4", "4o-mini", paired(b[b.llm == llm], a[a.llm == llm]))
    banks = [("E3", ["ablation_stress", "ablation_stress_revision"], ["C2", "C2KB", "C3", "C4", "FULLREV"]),
             ("E6", ["jwst_v1_bank", "jwst_v1_bank_flashlite"], ["C2", "C2KB", "C3", "C4", "FULLREV"])]
    for setting, phases, conds in banks:
        lj = pd.concat([load_ljs(f"{p}/ljs/gpt-4o-mini") for p in phases])
        res = pd.concat([pd.read_csv(RESULTS_DIR / p / ("ablation_results.csv" if "stress" in p else "pipeline_results.csv"))
                         for p in phases])
        inv = res[(res.condition == "C1") & (res.initial_errors > 0)][["llm", "run", "category"]].drop_duplicates()
        b = lj[lj.condition == "C1"][["llm", "run", "category", "ljs"]].drop_duplicates(["llm", "run", "category"]).merge(inv)
        for llm in model_sort(b.llm):
            for c in conds:
                a = lj[(lj.condition == c) & (lj.llm == llm)][["llm", "run", "category", "ljs"]].merge(inv)
                add("grammar", setting, llm, c, "4o-mini", paired(b[b.llm == llm], a))
    r = csv("r11_pilot_repair/ljs_before_after.csv")
    pairs = _c4p_ljs_pairs()
    for judge, short in (("gpt-4o-mini", "4o-mini, no doc"), ("claude-haiku-5.5", "haiku, no doc")):
        pj = pairs[pairs.judge == judge]
        for x in r[(r.judge == judge) & (r.document != "all")].itertuples():
            pp = pj[(pj.document == x.document) & (pj.llm == x.llm)]
            assert len(pp) == x.n_changed_pairs, (judge, x.document, x.llm)  # same pairs as the R11 analysis
            rows.append(["reference", f"E7 {x.document}", m(x.llm), "C4P", short, str(int(x.n_changed_pairs)),
                         "", "", f"{x.delta_changed:+.3f}", rb(pp.ljs_before, pp.ljs_after), fmt_p(x.p_changed)])
        x = r[(r.judge == judge) & (r.document == "all")].iloc[0]
        assert len(pj) == x.n_changed_pairs, judge
        rows.append(["reference", "E7 all", "all", "C4P", short, str(int(x.n_changed_pairs)), fmt(x.ljs_before, 3),
                     fmt(x.ljs_after, 3), f"{x.delta_changed:+.3f}", rb(pj.ljs_before, pj.ljs_after),
                     fmt_p(x.p_changed)])
    write_paper_table(
        OUT / "tab_repair_semantics.tex",
        "Semantic effect of repair, paired on the repaired models: LJS of the same model before and after repair. "
        "Grammar stage: generations with at least one diagnostic, judged with the doc comments by \\llm{gpt-4o-mini} "
        "(E1, E5: C1 vs C4; banks: C1 vs each condition). Reference stage (E7): models changed by C4P, judged without "
        "doc comments (\\llm{claude-haiku-5.5}: stratified random sample of 150 changed models; mean change per "
        "stratum). $r$: matched-pairs rank-biserial correlation (effect size of the Wilcoxon test; positive when the "
        "LJS rises after repair). $p$: Wilcoxon signed-rank test, not adjusted.",
        "tab:repair_semantics", ["Stage", "Setting", "Model", "Cond.", "Judge", "n", "Before", "After",
                                 "$\\Delta$LJS", "$r$", "$p$"], "lllllrrrrrr", rows, wide=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tab_models()
    tab_experiments()
    tab_validity()
    tab_semantics()
    tab_ranking()
    tab_c4p()
    tab_cost()
    tab_repair_semantics()


if __name__ == "__main__":
    main()
