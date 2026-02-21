# Wish Notebook MVP

Use this when speed matters and you still want rigor.

## Gamification is required in MVP

Every MVP wish should include:
- Quest name
- Current belt
- Target belt
- Promotion condition (what must pass to level up)

Suggested default:
- Start at `White Belt`
- Promote only after deterministic rerun and forbidden-state gates pass

## Required fields (minimum)

1. Wish ID
2. Capability sentence
3. Non-goals (2+)
4. Prime Mermaid graph
5. Acceptance tests (3+)
6. Forbidden states list
7. Evidence artifacts (`state.mmd`, `state.sha256`, `results.json`)
8. Gamification block (quest + belt progression)

## MVP pass criteria

- All tests pass
- Deterministic hash stays identical across 2 reruns
- No forbidden state observed
- One replay command documented

## Escalate to full wish when

- Security/compliance risk is high
- Public benchmark claim is made
- Failure class repeats
