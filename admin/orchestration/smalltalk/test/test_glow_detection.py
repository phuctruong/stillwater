"""
Test: GLOW signal detection (emotional/communicative intensity).

GLOW (0.0–1.0) = emotional intensity of a user message.
High GLOW (> 0.6) → CPU generates from keyword+template
Low GLOW (<= 0.6) → CPU pulls from repos

Verifies:
- detect_glow() returns float in [0.0, 1.0]
- High-intensity prompts produce GLOW > 0.6
- Low-intensity prompts produce GLOW <= 0.6
- GLOW is deterministic (same input → same float always)
- detect_register() correctly classifies formality, length, urgency, energy
- RegisterProfile.glow_score maps energy to GLOW float correctly

rung_target: 641
EXIT_PASS: All GLOW classifications correct, all deterministic
EXIT_BLOCKED: Non-deterministic output or wrong GLOW bucket
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.cpu import SmallTalkCPU
from admin.orchestration.smalltalk.database import BanterQueueDB, JokeRepo, TechFactRepo
from admin.orchestration.smalltalk.models import RegisterProfile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cpu():
    """Shared SmallTalkCPU instance for GLOW tests (empty DB, empty repos)."""
    return SmallTalkCPU(
        db=BanterQueueDB(":memory:"),
        joke_repo=JokeRepo(),
        fact_repo=TechFactRepo(),
    )


# ---------------------------------------------------------------------------
# GLOW detection tests
# ---------------------------------------------------------------------------

class TestGlowDetection:

    @pytest.mark.parametrize("prompt,expected_high", [
        # High-GLOW prompts (should return > 0.6)
        ("I just got PROMOTED!! Amazing day!!", True),
        ("WE WON THE HACKATHON!! SO EXCITED!!", True),
        ("I am devastated. My co-founder just died.", True),
        ("FINALLY SHIPPED IT!!! incredible feeling!!!", True),
        ("We just launched!! Amazing team!!", True),
        ("I got engaged!! Best day of my life!!", True),
        # Low-GLOW prompts (should return <= 0.6)
        ("working on python today", False),
        ("debugging the sql query", False),
        ("can you help me with docker?", False),
        ("git commit message ideas", False),
        ("hey", False),
        ("what is the weather like?", False),
    ])
    def test_glow_classification(self, cpu, prompt, expected_high):
        """Classify GLOW as high/low based on known prompts."""
        glow = cpu.detect_glow(prompt)
        assert 0.0 <= glow <= 1.0, f"GLOW out of range: {glow} for: {prompt!r}"
        if expected_high:
            assert glow > 0.6, (
                f"Expected GLOW > 0.6 for high-intensity prompt, got {glow}\n"
                f"Prompt: {prompt!r}"
            )
        else:
            assert glow <= 0.6, (
                f"Expected GLOW <= 0.6 for low-intensity prompt, got {glow}\n"
                f"Prompt: {prompt!r}"
            )

    def test_glow_is_deterministic(self, cpu):
        """Same prompt → same GLOW score every call."""
        prompt = "I just shipped the product! AMAZING! Incredible team!!"
        scores = [cpu.detect_glow(prompt) for _ in range(20)]
        assert len(set(scores)) == 1, (
            f"Non-deterministic GLOW: got {len(set(scores))} different values: {set(scores)}"
        )

    def test_glow_range_bounds(self, cpu):
        """GLOW score always in [0.0, 1.0]."""
        extreme_prompts = [
            "",
            "a",
            "AAAA!!!! WOW!!! INCREDIBLE!! AMAZING!! OMG!!",
            "x" * 1000,
            "!!!!!!!!!!!!!!!!",
        ]
        for p in extreme_prompts:
            glow = cpu.detect_glow(p)
            assert 0.0 <= glow <= 1.0, (
                f"GLOW out of bounds ({glow}) for prompt of length {len(p)}"
            )

    def test_glow_empty_string(self, cpu):
        """Empty string produces GLOW = 0.0 (no signals)."""
        glow = cpu.detect_glow("")
        assert glow == 0.0, f"Expected 0.0 for empty string, got {glow}"

    def test_glow_multiple_exclamation_marks(self, cpu):
        """Multiple exclamation marks boost GLOW."""
        single = cpu.detect_glow("nice work!")
        multi = cpu.detect_glow("nice work!!!")
        assert multi >= single, (
            f"Multiple '!' should not reduce GLOW. single={single}, multi={multi}"
        )

    def test_glow_celebration_keywords(self, cpu):
        """Celebration keywords boost GLOW above baseline."""
        baseline = cpu.detect_glow("hello there")
        with_celebration = cpu.detect_glow("Congratulations, you shipped it!")
        assert with_celebration > baseline, (
            f"Celebration keyword should boost GLOW. baseline={baseline}, with_celeb={with_celebration}"
        )

    def test_glow_high_intensity_keywords(self, cpu):
        """High-intensity emotional keywords (died, devastated, etc.) push GLOW high."""
        glow = cpu.detect_glow("My colleague died yesterday.")
        assert glow >= 0.3, (
            f"'died' keyword should register significant GLOW, got {glow}"
        )

    def test_glow_caps_words(self, cpu):
        """ALL_CAPS words (4+ chars) boost GLOW."""
        baseline = cpu.detect_glow("nice work today")
        with_caps = cpu.detect_glow("nice WORK today")
        # Single 4-char caps should give a small boost
        assert with_caps >= baseline


# ---------------------------------------------------------------------------
# Register detection tests
# ---------------------------------------------------------------------------

class TestRegisterDetection:

    def test_formal_register(self, cpu):
        """Formal markers → formality='formal'."""
        prompt = "Would you kindly assist me with the authentication implementation?"
        register = cpu.detect_register(prompt)
        assert register.formality == "formal", (
            f"Expected formal, got '{register.formality}' for: {prompt!r}"
        )

    def test_casual_register(self, cpu):
        """Casual markers → formality='casual'."""
        prompt = "hey can u help me fix auth lol"
        register = cpu.detect_register(prompt)
        assert register.formality == "casual", (
            f"Expected casual, got '{register.formality}' for: {prompt!r}"
        )

    def test_terse_length(self, cpu):
        """Short prompt (< 15 words) → length='terse'."""
        prompt = "help with auth"
        register = cpu.detect_register(prompt)
        assert register.length == "terse", (
            f"Expected terse for short prompt, got '{register.length}'"
        )

    def test_verbose_length(self, cpu):
        """Long prompt (>= 15 words) → length='verbose'."""
        prompt = (
            "I am currently working on implementing the authentication flow "
            "for our OAuth3 integration and I need some guidance on the "
            "token refresh mechanism and expiry handling strategy."
        )
        register = cpu.detect_register(prompt)
        assert register.length == "verbose", (
            f"Expected verbose for long prompt, got '{register.length}'"
        )

    def test_urgent_register(self, cpu):
        """Urgency markers → urgency='urgent'."""
        prompt = "Production is down! We need to fix this immediately!"
        register = cpu.detect_register(prompt)
        assert register.urgency == "urgent", (
            f"Expected urgent, got '{register.urgency}' for: {prompt!r}"
        )

    def test_reflective_register(self, cpu):
        """Reflective markers → urgency='reflective'."""
        prompt = "I am thinking about the long-term strategy for our authentication system"
        register = cpu.detect_register(prompt)
        assert register.urgency == "reflective", (
            f"Expected reflective, got '{register.urgency}' for: {prompt!r}"
        )

    def test_high_energy_register(self, cpu):
        """Multiple exclamation marks / caps → energy='high'."""
        prompt = "This is AMAZING!! I can't believe we finally shipped it!!"
        register = cpu.detect_register(prompt)
        assert register.energy == "high", (
            f"Expected high energy, got '{register.energy}' for: {prompt!r}"
        )

    def test_low_energy_register(self, cpu):
        """Exhaustion keywords → energy='low'."""
        prompt = "I am so tired today, it has been a really tough and exhausting week"
        register = cpu.detect_register(prompt)
        assert register.energy == "low", (
            f"Expected low energy, got '{register.energy}' for: {prompt!r}"
        )

    def test_register_is_deterministic(self, cpu):
        """Same prompt → same RegisterProfile every call."""
        prompt = "Would you kindly help me with OAuth3 implementation please?"
        registers = [cpu.detect_register(prompt) for _ in range(10)]
        first = registers[0]
        for r in registers[1:]:
            assert r.formality == first.formality
            assert r.length == first.length
            assert r.urgency == first.urgency
            assert r.energy == first.energy

    def test_register_profile_glow_score(self):
        """RegisterProfile.glow_score maps energy correctly."""
        assert RegisterProfile(energy="high").glow_score == 0.8
        assert RegisterProfile(energy="medium").glow_score == 0.5
        assert RegisterProfile(energy="low").glow_score == 0.2
