"""R11 review packet (no LLM calls): the ten interface usage -> interface definition cases of R11, ready for a
human reviewer.

Same ten cases (seed 0) as results/analysis/r11_pilot_repair/interface_def_cases.md. Writes
results/analysis/r11_interface_review/:
- review_packet.html: self-contained page with the instructions and, per case, the requirements of the category,
  the interface before and after the repair, the connections of the repaired model, and both complete models with
  the relevant lines highlighted;
- review_sheet.xlsx and review_sheet.csv: one row per case, with empty answer columns for the reviewer;
- all_cases.csv and summary.md: for every one of the 538 cases, whether the interface is named outside its
  declaration before and after the repair, and the connect statements of the model before and after.

The answer columns are left empty: they are filled by a person, never by this script.

    python -m evaluation.analysis.r11_interface_review
"""

from __future__ import annotations

import difflib
import html
import re

import pandas as pd

from core.config import RESULTS_DIR
from evaluation.analysis.common import jsonl, md_table, out_dir, write_md
from evaluation.analysis.r11_pilot_repair import _COMMENT_RE, DOC, NAME, SRC, interface_def_cases

QUESTIONS = [
    ("Q1_connection_before", "yes / no / unclear",
     "Antes de la reparación, ¿el modelo (la interfaz junto con el resto del modelo) representa una conexión entre "
     "partes identificables?"),
    ("Q1_parts", "texto libre", "Si Q1 = yes: ¿entre qué partes (o puertos)?"),
    ("Q2_connection_after", "yes / no / unclear / n.a.",
     "Después de la reparación, ¿el modelo representa esa misma conexión entre esas partes (con un connect, con un "
     "uso de la interface def con extremos o de otra forma)? n.a. si Q1 = no."),
    ("Q3_requirement_worse", "yes / no / unclear",
     "¿Algún requisito de la categoría que la interfaz ayudaba a representar queda peor representado tras la "
     "reparación?"),
    ("Q3_requirements", "texto libre", "Si Q3 = yes: ¿cuál o cuáles? (copiar el texto o su número R1, R2...)"),
    ("comment", "texto libre", "Cualquier observación (por ejemplo, si el caso es ambiguo y por qué)."),
]

CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:1100px;margin:0 auto;padding:16px;
     color:#1a1a1a;background:#fff;line-height:1.45}
