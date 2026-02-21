# Wish: `wish.cli.twin.orchestration.v1`

Date: 2026-02-19  
Level: L1 wish notebook compatible  
Skills: `prime-wishes`, `phuc-forecast`, `prime-coder`, `prime-safety`, `phuc-context`

## Quest + belt

- Quest: "Twin River Gate"
- Current belt: `Yellow Belt`
- Target belt: `Brown Belt`
- Promotion gate: CPU prepass + LLM fallback + receipt artifacts pass in harsh QA

## Capability

Provide natural-language twin orchestration in the CLI using CPU routing first and remote/local Ollama fallback.

## Non-goals

- No opaque hidden memory state
- No undocumented model routing policy

## Acceptance tests

1. `stillwater twin "/skills"` routes through CPU and emits receipts.
2. `stillwater twin "<nl prompt>"` reaches Ollama and returns a response.
3. `stillwater twin --interactive` supports multi-turn session with `/exit`.
