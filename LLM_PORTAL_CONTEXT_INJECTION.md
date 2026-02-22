# LLM Portal v2.1 — SW5.0 Context Injection API

## Summary

The LLM Portal now supports **context injection from Software 5.0 constructs** (skills, recipes, swarms, personas). This enables:

1. **Per-call context selection** — inject any skill, recipe, swarm, or persona as a system prompt
2. **Unit testing of recipe LLM nodes** — test each step independently with full context
3. **Evidence-stamped responses** — every call includes rung target and context metadata
4. **Backwards compatible** — existing `/v1/chat/completions` endpoint unchanged

**Rung target:** 641 (local correctness with verification)

---

## New Endpoints

### 1. GET `/api/context/catalog`

List all available SW5.0 constructs.

```bash
curl http://localhost:8788/api/context/catalog | python3 -m json.tool
```

**Response:**
```json
{
  "skills": ["prime-safety", "prime-coder", "phuc-forecast", ...],
  "recipes": ["null-zero-audit", "paper-from-run", ...],
  "swarms": ["coder", "planner", "mathematician", ...],
  "personas": ["guido", "linus", "bruce-lee", ...]
}
```

---

### 2. GET `/api/context/preview/{type}/{name}`

Preview what context will be injected for a construct.

```bash
curl "http://localhost:8788/api/context/preview/skill/prime-safety?mode=quick"
curl "http://localhost:8788/api/context/preview/recipe/null-zero-audit?mode=full"
```

**Parameters:**
- `type`: "skill" | "recipe" | "swarm" | "persona"
- `name`: construct name (without file extension or "recipe." prefix)
- `mode` (optional): "quick" (QUICK LOAD block only) or "full" (entire file). Default: "quick"

**Response:**
```json
{
  "type": "skill",
  "name": "prime-safety",
  "mode": "quick",
  "content": "<!-- QUICK LOAD ... -->"
}
```

---

### 3. POST `/v1/context/chat`

Chat with SW5.0 context injection. System prompt is built from selected constructs + optional CNF capsule.

```bash
curl -X POST http://localhost:8788/v1/context/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama",
    "messages": [{"role": "user", "content": "Review this for safety issues"}],
    "context_sources": [
      {"type": "skill", "name": "prime-safety", "mode": "quick"},
      {"type": "skill", "name": "prime-coder", "mode": "quick"}
    ],
    "cnf_capsule": {
      "task": "Security code review",
      "constraints": "Fail-closed on untrusted data",
      "rung_target": 641
    },
    "rung_target": 641
  }'
```

**Request body:**
```python
{
  "model": str,                              # LLM model to use
  "messages": list[{"role": str, "content": str}],  # Chat messages
  "context_sources": list[{                  # optional context to inject
    "type": str,                             # "skill", "recipe", "swarm", "persona", "raw"
    "name": str,                             # construct name
    "mode": str = "quick",                   # "quick" or "full"
    "content": str = ""                      # for type="raw" only
  }],
  "cnf_capsule": dict = {},                  # optional CNF capsule (task, constraints, etc.)
  "rung_target": int = 641,                  # explicit rung declaration (641, 274177, 65537)
  "temperature": float = 0.0,                # LLM temperature
  "max_tokens": int = 4096                   # max response tokens
}
```

**Response:**
OpenAI-compatible chat completion with enhanced metadata:

```json
{
  "id": "sw-ctx-...",
  "object": "chat.completion",
  "created": 1771793131,
  "model": "ollama",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "..."},
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 386,
    "completion_tokens": 205,
    "total_tokens": 592
  },
  "_meta": {
    "latency_ms": 21322,
    "provider": "ollama",
    "rung_target": 641,
    "context_sources": [
      {"type": "skill", "name": "prime-safety", "mode": "quick"}
    ],
    "cnf_capsule_keys": ["task", "constraints"],
    "system_prompt_chars": 1517
  }
}
```

---

## Usage Examples

### Example 1: Inject a skill as context

```bash
curl -X POST http://localhost:8788/v1/context/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is your prime directive?"}],
    "context_sources": [
      {"type": "skill", "name": "prime-safety", "mode": "quick"}
    ],
    "rung_target": 641
  }'
```

The LLM receives the QUICK LOAD block from `skills/prime-safety.md` as system context.

---

### Example 2: Unit test a recipe LLM node

```bash
curl -X POST http://localhost:8788/v1/context/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "How would you audit this function for null-zero coercion?"}],
    "context_sources": [
      {"type": "recipe", "name": "null-zero-audit", "mode": "quick"},
      {"type": "skill", "name": "prime-safety", "mode": "quick"}
    ],
    "cnf_capsule": {
      "task": "Audit Python function for null-zero coercion violations",
      "constraints": "Fail-closed on ambiguous null handling"
    },
    "rung_target": 641
  }'
```

---

### Example 3: Multiple context sources with CNF capsule

