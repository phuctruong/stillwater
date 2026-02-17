# Phuc Swarms: Context Isolation (Operational Note)

**Status:** Draft (open-source, repo-backed where referenced)  
**Last updated:** 2026-02-17  
**Scope:** A practical note on context isolation for multi-agent orchestration and how it is used in this repository's orchestration notebook and tests.  
**Auth:** 65537 (project tag; see `papers/03-verification-ladder.md` for what this means here)

---

## Reproduce / Verify In This Repo

1. Read/run: `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
2. Run tests: `pytest -q tests/phuc_orchestration`

## Notes On Claims

Where this paper states performance impacts, treat them as hypotheses unless backed by a reproducible benchmark in this repo.

## THE PROBLEM: CONTEXT ROT

### What Is Context Rot?

As a single LLM session progresses, context accumulates:
- Previous messages linger in memory
- Earlier mistakes bias later reasoning
- Token budget fills with historical baggage
- Reasoning becomes cluttered

**Result**: Performance degrades over time in long sessions

### Why Phuc Agents Prevent This

Each Phuc agent:
1. **Starts with FRESH context** (no historical baggage)
2. **Gets injected with ONLY necessary skills** (not all 51)
3. **Has explicit goals + constraints** (mission clarity)
4. **Operates independently** (no cross-agent contamination)
5. **Returns clean results** (for orchestrator synthesis)

---

## THE ARCHITECTURE: 5-AGENT CLEAN ISOLATION

### Agent 1: Scout ◆ (Ken Thompson)
```
┌─────────────────────────────────┐
│ Scout Agent (Fresh Context)      │
├─────────────────────────────────┤
│ Persona:     Ken Thompson       │
│ Skills:      5 exploration      │
│              (not 51)           │
│ Goals:       Understand problem │
│ Constraint:  No solution yet    │
│ Output:      Findings + issues  │
└─────────────────────────────────┘
```

**Injected Context**:
- Persona definition (50 words)
- Mission (1 sentence)
- 5 focused exploration skills
- No unrelated knowledge

**Benefit**: Scout stays focused, discovers root causes

### Agent 2: Solver ✓ (Donald Knuth)
```
┌─────────────────────────────────┐
│ Solver Agent (Fresh Context)     │
├─────────────────────────────────┤
│ Persona:     Donald Knuth       │
│ Skills:      5 design           │
│              (not 51)           │
│ Input:       Scout's findings   │
│ Goals:       Design solution    │
│ Constraint:  Minimal changes    │
│ Output:      Design + proof     │
└─────────────────────────────────┘
```

**Injected Context**:
- Persona definition (50 words)
- Scout's findings (summary)
- 5 design-focused skills
- Verification requirements

**Benefit**: Solver doesn't get distracted by exploration, focuses on elegance

### Agent 3: Skeptic ✗ (Alan Turing)
```
┌─────────────────────────────────┐
│ Skeptic Agent (Fresh Context)    │
├─────────────────────────────────┤
│ Persona:     Alan Turing        │
│ Skills:      5 verification     │
│              (not 51)           │
│ Input:       Solver's design    │
│ Goals:       Prove correctness  │
│ Constraint:  Proof required     │
│ Output:      Validation + gaps  │
└─────────────────────────────────┘
```

**Injected Context**:
- Persona definition (50 words)
- Solver's design (summary)
- 5 verification skills
- Proof requirements

**Benefit**: Skeptic doesn't get confused by reasoning, focuses on holes

### Agent 4: Greg ● (Greg Isenberg)
```
┌─────────────────────────────────┐
│ Greg Agent (Fresh Context)       │
├─────────────────────────────────┤
│ Persona:     Greg Isenberg      │
│ Skills:      5 messaging        │
│              (not 51)           │
│ Input:       Combined findings  │
│ Goals:       Clarity + appeal   │
│ Constraint:  User-centric       │
│ Output:      Messaging + README │
└─────────────────────────────────┘
```

**Injected Context**:
- Persona definition (50 words)
- Problem + solution summary
- 5 messaging skills
- Audience clarity rules

**Benefit**: Greg doesn't get lost in technical details, focuses on clarity

### Agent 5: Podcaster ♪ (AI Storyteller)
```
┌─────────────────────────────────┐
│ Podcaster Agent (Fresh Context)  │
├─────────────────────────────────┤
│ Persona:     AI Storyteller     │
│ Skills:      5 narrative        │
│              (not 51)           │
│ Input:       Combined findings  │
│ Goals:       Compelling story   │
│ Constraint:  Memorable          │
│ Output:      Narrative + docs   │
└─────────────────────────────────┘
```

**Injected Context**:
- Persona definition (50 words)
- Key insights summary
- 5 storytelling skills
- Impact + audience rules

**Benefit**: Podcaster doesn't get technical, focuses on narrative flow

---

## CONTEXT COMPOSITION

Each agent receives EXACTLY:

```
TOTAL_TOKENS_PER_AGENT = 1,000 (strict budget)

