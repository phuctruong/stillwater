# HOW-TO-CRUSH-SWE-BENCHMARK.ipynb Integration Analysis

**Status:** ⚠️ CONFIGURATION MISMATCH DETECTED
**Date:** 2026-02-17
**Issues Found:** 2 critical mismatches to resolve

---

## Summary

| Aspect | Finding | Status |
|--------|---------|--------|
| **Notebook URL** | localhost:8080 (from llm_config.yaml) | ✅ Correct |
| **Solver URL** | localhost:11434 (hardcoded in swe_solver_real.py) | ⚠️ **MISMATCH** |
| **Data Path** | /home/phuc/Downloads/benchmarks/SWE-bench/data/ | ❌ **DOESN'T EXIST** |
| **Instances Loaded** | 0 real instances (demo loads 6 max, tests 1) | ⚠️ Demo mode |
| **Overall Status** | Notebook framework correct, but solver not integrated | ⚠️ **NEEDS FIX** |

---

## Issue 1: URL Mismatch (Critical)

### Notebook Configuration (Cell 0)
```python
from src.llm_config_manager import setup_llm_client_for_notebook, get_llm_url

llm_config = setup_llm_client_for_notebook()
print(f"✅ LLM Provider initialized: {llm_config['name']}")
print(f"   Endpoint: {llm_config['url']}")
```

**Output:**
```
✅ LLM Provider initialized: Claude Code (Local Server)
   Endpoint: http://localhost:8080
```

**Source:** `llm_config.yaml`
```yaml
type: "http"
url: "http://localhost:8080"
name: "Claude Code (Local Server)"
```

### Solver Configuration (swe_solver_real.py, line 32)
```python
HAIKU_LOCAL_URL = os.environ.get("HAIKU_URL", "http://localhost:11434")
```

**Problem:**
- Notebook says: `http://localhost:8080`
- Solver defaults to: `http://localhost:11434` (Ollama port)
- Environment variable `HAIKU_URL` NOT set by notebook
- Result: **Solver ignores notebook configuration**

### Impact
```
Notebook Cell 6: Prints "Endpoint: http://localhost:8080"
                ↓
Notebook Cell 8: Calls subprocess.run(['python3', 'swe/src/swe_solver_real.py'])
                ↓
swe_solver_real.py: Reads HAIKU_URL env var (not set)
                ↓
                Uses hardcoded default: http://localhost:11434
                ↓
                MISMATCH! Tries to connect to wrong port
```

### Fix Needed
**Option 1: Notebook passes environment variable**
```python
# Cell 8: Before subprocess.run()
import os
env = os.environ.copy()
env['HAIKU_URL'] = llm_config['url']

result = subprocess.run(
    ['python3', 'swe/src/swe_solver_real.py'],
    capture_output=True,
    text=True,
    cwd=Path.cwd(),
    timeout=60,
    env=env  # ← Pass environment with HAIKU_URL
)
```

**Option 2: Solver reads configuration file**
```python
# swe/src/swe_solver_real.py
from src.llm_config_manager import get_llm_config

config = get_llm_config()
HAIKU_LOCAL_URL = config.get('url', 'http://localhost:11434')
```

**Option 3: Use Claude Code wrapper instead**
```python
# swe/src/swe_solver_real.py
from src.claude_code_wrapper import ClaudeCodeWrapper

class SWEBenchSolverReal:
    def __init__(self):
        self.wrapper = ClaudeCodeWrapper()  # Uses localhost:8080
        self.endpoint = self.wrapper.localhost_url
```

---

## Issue 2: Missing Data Directory (Critical)

### Expected Path
```
/home/phuc/Downloads/benchmarks/SWE-bench/data/
```

### Actual Status
```bash
$ ls /home/phuc/Downloads/benchmarks/SWE-bench/data/
ls: cannot access '/home/phuc/Downloads/benchmarks/SWE-bench/data/': No such file or directory
```

