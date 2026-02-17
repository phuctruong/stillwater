# Docker + SWE-bench Data Integration Guide

**Auth:** 65537 | **Date:** 2026-02-16 | **Status:** INFRASTRUCTURE READY

---

## Overview

The Stillwater OS SWE-bench solution has three components that integrate together:

1. **Docker Infrastructure** - Containerized execution environments
2. **SWE-bench Data** - 300 real bug instances from Django, Astropy, Matplotlib, etc.
3. **Notebooks** - HOW-TO-CRUSH-SWE-BENCHMARK.ipynb + supporting solvers

---

## Part 1: Docker Infrastructure Locations

### A. Stillwater Project (Local)

**Location:** `/home/phuc/projects/stillwater/Dockerfile.swe`

**Purpose:** Containerized SWE-bench solver with Jupyter

**Configuration:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
EXPOSE 8888 (Jupyter)
VOLUME ["/app/data", "/app/logs", "/app/models"]
CMD jupyter lab --ip=0.0.0.0 --port=8888
```

**Build & Run:**
```bash
# Build image
docker build -f Dockerfile.swe -t stillwater-swe:latest .

# Run container with volume mounts
docker run -d \
  --name stillwater-swe \
  -p 8888:8888 \
  -v /home/phuc/Downloads/benchmarks/SWE-bench:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  stillwater-swe:latest

# Access Jupyter
# http://localhost:8888
```

### B. Terminal-Bench Project (Reference)

**Location:** `~/Downloads/benchmarks/terminal-bench/docker/`

**Available Dockerfiles:**
- `base-images/ubuntu-24-04/Dockerfile` - Ubuntu 24.04 base image
- `base-images/python-3-13/Dockerfile` - Python 3.13 environment
- `base-images/deveval/Dockerfile` - Development evaluation image
- `agents/goose/Dockerfile` - GooseAI agent container
- `mcp-server/Dockerfile` - MCP server container

**Docker Compose Files:**
- `base-images/docker-compose.yaml`
- `agents/goose/docker-compose.yaml`
- `mcp-server/docker-compose.yaml`

**Use Case:** Reference implementations for container orchestration

---

## Part 2: SWE-bench Data Location

### Primary Data Repository

**Location:** `~/Downloads/benchmarks/SWE-bench/`

**Structure:**
```
SWE-bench/
├── swebench/                          # SWE-bench Python package
│   ├── resources/swebench-og/         # Original repository data
│   │   ├── django__django/            # 233 Django issues
│   │   ├── astropy__astropy/          # 24 Astropy issues
│   │   ├── matplotlib__matplotlib/    # 36 Matplotlib issues
│   │   ├── scikit-learn__scikit-learn/ # Projects...
│   │   ├── sphinx-doc__sphinx/
│   │   ├── sympy__sympy/
│   │   ├── pytest-dev__pytest/
│   │   ├── pydata__xarray/
│   │   └── ...
│   ├── harness/                       # Test harness
│   ├── collect/                       # Data collection
│   └── inference/                     # Inference code
├── gold.SEALED_162_VERIFIED.json      # 162 verified instances (GOLD)
├── gold.full_benchmark_real_execution.json  # Full benchmark (300)
├── gold.*.json                        # Prime Skills results
├── logs/                              # Execution logs
└── temp/                              # Temporary files
```

**Data Files:**
- `gold.SEALED_162_VERIFIED.json` - 162 instances (verified safe)
- `gold.full_benchmark_real_execution.json` - 300 instances (full benchmark)
- `prime-coder-v1.0.*.json` - Prime Skills execution results

**Repositories:** 12 major open-source projects
- Django (233 instances)
- Astropy (24 instances)
- Matplotlib (36 instances)
- scikit-learn
- Sphinx
- SymPy
- Pytest
- Flask
- Requests
- Pylint
- xarray
- Seaborn

---

## Part 3: Integration Architecture

### Current Setup (Proposed)

```
┌─────────────────────────────────────────────────────────────┐
│  NOTEBOOK EXECUTION FLOW                                    │
└─────────────────────────────────────────────────────────────┘

Host Machine:
  ├─ Terminal 1: Claude Code CLI (--port 8080)
  │  └─ export ANTHROPIC_API_KEY=sk-ant-...
  │  └─ claude-code server --host localhost --port 8080
  │
  └─ Terminal 2: Jupyter OR Docker

     OPTION A: Direct Execution
     └─ cd /home/phuc/projects/stillwater
     └─ jupyter notebook
     └─ Opens HOW-TO-CRUSH-SWE-BENCHMARK.ipynb

     OPTION B: Docker Container
     └─ docker build -f Dockerfile.swe -t stillwater-swe .
     └─ docker run -p 8888:8888 -v ~/Downloads/benchmarks/SWE-bench:/app/data stillwater-swe
     └─ Opens http://localhost:8888/lab