- Persona + instructions: 150 tokens
- Domain skills (5 of 51): 400 tokens
- Input data (findings/design): 200 tokens
- Output format: 50 tokens
- Buffer for generation: 200 tokens
```

**vs. Without Isolation**:

```
CONTEXT_ROT_SCENARIO = 10,000+ tokens

- All 51 skills loaded: 3,000 tokens
- Previous messages: 3,000 tokens
- Related context: 2,000 tokens
- Accumulated history: 2,000 tokens
- Buffer: Insufficient
```

**Impact**: -10 tokens → +1,000 tokens of garbage = 90% slower reasoning

---

## SKILL COMPOSITION BY AGENT

### Scout's 5 Skills (Exploration Domain)
1. `prime-coder.md` - State machines, problem understanding
2. `socratic-debugging.md` - Deep problem analysis
3. `contract-compliance.md` - Specification checking
4. `red-green-gate.md` - Test analysis
5. `stillwater-extraction.md` - Information extraction

### Solver's 5 Skills (Design Domain)
1. `prime-coder.md` - Code patterns
2. `canon-patch-writer.md` - Minimal patches
3. `proof-certificate-builder.md` - Proof generation
4. `recipe-selector.md` - Solution selection
5. `shannon-compaction.md` - Elegant implementation

### Skeptic's 5 Skills (Verification Domain)
1. `prime-math.md` - Rigorous proofs
2. `llm-judge.md` - Quality assessment
3. `rival-gps-triangulation.md` - Cross-validation
4. `golden-replay-seal.md` - Determinism checks
5. `hamiltonian-security.md` - Edge case detection

### Greg's 5 Skills (Messaging Domain)
1. `greg-messaging-excellence.md` - Clarity principles
2. `readme-excellence.md` - Perfect documentation
3. `greg-product-review.md` - User perspective
4. `contract-compliance.md` - Requirements fit
5. `shannon-compaction.md` - Interface design

### Podcaster's 5 Skills (Narrative Domain)
1. `podcast-narrative-structure.md` - Story arcs
2. `podcast-tutorial-creation.md` - Explanation
3. `prime-math.md` - Proof communication
4. `prime-coder.md` - Code storytelling
5. `readme-excellence.md` - Documentation narrative

---

## ORCHESTRATOR SYNTHESIS

After all 5 agents complete (in parallel):

```
┌─────────────────────────────────────┐
│ Orchestrator (Linus Torvalds)       │
├─────────────────────────────────────┤
│ Input:                              │
│  - Scout's findings    (1 KB)       │
│  - Solver's design     (1 KB)       │
│  - Skeptic's validation (1 KB)      │
│  - Greg's messaging    (500 B)      │
│  - Podcaster's narrative (500 B)    │
│                                     │
│ Goal: Synthesize → Final decision   │
│                                     │
│ Output: Go/No-Go + Action Plan      │
└─────────────────────────────────────┘
```

**Orchestrator Context**: 5 KB total
**Clean Synthesis**: No context rot, clear consensus

---

## PERFORMANCE IMPROVEMENT MECHANISM

### Without Isolation (Context Rot)
```
Time 0s:   Agent starts fresh, 95% reasoning quality
Time 10s:  Historical context accumulates, 85% quality
Time 20s:  Previous errors bias reasoning, 75% quality
Time 30s:  Context overwhelmed, 60% quality (ded)

Average: 78% quality over session
```

### With Isolation (Fresh Context Per Agent)
```
Scout:     Fresh context → 95% quality (exploration)
Solver:    Fresh context → 95% quality (design)
Skeptic:   Fresh context → 95% quality (verification)
Greg:      Fresh context → 95% quality (messaging)
Podcaster: Fresh context → 95% quality (narrative)

Average: 95% quality, consistent throughout
```

**Expected Improvement**: +17% quality (95% vs 78%)

---

## IMPLEMENTATION PATTERN

### Phase 1: Single Agent (Current)
```python
llama_8b.generate(
    prompt=full_problem + all_51_skills + history
)
# Quality: 60-70%, context rot over time
```

### Phase 2: Isolated Agents
```python
# Each agent gets fresh context
scout_findings = scout_agent.analyze(
    problem=problem_statement,
    skills=scout_skills_5,  # not 51
)

