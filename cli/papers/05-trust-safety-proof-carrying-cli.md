# Trust, Safety, And Proof-Carrying CLI

## Thesis

Trust must be earned per run:
- deterministic checks
- explicit receipts
- replayable verification

No "trust me" path.

## Safety Model

1. CPU prepass handles deterministic queries and controls.
2. LLM output is treated as candidate, not proof.
3. Gates and tests decide promotion/deployment.

## Receipts And Replay

Artifacts:
- `artifacts/twin/<run_id>/route.json`
- `artifacts/twin/<run_id>/twin.mmd`
- `artifacts/twin/<run_id>/twin.sha256`
- `artifacts/runs/<run_id>/manifest.json`
- `artifacts/oolong/<run_id>/results.json`

Commands:
- `stillwater stack run --profile offline`
- `stillwater stack verify --strict`
- `stillwater replay <run_id>`
- `stillwater oolong run`
- `stillwater oolong verify --strict`

## Hardening Policy

1. Fail closed on missing evidence.
2. Separate confidence from correctness.
3. Require deterministic witnesses for promotion.
4. Keep high-risk operations behind explicit gates.
