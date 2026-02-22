#!/usr/bin/env bash
# launch-swarm.sh — Phuc Swarm Launcher
# Usage: ./launch-swarm.sh <project> <phase>
# Example: ./launch-swarm.sh solace-browser oauth3-core
#
# ARCHITECTURE REMINDER:
#   stillwater/cli  = OSS (this repo — base CLI anyone can use)
#   solace-cli      = PRIVATE extension of stillwater/cli (powers solaceagi.com)
#   solace-browser  = OSS OAuth3 reference implementation
#   solaceagi.com   = Integration layer (solace-cli + twin browser + hosted LLM)
#                     → BYOK: users bring own API key (zero markup)
#                     → Managed LLM: hosted LLM routing (no API key needed)
#
# This script generates the copy-paste prompt for a haiku/sonnet session.
# Run this, paste the output into a new Claude session, report results back here.

set -euo pipefail

PROJECTS_ROOT="$HOME/projects"
STILLWATER="$PROJECTS_ROOT/stillwater"

show_prompt() {
  local project="$1"
  local phase="$2"
  local project_path="$PROJECTS_ROOT/$project"

  echo ""
  echo "═══════════════════════════════════════════════════════"
  echo "  PHUC SWARM LAUNCH PROMPT"
  echo "  Project: $project | Phase: $phase"
  echo "═══════════════════════════════════════════════════════"
  echo ""
  echo "Copy everything between the ─── lines into a new haiku/sonnet Claude session:"
  echo ""
  echo "────────────────────────────────────────────────────────"
  echo ""
  echo "## NORTHSTAR — Read this first. All work must align with it."
  echo ""
  if [ -f "$project_path/NORTHSTAR.md" ]; then
    cat "$project_path/NORTHSTAR.md"
  else
    echo "(No NORTHSTAR.md found at $project_path/NORTHSTAR.md)"
  fi
  echo ""
  echo "---"
  echo ""
  echo "## STILLWATER NORTHSTAR (ecosystem-level)"
  if [ -f "$STILLWATER/NORTHSTAR.md" ]; then
    head -30 "$STILLWATER/NORTHSTAR.md"
  else
    echo "(No NORTHSTAR.md found at $STILLWATER/NORTHSTAR.md)"
  fi
  echo ""
  echo "---"
  echo ""
}

usage() {
  echo "Usage: $0 <project> <phase>"
  echo ""
  echo "Projects + Phases:"
  echo "  solace-browser  oauth3-core       Build OAuth3 token/scope/enforcement module"
  echo "  solace-browser  oauth3-consent     Build consent UI + step-up auth"
  echo "  solace-browser  gmail-recipes      Build Gmail automation recipes"
  echo "  solace-browser  substack-recipes   Build Substack automation recipes (first-mover)"
  echo "  solace-browser  twitter-recipes    Build Twitter/X automation recipes"
  echo "  solace-browser  solaceagi-mvp      Build solaceagi.com FastAPI MVP"
  echo "  solace-cli      oauth3-commands    Build solace auth grant/revoke/list"
  echo "  solace-cli      rung-execution     Build rung-gated solace run command"
  echo "  solace-cli      store-commands     Build solace store install/submit/browse"
  echo "  solaceagi       api-backend        Build FastAPI backend (oauth3 vault + recipes)"
  echo "  solaceagi       cloud-twin         Build headless browser cloud twin"
  echo "  stillwater      oauth3-spec        Write oauth3-spec-v0.1.md + oauth3-enforcer skill"
  echo "  stillwater      store-api          Build Stillwater Store FastAPI endpoints"
  echo "  stillwater      northstar-reverse  Reverse-engineer path to any Northstar goal"
  echo "  ANY_PROJECT     northstar-path     Apply reverse engineering to project Northstar"
  echo "  paudio          audit              Phase 0: Audit & baseline (gap analysis)"
  echo "  paudio          engine-harden      Phase 1: Core engine hardening (100% determinism)"
  echo "  paudio          compute-grid       Phase 2: Volunteer compute network (PAudio Grid)"
  echo "  paudio          voice-arena        Phase 3: Voice Arena (AI singing competition)"
  echo "  paudio          karaoke            Phase 4: Karaoke learning sessions"
  echo "  paudio          stt-pipeline       Phase 5: STT pipeline (Whisper fine-tuning)"
  echo "  paudio          integration        Phase 6: Platform integration (solaceagi+cli+browser)"
  echo "  paudio          multilingual       Phase 7: Multilingual expansion (17 languages)"
  echo "  paudio          production         Phase 8: Production promotion (rung 65537)"
  echo ""
  echo "Example: $0 solace-browser oauth3-core"
  exit 1
}

