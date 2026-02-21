# ROADMAP: Stillwater — Phased Build Plan

> Last updated: 2026-02-21
> Northstar: `NORTHSTAR.md`
> See also: `case-studies/stillwater-itself.md`

---

## Phase 0: Audit (Now — Week 0)

**Goal**: Establish current rung baseline. Know what exists, what is at 641, what needs upgrade.

### Tasks

- [ ] Run all tests: `pytest tests/ -v` — record pass/fail per module
- [ ] List all skills in `skills/` and assign current rung (641 / 274177 / 65537 / unknown)
- [ ] List all swarm agent types in `swarms/` and note completeness
- [ ] Identify Stillwater Store gaps: API endpoints do not exist yet (STORE.md is spec only)
- [ ] Identify LLM Portal gaps: `stillwater.py` — which LLMs are wired, which are stubs
- [ ] Produce audit report: `case-studies/stillwater-itself.md` (update metrics table)

### Build Prompt (Phase 0)

```
Load prime-safety + prime-coder + phuc-forecast.
Task: Audit the stillwater repository for rung baseline.
Repo: stillwater/
Steps:
  1. Run: pytest tests/ -v > evidence/audit_tests.txt 2>&1
  2. List all files in skills/ with line counts
  3. List all files in swarms/ with line counts
  4. Check stillwater.py for LLM provider wiring
  5. Update case-studies/stillwater-itself.md Metrics table
Rung target: 641 (audit pass)
Evidence required: evidence/audit_tests.txt + updated case-studies/stillwater-itself.md
```

---

## Phase 1: OAuth3 Integration (Week 1–2) — COMPLETE

**Goal**: Stillwater has a formal OAuth3 spec and an enforcement skill that solace-browser and solace-cli can import.

### Tasks

- [x] Create `papers/oauth3-spec-v0.1.md` — formal OAuth3 specification (rung 641, 2026-02-21)
  - AgencyToken schema (JSON), 7 required + 5 optional fields
  - Scope registry: 5 platforms, 30 scopes, step-up annotations
  - Consent flow (GET /consent → POST /consent/approve)
  - Revocation (DELETE /tokens/{id}, bulk DELETE /tokens, mid-execution halt)
  - Evidence bundle: oauth3_audit.jsonl with SHA-256 sidecar
- [x] Create `skills/oauth3-enforcer.md` — enforcement skill (rung 641, 2026-02-21)
  - G1 (schema) → G2 (TTL) → G3 (scope) → G4 (revocation), fail-closed
  - 876 lines, 11 sections, FSM with 8 forbidden states
  - 16/16 tests pass (`tests/test_oauth3_enforcer.py`)
- [ ] Update `STORE.md` with OAuth3 requirements for skill submissions
- [ ] Update `skills/prime-browser.md` (or create if missing) — browser automation gating

### Build Prompt (Phase 1 — OAuth3 Spec)

```
Load prime-safety + prime-coder + phuc-forecast.
Task: Write papers/oauth3-spec-v0.1.md for stillwater.
Reference: solace-browser/OAUTH3-WHITEPAPER.md
Location: stillwater/papers/oauth3-spec-v0.1.md
Requirements:
  - AgencyToken JSON schema (id, issued_at, expires_at, scopes, issuer, subject, signature_stub)
  - Scope format: platform.action.resource (e.g., linkedin.post.text, gmail.read.inbox)
  - Consent flow: GET /consent?scopes=X,Y → human approval → POST /consent/approve → token
  - Revocation: DELETE /tokens/{id} → immediate effect on all enforcement gates
  - Evidence: every token operation produces oauth3_audit.json with sha256
Rung target: 641
Evidence required: papers/oauth3-spec-v0.1.md committed with sha256 in artifacts.json
```

### Build Prompt (Phase 1 — OAuth3 Enforcer Skill)

```
Load prime-safety + prime-coder.
Task: Write skills/oauth3-enforcer.md for stillwater.
Reference: stillwater/papers/oauth3-spec-v0.1.md (must exist first)
Location: stillwater/skills/oauth3-enforcer.md
Requirements:
  - Skill that any agent can load to enforce OAuth3 gates
  - Four gate checks: valid token, scope match, TTL, revocation
  - Output schema: oauth3_audit.json
  - Integration: how prime-coder + oauth3-enforcer interact in a recipe run
  - Fail-closed: if token missing → status=BLOCKED stop_reason=OAUTH3_MISSING_TOKEN
Rung target: 641
Evidence required: skills/oauth3-enforcer.md committed with sha256
```

---

## Phase 2: Store Client SDK + Rung Validator (Month 1)

**Goal**: Stillwater has a client SDK for submitting/fetching skills from the Stillwater Store. The server API lives in `solaceagi` — stillwater owns the client and the rung validation logic.

