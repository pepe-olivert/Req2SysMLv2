"""Analyses of the stored results (no LLM calls). Run as a script, each one stops first if there are no results."""

import sys

from evaluation import require_study_results

if sys.argv[:1] == ["-m"]:  # python -m evaluation.analysis.<script>; never when a test imports the package
    require_study_results()
