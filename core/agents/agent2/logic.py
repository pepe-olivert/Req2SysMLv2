import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...llm_client import LLMClient, UsageTracker
from ...utils import get_knowledge
from ...validate.SysMLv2LoggingParser import SysMLv2LoggingParser
from .error_router import ErrorRouter
from .prompts import FIX_SYSTEM_PROMPT, GENERATE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RepairKnobs:
    do_repair: bool
    use_routing: bool   # route + sort errors by (priority, line, column)
    use_kb: bool        # inject the knowledge base of the current error's router category into the fix prompt
    # Show the router category and priority in the repair message. None = same as use_routing (C1-C4).
    show_routing: bool | None = None
    # Whole-file revision baseline (LaVoie et al.): one call per iteration with the complete model and every
    # current diagnostic, asking for the corrected model; no router, no KB, same guard and iteration limit.
    whole_file: bool = False

    @property
    def shows_routing(self) -> bool:
        return self.use_routing if self.show_routing is None else self.show_routing


# Ablation conditions. C4 is the full framework (what execute() runs).
CONDITIONS: dict[str, RepairKnobs] = {
    "C1": RepairKnobs(do_repair=False, use_routing=False, use_kb=False),  # generate + validate
    "C2": RepairKnobs(do_repair=True, use_routing=False, use_kb=False),   # blind repair, parser order
    "C3": RepairKnobs(do_repair=True, use_routing=True, use_kb=False),    # + routing
    "C4": RepairKnobs(do_repair=True, use_routing=True, use_kb=True),     # + knowledge base
    # Decompositions of C3/C4 (JSS revision), all on the same loop and guard:
    # C2 + the KB of the current error (router used only to pick that KB; parser order, no label shown).
    "C2KB": RepairKnobs(do_repair=True, use_routing=False, use_kb=True, show_routing=False),
    # C3a: priority order without showing the label; C3b: parser order showing label and priority.
    "C3a": RepairKnobs(do_repair=True, use_routing=True, use_kb=False, show_routing=False),
    "C3b": RepairKnobs(do_repair=True, use_routing=False, use_kb=False, show_routing=True),
    # R8 baseline: whole-file revision from the full diagnostic list (system prompt: fix_all_prompt.md).
    "FULLREV": RepairKnobs(do_repair=True, use_routing=False, use_kb=False, show_routing=False, whole_file=True),
}

# System prompt of FULLREV: FIX_SYSTEM_PROMPT adapted to "fix all diagnostics" (single-error scope removed).
FIX_ALL_SYSTEM_PROMPT = (Path(__file__).resolve().parent / "fix_all_prompt.md").read_text(encoding="utf-8")

_NO_POS = 10**9
_FENCE_RE = re.compile(r"^[ \t]*```[^\n]*(?:\n|$)", re.MULTILINE)
_PACKAGE_RE = re.compile(r"\bpackage\b")

# Content-preservation guard: a repair must return the whole file. An answer shorter than this
# share of its input, or with fewer packages, is treated as a fragment: retried once, then rejected.
GUARD_MIN_LENGTH_RATIO = 0.7


def _position_key(error: Dict[str, Any]) -> tuple:
    line = error.get("line")
    column = error.get("column")
    return (line if line is not None else _NO_POS, column if column is not None else _NO_POS)


