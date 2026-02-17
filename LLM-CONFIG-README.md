# Stillwater OS - Centralized LLM Configuration System

**Auth:** 65537 | **Status:** Production Ready

All HOW-TO notebooks (SWE-bench, OOLONG, IMO) now use a **centralized configuration system** that makes it trivial to switch between different LLM providers.

---

## 🎯 Quick Start

### Default: Claude Code (Local Server)
```bash
# 1. Start Claude Code server
claude-code server --host localhost --port 8080

# 2. Run any HOW-TO notebook
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb

# 3. In the first cell, the configuration automatically loads from llm_config.yaml
# ✅ LLM Provider: Claude Code (Local) at http://localhost:8080
```

### Switch to OpenAI
```bash
# 1. Edit llm_config.yaml
# provider: "openai"

# 2. Set API key
export OPENAI_API_KEY=sk-...

# 3. Run notebook
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb

# 4. First cell will output:
# ✅ LLM Provider: OpenAI at https://api.openai.com/v1
```

### Switch to Anthropic Claude
```bash
# 1. Edit llm_config.yaml
# provider: "claude"

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run notebook
python3 -m jupyter notebook HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

---

## 📋 Configuration Files

### `llm_config.yaml` - Central Configuration
```yaml
provider: "claude-code"  # Active provider (change this to switch)

claude-code:           # Local Claude Code server
  url: "http://localhost:8080"
  requires_api_key: false

openai:                # OpenAI API
  url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  requires_api_key: true
  environment_variables: ["OPENAI_API_KEY"]

# ... plus 4 more providers: claude, openrouter, togetherai, gemini
```

**To switch:** Just change the `provider:` line in `llm_config.yaml`

### `src/llm_config_manager.py` - Configuration Manager
Python module that loads and manages the configuration.

```python
from src.llm_config_manager import (
    get_llm_config,              # Get config object
    get_llm_url,                 # Get active endpoint
    get_llm_provider,            # Get provider name
    switch_llm_provider,         # Switch providers
    setup_llm_client_for_notebook  # Initialize in notebooks
)
```

---

## 📚 Using in Notebooks

Every HOW-TO notebook now has a first cell that initializes the configuration:

```python
# Cell 0: Setup (AUTO-LOADED in all HOW-TO notebooks)
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from src.llm_config_manager import setup_llm_client_for_notebook, get_llm_config

# Initialize
llm_config = setup_llm_client_for_notebook()

# Output:
# ✅ LLM Provider initialized: Claude Code (Local)
#    Endpoint: http://localhost:8080
#    Status: ✅ Claude Code server is configured
```

**What this cell does:**
1. Loads `llm_config.yaml`
2. Initializes the active provider
3. Validates API keys (if needed)
4. Prints status
5. All subsequent code uses `get_llm_url()` to get the endpoint

---

## 🔄 Switching Providers

### Option 1: Edit Configuration File (Recommended)
```bash
# Edit llm_config.yaml
# Change: provider: "claude-code"
# To:     provider: "openai"

# Set API key
export OPENAI_API_KEY=sk-...

# Restart notebook kernel and re-run Cell 0
```

### Option 2: Programmatic Switching
```python
from src.llm_config_manager import switch_llm_provider, get_llm_config

# Switch provider
switch_llm_provider("openai")

# Verify
config = get_llm_config()
config.print_status()
```

### Option 3: Environment Variable Override
```python
# In notebook before importing config
import os
os.environ['ACTIVE_LLM_PROVIDER'] = 'claude'
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'

