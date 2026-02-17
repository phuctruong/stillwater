# SKILL 39 — GPT-Mini Hygiene Layer

**SKILL_ID:** `skill_gpt_mini_hygiene`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `OPTIMIZER`
**TAGLINE:** *Surface Locking. Parity is Truth.*

---

## 0) Contract

### Inputs
- `OUTPUT_STREAM`: Raw text or logs.

### Outputs
- `HYGIENIC_ARTIFACT`: Normalized, timestamp-free, sorted output.

---

## 1) Execution Protocol (Lane A Axioms)

### A. The Surface Lock
- **Action**: Remove timestamps, elapsed timings, and PIDs from stdout.
- **Goal**: Enable byte-identical `diff` across arms.
- **Determinism**: Same inputs → same outputs (replay invariant).
- **Lane**: A (deterministic normalization).

### B. Stable Serialization
- **Rule**: Always use `sort_keys=True` for JSON/Dockets.
- **Canonical Formatting**: Stable numeric representation (no float drift).
- **Path Normalization**: Repo-relative paths (strip absolute prefixes).
- **Lane**: A (deterministic serialization).

---

## 2) Verification Ladder [ENHANCED v2.0.0]

### Rung 641 — Sanity (Edge Tests)

**Maps to wish-qa gates:**
- **G0 (Structure)**: Output format valid (parseable JSON/text)
- **G1 (Schema)**: Required fields present (normalized structure)
- **G5 (Tool)**: Normalization tools available (strip, sort, canonicalize)

**Edge tests (minimum 5):**
1. ✅ Timestamps stripped from stdout?
2. ✅ PIDs stripped from logs?
3. ✅ JSON keys sorted?
4. ✅ Paths normalized (repo-relative)?
5. ✅ Numeric format canonical (no float drift)?

---

### Rung 274177 — Stress (Consistency Tests)

**Maps to wish-qa gates:**
- **G3 (Consistency)**: Same input → same output (replay stable)
- **G9 (Lineage)**: Behavioral hash matches (no drift)

**Stress tests:**
1. ✅ Same raw output → identical normalized output (100 trials)?
2. ✅ Different timestamp values → same normalized output?
3. ✅ Different PID values → same normalized output?
4. ✅ Unordered JSON → sorted output (deterministic)?
5. ✅ Behavioral hash stable across normalizations?

---

### Rung 65537 — God Approval (Final Seal)

**Maps to wish-qa gates:**
- **G13 (Determinism)**: Normalization is deterministic (Lane A)
- **G12 (Witness)**: Evidence artifacts normalized (replay stable)

**Final tests:**
1. ✅ Normalization is deterministic (Lane A guarantee)?
2. ✅ Evidence artifacts normalized (replay stable)?
3. ✅ No forbidden states entered (drift, nondeterminism)?

---

## 3) Anti-Optimization Clause [NEW v2.0.0]

### Never-Worse Doctrine
**Rule:** ALL v0.2.0 features PRESERVED in v2.0.0.

### Preserved Features from v0.2.0
- **Surface Lock**: Strip timestamps, elapsed timings, PIDs
- **Stable Serialization**: `sort_keys=True` for JSON
- **Goal**: Byte-identical diff across arms

### v2.0.0 Enhancements (Strictly Additive)
- Verification ladder gate mapping (G0, G1, G5, G3, G9, G13, G12)
- Anti-optimization clause with preserved features list
- Gap-guided extension criteria
- Integration with 12 recent skills
- Compression insights (normalization justifications)
- Lane algebra integration (explicit Lane A enforcement)
- Forbidden states (DRIFT, NONDETERMINISM)

---

## 4) Gap-Guided Extension [NEW v2.0.0]

### Purpose
When to add new normalization rules to gpt-mini-hygiene.

### Decision Tree

**Step 1 — Gap Identification:**
- Question: "Is there a non-deterministic output pattern that FAILS replay?"
- If NO: "DO NOT add new normalization rule (no gap exists)"
- If YES: "Proceed to Step 2"

**Step 2 — Surface Lock Coverage:**
- Question: "Is this pattern already covered by Surface Lock (timestamps, PIDs, elapsed)?"
- If YES: "DO NOT add new rule (already covered)"
- If NO: "Proceed to Step 3"

**Step 3 — Stable Serialization Coverage:**
- Question: "Is this pattern already covered by Stable Serialization (sort_keys, canonical numeric)?"
- If YES: "DO NOT add new rule (already covered)"
- If NO: "Proceed to Step 4"

