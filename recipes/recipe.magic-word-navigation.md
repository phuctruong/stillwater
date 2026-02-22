---
id: recipe.magic-word-navigation
version: 1.0.0
title: Magic Word Navigation (Trunk-First Context Loading)
description: Navigate a codebase or knowledge base using magic words as compressed tier keys. Extracts query keywords, maps them to tier anchors in the phuc-magic-words registry, traverses trunk-first to minimize context loaded, validates compression ratio, and returns targeted context with a navigation receipt.
skill_pack:
  - prime-safety
  - phuc-magic-words
  - phuc-gps
compression_gain_estimate: "Encodes 30–60 minutes of manual codebase navigation and context gathering into a 5-minute systematic trunk-first traversal with validated compression ratio"
steps:
  - step: 1
    action: "Extract magic words from query: read query verbatim, identify all nouns and domain terms, match against phuc-magic-words tier registry, emit scratch/navigation_keywords.json with {query, extracted_words: [{word, tier, anchor, confidence}]}"
    artifact: "scratch/navigation_keywords.json — {query, extracted_words list, unmatched_terms list}"
    checkpoint: "extracted_words list is non-empty; each entry has word + tier + anchor; unmatched_terms list explicitly present (may be empty but not null)"
    rollback: "If no magic words extractable from query AND no MAGIC_WORDS_HINT provided, emit status=NEED_INFO listing unmatched terms; do not proceed to tier mapping"
  - step: 2
    action: "Map extracted magic words to tier tree: for each magic word, identify its position in the phuc-gps tier hierarchy (trunk / branch / leaf); sort by tier level ascending (trunk first); emit scratch/navigation_tier_map.json"
    artifact: "scratch/navigation_tier_map.json — {words_by_tier: {trunk: [], branch: [], leaf: []}, traversal_order: [sorted word list]}"
    checkpoint: "traversal_order is non-empty; trunk-level words appear before branch-level words; leaf-level words appear last; no word appears more than once"
    rollback: "If tier mapping fails for any word, log the failure in scratch/navigation_run.log with the unresolved word; continue with remaining words; emit NEED_INFO only if ALL words fail to map"
  - step: 3
    action: "Traverse trunk tiers: for each trunk-tier magic word, locate the corresponding files in the repository (using the anchor as a search key); read only top-level entry points (not full subtrees); emit scratch/navigation_trunk_hits.json"
    artifact: "scratch/navigation_trunk_hits.json — {trunk_files: [{word, anchor, file_path, lines_read, justification}]}"
    checkpoint: "At least one trunk file found; each entry has file_path (repo-relative), lines_read, justification; justification explains why this file is the trunk entry for this word"
    rollback: "If trunk traversal finds no files, fall back to branch-tier traversal immediately; log trunk miss in scratch/navigation_run.log"
  - step: 4
    action: "Check if trunk context resolves query: review trunk_hits content against the query; if query is fully answered by trunk context, stop and proceed to step 5; otherwise identify remaining unresolved query facets and map to branch/leaf words"
    artifact: "scratch/navigation_resolution_check.json — {query_resolved_by_trunk: true|false, resolved_facets: [], unresolved_facets: [], branch_words_needed: []}"
    checkpoint: "resolution_check is present; query_resolved_by_trunk is explicitly set (never null); unresolved_facets list explicitly present even if empty"
    rollback: "If resolution check is inconclusive (cannot determine without reading more), proceed to branch traversal for all unresolved facets; do not loop indefinitely"
  - step: 5
    action: "Branch traversal (if needed): for each unresolved facet, load corresponding branch/leaf files using the tier map; limit to files within the localization budget; emit scratch/navigation_branch_hits.json"
    artifact: "scratch/navigation_branch_hits.json — {branch_files: [{word, anchor, file_path, lines_read, justification}]} — may be empty if trunk resolved query"
    checkpoint: "If query_resolved_by_trunk is true, branch_hits may be empty (valid); if false, branch_hits must have at least one entry; total files loaded across trunk + branch does not exceed budget"
    rollback: "If budget exceeded, stop loading additional files and proceed with what was loaded; log budget cap in scratch/navigation_run.log"
  - step: 6
    action: "Validate compression ratio: count query tokens; count total context tokens loaded (trunk + branch); compute ratio = query_tokens / context_loaded_tokens; check ratio >= 2.0 (minimum efficiency gate); emit scratch/navigation_compression.json"
    artifact: "scratch/navigation_compression.json — {query_tokens, context_loaded_tokens, compression_ratio, gate_passed: true|false, notes}"
    checkpoint: "compression_ratio is computed from actual counts (not estimated); gate_passed is set; notes present if gate_passed is false"
    rollback: "If compression_ratio < 2.0, do not fail automatically; log warning in notes field and proceed; BLOCK only if context_loaded_tokens > 5x query_tokens without clear justification"
  - step: 7
    action: "Respond with context: synthesize the loaded context into a direct answer to the query; include file path references for every factual claim; emit final context_load_receipt.json listing all files loaded with magic word match and relevance score"
    artifact: "scratch/context_load_receipt.json — {files_loaded: [{path, lines_read, magic_word_match, relevance_score}], total_lines_loaded, budget_used_fraction}"
    checkpoint: "context_load_receipt has entries for all files loaded in steps 3 and 5; every factual claim in the response has a file_path + line reference; relevance_score is non-null for every entry"
    rollback: "If context does not answer the query after full traversal, emit status=NEED_INFO listing what information is missing and what further files would be needed"
