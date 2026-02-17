#!/usr/bin/env python3
"""
BATCH 1 PHUC ORCHESTRATION: Execute 5 astropy instances to 100% success

Auth: 65537
Status: Ready for execution - WITH DIFF POST-PROCESSOR
Mission: Achieve 5/5 on Batch 1 using fail-closed prompting + anti-rot isolation

Instance IDs:
  1. astropy__astropy-12907
  2. astropy__astropy-14182
  3. astropy__astropy-14365
  4. astropy__astropy-14995
  5. astropy__astropy-6938

Phases:
  1. DREAM (Scout)     ✅ Working
  2. FORECAST (Grace)  ✅ Working
  3. DECIDE (Judge)    ✅ Working
  4. ACT (Solver)      ✅ + DIFF POST-PROCESSOR (fix malformed diffs)
  5. VERIFY (Skeptic)  ✅ RED-GREEN gate
"""

import json
import subprocess
import tempfile
import time
import shutil
import re
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Tuple, List
import logging

# Import the diff post-processor to fix malformed diffs
try:
    from diff_postprocessor import DiffPostProcessor
    DIFF_POSTPROCESSOR_AVAILABLE = True
except ImportError:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("DiffPostProcessor not available - diffs won't be repaired")
    DIFF_POSTPROCESSOR_AVAILABLE = False

# ============================================================================
# SETUP: Logging + Configuration
# ============================================================================