class SysMLAgent:
    """Generates SysML v2 from categorized requirements and repairs it against the ANTLR validator.

    Nothing is written to disk here: callers persist the returned results.
    The instance accumulates LLM usage per category, so use one instance per concurrent task.
    """

    _ERROR_RE = re.compile(r"^Syntax error at line\s+(?P<line>\d+),\s+column\s+(?P<col>\d+):\s*(?P<msg>.*)$")

    def __init__(self, llm_client: LLMClient):
        self.llm_client = UsageTracker(llm_client)
        self.router = ErrorRouter()

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _error_signature(self, error: Dict[str, Any]) -> str:
        line = error.get("line")
        column = error.get("column")
        msg = (error.get("error") or "").strip()
        return f"{line}:{column}:{msg}"

    def _indent_level(self, line: str) -> int:
        """
        Returns indentation level in 'spaces' with tabs expanded.
        """
        expanded = line.expandtabs(4)
        return len(expanded) - len(expanded.lstrip(" "))

    def _extract_block_by_indent(self, lines: List[str], err_line_1based: int) -> str:
        """
        Extracts a SysML 'block' using indentation rules.
        - err_line_1based: line number from parser (1-based)
        """
        idx = err_line_1based - 1
        if idx < 0 or idx >= len(lines):
            return ""

        start_line = lines[idx].rstrip("\n")
        start_indent = self._indent_level(start_line)

        # If there's no next line, block is the error line.
        if idx + 1 >= len(lines):
            return start_line.strip("\n")

        # Determine if it is a multi-line block according to the rule
        next_line = lines[idx + 1].rstrip("\n")
        next_indent = self._indent_level(next_line)

        if next_line.strip() == "":
            # Skip empty lines when deciding whether the block continues
            j = idx + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j >= len(lines):
                return start_line.strip("\n")
            next_line = lines[j].rstrip("\n")
            next_indent = self._indent_level(next_line)

            # If the first non-empty next line is not more indented -> single line block
            if next_indent <= start_indent:
                return start_line.strip("\n")
        else:
            if next_indent <= start_indent:
                return start_line.strip("\n")

        # Collect while indentation is greater than start_indent (blank lines allowed)
        block_lines = [start_line]
        k = idx + 1
        while k < len(lines):
            cur = lines[k].rstrip("\n")
            if cur.strip() == "":
                block_lines.append(cur)
                k += 1
                continue

            cur_indent = self._indent_level(cur)
            if cur_indent <= start_indent:
                break

            block_lines.append(cur)
            k += 1

        return "\n".join(block_lines).strip("\n")

    def _parse_validator_errors(self, errors_text: str) -> List[Dict[str, Any]]:
        """
        Parses the validator error string into structured entries.
        """
        entries: List[Dict[str, Any]] = []
        if not errors_text or errors_text.strip() == "" or errors_text.strip() == "No errors":
            return entries

        for raw_line in errors_text.splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            m = self._ERROR_RE.match(raw_line)
            if not m:
                # Unknown line format: keep it anyway
                entries.append({"error": raw_line, "line": None, "column": None})
                continue

            entries.append(
                {
                    "error": m.group("msg").strip(),
                    "line": int(m.group("line")),
                    "column": int(m.group("col")),
                }
            )
        return entries

    @staticmethod
    def clean_sysml(sysml_code: str) -> str:
        """
        Normalizes raw LLM output into the exact text handed to the parser: drops markdown
        fence lines (```sysml ... ```) and, only when the whole answer came back as one escaped
        line, decodes its literal escape sequences (e.g. "\\n").
        """
        sysml_code = _FENCE_RE.sub("", sysml_code)
        if "\n" not in sysml_code.strip() and "\\n" in sysml_code:
            try:
                # latin-1 + backslashreplace keeps non-ASCII characters intact.
                return sysml_code.encode("latin-1", "backslashreplace").decode("unicode_escape")
            except UnicodeDecodeError:
                return sysml_code
        return sysml_code

    def validate_sysml(self, sysml_code: str) -> List[Dict[str, Any]]:
        """
        Validates the syntax of the generated SysML v2 code. Returns [] when valid.
        """
        sysml_code = self.clean_sysml(sysml_code)

        validator = SysMLv2LoggingParser(sysml_code)
        validator.parse()
        errors_text = validator.get_errors().strip()

        if errors_text == "":
            return []

        lines = sysml_code.splitlines()
        results: List[Dict[str, Any]] = []
        for e in self._parse_validator_errors(errors_text):
            line_no = e.get("line")
            block = self._extract_block_by_indent(lines, line_no) if isinstance(line_no, int) else ""
            results.append(
                {
                    "error": e.get("error"),
                    "line": e.get("line"),
                    "column": e.get("column"),
                    "sysml_block": block,
                }
            )
        return results

    # ------------------------------------------------------------------
    # LLM steps
    # ------------------------------------------------------------------
    def generate_sysml(self, requirements: str, system_prompt: str = GENERATE_SYSTEM_PROMPT) -> str:
        """
        Uses the LLM to generate SysML v2 notation (system_prompt: see generation_prompts.py).
        """
        messages = [
            {"role": "developer", "content": system_prompt},
            {"role": "user", "content": f"Generate SysML v2 code for the following categorized requirements (JSON): \n {requirements} \n Remember: output only SysML v2 code."},
        ]
        return self.llm_client.chat_with_metadata(messages=messages)["content"]

    @staticmethod
    def _format_error(error: Dict[str, Any], show_routing: bool) -> str:
        text = f"line {error.get('line')}, column {error.get('column')}: {error.get('error')}"
        if show_routing and error.get("category_id"):
            text += f"  [category {error['category_id']}, priority {error.get('priority')}]"
        return text

    def build_repair_message(
        self,
        sysml_code: str,
        current_error: Dict[str, Any],
        all_errors: List[Dict[str, Any]],
        knowledge: str = "",
        show_routing: bool = False,
        retry_note: str = "",
    ) -> str:
        """User message of one repair call: delimited sections, the code last with real line breaks."""
        sections = [
            "Fix the CURRENT ERROR in the SysML v2 file below so that it passes the validator.\n"
            "Output ONLY the corrected COMPLETE file (every line), no explanations.",
        ]
        if retry_note:
            sections.append(f"=== WARNING ===\n{retry_note}")
        sections.append("=== CURRENT ERROR ===\n" + self._format_error(current_error, show_routing))
        sections.append("=== CODE BLOCK OF THE CURRENT ERROR (starts at the reported line) ===\n"
                        + (current_error.get("sysml_block") or ""))
        sections.append("=== ALL ERRORS CURRENTLY REPORTED BY THE VALIDATOR (context only) ===\n"
                        + "\n".join(f"- {self._format_error(e, show_routing)}" for e in all_errors))
        if knowledge and show_routing:
            category = current_error.get("category_id", "")
            sections.append(f"=== CATEGORY KNOWLEDGE BASE ({category}) ===\n{knowledge}")
        elif knowledge:  # C2KB: the KB is added without naming its category
            sections.append(f"=== KNOWLEDGE BASE ===\n{knowledge}")
        sections.append("=== SYSML V2 FILE ===\n" + self.clean_sysml(sysml_code))
        return "\n\n".join(sections)

    def fix_sysml_code(
        self,
        sysml_code: str,
        current_error: Dict[str, Any],
        all_errors: List[Dict[str, Any]],
        knowledge: str = "",
        show_routing: bool = False,
        retry_note: str = "",
    ) -> str:
        """One repair call for `current_error`. Returns the model's corrected file (raw text)."""
        message = self.build_repair_message(sysml_code, current_error, all_errors, knowledge, show_routing,
                                            retry_note)
        response = self.llm_client.chat_with_metadata(
            messages=[
                {"role": "developer", "content": FIX_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        )
        return response["content"].strip()

    def build_fix_all_message(self, sysml_code: str, all_errors: List[Dict[str, Any]], retry_note: str = "") -> str:
        """User message of one FULLREV call: every current diagnostic, then the complete file."""
        sections = [
            "Fix ALL the errors reported by the validator in the SysML v2 file below so that it passes the validator.\n"
            "Output ONLY the corrected COMPLETE file (every line), no explanations.",
        ]
        if retry_note:
            sections.append(f"=== WARNING ===\n{retry_note}")
        sections.append("=== ALL ERRORS CURRENTLY REPORTED BY THE VALIDATOR ===\n"
                        + "\n".join(f"- {self._format_error(e, False)}" for e in all_errors))
        sections.append("=== SYSML V2 FILE ===\n" + self.clean_sysml(sysml_code))
        return "\n\n".join(sections)

    def fix_all_sysml_code(self, sysml_code: str, all_errors: List[Dict[str, Any]], retry_note: str = "") -> str:
        """One FULLREV call: the model's revised complete file (raw text)."""
        response = self.llm_client.chat_with_metadata(
            messages=[
                {"role": "developer", "content": FIX_ALL_SYSTEM_PROMPT},
                {"role": "user", "content": self.build_fix_all_message(sysml_code, all_errors, retry_note)},
            ],
        )
        return response["content"].strip()

    def loses_content(self, before: str, after: str) -> bool:
        """Content-preservation guard: the repaired file must keep its size and its packages."""
        before, after = self.clean_sysml(before), self.clean_sysml(after)
        if len(after.strip()) < GUARD_MIN_LENGTH_RATIO * len(before.strip()):
            return True
        return len(_PACKAGE_RE.findall(after)) < len(_PACKAGE_RE.findall(before))

    # ------------------------------------------------------------------
    # Unified generate -> validate -> repair loop (pipeline and ablation)
    # ------------------------------------------------------------------
    def _report_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compact error records with router category (always computed, for reporting)."""
        return [
            {
                "line": e.get("line"),
                "column": e.get("column"),
                "message": e.get("error"),
                "error_category": e.get("category_id", "UNKNOWN"),
                "priority": e.get("priority"),
            }
            for e in self.router.route_all(errors)
        ]

    def run_category(
        self,
        category: str,
        requirements: List[str],
        knobs: RepairKnobs,
        max_iterations: int = 10,
        initial_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates the model for one category and repairs it according to `knobs`.

        With `initial_code` the generation step is skipped and the repair starts from that
        exact code (paired design: every condition repairs the same generated model); the
        returned usage then covers the repair calls only.

        Repair loop: after every repair call the model is re-validated and the next error is taken
        from the CURRENT diagnostics (first in parser order, or highest priority when routing is on),
        so every call sees the real line, block and error list. An iteration allows as many calls as
        it started with errors; the loop stops as soon as the model is valid or after
        `max_iterations`. Stagnation (an iteration that leaves the error set unchanged) is flagged
        but does not stop the loop. A repair that loses content (see `loses_content`) is retried
        once with a warning and, if it still loses content, rejected (the model is kept as before).
        """
        self.llm_client.reset()

        if initial_code is None:
            to_process = json.dumps({category: requirements}, ensure_ascii=False, indent=2)
            initial_code = self.generate_sysml(to_process)
        sysml_code = initial_code
        errors = self.validate_sysml(sysml_code)

        initial_error_count = len(errors)
        iterations_used = 0
        stagnation_detected = False
        guard_retries = 0
        guard_rejections = 0
        error_category_counts: Counter[str] = Counter()
        iteration_errors: List[Dict[str, Any]] = [{"iteration": 0, "errors": self._report_errors(errors)}]
        repairs: List[Dict[str, Any]] = []

        if errors and knobs.do_repair:
            for iteration in range(1, max_iterations + 1):
                iterations_used = iteration
                start_signatures = {self._error_signature(e) for e in errors}
                error_category_counts.update(e["error_category"] for e in self._report_errors(errors))
                calls_left = 1 if knobs.whole_file else len(errors)

                while errors and calls_left > 0:
                    calls_left -= 1
                    if knobs.use_routing:
                        to_fix = self.router.route_all(errors)
                        to_fix.sort(key=lambda e: (e.get("priority", 999), *_position_key(e)))
                    elif knobs.shows_routing:
                        to_fix = self.router.route_all(errors)  # C3b: parser order, labels shown
                    else:
                        to_fix = list(errors)  # parser order, no category/priority signal
                    current_error = to_fix[0]  # FULLREV: reported only; the call sees every diagnostic
                    error_category = self.router.route_one(current_error).category_id  # reporting only

                    knowledge_category, knowledge = None, ""
                    if knobs.use_kb:
                        # C4: the routed error carries its category; C2KB: the router only picks the KB.
                        knowledge_category = current_error.get("category_id", error_category)
                        try:
                            knowledge = get_knowledge(knowledge_category)
                        except FileNotFoundError:
                            knowledge_category, knowledge = None, ""

                    def attempt(note: str = "") -> str:
                        if knobs.whole_file:
                            return self.fix_all_sysml_code(sysml_code, to_fix, retry_note=note)
                        return self.fix_sysml_code(sysml_code, current_error, to_fix, knowledge=knowledge,
                                                   show_routing=knobs.shows_routing, retry_note=note)

                    candidate = attempt()
                    retried = rejected = False
                    if self.loses_content(sysml_code, candidate):
                        retried = True
                        guard_retries += 1
                        candidate = attempt(
                            f"Your previous answer kept only {len(self.clean_sysml(candidate).strip())} of the "
                            f"{len(self.clean_sysml(sysml_code).strip())} characters of the file. Return the "
                            f"COMPLETE file with every line, changing only what the "
                            f"{'reported errors require' if knobs.whole_file else 'CURRENT ERROR requires'}."
                        )
                        if self.loses_content(sysml_code, candidate):
                            rejected = True
                            guard_rejections += 1

                    code_before = sysml_code
                    errors_before = self._report_errors(errors)
                    if not rejected:
                        sysml_code = candidate
                        errors = self.validate_sysml(sysml_code)
                    repairs.append(
                        {
                            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                            "iteration": iteration,
                            "current_error": {
                                "line": current_error.get("line"),
                                "column": current_error.get("column"),
                                "message": current_error.get("error"),
                            },
                            "error_category": error_category,
                            "knowledge_category": knowledge_category,
                            "guard_retried": retried,
                            "guard_rejected": rejected,
                            "code_before": code_before,
                            "code_after": candidate,
                            "errors_before": errors_before,
                            "errors_after": self._report_errors(errors) if not rejected else errors_before,
                        }
                    )

                iteration_errors.append({"iteration": iteration, "errors": self._report_errors(errors)})
                if {self._error_signature(e) for e in errors} == start_signatures:
                    stagnation_detected = True
                if not errors:
                    break

        final_error_count = len(errors)
        error_reduction_pct = (
            ((initial_error_count - final_error_count) / initial_error_count) * 100
            if initial_error_count
            else 0.0
        )
        return {
            "category_name": category,
            "raw_output": sysml_code,  # final LLM text, before clean_sysml()
            "sysml_code": self.clean_sysml(sysml_code),  # exact text checked by the parser
            "final_errors": self._report_errors(errors),
            "converged": not errors,
            "iterations_used": iterations_used,
            "initial_error_count": initial_error_count,
            "final_error_count": final_error_count,
            "error_reduction_pct": error_reduction_pct,
            "stagnation_detected": stagnation_detected,
            "guard_retries": guard_retries,
            "guard_rejections": guard_rejections,
            "error_category_counts": dict(error_category_counts),
            "iteration_errors": iteration_errors,
            "repairs": repairs,
            "usage": self.llm_client.snapshot(),
        }

    def execute(self, requirements: Dict[str, List[str]], max_iterations: int = 10, condition: str = "C4"):
        """
        Runs the full framework (C4 by default) over every category of `requirements`.
        """
        if not isinstance(requirements, dict):
            raise ValueError("requirements must be a dict with category keys and requirement-list values.")

        knobs = CONDITIONS[condition]
        return {
            str(category): self.run_category(str(category), reqs, knobs, max_iterations)
            for category, reqs in requirements.items()
        }
