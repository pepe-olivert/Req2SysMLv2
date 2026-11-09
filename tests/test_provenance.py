import json

from evaluation import common
from evaluation.common import provenance, write_run_manifest


def test_provenance_has_every_field():
    p = provenance("openai/gpt-6-luna", "abc")
    assert set(p) == {"git_commit", "git_dirty", "frozen_prompt_kb_match", "timestamp_utc", "model_id",
                      "requirements_sha256"}
    assert p["model_id"] == "openai/gpt-6-luna" and p["requirements_sha256"] == "abc"
    assert p["timestamp_utc"].endswith("+00:00")


def test_explicit_timestamp_is_kept():
    assert provenance("m", "s", "2026-01-01T00:00:00+00:00")["timestamp_utc"] == "2026-01-01T00:00:00+00:00"


def test_manifest_appends_one_record_per_call(tmp_path):
    write_run_manifest(tmp_path, a=1)
    write_run_manifest(tmp_path, a=2)
    lines = (tmp_path / "run_manifest.jsonl").read_text().splitlines()
    assert [json.loads(line)["a"] for line in lines] == [1, 2]
    assert "git_commit" in json.loads(lines[0])


def test_repair_records_carry_a_timestamp():
    from frozen_support import bank_samples, EchoClient
    from core.agents.agent2.error_router import ErrorRouter
    from core.agents.agent2.logic import CONDITIONS, SysMLAgent

    agent = SysMLAgent.__new__(SysMLAgent)
    agent.llm_client = EchoClient()
    agent.router = ErrorRouter()
    result = agent.run_category("cat", ["r"], CONDITIONS["C4"], max_iterations=1,
                                initial_code=bank_samples(1)[0]["raw_output"])
    assert result["repairs"] and all(r["timestamp_utc"].endswith("+00:00") for r in result["repairs"])
