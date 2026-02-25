# Wish Prime Mermaid Template

```mermaid
flowchart TD
  START[STATE: START]
  INPUT_OK[STATE: INPUT_OK]
  NEED_INFO[STATE: NEED_INFO]
  PLAN_READY[STATE: PLAN_READY]
  EXECUTED[STATE: EXECUTED]
  VERIFIED[STATE: VERIFIED]
  BELT_GATE[STATE: BELT_PROMOTION_GATE]
  FAIL_CLOSED[STATE: FAIL_CLOSED]

  START --> INPUT_OK
  START --> NEED_INFO
  INPUT_OK --> PLAN_READY
  PLAN_READY --> EXECUTED
  EXECUTED --> VERIFIED
  VERIFIED --> BELT_GATE
  EXECUTED --> FAIL_CLOSED

  classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px;
```

## Notes

- Replace state names with concrete feature states.
- List forbidden states in notebook text and test for them.
- Export canonical body to `.mmd` and hash to `.sha256`.
- Include quest metadata and belt promotion criteria in companion markdown.
