"""A15 (no LLM calls). Rewriting (b) extended to every reference A::x whose first segment is a usage of the model.

A1b's (b) only rewrote connector ends. Here every qualified reference `A::x` (or `A::x::y`) outside comments,
strings and import lines becomes the feature chain `A.x` (`A.x.y`) when A is a usage declared in the model and is
not also a definition name, no later segment is a definition name, and the reference is not in a typing or
specialization position (after `:`, `:>`, `:>>`, specializes, subsets, redefines, defined by): there a type is
named, and types are qualified with `::`. A first version without these two exclusions rewrote type references
such as `port p : CabRadio::NetworkPort` (NetworkPort a port definition nested in the usage CabRadio) and broke
2.3-3.0% of the gpt-6-luna models under 2024-04.1. Names declared more than once are not rewritten either: in
one model a requirement and a part are both named ExternalSafetyDevice, and the chain resolves to the requirement
(the original (b) of A1b, which has no such exclusion, breaks that model under 2024-04.1). Checked by
hand on 20 real references outside connect statements (ref_check_20.csv: A is a usage and x is declared in A's body
or in its type, so A.x names the same feature through the usage) before being applied.

Applied to the final models of R11 (results/pilot_repair), validated with the Pilot 2026-08 and 2024-04.1 (to check
that it breaks nothing) and with our ANTLR validator. Acceptance with 2026-08 after R11, with the original (b) and
with the extended (b), per model and document; classification of the remaining errors.

    python -m evaluation.analysis.a15_extended_b
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from core.agents.agent2.logic import SysMLAgent
from core.config import RESULTS_DIR
from evaluation.analysis.a01_tool_acceptance import parse_issues
from evaluation.analysis.a01b_boilerplate import NAME, declared_usages, fix_connect, run_texts, sha20
from evaluation.analysis.common import fmt, jsonl, md_table, model_sort, out_dir, tex, write_md

SRC = RESULTS_DIR / "pilot_repair"
DOC = {"E1": "EIRENE", "E5": "JWST"}
_QUAL_RE = re.compile(rf"(?<![\w.:']){NAME}(?:\s*::\s*{NAME})+")
_SKIP_RE = re.compile(r"/\*.*?\*/|//[^\n]*|\"(?:[^\"\\]|\\.)*\"", re.DOTALL)
_IMPORT_RE = re.compile(r"^\s*(?:private\s+|public\s+)?import\b")


def declared_names(code: str) -> dict[str, int]:
    """How many times each name is declared (any element kind, definitions included)."""
    counts: dict[str, int] = {}
    for m in re.finditer(rf"\b(?:def|part|port|item|ref|occurrence|interface|connection|attribute|requirement|"
                         rf"constraint|action|state|enum|package|calc|case|view|flow|binding)\s+(?!def\b)({NAME})",
                         _SKIP_RE.sub(" ", code)):
        counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    return counts


def fix_references(code: str, stats: dict | None = None) -> str:
    usages, defs = declared_usages(code)
    declared = declared_names(code)

    def rewrite_part(text: str) -> str:
        out_lines = []
        for line in text.split("\n"):
            if _IMPORT_RE.match(line):
                out_lines.append(line)
                continue

            def sub(m: re.Match) -> str:
                segments = re.split(r"\s*::\s*", m.group(0))
                first = segments[0]
                before = line[:m.start()].rstrip()
                typing = bool(re.search(r"(?::|:>|:>>|\bspecializes|\bsubsets|\bredefines|\bdefined\s+by)$", before))
                if (first in usages and first not in defs and not typing and declared.get(first, 0) == 1
                        and not any(seg in defs for seg in segments[1:])):
                    if stats is not None:
                        stats["rewritten"] = stats.get("rewritten", 0) + 1
                    return re.sub(r"\s*::\s*", ".", m.group(0))
                if stats is not None:
                    stats["kept"] = stats.get("kept", 0) + 1
                return m.group(0)
            out_lines.append(_QUAL_RE.sub(sub, line))
        return "\n".join(out_lines)

    pieces, last = [], 0
    for m in _SKIP_RE.finditer(code):  # comments, doc text and strings are left untouched
        pieces.append(rewrite_part(code[last:m.start()]))
        pieces.append(m.group(0))
        last = m.end()
    pieces.append(rewrite_part(code[last:]))
    return "".join(pieces)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pilot-root", type=Path, default=Path.home() / "tools" / "pilot")
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "sysml_pilot_work_r11")
    parser.add_argument("--shards", type=int, default=5)
    args = parser.parse_args()
    out = out_dir("a15_extended_b")
    agent = SysMLAgent.__new__(SysMLAgent)

    rows = {}
    for m in jsonl(SRC / "sysml_models.jsonl"):
        rows[(m["set"], m["llm"], int(m["run"]), m["category"])] = m
    stats: dict[str, int] = {}
    recs = []
    for (s, llm, run, cat), m in rows.items():
        code = m["sysml_code"]
        variants = {"after_r11": code, "b_original": fix_connect(code), "b_extended": fix_references(code, stats)}
        recs.append({"set": s, "document": DOC[s], "llm": llm, "run": run, "category": cat,
                     **{f"text_{k}": v for k, v in variants.items()}})
    df = pd.DataFrame(recs)
    texts = {sha20(t): t for c in ("text_after_r11", "text_b_original", "text_b_extended") for t in df[c]}
    for release in ("2026-08", "2024-04.1"):
        (args.work / release).mkdir(parents=True, exist_ok=True)
        (args.work / release / "cache.tsv").touch()
        run_texts(args.pilot_root, release, args.work, texts, args.shards)
    res = {}
    for release in ("2026-08", "2024-04.1"):
        iss = parse_issues(args.work / release / "cache.tsv", set())
        res[release] = iss[iss.group.isin(["syntax", "name_library", "name_other", "validation", "exception"])]
    for v in ("after_r11", "b_original", "b_extended"):
        df[f"sha_{v}"] = df[f"text_{v}"].map(sha20)
        for release in ("2026-08", "2024-04.1"):
            df[f"acc_{release}_{v}"] = ~df[f"sha_{v}"].isin(set(res[release].sha))
    df["antlr_valid_b_extended"] = [not agent.validate_sysml(t) for t in df.text_b_extended]
    df["changed_by_b_extended"] = df.text_b_extended != df.text_after_r11

    keep = [c for c in df.columns if not c.startswith(("text_", "sha_"))]
    df[keep].to_csv(out / "per_model.csv", index=False)
    acc = df.groupby(["document", "llm"]).agg(
        n=("category", "size"), changed_by_b_extended=("changed_by_b_extended", "sum"),
        **{f"{r}_{v}": (f"acc_{r}_{v}", "mean") for r in ("2026-08", "2024-04.1")
           for v in ("after_r11", "b_original", "b_extended")},
        antlr_valid_b_extended=("antlr_valid_b_extended", "mean")).reset_index()
    for c in acc.columns:
        if c.startswith(("2026", "2024", "antlr")):
            acc[c] = (acc[c] * 100).round(1)
    acc.to_csv(out / "acceptance.csv", index=False)

    # Remaining errors with 2026-08 and the extended (b).
    e = res["2026-08"]
    shas = dict(zip(df.sha_b_extended, df.llm))
    e = e[e.sha.isin(shas)].assign(llm=lambda x: x.sha.map(shas))
    text_of = dict(zip(df.sha_b_extended, df.text_b_extended))

    def stmt(r) -> str:
        lines = text_of[r.sha].splitlines()
        n = int(r.line) if pd.notna(r.line) else 0
        return lines[n - 1].strip()[:110] if 0 < n <= len(lines) else ""
    e = e.assign(example_line=e.apply(stmt, axis=1))
    types = (e.groupby(["llm", "group", "code"]).agg(models=("sha", "nunique"), issues=("sha", "size"),
                                                    example_message=("message", "first"),
                                                    example_line=("example_line", "first"))
             .reset_index().sort_values(["llm", "models"], ascending=[True, False]))
    types.to_csv(out / "remaining_2026_b_extended.csv", index=False)

    # 20-case check: static evidence plus the Pilot 2026-08 errors on those lines before and after.
    check = pd.read_csv(out / "ref_check_20_static.csv")
    ev = []
    for r in check.itertuples():
        m = df[(df.set == r.set) & (df.llm == r.llm) & df.text_after_r11.str.contains(re.escape(r.ref))].iloc[0]
        before = res["2026-08"][(res["2026-08"].sha == m.sha_after_r11) & (res["2026-08"].line == r.line)]
        after = res["2026-08"][(res["2026-08"].sha == m.sha_b_extended) & (res["2026-08"].line == r.line)]
        ev.append({"errors_on_line_2026_before": len(before), "errors_on_line_2026_after": len(after),
                   "after_codes": ", ".join(sorted(set(after.code)))})
    check = pd.concat([check, pd.DataFrame(ev)], axis=1)
    check.to_csv(out / "ref_check_20.csv", index=False)

    write_md(out / "summary.md", "A15. Rewriting A::x as A.x for every usage reference", [
        f"References rewritten: {stats.get('rewritten', 0)}; kept (first segment not a usage or also a "
        f"definition): {stats.get('kept', 0)}. Models changed by the extended rewriting: "
        f"{int(df.changed_by_b_extended.sum())} of {len(df)}.",
        "## Acceptance (% of models without errors)", md_table(acc),
        "## Remaining errors with 2026-08 and the extended (b)", md_table(types.groupby("llm").head(8)),
        "## Check of 20 real references", md_table(check)])
    print(acc.to_string(index=False))


if __name__ == "__main__":
    main()
