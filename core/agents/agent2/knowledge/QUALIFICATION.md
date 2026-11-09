# QUALIFICATION.md
Repair guide for **qualified names, namespace paths, and reference/subsetting operators** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when errors involve:

- `::`
- `::>`
- `:>`
- `:>>`
- qualified names such as `Pkg::Type`
- imports such as `Pkg::*` or `Pkg::**`
- subsetting, references, and redefinitions using symbolic keywords

Typical signs:

- the offending token is `::`, `::>`, `:>`, `:>>` or `:`
- `mismatched input ':' ...`
- `no viable alternative at input 'A::B...'`
- parser expects `RULE_ID` / `RULE_UNRESTRICTED_NAME` near a scope operator

---

# 1) Core Grammar Facts

## 1.1 Qualified names

    ruleQualification: (ruleName '::')+;
    ruleQualifiedName: ruleQualification? ruleName;

This means a qualified name is:

    Name
    Name::Name
    Name::Name::Name

where each segment is a `ruleName`, and `ruleName` is:

    RULE_ID
    or
    RULE_UNRESTRICTED_NAME

Valid examples:

    Sensor
    EnvPkg::Sensor
    'My Package'::'CO2 Sensor'

Invalid examples:

    ::Sensor
    Sensor::
    Sensor::::Type

---

## 1.2 References keyword

    ruleReferencesKeyword:
        '::>'
      | 'references'
    ;

Repair implication:
- `::>` is not a general separator.
- It is the symbolic form of the `references` keyword in feature specialization contexts.

---

## 1.3 Subsets and specializes

    ruleSubsetsKeyword:
        ':>'
      | 'subsets'
    ;

    ruleSpecializesKeyword:
        ':>'
      | 'specializes'
    ;

Repair implication:
- `:>` is used in specialization/subsetting contexts, not as a namespace separator.
- Do not replace `::` with `:>` unless the grammar context is a specialization/subsetting clause.
- The keyword `specializes` is only valid on definitions: `part def Radio specializes Device;`.
  On usages use the symbol or `subsets`: `part cabRadio :> radios;` (never `part cabRadio specializes radios;`).

---

## 1.4 Redefines keyword

    ruleRedefinesKeyword:
        ':>>'
      | 'redefines'
    ;

Repair implication:
- `:>>` is only valid where redefinition is allowed.
- Do not confuse `:>>` with `::>`.

---

## 1.5 Imports

Relevant grammar:

    ruleImportedMembership: ruleQualifiedName ('::' '**')?;
    ruleImportedNamespace: ruleQualifiedName '::' '*' ('::' '**')?;

Valid examples:

    import Pkg::*;
    import all Pkg::SubPkg::*;
    import Pkg::Member;
    import Pkg::*::**;

Repair implication:
- `*` and `**` only appear in import/filter contexts.
- Do not introduce wildcard tails in normal qualified names.

---

# 2) Canonical Repair Patterns

## Case A — broken qualified name

Typical invalid forms:

    ::Type
    Pkg::
    Pkg::::Type

Fix policy:
- Remove leading or repeated separators.
- Ensure the path ends in a valid `ruleName`.

Preferred transformations:

    ::Type          -> Type
    Pkg::           -> Pkg
    Pkg::::Type     -> Pkg::Type

---

## Case B — `::>` used where `::` is required

Typical symptom:
- path-like expression uses `::>` between package/type segments.

Fix policy:
- If the intent is clearly a qualified name, replace `::>` with `::`.
- Keep `::>` only when the grammar context is a references specialization.

Example:

    Pkg::>Type
    ->
    Pkg::Type

---

## Case C — `:>` or `:>>` used as namespace separators

Wrong as qualified names (the parser may accept them as a typing followed by a subsets/redefines clause,
but they do not denote `Pkg::Type`):

    Pkg:>Type
    Pkg:>>Type

Fix policy:
- If the construct is a qualified name, replace with `::`.
- Keep `:>` only for specializes/subsets clauses.
- Keep `:>>` only for redefines clauses.

---

## Case D — malformed reference/subsetting/redefinition clause

Valid symbolic patterns in specialization contexts:

    : Type
    :> SuperType
    ::> ReferencedFeature
    :>> RedefinedFeature

Fix policy:
- Preserve the operator if the surrounding context is a feature specialization.
- Only normalize the target to a valid `ruleQualifiedName`.

---

# 3) Minimal Change Policy

The fixer MUST:

1. Preserve the intended operator semantics whenever possible.
2. Change only the operator or local target name if the surrounding declaration is otherwise valid.
3. Not invent new package segments.
4. Not rewrite imports into non-import declarations.
5. Not replace a valid keyword form (`references`, `redefines`, `specializes`) unless the symbolic form is already being used locally and a purely symbolic repair is smaller.

---

# 4) Final Checklist

Before returning the fix, verify:

- Every qualified name matches `(ruleName '::')* ruleName`.
- `::>` appears only in a references context.
- `:>` appears only in specializes/subsets contexts.
- `:>>` appears only in redefines contexts.
- Wildcards `*` and `**` are used only in import/filter contexts.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
