# Case Study: SolaceCLI — Terminal-Native Verified Delegated Intelligence

**Tracking since**: 2026-02-21
**Status**: Whitepaper written → Implementation planning
**Rung**: TBD (needs doctor.py audit)
**Belt**: ⬜ White

## What Exists

| Component | Status |
|-----------|--------|
| SOLACE-CLI-WHITEPAPER.md | ✅ Written |
| NORTHSTAR.md | ✅ Updated |
| ROADMAP.md | ✅ Created |
| `solace_cli/` Python package | Exists (needs audit) |
| `admin/` dashboard | Exists (needs audit) |
| OAuth3 commands | ❌ Not implemented |
| Rung-gated execution | ❌ Not implemented |
| Stillwater Store commands | ❌ Not implemented |

## Phase 1 Target (OAuth3 Core)

- [ ] `solace auth grant --scope X --ttl Y`
- [ ] `solace auth revoke`
- [ ] `solace auth list`
- [ ] Token vault: AES-256-GCM local encryption

## Build Prompt for Next Session

Copy and paste into haiku/sonnet session:

```
Load phuc-orchestration + prime-coder + prime-safety.
Task: Implement OAuth3 core module for solace-cli.
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
| Rung-gated tasks running | 0 |
| Store commands working | 0/3 |
| Doctor checks passing | TBD |
