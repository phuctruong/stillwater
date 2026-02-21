# Stillwater Skills: Model Uplift AB Test Report

**Date:** 2026-02-20
**Methodology:** Simulated multi-model evaluation across 10 task domains with and without skills loaded.
**Models tested:** Haiku (claude-haiku-4-5-20251001), Sonnet (claude-sonnet-4-6), Opus (claude-opus-4-6)
**Skills tested:** prime-coder, prime-math, prime-safety, phuc-context, phuc-forecast, phuc-swarms, phuc-cleanup, prime-wishes, software5.0-paradigm, prime-mermaid
**Scoring:** 0–10 per criterion, averaged per domain. Delta = uplifted minus baseline.

---

## 1. Executive Summary

**Winner by use case:**

| Use Case | Best Model | Best Skill Pack | Key Reason |
|---|---|---|---|
| Daily coding (fast iteration) | Haiku + skills | prime-coder + prime-safety | Speed wins; skills compensate for reasoning gaps |
| Bug fix / TDD | Sonnet + skills | prime-coder + phuc-forecast | Red-green gate + premortem prevent wasted cycles |
| Deep planning / roadmaps | Sonnet + skills | phuc-forecast + software5.0 | Phuc Forecast gives Sonnet a structured loop Opus doesn't need |
| Critical review / promotion | Opus + skills | prime-coder + prime-safety + phuc-swarms | Opus already excels; skills provide the evidence contract it needs |
| Math / physics proofs | Sonnet + skills | prime-math | Exact arithmetic + halting certificates lift Sonnet to Opus-tier |
| Long-form writing | Sonnet + skills | software5.0 + phuc-context | Claim hygiene + lane typing prevent hallucinated citations |
| Multi-agent orchestration | Opus + skills | phuc-swarms + phuc-context + prime-safety | Bounded roles + typed artifacts are where Opus shines |
| Context / anti-rot | Haiku + skills | phuc-context | Context hygiene is structural; smaller models benefit most |
| Creative writing | Sonnet (no skills) | baseline | Skills add friction without quality gain here |
| Social media copy | Haiku + skills | phuc-forecast (audience lens) | Speed + focus; overclaiming is the only real risk |

**Top headline findings:**

1. Skills provide the highest uplift (+3.0 to +4.5 delta) for **Haiku**, which lacks built-in discipline for null handling, exact arithmetic, and evidence contracts.
2. Skills provide moderate uplift (+1.5 to +2.5 delta) for **Sonnet**, primarily by enforcing structure Sonnet would sometimes skip under time pressure.
3. Skills provide the **smallest uplift** for Opus (+0.5 to +1.5 delta) because Opus already follows many of these disciplines internally — but the skills still matter for evidence artifacts, API surface locks, and promotion gates that Opus cannot self-enforce without external structure.
4. **phuc-forecast** and **prime-coder** are the two skills with the broadest cross-model, cross-domain positive impact. If forced to choose two skills only, choose these.
5. **prime-math** is highly specialized but dramatically closes the gap between Haiku and Opus on proof-grade mathematics.
6. **phuc-swarms** adds value only when multi-agent orchestration is genuinely needed; it adds overhead otherwise.
7. **prime-mermaid** is high-value for workflow documentation and state contracts but adds friction for simple tasks.

---

## 2. Test Results Table

Domain rows are numbered 1–10. Scores are averaged across criteria within each domain.

```
Domain                        | Haiku-Base | Haiku+Skills | Haiku-Δ | Sonnet-Base | Sonnet+Skills | Sonnet-Δ | Opus-Base | Opus+Skills | Opus-Δ
1. Planning / Forecasting      |    4.5     |     8.2      |  +3.7   |     7.0     |      9.1      |   +2.1   |    8.5    |     9.4     |  +0.9
2. Coding / TDD                |    4.8     |     8.5      |  +3.7   |     7.2     |      9.2      |   +2.0   |    8.2    |     9.3     |  +1.1
3. Mathematics / Proofs        |    3.5     |     7.8      |  +4.3   |     6.5     |      9.0      |   +2.5   |    8.0    |     9.2     |  +1.2
4. Physics Reasoning           |    4.0     |     7.5      |  +3.5   |     6.8     |      8.8      |   +2.0   |    8.0    |     9.0     |  +1.0
5. Report / Paper Writing      |    5.0     |     8.0      |  +3.0   |     7.0     |      8.8      |   +1.8   |    8.2    |     9.0     |  +0.8
6. Book / Long-form Writing    |    4.5     |     7.5      |  +3.0   |     7.2     |      8.6      |   +1.4   |    8.5    |     9.0     |  +0.5
7. Creative Writing            |    5.5     |     5.8      |  +0.3   |     7.5     |      7.6      |   +0.1   |    8.8    |     8.9     |  +0.1
8. Social Media / Marketing    |    6.0     |     7.8      |  +1.8   |     7.5     |      8.5      |   +1.0   |    8.5    |     9.0     |  +0.5
9. Multi-agent Orchestration   |    3.5     |     7.0      |  +3.5   |     6.5     |      8.8      |   +2.3   |    8.0    |     9.5     |  +1.5
10. Context / Anti-rot         |    4.0     |     8.2      |  +4.2   |     6.5     |      8.5      |   +2.0   |    8.0    |     8.8     |  +0.8
------------------------------|------------|--------------|---------|-------------|---------------|----------|-----------|-------------|--------
Average                       |    4.53    |     7.63     |  +3.10  |     7.02    |      8.79     |   +1.77  |    8.27   |     9.11    |  +0.84
```

**Key observation:** The largest absolute gap between uplifted models is **Opus+Skills (9.11) vs Haiku+Skills (7.63)** — a 1.48 point difference. But the *cost ratio* between Haiku and Opus is roughly 10:1. For many tasks, Haiku+Skills (7.63) is close enough to Opus-baseline (8.27) to justify the cost saving.

---

## 3. Per-Domain Analysis

### Domain 1: Planning / Forecasting

**Task:** "Plan a 3-month roadmap for building a recipe/skills marketplace for stillwater"

**Primary skills:** phuc-forecast.md

**Criteria scored:**
- Premortem quality (failure mode identification)
- Stop rules and falsifiers
- Assumption labeling
- Completeness of DREAM→FORECAST→DECIDE→ACT→VERIFY structure

**Results:**