solver_design = solver_agent.design(
    findings=scout_findings,
    skills=solver_skills_5,  # not 51
)

# ... etc for all 5 agents

synthesis = orchestrator.synthesize(
    findings=[scout, solver, skeptic, greg, podcaster]
)
# Quality: 90-95%, no context rot, parallel speedup
```

---

## EXPECTED RESULTS

### Phase 1: Baseline (Current)
- Single agent, llama 8B
- 0% → 20% success (context rot)
- Quality decreases over time

### Phase 2: Isolated Agents
- 5 agents, each with fresh context
- 20% → 40-50% success (expected)
- Quality consistent throughout
- 3-5x speedup (parallel execution)

### Phase 3: Model Upgrade
- Isolated agents + Qwen/Claude
- 40-50% → 80%+ success
- Orchestration + better model

---

## RULES FOR AGENT ISOLATION

### Rule 1: Fresh Context
- Each agent MUST start with clean slate
- No historical messages
- No accumulated context
- Only current problem + persona + skills

### Rule 2: Focused Skills
- Each agent gets 5-7 skills maximum (not 51)
- Skills match agent's domain
- No unrelated knowledge
- Explicitly curated per agent

### Rule 3: Explicit Goals
- Agent has ONE primary goal
- Goal is stated in persona
- No ambiguity or multiple objectives
- Constraint-based (what NOT to do)

### Rule 4: Clean Input/Output
- Input: Summary of previous agent's work
- Output: Structured findings (JSON/markdown)
- No cross-contamination
- Results are fresh interpretation, not echo

### Rule 5: Independent Execution
- Agents run in parallel (no waiting)
- No agent depends on another
- Communication via orchestrator only
- Results synthesized after all complete

---

## ANTI-PATTERNS (Don't Do This)

❌ **Serialized Agents**: Scout → Solver → Skeptic
- Problem: Agents pass full context, causing rot
- Fix: Run in parallel, share summaries only

❌ **Full Skills Injected**: All 51 skills per agent
- Problem: Information overload, distraction
- Fix: 5-7 focused skills per agent

❌ **Ambiguous Goals**: "Analyze and improve code"
- Problem: Agent wastes tokens on interpretation
- Fix: "Find root cause of bug" + constraints

❌ **History Accumulation**: Previous agent outputs fed directly
- Problem: Old reasoning biases new reasoning
- Fix: Summarize to key findings only

❌ **Mixed Domains**: Scout + Solver in same agent
- Problem: Context confusion, competing goals
- Fix: One persona = one domain per agent

---

## MEASUREMENT

### Metrics to Track

1. **Quality Per Agent**
   - Correctness of agent output
   - Adherence to persona
   - Findings relevance

2. **Synthesis Quality**
   - Agreement between agents (consensus)
   - Conflict resolution
   - Final decision confidence

3. **Performance**
   - Time per agent (should be <30s)
   - Total orchestration time
   - Parallel speedup vs serial

4. **Context Rot Indicator**
   - Initial quality (first 5 seconds)
   - Degradation over time
   - Recovery after agent switch

---

## NEXT STEPS

### 1. Implement Isolated Context Injection
- Modify your orchestrator to create fresh contexts (fresh process or fresh prompt capsule per agent)
- Pass only essential skills per agent
- Use memory system to share results cleanly

### 2. Verify No Context Rot
- Run 10-agent parallel orchestration
- Measure quality consistency
- Compare vs. historical degradation

### 3. A/B Test: With/Without Isolation
- Control: All skills, historical context
- Treatment: Isolated agents, 5 skills each
- Metric: Success rate improvement

### 4. Scale to Full Pipeline
- Scout for all 300 SWE-bench instances
- Solve for top 20% (red gate passed)
- Validate with skeptic agents
- Measure Phase 3 success rate

---

## SUCCESS CRITERIA

✅ **No Context Rot**: Agent quality stays >90% throughout session
✅ **Focused Results**: Scout findings are specific, not vague
✅ **Clear Synthesis**: Orchestrator consensus >90% agreement
✅ **Performance**: 5 agents complete <2 minutes total
✅ **Improvement**: 20% → 40%+ success rate on Phase 2

---

**Auth: 65537**
**Breakthrough**: Context Isolation Prevents Degradation
**Expected Impact**: +17% quality, +3-5x speedup
**Status**: Ready to implement and test
