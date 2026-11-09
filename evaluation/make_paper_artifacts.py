"""Phase 4: LaTeX tables, PNG figures and summary.md files from the result CSVs (no LLM calls).

    python -m evaluation.make_paper_artifacts
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from core.models import SUPPORTED_MODELS  # noqa: E402
from evaluator import DEFAULT_JUDGE  # noqa: E402

from evaluation import require_study_results  # noqa: E402
from evaluation.common import (  # noqa: E402
    ABLATION_DIR,
    ABLATION_STRESS_DIR,
    BEST_REQUIREMENTS_PATH,
    EXTRACTION_DIR,
    PIPELINE_DIR,
    read_json,
)


# Reference categorical palette (fixed order, never cycled) and recessive ink.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
STRATEGY_LABELS = {"raw": "Raw", "sliding_window": "Sliding Window"}
STRATEGY_MARKERS = {"raw": "o", "sliding_window": "s"}
CONDITION_ORDER = ["C1", "C2", "C3", "C4"]
CONDITIONS_REPAIR = {"C1": False, "C2": True, "C3": True, "C4": True}

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 9, "axes.edgecolor": INK_2, "axes.labelcolor": INK, "axes.titlesize": 10,
    "xtick.color": INK_2, "ytick.color": INK_2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False,
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def model_order(names) -> list[str]:
    registry = list(SUPPORTED_MODELS)
    names = list(dict.fromkeys(names))
    return sorted(names, key=lambda n: (registry.index(n) if n in registry else len(registry), n))


def model_colors(names) -> dict[str, str]:
    # Colour follows the model's registry slot, so it is stable across figures.
    registry = list(SUPPORTED_MODELS)
    return {n: SERIES[(registry.index(n) if n in registry else len(registry)) % len(SERIES)] for n in names}


def load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        print(f"  skip: {path} not found")
        return None
    df = pd.read_csv(path)
    if df.empty:
        print(f"  skip: {path} is empty")
        return None
    return df


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1"])


def tex_escape(text: str) -> str:
    return str(text).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def fmt(value, digits: int) -> str:
    return "" if value is None or (isinstance(value, float) and np.isnan(value)) else f"{value:.{digits}f}"


def write_table(path: Path, caption: str, label: str, columns: list[str], align: str,
                rows: list[list[str]], wide: bool = False) -> None:
    env = "table*" if wide else "table"
    lines = [f"\\begin{{{env}}}", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}",
             f"\\begin{{tabular}}{{{align}}}", "\\toprule", " & ".join(columns) + r" \\", "\\midrule"]
    for row in rows:
        lines.append(row[0] if len(row) == 1 else " & ".join(row) + r" \\")  # 1 cell = raw LaTeX line
    lines += ["\\bottomrule", "\\end{tabular}", f"\\end{{{env}}}", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote {path}")


def save_figure(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path}")


def write_summary(path: Path, title: str, lines: list[str]) -> None:
    path.write_text(f"# {title}\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {path}")


def pct(x: float) -> str:
    return f"{x:.1f}%"


def fmt_p(p: float) -> str:
    if p is None or np.isnan(p):
        return "--"
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


# ---------------------------------------------------------------------------
# Statistics (paired designs)
# ---------------------------------------------------------------------------
def holm(pvalues: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values (NaN entries are kept and not counted)."""
    p = np.asarray(pvalues, dtype=float)
    valid = np.flatnonzero(~np.isnan(p))
    adjusted = np.full(len(p), np.nan)
    running = 0.0
    for rank, i in enumerate(valid[np.argsort(p[valid], kind="stable")]):
        running = max(running, min(1.0, (len(valid) - rank) * p[i]))
        adjusted[i] = running
    return adjusted.tolist()


def cochran_q(matrix: np.ndarray) -> tuple[float, int, float]:
    """Cochran's Q test for k related binary samples (rows = blocks, columns = treatments)."""
    from scipy.stats import chi2

    x = np.asarray(matrix, dtype=float)
    k = x.shape[1]
    col, row, total = x.sum(axis=0), x.sum(axis=1), x.sum()
    denom = k * total - (row ** 2).sum()
    if denom == 0:
        return np.nan, k - 1, np.nan
    q = (k - 1) * (k * (col ** 2).sum() - total ** 2) / denom
    return float(q), k - 1, float(chi2.sf(q, k - 1))


def mcnemar_exact(a, b) -> float:
    """Exact McNemar test on two paired binary samples (binomial test on the discordant pairs)."""
    from scipy.stats import binomtest

    a, b = np.asarray(a, dtype=bool), np.asarray(b, dtype=bool)
    only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
    if only_a + only_b == 0:
        return 1.0
    return float(binomtest(only_a, only_a + only_b, 0.5).pvalue)


def wilcoxon_p(a, b) -> float:
    from scipy.stats import wilcoxon

    try:
        return float(wilcoxon(a, b).pvalue)
    except ValueError:  # all differences zero
        return np.nan


def rank_biserial(a, b) -> float:
    """Matched-pairs rank-biserial correlation of b - a (the effect size of the Wilcoxon signed-rank test).

    In [-1, 1]: +1 when every non-zero difference is positive (b > a). NaN when all differences are zero."""
    from scipy.stats import rankdata

    d = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    d = d[d != 0]
    if len(d) == 0:
        return np.nan
    ranks = rankdata(np.abs(d))
    return float((ranks[d > 0].sum() - ranks[d < 0].sum()) / ranks.sum())


def mcnemar_odds_ratio(only_b: int, only_a: int) -> float:
    """Odds ratio of the discordant pairs (only_b / only_a), with 0.5 added to both when one is zero.

    NaN when there are no discordant pairs."""
    if only_a + only_b == 0:
        return np.nan
    if only_a == 0 or only_b == 0:
        return (only_b + 0.5) / (only_a + 0.5)
    return only_b / only_a


def is_degenerate(initial_len, final_len, ratio: float = 0.5):
    """A repair is degenerate when the returned model keeps less than `ratio` of the generated code."""
    return np.asarray(final_len) < ratio * np.asarray(initial_len)


def literal_share(requirements: list[str], code: str, prefix: int = 60) -> float:
    """Share of requirements whose first `prefix` characters appear verbatim (case/space-normalised) in the code."""
    norm = lambda s: " ".join(str(s).lower().split())  # noqa: E731
    text = norm(code)
    reqs = [norm(r)[:prefix] for r in requirements if norm(r)]
    return float(np.mean([r in text for r in reqs])) if reqs else np.nan


def load_models(out_dir: Path) -> pd.DataFrame | None:
    """Final SysML code per row (sysml_models.jsonl) with its length and the category requirements."""
    path = out_dir / "sysml_models.jsonl"
    if not path.exists():
        print(f"  skip: {path} not found")
        return None
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    models = pd.DataFrame(rows)[["llm", "condition", "run", "category", "requirements", "sysml_code"]]
    models["code_len"] = models["sysml_code"].str.len()
    return models


