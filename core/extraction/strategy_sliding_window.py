from pathlib import Path

import tiktoken

from ..llm_client import LLMClient
from ..utils import read_pdf
from .base import ExtractionStrategy
from .dedup import deduplicate_requirements
from .json_utils import chat_json


_EXTRACTION_PROMPT_PATH = Path(__file__).resolve().parent / "extraction_prompt.md"
_USER_PROMPT = "Extract requirements from this text and return JSON:\n\n{}"


class SlidingWindowExtractionStrategy(ExtractionStrategy):
    def __init__(
        self, chunk_size_tokens: int = 4000, overlap_tokens: int = 500
    ) -> None:
        if chunk_size_tokens <= 0:
            raise ValueError("chunk_size_tokens must be greater than zero")
        if overlap_tokens < 0:
            raise ValueError("overlap_tokens must not be negative")
        if overlap_tokens >= chunk_size_tokens:
            raise ValueError("overlap_tokens must be smaller than chunk_size_tokens")

        self.chunk_size_tokens = chunk_size_tokens
        self.overlap_tokens = overlap_tokens

    def extract(self, pdf_path: str, llm: LLMClient) -> dict:
        pdf_text = read_pdf(pdf_path)
        encoding = tiktoken.get_encoding("cl100k_base")
        document_tokens = encoding.encode(pdf_text)
        chunks = self._create_chunks(document_tokens, encoding)
        system_prompt = _EXTRACTION_PROMPT_PATH.read_text(encoding="utf-8")

        merged_requirements: dict[str, list[str]] = {}
        latency_s = 0.0

        for chunk in chunks:
            parsed, response = chat_json(
                llm,
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": _USER_PROMPT.format(chunk)},
                ],
            )
            latency_s += response["latency_s"]

            for category, requirements in parsed.items():
                merged_requirements.setdefault(category, []).extend(requirements)

        deduplicated_requirements, duplicates_removed = deduplicate_requirements(
            merged_requirements
        )

        return {
            "requirements": deduplicated_requirements,
            "metadata": {
                "strategy": "sliding_window",
                "total_tokens_input": len(document_tokens),
                "chunks": len(chunks),
                "overlap_tokens": self.overlap_tokens,
                "llm_calls": len(chunks),
                "duplicates_removed": duplicates_removed,
                "latency_s": latency_s,
            },
        }

    def _create_chunks(self, tokens: list[int], encoding: object) -> list[str]:
        step = self.chunk_size_tokens - self.overlap_tokens
        return [
            encoding.decode(tokens[start : start + self.chunk_size_tokens])
            for start in range(0, len(tokens), step)
        ]
