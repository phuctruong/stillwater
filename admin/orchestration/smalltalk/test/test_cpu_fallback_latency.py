"""
Test: CPU fallback latency SLA < 50ms.

Verifies:
- CPU fallback (queue miss) completes in < 50ms P99
- High-GLOW path < 50ms
- Low-GLOW path (repo lookup) < 50ms
- Completely empty environment still < 50ms (last-resort fallback)

rung_target: 641
EXIT_PASS: P99 latency < 50ms across all 100 iterations
EXIT_BLOCKED: Any P99 exceeds 50ms
"""

import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.cpu import SmallTalkCPU
from admin.orchestration.smalltalk.database import BanterQueueDB, JokeRepo, TechFactRepo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_db():
    return BanterQueueDB(":memory:")


@pytest.fixture
def cpu_no_queue(empty_db):
    """SmallTalkCPU with empty queue so every call is a CPU fallback."""
    data_dir = str(Path(__file__).parent.parent)
    return SmallTalkCPU(db=empty_db, data_dir=data_dir)


@pytest.fixture
def cpu_empty_repos(empty_db):
    """SmallTalkCPU with empty repos — forces last-resort fallback path."""
    return SmallTalkCPU(
        db=empty_db,
        joke_repo=JokeRepo(),     # empty
        fact_repo=TechFactRepo(),  # empty
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCPUFallbackLatency:

    def test_cpu_fallback_under_50ms_p99(self, cpu_no_queue):
        """
        CPU fallback path must complete < 50ms (P99 over 100 iterations).
        """
        latencies_ms = []
        prompts = [
            "I just shipped the OAuth feature!",
            "Hey there",
            "Working on python performance",
            "debugging the sql query",
            "feels tired today",
            "AMAZING!! just launched!!",
            "can you help me with docker?",
            "git commit message ideas",
            "deploying to production now",
            "excited about the new react feature",
        ]

        for i in range(100):
            prompt = prompts[i % len(prompts)]
            start = time.perf_counter()
            token = cpu_no_queue.generate(
                user_id="cpu_test_user",
                session_id="cpu_test_sess",
                prompt=prompt,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies_ms.append(elapsed_ms)
            assert token.response, f"Iteration {i}: empty response"

        latencies_ms.sort()
        p99_idx = max(0, int(len(latencies_ms) * 0.99) - 1)
        p99_ms = latencies_ms[p99_idx]
        median_ms = latencies_ms[len(latencies_ms) // 2]

        assert p99_ms < 50.0, (
            f"CPU fallback P99 = {p99_ms:.3f}ms — exceeds 50ms SLA. "
            f"Median = {median_ms:.3f}ms. Max = {max(latencies_ms):.3f}ms."
        )

    def test_high_glow_path_under_50ms(self, cpu_no_queue):
        """High-GLOW template generation must complete < 50ms."""
        # These prompts are designed to trigger glow > 0.6
        high_glow_prompts = [
            "I just got PROMOTED!! Amazing day!!",
            "We just shipped the product!! Incredible!!",
            "Our team WON the hackathon!! So excited!!",
        ]
        for prompt in high_glow_prompts:
            start = time.perf_counter()
            token = cpu_no_queue.generate(
                user_id="glow_user",
                session_id="glow_sess",
                prompt=prompt,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert elapsed_ms < 50.0, (
                f"High-GLOW path took {elapsed_ms:.2f}ms for prompt: {prompt!r}"
            )
            assert token.glow_score > 0.6, (
                f"Expected high GLOW, got {token.glow_score} for: {prompt!r}"
            )

    def test_low_glow_repo_path_under_50ms(self, cpu_no_queue):
        """Low-GLOW repo lookup path must complete < 50ms."""
        low_glow_prompts = [
            "working on python today",
            "sql query optimization",
            "docker container setup",
        ]
        for prompt in low_glow_prompts:
            start = time.perf_counter()
            token = cpu_no_queue.generate(
                user_id="repo_user",
                session_id="repo_sess",
                prompt=prompt,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert elapsed_ms < 50.0, (
                f"Low-GLOW repo path took {elapsed_ms:.2f}ms for: {prompt!r}"
            )

    def test_empty_repos_fallback_under_50ms(self, cpu_empty_repos):
        """Last-resort fallback (no repos) must still complete < 50ms."""
        start = time.perf_counter()
        token = cpu_empty_repos.generate(
            user_id="empty_user",
            session_id="empty_sess",
            prompt="hello",
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 50.0, (
            f"Last-resort fallback took {elapsed_ms:.2f}ms"
        )
        assert token.response, "Last-resort fallback must return non-empty string"

    def test_token_latency_field_matches_measured(self, cpu_no_queue):
        """WarmToken.latency_ms must approximate real measured latency."""
        start = time.perf_counter()
        token = cpu_no_queue.generate(
            user_id="lat_user",
            session_id="lat_sess",
            prompt="testing latency",
        )
        wall_ms = (time.perf_counter() - start) * 1000

        # Token's self-reported latency should be in the same ballpark
        # (within 10x — measurement overhead can vary)
        assert token.latency_ms > 0.0, "latency_ms must be positive"
        assert token.latency_ms < wall_ms + 5.0, (
            f"Token reports {token.latency_ms:.2f}ms but wall clock is {wall_ms:.2f}ms"
        )