### Notebook Impact (Cell 4)
```python
swe_data_dir = Path('/home/phuc/Downloads/benchmarks/SWE-bench/data')

instances = []
if swe_data_dir.exists():
    for jsonl_file in sorted(swe_data_dir.glob('*.jsonl'))[:3]:
        with open(jsonl_file) as f:
            for i, line in enumerate(f):
                if i < 2:
                    data = json.loads(line)
                    instances.append(data)

print(f'✅ Loaded {len(instances)} SWE-bench instances')
```

**Actual Result:**
```
✅ Loaded 0 SWE-bench instances
```

### Why No Data?
1. Cell 4 looks for JSONL files in `/home/phuc/Downloads/benchmarks/SWE-bench/data/`
2. Directory doesn't exist
3. Code uses `if swe_data_dir.exists():` - silently returns 0 instances
4. Cell 8 tests only `instances[0]` if available, but `instances` list is empty

### Fix Needed
**Option 1: Create symlink to actual data**
```bash
mkdir -p /home/phuc/Downloads/benchmarks/SWE-bench/data
# Then copy/symlink actual JSONL files there
```

**Option 2: Update notebook to use actual data location**
```python
# Cell 4: Find actual data location
import subprocess
result = subprocess.run(['find', '/home/phuc/Downloads/benchmarks/SWE-bench',
                         '-name', '*.json', '-o', '-name', '*.jsonl'],
                        capture_output=True, text=True)
# Use first 3 files found
```

**Option 3: Load from swebench package**
```python
from swebench import get_resolved_instances

instances = get_resolved_instances(split='lite')[:6]
```

---

## Current Notebook Flow

### What Happens Now (Demo Mode)

```
Cell 0: Initialize config
├─ Loads: llm_config.yaml
├─ Validates: localhost:8080 ✅
└─ Status: "Claude Code (Local Server) at http://localhost:8080"

Cell 1: Test connection
├─ Tries: requests.get('http://localhost:8080/')
└─ Result: Connection check (passes if server running)

Cell 2: Load SWE-bench data
├─ Looks for: /home/phuc/Downloads/benchmarks/SWE-bench/data/
├─ Files found: 0 ❌
└─ Instances loaded: 0

Cell 3: Section header

Cell 4: More configuration info
└─ (Duplicate of Cell 0)

Cell 5: Load solver capabilities
└─ Prints: Solver info

Cell 6: Initialize solver
├─ Calls: subprocess.run(['python3', 'swe/src/swe_solver_real.py'])
├─ Solver defaults to: http://localhost:11434 ⚠️
└─ Mismatch with: http://localhost:8080

Cell 7: Section header

Cell 8: Test on instances
├─ Checks: if instances (empty list)
├─ Result: ⚠️  No instances loaded
└─ Skips actual testing

Cell 9: QA validation
└─ Asks/answers questions about features
```

### Expected Flow (When Fixed)

```
Cell 0: Initialize config
├─ Loads: llm_config.yaml
├─ Validates: localhost:8080 ✅
└─ Status: "Claude Code (Local Server) at http://localhost:8080"

Cell 1: Test connection ✅

Cell 2: Load SWE-bench data
├─ Looks for: /home/phuc/Downloads/benchmarks/SWE-bench/data/
├─ Files found: 3+ ✅
└─ Instances loaded: 6+ ✅

Cell 6: Initialize solver
├─ Sets: env['HAIKU_URL'] = 'http://localhost:8080' ✅
├─ Calls: subprocess.run(..., env=env)
├─ Solver uses: http://localhost:8080 ✅
└─ Matches: Notebook config ✅

Cell 8: Test on instances
├─ Checks: if instances (populated list)
├─ Runs: Solver on first instance ✅
├─ Gets: Patch generation results
└─ Shows: RED-GREEN gate verification ✅
```

---

## Detailed Analysis

### Notebook Architecture (Correct ✅)

```
Cell 0: Load llm_config.yaml
    ↓ type: "http", url: "http://localhost:8080"
    ↓ (Also supports: OpenAI, Claude, OpenRouter, etc.)

Cell 1: Validate HTTP connection
    ↓ requests.get('http://localhost:8080/') → 200 OK

Cell 2-8: Test solver
    ├─ Load SWE-bench instances (missing data directory ⚠️)
    ├─ Call solver subprocess
    ├─ Display results
    └─ Generate certificates
```

