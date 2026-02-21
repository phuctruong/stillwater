#!/usr/bin/env python3
"""
Stillwater Dragon Tip Hooks + Usage Tracker — Test Suite
Version: 1.0.0 | Target: 40+ tests | Phase 2.5

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_tip_hooks.py -v --tb=short
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the package is importable
CLI_SRC = Path(__file__).resolve().parent.parent / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ===========================================================================
# Group 1: TipConfig validation
# ===========================================================================


class TestTipConfig:
    """TipConfig frozen dataclass validation."""

    def test_create_default(self):
        from stillwater.tip_hooks import TipConfig
        c = TipConfig(tip_pct=5)
        assert c.tip_pct == 5
        assert c.oss_project == "paudio"
        assert c.enabled is True

    def test_create_custom_project(self):
        from stillwater.tip_hooks import TipConfig
        c = TipConfig(tip_pct=10, oss_project="my-project")
        assert c.oss_project == "my-project"

    def test_create_disabled(self):
        from stillwater.tip_hooks import TipConfig
        c = TipConfig(tip_pct=5, enabled=False)
        assert c.enabled is False

    def test_min_tip_pct_valid(self):
        from stillwater.tip_hooks import TipConfig
        c = TipConfig(tip_pct=2)
        assert c.tip_pct == 2

    def test_max_tip_pct_valid(self):
        from stillwater.tip_hooks import TipConfig
        c = TipConfig(tip_pct=50)
        assert c.tip_pct == 50

    def test_mid_range_tip_pct_valid(self):
        from stillwater.tip_hooks import TipConfig
        for pct in [2, 5, 8, 10, 25, 49, 50]:
            c = TipConfig(tip_pct=pct)
            assert c.tip_pct == pct

    def test_tip_pct_below_min_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(ValueError, match="between 2 and 50"):
            TipConfig(tip_pct=1)

    def test_tip_pct_zero_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(ValueError, match="between 2 and 50"):
            TipConfig(tip_pct=0)

    def test_tip_pct_negative_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(ValueError, match="between 2 and 50"):
            TipConfig(tip_pct=-1)

    def test_tip_pct_above_max_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(ValueError, match="between 2 and 50"):
            TipConfig(tip_pct=51)

    def test_tip_pct_bool_rejected(self):
        """bool is a subclass of int — must be explicitly rejected."""
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(TypeError):
            TipConfig(tip_pct=True)

    def test_tip_pct_float_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(TypeError):
            TipConfig(tip_pct=5.0)  # type: ignore

    def test_tip_pct_string_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(TypeError):
            TipConfig(tip_pct="5")  # type: ignore

    def test_config_is_frozen(self):
        """TipConfig must be immutable."""
        from stillwater.tip_hooks import TipConfig
        from dataclasses import FrozenInstanceError
        c = TipConfig(tip_pct=5)
        with pytest.raises(FrozenInstanceError):
            c.tip_pct = 10  # type: ignore

    def test_empty_oss_project_rejected(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(ValueError):
            TipConfig(tip_pct=5, oss_project="")


# ===========================================================================
# Group 2: SessionTipAccumulator — tip calculation
# ===========================================================================


class TestSessionTipAccumulatorCalculation:
    """tip_for_call math — exact int arithmetic, no float drift."""

    def test_tip_for_call_claude_sonnet(self):
        """1000 input + 500 output claude-sonnet, tip_pct=5."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.providers.pricing import estimate_cost

        config = TipConfig(tip_pct=5)
        acc = SessionTipAccumulator(config=config)

        # Base cost for reference
        cost = estimate_cost(1000, 500, "claude-sonnet-4-20250514")
        # input: (1000 * 30000) // 1M = 30
        # output: (500 * 150000) // 1M = 75
        # total: 105 hundredths of cent
        assert cost == 105

        tip = acc.tip_for_call("claude-sonnet-4-20250514", 1000, 500)
        # tip = 105 * 5 / 100 = 5.25 -> rounded = 5
        assert isinstance(tip, int)
        assert tip == 5

    def test_tip_for_call_gpt4o_mini(self):
        """gpt-4o-mini with tip_pct=10."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.providers.pricing import estimate_cost

        config = TipConfig(tip_pct=10)
        acc = SessionTipAccumulator(config=config)

        cost = estimate_cost(10_000, 2_000, "gpt-4o-mini")
        tip = acc.tip_for_call("gpt-4o-mini", 10_000, 2_000)
        # tip = cost * 10 / 100
        expected = round(cost * 10 / 100)  # approximate check
        assert tip == (cost * 10 + 50) // 100 or abs(tip - expected) <= 1

    def test_tip_for_call_zero_tokens(self):
        """Zero tokens = zero cost = zero tip."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=5)
        acc = SessionTipAccumulator(config=config)
        tip = acc.tip_for_call("claude-sonnet-4-20250514", 0, 0)
        assert tip == 0

    def test_tip_for_call_unknown_model(self):
        """Unknown model has zero pricing, so zero tip."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=50)
        acc = SessionTipAccumulator(config=config)
        tip = acc.tip_for_call("unknown-model-xyz-999", 100_000, 50_000)
        assert tip == 0

    def test_tip_for_call_disabled(self):
        """When disabled, tip_for_call returns 0 without recording."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=5, enabled=False)
        acc = SessionTipAccumulator(config=config)
        tip = acc.tip_for_call("claude-sonnet-4-20250514", 1000, 500)
        assert tip == 0
        assert acc.get_session_total() == 0
        assert acc.get_call_count() == 0

    def test_tip_for_call_is_always_int(self):
        """Return value must always be int, never float."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=3)
        acc = SessionTipAccumulator(config=config)
        for tokens in [1, 100, 1000, 1_000_000]:
            tip = acc.tip_for_call("claude-sonnet-4-20250514", tokens, tokens // 2)
            assert isinstance(tip, int), f"Got {type(tip)} for {tokens} tokens"

    def test_tip_for_call_with_explicit_cost(self):
        """Explicit cost_hundredths overrides model lookup."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=10)
        acc = SessionTipAccumulator(config=config)
        # explicit cost = 1000 hundredths; tip = 1000 * 10 / 100 = 100
        tip = acc.tip_for_call("any-model", 0, 0, cost_hundredths=1000)
        assert tip == 100

    def test_tip_for_call_large_tokens(self):
        """1M tokens, claude-opus, 2% tip — exact int arithmetic."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.providers.pricing import estimate_cost

        config = TipConfig(tip_pct=2)
        acc = SessionTipAccumulator(config=config)

        cost = estimate_cost(1_000_000, 0, "claude-opus-4-20250514")
        # 1M input at 1500_00 per 1M = 150000 hundredths
        assert cost == 150_000

        tip = acc.tip_for_call("claude-opus-4-20250514", 1_000_000, 0)
        # tip = 150000 * 2 / 100 = 3000
        assert tip == 3000


# ===========================================================================
# Group 3: SessionTipAccumulator — session totals and reset
# ===========================================================================


class TestSessionTipAccumulatorSession:
    """Session total accumulation and reset."""

    def test_get_session_total_empty(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        assert acc.get_session_total() == 0

    def test_get_session_total_after_calls(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=10)
        acc = SessionTipAccumulator(config=config)
        # explicit cost_hundredths for determinism
        acc.tip_for_call("m", 0, 0, cost_hundredths=1000)  # 100
        acc.tip_for_call("m", 0, 0, cost_hundredths=2000)  # 200
        assert acc.get_session_total() == 300

    def test_call_count_increments(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        assert acc.get_call_count() == 0
        acc.tip_for_call("m", 0, 0, cost_hundredths=100)
        acc.tip_for_call("m", 0, 0, cost_hundredths=100)
        assert acc.get_call_count() == 2

    def test_reset_clears_session(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        acc.tip_for_call("m", 0, 0, cost_hundredths=1000)
        acc.tip_for_call("m", 0, 0, cost_hundredths=1000)
        assert acc.get_session_total() > 0

        acc.reset()
        assert acc.get_session_total() == 0
        assert acc.get_call_count() == 0

    def test_reset_preserves_config(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=8, oss_project="test-project")
        acc = SessionTipAccumulator(config=config)
        acc.reset()
        assert acc._config.tip_pct == 8
        assert acc._config.oss_project == "test-project"

    def test_recipe_hit_tracked(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        acc.tip_for_call("m", 100, 50, recipe_hit=True, cost_hundredths=100)

        savings = acc.get_session_savings()
        assert savings["recipe_hits"] == 1
        assert savings["tokens_saved"] == 150  # 100 + 50
        assert savings["cost_saved_hundredths"] == 100

    def test_get_session_savings_empty(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        savings = acc.get_session_savings()
        assert savings["recipe_hits"] == 0
        assert savings["tokens_saved"] == 0
        assert savings["cost_saved_hundredths"] == 0


# ===========================================================================
# Group 4: tip_callback integration
# ===========================================================================


class TestTipCallback:
    """tip_callback method: extract fields from call_result dict."""

    def test_tip_callback_records_call(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=10)
        acc = SessionTipAccumulator(config=config)

        call_result = {
            "model": "gpt-4o-mini",
            "input_tokens": 100,
            "output_tokens": 50,
            "cost_hundredths_cent": 0,
            "text": "hello",
        }
        acc.tip_callback(call_result)
        assert acc.get_call_count() == 1

    def test_tip_callback_uses_cost_hundredths_cent(self):
        """If cost_hundredths_cent is present in result, uses it."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=10)
        acc = SessionTipAccumulator(config=config)

        call_result = {
            "model": "any-model",
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_hundredths_cent": 500,  # explicit cost
        }
        acc.tip_callback(call_result)
        # tip = 500 * 10 / 100 = 50
        assert acc.get_session_total() == 50

    def test_tip_callback_ignores_non_dict(self):
        """Non-dict call_result should be silently ignored."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        acc.tip_callback("not a dict")  # type: ignore
        acc.tip_callback(None)  # type: ignore
        acc.tip_callback(42)  # type: ignore
        assert acc.get_call_count() == 0

    def test_tip_callback_handles_missing_fields(self):
        """Missing fields should default gracefully, not raise."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        acc.tip_callback({})  # empty dict
        assert acc.get_call_count() == 1  # call still recorded

    def test_tip_callback_handles_bad_token_types(self):
        """Non-int tokens should default to 0."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        acc.tip_callback({
            "model": "m",
            "input_tokens": "not-an-int",  # bad type
            "output_tokens": None,          # bad type
        })
        # Should not raise; tokens default to 0
        assert acc.get_call_count() == 1


# ===========================================================================
# Group 5: get_tip_summary
# ===========================================================================


class TestGetTipSummary:
    """get_tip_summary returns correct dict structure."""

    def test_summary_all_fields_present(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator, get_tip_summary

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        summary = get_tip_summary(acc)

        required_keys = {
            "total_cost_hundredths",
            "total_tip_hundredths",
            "tip_pct",
            "oss_project",
            "call_count",
            "savings",
        }
        assert required_keys == set(summary.keys())

    def test_summary_values_after_calls(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator, get_tip_summary

        acc = SessionTipAccumulator(TipConfig(tip_pct=10, oss_project="myproject"))
        acc.tip_for_call("m", 0, 0, cost_hundredths=1000)  # tip=100
        acc.tip_for_call("m", 0, 0, cost_hundredths=2000)  # tip=200

        summary = get_tip_summary(acc)
        assert summary["total_tip_hundredths"] == 300
        assert summary["tip_pct"] == 10
        assert summary["oss_project"] == "myproject"
        assert summary["call_count"] == 2

    def test_summary_total_cost_reverse_computed(self):
        """total_cost_hundredths is reverse-computed from tip amount."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator, get_tip_summary

        config = TipConfig(tip_pct=10)
        acc = SessionTipAccumulator(config=config)
        # cost=1000, tip=100
        acc.tip_for_call("m", 0, 0, cost_hundredths=1000)
        summary = get_tip_summary(acc)
        # reverse: 100 * 100 / 10 = 1000
        assert summary["total_cost_hundredths"] == 1000

    def test_summary_empty_session(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator, get_tip_summary

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        summary = get_tip_summary(acc)
        assert summary["total_tip_hundredths"] == 0
        assert summary["call_count"] == 0
        assert isinstance(summary["savings"], dict)

    def test_summary_savings_key_present(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator, get_tip_summary

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        summary = get_tip_summary(acc)
        savings = summary["savings"]
        assert "recipe_hits" in savings
        assert "tokens_saved" in savings
        assert "cost_saved_hundredths" in savings


# ===========================================================================
# Group 6: SessionUsageTracker — record_call
# ===========================================================================


class TestSessionUsageTrackerRecord:
    """SessionUsageTracker.record_call basic behavior."""

    def test_record_call_returns_dict(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        record = tracker.record_call("gpt-4o-mini", 100, 50)
        assert isinstance(record, dict)

    def test_record_call_fields(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        record = tracker.record_call("claude-sonnet-4-20250514", 1000, 500)
        assert record["model"] == "claude-sonnet-4-20250514"
        assert record["input_tokens"] == 1000
        assert record["output_tokens"] == 500
        assert record["recipe_hit"] is False
        assert "timestamp" in record
        assert "cost_hundredths" in record

    def test_record_call_cost_is_int(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        record = tracker.record_call("claude-sonnet-4-20250514", 1000, 500)
        assert isinstance(record["cost_hundredths"], int)

    def test_record_call_explicit_cost(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        record = tracker.record_call("any-model", 0, 0, cost_hundredths=999)
        assert record["cost_hundredths"] == 999

    def test_record_call_recipe_hit(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        record = tracker.record_call("m", 100, 50, recipe_hit=True)
        assert record["recipe_hit"] is True

    def test_record_call_negative_tokens_rejected(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        with pytest.raises(ValueError):
            tracker.record_call("m", -1, 50)
        with pytest.raises(ValueError):
            tracker.record_call("m", 100, -1)

    def test_record_call_non_string_model_rejected(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        with pytest.raises(TypeError):
            tracker.record_call(123, 100, 50)  # type: ignore

    def test_record_call_zero_tokens_ok(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        record = tracker.record_call("m", 0, 0)
        assert record["input_tokens"] == 0
        assert record["output_tokens"] == 0
        assert record["cost_hundredths"] == 0


# ===========================================================================
# Group 7: SessionUsageTracker — get_stats
# ===========================================================================


class TestSessionUsageTrackerStats:
    """SessionUsageTracker.get_stats aggregation."""

    def test_stats_empty(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        stats = tracker.get_stats()
        assert stats["total_calls"] == 0
        assert stats["total_cost_hundredths"] == 0
        assert stats["recipe_hits"] == 0
        assert stats["llm_calls"] == 0

    def test_stats_after_calls(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 100, 50, cost_hundredths=200)
        tracker.record_call("m", 200, 100, cost_hundredths=400)
        stats = tracker.get_stats()
        assert stats["total_calls"] == 2
        assert stats["total_input_tokens"] == 300
        assert stats["total_output_tokens"] == 150
        assert stats["total_cost_hundredths"] == 600
        assert stats["llm_calls"] == 2
        assert stats["recipe_hits"] == 0

    def test_stats_recipe_hit_rate(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 0, 0, recipe_hit=True)
        tracker.record_call("m", 0, 0, recipe_hit=True)
        tracker.record_call("m", 0, 0, recipe_hit=False)
        stats = tracker.get_stats()
        assert stats["recipe_hits"] == 2
        assert stats["llm_calls"] == 1
        # 2/3 = 66.6%
        assert "66" in stats["recipe_hit_rate"] or "67" in stats["recipe_hit_rate"]

    def test_stats_100_pct_recipe_hit_rate(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 0, 0, recipe_hit=True)
        tracker.record_call("m", 0, 0, recipe_hit=True)
        stats = tracker.get_stats()
        assert stats["recipe_hit_rate"] == "100.0%"
        assert stats["recipe_hits"] == 2
        assert stats["llm_calls"] == 0

    def test_stats_avg_cost_per_llm_call(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 0, 0, cost_hundredths=300, recipe_hit=False)
        tracker.record_call("m", 0, 0, cost_hundredths=700, recipe_hit=False)
        stats = tracker.get_stats()
        assert stats["avg_cost_hundredths"] == 500


# ===========================================================================
# Group 8: SessionUsageTracker — get_savings
# ===========================================================================


class TestSessionUsageTrackerSavings:
    """get_savings: recipe + SW5.0 savings."""

    def test_savings_empty(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        savings = tracker.get_savings()
        assert savings["recipe_hits"] == 0
        assert savings["recipe_tokens_saved"] == 0
        assert savings["sw5_calls_avoided"] == 0
        assert savings["total_cost_saved_hundredths"] == 0

    def test_recipe_savings(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 500, 200, recipe_hit=True, cost_hundredths=300)
        savings = tracker.get_savings()
        assert savings["recipe_hits"] == 1
        assert savings["recipe_tokens_saved"] == 700  # 500 + 200
        assert savings["recipe_cost_saved_hundredths"] == 300

    def test_sw5_savings_factor(self):
        """SW5.0 savings = 40% of actual LLM call tokens/cost."""
        from stillwater.usage_tracker import SessionUsageTracker, SW5_ITERATION_REDUCTION_PCT

        assert SW5_ITERATION_REDUCTION_PCT == 40  # verify constant

        tracker = SessionUsageTracker()
        # 1 LLM call with 1000 tokens total, cost=1000
        tracker.record_call("m", 600, 400, recipe_hit=False, cost_hundredths=1000)

        savings = tracker.get_savings()
        # SW5.0 calls avoided = 40% of 1 = 0 (integer division)
        assert savings["sw5_calls_avoided"] == 0
        # Tokens saved = 40% of 1000 = 400
        assert savings["sw5_tokens_saved"] == 400
        # Cost saved = 40% of 1000 = 400
        assert savings["sw5_cost_saved_hundredths"] == 400

    def test_sw5_savings_multiple_calls(self):
        """SW5.0 calls avoided = 40% of llm_call count (integer)."""
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        for _ in range(10):
            tracker.record_call("m", 100, 50, recipe_hit=False, cost_hundredths=100)

        savings = tracker.get_savings()
        assert savings["sw5_calls_avoided"] == 4  # 40% of 10

    def test_total_savings_combines_both(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 100, 50, recipe_hit=True, cost_hundredths=200)
        tracker.record_call("m", 100, 50, recipe_hit=False, cost_hundredths=200)

        savings = tracker.get_savings()
        # recipe: 200 cost saved
        # sw5: 40% of 200 = 80 cost saved
        assert savings["total_cost_saved_hundredths"] == 280

    def test_savings_all_keys_present(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        savings = tracker.get_savings()
        expected_keys = {
            "recipe_hits", "recipe_tokens_saved", "recipe_cost_saved_hundredths",
            "sw5_calls_avoided", "sw5_tokens_saved", "sw5_cost_saved_hundredths",
            "total_tokens_saved", "total_cost_saved_hundredths",
        }
        assert expected_keys == set(savings.keys())


# ===========================================================================
# Group 9: SessionUsageTracker — export and reset
# ===========================================================================


class TestSessionUsageTrackerExport:
    """export_calls and reset."""

    def test_export_calls_empty(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        calls = tracker.export_calls()
        assert calls == []

    def test_export_calls_returns_copies(self):
        """Modifying exported list should not affect tracker state."""
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 100, 50, cost_hundredths=100)
        calls = tracker.export_calls()
        calls.clear()  # mutate the export
        assert len(tracker.export_calls()) == 1  # original unaffected

    def test_export_calls_all_recorded(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        for i in range(5):
            tracker.record_call(f"model-{i}", i * 100, i * 50)
        calls = tracker.export_calls()
        assert len(calls) == 5
        assert calls[0]["model"] == "model-0"
        assert calls[4]["model"] == "model-4"

    def test_reset_clears_calls(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 100, 50)
        tracker.reset()
        assert tracker.export_calls() == []
        stats = tracker.get_stats()
        assert stats["total_calls"] == 0


# ===========================================================================
# Group 10: Thread safety
# ===========================================================================


class TestThreadSafety:
    """Concurrent access safety for both accumulators."""

    def test_session_tip_accumulator_thread_safe(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=5)
        acc = SessionTipAccumulator(config=config)
        errors = []

        def record_many():
            try:
                for _ in range(50):
                    acc.tip_for_call("gpt-4o-mini", 100, 50, cost_hundredths=100)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread safety errors: {errors}"
        # 10 threads * 50 calls each = 500 calls
        assert acc.get_call_count() == 500

    def test_session_usage_tracker_thread_safe(self):
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        errors = []

        def record_many():
            try:
                for _ in range(50):
                    tracker.record_call("gpt-4o-mini", 100, 50, cost_hundredths=100)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread safety errors: {errors}"
        stats = tracker.get_stats()
        assert stats["total_calls"] == 500


# ===========================================================================
# Group 11: LLMClient integration — tip_callback + usage_tracker
# ===========================================================================


def _make_offline_response_dict():
    """Build a minimal LLMResponse-like dict for testing callbacks."""
    return {
        "text": "[offline: test]",
        "model": "offline",
        "provider": "offline",
        "input_tokens": 1,
        "output_tokens": 5,
        "cost_hundredths_cent": 0,
        "latency_ms": 0,
        "request_id": "abc",
        "timestamp": "2026-01-01T00:00:00+00:00",
    }


class TestLLMClientCallbackIntegration:
    """LLMClient.complete() and .chat() fire tip_callback and usage_tracker."""

    def test_complete_fires_tip_callback_offline(self):
        """complete() with offline provider fires tip_callback."""
        from stillwater.llm_client import LLMClient
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=5)
        acc = SessionTipAccumulator(config=config)

        client = LLMClient(provider="offline")
        client.complete("hello", provider="offline", tip_callback=acc.tip_callback)

        # offline response has tokens — callback should have fired
        assert acc.get_call_count() == 1

    def test_chat_fires_tip_callback_offline(self):
        """chat() with offline provider fires tip_callback."""
        from stillwater.llm_client import LLMClient
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        config = TipConfig(tip_pct=5)
        acc = SessionTipAccumulator(config=config)

        client = LLMClient(provider="offline")
        client.chat(
            [{"role": "user", "content": "hello"}],
            provider="offline",
            tip_callback=acc.tip_callback,
        )
        assert acc.get_call_count() == 1

    def test_complete_fires_usage_tracker_offline(self):
        """complete() fires usage_tracker.usage_callback on success."""
        from stillwater.llm_client import LLMClient
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        client = LLMClient(provider="offline")
        client.complete("hello", provider="offline", usage_tracker=tracker)

        stats = tracker.get_stats()
        assert stats["total_calls"] == 1

    def test_chat_fires_usage_tracker_offline(self):
        """chat() fires usage_tracker.usage_callback on success."""
        from stillwater.llm_client import LLMClient
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        client = LLMClient(provider="offline")
        client.chat(
            [{"role": "user", "content": "test"}],
            provider="offline",
            usage_tracker=tracker,
        )
        stats = tracker.get_stats()
        assert stats["total_calls"] == 1

    def test_both_callbacks_fire_together(self):
        """Both tip_callback and usage_tracker fire in same call."""
        from stillwater.llm_client import LLMClient
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.usage_tracker import SessionUsageTracker

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tracker = SessionUsageTracker()

        client = LLMClient(provider="offline")
        client.complete(
            "hello", provider="offline",
            tip_callback=acc.tip_callback,
            usage_tracker=tracker,
        )
        assert acc.get_call_count() == 1
        assert tracker.get_stats()["total_calls"] == 1

    def test_no_callbacks_no_side_effects(self):
        """No callbacks = no state changes anywhere."""
        from stillwater.llm_client import LLMClient

        client = LLMClient(provider="offline")
        result = client.complete("hello", provider="offline")
        assert result.text.startswith("[offline:")

    def test_callback_exception_does_not_crash_call(self):
        """If tip_callback raises, the LLM call still succeeds."""
        from stillwater.llm_client import LLMClient

        def bad_callback(result):
            raise RuntimeError("callback exploded")

        client = LLMClient(provider="offline")
        # Should NOT raise even though callback raises
        result = client.complete("hello", provider="offline", tip_callback=bad_callback)
        assert result.text.startswith("[offline:")

    def test_usage_tracker_callback_exception_does_not_crash(self):
        """If usage_tracker raises inside usage_callback, call still succeeds."""
        from stillwater.llm_client import LLMClient

        class BadTracker:
            def usage_callback(self, result):
                raise RuntimeError("tracker exploded")

        client = LLMClient(provider="offline")
        result = client.complete("hello", provider="offline", usage_tracker=BadTracker())
        assert result.text.startswith("[offline:")


# ===========================================================================
# Group 12: llm_call / llm_chat convenience functions — backward compat
# ===========================================================================


class TestConvenienceFunctionBackwardCompat:
    """llm_call and llm_chat preserve backward compatibility."""

    def test_llm_call_offline_no_callbacks(self):
        from stillwater.llm_client import llm_call
        result = llm_call("test", provider="offline")
        assert result.startswith("[offline:")

    def test_llm_chat_offline_no_callbacks(self):
        from stillwater.llm_client import llm_chat
        result = llm_chat([{"role": "user", "content": "hi"}], provider="offline")
        assert result.startswith("[offline:")

    def test_llm_call_with_tip_callback(self):
        from stillwater.llm_client import llm_call
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        result = llm_call("test", provider="offline", tip_callback=acc.tip_callback)
        assert result.startswith("[offline:")
        assert acc.get_call_count() == 1

    def test_llm_chat_with_usage_tracker(self):
        from stillwater.llm_client import llm_chat
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        result = llm_chat(
            [{"role": "user", "content": "hi"}],
            provider="offline",
            usage_tracker=tracker,
        )
        assert result.startswith("[offline:")
        assert tracker.get_stats()["total_calls"] == 1


# ===========================================================================
# Group 13: Import smoke tests
# ===========================================================================


class TestImports:
    """Verify all new imports work."""

    def test_import_tip_config(self):
        from stillwater.tip_hooks import TipConfig
        assert TipConfig is not None

    def test_import_session_tip_accumulator(self):
        from stillwater.tip_hooks import SessionTipAccumulator
        assert SessionTipAccumulator is not None

    def test_import_get_tip_summary(self):
        from stillwater.tip_hooks import get_tip_summary
        assert callable(get_tip_summary)

    def test_import_session_usage_tracker(self):
        from stillwater.usage_tracker import SessionUsageTracker
        assert SessionUsageTracker is not None

    def test_import_sw5_constant(self):
        from stillwater.usage_tracker import SW5_ITERATION_REDUCTION_PCT
        assert SW5_ITERATION_REDUCTION_PCT == 40

    def test_import_tip_pct_constants(self):
        from stillwater.tip_hooks import TIP_PCT_MIN, TIP_PCT_MAX
        assert TIP_PCT_MIN == 2
        assert TIP_PCT_MAX == 50
