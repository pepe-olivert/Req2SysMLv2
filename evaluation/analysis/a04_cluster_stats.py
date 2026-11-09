"""A4. Statistics that respect the dependence between runs of the same category.

The three runs of a category share its requirements, so (run, category) blocks are not independent. This script
recomputes the model comparisons of E1 (EIRENE) and E5 (JWST) in three ways:

- block tests (as in the paper): exact McNemar (convergence) or Wilcoxon signed-rank (LJS, cost), paired by
  (run, category), Holm over the 6 model pairs of each metric;
- cluster bootstrap: 5000 resamples of categories with replacement (all runs of a drawn category kept), 95%
  percentile CI of each model mean and of each pairwise difference, two-sided bootstrap p, Holm over the pairs;
- linear mixed model with a random intercept per category and the run as fixed effect (statsmodels MixedLM,
  REML), for the LJS and log(cost); Wald tests of the pairwise contrasts, Holm over the pairs.

Metrics: C1 convergence, C4 LJS for each judge with and without doc comments, C4 cost per category.

    python -m evaluation.analysis.a04_cluster_stats
"""

from __future__ import annotations

import itertools
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm

from evaluation.analysis.common import (KEYS, MODEL_ORDER, fmt, fmt_p, load_ljs, load_results, md_table, out_dir,
                                        tex, write_long_table, write_md, write_paper_table)
from evaluation.make_paper_artifacts import holm, mcnemar_exact, wilcoxon_p

B = 5000
SEED = 0
LJS_DIRS = {
    "E1": {"LJS gpt-4o-mini": "pipeline/ljs/gpt-4o-mini",
           "LJS gpt-4o-mini no-doc": "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
           "LJS haiku-5.5": "second_judge/pipeline_c4/ljs/claude-haiku-5.5",
           "LJS haiku-5.5 no-doc": "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5"},
    "E5": {"LJS gpt-4o-mini": "jwst_pipeline/ljs/gpt-4o-mini",
           "LJS gpt-4o-mini no-doc": "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
           "LJS haiku-5.5 no-doc": "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"},
}


def metric_frames(name: str) -> dict[str, pd.DataFrame]:
    res = load_results(name)
    frames = {
        "Convergence C1": res[res.condition == "C1"].assign(value=lambda d: d.converged.astype(float)),
        "Cost/cat C4 (USD)": res[res.condition == "C4"].assign(value=lambda d: d.cost_usd),
    }
    for metric, judge_dir in LJS_DIRS[name].items():
        lj = load_ljs(judge_dir)
        lj = lj[lj.condition == "C4"]
        frames[metric] = res[res.condition == "C4"][KEYS].merge(lj[KEYS + ["ljs"]], on=KEYS).rename(
            columns={"ljs": "value"})
    return {k: v[["llm", "run", "category", "value"]].dropna() for k, v in frames.items()}


def cluster_bootstrap(df: pd.DataFrame, models: list[str], rng) -> np.ndarray:
    """B x models matrix of model means over resampled categories."""
    cats = sorted(df.category.unique())
    idx = {c: i for i, c in enumerate(cats)}
    sums = np.zeros((len(cats), len(models)))
    counts = np.zeros((len(cats), len(models)))
    for j, m in enumerate(models):
        g = df[df.llm == m].groupby("category").value.agg(["sum", "count"])
        for c, row in g.iterrows():
            sums[idx[c], j], counts[idx[c], j] = row["sum"], row["count"]
    draws = rng.integers(0, len(cats), size=(B, len(cats)))
    s, n = sums[draws].sum(axis=1), counts[draws].sum(axis=1)
    with np.errstate(invalid="ignore"):
        return s / n


def block_test(df: pd.DataFrame, a: str, b: str, binary: bool) -> float:
    w = df.pivot_table(index=["run", "category"], columns="llm", values="value", aggfunc="first")[[a, b]].dropna()
    return mcnemar_exact(w[a].astype(bool), w[b].astype(bool)) if binary else wilcoxon_p(w[a], w[b])


def mixed_pairs(df: pd.DataFrame, models: list[str], log: bool) -> dict[tuple[str, str], tuple[float, float]]:
    d = df.copy()
    if log:
        d["value"] = np.log(d.value)
    d["llm"] = pd.Categorical(d.llm, categories=models)
    d["run"] = d.run.astype(str)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = smf.mixedlm("value ~ C(llm) + C(run)", d, groups=d["category"]).fit(reml=True)
    names = {m: (f"C(llm)[T.{m}]" if i else None) for i, m in enumerate(models)}
    cov = fit.cov_params()
    out = {}
    for a, b in itertools.combinations(models, 2):
        vec = pd.Series(0.0, index=fit.params.index)
        if names[a]:
            vec[names[a]] += 1
        if names[b]:
            vec[names[b]] -= 1
        est = float(vec @ fit.params)
        se = float(np.sqrt(vec @ cov.loc[vec.index, vec.index] @ vec))
        out[(a, b)] = (est, float(2 * norm.sf(abs(est / se))))
    return out


