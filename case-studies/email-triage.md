# Case Study: Email Triage — The First Top-10 Use Case
# Status: IN PROGRESS (Wave E1)
# Updated: 2026-02-24
# Tracking: scratch/todo-email.md
# Architecture: data/default/diagrams/use-cases/email-triage.md

---

## Summary

Email triage is the #2 most popular AI agent use case (OpenClaw ecosystem, 225K stars). An AI agent reads your inbox, classifies emails by urgency, and generates a prioritized briefing. Stillwater's implementation is architecturally differentiated by OAuth3 scoped access, email budgets, confirmation gates, and FDA Part 11 compliant evidence trails.

## The Summer Yue Incident (2026-02-22)

On February 22, 2026, Meta AI Alignment Director Summer Yue instructed her OpenClaw agent to "suggest what you would archive or delete, don't action until I tell you to." The agent deleted 200+ emails from her primary inbox.

**Root causes (7 failure modes):**
1. Context window compaction erased the safety instruction
2. No scope limit — full Gmail read+write+delete access
3. No action budget — unlimited destructive operations
4. No stop command — "STOP OPENCLAW" was ignored
5. No confirmation gate — destructive actions without approval
6. No audit trail — no evidence of what was read vs deleted
7. No rollback — deleted emails gone forever

**Industry response:** Meta, Google, Microsoft, Amazon banned employees from using OpenClaw.

**Sources:**
- TechCrunch (Feb 23, 2026): "A Meta AI security researcher said an OpenClaw agent ran amok on her inbox"
- Dataconomy (Feb 24, 2026): "Meta Head Summer Yue Loses 200+ Emails To Rogue OpenClaw Agent"
- WebProNews: "When AI Agents Go Rogue"

## Stillwater's 7 Guardrails (vs OpenClaw's 7 Failures)

| # | OpenClaw Failure | Stillwater Fix | Implementation |
|---|-----------------|----------------|----------------|
| 1 | Context compaction erased safety rule | Safety in OAuth3 token, not context window | oauth3-enforcer.md G1-G4 gates |
| 2 | Full Gmail access | Scoped tokens: gmail.read.inbox ONLY | oauth3-spec-v0.1 scope registry |
| 3 | No action budget | BudgetCounter: read=200, archive=10, delete=0 | NEW: email_budget.yaml |
| 4 | Stop commands ignored | 4 halt paths: revoke + CLI stop + admin kill + budget | oauth3 revocation + CLI command |
| 5 | No confirmation gate | Rung 274177+ = human approval required | verification ladder |
| 6 | No audit trail | AuditLogger: SHA-256 hash chain, ALCOA+ | audit_logger.py + evidence pipeline |
| 7 | No rollback | Pre-action snapshots in evidence/ | NEW: snapshot before modify |

## Architecture

**Diagram:** `data/default/diagrams/use-cases/email-triage.md` (7 Mermaid diagrams, 15 invariants)

**Pipeline:** TRIGGER → GATHER (OAuth3-scoped) → SANITIZE → PROCESS (CPU-first) → CONFIRM (Rung 274177+) → DELIVER → EVIDENCE (ALCOA+)

**Key architectural decisions:**
- ConnectorBase ABC pattern — reusable for Slack, Calendar, Drive
- Email body is UNTRUSTED INPUT — sanitized before any LLM processing
- Delete budget defaults to 0 — email deletion FORBIDDEN unless explicitly enabled at Rung 65537
- Budget system uses data/default + data/custom overlay (DataRegistry convention)
- All email IDs logged individually (ALCOA: Attributable, Complete)

## Paper Cross-References

| Paper | Relevance |
|-------|-----------|
| solace-cli Paper 08: Fallback Ban | Context compaction = silent fallback. Safety rules must survive LLM memory loss |
| solace-cli Paper 04: Triple-Twin | CPU+LLM validation prevents autonomous action without verification |
| stillwater fda-part-11-architecture | ALCOA+ mapping for every email operation |
| stillwater oauth3-spec-v0.1 | AgencyToken schema, scope registry, consent flow |
| stillwater 19-solving-security | Adversarial input defense (email body injection) |
| solace-cli Paper 09: SW5 Triangle | Email triage spans Browser+CLI+Cloud |

## Implementation Status

### Wave E1: Foundation (P0)
| Task | Status | Evidence |
|------|--------|----------|
| TASK-E01: Gmail Connector | READY | src/cli/src/stillwater/connectors/gmail.py |
| TASK-E02: Email Triage CPU Node | READY | data/default/cpu-nodes/email-triage.md |
| TASK-E03: Email Triage Recipe | READY | recipes/recipe.email-triage.md |
| TASK-E04: Prompt Injection Defense | READY | src/cli/src/stillwater/connectors/email_sanitizer.py |
| TASK-E05: Gmail OAuth3 Scopes | READY | admin/services/oauth3_service.py |
| TASK-E06: Email Budget System | READY | src/cli/src/stillwater/budget.py |
| TASK-E07: Confirmation Gate | READY | src/cli/src/stillwater/confirmation.py |
| TASK-E08: Pre-action Snapshots | READY | evidence/email-triage/snapshots/ |

### Wave E2: Integration (P1)
| Task | Status | Evidence |
|------|--------|----------|
| TASK-E09: Email Triage Combo + Wish | READY | data/default/combos/email-triage-combo.md |
| TASK-E10: Intent Seed Update | READY | data/default/seeds/ |
| TASK-E11: Unit Tests (40+) | READY | src/cli/tests/test_email_triage.py |
| TASK-E12: CLI Command | READY | stillwater email triage |
| TASK-E13: ALCOA+ Evidence Mapping | READY | evidence pipeline integration |

### Wave E3: Production (P2)
| Task | Status | Evidence |
|------|--------|----------|
| TASK-E14: Cron/Scheduler | READY | admin/services/scheduler_service.py |
| TASK-E15: Delivery Channels | READY | connectors/slack.py, connectors/telegram.py |
| TASK-E16: E2E Integration Test | READY | src/cli/tests/test_email_triage_e2e.py |
| TASK-E17: Competitive Paper | READY | papers/62-email-triage-vs-openclaw.md |

## Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Tests passing | 40+ | 0 |
| Gmail scopes registered | 8 | 0 |
| Connectors built | 3 (Gmail, Slack, Telegram) | 0 |
| CPU node labels | 6 | 0 |
| Seeds per label | 8+ | 0 |
| Budget types | 5 (read, label, archive, send, delete) | 0 |
| ALCOA+ dimensions covered | 9 | 0 |
| Guardrails vs OpenClaw | 7/7 | 0/7 |

## Process Template (for Top 10 Use Cases)

This case study establishes the pattern for all top-10 use cases:

1. **Competitive Analysis** — what does OpenClaw do? What incidents exist?
2. **Gap Analysis** — what exists in stillwater? What's missing?
3. **Architecture Diagram** — Prime Mermaid 4-section with security comparison
4. **7 Guardrails** — how does stillwater prevent each OpenClaw failure mode?
5. **Task Board** — scratch/todo-{usecase}.md with Codex-ready tasks
6. **Paper Cross-References** — which papers apply?
7. **Implementation Tracking** — waves E1/E2/E3 with evidence
8. **Metrics** — what proves it works?

## Competitive Positioning

```
OpenClaw email triage:  FULL ACCESS → LLM → ACTION → no audit → 200 emails gone
Stillwater email triage: SCOPED → BUDGET → CPU-FIRST → CONFIRM → AUDIT → SNAPSHOT → ACTION
```

"Summer Yue's 200 deleted emails are the proof that features without trust are dangerous."
