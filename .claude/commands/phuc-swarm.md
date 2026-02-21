# /phuc-swarm — Launch Phuc Swarm Agents

Dispatch typed sub-agents with correct model + full skill pack + CNF capsule.
Enforces phuc-orchestration: NO inline deep work, NO skill-less dispatch.

## Usage

```
/phuc-swarm coder    "fix the null check in src/foo.py"
/phuc-swarm planner  "design the NORTHSTAR metrics system"
/phuc-swarm skeptic  "verify the prime-coder changes in PR #42"
/phuc-swarm scout    "research MCP integration patterns"
/phuc-swarm math     "prove convergence of the compression algorithm"
/phuc-swarm janitor  "clean up stale logs and artifacts"
/phuc-swarm --list   # Show all available roles + models
```

## Agent Roles + Model Selection

| Role | Model | Skill Pack | Rung Default | Use For |
|------|-------|-----------|--------------|---------|
| `scout` | haiku | prime-safety | 641 | Research, file search, inventory |
| `janitor` | haiku | prime-safety + phuc-cleanup | 641 | Cleanup, archival, hygiene |
| `graph-designer` | haiku | prime-safety + prime-mermaid | 641 | State machines, FSM diagrams |
| `coder` | sonnet | prime-safety + prime-coder | 641 | Bugfix, feature, refactor |
| `planner` | sonnet | prime-safety + phuc-forecast | 641 | Architecture, risk analysis |
| `skeptic` | sonnet | prime-safety + prime-coder + phuc-forecast | 274177 | Verification, review |
| `writer` | sonnet | prime-safety + software5.0-paradigm | 641 | Papers, docs, long-form |
| `mathematician` | opus | prime-safety + prime-math | 274177 | Proofs, exact computation |
| `security-auditor` | opus | prime-safety + prime-coder | 65537 | Security scans, exploit repro |
| `final-audit` | opus | prime-safety + prime-coder + phuc-forecast | 65537 | Promotion gate |

## MANDATORY Dispatch Rules (Phuc-Orchestration)

1. **prime-safety ALWAYS first** in every skill pack — no exceptions
2. **Full skill file content pasted inline** — never reference by name only
3. **CNF capsule required** — full task + context, never "as before"
4. **Rung declared** before dispatch
5. **FORBIDDEN in prompt**: "as discussed", "as before", "recall that", "you know the context"

## CNF Capsule Template

Every sub-agent gets this structure injected:

```
You are a [ROLE] agent (model: [MODEL]).

## Loaded Skills
<BEGIN_SKILL name="prime-safety">
[FULL CONTENT of skills/prime-safety.md]
</BEGIN_SKILL>

<BEGIN_SKILL name="[domain-skill]">
[FULL CONTENT of skills/[domain-skill].md]
</BEGIN_SKILL>

## Task (CNF Capsule)
- task_id: [UNIQUE_ID]
- task_request: [FULL TASK TEXT]
- constraints: [EXPLICIT limits]
- context: [FULL context — no summaries]
- rung_target: [641 | 274177 | 65537]

## Expected Artifacts
[Exact list of what agent must produce]

## Stop Rules
- EXIT_PASS if: [concrete conditions]
- EXIT_BLOCKED if: [concrete conditions]
```

## Instructions for Claude

When user runs `/phuc-swarm [role] "[task]"`:

1. **Validate role** — must be in the table above; reject unknown roles
2. **Select model** — from table (haiku/sonnet/opus)
3. **Build skill pack** — read full content of each skill file from `skills/`
4. **Build CNF capsule** — full task + current context, no references to prior conversation
5. **Declare rung_target** — from table default, or override if task warrants higher
6. **Launch via Task tool** — subagent_type matching role (haiku/sonnet/opus)
7. **Await artifacts** — integrate JSON/diff outputs, reject prose summaries as Lane A evidence
8. **Report**: role dispatched, model used, rung_target, artifacts received

When user runs `/phuc-swarm --list`:

Display the roles table above with current skill file availability status.

## Example

```
User: /phuc-swarm coder "fix the missing null check in cli/src/stillwater/cli.py line 42"

Claude:
=== PHUC SWARM: Coder ===
Role:        coder
Model:       sonnet
Skill pack:  prime-safety + prime-coder
Rung target: 641

Building CNF capsule...
Loading skills/prime-safety.md (full content)
Loading skills/prime-coder.md (full content)

Dispatching Task tool (sonnet)...

[Agent returns: PATCH_DIFF, repro_red.log, repro_green.log, tests.json]

Integration: PASS (rung 641)
Evidence: evidence/repro_green.log, evidence/tests.json
```

## Forbidden States

- `SKILL_LESS_DISPATCH` — agent launched without skills pasted inline
- `FORGOTTEN_CAPSULE` — prompt says "as before" or "as discussed"
- `INLINE_DEEP_WORK` — you (main session) doing the coding instead of dispatching
- `SUMMARY_AS_EVIDENCE` — accepting prose "it works" instead of artifact
- `WRONG_MODEL` — using opus for scout tasks, or haiku for promotion gates

## Swarm Rung = MIN(all agent rungs)

If coder achieves rung 641 and skeptic achieves rung 274177:
Integration rung = 641 (the minimum). Never claim higher.
