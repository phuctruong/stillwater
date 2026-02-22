# Portal v3 Quick Start — 2-Minute Setup

**Status**: ✅ Portal running, test script ready, framework complete

---

## What You Have Right Now

1. **Portal v3** — REST API server for swarm execution
2. **test_llm_portal.sh** — Easy testing script
3. **ABCD Testing** — Comprehensive framework for measuring swarm quality
4. **Donald Knuth Persona** — Expert persona for coder swarm

All running and ready to use. No additional setup required.

---

## 1-Minute Quick Test

### Check Portal is Running
```bash
curl http://localhost:8788/health | jq
# Should return: {"status": "healthy", "portal": "v3.0.0", ...}
```

### Use Test Script
```bash
./admin/test_llm_portal.sh \
  --swarm coder \
  --prompt "Write a function that adds two numbers" \
  --model haiku
```

**What happens**:
- Script sends request to Portal
- Portal loads `swarms/coder.md` metadata
- Portal injects `skills/prime-coder.md` into system prompt
- Portal calls Claude with system prompt + prompt
- Results logged to `admin/logs/test_swarm_*.md`

### Expected Output
```
✗ Failed (because no LLM provider configured)
```

This is normal. The script and Portal are working. You just need an LLM provider.

---

## Next: Configure LLM Provider

Pick ONE option:

### Option A: Use Anthropic Claude (Recommended)
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Option B: Use OpenAI
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### Option C: Use Together.ai (Cheaper)
```bash
export TOGETHER_API_KEY=your-key-here
```

### Option D: Use Ollama (Local, Free)
```bash
# Install: https://ollama.ai
ollama pull mistral
ollama serve  # In separate terminal
```

Then test again:
```bash
./admin/test_llm_portal.sh --swarm coder --prompt "Write add function"
```

Expected output:
```
✓ Success
Elapsed Time: 1234ms
Model: haiku
Response:
def add(a, b):
    """Add two numbers."""
    return a + b
```

---

## Run Full Test Suite (Optional)

Once LLM provider is configured:

```bash
# Run all ABCD tests
bash admin/tests/swarms/run_abcd_tests.sh --setup

# Run just one model
bash admin/tests/swarms/run_abcd_tests.sh --model sonnet

# View results
cat admin/tests/swarms/results/ABCD_SUMMARY.json | jq
```

**What this tests**:
- 4 coding tasks (simple_sum, palindrome, fibonacci, dict_merge)
- 3 models (haiku, sonnet, opus)
- Syntax validation, functional correctness, code quality, context injection
- Results saved to `admin/tests/swarms/results/{model}/`

**Expected time**: 10-15 minutes for full suite

---

## Using Portal Directly (Advanced)

### Via Swagger UI
```bash
open http://localhost:8788/docs
```
Click "Try it out" on `/v1/swarm/execute`, fill in:
```json
{
  "swarm_type": "coder",
  "prompt": "Write a function that checks if a number is prime",
  "model": "haiku",
  "max_tokens": 256,
  "temperature": 0.0
}
```

### Via curl
```bash
curl -X POST http://localhost:8788/v1/swarm/execute \
  -H "Content-Type: application/json" \
  -d '{
    "swarm_type": "coder",
    "prompt": "Write a function that checks if a number is prime",
    "model": "haiku",
    "max_tokens": 256,
    "temperature": 0.0
  }' | jq
```

### Via test script
```bash
./admin/test_llm_portal.sh \
  --swarm coder \
  --prompt "Write a function that checks if a number is prime" \
  --model haiku \
  --max-tokens 256 \
  --temp 0.0
```

All three ways do the same thing. Test script is recommended for easy use.

---

## Understanding Results

### Test Script Output
```
✓ Success (or ✗ Failed)
Elapsed Time: 1234ms
Model: haiku
Response: [generated code]
```

Check logs for details:
```bash
cat admin/logs/test_swarm_output.md  # Response
cat admin/logs/test_swarm_input.md   # Request sent
```

### ABCD Test Results
```bash
cat admin/tests/swarms/results/ABCD_SUMMARY.json | jq
```

Shows per-model metrics:
- `syntax_rate` — Percentage with valid Python syntax
- `functional_rate` — Percentage that pass tests
- `quality_avg` — Average code quality score (0-1)
- `context_rate` — Percentage where skills were detected

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Not Found" error | Portal probably crashed. Restart: `python3 admin/llm_portal_v3.py` |
| "No LLM providers available" | Configure API key (see section above) |
| Tests hang | Check if LLM API is responding (test manually) |
| Script not executable | `chmod +x admin/test_llm_portal.sh` |
| Wrong results directory | Check `admin/logs/` exists, create if needed: `mkdir -p admin/logs` |

---

## File Locations

```
Key files:
  admin/llm_portal_v3.py          — Portal server
  admin/test_llm_portal.sh        — Test script
  admin/logs/                     — Test output
  admin/tests/swarms/results/     — Test results

Documentation:
  PORTAL_V3_STATUS.md             — Full status
  ABCD_TESTING_READY.md           — Testing guide
  admin/tests/swarms/ABCD_TESTING.md — Detailed docs

Configuration:
  swarms/coder.md                 — Coder swarm definition
  skills/prime-coder.md           — Coder skill (injected)
  personas/language-creators/donald-knuth.md — Knuth persona
```

---

## What's Happening Behind the Scenes

```
./admin/test_llm_portal.sh --swarm coder --prompt "..."
  ↓
  Sends POST to http://localhost:8788/v1/swarm/execute
  ↓
  Portal loads swarms/coder.md (persona + skill_pack list)
  ↓
  Portal injects skills (prime-safety, prime-coder) into system prompt
  ↓
  Portal calls LLM with:
    - system_prompt: [skills injected]
    - user_prompt: [your prompt]
  ↓
  Response logged to admin/logs/
  ↓
  Results displayed with timing
```

This is how skill injection works. Skills are embedded in the system prompt sent to the LLM.

---

## Next Actions

1. **Configure LLM provider** (pick one option above)
2. **Test Portal** (run test script once)
3. **Run ABCD suite** (optional, full benchmark)
4. **Review results** (check metrics)

---

**Everything is ready. Just configure an LLM provider and start testing.**

For detailed info, see:
- `PORTAL_V3_STATUS.md` — Complete status
- `ABCD_TESTING_READY.md` — Testing framework
- `admin/tests/swarms/ABCD_TESTING.md` — Full documentation
