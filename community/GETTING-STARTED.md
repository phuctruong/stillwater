# Getting Started with Stillwater

> "Absorb what is useful, discard what is useless, and add what is specifically your own." — Bruce Lee

> "Be water, my friend." — Bruce Lee

This document is your entry point. No prior context required. Estimated read time: under 10 minutes.

---

## What is Stillwater?

Stillwater is an open-source AI verification framework: a set of prompt-loadable skills, step-by-step recipes, and multi-agent swarm designs that make LLM outputs more reliable, honest, and reproducible. It is not a platform that replaces your tools. It is a discipline layer that sits on top of whatever LLM client you already use (Claude Code, the API, OpenClaw, or a local model). The core idea is simple: before you trust an AI output, you need a receipt. Stillwater gives you the protocol for getting that receipt.

---

## The Three Layers

Stillwater is organized into three layers that build on each other.

### Layer 1: Skills (`skills/`)

**What:** Prompt-loadable constraint packs. Each skill is a structured YAML/markdown file that, when pasted into an LLM session, changes how the model behaves.

**When to use:** Load skills when you want the model to follow specific rules -- like always requiring a red/green test gate before patching a bug, or always producing machine-parseable evidence bundles.

**Key skills:**
- `skills/prime-safety.md` -- tool safety + authority ordering (always load first)
- `skills/prime-coder.md` -- coding discipline, red/green gate, evidence contract
- `skills/phuc-forecast.md` -- decision loop: DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY
- `skills/phuc-orchestration.md` -- multi-agent dispatch + context anti-rot

**Rule:** Load the whole skill file. Do not summarize or compress it. Compressed skills drift.

### Layer 2: Recipes (`recipes/`)

**What:** Step-by-step workflow files with explicit artifact schemas, forbidden states, rollback steps, and verification checkpoints. A recipe tells you *what to do* and in what order; a skill tells you *how to behave* while doing it.

**When to use:** Run a recipe when you have a recurring workflow that needs to be repeatable and auditable -- like auditing all skills for completeness, or running a benchmark sweep.

**Example:** `recipes/recipe.skill-completeness-audit.md` runs a 5-criterion binary scorecard across all skill files.

### Layer 3: Swarm Agent Types (`swarms/`)

**What:** Typed agent definitions. Each file in `swarms/` defines a specific agent role -- its persona, its skill pack, the artifacts it must produce, its FSM (state machine), and its forbidden states.

**When to use:** When a task is too large or complex for a single LLM session, you decompose it into a swarm chain. Each agent in the chain receives a specific role definition from `swarms/`, operates within its constraints, and hands off artifacts to the next agent.

**Available agent types:**

| File | Agent Role | Persona |
|------|-----------|---------|
| `swarms/scout.md` | Map codebase, identify gaps | Ken Thompson |
| `swarms/forecaster.md` | Plan and premortem | Grace Hopper |
| `swarms/judge.md` | Score and approve artifacts | Ada Lovelace |
| `swarms/coder.md` | Write patches with evidence | Donald Knuth |
| `swarms/skeptic.md` | Challenge and stress-test | Alan Turing |
| `swarms/mathematician.md` | Exact arithmetic and proofs | Emmy Noether |
| `swarms/writer.md` | Write clear human-readable docs | Richard Feynman |
| `swarms/janitor.md` | Clean up and simplify | Edsger Dijkstra |
| `swarms/security-auditor.md` | Security scan and exploit repro | Bruce Schneier |
| `swarms/context-manager.md` | Context hygiene and CNF capsules | Barbara Liskov |

---

## How to Use a Skill

1. Open your LLM session (Claude, the API, any client).
2. Paste the full content of the skill file into the system prompt or the beginning of the conversation.
3. Issue your task.

The model will now follow the constraints in the skill file. Do not paraphrase or summarize the skill -- the invariants are in the structure.

**Example (loading prime-coder for a bug fix):**
```
[Paste full content of skills/prime-coder.md here]

Task: The function `parse_config` in src/config.py crashes when given a null input. Fix it.
```

The skill will enforce that you write a failing test first (RED gate), confirm the failure, apply the fix, and confirm the test now passes (GREEN gate) before declaring PASS.

---

## How to Use a Recipe

Recipes are workflows you run step by step.

1. Open `recipes/<recipe-name>.md`.
2. Read the frontmatter (the YAML block at the top) to understand the required skill pack, steps, forbidden states, and verification checkpoint.
3. Load the required skill pack into your LLM session.
4. Follow the steps in order. Each step has an expected artifact, a checkpoint condition, and a rollback action if the step fails.
5. Run the verification checkpoint at the end to confirm the recipe completed correctly.