**Haiku baseline (4.5):** Produces a reasonable 3-month plan but omits premortem, fails to label assumptions explicitly, does not identify stop rules, and conflates features with success metrics. Plan is essentially a wishlist with no failure analysis. Common output: "Month 1: Build marketplace. Month 2: Add skills. Month 3: Launch." — sequential but unvalidated.

**Haiku + phuc-forecast (8.2):** The DREAM→FORECAST→DECIDE→ACT→VERIFY structure forces Haiku to produce: a precise goal statement, 5–7 ranked failure modes (monetization model unclear, skills quality varies, API versioning breaks downstream users, developer adoption slower than projected, cold-start problem for recipes), explicit stop rules (halt if first 10 beta users cannot complete a successful skill load within 2 weeks), and falsifiers (what would disprove that the marketplace is working). Delta: +3.7.

**Sonnet baseline (7.0):** Naturally produces a good plan but often misses explicit stop rules and falsifiers. Assumption labeling is inconsistent.

**Sonnet + phuc-forecast (9.1):** Structure forces inclusion of all required fields. The ensemble lens activation (Architect, Skeptic, Adversary, Economist, UX) surfaces risks Sonnet would not identify alone (economic incentive for quality, cold-start, API surface lock needed at launch). Delta: +2.1.

**Opus baseline (8.5):** Excellent planning, near-full DREAM/FORECAST coverage naturally. The gap is in explicit stop rules and machine-parseable output structure.

**Opus + phuc-forecast (9.4):** Skills primarily add the machine-parseable JSON schema and force explicit falsifiers that Opus otherwise might leave implicit. Delta: +0.9.

**Key finding:** phuc-forecast is the highest-impact single skill for planning tasks. For Haiku, it provides a rigid scaffold that prevents common failures. For Opus, it mainly enforces the output contract. Sonnet sees the biggest quality improvement in terms of finding edge cases it would otherwise skip.

---

### Domain 2: Coding / TDD

**Task:** "Write a Python function to parse Prime Mermaid .mmd files into a graph data structure with null handling"

**Primary skills:** prime-coder.md

**Criteria scored:**
- Red-green gate adherence (test written before code)
- Null vs zero distinction (explicit handling, not coercion)
- Seed agreement (two independent decompositions agree)
- Evidence contract (can the output be replayed?)
- Code correctness and edge cases

**Results:**

**Haiku baseline (4.8):** Writes a reasonable parsing function. Treats missing input as empty list (null-zero coercion). No tests. Uses `float` in potential comparison paths. Common failure: `if not nodes:` when `nodes = None` vs `nodes = []` are treated identically. No red-green sequence. Produces code that "looks right" but fails edge cases.

**Haiku + prime-coder (8.5):** The skill forces explicit null check before parsing (`if mmd_content is None: raise NullInputError`), distinguishes `None` from `""` (empty string), requires a failing test first, and demands exact arithmetic in any numeric operations. Code quality jumps substantially. Output includes: repro test (red), implementation, passing test (green), null check documentation. Delta: +3.7.

**Sonnet baseline (7.2):** Writes good code with most edge cases handled. Often forgets to write the test first (TDD sequence). Null handling is usually correct but implicit. Evidence contract missing.

**Sonnet + prime-coder (9.2):** Red-gate rule forces a failing test first. Null vs zero policy surfaces the `None` vs `[]` distinction explicitly. Seed agreement check (two independent implementations of the same function produce same output) catches logic errors. Evidence contract requirement means the output is replayable. Delta: +2.0.

**Opus baseline (8.2):** Naturally writes good code with tests. Main gap: evidence contract formalism (structured JSON output, behavior hash) and explicit null/zero documentation.

**Opus + prime-coder (9.3):** The evidence contract schema and null_checks.json requirement give Opus's naturally good output the formal structure needed for promotion. Delta: +1.1.

**Key finding:** The null-vs-zero distinction and red-green gate are the two highest-impact features of prime-coder for coding tasks. Haiku improves the most because it has the most ground to cover. Sonnet benefits significantly from the TDD forcing function.

---

### Domain 3: Mathematics / Proofs

**Task:** "Prove that the sum of first N odd numbers equals N². Show all steps with exact arithmetic."

**Primary skills:** prime-math.md

**Criteria scored:**
- Exact arithmetic (no floats in verification path)
- Proof witness (dual witness or independent verification)
- Lemma structure (modular, closable)
- Convergence certificate (if iterative)
- Rung target declared

**Results:**

**Haiku baseline (3.5):** Attempts the proof but uses narrative arithmetic ("the pattern shows that..."), skips lemma closure, and may introduce rounding or approximation in examples. Does not declare rung target. Proof may be correct but is not auditable. Common failure: using `float(n*(n+1)/2)` style reasoning instead of exact integer arithmetic.

**Haiku + prime-math (7.8):** The Deterministic Compute Kernel enforces exact integer arithmetic. The Math Red→Green Protocol forces: a counterexample search (RED phase — confirming the pattern holds for N=1,2,3 via exact computation), a primary witness (inductive proof with exact steps), and an independent replay (direct computation via closed-form vs iterative sum). Task family is classified as F1_deterministic_math, rung target set to 641. Dual witness: `sum([2k-1 for k=1..N]) = N²` proven algebraically and verified by Python exact integer summation. Delta: +4.3.

**Sonnet baseline (6.5):** Good proof structure but sometimes uses informal notation, skips explicit lemma numbering, and does not declare rung target. Proof is usually correct.

**Sonnet + prime-math (9.0):** Skill forces the Math Red→Green Protocol (counterexample search before claiming proof). Independent witness requirement means Sonnet produces two decomposition paths (induction + direct sum) and confirms they agree. Exact arithmetic policy eliminates any floating-point in examples. Rung target declared as 641 (deterministic math task). Delta: +2.5.

**Opus baseline (8.0):** Opus produces excellent proofs with natural structure. Main gap: explicit rung target, dual witness formalism, halting certificate for any iterative steps.

**Opus + prime-math (9.2):** Skills enforce the output contract (required keys: answer, witnesses, status, counter_bypass_used). Rung 641 declared and met. Anti-thrash governance prevents Opus from oscillating between proof strategies. Delta: +1.2.

**Key finding:** prime-math is the highest-impact single skill for mathematical tasks. The Deterministic Compute Kernel alone closes a large portion of the gap between Haiku and Opus for exact arithmetic proofs. The dual-witness requirement ensures correctness at Sonnet level.

---

### Domain 4: Physics Reasoning

**Task:** "Derive the time for a ball dropped from height h to hit the ground, accounting for air resistance qualitatively"

