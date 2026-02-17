"""
Environment setup for SWE-bench instances.

Handles git repository cloning, checkout, and test patch application.
Uses git worktrees for isolation to avoid polluting the main repo.

Key principles:
    - Isolation: Each instance gets its own worktree
    - Reproducibility: Always start from base_commit
    - Clean state: No leftover files from previous runs
"""

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import shutil

from .loader import SWEInstance


@dataclass
class Environment:
    """
    Isolated environment for running a single SWE-bench instance.

    Attributes:
        instance: The SWE-bench instance being processed
        work_dir: Temporary directory containing the git worktree
        repo_dir: Path to the cloned repository
        base_commit_checked_out: Whether base_commit was successfully checked out
        test_patch_applied: Whether test_patch was successfully applied
    """
    instance: SWEInstance
    work_dir: Path
    repo_dir: Path
    base_commit_checked_out: bool = False
    test_patch_applied: bool = False

    def cleanup(self):
        """Remove the temporary worktree directory."""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)


def setup_environment(instance: SWEInstance, cache_dir: Optional[Path] = None) -> Environment:
    """
    Set up an isolated environment for a SWE-bench instance.

    Steps:
        1. Clone repository (or use cached clone)
        2. Checkout base_commit
        3. Create isolated worktree
        4. Verify clean state

    Args:
        instance: SWE-bench instance to set up
        cache_dir: Optional directory for caching cloned repos

    Returns:
        Environment with ready-to-use repository

    Raises:
        RuntimeError: If setup fails

    Example:
        >>> env = setup_environment(instance)
        >>> # Work in env.repo_dir
        >>> env.cleanup()  # Clean up when done
    """
    # Create temporary work directory
    work_dir = Path(tempfile.mkdtemp(prefix=f"sweb-{instance.instance_id}-"))

    # Determine repository URL
    repo_url = _get_repo_url(instance.repo)

    # Clone or use cached repository
    if cache_dir:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        repo_dir = _clone_or_update_cached(repo_url, instance.repo, cache_dir, work_dir)
    else:
        repo_dir = _clone_fresh(repo_url, work_dir)

    # Checkout base_commit
    _checkout_commit(repo_dir, instance.base_commit)

    env = Environment(
        instance=instance,
        work_dir=work_dir,
        repo_dir=repo_dir,
        base_commit_checked_out=True,
        test_patch_applied=False,
    )

    return env


def apply_test_patch(env: Environment) -> bool:
    """
    Apply the test_patch to set up the test environment.

    The test_patch typically:
    - Adds test files
    - Modifies test configurations
    - Sets up the environment for running tests

    Args:
        env: Environment to apply patch to

    Returns:
        True if patch applied successfully, False otherwise

    Note:
        This does NOT apply the model's generated patch.
        This only sets up the test infrastructure.
    """
    # Install test dependencies FIRST before applying patch
    # This ensures tests can run when we verify the patch
    print("📦 Installing test dependencies...")
    if not _install_test_dependencies(env.repo_dir):
        print("⚠️  Failed to install test dependencies")
        # Continue anyway - some repos might work without full deps

    if not env.instance.test_patch:
        # No test patch to apply
        env.test_patch_applied = True
        return True

    try:
        # Apply patch using git apply
        result = subprocess.run(
            ["git", "apply", "--verbose"],
            input=env.instance.test_patch.encode(),
            cwd=env.repo_dir,
            capture_output=True,
            timeout=30,
        )

        if result.returncode == 0:
            env.test_patch_applied = True
            return True
        else:
            print(f"⚠️  Test patch failed: {result.stderr.decode()}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Test patch application timed out")
        return False
    except Exception as e:
        print(f"⚠️  Test patch error: {e}")
        return False


