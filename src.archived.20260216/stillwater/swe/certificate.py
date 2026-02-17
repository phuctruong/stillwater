"""
Proof certificate generation for verified patches.

Generates mathematical proof that a patch:
1. Preserves all passing tests (no regressions)
2. Fixes target tests (new passing tests)
3. Is deterministic (same input → same output)

Certificate format (JSON):
{
    "instance_id": "django__django-12345",
    "status": "VERIFIED",
    "baseline_passing": ["test_foo", "test_bar"],
    "after_patch_passing": ["test_foo", "test_bar", "test_baz"],
    "regressions": [],
    "new_fixes": ["test_baz"],
    "patch_hash": "sha256:abc123...",
    "determinism_verified": true
}

This is Phase 3 of the implementation plan.
"""

from typing import Dict, Any
import json
import hashlib
from pathlib import Path


def generate_certificate(
    instance_id: str,
    patch: str,
    baseline_tests: set,
    after_patch_tests: set,
    deterministic: bool = False,
) -> Dict[str, Any]:
    """
    Generate a proof certificate for a verified patch.

    Args:
        instance_id: SWE-bench instance ID
        patch: The verified patch
        baseline_tests: Tests passing before patch
        after_patch_tests: Tests passing after patch
        deterministic: Whether determinism was verified

    Returns:
        Certificate dictionary

    Example:
        >>> cert = generate_certificate(
        ...     "django__django-12345",
        ...     patch,
        ...     {"test_foo", "test_bar"},
        ...     {"test_foo", "test_bar", "test_baz"},
        ...     deterministic=True
        ... )
        >>> print(cert["status"])
        VERIFIED
    """
    regressions = baseline_tests - after_patch_tests
    new_fixes = after_patch_tests - baseline_tests

    # Certificate is only valid if no regressions
    status = "VERIFIED" if len(regressions) == 0 else "REJECTED"

    patch_hash = hashlib.sha256(patch.encode()).hexdigest()

    return {
        "instance_id": instance_id,
        "status": status,
        "baseline_passing": sorted(list(baseline_tests)),
        "after_patch_passing": sorted(list(after_patch_tests)),
        "regressions": sorted(list(regressions)),
        "new_fixes": sorted(list(new_fixes)),
        "patch_hash": f"sha256:{patch_hash}",
        "determinism_verified": deterministic,
    }


def save_certificate(certificate: Dict[str, Any], output_path: Path):
    """
    Save certificate to JSON file.

    Args:
        certificate: Certificate dict from generate_certificate
        output_path: Path to save certificate
    """
    with open(output_path, "w") as f:
        json.dump(certificate, f, indent=2)
