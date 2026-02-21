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
3. `99-claims-and-evidence.md` (claim hygiene policy)

## Reproducibility (What Reviewers Can Run Today)

1. Root notebooks:
   - `HOW-TO-OOLONG-BENCHMARK.ipynb`
   - `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
   - `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
2. Unit tests:
   - `cli/tests/` (67 tests; run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest`)
   - `imo/tests/` (notebook QA harness)

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

---

## Reserved Slots (Planned; Not Yet Written)

Papers 13-17 are reserved for planned topics. These slots are intentionally left open for future contributors. Each stub includes a one-line rationale for why the topic belongs in this index.

| Number | Status | Planned Topic | Rationale |
|---|---|---|---|
| 13 | RESERVED | Multi-agent coordination theory | Swarms require a formal model of coordination, conflict resolution, and phase ownership — not yet formalized beyond the operational skill. |
| 14 | RESERVED | Skill portability across LLM families | As the community database grows, portability guarantees across model families (not just one vendor) require a formal treatment. |
| 15 | RESERVED | Benchmark gaming and adversarial skills | A systematic account of how adversarial skill design can game benchmarks, and the countermeasures the verification ladder provides. |
| 16 | RESERVED | Energy-efficient skill composition | Skill composition has a token-cost profile; this paper would formalize the energy/cost model for composition decisions at scale. |
| 17 | RESERVED | Formal verification of skill FSMs | Skill FSMs are currently checked by review; a formal verification approach (model checking, type theory) would strengthen the never-worse guarantee. |

---

## Extension Economy Papers (Solvers C: Software 5.0 Extensions)

Papers 23-26 form a cluster on the economics, quality theory, review methodology, and community governance of the Software 5.0 skill library.

| Number | File | Title | Summary |
|---|---|---|---|
| 23 | `23-software-5.0-extension-economy.md` | The Extension Economy | Skills and recipes as compression artifacts with increasing returns; compression gain metric; community network effects; failure modes (skill rot, recipe staleness, compatibility drift). |
| 24 | `24-skill-scoring-theory.md` | Binary Scorecards for Skill Quality | 5-criteria binary scorecard (FSM, forbidden states, verification ladder, null/zero handling, output contract); empirical results across 9 skills in this repo; model-agnosticism argument. |
| 25 | `25-persona-based-review-protocol.md` | Persona-Based Review | Named historical personas (Turing, Lovelace, Thompson) as review agents; three case studies from swarm runs; failure modes (persona capture, override, mismatch); canonical persona assignment table. |
| 26 | `26-community-skill-database.md` | The Stillwater Community Database | Design principles for a distributed skill library: sha256 identity + MANIFEST.json, quality gate at submission, never-worse versioning, canonical review agents; comparison to npm, PyPI, crates.io; open problems. |

---

## Community + Ecosystem Papers

| Number | File | Title | Summary |
|---|---|---|---|
| 27 | `27-bootstrapping-knowledge-commons.md` | Bootstrapping a Knowledge Commons with AI | How AI-bootstrapped content + human curation creates a self-reinforcing community knowledge base; MoltBot integration; submission quality gates. |
| 28 | `28-the-cheating-theorem.md` | The Cheating Theorem | Formal account of how verification-free AI systems structurally reward hallucination; the Stillwater claim hygiene policy as a countermeasure. |
| 29 | `29-software-5-0-in-one-session.md` | Software 5.0 in One Session | Case study: building a verification-grade software system in a single AI-orchestrated session; artifacts, rungs, and lessons. |
| 30 | `30-moltbot-community-platform.md` | The AI-Native Community Platform | Design and launch of the Stillwater Store: Apple App Store model for AI skills; account-gated submissions; human review queue; ecosystem lock-in via verification standards. |
| 31 | `31-universal-math-solver-architecture.md` | The Universal Math Solver Architecture | 5-phase PHUC pipeline (Scout→Forecast→Judge→Solver→Skeptic); CPU deterministic lane + LLM-only lane; self-learning oracle memory; 395/396 IMO corpus cold-start convergence in 2 iterations on llama3.1:8b. |
