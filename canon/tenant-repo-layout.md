# Tenant Repo Layout — Canonical Standard

**Sealed:** 2026-05-14 by Phuc Forecast
**Authorization:** 65537
**Anchor:** LEI-2 (universal convention), LAI-22 (diagram-first)
**Audience:** every tenant repo (`metalmark`, `gatan`, `maxsalesgroup`, future)

## Why this exists

Without a standard, every tenant repo drifts: `simplemdg` has a `canon/init` dir for one thing, `metalmark` uses `canon/specs/sissi/` for the same purpose, `gatan` uses `canon/init/` for PDFs. Workers reading the context-DB at runtime have to handle every variant — costly and error-prone. This doc locks the layout.

## The contract

```
~/projects/{tenant}/                  ← repo root
│
├── CLAUDE.md                         ← claude-code orientation (dual mode: GM + SDK)
├── CLAUDE-CODE-SETUP.md              ← optional: Day-1 walkthrough for operator
├── README.md                         ← human-readable repo description
├── NORTHSTAR.md                      ← OPTIONAL: top-level pointer (alias for canon/NORTHSTAR.md)
├── ROADMAP.md                        ← OPTIONAL: top-level pointer
├── SCOREBOARD.md                     ← OPTIONAL: top-level pointer
│
├── canon/                            ← LAYER 1: project specs (workers READ this)
│   ├── init/                         ← RESERVED — client-provided starter docs ONLY
│   │   └── *.pdf, *.docx, *.md       ← never edited; only added by operator
│   ├── NORTHSTAR.md                  ← mission + products + buyer + 12-month goals
│   ├── ROADMAP.md                    ← phased plan with measurable success criteria
│   ├── SCOREBOARD.md                 ← LAI-13 ratchet floors + current state
│   ├── company-information.md        ← context every worker should know
│   ├── operations-playbook.md        ← OPTIONAL: how the business actually runs
│   ├── product-catalog.md            ← OPTIONAL: per-product detail (if product-centric)
│   ├── INDEX.md                      ← table of contents for the directory
│   ├── tenant-repo-layout.md         ← this file (mirrored to every tenant)
│   ├── custom-collections.md         ← SDK doc for partner-defined collections
│   ├── sdk-improvements.md           ← SDK dev-loop reference
│   ├── build-a-worker.md             ← SDK recipe (mirrored from simplemdg)
│   ├── build-a-domain-app.md         ← SDK recipe
│   ├── abcd-harness.md               ← ABCD test pattern reference
│   ├── master-equation.md            ← LAI-23 framing
│   ├── inbox-outbox.md               ← LAI-5 filesystem API
│   ├── convention-lifecycle.md       ← LAI-2 promotion flow
│   ├── deployment-and-rollback.md    ← ops reference
│   ├── developer-onboarding.md       ← SDK dev onboarding
│   ├── support-and-sla.md            ← optional support model
│   ├── security-and-compliance.md    ← optional sec/compliance
│   ├── testing-and-qa.md             ← testing reference
│   ├── prime-mermaid.md              ← diagram-first reference
│   ├── thermodynamic-circuit.md      ← optional theory ref
│   ├── triangle.md                   ← optional ICP framework
│   ├── uplifts.md                    ← worker uplift recipes
│   ├── worker-design-patterns.md     ← reference patterns
│   ├── horizontal-civilization.md    ← biz-model reference
│   ├── fallback-ban.md               ← guardrail reference
│   ├── leak-lec.md                   ← evidence chain reference
│   ├── partner-playbook.md           ← optional partner ops
│   ├── prospector-pattern.md         ← outreach pattern reference
│   ├── consultant-onboarding.md      ← consultant flow
│   ├── specs/                        ← OPTIONAL: detailed specs / RFCs
│   ├── personas/                     ← OPTIONAL: per-tenant personas
│   ├── policies/                     ← OPTIONAL: tenant-specific guardrails
│   └── training/                     ← OPTIONAL: snapshot bundle (gitignored — large)
│
├── solace/                           ← LAYER 2/3: runtime context + worker definitions
│   ├── STANDARD.md                   ← tenant-specific slice of solace-hub/solace/STANDARD.md
│   ├── profile.json                  ← per-tenant worker_email_overrides + twin config
│   │
│   ├── workers/                      ← LAYER 3: editable worker overrides (Tier-1 only)
│   │   ├── README.md                 ← which workers are editable + override model
│   │   └── {wid}/                    ← one dir per editable worker
│   │       ├── manifest.prime-mermaid.md
│   │       ├── instructions.md
│   │       ├── SOUL.md
│   │       ├── MEMORY.md
│   │       ├── skills.yaml
│   │       ├── conventions/          ← runtime-learned rules (empty scaffold)
│   │       ├── inbox/                ← pending assignments (empty scaffold)
│   │       ├── outbox/               ← sealed evidence (empty scaffold)
│   │       └── journal/              ← chain-of-custody log (empty scaffold)
│   │
│   ├── diagrams/                     ← PM diagrams (LAI-22 — source of truth)
│   │   ├── company.prime-mermaid.md          ← PM root: products × customers × channels
│   │   ├── first-principles.prime-mermaid.md ← 5-6 tenant primitives
│   │   └── *.prime-mermaid.md                ← additional feature/system diagrams
│   │
│   ├── wiki/                         ← per-tenant wiki pages (syncs to wiki_pages)
│   │   └── *.md                      ← one file per page
│   │
│   ├── modules/                      ← per-tenant SaaS module wikis (syncs to saas_modules)
│   │   └── *.md                      ← one file per module
│   │
│   ├── apps/                         ← domain apps for Solace Browser (no Chromium rebuild)
│   │   └── {app_id}/
│   │       ├── manifest.yaml
│   │       ├── prompt.md             ← OPTIONAL: if managed-LLM
│   │       └── README.md             ← OPTIONAL
│   │
│   ├── conventions/                  ← OPTIONAL: tenant-wide promoted conventions
│   │
│   └── site/                         ← OPTIONAL: public website
│       ├── public/                   ← baked HTML + styles.css (from bake_website_to_static.py)
│       └── styles.css
│
├── evals/                            ← ABCD test cases
│   └── eval_<wid>_<n>q.json          ← one file per worker × 4-16 cases
│
├── scripts/                          ← SDK tooling (mirrored from simplemdg template)
│   ├── devkit-init.sh                ← bootstrap ~/.solace/devkit.env
│   ├── lint.sh                       ← repo-wide lint
│   ├── refresh-canon.sh              ← pull canon updates from platform
│   ├── run-abcd.sh                   ← ABCD test runner (--via ollama | cloud)
│   ├── run-worker-local.sh           ← single-action dry-run
│   ├── solace-sync.sh                ← PUT all kinds to companies/{co}/*
│   └── solace-promote.sh             ← admin: promote tenant content → canonical
│
├── scratch/                          ← local-only work, GITIGNORED
│   ├── abcd/                         ← eval run outputs
│   └── dryrun/                       ← run-worker-local outputs
│
├── app/                              ← OPTIONAL: public-site shell (FastAPI/Flask)
│   └── server.py
│
├── deploy/                           ← OPTIONAL: deploy config
│   └── Dockerfile
│
├── cloudbuild.yaml                   ← OPTIONAL: qa branch → Cloud Run
│
└── .gitignore                        ← excludes scratch/, .solace/, build artifacts
```

