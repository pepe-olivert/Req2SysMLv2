# LITERALS_STRINGS.md
Repair guide for **string literals, integer/real literals, names, and quote-sensitive tokens** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when errors involve:

- double-quoted strings
- single-quoted unrestricted names
- integer or real literal formatting
- a quoted token where the grammar expects a name
- a name where the grammar expects a string literal

Typical ANTLR signs:

- offending token starts with `"` or `'`
- parser expects `RULE_STRING_VALUE`
- parser expects `RULE_ID` or `RULE_UNRESTRICTED_NAME`
- parser expects `RULE_DECIMAL_VALUE`

---

# 1) Core Grammar Facts

## 1.1 Names

    ruleName:
        RULE_ID
      | RULE_UNRESTRICTED_NAME
    ;

`RULE_ID` examples:

    Sensor
    MeasureCO2
    pkg_1

`RULE_UNRESTRICTED_NAME` examples:

    'CO2 Sensor'
    'Port A'

Repair implication:
- Use single quotes only for names, not for string literals.

---

## 1.2 Strings

    ruleLiteralString: RULE_STRING_VALUE;

    RULE_STRING_VALUE:
        "..."

Repair implication:
- Text values are double-quoted string literals. They appear, for example, in:

    attribute text : String = "The radio shall ...";
    locale "en"
    language "en"

- Single quotes '...' are NOT text: they delimit a NAME (RULE_UNRESTRICTED_NAME).
  `attribute text : String = 'The radio shall';` parses, but the value is then a reference to an element
  named `The radio shall`, not a text. Never put text values in single quotes.

---

## 1.3 Integers and reals

    ruleLiteralInteger: RULE_DECIMAL_VALUE;

    ruleRealValue:
        RULE_DECIMAL_VALUE? '.' (RULE_DECIMAL_VALUE | RULE_EXP_VALUE)
      | RULE_EXP_VALUE
    ;

Valid integer examples:

    0
    1
    42

Valid real examples:

    0.5
    .5
    1.0
    1e3
    2E-4

Repair implication:
- Keep numeric literals in plain decimal/exponent grammar form.
- Do not add type suffixes like `f`, `d`, `L`.

---

## 1.4 Booleans and infinity

    true
    false
    *

Repair implication:
- `*` is the infinity literal in multiplicity contexts.
- Do not quote it.

---

# 2) Canonical Repair Patterns

## Case A — string used where an element name is required

Invalid:

    part "Sensor" : SensorDef;

Fix policy:
- Convert the double-quoted token into a valid name.
- If the content includes spaces/symbols, prefer `RULE_UNRESTRICTED_NAME` with single quotes.

Preferred repairs:

    part 'Sensor' : SensorDef;

or, if simple:

    part Sensor : SensorDef;

Choose the smaller valid edit that preserves the original text best.

---

## Case B — single-quoted name used where a string is required

Invalid:

    locale 'en'

Fix:

    locale "en"

Typical string-required contexts:
- `locale "..."`
- `language "..."`

---

## Case C — malformed numeric literal

Invalid examples:

    1.
    1.2.3
    1e

Fix policy:
- Normalize to a nearest valid plain numeric form without changing meaning more than necessary.

Preferred repairs:

    1.   -> 1.0
    1e   -> 1e0

If the intended value is unclear, prefer the smallest syntactic correction.

---

## Case D — quoted infinity in multiplicity

Wrong (the parser reads "*" as a name, not as the unbounded upper limit):

    [1.."*"]

Fix:

    [1..*]

---

## Case E — text written where a type is required

Invalid (a string in the type position of an attribute):

    attribute statement : "The radio shall support group calls.";
    attribute id : "ORF-038";

Fix: add the type and turn the text into the value, keeping the double quotes:

    attribute statement : String = "The radio shall support group calls.";
    attribute id : String = "ORF-038";

---

# 3) Minimal Change Policy

The fixer MUST:

1. Preserve literal content whenever possible.
2. Switch quote style only when the grammar requires it.
3. Preserve spacing and nearby structure unless that also causes syntax errors.
4. Avoid renaming identifiers beyond quote normalization.
5. Keep numeric edits minimal and syntactic.

---

# 4) Final Checklist

Before returning the fix, verify:

- Names use `RULE_ID` or single-quoted `RULE_UNRESTRICTED_NAME`.
- Strings use double quotes.
- Integers and reals match the grammar.
- `*` is unquoted in multiplicity/infinity contexts.
- The local construct still matches its surrounding grammar rule.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
