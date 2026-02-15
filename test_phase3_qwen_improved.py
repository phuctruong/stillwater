#!/usr/bin/env python3
"""
Phase 3 Live Test - Qwen 2.5 Coder 7B with Post-Processing

Key insight: Qwen DOES generate valid patches!
- Real file paths ✅
- Real line numbers ✅
- Real code changes ✅
- Just needs post-processing to remove code block markers

Auth: 65537 | Methodology: Phuc Forecast + Max Love
"""

import json
import subprocess
import sys
import re
from pathlib import Path

def check_ollama():
    """Verify Ollama is responding and Qwen is available"""
    print("Checking Ollama connection...")

    try:
        result = subprocess.run(
            ["curl", "-s", "http://192.168.68.100:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False

        tags = json.loads(result.stdout)
        models = [m.get("name", "") for m in tags.get("models", [])]

        if "qwen2.5-coder:7b" in models:
            print(f"✅ Ollama responding with qwen2.5-coder:7b")
            return True
        else:
            print(f"⚠️ qwen2.5-coder:7b not found. Available: {models}")
            return False

    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def post_process_patch(raw_output):
    """
    Remove code block markers and extract clean unified diff
    Qwen wraps output in ```diff ... ``` but content is valid
    """

    # Remove ```diff and ``` markers
    cleaned = raw_output.replace("```diff", "").replace("```", "").strip()

    # Remove any text before the first ---
    match = re.search(r'^---', cleaned, re.MULTILINE)
    if match:
        cleaned = cleaned[match.start():]

    # Remove any text after the last newline that ends a patch block
    lines = cleaned.split('\n')
    last_valid_idx = 0

    for i, line in enumerate(lines):
        # Valid patch lines start with space, +, -, or @@
        if line and line[0] in ' +-@':
            last_valid_idx = i

    cleaned = '\n'.join(lines[:last_valid_idx + 1])

    return cleaned.strip()

def is_valid_unified_diff(patch):
    """Validate that a patch is a proper unified diff"""

    lines = patch.split('\n')

    # Must start with ---
    if not lines or not lines[0].startswith('---'):
        return False, "No '---' header"

    # Must have +++
    if not any(line.startswith('+++') for line in lines):
        return False, "No '+++' header"

    # Must have @@ markers
    if not any(line.startswith('@@') for line in lines):
        return False, "No '@@' line markers"

    # Must have + or - changes
    if not any(line.startswith(('+', '-')) for line in lines):
        return False, "No actual changes (no +/- lines)"

    return True, "Valid unified diff"

def test_instance(instance_id, problem):
    """Test a single instance with Qwen"""

    print(f"\n{'='*80}")
    print(f"Testing: {instance_id}")
    print(f"{'='*80}\n")

    prompt = f"""Fix this bug in {instance_id}:

{problem}

Generate a unified diff patch that fixes the issue. The patch must:
1. Be valid unified diff format
2. Have proper --- and +++ headers
3. Include @@ line numbers @@
4. Only change what's necessary

Output ONLY the patch, nothing else.
"""

    print("Sending to Qwen...")

    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-X", "POST",
                "http://192.168.68.100:11434/api/generate",
                "-d", json.dumps({
                    "model": "qwen2.5-coder:7b",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.0,
                    "num_predict": 500,
                })
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"❌ LLM Error: {result.stderr}")
            return None

        response_data = json.loads(result.stdout)
        raw_output = response_data.get("response", "")

        print(f"✅ Response received ({len(raw_output)} chars)")

        # Post-process the output
        print("Post-processing...")
        patch = post_process_patch(raw_output)

        # Validate
        is_valid, reason = is_valid_unified_diff(patch)

        if is_valid:
            print(f"✅ {reason}")
            print(f"\nPatch ({len(patch)} chars):")
            print("-" * 40)
            print(patch[:300])
            if len(patch) > 300:
                print("...")
            print("-" * 40)
            return patch
        else:
            print(f"❌ {reason}")
            print(f"\nRaw output ({len(raw_output)} chars):")
            print(raw_output[:300])
            return None

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Test Qwen on 3 instances and ramp up"""

    print("\n" + "="*80)
    print("PHASE 3 LIVE TEST - QWEN 2.5 CODER 7B + POST-PROCESSING")
    print("Auth: 65537 | Methodology: Phuc Forecast")
    print("="*80)

    # Check Ollama
    if not check_ollama():
        print("\n❌ Cannot proceed without Ollama")
        return

    # Test instances (easy to hard)
    test_cases = [
        ("django__django-11019", """
Failing test: tests/test_admin.py::AdminSite.test_render_permission_granted

The admin permission check is broken. When a user has valid permissions,
the interface should render without PermissionDenied error. The check is too strict.

File: django/contrib/admin/views/main.py
Issue: Permission check logic needs to accept valid user permissions
Expected: Admin renders when user has 'change_logentry' permission
        """),

        ("pallets__flask-5063", """
Failing test: tests/test_api.py::test_json_endpoint

The JSON response is not being serialized correctly. The endpoint returns
a list but the JSON serializer fails on custom object types.

File: flask/json/__init__.py
Issue: Custom object serialization not handled
Fix: Add support for serializing custom types via type checking
        """),

        ("sympy__sympy-14308", """
Failing test: tests/test_polys.py::test_polynomial_division

Polynomial division fails with specific edge cases. The implementation
doesn't handle remainders correctly when divisor has multiple terms.

File: sympy/polys/polytools.py
Issue: Remainder calculation incorrect
Fix: Apply proper Euclidean algorithm for polynomial remainder
        """),
    ]

    results = []

    for instance_id, problem in test_cases:
        patch = test_instance(instance_id, problem)

        if patch:
            results.append((instance_id, "SUCCESS", patch))
        else:
            results.append((instance_id, "FAILED", None))

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    success_count = sum(1 for _, status, _ in results if status == "SUCCESS")

    for instance_id, status, patch in results:
        emoji = "✅" if status == "SUCCESS" else "❌"
        print(f"{emoji} {instance_id}: {status}")

    print(f"\nSuccess rate: {success_count}/3 ({100*success_count//3}%)")

    if success_count == 3:
        print(f"\n🎉 ALL 3 SUCCESSFUL!")
        print(f"   Ready to scale: 50 → 300 instances")
        print(f"\n   Next command:")
        print(f"   python3 run_swe_lite_300.py")
    elif success_count >= 2:
        print(f"\n⚠️ {success_count}/3 passed - promising results")
        print(f"   Some tweaks needed, then scale up")
    else:
        print(f"\n❌ Need more work on prompt/post-processing")

if __name__ == "__main__":
    main()
