# Scoring Rubric

The 5-criterion binary scorecard used for all community skill, recipe, and swarm agent type reviews.

---

## Overview

Every community submission is scored on 5 binary criteria. Each criterion is worth exactly 1 point. There is no partial credit. The minimum score for a community submission is 5/5.

A score below 5/5 means the submission is returned for revision. The reviewer will specify which criteria failed and what evidence is missing.

This scorecard is also available as an automated check via `recipes/recipe.skill-completeness-audit.md`. Run it before submitting.

---

## The 5 Criteria

### Criterion 1: FSM Present (C1)

**What it checks:** A state machine is defined with explicit states, transitions, and (for skills/swarm types) an input/output alphabet.

**Required evidence:** The file must contain one or more of:
- A `State_Machine:` section with `STATE_SET:` and `TRANSITIONS:` subsections
- A `## State Machine` or `## FSM` heading followed by a states list and a transitions list
- A `STATE_SET:` key anywhere in the YAML frontmatter or body

**Why it matters:** Without a state machine, the skill or agent is a collection of rules with no defined execution order. There is no way to verify completeness or detect invalid states.

**Detection pattern (automated):**
```
grep -i "State_Machine:\|STATE_SET:\|## State Machine\|## FSM"
```

**Pass:** Pattern found at least once in the file.
**Fail:** Pattern not found.

---

### Criterion 2: Forbidden States Defined (C2)

**What it checks:** At least one forbidden state is explicitly named, with a definition. For promoted submissions, each forbidden state must also have a detector predicate and a recovery action.

**Required evidence:** The file must contain one or more of:
- A `FORBIDDEN_STATES:` key with at least one named state
- A `Forbidden_States:` key with at least one named state
- A `forbidden_states:` key with at least one named state

**Why it matters:** Forbidden states are what make a skill fail-closed rather than fail-open. A skill without forbidden states will degrade silently under adversarial or edge-case inputs. "Do the right thing" without a list of forbidden states is not an operational constraint.

**Detection pattern (automated):**
```
grep -i "FORBIDDEN_STATES:\|Forbidden_States:\|forbidden_states:"
```

**Pass:** Pattern found and at least one named state follows.
**Fail:** Pattern not found or present but empty.

---

### Criterion 3: Verification Ladder Present (C3)

**What it checks:** At least one verification rung is declared with its requirements. The rung must be one of: 641 (local correctness), 274177 (stability), 65537 (promotion).

**Required evidence:** The file must contain one or more of:
- A `Verification_Ladder:` section with at least one `RUNG_` entry
- A `RUNG_641:`, `RUNG_274177:`, or `RUNG_65537:` key
- A `verification_rung` or `rung_target` field with a value of 641, 274177, or 65537

**Why it matters:** Without a declared rung target, every PASS claim is ungated. There is no way to check whether the required evidence was collected or whether the claimed level of verification was actually performed.

**Detection pattern (automated):**
```
grep -i "Verification_Ladder:\|RUNG_\|verification_rung\|rung_target"
```

**Pass:** Pattern found and a rung value (641, 274177, or 65537) is associated with it.
**Fail:** Pattern not found or rung value is not one of the three valid primes.

---

### Criterion 4: Null/Zero Handling (C4)

**What it checks:** The skill, recipe, or agent type has an explicit policy on null inputs. The policy must prohibit implicit null-to-zero coercion. It must require explicit null checks in the critical path.

**Required evidence:** The file must contain one or more of:
- A `Null_vs_Zero_Policy:` section
- A `null_handling_rules:` key with at least one rule
- A `NULL_ZERO` reference in the forbidden states
- A `null_check` requirement in a verification rung

**Why it matters:** The most common source of silent behavioral drift is implicit null-to-zero coercion. When a required input is absent, a skill that coerces it to zero will produce results that look valid but are based on garbage inputs. An explicit null policy prevents this class of failure.

**Detection pattern (automated):**
```
grep -i "Null_vs_Zero\|null_handling\|NULL_ZERO\|null_check"
```

**Pass:** Pattern found.
**Fail:** Pattern not found.

---

### Criterion 5: Output Contract Present (C5)

**What it checks:** The required output fields are declared for both the success path (PASS) and the failure path (BLOCKED or NEED_INFO).

**Required evidence:** The file must contain one or more of:
- An `Output_Contract:` section with `required_on_success` and `required_on_failure` subsections
- A `required_on_success:` key listing output fields
- A `structured_refusal_format:` key with required keys for failure outputs

**Why it matters:** Without an output contract, downstream agents cannot reliably parse this skill's output. The output contract is the API boundary between this skill and its callers. Missing contracts cause silent failures when outputs are consumed by swarm chains.

**Detection pattern (automated):**
```
grep -i "Output_Contract:\|output_contract\|required_on_success"
```

**Pass:** Pattern found and both success and failure paths are addressed.
**Fail:** Pattern not found or only one path is addressed.

---

## Scoring Table

Score 1 point for each criterion that passes. Total score is out of 5.

**Template for self-scoring (include this table in your PR):**

| Criterion | Description | Pass (1) / Fail (0) | Evidence (file path + line number or grep pattern) |
|-----------|-------------|---------------------|---------------------------------------------------|
| C1 | FSM present | | |
| C2 | Forbidden states defined | | |
| C3 | Verification ladder | | |
| C4 | Null/zero handling | | |
| C5 | Output contract | | |
| **Total** | | **/5** | |

---

## Minimum Score for Community Submission

**5/5** is required. There are no exceptions.

A submission scoring 4/5 is not "close enough." It is incomplete. The missing criterion is a real gap that will cause real failures in swarm chains. Fix it before submitting.

---

## How Automated Scoring Works

The recipe `recipes/recipe.skill-completeness-audit.md` automates C1-C5 checks for skill files. It:
1. Globs all files in the target directory.
2. Runs grep for each criterion's detection pattern.
3. Records pass/fail per file per criterion.
4. Produces `scratch/skill_audit_scorecard.json` with one entry per file.
5. Flags all files with total < 5.

To run the automated check on your skill file:
```
Load: skills/prime-safety.md + skills/prime-coder.md
Follow: recipes/recipe.skill-completeness-audit.md
```

The automated check is necessary but not sufficient. Automated checks only verify pattern presence. A human reviewer also verifies:
- The FSM is complete (no sink states, no unreachable states).
- Forbidden states have detector predicates and recovery actions (not just names).
- The verification ladder declares a valid rung (641, 274177, or 65537) with explicit requirements.
- The null policy explicitly prohibits coercion (not just mentions null).
- The output contract covers both success and failure paths.

---

## Scoring for Recipes and Swarm Agent Types

The same 5-criterion scorecard applies to recipes and swarm agent types, with adapted detection patterns:

**Recipes:**
- C1: FSM equivalent = `steps:` with ordered steps and explicit conditions
- C2: `forbidden_states:` key with named states
- C3: `rung_target:` field with a value of 641, 274177, or 65537
- C4: Explicit handling of empty results vs. null results in steps or forbidden states
- C5: `verification_checkpoint:` field present and runnable

**Swarm agent types:**
- C1: `## FSM` section with states and transitions
- C2: `## Forbidden States` section with named states
- C3: `rung_default:` in frontmatter and `## Verification Ladder` section
- C4: Null check in FSM (NULL_CHECK state) and `null_checks_performed` in artifact schema
- C5: Artifact schemas with required fields for both PASS and BLOCKED paths

---

*To submit: fill in the scoring table above and include it in your PR description. See `community/CONTRIBUTING.md` for the full submission process.*
