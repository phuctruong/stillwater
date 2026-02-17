# Contributing

This repo is documentation-first: notebooks and papers should be runnable, reviewable, and honest about what is verified vs. hypothesized.

## Ground Rules

- Prefer small PRs.
- Avoid machine-specific paths in committed artifacts.
- If you add a numeric claim, link to a runnable script/notebook that reproduces it.
- If a notebook requires external services, keep an offline demo path that still executes cleanly.

## Running Tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

Integration tests are opt-in:
```bash
STILLWATER_RUN_INTEGRATION_TESTS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

## Notebook Hygiene

- Before committing, execute notebooks and ensure there are no error outputs.
- Prefer deterministic, short-running demo mode by default.

