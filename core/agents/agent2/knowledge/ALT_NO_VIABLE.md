# ALT_NO_VIABLE.md
Repair guide for **`no viable alternative` parser failures** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when ANTLR reports:

- `no viable alternative at input '...'`

This usually means the local token sequence does not fit any grammar branch. It is often caused by one of these root causes:

1. malformed declaration order
2. broken qualification/operator sequence
3. missing delimiter that caused the parser to drift
4. wrong quote style for a token category

This category is a **fallback diagnosis category**. Use it to repair the local fragment conservatively by identifying the smallest plausible branch the author intended.

---

# 1) Diagnosis Strategy

When `no viable alternative` appears, inspect in this order:

## 1.1 Delimiter drift

Check whether a missing `;`, `}`, `]`, or `)` just before the offending region would restore a valid parse.

## 1.2 Qualification/operator confusion

Check whether the fragment misuses:

- `::`
- `::>`
- `:>`
- `:>>`
- `:`

## 1.3 Declaration-shape confusion

Check whether tokens are simply in the wrong order, for example:

- name after type instead of before it
- `locale` after comment instead of before it
- body members appearing after a declaration that never opened `{`

## 1.4 Literal/name confusion

Check whether the offending token should be:

- a string instead of a name
- a name instead of a string
- a comment block instead of a string

---

# 2) Conservative Repair Rules

## Rule A — prefer one local normalization over global rewriting

Do not rewrite the whole file. Repair the shortest fragment that can make one grammar branch valid.

## Rule B — prefer insertion of a missing structural token before deleting content

A missing `;` or `}` often explains a whole `no viable alternative` region.

## Rule C — preserve declaration kind

If the fragment starts as `package`, `part`, `port`, `attribute`, `action`, etc., keep that declaration kind and normalize the rest.

## Rule D — choose the nearest valid grammar form already suggested by local tokens

Examples:
- If you see `locale` and a string, aim for a documentation/comment form.
- If you see `A::B`, aim for a qualified-name form.
- If you see `:` followed by a type-like name, aim for a typing form.

---

# 3) Typical Repairs

## Example 1

Invalid:

    doc "text"

Likely intended branch:
- documentation

Repair:

    doc /* text */

## Example 2

Invalid:

    part 'S' Sensor;

Likely intended branch:
- typed feature declaration

Repair:

    part 'S' : Sensor;

## Example 3

Invalid:

    Pkg::>Type

Likely intended branch:
- qualified name

Repair:

    Pkg::Type

---

# 4) Minimal Change Policy

The fixer MUST:

1. Repair only the local root cause.
2. Not introduce speculative model content.
3. Prefer the nearest valid grammar branch supported by the visible tokens.
4. Preserve names and text unless they are syntactically malformed.
5. Fall back to delimiter insertion or local operator normalization before larger rearrangements.

---

# 5) Final Checklist

Before returning the fix, verify:

- The repaired fragment clearly matches one grammar branch.
- The change is local and minimal.
- No unrelated declarations were rewritten.
- The result does not introduce forbidden SysML v1/UML syntax.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
