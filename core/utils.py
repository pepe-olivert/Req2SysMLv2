from pathlib import Path

from pypdf import PdfReader


KNOWLEDGE_DIR = Path(__file__).resolve().parent / "agents" / "agent2" / "knowledge"


def read_pdf(pdf_path) -> str:
    reader = PdfReader(pdf_path)
    return "".join((page.extract_text() or "") + "\n" for page in reader.pages)


def get_knowledge(category: str) -> str:
    category = Path(category).name  # sanitize
    file_path = KNOWLEDGE_DIR / f"{category}.md"

    if not file_path.exists():
        raise FileNotFoundError(f"Knowledge file not found: {file_path}")

    return file_path.read_text(encoding="utf-8")
