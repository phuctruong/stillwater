---
id: recipe.paper-from-run
version: 1.0.0
title: Paper Extraction from Completed Swarm Run
description: Extract a publishable research paper from a completed swarm run by distilling the Podcast agent's LESSONS.md and RECIPE.md into a structured paper with typed claims [A/B/C], added to the papers/ directory with the next available number.
skill_pack:
  - prime-safety
  - software5.0-paradigm
compression_gain_estimate: "Encodes paper extraction process that produces publishable insight from swarm artifacts in 2 hours versus 1 week of manual writing"
steps:
  - step: 1
    action: "Read LESSONS.md and RECIPE.md from the completed swarm run's scratch/ or artifacts/ directory; verify both files exist and are non-empty; if missing, check for PODCAST_MEMO.md or SYNTHESIS.md as alternatives"
    artifact: "Confirmed paths to LESSONS.md and RECIPE.md (or equivalents); scratch/paper_extraction/source_artifacts.json — {lessons_path, recipe_path, run_id}"
    checkpoint: "Both source artifacts exist and are non-empty; source paths are repo-relative; run_id is recorded to establish provenance"
    rollback: "If LESSONS.md is missing, check if the Podcast step was skipped in the run; if so, re-run recipe.swarm-pipeline step 7 on the existing artifacts before proceeding; do not extract a paper from incomplete run artifacts"
  - step: 2
    action: "Read LESSONS.md and identify the single most generalizable insight: the insight must be (a) non-obvious, (b) supported by the run's evidence artifacts, and (c) applicable beyond this specific task; write the insight as one sentence"
    artifact: "scratch/paper_extraction/core_insight.txt — one sentence stating the generalizable insight; evidence pointers supporting it"
    checkpoint: "Insight is stated in one sentence; evidence pointers list at least 2 artifacts from the run that support it; insight is typed as Lane A (invariant), Lane B (engineering quality), or Lane C (heuristic)"
    rollback: "If no single generalizable insight emerges, list the top 3 candidates and ask for human selection; do not proceed with a vague or multi-part insight"
  - step: 3
    action: "Draft abstract (150 words max) and hypothesis (one falsifiable statement): abstract covers problem, approach, result, and implication; hypothesis states what the run confirmed or refuted"
    artifact: "scratch/paper_extraction/abstract_hypothesis.md — abstract + hypothesis in markdown"
    checkpoint: "Abstract is under 150 words; hypothesis is falsifiable (there exists an experiment that could disprove it); neither abstract nor hypothesis claims results beyond what run artifacts support"
    rollback: "If hypothesis cannot be stated as falsifiable, downgrade from hypothesis to observation; label clearly as 'Observation' not 'Hypothesis' in the paper"
  - step: 4
    action: "Write the paper body (3–5 sections): Section 1 Introduction (problem + why it matters), Section 2 Method (what the swarm did, typed claims for each key claim [A/B/C]), Section 3 Results (evidence from artifacts, exact numbers not estimates), Section 4 Discussion (implications, limitations), Section 5 Recipe (reusable steps extracted from RECIPE.md)"
    artifact: "scratch/paper_extraction/paper_draft.md — full paper draft in markdown"
    checkpoint: "Every key claim in the paper has a lane type annotation [A], [B], or [C]; all numbers/results are sourced from run artifacts (no invented figures); Section 5 references RECIPE.md content, not paraphrased memory"
    rollback: "If a claim cannot be typed or sourced, remove it from the paper; do not publish unsourced claims even if they are plausible; label speculation explicitly as 'Conjecture' with lane C annotation"
  - step: 5
    action: "Determine the next available paper number: list papers/ directory, find highest-numbered file (e.g., papers/18-*.md → next is 19), verify no numbering conflicts; assign number to this paper"
    artifact: "scratch/paper_extraction/paper_number.txt — the assigned paper number; list of existing paper files for verification"
    checkpoint: "Assigned number is exactly (highest existing number + 1); no existing paper has this number; number is a plain integer (not float, not null)"
    rollback: "If directory listing fails or is ambiguous, manually check papers/ with Read; do not guess the number; if conflict detected, skip the conflicting number and take next available"
  - step: 6
    action: "Finalize paper: assemble full markdown file with YAML frontmatter (id, version, title, run_id, rung_target, typed_claims_summary), body sections from step 4, and bibliography referencing run artifacts; save to papers/<number>-<slug>.md"
    artifact: "papers/<number>-<slug>.md — complete paper file at the assigned number"
    checkpoint: "File exists at the correct path; YAML frontmatter is well-formed; all typed claims have [A/B/C] annotations in the body; run_id in frontmatter matches source_artifacts.json; no absolute paths in file"
    rollback: "If YAML frontmatter breaks file parsing, simplify frontmatter to plain markdown header and note the parse issue; do not publish with broken frontmatter"
  - step: 7
    action: "Update papers/README.md or papers/00-index.md: add new paper to the index with its number, title, and one-line summary; verify index is in ascending order by paper number"
    artifact: "Updated papers/README.md or papers/00-index.md with new entry"
    checkpoint: "New paper appears in the index; index is in ascending numerical order; no duplicate entries"
    rollback: "If index file does not exist, create papers/00-index.md with the new entry as first item; do not add entries to arbitrary files"
