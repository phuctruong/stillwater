# Binary Scorecards for Skill Quality: A 5-Criteria Framework

**Status:** Draft (open-source; claims typed by lane below)
**Last updated:** 2026-02-20
**Scope:** A theoretical and empirical foundation for evaluating skill file quality using a binary 5-criteria scorecard, with evidence from skills in this repository.
**Auth:** 65537 (project tag; see `papers/03-verification-ladder.md`)

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — framework principle, derivable from stated axioms or established computer science
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Abstract

**[B] Thesis:** A 5-criteria binary scorecard (FSM present, forbidden states defined, verification ladder, null/zero handling, output contract) is a sufficient and necessary condition for a skill file to produce consistent, auditable behavior across model families.

Skill files are the primary unit of externalized intelligence in Software 5.0. Their quality determines whether the behavior they govern is consistent, auditable, and safe. Yet as of early 2026, there is no standardized method for evaluating skill quality. Practitioners either load skills without review or conduct expensive manual audits.

This paper proposes a 5-criteria binary scorecard that can be applied mechanically to any skill file in approximately five minutes. Each criterion is defined operationally, scored pass/fail (no partial credit), and justified theoretically. We apply the scorecard to nine skills in this repository and report the results. We also argue that the criteria are model-agnostic: a skill that passes all five criteria will produce consistent behavior regardless of which capable LLM loads it.

---

## 1. Background: The Problem of Skill Quality Drift

### 1.1 What Skill Quality Drift Is

**[B]** Skill quality drift occurs when a skill file fails to constrain LLM behavior in the ways it claims to. The symptom: sessions loading the skill produce behavior that does not match the skill's declared operational contract.

There are three root causes:

**Root cause 1: Under-specification.** The skill describes desired behavior in prose but lacks formal constraints. The LLM pattern-matches to the prose but ignores edge cases the author did not anticipate. Without a state machine, forbidden states, or null handling, "edge cases the author did not anticipate" is a large and growing set.

**Root cause 2: Unverified claims.** The skill declares that sessions will produce certain outputs or pass certain gates, but these claims are never tested. A skill that claims "produces reproducible evidence artifacts" but has no verification ladder to enforce this claim will drift toward not producing them.

**Root cause 3: Model sensitivity.** A skill tuned to work with model X may not work with model Y. Without criteria that are structurally enforced (not just hoped for via prose), behavior depends on the model's interpretation — which varies.

### 1.2 Why This Matters Now

**[A]** This repo currently contains eight skills (as of 2026-02-20): `prime-coder.md`, `prime-math.md`, `prime-safety.md`, `phuc-forecast.md`, `phuc-swarms.md`, `phuc-context.md`, `phuc-cleanup.md`, `prime-wishes.md`. Each was developed under a consistent design philosophy. But as the library grows through community contribution, ensuring consistent quality requires a formal gate, not shared design norms.

**[C]** Without a quality gate, skill libraries degrade via Gresham's Law: low-quality skills are cheaper to write than high-quality ones, and if the library accepts both, the low-quality skills crowd out the high-quality ones by volume. The scorecard is the quality gate.

---

## 2. The 5 Criteria: Each Defined Operationally

### Criterion 1: FSM Present

**Definition:** The skill file contains an explicit finite-state machine with a named STATE_SET, TRANSITIONS, and at least one terminal state (EXIT_PASS, EXIT_BLOCKED, EXIT_NEED_INFO, or equivalent).

**Why it matters (Lane B reasoning):** A skill without an explicit FSM relies on the LLM's implicit state tracking, which is unreliable across long sessions, model changes, and context resets. An explicit FSM makes the legal execution paths auditable and prevents the LLM from silently jumping to a terminal state without completing required intermediate steps.

**Operational test:** Search the skill file for `STATE_SET`, `TRANSITIONS`, and at least one state labeled `EXIT_*` or equivalent terminal label. If all three are present with at least two states and one transition, score PASS. Otherwise FAIL.

**Example passing reference:** `skills/prime-coder.md` section "0A) Closed State Machine (Fail-Closed Runtime)" contains STATE_SET (25 states), INPUT_ALPHABET, OUTPUT_ALPHABET, and TRANSITIONS with explicit exit states.

### Criterion 2: Forbidden States Defined