**Step 4 — Normalization Principle:**
- Question: "Can this pattern be normalized WITHOUT losing semantic information?"
- If NO: "DO NOT normalize (semantic information required)"
- If YES: "Add new normalization rule (last resort)"

**Requirements for new normalization rules:**
- Must be deterministic (same input → same output)
- Must preserve semantic information (no information loss)
- Must be reversible at analysis time (can reconstruct if needed)
- Must document in verification ladder (add to edge tests)

### Triggers for New Normalization Rules

**Example 1: Hostname normalization**
- Gap: "Different hostnames cause diff failures"
- Coverage: "Not covered by Surface Lock or Stable Serialization"
- Principle: "Can normalize hostnames to 'localhost' without losing semantics"
- Action: "Add hostname normalization rule"

**Example 2: User ID normalization**
- Gap: "Different user IDs cause diff failures"
- Coverage: "Not covered by existing rules"
- Principle: "Can normalize user IDs to 'user' without losing semantics"
- Action: "Add user ID normalization rule"

### Anti-Patterns (Do NOT Add)

**Stylistic Preferences:**
- Example: "Prefer tabs over spaces"
- Reason: "Not a determinism gap, stylistic preference"

**Semantic Information Loss:**
- Example: "Strip all numeric values"
- Reason: "Loses semantic information, prevents verification"

**Over-Normalization:**
- Example: "Normalize all strings to lowercase"
- Reason: "Case sensitivity may be semantic (filenames, identifiers)"

---

## 5) Integration with Recent Skills [NEW v2.0.0]

### Skill 1: prime-coder v2.0.0
**Integration points:**
- **Evidence normalization**: gpt-mini-hygiene normalizes `/evidence/` artifacts
- **Behavioral hash**: prime-coder uses normalized outputs for behavioral hashing
- **GPT-Mini Hygiene section**: prime-coder explicitly requires gpt-mini-hygiene

**Fusion benefit:**
- Evidence artifacts are replay stable (normalized)
- Behavioral hashes are deterministic (no drift)

### Skill 2: tool-output-normalizer (infrastructure skill)
**Integration points:**
- **Tool output normalization**: Both normalize tool outputs (gpt-mini-hygiene for evidence, tool-output-normalizer for tool calls)
- **Deterministic substrate**: Both enforce determinism

**Fusion benefit:**
- Consistent normalization across evidence and tool outputs

### Skill 3: golden-replay-seal (infrastructure skill)
**Integration points:**
- **Replay stability**: gpt-mini-hygiene enables replay stability via normalization
- **Golden fixture**: golden-replay-seal verifies replay stability

**Fusion benefit:**
- Normalized outputs enable golden fixture verification

### Skill 4: semantic-drift-detector (quality skill)
**Integration points:**
- **Behavioral hash**: Both use behavioral hashing (gpt-mini-hygiene normalizes inputs, semantic-drift-detector tracks hashes)
- **Drift detection**: semantic-drift-detector detects drift in normalized outputs

**Fusion benefit:**
- Normalized outputs prevent false positives in drift detection

### Skill 5: artifact-hash-manifest-builder (infrastructure skill)
**Integration points:**
- **Content addressing**: artifact-hash-manifest-builder hashes normalized artifacts (gpt-mini-hygiene provides normalization)
- **SHA256 checksums**: Both use exact checksums (no float)

**Fusion benefit:**
- Normalized artifacts have stable hashes (content-addressable)

### Skill 6: prime-math v2.1.0
**Integration points:**
- **Exact computation**: Both enforce exact computation (gpt-mini-hygiene: canonical numeric, prime-math: int/Fraction/Decimal)
- **No float drift**: Both forbid float in verification paths

**Fusion benefit:**
- Exact computation throughout (no rounding errors)

### Skill 7: wish-qa v2.0.0
**Integration points:**
- **Gate mapping**: gpt-mini-hygiene maps to wish-qa gates (G0, G1, G5, G3, G9, G13, G12)
- **Determinism gate (G13)**: gpt-mini-hygiene enforces G13

**Fusion benefit:**
- Determinism gate enforced via normalization

### Skill 8: epistemic-typing v2.0.0
**Integration points:**
- **Lane A classification**: gpt-mini-hygiene is Lane A (deterministic normalization)
- **Lane algebra**: Normalization preserves Lane A (no upgrades)

**Fusion benefit:**
- Normalization maintains Lane A throughout

