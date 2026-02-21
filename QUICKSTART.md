# Stillwater — Quickstart (< 5 minutes)

> "Absorb what is useful, discard what is useless, and add what is specifically your own." — Bruce Lee

## 1. Clone and install

```bash
git clone https://github.com/phuctruong/stillwater
cd stillwater
pip install -e ".[dev]"
```

## 2. Run your first task

```bash
# Dry run (no LLM needed)
stillwater run "What is Software 5.0?" --dry-run

# With a skill loaded
stillwater run "Audit this code for null/zero issues" --skill prime-coder --dry-run

# With a real LLM (set API key first)
export ANTHROPIC_API_KEY=your-key-here
stillwater run "Summarize the skills directory" --skill prime-safety
```

The `run` command writes artifacts to `artifacts/runs/<run-id>/manifest.json`.
Use `--json` for machine-readable output.

## 3. Browse skills

```bash
stillwater skills list          # list all skills
stillwater skills show prime-coder  # show a skill
```

## 4. Run the A/B benchmark

```bash
# No API key needed — runs against mock backend
STILLWATER_AB_BACKEND=mock stillwater skills-ab --backend mock
```

## 5. Launch the admin UI

```bash
bash admin/start-admin.sh
# Opens http://127.0.0.1:8787 in your browser
```

## 6. Install Stillwater into your own project

```bash
cd ~/projects/your-project
stillwater init project \
  --name "Your Project" \
  --skills prime-safety,prime-coder,phuc-forecast \
  --rung 641 \
  --domain "your project domain" \
  --force
```

This replaces a bloated CLAUDE.md with a lean 44–71-line version and creates:
- `ripples/project.md` — fill in your project-specific constraints
- `skills/` — full skill files for sub-agent dispatch

See [`STILLWATER-OS-UPGRADE-GUIDE.md`](STILLWATER-OS-UPGRADE-GUIDE.md) for the full upgrade guide including per-project skill pack recommendations and a 91% context reduction case study.

See [`recipes/project-onboard.md`](recipes/project-onboard.md) for the canonical recipe and verification checklist.

## Next steps

- Read [`STILLWATER-OS-UPGRADE-GUIDE.md`](STILLWATER-OS-UPGRADE-GUIDE.md) to upgrade your existing projects
- Read [`cli/README.md`](cli/README.md) for the full CLI manual
- Browse [`skills/`](skills/) for available skills
- Browse [`recipes/`](recipes/) for repeatable workflows
- Read [`papers/05-software-5.0.md`](papers/05-software-5.0.md) for the theory
- Read [`MESSAGE-TO-HUMANITY.md`](MESSAGE-TO-HUMANITY.md) for the mission