LOG_FILE = Path("/tmp/batch_1_phuc_orchestration.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("STILLWATER_SWE_BENCH_DATA", str(Path.home() / "Downloads/benchmarks/SWE-bench-official")))
WORK_DIR = Path(os.environ.get("STILLWATER_WORK_DIR", "/tmp/batch_1_phuc"))
RESULTS_DIR = REPO_ROOT / "batch_1_results"
WORK_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Batch 1 Instance IDs (all astropy)
BATCH_1_INSTANCES = [
    "astropy__astropy-12907",
    "astropy__astropy-14182",
    "astropy__astropy-14365",
    "astropy__astropy-14995",
    "astropy__astropy-6938",
]

# API Configuration
API_CONFIG = {
    "url": os.environ.get("STILLWATER_WRAPPER_URL", "http://localhost:8080/api/generate"),
    "model": os.environ.get("STILLWATER_WRAPPER_MODEL", "haiku"),
    "timeout": int(os.environ.get("STILLWATER_WRAPPER_TIMEOUT_SECONDS", "120")),
}

logger.info("="*80)
logger.info("🚀 BATCH 1 PHUC ORCHESTRATION")
logger.info("="*80)
logger.info(f"Instances: {len(BATCH_1_INSTANCES)}")
logger.info(f"Data: {DATA_DIR}")
logger.info(f"Work: {WORK_DIR}")
logger.info(f"Results: {RESULTS_DIR}")
logger.info(f"API: {API_CONFIG['url']}")

# ============================================================================
# UTILITY: Load SWE-Bench Data
# ============================================================================

def load_batch_1_instances() -> Dict[str, Dict]:
    """Load Batch 1 instances from SWE-bench data."""
    instances = {}

    lite_file = DATA_DIR / "SWE-bench_Lite-test.jsonl"
    if not lite_file.exists():
        logger.error(f"Data file not found: {lite_file}")
        return instances

    with open(lite_file) as f:
        for line in f:
            try:
                inst = json.loads(line)
                iid = inst.get('instance_id')
                if iid in BATCH_1_INSTANCES:
                    instances[iid] = inst
            except:
                continue

    logger.info(f"Loaded {len(instances)}/{len(BATCH_1_INSTANCES)} Batch 1 instances")
    return instances

# ============================================================================
# PHASE 0: Context Extraction (Hardened)
# ============================================================================

class HardenedContextExtractor:
    """Extract context with repo validation and test detection."""

    def __init__(self, work_dir: Path):
        self.work_dir = work_dir

    def clone_repo(self, repo_url: str, commit: str, instance_id: str) -> Optional[Path]:
        """Clone and checkout with validation."""
        repo_dir = self.work_dir / instance_id.replace("/", "_")

        if repo_dir.exists():
            if self._is_valid_repo(repo_dir, commit):
                logger.debug(f"Using existing valid repo: {repo_dir}")
                return repo_dir
            else:
                logger.warning(f"Repo corrupted, re-cloning: {repo_dir}")
                shutil.rmtree(repo_dir)

        try:
            logger.debug(f"Cloning {repo_url}")
            result = subprocess.run(
                ["git", "clone", "--quiet", repo_url, str(repo_dir)],
                capture_output=True,
                timeout=90,
                cwd=str(self.work_dir)
            )

            if result.returncode != 0:
                logger.warning(f"Clone failed: {result.stderr.decode() if result.stderr else 'unknown'}")
                if repo_dir.exists():
                    shutil.rmtree(repo_dir)
                return None

            result = subprocess.run(
                ["git", "checkout", "--quiet", commit],
                capture_output=True,
                timeout=30,
                cwd=str(repo_dir)
            )

            if result.returncode == 0 and self._is_valid_repo(repo_dir, commit):
                logger.info(f"✅ Cloned {instance_id}")
                return repo_dir
            else:
                logger.warning(f"Checkout failed for {commit}")
                shutil.rmtree(repo_dir)
                return None

        except subprocess.TimeoutExpired:
            logger.warning(f"Clone timeout")
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            return None
        except Exception as e:
            logger.error(f"Clone error: {e}")
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            return None

    def _is_valid_repo(self, repo_dir: Path, commit: str) -> bool:
        """Validate repo is not corrupted."""
        if not repo_dir.exists() or not (repo_dir / ".git").exists():
            return False

        try:
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                timeout=10,
                cwd=str(repo_dir)
            )
            if result.returncode != 0:
                return False

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(repo_dir)
            )
            if result.returncode == 0:
                current = result.stdout.strip()
                return current.startswith(commit[:7])
            return False
        except:
            return False

    def run_tests(self, repo_dir: Path) -> Tuple[bool, str, str]:
        """Run tests, return (test_passed, error_output, failing_test)."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-xvs", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(repo_dir)
            )

            output = result.stdout + result.stderr
            failing_test = ""
            if "FAILED" in output:
                match = re.search(r'FAILED ([\w/:.]+)', output)
                if match:
                    failing_test = match.group(1)

            if result.returncode != 0:
                logger.info(f"Test failed (as expected): {failing_test}")
                return (False, output[:2000], failing_test)
            else:
                logger.debug(f"Tests already passing")
                return (True, output[:2000], "")
        except subprocess.TimeoutExpired:
            logger.warning(f"Test timeout")
            return (False, "Test timeout", "")
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return (False, str(e), "")

    def extract_source_files(self, repo_dir: Path, error_output: str) -> Dict[str, str]:
        """Extract source files from error output."""
        files = {}
        try:
            file_pattern = r'(?:File\s+["\']|\s)([\\/\w\.\-]+\.py)(?:["\']:|:\d+)'
            matches = re.findall(file_pattern, error_output)

            if not matches:
                py_files = list(repo_dir.glob("**/*.py"))
                matches = [str(f.relative_to(repo_dir)) for f in py_files[:3]]

            for filepath in matches[:5]:
                try:
                    full_path = repo_dir / filepath
                    if full_path.exists() and full_path.is_file():
                        with open(full_path) as f:
                            content = f.read()
                            files[filepath] = content[:2000]
                except:
                    continue

            logger.info(f"Extracted {len(files)} source files")
            return files
        except Exception as e:
            logger.warning(f"Error extracting source files: {e}")
            return {}

    def extract_context(self, instance: Dict) -> Dict:
        """Extract full context with validation."""
        instance_id = instance.get("instance_id", "unknown")

        context = {
            "instance_id": instance_id,
            "repo": instance.get("repo"),
            "commit": instance.get("base_commit"),
            "problem": instance.get("problem_statement", "")[:2000],
            "source_files": {},
            "error_output": "",
            "failing_test": "",
            "status": "failed",
            "error_message": ""
        }

        try:
            repo_name = instance.get("repo", "")
            if not repo_name:
                context["error_message"] = "No repo name"
                return context

            repo_url = f"https://github.com/{repo_name}.git"
            commit = instance.get("base_commit", "")

            repo_dir = self.clone_repo(repo_url, commit, instance_id)
            if not repo_dir:
                context["error_message"] = "Clone failed"
                return context

            test_passed, error_output, failing_test = self.run_tests(repo_dir)

            if test_passed:
                context["error_message"] = "Tests already passing"
                return context

            source_files = self.extract_source_files(repo_dir, error_output)

            context["source_files"] = source_files
            context["error_output"] = error_output
            context["failing_test"] = failing_test
            context["status"] = "ready"

            logger.info(f"✅ Context ready for {instance_id}")
            return context

        except Exception as e:
            context["error_message"] = str(e)
            logger.error(f"Exception in extract_context: {e}")
            return context

# ============================================================================
# PHASE 1: DREAM — Scout Agent (Problem Analysis)
# ============================================================================

def scout_analyze(problem: str, error: str, source_files: Dict[str, str]) -> Dict:
    """DREAM phase: Analyze problem, extract structure."""

    system = """AUTHORITY: 65537 (Phuc Forecast + Prime Coder)

