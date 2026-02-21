# Recipe Authoring Guide

How to write a new recipe file for Stillwater.

---

## What Is a Recipe vs a Skill?

| | Recipe | Skill |
|---|---|---|
| **Answers** | What to do, and in what order | How to behave while doing it |
| **Format** | Step-by-step workflow with artifacts and rollbacks | Constraint pack (FSM, forbidden states, output contract) |
| **Audience** | An agent executing a workflow | An agent applying behavioral constraints |
| **Example** | `recipes/recipe.skill-completeness-audit.md` | `skills/prime-coder.md` |

A recipe tells you to "run grep on all skill files and record the output." A skill tells you "never claim PASS without a witness line pointing to a file path."

They work together: a recipe is always executed under one or more loaded skills. The skill provides the safety rails; the recipe provides the map.

---

## The 10-Field Canonical Schema (Required Fields)

Every recipe file must have a YAML frontmatter block with these 10 fields:

```yaml
---
id: recipe.<name-with-hyphens>
version: X.Y.Z
title: <Human-readable title>
description: <One sentence: what this recipe does and why>
skill_pack:
  - prime-safety   # Always first
  - <additional skills>
compression_gain_estimate: "<Quantified claim about time or effort saved>"
steps:
  - step: 1
    action: "<Imperative sentence: what to do>"
    artifact: "<What the step produces: path + description>"
    checkpoint: "<Condition that must be true for the step to be considered done>"
    rollback: "<What to do if the step fails or the checkpoint is not met>"
forbidden_states:
  - STATE_NAME: "<One-line definition of the forbidden state>"
verification_checkpoint: "<Command or assertion to run at the end to verify the whole recipe completed correctly>"
rung_target: 641
---
```

None of these fields are optional. A recipe missing any of these fields fails the schema check and is returned for revision.

---

## Field-by-Field Notes

### `id`

Must start with `recipe.` followed by a lowercase hyphenated name. Example: `recipe.skill-completeness-audit`. The ID is used in `community/MANIFEST.json` and in artifact references.

### `version`

Use semantic versioning: `X.Y.Z`. Start at `1.0.0`. Increment patch for corrections, minor for new optional steps, major for breaking changes to the step schema or artifact format.

### `description`

One sentence. It must answer: what does this recipe do, and what outcome does it produce? Bad example: "Runs a scan." Good example: "Runs a 5-criterion binary scorecard across all skill files and produces a machine-parseable scorecard JSON flagging any skill that fails one or more criteria."

### `skill_pack`

Always include `prime-safety` first. It wins all conflicts. Add `prime-coder` if the recipe involves code, file reading, or tool calls. Add `phuc-forecast` if the recipe involves planning or multi-step decision-making.

### `compression_gain_estimate`

This field makes the recipe's value explicit. It must be a specific, falsifiable claim. Examples:
- "Encodes 2 hours of manual swarm auditing into a 15-minute automated sweep."
- "Reduces context needed for onboarding from reading 14 files to following 6 steps."

Do not use vague claims ("saves time"). Estimate order of magnitude.

### `steps`

Each step has exactly 4 sub-fields: `action`, `artifact`, `checkpoint`, `rollback`. All 4 are required.

- `action`: Imperative. Starts with a verb. Describes one atomic action.
- `artifact`: Names the output (file path or structured description). Must be repo-relative or in `scratch/`.
- `checkpoint`: A condition that an agent can test deterministically. Avoid subjective checkpoints ("looks right"). Use testable predicates ("file is non-empty", "JSON parses", "exit code is 0").
- `rollback`: What to do if the checkpoint fails. Must be specific and actionable. "Try again" is not a rollback.

### `forbidden_states`

These are workflow-level forbidden states, not skill-level forbidden states. They describe things that must not happen during this specific recipe's execution. Examples:
- `AUDIT_WITHOUT_CRITERIA`: "Starting the audit loop before all 5 criteria are defined."
- `SILENT_FILE_SKIP`: "Omitting a file from the audit without logging the skip reason."

Each forbidden state needs a one-line definition. If you cannot define it in one line, it is too vague.

### `verification_checkpoint`

A runnable command or assertion that verifies the entire recipe completed correctly, not just the last step. It must be deterministic and reproducible. Examples:
- A `python3 -c "..."` assertion on the output JSON.
- A `grep -c` count that matches an expected value.
- A `sha256sum` comparison.

### `rung_target`

Declare the verification rung this recipe is designed to satisfy. Most recipes target rung 641 (local correctness). If the recipe includes seed sweeps or replay checks, target 274177. If it gates on adversarial or security checks, target 65537.

---

## How to Estimate Compression Gain

Compression gain is the ratio of time (or effort) saved by running the recipe versus doing the same work manually.

**Method:**
1. Estimate how long the manual process takes in wall-clock time (be honest).
2. Estimate how long following the recipe takes.
3. Express the ratio: "Encodes X hours of manual work into Y minutes."

**Common failure:** Estimating too aggressively without basis. If you have not actually run the manual process, use a conservative estimate and flag it as an estimate.

