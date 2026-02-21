# Persona-Based Review: Why Named Agents Surface Failure Modes That Generic Review Misses

**Status:** Draft (open-source; claims typed by lane below)
**Last updated:** 2026-02-20
**Scope:** The theoretical basis and empirical evidence for using named historical personas as review agents in multi-agent swarms; three case studies from the Stillwater repo.
**Auth:** 65537 (project tag; see `papers/03-verification-ladder.md`)

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — framework principle, derivable from stated axioms or established computer science
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Abstract

**[B] Thesis:** Assigning a named historical persona (Ken Thompson, Alan Turing, Ada Lovelace) to a review agent produces systematically different — and complementary — failure mode detection compared to a generic "reviewer" agent.

Code review, skill review, and artifact review in AI-assisted engineering typically uses one of two patterns: (1) a generic "reviewer" agent instructed to find problems, or (2) a checklist applied mechanically. Both patterns have well-documented blind spots: the generic reviewer converges on the most obvious issues; the checklist misses problems not anticipated by the checklist author.

This paper proposes persona-based review as a complementary technique. By instructing a review agent to embody a named historical figure with a known intellectual style, we activate systematically different attention patterns in the LLM. The personas do not replace checklists or generic review — they add coverage that generic review systematically misses.

Three case studies from the Stillwater swarm system demonstrate this empirically: Turing-as-Skeptic found 8 falsifiers in `prime-wishes.md`, Lovelace-as-Judge verified artifact exclusivity across 26 papers, and Thompson-as-Scout enforced evidence-first reasoning against speculative claims.

---

## 1. Introduction: The Persona Hypothesis

### 1.1 The Generic Reviewer Failure Mode

**[B]** A generic reviewer agent — instructed with "review this for problems" — exhibits a systematic failure mode: it reviews the artifact against the mean of what it has seen in training. Problems that are common in training data (syntax errors, obvious logical inconsistencies, missing documentation) are caught reliably. Problems that are unusual or domain-specific (subtle invariant violations, implicit null coercion, behavioral hash drift) are missed because they do not appear frequently enough in training to activate strong review attention.

This is not a deficiency unique to AI reviewers. Human reviewers exhibit the same bias: experts review against their habitual expectations; non-habitual problems require explicit attention direction.

### 1.2 The Persona Hypothesis

**[C]** The persona hypothesis: instructing an LLM agent to embody a named historical figure with a distinctive intellectual style shifts the agent's attention distribution in a predictable direction, causing it to find problems that its un-directed review would have missed.

**[B]** The mechanism is not magical: LLMs are trained on vast amounts of text about historical figures, including their intellectual contributions, their documented thinking styles, and their known concerns. When instructed to "review as Turing would," the model activates information about Turing's documented intellectual style: formal specification, computability analysis, skepticism toward anthropomorphism, concern with decidability.

**[B]** This activation shifts attention toward: formal specification gaps (where informal prose substitutes for rigorous specification), edge cases that are computationally interesting, and claims that anthropomorphize behavior that should be formally specified. These are precisely the failure modes that generic review underweights.

### 1.3 Scope and Claims

This paper makes three claims:

1. **[B]** Persona activation produces systematically different attention patterns than generic review.
2. **[A]** Three specific persona deployments in this repo's swarm system surfaced specific failure modes documented here.
3. **[C]** Persona-based review is most effective when personas are selected to complement, not duplicate, each other's attention patterns.

We do not claim that persona-based review is sufficient for complete quality assurance. It is one technique among several (scorecard, rung gates, adversarial paraphrase sweep) that together provide coverage.

---

## 2. Mechanism: Why Personas Activate Different Attention Patterns

### 2.1 The LLM as Persona Simulator

**[B]** An LLM trained on human text has learned statistical associations between named individuals and their documented intellectual styles. When instructed to reason "as Turing would," the model:

1. Activates its representation of Turing's documented concerns (computability, formal specification, the distinction between simulation and genuine cognition)
2. Biases generation toward outputs consistent with those concerns
3. Applies those biases to the artifact under review

This is not character simulation in the entertainment sense. It is a structured attention shift: the persona instruction is a learned prior over what questions the reviewer should ask.

### 2.2 Why This Produces Different Failures Than Generic Review