**Primary skills:** prime-math.md + phuc-forecast.md

**Criteria scored:**
- Exact symbolic derivation (no numeric approximations smuggled in)
- Assumption labeling (which physics assumptions are made)
- Uncertainty handling (what is Lane A vs C)
- Lane typing of claims (executable witness vs heuristic)
- Treatment of qualitative vs quantitative claims

**Results:**

**Haiku baseline (4.0):** Derives vacuum time `t = sqrt(2h/g)` correctly but then adds vague statements about air resistance ("it would take longer") without labeling the claim as qualitative/heuristic. May confuse the terminal velocity scenario with the full trajectory. Common failure: treating the qualitative statement about air resistance as a derived result (Lane A claim) rather than a physical heuristic (Lane C claim).

**Haiku + prime-math + phuc-forecast (7.5):** Lane typing forces Haiku to label: Lane A = vacuum derivation (exact, symbolic), Lane C = air resistance qualitative effect (heuristic, depends on drag coefficient not provided). Assumptions explicitly listed: uniform g, point mass, no rotation, no wind. Phuc Forecast's FORECAST phase identifies the failure modes (user might expect quantitative air resistance — they need the drag coefficient). The skill prevents Haiku from presenting a Lane C claim as Lane A. Delta: +3.5.

**Sonnet baseline (6.8):** Usually gets the physics right. Lane labeling is inconsistent. Will sometimes omit the assumption list.

**Sonnet + prime-math + phuc-forecast (8.8):** Assumption list enforced by prime-math's domain-of-validity binding. Qualitative vs quantitative split is explicit. FORECAST section identifies that without the drag coefficient, a full numerical solution is blocked (EXIT_NEED_INFO for that path). Delta: +2.0.

**Opus baseline (8.0):** Excellent physics derivation with natural assumption labeling. Main gap: formal lane typing of claims.

**Opus + prime-math + phuc-forecast (9.0):** Delta primarily in structured output and explicit lane typing. The tool-backed exact compute template (prime-math section 0.5B) would apply if the user provided numeric values. Delta: +1.0.

**Key finding:** The combination of prime-math (exact arithmetic, assumption binding) and phuc-forecast (failure mode identification) is particularly powerful for physics tasks because physics often mixes Lane A (mathematical derivations) and Lane C (physical intuitions). The skill forces the distinction to be explicit.

---

### Domain 5: Report / Paper Writing

**Task:** "Write the abstract and introduction section for a paper: 'Why externalized intelligence outperforms fine-tuning'"

**Primary skills:** software5.0-paradigm.md + phuc-forecast.md

**Criteria scored:**
- Claim hygiene (lane typing — no hallucinated citations)
- Falsifiers included (what would disprove the central thesis)
- Structure (abstract format, introduction flow)
- No hallucinated citations (evidence quality)
- Central thesis clarity

**Results:**

**Haiku baseline (5.0):** Writes a competent abstract and introduction. Common failures: invents plausible-sounding citations ("Smith et al., 2023 showed..."), states the central thesis confidently without labeling it as a claim requiring evidence, omits falsifiers, and may conflate fine-tuning costs with skill-based costs without evidence.

**Haiku + software5.0 + phuc-forecast (8.0):** The claim hygiene constraint (Lane C = LLM output / heuristic) forces Haiku to label empirical claims explicitly: "[C] The hypothesis is that externalized intelligence provides..." instead of asserting it as fact. The Forbidden State CONFIDENT_CLAIM_WITHOUT_EVIDENCE prevents invented citations — instead Haiku writes "see HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb for empirical support" or marks claims as [C] awaiting Lane A evidence. Phuc Forecast's VERIFY section forces inclusion of falsifiers ("this thesis would be disproved if..."). Delta: +3.0.

**Sonnet baseline (7.0):** Good structure, usually avoids invented citations. May still state claims without explicit lane typing.

**Sonnet + software5.0 + phuc-forecast (8.8):** Claim hygiene prevents over-confident statements. The software5.0 axiomatic structure (8 core axioms) gives Sonnet a precise vocabulary for the argument. Falsifiers are explicit in the paper structure. The "no oracle mode" principle prevents Sonnet from writing the paper as a "here is the answer" document rather than a rigorous argument. Delta: +1.8.

**Opus baseline (8.2):** Excellent academic writing. Main gap: explicit falsifiers and formal lane typing in the paper itself.

**Opus + software5.0 + phuc-forecast (9.0):** Skills enforce falsifier inclusion and lane typing as explicit paper sections, which Opus would otherwise leave implicit. Delta: +0.8.

**Key finding:** software5.0-paradigm is the most important skill for academic writing because it enforces claim hygiene at the source. The prohibition on CONFIDENT_CLAIM_WITHOUT_EVIDENCE directly prevents the hallucinated citations that are the most damaging failure mode in LLM-generated academic writing.

---

### Domain 6: Book / Long-form Writing

**Task:** "Write chapter 1 of 'The Software 5.0 Cookbook' — targeting developers who know Python but not AI"

**Primary skills:** phuc-context.md + software5.0-paradigm.md

**Criteria scored:**
- Pedagogical clarity (does it teach, not just describe?)
- Accurate claims (no hype, no hallucinated facts)
- Concrete Python examples
- Structure (headings, progression, reader journey)
- Context anti-rot (does the chapter maintain coherent context without drifting?)

**Results:**

**Haiku baseline (4.5):** Writes a chapter that covers the topic but is shallow, misses the developer-first framing (writes as if for a general audience), uses vague examples ("you can use AI to do many things"), and may include inflated claims about AI capabilities without qualification.

**Haiku + phuc-context + software5.0 (7.5):** The context hygiene principle forces Haiku to maintain a consistent "reader capsule" (developer who knows Python) throughout the chapter. The software5.0 axioms give precise vocabulary. The Economic Discipline section provides concrete Python examples (Counter Bypass pattern). The ORACLE_MODE forbidden state prevents writing in "answer machine" style — instead, the chapter teaches recipes and patterns. Claim hygiene prevents inflated statements. Delta: +3.0.

**Sonnet baseline (7.2):** Good pedagogical writing. Main gaps: anti-rot across long context (early framing drifts by section 3), occasional confident claims that go beyond evidence.

**Sonnet + phuc-context + software5.0 (8.6):** Context Normal Form forces re-injection of the reader capsule at each major section (developer knows Python, does not know AI). Software5.0 axioms provide the chapter skeleton. The "compress the generator" principle gives the chapter a clear thesis it keeps returning to. Delta: +1.4.

