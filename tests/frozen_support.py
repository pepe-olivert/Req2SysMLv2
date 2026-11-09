"""Helpers shared by tests/test_frozen.py and the script that wrote tests/golden/repair_messages.json."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.agents.agent2.error_router import ErrorRouter
from core.agents.agent2.logic import CONDITIONS, SysMLAgent

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples" / "greenhouse_requirements.json"
GOLDEN = Path(__file__).resolve().parent / "golden" / "repair_messages.json"
FROZEN_MANIFEST = Path(__file__).resolve().parent / "golden" / "frozen_files.json"

# Invented invalid models (no study data): together they reach every knowledge base through the router.
INVALID_SAMPLES = {
    "constraint expression": """package Greenhouse {
    part def Valve { attribute rate : Real; }
    assert rate >= 5;
}
""",
    "declaration form": """package Greenhouse {
    enum def Mode { auto, manual }
}
""",
    "delimiters": """package Greenhouse {
    part def Valve {
        attribute rate : Real
    }
    part valve : Valve;
""",
    "doc comment": """package Greenhouse {
    requirement limit {
        doc closes
    }
}
""",
    "lexer": """package Greenhouse {
    part def Valve;
    part valve : Valve; `
}
""",
    "literals": """package Greenhouse {
    part def Valve { attribute label : "valve"; }
}
""",
    "qualification": """package Greenhouse {
    part Valve::main;
}
""",
    "no viable alternative": """package Greenhouse {
    part valve : Valve [1;
}
""",
    "unknown": """package Greenhouse {
    connect pump valve;
}
""",
}


class EchoClient:
    """Answers every repair call with the code it was sent (no fix) and records each full request."""

    def __init__(self):
        self.requests = []

    def reset(self):
        pass

    def snapshot(self):
        return {"llm_calls": len(self.requests)}

    def chat_with_metadata(self, messages):
        self.requests.append(messages)
        code = messages[-1]["content"].split("=== SYSML V2 FILE ===\n", 1)[1]
        return {"content": code}


def first_iteration_requests(code: str, condition: str) -> list[list[dict]]:
    agent = SysMLAgent.__new__(SysMLAgent)
    agent.llm_client = EchoClient()
    agent.router = ErrorRouter()
    agent.run_category("cat", ["r"], CONDITIONS[condition], max_iterations=1, initial_code=code)
    return agent.llm_client.requests


def digest(requests: list[list[dict]]) -> str:
    return hashlib.sha256(json.dumps(requests, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def bank_samples(n: int = 15) -> list[dict]:
    """The first `n` invented invalid models, in the shape of the records of a generations file."""
    return [{"llm": "invented", "run": 1, "category": category, "raw_output": code}
            for category, code in list(INVALID_SAMPLES.items())[:n]]


class RecordingClient(EchoClient):
    def chat_with_metadata(self, messages):
        self.requests.append(messages)
        return {"content": "package P { }"}


def generation_request(category: str, requirements: list[str]) -> list[dict]:
    """The exact generation request for one category (as run_pipeline.generate_once builds it)."""
    agent = SysMLAgent.__new__(SysMLAgent)
    agent.llm_client = RecordingClient()
    agent.generate_sysml(json.dumps({category: requirements}, ensure_ascii=False, indent=2))
    return agent.llm_client.requests[0]
