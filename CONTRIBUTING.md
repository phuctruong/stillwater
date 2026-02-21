# Contributing to Stillwater

> "Absorb what is useful, discard what is useless, add what is essentially your own." — Bruce Lee

## Quick Links

| Contribution Type | Guide |
|---|---|
| Skills, recipes, swarm agents | [`community/CONTRIBUTING.md`](community/CONTRIBUTING.md) |
| Skill authoring | [`community/SKILL-AUTHORING-GUIDE.md`](community/SKILL-AUTHORING-GUIDE.md) |
| Recipe authoring | [`community/RECIPE-AUTHORING-GUIDE.md`](community/RECIPE-AUTHORING-GUIDE.md) |
| Swarm design | [`community/SWARM-DESIGN-GUIDE.md`](community/SWARM-DESIGN-GUIDE.md) |
| Papers | Follow existing structure in [`papers/`](papers/); see [`papers/00-index.md`](papers/00-index.md) |

## Code Contributions (tests, notebooks, CLI)

1. Fork and clone the repo
2. Install: `pip install -e .`
3. Run tests: `pytest imo/tests/ -x`
4. All skill/recipe/swarm changes must pass the appropriate verification rung (641 → 274177 → 65537)
5. Open a PR — reviewers will apply [`skills/prime-reviewer.md`](skills/prime-reviewer.md) discipline

## Verification Rungs

| Rung | Meaning | Required For |
|---|---|---|
| 641 | Local correctness (red/green gate + no regressions) | Any PR |
| 274177 | Stability (seed sweep + replay) | New skills/swarms |
| 65537 | Promotion (adversarial + security + drift explained) | Security-touching, API surface changes |

See [`papers/03-verification-ladder.md`](papers/03-verification-ladder.md) for the full ladder specification.
