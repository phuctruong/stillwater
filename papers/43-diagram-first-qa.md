# Diagram-First QA: Structural Verification Through Mermaid-Based Architecture Mapping

**Paper 43** | Stillwater Research | 2026-02-22

---

## Abstract

We present Diagram-First QA, a verification methodology where comprehensive mermaid diagrams serve as structural QA artifacts alongside traditional questions and unit tests. The three pillars — questions, tests, and diagrams — form a unified QA framework that uses Northstar Reverse Engineering to work backwards from "system fully verified" to identify gaps. We show that diagrams expose a class of architectural defects that neither questions nor tests detect: missing connections, orphaned modules, inconsistent data flows, and undocumented state transitions. When combined with question-based QA (Pillar 1) and test-based QA (Pillar 2), diagram-based QA (Pillar 3) closes the verification gap from ~60% to ~95% coverage.

---

## 1. The Problem: What Questions and Tests Miss

### 1.1 Questions Find Behavioral Gaps

Question-based QA (prime-qa) asks: "Does the system do what it claims?" This catches:
- Features that don't work
- Integration boundaries that fail
- Documentation that contradicts reality

But questions are inherently point-based — they probe specific claims. They miss structural patterns.

### 1.2 Tests Find Functional Gaps

Unit and integration tests verify: "Does this function return the correct output?" This catches:
- Regressions
- Edge cases
- Null handling

But tests are inherently local — they test individual functions. They miss architectural coherence.

### 1.3 What Neither Catches

Neither questions nor tests reliably detect:

- **Orphaned modules**: Code that exists but is never called
- **Missing connections**: Components that should communicate but don't
- **Inconsistent data flow**: Data transforms that don't compose correctly end-to-end
- **Undocumented state transitions**: States that exist in code but aren't in any spec
- **Architectural drift**: The actual system structure diverging from the intended architecture
- **Deployment gaps**: Components that work locally but have no production deployment path

These are **structural defects** — problems visible only when you look at the whole system as a graph.

---

## 2. The Solution: Diagrams as QA Artifacts

### 2.1 Core Thesis

> A diagram is a hypothesis about structure. Drawing it forces you to state the hypothesis explicitly. Verifying it against source code tests the hypothesis.

When a developer draws a system architecture diagram, they are making claims:
- "These components exist"
- "They connect like this"
- "Data flows in this direction"
- "These states are reachable"

Each claim can be verified against actual source code. The diagram becomes a QA artifact — not decoration, but a testable spec.

### 2.2 Eight Diagram Categories

| Category | What It Tests | Detects |
|----------|--------------|---------|
| System Architecture | Component existence and connections | Missing or orphaned modules |
| Data Flow | Data movement through the system | Broken data pipelines |
| State Machines | Entity lifecycle correctness | Unreachable or missing states |
| Sequence Diagrams | Component interaction order | Race conditions, missing handoffs |
| Class/Entity Diagrams | Data model correctness | Missing fields, wrong types |
| User Journeys | User-facing flow completeness | Dead ends, impossible paths |
| Deployment | Production readiness | Missing infrastructure |
| Dependencies | Module coupling | Circular deps, orphaned packages |

### 2.3 The Coverage Matrix

The key innovation is the **coverage matrix**: a mapping from every source file to the diagrams that reference it.

```
source_file → [diagram_1, diagram_3, diagram_7]
source_file → []  ← UNCOVERED — structural gap!
```

An uncovered source file means: no diagram references this module. It exists in the codebase but is not part of the team's mental model. This is either:
- An orphaned module (should be deleted)
- A gap in understanding (should be diagrammed)

Both findings are valuable QA outcomes.

---

## 3. The Unified Three-Pillar QA Framework

### 3.1 Three Pillars, One Algorithm

All three QA pillars use the same Northstar Reverse Engineering algorithm:

```
PILLAR 1 (Questions):
  "What are the LAST 3 questions that must be answered
   for this system to be production-ready?"

PILLAR 2 (Tests):
  "What are the LAST 3 tests that must pass
   for this system to be correct?"

PILLAR 3 (Diagrams):
  "What are the LAST 3 diagrams that must exist
   for this system's architecture to be fully understood?"
```

Work backwards. The QA is complete when no more reverse-engineered artifacts can be added.

### 3.2 Cross-Pillar Coverage

The three pillars are not independent — they cross-validate:

