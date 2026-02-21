"""
Stillwater Session Usage Tracker
Auth: 65537 | Status: STABLE | Version: 1.0.0

Session-level tracking of all LLM calls. Records token usage, cost, recipe
cache hits, and SW5.0 iteration savings. Thread-safe.

Design rules:
  - ALL cost arithmetic uses Python int (hundredths of a cent) — NEVER float
  - Thread-safe via threading.Lock
  - No external dependencies beyond stdlib
  - Recipe hit tracking: recipe_hit=True counts tokens as "saved"
  - SW5.0 savings: 40% iteration reduction factor for non-recipe calls

Usage:
    from stillwater.usage_tracker import SessionUsageTracker

    tracker = SessionUsageTracker()

    # Record a call
    record = tracker.record_call(
        model="claude-sonnet-4-20250514",
        input_tokens=1000,
        output_tokens=500,
    )

    # Or attach to llm_call:
    from stillwater.llm_client import llm_call
    llm_call("hello", usage_tracker=tracker)

    stats = tracker.get_stats()
    savings = tracker.get_savings()
    calls = tracker.export_calls()
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Optional

from .providers.pricing import estimate_cost as _estimate_cost

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# SW5.0 Iteration Reduction Factor: 40% of non-recipe LLM calls are
# avoided due to structured SW5.0 discipline (skill packs, verification ladders,
# red-green gates). This is the basis for SW5.0 savings calculation.
SW5_ITERATION_REDUCTION_PCT: int = 40  # integer percent


# ---------------------------------------------------------------------------
# SessionUsageTracker
# ---------------------------------------------------------------------------


class SessionUsageTracker:
    """
    Tracks all LLM calls in the current session.

    Provides:
      - Per-call recording with cost computation
      - Aggregate stats (total calls, tokens, cost)
      - Recipe hit tracking (tokens/cost saved via cache)
      - SW5.0 savings calculation (40% iteration reduction)
      - Thread-safe for concurrent use

    All monetary values in hundredths of a cent (int). Never float.

    Example:
        tracker = SessionUsageTracker()
        tracker.record_call("gpt-4o-mini", input_tokens=500, output_tokens=200)
        stats = tracker.get_stats()
        # stats["total_cost_hundredths"] -> int (exact, no float)
    """

    def __init__(self) -> None:
        self._calls: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Core recording
    # ------------------------------------------------------------------

    def record_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        recipe_hit: bool = False,
        cost_hundredths: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Record one LLM call (or recipe cache hit).

        Args:
            model:          Model name (used for cost lookup if cost not provided).
            input_tokens:   Number of input tokens used.
            output_tokens:  Number of output tokens produced.
            recipe_hit:     If True, this was a recipe cache hit — tokens were
                           NOT actually sent to the LLM. The cost is recorded
                           as "saved" rather than "spent".
            cost_hundredths: Override cost in hundredths of a cent. If None,
                            auto-computed from MODEL_PRICING.

        Returns:
            Dict record with all tracked fields.

        Raises:
            ValueError: If input_tokens or output_tokens is negative.
            TypeError:  If model is not a string.
        """
        if not isinstance(model, str):
            raise TypeError(f"model must be str, got {type(model).__name__}")
        if not isinstance(input_tokens, int) or isinstance(input_tokens, bool):
            raise TypeError(f"input_tokens must be int, got {type(input_tokens).__name__}")
        if not isinstance(output_tokens, int) or isinstance(output_tokens, bool):
            raise TypeError(f"output_tokens must be int, got {type(output_tokens).__name__}")
        if input_tokens < 0:
            raise ValueError(f"input_tokens must be >= 0, got {input_tokens}")
        if output_tokens < 0:
            raise ValueError(f"output_tokens must be >= 0, got {output_tokens}")

        # Compute cost if not provided
        if cost_hundredths is None:
            cost_hundredths = _estimate_cost(input_tokens, output_tokens, model)

        ts = datetime.now(timezone.utc).isoformat()

        record: dict[str, Any] = {
            "timestamp": ts,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_hundredths": cost_hundredths,
            "recipe_hit": recipe_hit,
        }

        with self._lock:
            self._calls.append(record)

        return record

    # ------------------------------------------------------------------
    # Aggregate stats
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """
        Return aggregate statistics for this session.

        Returns dict with:
            total_calls:             int — all recorded calls (LLM + recipe)
            total_input_tokens:      int — total input tokens (all calls)
            total_output_tokens:     int — total output tokens (all calls)
            total_cost_hundredths:   int — total cost in hundredths of a cent
            recipe_hits:             int — number of recipe cache hits
            llm_calls:               int — actual LLM calls (not recipe hits)
            recipe_hit_rate:         str — e.g. "70.0%" (formatted string)
            avg_cost_hundredths:     int — average cost per LLM call
        """
        with self._lock:
            calls = list(self._calls)

        if not calls:
            return {
                "total_calls": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost_hundredths": 0,
                "recipe_hits": 0,
                "llm_calls": 0,
                "recipe_hit_rate": "0.0%",
                "avg_cost_hundredths": 0,
            }

        total_calls = len(calls)
        total_input = sum(c["input_tokens"] for c in calls)
        total_output = sum(c["output_tokens"] for c in calls)
        total_cost = sum(c["cost_hundredths"] for c in calls)
        recipe_hits = sum(1 for c in calls if c["recipe_hit"])
        llm_calls = total_calls - recipe_hits

        # Recipe hit rate as formatted string (integer arithmetic for percentage)
        if total_calls > 0:
            # Multiply by 1000 for one decimal place, then format
            hit_rate_tenths = (recipe_hits * 1000) // total_calls
            hit_rate_str = f"{hit_rate_tenths // 10}.{hit_rate_tenths % 10}%"
        else:
            hit_rate_str = "0.0%"

        avg_cost = total_cost // llm_calls if llm_calls > 0 else 0

        return {
            "total_calls": total_calls,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost_hundredths": total_cost,
            "recipe_hits": recipe_hits,
            "llm_calls": llm_calls,
            "recipe_hit_rate": hit_rate_str,
            "avg_cost_hundredths": avg_cost,
        }

    # ------------------------------------------------------------------
    # Savings calculation
    # ------------------------------------------------------------------

    def get_savings(self) -> dict[str, Any]:
        """
        Return savings report combining recipe savings + SW5.0 savings.

        Recipe savings: tokens/cost avoided via cache hits.
        SW5.0 savings: 40% iteration reduction on actual LLM calls
                       (from structured skill discipline: prime-coder,
                        verification ladders, red-green gates).

        Returns dict with:
            recipe_hits:                    int — number of recipe hits
            recipe_tokens_saved:            int — tokens avoided by recipe replay
            recipe_cost_saved_hundredths:   int — cost saved by recipe replay
            sw5_calls_avoided:              int — estimated calls avoided (40% of llm_calls)
            sw5_tokens_saved:               int — estimated tokens avoided by SW5.0
            sw5_cost_saved_hundredths:      int — estimated cost saved by SW5.0
            total_tokens_saved:             int — recipe + SW5.0 tokens saved
            total_cost_saved_hundredths:    int — recipe + SW5.0 cost saved
        """
        with self._lock:
            calls = list(self._calls)

        recipe_hits = [c for c in calls if c["recipe_hit"]]
        llm_calls = [c for c in calls if not c["recipe_hit"]]

        # Recipe savings
        recipe_tokens_saved = sum(c["input_tokens"] + c["output_tokens"] for c in recipe_hits)
        recipe_cost_saved = sum(c["cost_hundredths"] for c in recipe_hits)

        # SW5.0 savings: 40% of actual LLM call tokens/cost
        # sw5_calls_avoided = 40% of llm_calls (integer)
        sw5_calls_avoided = (len(llm_calls) * SW5_ITERATION_REDUCTION_PCT) // 100
        sw5_tokens_saved = sum(
            (c["input_tokens"] + c["output_tokens"]) * SW5_ITERATION_REDUCTION_PCT // 100
            for c in llm_calls
        )
        sw5_cost_saved = sum(
            c["cost_hundredths"] * SW5_ITERATION_REDUCTION_PCT // 100
            for c in llm_calls
        )

        return {
            "recipe_hits": len(recipe_hits),
            "recipe_tokens_saved": recipe_tokens_saved,
            "recipe_cost_saved_hundredths": recipe_cost_saved,
            "sw5_calls_avoided": sw5_calls_avoided,
            "sw5_tokens_saved": sw5_tokens_saved,
            "sw5_cost_saved_hundredths": sw5_cost_saved,
            "total_tokens_saved": recipe_tokens_saved + sw5_tokens_saved,
            "total_cost_saved_hundredths": recipe_cost_saved + sw5_cost_saved,
        }

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_calls(self) -> list[dict[str, Any]]:
        """
        Return a copy of all recorded calls.

        Returns:
            List of dicts, each with: timestamp, model, input_tokens,
            output_tokens, cost_hundredths, recipe_hit.
        """
        with self._lock:
            return [dict(c) for c in self._calls]

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Clear all recorded calls. Does not affect configuration."""
        with self._lock:
            self._calls.clear()

    # ------------------------------------------------------------------
    # Callback interface (for llm_call integration)
    # ------------------------------------------------------------------

    def usage_callback(self, call_result: dict) -> None:
        """
        Callback suitable for passing to llm_call() / llm_chat().

        Extracts model, input_tokens, output_tokens from call_result dict
        and records the call via record_call().

        Args:
            call_result: Dict with keys: model, input_tokens, output_tokens.
                        Optional keys: cost_hundredths_cent, recipe_hit.
        """
        if not isinstance(call_result, dict):
            return

        model = str(call_result.get("model", ""))
        input_tokens = call_result.get("input_tokens", 0)
        output_tokens = call_result.get("output_tokens", 0)
        recipe_hit = call_result.get("recipe_hit", False)
        cost_hundredths = call_result.get("cost_hundredths_cent")

        # Sanitize: ensure non-negative ints
        if not isinstance(input_tokens, int) or isinstance(input_tokens, bool):
            input_tokens = 0
        if not isinstance(output_tokens, int) or isinstance(output_tokens, bool):
            output_tokens = 0
        input_tokens = max(0, input_tokens)
        output_tokens = max(0, output_tokens)

        try:
            self.record_call(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                recipe_hit=bool(recipe_hit),
                cost_hundredths=cost_hundredths,
            )
        except (ValueError, TypeError):
            pass  # Never let tracking crash the caller
