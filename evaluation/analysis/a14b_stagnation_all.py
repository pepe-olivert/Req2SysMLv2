"""A14b (no LLM calls). Stagnation with the A14 definition for every repair stage and experiment.

An iteration is stagnant when neither the diagnostics nor the model change during it (A14). The loop's own flag
(stored as `stagnation` in the results CSVs) only compares the diagnostics. Recomputed for the grammar stage
(E1, E2, E3 bank, E5, JWST banks; every condition, FULLREV included) from errors.csv (diagnostics per iteration)
and repairs.jsonl (model before/after each call; a rejected answer leaves the model as it was). R11 (C4P) is in
results/analysis/a14_guard_rejections/.

    python -m evaluation.analysis.a14b_stagnation_all
"""

from __future__ import annotations

import pandas as pd

from core.agents.agent2.logic import SysMLAgent
from core.config import RESULTS_DIR
from evaluation.analysis.common import jsonl, md_table, out_dir, write_md

PHASES = {"E1 (EIRENE)": ["pipeline"], "E2 (EIRENE)": ["ablation"],
          "E3 bank": ["ablation_stress", "ablation_stress_revision"], "E5 (JWST)": ["jwst_pipeline"],
          "JWST bank": ["jwst_v1_bank", "jwst_v1_bank_flashlite"]}


def main() -> None:
    out = out_dir("a14b_stagnation_all")
    rows = []
    for setting, phases in PHASES.items():
        for phase in phases:
            errs = pd.read_csv(RESULTS_DIR / phase / "errors.csv")
            diag = {}
            for k, g in errs.groupby(["llm", "condition", "run", "category", "iteration"]):
                diag[k] = sorted(zip(g.line.astype(str), g.column.astype(str), g.message))
            reps = {}
            for r in jsonl(RESULTS_DIR / phase / "repairs.jsonl"):
                reps.setdefault((r["llm"], r["condition"], int(r["run"]), r["category"]), {}) \
                    .setdefault(int(r["iteration"]), []).append(r)
            for (llm, cond, run, cat), its in reps.items():
                for it, calls in sorted(its.items()):
                    start = SysMLAgent.clean_sysml(calls[0]["code_before"])
                    end = start
                    for c in calls:
                        if not c.get("guard_rejected"):
                            end = SysMLAgent.clean_sysml(c["code_after"])
                    before = diag.get((llm, cond, run, cat, it - 1), [])
                    after = diag.get((llm, cond, run, cat, it), [])
                    same_diag = before == after
                    rows.append({"setting": setting, "llm": llm, "condition": cond, "run": run, "category": cat,
                                 "iteration": it, "stagnant_old": same_diag, "stagnant_new": same_diag and start == end})
    st = pd.DataFrame(rows)
    st.to_csv(out / "stagnation_per_iteration.csv.gz", index=False, compression="gzip")
    models = st.groupby(["setting", "llm", "condition", "run", "category"]).agg(old=("stagnant_old", "any"),
                                                                                new=("stagnant_new", "any")).reset_index()
    freq = models.groupby(["setting", "llm", "condition"]).agg(models_repaired=("old", "size"),
                                                               stagnant_models_old=("old", "sum"),
                                                               stagnant_models_new=("new", "sum")).reset_index()
    it = st.groupby(["setting", "llm", "condition"]).agg(iterations=("stagnant_old", "size"),
                                                         stagnant_iterations_old=("stagnant_old", "sum"),
                                                         stagnant_iterations_new=("stagnant_new", "sum")).reset_index()
    freq = freq.merge(it, on=["setting", "llm", "condition"])
    freq.to_csv(out / "stagnation_frequency.csv", index=False)
    write_md(out / "summary.md", "A14b. Stagnation (diagnostics and model unchanged) in every grammar-stage repair",
             [f"Iterations: {len(st)}; stagnant (old flag): {int(st.stagnant_old.sum())}; stagnant (new definition): "
              f"{int(st.stagnant_new.sum())}.", md_table(freq)])
    print(freq.to_string(index=False))


if __name__ == "__main__":
    main()
