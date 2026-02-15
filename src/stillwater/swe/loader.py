"""
SWE-bench dataset loader.

Loads instances from the SWE-bench dataset and provides structured access
to problem statements, repositories, and test configurations.

Dataset structure:
    - instance_id: Unique identifier (e.g., "django__django-12345")
    - problem_statement: Description of the bug to fix
    - repo: Repository name (e.g., "django/django")
    - base_commit: Git commit to checkout
    - test_patch: How to set up and run tests
    - gold_patch: Ground truth solution (not shown to model)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import json


@dataclass
class SWEInstance:
    """
    A single SWE-bench instance.

    Represents one bug-fixing task with all metadata needed for
    verification-based patching.
    """
    instance_id: str
    problem_statement: str
    repo: str
    base_commit: str
    test_patch: str
    gold_patch: Optional[str] = None  # Ground truth (for evaluation only)
    hints_text: Optional[str] = None
    created_at: Optional[str] = None
    patch: Optional[str] = None
    test_directives: Optional[str] = None
    version: Optional[str] = None

    def __repr__(self) -> str:
        return f"SWEInstance({self.instance_id})"


def load_instance(instance_id: str, dataset_path: Optional[Path] = None) -> SWEInstance:
    """
    Load a single SWE-bench instance by ID.

    Args:
        instance_id: Instance identifier (e.g., "django__django-12345")
        dataset_path: Path to local dataset file (optional)

    Returns:
        SWEInstance with all metadata

    Raises:
        ValueError: If instance not found

    Example:
        >>> instance = load_instance("django__django-12345")
        >>> print(instance.problem_statement)
        "Fix the bug in Django's..."
    """
    dataset = load_dataset(dataset_path)

    for item in dataset:
        if item.instance_id == instance_id:
            return item

    raise ValueError(f"Instance not found: {instance_id}")


def load_dataset(dataset_path: Optional[Path] = None) -> List[SWEInstance]:
    """
    Load the full SWE-bench dataset.

    Args:
        dataset_path: Path to local dataset file
                     If None, attempts to load from HuggingFace datasets library

    Returns:
        List of SWEInstance objects

    Example:
        >>> dataset = load_dataset()
        >>> print(f"Loaded {len(dataset)} instances")
        Loaded 300 instances
    """
    if dataset_path:
        return _load_from_file(dataset_path)
    else:
        return _load_from_huggingface()


def _load_from_file(path: Path) -> List[SWEInstance]:
    """
    Load dataset from local JSON/JSONL file.

    Supports both:
    - JSON array: [{"instance_id": "...", ...}, ...]
    - JSONL: one JSON object per line
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    instances = []

    # Try JSONL format first
    if path.suffix == ".jsonl":
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    instances.append(_parse_instance(data))
    else:
        # Try JSON array format
        with open(path, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    instances.append(_parse_instance(item))
            else:
                raise ValueError("JSON file must contain an array of instances")

    return instances


def _load_from_huggingface() -> List[SWEInstance]:
    """
    Load dataset from HuggingFace datasets library.

    Uses the princeton-nlp/SWE-bench dataset.
    Falls back to local cache if available.
    """
    try:
        from datasets import load_dataset as hf_load_dataset

        # Load from HuggingFace
        # Use "test" split (300 instances) or "dev" (small subset)
        dataset = hf_load_dataset("princeton-nlp/SWE-bench", split="test")

        instances = []
        for item in dataset:
            instances.append(_parse_instance(item))

        return instances

    except ImportError:
        raise ImportError(
            "HuggingFace datasets library not installed. "
            "Install with: pip install datasets\n"
            "Or provide a local dataset_path to load_dataset()"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load from HuggingFace: {e}")


def _parse_instance(data: Dict[str, Any]) -> SWEInstance:
    """
    Parse a raw dataset dict into SWEInstance.

    Handles variations in field names across dataset versions.
    """
    # Required fields
    instance_id = data["instance_id"]
    problem_statement = data.get("problem_statement", "")
    repo = data.get("repo", "")
    base_commit = data.get("base_commit", "")
    test_patch = data.get("test_patch", "")

    # Optional fields
    gold_patch = data.get("patch", None)
    hints_text = data.get("hints_text", None)
    created_at = data.get("created_at", None)
    test_directives = data.get("test_directives", None)
    version = data.get("version", None)

    return SWEInstance(
        instance_id=instance_id,
        problem_statement=problem_statement,
        repo=repo,
        base_commit=base_commit,
        test_patch=test_patch,
        gold_patch=gold_patch,
        hints_text=hints_text,
        created_at=created_at,
        test_directives=test_directives,
        version=version,
    )


def get_verified_subset() -> List[str]:
    """
    Get the list of 128 infrastructure-resilient instance IDs.

    These are the "hardest 10" + 118 instances with stable test infrastructure,
    as identified in the design document.

    Returns:
        List of instance IDs that have been validated for clean test environments

    Note:
        This is a curated subset where test flakiness and Docker issues
        have been minimized. Good starting point for initial development.
    """
    # TODO: Populate this list after validating instances
    # For now, return empty list until we've done the validation
    return []


def filter_by_repo(instances: List[SWEInstance], repo_pattern: str) -> List[SWEInstance]:
    """
    Filter instances by repository pattern.

    Args:
        instances: List of instances to filter
        repo_pattern: Pattern to match (e.g., "django", "requests")

    Returns:
        Filtered list of instances

    Example:
        >>> dataset = load_dataset()
        >>> django_instances = filter_by_repo(dataset, "django")
        >>> print(f"Found {len(django_instances)} Django instances")
    """
    return [
        inst for inst in instances
        if repo_pattern.lower() in inst.repo.lower()
    ]
