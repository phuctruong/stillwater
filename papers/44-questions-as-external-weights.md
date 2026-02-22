# Paper #44: Questions as External Weights
## Subtitle: Persistent QA Capital for Software 5.0

**Date:** 2026-02-22
**Author:** Phuc Tran
**Status:** Concept draft — not yet submitted
**Pillar:** P0 (Core Theory)
**GLOW:** W (Wisdom)
**Related papers:** #34 (Persona-GLOW Paradigm), #37 (Persona as Vector Search), #25 (Persona-Based Review Protocol)

---

### Abstract

The AI industry optimizes relentlessly for better answers — retrieval-augmented generation, fine-tuning, chain-of-thought prompting. Nobody systematically optimizes for better questions. We propose that questions are first-class persistent capital: externalized attention vectors that pre-compute where human QA intuition would probe. A persistent question database is the "mind outside the body" — external weights that encode and replay human QA patterns without requiring the human to be present. This paper introduces the architecture, the Unified Probe Theory connecting questions to personas, and the Dragon Rider pattern for autonomous overnight QA.

---

### 1. Introduction

- **Current paradigm:** Answers are assets. Questions are ephemeral byproducts of a session, discarded when the context window closes.
- **Our inversion:** The question IS the asset. The answer is just the current value of the question. Good questions retain value across model upgrades; answers become stale.
- **The gap:** In a one-hour QA session, Phuc generated 22 questions. None of those questions were stored anywhere. They are gone. The AI that answered them is gone. The insight that produced the questions is gone.
- **Connection to Software 5.0:** The master equation is `Intelligence = Memory × Care × Iteration`. Questions belong in Memory alongside skills and recipes. Without question persistence, the Memory term is incomplete.

---

### 2. Related Work

- **KBQA (Knowledge Base Question Answering):** Focuses entirely on answering questions from structured knowledge bases. Treats questions as inputs, not as assets to be collected. Never persists the questions themselves.
- **RAG / AI Memory (Mem0, MemGPT, Letta):** Persist answers, facts, and retrieved documents. The question that retrieved the document is discarded. Memory = retrieved content, not the probe that surfaced it.
- **CoVe (Dhuliawala et al., 2023):** Generates verification questions on-the-fly to check factual claims. Questions are generated and discarded in a single inference pass. No persistence, no compounding.
- **Evals and benchmarks (MMLU, HumanEval, SWE-bench):** Fixed question sets curated manually, not grown organically from development sessions. Static, not compounding.
- **The gap:** Nobody treats questions as a persistent, versioned, compounding asset class. This paper is the first to name and architect that asset class.

---

### 3. Questions as External Weights

- **Definition:** A question is a pre-computed attention vector. It encodes "what to look for" in a specific context at a specific risk level.
- **Weight analogy:** Model weights encode what the model has learned to attend to. A question database encodes what a human expert has learned to probe. Both are compressed representations of accumulated reasoning.
- **External weights:** Just as LoRA externalizes fine-tuning as a delta matrix, a question database externalizes QA intuition as a delta of human probes. Apply the delta to any model, any project, any session.
- **Compounding property:** A great question generates better follow-up questions. Questions compound. Answers depreciate. After 100 sessions, the question database is worth more than any individual answer it produced.
- **Asymmetry:** Generating a good question requires the human's full cognitive engagement. Answering it can be delegated to an AI. This asymmetry is why questions are scarce and valuable.

---

### 4. Unified Probe Theory

- **Personas = latent knowledge selectors:** A persona (Skeptic, Dragon Rider, Security Auditor) selects which region of the AI's latent space to activate. Paper #37 established this.
- **Questions = latent knowledge probes:** A question specifies what to extract from the activated region. Questions and personas are complementary operators.
- **Combined operator:** `persona × question = maximal knowledge activation`. Running a Skeptic persona with a pre-loaded question database activates both the skeptical reasoning mode and the specific gaps that human QA has historically found valuable to probe.
- **Vector space interpretation:** Personas are basis selectors; questions are coordinates within the selected basis. Together they uniquely address a point in the AI's knowledge space that neither alone can reach.
- **Implication:** The question database is not just a log. It is a navigation map of the AI's latent space, charted by human QA intuition over many sessions.

