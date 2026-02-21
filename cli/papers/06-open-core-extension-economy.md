# Open Core, Private Edge

## Thesis

Stillwater CLI can be the open reference kernel.  
Project-specific edge can remain private in extension packs.

This is the practical path for:
- open ecosystem growth
- enterprise customization
- trade-secret preservation

## Architecture

- Open kernel:
  - `cli/src/stillwater/`
  - reproducible tests and notebooks
- Extension overlays:
  - skills, recipes, persona, identity, splash
  - configured by kernel config + env vars

## Solace-CLI As Reference Extension

Use `~/projects/solace-cli/stillwater_extension/` as a concrete private overlay:
1. keep kernel stable in stillwater
2. iterate faster in extension files
3. upstream only what should be public

## Marketplace Direction

Software 5.0 package model (future):
1. skill packs
2. recipe packs
3. persona packs
4. policy packs
5. benchmark proof packs

Install/update model should mirror package ecosystems (pip/npm extensions), while retaining deterministic verification requirements.