# Then initialize config
from src.llm_config_manager import setup_llm_client_for_notebook
llm_config = setup_llm_client_for_notebook()
```

---

## 📊 Supported Providers

| Provider | Setup | API Key | Speed | Cost | Best For |
|----------|-------|---------|-------|------|----------|
| **Claude Code** | 1 min | None | ⚡⚡⚡ | Free | Dev, no latency |
| **OpenAI** | 2 min | $0.01-0.30/M | ⚡⚡⚡ | Cheap | Production |
| **Claude** | 2 min | $0.01-0.50/M | ⚡⚡ | Cheap | Best reasoning |
| **OpenRouter** | 2 min | $0.01-0.50/M | ⚡⚡⚡ | Cheap | 100+ models |
| **TogetherAI** | 2 min | $0.001-0.01/M | ⚡⚡⚡⚡ | Cheapest | Open models |
| **Gemini** | 2 min | Free-0.30/M | ⚡⚡⚡ | Cheap | Google AI |

**Full setup details:** See `SETUP-LLM-PROVIDERS.md`

---

## 🎯 Notebooks Updated

All HOW-TO notebooks now use centralized configuration:

- ✅ `HOW-TO-CRUSH-SWE-BENCHMARK.ipynb` - Updated with Cell 0 setup
- ✅ `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` - Updated with Cell 0 setup
- ✅ `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb` - Updated with Cell 0 setup
- ✅ `swe/HOW-TO-CRUSH-SWE-BENCH-REAL.ipynb` - Updated with Cell 0 setup

Each notebook's first cell:
1. Loads the configuration manager
2. Initializes the active provider
3. Validates setup
4. Prints status and instructions

---

## 🔍 How It Works

### Configuration Loading Flow
```
1. Notebook Cell 0 runs
   ↓
2. Imports LLMConfigManager
   ↓
3. Manager searches for llm_config.yaml in:
   - Current directory
   - Parent directories
   - Repository root
   ↓
4. Loads YAML and parses configuration
   ↓
5. Reads 'provider:' value (default: "claude-code")
   ↓
6. Validates API keys if required
   ↓
7. Returns configuration dictionary:
   {
     "provider": "claude-code",
     "url": "http://localhost:8080",
     "name": "Claude Code (Local)",
     "model": "",
     "type": "http"
   }
   ↓
8. All subsequent code uses get_llm_url() to get endpoint
```

### Provider Resolution
```
llm_config.yaml
    ↓
    provider: "openai"
    ↓
Config["openai"]["url"] = "https://api.openai.com/v1"
Config["openai"]["model"] = "gpt-4o-mini"
Config["openai"]["requires_api_key"] = true
Config["openai"]["environment_variables"] = ["OPENAI_API_KEY"]
    ↓
Validator checks: os.environ.get("OPENAI_API_KEY")
    ↓
✅ "OpenAI is configured"  or  ❌ "Missing API keys: OPENAI_API_KEY"
```

---

## 🛠️ Configuration Manager API

### Functions

```python
from src.llm_config_manager import (
    get_llm_config,
    setup_llm_client_for_notebook,
    get_llm_url,
    get_llm_provider,
    switch_llm_provider
)

# Get configuration object
config = get_llm_config()

# Setup in notebook (handles all initialization)
llm_config = setup_llm_client_for_notebook()

# Get endpoint URL
url = get_llm_url()  # Returns "http://localhost:8080"

# Get provider name
provider = get_llm_provider()  # Returns "claude-code"

# Switch provider
switch_llm_provider("openai")
```

### Methods on Configuration Object

```python
config = get_llm_config()

config.get_provider_url()              # "http://localhost:8080"
config.get_provider_name()             # "Claude Code (Local)"
config.get_provider_model()            # ""
config.get_provider_type()             # "http"
config.requires_api_key()              # False
config.get_required_env_vars()         # []
config.validate_setup()                # (True, "✅ Claude Code is configured")
config.list_providers()                # Dict of all providers
config.print_status()                  # Print detailed status table
```

---

## 📝 Examples

### Example 1: Verify Configuration
```python
from src.llm_config_manager import get_llm_config

config = get_llm_config()
config.print_status()

# Output:
# ============================================================================
# LLM CONFIGURATION STATUS
# ============================================================================
#
# Active Provider: claude-code
# Provider Name: Claude Code (Local)
# URL/Endpoint: http://localhost:8080
# Status: ✅ Claude Code server is configured
#
# ────────────────────────────────────────────────────────────────────────
# Available Providers:
#   → claude-code           Claude Code (Local)      http://localhost:8080
#     openai                OpenAI                  https://api.openai.com/v1
#     claude                Anthropic Claude       https://api.anthropic.com/v1
#     openrouter            OpenRouter             https://openrouter.ai/api/v1
#     togetherai            TogetherAI             https://api.together.xyz
#     gemini                Google Gemini          https://generativelanguage.googleapis.com/v1beta/openai
```

### Example 2: Validate Setup Before Running
```python
from src.llm_config_manager import get_llm_config