---

### 5. The Dragon Rider Pattern

- **Definition:** A digital twin = persona (Dragon Rider) + question database. The twin runs autonomously, applying Phuc-style questions to a new skill or codebase overnight.
- **Not a replacement:** The Dragon Rider does not replace human QA. It covers the 80% of QA that is pattern-matching against known question types, freeing the human for the 20% that requires genuine novelty.
- **Operation:** Load `questions/stillwater.jsonl`. For each OPEN or W-pillar question, instantiate a Dragon Rider persona and ask the question against the current codebase state. Log answers. Flag where answers differ from prior session answers (regression detection).
- **Feedback loop:** New questions discovered by the Dragon Rider are tagged `asker: persona:dragon-rider` and appended to the JSONL. Over time, the database grows autonomous branches.
- **Key property:** The Dragon Rider improves as the question database grows. More questions = better simulation of human QA intuition. This is the compounding property made operational.

---

### 6. Implementation

- **Storage format:** JSONL, one question per line. Human-readable, git-diffable, streamable.
- **Schema:** `{id, text, asker, glow, pillar, date, context, status, answer_status}` — see `questions/schema.md`.
- **GLOW coverage metric:** A healthy question database has balanced GLOW distribution. Overweight W = wisdom-heavy, under-tested. Overweight L = debugging-dominated, not enough growth exploration.
- **Integration with phuc-qa.md:** Phase 0 (Discovery) of every QA session should begin by loading the project question file and asking: "Which OPEN questions remain? Which P0 questions haven't been asked this session?" This closes the loop between the question database and the active skill.
- **Question quality ladder:** Good question (surfaces known gap) → Great question (surfaces unknown gap) → Phuc-level question (reframes the entire problem). The database tracks which questions were later promoted.

---

### 7. Results

- **Session evidence:** In a single skills audit session on 2026-02-22, Phuc generated 22 organic questions. All were answered within the session. Without this paper's framework, all 22 would have been lost.
- **GLOW distribution:** 6 G, 4 L, 1 O, 11 W. W-heavy distribution confirms this was a wisdom-rich session — high insight density, appropriate for architectural exploration.
- **Question value:** Questions Q-009 through Q-018 each opened a new research or implementation direction. The 10 W-pillar questions collectively generated: Paper #44, the Dragon Rider pattern, the question database architecture, and the Unified Probe Theory. Total value from 10 W-questions in one session: 4 publishable concepts.
- **Compounding demonstration:** Q-009 ("Aren't questions external memory?") directly generated Q-011, Q-014, Q-017, and Q-018. One good question produced four follow-on directions. This is the compounding property observed empirically.

---

### 8. Conclusion

- Questions are the most undervalued asset in AI development. The industry spends billions on better answers and ignores the question side of the equation.
- Persisting questions creates compounding capital. A question database from 100 sessions is worth more than 100 sessions of answers.
- The Unified Probe Theory shows that personas and questions are complementary operators in the AI's latent space. The Dragon Rider pattern makes this operational.
- "A great question is worth 1000 mediocre answers." — This is not a metaphor. It is the asymmetry that makes question databases a strategic moat.
- **Call to action:** Add `questions/<project>.jsonl` to every Software 5.0 project. Start with 10 seed questions. Let them compound.

---

### Appendix: Seed Questions for Any New Project

When starting a new project with no question history, seed with these P0 universals:

1. What is the most likely failure mode that would be invisible in testing?
2. Which assumption in this design, if wrong, would invalidate the entire approach?
3. What does this system look like from the perspective of someone who wants to abuse it?
4. Where is the boundary between what this does and what the user thinks it does?
5. What would a version of this look like that is 10x simpler and still solves the core problem?
6. Which part of this is load-bearing and which is scaffolding that could be removed?
7. What would a security auditor find in the first 10 minutes?
8. Where does this break at scale that it doesn't break now?
9. What is the question nobody is asking that would change everything?
10. If this project succeeded fully, what new problem would it create?