PERSONA: Linus Torvalds (Linux kernel debugging master)
ROLE: DREAM phase - Define what "fixed" means, locate suspects, minimal repro

YOU MUST OUTPUT VALID JSON. NO QUESTIONS, NO ESCAPE HATCHES.

REQUIRED JSON SCHEMA:
{
  "task_summary": "one sentence: what's broken?",
  "repro_command": "exact pytest command to reproduce (parse from error output if needed)",
  "failing_tests": ["list of test names from error output"],
  "suspect_files": ["files mentioned in problem or error, highest priority first"],
  "acceptance_criteria": ["test passes without failure", "no regressions"]
}

RULES:
1. Infer missing information from provided context (problem + error + source)
2. Extract test command from pytest error traceback
3. Extract test names from failure messages
4. Extract file paths from error output and source code
5. DO NOT ask for clarification - USE WHAT YOU HAVE
6. Output ONLY valid JSON, no text before or after
7. All five keys are required in output
"""

    source_section = "\n".join([
        f"### {filepath}\n```python\n{content}\n```"
        for filepath, content in source_files.items()
    ])

    prompt = f"""REAL SWE-BENCH INSTANCE:

PROBLEM STATEMENT:
{problem}

PYTEST ERROR OUTPUT:
{error}

SOURCE CODE:
{source_section}

