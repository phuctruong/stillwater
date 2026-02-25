# Wishes: Notebook-First Spec System

This directory is a lightweight replacement for heavyweight Prime Wishes authoring.

Goal:
- Keep the rigor that matters: closed states, tests, evidence, fail-closed behavior.
- Reduce authoring overhead by using notebook-centered specs + short Markdown contracts.
- Keep canonical externalization in Prime Mermaid.

## Theme: Dojo + Aladdin Quest

We use a dual analogy to make onboarding memorable:
- Bruce Lee dojo: discipline, repetition, proof.
- Aladdin quest: a wish must be precise, or the genie interprets it badly.

Translation to engineering:
- "Genie ambiguity" = hidden state/hallucinated policy.
- "Precise wish language" = Prime Mermaid state contract + explicit tests.

## Why this exists

Prime Wishes papers are excellent for high-assurance work, but full structure can be too heavy for everyday CLI evolution.

The compromise is a 3-tier model:
1. `L0` rapid note (short MD)
2. `L1` Wish Notebook (default)
3. `L2` full Prime Wish (only for critical/high-risk features)

## Gamified progression

Use this as a team leveling path:
1. `White Belt / Street Tier`: can write `L0` wish notes with clear non-goals.
2. `Yellow Belt / Cave Mapper`: can create Prime Mermaid state graphs and forbidden states.
3. `Green Belt / Lamp Holder`: can produce runnable wish notebooks with passing acceptance tests.
4. `Brown Belt / Contract Smith`: can stabilize deterministic hashes across reruns.
5. `Black Belt / Dragon Judge`: can promote reusable templates and escalate to `L2` when needed.

## Workflow

1. Copy `templates/WISH-NOTEBOOK-TEMPLATE.ipynb`.
2. Fill: capability, non-goals, Prime Mermaid state graph, acceptance tests, evidence plan.
3. Run notebook and emit artifacts (`.mmd`, `.sha256`, `results.json`).
4. If stable and reused, promote to `examples/`.
5. If high-risk or repeated failures, escalate to full L2 Prime Wish.

Quest framing for each wish:
1. Map the cave (state graph)
2. Phrase the wish (capability + non-goals)
3. Bind the genie (forbidden states + fail-closed policy)
4. Pass the trials (acceptance/adversarial tests)
5. Bring back the relic (artifacts + hashes)

## Layout

- `papers/`: theory + method
- `templates/`: notebook + MD scaffolds
- `mvp/`: minimum viable protocol
- `examples/`: concrete sample wishes for CLI
