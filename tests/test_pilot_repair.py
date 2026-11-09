import re

from core.agents.agent2.error_router import ErrorRouter
from core.agents.agent2.logic import SysMLAgent
from core.agents.agent2.pilot_repair import FIX_PILOT_SYSTEM_PROMPT, run_pilot_repair

BAD = "package P {\n    part alpha;\n    part beta;\n    interface i { }\n}\n"  # ANTLR-valid; the fake Pilot rejects 'interface'
GOOD = BAD.replace("interface i { }", "part delta;    ")                          # what a repair returns
BROKEN = BAD.replace("part beta;", "part beta ")                                  # same length, invalid for ANTLR


class FakePilot:
    def errors(self, code):
        return [{"kind": "ISSUE", "severity": "ERROR", "code": "validateConnectorRelatedFeatures",
                 "line": i + 1, "column": 5, "message": "Must have at least two related elements"}
                for i, line in enumerate(code.splitlines()) if "interface" in line]


class FakeClient:
    def __init__(self, answers):
        self.answers, self.messages, self.systems = list(answers), [], []

    def reset(self):
        pass

    def snapshot(self):
        return {"llm_calls": len(self.messages)}

    def chat_with_metadata(self, messages):
        self.systems.append(messages[0]["content"])
        self.messages.append(messages[-1]["content"])
        return {"content": self.answers.pop(0)}


def agent(answers):
    a = SysMLAgent.__new__(SysMLAgent)
    a.llm_client = FakeClient(answers)
    a.router = ErrorRouter()
    return a


def test_converges_with_the_c2_message_and_the_pilot_prompt():
    a = agent([GOOD])
    res = run_pilot_repair(a, FakePilot(), BAD)
    assert res["converged"] and res["initial_error_count"] == 1 and res["iterations_used"] == 1
    msg = a.llm_client.messages[0]
    assert "=== CURRENT ERROR ===\nline 4, column 5: Must have at least two related elements" in msg
    assert "KNOWLEDGE BASE" not in msg and "[category" not in msg
    assert a.llm_client.systems[0] == FIX_PILOT_SYSTEM_PROMPT and "Pilot Implementation" in FIX_PILOT_SYSTEM_PROMPT


def test_answer_that_breaks_antlr_is_retried_then_rejected():
    a = agent([BROKEN, BROKEN] + [BAD] * 30)
    res = run_pilot_repair(a, FakePilot(), BAD, max_iterations=2)
    assert res["guard"]["retries_antlr"] >= 1 and res["guard"]["rejections_antlr"] >= 1
    assert res["sysml_code"].strip() == BAD.strip()  # the broken answer never replaced the model
    assert "=== WARNING ===" in a.llm_client.messages[1] and "broke the SysML v2 grammar" in a.llm_client.messages[1]
    assert not res["converged"] and res["stagnation_detected"]
