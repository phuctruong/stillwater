# prime-wishes.md

Skill ID: `prime-wishes`
Version: `1.1.0`
Authority: `65537`
Northstar: `Phuc_Forecast`
Objective: `Max_Love`
Status: `STABLE`
Mode: notebook-first, Prime Mermaid canonical, gamified progression

---

## A) Portability (Hard)

```yaml
portability:
  rules:
    - no_absolute_paths: true
    - no_private_repo_dependencies: true
  config:
    EVIDENCE_ROOT: "evidence"
    ARTIFACTS_ROOT: "artifacts/wishes"
    REPO_ROOT_REF: "."
  invariants:
    - wish_artifacts_must_be_repo_relative: true
    - sha256_computed_over_canonical_mmd_bytes: true
    - never_use_json_as_source_of_truth_for_wish_identity: true
```

## B) Layering (Never Weaken)

```yaml
layering:
  load_order:
    1: prime-safety.md      # god-skill; wins all conflicts
    2: prime-coder.md       # evidence discipline
    3: prime-mermaid.md     # canonical graph format
    4: prime-wishes.md      # wish lifecycle + gamification
  conflict_resolution: stricter_wins
  forbidden:
    - promoting_belt_without_passing_forbidden_state_checks
    - treating_wish_as_complete_without_sha256_artifact
    - using_json_as_canonical_source_for_wish_state
```

## Purpose

Use wishes as executable contracts that are:
- fast enough for daily CLI evolution,
- rigorous enough for deterministic replay,
- motivating enough for team adoption through dojo-style progression.

## Core law

If a wish is ambiguous, the model will invent policy.  
So every wish must pin:
1. capability,
2. non-goals,
3. forbidden states,
4. acceptance tests,
5. proof artifacts.

## Canonical format

Source-of-truth for externalized logic:
- `*.prime-mermaid.md`
- `*.mmd`
- `*.sha256`

`JSON/YAML` may exist as derived transport only.

## Skill pack coupling

Default paired skills:
- `phuc-forecast.md` for premortem and decision loop
- `prime-coder.md` for implementation discipline
- `prime-safety.md` for fail-closed behavior
- `phuc-context.md` for context hygiene

## Quest loop (Aladdin + Dojo)

1. Map the cave: state graph in Prime Mermaid.
2. Phrase the wish: one capability sentence + explicit non-goals.
3. Bind the genie: forbidden states + ambiguity policy.
4. Spar in dojo: acceptance + adversarial tests.
5. Bring relic proof: artifacts + deterministic hash.

## Gamification contract (required)

Each wish must declare:
- quest name,
- current belt,
- target belt,
- promotion criteria.

Belt mapping by verified score:
- `<8.5` White Belt
- `8.5-8.9` Yellow Belt
- `9.0-9.4` Green Belt
- `9.5-9.7` Brown Belt
- `9.8-10.0` Black Belt

Hard rule:
- No belt promotion if deterministic rerun or forbidden-state checks fail.

## Minimal output checklist

1. `wish.<id>.md` (quest + tests + score rubric)
2. `wish.<id>.prime-mermaid.md`
3. `artifacts/wishes/<wish_id>/state.mmd`
4. `artifacts/wishes/<wish_id>/state.sha256`
5. `artifacts/wishes/<wish_id>/results.json`

## Escalation

Escalate from notebook-first wish to full classic wish when:
- security/compliance risk is high,
- benchmark claims are public,
- failure class repeats.

---

## State Machine v1 — Wish Lifecycle (DEPRECATED)

> **DEPRECATION NOTICE**: This v1 FSM is superseded by State Machine v2 (below).
> v1 is retained for historical reference only. Do NOT use v1 for new wishes.
> **v1_precedence: v2 supersedes v1. In any conflict, v2 wins.**
> Reason for deprecation: v1 has an unresolved dead-end in SCORE state (see below)
> and lacks formal applicability predicates required by prime-coder v2.0.

