# Solving Generalization: Constrain, Decompose, Verify (Operational)

**Status:** Draft (open-source, repo-backed where referenced)  
**Last updated:** 2026-02-17  
**Scope:** Practical techniques for improving generalization in tool-using systems.  
**Auth:** 65537 (project tag)

---

## Abstract

"Generalization" failures often come from asking a probabilistic generator to behave like a deterministic program.

This paper describes an operational alternative:
- constrain the problem into a stable schema
- decompose into deterministic subroutines where possible
- verify behavior with tests and replayable artifacts

This repo demonstrates these ideas in notebooks and skills. It does not claim universal 100% generalization on external benchmarks without an in-repo harness.

---

## Claim Hygiene

- No external benchmark percentages are claimed in this paper.
- Any future benchmark tables should ship with a runnable harness + logs.

See `papers/99-claims-and-evidence.md`.

---

## Reproduce / Verify In This Repo

- Claim typing: `papers/01-lane-algebra.md`
- Verification framing: `papers/03-verification-ladder.md`
- Example applications:
  - `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
  - `HOW-TO-MATH-OLYMPIAD.ipynb`

---

## 1. What "Generalization" Means Here

In this repo, "generalization" means:
- the system continues to work when surface form changes
- it fails closed when assumptions break
- it can explain its own limits and required witnesses

---

## 2. Three Techniques

### 2.1 Constrain via schema

Instead of letting the model invent structure, require structure.

Example: if a task can be expressed as a structured query, force the model to output that query and validate it.

### 2.2 Decompose into deterministic subroutines

Whenever a subproblem is deterministic (parsing, aggregation, arithmetic), route it to deterministic code.

This is the core of the Counter Bypass pattern for aggregation:
- `papers/02-counter-bypass.md`

### 2.3 Verify with replayable artifacts

Generalization claims are brittle without artifacts:
- tests
- fixed inputs
- logged tool outputs

---

## 3. Why This Helps

- Constraining reduces the space of possible wrong answers.
- Deterministic subroutines eliminate entire error classes.
- Verification turns "it seems right" into a witness-backed statement.

---

## 4. Limitations

- Some tasks are inherently open-ended.
- Not every domain has cheap deterministic witnesses.
- Good tests are work.

The goal is not to promise perfect generalization; it is to build systems that are auditable and degrade gracefully.

---

## References

- `papers/01-lane-algebra.md`
- `papers/03-verification-ladder.md`
- `papers/99-claims-and-evidence.md`
