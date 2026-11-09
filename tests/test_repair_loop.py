import re

import pytest

from core.agents.agent2.error_router import ErrorRouter
from core.agents.agent2.logic import CONDITIONS, SysMLAgent

BROKEN = """package P {
    part R {
        attribute v : Integer;
        assert v == 1;
    }
    part S {
        attribute w : Integer;
        assert w == 2;
    }
}"""

FIRST_FIXED = BROKEN.replace("assert v == 1;", "assert constraint { v == 1 }")
ALL_FIXED = FIRST_FIXED.replace("assert w == 2;", "assert constraint { w == 2 }")


class FakeClient:
    """Returns scripted answers and records the user message of every repair call."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.messages = []

    def reset(self):
        pass

    def snapshot(self):
        return {"llm_calls": len(self.messages)}

    def chat_with_metadata(self, messages):
        self.messages.append(messages[-1]["content"])
        return {"content": self.answers.pop(0)}


def make_agent(answers):
    agent = SysMLAgent.__new__(SysMLAgent)
    agent.llm_client = FakeClient(answers)
    agent.router = ErrorRouter()
    agent._ERROR_RE = re.compile(r"^Syntax error at line\s+(?P<line>\d+),\s+column\s+(?P<col>\d+):\s*(?P<msg>.*)$")
    return agent


def current_error_line(message):
    return int(re.search(r"=== CURRENT ERROR ===\nline (\d+)", message).group(1))


def test_broken_fixture_has_errors_on_both_asserts():
    lines = {e["line"] for e in make_agent([]).validate_sysml(BROKEN)}
    assert {4, 8} <= lines


@pytest.mark.parametrize("condition", ["C2", "C3", "C4"])
def test_each_call_targets_an_error_that_currently_exists(condition):
    agent = make_agent([FIRST_FIXED, ALL_FIXED])
    result = agent.run_category("cat", ["r"], CONDITIONS[condition], initial_code=BROKEN)
    assert result["converged"]
    first, second = agent.llm_client.messages
    assert current_error_line(first) == 4
    # The second call is chosen from the re-validated model, so it points at the remaining assert.
    remaining = {e["line"] for e in agent.validate_sysml(FIRST_FIXED)}
    assert current_error_line(second) in remaining and current_error_line(second) == 8
    assert "assert v == 1" not in second.split("=== CURRENT ERROR ===")[1].split("=== SYSML")[0]


def test_loop_stops_as_soon_as_the_model_is_valid():
    agent = make_agent([ALL_FIXED])
    result = agent.run_category("cat", ["r"], CONDITIONS["C4"], initial_code=BROKEN)
    assert result["converged"] and result["initial_error_count"] >= 2
    assert len(agent.llm_client.messages) == 1


def test_guard_retries_then_rejects_a_fragment():
    fragment = "assert constraint { v == 1 }"
    agent = make_agent([fragment, fragment] + [ALL_FIXED])
    result = agent.run_category("cat", ["r"], CONDITIONS["C2"], initial_code=BROKEN)
    first, retry = result["repairs"][0], agent.llm_client.messages[1]
    assert first["guard_retried"] and first["guard_rejected"]
    assert first["code_before"] == BROKEN  # the fragment never replaced the model
    assert "=== WARNING ===" in retry
    assert result["guard_rejections"] == 1 and result["converged"]


def test_guard_accepts_a_complete_retry():
    agent = make_agent(["package P { }", ALL_FIXED])
    result = agent.run_category("cat", ["r"], CONDITIONS["C2"], initial_code=BROKEN)
    assert result["guard_retries"] == 1 and result["guard_rejections"] == 0 and result["converged"]


def test_message_sections_depend_on_the_condition():
    blind = make_agent([ALL_FIXED])
    blind.run_category("cat", ["r"], CONDITIONS["C2"], initial_code=BROKEN)
    full = make_agent([ALL_FIXED])
    full.run_category("cat", ["r"], CONDITIONS["C4"], initial_code=BROKEN)
    c2, c4 = blind.llm_client.messages[0], full.llm_client.messages[0]
    assert "KNOWLEDGE BASE" not in c2 and "[category" not in c2
    assert "=== CATEGORY KNOWLEDGE BASE (CONSTRAINT_EXPR) ===" in c4 and "[category CONSTRAINT_EXPR" in c4
    # The code is sent with real line breaks, last, exactly as validated.
    assert c2.endswith("=== SYSML V2 FILE ===\n" + BROKEN)


def test_clean_sysml_only_strips_fences():
    raw = "```sysml\npackage sysmlTools { part sysmlParser; }\n```"
    assert SysMLAgent.clean_sysml(raw) == "package sysmlTools { part sysmlParser; }\n"
    assert SysMLAgent.clean_sysml('package P { doc /* a \\ b */ }') == 'package P { doc /* a \\ b */ }'


@pytest.mark.parametrize("code, expected", [
    ("package P { part R { attribute v : Real; } constraint C { assert R::v == 96; } }", "CONSTRAINT_EXPR"),
    ("package P { part R { attribute v : Real; assert v >= 1; } }", "CONSTRAINT_EXPR"),
    ('package P { requirement R { attribute doc : String = "t"; } }', "DOC_COMMENT"),
    ('package P { part R { attribute m : true; } }', "DECLARATION_FORM"),
])
def test_router_on_real_patterns(code, expected):
    agent = make_agent([])
    routed = agent.router.route_all(agent.validate_sysml(code))
    assert routed[0]["category_id"] == expected


def test_router_without_any_signal_is_unknown():
    assert ErrorRouter().route_one({"error": "something unexpected", "sysml_block": "x"}).category_id == "UNKNOWN"


def _first_message(condition, code=BROKEN):
    agent = make_agent([ALL_FIXED])
    agent.run_category("cat", ["r"], CONDITIONS[condition], initial_code=code)
    return agent.llm_client.messages[0]


def test_c2kb_adds_the_routed_kb_without_label_or_priority():
    from core.utils import get_knowledge

    c2kb, c2 = _first_message("C2KB"), _first_message("C2")
    assert "=== KNOWLEDGE BASE ===\n" + get_knowledge("CONSTRAINT_EXPR") in c2kb
    assert "[category" not in c2kb and "CATEGORY KNOWLEDGE BASE" not in c2kb and "priority" not in c2kb
    # Same current error and error list as C2 (parser order); only the KB section is added.
    section = lambda m, name: m.split(f"=== {name} ===\n")[1].split("\n\n===")[0]  # noqa: E731
    for name in ("CURRENT ERROR", "ALL ERRORS CURRENTLY REPORTED BY THE VALIDATOR (context only)"):
        assert section(c2kb, name) == section(c2, name)


# Two errors of different priority: DECLARATION_FORM (line 3, priority 40) before CONSTRAINT_EXPR (line 4, 25).
MIXED = """package P {
    part R { attribute v : Integer
    }
    part S { attribute w : Integer; assert w == 2; }
}"""


def test_c3a_orders_by_priority_without_labels_and_c3b_shows_labels_in_parser_order():
    agent = make_agent([])
    routed = agent.router.route_all(agent.validate_sysml(MIXED))
    parser_first = routed[0]
    by_priority = sorted(routed, key=lambda e: (e["priority"], e["line"], e["column"]))[0]
    c3, c3a, c3b = (_first_message(c, MIXED) for c in ("C3", "C3a", "C3b"))
    assert "[category" not in c3a and "[category" in c3b and "[category" in c3
    assert current_error_line(c3a) == current_error_line(c3) == by_priority["line"]
    assert current_error_line(c3b) == parser_first["line"]
    assert "KNOWLEDGE BASE" not in c3a + c3b


def test_fullrev_sends_the_whole_file_and_every_error_once_per_iteration():
    from core.agents.agent2.logic import FIX_ALL_SYSTEM_PROMPT

    class Recording(type(make_agent([]).llm_client)):
        def chat_with_metadata(self, messages):
            self.system = messages[0]["content"]
            return super().chat_with_metadata(messages)

    agent = make_agent([])
    agent.llm_client = Recording([FIRST_FIXED, ALL_FIXED])
    result = agent.run_category("cat", ["r"], CONDITIONS["FULLREV"], initial_code=BROKEN)
    first, second = agent.llm_client.messages
    assert result["converged"] and result["iterations_used"] == 2  # one call per iteration
    assert agent.llm_client.system == FIX_ALL_SYSTEM_PROMPT and "CURRENT ERROR" not in FIX_ALL_SYSTEM_PROMPT
    assert "CURRENT ERROR" not in first and "KNOWLEDGE BASE" not in first and "[category" not in first
    listed = first.split("=== ALL ERRORS CURRENTLY REPORTED BY THE VALIDATOR ===\n")[1].split("\n\n===")[0]
    assert len(listed.splitlines()) == len(agent.validate_sysml(BROKEN))
    assert first.endswith("=== SYSML V2 FILE ===\n" + BROKEN)


def test_fullrev_guard_retries_then_rejects():
    agent = make_agent(["package P { }", "package P { }"] + [ALL_FIXED])
    result = agent.run_category("cat", ["r"], CONDITIONS["FULLREV"], initial_code=BROKEN)
    assert result["guard_retries"] == 1 and result["guard_rejections"] == 1 and result["converged"]
    assert "=== WARNING ===" in agent.llm_client.messages[1]