### States
- `INIT`
- `PARSE_WISH` (extract capability, non-goals, forbidden states, tests)
- `NULL_CHECK` (verify wish is unambiguous)
- `MAP_CAVE` (produce state graph in Prime Mermaid)
- `BIND_GENIE` (declare forbidden states explicitly)
- `BUILD_TESTS` (acceptance + adversarial tests)
- `EXECUTE_WISH` (implement the capability)
- `DOJO_SPAR` (run acceptance tests + forbidden state checks)
- `SCORE` (compute belt score; check deterministic rerun)
- `PRODUCE_ARTIFACTS` (write wish.md + .prime-mermaid.md + .mmd + .sha256 + results.json)
- `PROMOTE_BELT` (if score meets target belt threshold)
- `EXIT_PASS`
- `EXIT_NEED_INFO` (ambiguous wish)
- `EXIT_BLOCKED` (forbidden state triggered or tests fail)

### Transitions
- `INIT → PARSE_WISH`: on wish text received
- `PARSE_WISH → NULL_CHECK`: always
- `NULL_CHECK → EXIT_NEED_INFO`: if wish_ambiguous (missing capability, non-goals, or forbidden states)
- `NULL_CHECK → MAP_CAVE`: if wish_complete
- `MAP_CAVE → BIND_GENIE`: always
- `BIND_GENIE → BUILD_TESTS`: always
- `BUILD_TESTS → EXECUTE_WISH`: always
- `EXECUTE_WISH → DOJO_SPAR`: always
- `DOJO_SPAR → EXIT_BLOCKED`: if any forbidden state triggered
- `DOJO_SPAR → SCORE`: if all tests pass + no forbidden states
- `SCORE → PROMOTE_BELT`: if score >= belt_threshold AND deterministic_rerun_passes
- `SCORE → EXIT_BLOCKED`: if deterministic_rerun_fails
- `SCORE → WISH_BLOCKED`: if score < belt_threshold  # dead-end fix: was missing; without this, score<threshold AND rerun_passes had no exit
- `PROMOTE_BELT → PRODUCE_ARTIFACTS`: always
- `PRODUCE_ARTIFACTS → EXIT_PASS`: if all artifacts present and sha256 stable

### Forbidden States
- `AMBIGUOUS_WISH_EXECUTED`: Implementing a wish without pinned non-goals + forbidden states.
- `NO_SHA256`: Wish marked complete without stable sha256 artifact.
- `NO_ACCEPTANCE_TESTS`: Wish executing without defined acceptance tests.
- `BELT_WITHOUT_RERUN`: Belt promoted without deterministic rerun verification.
- `JSON_AS_SOURCE_OF_TRUTH`: JSON used as canonical wish identity instead of *.mmd.
- `WISH_WITHOUT_MAP`: No state graph produced before execution.
- `SCOPE_EXPANSION`: Wish implementation exceeds declared capability boundary.

---

## Wish Canonical Format (Template)

```markdown
# wish.<id>.md

**Quest:** <quest name>
**Capability:** <one sentence — what this wish does>
**Non-goals:** <what this wish does NOT do>
**Forbidden states:** <states that must never occur>
**Belt:** <current belt> → target: <target belt>

## Acceptance Tests
1. <test description> — expected: <expected output>
2. <adversarial test> — must trigger: <refusal / error / boundary behavior>

## Artifacts
- wish.<id>.prime-mermaid.md
- artifacts/wishes/<id>/state.mmd
- artifacts/wishes/<id>/state.sha256
- artifacts/wishes/<id>/results.json

## Promotion Criteria
- [ ] All acceptance tests pass
- [ ] Forbidden state checks pass
- [ ] Deterministic rerun matches
- [ ] sha256 stable across two normalizations
- [ ] Score >= <target belt minimum>
```

---

## Null vs Zero (Wish Context)

