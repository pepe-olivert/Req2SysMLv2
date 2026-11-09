"""Registry of the LLMs supported through OpenRouter.

Adding a model = adding one entry to SUPPORTED_MODELS.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    alias: str                 # CLI name and name used in CSVs/figures
    openrouter_id: str         # exact OpenRouter id, never a "-latest" alias (not a pinned snapshot: see README.md)
    input_usd_per_m: float     # fallback pricing if OpenRouter does not return usage.cost
    output_usd_per_m: float
    reasoning_effort: str | None = None   # sent as extra_body={"reasoning": {"effort": ...}}
    supports_temperature: bool = True     # if False, temperature is not sent
    supports_json_mode: bool = True
    role: str = "candidate"   # "candidate" | "judge"
    # OpenRouter provider tag (e.g. "baidu/fp8") to pin, with no fallback: every call is served by the
    # same weights and quantization at a known price. None lets OpenRouter route freely.
    provider: str | None = None


# Prices: OpenRouter, checked 2026-10-09 (USD per million tokens, input/output).
# All candidates are reasoning models and use the same effort for a fair comparison.
_EFFORT = "medium"

SUPPORTED_MODELS: dict[str, ModelSpec] = {
    spec.alias: spec
    for spec in (
        ModelSpec("gpt-6-luna", "openai/gpt-6-luna", 0.10, 0.50,
                  reasoning_effort=_EFFORT, supports_temperature=False),
        ModelSpec("gpt-6.1-sol", "openai/gpt-6.1-sol", 2.00, 10.00,
                  reasoning_effort=_EFFORT, supports_temperature=False),
        ModelSpec("gemini-3.5-flash-lite", "google/gemini-3.5-flash-lite", 0.30, 2.50,
                  reasoning_effort=_EFFORT),
        ModelSpec("gemini-3.7-flash", "google/gemini-3.7-flash", 0.75, 3.75,
                  reasoning_effort=_EFFORT),
        # LLM-as-judge for LJS (evaluator/), never a candidate. The first one is the default judge: the one
        # used by our prior LLM-as-a-Judge framework (no reasoning, so fast). The rest are drop-in
        # alternatives from other families (prices checked 2026-10-11).
        ModelSpec("gpt-4o-mini", "openai/gpt-4o-mini", 0.15, 0.60, role="judge"),
        # Pinned: OpenRouter spreads deepseek-v4-pro over ~16 providers (fp4/fp8, $0.45-1.9/M input).
        # Not used in the paper (only in the discarded judge pilot). Price of the pinned endpoint
        # re-checked 2026-10-20: it rose from 0.17069/0.34138 to 1.69/3.38.
        ModelSpec("deepseek-v4-pro", "deepseek/deepseek-v4-pro", 1.69, 3.38,
                  provider="baidu/fp8", role="judge"),
        # Second judge of the JSS revision (another provider than every candidate). Same reasoning effort as
        # the candidates; pinned to Anthropic's own endpoint (price checked 2026-10-20: same on every endpoint).
        ModelSpec("claude-haiku-5.5", "anthropic/claude-haiku-5.5", 0.10, 0.50, reasoning_effort=_EFFORT,
                  supports_temperature=False, provider="anthropic", role="judge"),
        ModelSpec("qwen3.8-flash", "qwen/qwen3.8-flash", 0.15, 0.47, role="judge"),
        ModelSpec("mistral-small-2603", "mistralai/mistral-small-2603", 0.15, 0.60, role="judge"),
    )
}


def get_model(alias: str) -> ModelSpec:
    try:
        return SUPPORTED_MODELS[alias]
    except KeyError:
        valid = ", ".join(SUPPORTED_MODELS)
        raise ValueError(f"Unknown model alias '{alias}'. Valid aliases: {valid}") from None


def candidate_aliases() -> list[str]:
    return [alias for alias, spec in SUPPORTED_MODELS.items() if spec.role == "candidate"]


def judge_aliases() -> list[str]:
    return [alias for alias, spec in SUPPORTED_MODELS.items() if spec.role == "judge"]


def resolve_model_aliases(aliases: list[str]) -> list[str]:
    """Expand 'all' to every candidate and validate the rest (keeps order, no duplicates)."""
    resolved: list[str] = []
    for alias in aliases:
        for name in candidate_aliases() if alias == "all" else [alias]:
            get_model(name)
            if name not in resolved:
                resolved.append(name)
    return resolved