**[B]** Generic review activates the model's prior over "what problems are worth mentioning in a review." This prior is dominated by high-frequency review concerns: correctness, clarity, completeness, consistency with stated goals.

Persona-based review activates the model's prior over "what problems would concern [persona]." For non-generic personas, this prior is systematically different. Thompson cares about security at the systems level; Lovelace cares about the relationship between computation and notation; Turing cares about formal decidability and the limits of computation.

**[B]** The coverage property: if we select personas whose known concerns are complementary (no two personas with identical concern domains), the union of their review outputs covers a wider failure mode space than any single reviewer — generic or persona-based.

### 2.3 The Limits of This Mechanism

**[B]** The mechanism depends on the LLM having reliable associations between the named persona and their intellectual style. For well-documented historical figures (Turing, Thompson, Lovelace, Feynman, Shannon), this association is reliable. For obscure figures, living persons, or fictional characters, the association may be unreliable or dominated by training noise.

**[B]** The mechanism also depends on the artifact being in a domain where the persona's concerns are relevant. Turing-as-Skeptic is effective for reviewing formal specifications; he is less effective for reviewing UX design choices.

---

## 3. Case Study: Turing as Skeptic — 8 Falsifiers Found in prime-wishes.md

### 3.1 Context

**[A]** During a Stillwater swarm run, an agent instantiated as Turing-as-Skeptic was tasked with reviewing `skills/prime-wishes.md` — the skill governing wish notebook behavior, Prime Mermaid notation, and wish promotion governance.

The Turing persona was selected specifically because `prime-wishes.md` makes claims about formal notation (Prime Mermaid language) and governance (who can approve what). These are exactly the domains where Turing's documented concern with formal specification produces useful review bias.

### 3.2 The 8 Falsifiers

The Turing persona produced 8 falsifiers — claims that, if true, would invalidate parts of the skill:

**Falsifier 1:** "If Prime Mermaid is the required notation for wishes, but the FSM for validating Prime Mermaid syntax is absent from the skill, then the 'required notation' constraint is unenforceable. Any text can claim to be Prime Mermaid."

**Falsifier 2:** "The governance section lists who can approve skills but does not specify what happens when an approver is unavailable. If approval is a single point of failure, the governance model is non-robust."

**Falsifier 3:** "The skill does not specify whether wish promotion is monotone (once promoted, always promoted) or can be reversed. This creates ambiguity in long-running swarm runs where a wish may be promoted then invalidated by a later finding."

**Falsifier 4:** "The evidence requirements for wish promotion are prose descriptions, not machine-parseable schemas. A machine cannot verify promotion without a formal schema."

**Falsifier 5:** "The skill does not define 'wish collision' — what happens when two wishes claim ownership of the same artifact. Without a resolution rule, two solvers can produce conflicting artifacts with no defined winner."

**Falsifier 6:** "The skill's forbidden states include 'speculative promotion' but do not define the boundary between 'well-evidenced' and 'speculative.' Without a quantitative threshold, this forbidden state cannot be mechanically enforced."

**Falsifier 7:** "The skill claims wishes are idempotent but does not specify a canonical form for wish comparison. Two textually different wishes may be semantically identical; without canonical form, idempotency cannot be checked."

**Falsifier 8:** "The skill does not specify behavior when a wish's claimed artifact is deleted between submission and promotion. The governance protocol has no handling for artifact non-existence at promotion time."

### 3.3 What Generic Review Found (Comparison)

**[A]** A generic-reviewer pass on the same document (no persona instruction) produced a review that identified: unclear prose in the governance section, missing examples of Prime Mermaid notation, and a suggestion to add more forbidden states.

None of the 8 falsifiers above were identified by generic review. The falsifiers are structurally different: they identify conditions under which the skill's guarantees fail, not just areas where the prose is unclear. This is the systematic difference the persona mechanism produces.

---

## 4. Case Study: Lovelace as Judge — Artifact Exclusivity Verification

### 4.1 Context

**[A]** A Lovelace-as-Judge agent was tasked with verifying artifact exclusivity across the papers directory: confirming that no two solvers in the swarm were assigned overlapping artifact ownership.

The Lovelace persona was selected because her documented intellectual contribution — the recognition that Babbage's engine could manipulate symbols, not just numbers, and therefore operate on notation itself — is precisely relevant to checking whether the notation system (the artifact ownership table) is internally consistent.