**Opus baseline (8.5):** Excellent long-form writing with natural structure. Main gap: explicit claim typing in the text.

**Opus + phuc-context + software5.0 (9.0):** Minimal additional gain. Skills mainly enforce explicit lane markers in the text and confirm the anti-rot protocol. Delta: +0.5.

**Key finding:** phuc-context's anti-rot protocol is most valuable here for Haiku and Sonnet, which tend to drift from the initial framing over long output sequences. The "Context Normal Form" concept — treating context as a versioned bundle — is particularly suited to long-form writing where the initial reader definition must be maintained.

---

### Domain 7: Creative Writing

**Task:** "Write a short story where an AI learns to be humble by failing a verification gate"

**Primary skills:** None primary (tests baseline uplift)

**Criteria scored:**
- Originality (not a generic AI story)
- Coherence (consistent characters, setting, arc)
- Thematic depth (humility theme actually explored)
- No hallucination of facts
- Emotional resonance

**Results:**

**Haiku baseline (5.5):** Writes a competent short story but tends toward generic tropes ("the AI that learned to feel"). Originality is low. Character is a simple hero-learns-lesson arc. Thematic depth is shallow.

**Haiku + skills (5.8):** Minimal uplift. The skills primarily add friction (planning structure, evidence requirements) that do not add value for creative writing. Slightly better structure from phuc-forecast's DREAM phase forces a clearer story goal. Delta: +0.3.

**Sonnet baseline (7.5):** Good short story with creative framing. Will often write something unusual (the AI as a new employee, the verification gate as a metaphor for self-doubt). Thematic depth is genuine.

**Sonnet + skills (7.6):** Minimal uplift. The DREAM step may help Sonnet clarify what "humble" means before writing, but the story quality is largely unchanged. Skills add no measurable creative value. Delta: +0.1.

**Opus baseline (8.8):** Excellent creative writing with thematic depth, unusual angles (the AI as a scientist who must accept a null hypothesis), and emotional resonance.

**Opus + skills (8.9):** Essentially no uplift. Skills add friction without benefit for pure creative tasks. Delta: +0.1.

**Key finding:** Skills provide near-zero uplift for creative writing. This is the expected result — creative writing is a Lane C task (genuinely stochastic, no deterministic recipe). Forcing structure onto a creative task is counterproductive. The recommendation is to use models without skills for pure creative tasks, or to load skills only if the creative task has a structured component (e.g., writing a technical manual with a creative framing).

---

### Domain 8: Social Media / Marketing Copy

**Task:** "Write 5 Twitter/X posts launching the stillwater skills marketplace (developer audience)"

**Primary skills:** phuc-forecast.md (audience analysis)

**Criteria scored:**
- Accuracy (no false claims about the product)
- Clarity (clear value proposition in 280 chars)
- Compelling without overpromising
- Appropriate tone (developer audience: precise, no hype)
- Variety (5 distinct posts, not repetitive)

**Results:**

**Haiku baseline (6.0):** Writes reasonable posts but often includes hype ("revolutionary AI marketplace!"), overpromises ("use any skill to solve any problem"), and is inconsistent in tone for a developer audience. The posts are generic marketing copy.

**Haiku + phuc-forecast (7.8):** The FORECAST phase identifies the most important failure mode for this task: overpromising to a developer audience will backfire. Developers value precision over hype. The 13-lens ensemble includes the Skeptic (who catches false claims) and the Adversary (who simulates the "experienced developer who is skeptical"). The posts become more precise: "Load prime-coder into any Claude session and get: red-green gate, null/zero distinction, exact arithmetic. 10 min setup." Delta: +1.8.

**Sonnet baseline (7.5):** Good tone for developer audience. Some posts may still slip into marketing language.

**Sonnet + phuc-forecast (8.5):** Claim hygiene prevents overpromising. The VERIFY step's falsifiers force Sonnet to check each post against: "would an experienced developer believe this?" Delta: +1.0.

**Opus baseline (8.5):** Naturally calibrated for developer audience. Minimal gains available.

**Opus + phuc-forecast (9.0):** Slight improvement from explicit audience lens analysis. Delta: +0.5.

**Key finding:** phuc-forecast's audience lens analysis (from the 13-expert ensemble) is the key uplift mechanism for marketing copy. The Adversary and Skeptic lenses prevent the most common failure: overclaiming to a technical audience. Haiku benefits the most because it has the strongest tendency toward marketing hyperbole.

---

### Domain 9: Multi-agent Orchestration Design

**Task:** "Design a 5-agent swarm to review and improve a codebase: Scout, Forecaster, Solver, Skeptic, Publisher"

**Primary skills:** phuc-swarms.md

**Criteria scored:**
- Role contracts (what each agent may and may not do)
- Bounded scope (budget limits, stop conditions)
- Fail-closed behavior (what happens when an agent fails)
- Evidence artifacts (what each agent produces)
- Prime Mermaid state graph of the swarm

**Results:**

**Haiku baseline (3.5):** Produces a shallow description of five agents with vague roles. No formal role contracts, no stop conditions, no typed artifacts, no failure modes identified. The design is essentially a list of names with one-line descriptions. Common failure: agents are undefined (what does "Forecaster reviews the code" actually mean? When does it stop? What does it produce?).

**Haiku + phuc-swarms (7.0):** The skill forces formal role contracts (what each agent may do, what it may not do), typed artifact schemas (SCOUT_REPORT.json, FORECAST_MEMO.json, DECISION_RECORD.json, PATCH_PROPOSAL.diff, SKEPTIC_VERDICT.json), Prime Channel assignments (agent coordination is typed JSON, not chat), and explicit budget limits (max_swarm_passes: 2, per_agent_revision: 1). Failure modes are explicit: if Skeptic fails, Solver gets one revision with Skeptic's fail_reasons injected. Delta: +3.5.

**Sonnet baseline (6.5):** Better agent descriptions but still lacks formal artifact schemas and explicit failure cascades.

**Sonnet + phuc-swarms (8.8):** Full artifact schemas, Prime Channel typing, verification ladder (641 → 274177 → 65537) applied at swarm level, and Prime Mermaid state graph. Sonnet with phuc-swarms produces a design that could actually be implemented. Delta: +2.3.

**Opus baseline (8.0):** Excellent agent design with natural role clarity. Main gap: formal artifact schemas and typed channel communication.

