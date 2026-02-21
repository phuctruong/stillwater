# Case Study: SolaceCLI — PRIVATE Extension of stillwater/cli

**Tracking since**: 2026-02-21
**Status**: Whitepaper written → Implementation planning
**Rung**: TBD (needs doctor.py audit)
**Belt**: White

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

## What Exists

| Component | Status |
|-----------|--------|
| SOLACE-CLI-WHITEPAPER.md | Written |
| NORTHSTAR.md | Updated (PRIVATE extension framing) |
| ROADMAP.md | Created |
| `solace_cli/` Python package | Exists (needs audit) |
| `admin/` dashboard | Exists (needs audit) |
| OAuth3 commands | Not implemented |
| Rung-gated execution | Not implemented (delegates to stillwater/cli) |
| Managed LLM routing | Not implemented |
| Stillwater Store commands | Not implemented (delegates to stillwater/cli) |

## Phase 1 Target (OAuth3 Core)

- [ ] `solace auth grant --scope X --ttl Y`
- [ ] `solace auth revoke`
- [ ] `solace auth list`
- [ ] Token vault: AES-256-GCM local encryption

## Build Prompt for Next Session

Copy and paste into haiku/sonnet session:

```
Load phuc-orchestration + prime-coder + prime-safety.

Task: Implement OAuth3 core module for solace-cli (PRIVATE).
Note: solace-cli is a PRIVATE extension of stillwater/cli (OSS).
      stillwater/cli handles rung-gated execution and Store commands.
      solace-cli adds OAuth3 vault, twin browser, solaceagi.com connectivity.

Location: /home/phuc/projects/solace-cli/solace_cli/oauth3/
Files to create: token.py, scopes.py, enforcement.py, revocation.py
Reference: /home/phuc/projects/solace-cli/SOLACE-CLI-WHITEPAPER.md (Section 5)
Reference: /home/phuc/projects/solace-browser/OAUTH3-WHITEPAPER.md
Rung target: 641
Evidence required: tests.json showing auth grant + revoke working
```

## Metrics

| Metric | Value |
|--------|-------|
| OAuth3 commands implemented | 0/4 |
| Rung-gated tasks running | 0 (delegates to stillwater/cli) |
| Store commands working | 0/3 (delegates to stillwater/cli) |
| Doctor checks passing | TBD |
