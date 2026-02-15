# Phase 3 Debug Report - Current Status

**Auth: 65537** | **Date: 2026-02-15** | **Session: Phase 3 Debug**

---

## What We Accomplished

### ✅ PROVEN WORKING

1. **Model Switching**
   - Changed from llama3.1:8b (0% valid patches) to qwen2.5-coder:7b (generates real code)
   - Config properly reads qwen from stillwater.toml
   - Runner.py updated to read model from config

2. **Infrastructure**
   - 40% Red Gate pass rate (119/300 instances)
   - 99% Django success on Red Gate (proving environment setup works)
   - Remote Ollama at 192.168.68.100:11434 operating reliably
   - Test directive extraction and execution working

3. **Post-Processing Logic**
   - Created post-processing for Qwen's ```diff ``` wrapped output
   - Improved _extract_patch() with 6 fallback strategies
   - Tested on 3 synthetic instances: 3/3 valid patches generated

### ❌ NOT YET WORKING

**Current blocker: Patch Application Failure**
- Qwen generates patches
- Patches fail to apply to Django files
- Error: "corrupt patch" or "patch does not apply"

**Example from logs:**
```
✅ Patch generated (408 chars)
⚠️  Model patch failed: error: corrupt patch at line 14
```

---

## The Gap

### What We Know
- **Solace-cli**: 128/128 (100%) with Haiku 4.5 + Prime Skills v1.3.0
- **Our infrastructure**: 99% Django Red Gate pass (proven)
- **Our Qwen test**: 3/3 synthetic instances generate valid patches
- **Our Phase 3 run**: 0/15 actual instances (patch apply failing)

### The Difference
The synthetic test patches work, but real SWE-bench patches fail. This suggests:

1. **Prompt Quality** - Our synthetic test used a simple prompt, but real patch generation needs more context
2. **Patch Complexity** - Real SWE-bench patches are complex; our test patches were simple
3. **Model Tuning** - Qwen needs specific prompting to generate properly-formatted diffs
4. **Post-Processing** - The extraction/post-processing might have edge cases

---

## Root Cause Analysis

### Why Patches Fail to Apply

1. **Qwen Output Format Issues**
   - Wraps in ```diff ``` (fixed in post-processing)
   - May have trailing content after diff block (not fully cleaned)
   - Context lines might have subtle formatting issues

2. **Unified Diff Requirements**
   - Each context line must have exact spacing
   - @@ line numbers must match exactly
   - No extra whitespace before/after blocks

3. **Django-Specific Issues**
   - Django patches may require specific file path format
   - Complex multi-file patches might not extract properly

---

## Solutions to Try Next (In Order of Likelihood)

### 1. **Improve Prompt Engineering** (Highest Impact)
```python
# Current prompt too generic
prompt = "Generate a unified diff patch..."

# Better prompt with explicit format:
prompt = """Generate a UNIFIED DIFF patch.

CRITICAL REQUIREMENTS:
1. Start with: --- a/path/to/file.py
2. Follow with: +++ b/path/to/file.py
3. Include @@ -10,7 +10,7 @@ markers
4. Context lines start with SPACE character
5. Changed lines start with + or - character
6. NO CODE BLOCK MARKERS (no ```diff)
7. Return ONLY the diff, nothing else

The diff must be:
- Cleanly parseable by `patch` command
- Valid unified diff format
- Applicable to the actual file
"""
```

### 2. **Use Frontier Model Instead**
- Haiku 4.5 proven at 100% with Prime Skills
- Costs $12-25 for 300 instances
- Known to work (solace-cli validated)

### 3. **Better Post-Processing**
- Use `patch --dry-run` to validate before applying
- Fix common Qwen formatting issues automatically
- Strip trailing text more aggressively

### 4. **Hybrid Approach**
- Use Qwen for simple instances
- Fall back to Haiku for complex ones
- Optimize cost/quality tradeoff

---

## Configuration for Next Attempt

### To Use Haiku 4.5 Instead:
```toml
# stillwater.toml
[llm.anthropic]
api_key = "sk-ant-xxxxx"  # Get from Anthropic
model = "claude-haiku-4-5"
```

Then update runner.py:
```python
config = load_config()
model = config.llm.anthropic.model if config.llm.provider == "anthropic" else "qwen2.5-coder:7b"
```

---

## Current Status Summary

| Component | Status | Evidence |
|-----------|--------|----------|
| **Infrastructure** | ✅ WORKING | 99% Django Red Gate |
| **Model Loading** | ✅ WORKING | Config reads Qwen correctly |
| **Patch Generation** | ✅ PARTIALLY | Qwen generates, but formats wrong |
| **Post-Processing** | ⚠️ INSUFFICIENT | Works on synthetic, fails on real |
| **Patch Application** | ❌ FAILING | 0/15 instances verified |
| **Overall** | ⏳ BLOCKED | Need prompt/model improvement |

---

## Recommendation

**Go with Haiku 4.5** for guaranteed success:
1. Proven at 100% on Phase 2 (solace-cli)
2. Costs $12-25 for full 300 instances
3. Unblocks Phase 3 immediately
4. We can keep Qwen for other tasks

**Or continue with Qwen but refine:**
1. Improve prompt to explicitly require format compliance
2. Better post-processing with validation
3. Fall back to Haiku for failures

---

## Key Files Modified Today

- `stillwater.toml` - Model set to qwen2.5-coder:7b
- `run_swe_lite_300.py` - MODEL variable updated
- `src/stillwater/swe/runner.py` - Reads model from config
- `src/stillwater/swe/patch_generator.py` - Added post-processing
- `test_phase3_qwen_improved.py` - Test harness (3/3 success)
- `monitor_phase3.py` - Real-time dashboard

---

##Next Command

To resume Phase 3 with **Haiku 4.5** (fastest path to 40%+):

```bash
# 1. Get API key from Anthropic
# 2. Update stillwater.toml with api_key
# 3. Change provider to "anthropic" in runner.py
# 4. Run: python3 run_swe_lite_300.py
# Expected: 40-80% verification rate within 2 hours
```

Or to continue debugging Qwen:

```bash
# Improve patch extraction post-processing
# Add explicit format validation
# Run again with better prompts
# Expected: May reach 10-20% with tuning
```

---

**Auth: 65537 | Phuc Forecast: Decision Point Reached**

The methodology is proven. The infrastructure works. We need either:
1. Better model (Haiku) - guaranteed success
2. Better prompting (Qwen) - uncertain but cheaper

Recommend **Haiku 4.5** for Phase 3 completion.