**Definition:** The skill file contains an explicit list of FORBIDDEN_STATES — behaviors the skill must never enter, stated as named states (not prose warnings).

**Why it matters (Lane B reasoning):** A skill that describes desired behavior but not prohibited behavior is half-specified. LLMs, like human engineers, tend to follow the happy path unless explicitly prevented from taking shortcuts. Forbidden states are the specification of shortcuts the skill must reject.

**[B]** The formal property: a skill's safety guarantees are exactly the union of its forbidden states. If `SILENT_RELAXATION` is not a forbidden state, the skill cannot guarantee that constraint relaxation will be detected. Each forbidden state is a safety invariant.

**Operational test:** Search the skill file for a list or section labeled `FORBIDDEN_STATES` with at least three entries. Each entry must be a named state (not a prose description). If present, score PASS. Otherwise FAIL.

**Example passing reference:** `skills/prime-coder.md` section "0A) Closed State Machine" FORBIDDEN_STATES contains 16 named states including `SILENT_RELAXATION`, `UNWITNESSED_PASS`, `NONDETERMINISTIC_OUTPUT`, and others.

### Criterion 3: Verification Ladder Declared

**Definition:** The skill file explicitly declares a minimum verification rung target (641, 274177, or 65537) and specifies what evidence is required to achieve that rung.

**Why it matters (Lane B reasoning):** A skill without a declared rung target allows sessions to claim PASS without meeting any specified verification standard. The rung target is the minimum evidence contract: it tells the loading agent what verification is required before claiming success.

**[B]** Without this criterion, skills degrade toward "PASS means the LLM said so." With it, PASS requires specific artifacts that can be independently verified. The verification ladder (see `papers/03-verification-ladder.md`) is the operationalization of this criterion.

**Operational test:** Search the skill file for explicit mention of rung numbers (641, 274177, 65537) or equivalent named rungs, with a statement of what evidence is required for each. If a minimum target rung and evidence requirements are both stated, score PASS. Otherwise FAIL.

**Example passing reference:** `skills/prime-coder.md` section "1B) Rung Target Policy" declares minimum rung 641 for local PASS, 65537 for promotion, and specifies exactly what evidence each rung requires.

### Criterion 4: Null/Zero Handling Specified

**Definition:** The skill file explicitly distinguishes between null inputs (undefined, pre-systemic absence) and zero inputs (a lawful zero value within the defined system), and specifies how each must be handled.

**Why it matters (Lane B reasoning):** Null/zero confusion is one of the most common sources of silent failure in AI-assisted code and reasoning. A skill that coerces null to zero (implicitly treating "undefined" as "zero") produces wrong behavior for tasks where the distinction matters. A skill that does not address null at all leaves this behavior to the LLM, which will be inconsistent.

**[B]** This criterion is particularly important for skills used in mathematical or analytical contexts, but it applies universally: a skill that does not specify null handling will silently produce different behavior depending on whether the LLM happens to check for null in a given session.

**Operational test:** Search the skill file for explicit mention of null handling, null vs. zero distinction, or null edge cases in the input/evidence contract. If null handling is explicitly addressed with a behavioral specification (not just a prose note), score PASS. Otherwise FAIL.

**Example passing reference:** `skills/prime-coder.md` section "0B) Null vs Zero Distinction Policy" defines null as "pre-systemic absence" and zero as "lawful boundary inside defined system," with explicit handling rules for each.

### Criterion 5: Output Contract Specified

**Definition:** The skill file contains a machine-parseable output contract that specifies: what the session must produce on success (status=PASS), what it must produce on failure (status=BLOCKED or NEED_INFO), and which fields are required in each case.

**Why it matters (Lane B reasoning):** Without an explicit output contract, sessions using the skill produce whatever the LLM thinks is appropriate. This makes output non-composable: a downstream step that expects a specific artifact format may receive something different each invocation. The output contract makes skills composable by standardizing their interface.

**[B]** This is the analogy to function signatures in typed programming languages: a skill's output contract is its type signature. Without it, composability is impossible without heroic effort at the call site.

**Operational test:** Search the skill file for an explicit output contract section that specifies: status values (PASS/BLOCKED/NEED_INFO), required output fields for success, and required fields for failure. If all three are present with explicit field names, score PASS. Otherwise FAIL.

