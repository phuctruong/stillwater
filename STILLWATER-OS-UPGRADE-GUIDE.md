# Stillwater OS Upgrade Guide

> "Knowing is not enough, we must apply."

**Last updated:** 2026-02-21 | Stillwater v1.5.0

---

## TL;DR — The 30-Second Upgrade

```bash
pip install stillwater
cd ~/projects/your-project

stillwater init project \
  --name "Your Project" \
  --skills prime-safety,prime-coder,phuc-forecast \
  --rung 641 \
  --domain "your domain" \
  --force
```

This replaces a 793–1,692-line CLAUDE.md with a lean 44–71-line version and creates `ripples/project.md` + `skills/` for sub-agent dispatch. **Done in 30 seconds.**

---

## 1) The Problem This Solves

### Before (anti-pattern)

Every project had a monolithic CLAUDE.md:

| Project | CLAUDE.md Lines | Actually Project-Specific |
|---|---|---|
| pzip | 793 | ~50 lines |
| paudio | 1,113 | ~60 lines |
| pvideo | 816 | ~50 lines |
| solace-browser | 1,692 | ~80 lines |
| **Total** | **5,366** | **~280 lines** |

**93% was copy-pasted Stillwater skill content.** Every copy was potentially stale.

### After (`stillwater init project`)

| Project | CLAUDE.md Lines | Reduction |
|---|---|---|
| pzip | 66 | 92% ↓ |
| paudio | 66 | 94% ↓ |
| pvideo | 66 | 92% ↓ |
| solaceagi | 66 | 81% ↓ |
| solace-browser | 60 | 96% ↓ |
| solace-cli | 71 | 88% ↓ |
| if | 55 | (new) |
| phucnet | 44 | (new) |

Total context across 8 projects: **494 lines** vs former 5,366. 91% reduction.
Skills are always current (copied from installed package on each `stillwater sync`).

---

## 2) Three-File Architecture (OOP Model)

```
# Before: Inheritance by copy-paste (BAD)
class PZipClaudeMd:
    prime_safety  = "...(200 lines, copy-pasted, might be stale)..."
    prime_coder   = "...(300 lines, copy-pasted, might be stale)..."
    project_stuff = "Beat LZMA..."  # the only part that should be here

# After: Real inheritance (GOOD)
class PZipClaudeMd(StillwaterBase):  # skills loaded from package
    ripple = load("ripples/project.md")  # only the delta — 30 lines
```

**CLAUDE.md** (44–71 lines): QUICK LOAD skill summaries only + `SEE_ALSO: README.md`

**ripples/project.md** (≤50 lines): Domain, rung target, key constraints, entry points, forbidden behaviors. The only file you edit per project.