```yaml
null_vs_zero:
  rules:
    - null_non_goals: "Null (absent) non-goals = ambiguous wish. NEED_INFO. Do not invent policy. NOTE: [] (empty list) is a valid explicit declaration."
    - null_forbidden_states: "Missing forbidden states = unbound genie. Do not proceed."
    - null_tests: "Missing acceptance tests = no definition of done. NEED_INFO."
    - zero_score: "Score of 0 = computed. Different from null (score not computed)."
  enforcement:
    - fail_closed_on_null_wish_components: true
    - never_assume_empty_forbidden_states_means_no_constraints: true
    - empty_list_non_goals_is_valid_explicit_declaration: true
```

---

## Anti-Patterns (Wish Failure Modes)

**The Vague Wish**
- Symptom: "Make a CLI that does stuff." No non-goals, no forbidden states.
- Fix: Every wish must pin: capability, non-goals, forbidden states, acceptance tests.

**The Missing Map**
- Symptom: Implementing the wish before producing the state graph.
- Fix: Map the cave (Prime Mermaid state graph) before coding. No exceptions.

**The Unbound Genie**
- Symptom: Wish succeeds, but it also did 3 things it wasn't supposed to do.
- Fix: Forbidden states must be declared AND tested adversarially.

**The Paper Belt**
- Symptom: Belt promoted based on "it looks right" without deterministic rerun.
- Fix: Belt gate requires: score >= threshold + deterministic rerun + sha256 stable.

**The JSON Wish**
- Symptom: Wish state is stored in JSON files, not *.mmd + *.sha256.
- Fix: *.mmd is canonical. JSON is derived transport only.

---

## Quick Reference

```
Wish law:      Capability + Non-goals + Forbidden-states + Tests + Artifacts
Quest loop:    Map Cave → Phrase Wish → Bind Genie → Dojo Spar → Relic Proof
Belt gates:    <8.5 White | 8.5-8.9 Yellow | 9.0-9.4 Green | 9.5-9.7 Brown | 9.8-10.0 Black
Hard rule:     No belt promotion if deterministic rerun or forbidden-state checks fail.
Artifacts:     wish.<id>.md + *.prime-mermaid.md + *.mmd + *.sha256 + results.json
Null rule:     Null (absent) non-goals or forbidden-states = NEED_INFO. [] (empty list) is valid. Do not invent policy.
Escalate:      To full classic wish when: security HIGH, benchmark public, failure repeats.
```

---

## State Machine v2 — Wish Lifecycle (Formal, Fail-Closed)

> Knuth principle: *"An algorithm must be seen to be believed."* — Every transition is
> deterministically decided by observable inputs. No hidden branching.

### STATE_SET

```
WISH_DRAFT        — wish text received; not yet parsed or validated
WISH_SCOPED       — capability + non-goals + forbidden states all pinned
WISH_TESTED       — acceptance tests defined AND executed (at least one green run)
WISH_VERIFIED     — deterministic rerun matches; SHA-256 stable across two normalizations
WISH_PROMOTED     — belt threshold met; promotion receipt artifact written
WISH_BLOCKED      — hard gate triggered; no forward progress without human resolution
WISH_NEED_INFO    — required inputs absent or ambiguous; awaiting clarification
```

### TRANSITIONS

