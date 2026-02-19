# Red-Green Gate: Dual-Witness Verification For AI-Generated Changes

## Abstract

When an AI system proposes a patch, "it looks right" is not evidence. The Red-Green gate is a minimal, tool-friendly protocol that turns a patch proposal into a dual-witness claim:

- **RED witness:** the bug is real (a test or repro fails before the change).
- **GREEN witness:** the bug is fixed (the same repro passes after the change).
- **GOLD witness (optional but recommended):** no regressions (broader test suite passes).

This paper defines the protocol from first principles, shows how it composes with the verification ladder (641 -> 274177 -> 65537), and maps it to the concrete implementation patterns used in this repository (SWE-bench, notebooks, and skills).

## 1. Problem Statement

AI coding failures fall into a small number of buckets:

- **Non-reproducible bug reports:** patching a ghost.
- **Patch that "fixes" nothing:** no measurable behavior change.
- **Patch that fixes one thing and breaks another:** silent regressions.
- **Patch with hidden IO / nondeterminism:** flakiness mistaken for correctness.

The Red-Green gate addresses the most common failure: accepting a patch without a verified before/after witness.

## 2. First Principles: What "Correct" Means For A Patch

For a patch that claims to fix a defect:

1. There must exist an **observable predicate** of failure (test, repro script, invariant check).
2. The predicate must evaluate to **false** after the patch (the failure disappears).
3. The evaluation must be **replayable** under the same constraints (no time/random/hidden state dependencies in the judged path).

In engineering terms: correctness is a relation between (inputs, environment, code) and an observed output. If we cannot witness a change in that relation, we cannot claim a fix.

## 3. The Red-Green Gate Protocol (Spec)

### 3.1 Applicability

Use the Red-Green gate when a claim involves:

- bugfix
- regression
- "tests are failing"
- security fix (with additional security evidence)

### 3.2 RED Gate (Before)

Goal: prove the bug exists in the current baseline.

Required:

- a minimal repro command or test selection
- recorded exit code and output
- a stable invocation (pin inputs; disable time/random when possible)

Fail-closed:

- if the repro does not fail: status becomes `BLOCKED` (non-reproducible) or `NEED_INFO` (missing assets), but do not patch blindly.

### 3.3 GREEN Gate (After)

Goal: prove the same repro passes after the patch.

Required:

- apply the patch cleanly
- rerun the exact repro
- record exit code and output

Fail-closed:

- if the repro still fails: revert or iterate with an isolated delta (no stacked speculative patches).

### 3.4 GOLD Gate (Regressions)

Goal: prove the broader system did not break.

Required:

- run the relevant test suite (or an agreed subset)
- record command and results

Fail-closed:

- if regressions appear: revert and re-localize.

## 4. Composition With The Verification Ladder

The Red-Green gate is the minimal dual-witness at the lowest rung.

- **Rung 641:** Red-Green witness exists and is replayable.
- **Rung 274177:** Red-Green plus stress/seed/regression sweeps (broader confidence).
- **Rung 65537:** Red-Green plus formal/invariant proofs where applicable (highest confidence).

Important: a Red-Green witness does not guarantee you tested the right thing. The ladder is the control that expands coverage beyond a single repro.

## 5. Evidence Artifacts (What To Save)

To be peer-reviewable, every run should leave behind a minimal evidence bundle:

- `plan.json` (what you intended to do, and why)
- `run_log.txt` (commands executed, tool outputs)
- `tests.json` (test commands + pass/fail summary)
- `repro_red.log` (RED witness output)
- `repro_green.log` (GREEN witness output)
- `artifacts.json` (hashes of produced artifacts)

The exact schema is defined by the coding skill layer in this repository (`skills/prime-coder.md`).

## 6. Repository Mapping (Where This Lives In Code)

This repo contains multiple layers that refer to Red-Green:

- Skill spec: `skills/prime-coder.md` (Kent_Red_Green_Gate section + Output_Contract)
- SWE solver: `swe/src/swe_solver_real.py` (RED/GREEN gate plumbing and proof text generation; optional/legacy — requires `STILLWATER_ENABLE_LEGACY_SOLVERS=1`)
- Orchestration tests: `tests/phuc_orchestration/` (phase-wise unit tests)
- Notebooks:
  - `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` (evidence + ladder framing)
  - `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb` (ladder framing)
  - `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb` (Skeptic phase enforces red/green)

## 7. Limitations (Honest Boundaries)

- Red-Green is only as good as the repro predicate: if the predicate is wrong, you can get a "green" that doesn't fix the real issue.
- Some tasks are not naturally Red-Green (feature work, research writeups). Use a different verification predicate (golden files, contract tests, API diff lock).
- Formal proof claims must be backed by actual formal tooling or invariant checks; otherwise label as aspirational.

## 8. Practical Checklist

1. Define the failure predicate (test/repro).
2. Run it on baseline and record RED output.
3. Apply the smallest patch that can plausibly fix it.
4. Rerun the predicate and record GREEN output.
5. Run regression suite (GOLD) if available.
6. Save evidence artifacts with hashes.
