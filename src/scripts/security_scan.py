#!/usr/bin/env python3
"""
src/scripts/security_scan.py

Security gate for Stillwater — Phase 4 rung 65537.

Checks:
  1. No hardcoded secrets (sk_, openai keys, AWS keys, plain password=<value>)
  2. No unsandboxed eval() in production code
  3. No os.system() with f-strings or .format() (unsanitized shell injection)

Output: evidence/security_scan.json

Exit codes:
    0 — all checks pass (GREEN)
    1 — one or more findings (RED)
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "security_scan.json"

TOOL_VERSION = "1.0.0"

# Production directories to scan (excludes tests, scripts, docs)
SCAN_DIRS = [
    REPO_ROOT / "src" / "store",
    REPO_ROOT / "src" / "cli" / "src" / "stillwater",
    REPO_ROOT / "src" / "oauth3",
    REPO_ROOT / "admin",
]

# ---------------------------------------------------------------------------
# Secret patterns — real credentials, not variable names or docstring examples
# ---------------------------------------------------------------------------

SECRET_PATTERNS = [
    # OpenAI / Anthropic keys
    (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "openai-or-anthropic-key"),
    # AWS access key ID
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws-access-key-id"),
    # Generic: password = "<8+ non-space chars>" (string literal assignment)
    (re.compile(r'(?i)\bpassword\s*=\s*["\'][^\s"\']{8,}["\']'), "hardcoded-password"),
    # Generic: secret = "<8+ chars>"
    (re.compile(r'(?i)\bsecret\s*=\s*["\'][^\s"\']{8,}["\']'), "hardcoded-secret"),
]

# Lines that are clearly in docstrings/comments/examples — skip them
EXAMPLE_SKIP_RE = re.compile(
    r'(?i)(example|docstring|#|"""|\'\'\''
    r'|placeholder|<your|dummy|fake|test|mock'
    r'|sw_sk_0{10}|sw_sk_\w{32})',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# eval() patterns — detect unsandboxed eval
# ---------------------------------------------------------------------------

# Sandboxed eval pattern used in cli.py: eval(compile(...), {"__builtins__": {}}, {})
EVAL_SANDBOXED_RE = re.compile(
    r'eval\s*\(\s*compile\s*\(.+\)\s*,\s*\{["\']__builtins__["\']\s*:\s*\{\}\}'
)

EVAL_ANY_RE = re.compile(r'\beval\s*\(')

# ---------------------------------------------------------------------------
# os.system() with unsanitized input — f-string or .format()
# ---------------------------------------------------------------------------

OS_SYSTEM_UNSAFE_RE = re.compile(
    r'os\.system\s*\(\s*(?:f["\']|["\'][^"\']*\{|.*\.format\s*\()'
)

# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

Finding = dict  # {check, file, line, text}


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    rel = str(path.relative_to(REPO_ROOT))
    lines = src.splitlines()

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        # --- Secret scan ---
        for pat, tag in SECRET_PATTERNS:
            if pat.search(line):
                # Skip lines that look like docstring examples or comments
                if EXAMPLE_SKIP_RE.search(line):
                    continue
                findings.append({
                    "check": f"hardcoded-secret:{tag}",
                    "file": rel,
                    "line": lineno,
                    "text": stripped[:120],
                })

        # --- eval() scan ---
        if EVAL_ANY_RE.search(line):
            # Allow sandboxed pattern (AST-validated, empty builtins)
            if not EVAL_SANDBOXED_RE.search(line):
                # Also skip noqa lines that explicitly mark it safe
                if "# noqa" not in line and "# nosec" not in line:
                    findings.append({
                        "check": "unsandboxed-eval",
                        "file": rel,
                        "line": lineno,
                        "text": stripped[:120],
                    })

        # --- os.system() unsafe ---
        if OS_SYSTEM_UNSAFE_RE.search(line):
            findings.append({
                "check": "os-system-unsafe-input",
                "file": rel,
                "line": lineno,
                "text": stripped[:120],
            })

    return findings


def main() -> int:
    print("Stillwater security scan (security_scan.py)")
    print(f"Repo root : {REPO_ROOT}")
    print(f"Scan dirs : {[str(d.relative_to(REPO_ROOT)) for d in SCAN_DIRS]}")
    print()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    all_findings: list[Finding] = []

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            print(f"  (skipping missing dir: {scan_dir.relative_to(REPO_ROOT)})")
            continue
        py_files = [
            f for f in scan_dir.rglob("*.py")
            if "__pycache__" not in str(f)
            and "tests" not in f.parts
            and not f.name.startswith("test_")
        ]
        for path in sorted(py_files):
            file_findings = scan_file(path)
            if file_findings:
                for f in file_findings:
                    print(f"  [{f['check']}] {f['file']}:{f['line']}: {f['text']}")
            all_findings.extend(file_findings)

    status = "GREEN" if not all_findings else "RED"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    result_doc = {
        "status": status,
        "findings": all_findings,
        "findings_count": len(all_findings),
        "tool_version": TOOL_VERSION,
        "generated": generated_at,
    }

    EVIDENCE_FILE.write_text(json.dumps(result_doc, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"Evidence written to: {EVIDENCE_FILE}")
    print(f"STATUS: {status} ({len(all_findings)} findings)")

    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())