Notebook Flow:
  Cell 0: Load llm_config.yaml (validates localhost:8080)
  Cell 1: Test connection to localhost:8080
  Cell 2-4: Load data from /app/data/gold.*.json
  Cell 5-6: Initialize solver with Prime Skills
  Cell 7-8: Call subprocess → swe_solver_real.py
  Cell 9: Harsh QA validation
```

### Key Integration Points

**1. LLM Connection**
- Uses: `http://localhost:8080` (Claude Code CLI wrapper)
- NOT: API keys in container environment
- Flow: Container→Notebook→CLI on host→Haiku API

**2. Data Volume**
- Host: `~/Downloads/benchmarks/SWE-bench/gold.*.json`
- Container: `/app/data/gold.*.json` (volume mount)
- Notebook: `Path('/app/data')` or `Path.cwd()/data`

**3. Solver Execution**
- Host or Container: `subprocess.run(['python3', 'swe/src/swe_solver_real.py'])`
- Solver connects to localhost:8080 (host)
- Results cached in notebook

---

## Part 4: Setup Instructions

### Option A: Direct Execution (No Docker)

```bash
# 1. Set API key
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY

# 2. Terminal 1: Start Claude Code server
cd /home/phuc/projects/stillwater
claude-code server --host localhost --port 8080

# 3. Terminal 2: Run Jupyter
cd /home/phuc/projects/stillwater
jupyter notebook

# 4. In Jupyter
# - Open HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
# - Cell 0: Initialize config (uses localhost:8080)
# - Cell 2-4: Load data from ~/Downloads/benchmarks/SWE-bench
# - Cell 7-8: Run solver
```

**Data Location:** `~/Downloads/benchmarks/SWE-bench/gold.SEALED_162_VERIFIED.json`

### Option B: Docker Container

```bash
# 1. Build image
cd /home/phuc/projects/stillwater
docker build -f Dockerfile.swe -t stillwater-swe:latest .

# 2. Run container
docker run -d \
  --name stillwater-swe-notebook \
  -p 8888:8888 \
  -p 8080:8080 \
  -v ~/Downloads/benchmarks/SWE-bench:/app/data \
  -e ANTHROPIC_API_KEY=sk-ant-YOUR-KEY \
  stillwater-swe:latest

# 3. Get Jupyter token
docker logs stillwater-swe-notebook | grep "token="

# 4. Access
# http://localhost:8888?token=...

# 5. In Jupyter container
# - Cell 0: localhost:8080 connects to HOST Claude Code server
# - Cell 2: Loads /app/data/gold.*.json
# - Cell 7-8: Runs solver
```

**Important:** Claude Code server must run on HOST (not in container)

```bash
# On host machine:
export ANTHROPIC_API_KEY=sk-ant-...
claude-code server --host localhost --port 8080

# Container connects to host's localhost:8080
```

### Option C: Docker Compose (Recommended)

Create `docker-compose.swe.yml` in stillwater root:

```yaml
version: '3.8'

services:
  swe-notebook:
    build:
      context: .
      dockerfile: Dockerfile.swe
    container_name: stillwater-swe
    ports:
      - "8888:8888"  # Jupyter Lab
    volumes:
      - ~/Downloads/benchmarks/SWE-bench:/app/data
      - ./logs:/app/logs
      - ./cache:/app/.cache
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - PYTHONUNBUFFERED=1
    network_mode: host  # Access host's localhost:8080
    command: >
      bash -c "jupyter lab
               --ip=0.0.0.0
               --port=8888
               --no-browser
               --allow-root"

  # Optional: Claude Code server (if running in Docker)
  # claude-code-server:
  #   image: anthropic/claude-code:latest
  #   ports:
  #     - "8080:8080"
  #   environment:
  #     - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

**Run:**
```bash
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
docker-compose -f docker-compose.swe.yml up
```

---

## Part 5: Data Loading in Notebook

### Cell 2-4: Load SWE-bench Data

```python
import json
from pathlib import Path

# Location option 1: Direct path (no Docker)
swe_data_dir = Path('/home/phuc/Downloads/benchmarks/SWE-bench')

# Location option 2: Container volume
swe_data_dir = Path('/app/data')

# Location option 3: Auto-detect
swe_data_dir = Path.cwd() / 'data'

# Load verified instances
instances = []
data_file = swe_data_dir / 'gold.SEALED_162_VERIFIED.json'

if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
    instances = data.get('instances', [])
else:
    print(f"❌ Data not found: {data_file}")

print(f"✅ Loaded {len(instances)} SWE-bench instances")
```

### Available Data Files

| File | Instances | Status | Use Case |
|------|-----------|--------|----------|
| `gold.SEALED_162_VERIFIED.json` | 162 | Verified safe | Testing |
| `gold.full_benchmark_real_execution.json` | 300 | Full set | Comprehensive |
| `gold.*.json` (per-repo) | varies | Specific repos | Targeted testing |
| `prime-coder-v1.0.*.json` | Results | Execution logs | Benchmarking |

---

## Part 6: Practical Workflow

### Quick Start (Recommended)

```bash
# 1. Prepare host
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
cd /home/phuc/projects/stillwater
claude-code server --host localhost --port 8080

