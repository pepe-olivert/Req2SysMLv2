from pathlib import Path

import tiktoken

from ..llm_client import LLMClient
from ..utils import read_pdf
from .base import ExtractionStrategy
from .json_utils import chat_json


_EXTRACTION_PROMPT_PATH = Path(__file__).resolve().parent / "extraction_prompt.md"
_USER_PROMPT = "Extract requirements from this text and return JSON:\n\n{}"


class RawExtractionStrategy(ExtractionStrategy):
    def extract(self, pdf_path: str, llm: LLMClient) -> dict:
        pdf_text = read_pdf(pdf_path)
        total_tokens_input = len(tiktoken.get_encoding("cl100k_base").encode(pdf_text))
        system_prompt = _EXTRACTION_PROMPT_PATH.read_text(encoding="utf-8")

        requirements, response = chat_json(
            llm,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _USER_PROMPT.format(pdf_text)},
            ],
        )

        return {
            "requirements": requirements,
            "metadata": {
                "strategy": "raw",
                "total_tokens_input": total_tokens_input,
                "chunks": 1,
                "llm_calls": 1,
                "latency_s": response["latency_s"],
            },
        }
