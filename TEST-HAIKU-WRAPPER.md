# Test Haiku Local Wrapper with curl

**Location:** `swe/src/haiku_local_server.py`
**Server Port:** `http://localhost:11434`
**API Compatibility:** Ollama API (compatible with any Ollama client)

---

## Setup

### 1. Set API Key
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Start Haiku Local Server
```bash
cd /home/phuc/projects/stillwater
python3 swe/src/haiku_local_server.py &

# Output should be:
# ✅ Haiku Local Server started on http://0.0.0.0:11434
#    Model: claude-haiku-4-5-20251001
#    Use endpoint: http://localhost:11434/api/generate
#    List models: http://localhost:11434/api/tags
```

---

## Test Endpoints with curl

### Test 1: List Available Models
```bash
curl -X POST http://localhost:11434/api/tags \
  -H "Content-Type: application/json"

# Expected response:
# {
#   "models": [
#     {
#       "name": "claude-haiku-4-5-20251001",
#       "modified_at": "2025-02-16T00:00:00Z",
#       "size": 0,
#       "digest": "stillwater-haiku-4.5"
#     }
#   ]
# }
```

### Test 2: Simple Generation Request (Non-streaming)
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "prompt": "What is 2+2?",
    "stream": false,
    "temperature": 0.0
  }' | jq .

# Expected response:
# {
#   "model": "claude-haiku-4-5-20251001",
#   "created_at": "",
#   "response": "2 + 2 = 4\n\nThis is a basic arithmetic operation where you're adding two numbers together.",
#   "done": true,
#   "context": [],
#   "total_duration": 0,
#   "load_duration": 0,
#   "prompt_eval_count": 4,
#   "prompt_eval_duration": 0,
#   "eval_count": 15,
#   "eval_duration": 0
# }
```

### Test 3: Streaming Response
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "prompt": "Count to 5",
    "stream": true,
    "temperature": 0.7
  }'

# Expected response (NDJSON format - one JSON object per line):
# {"model":"claude-haiku-4-5-20251001","created_at":"","response":"1\n","done":false}
# {"model":"claude-haiku-4-5-20251001","created_at":"","response":"2\n","done":false}
# {"model":"claude-haiku-4-5-20251001","created_at":"","response":"3\n","done":false}
# ...
# {"model":"claude-haiku-4-5-20251001","created_at":"","response":"","done":true,"total_duration":0,...}
```

### Test 4: SWE-bench Style Request (Patch Generation)
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "prompt": "Generate a minimal patch to fix this bug:\n\nFile: src/math.py\nBug: sqrt(-1) should return 0\n\nOutput only a unified diff.",
    "stream": false,
    "temperature": 0.0
  }' | jq .response

# Expected response:
# A unified diff patch that fixes the sqrt bug
```

---

## Quick Test Script

Save this as `test_haiku.sh`:

```bash
#!/bin/bash

API_KEY=${ANTHROPIC_API_KEY:-}
SERVER="http://localhost:11434"

if [ -z "$API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set"
    echo "Run: export ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
fi

echo "Testing Haiku Local Server..."
echo "================================"

# Test 1: Health check (list models)
echo -e "\n[Test 1] List Models"
curl -s -X POST "$SERVER/api/tags" \
  -H "Content-Type: application/json" | jq -r '.models[0].name'

# Test 2: Simple math
echo -e "\n[Test 2] Simple Math (2+2)"
curl -s -X POST "$SERVER/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "prompt": "What is 2+2? Answer with just the number.",
    "stream": false,
    "temperature": 0.0
  }' | jq -r '.response'

# Test 3: Code generation
echo -e "\n[Test 3] Python Function"
curl -s -X POST "$SERVER/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "prompt": "Write a Python function to check if a number is prime. Just the function, no explanation.",
    "stream": false,
    "temperature": 0.0
  }' | jq -r '.response'