### Solver Architecture (Needs Fix ⚠️)

**Current (Broken):**
```python
# swe/src/swe_solver_real.py line 32
HAIKU_LOCAL_URL = os.environ.get("HAIKU_URL", "http://localhost:11434")
                                                     ↑ MISMATCH!
# Uses Ollama default port instead of notebook's 8080
```

**Needed:**
```python
# Option A: Accept environment variable from notebook
HAIKU_LOCAL_URL = os.environ.get("HAIKU_URL", "http://localhost:8080")
                                                     ↑ Match notebook default

# Option B: Read from config file
from src.llm_config_manager import get_llm_config
config = get_llm_config()
HAIKU_LOCAL_URL = config.get('url', 'http://localhost:8080')

# Option C: Use ClaudeCodeWrapper directly
from src.claude_code_wrapper import ClaudeCodeWrapper
wrapper = ClaudeCodeWrapper()  # Uses 8080 automatically
```

---

## Instance Count Analysis

### Cell 4: Data Loading Code
```python
swe_data_dir = Path('/home/phuc/Downloads/benchmarks/SWE-bench/data')

instances = []
if swe_data_dir.exists():
    for jsonl_file in sorted(swe_data_dir.glob('*.jsonl'))[:3]:  # ← Load first 3 files
        with open(jsonl_file) as f:
            for i, line in enumerate(f):
                if i < 2:  # ← Load first 2 instances per file
                    data = json.loads(line)
                    instances.append(data)
```

**Theoretical Maximum:**
- Files to load: 3 (hardcoded [:3])
- Instances per file: 2 (hardcoded if i < 2)
- **Max instances loaded: 6**

### Cell 8: Solver Testing Code
```python
if instances:
    instance_data = instances[0]  # ← Test only first instance
    print(f"Testing on: {instance_data.get('instance_id')}")

    result = subprocess.run(
        ['python3', 'swe/src/swe_solver_real.py'],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
        timeout=60
    )
```

