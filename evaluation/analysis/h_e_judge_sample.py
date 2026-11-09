"""Sample for the human evaluation of the LJS judges (no LLM calls).

48 requirements for two annotators, blind to the candidate model and to both judges: 24 of EIRENE (E1) and 24 of JWST
(E5), 6 per candidate model and document, each from a different category of its document, all from the final C4
models without doc comments (the main LJS measure). Only models and requirements with a verdict of both judges
(gpt-4o-mini and claude-haiku-5.5) are eligible. The sample does not look at the verdicts, so it can estimate the
agreement of each judge with the annotators without reweighting. Seed 0.

Writes data/h_e_judge_sample/:
- README.md: protocol and definitions (the same as the judge prompt);
- annotation_packet.html: per case, the requirements of the category (the one to judge marked) and the SysML code that
  the judges saw; neither the candidate model nor the run is shown, and the cases are shuffled;
- annotation_sheet_A.xlsx, annotation_sheet_B.xlsx and annotation_sheet.csv: one row per case, empty answer columns;
- key/sample_key.csv: candidate model, run, judgment keys and both judges' verdicts per case. Not for the annotators.

The answer columns are left empty: they are filled by people, never by this script.

    python -m evaluation.analysis.h_e_judge_sample
"""

from __future__ import annotations

import html
import random

import pandas as pd

from core.config import DATA_DIR, RESULTS_DIR
from evaluation.analysis.common import IEEE, MODEL_ORDER, jsonl, md_table
from evaluator.__main__ import judgment_key
from evaluator.semantic_judge import requirement_ids

SEED = 0
PER_MODEL = 6
JUDGES = ["gpt-4o-mini", "claude-haiku-5.5"]
SETS = [("EIRENE", RESULTS_DIR / "nodoc_control" / "pipeline_c4"),
        ("JWST", RESULTS_DIR / "nodoc_control" / "jwst_pipeline_c4")]
OUT = DATA_DIR / "h_e_judge_sample"

ANSWERS = [
    ("correctness", "yes / no", "¿El requisito está representado con exactitud en el modelo?"),
    ("completeness", "yes / no", "¿Todos los aspectos del requisito están cubiertos en el modelo?"),
    ("unambiguity", "yes / no", "¿La correspondencia entre el requisito y los elementos del modelo es clara e inequívoca?"),
    ("verifiability", "yes / no", "¿Se podría comprobar objetivamente el requisito a partir de la definición del modelo?"),
    ("traceability", "yes / no", "¿Se pueden señalar elementos explícitos del modelo que satisfacen el requisito?"),
    ("status", "satisfied / partial / missing / not_applicable",
     "Estado global: satisfied (los cinco atributos sí), partial (alguno no), missing (todos no), not_applicable."),
    ("evidence", "texto libre", "Elementos del modelo en los que te basas (nombres de part, attribute, satisfy...)."),
    ("comment", "texto libre", "Cualquier observación (por ejemplo, si el caso es dudoso y por qué)."),
]

CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:1100px;margin:0 auto;padding:16px;
     color:#1a1a1a;background:#fff;line-height:1.45}