```bash
curl -X POST http://localhost:8788/v1/context/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Design a test plan"}],
    "context_sources": [
      {"type": "swarm", "name": "coder", "mode": "quick"},
      {"type": "recipe", "name": "paper-from-run", "mode": "quick"},
      {"type": "persona", "name": "guido", "mode": "quick"}
    ],
    "cnf_capsule": {
      "task": "Design test plan for null audit feature",
      "rung_target": 641,
      "constraints": "Fail-closed on false negatives"
    },
    "rung_target": 641
  }'
```

---

### Example 4: Raw text context injection

```bash
curl -X POST http://localhost:8788/v1/context/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What should I do?"}],
    "context_sources": [
      {"type": "raw", "content": "You are a security auditor. Review all code for potential vulnerabilities. Fail-closed on uncertainty."}
    ],
    "rung_target": 641
  }'
```

---

## Python Unit Test Pattern

Here's how to unit test a recipe LLM node using the context API:

```python
import requests
import json

def test_recipe_llm_node_null_audit():
    """Unit test: null-zero-audit recipe LLM node"""

    resp = requests.post("http://localhost:8788/v1/context/chat", json={
        "model": "ollama",
        "messages": [
            {"role": "user", "content": "Audit this Python code for null-zero coercion: x = None; if not x: print('empty')"}
        ],
        "context_sources": [
            {"type": "recipe", "name": "null-zero-audit", "mode": "quick"},
            {"type": "skill", "name": "prime-safety", "mode": "quick"}
        ],
        "cnf_capsule": {
            "task": "Identify null-zero coercion bugs",
            "constraints": "Fail-closed on ambiguous cases"
        },
        "rung_target": 641
    })

    # Verify response structure
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()

    # Verify it's a valid OpenAI-compatible response
    assert "choices" in data
    assert "message" in data["choices"][0]
    assert "content" in data["choices"][0]["message"]

    # Verify context metadata
    assert "_meta" in data
    assert data["_meta"]["rung_target"] == 641
    assert len(data["_meta"]["context_sources"]) == 2
    assert data["_meta"]["system_prompt_chars"] > 0

    # Verify the LLM understood the context
    content = data["choices"][0]["message"]["content"].lower()
    assert any(word in content for word in ["null", "none", "coercion", "audit"])

    print("✓ Recipe LLM node test passed!")

if __name__ == "__main__":
    test_recipe_llm_node_null_audit()
```

---

## Web UI Enhancement

The web UI now includes a **Context Builder** panel:

1. **Skill/Recipe/Swarm/Persona selectors** — pick constructs to inject
2. **Rung target selector** — choose rung (641, 274177, 65537)
3. **Context tags** — see selected context, remove individually
4. **Two chat buttons:**
   - "Send" — regular chat (no context)
   - "Send with Context" — chat with selected context injected

The metadata shows:
- Provider and latency
- Rung target
- Context injected (system prompt char count)

---

## Files Modified

- `admin/llm_portal.py` — added 250+ lines:
  - `ContextSource`, `ContextChatRequest` models
  - `ContextLoader` class (loads skills/recipes/swarms/personas)
  - 3 new API endpoints (`/api/context/catalog`, `/api/context/preview`, `/v1/context/chat`)
  - Web UI Context Builder panel + JavaScript

---

## Backwards Compatibility

✅ **All existing endpoints unchanged:**
- `/v1/chat/completions` — works exactly as before
- `/v1/models` — works exactly as before
- `/api/providers` — works exactly as before
- Web UI chat test still functional

---

## Evidence & Testing

**Tested endpoints:**
```bash
# ✅ Catalog loading
curl http://localhost:8788/api/context/catalog

# ✅ Preview QUICK LOAD block
curl "http://localhost:8788/api/context/preview/skill/prime-safety?mode=quick"

# ✅ Context chat with recipe
curl -X POST http://localhost:8788/v1/context/chat -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What are the audit steps?"}],
       "context_sources": [{"type": "recipe", "name": "null-zero-audit", "mode": "quick"}],
       "rung_target": 641}'

# ✅ Backwards compatibility
curl -X POST http://localhost:8788/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "ping"}]}'
```

All tests pass with correct response structures and metadata.

---

## NORTHSTAR Alignment

This feature advances the **Recipe Hit Rate** metric (0% → 50% → 80%):

- **0% (now):** No recipes are testable because LLM context is fixed
- **50% (Q2):** Every recipe LLM node can be unit tested independently with context injection
- **80% (Q4):** Recipes improve through LEAK (cross-agent trade) + LEC (convention convergence)

The context injection API is the **prerequisite** for improving hit rate — you can't measure or improve what you can't test.

---

## Next Steps

1. **Recipe Engine Integration** — update `test_recipe_engine.py` to use context injection for `node_type: "llm"` steps
2. **Unit Test Templates** — add recipe testing patterns to `skills/phuc-unit-test-development.md`
3. **Store Policy** — update Stillwater Store criteria to require context-testable LLM steps
4. **Documentation** — publish patterns for context injection in technical blog posts
