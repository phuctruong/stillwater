# PZIP Built by Stillwater OS (Haiku Swarms) — Case Study + White Paper

**Date:** 2026-02-19  
**Stillwater OS version referenced:** `v1.2.3` (tag)  
**PZIP repo referenced:** `phuctruong/pzip` @ `5147e0e7` (local checkout)  
**Audience:** engineers evaluating “AI steroids” (process > model size)  

---

## 0) Executive summary (honest)

You can use **Stillwater OS skills + swarms** to get *frontier-level engineering discipline* out of a cheaper model (e.g., Haiku), **but** that claim is strongest when you also ship:

- receipts (prompts/responses + hashes)
- deterministic run records
- CI gates that a skeptic can replay

PZIP is a strong MVP demonstration of the approach **on the native (C++) delivery path**: the CLI round-trips and type-specific “weapons” fire (e.g., CSV lane). The Python packaging/test surface is currently **not** in “skeptic-proof” shape (missing module import breaks `pytest` collection), which is exactly the kind of gap Stillwater is designed to flush out and fix.

---

## 1) The claim we’re evaluating

> “Default Haiku is 5× cheaper. With Stillwater OS + Haiku Swarms, we can build real systems.”

This document evaluates that claim as:

- **Capability (Can Haiku do it?)**
- **Uplift (How much does Stillwater improve outcomes for cheap models?)**
- **Value (When does the economics win?)**

### Claim hygiene (important)

This repo (Stillwater) contains receipts for the **skills A/B harness** under `artifacts/skills_ab/`.  
It does **not** (yet) contain a full receipts harness for PZIP development sessions.

So: we can verify *some* PZIP behavior locally; we cannot fully prove “Haiku authored X% of the code” without the missing receipts.

---

## 2) What Stillwater OS adds (why cheap models become viable)

Stillwater OS is not “a bigger brain”. It’s a **control layer**:

- **Fail-closed defaults** (`NEED_INFO` / refusal when assets are missing)
- **Explicit contracts** (schemas, rung targets, forbidden states)
- **Verification gates** (Red→Green, plus ladder thinking)
- **Receipts** (replayable artifacts a skeptic can hash and re-run)

Net effect: cheap models spend fewer tokens “making things sound right” and more tokens “following a bounded procedure”.

---

## 3) PZIP as an MVP case study (what’s real and checkable today)

### 3.1 What PZIP is (1 sentence)

PZIP is a compression system that tries to beat baseline compressors by using **type-aware generators** (“compress the generator, not the bytes”), with a “never-worse” fallback.

### 3.2 What we can verify locally (without trusting narrative)

From the local checkout, the **native C++ CLI** works:

- `./pzip.sh --version` → reports `pzip 1.0.0-cpp`
- `./pzip.sh compress …` + `./pzip.sh decompress …` round-trips a file byte-exact
- `./pzip.sh info …` shows container metadata (`PZ01`, codec, sizes)
- `./pzip.sh benchmark test_data/sample.csv` shows the CSV weapon is firing and can beat LZMA on at least that sample

This is the kind of “minimum viable proof” Stillwater wants: *a skeptic can run it.*

### 3.3 What is currently *not* skeptic-proof (code-quality gaps)

Even with a working native MVP, PZIP has obvious repo-level quality hazards that will hurt outsiders:

- `pytest` collection fails because `pzip/__init__.py` imports `pzip.pipeline`, but `pzip/pipeline.py` is missing (import-time failure).
- `pytest` at repo root explodes due to vendored `google-cloud-sdk` tests that call `unittest.main()` during import (SystemExit).

These gaps don’t “invalidate” the MVP—but they *do* reduce the strength of “live production system” claims until there’s a pinned, replayable test/CI surface.

---

## 4) Was default Haiku capable of the code? (rating)

We separate two questions:

1) **Can Haiku produce working code with strong scaffolding?**  
2) **Can Haiku reliably produce a *maintainable, CI-gated, skeptic-proof repo* without that scaffolding?**