forbidden_states:
  - PAPER_WITHOUT_TYPED_CLAIMS: "Submitting a paper where key claims lack [A/B/C] lane type annotations — all claims must be typed to distinguish invariants from heuristics"
  - PAPER_FROM_MEMORY: "Writing paper content from memory or inference rather than directly from run artifacts (LESSONS.md, RECIPE.md, evidence files) — provenance must be traceable"
  - DUPLICATE_PAPER_NUMBER: "Assigning a paper number already used by an existing file in papers/ — causes index conflicts and version ambiguity"
  - UNFALSIFIABLE_HYPOTHESIS: "Presenting a non-falsifiable statement as the paper's hypothesis — hypotheses must be testable by a defined experiment"
  - INVENTED_FIGURES: "Including numerical results in the paper that are not directly sourced from run artifact files — all numbers must trace to evidence"
  - INDEX_OUT_OF_ORDER: "Adding a paper to the index without checking that the index remains in ascending numerical order"
verification_checkpoint: "Verify paper file exists at papers/<number>-<slug>.md; verify YAML frontmatter parses: python3 -c \"import yaml; yaml.safe_load(open('papers/<number>-<slug>.md').read().split('---')[1])\"; grep for '[A]' '[B]' '[C]' annotations in paper body — at least 3 typed claims required; verify paper number appears in papers/00-index.md or papers/README.md"
rung_target: 641
---

# Recipe: Paper Extraction from Completed Swarm Run

## Purpose

Transform a completed swarm run's artifacts (LESSONS.md + RECIPE.md + evidence) into a structured, publishable research paper with typed claims. Designed to compress 1 week of manual paper writing into 2 hours by following a deterministic extraction protocol.

## When to Use

- After any swarm run that produced a non-obvious generalizable insight
- When the Podcast agent's LESSONS.md contains a hypothesis worth formalizing
- When a recipe or skill upgrade reveals a new failure mode worth documenting

## Claim Typing Guide

Every key claim in the paper must be typed:

| Lane | Type | Meaning | Example |
|------|------|---------|---------|
| [A] | Invariant | Hard safety/correctness rule | "Dual FSM without precedence causes non-deterministic agent behavior" |
| [B] | Engineering quality | Strong preference with trade-off space | "Minimal diffs are preferred when evidence supports multiple solutions" |
| [C] | Heuristic | Guidance only, not sufficient for PASS | "Localization scoring heuristics typically converge in 3 iterations" |

## Paper Structure Template

```markdown
# <Number>. <Title>

## Abstract
(150 words max)

## 1. Introduction
## 2. Method
## 3. Results
## 4. Discussion
## 5. Recipe (Reusable Steps)
```

## Notes

- Every number in the results section must trace to a run artifact file with an explicit path
- The paper number is determined by the directory state at writing time — always re-check before finalizing
- Lane C claims are valuable in papers but must be clearly labeled as heuristics, not proofs
