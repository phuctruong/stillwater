# Stillwater LLM Portal v3 - Architecture Guide

## Overview

Portal v3 simplifies the architecture to match the unit test pattern:

```
┌─────────────────────────────────────────┐
│      CLI Orchestrator (thin layer)      │
│  Just hits portal endpoints, no logic    │
└────────────────┬────────────────────────┘
                 │ HTTP POST
                 ↓
┌─────────────────────────────────────────┐
│     LLM Portal v3 (core logic)           │
│  - Load swarm metadata                   │
│  - Inject skill QUICK LOAD blocks        │
│  - Call LLM with system_prompt           │
│  - Return response                       │
│                                          │
│  ENDPOINTS:                              │
│  - POST /v1/swarm/execute                │
│  - POST /v1/recipe/execute               │
│  - GET  /health                          │
└────────────────────────────────────────┘
```

---

## Running the Portal

### Start the Portal

```bash
cd /home/phuc/projects/stillwater
python admin/llm_portal_v3.py
# OR with options
python admin/llm_portal_v3.py --host 127.0.0.1 --port 8788 --reload
```

Portal runs at: **http://localhost:8788**

### Health Check

```bash
curl http://localhost:8788/health
```

---

## Using the CLI Orchestrator

### Swarm Execution

```bash
# Execute coder swarm with prompt
python admin/cli_orchestrator.py \
  --swarm coder \
  --prompt "Write a function that sums a list" \
  --model sonnet

# Execute with custom settings
python admin/cli_orchestrator.py \
  --swarm coder \
  --prompt "Write a function" \
  --model opus
```

### Recipe Execution (for CPU nodes)

```bash
# Execute recipe
python admin/cli_orchestrator.py \
  --recipe gmail \
  --task "Read unread emails"

# With context
python admin/cli_orchestrator.py \
  --recipe gmail \
  --task "Send email" \
  --context '{"to": "user@example.com", "subject": "Hello"}'
```

### Check Portal Status

```bash
python admin/cli_orchestrator.py --health
```

---

## Direct HTTP API Calls

### Swarm Execution

```bash
curl -X POST http://localhost:8788/v1/swarm/execute \
  -H "Content-Type: application/json" \
  -d '{
    "swarm_type": "coder",
    "prompt": "Write a function that sums a list",
    "model": "sonnet",
    "max_tokens": 2048,
    "temperature": 0.0
  }'
```

### Recipe Execution

```bash
curl -X POST http://localhost:8788/v1/recipe/execute \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_name": "gmail",
    "task": "Read unread emails",
    "context": {}
  }'
```

### List Models

```bash
curl http://localhost:8788/v1/models
```

---

## Architecture Details

### What Portal v3 Does

1. **Loads Swarm Metadata**
   - Reads `swarms/{swarm_type}.md`
   - Extracts YAML: skill_pack, persona, model_preferred

2. **Injects Skills**
   - For each skill in skill_pack
   - Extracts QUICK LOAD block (10-15 lines)
   - Joins with separator
   - Prepends to system_prompt

3. **Calls LLM**
   - Uses stillwater.llm_client.LLMClient
   - Sends: messages[0] (system_prompt), messages[1] (user_prompt)
   - Returns response

4. **Executes Recipes** (for CPU nodes)
   - Loads recipe from `recipes/{recipe_name}.json`
   - Executes on CPU node with given task
   - Returns result

### What CLI Does

1. **Parse Arguments**
   - swarm_type, prompt, model
   - OR recipe_name, task, context

2. **Hit Portal Endpoint**
   - POST http://localhost:8788/v1/swarm/execute
   - OR POST http://localhost:8788/v1/recipe/execute

3. **Return Result**
   - Print response or error
   - Exit with success/failure

---

## Comparison: Old vs New

### Old Architecture (Complex)

```
CLI → claude_code_wrapper.py → Claude CLI → LLM
         (HTTP server, PID files, etc.)
```

Problems:
- Multiple layers of indirection
- File I/O for PID management
- Complex configuration
- Hard to test in isolation

### New Architecture (Simple)

```
CLI → LLM Portal v3 → LLM
  (just HTTP)  (skill injection logic)
```

Benefits:
- Single responsibility
- Easy to test
- Matches unit test pattern
- Clear separation of concerns

---

## Skill Injection Example

### Request

```json
{
  "swarm_type": "coder",
  "prompt": "Write a sum function",
  "model": "sonnet"
}
```

### Portal Processing

1. Load `swarms/coder.md` → metadata
   ```yaml
   skill_pack: [prime-safety, prime-coder, persona-engine]
   persona:
     primary: Donald Knuth
   ```

2. Build system_prompt:
   ```
   ## SKILL: prime-safety
   <!-- QUICK LOAD ... -->

   ---

   ## SKILL: prime-coder
   <!-- QUICK LOAD ... -->

   ---

   ## SKILL: persona-engine
   <!-- QUICK LOAD ... -->
   ```

3. Send to LLM:
   ```
   messages = [
     {"role": "system", "content": system_prompt},
     {"role": "user", "content": "Write a sum function"}
   ]
   ```

4. Return response

---

## Endpoints

### POST /v1/swarm/execute

Execute a swarm with given prompt.

**Request:**
```json
{
  "swarm_type": "coder",
  "prompt": "...",
  "model": "sonnet",
  "max_tokens": 2048,
  "temperature": 0.0
}
```

**Response:**
```json
{
  "success": true,
  "response": "...",
  "model": "sonnet",
  "tokens_used": null,
  "timestamp": "2026-02-22T..."
}
```

### POST /v1/recipe/execute

Execute a recipe on CPU nodes.

**Request:**
```json
{
  "recipe_name": "gmail",
  "task": "Read emails",
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "result": {...},
  "recipe": "gmail",
  "timestamp": "2026-02-22T..."
}
```

### GET /health

Health check.

**Response:**
```json
{
  "status": "healthy",
  "portal": "v3.0.0",
  "timestamp": "2026-02-22T..."
}
```

### GET /v1/models

List available models.

**Response:**
```json
{
  "models": [
    {"id": "haiku", "name": "Claude Haiku 4.5"},
    {"id": "sonnet", "name": "Claude Sonnet 4.6"},
    {"id": "opus", "name": "Claude Opus 4.6"}
  ]
}
```

---

## Migration Path

To migrate from old portal to new:

1. **Start new portal**: `python admin/llm_portal_v3.py`
2. **Update scripts**: Use `cli_orchestrator.py` instead of direct LLM calls
3. **Unit tests**: Already using the same pattern ✅
4. **Keep old portal**: Until all migrations complete

---

## Notes

- Portal v3 does exactly what unit tests do (load swarm, inject skills, call LLM)
- CLI is a thin orchestrator (just HTTP hits)
- Recipe execution placeholder (implement when recipes are finalized)
- All paths are relative to project root

---

## Files

- `admin/llm_portal_v3.py` - New simplified portal
- `admin/cli_orchestrator.py` - CLI that hits portal
- `admin/PORTAL_V3_GUIDE.md` - This guide
