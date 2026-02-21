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
#                     → Managed LLM: Together.ai/OpenRouter +$3/mo (20% margin)
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
Location: /home/phuc/projects/solace-browser/oauth3/
Reference: /home/phuc/projects/solace-browser/OAUTH3-WHITEPAPER.md (Sections 1-5)
Reference: /home/phuc/projects/solace-browser/ROADMAP.md (Build Prompt 1)
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
Location: /home/phuc/projects/solace-browser/
Reference: /home/phuc/projects/solace-browser/OAUTH3-WHITEPAPER.md (Section 6)
Reference: /home/phuc/projects/solace-browser/ROADMAP.md (Build Prompt 2)
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
Location: /home/phuc/projects/solace-browser/recipes/
Reference: /home/phuc/projects/solace-browser/primewiki/gmail/gmail-page-flow.prime-mermaid.md
Reference: /home/phuc/projects/solace-browser/primewiki/gmail/gmail-oauth2.prime-mermaid.md
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

Location: /home/phuc/projects/solace-browser/
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

Reference /home/phuc/projects/solace-browser/primewiki/PRIMEWIKI_STANDARDS.md for PM format.
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
Location: /home/phuc/projects/solace-browser/recipes/
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

Reference existing recipes in /home/phuc/projects/solace-browser/recipes/ for format.
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
Location: /home/phuc/projects/solace-browser/api/
Reference: /home/phuc/projects/solaceagi/SOLACEAGI-WHITEPAPER.md
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
Location: /home/phuc/projects/solace-cli/
Reference: /home/phuc/projects/solace-cli/SOLACE-CLI-WHITEPAPER.md (Section 5)
Reference: /home/phuc/projects/solace-browser/OAUTH3-WHITEPAPER.md
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
Location: /home/phuc/projects/solace-cli/
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

Read /home/phuc/projects/solace-cli/SOLACE-CLI-WHITEPAPER.md first.
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
Location: /home/phuc/projects/solace-cli/
Reference: /home/phuc/projects/stillwater/NORTHSTAR.md (Store section)
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
Location: /home/phuc/projects/solaceagi/api/
Reference: /home/phuc/projects/solaceagi/SOLACEAGI-WHITEPAPER.md
Reference: /home/phuc/projects/solaceagi/ROADMAP.md
Rung target: 641

## Architecture (CORRECT):
- stillwater/cli = OSS base CLI
- solace-cli = PRIVATE extension of stillwater/cli → this is the backend
- solaceagi.com = integration layer (solace-cli + twin browser + hosted LLM)

The hosted platform provides:
1. OAuth3 vault management (user's agency tokens, encrypted)
2. LLM routing — TWO modes:
   a. BYOK: user provides own Anthropic/OpenAI/Llama key → zero markup, stored encrypted
   b. Managed LLM: we route to Together.ai/OpenRouter → charge 20% markup (flat ~$3/month)
3. Recipe execution endpoint (trigger cloud twin)
4. Stillwater Store access (browse/install skills)
5. Evidence bundle storage (90-day history for Pro users)

## Files to create:
- api/__init__.py
- api/main.py — FastAPI app, routes
- api/oauth3.py — Agency token vault (AES-256-GCM, zero-knowledge)
- api/users.py — User management (BYOK key storage, tier enforcement)
- api/llm_proxy.py — LLM router: BYOK passthrough OR Together.ai/OpenRouter managed
- api/recipes.py — Recipe execution dispatch
- api/store.py — Stillwater Store proxy
- tests/test_api.py — Tests for each endpoint

## LLM proxy (day-one strategy):
Together.ai primary (Llama 3.3 70B: $0.59/M tokens), OpenRouter fallback.
At 70% recipe hit rate: avg $0.0005/task LLM cost. Managed tier = $3/mo flat.
Never store API keys in plaintext. BYOK keys: AES-256-GCM encrypted per user.

## Business tier enforcement:
- Free: local execution only, BYOK only
- Managed LLM (+$3/mo): hosted LLM passthrough via Together.ai/OpenRouter
- Pro ($19/mo): cloud twin + OAuth3 vault + 90-day evidence + managed LLM included
- Enterprise ($99/mo): SOC2 audit mode, team tokens, private store, dedicated nodes
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
Location: /home/phuc/projects/solaceagi/twin/
Reference: /home/phuc/projects/solaceagi/SOLACEAGI-WHITEPAPER.md (Cloud Twin section)
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
1. /home/phuc/projects/stillwater/papers/oauth3-spec-v0.1.md
2. /home/phuc/projects/stillwater/skills/oauth3-enforcer.md

Reference: /home/phuc/projects/solace-browser/OAUTH3-WHITEPAPER.md (read this first)

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
Format: same as other skills in /home/phuc/projects/stillwater/skills/
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
Location: /home/phuc/projects/stillwater/store/
Reference: /home/phuc/projects/stillwater/NORTHSTAR.md (Store section)
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
