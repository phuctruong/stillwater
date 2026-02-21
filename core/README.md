# core/ — Always-On Skill Copies

**Purpose:** Always-on skill copies — authoritative versions live in `skills/`

This directory contains copies of the 4 always-on skills loaded by every agent run.
These copies exist here for portability (no symlinks; works on Windows/Linux/macOS).
Do not edit files in this directory directly; make changes upstream in `skills/` instead.

---

## Load Order

| Load Order | Skill | Notes |
|---|---|---|
| 1 | prime-safety.md | god-skill; wins all conflicts; always loaded |
| 2 | prime-coder.md | evidence discipline + red/green gate; always loaded |
| 3 | phuc-forecast.md | planning loop (DREAM→FORECAST→DECIDE→ACT→VERIFY); **optional in lean configurations** |
| 4 | phuc-context.md | context hygiene + orchestration substrate; **optional in lean configurations** |

`phuc-forecast` is load-order 3 (optional in lean configurations).
`phuc-context` is load-order 4 (optional in lean configurations).

---

## SHA256 Baseline Table

The SHA256 values below are of the **copy files** in `core/` (which include the header comment).
The `SHA256-AT-COPY` values embedded in each file's header are the sha256 of the **source** in `skills/` at the time of copy.

| Skill | Source Path | SHA256-at-copy (source) | SHA256 of core/ copy |
|---|---|---|---|
| prime-safety | skills/prime-safety.md | `49ed791516d7719231b13a1d8340accc5ffc186d3d68efe91c8729b5ab76f5d2` | `0670a223a6e4939687c7cf56a0f6038ab4c4f0d3a08ffa1f49dce5b5adf4fc1f` |
| prime-coder | skills/prime-coder.md | `b3c39bb8a0d580518768d4e97bc585516ac5a7172873a151103b4e2dd4ba55dc` | `f50891a51ee8459ec4850c570674e94356915781421eae7a854fed687764bf9c` |
| phuc-forecast | skills/phuc-forecast.md | `f121669338aa04a09449395b2048a3d3cca9e77a4ce74622dd4e57fd10d90be2` | `af21a17fca1c7e39c4d24e887a1fbf32cdcf1d5f226ce6b9509847e2a3c0c5a3` |
| phuc-context | skills/phuc-context.md | `531dc0e8a9897d98b7dbe19470406499f178456b5901301c4f705549b6091b7d` | `54bd3bb60330a889110e69371da18b8a2830beda19bc03ad1876df4ffc0cca37` |

---

## Divergence Policy

If these copies diverge from `skills/`, the `skills/` version wins.

Run `sha256sum` to detect drift:

```bash
# Check source files match SHA256-at-copy values recorded above
sha256sum skills/prime-safety.md skills/prime-coder.md skills/phuc-forecast.md skills/phuc-context.md

# Check copy files match SHA256 of core/ copy values recorded above
sha256sum core/prime-safety.md core/prime-coder.md core/phuc-forecast.md core/phuc-context.md
```

If drift is detected, re-copy from `skills/` and update this README's SHA256 baseline table.

---

## Files in this directory

- `README.md` — this file (drift detection baselines + policy)
- `prime-safety.md` — copy of `skills/prime-safety.md`
- `prime-coder.md` — copy of `skills/prime-coder.md`
- `phuc-forecast.md` — copy of `skills/phuc-forecast.md`
- `phuc-context.md` — copy of `skills/phuc-context.md`