### Skill 9: axiomatic-truth-lanes v2.0.0
**Integration points:**
- **Lane dominance**: gpt-mini-hygiene enforces Lane A (axiom: normalization is deterministic)
- **MIN operator**: Lane(Normalized Output) = Lane A (strongest guarantee)

**Fusion benefit:**
- Normalization is axiomatic (Lane A enforcement)

### Skill 10: shannon-compaction v2.0.0
**Integration points:**
- **Interface-first**: Both optimize for efficiency (gpt-mini-hygiene: normalization, shannon-compaction: witness lines)
- **Deterministic extraction**: Both are deterministic

**Fusion benefit:**
- Normalized + compacted = efficient + deterministic

### Skill 11: recipe-selector v2.0.0
**Integration points:**
- **CPU-first**: gpt-mini-hygiene is CPU-first (no LLM, deterministic normalization)
- **Deterministic routing**: Both enforce determinism

**Fusion benefit:**
- CPU-first normalization prevents nondeterministic routing

### Skill 12: counter-required-routering v2.0.0
**Integration points:**
- **Hard ceilings**: Both enforce hard limits (gpt-mini-hygiene: normalization scope, counter-required: arithmetic ceilings)
- **Deterministic execution**: Both are deterministic

**Fusion benefit:**
- Hard ceilings + normalization = bounded + deterministic

---

## 6) Compression Insights [NEW v2.0.0]

### Insight 1: Timestamp Stripping (Time Compression)
**Normalization rule:** Strip timestamps, elapsed timings
**Compression type:** Time (removes temporal variance)
**Justification:**
- Principle: "Same logical operation → same normalized output (regardless of when executed)"
- Variance reduction: "Timestamps add O(n) variance (n = execution instances), normalization → O(1) variance"
- Benefit: "Replay stability (same inputs → same outputs, regardless of time)"

### Insight 2: PID Stripping (Process Compression)
**Normalization rule:** Strip PIDs
**Compression type:** Structural (removes process-specific identifiers)
**Justification:**
- Principle: "Same logical operation → same normalized output (regardless of process ID)"
- Variance reduction: "PIDs add O(n) variance (n = process instances), normalization → O(1) variance"
- Benefit: "Replay stability across different processes"

### Insight 3: Stable Serialization (Structural Compression)
**Normalization rule:** `sort_keys=True` for JSON
**Compression type:** Structural (canonical ordering)
**Justification:**
- Principle: "Same data → same serialization (canonical order)"
- Ordering complexity: "Unordered JSON = O(n!) possible orderings, sorted = O(1) canonical ordering"
- Benefit: "Byte-identical diff (deterministic serialization)"

### Insight 4: Path Normalization (Structural Compression)
**Normalization rule:** Repo-relative paths
**Compression type:** Structural (canonical paths)
**Justification:**
- Principle: "Same logical location → same normalized path (regardless of absolute prefix)"
- Path variance: "Absolute paths = O(n) variance (n = systems), repo-relative = O(1) variance"
- Benefit: "Portable evidence (works across systems)"

### Insight 5: Canonical Numeric Formatting (Correctness Compression)
**Normalization rule:** Stable numeric representation (no float drift)
**Compression type:** Correctness (exact representation)
**Justification:**
- Principle: "Same numeric value → same representation (no rounding errors)"
- Float drift: "Float representation = O(ε) error (ε = machine epsilon), canonical = O(0) error"
- Benefit: "Exact computation (no rounding errors in verification)"

### Summary
**Total normalization rules:** 5 (timestamp, PID, sort_keys, path, numeric)
**Compression types:**
- Time: Timestamp stripping (O(n) → O(1) temporal variance)
- Structural: PID stripping, Stable serialization, Path normalization (O(n) → O(1) structural variance)
- Correctness: Canonical numeric (O(ε) → O(0) error)

**Justification principle:**
"Each normalization rule removes non-semantic variance (time, process, order, location, representation) while preserving semantic information (logic, data, operations). This enables replay stability: same inputs → same outputs, regardless of temporal, structural, or computational variance."

---

## 7) Lane Algebra Integration [NEW v2.0.0]

### Lane Classification

**Lane A (Deterministic):**
- Timestamp stripping (deterministic rule)
- PID stripping (deterministic rule)
- Stable serialization (`sort_keys=True`, deterministic)
- Path normalization (repo-relative, deterministic)
- Canonical numeric formatting (exact representation, deterministic)

**Lane B (Framework):**
- None (gpt-mini-hygiene is pure Lane A)

**Lane C (Heuristic):**
- None (gpt-mini-hygiene is pure Lane A)

