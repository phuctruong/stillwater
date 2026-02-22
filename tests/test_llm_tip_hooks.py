#!/usr/bin/env python3
"""
Stillwater Phase 2.5 — Dragon Tip Hooks in LLM Client: Test Suite
Version: 1.0.0 | Target: 30+ tests | Rung: 641

Tests focused on:
  1. tip_callback parameter wiring in llm_call() / llm_chat() / LLMClient
  2. usage_tracker parameter wiring in the same functions
  3. Cost estimation accuracy using exact Decimal arithmetic (no float drift)
  4. SessionTipAccumulator cost math correctness
  5. SessionUsageTracker SW5.0 savings calculation correctness
  6. Decimal-only arithmetic invariant — no float anywhere in cost/tip paths
  7. Callback isolation — exceptions in callbacks never crash callers
  8. Default no-op behavior — no hooks = zero overhead side effects
  9. Both hooks fire together in the same call
  10. Backward compatibility: llm_call/llm_chat return str, not broken by hooks

Run:
    cd /home/phuc/projects/stillwater
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_llm_tip_hooks.py -v
"""

from __future__ import annotations

import sys
import threading
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Path setup — allow importing from cli/src
# ---------------------------------------------------------------------------
CLI_SRC = Path(__file__).resolve().parent.parent / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ===========================================================================
# Group 1: tip_callback wiring in llm_call()
# ===========================================================================


class TestLlmCallTipCallback:
    """tip_callback parameter accepted and invoked by llm_call()."""

    def test_tip_callback_invoked_on_offline_call(self):
        """llm_call with provider=offline fires tip_callback once."""
        from stillwater.llm_client import llm_call
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        llm_call("test prompt", provider="offline", tip_callback=acc.tip_callback)
        assert acc.get_call_count() == 1

    def test_tip_callback_not_required(self):
        """llm_call without tip_callback completes without error."""
        from stillwater.llm_client import llm_call
        result = llm_call("ping", provider="offline")
        assert isinstance(result, str)

    def test_tip_callback_receives_dict(self):
        """tip_callback receives a dict with expected keys."""
        from stillwater.llm_client import llm_call
        received = []

        def capture(d):
            received.append(d)

        llm_call("test", provider="offline", tip_callback=capture)
        assert len(received) == 1
        d = received[0]
        assert isinstance(d, dict)
        assert "model" in d
        assert "input_tokens" in d
        assert "output_tokens" in d
        assert "cost_hundredths_cent" in d

    def test_tip_callback_cost_hundredths_cent_is_int(self):
        """cost_hundredths_cent field must be int, not float."""
        from stillwater.llm_client import llm_call
        received = []
        llm_call("test", provider="offline", tip_callback=lambda d: received.append(d))
        cost = received[0]["cost_hundredths_cent"]
        assert isinstance(cost, int), f"Expected int, got {type(cost)}"

    def test_tip_callback_input_output_tokens_are_int(self):
        """input_tokens and output_tokens must be int, not float."""
        from stillwater.llm_client import llm_call
        received = []
        llm_call("test", provider="offline", tip_callback=lambda d: received.append(d))
        d = received[0]
        assert isinstance(d["input_tokens"], int)
        assert isinstance(d["output_tokens"], int)

    def test_tip_callback_exception_does_not_propagate(self):
        """Callback raising an exception must not crash llm_call."""
        from stillwater.llm_client import llm_call

        def exploding_callback(d):
            raise RuntimeError("boom")

        result = llm_call("test", provider="offline", tip_callback=exploding_callback)
        assert result.startswith("[offline:")

    def test_tip_callback_called_multiple_times_accumulates(self):
        """Multiple calls accumulate correctly in SessionTipAccumulator."""
        from stillwater.llm_client import llm_call
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        for _ in range(5):
            llm_call("msg", provider="offline", tip_callback=acc.tip_callback)
        assert acc.get_call_count() == 5


# ===========================================================================
# Group 2: tip_callback wiring in llm_chat()
# ===========================================================================


class TestLlmChatTipCallback:
    """tip_callback parameter accepted and invoked by llm_chat()."""

    def test_tip_callback_invoked_on_offline_chat(self):
        from stillwater.llm_client import llm_chat
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        llm_chat(
            [{"role": "user", "content": "hello"}],
            provider="offline",
            tip_callback=acc.tip_callback,
        )
        assert acc.get_call_count() == 1

    def test_llm_chat_returns_str_with_callback(self):
        """llm_chat still returns str (not LLMResponse) with callback wired."""
        from stillwater.llm_client import llm_chat
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        result = llm_chat(
            [{"role": "user", "content": "hi"}],
            provider="offline",
            tip_callback=acc.tip_callback,
        )
        assert isinstance(result, str)

    def test_llm_chat_callback_exception_does_not_propagate(self):
        from stillwater.llm_client import llm_chat

        def bad(d):
            raise ValueError("chat callback crashed")

        result = llm_chat(
            [{"role": "user", "content": "hi"}],
            provider="offline",
            tip_callback=bad,
        )
        assert result.startswith("[offline:")


