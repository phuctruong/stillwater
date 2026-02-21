# Stillwater Skills and the SKILL.md Standard

## Overview

The Claude Code ecosystem uses a `SKILL.md` format: a markdown file with YAML
frontmatter that Claude Code can auto-discover from `~/.claude/skills/`.
Stillwater skills are fully compatible with this format — they are plain
markdown files that can be wrapped in the required frontmatter with one
command.

## How Stillwater Skills Relate to the SKILL.md Standard

| Feature | SKILL.md (Claude Code) | Stillwater Skill |
|---------|----------------------|-----------------|
| YAML frontmatter (`name`, `description`, `version`, `author`, `tags`) | Required | Added on export |
| Plain markdown body | Yes | Yes |
| Loaded into LLM context | Yes | Yes |
| Finite state machine (FSM) | Not specified | Embedded in skill body |
| Forbidden states | Not specified | Embedded in skill body |
| Verification ladder (rungs 641/274177/65537) | Not specified | Embedded in skill body |
| Evidence contract | Not specified | Embedded in skill body |
| Red/green gate (Kent TDD) | Not specified | Embedded in skill body |
| Fail-closed behavior | Not specified | Core constraint |

**In short:** every Stillwater skill is a valid SKILL.md file once you add the
YAML frontmatter. The additional FSM, forbidden states, and verification ladder
are layered on top of the base SKILL.md standard — they do not conflict with
it. The stricter wins (per the layering rule in `prime-coder.md`).

## Exporting a Stillwater Skill as SKILL.md

Use the `stillwater skills export` command:

```bash
# Export to stdout
stillwater skills export prime-coder

# Export to a file
stillwater skills export prime-coder --output ~/.claude/skills/prime-coder.md

# Export and install (Claude Code auto-discovery path)
stillwater skills install prime-coder
# This writes to ~/.claude/skills/prime-coder.md automatically.
```

The `install` command is equivalent to `export --output ~/.claude/skills/<name>.md`
and also saves a copy to the local `skills/` directory.

## The SKILL.md Frontmatter Format

When exported, a Stillwater skill gains this YAML frontmatter:

```yaml
---
name: <skill-name>
description: Stillwater skill — <skill-name> (FSM-verified, fail-closed)
version: <version extracted from skill body, or 1.0.0>
author: Phuc Vinh Truong <phuc@phuc.net>
tags: [stillwater, verification, prime-coder]
---

<original skill content here>
```

Claude Code reads this frontmatter to index the skill by `name` and
`description`. The `tags` field allows filtering in skill management UIs.

## Differences at a Glance

Stillwater adds the following on top of the SKILL.md base:

1. **Closed State Machine (FSM)** — explicit states, transitions, and
   forbidden states that prevent silent failures or hallucinated claims.

2. **Verification Ladder** — three rungs of evidence quality:
   - Rung 641: local correctness (red/green gate + no regressions)
   - Rung 274177: stability (seed sweep + replay)
   - Rung 65537: promotion (adversarial sweep + security gate + drift explained)

3. **Evidence Contract** — every PASS must produce a machine-parseable
   evidence bundle with SHA-256 checksums. No claim without receipts.

4. **Red/Green Gate** — for bugfix tasks, the bug must be reproduced (red)
   before patching, and the fix must be verified (green) after patching.

5. **Fail-Closed Defaults** — if inputs are missing or ambiguous, the skill
   returns `status: NEED_INFO` or `status: BLOCKED` rather than guessing.

6. **Null vs Zero Distinction** — explicit null checks; no implicit defaults
   that coerce `null` to `0`.

These additions are purely additive. A SKILL.md-compatible reader that ignores
the Stillwater FSM/verification content will still load the skill correctly —
it will just treat the FSM and verification sections as rich skill documentation
rather than as executable constraints.

## Auto-Discovery by Claude Code

When you run `stillwater skills install <name>`, the skill is written to:

```
~/.claude/skills/<name>.md
```

Claude Code scans this directory on startup and makes the skill available
for slash commands and context injection. No additional configuration required.

## Authoring a New Skill

To create a new Stillwater-compatible skill:

1. Write your skill as a markdown file in `skills/<name>.md`.
2. (Optional) Add a `version:` key anywhere in the body for version tracking.
3. Run `stillwater skills install <name>` to deploy it.
4. Verify with `stillwater skills list` that it appears.
5. Test with `stillwater run "your task" --skill <name> --dry-run`.

For the full authoring guide, see [community/SKILL-AUTHORING-GUIDE.md](../community/SKILL-AUTHORING-GUIDE.md)
(if present) or the skills in `skills/` as examples.
