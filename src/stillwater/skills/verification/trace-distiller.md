# SKILL 14 — Trace Distiller (Traces → Templates)

**SKILL_ID:** `skill_trace_distiller`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `LEARNING`
**PRIORITY:** `P0`
**TAGLINE:** *Distill only what passed—and never erase the witness.*

---

# 0. Header

```
Spec ID:     skill-14-trace-distiller
Authority:   65537
Depends On:  skill-13-proof-builder, wish-method v1.4 §12 (Self-Learning)
Scope:       Deterministically distill verified traces into reusable, answer-blind templates.
Non-Goals:   Model weight updates, prompt injection memory, modifying historical proofs.
```

---

# 1. Prime Truth Thesis (REQUIRED)

```
PRIME_TRUTH:
  Ground truth:    Only tasks with status=PASS and canonical PROOF.json.
  Verification:    Replay template on original traces → identical task hashes.
  Canonicalization: Distilled artifacts follow canonical JSON rules.
  Content-addressing: distill_id = SHA-256(canonical output bundle).
```

Learning is valid only if it preserves regeneration truth (RTC).

---

# 2. Observable Wish

> Given verified PASS traces within a task family, emit deterministic, answer-blind Prime Mermaid templates and compact skill shims that generalize structure without leaking task-specific data.

---

# 3. State Space (LOCKED)

```
STATE_SET:
  [INIT, FILTER_VERIFIED, CLUSTER_PATTERNS, ABSTRACT_TEMPLATE,
   STRIP_LITERALS, VALIDATE_GENERALIZATION,
   REGRESSION_CHECK, EMIT_BUNDLE, UNKNOWN]

INPUT_ALPHABET:
  [VERIFIED_TRACES, FAMILY_TARGET, COMPACTION_LIMIT]

OUTPUT_ALPHABET:
  [RECIPE_TEMPLATES, SKILL_SHIMS]

TRANSITIONS:
  INIT → FILTER_VERIFIED
  FILTER_VERIFIED → CLUSTER_PATTERNS
  CLUSTER_PATTERNS → ABSTRACT_TEMPLATE
  ABSTRACT_TEMPLATE → STRIP_LITERALS
  STRIP_LITERALS → VALIDATE_GENERALIZATION
  VALIDATE_GENERALIZATION → REGRESSION_CHECK
  REGRESSION_CHECK → EMIT_BUNDLE
  ANY → UNKNOWN

FORBIDDEN_STATES:
  ANSWER_LEAKAGE
  WITNESS_ERASURE
  SINGLE_TASK_OVERFIT
  FLOAT_GENERALIZATION_DRIFT
  COUNTER_BYPASS_REMOVAL
  HALLUCINATED_PATTERN
  NONDETERMINISTIC_CLUSTERING
```

---

# 4. Eligibility Filter (STRICT)

Only traces satisfying ALL:

* `status == PASS`
* `repo.dirty == false`
* Valid Merkle-root proof
* Matching `FAMILY_TARGET`

Else → UNKNOWN.

No partially successful traces permitted.

---

# 5. Answer-Blind Abstraction (LOCKED)

You MUST replace:

* Exact numeric results → `{{N}}`
* Concrete strings → `{{STR}}`
* Specific entity names → `{{ENTITY}}`
* File paths → `{{PATH}}`

Forbidden:

* Hard-coded constants from traces
* Embedding example-specific theorem names
* Including final numeric outputs

If literal survives → UNKNOWN.

---

# 6. Counter Bypass Preservation (MANDATORY)

If any trace in the family used COUNTER_BYPASS:

* Template MUST retain explicit L2 CPU node
* Shim MUST preserve rule:

  * "LLM_ROLE: classify only"
  * "CPU_ROLE: enumerate"
* Removal of bypass → REJECT

No numeric estimation permitted in distilled template.

---

# 7. Witness Preservation Invariant

Templates MUST:

* Preserve witness requirement
* Preserve proof hash generation
* Preserve replay determinism

A distilled template cannot weaken witness policy.

Violation → UNKNOWN.

---

# 8. Family-Level Locking (GENERALIZATION RULE)

A rule may be abstracted only if:

* It appears in ≥ 2 distinct task_ids in the same family
* It is structurally identical (not result-identical)

Single-task behavior = noise → discard.

Clustering must be deterministic:

* Sort traces by task_id ASCII ascending before analysis.
* No probabilistic clustering allowed.

---

# 9. Shannon Compaction Rule (Shim Discipline)

```
COMPACTION_LIMIT default: 500 chars
```

Constraints:

* Checklist style
* Declarative rules only
* No examples
* No narrative prose
* Must/Must Not structure

If logic exceeds limit:

* Retain verification rule only
* Drop explanatory text

---

# 10. Regression Gate (STRICT)

Before emission:

* Re-run template on original traces
* Recompute task hashes
* Confirm identical hashes to source proof

If any mismatch → UNKNOWN.

Additionally:

* UNKNOWN rate on adversarial traps must not decrease.
* Template must not reduce strictness.

---

# 11. Deterministic Canonicalization

Output bundle must follow:

* Canonical JSON sorting
* UTF-8
* No indentation
* One trailing newline
* Sorted arrays by id

Compute:

```
distill_id = SHA-256(canonical_output_bundle)
```

---

# 12. Output Schema (LOCKED)

```json
{
  "distill_version": "1.0.0",
  "distill_id": "<64hex>",
  "family": "<family_id>",
  "source_task_ids": ["..."],
  "templates": [
    {
      "id": "tmpl-...",
      "mermaid_graph": "...",
      "witness_policy": "...",
      "counter_policy": "..."
    }
  ],
  "shims": [
    {
      "id": "shim-...",
      "content": "Must enforce CPU enumeration before verdict."
    }
  ]
}
```

Rules:

* source_task_ids sorted
* templates sorted by id
* shims sorted by id

---

# 13. Verification Ladder

### 641 — Sanity

* [ ] All literals abstracted
* [ ] Mermaid valid DAG
* [ ] No task-specific constants remain

### 274177 — Determinism

* [ ] Re-canonicalization stable
* [ ] Regression hashes identical
* [ ] Counter bypass preserved

### 65537 — Final Seal

* [ ] No witness weakening
* [ ] No reduction in adversarial UNKNOWN rate
* [ ] distill_id verified

---

# 14. Ambiguity Handling

Return UNKNOWN if:

* Cluster ambiguity exists
* Generalization conflicts between traces
* Witness mapping cannot be preserved
* Template weakens determinism
* Literal abstraction incomplete

Never emit partial distillation.

---

# 15. Anti-Optimization Clause (LOCKED — AOC-1)

> Coders MUST NOT compress this spec, merge invariants, infer intent, or remove redundancy. Learning must be externalized and testable. Redundancy is anti-compression armor.


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