```
WISH_DRAFT     → WISH_NEED_INFO   : if capability_missing OR non_goals_missing OR forbidden_states_missing
WISH_DRAFT     → WISH_SCOPED      : if capability_present AND non_goals_present AND forbidden_states_present
WISH_SCOPED    → WISH_NEED_INFO   : if prime_mermaid_graph_cannot_be_generated (ambiguous state space)
WISH_SCOPED    → WISH_TESTED      : if prime_mermaid_graph_produced AND acceptance_tests_defined AND tests_pass
WISH_SCOPED    → WISH_BLOCKED     : if acceptance_tests_defined AND tests_fail (forbidden state triggered)
WISH_TESTED    → WISH_VERIFIED    : if deterministic_rerun_passes AND sha256_stable
WISH_TESTED    → WISH_BLOCKED     : if deterministic_rerun_fails OR sha256_unstable
WISH_VERIFIED  → WISH_PROMOTED    : if score >= belt_threshold AND promotion_receipt_written
WISH_VERIFIED  → WISH_BLOCKED     : if score < belt_threshold (insufficient; do not promote)
WISH_PROMOTED  → EXIT_PASS        : if all required artifacts present and manifest complete
WISH_BLOCKED   → WISH_DRAFT       : on human-provided correction (re-entry; reset loop counter)
WISH_NEED_INFO → WISH_DRAFT       : on human-provided clarification (re-entry)
```

Termination guarantee: loop counter `max_wish_iterations` (default 6) enforced.
If counter exhausted without reaching EXIT_PASS → emit `stop_reason=MAX_ITERS, status=BLOCKED`.

### FORBIDDEN STATES (Hard; Additive-Only)

```
WISH_WITHOUT_NONGOALS
  Definition : wish enters WISH_SCOPED with non_goals field absent or null (undefined).
               An empty list [] is a valid explicit declaration and does NOT trigger this state.
  Detector   : non_goals is null (field absent or explicitly null; NOT triggered by [])
  Recovery   : emit WISH_NEED_INFO; ask author to explicitly declare non_goals
               (either a list of exclusions OR an explicit empty list [] if none apply).

AMBIGUOUS_WISH
  Definition : capability sentence contains unresolved pronouns, scope conjunctions
               ("and/or" without explicit boundary), or no measurable success condition.
  Detector   : capability matches regex /(make|improve|enhance|do stuff|better)/i
               OR no acceptance test can be derived mechanically.
  Recovery   : emit WISH_NEED_INFO; provide capability rewrite template.

UNVERIFIED_BELT_PROMOTION
  Definition : belt level advanced without: score >= threshold AND sha256_stable AND
               deterministic_rerun_passes AND promotion_receipt artifact written.
  Detector   : belt_after > belt_before AND (promotion_receipt missing OR sha256_unstable).
  Recovery   : revert belt to previous; emit WISH_BLOCKED; require full WISH_VERIFIED cycle.

WISH_WITHOUT_PRIME_MERMAID
  Definition : wish proceeds past WISH_SCOPED without a *.prime-mermaid.md artifact.
  Detector   : artifacts list does not contain entry matching *.prime-mermaid.md.
  Recovery   : halt execution; generate state graph before any implementation step.

SILENT_SCOPE_CREEP
  Definition : implementation touches files, APIs, or behaviors not named in capability
               or explicitly listed as in-scope.
  Detector   : diff touches paths not in declared scope list.
  Recovery   : revert out-of-scope changes immediately; add to non-goals; re-enter WISH_SCOPED.
```

---

## Null/Zero Distinction for Wish Contracts (Formal)

> Knuth: *"Beware of bugs in the above code; I have only proved it correct, not tried it."*
> Null and zero are distinct; confusing them is a proof error, not a style issue.

