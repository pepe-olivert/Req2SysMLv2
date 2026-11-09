# CONSTRAINT_EXPR.md
Repair guide for **constraint and assert expressions** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This guide applies when a logical or arithmetic expression is written where the grammar expects a declaration.

Typical messages:

- `mismatched input '==' expecting {'redefines', 'ordered', 'nonunique', 'defined', 'subsets', ...}`
  (also with `!=`, `<=`, `>=`, `<`, `>`, `and`, `or`, `implies`, `true`, `false`)
- `extraneous input ';' expecting '}'` right after an expression
- `no viable alternative at input 'assert true'` / `'assert ('`
- `mismatched input '::' expecting '>'` on a line such as `assert A::x < B::y`

---

# 1) Core Grammar Facts

## 1.1 An expression is never a statement on its own

`assert` must be followed by a constraint (or a reference to one), not by an expression:

    ruleAssertConstraintUsage: ruleOccurrenceUsagePrefix 'assert' 'not'?
        ( ruleOwnedReferenceSubsetting ruleFeatureSpecializationPart?
        | ruleConstraintUsageKeyword ruleConstraintUsageDeclaration ) ruleCalculationBody;

So in `assert Radio::settingsRetained == true;` the parser reads `assert Radio::settingsRetained` as a
reference and fails at `==`. Removing `== true` silences the error but changes the meaning: do not do that.

## 1.2 Where an expression may appear

An expression is the body of a constraint, written between braces and WITHOUT a trailing `;`:

    constraint C_Name { <expression> }              (constraint usage, e.g. in a package)
    assert constraint C_Name { <expression> }       (inside a part or requirement; the name is optional)
    require constraint { <expression> }             (inside a requirement)

## 1.3 Operators

- Equality is `==` (also `!=`, `===`, `!==`). A single `=` is binding/assignment, not comparison.
- Comparison: `<`, `<=`, `>`, `>=`. Logic: `and`, `or`, `xor`, `not`, `implies`.
- Features may be qualified (`Radio::volume`) or, inside the owning part, simple (`volume`).

---

# 2) Canonical Repair Patterns

## Case A — bare `assert <expression>;`

Invalid:

    constraint C_Settings { assert Radio::settingsRetained == true; }
    part Radio { attribute settingsRetained : Boolean; assert settingsRetained == true; }

Fix (keep the expression, wrap it as a constraint body, drop the `;`):

    constraint C_Settings { Radio::settingsRetained == true }
    part Radio { attribute settingsRetained : Boolean; assert constraint { settingsRetained == true } }

## Case B — compound expression

Invalid:

    assert S::a == true and S::b == true and S::c == true;

Fix:

    constraint C { S::a == true and S::b == true and S::c == true }

## Case C — implication

Invalid:

    assert CabRadio::handsetOffHook == false implies CabRadio::broadcastActive == true;

Fix:

    constraint C { CabRadio::handsetOffHook == false implies CabRadio::broadcastActive == true }

## Case D — comparison misread as type brackets (`expecting '>'`)

Invalid:

    assert S::setup < L::maximum;

Fix:

    constraint C { S::setup < L::maximum }

## Case E — requirement condition

Invalid:

    requirement Q { assert R::v >= 5; }

Fix:

    requirement Q { require constraint { R::v >= 5 } }

## Case F — `;` after the expression inside a constraint body

Message: `extraneous input ';' expecting '}'`.

    constraint C { R::v == 1; }   ->   constraint C { R::v == 1 }

## Case G — `assert true;`, `assert (expr);`, `=` used as equality

    assert true;                    ->   assert constraint { true }
    assert (v == 1);                ->   assert constraint { v == 1 }
    assert constraint { v = 96 }    ->   assert constraint { v == 96 }

---

# 3) Minimal Change Policy

1. Keep every operand, operator and qualified name of the expression; only change the wrapper
   (`assert ... ;` -> `constraint { ... }` / `assert constraint { ... }`) and remove the trailing `;`.
2. Never delete the comparison (`== true`, `>= 5`) to make the line parse.
3. Never turn `==` into `=`.
4. If the same statement produced several errors (the operator and the `;`), one edit of that statement fixes all of them.

---

# 4) Final Checklist

Before returning, verify:

- The expression appears only inside `{ ... }` of a constraint, `assert constraint` or `require constraint`.
- There is no `;` between the expression and the closing `}`.
- Equality uses `==`.
- The meaning of the expression is unchanged.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
