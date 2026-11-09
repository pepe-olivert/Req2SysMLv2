# DOC_COMMENT.md
Repair guide for **documentation, comments, and textual representations** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when a parser error occurs in blocks containing:

- `doc ...`
- `comment ...`
- `rep ... language ...`
- `locale "..."` associated with the above
- or when the parser expects `RULE_REGULAR_COMMENT`

The goal of the fix is to **transform the fragment into a syntactically valid form according to the grammar with minimal changes**.

Large structural rewrites of the model are NOT allowed.

---

# 1) Relevant Grammar Tokens

## RULE_REGULAR_COMMENT

Mandatory comment block used by `doc`, `comment`, and `rep` constructs.

Valid format:

    /* ... */

Example:

    doc /* Sensor configured to measure CO2 concentration */

IMPORTANT:
`//` and `//* ... */` comments are defined as notes and go to the `HIDDEN` channel in the grammar.
They **do not count as RULE_REGULAR_COMMENT** and therefore cannot be used for `doc`, `comment`, or `rep`.

---

## RULE_STRING_VALUE

Double‑quoted strings.

Example:

    "Sensor configured to measure CO2 concentration"

Commonly used with:

    locale "en"
    language "en"

---

## RULE_UNRESTRICTED_NAME

Single‑quoted name used when identifiers contain spaces or symbols.

Example:

    'CO2 Sensor'

---

## RULE_ID

Standard identifier.

Examples:

    Sensor
    MeasureCO2
    MyPackage

---

# 2) Relevant Grammar Rules

## 2.1 ruleDocumentation

Grammar:

    ruleDocumentation:
        'doc'
        ruleIdentification?
        ('locale' RULE_STRING_VALUE)?
        RULE_REGULAR_COMMENT
    ;

Minimal valid form:

    doc /* text */

Valid forms:

    doc /* text */
    doc <Name> /* text */
    doc <Name> locale "en" /* text */
    doc locale "en" /* text */

Valid examples:

    doc /* Sensor configured to measure CO2 concentration */

    doc <CO2Sensor> /* Measures CO2 */

    doc <CO2Sensor> locale "en" /* Measures CO2 concentration */

Invalid examples:

    doc "Sensor configured to measure CO2 concentration"

Reason: missing `/* ... */`.

    doc // Sensor configured

Reason: `//` is not `RULE_REGULAR_COMMENT`.

    doc /* Sensor configured */ locale "en"

Reason: `locale` must appear BEFORE the comment block.

---

## 2.2 ruleComment

Grammar:

    ruleComment:
        ('comment' ruleIdentification?
            ('about' ruleAnnotation (',' ruleAnnotation)*)?
        )?
        ('locale' RULE_STRING_VALUE)?
        RULE_REGULAR_COMMENT
    ;

The `comment` keyword is optional, but the **RULE_REGULAR_COMMENT block is mandatory**.

Valid forms:

    /* comment text */

    comment /* comment text */

    comment <Id> /* comment text */

    comment about A::B /* explanation */

    comment <Id> about A::B locale "es" /* explanation */

Invalid examples:

    comment "text"

Reason: missing `/* ... */`.

    comment about X "text"

Must end with `/* ... */`.

    comment /* text */ about X

Incorrect order.

---

## 2.3 ruleTextualRepresentation

Grammar:

    ruleTextualRepresentation:
        ('rep' ruleIdentification?)?
        'language' RULE_STRING_VALUE
        RULE_REGULAR_COMMENT
    ;

Valid forms:

    language "en" /* text */

    rep <Id> language "en" /* text */

Invalid examples:

    rep language "en" "text"

Must end with `/* ... */`.

    rep <X> /* text */ language "en"

Incorrect order.

---

# 3) Identification Rules

Grammar:

    ruleIdentification:
        '<' ruleName '>' ruleName?
        | ruleName
    ;

Valid examples:

    <Name>

    <Name> Alias

    Name

    'Name With Spaces'

---

# 4) Common Error Patterns and Fixes

## Case A — String used instead of comment block

Typical error:

    mismatched input '"text"' expecting {... RULE_REGULAR_COMMENT ...}

Example block:

    doc "Sensor configured..."

Fix:

    doc /* Sensor configured... */

Transformation rule:

    doc "TEXT"  ->  doc /* TEXT */

If `locale` already exists, preserve it:

    doc locale "en" "TEXT"
    ->
    doc locale "en" /* TEXT */

Do NOT invent a locale if it does not exist.

---

## Case B — Using `//` comments

Invalid:

    doc // Sensor configured

Fix:

    doc /* Sensor configured */

---

## Case C — Incorrect `locale` ordering

Invalid:

    doc /* text */ locale "en"

Fix:

    doc locale "en" /* text */

`locale` must appear BEFORE the comment block.

---

## Case D — Missing comment in textual representation

Invalid:

    language "en" "text"

Fix:

    language "en" /* text */

---

## Case E — `doc` used as an attribute name

Messages: `no viable alternative at input 'attribute doc'`, then `mismatched input '=' expecting {'locale', RULE_REGULAR_COMMENT}`
and `extraneous input ':' expecting {'locale', ...}` on the same line. `doc` is a keyword, so the three errors
come from one statement.

Invalid:

    attribute doc : String = "The radio shall support group calls.";

Fix (one edit removes all three errors):

    doc /* The radio shall support group calls. */

---

# 5) Minimal Change Policy

The fixer MUST:

1. Modify only the local fragment around the error.
2. Preserve the original text content.
3. Avoid renaming identifiers.
4. Avoid structural model changes.
5. Only transform syntax into a valid grammar form.

If the text contains `*/`, replace it with `* /` inside the comment to avoid prematurely closing it.

---

# 6) Final Validation Checklist

Before returning the fix, verify:

- The statement ends with `/* ... */` where required.
- `locale "..."` appears before the comment block.
- No `//` comments are used as replacements.
- The original text content is preserved.
- Identifiers are unchanged unless absolutely necessary.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
