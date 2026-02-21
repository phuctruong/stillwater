# Post-Mainframe AI: Run Anywhere

## Thesis

The default architecture should assume:
- local-first where possible
- remote when needed
- provider portability at runtime

Mainframe-only AI is a dead end for trust, cost control, and resilience.

Stillwater CLI treats model endpoints as pluggable infrastructure, not a fixed cloud dependency.

## Why Now

Market signal: enterprise cost pressure and infrastructure reshoring are increasing.

Referenced signal:
- All-In episode notes/transcript discuss on-prem AI comeback and token budget pressure relative to payroll budgets.
- Source:
  - https://podcasts.happyscribe.com/all-in-with-chamath-jason-sacks-friedberg/debt-spiral-or-new-golden-age-super-bowl-insider-trading-booming-token-budgets-ferrari-s-new-ev
  - https://podcasts.apple.com/us/podcast/e214-debt-spiral-or-new-golden-age-super-bowl/id1502871393?i=1000694819708

Inference:
- If inference spend becomes budget-critical, teams need portability and deterministic fallback paths.

## Implementation In CLI

- Endpoint discovery and routing:
  - `stillwater llm probe-ollama`
  - `stillwater llm models`
  - `stillwater llm set-ollama --auto-url --activate`
- Twin runtime supports local/remote:
  - `stillwater twin --interactive`
  - `stillwater twin "/status"`
- Kernel config and env overrides:
  - `STILLWATER_KERNEL_CONFIG`
  - `STILLWATER_EXTENSION_ROOT`
  - `STILLWATER_SKILL_DIRS`
  - `STILLWATER_RECIPE_DIRS`
  - `STILLWATER_BOOK_DIRS`
  - `STILLWATER_PAPER_DIRS`

## Design Rule

No capability should require one provider to function.
At minimum:
1. CPU-only path for deterministic checks.
2. Mock/offline path for tests.
3. One local and one remote model route.
