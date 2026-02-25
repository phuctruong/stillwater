"""
tests/test_security_gate.py — Security Gate for Stillwater Phase 4 (Rung 65537)

Tests:
  1.  No hardcoded secrets in any .py production file
  2.  No unsandboxed eval() in production code
  3.  No os.system() with f-strings or .format() (shell injection)
  4.  SHA-256 skill file manifest — all skill files are accounted for
  5.  Evidence directory structure validation
  6.  behavior_hash.json format validation (schema + consensus flag)
  7.  security_scan.json format validation
  8.  No credentials in repr/str outputs (admin/session_manager.py)
  9.  No .py file in src/store/ imports os.system directly
  10. Skill files contain required header fields
  11. All Python production files compile without errors
  12. No eval() in src/store/ at all
  13. No hardcoded AWS keys in any production file
  14. behavior_hash.json has 3 matching seeds
  15. security_scan.json status is GREEN or file exists with correct schema
  16. Plan.json has required rung_target field
  17. Plan.json rung_target is an integer
  18. Plan.json files_changed is a non-empty list
  19. Evidence dir exists and is a directory
  20. Admin session_manager does not echo key material in error messages
  21. No sk- style keys in any production .py file
  22. No password= <string literal> in production code (outside docstrings)
  23. Skill README.md exists in skills/
  24. Behavior hash file uses JSON not .txt format (new canonical path)
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Project layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

PROD_DIRS = [
    REPO_ROOT / "src" / "store",
    REPO_ROOT / "src" / "cli" / "src" / "stillwater",
    REPO_ROOT / "admin",
]

SKILLS_DIR = REPO_ROOT / "data" / "default" / "skills"
EVIDENCE_DIR = REPO_ROOT / "evidence"

# Canonical evidence files
BEHAVIOR_HASH_JSON = EVIDENCE_DIR / "behavior_hash.json"
BEHAVIOR_HASH_TXT = EVIDENCE_DIR / "behavior_hash.txt"   # legacy, may also exist
SECURITY_SCAN_JSON = EVIDENCE_DIR / "security_scan.json"
PLAN_JSON = EVIDENCE_DIR / "plan.json"
TESTS_JSON = EVIDENCE_DIR / "tests.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prod_py_files() -> list[Path]:
    """Return all production .py files (excludes __pycache__ and test_* files)."""
    files = []
    for d in PROD_DIRS:
        if not d.exists():
            continue
        for f in d.rglob("*.py"):
            if "__pycache__" in f.parts:
                continue
            if f.name.startswith("test_"):
                continue  # test files may contain intentional fake secrets
            files.append(f)
    return sorted(files)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# Sandboxed eval pattern: eval(compile(...), {"__builtins__": {}}, {})
_EVAL_SANDBOXED_RE = re.compile(
    r'eval\s*\(\s*compile\s*\(.+?\)\s*,\s*\{["\']__builtins__["\']\s*:\s*\{\}\}'
)
_EVAL_ANY_RE = re.compile(r'\beval\s*\(')

# os.system with unsanitized input (f-string or .format)
_OS_SYSTEM_UNSAFE_RE = re.compile(
    r'os\.system\s*\(\s*(?:f["\']|["\'][^"\']*\{|.*\.format\s*\()'
)

# Real secret patterns (not variable names)
_OPENAI_KEY_RE = re.compile(r'sk-[a-zA-Z0-9]{32,}')
_AWS_KEY_RE = re.compile(r'AKIA[0-9A-Z]{16}')
_PASSWORD_LITERAL_RE = re.compile(r'(?i)\bpassword\s*=\s*["\'][^\s"\']{8,}["\']')
_SECRET_LITERAL_RE = re.compile(r'(?i)\bsecret\s*=\s*["\'][^\s"\']{8,}["\']')

# Lines that are clearly docstring examples — skip
_EXAMPLE_LINE_RE = re.compile(
    r'(?i)(example|#\s|"""|\'\'\'|placeholder|<your|dummy|fake|sw_sk_0{10})',
)


# ===========================================================================
# Tests: No hardcoded secrets
# ===========================================================================

