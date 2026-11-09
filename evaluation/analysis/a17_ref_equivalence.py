"""A17 (no LLM calls). Do A::x and the feature chain A.x of rewriting (b) resolve to the same element?

In SysML v2, A::x is a qualified name (x looked up in the namespace of A) and A.x a feature chain (the feature x
reached through the usage A), so the rewriting (b) of the reference stage could change the referenced element. For every
reference rewritten by the extended (b) of A15 in the final models of R11 (results/pilot_repair), both versions of
the model are linked by the Pilot Implementation (tools/pilot/PilotRefDump.java) and the element of the qualified
name before the rewriting is compared with the last element reached by A.x after it (a feature chain, a feature
chain expression inside an expression, or a flow end that redefines x). Releases 2024-04.1 (where A::x only raises a
warning) and 2026-08 (where A::x no longer resolves, so the chain is compared with the element of A::x in 2024-04.1).

    python -m evaluation.analysis.a17_ref_equivalence
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.a01b_boilerplate import sha20
from evaluation.analysis.a15_extended_b import _QUAL_RE, fix_references
from evaluation.analysis.common import jsonl, md_table, model_sort, out_dir, write_md

SRC = RESULTS_DIR / "pilot_repair"
DOC = {"E1": "EIRENE", "E5": "JWST"}
COLS = ["id", "line", "text", "eclass", "reference", "chain", "index", "proxy", "target"]


def rewritten_refs(before: str, after: str) -> list[tuple[int, str, list[str]]]:
    """(line, original reference, segments) of every reference that the rewriting turned into a chain."""
    refs = []
    for n, (b, a) in enumerate(zip(before.split("\n"), after.split("\n")), start=1):
        if a == b:
            continue
        shift = 0
        for m in _QUAL_RE.finditer(b):
            orig = m.group(0)
            new = re.sub(r"\s*::\s*", ".", orig)
            if a[m.start() + shift:m.start() + shift + len(new)] == new:
                refs.append((n, orig, re.split(r"\s*::\s*", orig)))
                shift += len(new) - len(orig)
    return refs


def dump(pilot_root: Path, release: str, work: Path, texts: dict[str, str], shards: int) -> pd.DataFrame:
    base = work / release
    base.mkdir(parents=True, exist_ok=True)
    cache = base / "refs.tsv"
    cache.touch()
    done = {l.split("\t")[0] for l in cache.read_text(encoding="utf-8").splitlines() if l.endswith("\tDONE")}
    todo = sorted((s, t) for s, t in texts.items() if s not in done)
    if todo:
        sysml = pilot_root / release / "sysml"
        from core.validate.pilot import pilot_jar

        jar = pilot_jar(sysml)
        classes = Path(__file__).resolve().parents[2] / "tools" / "pilot" / "build" / release
        if not (classes / "PilotRefDump.class").exists():
            classes.mkdir(parents=True, exist_ok=True)
            subprocess.run(["javac", "-cp", str(jar), "-d", str(classes),
                            str(Path(__file__).resolve().parents[2] / "tools" / "pilot" / "PilotRefDump.java")],
                           check=True)
        print(f"  Pilot {release}: {len(todo)} new texts ({len(texts) - len(todo)} cached), {shards} JVMs", flush=True)
        procs, parts = [], []
        for k in range(shards):
            src = base / f"in_{k}"
            src.mkdir(parents=True, exist_ok=True)
            for f in src.glob("*.sysml"):
                f.unlink()
            for s, t in todo[k::shards]:
                (src / f"{s}.sysml").write_text(t, encoding="utf-8")
            part = base / f"part_{k}.tsv"
            parts.append(part)
            procs.append(subprocess.Popen(["java", "-Xmx1500m", "-cp", f"{jar}:{classes}", "PilotRefDump",
                                           str(sysml / "sysml.library") + "/", str(src), str(part)],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        for p in procs:
            p.wait()
        with cache.open("a", encoding="utf-8") as fh:  # keep only completed files of each part
            for part in parts:
                if part.exists():
                    lines = part.read_text(encoding="utf-8").splitlines()
                    ok = {l.split("\t")[0] for l in lines if l.endswith("\tDONE")}
                    fh.write("".join(l + "\n" for l in lines if l.split("\t")[0] in ok))
                    part.unlink()
    rows = [l.split("\t") for l in cache.read_text(encoding="utf-8").splitlines()]
    df = pd.DataFrame([r for r in rows if len(r) == len(COLS)], columns=COLS)
    return df.assign(line=df.line.astype(int), proxy=df.proxy == "1")


def compare(refs: pd.DataFrame, d: pd.DataFrame) -> pd.DataFrame:
    d = d.assign(norm=d.text.str.replace(r"\s+", "", regex=True))
    plain = d[d.eclass != "FeatureChaining"].groupby(["id", "line", "norm"])
    chains = (d[d.eclass == "FeatureChaining"].assign(index=lambda x: x["index"].astype(int))
              .sort_values(["id", "chain", "index"])
              .groupby(["id", "line", "chain"]).agg(texts=("norm", tuple), targets=("target", tuple),
                                                    proxy=("proxy", "any")).reset_index())
    chain_of = {}
    for c in chains.itertuples():
        chain_of.setdefault((c.id, c.line, c.texts), []).append(c)
    # Other forms of A.x: inside an expression, a FeatureChainExpression (memberships A, x); as a flow end, a
    # reference subsetting of A with a redefinition of x. Consecutive references on the line, in dump order.
    for (i, line), g in d.groupby(["id", "line"], sort=False):
        texts, targets, proxies = list(g.norm), list(g.target), list(g.proxy)
        for start in range(len(texts)):
            for end in range(start + 2, min(start + 6, len(texts)) + 1):
                c = pd.Series({"targets": tuple(targets[start:end]), "proxy": any(proxies[start:end])})
                chain_of.setdefault((i, line, tuple(texts[start:end])), []).append(c)
    out = []
    for r in refs.itertuples():
        key = (r.sha_before, r.line, re.sub(r"\s+", "", r.ref))
        before = plain.get_group(key) if key in plain.groups else None
        cs = chain_of.get((r.sha_after, r.line, tuple(re.sub(r"\s+", "", s) for s in r.segments)), [])
        b_targets = set() if before is None else set(before[~before.proxy].target)
        a_targets = {c.targets[-1] for c in cs if not c.proxy}
        if before is None or not b_targets:
            verdict = "qualified name not resolved"
        elif not a_targets:
            verdict = "chain not resolved"
        elif b_targets & a_targets:
            verdict = "same element"
        else:
            verdict = "different element"
        out.append({"verdict": verdict, "target_before": "; ".join(sorted(b_targets)),
                    "target_after": "; ".join(sorted(a_targets))})
    return pd.concat([refs.reset_index(drop=True), pd.DataFrame(out)], axis=1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pilot-root", type=Path, default=Path.home() / "tools" / "pilot")
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work_a17")
    parser.add_argument("--shards", type=int, default=5)
    args = parser.parse_args()
    out = out_dir("a17_ref_equivalence")

    rows = {}
    for m in jsonl(SRC / "sysml_models.jsonl"):
        rows[(m["set"], m["llm"], int(m["run"]), m["category"])] = m
    refs, texts = [], {}
    for (s, llm, run, cat), m in rows.items():
        before = m["sysml_code"]
        after = fix_references(before)
        if after == before:
            continue
        sb, sa = sha20(before), sha20(after)
        texts[sb], texts[sa] = before, after
        for line, ref, segments in rewritten_refs(before, after):
            refs.append({"set": s, "document": DOC[s], "llm": llm, "run": run, "category": cat, "line": line,
                         "ref": ref, "segments": segments, "sha_before": sb, "sha_after": sa})
    refs = pd.DataFrame(refs)
    print(f"{len(refs)} rewritten references in {refs.sha_before.nunique()} models")

    per_release = []
    for release in ("2024-04.1", "2026-08"):
        res = compare(refs, dump(args.pilot_root, release, args.work, texts, args.shards)).assign(release=release)
        per_release.append(res)
    res = pd.concat(per_release, ignore_index=True)
    res.drop(columns=["segments", "sha_before", "sha_after"]).to_csv(out / "references.csv", index=False)

    summary = (res.groupby(["release", "document", "llm", "verdict"]).size().unstack("verdict", fill_value=0)
               .reset_index())
    order = {m: i for i, m in enumerate(model_sort(summary.llm))}
    summary = summary.sort_values(["release", "document", "llm"], key=lambda c: c.map(order) if c.name == "llm" else c)
    summary.to_csv(out / "summary.csv", index=False)
    total = res.groupby(["release", "verdict"]).size().unstack("verdict", fill_value=0).reset_index()
    # In 2026-08 the qualified name no longer resolves: compare the chain with the element of A::x in 2024-04.1.
    old, new = per_release
    both = (old.verdict == "same element") & (new.target_after != "")
    cross = pd.DataFrame([{"references same in 2024-04.1": int((old.verdict == "same element").sum()),
                           "chain resolved in 2026-08": int(both.sum()),
                           "same element as A::x in 2024-04.1": int((both & (new.target_after == old.target_before)).sum())}])
    cross.to_csv(out / "cross_release.csv", index=False)
    examples = res[res.verdict != "same element"].groupby(["release", "verdict"]).head(5)
    write_md(out / "summary.md", "A17. Do A::x and A.x resolve to the same element?", [
        f"References rewritten by the extended (b): {len(refs)} in {refs.sha_before.nunique()} models of R11.",
        "## Verdicts per release", md_table(total),
        "## Chain in 2026-08 against the qualified name in 2024-04.1", md_table(cross),
        "## Per document and model", md_table(summary),
        "## Examples that are not the same element",
        md_table(examples[["release", "set", "llm", "category", "line", "ref", "verdict", "target_before",
                           "target_after"]]) if len(examples) else "None."])
    print(total.to_string(index=False))


if __name__ == "__main__":
    main()