if [ $# -lt 2 ]; then
  usage
fi

PROJECT="$1"
PHASE="$2"

case "$PROJECT/$PHASE" in

  "solace-browser/oauth3-core")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills loaded.

## Task
Build the OAuth3 core module for solace-browser.
Location: solace-browser/oauth3/
Reference: solace-browser/OAUTH3-WHITEPAPER.md (Sections 1-5)
Reference: solace-browser/ROADMAP.md (Build Prompt 1)
Rung target: 641

## Files to create:
1. `oauth3/__init__.py` — AgencyToken dataclass + exports
2. `oauth3/token.py` — Token creation/storage (AES-256-GCM encrypted vault)
3. `oauth3/scopes.py` — Scope registry (linkedin.*, gmail.*, hackernews.*, reddit.*, notion.*)
4. `oauth3/enforcement.py` — Check token before recipe execution; reject if scope mismatch
5. `oauth3/revocation.py` — Instant token kill + vault clear
6. `tests/test_oauth3.py` — Tests for grant, list, revoke, enforcement gate

## AgencyToken Schema (from whitepaper):
{
  "token_id": str (uuid4),
  "scopes": list[str],  # e.g. ["linkedin.read_messages", "linkedin.comment"]
  "issued_at": int (unix timestamp),
  "expires_at": int (unix timestamp),
  "encrypted": bool,
  "revoked": bool
}

## Scope Registry (build these):
- linkedin.read_messages, linkedin.comment, linkedin.post_create, linkedin.connect
- gmail.read_inbox, gmail.send_email, gmail.search, gmail.label
- hackernews.submit, hackernews.comment, hackernews.vote
- reddit.post_create, reddit.comment, reddit.vote
- notion.read_page, notion.write_page, notion.search

## Evidence required:
- tests/test_oauth3.py passing (red→green gate)
- tests.json showing grant + revoke + enforcement gate working
- Token stored encrypted; revoked token blocked by enforcement

Read OAUTH3-WHITEPAPER.md first, then implement. Rung 641 minimum.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-browser/oauth3-consent")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build the OAuth3 consent UI for solace-browser.
Location: solace-browser/
Reference: solace-browser/OAUTH3-WHITEPAPER.md (Section 6)
Reference: solace-browser/ROADMAP.md (Build Prompt 2)
Rung target: 641

## Files to create/update:
1. `web/consent.html` — OAuth3 consent dialog at GET /consent?scopes=linkedin.read_messages,linkedin.comment
2. `web/settings_tokens.html` — Token management page: list active tokens, revoke button per token
3. `web/index.html` — Update home page: show OAuth3 scope badges per site (locked/unlocked)
4. `api/consent_routes.py` — FastAPI: GET /consent, POST /consent/grant, DELETE /consent/revoke/{token_id}

## Consent Dialog Requirements:
- Show: requested scopes in plain English ("Read your LinkedIn messages")
- Show: expiry (1h, 8h, 24h, 7d options)
- Show: what each scope allows (not technical jargon)
- Buttons: "Grant" | "Deny"
- Step-up auth: for destructive scopes (*.delete, *.send_email) show extra warning

