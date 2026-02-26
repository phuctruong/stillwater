# CLAUDE.md — Stillwater
# Software 5.0 OS | Updated: 2026-02-24

## Project
RUNG_TARGET: 65537
NORTHSTAR: Phuc_Forecast
PROJECT: Stillwater (OSS)
DOMAIN: verification + governance + skill store + LLM portal + orchestration engine
BELT: YELLOW (approaching Orange)
TESTS: 1,439 (all phases complete)

## Architecture
- `src/cli/src/stillwater/` — core engine (TripleTwinEngine, CPULearner, DataRegistry, AuditLogger, SmallTalkResponder)
- `admin/` — Admin UI and services (ports 8789-8794)
- `data/default/skills/` — 25+ skills (prime-safety, prime-coder, eq-*, phuc-*)
- `data/default/swarms/` — 25 agent types (persona-enhanced)
- `data/default/combos/` — wish+recipe combos
- `data/default/personas/` — personas by category
- `data/default/recipes/` — shipped recipe database
- `data/default/questions/` — question database
- `data/default/wishes/` — wish artifacts
- `data/default/` — shipped defaults (cpu-nodes, seeds, smalltalk)
- `data/custom/` — user overrides (DataRegistry overlay)
- `papers/` — 55 research papers
- `data/default/diagrams/` — architecture diagrams

## Orchestration Engine (Triple-Twin)
- Phase 1: Small Talk (cpu-first, threshold 0.70, 9 labels, 49 seeds)
- Phase 2: Intent Match (threshold 0.80, 21 labels, 52 seeds)
- Phase 3: Execution (threshold 0.90, 21 labels, 51 seeds)
- CPU hit rate: 100% across 24 test prompts
- AuditLogger: FDA Part 11 compliant, SHA-256 hash chain, wired to TripleTwinEngine
- SmallTalkResponder: 577 lines, WARM framework, wired to TripleTwinEngine

## Codex Collaboration
- `scratch/todo.md` — async task board (Claude writes tasks, Codex executes)
- Claude = roadmap orchestrator (plans, reviews, persists learnings)
- Codex = coder (tests, fixes, QA, implementations)
- Convention: Codex reads scratch/todo.md, picks READY tasks, marks DONE with evidence

## FALLBACK BAN (Software 5.0 Law — ABSOLUTE)
**Fallbacks are BANNED from Software 5.0. No exceptions.**
- NO `except Exception: pass` — stop and fix instead
- NO `except Exception: return None/""/{}/[]` — raise the error
- NO `except: return False` — bare except is forbidden
- NO fake data, mock responses, placeholder success in production code
- NO `success: true` on unimplemented endpoints — return 501 Not Implemented
- NO silent degradation — if a service is down, FAIL LOUDLY
- NO broad exception catches — catch SPECIFIC exceptions only
- Acceptable: `except (SpecificError, AnotherError)` with logging
- Acceptable: audit logging wrapped in try/except (logging must never crash caller)
- Rule: "Fallbacks = blackhole for AI hallucination. Stop and fix instead."
- LEC: LEC-FALLBACK-BAN — crystallized 2026-02-24

## Development Pipeline (5 steps, mandatory order)
1. DIAGRAM — Prime Mermaid diagram first (defines the contract)
2. WEBSERVICE — Implement the service (FastAPI, self-registering)
3. UNIT TEST — Write tests (minimum 25 per service)
4. STILLWATER SERVICE — Wire into stillwater-server.sh
5. CLI — Add CLI commands + documentation

## Key Conventions
- convention_combo_naming: {wish_id}-combo (no mapping file)
- convention_data_default: data/default/ shipped, data/custom/ user overrides
- convention_cpu_nodes: data/default/cpu-nodes/[name].md with YAML frontmatter
- convention_seed_chain: P3 combo keyword needs P1 task seed + P2 intent seed
- seed_vocab_rule: specific nouns (documentation, tests) not generic verbs (write, run)
- scratch_first: all working files → scratch/ until verified
- fallback_ban: NO silent fallbacks — stop and fix instead (LEC-FALLBACK-BAN)
- admin_ui_view_only: admin UI is VIEW-ONLY, opens files in VSCode, tests + prompts only
- claude_code_default_llm: Claude Code CLI is the default LLM backend (zero-config)
- supported_llm_providers: claude-code, anthropic, gemini, openai, together, openrouter (6 total)
- no_provider_fallback: use ONLY configured default_provider — never silently switch

## Running Tests
```bash
pytest tests/ -v                           # all 1,439 tests
pytest src/cli/tests/ -v                       # orchestration engine (104+43+72+49=268)
pytest tests/test_store_client.py -v       # store client (66)
pytest src/cli/tests/test_triple_twin.py -v    # triple-twin engine (104)
```

## Known Bugs (Phase 1 QA)
- BUG-P1-001: tie-break favors first keyword (position-dependent classification)
- BUG-P1-002: "question" label dead (keywords "what","how","why" are all stop words)
- BUG-P1-003: ultra-short inputs (<3 chars) bypass extraction
- BUG-P1-005: seed bias (87.8% task vs 12.2% non-task)

## Skills (reference only — load full file for production work)
- prime-safety: god-skill, fail-closed, wins all conflicts
- prime-coder: evidence-first coding, red/green gate, rung enforcement
- phuc-forecast: DREAM→FORECAST→DECIDE→ACT→VERIFY
- phuc-orchestration: dispatch matrix, sub-agent skill packs
- Full skill files: data/default/skills/*.md
