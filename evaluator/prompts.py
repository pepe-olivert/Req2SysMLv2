"""Prompt of the SemanticJudge agent, adapted from our prior LLM-as-a-Judge framework.

Adaptation to this paper:
- The judge reads the generated SysML v2 code directly (the prior framework fed it a summary
  produced by a Model2Text agent).
- The requirements are the validated input requirements, passed as given with fixed ids
  (the prior framework re-normalized them with a RequirementAgent, which changed the denominator).
"""

IEEE830_ATTRIBUTES = ("correctness", "completeness", "unambiguity", "verifiability", "traceability")
STATUSES = ("satisfied", "partial", "missing", "not_applicable")

JUDGE_SYSTEM_PROMPT = """You are SemanticJudgeAgent.
Evaluate each requirement against the SysML v2 model using IEEE 830 requirement quality attributes:

- Correctness: Is the requirement represented accurately in the model?
- Completeness: Are all aspects of the requirement covered in the model?
- Unambiguity: Is the mapping between requirement and model elements clear and deterministic?
- Verifiability: Could the requirement be objectively tested from the model definition?
- Traceability: Can you point to explicit model elements that satisfy the requirement?

For each attribute, return a Boolean (true/false) plus a short justification.
Also provide matched model evidence (element names, attributes, connections).
Finally, return an overall status derived from IEEE 830:
- satisfied (all attributes true),
- partial (some false),
- missing (all false),
- not_applicable."""

JUDGE_USER_TEMPLATE = """SysML v2 model:
---
{sysml_code}
---

Requirements (JSON list, evaluate every one of them and keep their ids):
{requirements}

Respond ONLY as JSON:
{{
  "per_requirement": [
    {{
      "req_id": "R1",
      "ieee830": {{
        "correctness": {{"value": true, "justification": "..."}},
        "completeness": {{"value": false, "justification": "..."}},
        "unambiguity": {{"value": true, "justification": "..."}},
        "verifiability": {{"value": true, "justification": "..."}},
        "traceability": {{"value": true, "justification": "..."}}
      }},
      "status": "partial",
      "matched_model_evidence": ["..."],
      "rationale": "Max speed modeled but temperature range missing."
    }}
  ],
  "global_notes": "short paragraph about general model-requirement alignment"
}}"""
