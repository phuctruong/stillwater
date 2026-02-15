"""Stillwater Benchmark Suite.

Each benchmark produces a BenchResult. The registry tracks all benchmarks.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BenchResult:
    """Result of a single benchmark run."""

    name: str
    passed: int
    total: int
    elapsed_ms: float
    details: list[dict] = field(default_factory=list)

    @property
    def score(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0

    @property
    def ok(self) -> bool:
        return self.passed >= self.total


# Registry of all benchmarks: name -> (module_path, run function name, threshold)
BENCHMARKS: dict[str, dict] = {
    "hallucination": {
        "module": "stillwater.bench.hallucination",
        "description": "Hallucination Gate",
        "threshold": 10,
        "total": 10,
    },
    "counting": {
        "module": "stillwater.bench.counting",
        "description": "Counting Accuracy",
        "threshold": 9,
        "total": 10,
    },
    "math_exact": {
        "module": "stillwater.bench.math_exact",
        "description": "Math Exactness",
        "threshold": 8,
        "total": 10,
    },
    "compositionality": {
        "module": "stillwater.bench.compositionality",
        "description": "Compositional Generalization",
        "threshold": 9,
        "total": 10,
    },
    "verification": {
        "module": "stillwater.bench.verification",
        "description": "Verification Correctness",
        "threshold": 5,
        "total": 5,
    },
    "security": {
        "module": "stillwater.bench.security",
        "description": "Security Injection",
        "threshold": 10,
        "total": 10,
    },
    "compression": {
        "module": "stillwater.bench.compression",
        "description": "Context Compression",
        "threshold": 8,
        "total": 10,
    },
    "determinism": {
        "module": "stillwater.bench.determinism",
        "description": "Determinism",
        "threshold": 5,
        "total": 5,
    },
}