Read OAUTH3-WHITEPAPER.md Section 6 first, then implement. Vanilla HTML/CSS/JS only.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-browser/gmail-recipes")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build Gmail automation recipes for solace-browser.
Location: solace-browser/recipes/
Reference: solace-browser/primewiki/gmail/gmail-page-flow.prime-mermaid.md
Reference: solace-browser/primewiki/gmail/gmail-oauth2.prime-mermaid.md
Rung target: 641

## Recipes to create (JSON format matching existing LinkedIn recipes):
1. `gmail-read-inbox.recipe.json` — List unread messages (subject, from, snippet)
2. `gmail-search.recipe.json` — Search messages by query string
3. `gmail-send-email.recipe.json` — Compose + send (requires step-up OAuth3 auth)
4. `gmail-label.recipe.json` — Apply/remove label on message

## CRITICAL: Bot detection bypass (from primewiki):
- Char-by-char typing: 80-200ms per character (NEVER use .fill() or .type() with fast speed)
- Selectors: [data-testid="compose-button"], [data-tooltip="Send"]
- Wait for: [role="dialog"] before composing
- Check: SID/HSID/SSID/APISID cookies present before starting

## OAuth3 scopes required:
- gmail.read_inbox → for read-inbox, search, label
- gmail.send_email → for send (step-up auth required)

Read both primewiki files first. Implement char-by-char typing for ALL text input.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-browser/substack-recipes")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent + Scout agent with Prime Coder + Prime Safety skills.

## Task
Build Substack automation recipes for solace-browser.
THIS IS A FIRST-MOVER OPPORTUNITY. No competitor has working Substack automation.

Location: solace-browser/
Steps:
1. SCOUT: Navigate to substack.com and map the page states using Prime Mermaid format
2. CREATE primewiki/substack/ directory with PM triplet
3. BUILD recipes

## Phase 1 - Scout (do this first):
Use browser automation to explore substack.com:
- Login page: selectors, cookie names, session storage keys
- Dashboard: post list, create button, draft list
- Editor: how compose works (rich text editor type? TipTap? Quill?)
- Publish flow: draft → preview → publish

## Phase 2 - PM Triplet:
Create:
- primewiki/substack/substack-page-flow.mmd (Mermaid state machine)
- primewiki/substack/substack-page-flow.sha256 (sha256sum of .mmd)
- primewiki/substack/substack-page-flow.prime-mermaid.md (human spec)

## Phase 3 - Recipes:
- substack-read-posts.recipe.json — List published posts
- substack-create-draft.recipe.json — Create new draft
- substack-publish.recipe.json — Publish existing draft (step-up OAuth3 auth)

Reference solace-browser/primewiki/PRIMEWIKI_STANDARDS.md for PM format.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-browser/twitter-recipes")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build Twitter/X automation recipes for solace-browser.
Location: solace-browser/recipes/
Rung target: 641

## Recipes to create:
1. `twitter-read-feed.recipe.json` — Read timeline (home feed, no auth wall bypass)
2. `twitter-post-tweet.recipe.json` — Post tweet (requires step-up OAuth3 auth)
3. `twitter-reply.recipe.json` — Reply to a tweet by URL

## OAuth3 scopes required:
- twitter.read_feed → read timeline
- twitter.post_tweet → create tweet (step-up auth)
- twitter.reply → reply to tweet (step-up auth)

## Bot detection: char-by-char typing at 80-200ms; no rapid automation.

Reference existing recipes in solace-browser/recipes/ for format.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-browser/solaceagi-mvp")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build the solaceagi.com FastAPI MVP wired to solace-browser.
Location: solace-browser/api/
Reference: solaceagi/SOLACEAGI-WHITEPAPER.md
Rung target: 641

## Goal: Minimal viable hosted platform endpoint
- POST /run-recipe — accepts {recipe_name, params, api_key (BYOK)}
- GET /recipes — list available recipes
- POST /tokens/grant — agency token grant
- DELETE /tokens/revoke — agency token revoke

## The hosted platform (day 1):
- BYOK only at launch (user provides Anthropic/OpenAI key — zero markup)
- Managed LLM ($3/mo) added in phase 2

