# CLI Notebook Track

These notebooks are executable proof, not slideware.

Theme:
- Bruce Lee dojo loop: Absorb -> Discard -> Add -> Verify
- each notebook is a quest
- each quest should produce belt-gate evidence

## How Wishes And Notebooks Work Together

1. Wish defines contract:
- capability
- non-goals
- acceptance tests
- belt target

2. Notebook executes contract:
- runs commands
- captures outputs
- writes artifacts

3. QA validates execution:
- notebook must run cleanly
- receipts must match wish expectations

## Notebook Index

- `HOW-TO-CLONE-TO-FIRST-RUN.ipynb`
- `HOW-TO-OLLAMA-LOCAL-REMOTE.ipynb`
- `HOW-TO-RECIPE-CONTRACT-BENCHMARK.ipynb`
- `HOW-TO-CONVENTION-DENSITY-BENCHMARK.ipynb`
- `HOW-TO-RIPPLE-LEARNING-BENCHMARK.ipynb`
- `HOW-TO-PLUGIN-SDK-BENCHMARK.ipynb`
- `HOW-TO-BRUCE-LEE-LLM-DOJO.ipynb`
- `HOW-TO-WISH-NOTEBOOK-LOOP.ipynb`
- `HOW-TO-TWIN-ORCHESTRATION.ipynb`
- `HOW-TO-SOFTWARE-5.0-PAPERS.ipynb`
- `HOW-TO-SECRET-SAUCE-INTEGRATION.ipynb`

## Run One Notebook

```bash
python -m nbconvert --execute --to notebook --inplace cli/notebooks/HOW-TO-TWIN-ORCHESTRATION.ipynb
```

## Harsh QA

```bash
./cli/stillwater-cli.sh qa-imo
./cli/stillwater-cli.sh qa-notebooks
./cli/stillwater-cli.sh qa-secret-sauce
```

IMO benchmark protocol details:
- `cli/IMO-CRUSH-WITH-CLI.md`

## Authoring Rules

1. Keep notebooks deterministic where possible.
2. Prefer Prime Mermaid outputs for reasoning state.
3. Record replayable commands.
4. Avoid hidden assumptions; state env/setup requirements explicitly.
