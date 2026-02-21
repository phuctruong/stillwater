"""
Stillwater Dragon Tip Hooks — integrates with LLM client.
Auth: 65537 | Status: STABLE | Version: 1.0.0

Dragon Tip system: users voluntarily tip a percentage of their LLM cost
to fund OSS projects. Named after the Dragon Tiers from Solace AGI.

Tip percentages: 2% (Dragon) → 50% (max cap).

Design rules:
  - ALL money math uses Python int (hundredths of a cent) — NEVER float
  - Decimal used for intermediate calculations, converted to int for storage
  - Thread-safe: threading.Lock guards all mutable state
  - No external dependencies beyond stdlib
  - Backward-compatible: opt-in via tip_callback= parameter on llm_call/llm_chat

Usage:
    from stillwater.tip_hooks import TipConfig, SessionTipAccumulator, get_tip_summary

    config = TipConfig(tip_pct=5, oss_project="paudio")
    accumulator = SessionTipAccumulator(config=config)

    # Attach to llm_call:
    from stillwater.llm_client import llm_call
    result = llm_call("hello", tip_callback=accumulator.tip_callback)

    summary = get_tip_summary(accumulator)
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Optional

from .providers.pricing import estimate_cost as _estimate_cost

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIP_PCT_MIN: int = 2
TIP_PCT_MAX: int = 50

# SW5.0 iteration reduction factor (40% = 0.40).
# Non-recipe calls benefit from SW5.0 discipline cutting ~40% of token usage.
SW5_SAVINGS_FACTOR_PCT: int = 40  # stored as integer percent


# ---------------------------------------------------------------------------
# TipConfig
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TipConfig:
    """
    Immutable configuration for Dragon Tip hooks.

    Attributes:
        tip_pct:     Tip percentage as integer. Must be between 2 and 50 (inclusive).
        oss_project: OSS project funded by this tip (default: "paudio").
        enabled:     Whether tipping is active (default: True).

    Raises:
        ValueError: If tip_pct is out of range [2, 50].
        TypeError:  If tip_pct is not an int (bool is also rejected).
    """

    tip_pct: int
    oss_project: str = "paudio"
    enabled: bool = True

    def __post_init__(self) -> None:
        # Reject bool subclass (bool is subclass of int in Python)
        if isinstance(self.tip_pct, bool):
            raise TypeError(
                f"tip_pct must be int, got bool. Use an integer like 5."
            )
        if not isinstance(self.tip_pct, int):
            raise TypeError(
                f"tip_pct must be int, got {type(self.tip_pct).__name__}"
            )
        if not (TIP_PCT_MIN <= self.tip_pct <= TIP_PCT_MAX):
            raise ValueError(
                f"tip_pct must be between {TIP_PCT_MIN} and {TIP_PCT_MAX}, "
                f"got {self.tip_pct}"
            )
        if not isinstance(self.oss_project, str) or not self.oss_project:
            raise ValueError("oss_project must be a non-empty string")
        if not isinstance(self.enabled, bool):
            raise TypeError(
                f"enabled must be bool, got {type(self.enabled).__name__}"
            )


# ---------------------------------------------------------------------------
# SessionTipAccumulator
# ---------------------------------------------------------------------------


class SessionTipAccumulator:
    """
    Tracks Dragon Tips accumulated during a single session.

    All monetary values are stored as integers in hundredths of a cent.
    Thread-safe via threading.Lock.

    Usage:
        config = TipConfig(tip_pct=5, oss_project="paudio")
        acc = SessionTipAccumulator(config=config)

        tip = acc.tip_for_call("claude-sonnet-4-20250514", input_tokens=1000, output_tokens=500)
        total = acc.get_session_total()
        summary = get_tip_summary(acc)
    """

    def __init__(self, config: Optional[TipConfig] = None) -> None:
        self._config = config or TipConfig(tip_pct=TIP_PCT_MIN)
        self._lock = threading.Lock()
        self._tips: list[int] = []           # each tip in hundredths of cent
        self._call_count: int = 0
        self._recipe_hits: int = 0
        self._tokens_saved: int = 0          # tokens not sent due to recipe hits
        self._cost_saved_hundredths: int = 0  # hundredths of cent saved via recipes

    # ------------------------------------------------------------------
    # Core calculation
    # ------------------------------------------------------------------

    def tip_for_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        recipe_hit: bool = False,
        cost_hundredths: Optional[int] = None,
    ) -> int:
        """
        Calculate and record a tip for one LLM call.

        Args:
            model:          Model name (used to look up pricing).
            input_tokens:   Number of input tokens.
            output_tokens:  Number of output tokens.
            recipe_hit:     If True, this call was served from a recipe cache.
            cost_hundredths: Override cost in hundredths of a cent. If None,
                            computed from MODEL_PRICING.

        Returns:
            Tip amount in hundredths of a cent (int). Returns 0 if disabled.
        """
        if not self._config.enabled:
            return 0

        # Compute base cost (int arithmetic, no float)
        if cost_hundredths is None:
            cost_hundredths = _estimate_cost(input_tokens, output_tokens, model)

        # Tip calculation via Decimal to ensure no float contamination
        # tip = cost_hundredths * tip_pct / 100
        cost_d = Decimal(str(cost_hundredths))
        pct_d = Decimal(str(self._config.tip_pct))
        tip_d = cost_d * pct_d / Decimal("100")
        tip_amount = int(tip_d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        with self._lock:
            self._tips.append(tip_amount)
            self._call_count += 1

            if recipe_hit:
                self._recipe_hits += 1
                # Tokens that would have been used without recipe cache
                self._tokens_saved += input_tokens + output_tokens
                self._cost_saved_hundredths += cost_hundredths

        return tip_amount

    # ------------------------------------------------------------------
    # Session queries
    # ------------------------------------------------------------------

    def get_session_total(self) -> int:
        """Return total tips accumulated this session in hundredths of a cent."""
        with self._lock:
            return sum(self._tips)

    def get_session_savings(self) -> dict[str, Any]:
        """
        Return savings report for this session.

        Returns dict with:
            recipe_hits:           Number of recipe cache hits.
            tokens_saved:          Total tokens avoided via recipe replay.
            cost_saved_hundredths: Total cost avoided (in hundredths of cent).
        """
        with self._lock:
            return {
                "recipe_hits": self._recipe_hits,
                "tokens_saved": self._tokens_saved,
                "cost_saved_hundredths": self._cost_saved_hundredths,
            }

    def get_call_count(self) -> int:
        """Return number of calls tracked this session."""
        with self._lock:
            return self._call_count

    def reset(self) -> None:
        """Clear all session state. Does NOT reset config."""
        with self._lock:
            self._tips.clear()
            self._call_count = 0
            self._recipe_hits = 0
            self._tokens_saved = 0
            self._cost_saved_hundredths = 0

    # ------------------------------------------------------------------
    # Callback interface
    # ------------------------------------------------------------------

    def tip_callback(self, call_result: dict) -> None:
        """
        Callback suitable for passing to llm_call() / llm_chat().

        Extracts model, input_tokens, output_tokens from call_result dict
        and records the tip via tip_for_call().

        Args:
            call_result: Dict with keys: model, input_tokens, output_tokens.
                        Optional keys: cost_hundredths_cent, recipe_hit.

        Example:
            acc = SessionTipAccumulator(TipConfig(tip_pct=5))
            llm_call("hello", tip_callback=acc.tip_callback)
        """
        if not isinstance(call_result, dict):
            return

        model = call_result.get("model", "")
        input_tokens = call_result.get("input_tokens", 0)
        output_tokens = call_result.get("output_tokens", 0)
        recipe_hit = call_result.get("recipe_hit", False)
        cost_hundredths = call_result.get("cost_hundredths_cent")

        # Validate token values are non-negative ints
        if not isinstance(input_tokens, int) or isinstance(input_tokens, bool):
            input_tokens = 0
        if not isinstance(output_tokens, int) or isinstance(output_tokens, bool):
            output_tokens = 0

        self.tip_for_call(
            model=str(model),
            input_tokens=max(0, input_tokens),
            output_tokens=max(0, output_tokens),
            recipe_hit=bool(recipe_hit),
            cost_hundredths=cost_hundredths,
        )


# ---------------------------------------------------------------------------
# Module-level default accumulator (singleton for simple use cases)
# ---------------------------------------------------------------------------

_default_accumulator: Optional[SessionTipAccumulator] = None
_default_lock = threading.Lock()


def get_default_accumulator() -> SessionTipAccumulator:
    """Return the module-level default accumulator (lazy-initialized)."""
    global _default_accumulator
    with _default_lock:
        if _default_accumulator is None:
            _default_accumulator = SessionTipAccumulator()
        return _default_accumulator


# ---------------------------------------------------------------------------
# Convenience: get_tip_summary
# ---------------------------------------------------------------------------


def get_tip_summary(accumulator: Optional[SessionTipAccumulator] = None) -> dict[str, Any]:
    """
    Return a complete tip summary for the given accumulator.

    Args:
        accumulator: SessionTipAccumulator instance. If None, uses the
                    module-level default accumulator.

    Returns:
        Dict with:
            total_cost_hundredths: int — estimated total LLM cost (hundredths of cent)
            total_tip_hundredths:  int — total tip amount (hundredths of cent)
            tip_pct:               int — configured tip percentage
            oss_project:           str — target OSS project
            call_count:            int — number of calls in session
            savings:               dict — recipe_hits, tokens_saved, cost_saved_hundredths
    """
    if accumulator is None:
        accumulator = get_default_accumulator()

    total_tip = accumulator.get_session_total()
    config = accumulator._config
    call_count = accumulator.get_call_count()

    # Reverse-compute approximate total cost:
    # total_tip = total_cost * tip_pct / 100
    # => total_cost = total_tip * 100 / tip_pct
    if config.tip_pct > 0 and total_tip > 0:
        cost_d = Decimal(str(total_tip)) * Decimal("100") / Decimal(str(config.tip_pct))
        total_cost = int(cost_d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    else:
        total_cost = 0

    return {
        "total_cost_hundredths": total_cost,
        "total_tip_hundredths": total_tip,
        "tip_pct": config.tip_pct,
        "oss_project": config.oss_project,
        "call_count": call_count,
        "savings": accumulator.get_session_savings(),
    }
