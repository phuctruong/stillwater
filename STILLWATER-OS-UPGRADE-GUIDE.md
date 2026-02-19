# Stillwater OS Upgrade Guide

> "Knowing is not enough, we must apply."

Date: 2026-02-19  
Goal: use Stillwater as a drop-in upgrade layer for an existing CLI/agent project (example: `~/projects/solace-cli`).

## 1) What This Guide Delivers

1. Sync Stillwater skill pack into a target repo.
2. Clean glow clutter with archive receipts (not blind deletion).
3. Preserve suspicious files until explicit approval.
4. Establish an A/B test loop to prove gains with and without skills.

## 2) Baseline Assumptions

1. Stillwater repo is available at `~/projects/stillwater`.
2. Target repo is available at `~/projects/solace-cli` (or equivalent).
3. Target CLI includes the `stillwater` command surface:
   - `stillwater doctor`
   - `stillwater sync-skills`
   - `stillwater cleanup-scan`
   - `stillwater cleanup-apply`

## 3) Apply to Solace CLI

From `~/projects/solace-cli`:

```bash
python3 -m solace_cli.cli.entry stillwater doctor
python3 -m solace_cli.cli.entry stillwater sync-skills --dest solace_cli/skills/stillwater
python3 -m solace_cli.cli.entry stillwater cleanup-scan
python3 -m solace_cli.cli.entry stillwater cleanup-apply --approve-safe
```

Optional tracked-file cleanup (explicit):

```bash
python3 -m solace_cli.cli.entry stillwater cleanup-apply --approve-safe --include-tracked-safe
```

Suspicious-file action (explicit, manual review first):

```bash
python3 -m solace_cli.cli.entry stillwater cleanup-apply --approve-suspicious
```

## 4) Approval Policy

1. Safe, untracked glow files: archive with `--approve-safe`.
2. Safe, tracked files: require `--include-tracked-safe`.
3. Suspicious files (from `FINAL-AUDIT.md`): require `--approve-suspicious`.
4. Always review generated receipts before broadening scope.

## 5) Receipt Artifacts

The process writes machine-readable receipts:

1. `artifacts/stillwater/sync-skills/*.json`
2. `artifacts/stillwater/cleanup-scan/*.json`
3. `artifacts/stillwater/cleanup-apply/*.json`
4. Archived files under `.archive/glow/<timestamp>/...`

## 6) A/B Test Protocol (Skills Impact)

1. Run a fixed coding task without injected Stillwater skills.
2. Run the same task with `prime-coder.md` (+ optional `prime-safety.md`).
3. Compare:
   - time-to-green
   - defect count
   - test pass rate
   - rework loops
4. Keep receipts for both arms; decide from evidence, not slogans.

## 7) Minimum Integration Pack

For fast adoption, sync these first:

1. `prime-coder.md`
2. `prime-math.md`
3. `prime-safety.md`
4. `phuc-cleanup.md`

Then expand to:

1. `phuc-context.md`
2. `phuc-forecast.md`
3. `phuc-swarms.md`

## 8) Done Criteria

1. Skill files synced into target repo.
2. Cleanup scan + apply receipts exist.
3. Glow clutter moved to archive, not deleted.
4. Suspicious files untouched unless explicitly approved.
5. One completed A/B result with evidence bundle.