Read SOLACEAGI-WHITEPAPER.md for full architecture before coding.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-cli/oauth3-commands")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Implement OAuth3 commands for solace-cli.
Location: solace-cli/
Reference: solace-cli/SOLACE-CLI-WHITEPAPER.md (Section 5)
Reference: solace-browser/OAUTH3-WHITEPAPER.md
Rung target: 641

## Commands to implement:
1. `solace auth grant --scope github.create_issue --ttl 1h`
   → Create agency token, store encrypted in ~/.solace/vault.enc
   → Print: [Lane A] Token granted: scope=github.create_issue ttl=1h expires=2026-02-21T10:00:00Z

2. `solace auth revoke`
   → Kill ALL active tokens, clear vault
   → Print: [Lane A] All tokens revoked. Vault cleared.

3. `solace auth list`
   → Show active tokens with expiry + scopes
   → Print table: token_id | scopes | expires_at | status

## Lane algebra (from whitepaper):
Every output must be prefixed with [Lane A], [Lane B], or [Lane C]:
- [Lane A] = executable evidence (test results, token grants, file hashes)
- [Lane B] = derived reasoning
- [Lane C] = heuristic (forecasts, estimates)

## Token vault:
- Store at ~/.solace/vault.enc
- Encrypted with AES-256-GCM
- Key derived from user passphrase (PBKDF2, 100k iterations)
- On first run: prompt to set vault password

## Evidence required:
- tests showing grant → list → revoke cycle
- Token encrypted at rest (verify vault file is not plaintext JSON)
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-cli/rung-execution")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build rung-gated execution for solace-cli.
Location: solace-cli/
Rung target: 641

## Command to implement:
`solace run <recipe> [args...]`
- Check OAuth3 scope BEFORE executing recipe
- If scope missing: prompt for grant (step-up auth)
- Run recipe and produce evidence bundle
- Print: [Lane A] Recipe complete. Evidence: evidence/<recipe>/<timestamp>/

## Gate enforcement:
- Rung 641: scope check + evidence bundle
- Rung 274177: scope check + seed replay (run twice, compare outputs)
- Rung 65537: scope check + adversarial check + security scan

Read solace-cli/SOLACE-CLI-WHITEPAPER.md first.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solace-cli/store-commands")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build Stillwater Store commands for solace-cli.
Location: solace-cli/
Reference: stillwater/NORTHSTAR.md (Store section)
Rung target: 641

## Commands to implement:
1. `solace store browse [--tag oauth3] [--tag recipe]`
   → List available skills/recipes from stillwater store API
2. `solace store install <skill-id>`
   → Download skill to ~/.solace/skills/<id>.md
3. `solace store submit <skill-file>`
   → Submit a skill for community review (POST to store API)

## Evidence required:
- browse returns JSON list
- install creates file at correct path
- submit returns submission ID

Read NORTHSTAR.md for store architecture context.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solaceagi/api-backend")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build the FastAPI backend for solaceagi.com.
Location: solaceagi/api/
Reference: solaceagi/SOLACEAGI-WHITEPAPER.md
Reference: solaceagi/ROADMAP.md
Rung target: 641

## Architecture (CORRECT):
- stillwater/cli = OSS base CLI
- solace-cli = PRIVATE extension of stillwater/cli → this is the backend
- solaceagi.com = integration layer (solace-cli + twin browser + hosted LLM)