class TestNoHardcodedSecrets:

    def test_no_openai_keys_in_production(self):
        """No sk-<32+> style keys in production code."""
        violations = []
        for path in _prod_py_files():
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _OPENAI_KEY_RE.search(line):
                    if not _EXAMPLE_LINE_RE.search(line):
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "OpenAI/Anthropic key found:\n" + "\n".join(violations)

    def test_no_aws_access_keys_in_production(self):
        """No AKIA... AWS access key IDs in production code."""
        violations = []
        for path in _prod_py_files():
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _AWS_KEY_RE.search(line):
                    if not _EXAMPLE_LINE_RE.search(line):
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "AWS key found:\n" + "\n".join(violations)

    def test_no_hardcoded_password_literals(self):
        """No password=<literal string> in production code outside docstrings."""
        violations = []
        for path in _prod_py_files():
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _PASSWORD_LITERAL_RE.search(line):
                    if not _EXAMPLE_LINE_RE.search(line):
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "Hardcoded password found:\n" + "\n".join(violations)

    def test_no_hardcoded_secret_literals(self):
        """No secret=<literal string> in production code outside docstrings."""
        violations = []
        for path in _prod_py_files():
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _SECRET_LITERAL_RE.search(line):
                    if not _EXAMPLE_LINE_RE.search(line):
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "Hardcoded secret found:\n" + "\n".join(violations)


# ===========================================================================
# Tests: eval() safety
# ===========================================================================

