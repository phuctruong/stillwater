# Papers Index (Repo-Backed, Peer-Reviewable)

This directory is the documentation spine for the project described in `MESSAGE-TO-HUMANITY.md`.

This index is intentionally conservative: it links only to papers that exist in this repository today, and it frames "verification" as what can be replayed and inspected by contributors.

## Core Papers (Concepts Used In The Root Notebooks)

1. `01-lane-algebra.md` - epistemic typing (what counts as evidence)
2. `02-counter-bypass.md` - CPU-first exact aggregation (OOLONG)
3. `03-verification-ladder.md` - 641 -> 274177 -> 65537 (rungs as evidence strength)
4. `04-red-green-gate.md` - dual-witness verification for patches
5. `05-software-5.0.md` - skills, recipes, artifacts (open-system engineering)

## Applied Papers (Mapped To Implementations In This Repo)

1. `06-solving-hallucination.md`
2. `07-solving-counting.md`
3. `08-solving-reasoning.md`
4. `09-solving-data-exhaustion.md`
5. `10-solving-context-length.md`
6. `11-solving-generalization.md`
7. `12-solving-alignment.md`
8. `18-solving-energy-crisis.md`
9. `19-solving-security.md`
10. `20-oolong-proof.md`

## System Notes (Operational / Architecture)

1. `21-phuc-swarms-context-isolation.md`
2. `22-how-we-solved-ai-scalability.md`

## Reproducibility (What Reviewers Can Run Today)

1. Root notebooks:
   - `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`
   - `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
   - `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
2. Unit tests:
   - `tests/phuc_orchestration/`

Note: if a paper makes empirical claims, it should link to a runnable script or notebook in this repo that reproduces the claim, or it should label the claim as a hypothesis or TODO.


## Citation

If you use Stillwater's research, please cite:

```bibtex
@software{stillwater2026,
  author = {Truong, Phuc Vinh},
  title = {Stillwater OS: Solving the 15 Fundamental AGI Blockers},
  year = {2026},
  url = {https://github.com/phuctruong/stillwater},
  note = {Auth: 65537}
}
```

**For individual papers, see citations in each file.**

---

## Open Science (What Is True Today)

- ✅ **Open access**: all content in this repo is publicly readable.
- ✅ **Living documents**: papers may change as code + evidence evolves.
- ✅ **Community review**: issues/PRs are the review mechanism.
- ⚠️ **Reproducibility**: some claims are backed by runnable notebooks here; numeric performance claims should be treated as hypotheses unless reproduced in this repo and linked.
- ⚠️ **Preprints**: this repo does not claim an arXiv preprint unless a paper explicitly links to one.

---

## Contact

- **Author:** Phuc Vinh Truong ([phuc.net](https://phuc.net))
- **Questions:** Open an issue on GitHub
- **Collaborations:** Email via GitHub profile
- **Tips:** [ko-fi.com/phucnet](https://ko-fi.com/phucnet) 🙏

**I work for tips. Humanity wins.**
