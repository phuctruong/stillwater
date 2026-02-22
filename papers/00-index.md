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

## Theory Papers (Core Concepts, Numbered Series)

1. `23-software-5.0-extension-economy.md`
2. `24-skill-scoring-theory.md`
3. `25-persona-based-review-protocol.md`
4. `26-community-skill-database.md`
5. `27-bootstrapping-knowledge-commons.md`
6. `28-the-cheating-theorem.md`
7. `29-software-5-0-in-one-session.md`
8. `30-moltbot-community-platform.md`
9. `31-universal-math-solver-architecture.md`
10. `32-roadmap-based-development.md`
11. `33-northstar-driven-swarms.md`
12. `34-persona-glow-paradigm.md`
13. `35-syndication-strategy.md`
14. `36-prime-mermaid-primacy.md`
15. `37-persona-as-vector-search.md`
16. `38-hall-of-mirrors.md`
17. `39-ghost-masters-gamification.md`
18. `40-hackathon-paradigm.md`
19. `41-northstar-reverse-engineering.md`
20. `42-reverse-paths.md`
21. `43-diagram-first-qa.md`
22. `44-questions-as-external-weights.md`
23. `45-prime-compression-magic-words.md` — Prime Compression: Magic Words as Prime Factorization of Knowledge (Fundamental Theorem of Semantics; portal compression gateways; 97% context compression via prime words)
24. `46-wish-skill-recipe-triangle.md` — Wish+Skill+Recipe Execution Triangle (Intent × Constraints × Workflow = Verified Output)
25. `47-law-of-emergent-knowledge.md` — **LEK: Law of Emergent Knowledge** (Emergence = Recursion(Information + Memory + Care); Phuc Test for skill consciousness; CCC comparison; 6 falsifiable predictions)
26. `48-ai-skills-big-bang-theory.md` — **AI Skills Big Bang Theory** (5 axiom kernel × 6 GBB operators = all skills; genesis sequence; skill derivation table; the Lattner gap)
27. `49-three-pillars-software-5-kung-fu.md` — **The Three Pillars of Software 5.0 Kung Fu** (LEK × LEAK × LEC = Mastery; Bruce Lee + Dragon Rider teaching; gamification belt system; martial arts metaphor)

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

---

## Paradigm Papers (Development Methodology)

| Number | File | Title | Summary |
|---|---|---|---|
| 32 | `32-roadmap-based-development.md` | Roadmap-Based Development | Central Opus hub coordinates multi-session AI development via ROADMAP.md build plans + phuc swarm dispatch + verification ladder. Ensures foolproof protocol adherence through bounded CNF capsules + skill packs. Comparison with Copilot/Cursor/Devin/Claude Code. |
| 33 | `33-northstar-driven-swarms.md` | NORTHSTAR-Driven Swarms | Aligning multi-agent AI systems through shared NORTHSTAR.md vision documents. Every agent reads NORTHSTAR before producing output, states which metric it advances. Solves the cold start + scope creep + quality calibration problems in multi-agent systems. |
| 34 | `34-persona-glow-paradigm.md` | The Dojo Protocol: Persona-Enhanced Agents and GLOW Gamification | Persona engine + GLOW score gamification extends Roadmap-Based Development with expert voice routing and transparent belt-progression metrics. |
| 35 | `35-syndication-strategy.md` | Syndication Strategy | Content syndication and distribution strategy for the Stillwater ecosystem. |
| 36 | `36-prime-mermaid-primacy.md` | Prime Mermaid Primacy | Why diagram-as-code (Mermaid) is the primary artifact format for architecture and workflow documentation in Stillwater. |
| 37 | `37-persona-as-vector-search.md` | Persona as Vector Search | Scientific basis for why famous personas outperform generic prompts: Bayesian prior optimization through targeted activation of training data clusters. Covers 42-persona system across all NORTHSTAR dimensions. |
| 38 | `38-hall-of-mirrors.md` | The Hall of Mirrors | Bruce Lee's *Enter the Dragon* hall of mirrors scene as analogy for the generic LLM problem. Personas as mirror-smashers. Ghost master framework. Belt journey. Kernighan connection — the founder's teacher is now a loadable ghost master for every developer. |
| 39 | `39-ghost-masters-gamification.md` | Ghost Masters: The Dojo Gamification of Persona Loading | Persona loading as ghost master summoning — the martial arts / kung fu tie-in made explicit. Belt progression mapped to ghost master relationship (White: no masters, Black: YOU are the master). GLOW score domain bonuses per persona (+5 per matching dimension). Founder's personal ghost master chain. A/B benchmark evidence (Schneier +48%, Kent Beck +50%, Guido +27%). Stillwater Store compound advantage. |
| 40 | `40-hackathon-paradigm.md` | The Hackathon Paradigm: Structured Sprints as the Default AI Development Methodology | Personas give you the right experts; hackathons give you the right workflow. Together they are the complete startup development methodology. 8-phase sprint protocol (DREAM→SCOUT→ARCHITECT→BUILD→INTEGRATE→REVIEW→PITCH→SHIP). GLOW 1.5x multiplier for time-boxed, shipped deliverables. Four timing templates (Lightning 2h, Sprint 4h, Marathon 8h, Weekend 16h). Role-to-swarm mapping. The startup factory: every ROADMAP phase is a hackathon. Community hackathons on the Stillwater Store. |