### Architecture Split
- **stillwater** (this repo): Store client SDK, rung validator, skill packaging, STORE.md spec
- **solaceagi** (server): FastAPI endpoints (POST/GET /store/*), auth, rate limiting, review queue

### Tasks

- [ ] Store client SDK: `store/client.py`
  - `submit_skill(skill_path, author, rung_claimed)` — package + submit to solaceagi Store API
  - `fetch_skill(skill_id)` — download a skill from the Store
  - `list_skills(query)` — search the Store catalog
  - `install_skill(skill_id, target_dir)` — fetch + write to local skills/
- [ ] Rung validator: `store/rung_validator.py`
  - Verify evidence bundle before submission (tests.json, plan.json, behavior_hash)
  - Check rung_claimed matches evidence artifacts
  - Run behavioral hash replay (3 seeds: 42, 137, 9001)
- [ ] Skill packager: `store/packager.py`
  - Bundle skill.md + tests + evidence into submission payload
  - Validate STORE.md requirements (OAuth3 scope declaration if external platform)
  - Compute SHA-256 manifest
- [ ] Tests: `tests/test_store_client.py`

### Build Prompt (Phase 2 — Store Client SDK)

```
Load prime-safety + prime-coder + phuc-forecast.
Task: Build Stillwater Store client SDK.
Location: stillwater/store/
Files to create:
  store/client.py (Store client — submit, fetch, list, install)
  store/rung_validator.py (evidence bundle + rung verification)
  store/packager.py (skill packaging for submission)
  tests/test_store_client.py
Reference: stillwater/STORE.md
Requirements:
  - Client calls solaceagi.com Store API (POST/GET /store/*)
  - Rung validator checks evidence bundle integrity before submission
  - Packager bundles skill.md + tests + evidence with SHA-256 manifest
  - Authentication: sw_sk_ API key passed via Authorization header
  - No server code — server lives in solaceagi project
Rung target: 641
Evidence required: tests/test_store_client.py passing (pytest -v)
```

---

## Phase 2.5: Dragon Tip Integration in LLM Client Library

**Goal**: Stillwater's LLM client library (`stillwater.llm_client`) includes hooks for the Dragon Tip Program so that solaceagi.com can calculate tips on BYOK API calls routed through the Stillwater stack.

### Tasks

- [ ] Add `tip_callback` parameter to `llm_call()` and `llm_chat()` — optional callback invoked after each API call with `{model, input_tokens, output_tokens, estimated_cost_usd}`
- [ ] Add `usage_tracker` module: accumulates per-session token usage, recipe hit/miss counts, and estimated savings
- [ ] Ensure cost estimation uses exact Decimal arithmetic (no float in any cost path)
- [ ] `tip_callback` is a no-op by default — only solaceagi.com sets it to route to `tip/engine.py`
- [ ] Tests: `tests/test_llm_tip_hooks.py` — callback invocation, cost estimation accuracy, Decimal-only arithmetic

### Build Prompt (Phase 2.5 — Tip Hooks)

```
Load prime-safety + prime-coder.
Task: Add Dragon Tip callback hooks to stillwater LLM client library.
Location: stillwater/ (llm_client module)
Requirements:
  - llm_call() and llm_chat() accept optional tip_callback(cost_report: dict)
  - cost_report: {model, input_tokens, output_tokens, estimated_cost_usd: Decimal}
  - usage_tracker module: accumulate session stats (total calls, recipe hits, tokens saved)
  - All cost estimates: exact Decimal — no float
  - Callback is no-op by default (zero overhead for non-solaceagi users)
  - Zero breaking changes to existing llm_call/llm_chat signatures
Rung target: 641
Evidence required: tests/test_llm_tip_hooks.py passing
```

---

## Phase 3: LLM Portal Polish (Month 2)

**Goal**: Stillwater's LLM Portal supports multiple providers, users bring own API keys, session management is clean.

### Tasks

- [ ] Multi-LLM provider support
  - Anthropic Claude (claude-opus-4-6, claude-sonnet-4-6, claude-haiku-3-5)
  - OpenAI (gpt-4o, gpt-4o-mini)
  - Llama (via Ollama local endpoint)
  - Qwen (via local or Dashscope endpoint)
  - Custom endpoint: `{base_url, api_key, model_id}` passthrough
- [ ] User brings own API key → zero LLM cost to Stillwater
  - Key stored encrypted in session (AES-256-GCM, session-scoped)
  - Never logged, never persisted to disk
- [ ] Session management
  - Session ID → skill pack → active task → evidence bundle
  - Session expiry: 24h
- [ ] Evidence bundle display
  - Show `tests.json`, `plan.json`, `behavior_hash.txt` inline in UI
  - Download as `.zip`

### Build Prompt (Phase 3 — LLM Portal Multi-Provider)

```
Load prime-safety + prime-coder.
Task: Add multi-LLM provider support to stillwater LLM Portal.
Location: stillwater/
Reference: existing stillwater.py (read first)
Requirements:
  - Providers: anthropic, openai, ollama (local), dashscope (qwen), custom
  - Config: llm_config.yaml already exists — extend it for new providers
  - User-supplied API key: encrypted in session dict, never written to disk
  - Model selection UI: dropdown or CLI flag
  - Zero breaking changes to existing Anthropic integration
Rung target: 641
Evidence required: tests showing each provider can be initialized (mock or live ping)
```

---

## Phase 4: Self-Promotion to Rung 65537 (Month 3)

**Goal**: Stillwater itself runs at rung 65537. Self-verification is the product demo.

### Tasks

- [ ] Adversarial sweep: 5 paraphrases per skill (13 skills × 5 = 65 paraphrase tests)
  - Use prime-coder adversarial_paraphrase_sweep (min_paraphrases=5)
  - Record behavioral hashes for each paraphrase
- [ ] Behavioral hash tracking across 3 seeds
  - `evidence/behavior_hash.txt` + `evidence/behavior_hash_verify.txt`
  - Seeds: 42, 137, 9001
- [ ] Security gate: semgrep + bandit clean
  - `semgrep --config=p/python stillwater.py store/ skills/` → 0 findings
  - `bandit -r stillwater.py store/ skills/` → 0 high/medium findings
  - Record tool versions + rule set hash in `evidence/security_scan.json`
- [ ] 30-day continuous verification
  - GitHub Actions: daily rung 641 check (pytest + behavioral hash)
  - Slack/email alert if hash drifts
  - Badge in README: "Rung 65537 — verified YYYY-MM-DD"
- [ ] Update CHANGELOG.md: v2.0.0 release

### Build Prompt (Phase 4 — Security Gate)

```
Load prime-safety + prime-coder + phuc-forecast.
Task: Run security gate for stillwater (rung 65537 requirement).
Repo: stillwater/
Steps:
  1. Install semgrep if not present: pip install semgrep
  2. Run: semgrep --config=p/python stillwater.py store/ --json > evidence/semgrep_results.json
  3. Install bandit if not present: pip install bandit
  4. Run: bandit -r stillwater.py store/ -f json > evidence/bandit_results.json
  5. Check: 0 high/medium findings in both tools
  6. Write evidence/security_scan.json with tool versions + rule set hash + verdict
Rung target: 65537 (security gate required)
Evidence required: evidence/security_scan.json with status=PASS
```

### Build Prompt (Phase 4 — 30-Day CI Badge)

```
Load prime-safety + prime-coder.
Task: Add GitHub Actions workflow for daily rung 641 verification + behavior hash check.
Location: stillwater/.github/workflows/rung-check.yml
Requirements:
  - Trigger: daily cron (00:00 UTC) + push to main
  - Steps: pip install -e . → pytest tests/ -v → python scripts/behavior_hash.py → compare hashes
  - On hash drift: fail the workflow + emit artifact with drift details
  - Badge: add to README.md: [![Rung Check](badge_url)](workflow_url)
  - Seeds: 42, 137, 9001 (all three must agree)
Rung target: 641 (CI pipeline itself)
Evidence required: .github/workflows/rung-check.yml passing on main branch
```

---

## Milestone Summary

| Phase | Target Date | Rung Gate | Key Deliverable |
|-------|------------|-----------|----------------|
| Phase 0: Audit | Week 0 | 641 | Baseline audit report |
| Phase 1: OAuth3 | Week 1–2 | 641 | `papers/oauth3-spec-v0.1.md` + `skills/oauth3-enforcer.md` — COMPLETE |
| Phase 2: Store Client | Month 1 | 641 | `store/client.py` + `store/rung_validator.py` (server in solaceagi) |
| Phase 2.5: Dragon Tip Hooks | Month 1 | 641 | `tip_callback` in llm_call/llm_chat + `usage_tracker` module |
| Phase 3: LLM Portal | Month 2 | 641 | Multi-provider support + session management |
| Phase 4: Rung 65537 | Month 3 | 65537 | Self-verification badge + 30-day CI |

---

## Build Discipline

All phases follow the prime-coder protocol:
1. Write failing test first (Kent's Red Gate)
2. Implement minimum code to pass (Green Gate)
3. Run full test suite — no regressions
4. Produce evidence bundle (`evidence/plan.json`, `evidence/tests.json`)
5. Commit with `feat:` or `fix:` prefix + evidence pointer

Model selection guidance:
- `haiku` — volume tasks (listing, formatting, boilerplate)
- `sonnet` — complex logic (API design, skill authoring)
- `opus` — promotion gate (adversarial sweep, security audit, rung 65537 seal)
