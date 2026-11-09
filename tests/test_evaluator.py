import json

import pytest

from evaluator.__main__ import judgment_key
from evaluator.prompts import IEEE830_ATTRIBUTES
from evaluator.scoring import score
from evaluator.semantic_judge import InvalidJudgment, judge, parse_judgment


REQUIREMENTS = ["The radio shall support group calls.", "The radio shall log every call."]


def _verdict(rid, status, values=(True,) * 5):
    return {
        "req_id": rid,
        "ieee830": {a: {"value": v, "justification": "j"} for a, v in zip(IEEE830_ATTRIBUTES, values)},
        "status": status,
        "matched_model_evidence": ["part def Radio"],
        "rationale": "r",
    }


def _content(*verdicts):
    return json.dumps({"per_requirement": list(verdicts), "global_notes": "ok"})


class FakeClient:
    model = "fake/judge"

    def __init__(self, contents):
        self.contents = list(contents)
        self.calls = 0

    def chat_with_metadata(self, messages, json_mode=False):
        self.calls += 1
        return {"content": self.contents.pop(0), "input_tokens": 100, "output_tokens": 50,
                "reasoning_tokens": 0, "latency_s": 1.0, "cost_usd": 0.001, "model": self.model,
                "finish_reason": "stop"}


def test_score_uses_prior_framework_formulas():
    per_req = parse_judgment(_content(
        _verdict("R1", "satisfied"),
        _verdict("R2", "partial", (True, False, True, True, False)),
    ), REQUIREMENTS)["per_requirement"]
    s = score(per_req)
    assert s["ljs"] == pytest.approx(0.75)
    assert s["ljs_strict"] == pytest.approx(0.5)
    assert s["ljs_lenient"] == pytest.approx(1.0)
    assert s["ieee_completeness"] == pytest.approx(0.5)
    assert s["ieee_correctness"] == pytest.approx(1.0)
    assert (s["n_satisfied"], s["n_partial"], s["n_missing"]) == (1, 1, 0)


def test_not_applicable_is_excluded_and_all_na_gives_none():
    na = parse_judgment(_content(_verdict("R1", "not_applicable"), _verdict("R2", "missing", (False,) * 5)),
                        REQUIREMENTS)["per_requirement"]
    assert score(na)["ljs"] == 0.0
    assert score(na)["n_not_applicable"] == 1
    assert score([na[0]])["ljs"] is None


def test_null_attributes_only_allowed_when_not_applicable():
    parsed = parse_judgment(_content(_verdict("R1", "not_applicable", (None,) * 5), _verdict("R2", "satisfied")),
                            REQUIREMENTS)
    assert parsed["per_requirement"][0]["ieee830"]["correctness"] is None
    assert score(parsed["per_requirement"])["ieee_correctness"] == 1.0
    with pytest.raises(InvalidJudgment, match="boolean"):
        parse_judgment(_content(_verdict("R1", "partial", (None,) * 5), _verdict("R2", "satisfied")), REQUIREMENTS)


def test_parse_rejects_missing_or_unknown_ids():
    with pytest.raises(InvalidJudgment, match="R2"):
        parse_judgment(_content(_verdict("R1", "satisfied")), REQUIREMENTS)
    with pytest.raises(InvalidJudgment):
        parse_judgment(_content(_verdict("R1", "satisfied"), _verdict("R9", "satisfied")), REQUIREMENTS)
    with pytest.raises(InvalidJudgment):
        parse_judgment(_content(_verdict("R1", "great"), _verdict("R2", "satisfied")), REQUIREMENTS)


def test_parse_keeps_requirement_text_and_string_booleans():
    v = _verdict("R2", "satisfied")
    v["ieee830"]["traceability"]["value"] = "true"
    parsed = parse_judgment(_content(_verdict("R1", "satisfied"), v), REQUIREMENTS)
    assert parsed["per_requirement"][1]["requirement"] == REQUIREMENTS[1]
    assert parsed["per_requirement"][1]["ieee830"]["traceability"] is True


def test_judge_retries_invalid_answer_and_counts_every_call():
    client = FakeClient(["not json", _content(_verdict("R1", "satisfied"), _verdict("R2", "missing", (False,) * 5))])
    result = judge(REQUIREMENTS, "package P {}", client)
    assert client.calls == 2
    assert result["usage"]["llm_calls"] == 2
    assert result["usage"]["cost_usd"] == pytest.approx(0.002)


def test_judge_gives_up_and_reports_spend():
    client = FakeClient(["{}"] * 3)
    with pytest.raises(InvalidJudgment) as info:
        judge(REQUIREMENTS, "package P {}", client)
    assert info.value.usage["llm_calls"] == 3


def test_judgment_key_depends_on_code_and_requirements():
    assert judgment_key(REQUIREMENTS, "a") == judgment_key(list(REQUIREMENTS), "a")
    assert judgment_key(REQUIREMENTS, "a") != judgment_key(REQUIREMENTS, "b")
    assert judgment_key(REQUIREMENTS, "a") != judgment_key(REQUIREMENTS[:1], "a")
