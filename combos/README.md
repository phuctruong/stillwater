# Stillwater Canon Combos

Public WISH + RECIPE pairs for common software engineering tasks.
Each combo = a WISH (contract) + RECIPE (L1-L5 node graph implementation).

## Available Combos

| Combo | What | WISH ID |
|---|---|---|
| plan.md | Plan→Execute governance split (zero side-effects in plan mode) | wish_plan_execute_split |
| bugfix.md | Bugfix→PR with Kent Red→Green mandatory proof | wish_bugfix_pr_red_green |
| run-test.md | Deterministic Run+Test harness with IO boundary | wish_run_test_harness |
| ci-triage-logs.md | CI failure triage: logs→signature→repro→fix plan | wish_ci_triage |
| review-security-scan-veto.md | Patch review with security tooling veto gate | wish_review_security_veto |
| dependency-bump.md | Safe dependency upgrade with evidence gate | wish_dependency_bump |
| prime-mermaid-meta-recipe.md | FSM→Mermaid→code meta-recipe | wish_prime_mermaid_meta |

## Trade Secret (not included)
- recipe-lifecycle.md — solace-cli core IP
- proof-first-wish.md — solace-browser proof system
- promotion-wish-golden-replay-seal.md — solace-browser golden replay

## L1–L5 Node Hierarchy
- L1 CPU: parse/normalize/filter (no LLM, deterministic)
- L2 CPU: count/aggregate/score
- L3 LLM: plan/classify (no exact math)
- L4 Tool: bounded external execution (declared IO boundary)
- L5 LLM Judge: APPROVE / PATCH / REJECT / FAIL_CLOSED