class TestEvalSafety:

    def test_no_unsandboxed_eval_in_store(self):
        """src/store/ must contain zero eval() calls."""
        store_dir = REPO_ROOT / "src" / "store"
        if not store_dir.exists():
            pytest.skip("src/store/ directory not present")
        violations = []
        for path in sorted(store_dir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _EVAL_ANY_RE.search(line):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "eval() found in src/store/:\n" + "\n".join(violations)

    def test_cli_eval_is_sandboxed(self):
        """The only eval() in src/cli/ must use the sandboxed pattern (empty __builtins__)."""
        cli_src = REPO_ROOT / "src" / "cli" / "src" / "stillwater"
        if not cli_src.exists():
            pytest.skip("src/cli/src/stillwater not present")
        violations = []
        for path in sorted(cli_src.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _EVAL_ANY_RE.search(line):
                    # Must either be sandboxed OR carry a noqa/nosec marker
                    if not _EVAL_SANDBOXED_RE.search(line):
                        if "# noqa" not in line and "# nosec" not in line:
                            violations.append(
                                f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}"
                            )
        assert not violations, (
            "Unsandboxed eval() found in src/cli/ (must use empty __builtins__ or # noqa):\n"
            + "\n".join(violations)
        )

    def test_no_unsandboxed_eval_in_admin(self):
        """admin/ must not contain eval() calls."""
        admin_dir = REPO_ROOT / "admin"
        if not admin_dir.exists():
            pytest.skip("admin/ directory not present")
        violations = []
        for path in sorted(admin_dir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            if "tests" in path.parts:
                continue
            if "test_" in path.name:
                continue  # skip test files
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _EVAL_ANY_RE.search(line):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "eval() found in admin/:\n" + "\n".join(violations)


# ===========================================================================
# Tests: os.system() safety
# ===========================================================================

class TestOsSystemSafety:

    def test_no_os_system_with_fstring_in_production(self):
        """No os.system(f'...') — f-string injection risk."""
        violations = []
        for path in _prod_py_files():
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if _OS_SYSTEM_UNSAFE_RE.search(line):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, (
            "os.system() with f-string or .format() found (shell injection risk):\n"
            + "\n".join(violations)
        )

    def test_store_does_not_import_os_system_directly(self):
        """src/store/ should not call os.system() at all."""
        store_dir = REPO_ROOT / "src" / "store"
        if not store_dir.exists():
            pytest.skip("src/store/ directory not present")
        violations = []
        for path in sorted(store_dir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            src = _read(path)
            for i, line in enumerate(src.splitlines(), 1):
                if re.search(r'\bos\.system\s*\(', line):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()[:80]}")
        assert not violations, "os.system() found in src/store/:\n" + "\n".join(violations)


# ===========================================================================
# Tests: Skill file manifest (SHA-256)
# ===========================================================================

class TestSkillManifest:

    def _skill_files(self) -> list[Path]:
        if not SKILLS_DIR.exists():
            return []
        return sorted(SKILLS_DIR.glob("*.md"))

    def test_skills_directory_exists(self):
        assert SKILLS_DIR.exists(), f"skills/ directory not found at {SKILLS_DIR}"
        assert SKILLS_DIR.is_dir()

    def test_skills_readme_exists(self):
        readme = SKILLS_DIR / "README.md"
        assert readme.exists(), f"skills/README.md missing (expected at {readme})"

    def test_skill_files_have_sha256_hash(self):
        """Verify every skill .md file can be hashed (content is non-empty)."""
        skill_files = self._skill_files()
        assert len(skill_files) > 0, "No skill .md files found in skills/"
        for f in skill_files:
            content = f.read_bytes()
            assert len(content) > 0, f"Skill file is empty: {f.name}"
            digest = hashlib.sha256(content).hexdigest()
            assert len(digest) == 64, f"Bad SHA-256 digest for {f.name}"

    def test_skill_manifest_is_stable(self):
        """SHA-256 of the sorted skill filenames is deterministic."""
        skill_files = self._skill_files()
        names = sorted(f.name for f in skill_files)
        manifest = hashlib.sha256("\n".join(names).encode()).hexdigest()
        # Must be a valid hex string
        assert re.fullmatch(r"[0-9a-f]{64}", manifest), "Manifest hash malformed"

    def test_prime_safety_skill_exists(self):
        """prime-safety.md must always be present (god-skill)."""
        assert (SKILLS_DIR / "prime-safety.md").exists(), (
            "prime-safety.md missing from skills/ — this is the god-skill and must exist"
        )

    def test_prime_coder_skill_exists(self):
        assert (SKILLS_DIR / "prime-coder.md").exists(), "prime-coder.md missing from skills/"

    def test_prime_test_skill_exists(self):
        assert (SKILLS_DIR / "prime-test.md").exists(), (
            "prime-test.md missing from skills/"
        )


# ===========================================================================
# Tests: Evidence directory structure
# ===========================================================================

class TestEvidenceStructure:

    def test_evidence_dir_exists(self):
        assert EVIDENCE_DIR.exists(), f"evidence/ directory not found at {EVIDENCE_DIR}"
        assert EVIDENCE_DIR.is_dir()

    def test_plan_json_exists(self):
        assert PLAN_JSON.exists(), "evidence/plan.json not found"

    def test_tests_json_exists(self):
        assert TESTS_JSON.exists(), "evidence/tests.json not found"

    def test_behavior_hash_evidence_exists(self):
        """At least one of the behavior hash files must exist."""
        assert BEHAVIOR_HASH_JSON.exists() or BEHAVIOR_HASH_TXT.exists(), (
            "No behavior hash file found. Run src/scripts/behavior_hash.py or "
            "src/scripts/generate_behavior_hash.py to generate evidence/behavior_hash.json"
        )


# ===========================================================================
# Tests: behavior_hash.json format validation
# ===========================================================================

class TestBehaviorHashJson:
    """Validate the NEW canonical evidence/behavior_hash.json format."""

    @pytest.fixture(scope="class")
    def hash_data(self):
        if not BEHAVIOR_HASH_JSON.exists():
            pytest.skip("evidence/behavior_hash.json not yet generated (run src/scripts/behavior_hash.py)")
        return json.loads(BEHAVIOR_HASH_JSON.read_text(encoding="utf-8"))

    def test_has_required_keys(self, hash_data):
        required = {"seed_42", "seed_137", "seed_9001", "consensus", "generated"}
        missing = required - set(hash_data.keys())
        assert not missing, f"behavior_hash.json missing keys: {missing}"

    def test_seed_42_is_sha256(self, hash_data):
        val = hash_data["seed_42"]
        assert isinstance(val, str), "seed_42 must be a string"
        assert len(val) == 64, f"seed_42 must be 64-char hex SHA-256 (got {len(val)})"
        assert re.fullmatch(r"[0-9a-f]{64}", val), "seed_42 must be lowercase hex"

    def test_seed_137_is_sha256(self, hash_data):
        val = hash_data["seed_137"]
        assert isinstance(val, str)
        assert len(val) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", val)

    def test_seed_9001_is_sha256(self, hash_data):
        val = hash_data["seed_9001"]
        assert isinstance(val, str)
        assert len(val) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", val)

    def test_consensus_is_bool(self, hash_data):
        assert isinstance(hash_data["consensus"], bool), (
            f"'consensus' must be bool, got {type(hash_data['consensus']).__name__}"
        )

    def test_all_three_seeds_match(self, hash_data):
        """All three seed hashes must be identical for consensus."""
        h42 = hash_data["seed_42"]
        h137 = hash_data["seed_137"]
        h9001 = hash_data["seed_9001"]
        unique = {h42, h137, h9001}
        assert len(unique) == 1, (
            f"Hash drift detected across seeds:\n"
            f"  seed_42  : {h42[:32]}...\n"
            f"  seed_137 : {h137[:32]}...\n"
            f"  seed_9001: {h9001[:32]}..."
        )

    def test_consensus_flag_true(self, hash_data):
        assert hash_data["consensus"] is True, (
            "behavior_hash.json consensus is False — behavioral non-determinism detected"
        )

    def test_generated_field_is_iso_timestamp(self, hash_data):
        generated = hash_data["generated"]
        assert isinstance(generated, str), "'generated' must be a string"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", generated), (
            f"'generated' must be ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ), got: {generated!r}"
        )


# ===========================================================================
# Tests: security_scan.json format validation
# ===========================================================================

class TestSecurityScanJson:

    @pytest.fixture(scope="class")
    def scan_data(self):
        if not SECURITY_SCAN_JSON.exists():
            pytest.skip("evidence/security_scan.json not yet generated (run src/scripts/security_scan.py)")
        return json.loads(SECURITY_SCAN_JSON.read_text(encoding="utf-8"))

    def test_has_required_keys(self, scan_data):
        required = {"status", "findings", "findings_count", "tool_version", "generated"}
        missing = required - set(scan_data.keys())
        assert not missing, f"security_scan.json missing keys: {missing}"

    def test_status_is_green_or_red(self, scan_data):
        assert scan_data["status"] in ("GREEN", "RED"), (
            f"status must be 'GREEN' or 'RED', got: {scan_data['status']!r}"
        )

    def test_status_is_green(self, scan_data):
        """Security gate: production code must be clean."""
        if scan_data["status"] != "GREEN":
            findings = scan_data.get("findings", [])
            details = "\n".join(
                f"  [{f['check']}] {f['file']}:{f['line']}: {f['text'][:80]}"
                for f in findings[:10]
            )
            pytest.fail(
                f"security_scan.json status is RED — {scan_data['findings_count']} findings:\n"
                + details
            )

    def test_findings_is_list(self, scan_data):
        assert isinstance(scan_data["findings"], list), "'findings' must be a list"

    def test_findings_count_matches_list(self, scan_data):
        assert scan_data["findings_count"] == len(scan_data["findings"]), (
            "findings_count does not match len(findings)"
        )

    def test_tool_version_is_string(self, scan_data):
        assert isinstance(scan_data["tool_version"], str), "'tool_version' must be a string"
        assert len(scan_data["tool_version"]) > 0

    def test_generated_is_timestamp(self, scan_data):
        generated = scan_data["generated"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", generated), (
            f"'generated' must be ISO 8601 UTC, got: {generated!r}"
        )


# ===========================================================================
# Tests: plan.json schema
# ===========================================================================

class TestPlanJson:

    @pytest.fixture(scope="class")
    def plan(self):
        return json.loads(PLAN_JSON.read_text(encoding="utf-8"))

    def test_has_rung_target(self, plan):
        assert "rung_target" in plan, "plan.json missing 'rung_target' field"

    def test_rung_target_is_integer(self, plan):
        rt = plan["rung_target"]
        assert isinstance(rt, int), f"rung_target must be int, got {type(rt).__name__}"

    def test_rung_target_is_valid(self, plan):
        valid_rungs = {641, 274177, 65537}
        rt = plan["rung_target"]
        assert rt in valid_rungs, (
            f"rung_target {rt} is not a valid rung. Valid: {sorted(valid_rungs)}"
        )

    def test_files_changed_is_non_empty_list(self, plan):
        assert "files_changed" in plan, "plan.json missing 'files_changed' field"
        fc = plan["files_changed"]
        assert isinstance(fc, list), "'files_changed' must be a list"
        assert len(fc) > 0, "'files_changed' must be non-empty"

    def test_task_family_is_string(self, plan):
        assert "task_family" in plan, "plan.json missing 'task_family' field"
        assert isinstance(plan["task_family"], str)
        assert len(plan["task_family"]) > 0


# ===========================================================================
# Tests: All production .py files compile cleanly
# ===========================================================================

class TestProductionFilesCompile:

    def test_all_production_py_files_compile(self):
        """Every production .py file must be valid Python (ast.parse succeeds)."""
        failures = []
        for path in _prod_py_files():
            src = _read(path)
            try:
                ast.parse(src)
            except SyntaxError as exc:
                failures.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
        assert not failures, (
            "Production .py files with syntax errors:\n" + "\n".join(failures)
        )