**Example (running the skill completeness audit):**
```
Load: skills/prime-safety.md + skills/prime-coder.md

Then follow steps 1-8 in recipes/recipe.skill-completeness-audit.md.
Expected output: scratch/skill_audit_scorecard.json with one entry per skill file.
```

---

## How to Use a Swarm Agent Type

A swarm agent type defines a *role*. To use one:

1. Open `swarms/<agent-type>.md`.
2. Read the Role section and Expected Artifacts section.
3. In a new LLM sub-session (separate from your main session), paste:
   - The required skill pack files (listed in the frontmatter)
   - The full content of the swarm agent type file
   - The CNF capsule (Context Normal Form: task statement, constraints, repo root, prior artifacts as links)
4. The agent will operate within its FSM, produce its required artifacts, and exit with a stop reason.

The main session acts as dispatcher. Sub-agent sessions carry their own full context. This prevents context rot.

---

## Where to Find Everything (Directory Map)

```
stillwater/
  skills/           Prompt-loadable skill packs
  recipes/          Step-by-step workflow definitions
  swarms/           Typed swarm agent definitions
  papers/           Theory papers with receipts (papers/00-index.md is the index)
  community/        This directory -- contribution guides and registry
    GETTING-STARTED.md       You are here
    SKILL-AUTHORING-GUIDE.md How to write a new skill
    RECIPE-AUTHORING-GUIDE.md How to write a new recipe
    SWARM-DESIGN-GUIDE.md    How to design a new swarm agent type
    SCORING-RUBRIC.md        The 5-criterion binary scorecard
    CONTRIBUTING.md          Submission and review process
    MANIFEST.json            Community contribution registry
  skills/           Prompt-loadable skill packs (includes the 4 foundational always-on skills)
  artifacts/        Cached run artifacts
  scratch/          Git-ignored scratch space
  README.md         Project overview
```

---

## How to Contribute

Read `community/CONTRIBUTING.md` for the full submission process.

Short version:
- Skills and swarm agent types must score 5/5 on the binary scorecard (`community/SCORING-RUBRIC.md`).
- Include your self-scored evidence table in the PR.
- Review is performed by a Scout + Judge + Skeptic swarm chain.
- Register your contribution in `community/MANIFEST.json`.

---

## Quick Example: Run the Swarm Pipeline Recipe

The fastest way to see the whole system in action is to run a Scout + Judge cycle on a small task.

**Step 1:** Load the skill pack.
```
Paste skills/prime-safety.md into a new session.
Paste skills/prime-coder.md into the same session.
```

**Step 2:** Assign the Scout role.
```
Paste swarms/scout.md into the session.

CNF capsule:
TASK: List all skill files in skills/ and score each for completeness.
CONSTRAINTS: max_files=12, max_tool_calls=40
REPO_ROOT: .
FAILING_TESTS: NONE
PRIOR_ARTIFACTS: NONE
SKILL_PACK: [prime-safety, prime-coder]
BUDGET: {max_files: 12, max_witness_lines: 200, max_tool_calls: 40}
```

**Step 3:** The Scout produces `SCOUT_REPORT.json` and `completeness_matrix.json`.

**Step 4:** Open a new session. Load the Judge role (`swarms/judge.md`). Feed it the Scout artifacts. The Judge scores them and produces a `JUDGE_REPORT.json` with a pass/fail verdict.

**Step 5:** Review the evidence. If the verdict is PASS with evidence, you have a receipt.

That is Stillwater. Not trust, but receipts.

---

*Next steps: read `community/SKILL-AUTHORING-GUIDE.md` to write your first skill, or read `papers/00-index.md` for the theory behind the tower.*

---

## Author

**Phuc Vinh Truong** — Coder, entrepreneur, theorist, writer.

| Link | URL |
|---|---|
| Personal site | https://www.phuc.net |
| IF Theory (physics) | https://github.com/phuctruong/if |
| PZIP (compression) | https://www.pzip.net |
| SolaceAGI (persistent AI) | https://www.solaceagi.com |
| Support this work | https://ko-fi.com/phucnet |
| Contact | phuc@phuc.net |
| GitHub | https://github.com/phuctruong |
| Stillwater repo | https://github.com/phuctruong/stillwater |

*Building open, reproducible, verifiable AI infrastructure — "Linux of AGI."*