The hosted platform provides:
1. OAuth3 vault management (user's agency tokens, encrypted)
2. LLM routing — TWO modes:
   a. BYOK: user provides own Anthropic/OpenAI/Llama key → zero markup, stored encrypted
   b. Managed LLM: we route to upstream LLM providers → markup applied (flat monthly add-on)
3. Recipe execution endpoint (trigger cloud twin)
4. Stillwater Store access (browse/install skills)
5. Evidence bundle storage (90-day history for Pro users)

## Files to create:
- api/__init__.py
- api/main.py — FastAPI app, routes
- api/oauth3.py — Agency token vault (AES-256-GCM, zero-knowledge)
- api/users.py — User management (BYOK key storage, tier enforcement)
- api/llm_proxy.py — LLM router: BYOK passthrough OR managed upstream routing
- api/recipes.py — Recipe execution dispatch
- api/store.py — Stillwater Store proxy
- tests/test_api.py — Tests for each endpoint

## LLM proxy (day-one strategy):
Route to upstream LLM providers (primary and fallback). Zero GPU infra.
Never store API keys in plaintext. BYOK keys: AES-256-GCM encrypted per user.

## Business tier enforcement:
- Free: local execution only, BYOK only
- Managed LLM (add-on): hosted LLM passthrough (no API key needed)
- Pro (paid tier): cloud twin + OAuth3 vault + 90-day evidence + managed LLM included
- Enterprise (paid tier): SOC2 audit mode, team tokens, private store, dedicated nodes
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "solaceagi/cloud-twin")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build the headless browser cloud twin for solaceagi.com.
Location: solaceagi/twin/
Reference: solaceagi/SOLACEAGI-WHITEPAPER.md (Cloud Twin section)
Rung target: 641

## Goal: Cloud twin = headless browser that executes recipes on behalf of the user
- Receives: {recipe_name, params, agency_token}
- Validates: agency token scope before execution
- Executes: recipe using playwright/puppeteer
- Returns: evidence bundle {screenshots, output, lane_typing}

## Files to create:
- twin/__init__.py
- twin/executor.py — Recipe executor (loads recipe JSON, runs steps)
- twin/oauth3_gate.py — Scope validation before execution
- twin/evidence.py — Evidence bundle builder
- tests/test_twin.py — Test executor with mock browser

Read SOLACEAGI-WHITEPAPER.md Cloud Twin section first.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "stillwater/oauth3-spec")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Writer agent with Software 5.0 Paradigm + Prime Safety skills.

## Task
Write two documents for the Stillwater project:
1. stillwater/papers/oauth3-spec-v0.1.md
2. stillwater/skills/oauth3-enforcer.md

Reference: solace-browser/OAUTH3-WHITEPAPER.md (read this first)

## Document 1: oauth3-spec-v0.1.md
A formal specification (not marketing). Audience: other developers implementing OAuth3.
Sections:
- Abstract (3 sentences)
- 1. Problem Statement (delegation without consent)
- 2. Core Definitions (Agency Token, Scope, Step-Up Auth, Revocation)
- 3. Token Schema (JSON schema, required fields)
- 4. Scope Naming Convention (platform.action format)
- 5. Consent Protocol (flow: request → display → grant → store → enforce)
- 6. Revocation Protocol (immediate, fail-closed, vault clear)
- 7. Evidence Requirements (every delegated action must produce evidence bundle)
- 8. Platform Respect Mode (rate limiting, human-like behavior)
- 9. Reference Implementation (solace-browser)

## Document 2: oauth3-enforcer.md
A Stillwater skill that can be loaded to enforce OAuth3 compliance in any project.
Format: same as other skills in stillwater/skills/
Include:
- Scope validation (reject execution if scope not granted)
- Step-up auth trigger (destructive actions)
- Revocation check (token not expired/revoked)
- Evidence bundle requirement (every action must produce evidence)
- Forbidden states: SCOPE_MISMATCH, EXPIRED_TOKEN, REVOKED_TOKEN, MISSING_EVIDENCE

Read OAUTH3-WHITEPAPER.md before writing. This becomes the official spec.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "stillwater/store-api")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Coder + Prime Safety skills.

## Task
Build Stillwater Store FastAPI endpoints.
Location: stillwater/store/
Reference: stillwater/NORTHSTAR.md (Store section)
Rung target: 641

## Endpoints to implement:
- GET /store/skills — list all published skills (filtered by tag, author, rung)
- GET /store/skills/{id} — get skill detail + download URL
- POST /store/skills — submit a skill (requires API key)
- GET /store/recipes — list all published recipes
- GET /store/recipes/{id} — get recipe detail
- POST /store/recipes — submit a recipe

