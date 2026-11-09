import os
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Documents used in the paper. Keys are the names used in CLIs, CSVs and file names.
DOCUMENTS: dict[str, str] = {
    "eirene": "data/eirene.pdf",
    "jwst": "data/jwst.pdf",
}


def document_path(doc: str) -> Path:
    try:
        return REPO_ROOT / DOCUMENTS[doc]
    except KeyError as exc:
        raise ValueError(
            f"Unknown document '{doc}'. Valid documents: {', '.join(DOCUMENTS)}"
        ) from exc


def openrouter_api_key() -> str:
    load_dotenv(REPO_ROOT / ".env")
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "error: OPENROUTER_API_KEY is not set. Copy .env.example to .env and fill it in. No LLM was called."
        )
    return key