## RESERVED paths (don't put other things here)

| Path | What goes here | What doesn't |
|---|---|---|
| `canon/init/` | Client-provided source documents (PDFs, DOCX, decks, contracts). Operator drops files here at onboarding. | Authored canon, auto-generated content, anything not from the client directly. |
| `solace/workers/{wid}/inbox/` | Runtime: pending action assignments | Anything the operator authors |
| `solace/workers/{wid}/outbox/` | Runtime: sealed evidence after each run | Anything the operator authors |
| `solace/workers/{wid}/conventions/` | Runtime: rules learned from feedback | Initial seeded rules (those go in `canon/`) |
| `scratch/` | Local-only experiment output | Anything committed to git |

## FORBIDDEN states (auto-rejected by `solace-sync.sh` or the cloud gate)

| State | Trigger | Cost |
|---|---|---|
| `CODE_IN_SOLACE` | `.py`/`.js`/`.cpp`/`.rs`/`.go`/`.sh` under `solace/` | KILL |
| `PY_CACHE_IN_SOLACE` | `__pycache__/` anywhere under `solace/` | KILL |
| `WORKER_MIRROR` | worker_id under `solace/workers/` that ALSO exists in `~/projects/solace-agent/solace/workers/` with same body | WARN — should be tenant override only |
| `STARTER_DOCS_OUTSIDE_INIT` | `*.pdf`/`*.docx` anywhere in `canon/` except `canon/init/` | KILL — move to canon/init/ |
| `MERMAID_SYNTAX_ERROR` | `.md` with invalid `\`\`\`mermaid` block | 400 from cloud gate |

## What gets synced where

```
canon/*.md (top-level)        →  companies/{co}/canon/<slug>          via solace-sync.sh --only canon
                                  AND companies/{co}/wiki_pages         via sync_canon_to_wiki.py
canon/init/*                  →  NEVER synced (gitignored from cloud sync; lives in git for archival)
solace/workers/{wid}/         →  companies/{co}/workers/{wid}          via solace-sync.sh --only workers
solace/apps/{aid}/            →  companies/{co}/apps/{aid}             via solace-sync.sh --only apps
solace/diagrams/*.prime-mermaid.md → companies/{co}/diagrams/<slug>    via solace-sync.sh --only diagrams
solace/wiki/*.md              →  companies/{co}/wiki_pages/<slug>      via solace-sync.sh --only wiki
solace/modules/*.md           →  companies/{co}/saas_modules/<mid>     via solace-sync.sh --only saas_modules
evals/                        →  NEVER synced (local test artifacts)
scripts/                      →  NEVER synced (local tooling)
scratch/                      →  NEVER synced + gitignored
```

## Bootstrap a new tenant (the script does this for you)

```bash
# 1. Create repo
mkdir -p ~/projects/{tenant} && cd ~/projects/{tenant}
git init && gh repo create phuctruong/{tenant} --private --source=.

# 2. Drop client-provided docs (PDFs, DOCX, deck exports) into:
mkdir -p canon/init
cp ~/Downloads/their-deck.pdf canon/init/
cp ~/Downloads/their-northstar.docx canon/init/

# 3. Scaffold from this standard
~/projects/solace-hub/scripts/bootstrap-tenant.sh {tenant}
# (this script reads tenant-repo-layout.md and creates the directory tree)

# 4. Phase 1 — Wiki Absorption (claude-code reads canon/init/ + authors canon/*.md)
claude .

# 5. Phase 2-6 — follow the canonical onboarding flow
# See: ~/projects/solace-agi/solace/diagrams/customer-onboarding.prime-mermaid.md
```

## When you find drift

A repo violating this standard is one of:
- **Legacy** — predates this doc (2026-05-14). File a cleanup task; tolerate it short-term.
- **Bug** — operator put a thing in the wrong place. Move it; update lint.sh to catch the case.
- **Better idea** — operator found a layout improvement. Update THIS DOC first (LAI-22 diagram-first), then propagate.

This doc is the source of truth. Tenant repos copy it.