def repair_semantics(df: pd.DataFrame, models: pd.DataFrame, tables: Path, label: str) -> list[str]:
    """LJS change caused by repair on the invalid generations, split into normal and degenerate repairs.

    Paired design: C1 keeps the generated code, so (repair condition - C1) on the same (run, category)
    isolates what the repair did to the model's content.
    """
    if df["ljs"].isna().all():
        return []
    data = df.merge(models[["llm", "condition", "run", "category", "code_len"]],
                    on=["llm", "condition", "run", "category"], how="left")
    rows, lines = [], []
    for m in model_order(data["llm"]):
        sub = data[data.llm == m]
        c1 = sub[sub.condition == "C1"].set_index(["run", "category"])
        for c in [c for c in CONDITION_ORDER[1:] if c in set(sub.condition)]:
            rep = sub[sub.condition == c].set_index(["run", "category"])
            j = c1[["ljs", "code_len", "initial_errors"]].join(rep[["ljs", "code_len"]], rsuffix="_rep", how="inner")
            j = j[j.initial_errors >= 1]
            if j.empty:
                continue
            j["degenerate"] = is_degenerate(j.code_len, j.code_len_rep)
            for group, g in (("Normal", j[~j.degenerate]), ("Degenerate", j[j.degenerate]), ("All", j)):
                if g.empty or (group == "All" and not j.degenerate.any()):
                    continue
                p = wilcoxon_p(g.ljs, g.ljs_rep) if len(g) > 1 else np.nan
                rows.append([tex_escape(m), c, group, str(len(g)), fmt(g.ljs.mean(), 3), fmt(g.ljs_rep.mean(), 3),
                             f"{g.ljs_rep.mean() - g.ljs.mean():+.3f}", fmt_p(p)])
                lines.append(f"- Repair semantics {m} {c} {group.lower()}: n = {len(g)}, LJS {g.ljs.mean():.3f} -> "
                             f"{g.ljs_rep.mean():.3f} (delta {g.ljs_rep.mean() - g.ljs.mean():+.3f}, Wilcoxon p = "
                             f"{p:.3f})")
    if rows:
        write_table(tables / "tab_repair_semantics.tex",
                    "Semantic effect of repair on the invalid generations (paired: same generated code under C1 and "
                    "the repair condition). Degenerate: the repaired model keeps less than half of the generated "
                    "code. LJS before = C1 (generated code); after = repaired code. $p$: Wilcoxon signed-rank.",
                    f"tab:{label}_repair_semantics",
                    ["Model", "Cond.", "Repairs", "n", "LJS before", "LJS after", "$\\Delta$LJS", "$p$"],
                    "lllrrrrr", rows)
    return lines


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def extraction_artifacts() -> None:
    print("Extraction")
    df = load_csv(EXTRACTION_DIR / "extraction_results.csv")
    if df is None:
        return
    tables, figures = EXTRACTION_DIR / "tables", EXTRACTION_DIR / "figures"
    agg = (df.groupby(["pdf", "strategy", "llm"])
           .agg(n_cat=("num_categories", "mean"), req=("num_requirements", "mean"), calls=("llm_calls", "mean"),
                cost=("cost_usd", "mean"), lat=("latency_s", "mean"), runs=("run", "nunique"))
           .reset_index())

    rows: list = []
    docs = sorted(agg["pdf"].unique())
    for i, doc in enumerate(docs):
        if i:
            rows.append(["\\midrule"])
        rows.append([f"\\multicolumn{{7}}{{l}}{{\\textbf{{{doc.upper()}}}}} \\\\"])
        sub = agg[agg["pdf"] == doc]
        for strategy in [s for s in STRATEGY_LABELS if s in set(sub["strategy"])]:
            for model in model_order(sub[sub["strategy"] == strategy]["llm"]):
                r = sub[(sub["strategy"] == strategy) & (sub["llm"] == model)].iloc[0]
                rows.append([STRATEGY_LABELS[strategy], tex_escape(model), fmt(r.n_cat, 1), fmt(r.req, 1),
                             fmt(r.calls, 1), fmt(r.cost, 4), fmt(r.lat, 1)])
    write_table(tables / "tab_extraction.tex",
                "Requirement extraction by document, strategy and model (means over runs; cost in USD, latency in s).",
                "tab:extraction", ["Strategy", "Model", "\\#Cat", "\\#Req", "Calls", "Cost", "Lat."],
                "llrrrrr", rows, wide=True)

    agreement = load_csv(EXTRACTION_DIR / "extraction_agreement.csv")
    if agreement is not None:
        jac = agreement.groupby(["pdf", "llm"])["jaccard_similarity"].mean().reset_index()
        rows = [[doc.upper(), tex_escape(m), fmt(jac[(jac.pdf == doc) & (jac.llm == m)].jaccard_similarity.iloc[0], 3)]
                for doc in sorted(jac["pdf"].unique()) for m in model_order(jac[jac.pdf == doc]["llm"])]
        write_table(tables / "tab_jaccard.tex",
                    "Agreement between raw and sliding-window extraction (fuzzy Jaccard, cosine $\\geq$ 0.85; mean over runs).",
                    "tab:jaccard", ["Document", "Model", "Jaccard"], "llr", rows)

    # Pareto: number of requirements (more is better) vs cost (less is better), one panel per document.
    colors = model_colors(agg["llm"])
    fig, axes = plt.subplots(1, len(docs), figsize=(4.2 * len(docs), 3.4), squeeze=False)
    for ax, doc in zip(axes[0], docs):
        sub = agg[agg["pdf"] == doc].reset_index(drop=True)
        for _, r in sub.iterrows():
            ax.scatter(r.req, r.cost, s=42, marker=STRATEGY_MARKERS.get(r.strategy, "o"), color=colors[r.llm],
                       edgecolor="white", linewidth=1.5, zorder=3)
        frontier = [i for i, r in sub.iterrows()
                    if not any((o.req >= r.req and o.cost <= r.cost and (o.req > r.req or o.cost < r.cost))
                               for j, o in sub.iterrows() if j != i)]
        front = sub.loc[frontier].sort_values("cost")
        ax.plot(front.req, front.cost, color=INK_2, linewidth=1, linestyle="--", zorder=2, label="Efficient frontier")
        for (req, cost), grp in front.groupby(["req", "cost"]):
            names = " / ".join(f"{STRATEGY_LABELS.get(r.strategy, r.strategy)} {r.llm}" for _, r in grp.iterrows())
            # Keep labels inside the panel: points on the right are labelled to their left (or above, when
            # low, so they clear the labels of the cheap points), the rest to their right.
            if req <= 0.6 * sub.req.max():
                offset, ha, va = (5, 4), "left", "baseline"
            elif cost > 0.5 * sub.cost.max():
                offset, ha, va = (-8, 0), "right", "center"
            else:
                offset, ha, va = (-6, 10), "right", "baseline"
            ax.annotate(names, (req, cost), textcoords="offset points", xytext=offset, ha=ha, va=va, fontsize=7,
                        color=INK_2)
        ax.set_title(doc.upper(), color=INK)
        ax.set_xlabel("Requirements extracted (mean)")
        ax.set_ylabel("Extraction cost (USD, mean)")
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=m) for m, c in colors.items()]
    handles += [plt.Line2D([], [], marker=STRATEGY_MARKERS[s], linestyle="", color=INK_2, markerfacecolor="none",
                           label=STRATEGY_LABELS[s]) for s in STRATEGY_LABELS]
    handles.append(plt.Line2D([], [], color=INK_2, linestyle="--", linewidth=1, label="Efficient frontier"))
    fig.legend(handles=handles, loc="lower center", ncol=min(5, len(handles)), fontsize=7, bbox_to_anchor=(0.5, -0.12))
    save_figure(fig, figures / "fig_extraction_pareto.png")

    lines = []
    for doc in docs:
        sub = agg[agg["pdf"] == doc].sort_values("req", ascending=False)
        top, cheap = sub.iloc[0], sub.sort_values("cost").iloc[0]
        lines.append(f"- **{doc}**: most requirements = {top.llm} / {top.strategy} ({top.req:.1f} req, "
                     f"{top.n_cat:.1f} cat, ${top.cost:.4f}); cheapest = {cheap.llm} / {cheap.strategy} (${cheap.cost:.4f}, "
                     f"{cheap.req:.1f} req).")
        for strategy in [s for s in STRATEGY_LABELS if s in set(sub["strategy"])]:
            s = sub[sub["strategy"] == strategy]
            lines.append(f"  - {strategy}: requirements {s.req.min():.1f}-{s.req.max():.1f}, "
                         f"cost ${s.cost.min():.4f}-${s.cost.max():.4f} across models.")
        if agreement is not None and doc in set(agreement["pdf"]):
            lines.append(f"  - mean raw vs sliding-window Jaccard: {agreement[agreement.pdf == doc].jaccard_similarity.mean():.3f}")
    if BEST_REQUIREMENTS_PATH.exists():
        s = read_json(BEST_REQUIREMENTS_PATH)["source"]
        lines.append(f"- **Best JSON** (input to pipeline and ablation): {s['file']} - {s['n_requirements']} requirements, "
                     f"{s['n_categories']} categories, extraction cost ${s['cost_usd']:.4f}. Criterion: {s['criterion']}.")
    lines.append(f"- Successful runs: {len(df)}.")
    write_summary(EXTRACTION_DIR / "summary.md", "Extraction - key figures", lines)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