h1{font-size:1.5em} h2{font-size:1.25em;margin-top:2.2em;border-top:2px solid #ccc;padding-top:.8em}
h3{font-size:1.05em;margin-bottom:.3em}
pre{background:#f6f7f9;border:1px solid #dde;padding:8px;overflow-x:auto;font-size:12.5px;line-height:1.35}
.hl{background:#fff2a8;display:block} .add{background:#dff5e1;display:block} .del{background:#fbe1e1;display:block}
.box{background:#eef4fb;border-left:4px solid #3b78c4;padding:8px 12px;margin:10px 0}
.q{background:#fff8e6;border-left:4px solid #d39b00;padding:8px 12px;margin:10px 0}
table{border-collapse:collapse;font-size:14px} td,th{border:1px solid #ccc;padding:4px 8px;vertical-align:top}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:12px} @media(max-width:800px){.cols{grid-template-columns:1fr}}
details{margin:8px 0} summary{cursor:pointer;font-weight:600}
ol.reqs li{margin:2px 0}
"""

INTRO = """
<h1>Revisión de 10 casos: <code>interface</code> → <code>interface def</code> (etapa de referencia, R11)</h1>
<div class="box">
<p><b>Contexto.</b> Un LLM genera, a partir de requisitos en lenguaje natural, un modelo SysML&nbsp;v2 por categoría
de requisitos. Muchos modelos declaraban interfaces así:</p>
<pre>interface NetworkLink {
    flow networkData of String;
}</pre>
<p>Eso es un <i>uso</i> de interfaz sin extremos (<code>end</code>): la gramática lo acepta, pero la implementación de
referencia de SysML&nbsp;v2 (Pilot Implementation) lo rechaza, porque un uso de interfaz debe conectar al menos dos
elementos. Una etapa de reparación automática (otro LLM, guiado por los errores de la Pilot) lo convirtió en una
<i>definición</i> de interfaz (<code>interface def</code>), que sí es válida:</p>
<pre>interface def NetworkLink {
    end port source;
    end port target;
    flow networkData of String from source to target;
}</pre>
<p>Una <code>interface def</code> es un tipo: por sí sola no conecta nada. Solo hay conexión si en el modelo aparece
un <b>uso</b> de ella con extremos (p.&nbsp;ej. <code>interface : NetworkLink connect A.p to B.q;</code>) o una
sentencia <code>connect</code> / <code>connection ... connect X to Y;</code> entre las partes.</p>
<p><b>La pregunta.</b> ¿El modelo reparado sigue representando la conexión entre las partes que la interfaz original
pretendía conectar? Los 10 casos se eligieron al azar (semilla 0) entre los 538 en los que la reparación hizo este
cambio.</p>
</div>
<div class="q">
<p><b>Cómo hacerlo</b> (unos 5 minutos por caso):</p>
<ol>
<li>Lee los requisitos de la categoría (lista numerada R1, R2...). Los marcados con ★ son los que más palabras comparten
con la interfaz; es una pista automática, no una respuesta.</li>
<li>Mira la interfaz antes y después, y la lista de conexiones del modelo reparado.</li>
<li>Si hace falta, abre los modelos completos (desplegables al final de cada caso). Las líneas que nombran la interfaz,
las líneas <code>connect</code> y las <code>interface</code> están resaltadas en amarillo; en el diff, verde = añadido,
rojo = quitado.</li>
<li>Responde a las preguntas en la hoja <code>review_sheet.xlsx</code> (una fila por caso). Si algo no se puede decidir,
responde <i>unclear</i> y explica por qué en <code>comment</code>.</li>
</ol>
<p>No hace falta saber SysML en detalle: basta con decidir si, leyendo el modelo, se ve qué partes están conectadas y
si eso cambia tras la reparación.</p>
</div>
"""


def highlight(code: str, name: str) -> str:
    out = []
    pat = re.compile(rf"\b{re.escape(name)}\b|\bconnect\b|\binterface\b")
    for line in code.splitlines():
        e = html.escape(line) or " "
        out.append(f'<span class="hl">{e}</span>' if pat.search(line) else e)
    return "\n".join(out)


def diff_html(before: str, after: str) -> str:
    out = []
    for line in difflib.unified_diff(before.splitlines(), after.splitlines(), "before", "after", n=2, lineterm=""):
        e = html.escape(line) or " "
        if line.startswith("+") and not line.startswith("+++"):
            out.append(f'<span class="add">{e}</span>')
        elif line.startswith("-") and not line.startswith("---"):
            out.append(f'<span class="del">{e}</span>')
        else:
            out.append(e)
    return "\n".join(out) or "(sin cambios)"


def connects(code: str) -> int:
    """connect statements outside comments and doc text (as in interface_def_cases)."""
    return sum(1 for l in _COMMENT_RE.sub("", code).splitlines()
               if re.search(r"\bconnect\b", l) and not l.strip().startswith("doc"))


def references(code: str, name: str, declaration: str) -> int:
    """Lines outside comments that name the interface, other than its own declaration."""
    e = re.escape(name)
    return sum(1 for l in _COMMENT_RE.sub("", code).splitlines()
               if re.search(rf"\b{e}\b", l) and not re.search(declaration.format(e), l))


def all_cases(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for r in df.itertuples():
        for m in re.finditer(rf"(?m)^\s*(?:\w+\s+)*interface\s+(?!def\b)({NAME})", r.input_code):
            name, e = m.group(1), re.escape(m.group(1))
            if re.search(rf"\binterface\s+def\s+{e}\b", r.sysml_code) and \
                    not re.search(rf"\binterface\s+def\s+{e}\b", r.input_code):
                rows.append({"document": DOC[r.set], "llm": r.llm, "run": r.run, "category": r.category,
                             "interface": name,
                             "references_before": references(r.input_code, name, r"\binterface\s+{}\b"),
                             "references_after": references(r.sysml_code, name, r"\binterface\s+def\s+{}\b"),
                             "connect_before": connects(r.input_code), "connect_after": connects(r.sysml_code)})
    return pd.DataFrame(rows)


def main() -> None:
    out = out_dir("r11_interface_review")
    # Same rows, in the same order, as evaluation/analysis/r11_pilot_repair.py, so that seed 0 gives the same cases.
    res = pd.read_csv(SRC / "pilot_repair_results.csv")
    rows = {}
    for m in jsonl(SRC / "sysml_models.jsonl"):
        rows[(m["set"], m["llm"], int(m["run"]), m["category"])] = m
    models = pd.DataFrame([{**{k: m[k] for k in ("set", "pdf", "llm", "category", "input_code", "sysml_code",
                                                 "requirements")}, "run": int(m["run"])} for m in rows.values()])
    df = res.merge(models, on=["set", "pdf", "llm", "run", "category"])
    cases = interface_def_cases(df)
    full = {(r.set, r.llm, r.run, r.category): r for r in df.itertuples()}

    parts, sheet = [INTRO, "<h2>Índice</h2><table><tr><th>Caso</th><th>Documento</th><th>Modelo</th><th>Run</th>"
                    "<th>Categoría</th><th>Interfaz</th></tr>"], []
    for i, c in enumerate(cases, 1):
        parts.append(f'<tr><td><a href="#case{i}">{i}</a></td><td>{DOC[c["set"]]}</td><td>{c["llm"]}</td>'
                     f'<td>{c["run"]}</td><td>{html.escape(c["category"])}</td><td><code>{html.escape(c["interface"])}'
                     "</code></td></tr>")
    parts.append("</table>")
    for i, c in enumerate(cases, 1):
        r = full[(c["set"], c["llm"], c["run"], c["category"])]
        name = c["interface"]
        reqs = "".join(f"<li>{'★ ' if t in c['related_requirements'] else ''}{html.escape(t)}</li>"
                       for t in r.requirements)
        conns = "".join(f"<li><code>{html.escape(u)}</code></li>" for u in c["connects_after"]) or "<li>ninguna</li>"
        uses = "".join(f"<li><code>{html.escape(u)}</code></li>" for u in c["uses_after"]) or "<li>ninguna</li>"
        sat = "".join(f"<li><code>{html.escape(u)}</code></li>" for u in c["satisfy_mentioning_interface"]) \
            or "<li>ninguna</li>"
        n_conn = connects(r.sysml_code)
        parts.append(
            f'<h2 id="case{i}">Caso {i}: {DOC[c["set"]]} · {c["llm"]} · run {c["run"]} · '
            f'{html.escape(c["category"])} · interfaz <code>{html.escape(name)}</code></h2>'
            f"<h3>Requisitos de la categoría ({len(r.requirements)})</h3><ol class='reqs'>{reqs}</ol>"
            f"<div class='cols'><div><h3>Interfaz antes</h3><pre>{html.escape(c['before'])}</pre></div>"
            f"<div><h3>Interfaz después</h3><pre>{html.escape(c['after'])}</pre></div></div>"
            f"<h3>Otras líneas del modelo reparado que nombran <code>{html.escape(name)}</code></h3><ul>{uses}</ul>"
            f"<h3>Sentencias <code>connect</code> del modelo reparado ({n_conn} en total; se muestran hasta 8)</h3>"
            f"<ul>{conns}</ul>"
            f"<h3>Relaciones <code>satisfy</code> que nombraban la interfaz antes</h3><ul>{sat}</ul>"
            f"<details><summary>Cambios de la reparación en todo el modelo (diff)</summary>"
            f"<pre>{diff_html(r.input_code, r.sysml_code)}</pre></details>"
            f"<details><summary>Modelo completo antes de la reparación</summary>"
            f"<pre>{highlight(r.input_code, name)}</pre></details>"
            f"<details><summary>Modelo completo después de la reparación</summary>"
            f"<pre>{highlight(r.sysml_code, name)}</pre></details>")
        sheet.append({"case": i, "document": DOC[c["set"]], "llm": c["llm"], "run": c["run"],
                      "category": c["category"], "interface": name, **{q: "" for q, _, _ in QUESTIONS},
                      "reviewer": "", "date": ""})
    qrows = "".join(f"<tr><td><code>{q}</code></td><td>{html.escape(a)}</td><td>{html.escape(t)}</td></tr>"
                    for q, a, t in QUESTIONS)
    parts.insert(1, "<h2>Preguntas (columnas de la hoja)</h2><table><tr><th>Columna</th><th>Respuestas</th>"
                    f"<th>Pregunta</th></tr>{qrows}</table>")
    page = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>Revisión interface def</title>"
            f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>")
    (out / "review_packet.html").write_text(page, encoding="utf-8")
    sh = pd.DataFrame(sheet)
    sh.to_csv(out / "review_sheet.csv", index=False)
    with pd.ExcelWriter(out / "review_sheet.xlsx") as xw:
        sh.to_excel(xw, sheet_name="review", index=False)
        pd.DataFrame(QUESTIONS, columns=["column", "answers", "question"]).to_excel(xw, sheet_name="questions",
                                                                                   index=False)
    allc = all_cases(df)
    allc.to_csv(out / "all_cases.csv", index=False)
    s = pd.DataFrame([{"cases": len(allc), "named_elsewhere_before": int((allc.references_before > 0).sum()),
                       "named_elsewhere_after": int((allc.references_after > 0).sum()),
                       "models": int(allc[["document", "llm", "run", "category"]].drop_duplicates().shape[0]),
                       "cases_with_fewer_connect_after": int((allc.connect_after < allc.connect_before).sum()),
                       "cases_with_more_connect_after": int((allc.connect_after > allc.connect_before).sum())}])
    write_md(out / "summary.md", "R11: interface usages turned into interface definitions (all cases)",
             ["Named elsewhere: lines outside comments that name the interface, other than its declaration, in the "
              "model before (as an interface usage) and after the repair (as an interface definition). connect: "
              "statements outside comments.", md_table(s)])
    print(f"  wrote {out / 'review_packet.html'}, review_sheet.xlsx and review_sheet.csv ({len(cases)} cases)")


if __name__ == "__main__":
    main()
