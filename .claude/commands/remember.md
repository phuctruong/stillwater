# /remember — External Memory (DISTILL-Compressed)

Storage: `.claude/memory/context.md` | Auth: 65537

## Usage

```
/remember                   # Display all memory
/remember [key]             # Get value for key
/remember [key] [value]     # Store (auto-distilled to key=value)
/remember --list            # List all keys by channel
/remember --clear [key]     # Delete a key
```

## AUTO-DISTILL RULE (MANDATORY)

When saving ANY information, compress to key=value format:

```
INPUT:  "I want to use haiku as the main session model for all projects"
OUTPUT: model_main_session: haiku

INPUT:  "Phuc swarms should dispatch sonnet for coding tasks"
OUTPUT: model_coder_swarm: sonnet

INPUT:  "RUNG_TARGET for PZip is 65537"
OUTPUT: pzip_rung: 65537
```

**Rules:**
- Key=value format only (no prose, no explanations)
- One fact per line
- Lists as comma-separated values
- Equations in terse form
- No mermaid diagrams
- No "I decided to...", just the decision

## Prime Channel Architecture

| Pattern | Channel | Stability |
|---------|---------|-----------|
| `user_*`, `kids`, `location`, `favorite_*` | [2] Identity | Stillwater |
| `project_*`, `goal_*`, `northstar_*` | [3] Goals | Stillwater |
| `decision_*`, `*_rule`, `model_*` | [5] Decisions | LOCKED |
| `current_*`, `phase_*`, `rung_*` | [7] Context | Ripple |
| `blocker_*`, `issue_*` | [11] Blockers | Ripple |

## Memory File Format

```markdown
# MEMORY | Auth:65537 | Updated:YYYY-MM-DD

## IDENTITY [2]
user: Phuc, Boston
projects: stillwater,solaceagi,solace-cli,solace-browser,pzip,paudio,pvideo,if,phucnet

## GOALS [3]
northstar: Phuc_Forecast
goal_stillwater: AI verification framework at rung 65537
goal_model_strategy: haiku=coordination, sonnet=domain, opus=promotion

## DECISIONS [5] LOCKED
model_main_session: haiku
model_coder_swarm: sonnet
model_math_swarm: opus
decision_combos_dir: combos/ (not canon/combos/)
decision_phuc_orch: mandatory for all projects, no inline deep work

## CONTEXT [7] RIPPLE
current_phase: Stillwater v1.5.0
current_rung_stillwater: 641
skills_loaded: prime-safety, prime-coder, phuc-orchestration, phuc-forecast

## BLOCKERS [11]
# (none)
```

## Auto-Save Triggers

Claude saves automatically when:
- User shares personal info → [2] Identity
- Design decision made → [5] LOCKED
- Milestone or rung achieved → [7] Context
- Blocker encountered → [11] Blockers

## Integration

- All Stillwater projects share IDENTITY + GOALS channels
- `/distill` reads context for compression decisions
- Phuc swarms inherit DECISIONS channel for model selection
- DECISIONS [5] is LOCKED — changes require explicit user confirmation

## OOLONG Insight

```
LLM memory: Probabilistic → Drift → ~85% recall
External:   Deterministic → Exact → 100% recall
Compression: 4.4x (prose → key=value)
```

*"External memory beats internal hallucination every time."*
*"To compress is to understand."*

## Instructions for Claude

When user runs `/remember`:
1. Read `.claude/memory/context.md` (create if absent)
2. Display all channels in formatted table
3. Show total key count

When user runs `/remember [key]`:
1. Read context.md
2. Find key across all channels
3. Return value or "key not found"

When user runs `/remember [key] [value]`:
1. Apply AUTO-DISTILL: compress value to terse form
2. Classify key into correct channel (2/3/5/7/11)
3. Write to context.md under correct channel
4. Confirm: "Saved [channel]: key=value"

When user runs `/remember --clear [key]`:
1. Remove key from context.md
2. Confirm deletion
