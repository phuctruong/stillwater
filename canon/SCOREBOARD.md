# stillwater Scoreboard
<!-- Auth: 65537 | Tenant: stillwater | Law: LAI-13 Never-Worse | Date: 2026-05-19 -->

```
DNA: ratchet = monotonic_up × evidence_anchored × no_silent_demotion
```

## Day-0 baseline (2026-05-19)

This is the reset state at the moment Phase A of the stillwater brand-spawn seals (canon files authored + Firestore tenant created + bake script wired + brand-portfolio updated). Workers tick from here.

| Dimension | Floor (Day-0) | Target (90 days) | Target (12 months) |
|---|---|---|---|
| GitHub stars (`gh repo view phuctruong/stillwater`) | 6 | 25 | 100 |
| GitHub forks | 1 | 5 | 15 |
| External merged-PR contributors (not Phuc, not solaceagi twins) | 0 | 1 | 5 |
| Belt rung | Orange (Store) | Orange (sealed + extended) | Green (rung 274177) |
| Canon files in `~/projects/stillwater/canon/` | 6 (Day-0 batch) | 12 | 20 |
| Papers in `papers/` | 61 | 65 | 75 |
| Diagrams in `solace/diagrams/` (stillwater scope) | 10 | 12 | 18 |
| Skills published (canonical) | 37 | 40 | 50 |
| Recipes hitting ≥ 70% target rate | UNKNOWN — measure during Phase C | recipe-validation run | 30 / 34 |
| Tests in harness | 2,399 | 2,500 | 5,000 (adversarial corpus) |
| Public marketing domain | UNKNOWN (`(TBD)` in Firestore) | decided + DNS up | live + linked from solaceagi.com |
| Paying customers | 0 (OSS, by design) | 0 | 0 |

## Ratchet floors (LAI-13: monotonic up — never demote silently)

The following counts are the **Never-Worse** ratchet. Once they tick up, they do not move back down without an audit event written to `companies/stillwater/evidence/`.

| Ratchet | Floor at Day-0 | Notes |
|---|---|---|
| `github_stars` | 6 | Monotonic up. If GitHub shows a lower count due to user-deletions, that's a measurement event, not a regression — record it; floor stays. |
| `github_forks` | 1 | Same as above. |
| `external_contributors` (distinct GitHub usernames with ≥ 1 merged PR, excluding Phuc + bot accounts) | 0 | Append-only. Each new external contributor writes an evidence row. |
| `belt_rung` | Orange (Store) | Belt only ratchets up; no demotions without operator override + audit memo. |
| `canonical_skills_published` | 37 | New skills add. A removed skill writes a `selective_forgetting_evidence` row (LAI-6). |
| `tests_passing` | 2,399 | Test count only ratchets up. A test moved or deleted writes an evidence row. |

## Floor commitments (LAI-13)

- **No release sealed without `Purpose × Evidence × Love`** (LAI-23). Every Belt rung announcement names the beneficiary (the external operator forking the substrate, the SDK partner building on it, the researcher studying canon-update RSI).
- **Belt regressions are blocking.** If a new harness run lowers `tests_passing` or breaks a previously-sealed Belt rung, the release is held until the regression is explained, reversed, or escalated to an operator audit memo.
- **No silent partial sealing.** A skill / paper / recipe is either `proposed`, `canonical`, or `archived`. There is no `partial`. The substrate refuses partial states.
- **External-contributor growth is NOT bought.** No paid stars, no fake forks, no astroturf PRs. The count is honest or it's nothing.

## Day-0 template scoring (fills in as workers tick)

```
[ ] github_stars                    = 6   (floor; honest gh repo view 2026-05-19)
[ ] github_forks                    = 1   (floor; same source)
[ ] external_contributors           = 0
[ ] belt_rung                       = Orange (Store)
[ ] canon_files                     = 6 / 6  (this batch)
[ ] papers                          = 61 / 65 (12-mo target 75)
[ ] diagrams                        = 10 / 12
[ ] skills_canonical                = 37 / 40
[ ] recipes_hit_rate                = UNKNOWN / 30 of 34 target
[ ] tests_passing                   = 2,399 / 2,500
[ ] marketing_domain                = UNKNOWN
[ ] never_worse_ratchet_armed       = YES (6,1,0,Orange,37,2399)
[ ] firestore_tenant_doc            = pending Phase A seal
[ ] brand_portfolio_row_updated     = pending Phase A seal
[ ] bake_script_REPO_PATHS_wired    = pending Phase A seal
```

## Verification commands (when scoring updates)

```bash
# honest github stats (used for ratchet)
gh repo view phuctruong/stillwater --json stargazerCount,forkCount

# external contributors (excluding Phuc + bots)
gh api repos/phuctruong/stillwater/contributors | \
  jq -r '.[] | select(.login != "phuctruong" and (.type != "Bot")) | .login'

# firestore tenant doc exists
python3 -c "
from google.cloud import firestore
db = firestore.Client(project='solace-461818')
doc = db.collection('companies').document('stillwater').get()
print('exists:', doc.exists)
if doc.exists:
    d = doc.to_dict()
    print('  parent_company:', d.get('parent_company'))
    print('  vertical:', d.get('vertical'))
    print('  tier:', d.get('tier'))
"

# belt rung sealed
grep -E '^\| (Yellow|Orange|Green|Blue|Black)' ~/projects/stillwater/README.md
```

## What does NOT count toward the scoreboard

- **Star purchases / fork purchases** — explicit zero-tolerance per the Day-0 honesty discipline.
- **PRs by Phuc himself** — Phuc is the maintainer; his merges do not advance `external_contributors`.
- **PRs by solaceagi.com-side twins / bots** — those are first-party, not external.
- **Tracking pixel hits / analytics** — substrate has no telemetry by design.
- **Press mentions / podcast appearances** — interesting, but not load-bearing for substrate adoption.

## Honest-unknowns ledger

| Item | Day-0 status | Resolver |
|---|---|---|
| Recipe hit-rate against ≥ 70% target | UNKNOWN — needs measurement run | Phase C deliverable |
| Public marketing domain | UNKNOWN — `(TBD)` flag in Firestore | operator |
| External contributors count | 0 (floor) | grows via Phase B onramp |