### 4.2 The Artifact Exclusivity Check

**[A]** Lovelace-as-Judge applied the following analysis pattern:

1. Treat each solver's artifact set as a formal notation: a set of claimed file paths
2. Check pairwise set intersection: any non-empty intersection is a conflict
3. For any conflict, identify the resolution rule: which solver's claim takes precedence?
4. If no resolution rule exists, flag as BLOCKED

For the 26 papers in the current papers directory, plus the index file, the check identified:

- Zero ownership conflicts on paper files (each paper assigned to exactly one solver)
- One potential conflict on `papers/00-index.md` (multiple solvers instructed to append, creating a race condition in sequential execution)
- One unresolved question: who owns `papers/README.md` (a file Solver E was designated to own but which was not in the artifact ownership table)

**[A]** Generic review would have found the papers/README.md question (it is obvious). The Lovelace approach found the `papers/00-index.md` race condition — a non-obvious structural conflict between solvers both instructed to append rather than own exclusively.

### 4.3 Why This Is a Lovelace Pattern

**[B]** The Lovelace pattern is: identify the abstract structure of the system, verify the structure is internally consistent, find cases where the abstraction leaks. The artifact ownership check is an application of this pattern: the artifact table is an abstraction; ownership conflicts are abstraction leaks.

A generic reviewer reads the artifact table and confirms it looks reasonable. Lovelace-as-Judge asks: "is the abstraction complete and consistent?" — a formally different question.

---

## 5. Case Study: Thompson as Scout — Evidence-First, No Speculation

### 5.1 Context

**[A]** A Thompson-as-Scout agent was tasked with auditing evidence claims across swarm task descriptions — specifically, flagging any task description that claimed an outcome without specifying the evidence that would confirm it.

The Thompson persona was selected because Thompson's documented engineering philosophy — "when in doubt, don't" and a deep skepticism toward any system whose security depends on trusting the user — maps to the PRIME_TRUTH requirement in this system: every claim must be backed by executable evidence, not narrative confidence.

### 5.2 The Evidence-First Pattern

**[A]** Thompson-as-Scout applied a simple but powerful filter to each task description:

For every claim of the form "X will Y," ask: "What artifact would confirm this, and does the task require producing that artifact?"

If the task requires Y but does not require the artifact that proves Y, the task is under-specified from an evidence standpoint.

Applied to the swarm task descriptions, this identified:

- 3 tasks that claimed "verify consistency" without specifying what consistency check to run
- 2 tasks that claimed "confirm X exists" without specifying a file path or search command
- 1 task that claimed "ensure no conflicts" without defining what constitutes a conflict

**[A]** In each case, the fix was straightforward: add a required artifact (a search output, a file listing, or a diff) that constitutes evidence for the claimed verification. Generic review had passed all six tasks as "clear enough."

### 5.3 Why This Is a Thompson Pattern

**[B]** Thompson's security engineering philosophy (documented in his 1984 Turing Award lecture "Reflections on Trusting Trust") centers on: trust no component you cannot verify. The Scout role operationalizes this: trust no claim that lacks a verifiable artifact. The persona activates the exact attention pattern the role requires.

---

## 6. Failure Modes of Persona-Based Review

### 6.1 Persona Capture

**[B]** Persona capture occurs when the review agent becomes so committed to the persona's perspective that it misses problems outside the persona's domain of concern. A Thompson-as-Scout agent focused on evidence artifacts may miss a subtle logic error in the skill's FSM transitions because that is not Thompson's documented domain of concern.

**[B]** The mitigation: use persona-based review as a complement to, not replacement for, generic review and scorecard-based review. The persona provides additional coverage; it does not provide complete coverage.

### 6.2 Persona Override

**[B]** Persona override occurs when the persona instruction is too strong, causing the agent to abandon the actual task in favor of producing in-character responses that entertain without reviewing. This can happen when the persona instruction is so detailed that the agent spends more context tokens on persona consistency than on the artifact under review.

**[B]** The mitigation: keep persona instructions minimal and task-focused. "Review this as Turing would, focusing on formal specification gaps" is more effective than a detailed description of Turing's personality and biography.

### 6.3 Persona Mismatch

