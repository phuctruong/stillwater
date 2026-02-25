"""Explicit confirmation gates for high-risk actions."""

from __future__ import annotations

from dataclasses import dataclass


class ConfirmationRequiredError(PermissionError):
    """Raised when explicit human approval is required but missing."""


@dataclass(frozen=True)
class ConfirmationDecision:
    action: str
    count: int
    rung: int
    required: bool
    approved: bool


class ConfirmationGate:
    """Rule engine for confirmation requirements."""

    _HIGH_RISK_ACTIONS = {"archive", "send", "delete", "reply", "compose"}

    def requires_confirmation(self, action: str, *, count: int = 1, rung: int = 641) -> bool:
        if count < 0:
            raise ValueError("count cannot be negative")
        act = (action or "").strip().lower()
        if not act:
            raise ValueError("action is required")

        if act in self._HIGH_RISK_ACTIONS and rung >= 274177:
            return True
        if act == "label" and count >= 5:
            return True
        return False

    @staticmethod
    def parse_approval(response: str) -> bool:
        text = (response or "").strip().lower()
        return text in {"yes", "y", "approve", "approved", "confirm"}

    def evaluate(
        self,
        *,
        action: str,
        count: int = 1,
        rung: int = 641,
        response: str = "",
    ) -> ConfirmationDecision:
        required = self.requires_confirmation(action, count=count, rung=rung)
        approved = self.parse_approval(response) if required else True
        return ConfirmationDecision(
            action=action,
            count=count,
            rung=rung,
            required=required,
            approved=approved,
        )

    def enforce(
        self,
        *,
        action: str,
        count: int = 1,
        rung: int = 641,
        response: str = "",
    ) -> None:
        decision = self.evaluate(action=action, count=count, rung=rung, response=response)
        if decision.required and not decision.approved:
            raise ConfirmationRequiredError(
                f"confirmation required for action={action} count={count} rung={rung}"
            )

