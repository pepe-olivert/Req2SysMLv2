"""R11 analysis (no LLM calls): the C4P repair loop with the Pilot Implementation as validator.

Reads results/pilot_repair/ (run_pilot_repair) and writes results/analysis/r11_pilot_repair/:
- acceptance with the Pilot 2024-04.1 before and after the loop, and with 2026-08 after it, with and without the
  deterministic rewriting (b) of connector ends A::p -> A.p (A1b);
- iterations, calls, cost, stagnation and guard interventions;
- line diff with respect to the input model (as in A3);
- elements before and after: requirement, part, attribute, constraint, satisfy, interface usages, interface
  definitions, and effective connections (interface usages with ends + connect statements);
- the LJS without doc comments before and after, paired, for gpt-4o-mini and claude-haiku-5.5 (when judged);
- the error types that remain after the loop;
- ten random cases (seed 0) where an interface usage becomes an interface definition, for manual review;
- the paper table tab:pilot_repair.

    python -m evaluation.analysis.r11_pilot_repair
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.a01b_boilerplate import fix_connect, run_texts, sha20
from evaluation.analysis.a01_tool_acceptance import parse_issues
from evaluation.analysis.a03_repair_diff import line_diff
from evaluation.analysis.common import fmt, jsonl, md_table, model_sort, out_dir, tex, write_md, write_paper_table
from evaluation.make_paper_artifacts import wilcoxon_p

SRC = RESULTS_DIR / "pilot_repair"
DOC = {"E1": "EIRENE", "E5": "JWST"}
_COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.DOTALL)
NAME = r"(?:'[^']+'|[A-Za-z_]\w*)"
BEFORE_LJS = {("E1", "gpt-4o-mini"): "nodoc_control/pipeline_c4/ljs/gpt-4o-mini",
              ("E1", "claude-haiku-5.5"): "nodoc_control/pipeline_c4/ljs/claude-haiku-5.5",
              ("E5", "gpt-4o-mini"): "nodoc_control/jwst_pipeline_c4/ljs/gpt-4o-mini",
              ("E5", "claude-haiku-5.5"): "nodoc_control/jwst_pipeline_c4/ljs/claude-haiku-5.5"}
AFTER_LJS = {j: f"pilot_repair/nodoc/ljs/{j}" for j in ("gpt-4o-mini", "claude-haiku-5.5")}


def elements(code: str) -> dict:
    body = _COMMENT_RE.sub("", code)
    lines = body.splitlines()
    n = lambda pat: sum(1 for l in lines if re.search(pat, l))  # noqa: E731
    iface_usage = [i for i, l in enumerate(lines) if re.match(rf"\s*(?:\w+\s+)*interface\s+(?!def\b)", l)]
    with_ends = 0
    for i in iface_usage:
        tail = "\n".join(lines[i:i + 8])
        if re.search(r"\bconnect\b", lines[i]) or re.search(r"\bend\b", tail.split("}")[0]):
            with_ends += 1
    connects = sum(1 for i, l in enumerate(lines) if re.search(r"\bconnect\b", l) and i not in iface_usage)
    return {"requirement": n(r"\brequirement\b"), "part": n(r"\bpart\b"), "attribute": n(r"\battribute\b"),
            "constraint": n(r"\bconstraint\b"), "satisfy": n(r"\bsatisfy\b"), "interface_usage": len(iface_usage),
            "interface_usage_with_ends": with_ends, "interface_def": n(r"\binterface\s+def\b"),
            "connect": connects, "effective_connections": connects + with_ends}


def interface_def_cases(models: pd.DataFrame, k: int = 10, seed: int = 0) -> list[dict]:
    cases = []
    for r in models.itertuples():
        for m in re.finditer(rf"(?m)^\s*(?:\w+\s+)*interface\s+(?!def\b)({NAME})", r.input_code):
            name = m.group(1)
            if re.search(rf"\binterface\s+def\s+{re.escape(name)}\b", r.sysml_code) and \
                    not re.search(rf"\binterface\s+def\s+{re.escape(name)}\b", r.input_code):
                cases.append((r, name))
    random.Random(seed).shuffle(cases)
    out = []
    for r, name in cases[:k]:
        def block(code: str, start_pat: str) -> str:
            lines = code.splitlines()
            i = next((i for i, l in enumerate(lines) if re.search(start_pat, l)), None)
            if i is None:
                return ""
            j, depth = i, 0
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                j += 1
                if depth <= 0:
                    break
            return "\n".join(lines[i:j])
        esc = re.escape(name)
        before = block(r.input_code, rf"\binterface\s+(?!def\b){esc}\b")
        after = block(r.sysml_code, rf"\binterface\s+def\s+{esc}\b")
        uses_after = [l.strip() for l in r.sysml_code.splitlines()
                      if re.search(rf"\b{esc}\b", l) and not re.search(rf"\binterface\s+def\s+{esc}\b", l)]
        typed_with_ends = [l for l in uses_after if re.search(r"\bconnect\b|\bend\b", l)]
        connects_after = [l.strip() for l in _COMMENT_RE.sub("", r.sysml_code).splitlines()
                          if re.search(r"\bconnect\b", l) and not l.strip().startswith("doc")]
        words = {w.lower() for w in re.findall(r"[A-Z]?[a-z]+", name) if len(w) > 3}
        flows = re.findall(r"\bflow\s+(\w+)", before)
        words |= {w.lower() for f in flows for w in re.findall(r"[A-Z]?[a-z]+", f) if len(w) > 3}
        reqs = sorted(r.requirements, key=lambda t: -len(words & set(re.findall(r"[a-z]+", t.lower()))))[:2]
        sat = [l.strip() for l in r.input_code.splitlines() if re.search(rf"\bsatisfy\b.*\b{esc}\b", l)]
        out.append({"set": r.set, "llm": r.llm, "run": r.run, "category": r.category, "interface": name,
                    "before": before, "after": after, "uses_after": uses_after[:6],
                    "typed_usages_with_ends_after": typed_with_ends, "connects_after": connects_after[:8],
                    "related_requirements": reqs, "satisfy_mentioning_interface": sat})
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pilot-root", type=Path, default=Path.home() / "tools" / "pilot")
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work_r11")
    parser.add_argument("--shards", type=int, default=4)
    args = parser.parse_args()
    out = out_dir("r11_pilot_repair")

    res = pd.read_csv(SRC / "pilot_repair_results.csv")
    res["converged"] = res.converged.astype(str).str.lower() == "true"
    res["stagnation"] = res.stagnation.astype(str).str.lower() == "true"
    rows = {}
    for m in jsonl(SRC / "sysml_models.jsonl"):
        rows[(m["set"], m["llm"], int(m["run"]), m["category"])] = m
    models = pd.DataFrame([{**{k: m[k] for k in ("set", "pdf", "llm", "category", "input_code", "sysml_code",
                                                 "requirements")}, "run": int(m["run"])} for m in rows.values()])
    df = res.merge(models, on=["set", "pdf", "llm", "run", "category"])
    df["document"] = df.set.map(DOC)
    df["changed"] = df.input_code != df.sysml_code
    df["accepted_2024_before"] = df.pilot_initial_errors == 0
    df["accepted_2024_after"] = df.pilot_final_errors == 0

    # 2026-08 after the loop, as repaired and with (b).
    texts = {}
    for c in df.sysml_code:
        texts[sha20(c)] = c
        texts[sha20(fix_connect(c))] = fix_connect(c)
    cache = args.work / "2026-08" / "cache.tsv"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    run_texts(args.pilot_root, "2026-08", args.work, texts, args.shards)
    issues = parse_issues(cache, set())
    errs = issues[issues.group.isin(["syntax", "name_library", "name_other", "validation", "exception"])]
    bad = set(errs.sha)
    df["accepted_2026_after"] = ~df.sysml_code.map(sha20).isin(bad)
    df["accepted_2026_after_b"] = ~df.sysml_code.map(lambda c: sha20(fix_connect(c))).isin(bad)

    # Errors that remain with 2026-08 after the loop and (b), per model.
    sha_b = {sha20(fix_connect(c)): llm for c, llm in zip(df.sysml_code, df.llm)}
    e26 = errs[errs.sha.isin(sha_b)].assign(llm=lambda x: x.sha.map(sha_b))
    e26_types = (e26.groupby(["llm", "group", "code"]).agg(models=("sha", "nunique"),
                                                          example=("message", "first"))
                 .reset_index().sort_values(["llm", "models"], ascending=[True, False]))
    e26_types.to_csv(out / "remaining_2026_after_b.csv", index=False)

    # Diff and elements.
    d = pd.DataFrame([line_diff(a, b) for a, b in zip(df.input_code, df.sysml_code)])
    df[["lines_before", "added", "deleted", "modified", "unchanged_pct"]] = d[["lines_before", "added", "deleted",
                                                                               "modified", "unchanged_pct"]]
    df["changed_lines"] = df.added + df.deleted + df.modified
    eb = pd.DataFrame([elements(c) for c in df.input_code]).add_suffix("_before")
    ea = pd.DataFrame([elements(c) for c in df.sysml_code]).add_suffix("_after")
    df = pd.concat([df.reset_index(drop=True), eb, ea], axis=1)
    df.drop(columns=["input_code", "sysml_code", "requirements"]).to_csv(out / "per_model.csv", index=False)

    g = df.groupby(["document", "llm"])
    summ = g.agg(n=("category", "size"), accepted_2024_before=("accepted_2024_before", "mean"),
                 accepted_2024_after=("accepted_2024_after", "mean"), accepted_2026_after=("accepted_2026_after", "mean"),
                 accepted_2026_after_b=("accepted_2026_after_b", "mean"), repaired=("changed", "sum"),
                 iterations_mean=("iterations", "mean"), calls_mean=("llm_calls", "mean"), cost_total=("cost_usd", "sum"),
                 stagnation=("stagnation", "sum"), guard_retries_antlr=("guard_retries_antlr", "sum"),
                 guard_rejections_antlr=("guard_rejections_antlr", "sum"),
                 guard_retries_content=("guard_retries_content", "sum"),
                 guard_rejections_content=("guard_rejections_content", "sum")).reset_index()
    for c in ("accepted_2024_before", "accepted_2024_after", "accepted_2026_after", "accepted_2026_after_b"):
        summ[c] = (summ[c] * 100).round(1)
    rep = df[df.pilot_initial_errors > 0]
    calls = rep.groupby(["document", "llm"]).agg(calls_per_repaired=("llm_calls", "mean"),
                                                 iterations_per_repaired=("iterations", "mean"),
                                                 cost_per_repaired=("cost_usd", "mean"),
                                                 changed_median=("changed_lines", "median"),
                                                 changed_p90=("changed_lines", lambda s: np.percentile(s, 90)),
                                                 changed_max=("changed_lines", "max"),
                                                 unchanged_median=("unchanged_pct", "median"),
                                                 unchanged_min=("unchanged_pct", "min")).reset_index()
    summ = summ.merge(calls, on=["document", "llm"], how="left")
    summ.to_csv(out / "summary_by_model.csv", index=False)
    el_cols = ["requirement", "part", "attribute", "constraint", "satisfy", "interface_usage",
               "interface_usage_with_ends", "interface_def", "connect", "effective_connections"]
    el = df.groupby(["document", "llm"])[[f"{c}_{w}" for c in el_cols for w in ("before", "after")]].sum().reset_index()
    el.to_csv(out / "elements.csv", index=False)
    lost = df[[f"{c}_after" for c in el_cols]].values < df[[f"{c}_before" for c in el_cols]].values
    df_lost = pd.DataFrame(lost, columns=el_cols).sum().rename("models_with_fewer").reset_index()
    df_lost.to_csv(out / "models_with_fewer_elements.csv", index=False)

    # Remaining error types after the loop (2024-04.1, from the loop's last validation).
    remaining = []
    for m in rows.values():
        for e in m.get("pilot_final_errors", []):
            remaining.append({"document": DOC[m["set"]], "llm": m["llm"], "code": e["pilot_code"],
                              "message": re.sub(r"'[^']*'", "'...'", e["error"])[:80], "category": m["category"],
                              "line": e["line"]})
    rem = pd.DataFrame(remaining, columns=["document", "llm", "code", "message", "category", "line"])
    rem_types = rem.groupby(["code", "message"]).agg(models=("category", "size"), example_category=("category", "first")) \
        .reset_index().sort_values("models", ascending=False) if len(rem) else rem
    rem_types.to_csv(out / "remaining_error_types.csv", index=False)

    # LJS without doc, before and after (paired); unchanged models keep their before value.
    ljs_rows = []
    for judge in ("gpt-4o-mini", "claude-haiku-5.5"):
        after = RESULTS_DIR / AFTER_LJS[judge] / "ljs_results.csv"
        a = pd.read_csv(after) if after.exists() else None
        for s in ("E1", "E5"):
            b = pd.read_csv(RESULTS_DIR / BEFORE_LJS[(s, judge)] / "ljs_results.csv")
            sub = df[df.set == s][["pdf", "llm", "run", "category", "changed"]]
            m = sub.merge(b[b.condition == "C4"][["pdf", "llm", "run", "category", "ljs"]], on=["pdf", "llm", "run",
                                                                                                 "category"])
            m = m.rename(columns={"ljs": "ljs_before"})
            if a is not None:
                m = m.merge(a[["pdf", "llm", "run", "category", "ljs"]].rename(columns={"ljs": "ljs_after_judged"}),
                            on=["pdf", "llm", "run", "category"], how="left")
                m["ljs_after"] = np.where(m.changed, m.ljs_after_judged, m.ljs_before)
            else:
                m["ljs_after"] = np.where(m.changed, np.nan, m.ljs_before)
            for llm, g2 in m.groupby("llm"):
                pair = g2.dropna(subset=["ljs_before", "ljs_after"])
                ch = pair[pair.changed]
                ljs_rows.append({"judge": judge, "document": DOC[s], "llm": llm, "n_pairs": len(pair),
                                 "n_changed_pairs": len(ch), "ljs_before": pair.ljs_before.mean() if len(pair) else np.nan,
                                 "ljs_after": pair.ljs_after.mean() if len(pair) else np.nan,
                                 "delta_changed": (ch.ljs_after - ch.ljs_before).mean() if len(ch) else np.nan,
                                 "p_changed": wilcoxon_p(ch.ljs_before, ch.ljs_after) if len(ch) > 1 else np.nan,
                                 "changed_not_judged": int(g2.changed.sum() - len(ch))})
        # Pooled paired test over every judged changed model of the judge (the whole haiku sample).
        pooled = []
        for s in ("E1", "E5"):
            b = pd.read_csv(RESULTS_DIR / BEFORE_LJS[(s, judge)] / "ljs_results.csv")
            if a is None:
                continue
            m = (df[(df.set == s) & df.changed][["pdf", "llm", "run", "category"]]
                 .merge(b[b.condition == "C4"][["pdf", "llm", "run", "category", "ljs"]], on=["pdf", "llm", "run", "category"])
                 .merge(a[["pdf", "llm", "run", "category", "ljs"]], on=["pdf", "llm", "run", "category"],
                        suffixes=("_before", "_after")).dropna())
            pooled.append(m)
        if pooled:
            m = pd.concat(pooled)
            ljs_rows.append({"judge": judge, "document": "all", "llm": "all (changed models judged)", "n_pairs": len(m),
                             "n_changed_pairs": len(m), "ljs_before": m.ljs_before.mean(), "ljs_after": m.ljs_after.mean(),
                             "delta_changed": (m.ljs_after - m.ljs_before).mean(),
                             "p_changed": wilcoxon_p(m.ljs_before, m.ljs_after), "changed_not_judged": np.nan})
    ljs = pd.DataFrame(ljs_rows)
    ljs.to_csv(out / "ljs_before_after.csv", index=False)

    # Interface usage -> definition cases.
    cases = interface_def_cases(df)
    md_cases = []
    for i, c in enumerate(cases, 1):
        md_cases.append(
            f"## Case {i}: {c['set']} {c['llm']} run {c['run']}, {c['category']} — interface `{c['interface']}`\n\n"
            f"Before:\n```\n{c['before']}\n```\nAfter:\n```\n{c['after']}\n```\n"
            f"Other lines naming `{c['interface']}` after the repair: "
            + ("; ".join(f"`{u}`" for u in c["uses_after"]) or "none") + "\n\n"
            f"Usages of it with ends after the repair: "
            + ("; ".join(f"`{u}`" for u in c["typed_usages_with_ends_after"]) or "**none**") + "\n\n"
            f"connect statements in the repaired model ({len(c['connects_after'])} shown, at most 8): "
            + ("; ".join(f"`{u}`" for u in c["connects_after"]) or "none") + "\n\n"
            f"satisfy relations naming the interface (before): "
            + ("; ".join(f"`{u}`" for u in c["satisfy_mentioning_interface"]) or "none") + "\n\n"
            "Requirements closest to the interface (word overlap with its name and flows; check by hand):\n"
            + "\n".join(f"- {t}" for t in c["related_requirements"]) + "\n\n"
            "Still models a connection between the parts involved? _to be judged by hand_: the interface usage had no "
            "ends, so it never connected parts; after the change, a connection exists only if a usage of the new "
            "definition with ends, or a connect between the parts that own its flows, appears above.")
    write_md(out / "interface_def_cases.md", "R11: interface usages turned into interface definitions (10 random "
             "cases, seed 0)", [f"Candidates: {len([1 for _ in interface_def_cases(df, k=10**6)])}."] + md_cases)

    # Paper table (with the extended rewriting of A15, when computed).
    a15_path = RESULTS_DIR / "analysis" / "a15_extended_b" / "acceptance.csv"
    a15 = pd.read_csv(a15_path) if a15_path.exists() else None
    trows = []
    for doc in ("EIRENE", "JWST"):
        for llm in model_sort(summ[summ.document == doc].llm):
            r = summ[(summ.document == doc) & (summ.llm == llm)].iloc[0]
            e = el[(el.document == doc) & (el.llm == llm)].iloc[0]
            lj = ljs[(ljs.document == doc) & (ljs.llm == llm)]
            lj_o, lj_h = lj[lj.judge == "gpt-4o-mini"], lj[lj.judge == "claude-haiku-5.5"]
            ljs_cell = lambda x: (f"{fmt(x.ljs_before.iloc[0], 3)} $\\rightarrow$ {fmt(x.ljs_after.iloc[0], 3)}"  # noqa: E731
                                  if len(x) and not np.isnan(x.ljs_after.iloc[0]) else "")
            trows.append([doc, tex(llm), str(int(r.n)), fmt(r.accepted_2024_before), fmt(r.accepted_2024_after),
                          fmt(r.accepted_2026_after), fmt(r.accepted_2026_after_b),
                          fmt(a15[(a15.document == doc) & (a15.llm == llm)]["2026-08_b_extended"].iloc[0])
                          if a15 is not None else "", fmt(r.calls_per_repaired, 2),
                          fmt(r.cost_per_repaired, 4), fmt(r.unchanged_median, 1),
                          f"{int(e.interface_usage_before)} $\\rightarrow$ {int(e.interface_usage_after)}",
                          f"{int(e.effective_connections_before)} $\\rightarrow$ {int(e.effective_connections_after)}",
                          ljs_cell(lj_o), ljs_cell(lj_h)])
    write_paper_table(
        out / "tab_pilot_repair.tex",
        "Repair with the SysML v2 Pilot Implementation (release 2024-04.1) as validator (C4P: the loop of "
        "Algorithm 1, one diagnostic per call, no router and no knowledge base, guard on content and on ANTLR "
        "validity), applied to the final C4 models after adding the standard-library imports. Acceptance (\\% of "
        "models without errors) before and after the loop with 2024-04.1, and after it with 2026-08 as repaired, "
        "with connector ends \\texttt{A::p} rewritten as \\texttt{A.p} (+b), and with every reference "
        "\\texttt{A::x} to a feature of a usage \\texttt{A} rewritten as \\texttt{A.x} (+b ext.). Calls and cost: per repaired model; "
        "Unch.: median share of lines kept. Interface usages and effective connections (interface usages with ends "
        "plus \\texttt{connect} statements), summed over the models. LJS without doc comments before $\\rightarrow$ "
        "after (gpt-4o-mini on every changed model; claude-haiku-5.5 on a stratified random sample of 150 changed "
        "models, seed 0; unchanged models keep their value).",
        "tab:pilot_repair", ["Doc.", "Model", "n", "Acc. before", "Acc. after", "26-08", "26-08 +b",
                             "26-08 +b ext.", "Calls", "Cost", "Unch. \\%", "Iface usages", "Eff. conn.",
                             "LJS 4o-mini", "LJS haiku"],
        "llrrrrrrrrrllll", trows, wide=True)
    write_md(out / "summary.md", "R11. Repair with the Pilot Implementation as validator (C4P)",
             [md_table(summ), "## Elements before/after (sums)", md_table(el),
              "## Models with fewer elements after the loop", md_table(df_lost),
              "## Remaining Pilot errors after the loop (2024-04.1)", md_table(rem_types),
              "## Errors with 2026-08 after the loop and (b), per model", md_table(e26_types.groupby("llm").head(6)),
              "## LJS without doc, before/after", md_table(ljs)])


if __name__ == "__main__":
    main()