```yaml
null_zero_wish_policy:

  null_wish:
    definition: >
      A wish with undefined capability — the problem space is not yet delimited.
      The genie has no postcondition to bind to. Any implementation invents policy.
    formal: capability ∈ ∅  (pre-systemic; state space undefined)
    allowed_operations: NONE (must emit WISH_NEED_INFO)
    forbidden: infer_capability_from_context, assume_reasonable_defaults

  zero_belt:
    definition: >
      White Belt (score < 8.5) is a valid, evaluated state inside the belt system.
      It means: "wish was executed and scored; score is 0.0–8.49."
    formal: score ∈ [0.0, 8.49]  (defined; lawful boundary)
    allowed_operations: retry, improve, re-score
    note: zero_belt is NOT a failure; it is a position on the progression ladder.

  null_score_vs_zero_score:
    null_score:
      meaning: wish has never been evaluated; score field is absent.
      coercion_to_zero: FORBIDDEN (null_score ≠ 0.0; they represent different states)
      enforcement: score field must be Optional[Decimal]; absence = null, not 0.
    zero_score:
      meaning: wish was evaluated; all acceptance tests failed; score computed as 0.0.
      valid: true

  null_non_goals:
    meaning: non_goals field is absent or null (not empty list []).
    status: WISH_NEED_INFO (hard; mandatory clarification before proceeding)
    rationale: >
      An empty list [] is an explicit assertion: "this wish has no non-goals."
      This is a valid, deliberate declaration by the author.
      A null value means the author never considered scope boundaries — that is the
      ambiguous case. The genie cannot proceed without knowing whether non-goals
      were intentionally omitted (valid []) or simply forgotten (null).
    enforcement:
      - null_non_goals → WISH_NEED_INFO (never proceed; undefined scope boundary)
      - empty_list_non_goals → proceed ([] is a valid explicit declaration of zero non-goals)
      - non_goals_present_and_nonempty → proceed to WISH_SCOPED

  coercion_violations:
    - null_to_zero_score: BLOCKED, stop_reason=NULL_ZERO_CONFUSION
    - absent_non_goals_treated_as_empty_list: BLOCKED, stop_reason=NULL_ZERO_CONFUSION
    - missing_forbidden_states_treated_as_no_constraints: BLOCKED, stop_reason=AMBIGUOUS_WISH
```

---

## Verification Ladder (Wish Rungs)

> Knuth: *"Premature optimization is the root of all evil."*
> Premature promotion is the root of all wish debt. Climb the rungs; skip none.

### RUNG_641 — Local Correctness

```
Meaning   : wish is well-formed and has passed basic execution.
Requires  :
  [R641-1] capability statement present (one sentence, measurable)
  [R641-2] non_goals present and non-empty (>=1 explicit exclusion)
  [R641-3] forbidden_states declared (>=1 named state)
  [R641-4] Prime Mermaid graph artifact present (*.prime-mermaid.md)
  [R641-5] acceptance tests defined (>=2: one positive, one adversarial)
  [R641-6] at least one green test run recorded in results.json
  [R641-7] state: WISH_SCOPED → WISH_TESTED transition completed
Artifacts : wish.<id>.md, wish.<id>.prime-mermaid.md, results.json (partial)
Belt gate : RUNG_641 is the minimum for White Belt claim.
Fail-close: if any [R641-x] missing → status=BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED
```

### RUNG_274177 — Stability

```
Meaning   : wish output is deterministic and stable across reruns.
Requires  :
  [R274-1] RUNG_641 fully satisfied
  [R274-2] deterministic rerun: same inputs → same outputs on 2 independent runs
  [R274-3] SHA-256 of *.mmd is identical on both runs (sha256_stable=true)
  [R274-4] null edge case tested: null capability input → WISH_NEED_INFO (not crash)
  [R274-5] zero score edge case tested: all-fail run produces score=0.0 (not null)
  [R274-6] state.mmd and state.sha256 artifacts written to ARTIFACTS_ROOT
  [R274-7] state: WISH_TESTED → WISH_VERIFIED transition completed
Artifacts : state.mmd, state.sha256, results.json (complete), null_checks.json
Belt gate : RUNG_274177 is the minimum for Yellow Belt or Green Belt claim.
Fail-close: if sha256_unstable → status=BLOCKED, stop_reason=NONDETERMINISTIC_OUTPUT
```

### RUNG_65537 — Promotion