## Skill/Recipe metadata schema:
{
  "id": str,
  "name": str,
  "version": str,
  "author": str,
  "tags": list[str],
  "rung_certified": int,  # 641, 274177, or 65537
  "description": str,
  "download_url": str,
  "sha256": str
}

## Evidence required:
- tests/test_store.py passing
- GET /store/skills returns list
- POST /store/skills creates entry

Read NORTHSTAR.md for store vision before coding.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/audit")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Scout agent with Prime Safety + Prime Coder skills loaded.

## Task
Run comprehensive audit of PAudio project.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 0)
Rung target: 641

## Steps:
1. Run test suite: pytest -q tests/ — record pass/fail
2. Run determinism sweep: 3 seeds (42, 137, 9001) × 2 replays for existing words
3. Inventory phoneme coverage (IPA symbols with working generators)
4. Inventory word database (verified words with STT QA pass)
5. Assess STT QA gate (faster-whisper integration)
6. Document MOS baseline

## Evidence required:
- audit-report.json (phoneme count, word count, test results, determinism %)
- gap-analysis.md (missing for Phase 1)

Read-only. Do not modify source code. Rung 641 minimum.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/engine-harden")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent (Donald Knuth) with Prime Safety + Prime Coder + Prime Math skills.

## Task
Achieve 100% determinism score. Expand phoneme coverage to 120 IPA symbols.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 1)
Rung target: 274177

## Steps:
1. Fix non-deterministic paths (seed all RNG, exact arithmetic for freq/pitch)
2. Expand Universal Phoneme Atlas to 120 IPA symbols
3. Implement seed sweep CI: 3 seeds × 3 platforms × 2 replays
4. Add null edge cases: silence, single phoneme, max-length
5. Establish behavioral hash registry

## Evidence required:
- tests/test_determinism_sweep.py (3 seeds × 2 replays)
- evidence/determinism-report.json (100% pass)
- No float in verification paths (prime-math enforced)

Never-worse doctrine. All existing tests must pass. Rung 274177.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/compute-grid")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent (Linus Torvalds) with Prime Safety + Prime Coder skills.

## Task
Build PAudio Grid — volunteer compute network for phoneme processing.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 2)
Reference: paudio/skills/paudio-worker.md
Rung target: 641

## Components:
1. Coordinator API (FastAPI): register workers, distribute work, collect results
2. Worker daemon: polls for work, runs synthesis, returns hash + trace
3. Deterministic validator: 2+ workers must agree on audio hash
4. Credit system: complexity_score-based credits after verification

## API pattern: Follow solaceagi Stillwater Store API (sw_sk_ keys, rate limiting)
## Key constraint: CPU-only, deterministic verification, no audio exfiltration

Evidence: tests/test_coordinator.py + tests/test_worker.py passing. Rung 641.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/voice-arena")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent (Shigeru Miyamoto) with Prime Safety + Prime Coder + Phuc Forecast skills.

## Task
Build Voice Arena — gamified AI singing competition for community MOS evaluation.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 3)
Reference: paudio/skills/paudio-judge.md
Rung target: 641

## Components:
1. Head-to-head arena (2 audio clips, pick the better one)
2. ELO rating system for voice models (Decimal only, no float)
3. XP + leaderboard + badges (10 XP per judgment, streaks, titles)
4. Phoneme Unlock Campaigns (community votes elect canonical generators)

## Key: Fun-first, no dark patterns. Inspired by LMSYS Arena + FoldIt + Duolingo.
## Free tier gate: 10 judgments/week required for free TTS access.

Evidence: tests/test_arena.py passing. ELO deterministic. Rung 641.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/karaoke")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent with Prime Safety + Prime Coder skills.

## Task
Build karaoke learning session system with consent-gated pronunciation harvesting.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 4)
Rung target: 641

## Components:
1. Session management (play target audio, record user)
2. Pronunciation scoring (pitch via YIN/PYIN, timing, formants)
3. OAuth3 consent gate (paudio.record_audio scope required)
4. Data harvesting pipeline (opt-in contributions → phoneme database)
5. Song curriculum (difficulty levels, language paths)

