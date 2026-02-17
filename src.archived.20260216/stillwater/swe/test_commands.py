"""
Test command configuration for different repositories.

Based on SWE-bench official test specifications.
"""

from typing import Dict, List

# Test command templates
TEST_DJANGO = "./tests/runtests.py --verbosity 2 --settings=test_sqlite --parallel 1"
TEST_PYTEST = "pytest -rA --tb=no -p no:cacheprovider"
TEST_PYTEST_VERBOSE = "pytest -xvs"

# Repository-specific test commands
# Maps repo name to test command
REPO_TEST_COMMANDS: Dict[str, str] = {
    "django/django": TEST_DJANGO,
    "psf/requests": TEST_PYTEST,
    "pytest-dev/pytest": TEST_PYTEST,
    "pallets/flask": TEST_PYTEST,
    "scikit-learn/scikit-learn": TEST_PYTEST,
    "matplotlib/matplotlib": TEST_PYTEST,
    "sympy/sympy": "bin/test",  # SymPy uses custom test script
    "sphinx-doc/sphinx": "tox --sitepackages -e py",  # Sphinx uses tox
    "pydata/xarray": TEST_PYTEST,
    "astropy/astropy": TEST_PYTEST,
    "pylint-dev/pylint": TEST_PYTEST,
    "marshmallow-code/marshmallow": TEST_PYTEST,
    "mwaskom/seaborn": TEST_PYTEST,
}

# Default test command for repos not in the map
DEFAULT_TEST_COMMAND = TEST_PYTEST_VERBOSE


def get_test_command(repo: str, test_directives: List[str] = None) -> str:
    """
    Get the test command for a repository.

    Args:
        repo: Repository name (e.g., "django/django")
        test_directives: Optional list of test directives to run

    Returns:
        Full test command string
    """
    base_command = REPO_TEST_COMMANDS.get(repo, DEFAULT_TEST_COMMAND)

    if test_directives:
        directives_str = " ".join(test_directives)
        return f"{base_command} {directives_str}"

    return base_command


def get_environment_vars(repo: str) -> Dict[str, str]:
    """
    Get environment variables needed for testing a specific repo.

    Args:
        repo: Repository name

    Returns:
        Dictionary of environment variable names to values
    """
    # Django needs locale environment
    if repo == "django/django":
        return {
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
            "PYTHONIOENCODING": "utf8",
            "LANGUAGE": "en_US:en",
        }

    return {}
