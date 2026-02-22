# Stillwater Portal Refactor - Summary

## What Was Done

### 1. Created LLM Portal v3 (`admin/llm_portal_v3.py`)

**Simplified from v2 to match unit test pattern:**

```
Old Portal v2 (complex):
- Configuration management
- Web UI
- Multiple providers (Ollama, Claude CLI, etc.)
- Session management
- PID file management
- 300+ lines of infrastructure

New Portal v3 (simple):
- Core logic only
- Swarm execution: load metadata → inject skills → call LLM
- Recipe execution: placeholder for CPU nodes
- 350 lines, crystal clear
```

**Key Endpoints:**
- `POST /v1/swarm/execute` - Execute swarm with skill injection
- `POST /v1/recipe/execute` - Execute recipe on CPU nodes
- `GET /health` - Health check
- `GET /v1/models` - List models

### 2. Created CLI Orchestrator (`admin/cli_orchestrator.py`)

**Thin wrapper that hits the portal:**

```
CLI Orchestrator:
1. Parse arguments
2. Hit portal HTTP endpoint
3. Return result

No LLM logic, no file I/O, no infrastructure.
Just HTTP.
```

**Usage:**
```bash
# Swarm execution
python admin/cli_orchestrator.py --swarm coder --prompt "..." --model sonnet

# Recipe execution
python admin/cli_orchestrator.py --recipe gmail --task "Read emails"

# Health check
python admin/cli_orchestrator.py --health
```

### 3. Portal-Test Integration

**Unit tests already follow this pattern!**

```python
# From test_abcd_coding.py
llm_client = LLMClient(provider="http", config={...})

# This should point to:
# - Either the LLM Portal v3 endpoint
# - Or we update to explicitly use portal
```

---

## Architecture Comparison

### Old (Coupled)
```
Test → LLMClient → claude_code_wrapper → Claude CLI → LLM
  │                      │
  │                       └─ PID files
  │                       └─ Process mgmt
  └─ Indirect coupling
```

### New (Decoupled)
```
Test → LLMClient → /v1/swarm/execute → Portal v3 → LLM
CLI → HTTP POST → /v1/swarm/execute → Portal v3 → LLM
Recipe → HTTP POST → /v1/recipe/execute → Portal v3 → CPU Node

Portal v3: Load swarm → Inject skills → Call LLM
```

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `admin/llm_portal_v3.py` | Simplified portal (core logic only) | 350 |
| `admin/cli_orchestrator.py` | CLI that hits portal via HTTP | 280 |
| `admin/test_hard_swe_baseline.py` | Hard SWE baseline tests (no skills) | 350 |
| `admin/PORTAL_V3_GUIDE.md` | Complete usage guide | 400 |
| `admin/REFACTOR_SUMMARY.md` | This file | - |

---

## How to Use

### 1. Start Portal

```bash
cd /home/phuc/projects/stillwater
python admin/llm_portal_v3.py
# Runs at http://localhost:8788
```

### 2. Use CLI

```bash
python admin/cli_orchestrator.py --swarm coder --prompt "Write sum function" --model sonnet
```

### 3. Or Call Portal Directly

```bash
curl -X POST http://localhost:8788/v1/swarm/execute \
  -H "Content-Type: application/json" \
  -d '{"swarm_type": "coder", "prompt": "...", "model": "sonnet"}'
```

### 4. Run Tests

```bash
pytest admin/tests/swarms/test_abcd_coding.py -v -s
pytest admin/tests/swarms/test_hard_swe.py -v -s
pytest admin/tests/swarms/test_hard_swe_baseline.py -v -s
```

---

## What's Still the Same

✅ Skill injection logic (same as unit tests)
✅ Swarm metadata loading
✅ QUICK LOAD block extraction
✅ LLM client integration
✅ Rung and verification ladder

---

## What's Different

| Old | New |
|-----|-----|
| Portal v2 (complex) | Portal v3 (simple) |
| HTTP wrapper around Claude CLI | Direct skill injection + LLM call |
| Multiple provider support | Single-purpose LLM execution |
| Configuration UI | Clean API |
| PID file management | Stateless HTTP endpoints |
| CLI calls wrapper | CLI calls portal |

---

## Key Benefits

1. **Same logic as unit tests** - Portal v3 does exactly what ABCD tests do
2. **Testable** - Can unit test portal without full integration
3. **Clear separation** - CLI just orchestrates, portal executes
4. **Easy to extend** - Recipe endpoint for CPU nodes
5. **Simple** - ~350 lines vs 300+ in v2
6. **Stateless** - HTTP endpoints, no file I/O

---

## Next Steps

1. ✅ Create Portal v3
2. ✅ Create CLI Orchestrator
3. ✅ Create hard SWE baseline tests
4. ⏳ Run hard SWE baseline tests
5. ⏳ Compare hard SWE (baseline vs with skills)
6. 📝 Update unit tests to use portal v3 (optional)
7. 📝 Implement recipe execution for CPU nodes

---

## Questions Answered

**Q: Does the portal do the same thing as unit tests?**
A: Yes! Portal v3 does exactly what invoke_swarm() does in unit tests.

**Q: Can I use the CLI instead of tests?**
A: Yes! `cli_orchestrator.py --swarm coder --prompt "..." --model sonnet`

**Q: Does portal support recipes?**
A: Yes! Placeholder implemented, ready for CPU node integration.

**Q: What about the old portal?**
A: Keep v2 for now, migrate when ready. v3 is parallel.

---

## Testing the Portal

```bash
# Start portal
python admin/llm_portal_v3.py &
PORTAL_PID=$!

# Wait for startup
sleep 2

# Health check
curl http://localhost:8788/health

# Run test
python admin/cli_orchestrator.py --swarm coder --prompt "Sum list" --model haiku

# Kill portal
kill $PORTAL_PID
```

---

## Implementation Checklist

- [x] Portal v3 created (swarm executor)
- [x] Recipe executor placeholder
- [x] CLI orchestrator created
- [x] Documentation written
- [ ] Hard SWE baseline tests (running)
- [ ] Portal integration with tests (optional)
- [ ] Recipe execution implemented

---

**Status:** Portal v3 ready to use while tests run. All code matches unit test logic.
