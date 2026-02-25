# Question Database Schema

## JSONL Format

One JSON object per line. Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique ID: `Q-NNN` (zero-padded 3 digits per project) |
| `text` | string | yes | The question, written as a clean English sentence or question |
| `asker` | string | yes | Who asked: `human:phuc`, `persona:skeptic`, `persona:dragon-rider`, etc. |
| `project` | string | yes | Project slug: `stillwater`, `solace-browser`, `paudio`, etc. |
| `glow` | string | yes | Single character: `G` (Growth) | `L` (Loss/bug) | `O` (Output) | `W` (Wisdom) |
| `pillar` | string | yes | `P0` (core theory) | `P1` (tooling/process) | `P2` (community/QA) | `P3` (GTM) |
| `date` | string | yes | ISO date: `YYYY-MM-DD` |
| `context` | string | yes | Short description of the session that produced the question |
| `status` | string | yes | `ASKED` | `REFINED` | `ARCHIVED` |
| `answer_status` | string | yes | `ANSWERED` | `PENDING` | `OPEN` |

## GLOW Definitions

- **G — Growth:** Questions about new features, capabilities, directions, expansions
- **L — Loss:** Questions about bugs, failures, regressions, what's broken or missing
- **O — Output:** Questions about artifacts, papers, deliverables, publications
- **W — Wisdom:** Questions about theory, insight, philosophy, deeper understanding

## Pillar Definitions

- **P0 — Core Theory:** Foundational concepts, architecture, first principles
- **P1 — Tooling/Process:** Implementation, skills, workflows, dev tooling
- **P2 — Community/QA:** Testing, review, community contributions, QA processes
- **P3 — GTM:** Go-to-market, pricing, positioning, competitive landscape

## Status Lifecycle

```
ASKED → REFINED (question improved/clarified) → ARCHIVED (superseded or resolved permanently)
```

## Answer Status Lifecycle

```
OPEN → PENDING (answer in progress) → ANSWERED (fully resolved for now)
```

ANSWERED questions can reopen if new information changes the answer. Add a new Q entry — never mutate old ones.

## Example

```json
{"id": "Q-001", "text": "Where are skills located and why are they at repo root?", "asker": "human:phuc", "project": "stillwater", "glow": "L", "pillar": "P0", "date": "2026-02-22", "context": "skills audit session", "status": "ASKED", "answer_status": "ANSWERED"}
```

## File Naming

One file per project: `questions/<project-slug>.jsonl`

Cross-project questions go in the most relevant project file and are referenced by ID from others.