**skills/** directory: Full skill files for sub-agent dispatch (copied from stillwater package). Never edited — updated by `stillwater sync`.

**README.md**: Project identity, mission, architecture, phases. Everything that used to be in CLAUDE.md.

See full recipe: [`recipes/project-onboard.md`](recipes/project-onboard.md)

---

## 3) Per-Project Skill Packs (Phuc.Net Ecosystem)

| Project | Skills | Rung | Notes |
|---|---|---|---|
| **pzip** | prime-safety, prime-coder, prime-math, phuc-forecast | 65537 | Compression + exact arithmetic |
| **paudio** | prime-safety, prime-coder, prime-math, phuc-forecast | 274177 | Deterministic synthesis |
| **pvideo** | prime-safety, prime-coder, prime-math, phuc-forecast | 65537 | IF Theory physics |
| **solaceagi** | prime-safety, prime-coder, phuc-orchestration, phuc-forecast | 65537 | Persistent AGI |
| **solace-browser** | prime-safety, prime-wishes, phuc-cleanup | 641 | Web automation |
| **solace-cli** | prime-safety, prime-coder, phuc-orchestration, phuc-context | 65537 | Memory hub |
| **if** | prime-safety, prime-coder, prime-math | 274177 | Physics simulation |
| **phucnet** | prime-safety, phuc-cleanup | 641 | Content publishing |

**Skill selection principles (learned from upgrading 8 projects):**
- Always include `prime-safety` first (god-skill; wins all conflicts)
- Add `prime-math` for projects with any arithmetic/scientific computation (pzip, paudio, pvideo, if)
- Add `phuc-orchestration` for projects that dispatch sub-agents (solaceagi, solace-cli)
- Add `phuc-context` for projects with long multi-session state (solace-cli)
- Add `phuc-cleanup` instead of prime-coder for pure content/cleanup workflows (phucnet, solace-browser)
- Add `prime-wishes` for backlog/task management workflows (solace-browser)

---

## 4) Quick Commands

### Install Stillwater into a new project

```bash
cd ~/projects/your-project
stillwater init project \
  --name "Your Project" \
  --skills prime-safety,prime-coder,phuc-forecast \
  --rung 641 \
  --domain "your domain description" \
  --force
```

### Sync skills after a Stillwater update

```bash
pip install --upgrade stillwater

# In each project:
stillwater sync              # updates skills/ from installed package
stillwater sync --check      # dry-run: shows what would change
```

### Verify project structure (v1.6.0)

```bash
stillwater verify-project-structure  # coming in v1.6.0
```

Manual checklist (until v1.6.0):

```bash
wc -l CLAUDE.md                  # should be < 150 lines
ls skills/                       # should have at minimum prime-safety.md
cat ripples/project.md           # should have rung_target, domain, constraints
```

---

## 5) Filling in ripples/project.md (The Key Step)

After `stillwater init project` runs, fill in the template:

```yaml
PROJECT: YourProject
DOMAIN: your domain (1 line)
RUNG_TARGET: 641  # or 274177 or 65537

KEY_CONSTRAINTS:
  - never-worse on standard test suite
  - [project-specific constraint 1]
  - [project-specific constraint 2]

ENTRY_POINTS:
  - src/yourproject/main.py
  - pytest -q tests/

FORBIDDEN_IN_THIS_PROJECT:
  - [anything specific to never do in this project]

SEE_ALSO: README.md  # architecture, mission, phases
```

**What goes here:** Only project-specific overrides to Stillwater's base behavior.
**What does NOT go here:** Skill content, architecture diagrams, phase trackers (those go in README.md).

---

## 6) Rung Target Selection Guide

| Rung | When to Use | Evidence Required |
|---|---|---|
| **641** | Content projects, cleanup, scripts, web automation | Tests pass, no regressions, evidence complete |
| **274177** | Stable APIs, audio/video synthesis, scientific computation | + seed sweep (3+), replay stability, null edge cases |
| **65537** | Promotion claims, universal compression, persistent AGI, public benchmarks | + adversarial sweep, security gate, behavioral hash drift explained |

**Rule:** Pick the rung that matches your project's most demanding verifiable claim.
Over-claiming a rung is a forbidden state. Under-claiming wastes evidence budget.

---

## 7) A/B Test Protocol (Proving Skill Impact)

Run the same coding task with and without skills loaded:

1. **Baseline:** No Stillwater skills. Record: time-to-green, defect count, test pass rate, rework loops.
2. **Skill run:** Inject `prime-coder.md` (+ `prime-safety.md`). Same task. Same acceptance tests.
3. **Compare with evidence.** Keep receipts for both arms.

The A/B benchmark harness:

```bash
STILLWATER_AB_BACKEND=mock stillwater skills-ab --backend mock
```

---

## 8) Lessons from the 8-Project Upgrade (2026-02-21)

**What worked:**
- `stillwater init project --force` on an existing project is safe: it creates new files, does not delete anything
- QUICK LOAD blocks in CLAUDE.md are small enough (10-15 lines per skill) to be valuable without bloat
- ripples/project.md is the right home for project-specific constraints — Claude reads it and applies it immediately
- The `skills/` directory for sub-agent dispatch is the missing piece that makes phuc-orchestration work

**What to watch for:**
- The ECOSYSTEM field defaults to PUBLIC — set to PRIVATE for internal projects (solaceagi, solace-browser, solace-cli)
- Entry points vary by project — don't leave them as `# e.g.` stubs; fill them in immediately
- Rung targets in old CLAUDE.md sometimes reflected aspirational goals, not current state — be honest when filling in ripples/project.md
- Some projects (solace-browser) need `prime-wishes` instead of `prime-coder` — match skills to actual workflow

**Insight from context reduction:**
CLAUDE.md bloat directly costs you context window. A 1,692-line CLAUDE.md (solace-browser) consumed ~1,200 lines of context just for skills that could be loaded on demand. The 60-line version puts that context back into actual work.

---

## 9) Done Criteria (Rung 641 Checklist)

Per [`recipes/project-onboard.md`](recipes/project-onboard.md):

- [ ] `wc -l CLAUDE.md` < 150 lines
- [ ] `ripples/project.md` exists with rung_target, domain, key_constraints filled in (not stubs)
- [ ] `skills/` directory has at minimum prime-safety.md and one domain skill
- [ ] `README.md` has mission, architecture, quick start
- [ ] CLAUDE.md references README.md for project context
- [ ] CLAUDE.md contains QUICK LOAD blocks for each skill (not full content)
- [ ] No project-specific architecture prose inside CLAUDE.md
- [ ] ECOSYSTEM field correct (PUBLIC vs PRIVATE)
- [ ] ENTRY_POINTS filled in (not stub comments)
