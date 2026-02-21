# Skill Authoring Guide

How to write a new skill file for Stillwater.

---

## What Makes a Good Skill (5-Criteria Scorecard)

A skill file is only useful if it can be mechanically audited. Every community-submitted skill is scored on 5 binary criteria. Score 5/5 to pass. Score below 5/5 and the skill is returned for revision.

| # | Criterion | What It Means |
|---|-----------|---------------|
| C1 | FSM present | A state machine is defined with explicit states, transitions, and input/output alphabets. |
| C2 | Forbidden states defined | At least one forbidden state is named, with a detector predicate and a recovery action. |
| C3 | Verification ladder | At least one rung (641, 274177, or 65537) is declared with explicit requirements. |
| C4 | Null/zero handling | The skill has an explicit null check policy and prohibits implicit null-to-zero coercion. |
| C5 | Output contract | Required output fields are declared for both PASS and BLOCKED/NEED_INFO paths. |

See `community/SCORING-RUBRIC.md` for the full scorecard template.

---

## Skill File Structure

A valid skill file has the following sections, in this order:

### 1. Header (YAML frontmatter)

```yaml
SKILL_NAME:
  version: X.Y.Z
  authority: 65537
  status: DRAFT | SEALED | FINAL
```

The `authority` field uses the prime number 65537 as a sentinel. It signals that this is a Stillwater-compliant skill file. Do not change this value.

### 2. FSM (State Machine)

The FSM is the heart of the skill. It defines:
- `STATE_SET`: All valid states the skill can be in.
- `INPUT_ALPHABET`: The set of valid inputs.
- `OUTPUT_ALPHABET`: The set of valid outputs.
- `TRANSITIONS`: A deterministic map from (state, input) to next state.
- `FORBIDDEN_STATES`: States that must never be entered (defined separately but referenced here).

Every branch in the transition table must be decidable from observable inputs. If a branch predicate cannot be decided, the skill must fail closed to `EXIT_NEED_INFO` or a stricter gate.

### 3. Forbidden States

Each forbidden state must have:
- A name (in `SCREAMING_SNAKE_CASE`).
- A one-line definition of what the state means.
- A detector: how to observe that this state has been entered.
- A recovery action: what to do immediately upon detection.

Example:
```yaml
FORBIDDEN_STATES:
  - UNWITNESSED_PASS:
      definition: "Claiming PASS without executable evidence."
      detector: "status == PASS AND evidence_bundle is empty"
      recovery: "Revert to EVIDENCE_BUILD state; do not emit PASS."
```

### 4. Verification Ladder

Declare at least one rung:

```yaml
Verification_Ladder:
  rungs:
    RUNG_641:
      meaning: "Local correctness claim"
      requires:
        - <list requirements>
    RUNG_274177:
      meaning: "Stability claim"
      requires:
        - RUNG_641
        - <additional requirements>
    RUNG_65537:
      meaning: "Promotion claim"
      requires:
        - RUNG_274177
        - <additional requirements>
```

The rung number is a prime. Do not invent new rung numbers. Use 641, 274177, or 65537.

### 5. Null/Zero Policy

```yaml
Null_vs_Zero_Policy:
  null_handling_rules:
    - explicit_null_check_required: true
    - no_implicit_defaults: true
    - no_null_as_zero_coercion: true
    - fail_closed_on_null_in_critical_path: true
```

This section is not optional. A skill without an explicit null policy will coerce nulls silently, which causes incorrect behavior at boundaries.

### 6. Output Contract

```yaml
Output_Contract:
  hard_gates:
    - if_required_evidence_missing: "status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE"
  required_on_success:
    status: PASS
    include:
      - <list required fields>
  required_on_failure:
    status: NEED_INFO_or_BLOCKED
    include:
      - stop_reason
      - what_ran_and_failed
      - next_actions
```

The output contract is what downstream agents rely on. Be precise. Missing fields in the contract cause silent failures in swarm chains.

---

## Step-by-Step: Write a New Skill

### Step 1: Write the FSM First

Before writing any other section, define your states. Ask:
- What are the distinct phases of this skill's operation?
- What can go wrong at each phase?
- Where does the skill exit (PASS, NEED_INFO, BLOCKED)?

Draw the states and transitions on paper or in a text sketch before coding anything.

Checkpoint: The FSM must have at least one exit state. It must have no sink states (states with no exit transition). Every state must be reachable from INIT.

### Step 2: Define Forbidden States

After the FSM is drawn, identify the states you do NOT want to be in. These are often the "shortcut" states -- what happens if the skill skips a gate, accepts an unverified claim, or silently ignores an error.

Common forbidden states for skills:
- `UNWITNESSED_PASS` -- claiming PASS without artifact evidence
- `SILENT_RELAXATION` -- weakening a constraint without logging the change
- `IMPLICIT_NULL_DEFAULT` -- using a default value when the input is null
- `FLOAT_IN_VERIFICATION_PATH` -- using floating-point comparison in an evidence check

Each forbidden state needs a detector and a recovery. Vague forbidden states (no detector) are not enforced.

### Step 3: Define the Verification Ladder

Decide the minimum rung this skill targets:
- 641 for a local correctness claim (most skills start here)
- 274177 for a stability claim (if the skill runs iterative or probabilistic methods)
- 65537 for a promotion claim (if the skill gates on adversarial sweeps or security)

State the rung target in the header and in the ladder section. Do not claim a higher rung than your requirements support.

