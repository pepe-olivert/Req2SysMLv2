"""Evaluation CLIs. This package distributes code only, so scripts explain what is missing instead of a traceback."""

import sys

_ON_REQUEST = ("The input requirements, generated models, error banks, judgments and annotation sheets of the study "
               "are not distributed; they are available on request (see Data availability in README.md).")


def require_study_results() -> None:
    """Stops a script that only reads stored results of the study when there are none (invented example excluded)."""
    from core.config import RESULTS_DIR

    if not any(path.parent.name != "example" for path in RESULTS_DIR.glob("*/*.csv")):
        raise SystemExit(f"error: this script reads the stored results of the study, and {RESULTS_DIR} has none.\n"
                         f"{_ON_REQUEST} No LLM was called and nothing was written.")


def _explain_failure(exc_type, exc, tb):
    if issubclass(exc_type, FileNotFoundError):
        if exc.filename in ("java", "javac"):
            print(f"error: {exc.filename} not found. This step needs a JDK and the Pilot Implementation (see README.md).",
                  file=sys.stderr)
        else:
            print(f"error: required input not found: {exc.filename or exc}\n{_ON_REQUEST}", file=sys.stderr)
        return
    sys.__excepthook__(exc_type, exc, tb)
    if issubclass(exc_type, (AttributeError, KeyError, ValueError, IndexError)):
        print(f"\nnote: if some stored results are missing, this error may come from reading them. {_ON_REQUEST}",
              file=sys.stderr)


sys.excepthook = _explain_failure
