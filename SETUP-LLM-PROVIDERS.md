# Stillwater OS - LLM Provider Setup Guide

**Auth:** 65537 | **Purpose:** Configure and switch between different LLM providers

All HOW-TO notebooks (SWE-bench, OOLONG, IMO) use the same centralized configuration system.

---

## Quick Start

### 1. Default (Claude Code - Local Server)

```bash
# Start Claude Code server on localhost:8080
claude-code server --host localhost --port 8080

# Run any notebook - it will connect to http://localhost:8080
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

**No API key required.** Configuration file: `llm_config.yaml` (provider: "claude-code")

---

## Switch Providers

Edit `llm_config.yaml` and change the `provider:` line, then set the appropriate API key:

### OpenAI

```yaml
provider: "openai"
```

```bash
export OPENAI_API_KEY=sk-...
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

**Models available:**
- `gpt-4o-mini` (default, faster, cheaper)
- `gpt-4` (classic)
- `gpt-4-turbo` (faster, cheaper GPT-4)
- `gpt-5` (when available)

---

### Anthropic Claude

```yaml
provider: "claude"
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

**Models available:**
- `claude-3-5-sonnet-20241022` (default, balanced)
- `claude-opus-4-1` (most powerful)
- `claude-3-haiku-20250307` (fastest)

---

### OpenRouter (100+ Models)

```yaml
provider: "openrouter"
```

```bash
export OPENROUTER_API_KEY=sk-or-...
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

**Why OpenRouter:**
- Access 100+ models via single API
- Mix and match models per task
- No vendor lock-in

**Models available:**
- `openai/gpt-4o`
- `openai/gpt-4-turbo`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-5-sonnet`
- `meta-llama/llama-3-70b-chat-hf`
- `deepseek/deepseek-r1` (reasoning model)
- Plus 90+ more

**Set different models:**

Edit `llm_config.yaml`:

```yaml
openrouter:
  model: "meta-llama/llama-3-70b-chat-hf"  # Change here
```

---

### TogetherAI

```yaml
provider: "togetherai"
```

```bash
export TOGETHER_API_KEY=...
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

**Models available:**
- `meta-llama/Llama-3-70b-chat-hf` (default)
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`

---

### Google Gemini

```yaml
provider: "gemini"
```

```bash
export GOOGLE_API_KEY=...
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

**Models available:**
- `gemini-2-0-pro` (default)
- `gemini-1-5-pro`
- `gemini-1-5-flash`

---

## Configuration File Structure

`llm_config.yaml`:

```yaml
# Active provider
provider: "claude-code"

# Each provider has a config section:
claude-code:
  name: "Claude Code (Local)"      # Display name
  type: "http"                      # Connection type: http or api
  url: "http://localhost:8080"      # Endpoint URL
  requires_api_key: false           # Whether API key needed
  environment_variables: []         # Required env vars

openai:
  name: "OpenAI"
  type: "api"
  url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"              # Default model
  requires_api_key: true
  environment_variables:
    - "OPENAI_API_KEY"
```

---

## Programmatic Switching (In Code)

```python
# In any Python script or notebook:

from src.llm_config_manager import get_llm_config, switch_llm_provider

# Check current config
config = get_llm_config()
config.print_status()

# Switch providers
switch_llm_provider("openai")
config.print_status()

# Get configuration details
print(f"URL: {config.get_provider_url()}")
print(f"Model: {config.get_provider_model()}")
print(f"Name: {config.get_provider_name()}")

# Validate setup
is_valid, msg = config.validate_setup()
print(msg)
```

---

## Notebooks Using This Configuration

All HOW-TO notebooks auto-load the configuration in their first cell:

```python
# Cell 1: Setup (in every HOW-TO notebook)
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.llm_config_manager import setup_llm_client_for_notebook, get_llm_url

# Initialize
llm_config = setup_llm_client_for_notebook()

# Use the URL in your solvers
llm_url = get_llm_url()
print(f"Using LLM: {llm_config['name']} at {llm_url}")
```

---

## Comparison Table

| Provider | Setup Time | API Key Cost | Best For | Speed | Quality |
|----------|-----------|------------|----------|-------|---------|
| **Claude Code** | 1 min | Free | Development, low latency | ⚡⚡⚡ | ★★★★★ |
| **OpenAI** | 2 min | $0.01-0.30/M | Production, most compatible | ⚡⚡⚡ | ★★★★★ |
| **Claude** | 2 min | $0.01-0.50/M | Production, best reasoning | ⚡⚡ | ★★★★★ |
| **OpenRouter** | 2 min | $0.01-0.50/M | Testing multiple models | ⚡⚡⚡ | ★★★★★ |
| **TogetherAI** | 2 min | $0.001-0.01/M | Open models, very cheap | ⚡⚡⚡⚡ | ★★★★ |
| **Gemini** | 2 min | Free-0.30/M | Google integration | ⚡⚡⚡ | ★★★★ |

---

## Troubleshooting

### "Missing API keys: OPENAI_API_KEY"

```bash
export OPENAI_API_KEY=sk-...
# Then restart notebook kernel
```

### "Cannot connect to localhost:8080"

Make sure Claude Code server is running:

```bash
claude-code server --host localhost --port 8080
```

Check it's running:

```bash
curl http://localhost:8080/
```

### Config file not found

Place `llm_config.yaml` in repository root:

```bash
# From notebook: /home/phuc/projects/stillwater/llm_config.yaml
# Config manager will find it automatically
```

### Want to use different model for each notebook?

Create separate config files:

```bash
cp llm_config.yaml llm_config_swe.yaml
cp llm_config.yaml llm_config_oolong.yaml

# Edit each file with different provider/model

# In notebook: config = LLMConfigManager("llm_config_swe.yaml")
```

---

## Advanced: Custom LLM Provider

To add a custom provider:

1. Edit `llm_config.yaml`:

```yaml
mycompany:
  name: "My Company LLM"
  type: "api"
  url: "https://api.mycompany.com/llm"
  model: "enterprise-model-v1"
  requires_api_key: true
  environment_variables:
    - "MYCOMPANY_API_KEY"
```

2. In your code:

```python
config = get_llm_config()
config.switch_provider("mycompany")
```

---

## Environment Variables Reference

```bash
# Claude Code (no API key)
# No env vars needed

# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter
export OPENROUTER_API_KEY=sk-or-...

# TogetherAI
export TOGETHER_API_KEY=...

# Google Gemini
export GOOGLE_API_KEY=...
```

Save to `.env` and load:

```bash
# In bash
set -a
source .env
set +a

# Or use python-dotenv
pip install python-dotenv
# In Python: from dotenv import load_dotenv; load_dotenv()
```

---

## Verification

To verify everything is set up correctly:

```python
from src.llm_config_manager import get_llm_config

config = get_llm_config()
config.print_status()

# Should output:
# ✅ Provider Name is configured
# Or: Missing API keys: OPENAI_API_KEY
```

---

**Auth:** 65537 | **Status:** Production Ready

*"One config to rule them all. Switch providers, not files."*
