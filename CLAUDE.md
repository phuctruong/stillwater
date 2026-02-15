# Stillwater Claude Code Configuration

**Auth: 65537** | **Date: 2026-02-15**

---

## Session Initialization

On every Claude Code session start:

### 1. Load Environment
```bash
cd /home/phuc/projects/stillwater
export OLLAMA_HOST=http://192.168.68.100:11434
export OLLAMA_MODEL=llama3.1:8b
```

### 2. Verify Configuration
```bash
cat stillwater.toml | grep -A3 "llm.ollama"
# Should show: host = "192.168.68.100"
```

### 3. Test Remote Ollama Connection
```bash
curl -s http://192.168.68.100:11434/api/tags | jq '.models[] | .name'
# Should show: llama3.1:8b
```

---

## LLM Configuration

**Provider**: Ollama (remote only)
**Host**: 192.168.68.100:11434
**Model**: llama3.1:8b
**Temperature**: 0.0 (deterministic)

**Rules**:
- ✅ ALWAYS use remote Ollama
- ❌ NEVER use local Ollama fallback
- ❌ NEVER switch to Haiku/Sonnet unless explicitly approved
- ✅ If connection fails, STOP and debug

---

## 5 Weapons Activated

Every session has access to:

### 1. Skills (51 Prime Skills)
- Location: `src/stillwater/skills/`
- Loaded by: `create_skills_summary()`
- Injected in: Every LLM prompt
- Size: 2,341 characters

### 2. Orchestration (Feedback Loop)
- Type: 6-attempt feedback loop
- Location: `runner.py` line 160-220
- Trigger: Test failures feed back to LLM
- Result: Error-driven refinement

### 3. Tools
- Test execution (Red Gate)
- Test verification (Green Gate)
- File operations
- Environment setup
- All available to LLM

### 4. Proper Context
- Full file reading (not snippets)
- Up to 8KB context per instance
- Includes imports, functions, classes
- Generator: `_build_context()` in `patch_generator.py`

### 5. Structure/Determinism
- 22-state machine
- 8 forbidden actions enforcement
- Verification ladder (641 → 274177 → 65537)
- State machine enforcer: `patch_state_machine.py`

---

## Verification Ladder

Every patch must pass:

1. **641 (Edge Sanity)**
   - Correct format
   - Applies cleanly to repo
   - No syntax errors

2. **274177 (Stress Test)**
   - All tests pass
   - No regressions
   - Edge cases handled

3. **65537 (God Approval)**
   - Deterministic (same input → same output)
   - Proof valid (witness generated)
   - Solution robust

---

## Testing Strategy

### Phase Tests (Fast Iteration)
- **Phase 1**: 1 instance (~2 min) → `test_1_instance_100pct.py`
- **Phase 2**: 5 instances (~10 min) → `test_5_instances_100pct.py`
- **Phase 3**: 10 instances (~20 min) → `test_10_instances_100pct.py`
- **Phase 4+**: Scale as needed

### Success Criteria
- Phase 1-3: ≥100% (maintain 100%)
- Phase 4-7: ≥80% (scale limit)

### If Tests Fail
1. Run: `python3 debug_5_weapons.py` (verify all working)
2. Check: Which instance(s) failed?
3. Fix: One of the 5 weapons
4. Retest: Same phase

---

## Haiku Swarms (Optional)

Multi-agent orchestration available when needed:

- **Scout Agent (Haiku)**: Problem exploration
- **Solver Agent (Haiku)**: Patch generation
- **Skeptic Agent (Haiku)**: Validation
- **Orchestrator (llama 8B)**: Decision making

**Current approach**: Single agent (llama 8B)
**When to use swarms**: If scaling hits ceiling (Phase 4+)

See: `HAIKU_SWARMS_WITH_SKILLS.md`

---

## Key Files Reference

### Implementation
- `src/stillwater/swe/patch_generator.py` - Skills + prompt
- `src/stillwater/swe/runner.py` - Feedback loop
- `src/stillwater/swe/direct_edit_generator.py` - Full context
- `src/stillwater/swe/patch_state_machine.py` - Structure

### Testing
- `debug_5_weapons.py` - Verify all working
- `test_1_instance_100pct.py` - Phase 1
- `test_5_instances_100pct.py` - Phase 2
- `test_10_instances_100pct.py` - Phase 3

### Documentation
- `QUICK_START.md` - Commands + next steps
- `5_WEAPONS_TRACKING.md` - Detailed breakdown
- `RAMP_100_GUIDE.md` - Testing strategy
- `HAIKU_SWARMS_WITH_SKILLS.md` - Multi-agent pattern
- `OLLAMA_CONFIG.md` - Remote Ollama setup

---

## Commands for This Session

```bash
# Verify all 5 weapons working
python3 debug_5_weapons.py

# Run testing phases
python3 test_1_instance_100pct.py
python3 test_5_instances_100pct.py
python3 test_10_instances_100pct.py

# Check results
cat phase_*_instances.json | jq '.success_rate'

# Verify remote Ollama
curl -s http://192.168.68.100:11434/api/tags | jq '.models[] | .name'
```

---

## Principles

1. **Infrastructure > Model Quality** - Good orchestration beats better models
2. **Maintain 100%** - Don't advance phases until current phase at 100%
3. **Fast Feedback** - Quick iterations for debugging
4. **Remote Only** - Always use remote Ollama, never local
5. **Evidence Driven** - Every decision backed by test results

---

## Mission

Transform llama 8B from 0% → 90%+ on SWE-bench by implementing:
- 51 Prime Skills (orchestration knowledge)
- 6-attempt feedback loop (error-driven refinement)
- Full file context (complete understanding)
- State machine guidance (explicit structure)
- Verification gates (proof requirements)

**Target**: Phase 1-3 at 100%, Phase 4+ at 80%+ success

**Timeline**: ~10 hours total

---

**Auth: 65537**
**Status**: Ready to start Phase 1 ramping
**Next**: Run `python3 test_1_instance_100pct.py`
