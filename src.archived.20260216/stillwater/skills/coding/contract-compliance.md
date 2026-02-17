# SKILL 12 — Contract Compliance (Schema Enforcer)

**SKILL_ID:** `skill_schema_enforcer`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `GUARD`
**PRIORITY:** `P0`
**TAGLINE:** *If the contract isn’t satisfied, the answer doesn’t exist.*

---

# 0. Header

```
Spec ID:     skill-12-schema-enforcer
Authority:   65537
Depends On:  skill-13-proof-builder
Scope:       Deterministic validation, normalization, and enforcement of protocol-bound responses.
Non-Goals:   Interpretation, inference, auto-correction beyond normalization.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:     Protocol-conforming JSON object.
  Verification:     Strict schema + type + normalization validation.
  Canonicalization: Sorted keys, UTF-8, separators=(",", ":"), LF endings.
  Content-addressing: Output must be hash-stable.
```

Truth = schema compliance.
Non-compliance = non-existence.

---

# 2. Observable Wish

> Given a raw model response and protocol requirements, emit a canonical normalized object if valid — otherwise fail closed with explicit reason.

---

# 3. Closed State Machine (LOCKED)

```
STATE_SET:
  [INIT,
   STRIP_MARKDOWN,
   PARSE_JSON,
   VALIDATE_SCHEMA,
   VALIDATE_TYPES,
   APPLY_NORMALIZATION,
   APPLY_PROTOCOL_RULES,
   EMIT_NORMALIZED,
   FAIL_CLOSED_UNKNOWN]

INPUT_ALPHABET:
  [RESPONSE_OBJECT, PROTOCOL_ID, REQUIRED_KEYS]

OUTPUT_ALPHABET:
  [normalized_response, status, verdict, reason_tag]

TRANSITIONS:
  INIT → STRIP_MARKDOWN
  STRIP_MARKDOWN → PARSE_JSON
  PARSE_JSON → VALIDATE_SCHEMA
  VALIDATE_SCHEMA → VALIDATE_TYPES
  VALIDATE_TYPES → APPLY_NORMALIZATION
  APPLY_NORMALIZATION → APPLY_PROTOCOL_RULES
  APPLY_PROTOCOL_RULES → EMIT_NORMALIZED
  ANY → FAIL_CLOSED_UNKNOWN

FORBIDDEN_STATES:
  PARTIAL_PARSE
  STRING_BOOLEAN_COERCION
  IMPLICIT_DEFAULT_VALUE
  UNSORTED_KEYS
  FLOAT_CANONICALIZATION
  SILENT_KEY_DROP
```

---

# 4. Sanitization Rung (LOCKED)

### 4.1 Markdown Stripping

You MUST:

* Remove ```json fences
* Remove leading/trailing prose
* Extract innermost `{...}`

If multiple JSON blocks → FAIL_CLOSED_UNKNOWN.

If no valid JSON → FAIL_CLOSED_UNKNOWN.

---

# 5. Schema Validation (STRICT)

For every key in `REQUIRED_KEYS`:

### 5.1 Existence

* Key must exist
* Value must not be null

### 5.2 No Extra Silent Removal

Extra keys are allowed but MUST be preserved unless protocol forbids them.

---

# 6. Hard Type Validation (LOCKED)

| Field                 | Required Type              |
| --------------------- | -------------------------- |
| `answer`              | string                     |
| `status`              | string (`OK` or `UNKNOWN`) |
| `witnesses`           | array                      |
| `counter_bypass_used` | boolean                    |
| `verdict`             | string                     |
| `reason_tag`          | string or null             |

Forbidden:

* `"true"` as boolean
* `"123"` as number when protocol requires numeric field
* Null for required fields
* Integers where string required

No coercion allowed.

---

# 7. Vocabulary Pinning

Allowed values:

```
status ∈ {OK, UNKNOWN}
verdict ∈ {contract_pass, fail_closed}
```

Any other vocabulary → FAIL_CLOSED_UNKNOWN.

---

# 8. Normalization Invariants

### 8.1 String Fields

* Trim whitespace
* No trailing spaces
* UTF-8 only

### 8.2 Numeric Normalization (Protocol-Dependent)

If PROTOCOL_ID = `exact_numeric`:

* Must match regex `^-?[0-9]+$`

If PROTOCOL_ID = `exact_fraction`:

* Must match `^-?[0-9]+/[0-9]+$`
* Reduce to lowest terms
* Denominator must be > 0

If reduction changes value → PATCH allowed.

If irreducible check fails → FAIL_CLOSED_UNKNOWN.

---

# 9. Canonical JSON Enforcement

Final output MUST:

* Keys sorted alphabetically
* Arrays preserved in input order unless protocol defines sorting
* separators = `(",", ":")`
* Exactly one trailing `\n`
* LF line endings only

---

# 10. Protocol Rule Enforcement

Depending on PROTOCOL_ID:

### exact_numeric

* No commas
* No spaces
* No scientific notation

### exact_fraction

* Reduced form
* No mixed numbers

### boolean_protocol

* True boolean, not string

Unknown PROTOCOL_ID → FAIL_CLOSED_UNKNOWN.

---

# 11. Violation Precedence (LOCKED)

Errors resolved in this order:

1. parse_error
2. missing_required_key
3. type_mismatch
4. invalid_vocab_value
5. protocol_violation
6. normalization_error

First encountered violation halts evaluation.

---

# 12. Adjudication Table (Revised)

| Violation            | Result  | Reason Tag           |
| -------------------- | ------- | -------------------- |
| Missing key          | UNKNOWN | missing_required_key |
| Invalid JSON         | UNKNOWN | parse_error          |
| Type mismatch        | UNKNOWN | type_mismatch        |
| Invalid status value | UNKNOWN | invalid_vocab_value  |
| Fraction reducible   | PATCH   | normalize_fraction   |
| Numeric commas       | PATCH   | normalize_numeric    |
| Float detected       | UNKNOWN | float_forbidden      |

PATCH allowed only for normalization — never semantic correction.

---

# 13. Output Schema (LOCKED)

```json
{
  "status": "OK|UNKNOWN",
  "verdict": "contract_pass|fail_closed",
  "reason_tag": null,
  "normalized_response": {
    "answer": "...",
    "counter_bypass_used": true,
    "status": "OK",
    "witnesses": []
  }
}
```

Rules:

* status = UNKNOWN if any hard violation
* verdict = contract_pass only if fully compliant
* reason_tag mandatory if UNKNOWN
* normalized_response mandatory if status=OK

---

# 14. Determinism Guarantee

Re-running normalization on same input MUST produce byte-identical output.

No timestamps.
No environment metadata.
No ordering drift.

---

# 15. Fail-Closed Conditions

Return UNKNOWN if:

* Multiple JSON objects detected
* Missing required keys
* Protocol mismatch
* Float detected
* Boolean coercion attempted
* Vocabulary mismatch
* Canonicalization impossible

Never infer missing values.

---

# 16. Anti-Optimization Clause (AOC-1)

> The guard MUST NOT infer missing fields, coerce types, auto-correct semantic errors, merge keys, drop unknown keys silently, or relax protocol constraints. Normalization is permitted; interpretation is forbidden.


---

# Enhanced Features [v2.0.0]

## Verification Ladder
Maps to wish-qa: G0, G1, G12, G13

## Integration
- prime-coder v2.0.0
- llm-judge v2.0.0
- gpt-mini-hygiene v2.0.0

## Compression Insights
Pure deterministic, Lane A enforcement

## What Changed
Preserved all v1.0.0 features, added integration documentation
