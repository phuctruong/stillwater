from __future__ import annotations

import pytest

from stillwater.confirmation import ConfirmationGate, ConfirmationRequiredError


def test_archive_requires_confirmation_at_high_rung() -> None:
    gate = ConfirmationGate()
    assert gate.requires_confirmation("archive", count=1, rung=274177) is True


def test_label_bulk_requires_confirmation() -> None:
    gate = ConfirmationGate()
    assert gate.requires_confirmation("label", count=5, rung=641) is True
    assert gate.requires_confirmation("label", count=4, rung=641) is False


def test_parse_approval_accepts_only_explicit_yes() -> None:
    gate = ConfirmationGate()
    assert gate.parse_approval("yes") is True
    assert gate.parse_approval("Y") is True
    assert gate.parse_approval("no") is False
    assert gate.parse_approval("") is False


def test_enforce_raises_when_required_not_approved() -> None:
    gate = ConfirmationGate()
    with pytest.raises(ConfirmationRequiredError):
        gate.enforce(action="archive", count=1, rung=274177, response="no")

