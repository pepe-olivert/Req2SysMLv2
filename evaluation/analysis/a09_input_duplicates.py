"""A9. Why 22 requirement texts are repeated among the 771 input requirements.

core/extraction/strategy_sliding_window.py merges the chunks by category name
(merged.setdefault(category, []).extend(...)) and then calls core/extraction/dedup.py, whose
deduplicate_requirements loops over the categories and removes exact and near duplicates (cosine > 0.92)
only within each category. The same sentence extracted from two overlapping windows (500 tokens of overlap)
under two different category names (from two overlapping windows or from one window) is therefore kept twice. This script checks that every repeated text of
results/extraction/best_requirements.json is in two or more different categories (none within one category)
and lists them. best_requirements.json applies the same per-category dedup again (select_best).

    python -m evaluation.analysis.a09_input_duplicates
"""

from __future__ import annotations

import json
from collections import Counter

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.common import md_table, out_dir, write_md


def main() -> None:
    out = out_dir("a09_input_duplicates")
    sections = []
    for label, path in (("EIRENE input (E1-E4)", RESULTS_DIR / "extraction" / "best_requirements.json"),
                        ("JWST input (E5, R9)", RESULTS_DIR / "jwst_pipeline" / "input_requirements.json"),
                        ("sol input (R3)", RESULTS_DIR / "input_control_sol" / "input_requirements.json")):
        reqs = json.loads(path.read_text(encoding="utf-8"))["requirements"]
        entries = [(c, r) for c, v in reqs.items() for r in v]
        counts = Counter(r for _, r in entries)
        within = sum(len(v) - len(set(v)) for v in reqs.values())
        dups = [{"text": r, "copies": n, "categories": " | ".join(c for c, v in reqs.items() if r in v)}
                for r, n in counts.items() if n > 1]
        df = pd.DataFrame(dups, columns=["text", "copies", "categories"])
        spread = int((df.categories.str.count(r" \| ") >= 1).sum()) if len(df) else 0
        extra = int((df.copies - 1).sum()) if len(df) else 0
        if label.startswith("EIRENE"):
            df.to_csv(out / "repeated_requirements_eirene.csv", index=False)
        sections.append(
            f"## {label}\n\nEntries: {len(entries)}; distinct texts: {len(counts)}; repeated texts: {len(df)} "
            f"({extra} extra copies); repeated within one category: {within}; "
            f"repeated texts spread over 2+ categories: {spread}."
            + ("\n\n" + md_table(df.assign(text=df.text.str.slice(0, 90))) if label.startswith("EIRENE") else ""))
    explanation = (
        "## Explanation\n\nThe sliding-window strategy extracts each window separately and merges the results by "
        "category name; deduplication (exact, then cosine > 0.92 of all-MiniLM-L6-v2 embeddings) runs inside each "
        "category only. A sentence filed under two category names survives twice, whether the two copies come "
        "from the 500-token overlap of two windows or from one window that lists it in two categories (the chunk "
        "outputs are not stored, so the two cases cannot be told apart). Every repeated text of the inputs is of "
        "this kind: none is repeated inside a category. The 771 entries of the EIRENE input are 749 distinct "
        "texts; the paper's 749 \"unique requirements\" (tab:input_coverage) counts texts, the 771 used by the "
        "pipeline counts entries, so 22 requirements are generated, judged and costed twice, in two categories.")
    write_md(out / "summary.md", "A9. Repeated requirement texts in the input", [explanation] + sections)


if __name__ == "__main__":
    main()
