"""LLM-as-a-Judge score (LJS) over stored SysML v2 models, computed after generation and repair.

Reuses the SemanticJudge agent of our prior LLM-as-a-Judge framework (IEEE 830 attributes per
requirement); see prompts.py for the adaptation. Run it with `python -m evaluator`.
"""

from core.models import judge_aliases

from .scoring import score
from .semantic_judge import InvalidJudgment, judge

DEFAULT_JUDGE = judge_aliases()[0]

__all__ = ["DEFAULT_JUDGE", "InvalidJudgment", "judge", "score"]