forbidden_states:
  - FULL_CORPUS_LOAD: "Loading all files in repo without magic word filtering; trunk-first discipline is the entire point of this recipe"
  - SKIP_TRUNK: "Jumping directly to branch or leaf files without first checking trunk tiers; every query must try trunk resolution first"
  - COMPRESSION_BYPASS: "Reporting PASS without computing compression ratio in step 6; ratio may be low but must be computed and logged"
  - MAGIC_WORD_INVENTION: "Adding magic words in step 1 that are not present in the query or MAGIC_WORDS_HINT; no synonym expansion without explicit authorization"
  - NULL_ZERO_CONFUSION: "Treating 'no magic words extracted' as an empty magic words list; null extraction is NEED_INFO; empty list is a different state"
  - CLAIM_WITHOUT_FILE_WITNESS: "Responding to query with factual claims not backed by a file_path + line reference in context_load_receipt.json"
verification_checkpoint: "Run: python3 -c \"import json; r=json.load(open('scratch/navigation_compression.json')); assert r['compression_ratio'] is not None; assert r['gate_passed'] is not None\" — must exit 0; Run: python3 -c \"import json; r=json.load(open('scratch/context_load_receipt.json')); assert len(r['files_loaded']) > 0; assert all(e['magic_word_match'] for e in r['files_loaded'])\" — must exit 0"
rung_target: 641
---

# Recipe: Magic Word Navigation (Trunk-First Context Loading)

## Purpose

Replace ad-hoc codebase navigation ("read everything that might be relevant") with a compressed, systematic, and auditable trunk-first traversal. Magic words act as tier keys that point the navigator directly to the right layer of the knowledge hierarchy. The compression ratio check enforces that the navigator is actually being efficient — not just reading files in a different order.

## When to Use

- When a query requires context from a large codebase and you need to minimize tokens loaded
- When onboarding a new agent to a project (give it the trunk magic words first)
- When answering a targeted question without loading the full codebase
- As the first step of any recipe that requires codebase context

## Tier System (phuc-gps)

Magic words map to one of three tier levels:

| Tier | Description | Examples |
|------|-------------|---------|
| Trunk | Top-level concepts; resolve most queries | `northstar`, `rung`, `skill`, `recipe` |
| Branch | Module-level concepts; resolve domain queries | `coder`, `scout`, `portal`, `citizen` |
| Leaf | File-level concepts; resolve specific queries | `repro_red`, `handshake`, `synthesis` |

Traverse trunk before branch before leaf. Stop as soon as the query is resolved.

## Compression Ratio

The compression ratio gate (>= 2.0) ensures the navigation was efficient:
- ratio = query_tokens / context_loaded_tokens
- A ratio of 2.0 means you loaded at most 2x the information actually needed
- A ratio > 10.0 is excellent (Shannon-optimal navigation)
- A ratio < 1.0 means you loaded MORE context than the query required (inefficient)

## Output Artifacts

- `scratch/navigation_keywords.json` — extracted magic words with tier assignments
- `scratch/navigation_tier_map.json` — traversal order (trunk first)
- `scratch/navigation_trunk_hits.json` — files found at trunk tier
- `scratch/navigation_resolution_check.json` — whether trunk resolved the query
- `scratch/navigation_branch_hits.json` — files found at branch/leaf tier (if needed)
- `scratch/navigation_compression.json` — compression ratio report
- `scratch/context_load_receipt.json` — final receipt of all loaded context

## Notes

- If the query has no magic words at all, this recipe returns NEED_INFO. Use recipe.swarm-pipeline to do full codebase exploration instead.
- Compression ratio is informational at rung 641; it becomes a hard gate at rung 274177.
- The trunk-first rule is the core invariant. Any navigator that starts at leaves is using this recipe incorrectly.
