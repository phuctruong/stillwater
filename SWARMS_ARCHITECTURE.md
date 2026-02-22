# Stillwater Swarms Architecture v3.0
## Simplified LLM Portal with Swarm-Driven Context Injection

Auth: 65537 | Date: 2026-02-22 | Status: IMPLEMENTED

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│  LLM Portal UI (http://localhost:8788)                         │
│  - Swarm Selector Dropdown                                    │
│  - Model Selector (haiku | sonnet | opus)                     │
│  - Prompt Input                                               │
│  - Response Display                                           │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│  Portal Backend: /api/swarm/invoke                             │
│  1. Load swarm metadata (YAML frontmatter)                     │
│  2. Load skill pack (prime-safety first)                       │
│  3. Load persona (if specified)                               │
│  4. Build system prompt (concatenate all)                      │
│  5. Prepend to user messages                                  │
│  6. Send to LLMClient → HTTPProvider → Wrapper                │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│  Claude Code Wrapper (http://localhost:8080)                   │
│  Ollama-compatible HTTP API                                   │
│  POST /api/generate accepts system + prompt                   │
└────────────────────────────────────────────────────────────────┘
                          ↓
                   claude CLI
                   (haiku/sonnet/opus)
```

---

## Components

### 1. Swarms (stillwater/swarms/*.md)

Each swarm is a YAML-fronted Markdown file defining:

```yaml
---
agent_type: coder
version: 1.0.0
authority: 65537
skill_pack:
  - prime-safety       # Always first
  - prime-coder        # Domain skill
  - persona-engine     # Optional
persona:
  primary: Donald Knuth
  alternatives:
    - Linus Torvalds
model_preferred: sonnet
rung_default: 641
artifacts:
  - PATCH_DIFF
  - tests.json
---

# Documentation below YAML frontmatter...
```

**34 available swarms:**
- coder, mathematician, planner, skeptic, judge
- forecaster, navigator, northstar-navigator
- coder, persona-coder, graph-designer
- citizen-council, eq-auditor, empath, conflict-resolver
- And 20+ more specialized agents

### 2. LLM Portal (admin/llm_portal_swarms.py)

**Simplified** to only handle swarms:
- No complex provider switching
- No skill/recipe/persona picker UI
- No CNF capsule injection
- Just: Swarm + Model + Prompt → Response

**Endpoints:**
- `GET /` - Web UI (swarm selector)
- `GET /api/health` - Health check
- `GET /api/swarms` - List all swarms
- `GET /api/swarm/{name}` - Get swarm metadata
- `POST /api/swarm/invoke` - Invoke swarm

**Request format:**
```json
{
  "swarm_name": "coder",
  "model": "haiku",
  "prompt": "Fix the bug in auth.py",
  "temperature": 0.0,
  "max_tokens": 4096
}
```

**Response format:**
```json
{
  "id": "sw-abc123def456",
  "swarm": "coder",
  "model": "haiku",
  "response": "The bug is in line 42...",
  "metadata": {
    "latency_ms": 2345,
    "skill_pack": ["prime-safety", "prime-coder"],
    "system_prompt_chars": 5000,
    "rung_default": 641
  }
}
```

### 3. Claude Code Wrapper (cli/src/claude_code_wrapper.py)

**Updated** to support optional system prompts:

```json
POST /api/generate
{
  "prompt": "user: Fix this bug",
  "system": "## SKILL: prime-coder\n...",
  "stream": false,
  "temperature": 0.0,
  "max_tokens": 4096
}
```

The wrapper prepends system to prompt:
```
full_prompt = system + "\n\n" + prompt
claude --model haiku -p "full_prompt"
```

### 4. CLAUDE.md (Project Context)

**Now intentionally blank.**

All context comes from swarms, not CLAUDE.md. This gives:
- ✅ Full control over context per task
- ✅ Clean separation: swarms define context
- ✅ Easy swapping of skills/personas
- ✅ No legacy context overhead

---

## Context Injection Flow

**Example: Invoke "coder" swarm with "fix auth bug"**

1. **Portal receives request:**
   ```
   swarm_name: "coder"
   model: "haiku"
   prompt: "Fix the authentication bug in login.py"
   ```

2. **Portal loads swarm metadata:**
   ```yaml
   skill_pack:
     - prime-safety
     - prime-coder
     - persona-engine
   persona:
     primary: Donald Knuth
   ```

3. **Portal loads skill pack:**
   - Reads `skills/prime-safety.md` (QUICK LOAD block)
   - Reads `skills/prime-coder.md` (QUICK LOAD block)
   - Reads `skills/persona-engine.md` (QUICK LOAD block)

4. **Portal loads persona:**
   - Reads `personas/donald-knuth.md` (QUICK LOAD block)

5. **Portal builds system prompt:**
   ```
   ## SKILL: prime-safety
   [content...]

   ---

   ## SKILL: prime-coder
   [content...]

   ---

   ## PERSONA: Donald Knuth
   [content...]
   ```

6. **Portal builds messages:**
   ```json
   [
     {
       "role": "system",
       "content": "[full system prompt above]"
     },
     {
       "role": "user",
       "content": "Fix the authentication bug in login.py"
     }
   ]
   ```

7. **Portal calls LLMClient:**
   ```python
   client.chat(messages, model="haiku", temperature=0.0)
   ```

8. **LLMClient routes to HTTPProvider:**
   - Extracts system message
   - Builds payload with system + prompt

9. **HTTPProvider calls wrapper:**
   ```json
   {
     "system": "[full skill pack + persona]",
     "prompt": "user: Fix the authentication bug..."
   }
   ```

10. **Wrapper prepends and calls Claude:**
    ```bash
    claude --model haiku -p "[system]\n\n[prompt]"
    ```

11. **Response flows back** through portal

---

## Unit Tests

**Location:** `admin/tests/swarms/`

**Test Coverage:**
- 34 swarms
- 2 test variants each (A: factual, B: domain-specific)
- Metadata validation
- Skill/persona existence checks
- Invocation tests with haiku

**Test Classes:**
- `TestSwarmMetadata` - Validate YAML structure
- `TestSwarmSkills` - Verify skill files exist
- `TestSwarmPersonas` - Verify persona files exist
- `TestSwarmInvocation` - Invoke with test prompts
- `TestSwarmConsistency` - Test deterministic behavior

**Running Tests:**
```bash
# All tests
pytest admin/tests/swarms/test_swarms.py -v

# Specific swarm
pytest admin/tests/swarms/test_swarms.py -k "coder" -v

# With setup
bash admin/tests/swarms/run_tests.sh --setup
```

---

## Benefits of This Architecture

### 1. **Simplicity**
- Portal does ONE thing: load swarm → inject context → call LLM
- No complex routing logic
- No provider switching UI clutter

### 2. **Control**
- Each swarm explicitly declares its skill pack
- Each swarm declares its preferred persona
- Each swarm declares its rung level
- No surprise context loading

### 3. **Flexibility**
- Add new swarms without portal changes
- Modify swarm context by editing YAML frontmatter
- Easy to version swarms (version field in metadata)

### 4. **Testability**
- Unit tests for all 34 swarms
- Metadata validation tests
- Invocation tests with both variants
- Consistency tests

### 5. **Scalability**
- Portal code <500 lines
- Easy to add new swarms (just create .md file)
- Easy to create new skills (just reference in swarm)
- Easy to create new personas (just reference in swarm)

---

## Extending the System

### Adding a New Swarm

1. Create `stillwater/swarms/my-swarm.md`:
```yaml
---
agent_type: my-agent
version: 1.0.0
authority: 65537
skill_pack:
  - prime-safety
  - prime-coder
model_preferred: sonnet
rung_default: 641
---

# Documentation here...
```

2. Tests automatically pick it up
3. Portal UI automatically lists it

### Adding a New Skill

1. Create `stillwater/skills/my-skill.md`
2. Reference in swarm `skill_pack`
3. Portal loads it automatically

### Modifying a Swarm's Context

1. Edit swarm YAML metadata
2. Change `skill_pack`, `persona`, `model_preferred`
3. Next invocation uses new context

---

## Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Portal | ✅ Running | Swarms-only, simplified |
| Wrapper | ✅ Running | Supports system prompts |
| CLAUDE.md | ✅ Blank | Context from swarms only |
| Unit Tests | ✅ Created | 34 swarms × 2 variants |
| Web UI | ✅ Working | Swarm selector + chat |
| Skill Loading | ✅ Working | QUICK LOAD extraction |
| Persona Loading | ✅ Working | QUICK LOAD extraction |

---

## Next Steps (Optional)

1. **Run full test suite** with all 34 swarms
2. **Add integration tests** for high-rung swarms
3. **Create swarm variants** (coder-fast, coder-thorough)
4. **Build skill registry** with metadata
5. **Add swarm versioning** and rollback capability

---

## See Also

- `admin/llm_portal_swarms.py` - Portal implementation
- `admin/tests/swarms/test_swarms.py` - Test suite
- `admin/tests/swarms/run_tests.sh` - Test runner
- `admin/tests/swarms/README.md` - Detailed test docs
- `swarms/*.md` - All swarms
- `skills/*.md` - All skills
- `personas/` - All personas
