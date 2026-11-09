# LEXER.md
Repair guide for **lexer-level token recognition errors** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when the validator reports lexer-style problems such as:

- `token recognition error at: '...'`
- illegal characters inside identifiers, names, or strings
- malformed quote escapes

Lexer errors happen before parsing. The goal is to transform raw text into valid tokens with minimal edits.

---

# 1) Core Token Facts

## 1.1 RULE_ID

    RULE_ID:
        ('a'..'z' | 'A'..'Z' | '_') ('a'..'z' | 'A'..'Z' | '_' | '0'..'9')*
    ;

Implications:
- Plain identifiers may contain only letters, digits, and underscore.
- They cannot start with a digit.
- Hyphens, spaces, and most symbols are not allowed in `RULE_ID`.

---

## 1.2 RULE_UNRESTRICTED_NAME

    RULE_UNRESTRICTED_NAME:
        ''' ... '''
    ;

Implications:
- If a name contains spaces or special characters, convert it into a single-quoted unrestricted name.
- Escapes must remain valid inside the quotes.

---

## 1.3 RULE_STRING_VALUE

    RULE_STRING_VALUE:
        '"' ... '"'
    ;

Implications:
- Strings require balanced double quotes.
- Embedded quotes must be escaped.

---

## 1.4 Comment tokens

    RULE_REGULAR_COMMENT: '/*' .*? '*/';
    RULE_ML_NOTE: '//*' .*? '*/' -> channel(HIDDEN);
    RULE_SL_NOTE: '//' ... -> channel(HIDDEN);

Implications:
- If the grammar expects a regular comment block, use `/* ... */`.
- `//` comments are hidden notes and may not satisfy parser rules that require `RULE_REGULAR_COMMENT`.

---

# 2) Canonical Repair Patterns

## Case A — illegal identifier characters

Invalid:

    part CO2-Sensor : SensorDef;

Fix policy:
- Either remove/replace the illegal character in a minimal way,
- or convert the token to an unrestricted name if preserving text matters more.

Preferred repair:

    part 'CO2-Sensor' : SensorDef;

---

## Case B — identifier starts with a digit

Invalid:

    part 3Sensor : SensorDef;

Fix policy:
- Convert it to a quoted unrestricted name unless there is an obvious local naming convention.

Repair:

    part '3Sensor' : SensorDef;

---

## Case C — unterminated string

Invalid:

    locale "en

Fix:

    locale "en"

---

## Case D — broken escape sequence in name or string

Fix policy:
- Normalize the escape so the token closes correctly.
- If escaping is unnecessary, remove the stray backslash.

---

## Case E — illegal raw character where a comment block is intended

Fix policy:
- If plain text appears where a regular comment token is expected, wrap it in `/* ... */`.

---

# 3) Minimal Change Policy

The fixer MUST:

1. Repair the token with the smallest textual edit.
2. Prefer quote conversion over renaming when preserving the original text matters.
3. Preserve valid neighboring tokens.
4. Avoid changing declaration structure unless the token error directly affects it.
5. Ensure the repaired text becomes a valid token before worrying about higher-level syntax.

---

# 4) Final Checklist

Before returning the fix, verify:

- Every identifier matches `RULE_ID` or is properly quoted as `RULE_UNRESTRICTED_NAME`.
- Every string is properly closed and escaped.
- Required regular comments use `/* ... */`.
- No illegal raw characters remain in tokens.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