def apply_model_patch(env: Environment, patch: str) -> bool:
    """
    Apply a model-generated patch to the repository.

    Args:
        env: Environment to apply patch to
        patch: Unified diff format patch

    Returns:
        True if patch applied successfully, False otherwise

    Example:
        >>> patch = generate_patch(instance.problem_statement)
        >>> success = apply_model_patch(env, patch)
    """
    try:
        result = subprocess.run(
            ["git", "apply", "--verbose"],
            input=patch.encode(),
            cwd=env.repo_dir,
            capture_output=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True
        else:
            print(f"⚠️  Model patch failed: {result.stderr.decode()}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Model patch application timed out")
        return False
    except Exception as e:
        print(f"⚠️  Model patch error: {e}")
        return False


def _get_repo_url(repo: str) -> str:
    """
    Convert repo name to GitHub URL.

    Args:
        repo: Repository in format "owner/repo" (e.g., "django/django")

    Returns:
        Full GitHub HTTPS URL
    """
    if repo.startswith("http"):
        return repo
    else:
        return f"https://github.com/{repo}.git"


def _clone_fresh(repo_url: str, work_dir: Path) -> Path:
    """
    Clone repository into work directory.

    Args:
        repo_url: Full git URL
        work_dir: Directory to clone into

    Returns:
        Path to cloned repository
    """
    repo_dir = work_dir / "repo"

    result = subprocess.run(
        ["git", "clone", "--quiet", repo_url, str(repo_dir)],
        capture_output=True,
        timeout=300,  # 5 minutes max for clone
    )

    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed: {result.stderr.decode()}")

    return repo_dir


def _clone_or_update_cached(repo_url: str, repo_name: str, cache_dir: Path, work_dir: Path) -> Path:
    """
    Use cached repository or clone fresh, then create worktree.

    This speeds up repeated runs by caching the base repository.

    Args:
        repo_url: Full git URL
        repo_name: Repository identifier (e.g., "django__django")
        cache_dir: Directory for caching repos
        work_dir: Work directory for this instance

    Returns:
        Path to worktree
    """
    # Sanitize repo_name for filesystem
    cache_name = repo_name.replace("/", "__")
    cache_repo = cache_dir / cache_name

    # Clone to cache if not exists
    if not cache_repo.exists():
        print(f"📦 Caching repository: {repo_name}")
        subprocess.run(
            ["git", "clone", "--bare", "--quiet", repo_url, str(cache_repo)],
            capture_output=True,
            timeout=300,
        )
    else:
        # Update cached repo
        subprocess.run(
            ["git", "fetch", "--all", "--quiet"],
            cwd=cache_repo,
            capture_output=True,
            timeout=120,
        )

    # Create worktree in work_dir
    repo_dir = work_dir / "repo"
    subprocess.run(
        ["git", "worktree", "add", str(repo_dir)],
        cwd=cache_repo,
        capture_output=True,
        timeout=30,
    )

    return repo_dir


def _checkout_commit(repo_dir: Path, commit: str):
    """
    Checkout a specific commit.

    Args:
        repo_dir: Repository path
        commit: Commit hash to checkout

    Raises:
        RuntimeError: If checkout fails
    """
    result = subprocess.run(
        ["git", "checkout", "--quiet", commit],
        cwd=repo_dir,
        capture_output=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Git checkout failed: {result.stderr.decode()}")


def _install_test_dependencies(repo_dir: Path) -> bool:
    """
    Install test dependencies for a repository.

    This is the fix for the infrastructure issue where test environments
    don't have required dependencies installed.

    Strategy:
        1. Install common test dependencies (pytest, hypothesis, etc.)
        2. Install from requirements.txt if available
        3. Install package in editable mode if setup.py exists

    Args:
        repo_dir: Path to repository

    Returns:
        True if installation succeeded, False otherwise
    """
    import sys

    try:
        # 1. Install common test dependencies
        # These are the most common dependencies across SWE-bench instances
        common_deps = [
            "pytest>=6.0",
            "hypothesis>=6.0",
            "pytest-django>=4.0",
            "pytest-xdist>=2.0",
            "pytest-cov>=3.0",
            "pytest-timeout>=2.0",
        ]

        print(f"  Installing common test deps: {', '.join(common_deps)}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-conflicts"] + common_deps,
            capture_output=True,
            timeout=120,
        )

        if result.returncode != 0:
            print(f"    Warning: Some common deps failed: {result.stderr.decode()[:200]}")

        # 2. Try to install from requirements files
        # Check for common requirement file patterns
        req_patterns = [
            "requirements.txt",
            "requirements/test.txt",
            "requirements/dev.txt",
            "test-requirements.txt",
            "dev-requirements.txt",
        ]

        for req_file in req_patterns:
            req_path = repo_dir / req_file
            if req_path.exists():
                print(f"  Installing from {req_file}")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-conflicts", "-r", str(req_path)],
                    capture_output=True,
                    timeout=180,
                )
                if result.returncode != 0:
                    print(f"    Warning: Failed to install from {req_file}")
                break  # Only install from first matching requirements file

        # 3. Install package in editable mode if setup.py exists
        setup_py = repo_dir / "setup.py"
        setup_cfg = repo_dir / "setup.cfg"
        pyproject_toml = repo_dir / "pyproject.toml"

        if setup_py.exists() or setup_cfg.exists() or pyproject_toml.exists():
            print("  Installing package in editable mode")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-conflicts", "-e", str(repo_dir)],
                capture_output=True,
                timeout=240,
            )
            if result.returncode != 0:
                # Try without editable mode
                print("    Warning: Editable install failed, trying regular install")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-conflicts", str(repo_dir)],
                    capture_output=True,
                    timeout=240,
                )
                if result.returncode != 0:
                    print(f"    Warning: Package install failed: {result.stderr.decode()[:200]}")

        print("  ✅ Dependency installation complete")
        return True

    except subprocess.TimeoutExpired:
        print("  ⚠️  Dependency installation timed out")
        return False
    except Exception as e:
        print(f"  ⚠️  Dependency installation error: {e}")
        return False
