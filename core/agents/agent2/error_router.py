import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# -------------------------
# Categories (allowlist)
# -------------------------
DELIMITERS = "DELIMITERS"
DOC_COMMENT = "DOC_COMMENT"
CONSTRAINT_EXPR = "CONSTRAINT_EXPR"
QUALIFICATION = "QUALIFICATION"
DECLARATION_FORM = "DECLARATION_FORM"
LITERALS_STRINGS = "LITERALS_STRINGS"
ALT_NO_VIABLE = "ALT_NO_VIABLE"
LEXER = "LEXER"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RoutedError:
    category_id: str
    confidence: float
    priority: int
    signals: List[str]


class ErrorRouter:
    """
    Deterministic router from ANTLR-like error message + sysml_block to a category_id.
    Input errors must be a list[dict] like:
      {
        "error": "...",
        "line": 46,
        "column": 21,
        "sysml_block": "   doc  \"...\" "
      }
    """

    # --- regex helpers for parsing ANTLR msg ---
    _re_mismatched = re.compile(r"mismatched input\s+'([^']*)'\s+expecting\s+\{([^}]*)\}", re.IGNORECASE)
    _re_extraneous = re.compile(r"extraneous input\s+'([^']*)'\s+expecting\s+\{([^}]*)\}", re.IGNORECASE)
    _re_missing = re.compile(r"missing\s+([^ ]+)\s+at\s+'([^']*)'", re.IGNORECASE)
    _re_no_viable = re.compile(r"no viable alternative at input\s+'([^']*)'", re.IGNORECASE)
    _re_token_recognition = re.compile(r"token recognition error at:\s*'([^']*)'", re.IGNORECASE)
    _re_any_input = re.compile(r"(?:mismatched|extraneous) input\s+'([^']*)'", re.IGNORECASE)
    _re_doc_word = re.compile(r"\b(doc|comment|rep)\b", re.IGNORECASE)
    _re_comparison = re.compile(r"==|!=|<=|>=|<|>|\b(and|or|xor|implies|not)\b")

    # Tokens that can only start or continue an expression, never a declaration.
    _expression_tokens = {"==", "!=", "===", "!==", "<=", ">=", "<", ">", "and", "or", "xor", "implies", "not",
                          "+", "-", "*", "/", "%", "**", "^", "true", "false"}

    @staticmethod
    def _norm(s: Optional[str]) -> str:
        return (s or "").strip()

    @staticmethod
    def _extract_expect_set(msg: str) -> List[str]:
        """
        Extract tokens listed in `expecting { ... }` when present.
        Returns normalized token strings (no quotes, stripped).
        """
        # Try mismatched/extraneous patterns first
        m = ErrorRouter._re_mismatched.search(msg) or ErrorRouter._re_extraneous.search(msg)
        if not m:
            return []
        raw = m.group(2)
        toks = [t.strip() for t in raw.split(",")]
        # Remove surrounding quotes if any
        toks = [t.strip().strip("'").strip('"') for t in toks if t]
        return toks

    @staticmethod
    def _extract_offending_token(msg: str) -> Optional[str]:
        """
        Return the offending token for common ANTLR messages.
        """
        m = ErrorRouter._re_mismatched.search(msg)
        if m:
            return m.group(1)
        m = ErrorRouter._re_extraneous.search(msg)
        if m:
            return m.group(1)
        m = ErrorRouter._re_missing.search(msg)
        if m:
            return m.group(2)
        m = ErrorRouter._re_no_viable.search(msg)
        if m:
            return m.group(1)
        m = ErrorRouter._re_token_recognition.search(msg)
        if m:
            return m.group(1)
        m = ErrorRouter._re_any_input.search(msg)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _contains_any(haystack: str, needles: List[str]) -> bool:
        h = haystack.lower()
        return any(n.lower() in h for n in needles)

    def route_one(self, err: Dict[str, Any]) -> RoutedError:
        msg = self._norm(err.get("error"))
        block = self._norm(err.get("sysml_block"))
        error_line = block.splitlines()[0] if block else ""  # the block starts at the reported line
        offending = self._extract_offending_token(msg) or ""
        expect = self._extract_expect_set(msg)

        signals: List[str] = []
        scores: Dict[str, int] = {
            DELIMITERS: 0,
            DOC_COMMENT: 0,
            CONSTRAINT_EXPR: 0,
            QUALIFICATION: 0,
            DECLARATION_FORM: 0,
            LITERALS_STRINGS: 0,
            ALT_NO_VIABLE: 0,
            LEXER: 0,
            UNKNOWN: 0,
        }

        # --- 1) Lexer-level errors ---
        if self._re_token_recognition.search(msg):
            scores[LEXER] += 10
            signals.append("msg:token_recognition_error")

        # --- 2) Missing delimiter tokens ---
        if "missing" in msg.lower():
            m = self._re_missing.search(msg)
            if m:
                missing_tok = m.group(1).strip()
                if missing_tok in {"';'", "'}'", "')'", "']'"} or missing_tok in {"';'", "'}'", "')'", "']'"}:
                    scores[DELIMITERS] += 10
                    signals.append(f"msg:missing:{missing_tok}")

            # Common missing delimiter substring fallback
            if self._contains_any(msg, ["missing ';'", "missing '}'", "missing ')'", "missing ']'"]):
                scores[DELIMITERS] += 10
                signals.append("msg:missing_delimiter")

        # --- 3) Extraneous input often means form/ordering issues, or delimiters ---
        if "extraneous input" in msg.lower():
            scores[DECLARATION_FORM] += 5
            signals.append("msg:extraneous_input")
            if self._contains_any(msg, ["expecting ';'", "expecting '}'", "expecting ')'", "expecting ']'"]):
                scores[DELIMITERS] += 6
                signals.append("msg:extraneous_expect_delimiter")

        # --- 4) No viable alternative is a useful bucket ---
        if "no viable alternative" in msg.lower():
            scores[ALT_NO_VIABLE] += 6
            signals.append("msg:no_viable_alternative")

        # --- 5) Detect DOC/COMMENT issues from the error line and expect-set ---
        if self._re_doc_word.search(error_line):
            scores[DOC_COMMENT] += 4
            signals.append("line:doc/comment/rep")
        if self._re_doc_word.search(offending):
            # e.g. "no viable alternative at input 'attribute doc'": 'doc' used as a name
            scores[DOC_COMMENT] += 8
            signals.append("offending:doc_keyword")
        if any(tok == "RULE_REGULAR_COMMENT" for tok in expect):
            scores[DOC_COMMENT] += 8
            signals.append("expect:RULE_REGULAR_COMMENT")
        if any(tok.lower() == "locale" for tok in expect):
            # In your grammar, doc rule often expects 'locale' then string + comment
            scores[DOC_COMMENT] += 2
            signals.append("expect:locale")

        # --- 6) Constraint/assert expressions written where a declaration is expected ---
        # e.g. "assert x == 1;" or "constraint C { assert a::b >= 5; }": the parser reads
        # "assert x" as a declaration and fails at the operator (expecting 'redefines', ...).
        if offending.lower() in self._expression_tokens and "redefines" in expect:
            scores[CONSTRAINT_EXPR] += 12
            signals.append("offending:expression_token_in_declaration")
        if offending.lower().startswith("assert") and "no viable alternative" in msg.lower():
            scores[CONSTRAINT_EXPR] += 12
            signals.append("msg:no_viable_assert")
        if (offending == ";" and "extraneous input" in msg.lower()
                and ("assert" in error_line or self._re_comparison.search(error_line))):
            scores[CONSTRAINT_EXPR] += 12
            signals.append("line:semicolon_after_expression")
        if re.match(r"\s*assert\b(?!\s+constraint\b)", error_line) and "redefines" not in expect:
            # bare "assert <expr>" whose operator the parser misreads (e.g. '<' taken as a type bracket)
            scores[CONSTRAINT_EXPR] += 12
            signals.append("line:bare_assert")

        # --- 7) Qualification issues: :: / ::> / :> at the offending token ---
        if ":" in offending:
            scores[QUALIFICATION] += 7
            signals.append("offending:qualification(:/::/::>/:>)")
        # Some mismatch messages include ':' trouble near namespaces/types
        if self._contains_any(msg, ["mismatched input ':'", "mismatched input '::'"]):
            scores[QUALIFICATION] += 5
            signals.append("msg:mismatched_colon_or_scope")

        # --- 8) Literal/string issues ---
        # If offending token contains quotes or looks like a string literal:
        if offending.startswith('"') or offending.startswith("'") or ('"' in offending) or ("'" in offending):
            scores[LITERALS_STRINGS] += 5
            signals.append("offending:quoted")
        if any(tok in {"RULE_STRING_VALUE", "RULE_INT", "RULE_DECIMAL"} for tok in expect):
            scores[LITERALS_STRINGS] += 3
            signals.append("expect:literal_token")
        if self._contains_any(msg, ["token recognition error", "invalid character"]):
            scores[LITERALS_STRINGS] += 3
            signals.append("msg:lexeme_issue")

        # --- 9) Declaration form / ordering issues (generic) ---
        if self._contains_any(msg, ["mismatched input", "extraneous input"]):
            scores[DECLARATION_FORM] += 2
            signals.append("msg:mismatch_or_extraneous")
        # Expecting identifiers/names is often "wrong form here"
        if any(tok in {"RULE_ID", "RULE_UNRESTRICTED_NAME"} for tok in expect):
            scores[DECLARATION_FORM] += 2
            signals.append("expect:id_or_name")

        # --- 10) Tie-break preference follows the repair priority ---
        ranking = [DELIMITERS, DOC_COMMENT, CONSTRAINT_EXPR, QUALIFICATION, DECLARATION_FORM, LITERALS_STRINGS,
                   ALT_NO_VIABLE, LEXER, UNKNOWN]

        best_cat = UNKNOWN
        best_score = -1
        for cat in ranking:
            sc = scores.get(cat, 0)
            if sc > best_score:
                best_score = sc
                best_cat = cat
        if best_score <= 0:
            best_cat = UNKNOWN  # no signal at all

        # Confidence: simple normalization (cap at 1.0)
        # You can tune these numbers later; the goal is a useful heuristic.
        confidence = min(1.0, max(0.2, best_score / 10.0))

        # Priority: lower is "fix earlier".
        # Delimiters first (they cause cascades), then doc/comment, then the rest.
        priority_map = {
            DELIMITERS: 10,
            DOC_COMMENT: 20,
            CONSTRAINT_EXPR: 25,
            QUALIFICATION: 30,
            DECLARATION_FORM: 40,
            LITERALS_STRINGS: 50,
            ALT_NO_VIABLE: 60,
            LEXER: 70,
            UNKNOWN: 90,
        }
        priority = priority_map.get(best_cat, 90)

        return RoutedError(category_id=best_cat, confidence=confidence, priority=priority, signals=signals)

    def route_all(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Annotate each error dict with routing info.
        Returns new list of dicts with added keys: category_id, confidence, priority, signals.
        """
        routed: List[Dict[str, Any]] = []
        for e in errors:
            r = self.route_one(e)
            out = dict(e)
            out["category_id"] = r.category_id
            out["confidence"] = r.confidence
            out["priority"] = r.priority
            out["signals"] = r.signals
            routed.append(out)
        return routed

    def pick_next_error(self, errors: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Choose the next error to fix.
        Strategy: route all, then pick lowest (priority, line, column).
        """
        if not errors:
            return None
        routed = self.route_all(errors)
        routed.sort(key=lambda e: (e.get("priority", 999), e.get("line", 10**9), e.get("column", 10**9)))
        return routed[0]