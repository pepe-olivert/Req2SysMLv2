from core.agents.agent2.logic import SysMLAgent
from core.validate.SysMLv2LoggingParser import SysMLv2LoggingParser


VALID_MODEL = """
package Vehicle {
    part def Engine {
        attribute power : Real;
    }
    part def Car {
        part engine : Engine;
    }
    requirement def MaxSpeed {
        doc /* The car shall reach 180 km/h. */
    }
}
"""

BROKEN_MODEL = """
package Vehicle {
    part def Engine
    part car : Engine
"""


def _errors(code: str) -> str:
    parser = SysMLv2LoggingParser(code)
    parser.parse()
    return parser.get_errors()


def test_valid_model_has_no_errors():
    assert _errors(VALID_MODEL) == ""


def test_broken_model_has_errors():
    assert _errors(BROKEN_MODEL).count("Syntax error") >= 1


def test_agent_validation_strips_markdown_fences():
    agent = SysMLAgent.__new__(SysMLAgent)
    SysMLAgent.__init__(agent, _DummyClient())
    assert agent.validate_sysml(f"```sysml\n{VALID_MODEL}\n```") == []
    errors = agent.validate_sysml(BROKEN_MODEL)
    assert errors and all({"error", "line", "column", "sysml_block"} <= set(e) for e in errors)


class _DummyClient:
    model = "dummy"
    alias = "dummy"


def test_rate_limiter_spaces_calls():
    import time

    from core.llm_client import RateLimiter

    limiter = RateLimiter(rpm=600)  # one call every 0.1 s
    start = time.monotonic()
    for _ in range(4):
        limiter.wait()
    assert time.monotonic() - start >= 0.29