SCOUT TASK: Analyze this bug. Extract test command, failing test names, suspect files.
Output valid JSON (no explanations):
{{"""

    try:
        payload = {
            "system": system,
            "prompt": prompt,
            "model": API_CONFIG["model"],
            "stream": False
        }

        result = subprocess.run(
            ["curl", "-s", "-X", "POST", API_CONFIG["url"],
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=API_CONFIG["timeout"]
        )

        if result.returncode == 0:
            response = json.loads(result.stdout).get('response', '')
            match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response, re.DOTALL)
            if match:
                scout_json = json.loads(match.group(0))
                required = ['task_summary', 'repro_command', 'failing_tests', 'suspect_files', 'acceptance_criteria']
                if all(k in scout_json for k in required):
                    logger.info("✅ Scout report valid")
                    return scout_json
    except Exception as e:
        logger.warning(f"Scout error: {e}")

    logger.warning("❌ Scout failed, using fallback")
    return {
        "task_summary": "Unable to parse Scout output",
        "repro_command": "pytest",
        "failing_tests": [],
        "suspect_files": [],
        "acceptance_criteria": ["All tests pass"]
    }

# ============================================================================
# PHASE 2: FORECAST — Grace Agent (Failure Analysis)
# ============================================================================

def grace_forecast(scout_report: Dict, problem: str, error: str) -> Dict:
    """FORECAST phase: Identify failure modes."""

    system = """AUTHORITY: 65537 (Phuc Forecast + Prime Coder)

PERSONA: Grace Hopper (computing pioneer)
ROLE: FORECAST phase - Premortem: how will this patch fail?

TASK: Identify failure modes adversarially. Think like a skeptic.

STRICT JSON SCHEMA:
{
  "top_failure_modes_ranked": [
    {"mode": "description", "risk_level": "HIGH|MED|LOW"}
  ],
  "edge_cases_to_test": ["specific test case", "..."],
  "compatibility_risks": ["backwards compat issue", "..."],
  "stop_rules": ["condition to abort", "..."]
}

RULES:
- Rank failure modes by severity (HIGH first)
- Consider: Python versions, OS platforms, backwards compatibility
- Output ONLY valid JSON
"""

    prompt = f"""FRESH CONTEXT (Anti-Rot):

SCOUT FOUND:
{json.dumps(scout_report, indent=2)}

PROBLEM (snippet):
{problem[:400]}

ERROR (snippet):
{error[:500]}

GRACE TASK (FORECAST Phase - Premortem):
Think adversarially: how will a patch for this BREAK other things?

Output ONLY JSON (valid JSON, no text):{{"""

    try:
        payload = {
            "system": system,
            "prompt": prompt,
            "model": API_CONFIG["model"],
            "stream": False
        }

        result = subprocess.run(
            ["curl", "-s", "-X", "POST", API_CONFIG["url"],
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=API_CONFIG["timeout"]
        )

        if result.returncode == 0:
            response = json.loads(result.stdout).get('response', '')
            match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response, re.DOTALL)
            if match:
                grace_json = json.loads(match.group(0))
                required = ['top_failure_modes_ranked', 'edge_cases_to_test', 'compatibility_risks', 'stop_rules']
                if all(k in grace_json for k in required):
                    logger.info("✅ Grace memo valid")
                    return grace_json
    except Exception as e:
        logger.warning(f"Grace error: {e}")

    logger.warning("❌ Grace failed, using fallback")
    return {
        "top_failure_modes_ranked": [],
        "edge_cases_to_test": [],
        "compatibility_risks": [],
        "stop_rules": []
    }

# ============================================================================
# PHASE 3: DECIDE — Judge Agent (Decision Locking)
# ============================================================================

def judge_decide(scout: Dict, grace: Dict, problem: str = "", error_output: str = "", source_context: Dict[str, str] = None) -> Dict:
    """DECIDE phase: Lock the approach with full context for specificity."""

    if source_context is None:
        source_context = {}

    system = """AUTHORITY: 65537 (Prime Coder + Phuc Forecast)

PERSONA: Donald Knuth (precise, meticulous, line-specific)
ROLE: DECIDE phase - Lock exact changes (line numbers, before/after code)

YOU MUST OUTPUT VALID JSON. NO VAGUE APPROACHES. SPECIFIC OR FAIL.

OUTPUT STRICT JSON (MANDATORY):
{
  "chosen_approach": "EXACT change: In FILE, at LINE N, change 'OLD_CODE' to 'NEW_CODE' because REASON",
  "scope_locked": ["ONLY these exact files"],
  "line_number": "N (where the bug is, if known from error/source)",
  "before_code": "The exact problematic code snippet (2-5 lines)",
  "after_code": "The exact fixed code snippet (2-5 lines)",
  "test_will_pass_if": "This specific condition is met (e.g., 'test_X passes AND test_Y passes')",
  "rationale": "Why this is the root cause and minimal fix",
  "stop_rules": ["reject if any existing tests fail", "reject if change goes beyond these files"],
  "required_evidence": ["SPECIFIC test name that was failing", "All other tests remain passing"]
}

CRITICAL RULES:
1. chosen_approach MUST include: FILE + LINE NUMBER + "change X to Y"
2. before_code MUST be the EXACT code from source (copy-paste, not paraphrased)
3. after_code MUST be the EXACT replacement (copy-paste the fix, not description)
4. line_number MUST be set if identifiable from error output
5. test_will_pass_if MUST be concrete, not vague
6. Output ONLY valid JSON, no text before or after
7. All nine keys are required

Do not guess or be vague. Use error output + source context to be PRECISE."""

    source_snippet = ""
    if source_context:
        source_snippet = "\n\nSOURCE CODE CONTEXT (relevant files):\n"
        for fname, content in list(source_context.items())[:3]:
            lines = content.split('\n')[:30]  # First 30 lines
            source_snippet += f"\n--- {fname} ---\n"
            for i, line in enumerate(lines, 1):
                source_snippet += f"{i:3d}: {line}\n"

    prompt = f"""FULL CONTEXT FOR PRECISE DECISION:

PROBLEM STATEMENT:
{problem[:800]}

PYTEST ERROR OUTPUT (where the bug shows):
{error_output[:800]}

SCOUT REPORT (what was analyzed):
{json.dumps(scout, indent=2)}

GRACE MEMO (failure modes to avoid):
{json.dumps(grace.get('top_failure_modes_ranked', [])[:2], indent=2)}
{source_snippet}

JUDGE TASK (DECIDE Phase - Precise Decision):
Using the error output, scout analysis, and source code:
1. IDENTIFY exact line number where bug is
2. COPY the exact problematic code from source
3. SPECIFY exact replacement code
4. NAME the specific test that will pass
5. Explain WHY this is the root cause

Output ONLY JSON (no explanations):
{{"""

    try:
        payload = {
            "system": system,
            "prompt": prompt,
            "model": API_CONFIG["model"],
            "stream": False
        }

        result = subprocess.run(
            ["curl", "-s", "-X", "POST", API_CONFIG["url"],
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=API_CONFIG["timeout"]
        )

        if result.returncode == 0:
            response = json.loads(result.stdout).get('response', '')
            match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response, re.DOTALL)
            if match:
                judge_json = json.loads(match.group(0))
                # Check for enhanced Judge fields (new format) or basic fields (fallback)
                required_new = ['chosen_approach', 'scope_locked', 'line_number', 'before_code', 'after_code', 'test_will_pass_if']
                required_old = ['chosen_approach', 'scope_locked', 'rationale', 'stop_rules', 'required_evidence']

                if all(k in judge_json for k in required_new):
                    logger.info("✅ Judge decision valid (enhanced format)")
                    return judge_json
                elif all(k in judge_json for k in required_old):
                    logger.info("✅ Judge decision valid (basic format)")
                    return judge_json
    except Exception as e:
        logger.warning(f"Judge error: {e}")

    logger.warning("❌ Judge failed, using fallback")
    return {
        "chosen_approach": "Unable to determine approach",
        "scope_locked": [],
        "rationale": "Insufficient information",
        "stop_rules": [],
        "required_evidence": []
    }

# ============================================================================
# PHASE 4: ACT — Solver Agent (Patch Generation)
# ============================================================================

class SolverGenerator:
    """Generate patches with JSON-to-diff conversion (avoids LLM formatting issues)."""

    def _json_to_unified_diff(self, change_spec: Dict, source_files: Dict[str, str]) -> Optional[str]:
        """Convert JSON change spec to proper unified diff format."""
        try:
            filepath = change_spec.get("file")
            line_num = change_spec.get("line_number", 1)
            old_text = change_spec.get("old_text", "")
            new_text = change_spec.get("new_text", "")

            if not filepath or filepath not in source_files:
                logger.warning(f"File not found in source: {filepath}")
                return None

            source = source_files[filepath]
            lines = source.split('\n')

            # Convert to 0-indexed
            line_idx = max(0, line_num - 1)

            # Find the old text in source
            found_idx = -1
            for i, line in enumerate(lines):
                if old_text.strip() in line:
                    found_idx = i
                    break

            if found_idx < 0:
                logger.warning(f"Could not locate '{old_text}' in {filepath}")
                return None

            # Build unified diff with proper format
            hunk_lines = []
            context_before = max(0, found_idx - 2)
            context_after = min(len(lines), found_idx + 2)

            # Generate diff header
            diff = f"--- a/{filepath}\n+++ b/{filepath}\n"
            old_lines_count = context_after - context_before + 1
            new_lines_count = old_lines_count  # Assume same count for now
            diff += f"@@ -{context_before+1},{old_lines_count} +{context_before+1},{new_lines_count} @@\n"

            # Add context and changes with proper prefixes
            for i in range(context_before, context_after):
                if i == found_idx:
                    diff += f"-{lines[i]}\n"  # Removed line with minus prefix
                    diff += f"+{new_text}\n"  # Added line with plus prefix
                else:
                    diff += f" {lines[i]}\n"  # Context lines with space prefix

            logger.debug(f"Generated diff:\n{diff}")
            return diff

        except Exception as e:
            logger.error(f"Error converting JSON to diff: {e}")
            return None

    def generate_patch(self, decision: Dict, problem: str, source_files: Dict[str, str]) -> Optional[str]:
        """ACT phase: Generate patch via JSON spec, convert to diff."""

        system = """AUTHORITY: 65537 (Prime Coder + Phuc Forecast)

PERSONA: Brian Kernighan (K&R C, clarity master)
ROLE: ACT phase - Specify exact changes in JSON format (NOT unified diff)

YOU MUST OUTPUT VALID JSON. NO QUESTIONS, NO ESCAPE HATCHES.

OUTPUT STRICT JSON (MANDATORY):
{
  "file": "path/to/file.py",
  "line_number": 42,
  "old_text": "the exact current code (1-3 lines)",
  "new_text": "the exact replacement code (1-3 lines)",
  "rationale": "why this change is correct"
}

RULES (STRICT):
1. file: MUST be exact path from source files provided
2. line_number: MUST be the line number where old_text appears
3. old_text: MUST be copy-pasted EXACTLY from source (including indentation)
4. new_text: MUST be the corrected version (same indentation)
5. Output ONLY valid JSON, no text before or after

Do NOT try to generate a unified diff. Output JSON only."""

        # Build source files with line numbers for reference
        source_section = ""
        for filepath, content in source_files.items():
            source_section += f"\n### {filepath}\n"
            for line_num, line in enumerate(content.split('\n')[:50], 1):
                source_section += f"{line_num:3d}: {line}\n"

        # Extract decision fields
        line_info = decision.get("line_number", "(not identified)")
        before = decision.get("before_code", "(see source code)")
        after = decision.get("after_code", "(see decision record)")

        prompt = f"""DECISION_RECORD (what to change):
FILE: {decision.get('scope_locked', ['(unknown)'])[0]}
AT LINE: {line_info}
FROM: {before}
TO: {after}

FULL DECISION:
{json.dumps(decision, indent=2)}

PROBLEM SUMMARY:
{problem[:400]}

SOURCE CODE WITH LINE NUMBERS:
{source_section}

TASK: Output JSON specifying the EXACT change needed.
The JSON must identify the exact line number where '{before}' appears and what to change it to.
Output ONLY JSON:
{{"""

        try:
            payload = {
                "system": system,
                "prompt": prompt,
                "model": API_CONFIG["model"],
                "stream": False
            }

            result = subprocess.run(
                ["curl", "-s", "-X", "POST", API_CONFIG["url"],
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps(payload)],
                capture_output=True,
                text=True,
                timeout=API_CONFIG["timeout"]
            )

            if result.returncode == 0:
                response = json.loads(result.stdout).get('response', '')
                logger.debug(f"Solver response length: {len(response)} chars")

                if not response:
                    logger.warning("Empty response from Solver")
                    return None

                logger.debug(f"Solver response (first 1000 chars):\n{response[:1000]}")

                # Extract JSON change specification from response
                json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response, re.DOTALL)
                if not json_match:
                    logger.warning("No JSON found in Solver response")
                    return None

                try:
                    change_spec = json.loads(json_match.group(0))
                    logger.debug(f"Extracted change spec: {json.dumps(change_spec, indent=2)}")

                    # Validate JSON has required fields
                    required_fields = ['file', 'line_number', 'old_text', 'new_text']
                    if not all(f in change_spec for f in required_fields):
                        logger.warning(f"Change spec missing fields. Has: {list(change_spec.keys())}")
                        return None

                    # Convert JSON to unified diff
                    patch = self._json_to_unified_diff(change_spec, source_files)
                    if patch:
                        logger.info("✅ Converted JSON change spec to unified diff")
                        return patch
                    else:
                        logger.warning("Failed to convert JSON to diff")
                        return None

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from response: {e}")
                    return None

        except subprocess.TimeoutExpired:
            logger.warning(f"Solver timeout ({API_CONFIG['timeout']}s)")
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response from Solver: {e}")
        except Exception as e:
            logger.warning(f"Solver error: {e}")

        logger.warning("❌ Solver failed")
        return None

    def _validate_diff_format(self, patch: str) -> bool:
        """Strict validation of unified diff format."""
        if not patch:
            logger.warning("Patch is empty")
            return False

        lines = patch.split('\n')
        logger.debug(f"Patch has {len(lines)} lines")

        if len(lines) < 4:
            logger.warning(f"Patch too short ({len(lines)} lines, need at least 4)")
            return False

        # Check headers
        has_minus_a = any(line.startswith('--- a/') for line in lines[:10])
        has_plus_b = any(line.startswith('+++ b/') for line in lines[:10])

        if not has_minus_a:
            logger.warning("Missing '--- a/' header")
            for i, line in enumerate(lines[:10]):
                logger.debug(f"  Line {i}: {repr(line[:50])}")
            return False

        if not has_plus_b:
            logger.warning("Missing '+++ b/' header")
            return False

        # Check hunk headers
        has_hunk = any(line.startswith('@@') for line in lines)
        if not has_hunk:
            logger.warning("No hunk headers (@@)")
            return False

        # Validate hunk header format
        hunk_issues = 0
        for line in lines:
            if line.startswith('@@'):
                if not re.match(r'^@@ -\d+,\d+ \+\d+,\d+ @@', line):
                    logger.warning(f"Malformed hunk header: {line[:60]}")
                    hunk_issues += 1

        if hunk_issues > 0:
            return False

        # Validate line prefixes
        prefix_issues = 0
        for i, line in enumerate(lines):
            if len(line) > 0:
                first_char = line[0]
                # Valid prefixes for diff lines
                if not (first_char in ' +-\\' or
                        line.startswith('---') or
                        line.startswith('+++') or
                        line.startswith('@@')):
                    logger.debug(f"Line {i}: Invalid prefix '{first_char}' in: {repr(line[:60])}")
                    prefix_issues += 1

        if prefix_issues > 10:  # Allow a few issues, but not many
            logger.warning(f"Invalid line prefixes: {prefix_issues} lines")
            return False

        logger.info("✅ Diff format validation passed")
        return True

# ============================================================================
# PHASE 5: VERIFY — Skeptic Agent (RED-GREEN Gate)
# ============================================================================

class SkepticVerifier:
    """Enforce RED-GREEN gate with strict verification."""

    def verify_red_green(self, repo_dir: Path, patch: str, failing_test: str) -> bool:
        """Verify RED gate (fail) and GREEN gate (pass)."""

        # RED: Baseline should fail
        logger.info("🔴 RED gate: Verify test fails without patch...")
        red_result = subprocess.run(
            ["python", "-m", "pytest", "-xvs", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(repo_dir)
        )

        red_passed = red_result.returncode != 0
        if red_passed:
            logger.info("✅ RED gate: Test fails (as expected)")
        else:
            logger.warning("❌ RED gate: Test passes (but should fail)")
            return False

        # Apply patch
        logger.info("📝 Applying patch...")
        temp_dir = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(repo_dir, temp_dir / "repo", dirs_exist_ok=True)
            repo_copy = temp_dir / "repo"

            result = subprocess.run(
                ["patch", "-p1"],
                input=patch,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(repo_copy)
            )

            if result.returncode != 0:
                logger.warning(f"❌ Patch application failed: {result.stderr}")
                return False

            logger.info("✅ Patch applied")

            # GREEN: After patch, should pass
            logger.info("🟢 GREEN gate: Verify test passes with patch...")
            if failing_test:
                result = subprocess.run(
                    ["python", "-m", "pytest", "-xvs", failing_test],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(repo_copy)
                )
            else:
                result = subprocess.run(
                    ["python", "-m", "pytest", "-xvs", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(repo_copy)
                )

            green_passed = result.returncode == 0
            if green_passed:
                logger.info("✅ GREEN gate: Test passes (as expected)")
                return True
            else:
                logger.warning("❌ GREEN gate: Test still fails")
                return False

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

# ============================================================================
# MAIN: Execute Batch 1 Pipeline
# ============================================================================

def run_batch_1():
    """Execute all 5 Batch 1 instances."""

    print("\n" + "="*80)
    print("🚀 BATCH 1 PHUC ORCHESTRATION - 5/5 TARGET")
    print("="*80)

    instances = load_batch_1_instances()
    if len(instances) != len(BATCH_1_INSTANCES):
        logger.error(f"Only loaded {len(instances)}/{len(BATCH_1_INSTANCES)} instances")
        for iid in BATCH_1_INSTANCES:
            if iid not in instances:
                print(f"  Missing: {iid}")

    results = {}
    extractor = HardenedContextExtractor(WORK_DIR)
    solver = SolverGenerator()
    verifier = SkepticVerifier()

    for i, iid in enumerate(BATCH_1_INSTANCES, 1):
        print(f"\n[{i}/5] {iid}")
        print("-" * 80)

        if iid not in instances:
            logger.warning(f"Instance not found: {iid}")
            results[iid] = {"status": "FAILED", "reason": "not_found"}
            continue

        inst = instances[iid]

        # PHASE 0: Extract context
        print(f"  [0/5] Extracting context...", end="", flush=True)
        context = extractor.extract_context(inst)

        if context["status"] != "ready":
            print(f" ❌ ({context['error_message']})")
            results[iid] = {"status": "FAILED", "reason": context['error_message']}
            continue

        print(f" ✅")
        repo_dir = WORK_DIR / iid.replace("/", "_")

        # PHASE 1: DREAM — Scout
        print(f"  [1/5] DREAM (Scout)...", end="", flush=True)
        scout = scout_analyze(
            problem=context["problem"],
            error=context["error_output"],
            source_files=context["source_files"]
        )
        if not scout.get("task_summary"):
            print(f" ❌")
            results[iid] = {"status": "FAILED", "reason": "scout_failed"}
            continue
        print(f" ✅")

        # PHASE 2: FORECAST — Grace
        print(f"  [2/5] FORECAST (Grace)...", end="", flush=True)
        grace = grace_forecast(
            scout_report=scout,
            problem=context["problem"],
            error=context["error_output"]
        )
        if not grace.get("top_failure_modes_ranked"):
            print(f" ❌")
            results[iid] = {"status": "FAILED", "reason": "grace_failed"}
            continue
        print(f" ✅")

        # PHASE 3: DECIDE — Judge (with full context for specificity)
        print(f"  [3/5] DECIDE (Judge)...", end="", flush=True)
        decision = judge_decide(
            scout=scout,
            grace=grace,
            problem=context["problem"],
            error_output=context["error_output"],
            source_context=context["source_files"]
        )
        if not decision.get("chosen_approach"):
            print(f" ❌")
            results[iid] = {"status": "FAILED", "reason": "judge_failed"}
            continue
        print(f" ✅")

        # PHASE 4: ACT — Solver
        print(f"  [4/5] ACT (Solver)...", end="", flush=True)
        patch = solver.generate_patch(
            decision=decision,
            problem=context["problem"],
            source_files=context["source_files"]
        )
        if not patch:
            print(f" ❌")
            results[iid] = {"status": "FAILED", "reason": "solver_failed"}
            continue
        print(f" ✅")

        # PHASE 4B: POST-PROCESS — Repair malformed diffs if needed
        if DIFF_POSTPROCESSOR_AVAILABLE:
            postprocessor = DiffPostProcessor()
            # Combine all source files into one context string
            full_source = ""
            for filepath, content in context["source_files"].items():
                full_source += f"# File: {filepath}\n{content}\n\n"

            # Try to repair the patch
            repaired_patch = postprocessor.repair(patch, full_source)
            if repaired_patch:
                logger.info("✅ Diff post-processor repaired malformed patch")
                patch = repaired_patch

        # PHASE 5: VERIFY — Skeptic
        print(f"  [5/5] VERIFY (Skeptic - RED-GREEN)...", end="", flush=True)
        verdict = verifier.verify_red_green(
            repo_dir=repo_dir,
            patch=patch,
            failing_test=context.get("failing_test", "")
        )
        print(f" {'✅' if verdict else '❌'}")

        results[iid] = {
            "status": "APPROVED" if verdict else "REJECTED",
            "phases": {
                "scout": bool(scout.get("task_summary")),
                "grace": bool(grace.get("top_failure_modes_ranked")),
                "judge": bool(decision.get("chosen_approach")),
                "solver": bool(patch),
                "skeptic": verdict
            }
        }

    # Summary
    print("\n" + "="*80)
    print("📊 BATCH 1 RESULTS")
    print("="*80)

    approved = sum(1 for r in results.values() if r["status"] == "APPROVED")
    total = len(results)

    print(f"\n✅ APPROVED: {approved}/{total}")
    for iid, result in results.items():
        status = "✅" if result["status"] == "APPROVED" else "❌"
        reason = result.get("reason", "")
        print(f"  {status} {iid} {f'({reason})' if reason else ''}")

    print(f"\n🎯 TARGET: 5/5 (100%)")
    print(f"📈 ACHIEVED: {approved}/5 ({approved*100//5}%)")

    if approved == 5:
        print(f"\n🎉 SUCCESS! BATCH 1 COMPLETE (5/5 = 100%)")
    else:
        print(f"\n⚠️  {5-approved} instances failed - Review logs for fixes")

    logger.info(f"Batch 1 complete: {approved}/{total} APPROVED")

    return approved == 5

if __name__ == "__main__":
    try:
        success = run_batch_1()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
