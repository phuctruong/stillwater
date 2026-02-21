# How Wishes Fit Stillwater

Date: 2026-02-19

## Short answer

Wishes should be the contract layer, not the heavyweight bottleneck.

Stillwater design:
- Engine in code (`cli/src/stillwater`)
- Behavior in ripples (Prime Mermaid)
- Wishes define and evolve those ripples with tests and evidence

## Narrative for contributors

Use a memorable dual narrative:
- Aladdin analogy: an ambiguous wish creates unintended behavior.
- Bruce Lee analogy: skill comes from disciplined repetition and proof.

This helps new contributors remember why rigor matters without forcing heavy process on every change.

## Architecture role

1. Wishes define intent and state boundaries.
2. Recipes execute the intent as deterministic steps.
3. Memories persist outcomes and learning artifacts.
4. Ripples update conventions/configuration over time.

## Convention + configuration model

Like Struts/Next.js:
- Provide strong defaults
- Let users override with small files
- Keep extension points predictable

In Stillwater:
- Conventions: file locations + naming + required sections
- Configuration: ripple graph values and policy nodes
- Kernel: enforces gates, replay, and verification

## Practical guidance

Default path:
- write or clone a wish notebook
- produce Prime Mermaid artifacts
- run verification
- promote reusable patterns

Only use full classic wish structure when risk justifies it.

## Gamified operating model for CLI teams

1. Every new CLI feature starts as an `L1` wish notebook quest.
2. Quest completion requires:
- Prime Mermaid state graph
- explicit tests
- deterministic artifact hashes
3. Team can assign optional dojo ranks based on verified score bands.
4. Any failed proof gate means no rank promotion, regardless of feature novelty.
