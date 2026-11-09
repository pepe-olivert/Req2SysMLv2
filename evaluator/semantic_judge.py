"""SemanticJudge: one LLM call that labels every requirement of a category against its SysML v2 model."""

from __future__ import annotations

import json
import logging

from core.extraction.json_utils import parse_json_object

from .prompts import IEEE830_ATTRIBUTES, JUDGE_SYSTEM_PROMPT, JUDGE_USER_TEMPLATE, STATUSES


logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


class InvalidJudgment(ValueError):
    """The judge answered, but not with one valid verdict per requirement."""


def requirement_ids(requirements: list[str]) -> list[str]:
    return [f"R{i}" for i in range(1, len(requirements) + 1)]


def build_messages(requirements: list[str], sysml_code: str) -> list[dict]:
    items = [{"id": rid, "text": text} for rid, text in zip(requirement_ids(requirements), requirements)]
    return [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": JUDGE_USER_TEMPLATE.format(
            sysml_code=sysml_code, requirements=json.dumps(items, ensure_ascii=False, indent=2))},
    ]


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    raise InvalidJudgment(f"not a boolean: {value!r}")


def parse_judgment(content: str, requirements: list[str]) -> dict:
    """Strict parse: exactly one verdict per requirement id, a known status and the five IEEE 830 booleans."""
    try:
        payload = parse_json_object(content)
    except json.JSONDecodeError as exc:
        raise InvalidJudgment(str(exc)) from None
    items = payload.get("per_requirement")
    if not isinstance(items, list):
        raise InvalidJudgment("missing per_requirement list")

    expected = requirement_ids(requirements)
    verdicts: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            raise InvalidJudgment(f"verdict is not an object: {item!r}")
        rid = str(item.get("req_id", "")).strip()
        if rid not in expected or rid in verdicts:
            raise InvalidJudgment(f"unexpected or repeated req_id {rid!r}")
        status = str(item.get("status", "")).strip().lower()
        if status not in STATUSES:
            raise InvalidJudgment(f"{rid}: unknown status {status!r}")
        ieee = item.get("ieee830")
        if not isinstance(ieee, dict):
            raise InvalidJudgment(f"{rid}: missing ieee830")
        attributes, justifications = {}, {}
        for attr in IEEE830_ATTRIBUTES:
            entry = ieee.get(attr)
            value = entry.get("value") if isinstance(entry, dict) else entry
            # A not_applicable requirement is left out of every score, so its attributes may be null.
            attributes[attr] = None if value is None and status == "not_applicable" else _as_bool(value)
            justifications[attr] = entry.get("justification", "") if isinstance(entry, dict) else ""
        evidence = item.get("matched_model_evidence") or []
        verdicts[rid] = {
            "req_id": rid,
            "requirement": requirements[expected.index(rid)],
            "status": status,
            "ieee830": attributes,
            "justifications": justifications,
            "matched_model_evidence": evidence if isinstance(evidence, list) else [evidence],
            "rationale": item.get("rationale", ""),
        }
    missing = [rid for rid in expected if rid not in verdicts]
    if missing:
        raise InvalidJudgment(f"no verdict for {', '.join(missing)}")
    return {
        "per_requirement": [verdicts[rid] for rid in expected],
        "global_notes": payload.get("global_notes", ""),
    }


def judge(requirements: list[str], sysml_code: str, client) -> dict:
    """Judges one SysML model. Re-asks on an invalid answer; every attempt counts in the returned usage."""
    messages = build_messages(requirements, sysml_code)
    usage = {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0,
             "latency_s": 0.0, "cost_usd": 0.0}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.chat_with_metadata(messages, json_mode=True)
        usage["llm_calls"] += 1
        for key in ("input_tokens", "output_tokens", "reasoning_tokens", "latency_s", "cost_usd"):
            usage[key] += response[key]
        try:
            return {**parse_judgment(response["content"], requirements), "usage": usage,
                    "provider": response.get("provider")}
        except InvalidJudgment as exc:
            logger.warning("Invalid judgment from %s (attempt %d/%d, finish_reason=%s): %s",
                           response.get("model"), attempt, MAX_ATTEMPTS, response.get("finish_reason"), exc)
            if attempt == MAX_ATTEMPTS:
                error = InvalidJudgment(f"{exc} (after {attempt} attempts)")
                error.usage = usage  # so the caller can still account for what was spent
                raise error from None
