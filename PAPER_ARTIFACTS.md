# Which script produces each table and figure of the paper

Tables and figures are identified by their LaTeX label. Scripts run as `python -m <module>`, from the repository root.

**None of the data these scripts read are in this repository.** Availability of what each row needs:

| Mark | Needs |
|---|---|
| **none** | Nothing: written by hand in the paper; no script. |
| **R** | Stored results of the study, available on request (see Data availability in [README.md](README.md)), placed under `results/`. |
| **A** | Also the human annotation sheets, available on request. |
| **P** | Also the Pilot Implementation, installed as explained in [README.md](README.md). No LLM calls. |

The scripts make no LLM calls: they only read what the phases of the README stored. Without their inputs they stop
with a message that names what is missing.

## Paper

| Label | Script | Reads (under `results/` unless noted) | Needs |
|---|---|---|---|
| `tab:related`, `tab:error_categories`, `tab:conditions`, `tab:rq_summary`, `tab:lessons`, `fig:architecture` | None (hand-written) | - | none |
| `fig:repair_example`, `fig:richness_example` | `evaluation.analysis.a12_paper_examples` | `jwst_v1_bank_flashlite`, `pipeline`, `c0_minimal_prompt` | R |
| `tab:models` | `evaluation.make_paper_tables` | `analysis/a19_tokens` (from `evaluation.analysis.a19_tokens`) | R |
| `tab:experiments` | `evaluation.make_paper_tables` | Results, manifests and judgments of every phase | R |
| `tab:validity` | `evaluation.make_paper_tables` | `analysis/{a01_tool_acceptance, a01b_boilerplate, a15_extended_b, r11_pilot_repair, a02_richness}`, results of every model set | R, P |
| `tab:semantics` | `evaluation.make_paper_tables` | `analysis/a04_cluster_stats`, LJS of `nodoc_control` and `second_judge` | R |
| `tab:ranking` | `evaluation.make_paper_tables` | `analysis/a04_cluster_stats` | R |
| `tab:ablation_unified`, `tab:ablation_unified_tests` | `evaluation.analysis.a11_ablation_unified` | `ablation_stress`, `ablation_stress_revision`, `jwst_v1_bank`, `jwst_v1_bank_flashlite` | R |
| `tab:c4p` | `evaluation.make_paper_tables` | `analysis/{r11_pilot_repair, a14_guard_rejections}` | R, P |
| `tab:cost` | `evaluation.make_paper_tables` | `pilot_repair`, `extraction/runs`, results of `pipeline` and `jwst_pipeline` | R |
| `tab:repair_semantics` | `evaluation.make_paper_tables` | Results and LJS of the repaired phases, `analysis/r11_pilot_repair`, `pilot_repair/nodoc` | R, P |

## Supplementary Material

| Label | Script | Reads (under `results/` unless noted) | Needs |
|---|---|---|---|
| `tab:sup_extraction`, `tab:sup_jaccard` | `evaluation.make_supplement_tables` | `extraction/extraction_results.csv`, `extraction/extraction_agreement.csv` | R |
| `fig:sup_pareto` | `evaluation.make_paper_artifacts` | `extraction/extraction_results.csv` | R |
| `tab:extraction_truncation` | `evaluation.analysis.a06_extraction_truncation` | `extraction/runs` | R |
| `tab:sup_input_coverage` | `evaluation.make_supplement_tables` | `extraction/input_coverage.csv` (from `evaluation.input_coverage`) | R |
| `tab:manual_validation` | `evaluation.input_coverage --summarize` | `extraction/manual_validation_sample_completed.csv` | R, A |
| `tab:extraction_agreement` | `evaluation.analysis.a22_extraction_agreement` | `extraction/manual_validation_sample_completed.csv` | R, A |
| `tab:sup_attributes` | `evaluation.make_supplement_tables` | LJS of `nodoc_control` and `second_judge` | R |
| `tab:sup_kappa` | `evaluation.make_supplement_tables` | `revision_summary/kappa.csv` (from `evaluation.revision_summary`) | R |
| `tab:judge_human` | `evaluation.analysis.a23_judge_human_agreement` | `data/h_e_judge_sample/` (sample from `evaluation.analysis.h_e_judge_sample`, filled sheets) | R, A |
| `tab:not_applicable` | `evaluation.analysis.a05_not_applicable` | LJS of every phase | R |
| `tab:richness_ljs` | `evaluation.analysis.a02_richness` | Models and LJS of every model set | R |
| `tab:missing_bounds` | `evaluation.analysis.a13_missing_judgments` | Models and LJS of `nodoc_control` and `second_judge` | R |
| `tab:cluster_means`, `tab:cluster_tests` | `evaluation.analysis.a04_cluster_stats` | Results and LJS of `pipeline`, `jwst_pipeline`, `nodoc_control`, `second_judge` | R |
| `tab:e1_e2_variability` | `evaluation.analysis.a10_e1_e2_variability` | Results and errors of `pipeline`, `ablation` | R |
| `tab:ablation_tests` | `evaluation.make_paper_artifacts` | `ablation` | R |
| `tab:repair_diff` | `evaluation.analysis.a03_repair_diff` | Models of the repaired sets | R |
| `tab:block_localisation` | `evaluation.analysis.a08_block_localisation` | Repair records of the repaired sets | R |
| `tab:constraint_expr_answers` | `evaluation.analysis.a07_c3_vs_c2` | `ablation_stress`, `ablation_stress_revision` | R |
| Case listing of the section `sec:s-c3` (no label) | `evaluation.make_supplement_tables` | `analysis/a07_c3_vs_c2/c3_vs_c2_cases.md` | R |
| `tab:tool_acceptance` | `evaluation.analysis.a01b_boilerplate`, after `a01_tool_acceptance` | Models of every set | R, P |
| `tab:sup_pilot_errors`, `tab:sup_prompt_kb_examples` | `evaluation.make_supplement_tables` | `analysis/{a01b_boilerplate, a15_extended_b, a14_guard_rejections}` | R, P |
| `tab:sup_guard_rejections` | `evaluation.make_supplement_tables` | `analysis/a14_guard_rejections` | R, P |
| `tab:sup_pilot_2026` | `evaluation.make_supplement_tables` | `analysis/a15_extended_b` | R, P |
| Interface case listing (no label) | `evaluation.make_supplement_tables` | `analysis/r11_pilot_repair/interface_def_cases.md`, `analysis/r11_interface_review/review_sheet_completed.csv` | R, A, P |
| `tab:sup_ref_equivalence` | `evaluation.make_supplement_tables` | `analysis/a17_ref_equivalence/references.csv` | R, P |
| `tab:sup_tokens` | `evaluation.analysis.a19_tokens` | `extraction`, results of every phase, `pilot_repair` | R |

## Notes

- **Order:** run the `evaluation.analysis.*` scripts before `evaluation.make_paper_tables` and
  `evaluation.make_supplement_tables`, which read their outputs. `evaluation.analysis.r11_pilot_repair` needs
  `a15_extended_b`.
- `evaluation.export_supplement_overleaf` only copies existing tables into the layout of the LaTeX project. It reads
  the source of the Supplementary Material, which is not distributed.
- `tab:experiments` takes the dates of the first runs, which predate the run manifests, from the git history of the
  original repository. In this repository, which has no such history, those dates come out empty.
