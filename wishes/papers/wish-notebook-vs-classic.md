# Classic Wishes vs Wish Notebook

Date: 2026-02-19

## Recommendation

Use a hybrid model:
- Default: Wish Notebook (`L1`)
- Escalation: full Prime Wish (`L2`) for high-risk or public benchmark claims

## Practical tradeoffs

| Criterion | Classic Prime Wish | Wish Notebook |
|---|---|---|
| Rigor ceiling | Highest | High |
| Authoring speed | Slow | Fast |
| Onboarding friendliness | Medium | High |
| Drift resistance | Highest when enforced | High with template discipline |
| Audit readability | High but long | High with compact flow |
| Best use case | Critical features and compliance | Day-to-day feature development |
| Gamified adoption fit | Medium | High |

## Why notebooks can match most rigor

Notebook + MD can preserve the core controls if these are enforced:
1. Closed Prime Mermaid state graph
2. Explicit acceptance tests
3. Deterministic artifacts with hashes
4. Fail-closed ambiguity protocol

Without those four, notebook format alone is not enough.

## Aladdin + Dojo framing

This framing improves behavior without reducing rigor:
- Aladdin reminder: vague wishes create bad interpretations.
- Dojo reminder: repetition + evidence beats one-shot cleverness.

Use it for onboarding and team rituals, not as a substitute for proof gates.

## Migration strategy

1. Start all new features as L1 wish notebooks.
2. Promote successful patterns into reusable templates.
3. Escalate recurring failures into L2 canonical wishes.
4. Track belt/rank progression only when deterministic proof gates pass.
