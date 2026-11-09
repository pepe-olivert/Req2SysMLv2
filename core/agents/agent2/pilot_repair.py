"""C4P (R11): the repair loop of Algorithm 1 with the SysML v2 Pilot Implementation as validator.

Same loop as SysMLAgent.run_category under C2: one diagnostic per call (the first one the Pilot reports),
re-validation after every call, an iteration allows as many calls as it started with diagnostics, at most
`max_iterations` iterations, stagnation flagged but not stopping. Only Pilot ERROR issues count (warnings do not).
No router and no knowledge base. The repair message is the one of C2 (current diagnostic with line and column,
its code block, the current diagnostics, the complete file); the system prompt is FIX_SYSTEM_PROMPT with the
validator sentence changed (fix_pilot_prompt.md).

Guard: an answer that loses content (SysMLAgent.loses_content) or that our ANTLR validator rejects is retried
once with a warning and, if it fails again, rejected (the model is kept as before).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .logic import SysMLAgent

FIX_PILOT_SYSTEM_PROMPT = (Path(__file__).resolve().parent / "fix_pilot_prompt.md").read_text(encoding="utf-8")


def _signature(e: dict) -> str:
    return f"{e.get('line')}:{e.get('column')}:{e.get('error')}"


def pilot_diagnostics(agent: SysMLAgent, pilot, code: str) -> list[dict]:
    """Pilot ERROR issues in the record format of the loop (error, line, column, sysml_block, pilot_code)."""
    code = agent.clean_sysml(code)
    lines = code.splitlines()
    out = []
    for i in pilot.errors(code):
        line = i.get("line")
        out.append({"error": i["message"], "line": line, "column": i.get("column"), "pilot_code": i["code"],
                    "pilot_kind": i["kind"],
                    "sysml_block": agent._extract_block_by_indent(lines, line) if isinstance(line, int) else ""})
    return out


def run_pilot_repair(agent: SysMLAgent, pilot, code: str, max_iterations: int = 10) -> dict[str, Any]:
    agent.llm_client.reset()
    errors = pilot_diagnostics(agent, pilot, code)
    initial = len(errors)
    iterations_used = 0
    stagnation = False
    guard = {"retries_content": 0, "retries_antlr": 0, "rejections_content": 0, "rejections_antlr": 0}
    trace = [{"iteration": 0, "errors": [{k: e[k] for k in ("line", "column", "error", "pilot_code")} for e in errors]}]
    repairs = []

    def problem(before: str, candidate: str) -> tuple[str, str] | None:
        if agent.loses_content(before, candidate):
            return "content", (f"Your previous answer kept only {len(agent.clean_sysml(candidate).strip())} of the "
                               f"{len(agent.clean_sysml(before).strip())} characters of the file. Return the COMPLETE "
                               "file with every line, changing only what the CURRENT ERROR requires.")
        antlr = agent.validate_sysml(candidate)
        if antlr:
            e = antlr[0]
            return "antlr", (f"Your previous answer broke the SysML v2 grammar (parser error at line {e.get('line')}, "
                             f"column {e.get('column')}: {e.get('error')}). Return the COMPLETE file, valid for the "
                             "grammar, changing only what the CURRENT ERROR requires.")
        return None

    if errors:
        for iteration in range(1, max_iterations + 1):
            iterations_used = iteration
            start = {_signature(e) for e in errors}
            calls_left = len(errors)
            while errors and calls_left > 0:
                calls_left -= 1
                current = errors[0]

                def attempt(note: str = "") -> str:
                    message = agent.build_repair_message(code, current, errors, knowledge="", show_routing=False,
                                                         retry_note=note)
                    response = agent.llm_client.chat_with_metadata(messages=[
                        {"role": "developer", "content": FIX_PILOT_SYSTEM_PROMPT},
                        {"role": "user", "content": message}])
                    return response["content"].strip()

                candidate = attempt()
                retried_for = rejected_for = None
                p = problem(code, candidate)
                if p:
                    retried_for = p[0]
                    guard[f"retries_{p[0]}"] += 1
                    candidate = attempt(p[1])
                    p2 = problem(code, candidate)
                    if p2:
                        rejected_for = p2[0]
                        guard[f"rejections_{p2[0]}"] += 1
                before, errors_before = code, errors
                if not rejected_for:
                    code = agent.clean_sysml(candidate)
                    errors = pilot_diagnostics(agent, pilot, code)
                repairs.append({
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(), "iteration": iteration,
                    "current_error": {k: current[k] for k in ("line", "column", "error", "pilot_code")},
                    "guard_retried": retried_for, "guard_rejected": rejected_for,
                    "code_before": before, "code_after": candidate,
                    "errors_before": [{k: e[k] for k in ("line", "column", "error", "pilot_code")} for e in errors_before],
                    "errors_after": [{k: e[k] for k in ("line", "column", "error", "pilot_code")} for e in errors],
                })
            trace.append({"iteration": iteration,
                          "errors": [{k: e[k] for k in ("line", "column", "error", "pilot_code")} for e in errors]})
            if {_signature(e) for e in errors} == start:
                stagnation = True
            if not errors:
                break
    return {"sysml_code": code, "initial_error_count": initial, "final_error_count": len(errors),
            "final_errors": [{k: e[k] for k in ("line", "column", "error", "pilot_code")} for e in errors],
            "converged": not errors, "iterations_used": iterations_used, "stagnation_detected": stagnation,
            "guard": guard, "trace": trace, "repairs": repairs, "usage": agent.llm_client.snapshot()}