## Critical: NO recording without explicit OAuth3 consent. GDPR-compatible.

Evidence: tests/test_karaoke.py passing. Consent flow verified. Rung 641.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/stt-pipeline")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent (Geoffrey Hinton) with Prime Safety + Prime Coder + Prime Math skills.

## Task
Build community-trained STT pipeline with Whisper fine-tuning.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 5)
Rung target: 274177

## Components:
1. Dataset pipeline: community audio → Common Voice format
2. Whisper fine-tuning via LoRA (reproducible with seed)
3. STT API endpoint: POST /api/v1/stt/transcribe
4. Round-trip verification: TTS→STT→text must match
5. Phoneme-level accuracy (not just word-level)

## Evidence: tests/test_stt_pipeline.py + evidence/stt-baseline-vs-finetuned.json
## Constraint: Reproducible fine-tuning (seeded), Decimal WER, consent-only data.

Rung 274177 (seed sweep on fine-tuning).
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/integration")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent (Rob Pike) with Prime Safety + Prime Coder skills.

## Task
Integrate PAudio with stillwater + solaceagi + solace-cli + solace-browser.
Location: paudio/ (+ cross-project files)
Reference: paudio/ROADMAP.md (Phase 6)
Rung target: 274177

## Integration points:
1. solaceagi API: POST /api/v1/tts/synthesize, POST /api/v1/stt/transcribe
2. solace-cli: solace tts, solace stt, solace judge, solace compute
3. stillwater: publish paudio-judge + paudio-worker skills to Store
4. solace-browser: karaoke UI + Voice Arena UI
5. Free tier: 10 judgments/week → free TTS access

## Evidence: end-to-end TTS/STT via solaceagi API, CLI commands working. Rung 274177.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/multilingual")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Coder agent (Noam Chomsky) with Prime Safety + Prime Coder + Prime Math skills.

## Task
Expand PAudio to 5+ languages with cross-language phoneme transfer.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 7)
Rung target: 274177

## Priority languages: Spanish, French, German, Japanese, Mandarin
## Components:
1. Cross-language phoneme transfer (shared generators for /a/, /i/, /u/)
2. Language-specific phoneme sets (unique sounds per language)
3. Tonal phoneme system (Mandarin 4 tones + neutral)
4. Karaoke curriculum per language
5. Community Phoneme Unlock Campaigns per language

## Constraint: English must not regress. Exact arithmetic for tonal system.

Evidence: tests/test_multilingual.py (5 languages × determinism sweep). Rung 274177.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  "paudio/production")
    show_prompt "$PROJECT" "$PHASE"
    cat << 'PROMPT'
You are a Skeptic agent (Bruce Schneier) with Prime Safety + Prime Coder + Phuc Forecast skills.

## Task
Promote PAudio to rung 65537 (production). Full adversarial + security audit.
Location: paudio/
Reference: paudio/ROADMAP.md (Phase 8)
Rung target: 65537

## Sweeps:
1. Adversarial audio: noise injection, accent edge cases, adversarial phonemes
2. Security: compute worker tampering, OAuth3 bypass, API abuse
3. Behavioral hash: 30 daily builds, document all drift
4. Skeptic review: 5 paraphrases per skill
5. Stress test: 100 concurrent judges, 50 concurrent workers

## Assume attacker has read all source code. Every vulnerability = repro script.

Evidence: evidence/promotion-certificate.json (65537 seal). Rung 65537.
PROMPT
    echo ""
    echo "────────────────────────────────────────────────────────"
    ;;

  *)
    echo "Unknown project/phase: $PROJECT/$PHASE"
    echo ""
    usage
    ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  After the session completes:"
echo "  1. Report the rung achieved back here"
echo "  2. Update: $STILLWATER/case-studies/${PROJECT}.md"
echo "  3. Commit: cd $PROJECTS_ROOT/$PROJECT && git add -A && git commit"
echo "═══════════════════════════════════════════════════════"
echo ""
