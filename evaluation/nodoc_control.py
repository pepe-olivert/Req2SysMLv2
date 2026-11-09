"""Judge control without documentation comments (R5): does the LJS depend on the copied requirement text?

The guided generation prompt puts each requirement's text in `doc /* ... */`, so the judge can match a
requirement by reading its own words. This script writes a copy of stored SysML models with that text
removed, for the evaluator to judge again (no LLM calls here):

- every `doc` comment is removed (`doc [name] [locale "..."] /* ... */`);
- every other comment (`comment ... /* */`, anonymous `/* */`, notes `//...` and `//* ... */`) and every
  textual representation (`rep ... /* */`) is removed when it contains requirement text, i.e. a run of
  at least LEAK_WORDS consecutive words of one of the category's requirements.

The stripped code is re-validated; invalid ones are excluded and listed in exclusions.csv. The script
also measures, on the ORIGINAL code, how many requirement names carry requirement text (LEAK_WORDS or
more consecutive words of a requirement, after splitting camelCase/underscores) and, as residual text
the control does not remove, how many string literals do.

    python -m evaluation.nodoc_control --source results/pipeline/sysml_models.jsonl --conditions C4 \\
        --out-dir results/nodoc_control/pipeline_c4
    python -m evaluator --input results/nodoc_control/pipeline_c4/sysml_models.jsonl \\
        --out-dir results/nodoc_control/pipeline_c4/ljs/gpt-4o-mini --workers 10 --max-rpm 18
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from evaluation.common import write_csv, write_run_manifest

LEAK_WORDS = 5

_WORD_RE = re.compile(r"[a-z0-9]+")
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_DOC_RE = re.compile(r"\bdoc\b(?:\s+(?:<[^>]*>\s*)?(?:'[^']*'|[A-Za-z_]\w*))?(?:\s+locale\s+\"[^\"]*\")?\s*/\*.*?\*/",
                     re.DOTALL)
_COMMENT_RE = re.compile(r"\b(?:comment|rep)\b[^;{}]*?/\*.*?\*/", re.DOTALL)
_NOTE_BLOCK_RE = re.compile(r"//\*.*?\*/", re.DOTALL)
_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_NOTE_LINE_RE = re.compile(r"//[^\n]*")
_STRING_RE = re.compile(r"\"(?:[^\"\\]|\\.)*\"")
_REQ_NAME_RE = re.compile(r"\brequirement\s+(?:def\s+)?(?:<[^>]*>\s*)?('(?:[^'\\]|\\.)*'|[A-Za-z_]\w*)")


def words(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def name_words(name: str) -> list[str]:
    return words(_CAMEL_RE.sub(" ", name.strip("'").replace("_", " ")))


def ngrams(tokens: list[str], n: int = LEAK_WORDS) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def requirement_ngrams(requirements: list[str]) -> set[tuple[str, ...]]:
    grams: set[tuple[str, ...]] = set()
    for r in requirements:
        grams |= ngrams(words(r))
    return grams


def leaks(tokens: list[str], grams: set[tuple[str, ...]]) -> bool:
    return bool(ngrams(tokens) & grams)


def strip_requirement_text(code: str, requirements: list[str]) -> tuple[str, dict]:
    """Returns the code without doc comments and without other comments that contain requirement text."""
    grams = requirement_ngrams(requirements)
    counts = defaultdict(int)

    def drop_if_leaks(kind: str):
        def repl(m: re.Match) -> str:
            if leaks(words(m.group(0)), grams):
                counts[kind] += 1
                return ""
            return m.group(0)
        return repl

    def drop(m: re.Match) -> str:
        counts["doc"] += 1
        return ""

    code = _NOTE_BLOCK_RE.sub(drop_if_leaks("note"), code)   # before /* */: a //* note ends with */
    code = _DOC_RE.sub(drop, code)
    code = _COMMENT_RE.sub(drop_if_leaks("comment"), code)
    code = _BLOCK_RE.sub(drop_if_leaks("comment"), code)
    code = _NOTE_LINE_RE.sub(drop_if_leaks("note"), code)
    code = re.sub(r"[ \t]+\n", "\n", code)
    code = re.sub(r"\n{3,}", "\n\n", code)
    return code, dict(counts)


def leak_stats(code: str, requirements: list[str]) -> dict:
    """Requirement names and string literals of the code that carry requirement text."""
    grams = requirement_ngrams(requirements)
    names = [m.group(1) for m in _REQ_NAME_RE.finditer(_BLOCK_RE.sub("", code))]
    strings = _STRING_RE.findall(_BLOCK_RE.sub("", code))
    return {
        "n_requirement_names": len(names),
        "n_names_with_text": sum(leaks(name_words(n), grams) for n in names),
        "n_strings": len(strings),
        "n_strings_with_text": sum(leaks(words(s), grams) for s in strings),
    }


def main() -> None:
    from core.agents.agent2.logic import SysMLAgent
    from evaluator.__main__ import judgment_key

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, required=True, help="A phase's sysml_models.jsonl.")
    parser.add_argument("--conditions", nargs="+", default=None, help="Only these conditions (default: all).")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    agent = SysMLAgent.__new__(SysMLAgent)  # validation only
    records = {}
    for line in args.source.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if args.conditions is None or r["condition"] in args.conditions:
                records[(r["pdf"], r["llm"], r["condition"], str(r["run"]), r["category"])] = r  # last wins

    out_models, exclusions, leak_rows = [], [], []
    for r in records.values():
        key = {k: r[k] for k in ("pdf", "llm", "condition", "run", "category")}
        stats = leak_stats(r["sysml_code"], r["requirements"])
        stripped, removed = strip_requirement_text(r["sysml_code"], r["requirements"])
        after = leak_stats(stripped, r["requirements"])
        leak_rows.append({**key, **stats, "removed_doc": removed.get("doc", 0),
                          "removed_comment": removed.get("comment", 0), "removed_note": removed.get("note", 0),
                          "chars_before": len(r["sysml_code"]), "chars_after": len(stripped),
                          "n_strings_with_text_after": after["n_strings_with_text"]})
        if not r.get("valid", True):
            exclusions.append({**key, "reason": "invalid before stripping", "n_errors": ""})
            continue
        errors = agent.validate_sysml(stripped)
        if errors:
            exclusions.append({**key, "reason": "invalid after stripping", "n_errors": len(errors)})
            continue
        out_models.append({
            **key, "requirements_sha256": r.get("requirements_sha256", ""), "requirements": r["requirements"],
            "sysml_code": stripped, "valid": True, "nodoc": True, "removed": removed,
            "original_judgment_key": judgment_key(r["requirements"], r["sysml_code"]),
            "source": str(args.source),
        })

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "sysml_models.jsonl").write_text(
        "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out_models), encoding="utf-8")
    write_csv(args.out_dir / "exclusions.csv", ["pdf", "llm", "condition", "run", "category", "reason", "n_errors"],
              exclusions)
    write_csv(args.out_dir / "requirement_text_leaks.csv", list(leak_rows[0]) if leak_rows else [], leak_rows)
    write_run_manifest(args.out_dir, source=str(args.source), conditions=args.conditions, leak_words=LEAK_WORDS,
                       n_models=len(records), n_written=len(out_models), n_excluded=len(exclusions))
    print(f"{args.out_dir}: {len(out_models)}/{len(records)} stripped models written, {len(exclusions)} excluded")
    by_model = defaultdict(lambda: [0, 0])
    for row in leak_rows:
        by_model[row["llm"]][0] += row["n_names_with_text"]
        by_model[row["llm"]][1] += row["n_requirement_names"]
    for model, (hit, total) in sorted(by_model.items()):
        print(f"  {model}: {hit}/{total} requirement names with >= {LEAK_WORDS} consecutive requirement words")


if __name__ == "__main__":
    main()
