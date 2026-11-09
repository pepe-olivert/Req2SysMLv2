"""A1. Acceptance by the SysML v2 Pilot Implementation (name resolution, typing and validation).

Validates every stored final model (E1/E5 C1 and C4, C0, and the repaired banks E3, R9, R9b under every
condition) with two releases of the Pilot Implementation: 2024-04.1 (the grammar of our ANTLR validator) and
2026-08. Each distinct code is validated once per release, in its own resource (tools/pilot/PilotBatch.java),
in two variants:

- as stored;
- with `private import ScalarValues::*; private import ISQ::*; private import SI::*;` inserted right after the
  `{` of every top-level package (same line, so line numbers do not move). It separates "the model only lacks
  the standard-library imports" from real naming and typing errors.

Issues are split into syntax (parser/lexer), names (Xtext linking: unresolved references), and validation (the
SysML validator: typing and other semantic rules). Unresolved names are split into standard-library names
(declared somewhere in sysml.library) and other names. A model is accepted when it has no ERROR issue.
A satisfy relation resolves when its line has no linking error (only for models without syntax errors).

    python -m evaluation.analysis.a01_tool_acceptance --pilot-root ~/tools/pilot
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

import pandas as pd

from evaluation.analysis.common import (CONDITION_ORDER, fmt, load_models, model_sort, out_dir, tex, write_md,
                                        md_table, write_paper_table)

RELEASES = ["2024-04.1", "2026-08"]
SETS_CONDITIONS = {  # set -> conditions validated
    "E1": ["C1", "C4"], "E5": ["C1", "C4"], "E4": ["C1"], "E5C0": ["C1"],
    "E3": ["C1", "C2", "C3", "C4"], "E3rev": ["C2KB", "FULLREV"],
    "R9": ["C1", "C2", "C2KB", "C3", "C4", "FULLREV"], "R9b": ["C1", "C2", "C2KB", "C4", "FULLREV"],
}
_PACKAGE_RE = re.compile(r"(?:(?:library|standard)\s+)*package\b")
IMPORTS = " private import ScalarValues::*; private import ISQ::*; private import SI::*;"
_LINK_RE = re.compile(r"Couldn't resolve reference to (\w+) '([^']*)'")
_DECL_RE = re.compile(r"\b(?:def|abstract|attribute|part|item|enum|calc|constraint|requirement|port|action|state|"
                      r"occurrence|metadata|datatype|struct|class|feature|function|predicate|type|classifier|"
                      r"alias|package|library|standard|interaction|behavior|connector|binding|succession|flow|"
                      r"view|viewpoint|rendering|concern|case|analysis|verification|allocation|interface|"
                      r"connection|individual|snapshot|timeslice|ref|in|out|inout|return|subject|actor|stakeholder)"
                      r"\s+(?:def\s+)?(?:<'?([\w ]+?)'?>\s*)?'?([A-Za-z_][\w ]*?)'?(?=\s*[;:{<\[(=,]|\s+(?::>|:|"
                      r"specializes|subsets|redefines|references|defined|typed|ordered|nonunique))")


def with_imports(code: str) -> str:
    """Inserts the library imports after the '{' of every top-level package (brace depth 0)."""
    out, depth, i, n = [], 0, 0, len(code)
    pending_package = False
    while i < n:
        if code.startswith("/*", i):
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(code[i:j]); i = j; continue
        if code.startswith("//", i):
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append(code[i:j]); i = j; continue
        ch = code[i]
        if ch in "\"'":
            j = i + 1
            while j < n and code[j] != ch:
                j += 2 if code[j] == "\\" else 1
            out.append(code[i:j + 1]); i = j + 1; continue
        if depth == 0 and _PACKAGE_RE.match(code, i) and (i == 0 or not (code[i - 1].isalnum() or code[i - 1] == "_")):
            pending_package = True
        if ch == "{":
            out.append(ch)
            if depth == 0 and pending_package:
                out.append(IMPORTS)
                pending_package = False
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1); out.append(ch)
        elif ch == ";" and depth == 0:
            pending_package = False; out.append(ch)
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def library_names(library: Path) -> set[str]:
    names = set()
    for f in library.rglob("*.*ml"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in _DECL_RE.finditer(text):
            for g in m.groups():
                if g:
                    names.add(g.strip())
    return names


def run_pilot(pilot_root: Path, release: str, work: Path, variant: str, codes: dict[str, str],
              shards: int = 2) -> Path:
    """Validates `codes` with one release, split into `shards` JVMs run in parallel; returns the merged TSV."""
    base = work / release / variant
    tsv = base / "issues.tsv"
    if tsv.exists():
        done = {line.split("\t")[0] for line in tsv.read_text(encoding="utf-8").splitlines() if "\tDONE\t" in line}
        if set(codes) <= done:
            return tsv
    sysml = pilot_root / release / "sysml"
    from core.validate.pilot import pilot_jar

    jar = pilot_jar(sysml)
    classes = Path(__file__).resolve().parents[2] / "tools" / "pilot" / "build" / release
    if not (classes / "PilotBatch.class").exists():
        classes.mkdir(parents=True, exist_ok=True)
        subprocess.run(["javac", "-cp", str(jar), "-d", str(classes),
                        str(Path(__file__).resolve().parents[2] / "tools" / "pilot" / "PilotBatch.java")], check=True)
    # Resume: keep every file already validated by an earlier (interrupted) invocation.
    import shutil
    import time

    prev = base / "previous.tsv"
    kept = prev.read_text(encoding="utf-8") if prev.exists() else ""
    for part in sorted(base.glob("issues_*.tsv")):
        text = part.read_text(encoding="utf-8")
        done = {line.split("\t")[0] for line in text.splitlines() if "\tDONE\t" in line}
        kept += "".join(line + "\n" for line in text.splitlines() if line.split("\t")[0] in done)
        part.unlink()
    prev.write_text(kept, encoding="utf-8")
    done = {line.split("\t")[0] for line in kept.splitlines() if "\tDONE\t" in line}
    for d in base.glob("in_*"):
        shutil.rmtree(d)
    items = sorted((sha, code) for sha, code in codes.items() if sha not in done)
    procs, outs = [], [prev]
    for k in range(shards):
        src = base / f"in_{k}"
        src.mkdir(parents=True, exist_ok=True)
        for sha, code in items[k::shards]:
            (src / f"{sha}.sysml").write_text(with_imports(code) if variant == "imports" else code, encoding="utf-8")
        part = base / f"issues_{k}.tsv"
        outs.append(part)
        procs.append(subprocess.Popen(["java", "-Xmx1500m", "-cp", f"{jar}:{classes}", "PilotBatch",
                                       str(sysml / "sysml.library") + "/", str(src), str(part)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    print(f"  Pilot {release} ({variant}): {len(items)} of {len(codes)} models left, {shards} JVMs ...", flush=True)
    for proc in procs:
        if proc.wait() != 0:
            raise RuntimeError(f"PilotBatch failed for {release} {variant}")
    tsv.write_text("".join(part.read_text(encoding="utf-8") for part in outs), encoding="utf-8")
    prev.unlink()
    return tsv


def parse_issues(tsv: Path, lib: set[str]) -> pd.DataFrame:
    rows = []
    for line in tsv.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) < 6 or parts[1] == "DONE":
            continue
        sha, kind, severity, code, line_no, message = parts[:6]
        if kind == "EXCEPTION":
            group = "exception"
        elif severity != "ERROR":
            group = "warning"
        elif kind == "SYNTAX":
            group = "syntax"
        elif code.endswith("Diagnostic.Linking"):
            m = _LINK_RE.search(message)
            name = (m.group(2) if m else "").split("::")[-1].strip("'")
            group = "name_library" if name in lib else "name_other"
        else:
            group = "validation"
        rows.append({"sha": sha, "group": group, "code": code, "line": int(line_no) if line_no.isdigit() else None,
                     "message": message})
    return pd.DataFrame(rows, columns=["sha", "group", "code", "line", "message"])


def per_model(issues: pd.DataFrame, shas: list[str]) -> pd.DataFrame:
    counts = issues[issues.group != "warning"].pivot_table(index="sha", columns="group", values="code",
                                                           aggfunc="count", fill_value=0)
    counts = counts.reindex(shas, fill_value=0)
    for g in ("syntax", "name_library", "name_other", "validation", "exception"):
        if g not in counts:
            counts[g] = 0
    counts["accepted"] = counts[["syntax", "name_library", "name_other", "validation", "exception"]].sum(axis=1) == 0
    return counts.reset_index()


def satisfy_resolution(models: pd.DataFrame, issues: pd.DataFrame) -> pd.DataFrame:
    """Per model: satisfy statements and how many have no linking error on their line (no syntax errors only)."""
    link_lines = issues[issues.group.isin(["name_library", "name_other"])].groupby("sha")["line"].apply(set).to_dict()
    syntax = set(issues[issues.group == "syntax"].sha)
    rows = []
    for r in models.drop_duplicates("sha").itertuples():
        if r.sha in syntax:
            continue
        lines = [i + 1 for i, text in enumerate(r.sysml_code.splitlines()) if re.search(r"\bsatisfy\b", text)
                 and not text.strip().startswith(("//", "/*", "doc"))]
        bad = link_lines.get(r.sha, set())
        rows.append({"sha": r.sha, "satisfy": len(lines), "satisfy_resolved": sum(1 for x in lines if x not in bad)})
    return pd.DataFrame(rows, columns=["sha", "satisfy", "satisfy_resolved"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pilot-root", type=Path, default=Path.home() / "tools" / "pilot",
                        help="Directory with one unpacked jupyter-sysml-kernel release per subdirectory.")
    parser.add_argument("--shards", type=int, default=2, help="JVMs per release and variant (~0.7-1.5 GB each).")
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work",
                        help="Scratch directory for the .sysml inputs and the raw issue lists.")
    args = parser.parse_args()
    out = out_dir("a01_tool_acceptance")

    frames = []
    for name, conditions in SETS_CONDITIONS.items():
        m = load_models(name)
        frames.append(m[m.condition.isin(conditions)])
    models = pd.concat(frames, ignore_index=True)
    models["sha"] = models.sysml_code.map(lambda c: hashlib.sha256(c.encode("utf-8")).hexdigest()[:20])
    codes = dict(zip(models.sha, models.sysml_code))
    models["antlr_valid"] = models.valid.astype(bool)  # stored by the run: same ANTLR validator
    print(f"{len(models)} rows, {len(codes)} distinct models")

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as pool:  # 4 passes x 2 JVMs (about 1.5 GB each)
        list(pool.map(lambda rv: run_pilot(args.pilot_root, rv[0], args.work, rv[1], codes, shards=args.shards),
                      [(r, v) for r in RELEASES for v in ("as_stored", "imports")]))

    summary_rows, satisfy_rows, all_counts = [], [], []
    for release in RELEASES:
        lib = library_names(args.pilot_root / release / "sysml" / "sysml.library")
        for variant in ("as_stored", "imports"):
            tsv = run_pilot(args.pilot_root, release, args.work, variant, codes)
            issues = parse_issues(tsv, lib)
            issues.to_csv(out / f"issues_{release}_{variant}.csv.gz", index=False, compression="gzip")
            counts = per_model(issues, list(codes))
            m = models.merge(counts, on="sha", how="left")
            m["release"], m["variant"] = release, variant
            all_counts.append(m.drop(columns=["requirements", "sysml_code", "generated_code"]))
            if variant == "as_stored":
                sat = satisfy_resolution(models, issues)
                ms = models.merge(sat, on="sha")
                g = ms.groupby(["set", "llm", "condition"])[["satisfy", "satisfy_resolved"]].sum().reset_index()
                g["release"] = release
                satisfy_rows.append(g)
    per_row = pd.concat(all_counts, ignore_index=True)
    per_row.to_csv(out / "acceptance_per_model.csv.gz", index=False, compression="gzip")

    agg = (per_row.groupby(["set", "document", "llm", "condition", "release", "variant"])
           .agg(n=("sha", "size"), antlr_valid=("antlr_valid", "mean"), accepted=("accepted", "mean"),
                with_syntax=("syntax", lambda s: (s > 0).mean()),
                with_name_library=("name_library", lambda s: (s > 0).mean()),
                with_name_other=("name_other", lambda s: (s > 0).mean()),
                with_validation=("validation", lambda s: (s > 0).mean()),
                exceptions=("exception", lambda s: (s > 0).sum()))
           .reset_index())
    for c in ("antlr_valid", "accepted", "with_syntax", "with_name_library", "with_name_other", "with_validation"):
        agg[c] = (agg[c] * 100).round(1)
    agg.to_csv(out / "acceptance.csv", index=False)
    sat = pd.concat(satisfy_rows, ignore_index=True)
    sat["resolved_pct"] = (sat.satisfy_resolved / sat.satisfy.where(sat.satisfy > 0) * 100).round(1)
    sat.to_csv(out / "satisfy_resolution.csv", index=False)

    # Most frequent remaining issues after adding the imports (what is really wrong).
    top = []
    for release in RELEASES:
        issues = pd.read_csv(out / f"issues_{release}_imports.csv.gz")
        issues = issues[issues.group.isin(["syntax", "name_other", "name_library", "validation"])]
        issues["what"] = issues.apply(lambda r: r.code if r.group == "validation" else (
            _LINK_RE.sub(r"unresolved \1", r.message) if r.group.startswith("name") else r.message[:60]), axis=1)
        t = issues.groupby(["group", "what"]).sha.nunique().sort_values(ascending=False).head(15).rename("models")
        top.append(t.reset_index().assign(release=release))
    top_df = pd.concat(top)
    top_df.to_csv(out / "top_issues_with_imports.csv", index=False)

    # Paper table: final models (C4 for E1/E5/banks; C1 for C0), per set and model, both releases, as stored and
    # with imports.
    final = agg[((agg.condition == "C4") & agg.set.isin(["E1", "E5", "E3", "R9", "R9b"]))
                | (agg.set.isin(["E4", "E5C0"]) & (agg.condition == "C1"))]
    order = {"E1": 0, "E4": 1, "E3": 2, "E5": 3, "E5C0": 4, "R9": 5, "R9b": 6}
    labels = {"E1": "E1 (EIRENE)", "E4": "C0 (EIRENE)", "E3": "E3 bank, C4", "E5": "E5 (JWST)",
              "E5C0": "C0 (JWST)", "R9": "JWST bank, C4", "R9b": "JWST bank, C4"}
    rows = []
    for s in sorted(final.set.unique(), key=order.get):
        for llm in model_sort(final[final.set == s].llm):
            sel = lambda rel, var: final[(final.set == s) & (final.llm == llm) & (final.release == rel)  # noqa: E731
                                         & (final.variant == var)].iloc[0]
            a, b, ai, bi = sel("2024-04.1", "as_stored"), sel("2026-08", "as_stored"), sel("2024-04.1", "imports"), \
                sel("2026-08", "imports")
            srow = sat[(sat.set == s) & (sat.llm == llm) & (sat.condition == a.condition) & (sat.release == "2024-04.1")]
            rows.append([labels[s], tex(llm), str(int(a.n)), fmt(a.antlr_valid), fmt(a.accepted), fmt(b.accepted),
                         fmt(a.with_name_library), fmt(ai.accepted), fmt(bi.accepted), fmt(ai.with_name_other),
                         fmt(ai.with_validation), fmt(srow.resolved_pct.iloc[0]) if len(srow) else ""])
    write_paper_table(
        out / "tab_tool_acceptance_detail.tex",
        "Acceptance of the final models by the SysML v2 Pilot Implementation (releases 2024-04.1 and 2026-08), with "
        "name resolution and validation. ANTLR: valid for our parser. Accepted: no error. Lib. names: models with "
        "an unresolved standard-library name (e.g. \\texttt{Real}, \\texttt{String}), i.e. a missing import. "
        "+imports: the same models with \\texttt{ScalarValues}, \\texttt{ISQ} and \\texttt{SI} imported in every "
        "top-level package; Names and Valid. are the models that still have an unresolved name or a validation "
        "(typing) error under 2024-04.1. Satisfy: \\% of \\texttt{satisfy} relations whose references resolve "
        "(models without syntax errors, 2024-04.1). All values in \\%.",
        "tab:tool_acceptance_detail",
        ["Set", "Model", "n", "ANTLR", "Acc. 24-04", "Acc. 26-08", "Lib. names", "+imp. 24-04", "+imp. 26-08",
         "Names", "Valid.", "Satisfy"],
        "llrrrrrrrrrr", rows, wide=True)

    iss = pd.read_csv(out / "issues_2024-04.1_imports.csv.gz")
    conn = iss[iss.code == "validateConnectorRelatedFeatures"]
    keyword = lambda r: (re.match(r"\s*(\w+)", with_imports(codes[r.sha]).splitlines()[int(r.line) - 1])  # noqa: E731
                         or [None, "?"])[1] if pd.notna(r.line) and int(r.line) <= len(codes[r.sha].splitlines()) else "?"
    conn_kw = conn.apply(keyword, axis=1).value_counts()
    iface = int(conn_kw.get("interface", 0))
    i26 = pd.read_csv(out / "issues_2026-08_as_stored.csv.gz")
    plain = set(i26[i26.message.str.contains("mismatched input 'import'", na=False)].sha)
    plain_by_model = models[models.sha.isin(plain)].drop_duplicates("sha").llm.value_counts().to_dict()
    notes = (
        "## Main causes\n\n"
        f"- validateConnectorRelatedFeatures ('Must have at least two related elements'): {conn.sha.nunique()} distinct "
        f"models under 2024-04.1 even with the library imports; {iface} of its {len(conn)} issues are on "
        "`interface <Name> {` lines, i.e. interface usages declared without ends, as in the frozen prompt template "
        "`interface <InterfaceName> { flow ... }` (core/agents/agent2/prompts.py). It is not caused by the connector "
        "ends (see A1b).\n"
        "- Connector ends written `A::p` (the prompt template `connect <PartName>::<PortA> to <PartName>::<PortB>`) "
        "raise 'Should be an accessible feature (use dot notation for nesting)': a warning in 2024-04.1 and an error "
        "in 2026-08 (A1b).\n"
        "- Library types: most guided models use `Real`, `String`, `Integer`, `Boolean` without importing "
        "ScalarValues; gpt-6.1-sol usually writes `import ScalarValues::*;`.\n"
        f"- 2026-08 rejects an `import` without visibility (`private`/`public`) as a syntax error: {len(plain)} "
        f"distinct models as stored ({plain_by_model}). It is a grammar change after 2024-04.1, not a defect "
        "under the grammar of our validator.")
    lines = [f"Distinct models validated: {len(codes)} ({len(models)} rows).", notes, md_table(final), "## satisfy", md_table(sat),
             "## Most frequent issues with the imports added", md_table(top_df)]
    write_md(out / "summary.md", "A1. Acceptance by the SysML v2 Pilot Implementation", lines)


if __name__ == "__main__":
    main()
