# /distill — Documentation → Stillwater CLAUDE.md Generator

Compress documentation, skills, or recipes into minimal QUICK LOAD generators.

## Usage

```
/distill [directory]             # Compress docs → README.md + CLAUDE.md
/distill skills/[name].md        # Compress single skill → QUICK LOAD block
/distill recipes/                # Compress all recipes → recipes/README.md
/distill --verify [path]         # Check RTC (all concepts preserved)
/distill --ratio [directory]     # Show compression ratios only
```

## What It Does

1. **Inventory** — Scan all `*.md` files in the target directory
2. **Measure** — Calculate source sizes and concept counts
3. **Extract** — Create/update README.md (interface layer — diagrams, tables, structure)
4. **Compress** — Create/update CLAUDE.md (generator — axioms only, no prose)
5. **Verify RTC** — Check all concepts traceable from source → README → CLAUDE.md
6. **Report** — Show compression ratios

## Target Compression Ratios

| Layer | Target | Role |
|-------|--------|------|
| Sources → README | 5–15x | Remove pedagogy, keep structure |
| README → CLAUDE.md | 1.5–3x | Remove visuals, keep axioms |
| Total | 10–30x | Maximum lossless compression |

## QUICK LOAD Block Format (for skills)

When distilling a single skill, output format is:

```markdown
<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: [name] v[version]
PURPOSE: [one sentence — what it does]
CORE CONTRACT: [one sentence — key guarantee]
HARD GATES: [2-3 key blocked conditions]
FSM STATES: [abbreviated state list]
FORBIDDEN: [3-5 named forbidden states]
VERIFY: rung_641 ([what]) | rung_274177 ([what]) | rung_65537 ([what])
LOAD FULL: always for production; quick block is for orientation only
-->
```

## Output Structure

```
[directory]/
├── CLAUDE.md     # Stillwater generator (smallest, axioms only)
├── README.md     # Interface layer (diagrams, tables, structure)
└── *.md          # Source files (full content, never edited by distill)
```

## Instructions for Claude

When user runs `/distill [dir]`:

1. List all `*.md` files in `[dir]` (exclude README.md, CLAUDE.md)
2. Calculate total source size
3. Read or create README.md:
   - Extract all `##` headers
   - Keep all tables
   - Keep key diagrams (structural only)
   - Remove prose/examples/tutorials
4. Read or create CLAUDE.md:
   - Core equations or axioms (4–6 lines)
   - Invariants table (5–9 rows)
   - Operational rules (G1–G7 style sections)
   - No diagrams, no prose, no examples
5. Verify RTC:
   - All CLAUDE.md concepts traceable to README
   - All README concepts traceable to sources
6. Report compression ratios

When user runs `/distill skills/[name].md`:
1. Read the full skill file
2. Extract: PURPOSE, CORE CONTRACT, HARD GATES, FSM STATES, FORBIDDEN, VERIFY
3. Output as a QUICK LOAD comment block (10–15 lines)
4. Suggest placement in CLAUDE.md

## Example Output

```
=== DISTILL: skills/ ===

Sources: 12 skills, 180KB total
README:  Not created (skills have individual QUICK LOAD blocks)
QUICK LOAD blocks generated: 12

Compression: 12x average per skill (full → QUICK LOAD)
RTC: ✅ 100% concept traceability verified

Updated:
- skills/prime-safety.md → QUICK LOAD block (14 lines)
- skills/prime-coder.md  → QUICK LOAD block (12 lines)
- skills/phuc-forecast.md → QUICK LOAD block (11 lines)
```

## Related Commands

- `/remember` — Save distilled facts to persistent memory
- `/phuc-swarm` — Launch swarm agents with distilled skill packs
- `/northstar` — Load NORTHSTAR.md for current project
