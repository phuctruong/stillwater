"""
Extract test directives from test patches.

Based on SWE-bench test_spec/python.py
"""

import re
from typing import List

# File extensions that are not test files
NON_TEST_EXTS = [
    ".json",
    ".txt",
    ".md",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".csv",
    ".tsv",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".yml",
    ".yaml",
]


def get_test_directives(repo: str, test_patch: str) -> List[str]:
    """
    Extract test directives from a test patch.

    Args:
        repo: Repository name (e.g., "django/django")
        test_patch: The test patch content

    Returns:
        List of test directives to run

    Example:
        >>> directives = get_test_directives("django/django", patch)
        >>> # Returns: ["admin_inlines.tests", "forms_tests.tests.test_media"]
    """
    if not test_patch:
        return []

    # Extract file paths from diff headers
    diff_pat = r"diff --git a/.* b/(.*)"
    directives = re.findall(diff_pat, test_patch)

    # Remove non-test files
    directives = [
        d for d in directives if not any(d.endswith(ext) for ext in NON_TEST_EXTS)
    ]

    # Apply repo-specific transformations
    if repo == "django/django":
        return _transform_django_directives(directives)
    else:
        # For other repos, return file paths as-is
        return directives


def _transform_django_directives(directives: List[str]) -> List[str]:
    """
    Transform Django test file paths to module references.

    Django test runner uses module references, not file paths.

    Example:
        tests/admin_inlines/tests.py -> admin_inlines.tests
        tests/forms_tests/tests/test_media.py -> forms_tests.tests.test_media
    """
    transformed = []

    for d in directives:
        # Remove .py extension
        if d.endswith(".py"):
            d = d[:-3]

        # Remove "tests/" prefix
        if d.startswith("tests/"):
            d = d[6:]

        # Convert path separators to dots
        d = d.replace("/", ".")

        transformed.append(d)

    return transformed
