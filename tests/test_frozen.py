"""The generation prompt, repair prompt, router and knowledge bases must stay as they were in the experiments.

tests/golden/frozen_files.json holds the SHA-256 of every frozen file, taken from the frozen version of the code.
tests/golden/repair_messages.json pins the exact requests of C2, C3, C4 (repair) and of the generation stage, built
from the invented inputs of tests/frozen_support.py and examples/ (the study data are not distributed).
"""

import json
import re

from evaluation.common import frozen_file_mismatches
from frozen_support import EXAMPLE, FROZEN_MANIFEST, GOLDEN, INVALID_SAMPLES, digest, first_iteration_requests, generation_request


def test_frozen_files_match_the_stored_hashes():
    manifest = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    assert len(manifest["files"]) >= 11  # prompts, router and every knowledge base
    assert frozen_file_mismatches() == []


def test_repair_requests_of_c2_c3_c4_are_unchanged():
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))["samples"]
    assert {entry["category"] for entry in golden} == set(INVALID_SAMPLES)
    for entry in golden:
        for condition in ("C2", "C3", "C4"):
            requests = first_iteration_requests(INVALID_SAMPLES[entry["category"]], condition)
            assert len(requests) == entry[condition]["calls"] and requests
            assert digest(requests) == entry[condition]["sha256"], (entry["category"], condition)


def test_invalid_samples_reach_every_knowledge_base_in_c4():
    reached = set()
    for code in INVALID_SAMPLES.values():
        for request in first_iteration_requests(code, "C4"):
            reached |= set(re.findall(r"=== CATEGORY KNOWLEDGE BASE \((\w+)\) ===", request[-1]["content"]))
    assert reached == {"ALT_NO_VIABLE", "CONSTRAINT_EXPR", "DECLARATION_FORM", "DELIMITERS", "DOC_COMMENT", "LEXER",
                       "LITERALS_STRINGS", "QUALIFICATION", "UNKNOWN"}


def test_generation_request_is_unchanged():
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))["generation"]
    reqs = json.loads(EXAMPLE.read_text(encoding="utf-8"))["requirements"]
    assert set(golden) == set(reqs)
    for category, expected in golden.items():
        assert digest([generation_request(category, reqs[category])]) == expected


def test_example_is_marked_as_invented_and_its_digest_is_valid():
    from evaluation.common import load_best_requirements

    payload = load_best_requirements(EXAMPLE)
    assert "INVENTED" in payload["notice"]
    assert len(payload["requirements"]) == 2 and 4 <= sum(map(len, payload["requirements"].values())) <= 6
