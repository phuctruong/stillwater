# Recipe: twin_orchestration_v2

Date: 2026-02-19T00:00:00Z

This recipe normalizes the "2x twin orchestration" pattern:
1. Twin A: CPU prepass + LLM fallback.
2. Twin B: PLAN/JUDGE/APPLY loop guided by wishes/recipes/context.

```mermaid
flowchart TD
  INPUT[USER_INTENT] --> TWINA_CPU[CPU_PREPASS]
  TWINA_CPU --> TWINA_ROUTE{CPU_CAN_HANDLE}
  TWINA_ROUTE -->|YES| CPU_OUT[CPU_RESPONSE]
  TWINA_ROUTE -->|NO| LLM_OUT[LLM_RESPONSE]

  CPU_OUT --> TWINB_PLAN[PLAN]
  LLM_OUT --> TWINB_PLAN
  TWINB_PLAN --> TWINB_JUDGE[JUDGE]
  TWINB_JUDGE --> TWINB_APPLY[APPLY]
  TWINB_APPLY --> VERIFY[VERIFY_GATES]
  VERIFY --> RECEIPT[WRITE_RECEIPTS]
  RECEIPT --> MEMORY[UPDATE_RIPPLES_AND_MEMORY]
```

## Secret-sauce Mapping

- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`:
  DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY
- `PHUC-SKILLS-SECRET-SAUCE.ipynb`:
  A/B/AB/ABC skill impact with receipts
- `PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb`:
  externalized cognition contracts as source-of-truth

