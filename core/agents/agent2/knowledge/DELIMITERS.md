# DELIMITERS.md
Repair guide for **missing or extra delimiters and body terminators** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when validator errors indicate missing, extra, or misplaced:

- `;`
- `{` `}`
- `(` `)`
- `[` `]`
- `,`
- `.` in qualified/chain contexts

Typical ANTLR messages include:

- `missing ';' at ...`
- `missing '}' at ...`
- `extraneous input 'X' expecting ';'`
- `extraneous input 'X' expecting '}'`
- `mismatched input 'X' expecting ')'`

The goal is to restore a **syntactically valid local structure** with the smallest possible edit.

---

# 1) Core Grammar Facts

## 1.1 Relationship and definition bodies

Many declarations and relationships terminate in one of two ways:

    ';'

or

    '{' ... '}'

Examples from the grammar:

    ruleRelationshipBody:
        ';'
      | '{' ruleOwnedAnnotation* '}'
    ;

    ruleDefinitionBody:
        ';'
      | '{' ruleDefinitionBodyItem* '}'
    ;

    rulePackageBody:
        ';'
      | '{' (rulePackageMember | ruleElementFilterMember | ruleAliasMember | ruleImport)* '}'
    ;

Repair implication:
- If a declaration opens a body with `{`, it must close with `}`.
- If it does not open a body, it usually must end with `;`.

---

## 1.2 Multiplicity uses square brackets

    ruleMultiplicityRange:
        '[' ruleMultiplicityExpressionMember ('..' ruleMultiplicityExpressionMember)? ']'
    ;

Valid examples:

    [1]
    [0..1]
    [1..*]

Repair implication:
- Missing `]` is usually a local multiplicity issue.
- Do not replace `[` `]` with parentheses.

---

## 1.3 Argument lists use parentheses

    ruleArgumentList:
        '(' (rulePositionalArgumentList | ruleNamedArgumentList)? ')'
    ;

Repair implication:
- If a call-like expression starts with `(`, it must close with `)`.
- Named arguments use commas between members.

---

## 1.4 Commas separate repeated items

Many grammar rules use comma-separated lists, for example:

    ruleDependency: ... ruleQualifiedName (',' ruleQualifiedName)* 'to' ruleQualifiedName (',' ruleQualifiedName)* ...

    ruleNamedArgumentList: ruleNamedArgumentMember (',' ruleNamedArgumentMember)*

Repair implication:
- If ANTLR expects `,`, insert it only between sibling list items.
- Do not add trailing commas unless the grammar explicitly allows them.

---

# 2) Canonical Repair Patterns

## Case A — missing semicolon

Typical error:

    missing ';' at '...'

Fix policy:
- Add `;` at the end of the current statement if the construct is not opening a `{ ... }` body.
- Prefer inserting `;` before the next sibling declaration keyword.

Examples:

    package Sensors
    ->
    package Sensors;

    part 'Sensor' : SensorDef
    ->
    part 'Sensor' : SensorDef;

---

## Case B — missing right brace

Typical error:

    missing '}' at '...'

Fix policy:
- Close the nearest unmatched `{`.
- Do not delete valid inner content to silence the error.

Example:

    package Sensors {
        part 'S' : Sensor;
    ->
    package Sensors {
        part 'S' : Sensor;
    }

---

## Case C — extraneous token before semicolon or brace

Typical error:

    extraneous input 'X' expecting ';'

Fix policy:
- First check whether `X` belongs to the next statement.
- If yes, insert `;` before `X`.
- Only delete `X` if it is clearly duplicated noise.

Preferred transformation:

    part 'A' : T part 'B' : U;
    ->
    part 'A' : T;
    part 'B' : U;

---

## Case D — multiplicity bracket not closed

Typical error:

    missing ']' at '...'

Fix policy:
- Complete the multiplicity range locally.

Examples:

    [1..*
    ->
    [1..*]

    [0..1
    ->
    [0..1]

---

## Case E — missing comma in a list

Typical error:

    mismatched input 'B' expecting ','

Fix policy:
- Insert `,` only if the surrounding rule is a repeated list.
- Common contexts: dependency source/target lists, named arguments, annotation lists.

---

# 3) Minimal Change Policy

The fixer MUST:

1. Prefer insertion over deletion for delimiter errors.
2. Close the nearest open structure rather than rewriting the whole declaration.
3. Preserve identifiers, names, and ordering of valid elements.
4. Avoid converting a body form into a semicolon form unless the body is empty and clearly unintended.
5. Never introduce SysML v1/UML syntax.

---

# 4) Final Checklist

Before returning the fix, verify:

- Every opened `{` has a matching `}`.
- Every opened `(` has a matching `)`.
- Every opened `[` has a matching `]`.
- Statements that require termination end in `;` or a valid `{ ... }` body.
- Commas appear only between repeated sibling items.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
