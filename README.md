# Req2SysMLv2

Code of Req2SysMLv2, a generate-validate-repair framework that turns structured natural-language requirements into
SysML v2 models, and of the experiments and analyses of the paper that evaluates it.

A generation agent produces one model per requirement category. A grammar stage validates it with an ANTLR parser and
repairs each diagnostic with a knowledge base chosen by an error router. A reference stage then repairs it against the
SysML v2 Pilot Implementation. Two LLM judges assess each requirement afterwards.

**This repository contains code only.** It includes an invented example to try the pipeline, but none of the study
data; see [Data availability](#data-availability).

## How to cite

<!-- citation-start -->
Please cite the paper, and this software through the metadata in [CITATION.cff](CITATION.cff):

> Jose Francisco Olivert-Iserte, Eduardo Cibrián, Roy Mendieta, José María Álvarez-Rodríguez. *Beyond Parseability:
> Generating and Repairing SysML v2 Models from Industrial Requirements with LLMs.* Under review.
<!-- citation-end -->

## Structure

| Path | Contents |
|---|---|
| `core/agents/agent2/` | Generation and repair loop (`logic.py`), conditions C1-C4 and later ones, prompts, error router, Pilot repair loop |
| `core/agents/agent2/knowledge/` | Knowledge base of each error class |
| `core/validate/` | ANTLR validator; grammar and generated parser in `SysMLv2/` (LGPL-3.0, see [THIRD_PARTY.md](THIRD_PARTY.md)); bridge to the Pilot Implementation |
| `core/extraction/` | Extraction of requirements from PDF |
| `core/models.py`, `core/llm_client.py` | Model registry and the OpenRouter client |
| `evaluator/` | LLM-as-a-Judge Score (LJS), computed on stored models |
| `evaluation/` | Command-line scripts of each phase, tables and figures |
| `evaluation/analysis/` | Analyses of the stored results (no LLM calls) |
| `tools/pilot/` | Java programs that run the Pilot Implementation |
| `tests/` | Tests (need no key, documents or results) |
| `examples/` | **Invented** example, not data from the study |

[PAPER_ARTIFACTS.md](PAPER_ARTIFACTS.md) lists which script produces each table and figure of the paper, and what it
needs.

The frozen generation prompts, repair prompts, router and knowledge bases are pinned by the SHA-256 digests in
`tests/golden/frozen_files.json`, which `tests/test_frozen.py` checks. In the original repository the guided
generation prompt, the router and the knowledge bases were also fixed by the tag `frozen-prompt-kb`; this repository
has no earlier history, so the digests take its place.

## Installation

Tested with Python 3.10 on Linux. The pinned dependencies take about 6 GB, mostly PyTorch.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

The tests make no LLM calls. They need no key, but the first run of the pipeline downloads an embedding model
(all-MiniLM-L6-v2) and a tokenizer table.

For anything that calls an LLM, create a key at [OpenRouter](https://openrouter.ai) and add it to `.env`, which git
ignores:

```bash
cp .env.example .env    # then fill in OPENROUTER_API_KEY
python -m evaluation.list_models --check    # compares the model registry with the OpenRouter catalogue
```

The check exits with an error if a registered model is gone or its price has changed; that does not stop other commands.

Run every command from the repository root. Scripts write under `results/`, which git ignores.

## Run the invented example

`examples/greenhouse_requirements.json` describes a fictional irrigation controller, with 2 categories and 5
requirements. It is **invented and is not data from the study**.

```bash
# Plan and estimated cost; nothing is called
python -m evaluation.run_pipeline --requirements examples/greenhouse_requirements.json --out-dir results/example --models gpt-6-luna --conditions C1 C4 --runs 1 --dry-run

# Generation and repair
python -m evaluation.run_pipeline --requirements examples/greenhouse_requirements.json --out-dir results/example --models gpt-6-luna --conditions C1 C4 --runs 1 --workers 2 --max-rpm 18 --budget-usd 0.5

# Judge the stored models
python -m evaluator --input results/example/sysml_models.jsonl --out-dir results/example/ljs/gpt-4o-mini --workers 2 --max-rpm 18 --budget-usd 0.5
```

The cost should be around one cent at the prices of the study. Results are in `results/example/`:
`pipeline_results.csv`, `sysml_models.jsonl`, `valid_models/` and `ljs/gpt-4o-mini/ljs_results.csv`.

## Run the phases of the study

These commands need the key and, as stated for each one, data that are not in this repository. You can use the same
commands on your own requirements, with `--requirements` and a new `--out-dir`.

**Before any paid run, use `--dry-run` and set `--budget-usd`.** The phases can be resumed: running the same command
again skips what is done and does not pay for it twice.

**Rate limit.** New OpenRouter accounts are limited to 20 requests per minute per model, for the whole account. Use
`--max-rpm 18` and run only one process per model at a time. For long runs, use a local Linux disk.

### Extraction

Needs the source documents at `data/eirene.pdf` and `data/jwst.pdf`, which are not distributed with this repository:
obtain them from their publishers (UIC for the EIRENE Functional Requirements Specification, version 7; NASA for the
JWST Mission Requirements Document, Revision P; full references in the paper). Other documents: add them to
`DOCUMENTS` in `core/config.py`.

```bash
python -m evaluation.run_extraction --models all --runs 3 --workers 4 --max-rpm 18
python -m evaluation.run_extraction --select-best-only --best-file eirene_sliding_window_gpt-6-luna_run1.json
python -m evaluation.input_coverage
python -m evaluation.input_coverage --summarize --annotations results/extraction/manual_validation_sample_completed.csv
python -m evaluation.make_input --run-file jwst_sliding_window_gpt-6-luna_run1.json --out results/jwst_pipeline/input_requirements.json
```

### Pipeline and ablation

Read `results/extraction/best_requirements.json`, or the file given in `--requirements`.

```bash
python -m evaluation.run_pipeline --models all --conditions C1 C4 --runs 3 --dry-run
python -m evaluation.run_pipeline --models all --conditions C1 C4 --runs 3 --workers 8 --max-rpm 18 --budget-usd 40
python -m evaluation.run_pipeline --requirements results/jwst_pipeline/input_requirements.json --out-dir results/jwst_pipeline --models all --conditions C1 C4 --runs 3 --workers 24 --max-rpm 18
python -m evaluation.run_pipeline --generation-prompt c0_minimal --out-dir results/c0_minimal_prompt --models gpt-6-luna --conditions C1 C4 --runs 3
python -m evaluation.run_ablation --model gpt-6-luna --runs 3 --workers 8 --max-rpm 18 --budget-usd 10
```

### Ablation on error banks

Repairs stored generations and generates nothing. Needs the banks, which are available on request.

```bash
python -m evaluation.run_ablation_stress --seed-from <generations.jsonl of the bank> --runs 3 --workers 8 --max-rpm 18 --budget-usd 8
python -m evaluation.run_ablation_stress --out-dir results/ablation_stress_revision --seed-from results/ablation_stress/generations.jsonl --conditions C1 C2KB FULLREV --runs 3
```

### Judges (LJS)

Read stored models.

```bash
python -m evaluator --phase pipeline --dry-run
python -m evaluator --phase pipeline --workers 10 --max-rpm 18 --budget-usd 5
python -m evaluator --phase ablation --workers 10 --max-rpm 18 --budget-usd 2
python -m evaluation.nodoc_control --source results/pipeline/sysml_models.jsonl --conditions C4 --out-dir results/nodoc_control/pipeline_c4
python -m evaluator --input results/nodoc_control/pipeline_c4/sysml_models.jsonl --out-dir results/nodoc_control/pipeline_c4/ljs/gpt-4o-mini --workers 10 --max-rpm 18
python -m evaluator --input results/pipeline/sysml_models.jsonl --conditions C4 --out-dir results/second_judge/pipeline_c4/ljs/claude-haiku-5.5 --judge claude-haiku-5.5
```

### Reference stage (C4P)

Needs the stored models and the [Pilot Implementation](#sysml-v2-pilot-implementation).

```bash
python -m evaluation.run_pilot_repair --sets E5 --models gpt-6-luna --limit 20 --dry-run
python -m evaluation.run_pilot_repair --sets E5 --models gpt-6-luna --limit 20 --workers 6 --max-rpm 18 --budget-usd 1
```

### Tables and figures (no LLM calls)

```bash
python -m evaluation.revision_summary
python -m evaluation.make_paper_artifacts
python -m evaluation.make_paper_tables
python -m evaluation.make_supplement_tables
```

### Cost of the experiments

Cost recorded in the study, in USD, at the prices of late 2026. A rerun will differ. Calls that failed and were not
stored (for example, judgments rejected after three attempts) are not counted, so the real spend was somewhat higher.

| Experiment | Models | Recorded cost |
|---|---|---|
| Extraction, 2 documents, 2 strategies, 4 models, 3 runs (48 runs) | Candidates | 5.45 |
| E1: pipeline on the first document, C1 and C4 | 4 candidates | 11.43 |
| E2: ablation C1-C4 | gpt-6-luna | 0.38 |
| E3: ablation on the error bank (repair only) | gpt-6-luna, gemini-3.5-flash-lite | 7.22 |
| LJS of E1-E3 | gpt-4o-mini | 3.13 |
| E5: pipeline on the second document, with LJS | 4 candidates, gpt-4o-mini | 15.03 |
| C2KB and FULLREV on the E3 bank, with LJS | gpt-6-luna, gemini-3.5-flash-lite, gpt-4o-mini | 2.83 |
| Input control, with LJS | 4 candidates, gpt-4o-mini | 5.54 |
| E4: minimal prompt (C0), with LJS | gpt-6-luna, gpt-4o-mini | 0.82 |
| LJS without doc comments | gpt-4o-mini | 3.37 |
| Second judge | claude-haiku-5.5 | 14.12 |
| Out-of-sample error bank, generation, repair and LJS | gpt-6-luna, gpt-4o-mini | 2.11 |
| Out-of-sample error bank, generation, repair and LJS | gemini-3.5-flash-lite, gpt-4o-mini | 7.05 |
| Reference stage (C4P), with LJS | gpt-6-luna, gemini-3.5-flash-lite, both judges | 15.71 |
| **Total** | | **about 94** |

### Results will not be identical

OpenRouter identifiers are **not pinned versions**: the same identifier may later serve another version of a model,
another provider or another price, or stop existing. Generation is also not deterministic. Reruns show the method, but
they will not reproduce the published numbers exactly. To reanalyse the published numbers, ask for the stored results.

## SysML v2 Pilot Implementation

The reference stage and the acceptance analyses use releases **2024-04.1** and **2026-08** of the
[Pilot Implementation](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation). It is not included. You
need a JDK (tested with OpenJDK 23) and these steps:

```bash
mkdir -p ~/tools/pilot/2024-04.1 ~/tools/pilot/2026-08

cd ~/tools/pilot/2024-04.1
curl -LO https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/releases/download/2024-04.1/jupyter-sysml-kernel-0.41.1.zip
unzip -q jupyter-sysml-kernel-0.41.1.zip

cd ~/tools/pilot/2026-08
curl -LO https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/releases/download/2026-08/jupyter-sysml-kernel-0.62.0.zip
unzip -q jupyter-sysml-kernel-0.62.0.zip
```

Each release must end up with `sysml/jupyter-sysml-kernel-*-all.jar` and `sysml/sysml.library/`. The scripts look in
`~/tools/pilot`; to use another location, pass `--pilot-root` or, for `evaluation.run_pilot_repair`, `--pilot-release`.
`tools/pilot/*.java` are compiled on first use into `tools/pilot/build/`.

Scripts that use it: `evaluation.run_pilot_repair` and the analyses `a01_tool_acceptance`, `a01b_boilerplate`,
`a14_guard_rejections`, `a15_extended_b`, `a17_ref_equivalence` and `r11_pilot_repair`.

## Data availability

The source documents are not included; they are published by UIC (EIRENE) and NASA (JWST), and the paper gives
their full references.

The following are **not included** and are available on request from jolivert@inf.uc3m.es:

- the input requirements;
- the generated and repaired models;
- the error banks;
- the judgments;
- the annotation sheets.

Scripts that need them stop with a message saying what is missing, without calling any LLM.

## Licence

Apache-2.0 ([LICENSE](LICENSE)), except `core/validate/SysMLv2/`, which is under LGPL-3.0. See
[THIRD_PARTY.md](THIRD_PARTY.md).
