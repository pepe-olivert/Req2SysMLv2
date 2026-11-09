"""Deterministic LJS from the judge's per-requirement verdicts (no LLM calls).

Same formulas as the prior framework: over the applicable requirements (not `not_applicable`),
strict = satisfied share, lenient = (satisfied + partial) share and weighted = (satisfied + 0.5 partial)
share. LJS is the weighted score. The IEEE 830 columns give the share of applicable requirements with
each attribute true. With no applicable requirement the scores are None (never 0).
"""

from __future__ import annotations

from .prompts import IEEE830_ATTRIBUTES, STATUSES

PARTIAL_WEIGHT = 0.5


def score(per_requirement: list[dict]) -> dict:
    tally = {status: 0 for status in STATUSES}
    for item in per_requirement:
        tally[item["status"]] += 1
    applicable = [item for item in per_requirement if item["status"] != "not_applicable"]
    n = len(applicable)

    def share(count: float) -> float | None:
        return count / n if n else None

    return {
        "ljs": share(tally["satisfied"] + PARTIAL_WEIGHT * tally["partial"]),
        "ljs_strict": share(tally["satisfied"]),
        "ljs_lenient": share(tally["satisfied"] + tally["partial"]),
        "n_requirements": len(per_requirement),
        **{f"n_{status}": tally[status] for status in STATUSES},
        **{f"ieee_{attr}": share(sum(item["ieee830"][attr] for item in applicable)) for attr in IEEE830_ATTRIBUTES},
    }
