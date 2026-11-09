"""A1b. How much of the Pilot rejection is boilerplate or a template error (no LLM calls).

Deterministic fixes applied to a copy of every final model of A1 (the stored models are not changed):

(a) imports: every `import` without visibility becomes `private import` (2026-08 requires visibility), and
    `private import ScalarValues::*; private import ISQ::*; private import SI::*;` is inserted after the `{` of
    every top-level package (same line, so line numbers do not move);
(b) connector ends: in `connect X to Y`, an end written `A::p` (or `A::b::p`) becomes `A.p` (`A.b.p`) when its
    first segment A is a usage declared in the model (part, port, item, ref, occurrence, interface, connection or
    attribute usage, and not a definition). That is the feature chain the Pilot resolves connector ends with; A::p
    names the same feature p through the namespace A. Ends whose first segment is a definition or is not declared
    are left as they are and counted. Checked by hand on 20 real ends (connect_check_20.csv) before being applied.

The Pilot (2024-04.1 and 2026-08) validates the same sets as A1 in the variants (a), (b) and (a)+(b); the results
of A1 are reused for texts that are identical to an A1 input. Outputs: acceptance per set, model, condition and
document; the remaining error types under (a)+(b) with frequency and one example each; which code examples of the
frozen generation prompt and of the knowledge bases the Pilot accepts (with the minimal imports); and the paper table
tab:tool_acceptance.

    python -m evaluation.analysis.a01b_boilerplate --shards 6
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from core.agents.agent2.prompts import GENERATE_SYSTEM_PROMPT
from core.utils import KNOWLEDGE_DIR
from evaluation.analysis.a01_tool_acceptance import (_LINK_RE, RELEASES, SETS_CONDITIONS, library_names,
                                                     parse_issues, per_model, with_imports)
from evaluation.analysis.common import (ANALYSIS_DIR, fmt, load_models, md_table, model_sort, out_dir, tex, write_md,
                                        write_paper_table)

NAME = r"(?:'[^']+'|[A-Za-z_]\w*)"
END = rf"{NAME}(?:\s*(?:::|\.)\s*{NAME})+"
_CONNECT_RE = re.compile(rf"(\bconnect\s+)({END})(\s+to\s+)({END})")
_PLAIN_IMPORT_RE = re.compile(r"(?m)^(\s*)import\b")
_USAGE_KW = r"(?:part|port|item|ref|occurrence|interface|connection|attribute)"
VARIANTS = ["as_stored", "a", "b", "ab"]


def sha20(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def fix_imports(code: str) -> str:
    return with_imports(_PLAIN_IMPORT_RE.sub(r"\1private import", code))


def declared_usages(code: str) -> tuple[set[str], set[str]]:
    usages = {m.group(1) for m in re.finditer(rf"\b{_USAGE_KW}\s+(?!def\b)({NAME})", code)}
    defs = {m.group(1) for m in re.finditer(rf"\b\w+\s+def\s+({NAME})", code)}
    return usages, defs


def fix_connect(code: str, stats: dict | None = None) -> str:
    usages, defs = declared_usages(code)

    def end(e: str) -> str:
        if "::" not in e:
            return e
        first = re.split(r"\s*(?:::|\.)\s*", e)[0]
        if first in usages and first not in defs:
            if stats is not None:
                stats["rewritten"] = stats.get("rewritten", 0) + 1
            return re.sub(r"\s*::\s*", ".", e)
        if stats is not None:
            key = "kept_definition" if first in defs else "kept_undeclared"
            stats[key] = stats.get(key, 0) + 1
        return e

    return _CONNECT_RE.sub(lambda m: m.group(1) + end(m.group(2)) + m.group(3) + end(m.group(4)), code)


def variant_text(code: str, variant: str) -> str:
    if variant == "as_stored":
        return code
    if variant == "a":
        return fix_imports(code)
    if variant == "b":
        return fix_connect(code)
    return fix_imports(fix_connect(code))


# ---------------------------------------------------------------------------
# Pilot runs with a cache keyed by the sha of the validated text
# ---------------------------------------------------------------------------
def seed_cache(work_a1: Path, release: str, codes: dict[str, str], cache: Path) -> None:
    """Re-keys the A1 issue lists (keyed by model sha) by the sha of the text A1 validated."""
    if cache.exists():
        return
    lines = []
    for variant, transform in (("as_stored", lambda c: c), ("imports", with_imports)):
        tsv = work_a1 / release / variant / "issues.tsv"
        if not tsv.exists():
            continue
        tsha = {m: sha20(transform(c)) for m, c in codes.items()}
        for line in tsv.read_text(encoding="utf-8").splitlines():
            model = line.split("\t", 1)[0]
            if model in tsha:
                lines.append(tsha[model] + line[len(model):])
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def run_texts(pilot_root: Path, release: str, work: Path, texts: dict[str, str], shards: int) -> Path:
    base = work / release
    cache = base / "cache.tsv"
    done = {l.split("\t")[0] for l in cache.read_text(encoding="utf-8").splitlines() if "\tDONE\t" in l}
    todo = sorted((s, t) for s, t in texts.items() if s not in done)
    if not todo:
        return cache
    sysml = pilot_root / release / "sysml"
    from core.validate.pilot import pilot_jar

    jar = pilot_jar(sysml)
    classes = Path(__file__).resolve().parents[2] / "tools" / "pilot" / "build" / release
    if not (classes / "PilotBatch.class").exists():
        classes.mkdir(parents=True, exist_ok=True)
        subprocess.run(["javac", "-cp", str(jar), "-d", str(classes),
                        str(Path(__file__).resolve().parents[2] / "tools" / "pilot" / "PilotBatch.java")], check=True)
    print(f"  Pilot {release}: {len(todo)} new texts ({len(texts) - len(todo)} cached), {shards} JVMs", flush=True)
    procs, parts = [], []
    for k in range(shards):
        src = base / f"in_{k}"
        if src.exists():
            for f in src.glob("*.sysml"):
                f.unlink()
        src.mkdir(parents=True, exist_ok=True)
        for s, t in todo[k::shards]:
            (src / f"{s}.sysml").write_text(t, encoding="utf-8")
        part = base / f"part_{k}.tsv"
        parts.append(part)
        procs.append(subprocess.Popen(["java", "-Xmx1500m", "-cp", f"{jar}:{classes}", "PilotBatch",
                                       str(sysml / "sysml.library") + "/", str(src), str(part)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    for p in procs:
        p.wait()
    with cache.open("a", encoding="utf-8") as fh:  # keep only completed files of each part
        for part in parts:
            if part.exists():
                text = part.read_text(encoding="utf-8").splitlines()
                ok = {l.split("\t")[0] for l in text if "\tDONE\t" in l}
                fh.write("".join(l + "\n" for l in text if l.split("\t")[0] in ok))
                part.unlink()
    return cache


# ---------------------------------------------------------------------------
# Examples of the frozen prompt and the knowledge bases
# ---------------------------------------------------------------------------
_PLACEHOLDERS = {"<logical_expression>": "true", "<expression>": "true", "<expr>": "true", "<Type>": "Real", "<Value>": "1.0",
                 "<requirement text>": "text", "<id>": "R1"}


_KEYWORDS = {"attribute", "part", "port", "constraint", "requirement", "package", "connection", "interface", "flow",
             "binding", "enum", "def", "item", "action", "state"}
_STATEMENT_RE = re.compile(r"\b(?:package|part|port|requirement|attribute|constraint|assert|doc|comment|connect|"
                           r"connection|satisfy|enum|import|action|bind|binding|interface|item|calc|state)\b")


def fill(text: str) -> str:
    for k, v in _PLACEHOLDERS.items():
        text = text.replace(k, v)

    def name(m: re.Match) -> str:
        n = m.group(1).replace(" ", "_")
        return n + "_" if n in _KEYWORDS else n
    return re.sub(r"<([A-Za-z_][\w ]*)>", name, text)


def wrap(snippet: str, context: str = "") -> str:
    """A complete file around a fragment, with the minimal library imports; `context` = part | requirement."""
    if re.match(r"\s*package\b", snippet):
        return fix_imports(snippet)
    if context:
        snippet = f"{context} Owner {{\n{snippet}\n}}"
    return "package Example { private import ScalarValues::*;\n" + snippet + "\n}\n"


def prompt_examples() -> list[dict]:
    out = []
    template = GENERATE_SYSTEM_PROMPT.split("Package:\n", 1)[1].split("\n====", 1)[0]
    template = template[: template.rfind("}") + 1]
    out.append({"source": "prompt", "where": "STRUCTURAL TEMPLATES (package template, placeholders filled)",
                "intended": "valid", "code": wrap(fill(template))})
    # A consistent instance of the same template: every placeholder bound to an element the template declares.
    consistent = (template.replace("    import <OtherPkg>::* ;\n", "").replace("<PortA>", "<PortName>")
                  .replace("<PortB>", "<PortName>").replace("<OtherPart>", "<PartName>").replace("<attribute>", "mass"))
    out.append({"source": "prompt", "where": "STRUCTURAL TEMPLATES (consistent instance, connector ends A::p)",
                "intended": "valid", "code": wrap(fill(consistent))})
    out.append({"source": "prompt", "where": "STRUCTURAL TEMPLATES (consistent instance, ends rewritten A.p by (b))",
                "intended": "valid", "code": wrap(fix_connect(fill(consistent)))})
    for m in re.finditer(r"(?<!IN)VALID: (.+?)(?:\s{2,}|$)", GENERATE_SYSTEM_PROMPT, re.M):
        out.append({"source": "prompt", "where": "attribute rule (VALID)", "intended": "valid",
                    "code": wrap("part P { " + fill(m.group(1).strip()) + " }")})
    for line in GENERATE_SYSTEM_PROMPT.splitlines():
        s = line.strip()
        if (s.startswith("- ") and re.match(r"- (connect|connection|bind|binding|satisfy|constraint|assert constraint|"
                                            r"require constraint|attribute) ", s) and "MUST" not in s):
            s = s.replace("{ ... }", "{ }")
            context = ("requirement" if "inside a requirement)" in s else "part" if "inside a part" in s else "")
            out.append({"source": "prompt", "where": f"rule: {s[2:60]}", "intended": "valid",
                        "code": wrap(fill(re.sub(r"\s+\(.*\)\s*$", "", s[2:])), context)})
    return out


def kb_examples() -> list[dict]:
    out = []
    for f in sorted(KNOWLEDGE_DIR.glob("*.md")):
        lines = f.read_text(encoding="utf-8").splitlines()
        label, i = None, 0
        while i < len(lines):
            s = lines[i].strip().lower()
            if s.endswith(":") and ("invalid" in s or s.startswith(("wrong", "bad"))):
                label = "invalid"
            elif s.endswith(":") and any(w in s for w in ("fix", "valid", "correct", "repaired", "good", "after")):
                label = "valid"
            elif s.endswith(":") and s.startswith("examples"):
                label = "pairs"  # "before -> after" pairs
            if lines[i].startswith("    ") and lines[i].strip() and label:
                j = i
                while j < len(lines) and (lines[j].startswith("    ") or not lines[j].strip()):
                    j += 1
                block = "\n".join(l[4:] for l in lines[i:j]).strip()
                if ("rule" not in block and "::=" not in block and not block.startswith(("rule", "-", "#"))
                        and _STATEMENT_RE.search(block) and re.search(r"[;{}]|\*/", block)):
                    for para in re.split(r"\n\s*\n", block):  # one example (or before -> after pair) per paragraph
                        inline = [l for l in para.splitlines() if re.search(r"\S\s+->\s+\S", l)]
                        if inline and len(inline) == len([l for l in para.splitlines() if l.strip()]):
                            for line in inline:  # "invalid  ->  fixed" on one line
                                before, after = re.split(r"\s+->\s+", line.strip(), maxsplit=1)
                                for intended, piece in (("invalid", before), ("valid", after)):
                                    out.append({"source": f.stem, "where": f"line {i + 1}", "intended": intended,
                                                "code": wrap(fill(piece))})
                            continue
                        pieces = re.split(r"\n\s*->\s*\n", para)
                        for k, piece in enumerate(pieces):
                            if len(pieces) > 1:
                                intended = "invalid" if k == 0 else "valid"
                            else:
                                intended = "valid" if label == "pairs" else label
                            if _STATEMENT_RE.search(piece):
                                out.append({"source": f.stem, "where": f"line {i + 1}", "intended": intended,
                                            "code": wrap(fill(piece))})
                i = j
                continue
            i += 1
    return out


# Validation errors that only follow from a name the fragment does not declare (the element has no type, etc.).
_CONSEQUENCES = {"validatePartUsageType_", "validateFeatureReferenceExpressionReferentIsFeature",
                 "validateAttributeUsageType_", "validateFeatureHasType_", "validatePortUsageType_",
                 "validateUsageType_", "validateOccurrenceUsageType_"}


def example_status(issues: pd.DataFrame) -> str:
    if issues.empty:
        return "accepted"
    groups = set(issues.group)
    if "syntax" in groups:
        return "syntax error"
    other_validation = set(issues[issues.group == "validation"].code) - _CONSEQUENCES
    if other_validation:
        return "validation error"
    return "only names not declared in the fragment"


def classify_example(issues: pd.DataFrame, code: str) -> str:
    if issues.empty:
        return "accepted"
    groups = set(issues.group)
    reasons = []
    if "syntax" in groups:
        reasons.append("syntax: " + issues[issues.group == "syntax"].message.iloc[0][:70])
    if groups & {"name_other", "name_library"}:
        names = issues[issues.group.isin(["name_other", "name_library"])].message.map(
            lambda m: (_LINK_RE.search(m) or [None, None, None])[2])
        reasons.append("unresolved names (not declared in the fragment): " + ", ".join(sorted(set(names.dropna()))[:4]))
    if "validation" in groups:
        reasons.append("validation: " + ", ".join(sorted(set(issues[issues.group == "validation"].code)))[:90])
    return "; ".join(reasons)


# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pilot-root", type=Path, default=Path.home() / "tools" / "pilot")
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work_a01b")
    parser.add_argument("--work-a1", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work")
    parser.add_argument("--shards", type=int, default=6)
    args = parser.parse_args()
    out = out_dir("a01b_boilerplate")

    frames = []
    for name, conditions in SETS_CONDITIONS.items():
        m = load_models(name)
        frames.append(m[m.condition.isin(conditions)])
    models = pd.concat(frames, ignore_index=True)
    models["sha"] = models.sysml_code.map(sha20)
    codes = dict(zip(models.sha, models.sysml_code))

    stats: dict[str, int] = {}
    variant_texts = {v: {} for v in VARIANTS}  # variant -> model sha -> text
    for s, c in codes.items():
        for v in VARIANTS:
            variant_texts[v][s] = variant_text(c, v)
    for c in codes.values():
        fix_connect(c, stats)

    examples = prompt_examples() + kb_examples()
    for e in examples:
        e["sha"] = sha20(e["code"])

    def release_run(release: str) -> None:
        seed_cache(args.work_a1, release, codes, args.work / release / "cache.tsv")
        texts = {sha20(t): t for v in VARIANTS for t in variant_texts[v].values()}
        texts.update({e["sha"]: e["code"] for e in examples})
        run_texts(args.pilot_root, release, args.work, texts, args.shards)

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(release_run, RELEASES))

    rows, remaining, example_rows = [], [], []
    for release in RELEASES:
        lib = library_names(args.pilot_root / release / "sysml" / "sysml.library")
        issues = parse_issues(args.work / release / "cache.tsv", lib)
        for v in VARIANTS:
            tsha = {m: sha20(t) for m, t in variant_texts[v].items()}
            counts = per_model(issues, sorted(set(tsha.values()))).rename(columns={"sha": "tsha"})
            m = models.assign(tsha=models.sha.map(tsha)).merge(counts, on="tsha", how="left")
            rows.append(m.drop(columns=["requirements", "sysml_code", "generated_code"]).assign(release=release,
                                                                                                variant=v))
            if v == "ab":
                # Remaining errors of the models our ANTLR validator accepts (the final models of interest).
                valid_tsha = {tsha[m] for m in models[models.valid.astype(bool)].sha}
                rem = issues[issues.sha.isin(valid_tsha) & (issues.group != "warning")].copy()
                inv = {}
                for msha, t in tsha.items():
                    inv.setdefault(t, msha)
                rem["model_sha"] = rem.sha.map(inv)
                remaining.append(rem.assign(release=release))
        for e in examples:
            iss = issues[(issues.sha == e["sha"]) & (issues.group != "warning")]
            example_rows.append({**{k: e[k] for k in ("source", "where", "intended")}, "release": release,
                                 "accepted": iss.empty, "status": example_status(iss),
                                 "reason": classify_example(iss, e["code"]),
                                 "code": e["code"].replace("\n", " ")[:220]})
    per_row = pd.concat(rows, ignore_index=True)
    per_row.to_csv(out / "acceptance_per_model.csv.gz", index=False, compression="gzip")
    agg = (per_row.groupby(["set", "document", "llm", "condition", "release", "variant"])
           .agg(n=("sha", "size"), antlr_valid=("valid", "mean"), accepted=("accepted", "mean"),
                with_syntax=("syntax", lambda s: (s > 0).mean()),
                with_name_library=("name_library", lambda s: (s > 0).mean()),
                with_name_other=("name_other", lambda s: (s > 0).mean()),
                with_validation=("validation", lambda s: (s > 0).mean()))
           .reset_index())
    for c in ("antlr_valid", "accepted", "with_syntax", "with_name_library", "with_name_other", "with_validation"):
        agg[c] = (agg[c].astype(float) * 100).round(1)
    agg.to_csv(out / "acceptance.csv", index=False)
    by_doc = (per_row[per_row.condition.isin(["C1", "C4"])].groupby(["document", "condition", "release", "variant"])
              .accepted.mean().mul(100).round(1).unstack("variant").reset_index())
    by_doc.to_csv(out / "acceptance_by_document.csv", index=False)

    # Remaining error types under (a)+(b).
    rem = pd.concat(remaining, ignore_index=True)
    generic = lambda msg: re.sub(r"'[^']*'", "'...'", str(msg))  # noqa: E731
    rem["type"] = rem.apply(lambda r: f"validation: {r.code}" if r.group == "validation" else (
        f"syntax: {generic(r.message)[:60]}" if r.group == "syntax" else f"{generic(r.message)[:70]} [{r.group}]"),
        axis=1)
    def statement(r) -> str:
        lines = codes.get(r.model_sha, "").splitlines()
        n = int(r.line) if pd.notna(r.line) else 0
        m = re.match(r"\s*((?:private\s+|public\s+)?\w+(?:\s+def)?)", variant_text(codes.get(r.model_sha, ""), "ab")
                     .splitlines()[n - 1]) if 0 < n <= len(lines) else None
        return m.group(1) if m else "?"
    rem["statement"] = rem.apply(statement, axis=1)
    types = (rem.groupby(["release", "type"]).agg(models=("model_sha", "nunique"), issues=("sha", "size"),
                                                 statements=("statement", lambda x: ", ".join(
                                                     f"{k} {v}" for k, v in x.value_counts().head(3).items())),
                                                 example_model=("model_sha", "first"), example_line=("line", "first"),
                                                 example_message=("message", "first"))
             .reset_index().sort_values(["release", "models"], ascending=[True, False]))

    def example_line(r) -> str:
        code = variant_text(codes.get(r.example_model, ""), "ab")
        lines = code.splitlines()
        n = int(r.example_line) if pd.notna(r.example_line) else 0
        return lines[n - 1].strip()[:120] if 0 < n <= len(lines) else ""
    types["example_code"] = types.apply(example_line, axis=1)
    types.to_csv(out / "remaining_error_types.csv", index=False)
    ex = pd.DataFrame(example_rows)
    ex.to_csv(out / "prompt_kb_examples.csv", index=False)

    # 20 real connector ends: static check + Pilot evidence on their lines.
    check = pd.read_csv(out / "connect_check_20_static.csv")
    ev = []
    issues24 = parse_issues(args.work / "2024-04.1" / "cache.tsv", set())
    for r in check.itertuples():
        msha = next(s for s, c in codes.items() if r.end in c and models[models.sha == s].set.iloc[0] == r.set
                    and models[models.sha == s].llm.iloc[0] == r.llm)
        before = issues24[(issues24.sha == sha20(variant_texts["a"][msha])) & (issues24.line == r.line)]
        after = issues24[(issues24.sha == sha20(variant_texts["ab"][msha])) & (issues24.line == r.line)]
        ev.append({"connector_issues_line_a": int(before.code.str.contains("Connector|Linking", regex=True).sum()),
                   "connector_issues_line_ab": int(after.code.str.contains("Connector|Linking", regex=True).sum())})
    check = pd.concat([check, pd.DataFrame(ev)], axis=1)
    check.to_csv(out / "connect_check_20.csv", index=False)

    # Paper table.
    rows_tex = []
    sel = agg[((agg.condition == "C4") & agg.set.isin(["E1", "E5"])) | (agg.set.isin(["E4", "E5C0"]) & (agg.condition == "C1"))]
    labels = {"E1": "E1 (EIRENE)", "E4": "C0 (EIRENE)", "E5": "E5 (JWST)", "E5C0": "C0 (JWST)"}
    for s in ["E1", "E4", "E5", "E5C0"]:
        for llm in model_sort(sel[sel.set == s].llm):
            g = lambda rel, v: sel[(sel.set == s) & (sel.llm == llm) & (sel.release == rel) & (sel.variant == v)].iloc[0]  # noqa: E731
            r0 = g("2024-04.1", "as_stored")
            rows_tex.append([labels[s], tex(llm), str(int(r0.n)), fmt(r0.antlr_valid)]
                            + [fmt(g(rel, v).accepted) for v in ("as_stored", "a", "ab") for rel in RELEASES])
    write_paper_table(
        out / "tab_tool_acceptance.tex",
        "Acceptance of the final models (C4; C1 for the minimal prompt C0) by the SysML v2 Pilot Implementation, "
        "releases 2024-04.1 and 2026-08, with name resolution, typing and validation (\\% of models without "
        "errors). ANTLR: valid for our parser. As stored: the models as generated and repaired. (a): standard-"
        "library imports added with explicit visibility (\\texttt{private import ScalarValues::*;} and "
        "\\texttt{ISQ}, \\texttt{SI}) and visibility added to existing imports. (a)+(b): also connector ends "
        "written \\texttt{A::p} rewritten as the feature chain \\texttt{A.p} when \\texttt{A} is a usage. Both "
        "fixes are deterministic and applied to copies of the models.",
        "tab:tool_acceptance", ["Set", "Model", "n", "ANTLR", "As stored 24-04", "26-08", "(a) 24-04", "26-08",
                                "(a)+(b) 24-04", "26-08"], "llrrrrrrrr", rows_tex, wide=True)

    # Where the remaining connector errors are, and the severity of the A::p end issues per release.
    notes = ["## Interpretation"]
    for release in RELEASES:
        r = rem[(rem.release == release) & (rem.code == "validateConnectorRelatedFeatures")]
        on_iface = int((r.statement == "interface").sum())
        notes.append(f"- {release}, (a)+(b): validateConnectorRelatedFeatures remains in {r.model_sha.nunique()} models; "
                     f"{on_iface} of its {len(r)} issues are on `interface <Name> {{` lines, i.e. interface usages "
                     "declared without ends, as in the frozen prompt template `interface <InterfaceName> { flow ... }`.")
    sev = {}
    for release in RELEASES:
        raw = (args.work / release / "cache.tsv").read_text(encoding="utf-8").splitlines()
        hits = [l.split("\t")[2] for l in raw if "accessible feature (use dot notation" in l]
        sev[release] = pd.Series(hits).value_counts().to_dict()
    notes.append(f"- Connector ends written `A::p` raise 'Should be an accessible feature (use dot notation for "
                 f"nesting)': severity per release {sev}. In 2024-04.1 they are warnings, so (b) does not change the "
                 "acceptance there; in 2026-08 they are errors, and (b) removes them.")
    stats_line = (f"Connector ends with '::': {stats.get('rewritten', 0) + stats.get('kept_definition', 0) + stats.get('kept_undeclared', 0)}; "
                  f"rewritten {stats.get('rewritten', 0)}, kept because the first segment is a definition "
                  f"{stats.get('kept_definition', 0)}, kept because it is not declared {stats.get('kept_undeclared', 0)}.")
    write_md(out / "summary.md", "A1b. Boilerplate and template errors in the Pilot rejection", [
        stats_line, "\n".join(notes), "## Acceptance by document", md_table(by_doc), "## Acceptance per set, model and condition",
        md_table(agg), "## Remaining error types with (a)+(b) (models valid for our ANTLR validator)",
        md_table(types.drop(columns=["example_model"]).head(60)),
        "## Examples of the frozen prompt and the knowledge bases", md_table(ex.drop(columns=["code"])),
        "## Check of 20 real connector ends", md_table(check)])


if __name__ == "__main__":
    main()
