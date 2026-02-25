# Wish Notebook Method (L1 Default)

Date: 2026-02-19  
Authority: 65537  
Canonical externalization: Prime Mermaid

Key concept:
- Gamification is a required reporting layer for wishes (`quest`, `belt`, `promotion gate`), while correctness still depends on deterministic verification.

## 0) Entry criteria

Use this method for:
- New CLI commands
- Recipe/ripple changes
- Learning loop updates
- Integration changes (local/remote model routing)

Escalate to L2 full wish when:
- Security/safety/compliance impact is high
- Benchmark claim is externally published
- Same failure mode repeats 2+ times

## 0A) Quest framing (Aladdin + Dojo)

Use this mnemonic while keeping the method strict:
1. Cave map: define state graph.
2. Lamp wording: define capability and non-goals precisely.
3. Genie leash: define forbidden states and fail-closed rules.
4. Dojo sparring: run acceptance plus adversarial tests.
5. Relic proof: emit deterministic artifacts.

## 1) Notebook contract (required sections)

Every wish notebook MUST contain:
1. Capability statement (one sentence)
2. Non-goals (explicit exclusions)
3. Prime Mermaid state graph (canonical)
4. Acceptance tests (explicit pass/fail)
5. Evidence plan (artifacts + hashes)
6. Ambiguity policy (`NEED_INFO` or fail-closed)

## 2) Prime Mermaid rule

The notebook may include helper JSON tables, but the canonical logic is:
- `*.prime-mermaid.md` (human contract)
- `*.mmd` (canonical body)
- `*.sha256` (identity)

No net-new YAML/JSON reasoning file is source-of-truth.

## 3) Minimal execution loop

1. Draft notebook from template
2. Run tests in notebook
3. Emit artifacts in `artifacts/wishes/<wish_id>/`
4. Verify deterministic rerun
5. Promote to `examples/` if reusable

## 4) Required outputs

For each wish notebook run:
- `results.json` (derived summary)
- `state.mmd`
- `state.sha256`
- `verification.md`

## 5) Scoring gate (10-point scale)

1. Clarity of capability and non-goals
2. Closed state graph
3. Test completeness
4. Determinism under rerun
5. Evidence quality
6. Counter-bypass compliance (if numeric task)
7. Fail-closed behavior
8. Replayability
9. Human audit speed
10. Promotion readiness

Promotion rule:
- `<8.5`: keep local draft
- `8.5-9.4`: usable; monitor
- `>=9.5`: promote to template/example candidate

## 5A) Belt system (gamified reporting)

Map score to optional rank badges:
- `<8.5`: `White Belt`
- `8.5-8.9`: `Yellow Belt`
- `9.0-9.4`: `Green Belt`
- `9.5-9.7`: `Brown Belt`
- `9.8-10.0`: `Black Belt`

Badge rules:
- Badge is valid only if deterministic rerun checks pass.
- Any failed forbidden-state test drops rank to `White Belt` until fixed.

## 6) Role split (lightweight)

- Planner: owns notebook contract and tests
- Coder: implements code/ripple changes only
- Runner: executes and reports evidence

If one person does all roles, still follow role boundaries per phase.

## 7) Anti-drift defaults

1. One Prime Mermaid graph per wish (single canonical graph)
2. One artifact directory per run
3. One replay command in verification cell
4. One explicit forbidden-state list
5. One ambiguity output contract

## 8) Definition of done

A wish notebook is done when:
- all acceptance tests pass
- artifact hashes are stable across reruns
- no forbidden state appears
- replay reproduces the same result

## 9) Optional team game loop

For weekly CLI evolution sprints:
1. Each feature starts as one wish notebook quest.
2. Team demo includes graph, tests, and artifact hash replay.
3. Top reproducibility score wins promotion to `examples/`.
4. Regressions trigger rematch with stricter adversarial tests.
