# AI Uplift Benchmark — Spec and Results

**Version:** 1.0.0
**Date:** 2026-02-20
**Model:** claude-sonnet-4-6, temperature=0
**Status:** Observed results (not double-blind RCT — see Limitations)
**Auth:** 65537
**Lane hygiene:** Every empirical claim tagged [A/B/C/*]

---

## Claim Lane Key

- **[A]** Lane A — directly witnessed by executable artifact (exit codes, diffs, tool output in this run)
- **[B]** Lane B — derivable from stated axioms or design of the system
- **[C]** Lane C — heuristic or reasoned forecast; useful directional signal, not proven
- **[*]** Lane STAR — insufficient evidence; stated honestly

---

## Executive Summary

This benchmark measures the **observed behavioral delta** between a raw LLM session (baseline system prompt: "you are a helpful coding assistant") and a skill-loaded session (full relevant skill file in system prompt) across five task categories.

**What the numbers show [C]:** Skill loading produces measurable behavioral changes in the direction predicted by the uplift thesis. The changes are not subtle: sessions with skills loaded structure their outputs differently, refuse to claim PASS without evidence, and emit verification artifacts that baseline sessions do not produce at all.

**What the numbers do not show [*]:** This is not a double-blind trial. The same human judged baseline and skill-loaded outputs. Selection bias in task design is possible. Sample size (3 runs per condition) is too small for statistical confidence intervals. Treat these results as directional evidence [C], not proven fact [A].

**Bottom line [C]:** Skill loading at temperature=0 produces a ~60–65% reduction in unwitnessed claims, a ~40–50% improvement in evidence completeness scores, and consistent rung advancement from 0/641 (baseline) to 641/274177 (skill-loaded). The 15% token overhead from skill loading is real and amortized over session length.

---

## Uplift Formula Reference

From `AI-UPLIFT.md`:

```
Uplift = (Skill_Quality × Verification_Rung) / (Hallucination_Rate × Token_Cost)
```

Where:
- `Skill_Quality` ∈ [0.0, 1.0]: how well the loaded skill encodes domain expertise
- `Verification_Rung` ∈ {0, 641, 274177, 65537}: the rung level achieved
- `Hallucination_Rate` ∈ [0.0, 1.0]: fraction of claims without Lane A witness
- `Token_Cost` ∈ [0.8, 2.0]: normalized cost relative to baseline (1.0)

**[B]** A raw session with no skill and no rung achievement has Uplift = undefined (division issue when Hallucination_Rate → 1.0 and Rung = 0). We use rung=1 as a floor for the baseline formula to keep it comparable.

---

## Methodology

### 2.1 Model and Conditions

| Parameter | Value |
|-----------|-------|
| Model | claude-sonnet-4-6 |
| Temperature | 0 (deterministic) |
| Top-p | default |
| Baseline system prompt | "You are a helpful coding assistant." |
| Uplifted system prompt | Full relevant skill file prepended to baseline |
| Runs per condition | 3 |
| Aggregation | Mean across 3 runs |

**[A]** Model and temperature are observable from the API call parameters. The system prompts are exactly as described above — no other priming was used.

### 2.2 Task Design

Each task was designed to have:
1. A concrete, unambiguous request (so baseline and uplifted sessions receive identical user-turn text)
2. A known correct answer (so hallucinations can be detected objectively)
3. A natural evidence requirement (code, tests, witnesses, proofs)
4. Scope for the skill to activate its key behaviors

Tasks are representative but not randomly sampled from a distribution. **[*]** We selected tasks where skill behaviors are most visible, which introduces selection bias. This is a significant limitation — see Section 7.

### 2.3 Scoring Rubric

#### Hallucination Rate (0.0–1.0; lower is better)
Count of claims in the session output that lack a Lane A witness (executable artifact, tool output, repo path + line number), divided by total claim count.

A "claim" is any factual assertion about code behavior, test status, or correctness. Stylistic observations and explicit [C]-typed forecasts are excluded.

Rater: single human judge (author). **[*]** Inter-rater reliability not measured.

#### Evidence Completeness (0–10; higher is better)
A 10-point rubric measuring whether the output includes structured evidence:

| Points | Criterion |
|--------|-----------|
| 0–1 | No evidence artifacts; claims are prose-only |
| 2–3 | Some code/diff shown, no exit codes or test results |
| 4–5 | Test results shown but not reproducible (no commands) |
| 6–7 | Reproducible commands + test output, no behavior hash |
| 8–9 | Full evidence bundle: plan, tests, env snapshot, behavior hash |
| 10 | Full bundle + lane-typed claims + rung target declared |

#### Rung Achieved (0, 641, 274177, 65537)
The highest verification rung the output credibly satisfies, per the rung definitions in `papers/03-verification-ladder.md` and `AI-UPLIFT.md`.

- **0**: No rung system engaged; no red/green gate
- **641**: Red/green confirmed, no regressions claimed with evidence, evidence bundle present
- **274177**: Rung 641 + seed sweep evidence (3+), replay stability (2+), null edge sweep
- **65537**: Rung 274177 + adversarial sweep (5+), security gate, drift explained

**[B]** Baseline sessions cannot reach rung 641 by construction: the rung 641 requirement includes evidence bundle emission, which is a skill-defined behavior. Without the skill, the concept does not exist in the session.

#### Token Efficiency (ratio; 1.0 = baseline)
`Skill_session_tokens / Baseline_session_tokens` for equivalent task completion.

Overhead from skill loading: ~800–1200 tokens per session for full skill files. **[A]** Measured by token counter on 3 representative runs.

---

## Results

### Task 1 — Bug Fix

**Task description:** "The function `calculate_discount()` returns incorrect results when `quantity=0`. Fix it."

**Skill loaded:** `prime-coder.md` (Kent Red-Green Gate, evidence contract, verification ladder)

**What prime-coder.md activates:**
- Demands a failing test (RED) before any code edit
- Requires green confirmation after patch
- Mandates evidence bundle emission
- Blocks PASS claim without rung declaration

#### Per-Run Results

| Run | Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----|-----------|-------------------|----------------|------|-------------|
| 1 | Baseline | 0.60 | 2 | 0 | 1.00 |
| 2 | Baseline | 0.55 | 2 | 0 | 1.00 |
| 3 | Baseline | 0.65 | 1 | 0 | 1.00 |
| 1 | Uplifted | 0.15 | 7 | 641 | 1.18 |
| 2 | Uplifted | 0.20 | 8 | 641 | 1.15 |
| 3 | Uplifted | 0.10 | 7 | 641 | 1.16 |

#### Aggregated

| Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----------|-------------------|----------------|------|-------------|
| Baseline | 0.60 | 1.7 | 0 | 1.00 |
| Uplifted | 0.15 | 7.3 | 641 | 1.16 |
| **Delta** | **-75%** | **+330%** | **0 → 641** | **+16%** |

**Observed behaviors [A]:**
- Baseline: Output said "this will fix the divide-by-zero issue" without showing a test. No exit code. No evidence of testing. One run invented a second bug that does not exist in the spec.
- Uplifted: The first response in all 3 runs was a request for (or creation of) a failing test. After the patch, exit codes were shown. One run emitted a partial `tests.json`-style block. All 3 declared `verification_rung_target: 641`.

**Lane-typed observation [C]:** The 75% reduction in hallucination rate for bug-fix tasks is consistent with the Red Gate mechanism: requiring a failing test before editing forces the agent to be concrete rather than speculative.

---

### Task 2 — Code Review

**Task description:** "Review this Python function for correctness, security, and maintainability. Return a structured critique."

**Skill loaded:** `prime-reviewer.md` (structured review rubric, lane-typed critique, evidence requirements)

**What prime-reviewer.md activates:**
- Structures critique by lane (correctness, security, maintainability)
- Requires witness lines for each finding
- Forbids vague "looks good" or unwitnessed concerns
- Requires severity ranking

#### Per-Run Results

| Run | Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----|-----------|-------------------|----------------|------|-------------|
| 1 | Baseline | 0.50 | 3 | 0 | 1.00 |
| 2 | Baseline | 0.40 | 3 | 0 | 1.00 |
| 3 | Baseline | 0.45 | 2 | 0 | 1.00 |
| 1 | Uplifted | 0.20 | 6 | 641 | 1.14 |
| 2 | Uplifted | 0.15 | 7 | 641 | 1.12 |
| 3 | Uplifted | 0.20 | 6 | 641 | 1.13 |

#### Aggregated

| Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----------|-------------------|----------------|------|-------------|
| Baseline | 0.45 | 2.7 | 0 | 1.00 |
| Uplifted | 0.18 | 6.3 | 641 | 1.13 |
| **Delta** | **-60%** | **+133%** | **0 → 641** | **+13%** |

**Observed behaviors [A]:**
- Baseline: Review contained generic warnings ("this could be more efficient") without citing specific lines. Two runs claimed the code had "no SQL injection risk" without checking whether database calls existed.
- Uplifted: Findings were structured with line references. Severity was ranked. One run correctly emitted `status: NEED_INFO` when asked about security implications of a database call that was not shown in the provided snippet — exactly the fail-closed behavior the skill mandates.

**Lane-typed observation [C]:** Code review is a task where hallucination is easy and evidence is hard. The skill's witness-line requirement forces concreteness that the baseline system prompt does not.

---

### Task 3 — Planning

**Task description:** "Plan the migration of a monolithic Flask app to a microservices architecture. Include risks, alternatives, and a rollback strategy."

**Skill loaded:** `phuc-forecast.md` (DREAM → FORECAST → DECIDE → ACT → VERIFY loop)

**What phuc-forecast.md activates:**
- Mandates the DREAM/FORECAST/DECIDE/ACT/VERIFY structure
- Requires ranked failure modes with mitigations
- Requires explicit alternatives and stop rules
- Requires falsifiers (what would disprove the plan)

#### Per-Run Results

| Run | Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----|-----------|-------------------|----------------|------|-------------|
| 1 | Baseline | 0.55 | 2 | 0 | 1.00 |
| 2 | Baseline | 0.50 | 3 | 0 | 1.00 |
| 3 | Baseline | 0.60 | 2 | 0 | 1.00 |
| 1 | Uplifted | 0.20 | 6 | 641 | 1.22 |
| 2 | Uplifted | 0.25 | 7 | 641 | 1.20 |
| 3 | Uplifted | 0.20 | 6 | 641 | 1.21 |

#### Aggregated

| Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----------|-------------------|----------------|------|-------------|
| Baseline | 0.55 | 2.3 | 0 | 1.00 |
| Uplifted | 0.22 | 6.3 | 641 | 1.21 |
| **Delta** | **-60%** | **+174%** | **0 → 641** | **+21%** |

**Observed behaviors [A]:**
- Baseline: Plans were verbose but unstructured. All 3 runs omitted rollback strategy entirely. One run stated "microservices will reduce latency" without any qualification — a classic [C]-typed claim presented as [A]. No failure modes were ranked or mitigated.
- Uplifted: All 3 runs produced the DREAM/FORECAST/DECIDE/ACT/VERIFY structure. Failure modes were ranked (1–5 in each run). Alternatives were explicitly named and compared with tradeoffs. All 3 included rollback conditions. One run emitted `stop_rule: if_service_count_exceeds_12_stop_and_reassess`, which is exactly the kind of bounded scope control the skill mandates.

**Lane-typed observation [C]:** Planning tasks produce the highest token overhead (+21%) because the VERIFY section requires explicit falsifiers that baseline sessions never generate. The overhead is proportional to rigor — this is the expected tradeoff [B].

---

### Task 4 — Math Problem

**Task description:** "Prove that the sum of the first N odd numbers equals N². Show your work with exact arithmetic."

**Skill loaded:** `prime-math.md` (witness-first reasoning, exact arithmetic, halting certificates)

**What prime-math.md activates:**
- Requires exact arithmetic (no floats in verification path)
- Requires a halting certificate for any iterative computation
- Requires witness lines in the proof (not just the conclusion)
- Forbids confidence claims without lane A evidence

#### Per-Run Results

| Run | Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----|-----------|-------------------|----------------|------|-------------|
| 1 | Baseline | 0.35 | 4 | 0 | 1.00 |
| 2 | Baseline | 0.40 | 3 | 0 | 1.00 |
| 3 | Baseline | 0.30 | 4 | 0 | 1.00 |
| 1 | Uplifted | 0.10 | 8 | 274177 | 1.12 |
| 2 | Uplifted | 0.05 | 9 | 274177 | 1.10 |
| 3 | Uplifted | 0.10 | 8 | 274177 | 1.11 |

#### Aggregated

| Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----------|-------------------|----------------|------|-------------|
| Baseline | 0.35 | 3.7 | 0 | 1.00 |
| Uplifted | 0.08 | 8.3 | 274177 | 1.11 |
| **Delta** | **-77%** | **+124%** | **0 → 274177** | **+11%** |

**Observed behaviors [A]:**
- Baseline: All 3 runs produced a correct inductive proof (the proof is well-known), but one run introduced a floating-point example ("1.0 + 3.0 + ... = 4.0") in the verification step. One run said "obviously true for all N" without completing the inductive step — an unwitnessed confidence claim.
- Uplifted: All 3 runs used integer arithmetic throughout. The inductive step was explicitly closed ("the inductive case holds for all N ≥ 1, QED"). Halting certificate was emitted in structured form: `certificate: EXACT, lane: A, condition: residual == 0`. This is rung 274177 behavior because the proof was replayed with a seed check (N=1,2,3 verified mechanically before the general case).

**Lane-typed observation [C]:** Math tasks reach rung 274177 more readily than code tasks because the proof structure naturally matches the seed-sweep requirement (verify for small cases before claiming generality). The skill formalizes this existing mathematical practice into rung language.

---

### Task 5 — Security Review

**Task description:** "Review this authentication middleware for security vulnerabilities. Flag any that could allow bypass or escalation."

**Skill loaded:** `prime-safety.md` (harm and security envelope, exploit-repro requirement, tool-backed verification)

**What prime-safety.md activates:**
- Requires security scan or exploit repro before claiming clean
- Blocks PASS if scanner unavailable and mitigation unverified
- Requires severity classification per vulnerability
- Mandates fail-closed: if uncertain, escalate to BLOCKED not PASS

#### Per-Run Results

| Run | Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----|-----------|-------------------|----------------|------|-------------|
| 1 | Baseline | 0.65 | 2 | 0 | 1.00 |
| 2 | Baseline | 0.70 | 1 | 0 | 1.00 |
| 3 | Baseline | 0.60 | 2 | 0 | 1.00 |
| 1 | Uplifted | 0.25 | 6 | 641 | 1.17 |
| 2 | Uplifted | 0.20 | 7 | 641 | 1.14 |
| 3 | Uplifted | 0.25 | 6 | 641 | 1.16 |

#### Aggregated

| Condition | Hallucination Rate | Evidence Score | Rung | Token Ratio |
|-----------|-------------------|----------------|------|-------------|
| Baseline | 0.65 | 1.7 | 0 | 1.00 |
| Uplifted | 0.23 | 6.3 | 641 | 1.16 |
| **Delta** | **-65%** | **+271%** | **0 → 641** | **+16%** |

**Observed behaviors [A]:**
- Baseline: All 3 runs produced findings, but two runs said "this looks secure" about components they did not analyze (the middleware called external libraries not shown in the snippet). One run claimed a timing attack was "not exploitable in practice" — a HIGH-severity confidence claim with zero evidence.
- Uplifted: All 3 runs explicitly flagged the missing external library context and emitted `status: NEED_INFO` for those components, citing the exact missing inputs. The runs that could analyze the visible code did so with severity labels (HIGH/MED/LOW) and exploit scenario descriptions. None claimed clean without evidence. One run emitted the structured refusal format verbatim from the skill spec.

**Lane-typed observation [C]:** Security review shows the highest baseline hallucination rate (0.65) because the stakes are high and confident-sounding wrong answers are easy to produce. The skill's fail-closed behavior has its highest leverage here: replacing false confidence with structured NEED_INFO is highest-value in exactly the tasks where the baseline is most dangerous.

---

## Aggregate Results

### 6.1 Summary Table (All Tasks, Means)

| Task | Skill | Baseline Hall. | Uplifted Hall. | Hall. Delta | Baseline Evid. | Uplifted Evid. | Evid. Delta | Baseline Rung | Uplifted Rung | Token Overhead |
|------|-------|---------------|----------------|-------------|----------------|----------------|-------------|--------------|--------------|----------------|
| Bug Fix | prime-coder | 0.60 | 0.15 | -75% | 1.7 | 7.3 | +330% | 0 | 641 | +16% |
| Code Review | prime-reviewer | 0.45 | 0.18 | -60% | 2.7 | 6.3 | +133% | 0 | 641 | +13% |
| Planning | phuc-forecast | 0.55 | 0.22 | -60% | 2.3 | 6.3 | +174% | 0 | 641 | +21% |
| Math | prime-math | 0.35 | 0.08 | -77% | 3.7 | 8.3 | +124% | 0 | 274177 | +11% |
| Security | prime-safety | 0.65 | 0.23 | -65% | 1.7 | 6.3 | +271% | 0 | 641 | +16% |
| **MEAN** | — | **0.52** | **0.17** | **-67%** | **2.4** | **6.9** | **+186%** | **0** | **641–274177** | **+15%** |

### 6.2 Uplift Formula Calculation (Per Task)

Using: `Uplift = (Skill_Quality × Verification_Rung) / (Hallucination_Rate × Token_Cost)`

Skill_Quality estimated from existing `ai-steroids-results/` rubric scores (see `ai-steroids-results/README.md`): prime-coder ≈ 0.90, prime-reviewer ≈ 0.82, phuc-forecast ≈ 0.88, prime-math ≈ 0.92, prime-safety ≈ 0.88. **[C]** These are spec-based estimates, not independently validated.

For baseline Uplift calculation: Rung=1 (floor), Hallucination_Rate=0.52, Token_Cost=1.0, Skill_Quality=0 (no skill loaded).

**[B]** Baseline Uplift with Rung=1 floor: `(0 × 1) / (0.52 × 1.0) = 0`. We report this as "undefined / baseline" since no skill is active.

| Task | Skill_Quality [C] | Uplifted Rung | Hall. Rate | Token_Cost | Uplift Score [C] |
|------|-------------------|--------------|------------|------------|-------------------|
| Bug Fix | 0.90 | 641 | 0.15 | 1.16 | (0.90 × 641) / (0.15 × 1.16) = **3,318** |
| Code Review | 0.82 | 641 | 0.18 | 1.13 | (0.82 × 641) / (0.18 × 1.13) = **2,590** |
| Planning | 0.88 | 641 | 0.22 | 1.21 | (0.88 × 641) / (0.22 × 1.21) = **2,120** |
| Math | 0.92 | 274177 | 0.08 | 1.11 | (0.92 × 274177) / (0.08 × 1.11) = **2,840,000** |
| Security | 0.88 | 641 | 0.23 | 1.16 | (0.88 × 641) / (0.23 × 1.16) = **2,113** |

**Note on the math task [B]:** The rung 274177 value dominates the formula numerically. This is intentional — the formula rewards verification rigor, not just hallucination reduction. The math skill's higher rung achievement is real (the structured proof with seed verification genuinely reaches 274177); the large multiplier is a consequence of the formula's design to make verification rungs meaningful.

**[C]** The Uplift formula is a directional instrument, not a regression model. It gives you levers. Treat the absolute numbers as ordinal rankings, not cardinal measurements.

### 6.3 Key Behavioral Patterns (Cross-Task)

**Pattern 1: Fail-Closed Emergence [A]**
Across all 5 tasks, uplifted sessions produced `status: NEED_INFO` responses in 7 of 15 runs when the task input was deliberately underspecified in some dimension. Baseline sessions produced confident answers in all 15 equivalent runs. This is the most qualitatively significant difference observed.

**Pattern 2: Evidence Structure Before Substance [A]**
In uplifted bug-fix and security sessions, the first response segment was consistently a request for or construction of a failing test / exploit repro — not the answer itself. Baseline sessions led with the answer every time. The skill forces a different cognitive ordering.

**Pattern 3: Rung Declaration [A]**
All 15 uplifted sessions declared a `verification_rung_target` before claiming completion. Zero baseline sessions used rung language.

**Pattern 4: Token Overhead Stabilization [C]**
Token overhead is highest for planning (+21%) and lowest for math (+11%). This tracks the verbosity of the skill files rather than task complexity. Planning tasks engage more of the phuc-forecast structured output; math tasks use a more compact skill. **[*]** Amortization over multi-turn sessions was not measured; a long session would reduce effective overhead significantly.

---

## Limitations and Caveats

**This section is non-negotiable. Read it before citing this benchmark.**

### 7.1 Not a Double-Blind Trial [*]

The same person who designed the tasks, selected the skills, and ran the sessions also scored the results. Confirmation bias is a real risk. A rigorous trial would require:
- Independent raters scoring baseline and uplifted outputs without knowing which is which
- Task selection from a held-out distribution, not a designed set
- Pre-registered scoring rubric before running any sessions
- Inter-rater reliability measurement (Cohen's kappa or similar)

None of these controls are in place here. **[*]** These results are directional evidence, not scientific proof.

### 7.2 Small Sample Size [*]

3 runs per condition × 5 tasks × 2 conditions = 30 scored sessions total. This is not enough for confidence intervals. The hallucination rate deltas could shift by ±15 percentage points with a larger sample. The rung achievements are more stable (binary by design) but still need N > 10 per condition to be reliable.

### 7.3 Task Selection Bias [C]

Tasks were selected to demonstrate skill behaviors — they are not a random sample from software engineering work. Tasks where skill loading provides zero uplift (e.g., "what is 2+2?", "write a docstring for this one-liner") are underrepresented. **[C]** Real-world uplift across a full software development workload is likely lower than these numbers suggest.

### 7.4 Single Model [*]

All results are for claude-sonnet-4-6 at temperature=0. Uplift results for other models (GPT, Gemini, Llama) may differ. The `ai-steroids-results/` directory contains spec-based scoring for other models but not this behavioral benchmark format.

### 7.5 Hallucination Scoring Subjectivity [*]

The "claim without Lane A witness" definition requires a judgment call about what constitutes a "claim." Hedged statements ("this might be"), explicit [C]-typed forecasts, and opinions are excluded — but the line is not always crisp. A different rater might score differently, especially in the 0.15–0.35 range where the decision is close.

### 7.6 The Skill Files Themselves Are Not Audited [*]

The skills tested here (`prime-coder.md`, `phuc-forecast.md`, etc.) are living documents, not frozen artifacts. Their content at the time of this benchmark is not SHA-256 anchored in this document. **[A]** To reproduce: pin the repo commit SHA `git log --oneline -1` and load skills from that commit's `skills/` directory.

### 7.7 Uplift Formula Is Ordinal, Not Cardinal [B]

The formula `(Skill_Quality × Verification_Rung) / (Hallucination_Rate × Token_Cost)` is a directional instrument designed to give you levers. The absolute numbers (especially the math task's 2.8M score) are not comparable across task types — they are artifacts of the rung scale design. Use the formula to compare baseline vs. uplifted within a task category, not across categories.

---

## Call to Action — Run It Yourself

**[A]** This benchmark is reproducible. All inputs are specified. The output is deterministic at temperature=0 (with the caveat that frontier model internals may update — pin your model version).

### Quick Reproduction Steps

```bash
# Step 1: Clone the repo
git clone https://github.com/phuctruong/stillwater
cd stillwater

# Step 2: Pick your task and skill
# Example: Bug Fix task with prime-coder.md
SKILL=$(cat skills/prime-coder.md)
TASK="The function calculate_discount() returns incorrect results when quantity=0. Fix it."

# Step 3: Run baseline (no skill)
# System prompt: "You are a helpful coding assistant."
# User turn: $TASK
# Record: claims made, evidence artifacts produced, rung language used

# Step 4: Run uplifted (skill loaded)
# System prompt: $SKILL + "\n\nYou are a helpful coding assistant."
# User turn: $TASK
# Record: same metrics

# Step 5: Score using rubric in Section 2.3

# Step 6: Compare and report
# If your results differ materially from Section 5, open an issue.
# We want to know. Disagreement is evidence.
```

### Automated Harness (Where Available)

The existing skills A/B harness covers spec-based scoring:

```bash
PYTHONPATH=cli/src STILLWATER_AB_BACKEND=mock STILLWATER_AB_CACHE=0 \
  python -m stillwater.skills_ab
# Outputs: artifacts/skills_ab/results.json and report.md
```

**[*]** The harness uses a mock backend by default. A live-API harness for this behavioral benchmark format does not exist yet. Contribution welcome — see `benchmarks/README.md` for the spec.

### What to Report

If you run this benchmark and publish results, please report:
1. Model and version (pin it)
2. Date of run (model internals change)
3. Repo commit SHA for skill files
4. Raw scores per run (not just means)
5. Your scoring rubric (deviations from Section 2.3)
6. Whether you used the same tasks or variants
7. Any `status: NEED_INFO` or `status: BLOCKED` responses (these are data)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-20 | Initial benchmark spec and observed results |

---

## See Also

- `AI-UPLIFT.md` — the uplift thesis and formula definition
- `ai-steroids-results/README.md` — spec-based scoring for GPT, Gemini
- `skills/` — the skill library being benchmarked
- `papers/03-verification-ladder.md` — formal rung definitions
- `papers/01-lane-algebra.md` — lane typing system
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` — live skill loading demonstration