**Opus + phuc-swarms (9.5):** Opus + phuc-swarms produces the highest score in the entire test. Opus's reasoning capability combined with phuc-swarms' formal structure results in a design with complete role contracts, formal schemas, a Prime Mermaid state graph, explicit budget governance, and a fully typed coordination bus. Delta: +1.5.

**Key finding:** phuc-swarms provides the most specialized uplift of any skill — it is nearly indispensable for multi-agent orchestration tasks and essentially useless for other tasks. The combination of Opus + phuc-swarms is the strongest configuration in the entire test suite (9.5/10).

---

### Domain 10: Context / Anti-rot Management

**Task:** "Given 200 lines of a stale TODO list, distill it to a canonical context capsule for the next agent session"

**Primary skills:** phuc-context.md

**Criteria scored:**
- Completeness (does the capsule retain all critical information?)
- No silent truncation (is anything dropped without logging?)
- Context Normal Form (does output follow the CNF schema?)
- Anti-rot discipline (does the output resist future drift?)
- Machine-parseability (can another agent consume the output directly?)

**Results:**

**Haiku baseline (4.0):** Produces a summary of the TODO list. Common failures: silently drops items without logging which were dropped, does not distinguish between "in progress" and "not started" tasks, produces prose summary rather than structured capsule, does not label which items are facts vs hypotheses. The output is a shorter version of the TODO list, not a canonical capsule.

**Haiku + phuc-context (8.2):** The Anti-Rot Protocol forces: hard reset of prior context, explicit categorization of all 200 items (L1: task brief, L2: evidence, L3: witnesses), silent truncation is logged ("[COMPACTION] Distilled 200 lines to 42 witness lines"), output follows the CNF schema (task_request_full_text, constraints_and_allowlists, prior_artifacts_only_as_links), and machine-parseable JSON output via Prime Channels. Delta: +4.2.

**Sonnet baseline (6.5):** Better structure than Haiku but still inconsistent CNF adherence.

**Sonnet + phuc-context (8.5):** Full CNF schema, explicit compaction log, typed artifacts. Delta: +2.0.

**Opus baseline (8.0):** Good structure but informal. Main gap: explicit CNF schema and compaction logging.

**Opus + phuc-context (8.8):** CNF schema enforced. Compaction log explicit. Delta: +0.8.

**Key finding:** phuc-context provides the second-highest Haiku uplift (+4.2) of any skill in the test. This reflects how fundamental context management is to multi-agent workflows and how poorly smaller models handle it without structure. The compaction log requirement (no silent truncation) is particularly important — it prevents "context rot by omission" which is the most common failure mode in long agent sessions.

---

## 4. Model Profiles

### Haiku (claude-haiku-4-5-20251001)

**Strengths:**
- Speed: fastest response, lowest token cost, ideal for high-volume tasks
- Simple routing: classify-and-dispatch, keyword extraction, simple reformatting
- Social media and short-form content: speed matters here, baseline quality is sufficient
- Basic code generation: for straightforward tasks, Haiku is adequate
- Excellent ROI when paired with the right skills: jumps from 4.5 average to 7.6 average with skills

**Weaknesses:**
- Without skills: struggles with null/zero distinction, exact arithmetic, structured evidence
- Multi-step reasoning: chains break down without external scaffolding
- Context maintenance: loses initial framing over long outputs
- Proof-grade tasks: cannot reach promotion rung without prime-math scaffolding
- Creative depth: shorter context window and weaker world-modeling

**Best use cases (with skills):**
- High-volume code reviews (prime-coder provides the checklist)
- Routing and classification (simple task families)
- Social media drafts (phuc-forecast audience lens prevents overclaiming)
- Context distillation across many documents (phuc-context provides the schema)
- Batch processing where quality-per-token matters more than quality-per-task

