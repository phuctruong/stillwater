# /distill - Documentation Knowledge Extraction for Stillwater

Apply the DISTILL recipe to compress Stillwater documentation.

## Usage

```
/distill [directory]
```

## What It Does

1. **Inventory** - Scan all *.md files in the target directory
2. **Measure** - Calculate source sizes and concept counts
3. **Extract** - Create/update README.md (interface layer)
4. **Compress** - Create/update CLAUDE.md (generator layer)
5. **Verify** - Check RTC (all concepts preserved)
6. **Report** - Show compression ratios
7. **Publish** - Publish to PM Network (optional)

## Recipe Reference

See: `/home/phuc/projects/stillwater/papers/*.md` for theoretical foundation

## Target Ratios

| Layer | Compression | Role |
|-------|-------------|------|
| Sources → README | 5-15x | Remove pedagogy, keep structure |
| README → CLAUDE.md | 1.5-3x | Remove visuals, keep axioms |
| Total | 10-30x | Maximum lossless compression |

## Output Structure

```
[directory]/
├── CLAUDE.md     # Stillwater generator (smallest, axioms)
├── README.md     # Interface layer (diagrams, tables)
└── *.md          # Source ripples (full content)
```

## Instructions for Claude

When user runs `/distill [dir]`:

1. List all *.md files in `[dir]` (excluding README.md and CLAUDE.md)
2. Calculate total size of source files
3. If README.md exists, read it; otherwise create from sources:
   - Extract all ## headers
   - Keep all tables
   - Keep key diagrams (structural only)
   - Remove prose/examples
4. If CLAUDE.md exists, read it; otherwise create from README:
   - Core axioms (2-4 lines)
   - Verification approach (table)
   - Operational controls (list)
   - No diagrams, no prose
5. Verify RTC:
   - All README concepts traceable to sources
   - All CLAUDE.md concepts traceable to README
6. Report compression ratios

## Example

```
User: /distill papers/

Claude:
=== DISTILL: papers ===

Sources: 15 files, 450KB
README:  85KB (5.3x compression)
CLAUDE:  22KB (3.8x from README)

Total:   20.5x compression
RTC:     ✅ 100% verified

Files updated:
- papers/CLAUDE.md
- papers/README.md
```

## Publishing to Network

After distilling, publish to the PM Network:

```
/distill-publish <path>       # Publish CLAUDE.md to network
/distill-verify <id>          # Verify artifact in network
/distill-list                 # List all network artifacts
```

## Related Commands

- `/compress` - Apply compression to data files
- `/verify` - Run RTC verification on existing CLAUDE.md
- `/expand` - Generate README from CLAUDE.md
- `/remember` - Store memory about distilled content
