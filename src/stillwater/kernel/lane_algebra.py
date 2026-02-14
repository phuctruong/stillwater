from __future__ import annotations

import enum
from dataclasses import dataclass


class Lane(enum.IntEnum):
    """Lane classification with total order: A > B > C > STAR."""
    STAR = 1
    C = 2
    B = 3
    A = 4


class UpgradeViolation(Exception):
    """Raised when a claim is reclassified to a stronger lane."""
    pass


@dataclass(frozen=True)
class LaneResult:
    """Immutable result of a lane classification."""
    claim: str
    lane: Lane


class LaneAlgebra:
    """Lane Algebra engine enforcing epistemic hygiene.

    Core invariant: Lane(Conclusion) = MIN(Lane(premises)).
    Upgrades (weaker -> stronger) are FORBIDDEN.
    """

    def __init__(self) -> None:
        self._claims: dict[str, Lane] = {}

    def classify(self, claim: str, lane: Lane) -> LaneResult:
        """Classify a claim into a lane.

        Raises TypeError if claim is not a str (bool rejected explicitly).
        Raises UpgradeViolation if reclassifying to a stronger lane.
        Same lane (idempotent) or weaker lane (downgrade) is OK.
        """
        if isinstance(claim, bool):
            raise TypeError(f"claim must be str, not {type(claim).__name__}")
        if not isinstance(claim, str):
            raise TypeError(f"claim must be str, not {type(claim).__name__}")

        if claim in self._claims:
            existing = self._claims[claim]
            if lane > existing:
                raise UpgradeViolation(
                    f"cannot upgrade {claim!r} from {existing.name} to {lane.name}"
                )

        self._claims[claim] = lane
        return LaneResult(claim=claim, lane=lane)

    def combine(self, lanes: list[Lane]) -> Lane:
        """Combine lanes: returns MIN (weakest wins).

        Raises ValueError on empty list.
        """
        if not lanes:
            raise ValueError("cannot combine empty lane list")
        return min(lanes)

    def conclude(
        self,
        claim: str,
        premises: list[LaneResult],
        override_lane: Lane | None = None,
    ) -> LaneResult:
        """Draw a conclusion from premises.

        Conclusion lane = MIN of premise lanes.
        If override_lane is provided and STRONGER than premise min, raises UpgradeViolation.
        If override_lane is WEAKER, it is used instead.
        Empty premises with no override defaults to STAR.
        """
        if premises:
            premise_min = self.combine([p.lane for p in premises])
        else:
            premise_min = Lane.STAR

        if override_lane is not None:
            if override_lane > premise_min:
                raise UpgradeViolation(
                    f"cannot override to {override_lane.name}, "
                    f"premises support at most {premise_min.name}"
                )
            result_lane = override_lane
        else:
            result_lane = premise_min

        return self.classify(claim, result_lane)
