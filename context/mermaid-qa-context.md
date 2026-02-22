# Context: Mermaid-Based QA

## Quick Load

This context document provides the essential information for any agent running mermaid-based QA on a Stillwater ecosystem project.

## Three-Pillar QA Framework

```
PILLAR 1: Questions  → skills/phuc-qa.md + combos/qa-audit.md
PILLAR 2: Tests      → skills/prime-coder.md + combos/run-test.md
PILLAR 3: Diagrams   → skills/prime-mermaid.md + combos/mermaid-qa.md

UNIFIED:  skills/phuc-qa.md (all three pillars)
```

## Diagram Categories (8 Required)

| # | Category | Mermaid Type | What It Covers |
|---|----------|-------------|----------------|
| 1 | System Architecture | flowchart TD | Components + connections |
| 2 | Data Flow | flowchart LR | Data movement between components |
| 3 | State Machines | stateDiagram-v2 | Entity lifecycle (session, skill, auth) |
| 4 | Sequence Diagrams | sequenceDiagram | Component interaction sequences |
| 5 | Class/Entity | classDiagram | Data models + relationships |
| 6 | User Journey | journey | User interaction flows |
| 7 | Deployment | flowchart TD | Production infrastructure |
| 8 | Dependencies | flowchart TD | Module/package dependency graph |

## File Naming Convention

```
diagrams/{project}/01-system-architecture.md
diagrams/{project}/02-project-ecosystem.md
diagrams/{project}/03-cli-command-flow.md
...
diagrams/{project}/NN-{descriptive-name}.md
```

## Diagram File Structure

Each diagram file should contain:

```markdown
# {Title}

{Brief description of what this diagram covers}

## Diagram

```mermaid
{mermaid code}
```

## Source Files

- `path/to/file1.py` — {what it contributes to this diagram}
- `path/to/file2.py` — {what it contributes to this diagram}

## Coverage

- [ ] Component A
- [ ] Component B
- [ ] ...
```

## Coverage Matrix Format

```json
{
  "project": "stillwater",
  "generated": "2026-02-22",
  "total_source_files": 42,
  "covered_files": 40,
  "uncovered_files": ["path/to/orphan1.py", "path/to/orphan2.py"],
  "coverage_pct": 95.2,
  "matrix": {
    "cli/src/stillwater/cli.py": ["01-system-architecture.md", "03-cli-command-flow.md"],
    "store/models.py": ["04-store-data-model.md", "05-store-operations.md"]
  }
}
```

## Northstar Reverse Engineering Applied

When generating diagrams, work backwards:

1. "What must be true for the system architecture to be fully understood?"
2. "What are the LAST 3 diagrams needed?"
3. "What connections between components are missing from the diagrams?"
4. "What states exist in code but not in any state diagram?"

## Stillwater Project Source Map

```
cli/src/stillwater/     — CLI entry point + LLM client + providers + session + usage
store/                  — Pydantic models + JSON persistence + auth + rung validation
admin/                  — HTTP admin server + LLM portal + session management
skills/                 — 40+ skill files (agent capabilities)
swarms/                 — 25+ swarm agent type definitions
combos/                 — WISH+RECIPE pairs for common tasks
papers/                 — Research papers (43+)
personas/               — Persona definitions
recipes/                — Reusable task recipes
evidence/               — Evidence bundles from verification
diagrams/               — Mermaid QA diagrams (this effort)
```

## Integration with Other Combos

```
combos/mermaid-qa.md → Produces diagrams/
combos/qa-audit.md   → Produces qa_scorecard.json
combos/run-test.md   → Produces test results

All three feed into unified gap report.
```