### 4.1 Capability score (Haiku, with Stillwater constraints)

- **Capability (with Stillwater): 8/10**  
  Reason: bounded workflows (Scout/Grace/Judge/Skeptic), explicit schemas, and verification gates shrink the search space. A cheaper model can execute within that box effectively.

- **Capability (without Stillwater): 5/10**  
  Reason: without receipts + gates, small models regress into “plausible patches” and unverifiable claims more often.

### 4.2 Confidence in attribution (“Haiku did the coding”)

- **Confidence that Haiku contributed materially to the MVP:** 7/10  
  Based on your report and the “agentic workflow” structure present in PZIP docs, it’s plausible.

- **Confidence that default Haiku alone authored the majority of the codebase:** 3/10  
  Without prompt/response receipts and a session manifest, authorship share is not provable from code quality alone.

If you want this to be 9–10/10 confidence, add the same kind of receipts we now emit in Stillwater’s `skills_ab` harness.

---

## 5) Uplift: what Stillwater changes for cheap models (estimate)

### 5.1 Expected uplift categories (where cheap models benefit most)

Stillwater tends to add the biggest uplift on:

- **refusal discipline** (stop when unsafe or missing assets)
- **schema compliance** (machine-readable outputs)
- **test-first behavior** (Red→Green)
- **auditability** (why decisions happened)

### 5.2 Estimated uplift (Haiku + Stillwater vs Haiku alone)

For a real engineering repo:

- **Reliability uplift:** +2 to +3 points (on a 10-point “skeptic acceptance” scale)  
- **Time-to-green uplift:** 1.3×–2× fewer “false green” iterations  
- **Ops uplift:** much higher if CI + receipts are wired early (the difference between a demo and a product)

These are estimates; the correct way to validate is to run A/B runs with receipts on the same tasks (Stillwater now has the harness pattern you can reuse).

---

## 6) Value: why “5× cheaper” can be true in practice

Let:

- `C_big` = cost per token of an expensive model
- `C_small` = cost per token of a cheap model (assume `C_small ≈ C_big/5` per your note)
- `T` = total tokens spent per task
- `I` = number of iterations to get a verified result

Total cost is roughly:

`Total ≈ C * T * I`

Stillwater’s value is primarily in reducing `I` (wasted iterations) and avoiding high-cost failures:

- “plausible but wrong” patches that fail later
- missing-asset guesswork
- unbounded scope refactors
- unsafe tool use

So even if Stillwater adds a bit of overhead per iteration, it can still win by cutting iteration count and preventing rework.

---

## 7) Productionizing the case study (what to do next)

To turn PZIP into a **Stillwater-grade, skeptic-proof production case study**, do this:

1) **Add receipts for PZIP development runs**  
   - mirror `artifacts/skills_ab/runs/<run_id>/manifest.json` behavior
   - record prompts, diffs, test commands, outputs, and hashes

2) **Fix repo test hygiene**  
   - resolve `pzip.pipeline` import failure (or remove import from `pzip/__init__.py`)
   - configure pytest to ignore vendored directories (e.g., `google-cloud-sdk/`)

3) **Add CI gates**  
   - `pytest -q tests`
   - `python -m compileall -q pzip`
   - minimal smoke round-trip (native and/or python SDK)

4) **Pin and publish benchmark receipts**  
   - if claiming win rates, ship the corpus list + logs + exact command lines

At that point, the “built with Haiku + Stillwater” story becomes a receipts-backed white paper, not a marketing claim.

---

## 8) Bottom line

**Is Haiku capable?** Yes—especially when Stillwater constrains the workflow and forces verification.  
**Does Stillwater create real uplift for cheap models?** Yes—primarily via fewer failed iterations and higher auditability.  
**Is PZIP already a perfect public “live production” proof?** Not yet, based on repo-level test/CI hygiene; the native MVP is strong, but the skeptic-proof harness is the missing last mile.