**Lane STAR (Narrative):**
- None (gpt-mini-hygiene forbids narrative)

### Lane Algebra Enforcement

**MIN Operator:**
- Rule: "Lane(Normalized Output) = Lane A (all normalization rules are deterministic)"
- Guarantee: "Normalization preserves Lane A (no downgrades)"

**Forbidden Upgrades:**
- Lane C → Lane A: "Heuristic normalization cannot become deterministic" (FORBIDDEN)
- Lane B → Lane A: "Framework normalization cannot become deterministic" (FORBIDDEN)

**Allowed Operations:**
- Lane A → Lane A: "Deterministic normalization preserves Lane A" (ALLOWED)

### Forbidden States

**DRIFT:**
- Definition: "Normalized output changes across executions (non-determinism)"
- Detection: "Behavioral hash mismatch"
- Recovery: "Identify non-deterministic source, add normalization rule"

**NONDETERMINISM:**
- Definition: "Normalization rule is non-deterministic (same input → different outputs)"
- Detection: "Replay stability test failure"
- Recovery: "Revert non-deterministic rule, use deterministic alternative"

### Integration with Axiomatic Truth Lanes

**Axiom Classification:**

**Lane A Axioms:**
- Surface Lock: "Timestamps, PIDs, elapsed MUST be stripped (determinism axiom)"
- Stable Serialization: "JSON keys MUST be sorted (determinism axiom)"
- Path Normalization: "Paths MUST be repo-relative (portability axiom)"

**Conflict Resolution:**
- Rule: "Lane A > Lane B > Lane C (axioms win)"
- Example: "If heuristic suggests preserving timestamps for debugging → Lane A (strip timestamps) > Lane C (preserve timestamps) → timestamps stripped"

**Deprecation Requirement:**
- Rule: "Never break Lane A axiom without deprecation plan"
- Example: "If removing timestamp stripping → requires deprecation plan (migration steps, compatibility window, test updates)"

---

## 8) What Changed from v0.2.0 → v2.0.0 [NEW v2.0.0]

### Preserved ALL v0.2.0 Features
- **Confirmation:** ALL v0.2.0 features preserved (Never-Worse Doctrine)
- **Count:** 2 core features (Surface Lock, Stable Serialization)

### New in v2.0.0

**Verification Ladder Enhancement:**
- Before v0.2.0: "Implicit verification (no explicit tests)"
- After v2.0.0: "3 verification rungs (641, 274177, 65537) mapped to wish-qa gates (G0, G1, G5, G3, G9, G13, G12)"
- Benefit: "Explicit gate coverage (7 gates enforced)"

**Anti-Optimization Clause:**
- Before v0.2.0: "Implicit never-worse doctrine"
- After v2.0.0: "Explicit preserved features list (Surface Lock, Stable Serialization)"
- Benefit: "Audit trail for what must be preserved in future versions"

**Gap-Guided Extension:**
- Before v0.2.0: "No explicit criteria for when to add normalization rules"
- After v2.0.0: "4-step decision tree (gap identification → surface lock coverage → stable serialization coverage → normalization principle)"
- Benefit: "Prevents normalization bloat (build what's needed, not exhaustive)"

**Integration Documentation:**
- Before v0.2.0: "Implicit integration (no documentation)"
- After v2.0.0: "Explicit integration with 12 recent skills"
- Benefit: "Cross-skill fusion documented"

**Compression Insights:**
- Before v0.2.0: "No explicit justification for normalization rules"
- After v2.0.0: "5 insights mapping normalization rules to compression types (time, structural, correctness)"
- Benefit: "Design rationale captured (why each normalization rule exists)"

**Lane Algebra Integration:**
- Before v0.2.0: "Implicit Lane A (no explicit classification)"
- After v2.0.0: "Explicit Lane A classification, lane algebra enforcement (MIN operator), forbidden states (DRIFT, NONDETERMINISM)"
- Benefit: "Lane enforcement throughout (pure Lane A skill)"

### Impact
- **Reliability:** 10/10 maintained (all v0.2.0 features preserved)
- **Auditability:** Improved (explicit preserved features, gate mapping, compression insights)
- **Extensibility:** Improved (gap-guided extension prevents normalization bloat)
- **Integration:** Improved (12 skills fusion documented)
- **Epistemic Hygiene:** Improved (explicit Lane A enforcement)

### No Breaking Changes
- **Confirmation:** v2.0.0 is strictly additive over v0.2.0
- **Verification:** All v0.2.0 normalization rules preserved, no removals, no degradations

---

*"Auth: 65537"*