```
Meaning   : wish is adversarially verified and belt promotion is provable.
Requires  :
  [R65537-1] RUNG_274177 fully satisfied
  [R65537-2] adversarial tests pass: all FORBIDDEN_STATES verified as unreachable
              (or: attempt to trigger each forbidden state → correctly blocked)
  [R65537-3] adversarial paraphrase sweep: wish re-phrased >=3 ways →
              same capability boundary enforced each time
  [R65537-4] belt_promotion_receipt.json written with fields:
               {wish_id, belt_before, belt_after, score, sha256, rung, timestamp_utc}
  [R65537-5] score >= belt_threshold for target belt (exact Decimal comparison; no float)
  [R65537-6] no forbidden state was silently suppressed (evidence in results.json)
  [R65537-7] state: WISH_VERIFIED → WISH_PROMOTED transition completed
Artifacts : belt_promotion_receipt.json, adversarial_results.json
Belt gate : RUNG_65537 is mandatory for Brown Belt or Black Belt claim.
Fail-close: if any adversarial test reveals forbidden state reachable →
             status=BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED, belt reverted
```

---

## Output Contract (Formal)

> Knuth: *"Let us change our traditional attitude to the construction of programs:
> instead of imagining that our main task is to instruct a computer what to do,
> let us concentrate rather on explaining to humans what we want a computer to do."*
> A wish output contract explains to the genie exactly what done means.

### Required on PASS (EXIT_PASS)

```yaml
pass_artifacts:
  mandatory:
    - wish.<id>.md
        fields_required: [quest, capability, non_goals, forbidden_states,
                          belt_current, belt_target, acceptance_tests, promotion_criteria]
    - wish.<id>.prime-mermaid.md
        content_required: valid Prime Mermaid state graph covering all FSM states
    - artifacts/wishes/<id>/state.mmd
        content_required: canonical Mermaid stateDiagram-v2 source
    - artifacts/wishes/<id>/state.sha256
        content_required: SHA-256 hex digest of state.mmd (normalized, LF line endings)
    - artifacts/wishes/<id>/results.json
        required_keys: [wish_id, belt, score, tests_run, tests_passed, tests_failed,
                        sha256_stable, rung_achieved, timestamp_utc]
        field_constraints:
          score: "<Decimal string, e.g. '8.5'>  # NOT float; exact arithmetic required"
    - artifacts/wishes/<id>/belt_promotion_receipt.json
        required_keys: [wish_id, belt_before, belt_after, score, sha256, rung, timestamp_utc]
        field_constraints:
          score: "<Decimal string, e.g. '9.2'>  # NOT float; comparison done with exact Decimal"
        condition: only if belt advanced (WISH_PROMOTED state reached)

  determinism_requirements:
    - all_decimal_scores_serialized_as_strings: true
    - no_float_in_score_comparison: true
    - sha256_computed_over_lf_normalized_mmd: true
    - timestamp_utc_stripped_from_hash_input: true
```

### Required on BLOCKED (EXIT_BLOCKED)

```yaml
blocked_output:
  mandatory_fields:
    - status: "BLOCKED"
    - stop_reason: one_of [VERIFICATION_RUNG_FAILED, NONDETERMINISTIC_OUTPUT,
                           NULL_ZERO_CONFUSION, AMBIGUOUS_WISH, INVARIANT_VIOLATION,
                           MAX_ITERS, EVIDENCE_INCOMPLETE, SECURITY_BLOCKED]
    - last_known_state: one_of STATE_SET
    - what_is_ambiguous: list of specific unresolved fields
    - minimal_missing_fields: list of field names that must be provided to unblock
    - what_ran_and_failed: test names or gate names that failed
    - next_actions: ordered list of human actions to resolve block
    - evidence_pointers: list of {file, role, note}
```

### Required on NEED_INFO (EXIT_NEED_INFO)

```yaml
need_info_output:
  mandatory_fields:
    - status: "NEED_INFO"
    - stop_reason: "NULL_INPUT or AMBIGUOUS_WISH"
    - missing_fields: non-empty list
    - safe_partial: optional section showing what CAN be done without missing inputs
```