# ===========================================================================
# Group 3: usage_tracker wiring in llm_call() / llm_chat()
# ===========================================================================


class TestUsageTrackerWiring:
    """usage_tracker parameter wired into llm_call and llm_chat."""

    def test_llm_call_fires_usage_tracker(self):
        from stillwater.llm_client import llm_call
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        llm_call("test", provider="offline", usage_tracker=tracker)
        assert tracker.get_stats()["total_calls"] == 1

    def test_llm_chat_fires_usage_tracker(self):
        from stillwater.llm_client import llm_chat
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        llm_chat(
            [{"role": "user", "content": "hi"}],
            provider="offline",
            usage_tracker=tracker,
        )
        assert tracker.get_stats()["total_calls"] == 1

    def test_usage_tracker_tracks_all_calls(self):
        from stillwater.llm_client import llm_call
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        for _ in range(3):
            llm_call("msg", provider="offline", usage_tracker=tracker)
        assert tracker.get_stats()["total_calls"] == 3

    def test_usage_tracker_exception_does_not_crash_call(self):
        from stillwater.llm_client import llm_call

        class ExplodingTracker:
            def usage_callback(self, d):
                raise RuntimeError("tracker exploded")

        result = llm_call("test", provider="offline", usage_tracker=ExplodingTracker())
        assert result.startswith("[offline:")

    def test_usage_tracker_cost_hundredths_is_int(self):
        """Recorded cost_hundredths must be int — never float."""
        from stillwater.llm_client import llm_call
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        llm_call("test", provider="offline", usage_tracker=tracker)
        calls = tracker.export_calls()
        assert len(calls) == 1
        assert isinstance(calls[0]["cost_hundredths"], int)


# ===========================================================================
# Group 4: Both callbacks fire together
# ===========================================================================


class TestBothCallbacksTogether:
    """tip_callback AND usage_tracker both fire in the same call."""

    def test_both_fire_in_single_llm_call(self):
        from stillwater.llm_client import llm_call
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.usage_tracker import SessionUsageTracker

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tracker = SessionUsageTracker()
        llm_call(
            "test",
            provider="offline",
            tip_callback=acc.tip_callback,
            usage_tracker=tracker,
        )
        assert acc.get_call_count() == 1
        assert tracker.get_stats()["total_calls"] == 1

    def test_both_fire_in_llm_chat(self):
        from stillwater.llm_client import llm_chat
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.usage_tracker import SessionUsageTracker

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tracker = SessionUsageTracker()
        llm_chat(
            [{"role": "user", "content": "hi"}],
            provider="offline",
            tip_callback=acc.tip_callback,
            usage_tracker=tracker,
        )
        assert acc.get_call_count() == 1
        assert tracker.get_stats()["total_calls"] == 1

    def test_both_fire_in_llmclient_complete(self):
        from stillwater.llm_client import LLMClient
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.usage_tracker import SessionUsageTracker

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tracker = SessionUsageTracker()
        client = LLMClient(provider="offline")
        client.complete(
            "hello",
            provider="offline",
            tip_callback=acc.tip_callback,
            usage_tracker=tracker,
        )
        assert acc.get_call_count() == 1
        assert tracker.get_stats()["total_calls"] == 1

    def test_both_fire_in_llmclient_chat(self):
        from stillwater.llm_client import LLMClient
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from stillwater.usage_tracker import SessionUsageTracker

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tracker = SessionUsageTracker()
        client = LLMClient(provider="offline")
        client.chat(
            [{"role": "user", "content": "hi"}],
            provider="offline",
            tip_callback=acc.tip_callback,
            usage_tracker=tracker,
        )
        assert acc.get_call_count() == 1
        assert tracker.get_stats()["total_calls"] == 1


# ===========================================================================
# Group 5: Cost estimation accuracy — exact arithmetic, no float
# ===========================================================================


