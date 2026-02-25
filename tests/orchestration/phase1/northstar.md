# Phase 1 — Small Talk CPU Node: Northstar

## What Phase 1 Does
Phase 1 is the **gatekeeper**. It classifies every user input into one of 9 labels:
- `greeting`, `gratitude`, `humor`, `question`, `farewell`, `emotion`, `weather` → **STOP** (small talk response)
- `task` → **CONTINUE** to Phase 2 (intent classification)
- `unknown` → **LLM FALLBACK** (CPU couldn't classify)

## Northstar Metric
**CPU hit rate for Phase 1 classification** — percentage of inputs correctly classified by CPU without LLM fallback.

| Metric | Target | Current |
|--------|--------|---------|
| CPU hit rate | >95% | 100% (on 24 test prompts) |
| Task detection accuracy | 100% | ~90% (edge cases fail) |
| Non-task detection accuracy | 100% | ~60% (only 6 non-task seeds) |
| LLM fallback rate | <5% | 0% (all seeded — but edge cases untested) |

## What Phase 1 Should NOT Do
- Should NOT classify multi-intent inputs (e.g., "hello, fix the bug") — that's Phase 2's job
- Should NOT try to understand task details — just detect task vs non-task
- Should NOT call LLM if ANY keyword matches above threshold (CPU-first)
- Should NOT silently drop inputs — unknown → LLM fallback, never silent failure

## Critical Invariants
1. **Threshold invariant**: confidence >= 0.70 → CPU classifies; confidence < 0.70 → LLM fallback
2. **Gatekeeper invariant**: if label != "task" → pipeline STOPS. No Phase 2/3.
3. **Seed chain invariant**: every task keyword in Phase 2/3 MUST also exist as "task" seed in Phase 1
4. **Confidence bounds**: 0.0 <= confidence <= 1.0 for all inputs

## Known Issues (from QA audit)
- "question" label is DEAD — keywords "what","how","why" are all in stop_words
- Only 6 non-task seeds vs 43 task seeds — 87.8% bias
- Tie-breaking favors first keyword (position-dependent)
- Ultra-short inputs (< 3 chars) bypass keyword extraction
- Mixed inputs ("Hello! Fix the tests") may misclassify

## Files
- CPU node: `data/default/cpu-nodes/small-talk.md`
- Seeds: `data/default/seeds/small-talk-seeds.jsonl`
- Engine: `src/cli/src/stillwater/triple_twin.py` (_run_phase method)
- Learner: `src/cli/src/stillwater/cpu_learner.py`