def main() -> None:
    out = out_dir("a04_cluster_stats")
    rng = np.random.default_rng(SEED)
    mean_rows, pair_rows = [], []
    for name, doc in (("E1", "EIRENE"), ("E5", "JWST")):
        for metric, df in metric_frames(name).items():
            models = [m for m in MODEL_ORDER if m in set(df.llm)]
            boot = cluster_bootstrap(df, models, rng)
            for j, m in enumerate(models):
                sub = df[df.llm == m].value
                lo, hi = np.nanpercentile(boot[:, j], [2.5, 97.5])
                mean_rows.append({"document": doc, "metric": metric, "llm": m, "n": len(sub), "mean": sub.mean(),
                                  "ci_low": lo, "ci_high": hi})
            binary = metric.startswith("Convergence")
            mixed = None if binary else mixed_pairs(df, models, log=metric.startswith("Cost"))
            rows = []
            for (ia, a), (ib, b) in itertools.combinations(enumerate(models), 2):
                diff = boot[:, ia] - boot[:, ib]
                p_boot = float(min(1.0, 2 * min((diff <= 0).mean(), (diff >= 0).mean())))
                lo, hi = np.nanpercentile(diff, [2.5, 97.5])
                rows.append({"document": doc, "metric": metric, "a": a, "b": b,
                             "diff": df[df.llm == a].value.mean() - df[df.llm == b].value.mean(),
                             "p_block": block_test(df, a, b, binary), "boot_ci_low": lo, "boot_ci_high": hi,
                             "p_cluster": p_boot,
                             "mixed_est": mixed[(a, b)][0] if mixed else np.nan,
                             "p_mixed": mixed[(a, b)][1] if mixed else np.nan})
            for key in ("p_block", "p_cluster", "p_mixed"):
                for r, ph in zip(rows, holm([r[key] for r in rows])):
                    r[key + "_holm"] = ph
            pair_rows += rows
    means = pd.DataFrame(mean_rows)
    pairs = pd.DataFrame(pair_rows)
    sig = lambda p: (not np.isnan(p)) and p < 0.05  # noqa: E731
    pairs["sig_block"] = pairs.p_block_holm.map(sig)
    pairs["sig_cluster"] = pairs.p_cluster_holm.map(sig)
    pairs["sig_mixed"] = pairs.p_mixed_holm.map(sig)
    pairs["conclusion_changes"] = (pairs.sig_block != pairs.sig_cluster) | (
        pairs.p_mixed_holm.notna() & (pairs.sig_block != pairs.sig_mixed))
    means.to_csv(out / "model_means_cluster_ci.csv", index=False)
    pairs.to_csv(out / "pairwise_tests.csv", index=False)

    digits = lambda metric: 4 if metric.startswith("Cost") else 3  # noqa: E731
    scale = lambda metric: 100.0 if metric.startswith("Convergence") else 1.0  # noqa: E731
    mrows = []
    for doc in ("EIRENE", "JWST"):
        sub = means[means.document == doc]
        for metric in sub.metric.unique():
            cells = []
            for m in MODEL_ORDER:
                r = sub[(sub.metric == metric) & (sub.llm == m)]
                if r.empty:
                    cells.append("")
                    continue
                r = r.iloc[0]
                s, d = scale(metric), digits(metric) if not metric.startswith("Convergence") else 1
                cells.append(f"{fmt(r['mean'] * s, d)} [{fmt(r.ci_low * s, d)}, {fmt(r.ci_high * s, d)}]")
            mrows.append([doc, tex(metric.replace("Convergence C1", "Convergence C1 (\\%)"))] + cells)
    write_paper_table(
        out / "tab_cluster_means.tex",
        "Model means with 95\\% cluster-bootstrap confidence intervals (5000 resamples of categories; the three "
        "runs of a category are kept together). LJS and cost under C4; convergence without repair (C1).",
        "tab:cluster_means", ["Document", "Metric", *[tex(m) for m in MODEL_ORDER]], "llrrrr", mrows, wide=True)

    prow = []
    for r in pairs.itertuples():
        d = digits(r.metric)
        s = scale(r.metric)
        prow.append([r.document, tex(r.metric), f"{tex(r.a)} -- {tex(r.b)}", fmt(r.diff * s, d),
                     fmt_p(r.p_block_holm), f"[{fmt(r.boot_ci_low * s, d)}, {fmt(r.boot_ci_high * s, d)}]",
                     fmt_p(r.p_cluster_holm), fmt_p(r.p_mixed_holm), "yes" if r.conclusion_changes else ""])
    write_long_table(
        out / "tab_cluster_tests.tex",
        "Pairwise model comparisons with and without the dependence between runs. Block: exact McNemar "
        "(convergence) or Wilcoxon signed-rank test paired by (run, category), as in the paper. Cluster: bootstrap "
        "of categories (95\\% CI of the difference and two-sided $p$). Mixed: linear mixed model with a random "
        "intercept per category and the run as fixed effect (LJS; log cost), Wald test of the contrast. All $p$ "
        "Holm-adjusted over the six pairs of each metric. Changes: the significance at 0.05 differs from the "
        "block test.",
        "tab:cluster_tests", ["Document", "Metric", "Pair", "Diff.", "$p$ block", "Cluster 95\\% CI",
                              "$p$ cluster", "$p$ mixed", "Changes"], "lllrrrrrl", prow)

    changed = pairs[pairs.conclusion_changes]
    write_md(out / "summary.md", "A4. Statistics with dependence between runs",
             [md_table(means), "## Pairwise tests", md_table(pairs.drop(columns=["sig_block", "sig_cluster",
                                                                                  "sig_mixed"])),
              "## Pairs whose conclusion changes", md_table(changed[["document", "metric", "a", "b", "diff",
                                                                     "p_block_holm", "p_cluster_holm",
                                                                     "p_mixed_holm"]])])


if __name__ == "__main__":
    main()
