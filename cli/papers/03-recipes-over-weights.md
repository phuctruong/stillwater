# Recipes Over Weights

## Thesis

Weights are powerful but opaque.  
Recipes are inspectable, testable, and replayable.

Stillwater CLI treats recipes as the primary externalized reasoning layer.

## Core Principle

LLM proposes. CPU verifies. Recipes encode.

This aligns with:
- root `papers/05-software-5.0.md`
- `prime-wishes` Law 17 (learning externalized to persist)
- `prime-mermaid` CLI plan ("infrastructure > weights")

## Prime Mermaid Policy

Canonical source of reasoning should be Prime Mermaid files:
- `*.prime-mermaid.md`
- deterministic linting and receipt hashing

CLI support:
- `stillwater recipe list`
- `stillwater recipe add <name>`
- `stillwater recipe lint --prime-mermaid-only`
- `stillwater stack run`
- `stillwater replay <run_id>`

## Software 5.0 Recipe Contract (Adapted)

Each serious workflow should define:
1. Identity (id/version/hash)
2. Inputs and outputs (typed)
3. Steps (CPU/Tool/LLM/Gate DAG)
4. Policy (budgets/permissions/timeouts)
5. Verification criteria
6. Trace artifacts (hashes, logs, proofs)

## Maturity Metric

Convention Density:
- deterministic_step_ratio x test_pass_rate
- trend target: exploratory -> maturing -> crystallizing -> production
