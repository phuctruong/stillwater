# TODO.md — Stillwater (Software 5.0 OS)
# Updated: 2026-03-01 | Belt: Orange | Rung: 65537 | Auth: 65537

## Architecture

```
stillwater/
  src/cli/src/stillwater/   -- core engine (TripleTwinEngine, CPULearner, DataRegistry, AuditLogger)
  src/store/                -- store client/validator/packager
  src/oauth3/               -- OAuth3 enforcer
  admin/                    -- admin UI + services (ports 8789-8794)
  data/default/             -- skills(37), recipes(34), swarms(13), personas(29), combos(40)
  papers/                   -- 61 research papers
  tests/                    -- 2,399 tests

DNA: Intelligence(session) = CPU_proposes x LLM_validates x confidence_gate -> learned_patterns
Pipeline: papers -> diagrams -> styleguides -> webservices -> tests -> code -> seal
```

## Codex Instructions

Read this file. Pick the next READY task (P0 first, then P1). Execute. Mark DONE with evidence.
Run `pytest tests/ src/cli/tests/ -v` after each task. Zero regressions allowed.

---

## P0 — Critical (Belt Advancement)

### T1: Paper format migration (backfill papers 01-55 with prime headers)
- **Status:** READY
- **Rung:** 641
- **What:** Add Paper 16 prime headers (Channel, Rung, GLOW, Diagram, Depends, Unlocks, Pipeline, DNA) to all 61 papers missing them.
- **Evidence:** Each paper has [2]Identity, [3]Architecture, [5]Laws, [7]Context, [11]Issues, [13]Evolution sections.
- **Test:** `grep -L "Channel:" papers/*.md` returns empty (all papers have Channel header).

### T2: Diagram gap — create Mermaid diagrams for undocumented services
- **Status:** READY
- **Rung:** 641
- **What:** Triple-Twin FSM, Store submission flow, OAuth3 enforcer flow, LLM Portal routing, Admin service mesh — all need Mermaid diagrams in `data/default/diagrams/`.
- **Evidence:** Each diagram is valid Mermaid, renders without error, and is referenced from its parent paper.
- **Test:** All `.md` files in `data/default/diagrams/` contain valid ```` ```mermaid ```` blocks.

### T3: Store client test fix (test_store_client.py import error)
- **Status:** READY
- **Rung:** 641
- **What:** `src/cli/tests/test_store_client.py` has import collision with `tests/test_store_client.py`. Fix the import path or rename to avoid pytest collection error.
- **Evidence:** `pytest src/cli/tests/test_store_client.py -v` passes cleanly.
- **Test:** `pytest tests/ src/cli/tests/ -v` collects all 2,399+ tests without errors.

## P1 — Important (Rung Advancement)

### T4: Seed bias fix (BUG-P1-005: 87.8% task vs 12.2% non-task)
- **Status:** READY
- **Rung:** 274177
- **What:** Rebalance CPU seed distribution so non-task intents (greeting, question, feedback, etc.) get fair representation. Target: no single label >40% of seeds.
- **Evidence:** Seed distribution histogram in test output. No label exceeds 40%.
- **Test:** New test `test_seed_balance.py` with parametrized assertion per label.

### T5: Ultra-short input handling (BUG-P1-003: <3 chars bypass extraction)
- **Status:** READY
- **Rung:** 274177
- **What:** Inputs <3 chars should route to SmallTalkResponder (friendly fallback), not bypass classification entirely.
- **Evidence:** `"hi"`, `"ok"`, `"?"` all classified correctly.
- **Test:** Parametrized test in `test_triple_twin.py` for inputs of length 1, 2, 3.

### T6: Question label resurrection (BUG-P1-002: dead label)
- **Status:** READY
- **Rung:** 274177
- **What:** "what", "how", "why" are stop words and get filtered before keyword matching. Add non-stop-word question indicators or adjust stop word list.
- **Evidence:** `"What is Stillwater?"` classifies as `question`, not `task`.
- **Test:** 5+ question-format inputs all hit `question` label.

### T7: pyproject.toml audit and cleanup
- **Status:** READY
- **Rung:** 641
- **What:** Verify `pyproject.toml` has correct entry points, dependencies, and metadata. Ensure `pip install -e ".[dev]"` works cleanly. Remove dead dependencies.
- **Evidence:** `pip install -e ".[dev]"` succeeds. `stillwater --help` runs.
- **Test:** Fresh virtualenv install smoke test.

## P2 — Enhancement

### T8: Evidence bundle export command
- **Status:** READY
- **Rung:** 274177
- **What:** CLI command `stillwater evidence export --run-id <ID>` that exports a sealed evidence bundle (ZIP with manifest + hash chain).
- **Evidence:** Export produces valid ZIP. Re-import verifies hash chain.
- **Test:** Round-trip export/import test with hash verification.

### T9: GLOW score CLI integration
- **Status:** READY
- **Rung:** 641
- **What:** CLI command `stillwater glow` that calculates GLOW score for current session based on git diff + test results + NORTHSTAR metrics.
- **Evidence:** Command runs, outputs G/L/O/W breakdown.
- **Test:** Unit test with mock git output.

### T10: Content syndication automation
- **Status:** READY
- **Rung:** 641
- **What:** Recipe that converts a paper from `papers/` to multi-platform content (phuc.net article, LinkedIn post, Substack newsletter, Twitter thread). Uses Brunson Hook+Story+Offer template.
- **Evidence:** Recipe file in `data/default/recipes/`. Dry run produces content.
- **Test:** Recipe validation passes store validator.

## P3 — Future

### T11: Rung 65537 adversarial test suite
- **Status:** BLOCKED (needs T4, T5, T6 first)
- **Rung:** 65537
- **What:** Full adversarial sweep: paraphrase attacks, injection attempts, edge cases, malicious input rejection, behavioral hash verification.
- **Evidence:** All adversarial tests pass. Behavioral hash stable across 10 runs.
- **Test:** `tests/test_adversarial.py` with 100+ parametrized cases.

### T12: Stillwater Store v2 (community submission pipeline)
- **Status:** BLOCKED (needs T8 evidence bundle)
- **Rung:** 65537
- **What:** Full submission → review → publish pipeline with rung gating. Contributors earn belt XP.
- **Evidence:** Skill submitted, reviewed, published. Belt XP incremented.
- **Test:** End-to-end submission test with mock reviewer.
