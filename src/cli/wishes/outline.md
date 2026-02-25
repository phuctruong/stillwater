# CLI Wishes Outline (Notebook-First)

Date: 2026-02-19  
Scope: Build and evolve Stillwater CLI using wish notebooks and Prime Mermaid ripples.

## Why this exists

This folder makes the CLI a concrete example of the Stillwater wish process:
- code is the runtime kernel,
- ripples encode behavior and conventions,
- wish notebooks drive change with tests and evidence.

Gamification is a core concept here:
- every wish is a quest,
- every quest has belt progression,
- belt promotion requires proof artifacts.

## Levels

1. `L0` quick wish note: one-page markdown capability + non-goals.
2. `L1` wish notebook: default path for CLI features.
3. `L2` full prime wish: only for high-risk/public benchmark/security paths.

## Required gamification block per wish

Each wish MUST declare:
1. quest title
2. current belt
3. target belt
4. promotion gate criteria

## Build workflow for each CLI feature

1. Define wish:
- one sentence capability
- explicit non-goals
- fail-closed ambiguity policy

2. Externalize state:
- write canonical Prime Mermaid graph
- list forbidden states
- define artifact paths

3. Specify tests:
- acceptance tests with explicit pass/fail
- adversarial tests when risk is medium/high
- determinism rerun check

4. Implement minimal code:
- patch only required modules
- keep interface stable
- avoid hidden state additions

5. Verify and publish artifacts:
- emit `.mmd` + `.sha256` + `results.json`
- add replay command
- summarize evidence in markdown

6. Promote:
- if reusable, move to examples/template
- if repeated failure occurs, escalate to `L2`

## Conventions for this folder

- `wish-*.md`: short intent docs (`L0`)
- `wish-*.ipynb`: executable wish notebooks (`L1`)
- `artifacts/<wish_id>/`: emitted evidence bundle
- canonical logic always in Prime Mermaid, never YAML/JSON as source-of-truth

## Current CLI as an example

These existing capabilities map naturally to wish notebooks:

1. Model connectivity and fallback:
- `stillwater llm status`
- `stillwater llm probe-ollama`
- `stillwater llm models`
- `stillwater llm set-ollama --auto-url --activate`

2. Skills benchmark evidence path:
- `stillwater skills-ab --backend auto`

3. Notebook proof track:
- `notebooks/HOW-TO-CLONE-TO-FIRST-RUN.ipynb`
- `notebooks/HOW-TO-OLLAMA-LOCAL-REMOTE.ipynb`
- `notebooks/HOW-TO-RECIPE-CONTRACT-BENCHMARK.ipynb`
- `notebooks/HOW-TO-RIPPLE-LEARNING-BENCHMARK.ipynb`
- `notebooks/HOW-TO-BRUCE-LEE-LLM-DOJO.ipynb`
- `notebooks/HOW-TO-WISH-NOTEBOOK-LOOP.ipynb`
- `notebooks/HOW-TO-TWIN-ORCHESTRATION.ipynb`

## Next wishlist (recommended)

1. `wish.cli.stack.run.v1`: full-stack command orchestration.
2. `wish.cli.recipe.lint.v1`: enforce Prime Mermaid-only reasoning artifacts.
3. `wish.cli.replay.v1`: universal replay for all run classes.
4. `wish.cli.learn.loop.v1`: propose/apply ripple learning with receipts.
5. `wish.cli.oolong.verify.v1`: strict CPU-only aggregation verifier.
6. `wish.cli.notebook.qa.v1`: run and gate all HOW-TO notebooks in one pass.
7. `wish.cli.twin.orchestration.v1`: natural-language CPU+LLM orchestration with receipts.