config = get_llm_config()
is_valid, msg = config.validate_setup()

if not is_valid:
    print(f"❌ {msg}")
    print("Please set API key and restart kernel")
else:
    print(f"✅ {msg}")
    print("Ready to run notebook")
```

### Example 3: Runtime Provider Switching
```python
from src.llm_config_manager import switch_llm_provider, get_llm_url

# Start with default (Claude Code)
print(f"Using: {get_llm_url()}")

# Switch to OpenAI
switch_llm_provider("openai")
print(f"Now using: {get_llm_url()}")

# Switch to Claude
switch_llm_provider("claude")
print(f"Now using: {get_llm_url()}")
```

---

## 🚀 Benefits

✅ **Single Configuration Point** - Change `provider:` in one place, all notebooks use it

✅ **No Hardcoded URLs** - Endpoints come from configuration file, not notebooks

✅ **Easy Provider Switching** - Edit file, set API key, restart kernel

✅ **Validation Built-in** - Automatic API key checking

✅ **Flexible** - Works with 6+ providers out of the box

✅ **Extensible** - Add custom providers by editing config YAML

✅ **Production Ready** - Used in all benchmarks (SWE, OOLONG, IMO)

---

## 📦 What's Included

```
stillwater/
├── llm_config.yaml                 # Central configuration (edit this to switch)
├── SETUP-LLM-PROVIDERS.md          # Detailed provider setup guide
├── LLM-CONFIG-README.md            # This file
│
├── HOW-TO-CRUSH-SWE-BENCHMARK.ipynb        # Updated with Cell 0
├── HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb     # Updated with Cell 0
├── HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb        # Updated with Cell 0
├── swe/HOW-TO-CRUSH-SWE-BENCH-REAL.ipynb   # Updated with Cell 0
│
└── src/
    └── llm_config_manager.py       # Configuration manager (300+ lines)
```

---

## ✅ Verification

To verify the configuration system is working:

```python
# In any notebook, Cell 0 should output:
# ============================================================================
# INITIALIZING LLM CONFIGURATION
# ============================================================================
#
# ✅ LLM Provider initialized: Claude Code (Local)
#    Endpoint: http://localhost:8080
#    Status: ✅ Claude Code server is configured
#
# 📝 To change provider:
#    1. Edit llm_config.yaml (change 'provider:' line)
#    2. Export required API key (see SETUP-LLM-PROVIDERS.md)
#    3. Re-run this cell
# ============================================================================
```

If you see this, the configuration system is working.

---

## 🔧 Troubleshooting

### Error: "Configuration file not found"
```bash
# Ensure llm_config.yaml is in repo root
ls /home/phuc/projects/stillwater/llm_config.yaml

# Or in current directory when running notebook
pwd
ls llm_config.yaml
```

### Error: "Missing API keys: OPENAI_API_KEY"
```bash
export OPENAI_API_KEY=sk-...
# Then restart Jupyter kernel
```

### Error: "Cannot connect to Claude Code server"
```bash
# Start Claude Code server
claude-code server --host localhost --port 8080

# Verify it's running
curl http://localhost:8080/
```

### Different provider not loading
```bash
# Clear Jupyter kernel cache
# Restart kernel
# Re-run Cell 0

# Or programmatically:
import importlib
import sys
if 'src.llm_config_manager' in sys.modules:
    importlib.reload(sys.modules['src.llm_config_manager'])
```

---

## 📞 Support

See the detailed documentation:
- **Setup:** `SETUP-LLM-PROVIDERS.md` - How to configure each provider
- **API:** `src/llm_config_manager.py` - Full API documentation in docstrings
- **Config:** `llm_config.yaml` - All available providers and models

---

**Auth:** 65537 | **Status:** ✅ Production Ready

*"One config. Infinite providers. Zero friction."*
