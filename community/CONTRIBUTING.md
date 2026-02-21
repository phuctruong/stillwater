# Contributing to the Stillwater Community

> "Absorb what is useful, discard what is useless, add what is essentially your own." -- Bruce Lee

Welcome. This document covers community contributions of skills, recipes, swarm agent types, and papers. For code contributions to the core repo (tests, notebooks, src), see the root `CONTRIBUTING.md`.

---

## Types of Contributions Accepted

| Type | Directory | Guide |
|------|-----------|-------|
| Skills | `skills/` | `community/SKILL-AUTHORING-GUIDE.md` |
| Recipes | `recipes/` | `community/RECIPE-AUTHORING-GUIDE.md` |
| Swarm agent types | `swarms/` | `community/SWARM-DESIGN-GUIDE.md` |
| Papers | `papers/` | Follow existing papers structure; see `papers/00-index.md` |

All contributions must be in text form (Markdown, YAML, JSON). No binaries.

---

## Submission Requirements by Type

### Skills

A community-contributed skill must:

1. Pass the 5/5 binary scorecard (`community/SCORING-RUBRIC.md`).
2. Include the completed scoring table (with evidence column filled) in the PR description.
3. Have a version string in `X.Y.Z` format, starting at `1.0.0`.
4. Have `authority: 65537` in the header.
5. Contain no absolute file paths.
6. Contain no private repository dependencies.
7. Be loadable standalone (does not require a specific prior session state).

### Recipes

A community-contributed recipe must:

1. Pass the adapted 5/5 scorecard (see `community/SCORING-RUBRIC.md`, recipes section).
2. Include the scoring table in the PR description.
3. Have all 10 required frontmatter fields (see `community/RECIPE-AUTHORING-GUIDE.md`).
4. Have a `compression_gain_estimate` that is specific and falsifiable.
5. Have a `verification_checkpoint` that is a runnable command.
6. Contain no absolute file paths.
7. Reference `scratch/` for all intermediate artifacts (scratch is git-ignored).

### Swarm Agent Types

A community-contributed swarm agent type must:

1. Pass the adapted 5/5 scorecard (see `community/SCORING-RUBRIC.md`, swarm types section).
2. Include the scoring table in the PR description.
3. Include all required sections: Role, Skill Pack, Persona Guidance, Expected Artifacts, CNF Capsule Template, FSM, Forbidden States, Verification Ladder, Anti-Patterns.
4. Define artifact schemas with `schema_version`, `stop_reason`, and `evidence` fields.
5. Have `authority: 65537` in the YAML frontmatter.
6. Include a persona with at least one primary figure and one alternative.
7. Contain no absolute file paths.

### Papers

A community-contributed paper must:

1. Be an original analysis, proof, or case study related to AI verification, skills, or orchestration.
2. Follow the existing papers format (see `papers/00-index.md` for the index structure).
3. Separate verified claims (with executable evidence) from hypotheses.
4. Include a numbered entry in `papers/00-index.md`.
5. Contain no unverified benchmark claims.

---

## Self-Scoring Requirement

Every PR that contributes a skill, recipe, or swarm agent type must include a completed scoring table in the PR description. The format is:

```
| Criterion | Description | Pass (1) / Fail (0) | Evidence |
|-----------|-------------|---------------------|---------|
| C1 | FSM present | 1 | Line 42: STATE_SET: [...] |
| C2 | Forbidden states defined | 1 | Line 87: FORBIDDEN_STATES: [...] |
| C3 | Verification ladder | 1 | Line 103: RUNG_641: ... |
| C4 | Null/zero handling | 1 | Line 67: Null_vs_Zero_Policy: ... |
| C5 | Output contract | 1 | Line 119: Output_Contract: ... |
| Total | | 5/5 | |
```

PRs without this table will not be reviewed. The evidence column must cite a specific line or pattern in the submitted file.

---

## Review Process

All community submissions go through a 3-stage review:

### Stage 1: Automated Scorecard Check

A CI step runs the pattern-matching check from `recipes/recipe.skill-completeness-audit.md` on the submitted file. If any of the 5 criteria fail the automated check, the PR is flagged for revision before human review begins.

Automated check results are posted as a PR comment with:
- Pass/fail per criterion
- The detection pattern that failed
- A link to `community/SCORING-RUBRIC.md`

### Stage 2: Swarm Agent Review

A Scout + Judge + Skeptic swarm chain reviews the submission:

- **Scout** maps the submission: checks structure, counts sections, identifies missing fields.
- **Judge** scores the submission: runs the full scorecard including human-readable checks (not just grep patterns).
- **Skeptic** stress-tests the submission: identifies edge cases, missing forbidden states, and adversarial inputs that the submission does not handle.

The swarm chain produces a `REVIEW_REPORT.json` that is posted as a PR comment.

### Stage 3: Maintainer Approval

A project maintainer reviews the `REVIEW_REPORT.json` and the PR diff. If the swarm review is PASS and the self-scoring table is consistent with the automated check, the maintainer merges.

If the review finds issues, a revision is requested with specific criteria noted.

**Timeline:** Reviews are best-effort. There is no guaranteed turnaround time. Complex submissions may take longer.

---

## Registration in MANIFEST.json

After merge, add your contribution to `community/MANIFEST.json` by filling in the `submission_template`:

```json
{
  "id": "<recipe.name or skill-name or swarm-name>",
  "version": "1.0.0",
  "title": "<Human-readable title>",
  "author": "<your name or handle>",
  "score": "5/5",
  "evidence_path": "<repo-relative path to your submitted file>",
  "pr_url": "<GitHub PR URL>",
  "submitted_at": "<YYYY-MM-DD>"
}
```

Add this object to the appropriate array: `skills_submitted`, `recipes_submitted`, `swarms_submitted`, or `papers_submitted`.

This can be done in the same PR as the submission or in a follow-up PR. Either is acceptable.

---

## Code of Conduct

The Stillwater community follows a simple standard: discipline over cleverness, receipts over promises, honesty over confidence.

In practice:
- Separate what you know from what you guess. Label both.
- Do not submit a skill claiming it works if you have not run it.
- If you find a gap in someone else's submission, point to the specific criterion and the specific line. Be precise, not hostile.
- If you disagree with a review decision, ask a clarifying question before escalating.

There is no formal CoC document. The root `CONTRIBUTING.md` describes the "dojo rules." Follow them.

---

## License

Contributions to this repository are made under the same license as the project. See `LICENSE` at the repository root. By submitting a PR, you agree to license your contribution under those terms.

Do not submit content you do not have the right to license.

---

## How to Propose a New Swarm Agent Persona

If you want to propose a new persona (historical figure) for an existing or new swarm agent type:

1. Write a one-paragraph justification: what is this figure's characteristic lens, and why does it match the agent's failure mode?
2. Cite at least one documented example of this figure applying that lens to a real problem.
3. Identify the figure's most famous failure mode and explain how it is a useful cautionary signal for the agent.
4. Open a PR or issue with this justification and the proposed swarm agent type file.

Persona proposals are reviewed by a maintainer. The selection criterion is: does this persona meaningfully narrow the search heuristic for the agent's role, without conflicting with the skill pack constraints?

Historical figures are preferred over fictional characters. Living persons are not accepted as personas.

---

*Questions? Open a GitHub issue with the label `community`. Include the file you are working on and the specific criterion or step where you are stuck.*
