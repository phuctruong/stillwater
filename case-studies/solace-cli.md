# Case Study: SolaceCLI — PRIVATE Extension of stillwater/cli

**Tracking since**: 2026-02-21
**Status**: All 4 Phases COMPLETE
**Rung**: 641 (63/63 tests passing)
**Belt**: Yellow

## Architecture Clarity

```
stillwater/cli (OSS)           ← base CLI, lives inside the stillwater repo
    │                             open source; anyone who clones stillwater gets it
    │  provides:
    │    - rung-gated local execution (stillwater run task.md --rung 641)
    │    - Stillwater Store commands (stillwater store install/submit/browse)
    │    - evidence bundle validation (stillwater verify evidence/)
    │    - model-neutral LLM invocation (BYOK: user provides their own key)
    │
    └── solace-cli (PRIVATE)   ← extends stillwater/cli; NOT open source
            adds:
              - OAuth3 vault management (local AES-256-GCM token store)
              - Twin browser orchestration (spawn, sync, delegate to solace-browser)
              - solaceagi.com API connectivity (auth, billing tier check)
              - Managed LLM routing (Together.ai/OpenRouter passthrough)
              - Private backend for solaceagi.com
```

**What stillwater/cli provides to the public (OSS):**
- `stillwater run task.md --rung 641` — verified local execution
- `stillwater store install skill@65537` — install from Stillwater Store
- `stillwater store submit skill.md` — submit skill (rung-gated)
- `stillwater verify evidence/` — validate evidence bundle
- BYOK model invocation (Anthropic/OpenAI/Llama key in env)

**What solace-cli adds (PRIVATE — not open source):**
- `solace auth grant --scope github.create_issue --ttl 1h` — OAuth3 vault
- `solace auth revoke` / `solace auth list` — token management
- `solace browser spawn --scope linkedin.read` — twin browser delegation
- `solace llm complete` — managed LLM routing (Together.ai/OpenRouter)
- Tier enforcement: checks user's solaceagi.com tier before routing LLM calls
- Cloud twin sync (AES-256-GCM session state → solaceagi.com)

## What Was Built

| Component | Status | Tests | Rung |
|-----------|--------|-------|------|
| auth/vault.py | done | — | 641 |
| auth/token.py | done | — | 641 |
| commands/auth.py | done | 16 | 641 |
| task_parser.py | done | — | 641 |
| evidence.py | done | — | 641 |
| commands/run.py | done | 15 | 641 |
| skill_validator.py | done | — | 641 |
| store_client.py | done | — | 641 |
| commands/store.py | done | 18 | 641 |
| browser/session.py | done | — | 641 |
| browser/scope_guard.py | done | — | 641 |
| browser/recipe_runner.py | done | — | 641 |
| commands/browser.py | done | 14 | 641 |

## Phase 1: OAuth3 Auth Vault (COMPLETE)

| Item | Status | Rung | Date | Tests | Commit |
|------|--------|------|------|-------|--------|
| auth/vault.py | done | 641 | 2026-02-21 | — | a24a380 |
| auth/token.py | done | 641 | 2026-02-21 | — | a24a380 |
| commands/auth.py | done | 641 | 2026-02-21 | 16 | a24a380 |

**Features:**
- `solace auth grant --scope github.create_issue --ttl 1h` — issue tokens with expiry + scopes
- `solace auth list` — list active tokens with revocation status
- `solace auth revoke <token_id>` — instant revocation
- Token vault: AES-256-GCM encrypted at ~/.solace/vault.enc (cryptographic erasure)
- AgencyToken dataclass with validation

## Phase 2: Rung-Gated Execution (COMPLETE)

| Item | Status | Rung | Date | Tests | Commit |
|------|--------|------|------|-------|--------|
| task_parser.py | done | 641 | 2026-02-21 | — | ce65968 |
| evidence.py | done | 641 | 2026-02-21 | — | ce65968 |
| commands/run.py | done | 641 | 2026-02-21 | 15 | ce65968 |

**Features:**
- `solace run task.md --rung 641 --dry-run` — parse + validate Markdown tasks
- Evidence bundle writer (timestamps, outputs, errors)
- Delegates to stillwater/cli for actual rung-gated execution

## Phase 3: Store Integration (COMPLETE)

| Item | Status | Rung | Date | Tests | Commit |
|------|--------|------|------|-------|--------|
| skill_validator.py | done | 641 | 2026-02-21 | — | 496c1e7 |
| store_client.py | done | 641 | 2026-02-21 | — | 496c1e7 |
| commands/store.py | done | 641 | 2026-02-21 | 18 | 496c1e7 |

**Features:**
- `solace store validate skill.md` — local skill .md validation
- `solace store install skill@65537` — download from Stillwater Store
- `solace store browse` — list available skills
- `solace store submit skill.md` — submit to Store (rung-gated)
- Lightweight urllib Store API client (no external deps)

## Phase 4: Twin Browser (COMPLETE)

| Item | Status | Rung | Date | Tests | Commit |
|------|--------|------|------|-------|--------|
| browser/session.py | done | 641 | 2026-02-21 | — | d3cfbe2d |
| browser/scope_guard.py | done | 641 | 2026-02-21 | — | d3cfbe2d |
| browser/recipe_runner.py | done | 641 | 2026-02-21 | — | d3cfbe2d |
| commands/browser.py | done | 641 | 2026-02-21 | 14 | d3cfbe2d |

**Features:**
- `solace browser spawn --scope linkedin.read` — spawn headless browser with OAuth3 scope guard
- `solace browser run recipe.json` — execute recipe with Lane A evidence
- `solace browser status` — list running browsers
- `solace browser kill <session_id>` — terminate session
- Session management + URL allowlist + recipe execution with evidence

## Metrics

| Metric | Value |
|--------|-------|
| Phases complete | 4/4 |
| Total tests passing | 63/63 |
| OAuth3 commands | 3/3 (grant, list, revoke) |
| Rung-gated tasks | Working (delegates to stillwater/cli) |
| Store commands | 4/4 (validate, install, browse, submit) |
| Browser commands | 4/4 (spawn, run, status, kill) |
| Rung target | 641 |
| Belt | Yellow |
