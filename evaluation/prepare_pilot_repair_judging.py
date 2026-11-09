"""R11: inputs of the LJS-after judgments (no LLM calls).

From results/pilot_repair/sysml_models.jsonl keeps the models the C4P loop changed, removes their doc comments
(and comments with requirement text) exactly as the no-doc control (evaluation/nodoc_control.py), and writes:
- results/pilot_repair/nodoc/sysml_models.jsonl  every changed model (judged with gpt-4o-mini);
- results/pilot_repair/nodoc/haiku_sample.jsonl  a stratified random sample of SAMPLE changed models, balanced
  by model and document (seed 0), judged with claude-haiku-5.5.
Unchanged models keep their no-doc LJS of before (the loop did not touch them; only the import lines differ).

    python -m evaluation.prepare_pilot_repair_judging
"""

from __future__ import annotations

import json
import random

from core.agents.agent2.logic import SysMLAgent
from core.config import RESULTS_DIR
from evaluation.common import write_run_manifest
from evaluation.nodoc_control import strip_requirement_text

SRC = RESULTS_DIR / "pilot_repair"
OUT = SRC / "nodoc"
SAMPLE = 150
SEED = 0


def main() -> None:
    agent = SysMLAgent.__new__(SysMLAgent)
    last = {}
    for line in (SRC / "sysml_models.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            last[(r["set"], r["llm"], int(r["run"]), r["category"])] = r
    changed, excluded = [], 0
    for r in last.values():
        if r["sysml_code"] == r["input_code"]:
            continue
        stripped, removed = strip_requirement_text(r["sysml_code"], r["requirements"])
        if agent.validate_sysml(stripped):
            excluded += 1
            continue
        changed.append({"pdf": r["pdf"], "llm": r["llm"], "condition": "C4P", "run": r["run"], "category": r["category"],
                        "set": r["set"], "requirements_sha256": r["requirements_sha256"], "requirements": r["requirements"],
                        "sysml_code": stripped, "valid": True, "nodoc": True, "removed": removed})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sysml_models.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in changed),
                                            encoding="utf-8")
    strata = {}
    for m in changed:
        strata.setdefault((m["set"], m["llm"]), []).append(m)
    rng = random.Random(SEED)
    keys = sorted(strata)
    per = {k: SAMPLE // len(keys) for k in keys}
    for k in keys[: SAMPLE - sum(per.values())]:
        per[k] += 1
    sample = []
    for k in keys:
        pool = sorted(strata[k], key=lambda m: (m["run"], m["category"]))
        sample += rng.sample(pool, min(per[k], len(pool)))
    (OUT / "haiku_sample.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in sample),
                                            encoding="utf-8")
    write_run_manifest(OUT, n_changed=len(changed), excluded_invalid_after_strip=excluded, sample=len(sample),
                       seed=SEED, strata={f"{s}/{l}": len(v) for (s, l), v in strata.items()})
    print(f"changed models: {len(changed)} (+{excluded} excluded: invalid after stripping doc); "
          f"haiku sample: {len(sample)} {[(k, min(per[k], len(strata[k]))) for k in keys]}")


if __name__ == "__main__":
    main()
