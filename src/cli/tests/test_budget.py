from __future__ import annotations

import pytest

from stillwater.budget import BudgetCounter, BudgetExceededError


def test_budget_remaining_and_consume() -> None:
    b = BudgetCounter({"read": 2})
    assert b.remaining("read") == 2
    b.consume("read", 1)
    assert b.remaining("read") == 1


def test_budget_exhaustion_raises() -> None:
    b = BudgetCounter({"archive": 1})
    b.consume("archive", 1)
    with pytest.raises(BudgetExceededError):
        b.consume("archive", 1)


def test_zero_budget_blocks_action() -> None:
    b = BudgetCounter({"delete": 0})
    assert b.exhausted("delete") is True
    with pytest.raises(BudgetExceededError):
        b.consume("delete", 1)


def test_to_evidence_contains_limits_consumed_remaining() -> None:
    b = BudgetCounter({"read": 3, "label": 1})
    b.consume("read", 2)
    evidence = b.to_evidence()
    assert evidence["limits"]["read"] == 3
    assert evidence["consumed"]["read"] == 2
    assert evidence["remaining"]["read"] == 1

