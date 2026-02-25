"""Session budget gates for bounded agent actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


class BudgetExceededError(RuntimeError):
    """Raised when an action would exceed the configured session budget."""


@dataclass
class BudgetCounter:
    """Hard per-session budget tracker.

    Limits are immutable during a session. Counters are one-way ratchets.
    """

    limits: Dict[str, int]
    consumed: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized: dict[str, int] = {}
        for action, limit in self.limits.items():
            if not isinstance(limit, int):
                raise TypeError(f"budget limit for {action!r} must be int")
            if limit < 0:
                raise ValueError(f"budget limit for {action!r} cannot be negative")
            normalized[action] = limit
        self.limits = normalized
        for action in self.limits:
            self.consumed.setdefault(action, 0)

    def remaining(self, action: str) -> int:
        self._require_action(action)
        remain = self.limits[action] - self.consumed[action]
        return max(remain, 0)

    def exhausted(self, action: str) -> bool:
        return self.remaining(action) == 0

    def consume(self, action: str, amount: int = 1) -> int:
        self._require_action(action)
        if amount <= 0:
            raise ValueError("amount must be positive")

        current = self.consumed[action]
        limit = self.limits[action]
        next_value = current + amount
        if next_value > limit:
            raise BudgetExceededError(
                f"EMAIL_BUDGET_EXCEEDED: action={action} consumed={current} requested={amount} limit={limit}"
            )
        self.consumed[action] = next_value
        return self.remaining(action)

    def to_evidence(self) -> dict[str, dict[str, int]]:
        remaining = {k: self.remaining(k) for k in self.limits}
        return {
            "limits": dict(self.limits),
            "consumed": dict(self.consumed),
            "remaining": remaining,
        }

    def _require_action(self, action: str) -> None:
        if action not in self.limits:
            raise KeyError(f"unknown budget action: {action}")

