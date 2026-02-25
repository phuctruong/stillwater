# Persona A/B Benchmark — Methodology Overview

## What This Is

A structured A/B testing framework for measuring whether loading a domain-expert persona
into an LLM prompt produces measurably better output than a generic prompt covering the
same task. The hypothesis is that persona loading shifts both the voice and the epistemic
frame — not just style, but depth, accuracy, and the quality of principles cited.

---

## Test Structure

Every benchmark is a controlled comparison:

```
Variant A (control):    Generic instruction. No persona loaded.
                        Example: "Review this Python code and suggest improvements."

Variant B (treatment):  Same task, persona-loaded.
                        Example: "You are Guido van Rossum, creator of Python.
                                  Review this code through the lens of PEP 20..."
```

The task is identical. The framing and persona context differ. The scoring reveals whether
the persona loading shifts output quality on measurable dimensions.

---

## Scoring Dimensions (5 × 10 = 50 max)

Each test uses five dimensions tailored to the domain. General dimensions are:

| Dimension | What it measures |
|---|---|
| **Domain Depth** | Does the response cite first-principles, specific frameworks, named techniques, or does it stay surface-level? |
| **Accuracy / Correctness** | Are the claims technically correct? No invented facts, no hand-waving. |
| **Actionability** | Can a developer implement the feedback with no ambiguity? Or is it generic advice? |
| **Principles Cited** | Does the response invoke named principles (Zen of Python, STRIDE, red-green-refactor) rather than vague best-practices? |
| **Style Authenticity** | Does Variant B actually sound like the loaded persona? Is the voice distinctive and consistent? |

Domain-specific scoring dimensions are defined per test in `test_cases.md`.

---

## Scoring Scale

```
10 — Exceptional. Could not be improved on this dimension.
 9 — Near-perfect. Minor gap only.
 8 — Strong. Clearly above average.
 7 — Good. Solid, no major gaps.
 6 — Adequate. Meets the bar but misses opportunities.
 5 — Mediocre. Some value but significant gaps.
 4 — Weak. Surface-level treatment.
 3 — Poor. Fails the dimension in a noticeable way.
 2 — Very poor. Almost no value on this dimension.
 1 — Did not address the dimension at all.
```

---

## Statistical Significance Protocol

Minimum: **5 independent runs** per variant before drawing conclusions about a test case.
Why: LLM outputs have non-trivial variance. A single run can be a lucky outlier or a
degraded sample. Five runs give enough spread to compute mean and standard deviation.

```
Reported score = mean across 5 runs
SD threshold:   SD > 2.0 on any dimension flags that dimension as high-variance;
                treat result as preliminary until more runs collected.
Significance:   Delta >= +5 over A across 5 runs is considered a meaningful advantage.
                Delta >= +10 is a strong, consistent persona win.
                Delta < 3 should be reported as "no clear advantage."
```

---

## Persona Advantage Hypothesis

The benchmark tests three specific hypotheses:

1. **Frame hypothesis**: A persona-loaded prompt shifts the epistemic frame from
   "give useful advice" to "what would this specific expert do?" This produces responses
   anchored in named principles rather than generic best practices.

2. **Depth hypothesis**: Domain experts cite domain-specific frameworks (STRIDE for
   Schneier, red-green-refactor for Kent Beck, Zen of Python for Guido). Generic prompts
   do not. Persona loading should therefore increase score on the Principles Cited and
   Domain Depth dimensions more than on Accuracy and Actionability.

3. **Style hypothesis**: Style Authenticity should be near-zero for Variant A (generic
   voice, no distinctive style) and high for well-crafted personas. This dimension
   primarily measures persona quality, not task quality.

---

## What We Are NOT Measuring

- Raw intelligence of the model (both variants use the same model)
- Factual knowledge cutoff (both use the same training data)
- Token efficiency (not a dimension here — only output quality)
- Whether the persona is historically accurate (personas are optimization tools, not
  encyclopedias; verified against public records but not cited as authoritative sources)

---

## Failure Modes to Watch

| Failure | Description | Mitigation |
|---|---|---|
| **Persona flattery inflation** | Persona variant gets higher Authenticity scores regardless of content quality | Score Authenticity separately; validate that content scores are independent |
| **Prompt length confound** | Persona variant prompts are longer, producing longer outputs that score higher simply due to length | Evaluate density, not length. A short, precise review beats a long meandering one. |
| **Evaluator bias** | Knowing which is A vs B before scoring | Score both variants before labeling where possible |
| **Single-run fragility** | One run happens to be a strong sample for A and weak for B | Minimum 5 runs; report mean |
| **Generic persona drift** | Persona prompt does not actually load the expert's specific frameworks — just adds "You are X" | Persona files must include voice rules, catchphrases, domain expertise, and named frameworks |

---

## Files in This Directory

```
README.md            — This file. Methodology overview.
test_cases.md        — 10 defined A/B test cases with prompts, rubrics, hypotheses.
results.md           — Actual scored results from live runs (first 3 cases run in full).
founder-assessment.md — Honest assessment of Phuc Vinh Truong based on ecosystem evidence.
```

---

## Roadmap

Phase 1 (now): Run tests 1-3 with full A/B responses and scoring.
Phase 2: Run tests 4-7 with persona files that exist in personas/ directory.
Phase 3: Add 5-run statistical averaging for each test.
Phase 4: Cross-persona tests (e.g., guido + kent-beck combined vs. either alone).
Phase 5: Automated scoring using a separate judge agent (prime-judge model reads both
         variants without labels and scores them independently).

---

## Integration with Stillwater

This benchmark infrastructure is part of the Stillwater persona engine validation.
The rung target for persona loading is 641 (trivial tasks, no evidence bundle required).
A persona benchmark result that demonstrates consistent Delta >= +5 across 5 runs at
rung 641 is sufficient evidence to include that persona in the Stillwater Store.

Benchmark outputs are also used to tune the `quick_reference.probe_question` field in
each persona file — the probe question should be the one question that most reliably
elicits the persona's distinctive expertise.