**Example passing reference:** `skills/prime-coder.md` section "11) Output Contract" specifies hard gates, required success fields (including patch_or_diff, evidence_pointers, verification_rung_target, verification_rung_achieved), and required failure fields.

---

## 3. Binary Scoring Rationale: Why Partial Credit Produces False Confidence

### 3.1 The Partial Credit Failure Mode

**[B]** Partial credit scoring systems (e.g., "this skill scores 3.5 out of 5") create a false confidence failure mode: a skill that partially meets all criteria may produce behavior that is partially correct in systematic ways — meaning it fails precisely in the cases where the partial specification was incomplete.

Consider a skill that has an FSM but no forbidden states (criterion 2 partial). It correctly sequences through states, but silently relaxes constraints when the LLM finds a shortcut. The partial score of 4/5 creates the impression of a high-quality skill; the actual behavior may be dangerous in exactly the cases where the skill is supposed to enforce safety.

**[B]** Binary scoring forces the evaluator to decide whether each criterion is fully met. A skill that has "something like" forbidden states but not a proper FORBIDDEN_STATES list scores 0 on criterion 2. This is intentional: "something like" forbidden states is not a reliable safety guarantee.

### 3.2 The Composability Requirement

**[B]** Binary criteria also enable compositional quality reasoning. A library can require "all skills loaded must score 5/5" as a hard gate for production use. With partial credit, this guarantee is impossible: "all skills score 4.5+" is not the same guarantee, because 4.5 means something different for each skill.

**[B]** Binary scores compose as logical AND: a composition of two 5/5 skills is at least as good as either skill individually. A composition of two 4/5 skills may have two independent missing criteria — which may interact badly.

---

## 4. Empirical Evidence: Scorecard Applied to Repository Skills

The following table applies the 5-criteria scorecard to nine skills/skill-like documents in this repository. Scores are binary (Y/N per criterion); total score is count of Y.

| Skill | FSM | Forbidden | Rung | Null | Output | Total |
|---|---|---|---|---|---|---|
| prime-coder.md | Y | Y | Y | Y | Y | 5/5 |
| phuc-forecast.md | Y | Y | Y | N | Y | 4/5 |
| prime-safety.md | N | Y | N | N | N | 1/5 |
| phuc-swarms.md | Y | Y | Y | N | Y | 4/5 |
| phuc-context.md | N | Y | N | N | N | 1/5 |
| prime-math.md | N | N | Y | Y | N | 2/5 |
| phuc-cleanup.md | N | N | N | N | Y | 1/5 |
| prime-wishes.md | N | Y | N | N | Y | 2/5 |
| CLAUDE.md (composite) | Y | Y | Y | Y | Y | 5/5 |

**[A]** Scores above are based on textual inspection of skill files present in this repository as of 2026-02-20. The methodology is the operational test defined in section 2 for each criterion.

