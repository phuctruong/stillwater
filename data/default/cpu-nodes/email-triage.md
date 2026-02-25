---
id: cpu-node-email-triage-v1
type: cpu-node
phase: custom
name: "Email Triage"
threshold: 0.80
seeds_file: "seeds/email-triage-seeds.jsonl"
learnings_file: "learned_email_triage.jsonl"
validator_model: "haiku"
labels: [urgent, action-required, informational, fyi, spam, newsletter]
---

# Email Triage CPU Node

CPU-first triage label routing for inbox workflows.
Any label confidence below `0.80` should be escalated to validator.

## State Machine

```mermaid
stateDiagram-v2
    [*] --> Extract
    Extract --> Predict
    Predict --> Route : confidence >= 0.80
    Predict --> Validate : confidence < 0.80
    Validate --> Learn
    Learn --> Route
    Route --> [*]
```

## Labels

- `urgent`
- `action-required`
- `informational`
- `fyi`
- `spam`
- `newsletter`

