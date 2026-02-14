from __future__ import annotations

import pytest

from stillwater.kernel.lane_algebra import (
    Lane,
    LaneAlgebra,
    LaneResult,
    UpgradeViolation,
)


@pytest.fixture
def engine() -> LaneAlgebra:
    return LaneAlgebra()


# T1 - Classify A
def test_classify_a(engine: LaneAlgebra) -> None:
    result = engine.classify("2+2=4", Lane.A)
    assert result.lane == Lane.A
    assert result.claim == "2+2=4"


# T2 - Classify C and total order
def test_classify_c_and_total_order(engine: LaneAlgebra) -> None:
    result = engine.classify("AI will be conscious by 2030", Lane.C)
    assert result.lane == Lane.C
    assert Lane.C < Lane.B < Lane.A


# T3 - Min rule: A + B = B
def test_combine_a_b(engine: LaneAlgebra) -> None:
    assert engine.combine([Lane.A, Lane.B]) == Lane.B


# T4 - Min rule: A + C = C
def test_combine_a_c(engine: LaneAlgebra) -> None:
    assert engine.combine([Lane.A, Lane.C]) == Lane.C


# T5 - Min rule: B + STAR = STAR
def test_combine_b_star(engine: LaneAlgebra) -> None:
    assert engine.combine([Lane.B, Lane.STAR]) == Lane.STAR


# T6 - Identity: A + A = A
def test_combine_identity(engine: LaneAlgebra) -> None:
    assert engine.combine([Lane.A, Lane.A]) == Lane.A


# T7 - Upgrade violation
def test_upgrade_violation(engine: LaneAlgebra) -> None:
    engine.classify("claim1", Lane.C)
    with pytest.raises(UpgradeViolation) as exc_info:
        engine.classify("claim1", Lane.A)
    msg = str(exc_info.value)
    assert "claim1" in msg
    assert "C" in msg
    assert "A" in msg


# T8 - Empty combine
def test_combine_empty(engine: LaneAlgebra) -> None:
    with pytest.raises(ValueError, match="cannot combine empty lane list"):
        engine.combine([])


# T9 - Single combine
def test_combine_single(engine: LaneAlgebra) -> None:
    assert engine.combine([Lane.B]) == Lane.B


# T10 - Bool rejection
def test_bool_rejection(engine: LaneAlgebra) -> None:
    with pytest.raises(TypeError):
        engine.classify(True, Lane.A)


# T11 - Conclusion with premises
def test_conclusion_with_premises(engine: LaneAlgebra) -> None:
    p1 = engine.classify("axiom1", Lane.A)
    p2 = engine.classify("observation1", Lane.B)
    conclusion = engine.conclude("therefore X", premises=[p1, p2])
    assert conclusion.lane == Lane.B


# T12 - Framework to Classical blocked
def test_framework_to_classical_blocked(engine: LaneAlgebra) -> None:
    engine.classify("Stillwater is better", Lane.C)
    with pytest.raises(UpgradeViolation):
        engine.conclude(
            "Stillwater is proven better",
            premises=[],
            override_lane=Lane.A,
        )
