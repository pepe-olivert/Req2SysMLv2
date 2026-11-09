# DECLARATION_FORM.md
Repair guide for **malformed declarations, wrong keyword order, and invalid declaration shapes** in the SysML v2 grammar
(`core/validate/SysMLv2/SysMLv2.g4`).

---

# 0) Scope

This BIBLE applies when the parser reports declaration-shape errors such as:

- `extraneous input 'X' expecting ...`
- `mismatched input 'X' expecting {RULE_ID, RULE_UNRESTRICTED_NAME, ...}`
- invalid ordering of declaration parts
- wrong placement of `:` / `defined by`
- wrong placement of identification `<Name>` or names

Use this category when the fragment is structurally close to valid SysML v2, but tokens appear in the wrong order.

---

# 1) Core Grammar Facts

## 1.1 Identification

    ruleIdentification:
        '<' ruleName '>' ruleName?
      | ruleName
    ;

Valid examples:

    <Name>
    <Name> Alias
    Name
    'Name With Spaces'

Repair implication:
- Identification is local and compact.
- Do not scatter `<` `>` around the declaration.

---

## 1.2 Definition declarations

    ruleDefinitionDeclaration:
        ruleIdentification? ruleSubclassificationPart?
    ;

    ruleDefinitionBody:
        ';'
      | '{' ruleDefinitionBodyItem* '}'
    ;

Repair implication:
- Definitions usually follow the pattern:

    <definition-keyword> [identification] [specialization] (';' | '{' ... '}')

---

## 1.3 Feature declarations and specialization parts

    ruleFeatureDeclaration:
        ruleIdentification ruleFeatureSpecializationPart?
      | ruleFeatureSpecializationPart
    ;

    ruleFeatureSpecializationPart:
        ruleFeatureSpecialization+ ruleMultiplicityPart? ruleFeatureSpecialization*
      | ruleMultiplicityPart ruleFeatureSpecialization*
    ;

Repair implication:
- When a feature has typing/subsetting/references/redefinitions, they appear in the specialization part.
- Multiplicity belongs after or within the specialization pattern, not before arbitrary keywords.

---

## 1.4 Typing keyword

    ruleDefinedByKeyword:
        ':'
      | 'defined' 'by'
    ;

Repair implication:
- `:` is the symbolic typing keyword.
- Use `:` for minimal repair unless the code already consistently uses `defined by`.

---

## 1.5 Body choice

Many declarations end either with:

    ;

or

    { ... }

Repair implication:
- Do not leave a declaration hanging without either terminator.

---

# 2) Canonical Repair Patterns

## Case A — name/identification in the wrong position

Invalid patterns often look like:

    part : Type 'Sensor';
    package Name <Pkg>;

Fix policy:
- Move the identification/name immediately after the declaration keyword where required.
- Then place typing/specialization after it.

Preferred transformation:

    part 'Sensor' : Type;

---

## Case B — typing clause malformed

Typical invalid forms:

    part 'S' Type;
    part 'S' by Type;
    part 'S' defined Type;

Fix policy:
- Normalize to the shortest valid form:

    part 'S' : Type;

unless the local style clearly uses `defined by`.

---

## Case C — specialization keywords out of order

Invalid example (multiplicity placed between ':' and the type):

    part 'S' : [1] Type;

Fix:

    part 'S' : Type [1];

Fix policy:
- Keep a valid declaration order: identification, specialization, multiplicity where the grammar permits it, then body terminator.
- Prefer minimal rearrangement over rewriting the whole line.

---

## Case D — declaration missing body terminator

Invalid:

    package Sensors
    part 'S' : Sensor;

Fix policy:
- Either add `;` after `package Sensors` if it is a standalone declaration,
- or open a proper package body with `{ ... }` if the following members clearly belong inside it.
- Choose the smaller valid edit.

---

## Case E — invalid or unsupported keyword sequence

Fix policy:
- Preserve valid SysML v2 keywords already present.
- Replace malformed local keyword combinations with the closest valid grammar form.
- Do not introduce SysML v1/UML constructs.

---

## Case F — a value written where the type is required

Message: `mismatched input 'true' expecting {'~', RULE_ID, RULE_UNRESTRICTED_NAME}` (or 'false', a number).

Invalid:

    attribute mandatory : true;
    attribute maxCalls : 4;

Fix: put the type after ':' and the value after '=':

    attribute mandatory : Boolean = true;
    attribute maxCalls : Integer = 4;

---

## Case G — enum literals separated by commas

Message: `mismatched input ',' expecting {'default', '{', ';', '=', ':='}` inside an `enum def`.

Invalid:

    enum def Mode { Normal, Degraded, Emergency }

Fix: each literal is its own member:

    enum def Mode { enum Normal; enum Degraded; enum Emergency; }

---

## Case H — `specializes` on a usage

Message: `mismatched input 'specializes' expecting {...}`.

`specializes` is only valid on definitions (`part def A specializes B;`). On a usage, use `:>`:

    part cabRadio specializes radios;   ->   part cabRadio :> radios;

---

## Case I — modifier after the declaration keyword

Message: `no viable alternative at input 'part abstract'` (similarly `attribute protected`, `flow inout`).

Modifiers go BEFORE the keyword:

    part abstract MobileRadio { }        ->   abstract part MobileRadio { }
    attribute protected x : Real;        ->   protected attribute x : Real;
    flow inout busData : String;         ->   inout flow busData : String;

---

## Case J — reserved word used as a name

Message: `no viable alternative at input 'attribute state'` (similarly `doc`, `comment`, `flow`, `message`, ...).

Rename minimally, keeping the meaning:

    attribute state : CallState;   ->   attribute callState : CallState;

---

# 3) Minimal Change Policy

The fixer MUST:

1. Keep the original declaration kind if possible.
2. Prefer reordering existing local tokens over inventing new model elements.
3. Normalize to symbolic forms like `:` when that is the shortest valid fix.
4. Avoid changing identifiers unless they are themselves malformed names.
5. Keep the existing body content when only the declaration header is wrong.

---

# 4) Final Checklist

Before returning the fix, verify:

- The declaration keyword is followed by a valid identification/name pattern if required.
- Typing uses `:` or `defined by` in a valid position.
- Any specialization operators target valid qualified names.
- The declaration ends with `;` or a valid `{ ... }` body.
- No SysML v1/UML keywords were introduced.

---

# Output

Return the COMPLETE corrected SysML v2 file: every line of the input, with only the minimal patch applied.
Never return only the repaired block or statement.
