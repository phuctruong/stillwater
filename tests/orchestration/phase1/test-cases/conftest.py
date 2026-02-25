"""conftest.py -- shared fixtures for Phase 1 orchestration audit tests.

Provides:
  - phase1_engine: TripleTwinEngine configured with real Phase 1 seeds
  - cpu_learner:   CPULearner loaded with default Phase 1 seeds

Constants are in phase1_shared.py (avoids pytest conftest resolution collisions).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stillwater.cpu_learner import CPULearner
from stillwater.data_registry import DataRegistry
from stillwater.triple_twin import TripleTwinEngine

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "phase1_shared", Path(__file__).with_name("phase1_shared.py")
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PHASE1_LABELS = _mod.PHASE1_LABELS
PHASE1_THRESHOLD = _mod.PHASE1_THRESHOLD
SEED_CONFIDENCE = _mod.SEED_CONFIDENCE
PHASE1_DATASET = _mod.PHASE1_DATASET
HAPPY_PATH_INDICES = _mod.HAPPY_PATH_INDICES
BREAKING_PATTERNS = _mod.BREAKING_PATTERNS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _find_stillwater_root() -> Path:
    """Locate the stillwater repo root by walking up from this file."""
    candidate = Path(__file__).resolve()
    for _ in range(10):
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists() and (candidate / "data").exists():
            return candidate
    raise RuntimeError("Could not find stillwater repo root from test file")


@pytest.fixture()
def stillwater_root() -> Path:
    """Return the stillwater repository root path."""
    return _find_stillwater_root()


@pytest.fixture()
def phase1_engine(stillwater_root: Path) -> TripleTwinEngine:
    """TripleTwinEngine loaded from the real data/default/ directory.

    CPU-only mode (no LLM client) -- matches the simulation run.
    """
    registry = DataRegistry(repo_root=stillwater_root)
    return TripleTwinEngine(registry=registry, llm_client=None)


@pytest.fixture()
def cpu_learner(stillwater_root: Path) -> CPULearner:
    """CPULearner for Phase 1 with default seeds loaded from the real seeds file.

    This manually reads the JSONL seeds and injects them into the learner,
    bypassing TripleTwinEngine so we can test the learner in isolation.
    """
    learner = CPULearner(phase="phase1")
    seeds_path = stillwater_root / "data" / "default" / "seeds" / "small-talk-seeds.jsonl"
    if seeds_path.exists():
        for line in seeds_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("phase") != "phase1":
                continue
            kw = record.get("keyword")
            if not kw:
                continue
            learner._patterns[kw] = {
                "count": record.get("count", 1),
                "label": record.get("label", "unknown"),
                "examples": record.get("examples", []),
            }
            learner._confidence_cache.pop(kw, None)
    return learner


@pytest.fixture()
def seeds_path(stillwater_root: Path) -> Path:
    """Path to the default small-talk seeds JSONL file."""
    return stillwater_root / "data" / "default" / "seeds" / "small-talk-seeds.jsonl"


@pytest.fixture()
def seeds_records(seeds_path: Path) -> list:
    """Parsed list of seed records from the JSONL file."""
    records = []
    for line in seeds_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records
