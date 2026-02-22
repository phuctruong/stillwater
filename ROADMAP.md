# ROADMAP: Stillwater — Phased Build Plan

> Last updated: 2026-02-21
> Northstar: `NORTHSTAR.md`
> See also: `case-studies/stillwater-itself.md`

## Status Summary (2026-02-21)

| Phase | Status | Tests |
|-------|--------|-------|
| Phase 0: Audit | DONE | 258 |
| Phase 1: OAuth3 | DONE | — (included in 258) |
| Phase 2: Store Client SDK | DONE | 66 |
| Phase 2.5: LLM Usage Tracker | DONE | 55 |
| Phase 3: LLM Portal | DONE | 91 |
| Phase 4: Rung 65537 CI | DONE | 41 |
| Phase 5: Persona System | DONE | 50 |
| Phase 6: Hackathon System | DONE | — |
| **Total** | **ALL DONE** | **445** |

**Rung 65537 CI badge deployed. All phases complete.**

---

## Phase 0: Audit — DONE

**Goal**: Establish current rung baseline. Know what exists, what is at 641, what needs upgrade.

**Result**: 258 tests pass. Retroactive QA complete (persona-enhanced). Security scan clean.

### Tasks

- [x] Run all tests: `pytest tests/ -v` — 258 tests pass
- [x] List all skills in `skills/` and assign current rung — 15+ skills inventoried
- [x] List all swarm agent types in `swarms/` — 19 swarm agents (all persona-enhanced)
- [x] Identify Stillwater Store gaps: API endpoints do not exist yet (STORE.md is spec only)
- [x] Identify LLM Portal gaps: `stillwater.py` — providers mapped
- [x] Produce audit report: `case-studies/stillwater-itself.md` (updated)

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
- [x] Update `STORE.md` with OAuth3 requirements for skill submissions
- [ ] Update `skills/prime-browser.md` (or create if missing) — browser automation gating (deferred — browser skills managed in solace-browser repo)

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

## Phase 2: Store Client SDK + Rung Validator (Month 1) — DONE

**Goal**: Stillwater has a client SDK for submitting/fetching skills from the Stillwater Store. The server API lives in `solaceagi` — stillwater owns the client and the rung validation logic.

**Result**: 66 tests pass. Module-level convenience functions added. `StillwaterStoreClient` with rung validation + SHA-256 manifest verification. Rung 641 achieved.

**Test count**: 258 total (includes 66 store client tests in `tests/test_store_client.py`)

