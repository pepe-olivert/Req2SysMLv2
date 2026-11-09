from typing import Any


def deduplicate_requirements(
    requirements: dict[str, list[str]], similarity_threshold: float = 0.92
) -> tuple[dict[str, list[str]], int]:
    deduplicated: dict[str, list[str]] = {}
    duplicates_removed = 0

    for category, category_requirements in requirements.items():
        unique_requirements = list(dict.fromkeys(category_requirements))
        duplicates_removed += len(category_requirements) - len(unique_requirements)

        if len(unique_requirements) < 2:
            deduplicated[category] = unique_requirements
            continue

        # Shared all-MiniLM-L6-v2 instance: safe when several extractions run in parallel.
        from ..evaluation.semantic_eval import encode

        embeddings = encode(unique_requirements)
        kept_requirements: list[str] = []
        kept_embeddings: list[Any] = []

        for requirement, embedding in zip(unique_requirements, embeddings):
            if any(
                float(embedding @ kept_embedding) > similarity_threshold
                for kept_embedding in kept_embeddings
            ):
                duplicates_removed += 1
                continue

            kept_requirements.append(requirement)
            kept_embeddings.append(embedding)

        deduplicated[category] = kept_requirements

    return deduplicated, duplicates_removed
