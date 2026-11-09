# UNKNOWN.md
Fallback repair guide for **uncertain or unclassified syntax errors** in the SysML v2 grammar.

---

# 0) Scope

Use this BIBLE when the router cannot confidently classify the error.

This category is a safe fallback. The goal is to make the **smallest syntactic repair** that is strongly supported by the local code and validator message.

---

# 1) Fallback Repair Strategy

Inspect the local fragment in this order:

1. Delimiters
   - missing `;`, `}`, `)`, `]`, or `,`
2. Documentation/comment syntax
   - `doc`, `comment`, `language`, `locale`, `/* ... */`
3. Declaration form
   - name order, `:` typing, body terminator
4. Qualification and operators
   - `::`, `::>`, `:>`, `:>>`
5. Literals and quote style
   - strings vs names vs numbers
6. Lexer issues
   - illegal characters, unterminated strings, malformed names

---

# 2) Conservative Repair Rules

- Make only local edits near the reported error.
- Prefer inserting a missing structural token before deleting content.
- Preserve declaration kind and existing identifiers whenever possible.
- Normalize obvious grammar forms instead of inventing new model content.
- Do not introduce SysML v1/UML syntax.

---

# 3) Safe Default Transformations

## Default A — likely missing semicolon

If two declarations appear fused, insert `;` between them.

## Default B — likely broken comment/documentation block

If `doc`, `comment`, or `language` is followed by plain text or a string where a comment is expected, wrap the content in `/* ... */`.

## Default C — likely missing typing colon

If a declaration name is directly followed by a type-like qualified name, try inserting `:`.

## Default D — likely broken qualified name

Normalize repeated or malformed scope separators to `::` when the fragment is clearly path-like.

---

# 4) Final Checklist

Before returning the fix, verify:

- The change is minimal and local.
- The repaired fragment matches an obvious SysML v2 grammar pattern.
- No unrelated declarations were modified.
- The output is plain corrected SysML v2 code only.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
