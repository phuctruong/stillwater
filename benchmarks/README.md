# Benchmarks

> "Knowing is not enough, we must apply. Willing is not enough, we must do." — Bruce Lee

This directory contains benchmark specs, results, and harness documentation for measuring **AI uplift** — the measurable delta in capability, safety, and verifiability between a raw LLM session and a skill-loaded, verification-gated session.

**Version:** 1.0.0 | **Date:** 2026-02-20 | **Auth:** 65537

---

## Claim Lane Key

- **[A]** Lane A — directly witnessed by executable artifact
- **[B]** Lane B — derivable from stated axioms
- **[C]** Lane C — heuristic or forecast; directional, not proven
- **[*]** Lane STAR — insufficient evidence; stated honestly

---

## What Lives Here

| File | What It Is |
|------|-----------|
| `ai-uplift-benchmark.md` | Primary benchmark: 5 tasks × baseline vs. skill-loaded, with methodology, results, and caveats |

**[*]** Additional benchmark files (automated harness, multi-model comparison, adversarial suite) are planned but do not exist yet. This README will be updated as they land.

---

## The Core Question

**Does loading a skill file into a system prompt produce measurable behavioral improvement?**

Specifically: does it reduce hallucinations, increase evidence completeness, and advance the verification rung achieved — at acceptable token cost?

**[C]** The answer the benchmark finds: yes, directionally and consistently, with the caveats documented in `ai-uplift-benchmark.md` Section 7. This is not a double-blind RCT. Treat results as directional evidence, not scientific proof.

---

## Uplift Formula

From `AI-UPLIFT.md`:

```
Uplift = (Skill_Quality × Verification_Rung) / (Hallucination_Rate × Token_Cost)
```

The benchmarks in this directory operationalize each term:
- `Skill_Quality` — estimated from `ai-steroids-results/` rubric scoring **[C]**
- `Verification_Rung` — measured by whether rung criteria are met in session output **[A]**
- `Hallucination_Rate` — fraction of unwitnessed claims in session output **[*]** (subjective scoring)
- `Token_Cost` — normalized token count, baseline=1.0 **[A]**

---

## Benchmark Design Principles

All benchmarks in this directory follow these rules:

1. **Lane-type every empirical claim.** [A/B/C/*] on every factual assertion.
2. **State limitations prominently.** A benchmark without a limitations section is marketing, not science.
3. **Make it reproducible.** Every benchmark must include the exact prompts, scoring rubric, and model/version used. **[A]**
4. **Separate spec-based from receipt-based scoring.** Spec scoring (reading a skill and rating expected behavior) is [C]-typed. Receipt scoring (running sessions and measuring output) is [A]-typed where artifacts exist.
5. **Do not cherry-pick.** Report all runs, not just the good ones. Include `status: NEED_INFO` and `status: BLOCKED` responses — they are data.
6. **Track skill file versions.** Skills evolve. Pin the repo commit SHA in any published result.

---

## How to Contribute a Benchmark

To add a new benchmark to this directory:

**Minimum viable benchmark (Lane [A] claims only):**
1. Specify the task(s) in unambiguous natural language
2. Specify the skill(s) being tested (with repo-relative path and commit SHA)
3. Specify the model, version, and temperature (pin it)
4. Run at least 3 sessions per condition (baseline and uplifted)
5. Score using the rubric in `ai-uplift-benchmark.md` Section 2.3, or define your own rubric explicitly
6. Report raw scores (all runs, not just means)
7. Write a limitations section that honestly addresses:
   - Sample size
   - Rater bias (single-rater? blind?)
   - Task selection method
   - Whether results would generalize

**Submit as a PR.** The benchmark will be reviewed for lane hygiene and limitations honesty before merge. A benchmark that hides its weaknesses will be rejected.

---

## Relationship to Other Evidence in This Repo

| Source | Type | What It Measures |
|--------|------|-----------------|
| `benchmarks/ai-uplift-benchmark.md` | Behavioral [A] + subjective [*] | Session output quality: hallucination rate, evidence completeness, rung |
| `ai-steroids-results/*.md` | Spec-based [C] | Expected discipline uplift from reading skill specs |
| `artifacts/skills_ab/` | Receipt-based [A] | Automated A/B harness output (mock backend) |
| `PHUC-SKILLS-SECRET-SAUCE.ipynb` | Demonstration [A] | Live skill loading walkthrough |
| `imo/` | Task-specific [A] | IMO math problem performance with prime-math loaded |
| `src/oolong/` | Task-specific [A] | Oolong benchmark performance with skill stack |
| `src/swe/` | Task-specific [A] | SWE-bench performance with prime-coder loaded |

**[B]** These sources are complementary, not redundant. Spec-based scoring tells you what to expect. Receipt-based scoring tells you what happened. Behavioral benchmarks tell you why it happened.

---

## Planned Work

The following benchmark formats are planned but not yet implemented. **[*]**

| Benchmark | Description | Blocking Dependency |
|-----------|-------------|---------------------|
| `multi-model-uplift.md` | Run ai-uplift-benchmark across GPT, Gemini, Llama | Live API harness (no mock) |
| `adversarial-paraphrase.md` | Test rung 65537 adversarial sweep: 5+ task paraphrases, measure drift | Manual session scoring |
| `session-length-amortization.md` | Measure how token overhead amortizes over 10+ turn sessions | Multi-turn harness |
| `null-edge-sweep.md` | Dedicated null/zero/empty input handling benchmark | Task design |
| `automated-harness.md` | Spec for a live-API A/B harness replacing the mock backend | API key + tooling |

Contributions to any of these are welcome. Open an issue or submit a PR with a benchmark proposal following the "minimum viable benchmark" requirements above.

---

## Quick Start

```bash
# Read the primary benchmark
cat benchmarks/ai-uplift-benchmark.md

# Run the existing automated harness (mock backend)
PYTHONPATH=src/cli/src STILLWATER_AB_BACKEND=mock STILLWATER_AB_CACHE=0 \
  python -m stillwater.skills_ab

# Check ai-steroids-results for spec-based scoring comparisons
cat ai-steroids-results/README.md

# Load a skill yourself and compare
SKILL=$(cat skills/prime-coder.md)
# Then run your task with and without $SKILL in the system prompt.
# Score using benchmarks/ai-uplift-benchmark.md Section 2.3.
```

---

## See Also

- `AI-UPLIFT.md` — the uplift thesis, formula, and belt progression
- `skills/README.md` — the skill library being benchmarked
- `papers/03-verification-ladder.md` — formal rung definitions
- `papers/01-lane-algebra.md` — lane typing system (epistemic hygiene)
- `ai-steroids-results/README.md` — spec-based model scoring