**[C]** Persona mismatch occurs when the selected persona's known concerns are orthogonal to the artifact's failure modes. A Lovelace persona applied to a systems security audit will produce different insights than a Thompson persona — but they may be less relevant to the security domain.

**[C]** Persona selection should be driven by the artifact's domain and the known concerns of candidate personas. A simple matching heuristic: what is the primary invariant that must hold for this artifact? Select the persona whose documented concerns most directly address that invariant.

---

## 7. Protocol: How to Select and Constrain Personas

### 7.1 Selection Criteria

**[B]** Effective persona selection for review tasks requires:

1. **Domain relevance:** The persona's known intellectual concerns must overlap with the artifact's failure mode space.
2. **Complementarity:** If multiple personas are used, their concern domains should be disjoint, maximizing collective coverage.
3. **Documentation depth:** The persona must be well-documented in training data, so the LLM's representation of the persona is reliable.
4. **Tractability:** The persona's intellectual style must be expressible in a brief instruction, not requiring extensive context.

### 7.2 Canonical Persona Assignments

**[B]** Based on the case studies above, the following canonical persona assignments are recommended for Software 5.0 swarm review:

| Role | Persona | Primary concern | Failure modes detected |
|---|---|---|---|
| Skeptic | Alan Turing | Formal specification, decidability | Unenforceable constraints, ambiguous halting conditions |
| Judge | Ada Lovelace | Structural consistency, notation | Abstraction leaks, ownership conflicts, notation inconsistency |
| Scout | Ken Thompson | Evidence grounding, trust | Claims without artifacts, implicit trust assumptions |
| Architect | Claude Shannon | Information-theoretic efficiency | Redundancy, information loss, compression failures |
| Adversary | Edsger Dijkstra | Correctness proofs, edge cases | Invariant violations, off-by-one conditions, boundary failures |

### 7.3 Persona Constraint Template

**[A]** The effective instruction format used in this repo's swarm system:

```
You are [NAME] reviewing [ARTIFACT].
Your primary concern: [CONCERN].
For every claim in this artifact, ask: [QUESTION THAT PERSONA WOULD ASK].
Output format: list of findings as falsifiers — conditions under which the claim fails.
Do not stay in character beyond what is necessary to apply [CONCERN].
```

This format keeps the persona focused on the review task while activating the concern-domain attention shift.

---

## 8. Conclusion

**[B]** Persona-based review is a practical technique for surfacing failure modes that generic review systematically misses. The mechanism is not mysterious: named historical personas with documented intellectual styles activate different attention patterns in LLMs, producing reviews biased toward the persona's domain of concern.

**[A]** Three case studies from this repo's swarm system demonstrate this empirically. Turing found 8 falsifiers that generic review missed. Lovelace found a race condition in artifact ownership. Thompson identified 6 tasks with evidence-free claims.

**[B]** The protocol is simple: select personas whose concern domains are relevant to the artifact's failure mode space and complementary to each other; keep persona instructions minimal and task-focused; treat persona-based review as supplementary to, not replacing, scorecard and rung-gate review.

**[C]** The long-term vision: a canonical set of persona agents that every swarm run instantiates as part of the SOCRATIC_REVIEW phase — not as optional extras, but as required coverage for promotion claims.

---

## References

- `papers/05-software-5.0.md` — Software 5.0 theoretical foundation
- `papers/24-skill-scoring-theory.md` — skill quality scorecard (complementary technique)
- `skills/phuc-swarms.md` — multi-agent orchestration (context for swarm review phases)
- `skills/prime-wishes.md` — artifact reviewed in case study 1
- `papers/00-index.md` — artifact ownership table reviewed in case study 2
- Thompson, K. (1984). "Reflections on Trusting Trust." ACM Turing Award Lecture.
- Lovelace, A. (1843). Notes on Menabrea's "Sketch of the Analytical Engine."

---

**Auth: 65537** (project tag; see `papers/03-verification-ladder.md`)
**License:** Apache 2.0
**Citation:**
```bibtex
@software{stillwater2026_persona_review,
  author = {Truong, Phuc Vinh},
  title = {Persona-Based Review: Why Named Agents Surface Failure Modes That Generic Review Misses},
  year = {2026},
  url = {https://github.com/phuctruong/stillwater/papers/25-persona-based-review-protocol.md},
  note = {Auth: 65537}
}
```
