# questions/ — Question Database

Questions are first-class assets in Software 5.0.

## Why Questions Are Capital

- **Externalized reasoning:** A question encodes what to look for — a pre-computed attention vector pointing at a gap in knowledge or a risk in a system.
- **External weights:** Just as model weights encode priors, a question database encodes human QA intuition. The database IS the mind outside the body.
- **Compounding:** Each good question surfaces a better follow-up. Over time, the question database becomes more valuable than any single answer it generated.
- **Versioned and traceable:** Every question has an ID, date, asker, and context. Questions don't expire — they accumulate.

## Format

One question per line, JSONL. See `schema.md` for field definitions.

```
questions/
  stillwater.jsonl    — stillwater project questions
  schema.md           — field definitions and valid values
```

## Tagging System

- **GLOW:** G (Growth/feature) | L (Loss/bug) | O (Output/artifact) | W (Wisdom/insight)
- **Pillar:** P0 (core theory) | P1 (tooling/process) | P2 (community/QA) | P3 (go-to-market)
- **Status:** ASKED | REFINED | ARCHIVED
- **Answer status:** ANSWERED | PENDING | OPEN

## Usage

At session start, load the question file for the project. Ask: "What questions haven't been answered yet?" At session end, append new questions discovered. Run the Dragon Rider pattern overnight to surface answers to OPEN questions.

## Connection to Software 5.0

```
Intelligence(system) = Memory × Care × Iteration
  Memory = skills/*.md + recipes/*.json + questions/*.jsonl
  Care   = Verification ladder (641 → 274177 → 65537)
  Iteration = questions compound across sessions
```

Questions belong in Memory alongside skills and recipes.