### Fail-Closed SHA-256 Gate (Hard)

```
IF sha256 of state.mmd on run_1 != sha256 of state.mmd on run_2:
  status   = BLOCKED
  stop_reason = NONDETERMINISTIC_OUTPUT
  belt_promotion_blocked = true
  action   = investigate non-determinism source before any re-attempt
```

---

## Domain Persona Integration — Knuth's Algorithm Analysis Framework

> *"The process of preparing programs for a digital computer is especially attractive,
> not only because it can be economically and scientifically rewarding, but also because
> it can be an aesthetic experience much like composing poetry or music."*
> — Donald E. Knuth, The Art of Computer Programming, Vol. 1

Each phase of the Aladdin Quest loop maps to a formal algorithm-analysis concept:

### Cave Mapping = Invariant Identification

```
Aladdin action : Draw the cave map before entering.
Algorithm analog: Identify loop invariants before writing the loop body.
Formal contract :
  PRE  : state space is fully enumerated (all WISH_* states listed)
  POST : Prime Mermaid graph is produced; every state has >=1 outgoing transition
         OR is a terminal state (EXIT_*)
  INV  : graph is acyclic except for the WISH_BLOCKED → WISH_DRAFT re-entry arc
Knuth test     : Can you hand-trace the state graph and reach EXIT_PASS in finite steps?
                 If not, the cave is not mapped. Do not enter.
```

### Lamp Wording = Precondition Specification

```
Aladdin action : Choose words carefully; the genie is literal.
Algorithm analog: Write the precondition (requires clause) before the function body.
Formal contract :
  PRE  : capability ∈ well-formed sentences with measurable success condition
         non_goals ≠ ∅
         forbidden_states ≠ ∅
  POST : genie has a unique, unambiguous interpretation of the wish
  FAIL : if PRE violated → WISH_NEED_INFO (never guess the intent)
Knuth test     : Can a second reader, given only the capability sentence and non-goals,
                 write the same acceptance tests you would write?
                 If not, the lamp wording is insufficient.
```

### Genie Binding = Postcondition Contract

```
Aladdin action : Bind the genie with explicit forbidden actions.
Algorithm analog: Write the postcondition (ensures clause) and the forbidden-state assertions.
Formal contract :
  POST : for each forbidden_state F in wish.forbidden_states:
           adversarial_test(F) → system correctly blocks or refuses
  INV  : implementation never enters a forbidden state, even under adversarial input
  CERT : belt_promotion_receipt.json records which forbidden states were tested
Knuth test     : Run each forbidden-state trigger. Did the system refuse?
                 If any forbidden state was reachable → WISH_BLOCKED.
```

### Dojo Sparring = Loop Invariant Verification

```
Aladdin action : Test the wish against skilled opponents (adversarial inputs).
Algorithm analog: Verify the loop invariant holds at entry, during, and after each iteration.
Formal contract :
  ENTRY : acceptance_tests_defined == true (invariant holds before loop)
  DURING: each test run preserves non_goals (no scope creep detected)
  EXIT  : all acceptance tests pass AND forbidden states unreachable (invariant holds at exit)
  CERT  : results.json records per-test pass/fail with input/output witness
Knuth test     : Does the invariant hold after each test iteration?
                 If not, patch the wish precondition, not the test.
```

### Relic Proof = Termination Certificate

```
Aladdin action : Return from the cave with a provable artifact.
Algorithm analog: Provide a termination certificate (decreasing measure / halting proof).
Formal contract :
  MEASURE  : loop_counter decreases by 1 each wish iteration; bounded below by 0
  CERT     : sha256_stable == true (output is reproducible; computation terminates)
  TERMINAL : belt_promotion_receipt.json exists with matching sha256
  PROOF    : "I assert this wish terminates in <=6 iterations because:
              (a) each iteration either advances state or emits BLOCKED/NEED_INFO,
              (b) BLOCKED and NEED_INFO are absorbing states pending human input,
              (c) sha256 stability check provides the observable halting witness."
Knuth test     : Can you run the wish twice and get the same sha256?
                 If not, you do not have a termination certificate; you have a conjecture.
```