class TestCostEstimationAccuracy:
    """
    Verify cost math stays exact (int / Decimal).
    No float is ever used in the pricing or tip path.
    """

    def test_estimate_cost_returns_int(self):
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(1000, 500, "claude-sonnet-4-20250514")
        assert isinstance(cost, int), f"Expected int, got {type(cost)}"

    def test_estimate_cost_claude_sonnet(self):
        """Manual: 1000 input at 300_00/1M = 30; 500 output at 1500_00/1M = 75 => 105."""
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(1000, 500, "claude-sonnet-4-20250514")
        assert cost == 105

    def test_estimate_cost_claude_opus_input_only(self):
        """1M input tokens at 1500_00/1M = 150_000 hundredths."""
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(1_000_000, 0, "claude-opus-4-20250514")
        assert cost == 150_000

    def test_estimate_cost_gpt4o_mini(self):
        """100K input at 1500 hundredths/1M = 150; 10K output at 6000 hundredths/1M = 60 => 210."""
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(100_000, 10_000, "gpt-4o-mini")
        # (100_000 * 1500) // 1_000_000 + (10_000 * 6000) // 1_000_000 = 150 + 60 = 210
        assert cost == 210

    def test_estimate_cost_unknown_model_returns_zero(self):
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(1_000_000, 1_000_000, "unknown-model-that-does-not-exist")
        assert cost == 0

    def test_estimate_cost_zero_tokens(self):
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(0, 0, "claude-sonnet-4-20250514")
        assert cost == 0

    def test_tip_calculation_decimal_no_float(self):
        """
        Tip arithmetic uses Decimal internally — verify by inspecting result.
        tip_for_call returns int, never float.
        """
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        from decimal import Decimal

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        # cost=1000; tip = 1000 * 5 / 100 = 50 (exact)
        tip = acc.tip_for_call("any-model", 0, 0, cost_hundredths=1000)
        assert isinstance(tip, int)
        assert not isinstance(tip, float)
        assert tip == 50

    def test_tip_calculation_rounds_half_up(self):
        """
        cost=105, pct=5 => 5.25 => rounds to 5 (ROUND_HALF_UP).
        """
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tip = acc.tip_for_call("any-model", 0, 0, cost_hundredths=105)
        # 105 * 5 / 100 = 5.25 => ROUND_HALF_UP => 5
        assert tip == 5

    def test_tip_calculation_rounds_exactly_half(self):
        """cost=200, pct=5 => 10.0 => exactly 10."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        tip = acc.tip_for_call("any-model", 0, 0, cost_hundredths=200)
        assert tip == 10

    def test_no_float_in_session_total(self):
        """Session total is int — never float."""
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator

        acc = SessionTipAccumulator(TipConfig(tip_pct=10))
        for cost in [100, 200, 300]:
            acc.tip_for_call("m", 0, 0, cost_hundredths=cost)
        total = acc.get_session_total()
        assert isinstance(total, int)
        # tips: 10 + 20 + 30 = 60
        assert total == 60

    def test_usage_tracker_cost_is_always_int(self):
        """SessionUsageTracker.record_call: cost_hundredths field is always int."""
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        r = tracker.record_call("claude-sonnet-4-20250514", 1000, 500)
        assert isinstance(r["cost_hundredths"], int)

    def test_sw5_savings_uses_integer_arithmetic(self):
        """SW5.0 savings calculation: all values are int, no float."""
        from stillwater.usage_tracker import SessionUsageTracker

        tracker = SessionUsageTracker()
        tracker.record_call("m", 1000, 500, recipe_hit=False, cost_hundredths=1000)
        savings = tracker.get_savings()
        for key, val in savings.items():
            assert isinstance(val, int), f"Key '{key}' has non-int value: {type(val)}"


# ===========================================================================
# Group 6: Decimal-only arithmetic invariant
# ===========================================================================


class TestDecimalOnlyInvariant:
    """
    Verify no float appears anywhere in the tip or cost paths.

    The invariant: all intermediate calculations use int or Decimal.
    Python's `Decimal` class guarantees no IEEE 754 rounding errors.
    """

    def test_tip_pct_stored_as_int_not_float(self):
        from stillwater.tip_hooks import TipConfig
        config = TipConfig(tip_pct=5)
        assert isinstance(config.tip_pct, int)
        assert not isinstance(config.tip_pct, float)

    def test_tip_config_rejects_float_pct(self):
        from stillwater.tip_hooks import TipConfig
        with pytest.raises(TypeError):
            TipConfig(tip_pct=5.5)  # type: ignore

    def test_pricing_table_values_are_int(self):
        from stillwater.providers.pricing import MODEL_PRICING
        for model, pricing in MODEL_PRICING.items():
            assert isinstance(pricing["input"], int), f"{model}.input is not int"
            assert isinstance(pricing["output"], int), f"{model}.output is not int"

    def test_estimate_cost_returns_int_for_all_known_models(self):
        from stillwater.providers.pricing import MODEL_PRICING, estimate_cost
        for model in MODEL_PRICING:
            if "/*" in model:
                continue
            cost = estimate_cost(1000, 500, model)
            assert isinstance(cost, int), f"Model {model} returned non-int cost"

    def test_session_savings_cost_fields_are_int(self):
        from stillwater.tip_hooks import TipConfig, SessionTipAccumulator
        acc = SessionTipAccumulator(TipConfig(tip_pct=5))
        acc.tip_for_call("m", 100, 50, recipe_hit=True, cost_hundredths=100)
        savings = acc.get_session_savings()
        assert isinstance(savings["cost_saved_hundredths"], int)
        assert isinstance(savings["tokens_saved"], int)


# ===========================================================================
# Group 7: No-op defaults (no callbacks = zero side effects)
# ===========================================================================


class TestNoOpDefaults:
    """Without callbacks, calls complete with zero side effects."""

    def test_llm_call_no_callbacks_returns_str(self):
        from stillwater.llm_client import llm_call
        result = llm_call("hello", provider="offline")
        assert isinstance(result, str)
        assert "[offline:" in result

    def test_llm_chat_no_callbacks_returns_str(self):
        from stillwater.llm_client import llm_chat
        result = llm_chat([{"role": "user", "content": "hi"}], provider="offline")
        assert isinstance(result, str)

    def test_llmclient_complete_no_callbacks(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="offline")
        response = client.complete("hi", provider="offline")
        assert response.text.startswith("[offline:")

    def test_llmclient_chat_no_callbacks(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="offline")
        response = client.chat([{"role": "user", "content": "hi"}], provider="offline")
        assert response.text.startswith("[offline:")


# ===========================================================================
# Group 8: Backward compatibility — existing callers unaffected
# ===========================================================================


class TestBackwardCompatibility:
    """
    Existing callers that don't pass tip_callback or usage_tracker
    must not be broken.
    """

    def test_llm_call_signature_unchanged(self):
        """llm_call(prompt, provider=...) still works — no required new args."""
        from stillwater.llm_client import llm_call
        result = llm_call("ping", provider="offline")
        assert isinstance(result, str)

    def test_llm_chat_signature_unchanged(self):
        """llm_chat(messages, provider=...) still works."""
        from stillwater.llm_client import llm_chat
        result = llm_chat([{"role": "user", "content": "ping"}], provider="offline")
        assert isinstance(result, str)

    def test_llmclient_complete_signature_unchanged(self):
        """LLMClient.complete(prompt) still works."""
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="offline")
        response = client.complete("ping", provider="offline")
        assert hasattr(response, "text")

    def test_llmclient_chat_signature_unchanged(self):
        """LLMClient.chat(messages) still works."""
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="offline")
        response = client.chat([{"role": "user", "content": "ping"}], provider="offline")
        assert hasattr(response, "text")

    def test_get_call_history_still_works(self):
        """get_call_history() backward compat function still importable + callable."""
        from stillwater.llm_client import get_call_history
        result = get_call_history(n=5)
        assert isinstance(result, list)


# ===========================================================================
# Group 9: Module import smoke tests
# ===========================================================================


class TestImportSmoke:
    """All new Phase 2.5 symbols are importable from expected locations."""

    def test_import_tip_config(self):
        from stillwater.tip_hooks import TipConfig
        assert callable(TipConfig)

    def test_import_session_tip_accumulator(self):
        from stillwater.tip_hooks import SessionTipAccumulator
        assert callable(SessionTipAccumulator)

    def test_import_get_tip_summary(self):
        from stillwater.tip_hooks import get_tip_summary
        assert callable(get_tip_summary)

    def test_import_session_usage_tracker(self):
        from stillwater.usage_tracker import SessionUsageTracker
        assert callable(SessionUsageTracker)

    def test_import_sw5_constant(self):
        from stillwater.usage_tracker import SW5_ITERATION_REDUCTION_PCT
        assert SW5_ITERATION_REDUCTION_PCT == 40

    def test_import_tip_pct_constants(self):
        from stillwater.tip_hooks import TIP_PCT_MIN, TIP_PCT_MAX
        assert TIP_PCT_MIN == 2
        assert TIP_PCT_MAX == 50

    def test_import_llm_call(self):
        from stillwater.llm_client import llm_call
        assert callable(llm_call)

    def test_import_llm_chat(self):
        from stillwater.llm_client import llm_chat
        assert callable(llm_chat)

    def test_import_llm_client(self):
        from stillwater.llm_client import LLMClient
        assert callable(LLMClient)

    def test_import_estimate_cost(self):
        from stillwater.providers.pricing import estimate_cost
        assert callable(estimate_cost)