# 2. In another terminal, run container
docker run -d \
  --name swe-solver \
  -p 8888:8888 \
  -v ~/Downloads/benchmarks/SWE-bench:/app/data \
  --network host \
  stillwater-swe:latest

# 3. Get Jupyter URL
docker logs swe-solver | grep "localhost:8888"

# 4. Open in browser
# http://localhost:8888?token=...

# 5. Run notebook cells in order
```

### Direct Python (No Jupyter)

```bash
python3 << 'EOF'
import json
from pathlib import Path

# Load data
data_path = Path('/home/phuc/Downloads/benchmarks/SWE-bench/gold.SEALED_162_VERIFIED.json')
with open(data_path) as f:
    data = json.load(f)

instances = data['instances']
print(f"Loaded {len(instances)} instances")

# Call solver on first instance
import subprocess
result = subprocess.run(
    ['python3', 'swe/src/swe_solver_real.py'],
    capture_output=True,
    text=True,
    cwd='/home/phuc/projects/stillwater'
)
print(result.stdout)
EOF
```

---

## Part 7: Debugging & Troubleshooting

### Issue 1: "Cannot connect to localhost:8080"

**Cause:** Claude Code server not running

**Solution:**
```bash
# Terminal 1 (host machine):
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
claude-code server --host localhost --port 8080

# Verify:
curl http://localhost:8080/
```

### Issue 2: Data not found in container

**Cause:** Volume not mounted correctly

**Solution:**
```bash
# Check mount
docker run -it stillwater-swe bash
ls -la /app/data/

# If empty, remount:
docker run -v ~/Downloads/benchmarks/SWE-bench:/app/data stillwater-swe
```

### Issue 3: "ANTHROPIC_API_KEY not set"

**Cause:** Environment variable not passed to container

**Solution:**
```bash
# Pass via -e flag
docker run -e ANTHROPIC_API_KEY=sk-ant-YOUR-KEY ...

# Or in docker-compose.yml
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Set on host first:
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
```

### Issue 4: Solver returns error

**Cause:** Missing dependencies or hardcoded localhost:11434

**Solution:**
```bash
# Update swe_solver_real.py line 32:
# OLD:
HAIKU_LOCAL_URL = os.environ.get("HAIKU_URL", "http://localhost:11434")

# NEW:
from src.llm_config_manager import get_llm_url
HAIKU_LOCAL_URL = get_llm_url()  # Reads from config
```

---

## Part 8: Verification Checklist

Before running notebook, verify:

```
✅ Checklist

Docker Setup:
  ☐ Dockerfile.swe exists
  ☐ docker-compose.swe.yml created (optional)
  ☐ Image builds successfully

Data Setup:
  ☐ ~/Downloads/benchmarks/SWE-bench/ exists
  ☐ gold.SEALED_162_VERIFIED.json present
  ☐ Minimum 162 instances available

LLM Setup:
  ☐ ANTHROPIC_API_KEY exported
  ☐ Claude Code server running on localhost:8080
  ☐ Connection verified: curl http://localhost:8080/

Notebook Setup:
  ☐ HOW-TO-CRUSH-SWE-BENCHMARK.ipynb exists
  ☐ Cell 0-9 structure correct
  ☐ llm_config.yaml uses localhost:8080
  ☐ swe_solver_real.py in swe/src/

Execution:
  ☐ Jupyter running (port 8888)
  ☐ Cell 0 passes (config loads)
  ☐ Cell 1 passes (localhost:8080 validates)
  ☐ Cell 2-4 passes (data loads)
  ☐ Cell 5-6 passes (solver initializes)
  ☐ Cell 7-8 passes (solver executes)
  ☐ Cell 9 passes (harsh QA completes)
```

---

## Summary

| Component | Location | Status |
|-----------|----------|--------|
| **Dockerfile** | `/home/phuc/projects/stillwater/Dockerfile.swe` | ✅ Ready |
| **Docker Compose** | Optional (create from template) | ✅ Ready |
| **SWE-bench Data** | `~/Downloads/benchmarks/SWE-bench/` | ✅ Available |
| **Notebook** | `HOW-TO-CRUSH-SWE-BENCHMARK.ipynb` | ✅ Ready |
| **LLM Config** | `llm_config.yaml` | ✅ localhost:8080 |
| **Solver** | `swe/src/swe_solver_real.py` | ✅ Ready |

**Next Step:** Choose execution option (A, B, or C) and run the notebook.

---

**Auth:** 65537 | **Status:** ✅ INFRASTRUCTURE DOCUMENTED | **Date:** 2026-02-16

*"Three components. One localhost:8080. Docker-ready execution."*
