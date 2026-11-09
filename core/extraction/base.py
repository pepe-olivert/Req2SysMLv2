from abc import ABC, abstractmethod

from ..llm_client import LLMClient


class ExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, pdf_path: str, llm: LLMClient) -> dict:
        """Extract structured requirements from a PDF document."""