**Actual Execution:**
- Instances loaded: **0** (data directory doesn't exist)
- Instances tested: **0** (empty list, if block skipped)
- Result: No testing happens ⚠️

---

## Three Notebooks Comparison

| Aspect | OOLONG | Math Olympiad | SWE-Bench |
|--------|--------|---------------|-----------|
| **Cell 0 Config** | ✅ Works | ✅ Works | ✅ Works |
| **Uses localhost:8080** | ✅ Yes (via wrapper) | ✅ Yes (via wrapper) | ⚠️ **Config says 8080, solver uses 11434** |
| **Imports wrapper** | ✅ oolong_solver_real.py | ✅ imo_solver_real.py | ❌ swe_solver_real.py doesn't import wrapper |
| **Calls wrapper methods** | ✅ query(), solve_counting() | ✅ solve_math(), query() | ❌ Uses raw HTTP requests instead |
| **Data source** | Tests hardcoded | Tests hardcoded | Tries to load from disk |
| **Instances run** | 4 hardcoded tests | 6 hardcoded problems | 0 (data missing) |
| **Status** | ✅ VERIFIED | ✅ VERIFIED | ⚠️ **NEEDS FIX** |

---

## How to Fix SWE Notebook

### Fix 1: Update swe_solver_real.py to use ClaudeCodeWrapper

**Current (Lines 32, 66-69):**
```python
HAIKU_LOCAL_URL = os.environ.get("HAIKU_URL", "http://localhost:11434")

class SWEBenchSolverReal:
    def __init__(self, haiku_url: str = HAIKU_LOCAL_URL):
        self.haiku_url = haiku_url
        self.endpoint = f"{haiku_url}/api/generate"
```

**Better (Unified with OOLONG/IMO):**
```python
from src.claude_code_wrapper import ClaudeCodeWrapper

class SWEBenchSolverReal:
    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.wrapper = ClaudeCodeWrapper(model=model)
        self.endpoint = self.wrapper.localhost_url + "/api/generate"
```

**Benefit:**
- Automatically uses localhost:8080 (from wrapper)
- Matches OOLONG and IMO notebooks
- Single source of truth for URL

### Fix 2: Update Notebook Cell 8 to pass environment variable

**Current:**
```python
result = subprocess.run(
    ['python3', 'swe/src/swe_solver_real.py'],
    capture_output=True,
    text=True,
    cwd=Path.cwd(),
    timeout=60
)
```

**Better:**
```python
import os
env = os.environ.copy()
env['HAIKU_URL'] = llm_config['url']  # Pass http://localhost:8080

result = subprocess.run(
    ['python3', 'swe/src/swe_solver_real.py'],
    capture_output=True,
    text=True,
    cwd=Path.cwd(),
    timeout=60,
    env=env  # ← Include environment
)
```

### Fix 3: Create data directory or update path

**Option A: Create symlink**
```bash
mkdir -p /home/phuc/Downloads/benchmarks/SWE-bench/data
# Then populate with JSONL files
```

**Option B: Update notebook path**
```python
# Cell 4: Check multiple possible locations
for data_path in [
    Path('/home/phuc/Downloads/benchmarks/SWE-bench/data'),
    Path('/home/phuc/Downloads/benchmarks/SWE-bench'),
    Path('/home/phuc/Downloads/benchmarks'),
]:
    if data_path.exists():
        swe_data_dir = data_path
        break
else:
    print(f"⚠️  SWE-bench data not found")
```

---

## Testing Instructions

### Verify Notebook Configuration (NOW)
```bash
cd /home/phuc/projects/stillwater
python3 -c "
from src.llm_config_manager import get_llm_config
config = get_llm_config()
print(f'Notebook URL: {config.get(\"url\")}')
"
# Output: Notebook URL: http://localhost:8080
```

### Verify Solver Configuration (BEFORE FIX)
```bash
python3 -c "
import os
# Simulates what swe_solver_real.py does
HAIKU_LOCAL_URL = os.environ.get('HAIKU_URL', 'http://localhost:11434')
print(f'Solver URL: {HAIKU_LOCAL_URL}')
"
# Output: Solver URL: http://localhost:11434
# ⚠️  MISMATCH!
```

### Verify Solver Configuration (AFTER FIX)
```bash
HAIKU_URL=http://localhost:8080 python3 -c "
import os
HAIKU_LOCAL_URL = os.environ.get('HAIKU_URL', 'http://localhost:11434')
print(f'Solver URL: {HAIKU_LOCAL_URL}')
"
# Output: Solver URL: http://localhost:8080
# ✅ MATCH!
```

---

## Summary of Findings

| Finding | Severity | Recommendation |
|---------|----------|-----------------|
| Notebook config says 8080 | HIGH | ✅ Correct - no change needed |
| Solver hardcoded to 11434 | **CRITICAL** | ❌ FIX: Pass env var or use wrapper |
| Data directory missing | **CRITICAL** | ❌ FIX: Create directory or update path |
| Only 1 instance tested | MEDIUM | ⚠️  Should test multiple (currently 0) |
| Mismatch between notebooks | HIGH | ❌ FIX: Make all three use same pattern |

---

## Recommendation

**Priority 1: Fix solver to use ClaudeCodeWrapper**
- Makes SWE notebook identical to OOLONG/IMO pattern
- Automatically uses correct localhost:8080 URL
- Prevents environment variable confusion
- Estimated effort: 10 lines of code

**Priority 2: Fix data directory path**
- Create /home/phuc/Downloads/benchmarks/SWE-bench/data/
- Or update notebook to find existing data
- Estimated effort: 1-5 lines of code

**Priority 3: Test with real SWE instances**
- Once data directory exists
- Should test multiple instances (currently tests 0)
- Estimated effort: Already implemented in notebook

---

**Status:** ⚠️ Notebook framework correct, but solver integration needs fixes
**Auth:** 65537
**Date:** 2026-02-17

*"OOLONG and IMO are verified working. SWE-bench has the right framework but needs URL config and data fixes."*