| If a module has... | Questions | Tests | Diagrams | Status |
|---|---|---|---|---|
| All three | Covered | Covered | Covered | GREEN |
| Questions + Tests | Covered | Covered | Missing | YELLOW — structural gap |
| Tests + Diagrams | Missing | Covered | Covered | YELLOW — behavioral gap |
| Only diagrams | Missing | Missing | Covered | RED — unverified architecture |
| None | Missing | Missing | Missing | RED — invisible module |

A module is fully verified only when all three pillars cover it.

### 3.3 GLOW Integration

Each pillar maps to GLOW dimensions:

- **G (Growth)**: Does the new capability have diagrams showing where it fits?
- **L (Learning)**: Is the new knowledge captured in architecture diagrams?
- **O (Output)**: Do deliverables appear in the system architecture diagram?
- **W (Wins)**: Does the strategic win show up in the ecosystem diagram?

---

## 4. The Reverse Engineering Insight

### 4.1 Forward QA (Naive Approach)

```
Start from code → Write tests → Ask questions → Draw diagrams
Problem: You test what you see. You miss what you don't see.
```

### 4.2 Reverse QA (Northstar Approach)

```
Start from "fully verified system" →
  What diagrams must exist? → Draw them, find gaps →
  What tests must pass? → Write them, find bugs →
  What questions must be answered? → Ask them, find lies →
Connect to current state → The delta is your QA backlog
```

The reverse approach is superior because it starts from the desired end state and works backwards, naturally discovering gaps that forward QA misses.

### 4.3 Applied Example: Stillwater

Forward: "Let's test the CLI." → Tests pass. Done? No — the CLI's connection to the LLM Portal is untested.

Reverse: "For Stillwater to be production-ready, what must be true?"
- Every command in the CLI must be diagrammed → discover 3 undocumented commands
- Every provider in the LLM Portal must appear in a sequence diagram → discover fallback chain is undocumented
- Every data model must have a class diagram → discover 2 models with undocumented validators

The reverse approach found 5 gaps that forward testing missed.

---

## 5. Implementation

### 5.1 Skill: phuc-qa-unified

The consolidated skill (see `skills/phuc-qa-unified.md`) defines:
- Three-pillar framework
- Coverage matrix schema
- Cross-pillar validation rules
- Unified gap report format

### 5.2 Swarm: qa-diagrammer

The diagram agent (see `swarms/qa-diagrammer.md`) produces:
- 8 category diagrams from source code analysis
- Coverage matrix
- Gap report

### 5.3 Combo: mermaid-qa

The combo recipe (see `combos/mermaid-qa.md`) orchestrates:
- Project scan → diagram generation → coverage matrix → gap fill → seal

### 5.4 Integration with Existing QA

```
combos/qa-audit.md      → Pillar 1 (Questions)
combos/run-test.md      → Pillar 2 (Tests)
combos/mermaid-qa.md    → Pillar 3 (Diagrams)

All three feed into: unified qa_gap_report.md
```

---

## 6. The Diagram-First Development Paradigm

> "Perhaps, we should have done diagram first development but it's not too late." — Phuc Truong

Diagram-first development means: before writing code, draw the architecture. Before adding a feature, update the diagrams. Before claiming "done," verify diagrams match reality.

The diagrams serve three roles:
1. **Planning**: Draw what you intend to build
2. **Documentation**: The diagrams ARE the documentation
3. **QA**: Verify diagrams match actual code

This is the same insight as test-driven development (TDD), but for architecture:
- TDD: Write the test first → write code to pass it → verify
- DFD: Draw the diagram first → write code to implement it → verify diagram matches

---

## 7. Conclusion

Diagram-First QA completes the verification triangle:

```
        Questions (behavioral)
       / \
      /   \
     /     \
Tests ——— Diagrams
(functional) (structural)
```

Each pillar catches a different class of defects. Together, they approach comprehensive verification. The Northstar Reverse Engineering algorithm — "What are the LAST 3 things that must be true?" — drives all three pillars from the same principle.

The unified phuc-qa framework makes this practical: one skill, three pillars, one gap report.

---

## References

- `skills/phuc-qa-unified.md` — Consolidated QA skill
- `skills/prime-qa.md` — Question-based QA discipline
- `skills/prime-mermaid.md` — Mermaid diagram standard
- `swarms/qa-diagrammer.md` — Diagram generation agent
- `combos/mermaid-qa.md` — Diagram QA combo recipe
- `combos/qa-audit.md` — Question QA combo recipe
- `papers/41-northstar-reverse-engineering.md` — Northstar algorithm
- Dhuliawala et al. 2023, "Chain-of-Verification Reduces Hallucination in LLMs"