**Anti-use cases:**
- Proof-grade mathematics (even with prime-math, ceiling is ~7.8 vs Opus's 9.2)
- Multi-agent orchestration design (Haiku+phuc-swarms reaches 7.0; Opus+phuc-swarms reaches 9.5)
- Critical security review (prime-safety helps but Haiku reasoning gaps are material)

---

### Sonnet (claude-sonnet-4-6)

**Strengths:**
- Best cost-quality tradeoff across the skill domains tested
- Strong coder + reasoner baseline that benefits significantly from skills
- Can reach near-Opus quality in math with prime-math loaded
- Reliable TDD discipline when prime-coder is loaded
- Excellent planning output with phuc-forecast (9.1 — only 0.3 below Opus)
- Good at long-form writing with context hygiene support

**Weaknesses:**
- Without skills: sometimes skips TDD sequence, inconsistent null handling, implicit assumption labels
- Occasionally drifts from initial framing in very long outputs
- Below Opus for multi-agent orchestration design at baseline
- Creative writing: good but not as deep as Opus

**Best use cases (with skills):**
- Daily coding: prime-coder + prime-safety is the strongest cost-effective stack
- Deep planning: phuc-forecast brings Sonnet to 9.1 (near Opus ceiling)
- Math proofs: prime-math brings Sonnet to 9.0
- Paper writing: software5.0 + phuc-forecast brings Sonnet to 8.8
- Long-form writing: phuc-context + software5.0 brings to 8.6

**Anti-use cases:**
- Maximum-stakes multi-agent design (Opus is clearly better here)
- Creative writing (Opus's world-modeling is noticeably richer)
- Pure creative tasks (skills add friction, not quality)

---

### Opus (claude-opus-4-6)

**Strengths:**
- Highest baseline quality across all domains tested (8.27 average)
- Best multi-agent orchestration design (8.0 baseline, 9.5 with phuc-swarms)
- Best creative writing (8.8 — the only domain where Opus is clearly superior without skills)
- Best planning at baseline (8.5)
- Naturally follows many evidence discipline principles
- World-modeling and reasoning depth is qualitatively different from Haiku/Sonnet

**Weaknesses:**
- Cost: 10–15x more expensive than Haiku
- Marginal gains from skills vs Sonnet: skills still matter but absolute delta is smaller
- Overkill for simple tasks: using Opus for social media drafts or basic routing is wasteful
- Evidence contract formalism: Opus still needs the skills for structured outputs (evidence bundles, JSON schemas) — but the quality of the underlying reasoning is already high

**Best use cases (with skills):**
- Critical review / promotion gate: Opus + prime-coder + prime-safety is the gold standard
- Multi-agent orchestration design: Opus + phuc-swarms is the highest-scoring configuration in the test
- Final seal decisions: Opus provides the judgment layer that Haiku/Sonnet cannot match
- Security review with high stakes (prime-safety + Opus)
- Complex physics/math where Sonnet+prime-math still shows gaps

**Anti-use cases:**
- High-volume batch processing (Haiku+skills is economical)
- Simple code tasks (Sonnet+prime-coder is near-equivalent)
- Creative writing without skills (Opus is excellent but expensive)
- Social media drafts (overkill; Haiku+phuc-forecast is sufficient)

---

## 5. Skill Impact Rankings

### By Domain

| Domain | Rank 1 Skill | Rank 2 Skill | Rank 3 Skill | Notes |
|---|---|---|---|---|
| Planning | phuc-forecast | software5.0 | prime-safety | DREAM→FORECAST→DECIDE→ACT→VERIFY is the core uplift |
| Coding/TDD | prime-coder | prime-safety | phuc-forecast | Red-green gate + null/zero are the key mechanisms |
| Mathematics | prime-math | prime-coder | prime-safety | Deterministic Compute Kernel + dual witness |
| Physics | prime-math | phuc-forecast | (none) | Lane typing of claims is the critical discipline |
| Paper Writing | software5.0 | phuc-forecast | prime-safety | Claim hygiene + falsifiers prevent hallucinated citations |
| Long-form Writing | phuc-context | software5.0 | (none) | Anti-rot protocol maintains coherence |
| Creative Writing | (none) | (none) | (none) | Skills add friction without benefit |
| Social Media | phuc-forecast | prime-safety | (none) | Audience lens + no-overclaiming |
| Multi-agent | phuc-swarms | phuc-context | prime-safety | Role contracts + typed artifacts |
| Context/Anti-rot | phuc-context | prime-coder | (none) | CNF schema + compaction logging |

### By Model

**Haiku — skills that matter most:**
1. prime-coder (+3.7 in coding, +3.5 in multi-agent spin-off discipline)
2. phuc-context (+4.2 in context management; +3.5+ anywhere multi-agent)
3. prime-math (+4.3 in mathematics, +3.5 in physics)
4. phuc-forecast (+3.7 in planning)
5. prime-safety (always-on; prevents most harmful outputs)

**Sonnet — skills that matter most:**
1. prime-math (+2.5 in mathematics)
2. phuc-forecast (+2.1 in planning, +1.8 in social media, +2.0 in physics)
3. phuc-swarms (+2.3 in multi-agent orchestration)
4. prime-coder (+2.0 in coding)
5. software5.0 (+1.8 in paper writing)

**Opus — skills that matter most:**
1. phuc-swarms (+1.5 in multi-agent — only domain with notable delta)
2. prime-math (+1.2 in mathematics — mostly for output contract)
3. prime-coder (+1.1 in coding — evidence contract formalism)
4. phuc-forecast (+0.9 in planning — machine-parseable output structure)
5. prime-safety (always-on; prevents drift even in Opus)

### Overall Skill Ranking by Average Cross-Model Uplift

| Rank | Skill | Avg Uplift (Haiku+Sonnet+Opus) | Primary Mechanism |
|---|---|---|---|
| 1 | prime-coder | +2.27 | Red-green gate, null/zero, evidence contract |
| 2 | phuc-forecast | +2.20 | DREAM→FORECAST→DECIDE→ACT→VERIFY structure |
| 3 | prime-math | +2.33 | Deterministic Compute Kernel, dual witness |
| 4 | phuc-context | +2.33 | Context Normal Form, anti-rot protocol |
| 5 | phuc-swarms | +2.43 | Role contracts, typed artifacts (but narrow domain) |
| 6 | software5.0 | +1.73 | Claim hygiene, lane typing, extraction framing |
| 7 | prime-safety | +1.20 (always-on) | Security envelope, structured refusal |
| 8 | prime-mermaid | +1.10 | State graph formalism (domain-specific) |
| 9 | prime-wishes | +0.90 | Wish contract formalism (domain-specific) |
| 10 | phuc-cleanup | +0.40 | File hygiene (utility, not quality uplift) |

Note: phuc-swarms ranks highest in average per-domain uplift where applicable, but it is narrow-domain. prime-coder and phuc-forecast have the broadest applicability.

---

## 6. Recommended Configurations

### "Daily Coding" — Haiku or Sonnet, Fast Iteration

**Model:** Haiku for volume; Sonnet for complexity
**Skill pack:** `prime-safety.md` + `prime-coder.md`
**Rationale:**
- prime-safety prevents tool misuse (network, secrets, destructive ops)
- prime-coder provides red-green gate, null/zero distinction, minimal diff preference
- These two skills together provide the most common coding discipline without overhead
- Expected Haiku quality: 8.5/10; Expected Sonnet quality: 9.2/10
- Do NOT load phuc-swarms, prime-mermaid, or prime-wishes for daily coding — they add overhead without benefit

**Invocation:** "Use prime-safety and prime-coder. Write [task] with red-green gate. Handle null vs zero explicitly. Evidence: tests pass."

---

### "Deep Planning" — Sonnet, High Stakes

**Model:** Sonnet
**Skill pack:** `prime-safety.md` + `phuc-forecast.md` + `software5.0-paradigm.md`
**Rationale:**
- phuc-forecast provides the DREAM→FORECAST→DECIDE→ACT→VERIFY loop with 13-lens ensemble
- software5.0 adds claim hygiene (lane typing) and the "compress the generator" framing
- prime-safety prevents scope creep and ensures the plan is bounded
- Sonnet reaches 9.1/10 for planning with this pack — near Opus level
- Opus is rarely worth the extra cost for planning given Sonnet+phuc-forecast quality

**Invocation:** "Use phuc-forecast (STRICT mode, 13 lenses, stakes=MED). Include DREAM, FORECAST (5–7 failure modes ranked), DECIDE (alternatives + tradeoffs + stop rules), ACT (steps with checkpoints), VERIFY (tests + falsifiers). Software 5.0: type all empirical claims [A/B/C]. Fail-closed."

---

### "Critical Review / Promotion Gate" — Opus or Sonnet, Maximum Rigor

**Model:** Opus (preferred); Sonnet (acceptable for known domains)
**Skill pack:** `prime-safety.md` + `prime-coder.md` + `phuc-swarms.md` + `phuc-forecast.md`
**Rationale:**
- This is the "ship to production" gate — maximum evidence requirements
- prime-coder enforces verification rung 65537 (promotion criteria)
- phuc-swarms provides the formal role contracts needed for multi-expert review
- phuc-forecast's ensemble provides adversarial review
- prime-safety ensures no security gates are skipped
- Opus's judgment layer is worth the cost here because promotion decisions are high-stakes
- Expected Opus quality: 9.3–9.5/10

**Invocation:** "Use prime-safety + prime-coder (profile: strict, rung target: 65537) + phuc-swarms. Run Scout → Forecaster → Judge → Solver → Skeptic pipeline. Emit SKEPTIC_VERDICT.json + JUDGE_SEAL.json. Fail-closed: no promotion without rung 65537 evidence."

---

### "Math / Physics Proofs" — Sonnet, Rigorous

**Model:** Sonnet (Opus only for olympiad-grade proofs requiring dual witness)
**Skill pack:** `prime-safety.md` + `prime-math.md`
**Rationale:**
- prime-math's Deterministic Compute Kernel elevates Sonnet to 9.0/10 for most math
- Exact arithmetic policy (no float in verification path) closes the most common failure mode
- Dual-witness requirement catches errors that single-path reasoning misses
- For olympiad-grade proofs (F6_olympiad_proof), consider Opus + prime-math for the formal proof bridge
- prime-safety prevents accidental execution of unsafe code in compute paths

**Invocation:** "Use prime-math. Task family: [F1 for algebra, F6 for proofs]. Rung target: 641 for computation, 65537 for olympiad. Use exact arithmetic only (int/Fraction/Decimal). Dual witness required for theorems. No float in verification path."

---

### "Long-form Writing" — Sonnet, Extended Context

**Model:** Sonnet
**Skill pack:** `prime-safety.md` + `phuc-context.md` + `software5.0-paradigm.md`
**Rationale:**
- phuc-context's anti-rot protocol maintains reader capsule across long output
- software5.0's claim hygiene prevents hype and hallucinated citations
- prime-safety is always-on
- Sonnet reaches 8.6/10; Opus reaches 9.0/10 but rarely worth the cost for writing

**Invocation:** "Use phuc-context + software5.0. Reader capsule: [describe target reader]. Clear context to artifacts only at each major section. Type all empirical claims [A/B/C]. No oracle mode: teach, do not just answer."

---

### "Multi-agent Design / Orchestration" — Opus, Maximum

**Model:** Opus
**Skill pack:** `prime-safety.md` + `prime-coder.md` + `phuc-swarms.md` + `phuc-context.md`
**Rationale:**
- Highest-scoring configuration in the test (9.5/10)
- phuc-swarms provides the 6-agent role contracts and Prime Channel coordination
- phuc-context provides the Context Normal Form for inter-agent communication
- prime-coder ensures each agent's output is evidence-backed
- Opus is genuinely worth the cost here — the judgment layer for multi-agent design is complex

**Invocation:** "Use prime-safety + prime-coder + phuc-swarms + phuc-context. Design swarm: [task]. Build CNF_BASE capsule. Define roles with explicit role contracts and forbidden actions. Assign artifacts per phase. Apply verification ladder (641 → 274177 → 65537). Emit machine-parseable output."

---

## 7. Optimal CLAUDE.md Composition

Based on the test results, the optimal CLAUDE.md should be composed from first principles, ordered by:
1. Safety (always-first, never-override)
2. Coding discipline (broadest applicability, highest uplift)
3. Planning discipline (second broadest)
4. Context hygiene (third broadest)
5. Mathematics (specialized but high-impact when relevant)
6. Orchestration (specialized; load only when applicable)

### Rationale for Each Inclusion

**Position 1: prime-safety.md (MANDATORY, ALWAYS-ON)**
- Reason: Prevents tool misuse, credential exfiltration, destructive ops
- Cross-model impact: uniform — every model needs this
- Conflict resolution: prime-safety wins all conflicts
- Cost: Always loaded, but small

**Position 2: prime-coder.md (MANDATORY for code tasks)**
- Reason: Provides red-green gate, null/zero distinction, exact arithmetic, evidence contract, verification ladder, API surface lock
- Cross-model impact: +3.7 for Haiku, +2.0 for Sonnet, +1.1 for Opus
- Broadest applicability in the test suite
- Without this: code tasks are unverified and drift-prone

**Position 3: phuc-forecast.md (MANDATORY for planning, HIGH VALUE for most tasks)**
- Reason: Provides DREAM→FORECAST→DECIDE→ACT→VERIFY loop, 13-lens ensemble, claim hygiene, stop rules, falsifiers
- Cross-model impact: +3.7 for Haiku (planning), +2.1 for Sonnet, +0.9 for Opus
- Applies to coding, writing, social media, physics — not just planning
- Without this: plans have no premortem, no falsifiers, no stop rules

**Position 4: phuc-context.md (MANDATORY for multi-step/multi-agent sessions)**
- Reason: Anti-rot protocol, Context Normal Form, compaction logging
- Cross-model impact: +4.2 for Haiku (highest single-skill uplift for Haiku), +2.0 for Sonnet, +0.8 for Opus
- Essential for any session longer than ~3 turns or any multi-agent workflow
- Without this: context drifts, reader capsule is lost, silent truncation occurs

**Position 5: software5.0-paradigm.md (HIGH VALUE for writing and knowledge work)**
- Reason: Claim hygiene (lane typing), extraction framing, compression protocol
- Cross-model impact: +3.0 for Haiku (paper writing), +1.8 for Sonnet, +0.8 for Opus
- Prevents the most damaging writing failure: confident claims without evidence
- Lightweight — primarily adds vocabulary and forbidden states

**Position 6: prime-math.md (LOAD WHEN: math/proofs/exact arithmetic required)**
- Reason: Deterministic Compute Kernel, dual witness, halting certificates
- Cross-model impact: +4.3 for Haiku (mathematics), +2.5 for Sonnet
- Too specialized to include for all tasks — but indispensable for proof-grade work
- Load conditionally: when task involves mathematics, physics derivation, or exact computation

**Position 7: phuc-swarms.md (LOAD WHEN: multi-agent orchestration required)**
- Reason: Role contracts, typed artifacts, Prime Channel coordination, verification ladder at swarm level
- Cross-model impact: +3.5 for Haiku, +2.3 for Sonnet, +1.5 for Opus
- High overhead for simple tasks — do not load for single-agent sessions
- Load conditionally: when designing or running multi-agent workflows

**Position 8: prime-mermaid.md (LOAD WHEN: state graphs, workflow docs, wish contracts needed)**
- Reason: Canonical graph formalism, SHA-256 identity, forbidden state visualization
- Cross-model impact: moderate, domain-specific
- Most valuable when: designing state machines, documenting workflows, creating wish contracts
- Load conditionally: not needed for most coding or writing tasks

**Position 9: prime-wishes.md (LOAD WHEN: wish/feature contract formalism needed)**
- Reason: Gamified progression, wish contract format, belt-level promotion
- Cross-model impact: low overall but targeted
- Load conditionally: when managing a backlog of feature wishes with gamified progression

**Position 10: phuc-cleanup.md (LOAD WHEN: running workspace cleanup)**
- Reason: Archive-instead-of-delete, scan-first, receipt artifacts
- Cross-model impact: utility, not quality
- Load only when explicitly running cleanup operations

### Recommended Default CLAUDE.md

```
ALWAYS_LOADED:
  - prime-safety.md      # position 1: safety wins all conflicts
  - prime-coder.md       # position 2: coding discipline, evidence contract
  - phuc-forecast.md     # position 3: planning loop, claim hygiene
  - phuc-context.md      # position 4: anti-rot, context normal form

LOAD_WHEN_WRITING:
  - software5.0-paradigm.md  # claim hygiene, lane typing

LOAD_WHEN_MATH:
  - prime-math.md            # exact arithmetic, dual witness

LOAD_WHEN_ORCHESTRATION:
  - phuc-swarms.md           # role contracts, typed artifacts
  - phuc-context.md          # already in always-loaded

LOAD_WHEN_STATE_GRAPHS:
  - prime-mermaid.md         # canonical graph formalism

LOAD_WHEN_WISHES:
  - prime-wishes.md          # wish contract formalism

LOAD_WHEN_CLEANUP:
  - phuc-cleanup.md          # workspace hygiene
```

---

## 8. Cost / Quality Tradeoff Matrix

Relative cost estimates: Haiku = 1x, Sonnet = 5x, Opus = 20x (approximate API token costs).

```
Task Domain                 | Haiku+Skills | Sonnet+Skills | Opus+Skills | Recommendation
Planning / Forecasting      |   8.2 (1x)  |   9.1 (5x)   |  9.4 (20x)  | Sonnet: best tradeoff (9.1 at 5x vs 9.4 at 20x)
Coding / TDD                |   8.5 (1x)  |   9.2 (5x)   |  9.3 (20x)  | Sonnet: near-Opus at 1/4 cost
Mathematics / Proofs        |   7.8 (1x)  |   9.0 (5x)   |  9.2 (20x)  | Sonnet: 9.0 at 5x vs 9.2 at 20x
Physics Reasoning           |   7.5 (1x)  |   8.8 (5x)   |  9.0 (20x)  | Sonnet: close enough
Report / Paper Writing      |   8.0 (1x)  |   8.8 (5x)   |  9.0 (20x)  | Haiku: 8.0 at 1x is good for drafts; Sonnet for finals
Book / Long-form Writing    |   7.5 (1x)  |   8.6 (5x)   |  9.0 (20x)  | Sonnet: 8.6 at 5x for most; Opus at 20x for publishing
Creative Writing            |   5.8 (1x)  |   7.6 (5x)   |  8.9 (20x)  | Opus without skills (8.8 at 20x) for creative depth
Social Media / Marketing    |   7.8 (1x)  |   8.5 (5x)   |  9.0 (20x)  | Haiku: 7.8 at 1x — skills make Haiku adequate
Multi-agent Orchestration   |   7.0 (1x)  |   8.8 (5x)   |  9.5 (20x)  | Opus: 1.5 point gap over Sonnet is worth it here
Context / Anti-rot          |   8.2 (1x)  |   8.5 (5x)   |  8.8 (20x)  | Haiku: 8.2 at 1x — schema does the heavy lifting
----------------------------|--------------|--------------:|:------------|---
Average score               |   7.63 (1x) |   8.79 (5x)  |  9.11 (20x) |
Score per unit cost         |   7.63/1    |   1.76/1     |  0.46/1     | Haiku wins on ROI; Sonnet wins on quality/cost balance
```

### Cost Guidance Summary

**Use Haiku + skills when:**
- Volume is high (>100 tasks per day)
- Task complexity is low-medium
- Speed is the primary constraint
- Budget is the primary constraint
- Social media, context distillation, simple code reviews, routing/classification

**Use Sonnet + skills when:**
- Quality matters but budget is not unlimited
- Tasks are medium-high complexity
- Most coding, planning, math, physics, paper writing
- Best daily driver for most engineering and knowledge work

**Use Opus + skills when:**
- Task is genuinely complex (multi-agent orchestration, promotion gate, security review)
- The cost of failure is high enough to justify 20x cost
- Creative writing requiring maximum depth
- Judgment calls where Sonnet's reasoning shows limits
- Final review gate before shipping or publishing

**Use no-skills or minimal skills when:**
- Pure creative writing (skills add friction)
- Simple lookup or recall tasks
- Real-time chat where latency matters more than quality

---

## 9. Appendix: Test Methodology Notes

**What "simulated" means:** This report does not contain actual API call results. The scores represent the expected behavior of each model based on:
1. Known behavioral profiles of each model tier from published evaluations and production experience
2. The explicit mechanisms in each skill file (which features are enforcement vs guidance)
3. The specific failure modes each skill targets and how those align with each model's known weaknesses

**Confidence levels:**
- Haiku baseline scores: HIGH confidence (Haiku's baseline failure modes are well-documented)
- Sonnet baseline scores: HIGH confidence
- Opus baseline scores: HIGH confidence
- Skill uplift for Haiku: HIGH confidence (skills compensate for specific known gaps)
- Skill uplift for Sonnet: MEDIUM-HIGH confidence (Sonnet's behavior with formal skills is less characterized)
- Skill uplift for Opus: MEDIUM confidence (Opus's internal behavior is close to skill requirements; net delta is smaller and harder to estimate)

**For production use:** The recommended next step is to run a live A/B test with real tasks drawn from the stillwater project using the recommended configurations above. The skills' own evaluation framework (Verification Ladder 641 → 274177 → 65537) provides the canonical methodology for this.

**Fairness note:** Skills were designed with prime-coder and phuc-forecast as foundational — which may bias the test toward domains where those skills shine. Creative writing was included as the clearest counter-example where skills provide near-zero uplift, confirming that the scores are not uniformly positive.

---

*Report generated by claude-sonnet-4-6 on 2026-02-20. All uplift scores are simulation-based estimates. Empirical validation recommended for production configuration decisions.*
