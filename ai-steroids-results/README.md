# AI Steroids Results (Consolidated)

This folder contains **human-readable score reports** for “model on Stillwater skills” evaluations.

Two different things are mixed in these reports:
1) **Spec-based scoring** (reading `skills/*.md` and rating how much they *should* improve discipline, auditability, and fail-closed behavior).
2) **Receipt-based benchmarking** (running the deterministic A/B harness that emits artifacts under `artifacts/skills_ab/`).

If you want the *replayable evidence*, use the harness (`python -m stillwater.skills_ab`). The per-model Markdown reports are summaries/interpretations.

## Files

- `gemini3-flash-on-steroids.md`: A/B story + scorecard framing “Gemini Flash on Steroids” (derived from the skills bench harness).
- `gpt5.1-mini-on-ai-steroids.md`: per-skill before/after (spec-based).
- `gpt5.2-on-ai-steroids.md`: per-skill before/after (spec-based).
- `gpt5.3-on-ai-steroids.md`: per-skill before/after (spec-based expectations; explicitly *not* backed by a gpt-5.3 harness run).

## Rubric (shared)

All the `gpt5.*` reports use a similar rubric: **1–10** scoring for how well each skill pushes the model toward:
- determinism (repeatable process),
- evidence/receipts (Red→Green gates; “no green without proof”),
- bounded scope + stop rules,
- auditability (why actions happened),
- safe tool use + fail-closed refusal/NEED_INFO.

## Consolidated scores (by skill)

These are the “before → after” numbers *as reported in each file* (not re-measured here).

| Skill | GPT-5.1 mini | GPT-5.2 | GPT-5.3 | Gemini report |
|---|---:|---:|---:|---:|
| `prime-coder.md` | 6 → 9 | 7 → 9 | 8 → 9 | 7 → 9 |
| `prime-math.md` | 4 → 9 | 6 → 9 | 7 → 9 | 0 → 10 |
| `prime-safety.md` | 5 → 9 | 6 → 9 | 7 → 9 | 4 → 10 |
| `phuc-context.md` | 5 → 8 | 6 → 8 | 7 → 8 | 6 → 10 |
| `phuc-forecast.md` | 5 → 9 | 6 → 9 | 7 → 9 | n/a |
| `phuc-swarms.md` | 4 → 8 | 5 → 8 | 6 → 8 | n/a |
| `phuc-cleanup.md` | 5 → 7 | 6 → 7 | 6 → 7 | n/a |

Notes:
- The Gemini report only assigns explicit “Score: X/10” for a subset of skills; missing entries are `n/a`.
- `gpt5.3-on-ai-steroids.md` is explicitly **spec-based expectation scoring** (not a receipt-backed run).

## What’s actually reproducible (receipts)

The repo’s “receipts generator” for these moves is the skills A/B harness:

```bash
PYTHONPATH=src STILLWATER_AB_BACKEND=mock STILLWATER_AB_CACHE=0 \
  python -m stillwater.skills_ab
```

Outputs:
- `artifacts/skills_ab/results.json` (machine-readable)
- `artifacts/skills_ab/report.md` (human-readable)

The notebook `PHUC-SKILLS-SECRET-SAUCE.ipynb` is a thin UI wrapper over the same harness.

