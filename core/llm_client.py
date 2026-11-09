"""Single LLM layer: every call goes through OpenRouter (OpenAI-compatible API)."""

import logging
import random
import threading
import time
from typing import Any

import openai
from openai import OpenAI

from .config import OPENROUTER_BASE_URL, openrouter_api_key
from .models import ModelSpec, get_model


logger = logging.getLogger(__name__)

_JSON_INSTRUCTION = "Respond ONLY with valid JSON."
_MAX_RETRIES = 5
_BACKOFF_BASE_S = 2.0
_BACKOFF_MAX_S = 60.0


class RetryableResponseError(RuntimeError):
    """OpenRouter answered 200 but without a usable completion (upstream hiccup)."""


class RateLimiter:
    """Spaces out calls so that at most `rpm` requests per minute are started (thread-safe)."""

    def __init__(self, rpm: float) -> None:
        self.interval_s = 60.0 / rpm
        self._next_slot = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            slot = max(now, self._next_slot)
            self._next_slot = slot + self.interval_s
        if slot > now:
            time.sleep(slot - now)


# One limiter per OpenRouter model id, shared by every client of that model in the process
# (OpenRouter rate limits are per account and model).
_RATE_LIMITERS: dict[str, RateLimiter] = {}
_RATE_LIMITERS_LOCK = threading.Lock()


def _rate_limiter(model_id: str, rpm: float | None) -> RateLimiter | None:
    if not rpm:
        return None
    with _RATE_LIMITERS_LOCK:
        if model_id not in _RATE_LIMITERS:
            _RATE_LIMITERS[model_id] = RateLimiter(rpm)
        return _RATE_LIMITERS[model_id]


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, (openai.APITimeoutError, openai.APIConnectionError,
                        openai.RateLimitError, RetryableResponseError)):
        return True
    if isinstance(exc, openai.APIStatusError):
        return exc.status_code == 429 or exc.status_code >= 500
    return False


