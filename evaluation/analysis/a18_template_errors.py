"""A18. How much of the reference stage (C4P) is due to the interface template of the frozen prompt.

The template `interface <Name> { flow ... }` is an interface usage without ends: the Pilot reports
validateConnectorRelatedFeatures. Once the agent turns it into an interface definition, the Pilot often reports
validateAssociationRelatedTypes on the same element, so both codes are counted as template errors when the second
follows the first. From the stored logs of results/pilot_repair/ (no LLM, no Pilot):

- models whose only initial Pilot error is the template error, per document and generator;
- repair calls whose current error is a template error;
- C4P cost of the models whose only initial error is the template error.

Estimate: with a template validated by the Pilot, and assuming it introduces no other errors, the models that would
still need reference repair are those with some other initial error.

    python -m evaluation.analysis.a18_template_errors
"""

from __future__ import annotations

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.common import jsonl, md_table, model_sort, out_dir, write_md

SRC = RESULTS_DIR / "pilot_repair"
DOC = {"E1": "EIRENE", "E5": "JWST"}
TEMPLATE = "validateConnectorRelatedFeatures"
FOLLOW_UP = "validateAssociationRelatedTypes"
KEY = ["set", "llm", "run", "category"]


def main() -> None:
    out = out_dir("a18_template_errors")
    initial = {tuple(t[k] for k in KEY): {e.get("pilot_code") for e in t["errors"]}
               for t in jsonl(SRC / "iteration_trace.jsonl") if t["iteration"] == 0}
    res = pd.read_csv(SRC / "pilot_repair_results.csv")
    res["codes"] = [initial[(r.set, r.llm, r.run, r.category)] for r in res.itertuples()]
    res["needs_repair"] = res.codes.map(bool)
    res["only_template"] = res.codes.map(lambda c: c == {TEMPLATE})
    calls = pd.DataFrame([{"set": r["set"], "llm": r["llm"], "code": r["current_error"].get("pilot_code")}
                          for r in jsonl(SRC / "repairs.jsonl")])

    rows = []
    groups = [(s, llm) for s in DOC for llm in model_sort(res[res.set == s].llm)] + [("all", "all")]
    for s, llm in groups:
        r = res if s == "all" else res[(res.set == s) & (res.llm == llm)]
        c = calls if s == "all" else calls[(calls.set == s) & (calls.llm == llm)]
        need = r[r.needs_repair]
        rows.append({
            "document": DOC.get(s, "all"), "llm": llm, "models": len(r), "needing_c4p": len(need),
            "only_template": int(need.only_template.sum()),
            "only_template_pct_of_needing": need.only_template.mean() * 100,
            "any_template_pct_of_needing": need.codes.map(lambda x: TEMPLATE in x).mean() * 100,
            "repair_calls": len(c), "template_calls_pct": (c.code == TEMPLATE).mean() * 100,
            "template_or_follow_up_calls_pct": c.code.isin([TEMPLATE, FOLLOW_UP]).mean() * 100,
            "c4p_cost_usd": r.cost_usd.sum(), "only_template_cost_usd": r[r.only_template].cost_usd.sum(),
            "only_template_cost_pct": r[r.only_template].cost_usd.sum() / r.cost_usd.sum() * 100,
            "needing_with_validated_template": len(need) - int(need.only_template.sum()),
            "needing_pct_now": len(need) / len(r) * 100,
            "needing_pct_with_validated_template": (len(need) - need.only_template.sum()) / len(r) * 100})
    df = pd.DataFrame(rows)
    df.to_csv(out / "template_share.csv", index=False)
    top = calls.code.value_counts().rename_axis("pilot_code").reset_index(name="repair_calls")
    top.to_csv(out / "repair_calls_by_code.csv", index=False)
    write_md(out / "summary.md", "A18. Share of the reference stage due to the interface template",
             [f"Template error: `{TEMPLATE}` (interface usage without ends); follow-up: `{FOLLOW_UP}` (the definition "
              "the agent creates). Estimate with a validated template: models needing C4P minus those whose only "
              "initial error is the template error (assumes the corrected template introduces no other error).",
              md_table(df, 1), "## Repair calls by Pilot code", md_table(top.head(15))])
    a = df[df.document == "all"].iloc[0]
    print(f"  only template: {a.only_template}/{a.needing_c4p} ({a.only_template_pct_of_needing:.1f}%), calls "
          f"{a.template_calls_pct:.1f}% (+follow-up {a.template_or_follow_up_calls_pct:.1f}%), cost "
          f"{a.only_template_cost_pct:.1f}%; needing {a.needing_pct_now:.1f}% -> {a.needing_pct_with_validated_template:.1f}%")


if __name__ == "__main__":
    main()
