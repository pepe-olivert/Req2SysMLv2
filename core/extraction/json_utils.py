import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

_MAX_JSON_ATTEMPTS = 3


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def parse_json_object(content: str) -> dict[str, Any]:
    candidates = [content.strip()]
    candidates.extend(match.strip() for match in _JSON_BLOCK_RE.findall(content))

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(content[start : end + 1])

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    preview = content[:500].replace("\n", "\\n")
    raise json.JSONDecodeError(
        f"Could not parse a JSON object from LLM response. Preview: {preview}",
        content,
        0,
    )


def chat_json(llm: Any, messages: list[dict], max_attempts: int = _MAX_JSON_ATTEMPTS) -> tuple[dict[str, Any], dict]:
    """
    JSON-mode call that re-asks when the reply is not a parseable JSON object
    (models occasionally emit malformed or truncated JSON). Every attempt goes
    through `llm`, so retries are counted in calls, tokens and cost.
    Returns (parsed_object, response_metadata_of_the_successful_call).
    """
    for attempt in range(1, max_attempts + 1):
        response = llm.chat_with_metadata(messages=messages, json_mode=True)
        try:
            return parse_json_object(response["content"]), response
        except json.JSONDecodeError:
            logger.warning(
                "Unparseable JSON from %s (attempt %d/%d, finish_reason=%s, %d chars)",
                response.get("model"), attempt, max_attempts,
                response.get("finish_reason"), len(response["content"]),
            )
            if attempt == max_attempts:
                raise
