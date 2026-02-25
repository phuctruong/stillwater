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

---

## Paper Extraction Flow (Mermaid Diagram)

```mermaid
flowchart TD
    A[Step 1: VERIFY SOURCES\nsource_artifacts.json\nLESSONS.md + RECIPE.md present + non-empty] --> B[Step 2: EXTRACT INSIGHT\ncore_insight.txt\none sentence, non-obvious, typed A/B/C]
    B --> C[Step 3: DRAFT ABSTRACT + HYPOTHESIS\nabstract_hypothesis.md\n<= 150 words + falsifiable hypothesis]
    C --> D[Step 4: WRITE PAPER BODY\npaper_draft.md\nSections 1-5 with A/B/C typed claims]
    D --> E[Step 5: ASSIGN NUMBER\npaper_number.txt\nhighest existing + 1, no conflicts]
    E --> F[Step 6: FINALIZE PAPER\npapers/N-slug.md\nYAML frontmatter + typed claims + bibliography]
    F --> G[Step 7: UPDATE INDEX\npapers/00-index.md\nnew entry in ascending order]

    A -->|LESSONS.md missing| A2[Re-run swarm-pipeline\nstep 7 Podcast first]
    B -->|no single insight| B2[NEED_INFO\nlist top 3 candidates for human selection]
    C -->|hypothesis not falsifiable| C2[Downgrade to Observation\nlabel clearly]
    D -->|claim untyped| D2[Remove claim\nno unsourced claims published]
    E -->|numbering conflict| E2[Skip conflict number\ntake next available]
    G --> PASS[PASS\npaper at correct path + index entry]
```

---

## FSM: Paper Extraction State Machine

```
States: VERIFY_SOURCES | EXTRACT_INSIGHT | DRAFT_ABSTRACT |
        WRITE_BODY | ASSIGN_NUMBER | FINALIZE | UPDATE_INDEX |
        PASS | BLOCKED | NEED_INFO

Transitions:
  [*] → VERIFY_SOURCES: completed swarm run artifacts provided
  VERIFY_SOURCES → NEED_INFO: LESSONS.md or RECIPE.md missing (re-run Podcast step first)
  VERIFY_SOURCES → EXTRACT_INSIGHT: both source artifacts exist and non-empty
  EXTRACT_INSIGHT → NEED_INFO: no single generalizable insight (emit top 3 candidates)
  EXTRACT_INSIGHT → DRAFT_ABSTRACT: core_insight.txt with typed lane annotation
  DRAFT_ABSTRACT → DRAFT_ABSTRACT (DOWNGRADE): hypothesis not falsifiable → label as Observation
  DRAFT_ABSTRACT → WRITE_BODY: abstract <= 150 words + hypothesis/observation stated
  WRITE_BODY → WRITE_BODY (REMOVE): claim cannot be typed → remove, do not publish unsourced
  WRITE_BODY → ASSIGN_NUMBER: all claims typed [A/B/C], all numbers sourced to artifacts
  ASSIGN_NUMBER → ASSIGN_NUMBER (SKIP): numbering conflict → take next available
  ASSIGN_NUMBER → FINALIZE: number confirmed unique
  FINALIZE → BLOCKED: YAML frontmatter breaks file parsing (simplify, flag parse issue)
  FINALIZE → UPDATE_INDEX: paper at correct path, frontmatter parses
  UPDATE_INDEX → PASS: index entry present, ascending order maintained

Exit conditions:
  PASS: paper exists at papers/N-slug.md; YAML parses; >= 3 typed claims; index entry correct
  BLOCKED: YAML parse failure unresolvable
  NEED_INFO: source artifacts missing; no single generalizable insight
```

---

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | Paper extracts a non-obvious generalizable insight from swarm artifacts; typed Lane A claim (invariant) discovered | +6 per paper with at least 1 Lane A [A] claim |
| **L** (Love/Quality) | All claims typed [A/B/C]; all figures sourced to run artifacts; hypothesis is falsifiable (not forced consensus) | +6 when python3 grep for [A][B][C] confirms >= 3 annotations |
| **O** (Output) | Paper committed at papers/N-slug.md; index updated in ascending order; frontmatter parses | +6 per published paper |
| **W** (Wisdom) | Northstar metric (skill_quality_avg + recipe_hit_rate) advanced because paper formalizes a new convention or invariant | +6 when paper documents a new Lane A invariant adopted by others |

**Northstar Metric:** `skill_quality_avg` + `recipe_hit_rate` — papers that document Lane A invariants (discovered during swarm runs) directly improve both: the invariant becomes a skill constraint (raising quality score) and the RECIPE.md section becomes a replayable recipe (raising hit rate).

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each paper extraction run trains the agent to identify which swarm artifacts contain publishable insights — the feedback loop between LESSONS.md quality and paper generalizability improves the Podcast agent's synthesis discipline in future swarm runs |
| **LEAK** (Cross-Agent Trade) | The Podcast agent distills the Solver and Skeptic agents' combined evidence into typed claims [A/B/C], enabling the Writer agent to produce a paper without needing to re-read all underlying artifacts — compressed, typed knowledge traded across agent roles |
| **LEC** (Emergent Conventions) | Establishes the [A/B/C] claim typing system as a reusable convention for all published work: Lane A = invariant, Lane B = engineering preference, Lane C = heuristic — making the epistemic status of every claim explicit and reviewable |

**Belt Level:** Green — demonstrates the full lifecycle from execution to knowledge: running a swarm, synthesizing its insights via Podcast, extracting typed claims, and publishing a falsifiable paper with traceable provenance to run artifacts.

**GLOW Score:** +6 per published paper with at least 3 typed claims [A/B/C], a falsifiable hypothesis, all figures sourced to run artifacts, and a correct index entry in papers/00-index.md.
