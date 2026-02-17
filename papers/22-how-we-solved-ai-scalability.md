# How We Approach Scalability: Orchestration, Artifact Discipline, and Fail-Closed Defaults

**Status:** Draft (open-source, repo-backed where referenced)  
**Last updated:** 2026-02-17  
**Scope:** A pragmatic scalability story: make systems reliable by constraining outputs, isolating context, and requiring evidence artifacts.  
**Auth:** 65537 (project tag)

---

## Abstract

"Scalability" is not only bigger models.

In practice, many failures are process failures:
- too much context (attention rot)
- ambiguous task routing
- unverifiable claims

This repo focuses on orchestration patterns that scale reliability:
- context isolation
- fail-closed prompting
- phase artifacts
- explicit claim hygiene

---

## Claim Hygiene

This paper intentionally avoids numeric success rates and model-vs-model tables unless reproduced by an in-repo harness.

See `papers/99-claims-and-evidence.md`.

---

## Reproduce / Verify In This Repo

- Orchestration notebook:
  - `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
- Skills discipline (coding):
  - `skills/prime-coder.md`
- Policy:
  - `papers/99-claims-and-evidence.md`

---

## 1. The Scalability Problem (Operational)

As tasks scale, two things break:
- the model's implicit state (it forgets constraints)
- humans lose the ability to audit what happened

The remedy is not just "more reasoning"; it is stronger structure.

---

## 2. The Pattern: Phase-Structured Work

```mermaid
flowchart LR
  D["DREAM: clarify"] --> F["FORECAST: predict failure modes"] --> DC["DECIDE: choose route"] --> A["ACT: implement"] --> V["VERIFY: prove with artifacts"]
```

This pattern scales because each phase produces artifacts that can be reviewed independently.

---

## 3. Fail-Closed Defaults

When routing is ambiguous:
- prefer returning "UNKNOWN" with required witnesses
- avoid confident guesses

This reduces catastrophic regressions in long tool-using sessions.

---

## 4. Why This Is a Better Scalability Story Than "More Agents"

More agents can help, but only if:
- roles are constrained
- artifacts are shared
- verification gates exist

Otherwise, you just scale confusion.

---

## 5. Limitations

- Orchestration increases process overhead.
- It requires discipline in how outputs are logged and verified.

---

## References

- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
- `papers/99-claims-and-evidence.md`
