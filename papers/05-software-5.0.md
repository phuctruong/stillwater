# Software 5.0: Skills, Recipes, And Verification As An Open System

## Abstract

Most AI productivity today is paid by the token: you rent the same reasoning over and over, and you cannot audit what happened after the chat ends. Software 5.0 is a different framing:

- **Skills** are versioned operational constraints (how work is performed).
- **Recipes** are replayable workflows (what steps are performed).
- **Verification artifacts** are the output contract (why you can trust the result).

This paper rebuilds those ideas from first principles and maps them to the concrete structure of this repository: `skills/*.md`, the notebooks in the root, the solvers in `oolong/src`, `imo/src`, `swe/src`, and the evidence/verification conventions they use.

## 1. From First Principles: What "Intelligence" Must Do

Any useful "intelligence" system in a production setting must reliably:

1. **Represent the task** (what is requested, constraints, definition of done).
2. **Choose actions** (plan a sequence of bounded steps).
3. **Execute actions** (generate artifacts, run tools, produce code).
4. **Verify outcomes** (demonstrate correctness, safety, and replayability).
5. **Evolve without forgetting** (add capability without breaking old behaviors).

LLM chat by itself is strong at (1) and (2) in prose form, sometimes good at (3), and weak at (4) and (5) unless the system forces it.

Software 5.0 is a practical packaging for (4) and (5).

## 2. Skills: Operational Controls (The "How")

A skill is a versioned constraint bundle that:

- enforces a state machine (what phases exist)
- defines forbidden states (what is never allowed)
- specifies evidence requirements (what must be produced)
- sets fail-closed defaults (how to behave with missing assets)

In this repository, skills are plain Markdown, loadable as prompt layers:

- `skills/prime-coder.md`: coding reliability, red/green gate, evidence contract
- `skills/prime-math.md`: exact compute discipline and witness requirements
- `skills/prime-safety.md`: tool safety envelope, prompt injection firewall
- `skills/phuc-forecast.md`: planning loop (DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY)
- `skills/phuc-swarms.md`: multi-agent orchestration contracts
- `skills/phuc-context.md`: context hygiene and asset policy

### 2.1 Why Plain Markdown Works

Markdown is:

- portable (works in any editor, repo, or chat system)
- diffable (reviewable like code)
- versionable (git history + tags)

The point is not the format; the point is **reviewability**.

## 3. Recipes: Replayable Workflows (The "What")

A recipe is the executable shape of work:

- the sequence of actions
- the inputs required
- the outputs produced
- the checks that must pass

In this repository, recipes appear as:

- notebooks (end-to-end executions with visible steps)
- solver scripts (deterministic pipelines)
- unit tests (phase contracts)

The goal is to make each workflow replayable for third parties.

## 4. Verification Artifacts: Trust You Can Audit (The "Why")

If an OSS project claims "this works," reviewers need:

- commands that were run
- test outputs
- constraints and assumptions
- hashes of outputs for drift detection

This is why the `prime-coder` skill insists on evidence artifacts. The details matter: without them, results are not peer-reviewable.

## 5. Mapping To The Root Notebooks

The root notebooks are the public "recipes" for major claims:

- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`
  - concept: counter bypass (LLM classifies, CPU enumerates)
  - evidence: deterministic solver + ladder framing
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
  - concept: exact compute / lemma libraries + verification ladder
  - evidence: runnable solver + rung checks
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
  - concept: swarm spine + fail-closed prompting + phase artifacts
  - evidence: unit tests for phases
- `HOW-TO-CRUSH-SWE-BENCHMARK.md`
  - concept: patch generation pipeline + wrapper + progress tracking
  - evidence: batch runs, logs, result summaries (this notebook is treated separately for harsh QA)

## 6. Mapping To The Code

Concrete implementations live here:

- OOLONG (repo-local demo): `oolong/src/oolong_solver.py`, `oolong/src/solve-oolong.py`
  - optional (external tooling): `oolong/src/oolong_solver_real.py`
- IMO: `imo/src/imo_2024_complete_solver.py`, `imo/src/imo_2024_solver_proper.py`
- SWE: `swe/src/swe_solver_real.py`, wrapper in `src/claude_code_wrapper.py`
- Orchestration: `tests/phuc_orchestration/` plus the orchestration notebook

## 7. What This Enables For Open Source

With skills + recipes + artifacts:

- reviewers can reproduce results without trusting a maintainer
- regressions are easier to detect (artifact hashes)
- improvements become additive: new skills/recipes do not require rewriting the system

Without them:

- results regress silently
- claims become marketing
- "works on my machine" dominates

## 8. Limitations And Honest Claims

Software 5.0 is a methodology. It does not automatically create:

- complete test suites
- explicit claim hygiene for every claim (what is verified vs. hypothesis)
- security guarantees beyond the evidence you actually run

The system is only as strong as its verification artifacts.

## 9. Practical Checklist For Contributors

When you add a new capability:

1. Add or update a skill (operational constraints).
2. Add a recipe (notebook/script/tests).
3. Add verification artifacts (commands, outputs, hashes).
4. Update `papers/00-index.md` with accurate links and reproduction steps.
