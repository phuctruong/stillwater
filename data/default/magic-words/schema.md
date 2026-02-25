# Magic Words JSONL Schema

Each line in a `.jsonl` magic words file is a single JSON object with the following fields.

## Field Definitions

```json
{
  "id": "MW-001",
  "word": "coherence",
  "tier": 0,
  "definition": "The property that all parts of a system reinforce rather than contradict each other",
  "parent": null,
  "children": ["convergence", "stability", "alignment"],
  "gravity": 1.0,
  "domain": "universal",
  "project": "stillwater",
  "date_added": "2026-02-22",
  "usage_count": 0,
  "last_used": null,
  "related_words": ["integrity", "alignment", "symmetry"],
  "compression_ratio": null
}
```

## Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique identifier. Format: `MW-NNN` for universal words. Project-specific words use `<PROJECT>-NNN` (e.g., `SW-001`). Never reuse an ID even after deprecation. |
| `word` | string | yes | The canonical magic word in lowercase. Single word or hyphenated compound. No spaces. |
| `tier` | integer | yes | Tier level: 0 = trunk, 1 = primary branch, 2 = secondary branch, 3 = domain leaf. |
| `definition` | string | yes | Operational definition in one sentence. Must describe what the word implies about structure or behavior — not a dictionary entry. |
| `parent` | string or null | yes | The canonical parent word one tier above. `null` for Tier 0 trunk words only. Must reference a word that exists in the database. |
| `children` | array of strings | yes | Canonical child words one tier below. Empty array `[]` for leaf words with no seeded children. Each string must be a word that exists or is planned in the database. |
| `gravity` | float | yes | Fundamentality score from 0.0 to 1.0. Tier 0 = 1.0, Tier 1 = 0.7, Tier 2 = 0.4, Tier 3 = context-dependent (0.1–0.3). Higher gravity = more universal = should appear in more navigation paths. |
| `domain` | string | yes | Scope of applicability. One of: `universal` (Tier 0–1), `protocol` (Tier 1–2), `domain-specific` (Tier 3), `temporary` (Tier 3 candidates under evaluation). |
| `project` | string | yes | The project namespace this word belongs to. `stillwater` for the seed database. Use project name for project-specific extensions. |
| `date_added` | string | yes | ISO 8601 date when this word was added to the database (`YYYY-MM-DD`). |
| `usage_count` | integer | yes | Number of times this word has been used in a navigation query. Starts at 0. Incremented by the navigation runtime. |
| `last_used` | string or null | yes | ISO 8601 datetime of last use in a query. `null` if never used. |
| `related_words` | array of strings | yes | Sibling or cross-tier words with strong semantic overlap. Used for fallback when the primary word yields sparse context. |
| `compression_ratio` | float or null | yes | Average measured compression ratio when this word is used as a navigation anchor. `null` until first measured use. Range: 0.0–1.0. |

## Constraints

- `id` is immutable once assigned. Never renumber. Deprecated words keep their ID.
- `word` must be unique across the entire database. No two words can share a canonical form.
- `parent` of a Tier 1 word must be a Tier 0 word. Parent of Tier 2 must be Tier 1 or Tier 0.
- `children` list is non-authoritative at write time but must be kept consistent with `parent` fields of child records.
- `gravity` must exactly equal: 1.0 for tier 0, 0.7 for tier 1, 0.4 for tier 2, variable for tier 3.
- `domain` must be `universal` for all Tier 0 and Tier 1 words.
- Deprecated words must set `domain` to `deprecated` and `children` to `[]`.

## DELTA Governance

Changes to existing records (other than `usage_count`, `last_used`, `compression_ratio`) require a DELTA entry documenting:
- version before change
- version after change
- rationale
- migration note for any system relying on the old values

New words added at Tier 0 or Tier 1 require review and explicit rung_target RUNG_65537 before promotion.

## Null vs Zero

- `compression_ratio: null` means the word has never been used in a measured navigation. Not the same as `compression_ratio: 0.0` (which would mean navigation used this word and compressed nothing).
- `usage_count: 0` means the word exists but has never been queried. Not the same as the word being absent.
- `last_used: null` means no usage has occurred. Not the same as an empty string.