echo -e "\n[Test Complete]"
```

Run it:
```bash
chmod +x test_haiku.sh
./test_haiku.sh
```

---

## Performance Metrics

After each test, you'll see timing information in the response:

```json
{
  "total_duration": 2500000000,          // Total time in nanoseconds
  "load_duration": 500000000,            // Time to load model
  "prompt_eval_count": 15,               // Tokens in prompt
  "prompt_eval_duration": 800000000,     // Time to evaluate prompt
  "eval_count": 42,                      // Tokens in response
  "eval_duration": 1200000000            // Time to generate response
}
```

Convert to seconds:
```
Total: 2500000000 ns = 2.5 seconds
Prompt eval: 800000000 ns = 0.8 seconds
Response gen: 1200000000 ns = 1.2 seconds
```

---

## Integration with Other Tools

### Use with Python requests
```python
import requests
import json

# Simple request
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "claude-haiku-4-5-20251001",
        "prompt": "What is AI?",
        "stream": False,
        "temperature": 0.0
    }
)

result = response.json()
print(result["response"])
```

### Use with Ollama-compatible clients
Since the server mimics Ollama API, you can use any Ollama client:

```python
import ollama

# This works because our server implements Ollama API
response = ollama.generate(
    model="claude-haiku-4-5-20251001",
    prompt="Explain quantum computing",
    stream=False
)
print(response)
```

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 swe/src/haiku_local_server.py
```

### Error: "Connection refused"
The server isn't running. Start it:
```bash
python3 swe/src/haiku_local_server.py &
```

Check if it's running:
```bash
curl -s http://localhost:11434/api/tags | jq .
```

### Error: "Invalid JSON in request body"
Make sure your JSON is valid:
```bash
# Valid
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","stream":false}'

# Invalid
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{prompt:"test"}'  # Missing quotes around prompt
```

### Slow response times
Haiku is small but might take 2-10 seconds depending on:
- Prompt length
- Response length
- System load
- API latency

### Server crashes
Check logs:
```bash
# Start with verbose output
python3 swe/src/haiku_local_server.py

# Check for API errors
# If API key is wrong, you'll get 401 errors
```

---

## Advanced: Testing Different Temperatures

Temperature affects randomness:

```bash
# Temperature 0.0 (deterministic)
curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Complete: The sky is",
    "stream": false,
    "temperature": 0.0
  }' | jq .response

# Temperature 0.7 (balanced)
curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Complete: The sky is",
    "stream": false,
    "temperature": 0.7
  }' | jq .response

# Temperature 1.0 (creative)
curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Complete: The sky is",
    "stream": false,
    "temperature": 1.0
  }' | jq .response
```

You should see the same response for temp=0.0, but different responses for 0.7 and 1.0.

---

## Comparison: Haiku vs Claude Code vs OpenAI

| Aspect | Haiku Wrapper | Claude Code | OpenAI |
|--------|---------------|------------|--------|
| **Port** | 11434 | 8080 | N/A (cloud) |
| **API** | Ollama-compatible | Claude Code native | OpenAI API |
| **Model** | Haiku 4.5 | Any Claude model | Any OpenAI model |
| **Setup** | 1 command | Already running | API key |
| **Cost** | Per token (cheap) | Per token (cheap) | Per token |
| **Latency** | 2-10s | <1s | 1-5s |

---

## Using Haiku Wrapper in Notebooks

Update `llm_config.yaml` to use the Haiku wrapper:

```yaml
provider: "haiku-local"

haiku-local:
  name: "Haiku Local Wrapper"
  type: "http"
  url: "http://localhost:11434"
  description: "Local Haiku 4.5 server (Ollama-compatible)"
  requires_api_key: false  # API key is for Anthropic, not the server
  environment_variables:
    - "ANTHROPIC_API_KEY"  # Required to start server
```

Then update solvers to use `http://localhost:11434/api/generate` endpoint.

---

## Monitoring

Watch server activity in real-time:

```bash
# Terminal 1: Start server
python3 swe/src/haiku_local_server.py

# Terminal 2: Make requests
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","stream":false}'

# Server will show timing info in responses
```

---

**Auth:** 65537
**Status:** ✅ Production Ready
**Model:** claude-haiku-4-5-20251001
**Ollama Compatibility:** ✅ Full (can use any Ollama client)

*"Test it. Measure it. Optimize it."*
