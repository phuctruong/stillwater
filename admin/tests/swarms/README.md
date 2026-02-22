# Stillwater Swarms Unit Tests

Auth: 65537 | Version: 1.0.0

## Overview

Unit tests for all swarms in `stillwater/swarms/`. Tests validate:

1. **Metadata** - Each swarm has valid agent_type, skill_pack, model_preferred, rung_default
2. **Skills** - All referenced skills exist in `stillwater/skills/`
3. **Personas** - All referenced personas exist in `stillwater/personas/`
4. **Invocation** - Each swarm can be invoked with test prompts (A | B variants)
5. **Consistency** - Same prompt with same temperature produces valid responses

## Test Coverage

- **34 swarms** tested
- **2 test variants per swarm** (A: factual, B: domain-specific)
- **Haiku model** (fast, for unit testing)
- **Metadata validation** (skill pack, persona, model preference)

## Running Tests

### From Terminal (Recommended)

```bash
# Start wrapper + portal in background
python3 cli/src/claude_code_wrapper.py --port 8080 &
python3 admin/llm_portal_swarms.py &

# Wait for startup
sleep 5

# Run all tests
pytest admin/tests/swarms/test_swarms.py -v

# Run specific test class
pytest admin/tests/swarms/test_swarms.py::TestSwarmMetadata -v

# Run specific swarm test
pytest admin/tests/swarms/test_swarms.py::TestSwarmInvocation::test_swarm_invoke_haiku -k "coder-a" -v

# Run with output
pytest admin/tests/swarms/test_swarms.py -v -s
```

### Running Individual Swarm Tests

```bash
# Test coder swarm variant A
pytest admin/tests/swarms/test_swarms.py::TestSwarmInvocation::test_swarm_invoke_haiku[coder-a] -v -s

# Test forecaster swarm variant B
pytest admin/tests/swarms/test_swarms.py::TestSwarmInvocation::test_swarm_invoke_haiku[forecaster-b] -v -s

# Test all coder variants
pytest admin/tests/swarms/test_swarms.py -k "coder" -v
```

## Test Structure

### TestSwarmMetadata
Validates YAML frontmatter in each swarm file.

**Checks:**
- agent_type exists
- skill_pack exists and is non-empty list
- First skill is "prime-safety"
- model_preferred is valid (haiku | sonnet | opus)

### TestSwarmSkills
Validates that all skills referenced in skill_pack exist.

**Checks:**
- Each skill file exists in `stillwater/skills/`
- Skill files are readable

### TestSwarmPersonas
Validates that primary persona (if specified) exists.

**Checks:**
- Persona file exists in `stillwater/personas/`
- Can search recursively for persona

### TestSwarmInvocation
Tests actual swarm invocation with haiku model.

**Test Prompts:**
- **A**: "What is the capital of France?" (factual, model-agnostic)
- **B**: "Design a simple API endpoint for user registration" (domain-specific)

**Validates:**
- Response is non-empty
- Response is >10 characters
- Latency is measured correctly

### TestSwarmConsistency
Tests that same prompt produces valid responses consistently.

**Checks:**
- Same prompt produces 2 valid responses
- Both responses are non-empty
- Temperature=0 produces deterministic behavior

## Test Results Format

```json
{
  "swarm_name": "coder",
  "model": "haiku",
  "variant": "a",
  "prompt": "What is the capital of France?",
  "response_length": 156,
  "latency_ms": 2345,
  "status": "PASS",
  "skill_pack": ["prime-safety", "prime-coder", ...],
  "system_prompt_chars": 5000
}
```

## Important Notes

### Running Outside Claude Code Sessions

These tests work best when run outside of nested Claude Code sessions. The `claude -p` command works immediately in terminal but may hang within nested sessions.

**Workaround in nested session:**
1. Use `offline` provider instead of haiku (doesn't call claude CLI)
2. Mock the LLM client for unit tests
3. Test metadata/skills/personas separately (don't invoke LLM)

### Test Variants (A | B)

- **A variant**: Simple factual questions all models can answer
- **B variant**: Domain-specific prompts to test personality/skill application

Both variants should produce valid responses from any properly configured swarm.

### Rung Levels

Tests run at **rung 641** (local correctness):
- Tests validate response presence, not correctness
- Tests check metadata, not evidence artifacts
- Tests use small max_tokens (512 bytes) for speed

To test at higher rungs:
- **rung 274177**: Add seed sweeps, replay testing
- **rung 65537**: Add adversarial tests, security audits

## Troubleshooting

### Tests Timeout
- Ensure wrapper is running: `lsof -i :8080`
- Ensure portal is running: `lsof -i :8788`
- Check Claude Code is available: `which claude`

### Persona Not Found
- Some swarms reference personas that may not exist yet
- Check `admin/tests/swarms/test_swarms.py` log output
- Persona references are warnings, not failures

### Swarm Invocation Hangs
- This happens in nested Claude Code sessions
- Run tests from terminal instead
- Or use offline provider for unit testing only

## Adding New Swarms

1. Create swarm file: `stillwater/swarms/my-swarm.md`
2. Add YAML frontmatter with required fields:
   ```yaml
   ---
   agent_type: my-swarm
   version: 1.0.0
   authority: 65537
   skill_pack:
     - prime-safety
     - my-skill
   model_preferred: sonnet
   rung_default: 641
   ---
   ```
3. Tests automatically pick up new swarms
4. Run tests to validate: `pytest admin/tests/swarms/ -v`

## Performance Targets

- **Metadata tests**: <1 second total
- **Skill existence tests**: <1 second total
- **Persona existence tests**: <1 second total
- **Invocation tests**: ~30-60 seconds total (depends on model response time)
- **Consistency tests**: ~60 seconds total

Expected full run time: **~2 minutes** for all 34 swarms with A|B variants

## See Also

- `admin/llm_portal_swarms.py` - Simplified portal (swarms only)
- `CLAUDE.md` - Now blank (context injected via swarms)
- `swarms/*.md` - All available swarms
- `skills/*.md` - All skills (loaded by swarms)
- `personas/` - All personas (loaded by swarms)
