from pathlib import Path

import pytest

from evaluation.common import requirements_sha256
from evaluation.run_extraction import select_best


def _run(doc, strategy, model, run, cost, requirements):
    meta = {"doc": doc, "strategy": strategy, "model": model, "run": run, "cost_usd": cost}
    return Path(f"{doc}_{strategy}_{model}_run{run}.json"), {"requirements": requirements, "metadata": meta}


def _identity(requirements):
    return requirements


def _exact_dedup(requirements):
    return {cat: list(dict.fromkeys(reqs)) for cat, reqs in requirements.items()}


def test_picks_max_requirements_for_requested_doc_only():
    runs = [
        _run("eirene", "raw", "a", 1, 0.01, {"X": ["r1", "r2"]}),
        _run("eirene", "sliding_window", "b", 1, 0.50, {"X": ["r1", "r2"], "Y": ["r3"]}),
        _run("jwst", "sliding_window", "a", 1, 0.01, {"X": ["r1", "r2", "r3", "r4", "r5"]}),
    ]
    best = select_best(runs, "eirene", dedup=_identity)
    assert best["source"]["model"] == "b"
    assert best["source"]["n_requirements"] == 3
    assert best["sha256"] == requirements_sha256(best["requirements"])


def test_count_is_after_dedup_and_tie_breaks_on_cost():
    runs = [
        # 4 raw requirements but only 2 unique
        _run("eirene", "raw", "a", 1, 0.01, {"X": ["r1", "r1", "r2", "r2"]}),
        _run("eirene", "raw", "b", 1, 0.20, {"X": ["r1", "r2", "r3"]}),
        _run("eirene", "raw", "c", 1, 0.05, {"X": ["r4", "r5", "r6"]}),
    ]
    best = select_best(runs, "eirene", dedup=_exact_dedup)
    assert best["source"]["model"] == "c"  # tie at 3 requirements -> cheaper wins


def test_ignores_malformed_requirements_and_errors_without_candidates():
    runs = [_run("eirene", "raw", "a", 1, 0.01, {"X": "not a list", "Y": []})]
    with pytest.raises(ValueError):
        select_best(runs, "eirene", dedup=_identity)


def test_chat_json_retries_on_malformed_json():
    from core.extraction.json_utils import chat_json

    replies = iter(['{"A": ["r1", ', '{"A": ["r1"]}'])

    class FakeLLM:
        calls = 0

        def chat_with_metadata(self, messages, json_mode=False):
            FakeLLM.calls += 1
            return {"content": next(replies), "latency_s": 0.0, "model": "fake", "finish_reason": "stop"}

    parsed, _ = chat_json(FakeLLM(), [])
    assert parsed == {"A": ["r1"]} and FakeLLM.calls == 2


def test_manual_best_file_overrides_criterion():
    runs = [
        _run("eirene", "raw", "a", 1, 0.01, {"X": ["r1", "r2", "r3"]}),
        _run("eirene", "sliding_window", "b", 1, 0.01, {"X": ["r1"]}),
    ]
    best = select_best(runs, "eirene", dedup=_identity, best_file="eirene_sliding_window_b_run1.json")
    assert best["source"]["model"] == "b" and "manually selected" in best["source"]["criterion"]
    with pytest.raises(ValueError):
        select_best(runs, "eirene", dedup=_identity, best_file="missing.json")