h1{font-size:1.5em} h2{font-size:1.25em;margin-top:2.2em;border-top:2px solid #ccc;padding-top:.8em}
h3{font-size:1.05em;margin-bottom:.3em}
pre{background:#f6f7f9;border:1px solid #dde;padding:8px;overflow-x:auto;font-size:12.5px;line-height:1.35}
.box{background:#eef4fb;border-left:4px solid #3b78c4;padding:8px 12px;margin:10px 0}
.q{background:#fff8e6;border-left:4px solid #d39b00;padding:8px 12px;margin:10px 0}
.target{background:#fff2a8;font-weight:600}
table{border-collapse:collapse;font-size:14px} td,th{border:1px solid #ccc;padding:4px 8px;vertical-align:top}
ol.reqs li{margin:2px 0}
"""

PROTOCOL = """
<div class="box">
<p><b>Contexto.</b> Un LLM generó, a partir de requisitos en lenguaje natural, un modelo SysML&nbsp;v2 por categoría de
requisitos. Un juez LLM puntuó después cada requisito frente al modelo. Esta muestra sirve para medir el acuerdo entre
dos anotadores humanos y el de cada juez con ellos.</p>
<p>Cada caso muestra los requisitos de la categoría y el código SysML&nbsp;v2 tal como lo vio el juez (sin los
comentarios <code>doc</code> ni los comentarios que copiaban el texto de los requisitos). Se evalúa un único requisito
por caso, marcado en amarillo; los demás se muestran porque el modelo los cubre a la vez.</p>
</div>
<div class="q">
<p><b>Cómo hacerlo</b> (unos 5 minutos por caso):</p>
<ol>
<li>Cada anotador trabaja solo, sin hablar de los casos con el otro hasta que los dos hayan terminado.</li>
<li>No abras la carpeta <code>key/</code> ni otros resultados del repositorio antes de terminar: contienen el modelo
generador y los veredictos de los jueces.</li>
<li>Lee el requisito marcado y el código. Responde a los cinco atributos (yes/no) y al estado global en tu hoja
(<code>annotation_sheet_A.xlsx</code> o <code>annotation_sheet_B.xlsx</code>), una fila por caso.</li>
<li>El estado se deriva de los atributos como en el juez: satisfied si los cinco son yes, missing si los cinco son no,
partial en otro caso; not_applicable solo si el requisito no puede representarse en un modelo de sistema.</li>
<li>Juzga lo que dice el modelo, no lo que podría haber querido decir: un elemento que solo tiene el nombre adecuado,
sin atributos ni relaciones que lo concreten, no cubre por sí solo los aspectos cuantitativos del requisito.</li>
</ol>
</div>
"""


def verdicts(phase_dir, judge: str) -> dict[str, dict[str, dict]]:
    return {j["judgment_key"]: {p["req_id"]: p for p in j["per_requirement"]}
            for j in jsonl(phase_dir / "ljs" / judge / "judgments.jsonl")}


def sample() -> list[dict]:
    rng = random.Random(SEED)
    cases = []
    for document, phase_dir in SETS:
        judged = [verdicts(phase_dir, j) for j in JUDGES]
        eligible: dict[str, dict[str, list[dict]]] = {}
        for m in jsonl(phase_dir / "sysml_models.jsonl"):
            key = judgment_key(m["requirements"], m["sysml_code"])
            if not all(key in v for v in judged):
                continue
            ids = [rid for rid in requirement_ids(m["requirements"])
                   if all(v[key].get(rid, {}).get("status") not in (None, "not_applicable") for v in judged)]
            if ids:
                eligible.setdefault(m["category"], {}).setdefault(m["llm"], []).append({**m, "key": key, "ids": ids})
        # Categories with eligible models of all four candidates, drawn without replacement and dealt to the models.
        categories = sorted(c for c, by in eligible.items() if all(llm in by for llm in MODEL_ORDER))
        drawn = rng.sample(categories, PER_MODEL * len(MODEL_ORDER))
        for i, category in enumerate(drawn):
            llm = MODEL_ORDER[i % len(MODEL_ORDER)]
            m = rng.choice(sorted(eligible[category][llm], key=lambda r: r["run"]))
            rid = rng.choice(m["ids"])
            cases.append({"document": document, "model": m, "req_id": rid,
                          "verdicts": {j: v[m["key"]][rid] for j, v in zip(JUDGES, judged)}})
    rng.shuffle(cases)
    return cases


def packet(cases: list[dict]) -> str:
    parts = ["<h1>Evaluación humana del juez LJS: 48 requisitos</h1>", PROTOCOL,
             "<h2>Preguntas (columnas de la hoja)</h2><table><tr><th>Columna</th><th>Respuestas</th><th>Pregunta</th>"
             "</tr>" + "".join(f"<tr><td><code>{c}</code></td><td>{html.escape(a)}</td><td>{html.escape(q)}</td></tr>"
                               for c, a, q in ANSWERS) + "</table>",
             "<h2>Índice</h2><table><tr><th>Caso</th><th>Documento</th><th>Categoría</th><th>Requisito</th></tr>"]
    for i, c in enumerate(cases, 1):
        parts.append(f'<tr><td><a href="#case{i}">{i}</a></td><td>{c["document"]}</td>'
                     f'<td>{html.escape(c["model"]["category"])}</td><td>{c["req_id"]}</td></tr>')
    parts.append("</table>")
    for i, c in enumerate(cases, 1):
        m = c["model"]
        reqs = "".join(f'<li{" class=target" if rid == c["req_id"] else ""}>{rid}. {html.escape(t)}</li>'
                       for rid, t in zip(requirement_ids(m["requirements"]), m["requirements"]))
        target = m["requirements"][int(c["req_id"][1:]) - 1]
        parts.append(f'<h2 id="case{i}">Caso {i}: {c["document"]} · {html.escape(m["category"])} · '
                     f'{c["req_id"]}</h2>'
                     f'<div class="q"><b>Requisito a evaluar ({c["req_id"]}):</b> {html.escape(target)}</div>'
                     f"<h3>Requisitos de la categoría ({len(m['requirements'])})</h3><ol class='reqs'>{reqs}</ol>"
                     f"<h3>Modelo SysML v2</h3><pre>{html.escape(m['sysml_code'])}</pre>")
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>Evaluación humana LJS</title>"
            f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>")


def readme(cases: list[dict]) -> str:
    counts = pd.crosstab(pd.Series([c["document"] for c in cases], name="document"),
                         pd.Series([c["model"]["llm"] for c in cases], name="candidate model"))
    return f"""# Human evaluation of the LJS judges

Generated by `python -m evaluation.analysis.h_e_judge_sample` (no LLM calls, seed {SEED}). Do not edit by hand.

## For the annotators

Open `annotation_packet.html`, read the instructions at the top and fill in your own sheet:
annotator A `annotation_sheet_A.xlsx`, annotator B `annotation_sheet_B.xlsx` (`annotation_sheet.csv` is the same
empty sheet as CSV). Work independently and **do not open `key/`** (or any other result of the repository) until both
of you have finished: it contains the generating model and the verdicts of the judges.

Per case: the five quality attributes (yes/no) and the overall status, with the same definitions as the judge prompt
(`evaluator/prompts.py`): satisfied if all five hold, missing if none holds, partial otherwise; not_applicable only if
the requirement cannot be represented in a system model.

## Sample

- {len(cases)} requirements: one per (document, category) from the final C4 models of E1 (EIRENE) and E5 (JWST) with the
  doc comments and the comments containing requirement text removed (`results/nodoc_control/pipeline_c4` and
  `results/nodoc_control/jwst_pipeline_c4`), which is the main LJS measure.
- Stratified by document and candidate model ({PER_MODEL} per cell); categories drawn without replacement among those
  with an eligible model of every candidate, then a run and a requirement drawn at random.
- Eligible: models judged by both judges ({", ".join(JUDGES)}) and requirements that neither judge marked
  not_applicable. The judges' verdicts are not used to draw the sample, so agreement with the annotators needs no
  reweighting.
- The cases are shuffled; the packet shows the document and the category (visible from the requirements anyway) but
  not the candidate model, the run or any verdict.

{md_table(counts.reset_index())}

## Key (`key/sample_key.csv`)

Per case: candidate model, run, category, requirement id, `judgment_key` (as in each judge's `judgments.jsonl`) and
both judges' status and attributes. Planned analysis: Cohen's kappa between the annotators (status and each attribute),
and the agreement of each judge with each annotator and with the consensus of both.
"""


def main() -> None:
    cases = sample()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "key").mkdir(exist_ok=True)
    (OUT / "annotation_packet.html").write_text(packet(cases), encoding="utf-8")
    (OUT / "README.md").write_text(readme(cases), encoding="utf-8")
    sheet = pd.DataFrame([{"case": i, "document": c["document"], "category": c["model"]["category"],
                           "req_id": c["req_id"],
                           "requirement": c["model"]["requirements"][int(c["req_id"][1:]) - 1],
                           **{a: "" for a, _, _ in ANSWERS}, "annotator": "", "date": ""}
                          for i, c in enumerate(cases, 1)])
    sheet.to_csv(OUT / "annotation_sheet.csv", index=False)
    for who in ("A", "B"):
        with pd.ExcelWriter(OUT / f"annotation_sheet_{who}.xlsx") as xw:
            sheet.assign(annotator=who).to_excel(xw, sheet_name="annotation", index=False)
            pd.DataFrame(ANSWERS, columns=["column", "answers", "question"]).to_excel(xw, sheet_name="questions",
                                                                                     index=False)
    key = []
    for i, c in enumerate(cases, 1):
        m = c["model"]
        row = {"case": i, "document": c["document"], "pdf": m["pdf"], "llm": m["llm"], "condition": m["condition"],
               "run": m["run"], "category": m["category"], "req_id": c["req_id"],
               "n_requirements": len(m["requirements"]), "judgment_key": m["key"],
               "source": str((dict(SETS)[c["document"]] / "sysml_models.jsonl").relative_to(RESULTS_DIR.parent))}
        for j, v in c["verdicts"].items():
            row[f"{j}_status"] = v["status"]
            row.update({f"{j}_{a}": v["ieee830"][a] for a in IEEE})
        key.append(row)
    pd.DataFrame(key).to_csv(OUT / "key" / "sample_key.csv", index=False)
    print(f"  wrote {OUT} ({len(cases)} cases)")


if __name__ == "__main__":
    main()