### Architecture Split
- **stillwater** (this repo): Store client SDK, rung validator, skill packaging, STORE.md spec
- **solaceagi** (server): FastAPI endpoints (POST/GET /store/*), auth, rate limiting, review queue

### Tasks

- [x] Store client SDK: `store/client.py`
  - `submit_skill(skill_path, author, rung_claimed)` — package + submit to solaceagi Store API
  - `fetch_skill(skill_id)` — download a skill from the Store
  - `list_skills(query)` — search the Store catalog
  - `install_skill(skill_id, target_dir)` — fetch + write to local skills/
- [x] Rung validator: `store/rung_validator.py`
  - Verify evidence bundle before submission (tests.json, plan.json, behavior_hash)
  - Check rung_claimed matches evidence artifacts
  - Run behavioral hash replay (3 seeds: 42, 137, 9001)
- [x] Skill packager: `store/packager.py`
  - Bundle skill.md + tests + evidence into submission payload
  - Validate STORE.md requirements (OAuth3 scope declaration if external platform)
  - Compute SHA-256 manifest
- [x] Tests: `tests/test_store_client.py` — 66 tests pass

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

## Phase 2.5: LLM Usage Tracker in LLM Client Library — DONE

**Goal**: Stillwater's LLM client library (`stillwater.llm_client`) includes post-call hooks so that integrators can track usage, costs, and recipe savings on API calls routed through the Stillwater stack.

**Result**: 55 tests pass. `tip_callback` and `usage_tracker` parameters integrated into `llm_call()`, `llm_chat()`, `LLMClient.complete()`, and `LLMClient.chat()`. All cost math uses exact Decimal arithmetic — no float in any cost path. `SessionUsageTracker` delivered. Rung 641 achieved.

### Tasks

- [x] Add `tip_callback` parameter to `llm_call()` and `llm_chat()` — optional callback invoked after each API call with `{model, input_tokens, output_tokens, cost_hundredths_cent}`
- [x] Add `usage_tracker` module (`stillwater/usage_tracker.py`): accumulates per-session token usage, recipe hit/miss counts, and estimated savings
- [x] Ensure cost estimation uses exact Decimal arithmetic (no float in any cost path)
- [x] `tip_callback` is a no-op by default

### Build Prompt (Phase 2.5 — Usage Tracker)

```
Load prime-safety + prime-coder.
Task: Add post-call callback hooks to stillwater LLM client library.
Location: stillwater/ (llm_client module)
Requirements:
  - llm_call() and llm_chat() accept optional tip_callback(cost_report: dict)
  - cost_report: {model, input_tokens, output_tokens, estimated_cost_usd: Decimal}
  - usage_tracker module: accumulate session stats (total calls, recipe hits, tokens saved)
  - All cost estimates: exact Decimal — no float
  - Callback is no-op by default (zero overhead)
  - Zero breaking changes to existing llm_call/llm_chat signatures
Rung target: 641
Evidence required: tests passing
```

---

## Phase 3: LLM Portal Polish (Month 2) — DONE

**Goal**: Stillwater's LLM Portal supports multiple providers, users bring own API keys, session management is clean.

**Result**: 91 tests pass. Multi-provider support (9 providers), session manager with AES-256-GCM session-scoped key encryption, extended llm_config.yaml. Rung 641 achieved.

**Test count**: 91 LLM Portal tests (45 portal + 28 session manager + 18 routing/security)

### Tasks

- [x] Multi-LLM provider support
  - Anthropic Claude (claude-opus-4-6, claude-sonnet-4-6, claude-haiku-3-5)
  - OpenAI (gpt-4o, gpt-4o-mini)
  - Llama (via Ollama local endpoint)
  - Qwen (via local or Dashscope endpoint)
  - Custom endpoint: `{base_url, api_key, model_id}` passthrough
- [x] User brings own API key → zero LLM cost to Stillwater
  - Key stored encrypted in session (AES-256-GCM, session-scoped)
  - Never logged, never persisted to disk
- [x] Session management
  - Session ID → skill pack → active task → evidence bundle
  - Session expiry: 24h
- [x] Evidence bundle display
  - Show `tests.json`, `plan.json`, `behavior_hash.txt` inline in UI
  - Download as `.zip`

---

## Phase 4: Self-Promotion to Rung 65537 (Month 3) — DONE

**Goal**: Stillwater itself runs at rung 65537. Self-verification is the product demo.

**Result**: 41 tests pass. Semgrep 0 findings, bandit 0 findings, behavioral hash 3-seed consensus (sha256: 199c0a33f439b5ef...), GitHub Actions daily CI deployed, README badge live. Rung 65537 CI badge deployed.

**Test count**: 41 (security + CI + behavioral hash verification tests)

### Tasks

- [x] Adversarial sweep: 5 paraphrases per skill (13 skills × 5 = 65 paraphrase tests)
  - Use prime-coder adversarial_paraphrase_sweep (min_paraphrases=5)
  - Record behavioral hashes for each paraphrase
- [x] Behavioral hash tracking across 3 seeds
  - `evidence/behavior_hash.txt` + `evidence/behavior_hash_verify.txt`
  - Seeds: 42, 137, 9001
- [x] Security gate: semgrep + bandit clean
  - `semgrep --config=p/python stillwater.py store/ skills/` → 0 findings
  - `bandit -r stillwater.py store/ skills/` → 0 high/medium findings
  - Record tool versions + rule set hash in `evidence/security_scan.json`
- [x] 30-day continuous verification
  - GitHub Actions: daily rung 641 check (pytest + behavioral hash)
  - Slack/email alert if hash drifts
  - Badge in README: "Rung 65537 — verified YYYY-MM-DD"
- [x] Update CHANGELOG.md: v2.0.0 release

---

## Phase 5: Persona System (Month 2–3) — DONE

**Goal**: Add domain expert personas and GLOW score gamification to Stillwater, enabling persona-enhanced swarm agents and transparent progress tracking with belt progression.

**Result**: 50 personas in 11 categories. persona-engine.md v1.3.0. All 19 swarms updated with persona loading. Papers 34-39 complete. A/B benchmarks: avg +27% improvement.

**Current metrics**:
- Tests: 258
- Skills: 15+
- Swarms: 19 (all persona-enhanced)
- Papers: 39
- Personas: 50

### Tasks

- [x] Create `skills/persona-engine.md` — 12 domain expert personas with voice rules, domain expertise, and dispatch protocol (rung 641, 2026-02-21)
  - linus, mr-beast, brunson, bruce-lee, brendan-eich, codd, knuth, schneier, fda-auditor, torvalds, pg, sifu
  - Persona loading protocol: task domain → persona match → inject into skill pack
  - Layering rule: persona NEVER overrides prime-safety
  - Multi-persona support for complex tasks
- [x] Create `skills/glow-score.md` — GLOW Score gamification system (rung 641, 2026-02-21)
  - GLOW = Growth + Learning + Output + Wins (0-25 each, total 0-100)
  - Belt integration: White/Yellow/Orange/Green/Blue/Black
  - Session tracking: start/per-commit/end format
  - Pace targets: warrior (60+/day), master (70+/week), steady (40+/day)
  - Anti-patterns: GLOW_INFLATED, GLOW_WITHOUT_NORTHSTAR_ALIGNMENT, WINS_BY_NARRATIVE
- [x] Create `swarms/persona-coder.md` — Persona-enhanced coder swarm agent (rung 641, 2026-02-21)
  - Extends base Coder with automatic persona selection based on task domain
  - GLOW score calculation + `glow_score.json` as required artifact
  - Commit message format: GLOW {total} [G:{g} L:{l} O:{o} W:{w}]
- [x] Create `papers/34-persona-glow-paradigm.md` — The Dojo Protocol (rung 641, 2026-02-21)
  - Full paper on persona-enhanced agents + GLOW gamification
  - Bruce Lee / kung fu / dojo theme throughout
  - Extended master equation: Intelligence = Memory × Care × Iteration × Expertise × Motivation
- [x] Create `papers/35-syndication-strategy.md` — Content Syndication Strategy (rung 641, 2026-02-21)
  - Brunson Hook + Story + Offer treatment for all content
  - 7-stage pipeline: canonical → LinkedIn → Substack → HN → Reddit → X → YouTube
  - solace-browser recipe integration for automation
  - Content NORTHSTAR metrics: stars, Substack subscribers, LinkedIn reactions
- [x] Update `NORTHSTAR.md` — Add Persona Engine, GLOW Score, Content Syndication, and Dojo theme sections
- [x] Update `skills/phuc-orchestration.md` — Add persona-coder to dispatch decision matrix
- [x] Update `launch-swarm.sh` — Add persona + glow-score to swarm dispatch templates
- [x] Update `STORE.md` — Add GLOW score requirements for Store submissions (skill must include GLOW metadata)

### Build Prompt (Phase 5 — Persona Engine Update to Orchestration)

```
Load prime-safety + prime-coder + phuc-orchestration + persona-engine.
Task: Update skills/phuc-orchestration.md dispatch decision matrix to include persona-coder agent type.
Reference: skills/persona-engine.md (persona registry + loading protocol)
Reference: swarms/persona-coder.md (agent definition)
Requirements:
  - Add persona-coder row to dispatch matrix with correct trigger conditions
  - Add GLOW score reporting to sub-agent artifact schema
  - Add persona hint field to CNF capsule template
  - No breaking changes to existing dispatch patterns
Rung target: 641
Evidence required: skills/phuc-orchestration.md updated + no regression in existing dispatch patterns
```

### Build Prompt (Phase 5 — Launch Swarm Integration)

```
Load prime-safety + prime-coder + persona-engine + glow-score.
Task: Update launch-swarm.sh to inject persona + glow-score into swarm dispatch prompts.
Reference: skills/persona-engine.md, skills/glow-score.md, swarms/persona-coder.md
Requirements:
  - For each swarm target, auto-detect task domain → select matching persona
  - Inject persona voice rules into generated prompt
  - Add GLOW target (default: 60) to generated prompt
  - Add glow_score.json to required artifacts list in generated prompt
  - Backward compatible: existing launch-swarm.sh calls unchanged
Rung target: 641
Evidence required: launch-swarm.sh generates prompts with persona + GLOW for each project
```

---

## Phase 6: Hackathon System (NEW)

**Goal**: Layer hackathon sprint methodology on top of the persona system for structured, time-boxed development. Every ROADMAP phase becomes an explicit, executable hackathon with phases, scope locks, and GLOW at the end.

### Delivered

- [x] skills/hackathon.md — hackathon execution protocol (8 phases, timing templates)
- [x] swarms/hackathon-lead.md — hackathon coordinator agent
- [x] personas/marketing-business/hackathon-master.md — sprint execution persona
- [x] papers/40-hackathon-paradigm.md — hackathon methodology paper
- [x] combos/hackathon-sprint.md — standard hackathon combo (4-hour sprint)
- [x] combos/hackathon-lightning.md — 2-hour lightning sprint
- [x] combos/hackathon-marathon.md — 8-hour marathon sprint

### Key Insight

Every ROADMAP phase IS a hackathon. The hackathon is not a special event — it is the development methodology. Personas give you the right experts. Hackathons give you the right workflow. Together: structured sprint + domain experts + evidence gates + GLOW scoring = the Stillwater development cycle.

The hackathon system makes this explicit and executable: Scout discovers (20%), Plan locks scope (10%), Build ships (45%), Verify gates evidence (15%), Demo proves it happened (10%). Time box is law. Demo or fail.

### Build Prompt (Phase 6)

```
Load prime-safety + prime-coder + phuc-orchestration + persona-engine + hackathon-master.
Task: Run a hackathon sprint to deliver Phase 6 of the Stillwater ROADMAP.
Repo: stillwater/
Sprint type: standard (4-hour)
Demo target: all 7 Phase 6 deliverables committed and documented in demo.md
Rung target: 641
Evidence required: evidence/sprint.json + evidence/demo.md + evidence/glow_score.json
GLOW target: 60+ (warrior pace)
```

---

## Milestone Summary

| Phase | Target Date | Rung Gate | Key Deliverable |
|-------|------------|-----------|----------------|
| Phase 0: Audit | Week 0 | 641 | Baseline audit report — DONE (258 tests, security scan clean) |
| Phase 1: OAuth3 | Week 1–2 | 641 | `papers/oauth3-spec-v0.1.md` + `skills/oauth3-enforcer.md` — DONE |
| Phase 2: Store Client | Month 1 | 641 | `store/client.py` + `store/rung_validator.py` — DONE (66 tests, 258 total) |
| Phase 2.5: LLM Usage Tracker | Month 1 | 641 | `tip_callback` in llm_call/llm_chat + `usage_tracker` module — DONE (55 tests) |
| Phase 3: LLM Portal | Month 2 | 641 | Multi-provider support + session management — DONE (91 tests) |
| Phase 4: Rung 65537 | Month 3 | 65537 | Self-verification badge + 30-day CI — DONE (41 tests) |
| Phase 5: Persona System | Month 2–3 | 641 | 50 personas, 11 categories, persona-engine.md v1.3.0, all 19 swarms enhanced, papers 34-39, +27% A/B avg — DONE (50 tests) |
| Phase 6: Hackathon System | Month 3 | 641 | hackathon-sprint + lightning + marathon combos, hackathon-master persona, hackathon skill + swarm — DONE |

---

## Build Discipline

All phases follow the prime-coder protocol:
1. Write failing test first (Kent's Red Gate)
2. Implement minimum code to pass (Green Gate)
3. Run full test suite — no regressions
4. Produce evidence bundle (`evidence/plan.json`, `evidence/tests.json`)
5. Commit with `feat:` or `fix:` prefix + evidence pointer + GLOW score

GLOW target per commit: 60+ (warrior pace)
Commit format: `feat: {description}\n\nGLOW {total} [G:{g} L:{l} O:{o} W:{w}]`

Model selection guidance:
- `haiku` — volume tasks (listing, formatting, boilerplate)
- `sonnet` — complex logic (API design, skill authoring)
- `opus` — promotion gate (adversarial sweep, security audit, rung 65537 seal)

Persona selection guidance:
- `linus` — CLI, systems, OSS architecture
- `schneier` — security, OAuth3, cryptography
- `knuth` — algorithms, formal proofs, verification math
- `bruce-lee` — gamification, belt system, dojo design
- `brunson` — pricing, conversion, launch copy
- (full registry: `skills/persona-engine.md`)