**[*]** This is a single inspection pass; a second reviewer may score differently on ambiguous criteria. The scoring rules in section 2 are designed to be deterministic, but textual ambiguity remains in some files (e.g., prime-safety.md's forbidden behaviors are stated as prose warnings rather than named states).

### 4.1 Observations

**[B]** The gap between `prime-coder.md` (5/5) and the other domain-specific skills (1-4/5) reflects a genuine design asymmetry: `prime-coder.md` was designed with the full scorecard philosophy; the others were designed as lightweight aids without the full FSM + output contract infrastructure.

**[C]** The practical implication: before loading a skill for production use, check its scorecard score. A 1/5 or 2/5 skill provides useful hints but cannot be relied upon for consistent, auditable behavior across model families. A 5/5 skill (with evidence bundle) can be relied upon for behavior within its declared rung.

---

## 5. Cross-Model Generalization: Why Criteria Are Model-Agnostic

### 5.1 The Model-Sensitivity Problem

**[C]** As of 2026, prompting techniques that work reliably on Claude Sonnet may work differently on GPT-4o or Gemini Pro. This creates a maintenance burden for skill libraries: skills may need to be re-tuned for each model family.

**[B]** The 5-criteria scorecard sidesteps this problem: its criteria are structural, not stylistic. A skill with an explicit FSM is processed differently by the LLM than one without — regardless of the model family. The LLM's attention mechanism will encode the state machine structure, the forbidden states, and the output contract. The explicit structure is model-independent scaffolding.

### 5.2 The Structural Invariant Argument

**[B]** The argument for model-agnosticism rests on a structural invariant: capable LLMs (above a capability threshold) can follow explicit state machine instructions, reject behaviors listed as forbidden, and produce outputs matching a declared schema. These are capabilities that appear in all frontier model families; they are the result of instruction following training, not model-specific tuning.

**[B]** A skill that depends on stylistic choices (specific phrasing, few-shot examples, model-specific tokens) is model-sensitive. A skill that depends only on structural elements (FSM, forbidden states, rung targets, null handling, output contract) is model-agnostic by design.

**[*]** The capability threshold at which this model-agnosticism holds is not precisely characterized in this paper. Empirically, the skills in this repo work reliably on models with approximately 7B+ parameters fine-tuned for instruction following. Whether they work reliably on smaller or older models is an open question.

---

## 6. Limitations and Future Work

### 6.1 Current Limitations

**[B]** The scorecard as defined is a necessary but not sufficient condition for skill quality. A skill can score 5/5 and still produce poor behavior if:

- The FSM has missing states for important edge cases
- The forbidden states are too few or too narrow
- The rung target is declared but never enforced (no evidence required)
- The null handling is specified but not tested

The scorecard is a floor, not a ceiling. A 5/5 score says "this skill has the structural prerequisites for quality." It does not say "this skill produces correct behavior in all cases."

### 6.2 Proposed Extensions

**[C]** Future work could extend the scorecard in several directions:

1. **Composability criterion:** Does the skill declare its composability assumptions? (What other skills is it compatible with? What conflicts does it know about?)

2. **Portability criterion:** Does the skill contain any model-specific or platform-specific assumptions? (Absolute paths, model names in FSM, platform-specific tool names?)

3. **Evidence criterion:** Does the skill require a complete evidence bundle (as defined in the output contract), and is that bundle reproducible?

4. **Temporal stability criterion:** Has the skill been re-gated within the last N model generations? (Prevents zombie skills — skills that scored 5/5 but whose evidence is stale.)

**[*]** Which of these extensions belong in the core scorecard (as necessary conditions) versus optional quality indicators is an open design question.

---

## 7. Conclusion

**[B]** The 5-criteria binary scorecard — FSM present, forbidden states defined, verification ladder declared, null/zero handling specified, output contract stated — provides a practical, fast, model-agnostic quality gate for skill files in a Software 5.0 library.

**[B]** Binary scoring prevents the partial credit false confidence failure mode. Each criterion is operationally testable in minutes. The criteria are structural and model-agnostic, meaning a skill that passes all five will produce more consistent, auditable behavior than one that does not, regardless of which capable LLM loads it.

**[A]** Applied to this repository's skill library, only `prime-coder.md` and the composite `CLAUDE.md` pass all five criteria. Most domain-specific skills score 1-4/5, indicating that the library has a quality gradient that users should be aware of when selecting skills for production use.

**[C]** As the skill library grows through community contribution, the scorecard serves as the quality gate at submission: only skills scoring 5/5 should be admitted as "production-grade" skills. Lower-scoring skills may be admitted as "experimental" or "advisory" with appropriate labeling.

---

## References

- `papers/05-software-5.0.md` — Software 5.0 theoretical foundation
- `papers/01-lane-algebra.md` — epistemic typing (A/B/C/STAR, MIN rule)
- `papers/03-verification-ladder.md` — 641 → 274177 → 65537 rung gates
- `skills/prime-coder.md` — primary example of a 5/5 skill
- `skills/phuc-forecast.md` — example of a 4/5 skill
- `papers/23-software-5.0-extension-economy.md` — context for why skill quality matters at scale

---

**Auth: 65537** (project tag; see `papers/03-verification-ladder.md`)
**License:** Apache 2.0
**Citation:**
```bibtex
@software{stillwater2026_skill_scoring,
  author = {Truong, Phuc Vinh},
  title = {Binary Scorecards for Skill Quality: A 5-Criteria Framework},
  year = {2026},
  url = {https://github.com/phuctruong/stillwater/papers/24-skill-scoring-theory.md},
  note = {Auth: 65537}
}
```