class LLMClient:
    def __init__(
        self,
        spec: ModelSpec,
        temperature: float = 0.0,
        timeout_s: float = 600.0,
        max_retries: int = _MAX_RETRIES,
        api_key: str | None = None,
        max_rpm: float | None = None,
    ) -> None:
        self.spec = spec
        self.rate_limiter = _rate_limiter(spec.openrouter_id, max_rpm)
        self.alias = spec.alias
        self.model = spec.openrouter_id
        self.temperature = temperature
        self.max_retries = max_retries
        # Retries are handled here (exponential backoff), not by the SDK.
        self.client = OpenAI(
            api_key=api_key or openrouter_api_key(),
            base_url=OPENROUTER_BASE_URL,
            timeout=timeout_s,
            max_retries=0,
        )
        self.last_metadata: dict | None = None

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        self.last_metadata = self.chat_with_metadata(messages, json_mode)
        return self.last_metadata["content"]

    def chat_with_metadata(self, messages: list[dict], json_mode: bool = False) -> dict:
        request_kwargs = self._build_request(messages, json_mode)

        for attempt in range(self.max_retries + 1):
            if self.rate_limiter is not None:
                self.rate_limiter.wait()
            start_time = time.perf_counter()
            try:
                completion = self.client.chat.completions.create(**request_kwargs)
                if not completion.choices:
                    error = (completion.model_extra or {}).get("error")
                    raise RetryableResponseError(f"Empty completion from OpenRouter: {error}")
                if completion.choices[0].finish_reason == "error":
                    # Upstream provider failed mid-generation: the content is empty or truncated.
                    raise RetryableResponseError("Completion ended with finish_reason=error")
                break
            except Exception as exc:
                if attempt >= self.max_retries or not _is_retryable(exc):
                    raise
                delay = min(_BACKOFF_MAX_S, _BACKOFF_BASE_S * 2**attempt) * (0.5 + random.random())
                logger.warning("LLM call failed (%s: %s). Retry %d/%d in %.1fs",
                               type(exc).__name__, exc, attempt + 1, self.max_retries, delay)
                time.sleep(delay)
        latency_s = time.perf_counter() - start_time

        content = completion.choices[0].message.content or ""
        finish_reason = completion.choices[0].finish_reason
        usage = completion.usage
        input_tokens = getattr(usage, "prompt_tokens", 0) or 0
        output_tokens = getattr(usage, "completion_tokens", 0) or 0
        details = getattr(usage, "completion_tokens_details", None)
        reasoning_tokens = getattr(details, "reasoning_tokens", 0) or 0
        cost_usd = getattr(usage, "cost", None)
        cost_source = "openrouter"
        if cost_usd is None:
            cost_usd = self.estimate_cost(input_tokens, output_tokens)
            cost_source = "registry"

        logger.info(
            "LLM call model=%s in=%s out=%s reasoning=%s cost=%.6f latency_s=%.2f",
            self.model, input_tokens, output_tokens, reasoning_tokens, cost_usd, latency_s,
        )
        return {
            "content": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
            "latency_s": latency_s,
            "cost_usd": float(cost_usd),
            "cost_source": cost_source,
            "finish_reason": finish_reason,
            "model": self.model,
            "provider": (completion.model_extra or {}).get("provider"),
        }

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.spec.input_usd_per_m
                + output_tokens * self.spec.output_usd_per_m) / 1_000_000

    def _build_request(self, messages: list[dict], json_mode: bool) -> dict[str, Any]:
        # "developer" is OpenAI-specific; "system" is accepted by every OpenRouter provider.
        request_messages = [
            {**message, "role": "system" if message.get("role") == "developer" else message["role"]}
            for message in messages
        ]
        extra_body: dict[str, Any] = {"usage": {"include": True}}
        if self.spec.reasoning_effort:
            extra_body["reasoning"] = {"effort": self.spec.reasoning_effort}
        if self.spec.provider:
            extra_body["provider"] = {"order": [self.spec.provider], "allow_fallbacks": False}

        request_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": request_messages,
            "extra_body": extra_body,
        }
        if self.spec.supports_temperature:
            request_kwargs["temperature"] = self.temperature
        if json_mode:
            if self.spec.supports_json_mode:
                request_kwargs["response_format"] = {"type": "json_object"}
            else:
                request_kwargs["messages"] = self._add_json_instruction(request_messages)
        return request_kwargs

    @staticmethod
    def _add_json_instruction(messages: list[dict]) -> list[dict]:
        for message in messages:
            if message.get("role") == "system":
                content = message.get("content", "")
                message["content"] = f"{content}\n\n{_JSON_INSTRUCTION}" if content else _JSON_INSTRUCTION
                return messages
        return [{"role": "system", "content": _JSON_INSTRUCTION}, *messages]


class UsageTracker:
    """Wraps an LLMClient and accumulates calls, tokens, cost and latency."""

    FIELDS = ("llm_calls", "input_tokens", "output_tokens", "reasoning_tokens", "latency_s", "cost_usd")

    def __init__(self, client: LLMClient) -> None:
        self.client = client
        self.model = client.model
        self.alias = client.alias
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        self.llm_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.reasoning_tokens = 0
        self.latency_s = 0.0
        self.cost_usd = 0.0

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        return self.chat_with_metadata(messages, json_mode)["content"]

    def chat_with_metadata(self, messages: list[dict], json_mode: bool = False) -> dict:
        response = self.client.chat_with_metadata(messages, json_mode)
        with self._lock:
            self.llm_calls += 1
            self.input_tokens += response["input_tokens"]
            self.output_tokens += response["output_tokens"]
            self.reasoning_tokens += response["reasoning_tokens"]
            self.latency_s += response["latency_s"]
            self.cost_usd += response["cost_usd"]
        return response

    def snapshot(self) -> dict:
        return {field: getattr(self, field) for field in self.FIELDS}


def create_client(alias: str, **kwargs: Any) -> LLMClient:
    return LLMClient(get_model(alias), **kwargs)