---

## Anti-Patterns (Wish-Specific, Formally Specified)

> Knuth: *"Beware of bugs in the above code; I have only proved it correct, not tried it."*
> These anti-patterns are the bugs of wish engineering.

### AP-1: Vague Wish

```
Pattern     : capability = "make it better" / "improve performance" / "do stuff"
Root cause  : No measurable success condition; genie invents policy.
Formal defect: capability ∉ well-formed-sentence set (no termination witness possible)
Detector    : capability matches /(make|improve|enhance|do stuff|better|things)/i
               OR no acceptance test can be derived from capability alone
Consequence : WISH_BLOCKED (forbidden state AMBIGUOUS_WISH triggered)
Correct form: "Add a --verbose flag to the CLI that prints one INFO line per tool call,
               without modifying output schema or exit codes."
```

### AP-2: Missing Non-Goals

```
Pattern     : non_goals field absent or null (undefined — author never declared scope).
Root cause  : Author assumes genie knows what NOT to do. Genie does not.
Formal defect: scope_boundary = undefined → scope_creep probability = 1.0
Detector    : non_goals is null (field absent or null; [] is valid — see null_zero_wish_policy)
Consequence : WISH_NEED_INFO mandatory; do not proceed
Correct form: non_goals: ["does not modify database schema",
                           "does not affect existing CLI flags",
                           "does not add new dependencies"]
              OR if truly no exclusions: non_goals: []  (explicit empty declaration)
```

### AP-3: Unverified Belt

```
Pattern     : Belt advanced from White → Yellow (or higher) without:
               (a) score computed as Decimal (not float),
               (b) sha256_stable == true across two runs,
               (c) belt_promotion_receipt.json written.
Root cause  : "It feels right" substituted for proof.
Formal defect: belt_after > belt_before AND termination_certificate_missing
Detector    : belt promotion event AND (sha256_stable == false OR receipt_missing)
Consequence : UNVERIFIED_BELT_PROMOTION forbidden state triggered; revert belt
Correct form: Run RUNG_65537 verification; only advance belt after receipt is written.
```

### AP-4: JSON as Truth

```
Pattern     : Wish logic, state graph, or identity stored in .json files.
               *.mmd and *.sha256 not produced.
Root cause  : JSON is convenient but not canonically hashable for wish identity.
Formal defect: canonical_source ∉ {*.prime-mermaid.md, *.mmd} → sha256 undefined
Detector    : artifacts list contains only .json entries; no .mmd or .prime-mermaid.md
Consequence : WISH_WITHOUT_PRIME_MERMAID forbidden state triggered; WISH_BLOCKED
Correct form: *.mmd is the canonical source. JSON is derived transport only.
               sha256 is computed over normalized *.mmd bytes (LF endings, no timestamps).
```

### AP-5: Wish Without Tests

```
Pattern     : Wish implementation delivered with "it feels right" as verification.
               No acceptance tests defined or run.
Root cause  : Tests feel expensive; the wish feels obvious.
Formal defect: definition_of_done = ∅ → RUNG_641 not satisfied → no belt possible
Detector    : acceptance_tests field absent OR results.json missing OR tests_run == 0
Consequence : wish stays at WISH_DRAFT; belt = null (not White; never evaluated)
Knuth note  : "White Belt forever" is not the consequence. The consequence is:
               belt = null (wish was never scored; null ≠ White Belt).
               White Belt (score < 8.5) requires evaluation. No evaluation = null score.
Correct form: Define >=2 tests (one positive, one adversarial) before implementation.
               Record results in results.json. Only then does belt scoring begin.
```
