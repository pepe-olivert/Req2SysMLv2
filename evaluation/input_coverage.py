"""Justification of the pipeline input: coverage of the selected requirement set and manual-validation sample.

Compares the requirements used by the pipeline/ablation (best_requirements.json) with the most
exhaustive extraction of the same document (the run picked by the automatic max-requirements
criterion), using the same embeddings as the rest of the evaluation. No LLM calls.

    python -m evaluation.input_coverage              # coverage CSV + table + manual-validation sample
    python -m evaluation.input_coverage --summarize [--annotations FILE]  # after annotating the sample

Outputs (results/extraction/):
    input_coverage.csv, tables/tab_input_coverage.tex
    input_uncovered_reference.csv          reference requirements without any counterpart
    manual_validation_sample.csv           to be annotated by hand (columns *_annotation)
    tables/tab_manual_validation.tex       written by --summarize once annotated
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from collections import Counter

import numpy as np

from core.config import document_path
from core.extraction.dedup import deduplicate_requirements
from core.evaluation.semantic_eval import encode

from evaluation.common import (
    BEST_REQUIREMENTS_PATH,
    EXTRACTION_DIR,
    normalize_requirements,
    read_csv_rows,
    read_json,
    write_csv,
)
from evaluation.make_paper_artifacts import fmt, tex_escape, write_table
from evaluation.run_extraction import RUNS_DIR, select_best, successful_runs


THRESHOLDS = (0.85, 0.75, 0.65)
NO_COUNTERPART_THRESHOLD = 0.65
SAMPLE_SIZE = 50
SEED = 42

COVERAGE_PATH = EXTRACTION_DIR / "input_coverage.csv"
UNCOVERED_PATH = EXTRACTION_DIR / "input_uncovered_reference.csv"
SAMPLE_PATH = EXTRACTION_DIR / "manual_validation_sample.csv"
TABLES_DIR = EXTRACTION_DIR / "tables"

COVERAGE_COLUMNS = (
    "threshold", "selected_n", "reference_n",
    "one_to_one_matched", "reference_covered_one_to_one_pct", "selected_in_reference_pct",
    "reference_with_counterpart_pct",
)
SAMPLE_COLUMNS = (
    "sample_id", "set", "category", "requirement", "pdf_page", "pdf_snippet",
    "nearest_in_other_set", "similarity",
    "exists_in_document_annotation", "faithful_annotation", "comment",
)
ANNOTATION_HELP = {
    "exists_in_document_annotation": "yes | partial | no",
    "faithful_annotation": "yes | no  (meaning preserved, no invented content)",
}


def _flat(requirements: dict[str, list[str]]) -> list[tuple[str, str]]:
    """(category, requirement) pairs, unique requirement texts across categories."""
    seen: dict[str, str] = {}
    for category, reqs in requirements.items():
        for req in reqs:
            seen.setdefault(req, category)
    return [(cat, req) for req, cat in seen.items()]


def _one_to_one(sim: np.ndarray, threshold: float) -> int:
    rows, cols = np.where(sim >= threshold)
    order = np.argsort(-sim[rows, cols])
    used_a: set[int] = set()
    used_b: set[int] = set()
    for k in order:
        i, j = int(rows[k]), int(cols[k])
        if i not in used_a and j not in used_b:
            used_a.add(i)
            used_b.add(j)
    return len(used_a)


def _near_duplicate_pct(embeddings: np.ndarray, threshold: float = 0.85) -> float:
    sim = embeddings @ embeddings.T
    np.fill_diagonal(sim, 0.0)
    return float((sim.max(axis=1) >= threshold).mean() * 100)


def _pdf_segments(doc: str) -> list[tuple[int, str]]:
    """(page, segment) pairs: sentence-like segments of each PDF page, for locating requirements."""
    from pypdf import PdfReader

    segments = []
    for page_no, page in enumerate(PdfReader(document_path(doc)).pages, start=1):
        text = " ".join((page.extract_text() or "").split())
        for sentence in text.replace("•", ". ").split(". "):
            if len(sentence) > 25:
                segments.append((page_no, sentence.strip()))
    return segments


def load_sets() -> tuple[dict, dict, dict]:
    best = read_json(BEST_REQUIREMENTS_PATH)
    doc = best["source"]["doc"]
    reference = select_best(successful_runs(), doc)  # automatic criterion = most exhaustive set
    return best, reference, read_json(RUNS_DIR / reference["source"]["file"])


def coverage() -> None:
    best, reference, _ = load_sets()
    sel_src, ref_src = best["source"], reference["source"]
    if sel_src["file"] == ref_src["file"]:
        print("The pipeline input already is the most exhaustive extraction; nothing to compare.")
        return

    selected = _flat(best["requirements"])
    ref = _flat(normalize_requirements(deduplicate_requirements(reference["requirements"])[0]))
    e_sel = encode([r for _, r in selected])
    e_ref = encode([r for _, r in ref])
    sim = e_ref @ e_sel.T  # reference x selected
    best_for_ref = sim.max(axis=1)

    rows = []
    for th in THRESHOLDS:
        matched = _one_to_one(sim, th)
        rows.append({
            "threshold": th, "selected_n": len(selected), "reference_n": len(ref),
            "one_to_one_matched": matched,
            "reference_covered_one_to_one_pct": matched / len(ref) * 100,
            "selected_in_reference_pct": matched / len(selected) * 100,
            "reference_with_counterpart_pct": float((best_for_ref >= th).mean() * 100),
        })
    write_csv(COVERAGE_PATH, COVERAGE_COLUMNS, rows)

    uncovered = np.where(best_for_ref < NO_COUNTERPART_THRESHOLD)[0]
    write_csv(UNCOVERED_PATH, ("category", "requirement", "best_similarity"),
              [{"category": ref[i][0], "requirement": ref[i][1], "best_similarity": round(float(best_for_ref[i]), 3)}
               for i in uncovered])

    nearest = sim.argmax(axis=1)
    groups = Counter(int(nearest[i]) for i in np.where(best_for_ref >= 0.75)[0])
    split = [v for v in groups.values() if v >= 2]
    dup_sel, dup_ref = _near_duplicate_pct(e_sel), _near_duplicate_pct(e_ref)

    label = lambda s: f"{tex_escape(s['model'])} ({s['strategy'].replace('_', ' ')}, run {s['run']})"  # noqa: E731
    table_rows = [[fmt(r["threshold"], 2), fmt(r["reference_with_counterpart_pct"], 1),
                   fmt(r["reference_covered_one_to_one_pct"], 1), fmt(r["selected_in_reference_pct"], 1)]
                  for r in rows]
    write_table(
        TABLES_DIR / "tab_input_coverage.tex",
        f"Semantic coverage of the pipeline input ({label(sel_src)}: {len(selected)} unique requirements, "
        f"{sel_src['n_categories']} categories, \\${sel_src['cost_usd']:.3f}) with respect to the most exhaustive "
        f"extraction ({label(ref_src)}: {len(ref)} requirements, {ref_src['n_categories']} categories, "
        f"\\${ref_src['cost_usd']:.3f}). Cosine similarity of all-MiniLM-L6-v2 embeddings. "
        f"{len(split)} input requirements are the closest match of two or more reference requirements "
        f"({sum(split)} in total); {len(uncovered)} reference requirements "
        f"({len(uncovered) / len(ref) * 100:.1f}\\%) have no counterpart at cosine $\\geq$ {NO_COUNTERPART_THRESHOLD}.",
        "tab:input_coverage",
        ["Cosine $\\geq$", "Ref. with counterpart \\%", "Ref. matched 1:1 \\%", "Input found in ref. \\%"],
        "rrrr", table_rows,
    )

    print(f"Input:     {sel_src['file']} ({len(selected)} unique requirements, ${sel_src['cost_usd']:.4f})")
    print(f"Reference: {ref_src['file']} ({len(ref)} unique requirements, ${ref_src['cost_usd']:.4f})")
    for r in rows:
        print(f"  cos>={r['threshold']:.2f}: reference with counterpart {r['reference_with_counterpart_pct']:.1f}% | "
              f"1:1 coverage {r['reference_covered_one_to_one_pct']:.1f}% | "
              f"input found in reference {r['selected_in_reference_pct']:.1f}%")
    print(f"  {len(split)} input requirements are the best match of >=2 reference requirements ({sum(split)} reference reqs)")
    print(f"  {len(uncovered)} reference requirements without counterpart (< {NO_COUNTERPART_THRESHOLD}) -> {UNCOVERED_PATH.name}")
    print(f"  cross-category near-duplicates (>=0.85): input {dup_sel:.1f}%, reference {dup_ref:.1f}%")

    _write_sample(best, selected, ref, e_sel, e_ref, sim, uncovered)


def _write_sample(best, selected, ref, e_sel, e_ref, sim, uncovered) -> None:
    if SAMPLE_PATH.exists() and any(
        r.get("exists_in_document_annotation") or r.get("faithful_annotation") for r in read_csv_rows(SAMPLE_PATH)
    ):
        print(f"  {SAMPLE_PATH.name} already annotated; not overwritten.")
        return

    segments = _pdf_segments(best["source"]["doc"])
    e_seg = encode([s for _, s in segments])
    rng = random.Random(SEED)
    picked = sorted(rng.sample(range(len(selected)), min(SAMPLE_SIZE, len(selected))))

    def locate(embedding):
        k = int((e_seg @ embedding).argmax())
        return segments[k][0], segments[k][1][:200]

    rows = []
    for n, i in enumerate(picked, start=1):
        page, snippet = locate(e_sel[i])
        j = int(sim[:, i].argmax())
        rows.append({"sample_id": f"IN{n:02d}", "set": "input_random", "category": selected[i][0],
                     "requirement": selected[i][1], "pdf_page": page, "pdf_snippet": snippet,
                     "nearest_in_other_set": ref[j][1], "similarity": round(float(sim[j, i]), 3)})
    for n, i in enumerate(uncovered, start=1):
        page, snippet = locate(e_ref[i])
        j = int(sim[i].argmax())
        rows.append({"sample_id": f"REF{n:02d}", "set": "reference_only", "category": ref[i][0],
                     "requirement": ref[i][1], "pdf_page": page, "pdf_snippet": snippet,
                     "nearest_in_other_set": selected[j][1], "similarity": round(float(sim[i, j]), 3)})
    for row in rows:
        row.update({c: "" for c in ("exists_in_document_annotation", "faithful_annotation", "comment")})
    write_csv(SAMPLE_PATH, SAMPLE_COLUMNS, rows)
    print(f"  manual-validation sample -> {SAMPLE_PATH} ({len(picked)} random input reqs + "
          f"{len(uncovered)} reference-only reqs). Fill: {ANNOTATION_HELP}")


def summarize(annotations: Path) -> None:
    from scipy.stats import binomtest, fisher_exact

    rows = [r for r in read_csv_rows(annotations) if r.get("exists_in_document_annotation")]
    if not rows:
        raise SystemExit(f"No annotations found in {annotations}.")

    def pct_ci(k: int, n: int) -> str:
        ci = binomtest(k, n).proportion_ci(method="wilson")
        return f"{k / n * 100:.1f} [{ci.low * 100:.0f}--{ci.high * 100:.0f}]"

    table, lines, faithful_counts = [], [], {}
    for subset, label in (("input_random", "Input (random sample)"), ("reference_only", "Reference-only")):
        sub = [r for r in rows if r["set"] == subset]
        if not sub:
            continue
        exists = Counter(r["exists_in_document_annotation"].strip().lower() for r in sub)
        faithful = sum(r["faithful_annotation"].strip().lower() == "yes" for r in sub)
        n = len(sub)
        faithful_counts[subset] = (faithful, n)
        table.append([label, str(n), pct_ci(exists["yes"], n), fmt(exists["partial"] / n * 100, 1),
                      fmt(exists["no"] / n * 100, 1), pct_ci(faithful, n)])
        lines.append(f"{label}: n={n}, exists yes/partial/no = {exists['yes']}/{exists['partial']}/{exists['no']}, "
                     f"faithful = {faithful}")

    test_txt = ""
    if len(faithful_counts) == 2:
        (f_in, n_in), (f_ref, n_ref) = faithful_counts["input_random"], faithful_counts["reference_only"]
        p_value = fisher_exact([[f_in, n_in - f_in], [f_ref, n_ref - f_ref]]).pvalue
        test_txt = (f" Faithfulness differs between the input sample and the reference-only requirements "
                    f"(Fisher's exact test, $p = {p_value:.3f}$).")
        lines.append(f"Fisher's exact test on faithfulness (input vs reference-only): p = {p_value:.4f}")
    write_table(TABLES_DIR / "tab_manual_validation.tex",
                "Manual validation of extracted requirements against the source document. Input: random sample of "
                "the requirements used in the experiments; Reference-only: requirements found only by the most "
                "exhaustive extraction. Percentages with Wilson 95\\% confidence intervals." + test_txt,
                "tab:manual_validation", ["Set", "n", "Exists \\%", "Partial \\%", "Not found \\%", "Faithful \\%"],
                "lrrrrr", table)
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--summarize", action="store_true", help="Summarize the annotated manual-validation sample.")
    parser.add_argument("--annotations", type=Path, default=SAMPLE_PATH,
                        help="Annotated copy of the sample (default: the sample file itself).")
    args = parser.parse_args()
    summarize(args.annotations) if args.summarize else coverage()


if __name__ == "__main__":
    main()
