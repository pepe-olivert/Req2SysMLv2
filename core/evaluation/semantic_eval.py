import re
import threading
from typing import Any


_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_RCS_THRESHOLD = 0.5
_SRS_ELEMENTS = {
    "package": (re.compile(r"\bpackage\b"), 1.0),
    "part def": (re.compile(r"\bpart\s+def\b"), 2.0),
    "part": (re.compile(r"\bpart\b(?!\s+def\b)"), 1.5),
    "attribute": (re.compile(r"\battribute\b"), 1.0),
    "port": (re.compile(r"\bport\b"), 1.0),
    "connection": (re.compile(r"\bconnection\b"), 1.5),
    "constraint": (re.compile(r"\bconstraint\b"), 1.5),
    "requirement": (re.compile(r"\brequirement\b"), 1.5),
    "import": (re.compile(r"\bimport\b"), 0.5),
    "enum def": (re.compile(r"\benum\s+def\b"), 1.0),
    "use case": (re.compile(r"\buse\s+case\b"), 1.0),
}


_MODEL_LOCK = threading.Lock()
_embedding_model: Any | None = None


def get_embedding_model() -> Any:
    """Shared all-MiniLM-L6-v2 instance (loaded once, safe to call from several threads)."""
    global _embedding_model
    with _MODEL_LOCK:
        if _embedding_model is None:
            from sentence_transformers import SentenceTransformer

            _embedding_model = SentenceTransformer(_EMBEDDING_MODEL)
        return _embedding_model


def encode(texts: list[str]) -> Any:
    """Thread-safe normalized embeddings."""
    model = get_embedding_model()
    with _MODEL_LOCK:
        return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def requirement_coverage_score(
    requirements_json: dict[str, list[str]], sysml_code: str
) -> dict:
    requirements = [
        requirement
        for category_requirements in requirements_json.values()
        for requirement in category_requirements
    ]
    sysml_lines = [line.strip() for line in sysml_code.splitlines() if line.strip()]

    if not requirements:
        return {
            "rcs": 1.0,
            "covered": 0,
            "total": 0,
            "uncovered_requirements": [],
        }
    if not sysml_lines:
        return {
            "rcs": 0.0,
            "covered": 0,
            "total": len(requirements),
            "uncovered_requirements": requirements,
        }

    requirement_embeddings = encode(requirements)
    line_embeddings = encode(sysml_lines)

    uncovered_requirements = []
    covered = 0
    for requirement, requirement_embedding in zip(
        requirements, requirement_embeddings
    ):
        max_similarity = max(
            float(requirement_embedding @ line_embedding)
            for line_embedding in line_embeddings
        )
        if max_similarity >= _RCS_THRESHOLD:
            covered += 1
        else:
            uncovered_requirements.append(requirement)

    return {
        "rcs": covered / len(requirements),
        "covered": covered,
        "total": len(requirements),
        "uncovered_requirements": uncovered_requirements,
    }


def structural_richness_score(sysml_code: str) -> dict:
    elements = {
        element: len(pattern.findall(sysml_code))
        for element, (pattern, _) in _SRS_ELEMENTS.items()
    }
    max_possible = sum(weight for _, weight in _SRS_ELEMENTS.values())
    weighted_sum = sum(
        weight for element, (_, weight) in _SRS_ELEMENTS.items() if elements[element]
    )
    return {
        "srs": weighted_sum / max_possible,
        "elements": elements,
    }


def evaluate_model(requirements_json: dict[str, list[str]], sysml_code: str) -> dict:
    """RCS and SRS (no LLM calls). The LJS is computed afterwards by evaluator/ over the stored models."""
    return {
        "requirement_coverage": requirement_coverage_score(
            requirements_json,
            sysml_code,
        ),
        "structural_richness": structural_richness_score(sysml_code),
    }
