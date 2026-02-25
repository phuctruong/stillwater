# Wish Notebook Theory

Date: 2026-02-19  
Scope: Stillwater CLI framework conventions

## Thesis

Wishes are still useful, but their value comes from three things, not maximal document structure:
1. Explicit state boundaries
2. Executable tests
3. Replayable evidence

Jupyter notebooks plus strong Markdown specs can preserve that rigor with less authoring friction.

Key concept:
- Gamification is not optional decoration in this model; it is an adoption and behavior-shaping mechanism tied to objective proof gates.

## Analogy: Aladdin as spec hygiene

Non-normative framing:
- In the Aladdin story, vague wishes can be interpreted in unexpected ways.
- In software, vague specs are interpreted by the model as hidden policy.

Therefore:
- Wish text must be explicit.
- Non-goals must be explicit.
- Forbidden states must be explicit.

This is not decoration; it is a memory aid for anti-hallucination design.

## Position

Full Prime Wish format remains the strongest governance model for safety-critical and high-cost changes.  
For daily CLI evolution, a notebook-first model is faster and often enough.

Use this escalation ladder:
- `L0` Note: one-page Markdown intent and constraints
- `L1` Wish Notebook: default path for new features and experiments
- `L2` Full Prime Wish: required for critical paths and repeated failure classes

## What to preserve from classic wishes

Keep:
- Closed state machine mindset
- Forbidden states
- Counter bypass for counting/aggregation tasks
- Harsh verification and proof artifacts
- Fail-closed ambiguity handling

Simplify:
- Reduce repeated prose sections
- Collapse many headings into notebook cells
- Keep one canonical Prime Mermaid graph as source-of-truth

## Why this fits Stillwater

Stillwater already treats notebooks as executable proofs.  
A Wish Notebook system aligns with:
- clone-to-first-value onboarding
- software 5.0 externalized cognition
- Prime Mermaid as canonical externalization format

## Convention over configuration

Like Struts and Next.js:
- Stable runtime kernel in code
- Behavior customization in convention files
- Auto-discovery by directory and filename

In Stillwater:
- code = engine
- ripples = configuration/conventions
- Prime Mermaid = executable contract

## Gamification model (adoption accelerator)

To improve team adoption, use a dojo progression:
1. `Form`: write the smallest valid wish notebook.
2. `Discipline`: rerun until hashes are stable.
3. `Sparring`: add adversarial tests for likely failure modes.
4. `Mastery`: promote reusable templates and coach others.

Game mechanics are optional, but the proof gates are not optional.

## Decision

Adopt `L1 Wish Notebook` as default for CLI feature development.  
Escalate to `L2` only when risk, compliance, or recurrence justifies the overhead.
