# /hub — Central Opus Hub Display

Display the full Phuc ecosystem overview — all 4 projects, NORTHSTAR metrics vs actuals, pricing tiers, and suggested next launch-swarm commands. This is the coordination view for the Opus hub session.

## Usage

```
/hub                    # Full ecosystem overview
/hub --metrics          # NORTHSTAR metrics vs actuals only
/hub --pricing          # Pricing tiers only
/hub --swarms           # Next swarm commands only
```

ARGUMENTS: $ARGUMENTS

## Instructions for Claude

When user runs `/hub`:

### Step 1 — Load All Context

Read these files in parallel:
- `/home/phuc/projects/stillwater/NORTHSTAR.md` (master northstar)
- `/home/phuc/projects/stillwater/case-studies/stillwater-itself.md`
- `/home/phuc/projects/stillwater/case-studies/solace-browser.md`
- `/home/phuc/projects/stillwater/case-studies/solace-cli.md`
- `/home/phuc/projects/stillwater/case-studies/solaceagi.md`
- `/home/phuc/projects/stillwater/.claude/memory/context.md` (if it exists)

### Step 2 — Display Full Hub

```
==================================================
PHUC ECOSYSTEM HUB — [TODAY's DATE]
Coordination model: Opus | Session: Hub
==================================================

MASTER EQUATION:
  Intelligence(system) = Memory × Care × Iteration
  Memory  = skills/*.md + recipes/*.json + swarms/*.yaml
  Care    = Verification ladder: 641 → 274177 → 65537
  Iteration = Never-Worse doctrine + git versioning

==================================================
5-PROJECT ARCHITECTURE
==================================================

stillwater (OSS)         — SW5.0 OS + verification + skill store
  ├── stillwater/cli (OSS) — base CLI, part of stillwater repo
  └── stillwater store (OSS) — skill governance + rung-gated publishing

solace-browser (OSS)     — OAuth3 reference impl + twin browser + PM triplets

solace-cli (PRIVATE)     — extends stillwater/cli
  ├── OAuth3 vault management (local AES-256-GCM)
  ├── Twin browser orchestration
  └── solaceagi.com API backend (auth, tier check, managed LLM routing)

solaceagi.com (PAID)     — integration layer
  ├── solace-cli backend (private)
  ├── solace-browser cloud twin
  ├── BYOK: Anthropic/OpenAI/Llama (zero markup)
  └── Managed LLM: Together.ai/OpenRouter (+$3/mo flat)

solace-marketing (PRIVATE) — strategy, GTM, content

==================================================
NORTHSTAR METRICS (target vs actual)
==================================================

[Read NORTHSTAR.md and fill in the table:]

  Metric                          Now      Q2 2026   End 2026
  GitHub stars                    [now]    1,000     10,000
  Projects at rung 65537          [now]    2         8
  Stillwater Store skills         [now]    25        100+
  Recipe hit rate (ecosystem)     [now]    50%       80%
  Community contributors          [now]    5         50
  Paying solaceagi.com users      [now]    1,000     5,000
  MRR                             [now]    $19K      $95K

  NORTHSTAR alignment: ALIGNED | needs attention on [metric]

==================================================
PER-PROJECT STATUS
==================================================

[For each project, read case-study and extract:]

STILLWATER     Path: /home/phuc/projects/stillwater/
  Belt:        [from case study]
  Rung:        [current rung]
  Done:        [completed phases]
  In progress: [current phase]
  Next:        [next phase from ROADMAP]
  Command:     /build stillwater [next-phase]

SOLACE-BROWSER Path: /home/phuc/projects/solace-browser/
  Belt:        [from case study]
  Rung:        [current rung]
  Done:        [completed phases]
  In progress: [current phase]
  Next:        [next phase from ROADMAP]
  Command:     /build solace-browser [next-phase]

SOLACE-CLI     Path: /home/phuc/projects/solace-cli/  [PRIVATE]
  Belt:        [from case study]
  Rung:        [current rung]
  Done:        [completed phases]
  In progress: [current phase]
  Next:        [next phase from ROADMAP]
  Command:     /build solace-cli [next-phase]

SOLACEAGI      Path: /home/phuc/projects/solaceagi/
  Belt:        [from case study]
  Rung:        [current rung]
  Done:        [completed phases]
  In progress: [current phase]
  Next:        [next phase from ROADMAP]
  Command:     /build solaceagi [next-phase]

==================================================
PRICING TIERS (solaceagi.com)
==================================================

Tier          Price    What
Free          $0       Local execution, BYOK, OSS client (stillwater/cli), community skills
Managed LLM   +$3/mo   Hosted LLM (Together.ai/OpenRouter passthrough, no API key needed)
Pro           $19/mo   Cloud twin + OAuth3 vault + 90-day evidence + Managed LLM included
Enterprise    $99/mo   SOC2 audit + team tokens + private store + dedicated nodes

COGS model (BYOK path):
  Recipe hit rate 70% → $0.001/task (Haiku replay)
  COGS: $5.75/user/month → 70% gross margin at $19/mo
  Managed LLM primary: Llama 3.3 70B at $0.59/M tokens (Together.ai)

==================================================
COMPETITIVE POSITION (Feb 2026)
==================================================

Competitor       Missing (vs Phuc ecosystem)
OpenClaw         No evidence trail, no consent, no revocation
Browser-Use      No session persistence, no recipe system, no OAuth3
Bardeen          Chrome extension only, no cloud twin, no step-up auth
Vercel browser   Cloud-only, no recipe library, no OAuth3

Strategic win:   First open standard for AI agency delegation (OAuth3)
Why uncopyable:  Token-revenue vendors (OpenAI, Anthropic) cannot implement OAuth3
                 — it reduces token usage, cannibalizing their revenue

==================================================
NEXT LAUNCH-SWARM COMMANDS (ranked by leverage)
==================================================

[Rank by: (1) unblocks most other work, (2) achieves next belt, (3) serves northstar metric]

Priority 1 — Highest leverage:
  [project] — [phase] — [1 line reason]
  Command: /build [project] [phase]

Priority 2:
  [project] — [phase] — [1 line reason]
  Command: /build [project] [phase]

Priority 3:
  [project] — [phase] — [1 line reason]
  Command: /build [project] [phase]

Swarm shortcuts (copy-paste):
  ./launch-swarm.sh solace-browser oauth3-core       # OAuth3 token module
  ./launch-swarm.sh solace-browser oauth3-consent    # Consent UI
  ./launch-swarm.sh stillwater oauth3-spec           # OAuth3 formal spec
  ./launch-swarm.sh solace-cli oauth3-commands       # CLI auth (PRIVATE)
  ./launch-swarm.sh solaceagi api-backend            # FastAPI + LLM proxy

==================================================
BELT TRACKER
==================================================

  stillwater:     [belt emoji + name]
  solace-browser: [belt emoji + name]
  solace-cli:     [belt emoji + name]
  solaceagi:      [belt emoji + name]

  Belt criteria:
    White  = rung 641 achieved
    Yellow = rung 274177 achieved
    Orange = first skill in Stillwater Store
    Green  = rung 65537 achieved
    Black  = Models=commodities, Skills=capital, OAuth3=law

==================================================
SESSION START SEQUENCE (for new Claude Code session)
==================================================

1. /northstar       — load project NORTHSTAR
2. /remember        — check persistent memory
3. /status          — verify current state
4. /build [project] [phase]   — launch swarm

==================================================
```

## When user runs `/hub --metrics`

Show only the NORTHSTAR metrics table (actuals vs targets).
Read NORTHSTAR.md for targets. Read case-studies/ for actuals.

## When user runs `/hub --pricing`

Show only the pricing tiers + COGS model. No project status.

## When user runs `/hub --swarms`

Show only the next recommended swarm commands in copy-paste format:

```
NEXT SWARM COMMANDS (ranked by leverage):

1. /build [project] [phase]
   Why: [1 line reason]

2. /build [project] [phase]
   Why: [1 line reason]

3. /build [project] [phase]
   Why: [1 line reason]

Bash shortcuts:
  ./launch-swarm.sh [project] [phase]  # From /home/phuc/projects/stillwater/
```

## Related Commands

- `/status` — Detailed per-project status dashboard
- `/build [project] [phase]` — Launch a swarm build session
- `/northstar` — Load NORTHSTAR for current project
- `/remember` — View/update persistent memory