### Step 4: Write the Null/Zero Policy

Copy the minimal policy from the template below. Extend it if your skill has specific boundary cases (e.g., if your skill processes lists and must distinguish "empty list" from "null list").

### Step 5: Write the Output Contract

List every field that a downstream agent or human reviewer would need in order to verify your skill's output. For PASS: what evidence exists? For BLOCKED/NEED_INFO: what is missing and what are the next actions?

---

## Common Mistakes (From Swarm Run Lessons)

**Mistake 1: FSM with no forbidden states.**
A state machine with no forbidden states is just a flowchart. Forbidden states are what make the FSM fail-closed. Without them, the skill degrades silently.

**Mistake 2: Forbidden states with no detectors.**
A forbidden state with no detector is aspirational, not operational. Write the detector predicate first; then the recovery action.

**Mistake 3: Null policy that says "use None."**
Python's `None` is not a null policy. The policy must specify: what happens when a required input is absent? Does the skill halt? Emit NEED_INFO? The policy must be declarative and machine-checkable.

**Mistake 4: Output contract with "see the docs."**
The output contract must be inline. Downstream agents do not read docs. They parse the contract.

**Mistake 5: Rung target not declared.**
Every skill must declare a rung target before claiming PASS. If the target is not declared, the PASS is ungated and unreliable.

**Mistake 6: Compressing an existing skill and resubmitting.**
If you load an existing skill and summarize it into a shorter version, you lose the invariants. The compressed version will drift from the original under adversarial inputs. Always write new skills from scratch against the template.

---

## Self-Audit Checklist

Before submitting your skill, run this checklist:

```
[ ] C1: Does the file contain a STATE_SET with at least 3 states including an exit state?
[ ] C1: Does the file contain a TRANSITIONS section mapping (state, input) -> next state?
[ ] C2: Does the file contain FORBIDDEN_STATES with at least one named state?
[ ] C2: Does each forbidden state have a detector predicate and a recovery action?
[ ] C3: Does the file contain a Verification_Ladder section?
[ ] C3: Is at least one rung (641, 274177, or 65537) declared with explicit requirements?
[ ] C4: Does the file contain a Null_vs_Zero_Policy or equivalent?
[ ] C4: Does the policy explicitly prohibit null-to-zero coercion?
[ ] C5: Does the file contain an Output_Contract section?
[ ] C5: Are required fields listed for both PASS and BLOCKED/NEED_INFO paths?
[ ] General: No absolute paths anywhere in the file?
[ ] General: Authority field set to 65537?
[ ] General: Version string in X.Y.Z format?
```

Score 1 point per binary criterion (C1-C5). Pass threshold: 5/5.

---

## Template (Minimal Valid Skill Structure)

Copy this template and fill in the placeholders.

```yaml
MY_SKILL_NAME:
  version: 1.0.0
  authority: 65537
  status: DRAFT

  # ------------------------------------------------------------
  # A) What This Skill Does (one paragraph)
  # ------------------------------------------------------------
  # <describe the skill's purpose>

  # ------------------------------------------------------------
  # B) FSM
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE_TASK
      - NULL_CHECK
      - # <add domain-specific states here>
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    INPUT_ALPHABET:
      - TASK_REQUEST
      - TOOL_OUTPUT
      # <add domain-specific inputs>

    OUTPUT_ALPHABET:
      - RESULT_ARTIFACT
      - STRUCTURED_REFUSAL
      # <add domain-specific outputs>

    TRANSITIONS:
      - INIT -> INTAKE_TASK: on TASK_REQUEST
      - INTAKE_TASK -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if required_inputs_missing
      - NULL_CHECK -> # <next state>: if inputs_defined
      # <add transitions>
      - # <final state> -> EXIT_PASS: if evidence_complete
      - # <final state> -> EXIT_BLOCKED: otherwise

    FORBIDDEN_STATES:
      - UNWITNESSED_PASS:
          definition: "Claiming PASS without artifact evidence."
          detector: "status == PASS AND evidence is empty"
          recovery: "Do not emit PASS; revert to evidence-building state."
      # <add skill-specific forbidden states>

  # ------------------------------------------------------------
  # C) Null/Zero Policy
  # ------------------------------------------------------------
  Null_vs_Zero_Policy:
    null_handling_rules:
      - explicit_null_check_required: true
      - no_implicit_defaults: true
      - no_null_as_zero_coercion: true
      - fail_closed_on_null_in_critical_path: true

  # ------------------------------------------------------------
  # D) Verification Ladder
  # ------------------------------------------------------------
  Verification_Ladder:
    rung_target: 641
    rungs:
      RUNG_641:
        meaning: "Local correctness claim"
        requires:
          - null_check_performed
          - no_forbidden_states_entered
          - output_contract_fields_present

  # ------------------------------------------------------------
  # E) Output Contract
  # ------------------------------------------------------------
  Output_Contract:
    hard_gates:
      - if_required_evidence_missing: "status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE"
    required_on_success:
      status: PASS
      include:
        - result_artifact_path
        - stop_reason
        - verification_rung_achieved
    required_on_failure:
      status: NEED_INFO_or_BLOCKED
      include:
        - stop_reason
        - missing_fields_or_contradictions
        - what_ran_and_failed
        - next_actions
```

---

*Next steps: score your skill using `community/SCORING-RUBRIC.md`, then submit via the process in `community/CONTRIBUTING.md`.*