LJS_COLUMNS = ["ljs", "ljs_strict", "ljs_lenient", "ieee_correctness", "ieee_completeness", "ieee_unambiguity",
               "ieee_verifiability", "ieee_traceability"]
IEEE_LABELS = {"ieee_correctness": "Corr.", "ieee_completeness": "Compl.", "ieee_unambiguity": "Unamb.",
               "ieee_verifiability": "Verif.", "ieee_traceability": "Trace."}


def load_phase(out_dir: Path, results_name: str) -> pd.DataFrame | None:
    df = load_csv(out_dir / results_name)
    if df is None:
        return None
    for col in ("converged", "stagnation"):
        df[col] = as_bool(df[col])
    return attach_ljs(df, out_dir)


def attach_ljs(df: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    """Adds the LJS columns computed by `python -m evaluator` with the default judge.

    LJS is only reported when every row has been judged: a partial run (e.g. a pilot) would compare
    models on different samples, so the columns are then left empty, never filled.
    """
    path = out_dir / "ljs" / DEFAULT_JUDGE / "ljs_results.csv"
    keys = ["pdf", "llm", "condition", "run", "category"]
    ljs = pd.read_csv(path) if path.exists() else None
    if ljs is not None and not ljs.empty:
        df = df.merge(ljs[keys + ["judgment_key"] + LJS_COLUMNS + ["judge_cost_usd"]], on=keys, how="left")
        missing = int(df["judgment_key"].isna().sum())
        if missing:
            print(f"  LJS ({DEFAULT_JUDGE}): {missing}/{len(df)} rows not judged yet, LJS omitted")
            df[LJS_COLUMNS + ["judge_cost_usd"]] = np.nan
    else:
        print(f"  LJS ({DEFAULT_JUDGE}): {path} not found, LJS omitted")
        for col in LJS_COLUMNS + ["judgment_key", "judge_cost_usd"]:
            df[col] = np.nan
    return df


def ljs_artifacts(df: pd.DataFrame, tables: Path, label: str) -> list[str]:
    """LJS breakdown table per model and condition; returns summary lines (none if LJS is missing)."""
    if df["ljs"].isna().all():
        return []
    g = df.groupby(["llm", "condition"])[LJS_COLUMNS].mean().reset_index()
    rows, lines = [], []
    for m in model_order(g["llm"]):
        for c in CONDITION_ORDER:
            sel = g[(g.llm == m) & (g.condition == c)]
            if sel.empty:
                continue
            r = sel.iloc[0]
            rows.append([tex_escape(m), c, fmt(r.ljs, 3), fmt(r.ljs_strict, 3), fmt(r.ljs_lenient, 3)]
                        + [fmt(r[col] * 100, 1) for col in IEEE_LABELS])
            lines.append(f"- LJS {m} {c}: {r.ljs:.3f} (strict {r.ljs_strict:.3f}, lenient {r.ljs_lenient:.3f})")
    judged = df.dropna(subset=["judgment_key"]).drop_duplicates("judgment_key")
    write_table(tables / "tab_ljs.tex",
                f"LLM-as-a-Judge score per model and condition (judge: {tex_escape(DEFAULT_JUDGE)}). LJS = (satisfied "
                f"+ 0.5 partial) / applicable requirements; Strict and Lenient count only satisfied, or satisfied and "
                f"partial. IEEE 830 columns: \\% of applicable requirements with the attribute met.",
                f"tab:{label}_ljs", ["Model", "Cond.", "LJS", "Strict", "Lenient", *IEEE_LABELS.values()],
                "llrrrrrrrr", rows, wide=True)
    lines.append(f"- LJS judge {DEFAULT_JUDGE}: {len(judged)} distinct models judged, ${judged.judge_cost_usd.sum():.4f}.")
    return lines


PAIR_KEYS = ["llm", "run", "category"]


def paired_only(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Keep the (model, run, category) pairs that have every condition; return (paired rows, excluded pairs).

    In the paired design C1 and C4 share one generation, so a pair missing a condition (e.g. an aborted
    repair) would make the conditions compare different samples. Missing rows are dropped, never filled.
    """
    n_conditions = df["condition"].nunique()
    counts = df.groupby(PAIR_KEYS)["condition"].nunique()
    complete = counts[counts == n_conditions].index
    keyed = df.set_index(PAIR_KEYS)
    excluded = keyed.loc[~keyed.index.isin(complete)].reset_index()
    return keyed.loc[keyed.index.isin(complete)].reset_index(), excluded


def error_distribution(out_dir: Path, pairs: pd.DataFrame | None = None) -> pd.DataFrame | None:
    errors = load_csv(out_dir / "errors.csv")
    if errors is None:
        return None
    if pairs is not None:
        errors = errors.merge(pairs[PAIR_KEYS].drop_duplicates(), on=PAIR_KEYS)
    # Errors of the first generation (iteration 0). In the paired design every condition starts from
    # the same generation, so each (model, run, category) error is counted once.
    initial = errors[errors["iteration"] == 0].drop_duplicates(
        subset=["llm", "run", "category", "line", "column", "message"])
    dist = initial.groupby("error_category").size().sort_values(ascending=False).rename("count").reset_index()
    dist["share"] = dist["count"] / dist["count"].sum() * 100
    return dist


ROUTER_LABELS = {"DELIMITERS": "Delimiters", "DOC_COMMENT": "Doc/Comment", "CONSTRAINT_EXPR": "Constraint expr.", "QUALIFICATION": "Qualification",
                 "DECLARATION_FORM": "Decl. form", "LITERALS_STRINGS": "Literals", "ALT_NO_VIABLE": "No viable alt.",
                 "LEXER": "Lexer", "UNKNOWN": "Unknown"}


def pretty_category(cat: str) -> str:
    return ROUTER_LABELS.get(cat, cat.replace("_", " ").title())


def model_tests(df: pd.DataFrame, tables: Path) -> list[str]:
    """Between-model comparison, paired by (run, category) over the blocks every model has.

    C1 convergence: Cochran's Q + pairwise exact McNemar. LJS and cost per category under C4: Friedman +
    pairwise Wilcoxon. Pairwise p-values are Holm-adjusted within each metric.
    """
    from scipy.stats import friedmanchisquare

    models = model_order(df["llm"])
    if len(models) < 3:
        return []
    metrics = [("Convergence (C1, \\%)", "C1", "converged", 100.0, 1),
               ("LJS (C4)", "C4", "ljs", 1.0, 3),
               ("Cost/cat (C4, USD)", "C4", "cost_usd", 1.0, 4)]
    rows, lines = [], []
    for name, cond, col, scale, digits in metrics:
        if df[col].isna().all():
            continue
        wide = df[df.condition == cond].pivot_table(index=["run", "category"], columns="llm", values=col).dropna()
        wide = wide[models]
        n = len(wide)
        if col == "converged":
            stat, dof, p_all = cochran_q(wide.values)
            omnibus = f"Cochran's $Q({dof})={stat:.1f}$"
            pair_p = [mcnemar_exact(wide[a], wide[b]) for a, b in combinations(models, 2)]
        else:
            res = friedmanchisquare(*[wide[m] for m in models])
            stat, p_all = res.statistic, res.pvalue
            omnibus = f"Friedman $\\chi^2({len(models) - 1})={stat:.1f}$"
            pair_p = [wilcoxon_p(wide[a], wide[b]) for a, b in combinations(models, 2)]
        rows.append([f"\\multicolumn{{6}}{{l}}{{\\textit{{{name}}}: {omnibus}, $p$ = {fmt_p(p_all)}, n = {n}}} \\\\"])
        lines.append(f"- Between models, {name.replace(chr(92), '')}: omnibus p = {p_all:.2e}, n = {n}")
        for (a, b), p, p_holm in zip(combinations(models, 2), pair_p, holm(pair_p)):
            ma, mb = wide[a].mean() * scale, wide[b].mean() * scale
            rows.append([tex_escape(a), tex_escape(b), fmt(ma, digits), fmt(mb, digits), fmt_p(p), fmt_p(p_holm)])
            lines.append(f"  - {a} vs {b}: {ma:.{digits}f} vs {mb:.{digits}f}, p = {p:.3g}, Holm p = {p_holm:.3g}")
    if rows:
        write_table(tables / "tab_model_tests.tex",
                    "Pairwise comparison of the models, paired by (run, category) over the blocks available for all "
                    "models. Convergence: Cochran's $Q$ and exact McNemar tests; LJS and cost: Friedman and Wilcoxon "
                    "signed-rank tests. $p_{\\mathrm{Holm}}$: Holm-adjusted within each metric.",
                    "tab:model_tests", ["Model A", "Model B", "Mean A", "Mean B", "$p$", "$p_{\\mathrm{Holm}}$"],
                    "llrrrr", rows)
    return lines


def errordist_by_model(df: pd.DataFrame, tables: Path, out_dir: Path = PIPELINE_DIR,
                       label: str = "errordist_by_model") -> list[str]:
    """Initial (iteration 0) validation errors per model and router category, counted once per generation."""
    errors = load_csv(out_dir / "errors.csv")
    if errors is None:
        return []
    errors = errors.merge(df[PAIR_KEYS].drop_duplicates(), on=PAIR_KEYS)
    initial = errors[errors["iteration"] == 0].drop_duplicates(
        subset=["llm", "run", "category", "line", "column", "message"])
    cats = initial.groupby("error_category").size().sort_values(ascending=False).index.tolist()
    c1 = df[df.condition == "C1"]
    rows, lines = [], []
    for m in model_order(df["llm"]):
        sub = initial[initial.llm == m]
        n_invalid = int((c1[c1.llm == m].initial_errors >= 1).sum())
        total = len(sub)
        cells = [f"{int((sub.error_category == c).sum())} ({(sub.error_category == c).mean() * 100:.0f})" if total
                 else "0" for c in cats]
        rows.append([tex_escape(m), f"{n_invalid}/{int((c1.llm == m).sum())}", str(total)] + cells)
        top = sub.error_category.value_counts(normalize=True).head(2)
        lines.append(f"- Initial errors {m}: {total} in {n_invalid} invalid generations"
                     + ("; " + ", ".join(f"{k} {v * 100:.1f}%" for k, v in top.items()) if total else ""))
    write_table(tables / f"tab_{label}.tex",
                "Validation errors in the generated models (before any repair) per model and router category: "
                "count (\\% of the model's errors). Invalid: generations with at least one error.",
                f"tab:{label}",
                ["Model", "Invalid", "Errors"] + [pretty_category(c) for c in cats], "lrr" + "r" * len(cats), rows,
                wide=True)
    return lines


def rcs_literal(df: pd.DataFrame, models: pd.DataFrame, tables: Path) -> list[str]:
    """How much of RCS is explained by copying the requirement text verbatim into the model (C4)."""
    from scipy.stats import spearmanr

    c4 = df[df.condition == "C4"].merge(models[["llm", "condition", "run", "category", "requirements", "sysml_code"]],
                                         on=["llm", "condition", "run", "category"], how="left")
    c4["literal"] = [literal_share(r, c) for r, c in zip(c4.requirements, c4.sysml_code)]
    rows, lines = [], []
    for m in model_order(c4["llm"]):
        s = c4[c4.llm == m]
        rows.append([tex_escape(m), fmt(s.literal.mean() * 100, 1), fmt(s.rcs.mean(), 3), fmt(s.ljs.mean(), 3)])
        lines.append(f"- Literal copy {m} (C4): {s.literal.mean() * 100:.1f}% of requirements, RCS {s.rcs.mean():.3f}, "
                     f"LJS {s.ljs.mean():.3f}")
    ok = c4.dropna(subset=["literal", "rcs", "ljs"])
    rho_rcs, rho_ljs = spearmanr(ok.literal, ok.rcs).statistic, spearmanr(ok.literal, ok.ljs).statistic
    write_table(tables / "tab_rcs_literal.tex",
                f"Requirement text copied verbatim into the model (first 60 characters, case- and space-normalised) "
                f"versus RCS and LJS under C4. Across the {len(ok)} models, Spearman $\\rho$ between the literal share "
                f"and RCS is {rho_rcs:.2f}, and between the literal share and LJS {rho_ljs:.2f}.",
                "tab:rcs_literal", ["Model", "Literal copy\\%", "RCS", "LJS"], "lrrr", rows)
    lines.append(f"- Spearman literal share vs RCS = {rho_rcs:.2f}, vs LJS = {rho_ljs:.2f} (n = {len(ok)}).")
    return lines


def repair_effort(df: pd.DataFrame, tables: Path) -> list[str]:
    """What the C4 loop spends on the invalid generations of each model (the valid ones never enter it)."""
    c4 = df[df.condition == "C4"].copy()
    c4["repair_calls"] = c4["llm_calls"] - 1
    c4["repair_cost"] = c4["cost_usd"] - c4["generation_cost_usd"]
    rows, lines = [], []
    for m in model_order(c4["llm"]):
        b = c4[(c4.llm == m) & (c4.initial_errors >= 1)]
        if b.empty:
            rows.append([tex_escape(m), "0", "--", "--", "--", "--", "--", "--", "--"])
            continue
        rows.append([tex_escape(m), str(len(b)), fmt(b.initial_errors.mean(), 1), fmt(b.iterations.mean(), 2),
                     str(int(b.iterations.max())), fmt(b.repair_calls.mean(), 1), fmt(b.repair_cost.mean(), 4),
                     str(int((~b.converged).sum())), str(int(b.stagnation.sum()))])
        lines.append(f"- Repair effort {m} (C4, {len(b)} invalid generations): initial errors {b.initial_errors.mean():.1f}, "
                     f"iterations {b.iterations.mean():.2f} (max {int(b.iterations.max())}), repair calls "
                     f"{b.repair_calls.mean():.1f}, repair cost ${b.repair_cost.mean():.4f}, not converged "
                     f"{int((~b.converged).sum())}, stagnated {int(b.stagnation.sum())}; max repair cost "
                     f"${b.repair_cost.max():.2f} ({int(b.loc[b.repair_cost.idxmax()].initial_errors)} initial errors)")
    write_table(tables / "tab_repair_effort.tex",
                "Repair effort of the full framework (C4) on the invalid generations of each model (means per "
                "invalid generation; repair cost in USD). Not conv.: still invalid after the iteration limit; "
                "Stagn.: the error set stopped changing between iterations.",
                "tab:repair_effort", ["Model", "Invalid", "Init. err", "Iters", "Max iters", "Repair calls",
                                      "Repair cost", "Not conv.", "Stagn."], "lrrrrrrrr", rows)
    return lines


def bootstrap_ci(values, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    rng = np.random.default_rng(seed)
    means = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def semantic_syntactic_figure(df: pd.DataFrame, cost_spec: dict, path: Path) -> None:
    """Syntactic validity (x) vs semantic adequacy (y) per model: C1 (hollow) -> C4 (filled)."""
    if df["ljs"].isna().all():
        return
    models = model_order(df["llm"])
    colors = model_colors(models)
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    top, bottom, lows = 0.0, 1.0, []
    c4_ljs = df[df.condition == "C4"].groupby("llm").ljs.mean()
    rank = {m: i for i, m in enumerate(c4_ljs.sort_values(ascending=False).index)}
    for m in models:
        pts = {}
        for c in ("C1", "C4"):
            s = df[(df.llm == m) & (df.condition == c)]
            lo, hi = bootstrap_ci(s.ljs)
            pts[c] = (s.converged.mean() * 100, s.ljs.mean())
            ax.errorbar(*pts[c], yerr=[[pts[c][1] - lo], [hi - pts[c][1]]], fmt="none", ecolor=colors[m],
                        elinewidth=1, capsize=2, zorder=2)
            ax.scatter(*pts[c], s=64, marker="o", zorder=3, linewidth=2, edgecolor=colors[m],
                       facecolor=colors[m] if c == "C4" else "white")
        if pts["C1"] != pts["C4"]:
            ax.annotate("", xy=pts["C4"], xytext=pts["C1"], zorder=1,
                        arrowprops=dict(arrowstyle="-|>", color=colors[m], linewidth=1.2, shrinkA=6, shrinkB=6))
        cost = cost_spec.get(m)
        label = m + (f"\n${cost:.2f}/spec" if cost is not None else "")
        # Label at the C1 point (C4 points coincide at 100%), alternating above/below by LJS rank so that
        # models with close scores do not overlap.
        below = rank[m] % 2 == 1
        ax.annotate(label, pts["C1"], textcoords="offset points", xytext=(0, -16 if below else 13), ha="center",
                    va="top" if below else "bottom", fontsize=7, color=INK)
        top = max(top, hi)
        bottom = min(bottom, lo)
        lows.append(pts["C1"][0])
    ax.set_xlabel("Convergence: parser-accepted models (%)")
    ax.set_ylabel("LJS (mean, 95% bootstrap CI)")
    ax.set_xlim(left=np.floor(min(lows) - 2), right=101.5)
    ax.set_ylim(bottom=bottom - 0.06, top=top + 0.05)
    handles = [plt.Line2D([], [], marker="o", linestyle="", markeredgecolor=INK_2, markerfacecolor="white",
                          markeredgewidth=2, label="C1 (generation only)"),
               plt.Line2D([], [], marker="o", linestyle="", color=INK_2, label="C4 (full repair)")]
    ax.legend(handles=handles, fontsize=7, loc="upper left")
    save_figure(fig, path)


def pipeline_artifacts() -> None:
    print("Pipeline")
    df = load_phase(PIPELINE_DIR, "pipeline_results.csv")
    if df is None:
        return
    df, excluded = paired_only(df)
    tables, figures = PIPELINE_DIR / "tables", PIPELINE_DIR / "figures"
    models = model_order(df["llm"])
    g = (df.groupby(["llm", "condition"])
         .agg(conv=("converged", "mean"), init=("initial_errors", "mean"), final=("final_errors", "mean"),
              iters=("iterations", "mean"), rcs=("rcs", "mean"), srs=("srs", "mean"), ljs=("ljs", "mean"),
              cost=("cost_usd", "mean"), n=("category", "size"))
         .reset_index())
    g["conv"] *= 100

    rows = []
    for m in models:
        for c in CONDITION_ORDER:
            sel = g[(g.llm == m) & (g.condition == c)]
            if sel.empty:
                continue  # missing combinations are omitted, never filled with 0
            r = sel.iloc[0]
            rows.append([tex_escape(m), c, fmt(r.conv, 1), fmt(r.init, 2), fmt(r.final, 2), fmt(r.iters, 2),
                         fmt(r.ljs, 3), fmt(r.cost, 4)])
    write_table(tables / "tab_pipeline.tex",
                "Pipeline results per model and condition (means over categories and runs). LJS: see "
                "Table~\\ref{tab:pipeline_ljs}; Cost/cat is generation + repair only (USD).",
                "tab:pipeline", ["Model", "Cond.", "Conv.\\%", "Init. err", "Final err", "Iters", "LJS", "Cost/cat"],
                "llrrrrrr", rows, wide=True)

    dist = error_distribution(PIPELINE_DIR, df)

    # Cost per specification: best extraction once + number of categories x mean cost per category. With
    # every pair present this equals the mean over runs of the per-run total; with excluded pairs it neither
    # sums them as 0 nor drops the rest of their run.
    extraction_cost = read_json(BEST_REQUIREMENTS_PATH)["source"]["cost_usd"] if BEST_REQUIREMENTS_PATH.exists() else None
    c4 = df[df.condition == "C4"]
    n_categories = df.category.nunique()
    cost_rows, cost_spec = [], {}
    for m in model_order(c4["llm"]):
        sub = c4[c4.llm == m]
        per_spec = n_categories * sub.cost_usd.mean()
        spec_cost = per_spec + extraction_cost if extraction_cost is not None else None
        cost_spec[m] = spec_cost
        gen, rep = sub.generation_cost_usd.mean(), (sub.cost_usd - sub.generation_cost_usd).mean()
        cost_rows.append([tex_escape(m), fmt(sub.converged.mean() * 100, 1), fmt(gen, 4), fmt(rep, 4),
                          fmt(sub.cost_usd.mean(), 4), fmt(spec_cost, 2) if spec_cost is not None else "--"])
    if cost_rows:
        write_table(tables / "tab_cost.tex",
                    f"Cost under the full framework (C4), in USD. Gen./cat and Rep./cat: mean generation and repair "
                    f"cost per category; Cost/cat is their sum; Cost/spec: extraction of the input requirements "
                    f"(once) plus {n_categories} $\\times$ Cost/cat.",
                    "tab:cost", ["Model (C4)", "Conv.\\%", "Gen./cat", "Rep./cat", "Cost/cat", "Cost/spec"], "lrrrrr",
                    cost_rows)

    colors = model_colors(models)
    conds = [c for c in ("C1", "C4") if c in set(g.condition)]
    fig, ax = plt.subplots(figsize=(max(4.0, 1.1 * len(models) + 1.5), 3.2))
    width = 0.8 / max(1, len(conds))
    x = np.arange(len(models))
    for k, c in enumerate(conds):
        vals = [g[(g.llm == m) & (g.condition == c)].conv.iloc[0] if not g[(g.llm == m) & (g.condition == c)].empty
                else np.nan for m in models]
        bars = ax.bar(x + (k - (len(conds) - 1) / 2) * width, vals, width * 0.92, color=SERIES[k], label=c,
                      edgecolor="white", linewidth=1)
        for b, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}", ha="center", va="bottom", fontsize=7, color=INK_2)
    ax.set_xticks(x, models, rotation=20, ha="right")
    ax.set_ylabel("Convergence (%)")
    ax.set_ylim(0, 108)
    ax.grid(axis="x", visible=False)
    ax.legend(title="Condition", fontsize=8, title_fontsize=8, loc="lower right")
    save_figure(fig, figures / "fig_convergence.png")

    semantic_syntactic_figure(df, cost_spec, figures / "fig_semantic_syntactic.png")

    lines = []
    for m in models:
        parts = [f"{c} {g[(g.llm == m) & (g.condition == c)].conv.iloc[0]:.1f}%"
                 for c in CONDITION_ORDER if not g[(g.llm == m) & (g.condition == c)].empty]
        lines.append(f"- **{m}** convergence: " + ", ".join(parts))
    if dist is not None and len(dist):
        top = dist.head(2)
        lines.append("- Top error categories: " + ", ".join(f"{r.error_category} {r.share:.1f}%" for _, r in top.iterrows())
                     + f" (combined {top.share.sum():.1f}% of n = {int(dist['count'].sum())}).")
    c4g = g[g.condition == "C4"].sort_values("cost")
    if len(c4g) >= 2 and c4g.cost.iloc[0] > 0:
        lines.append(f"- C4 cost/cat ratio most/least expensive: {c4g.cost.iloc[-1] / c4g.cost.iloc[0]:.1f}x "
                     f"({c4g.llm.iloc[-1]} ${c4g.cost.iloc[-1]:.4f} vs {c4g.llm.iloc[0]} ${c4g.cost.iloc[0]:.4f}).")
    for m, v in cost_spec.items():
        if v is not None:
            lines.append(f"- Cost per specification (C4) {m}: ${v:.4f}")
    n_pairs = len(df[PAIR_KEYS].drop_duplicates())
    lines.append(f"- Paired comparison: n = {n_pairs} (model, run, category) pairs evaluated under every condition "
                 f"({', '.join(c for c in CONDITION_ORDER if c in set(df.condition))}).")
    excluded_pairs = excluded[PAIR_KEYS].drop_duplicates()
    if len(excluded_pairs):
        lines.append(f"- Excluded: {len(excluded_pairs)} pairs missing a condition (aborted runs), left out of every "
                     f"table and figure:")
        for _, r in excluded_pairs.iterrows():
            have = ", ".join(sorted(excluded[(excluded.llm == r.llm) & (excluded.run == r.run)
                                             & (excluded.category == r.category)].condition))
            lines.append(f"  - {r.llm}, run {r.run}, {r.category} (only {have})")
    lines += ljs_artifacts(df, tables, "pipeline")
    lines += errordist_by_model(df, tables)
    lines += repair_effort(df, tables)
    lines += model_tests(df, tables)
    models_code = load_models(PIPELINE_DIR)
    if models_code is not None and not df["ljs"].isna().all():
        lines += repair_semantics(df, models_code, tables, "pipeline")
        lines += rcs_literal(df, models_code, tables)
    shared = df.drop_duplicates(PAIR_KEYS)["generation_cost_usd"].sum()
    lines.append(f"- LLM spend (paired rows): shared generations ${shared:.2f} + repairs "
                 f"${(df.cost_usd - df.generation_cost_usd).sum():.2f}.")
    lines.append(f"- Sum of per-condition standalone costs (the shared generation counts in each condition): "
                 f"generation+repair ${df.cost_usd.sum():.4f}.")
    write_summary(PIPELINE_DIR / "summary.md", "Pipeline - key figures", lines)


# ---------------------------------------------------------------------------
# Ablation
# ---------------------------------------------------------------------------
def call_success(out_dir: Path, tables: Path, label: str) -> list[str]:
    """Share of repair calls that reduce the number of diagnostics, per model, condition and router category."""
    path = out_dir / "repairs.jsonl"
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    calls = pd.DataFrame([{"llm": r["llm"], "condition": r["condition"], "category": r["error_category"],
                           "success": len(r["errors_after"]) < len(r["errors_before"])} for r in rows])
    if calls.empty:
        return []
    cats = calls.category.value_counts().index[:3].tolist()  # most frequent categories
    out, lines = [], []
    for m in model_order(calls["llm"]):
        for c in [c for c in CONDITION_ORDER if c in set(calls[calls.llm == m].condition)]:
            sub = calls[(calls.llm == m) & (calls.condition == c)]
            cells = []
            for cat in cats:
                k = sub[sub.category == cat]
                cells.append(f"{int(k.success.sum())}/{len(k)} ({k.success.mean() * 100:.0f})" if len(k) else "--")
            out.append([tex_escape(m), c, f"{int(sub.success.sum())}/{len(sub)} ({sub.success.mean() * 100:.0f})"]
                       + cells)
            lines.append(f"- Call success {m} {c}: {sub.success.mean() * 100:.1f}% of {len(sub)} repair calls; "
                         + ", ".join(f"{cat} {sub[sub.category == cat].success.mean() * 100:.1f}% "
                                     f"(n = {len(sub[sub.category == cat])})" for cat in cats
                                     if len(sub[sub.category == cat])))
    write_table(tables / f"tab_{label}_call_success.tex",
                "Repair calls that reduce the number of diagnostics: successful/total (\\%), overall and for the most "
                "frequent router categories of the diagnostic being repaired.",
                f"tab:{label}_call_success", ["Model", "Cond.", "All calls"] + [pretty_category(c) for c in cats],
                "ll" + "r" * (1 + len(cats)), out)
    return lines


def bank_source(tables: Path) -> list[str]:
    """Validity of the earlier-prompt generations of every model: why the bank uses the models it uses."""
    src = load_csv(ABLATION_STRESS_DIR / "source_validity.csv")
    if src is None:
        return []
    src["valid"] = as_bool(src["valid"])
    rows, lines = [], []
    for m in model_order(src["llm"]):
        x = src[src.llm == m]
        invalid = int((~x.valid).sum())
        rows.append([tex_escape(m), f"{invalid}/{len(x)}", fmt(x.valid.mean() * 100, 1), str(int(x.errors.sum()))])
        lines.append(f"- Earlier prompt {m}: {invalid}/{len(x)} invalid generations, {int(x.errors.sum())} diagnostics")
    write_table(tables / "tab_bank_source.tex",
                "Generations of the earlier prompt (all four models, same requirements), validated with the current "
                "validator. The error bank of E3 takes the two models with the most invalid generations.",
                "tab:bank_source", ["Model", "Invalid", "Conv.\\% (C1)", "Diagnostics"], "lrrr", rows)
    return lines


def prompt_effect(bank: pd.DataFrame, tables: Path) -> list[str]:
    """Single-shot validity and LJS with the original prompt (error bank, C1) vs the corrected one (pipeline, C1).

    Same models and requirements; paired by (run, category).
    """
    pipe = load_phase(PIPELINE_DIR, "pipeline_results.csv")
    if pipe is None:
        return []
    keys = ["llm", "run", "category"]
    old = bank[bank.condition == "C1"][keys + ["converged", "ljs"]]
    new = pipe[pipe.condition == "C1"][keys + ["converged", "ljs"]]
    both = old.merge(new, on=keys, suffixes=("_v1", "_v2"))
    rows, lines = [], []
    for m in model_order(both["llm"]):
        b = both[both.llm == m]
        p_conv = mcnemar_exact(b.converged_v1.astype(bool), b.converged_v2.astype(bool))
        ok = b.dropna(subset=["ljs_v1", "ljs_v2"])
        p_ljs = wilcoxon_p(ok.ljs_v1, ok.ljs_v2) if len(ok) > 1 else np.nan
        rows.append([tex_escape(m), str(len(b)), fmt(b.converged_v1.mean() * 100, 1), fmt(b.converged_v2.mean() * 100, 1),
                     fmt_p(p_conv), fmt(ok.ljs_v1.mean(), 3), fmt(ok.ljs_v2.mean(), 3), fmt_p(p_ljs)])
        lines.append(f"- Prompt effect {m}: C1 convergence {b.converged_v1.mean() * 100:.1f}% -> "
                     f"{b.converged_v2.mean() * 100:.1f}% (McNemar p = {p_conv:.2g}); LJS {ok.ljs_v1.mean():.3f} -> "
                     f"{ok.ljs_v2.mean():.3f} (Wilcoxon p = {p_ljs:.2g}), n = {len(b)}")
    write_table(tables / "tab_prompt_effect.tex",
                "Single-shot generation (C1) with the original generation prompt (error bank) and with the corrected "
                "one (pipeline): same models and requirements, paired by (run, category). Convergence: exact McNemar "
                "test; LJS: Wilcoxon signed-rank test.",
                "tab:prompt_effect", ["Model", "n", "Conv.\\% v1", "Conv.\\% v2", "$p$", "LJS v1", "LJS v2", "$p$"],
                "lrrrrrrr", rows)
    return lines


def ablation_artifacts(out_dir: Path = ABLATION_DIR, label: str = "ablation", title: str = "Ablation") -> None:
    """Tables, figures and summary of a C1-C4 ablation phase (regular ablation or the error bank)."""
    print(title)
    df = load_phase(out_dir, "ablation_results.csv")
    if df is None:
        return
    tables, figures = out_dir / "tables", out_dir / "figures"
    multi_model = df["llm"].nunique() > 1
    df["repair_calls"] = df["llm_calls"] - 1
    df["repair_cost"] = df["cost_usd"] - df["generation_cost_usd"]
    stats = []
    for m in model_order(df["llm"]):
        for c in CONDITION_ORDER:
            sub = df[(df.llm == m) & (df.condition == c)]
            if sub.empty:
                continue
            # Paired design: every condition starts from the same generation, so "broken" is the same set.
            broken = sub[sub.initial_errors >= 1]
            repairs = CONDITIONS_REPAIR.get(c, True) and len(broken) > 0
            stats.append({
                "llm": m, "condition": c, "n": len(sub), "n_broken": len(broken),
                "conv": sub.converged.mean() * 100,
                "rescued": broken.converged.mean() * 100 if len(broken) else np.nan,
                "err_red": broken.error_reduction_pct.mean() if len(broken) else np.nan,
                "iters_broken": broken.iterations.mean() if repairs else np.nan,
                "calls_broken": broken.repair_calls.mean() if repairs else np.nan,
                "cost_broken": broken.repair_cost.mean() if repairs else np.nan,
                "iters": sub.iterations.mean(), "stag": sub.stagnation.mean() * 100,
            })
    st = pd.DataFrame(stats)
    models_txt = ", ".join(model_order(df["llm"]))
    n_broken = int(st.n_broken.max()) if len(st) else 0
    n_total = int(st.n.max()) if len(st) else 0
    dash = lambda v, d: fmt(v, d) or "--"  # noqa: E731
    rows = [([tex_escape(r.llm)] if multi_model else []) + [
        r.condition, str(int(r.n_broken)), fmt(r.conv, 1), dash(r.rescued, 1), dash(r.err_red, 1), dash(r.iters_broken, 2),
        dash(r.calls_broken, 1), dash(r.cost_broken, 4), fmt(r.stag, 1)] for _, r in st.iterrows()]
    write_table(tables / "tab_ablation.tex",
                f"Repair-loop ablation ({models_txt}; paired design: all conditions repair the same generated "
                f"models). Invalid: generations with at least one initial validation error. Conv.\\% over all "
                f"{n_total} category evaluations per model; the remaining columns (except Stagn.\\%) over the invalid "
                f"generations. Repair cost in USD per invalid generation.",
                f"tab:{label}", (["Model"] if multi_model else []) + [
                    "Cond.", "Invalid", "Conv.\\%", "Rescued\\%", "Err. red.\\%", "Iters", "Repair calls", "Repair cost",
                    "Stagn.\\%"],
                ("l" if multi_model else "") + "lrrrrrrrr", rows, wide=True)

    # Paired tests on the invalid generations (same code repaired by each condition): exact McNemar on
    # rescue, Wilcoxon signed-rank on iterations, repair calls and repair cost.
    test_rows, test_lines = [], []
    for m in model_order(df["llm"]):
        model_rows, model_p = [], []
        broken = df[(df.llm == m) & (df.initial_errors >= 1)]
        metrics = (("converged", "Rescued (\\%)", 100.0, 1), ("iterations", "Iterations", 1.0, 2),
                   ("repair_calls", "Repair calls", 1.0, 2), ("repair_cost", "Repair cost (USD)", 1.0, 4))
        for metric, name, scale, digits in metrics:
            wide = broken.pivot_table(index=["run", "category"], columns="condition", values=metric, aggfunc="first")
            for a, b in (("C2", "C3"), ("C2", "C4"), ("C3", "C4")):
                if a not in wide or b not in wide:
                    continue
                pair = wide[[a, b]].dropna()
                if metric == "converged":
                    first, second = pair[a].astype(bool), pair[b].astype(bool)
                    p_value = mcnemar_exact(first, second)
                    lower, higher = int((first & ~second).sum()), int((~first & second).sum())
                    counts = f"{higher}/{lower}/{len(pair) - lower - higher}"  # second better / worse / tie
                else:
                    diff = pair[b] - pair[a]
                    p_value = wilcoxon_p(pair[a], pair[b])
                    counts = f"{int((diff < 0).sum())}/{int((diff > 0).sum())}/{int((diff == 0).sum())}"
                model_p.append(p_value)
                model_rows.append(([tex_escape(m)] if multi_model else []) + [
                    name, f"{a} $\\rightarrow$ {b}", str(len(pair)), fmt(pair[a].mean() * scale, digits),
                    fmt(pair[b].mean() * scale, digits), counts, fmt_p(p_value)])
                test_lines.append(f"- {m} {name} {a} -> {b}: {pair[a].mean() * scale:.{digits}f} -> "
                                  f"{pair[b].mean() * scale:.{digits}f} ({counts}, p = {p_value:.3g}, n = {len(pair)})")
        # Holm correction over the model's family of tests (3 comparisons x 4 metrics).
        test_rows += [row + [fmt_p(p_holm)] for row, p_holm in zip(model_rows, holm(model_p))]
    if test_rows:
        write_table(tables / "tab_ablation_tests.tex",
                    "Paired comparison of the repair conditions on the invalid generations. Comparison A "
                    "$\\rightarrow$ B: Mean (from) is the mean under A, Mean (to) under B. Better/worse/tie: number of "
                    "generations in which the condition after the arrow is better (rescues a generation the other does "
                    "not, or needs fewer iterations, calls or cost), worse, or equal. Rescue: exact McNemar test; other "
                    "metrics: Wilcoxon signed-rank test. $p_{\\mathrm{Holm}}$: Holm-adjusted over each model's twelve "
                    "tests.",
                    f"tab:{label}_tests", (["Model"] if multi_model else []) + [
                        "Metric", "Comparison", "n", "Mean (from)", "Mean (to)", "Better/worse/tie", "$p$",
                        "$p_{\\mathrm{Holm}}$"],
                    ("l" if multi_model else "") + "llrrrrrr", test_rows)

    models = model_order(df["llm"])
    fig, axes = plt.subplots(1, len(models), figsize=(4.4 * len(models), 3.2), squeeze=False)
    for ax, m in zip(axes[0], models):
        sm = st[st.llm == m]
        x = np.arange(len(sm))
        for k, (col, name) in enumerate((("conv", "Convergence (all)"), ("rescued", "Rescued (≥1 initial error)"))):
            bars = ax.bar(x + (k - 0.5) * 0.4, sm[col], 0.37, color=SERIES[k], label=name, edgecolor="white",
                          linewidth=1)
            for b, v in zip(bars, sm[col]):
                if not np.isnan(v):
                    ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}", ha="center", va="bottom", fontsize=7,
                            color=INK_2)
        ax.set_xticks(x, sm.condition)
        ax.set_ylabel("%")
        ax.set_ylim(0, 125)
        ax.grid(axis="x", visible=False)
        ax.set_title(m, color=INK)
        ax.legend(fontsize=7, loc="upper left", ncol=2)
    save_figure(fig, figures / "fig_ablation_ladder.png")

    trace = load_csv(out_dir / "iteration_trace.csv")
    if trace is not None:
        fig, axes = plt.subplots(1, len(models), figsize=(4.4 * len(models), 3.2), squeeze=False)
        for ax, m in zip(axes[0], models):
            plotted = False
            for k, c in enumerate(["C2", "C3", "C4"]):
                sub = trace[(trace.llm == m) & (trace.condition == c)]
                if sub.empty:
                    continue
                wide = sub.pivot_table(index=["run", "category"], columns="iteration", values="error_count",
                                       aggfunc="last")
                wide = wide[wide[0] >= 1] if 0 in wide.columns else wide
                if wide.empty:
                    continue
                wide = wide.reindex(columns=range(int(wide.columns.max()) + 1)).ffill(axis=1)  # carry final count
                mean = wide.mean(axis=0)
                ax.plot(mean.index, mean.values, color=SERIES[k + 1], linewidth=2, marker="o", markersize=4,
                        label=f"{c} (n={len(wide)})")
                plotted = True
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
            ax.set_xlabel("Repair iteration (0 = after generation)")
            ax.set_ylabel("Mean validation errors")
            ax.set_title(f"{m} - generations with ≥1 initial error", color=INK, fontsize=9)
            if plotted:
                ax.legend(fontsize=7)
        save_figure(fig, figures / "fig_iteration_trajectory.png")

    lines = [f"- Model: {models_txt}. Paired design: each condition repairs the same generated models."]
    for _, r in st.iterrows():
        repair_txt = (f"; on invalid generations: iters {r.iters_broken:.2f}, repair calls {r.calls_broken:.1f}, "
                      f"repair cost ${r.cost_broken:.4f}" if not np.isnan(r.iters_broken) else "")
        lines.append(f"- {r.llm} {r.condition}: convergence {pct(r.conv)}, rescued "
                     f"{pct(r.rescued) if not np.isnan(r.rescued) else 'n/a'} of {r.n_broken} invalid, "
                     f"stagnation {pct(r.stag)}{repair_txt}; n = {r.n} category evaluations.")
    lines += test_lines
    dist = error_distribution(out_dir)
    if dist is not None and len(dist):
        top = dist.head(2)
        lines.append("- Top error categories: " + ", ".join(f"{r.error_category} {r.share:.1f}%" for _, r in top.iterrows())
                     + f" (n = {int(dist['count'].sum())}).")
    shared = df.drop_duplicates(["llm", "run", "category"])["generation_cost_usd"].sum()
    repairs = (df["cost_usd"] - df["generation_cost_usd"]).sum()
    lines.append(f"- LLM spend: shared generations ${shared:.4f} + repairs ${repairs:.4f}.")
    guard = df[df.condition != "C1"].groupby("condition")[["guard_retries", "guard_rejections"]].sum() \
        if "guard_retries" in df else None
    if guard is not None:
        lines.append("- Content guard (retries/rejections): " + ", ".join(
            f"{c} {int(r.guard_retries)}/{int(r.guard_rejections)}" for c, r in guard.iterrows()))
    lines += errordist_by_model(df, tables, out_dir, f"{label}_errordist")
    lines += call_success(out_dir, tables, label)
    if out_dir == ABLATION_STRESS_DIR:
        lines += prompt_effect(df, tables)
        lines += bank_source(tables)
    lines += ljs_artifacts(df, tables, label)
    models_code = load_models(out_dir)
    if models_code is not None:
        lines += repair_semantics(df, models_code, tables, label)
    write_summary(out_dir / "summary.md", f"{title} - key figures", lines)


def main() -> None:
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    require_study_results()
    extraction_artifacts()
    pipeline_artifacts()
    ablation_artifacts()
    ablation_artifacts(ABLATION_STRESS_DIR, "ablation_stress", "Ablation on the error bank")


if __name__ == "__main__":
    main()