**Common mistake:** Omitting the estimate entirely. The `compression_gain_estimate` field exists specifically to prevent recipes from being added without a clear articulated value.

---

## Step-by-Step: Write a New Recipe

### Step 1: Identify the Workflow

What is the recurring task you are encoding? Write it in one sentence. If you cannot write it in one sentence, the scope is too large. Split it into two recipes.

Good candidates for recipes:
- Any task you have done manually more than twice.
- Any task with a clear artifact output that can be checksummed.
- Any task where the order of steps matters (if you skip a step, the result is wrong).

Bad candidates for recipes:
- Tasks that require human judgment at every step (these belong in a swarm design, not a recipe).
- Tasks that change every time they are run (recipes must be repeatable).

### Step 2: Extract the Steps

Write out the steps in order. For each step, ask:
- What is the single action?
- What does the step produce?
- How do I know it worked?
- What do I do if it did not work?

If a step has no artifact, it is probably a sub-step. Merge it into the previous step or the next step.

If a step has no rollback, it is probably irreversible. Warn the user in the step description and add a checkpoint that confirms the action is safe before taking it.

### Step 3: Identify Forbidden States

Read through your steps and ask: what could go wrong in a way that is hard to detect? These become your forbidden states.

Look for:
- Silent omissions (a file is skipped without logging).
- Premature completions (reporting done before all steps are finished).
- State confusion (treating an empty result as an error vs. a valid empty set).

### Step 4: Set the Rung Target

Match the rung target to the verification strength of your recipe:
- 641: the recipe produces correct output on a single run with a single input.
- 274177: the recipe produces stable output across multiple seeds or inputs.
- 65537: the recipe gates on adversarial inputs, security scans, or behavioral hash verification.

Most new recipes start at 641.

---

## Template (Canonical Recipe Schema with Placeholder Values)

Copy this template and replace every placeholder in angle brackets.

```yaml
---
id: recipe.<your-recipe-name>
version: 1.0.0
title: <Human-Readable Title>
description: <One sentence describing what this recipe does and what it produces.>
skill_pack:
  - prime-safety
  - prime-coder
compression_gain_estimate: "<Estimated time savings, e.g., 'Encodes 1 hour of manual work into a 10-minute automated sweep'>"
steps:
  - step: 1
    action: "<Imperative verb phrase describing the first action>"
    artifact: "<repo-relative path or scratch/ path> -- <description of what it contains>"
    checkpoint: "<Testable predicate: file exists AND is non-empty AND parses correctly>"
    rollback: "<Specific action to take if checkpoint fails>"
  - step: 2
    action: "<Imperative verb phrase describing the second action>"
    artifact: "<repo-relative path or scratch/ path> -- <description>"
    checkpoint: "<Testable predicate>"
    rollback: "<Specific rollback action>"
  - step: 3
    action: "<Final step: aggregate results and emit summary>"
    artifact: "<summary artifact path> -- <description>"
    checkpoint: "<Summary artifact is present, parses correctly, and all required fields are populated>"
    rollback: "<If summary fails, re-run individual step artifacts and merge manually>"
forbidden_states:
  - PREMATURE_COMPLETION: "Emitting a summary artifact before all steps are complete."
  - SILENT_SKIP: "Skipping an item without logging the skip reason."
  - NULL_ZERO_CONFUSION: "Treating a result of 0 items as null/error rather than a valid empty set."
verification_checkpoint: "Run: python3 -c \"import json; data = json.load(open('<summary artifact path>')); assert len(data) > 0\" -- must exit 0."
rung_target: 641
---

# Recipe: <Human-Readable Title>

## Purpose

<One paragraph: what problem does this recipe solve, why does it exist, and when should it be used.>

## When to Use

- <Bullet: specific trigger condition 1>
- <Bullet: specific trigger condition 2>

## Output Artifacts

- `<artifact path>` -- <description>

## Notes

- <Any important constraint, caveat, or non-obvious behavior>
```

---

## Common Mistakes

**Mistake 1: No compression estimate.**
The `compression_gain_estimate` field is required. If the recipe saves no measurable time or effort, it should not be a recipe.

**Mistake 2: Missing forbidden states.**
Forbidden states catch workflow failures that are hard to detect. A recipe without forbidden states will fail silently in edge cases.

**Mistake 3: No rollback in steps.**
"Try again" is not a rollback. A rollback must specify exactly what to do: revert a file, widen a glob, emit a specific error, or stop and emit `NEED_INFO`.

**Mistake 4: Subjective checkpoints.**
"Looks reasonable" is not a checkpoint. Write a machine-testable predicate: a command that exits 0 on success and non-zero on failure.

**Mistake 5: Steps with no artifacts.**
If a step produces no artifact, it cannot be verified independently. Combine it with an adjacent step or make the artifact explicit (even if it is a log file or a flag file).

**Mistake 6: Rung target not declared.**
The rung target must be declared in the frontmatter. An undeclared rung target means the recipe makes an implicit claim that cannot be checked.

---

*Next steps: score your recipe using `community/SCORING-RUBRIC.md` (adapted for recipes), then submit via `community/CONTRIBUTING.md`.*
