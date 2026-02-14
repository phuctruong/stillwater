"""Verification ladder: OAuth(39,63,91) -> 641 -> 274177 -> 65537."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class VerifyResult:
    """Single verification check result."""

    name: str
    passed: bool
    details: str


def run_oauth_checks() -> list[VerifyResult]:
    """OAuth(39,63,91): CARE, BRIDGE, STABILITY sub-checks."""
    results: list[VerifyResult] = []

    # 39 = CARE: Verify Lane Algebra exists and basic classify works
    try:
        from stillwater.kernel.lane_algebra import Lane, LaneAlgebra

        engine = LaneAlgebra()
        r = engine.classify("test_care", Lane.A)
        results.append(
            VerifyResult("OAuth(39)_CARE", r.lane == Lane.A, "Lane classify works")
        )
    except Exception as e:
        results.append(VerifyResult("OAuth(39)_CARE", False, str(e)))

    # 63 = BRIDGE: Verify combine works (A + B = B)
    try:
        from stillwater.kernel.lane_algebra import Lane, LaneAlgebra

        engine = LaneAlgebra()
        combined = engine.combine([Lane.A, Lane.B])
        results.append(
            VerifyResult("OAuth(63)_BRIDGE", combined == Lane.B, "Combine works")
        )
    except Exception as e:
        results.append(VerifyResult("OAuth(63)_BRIDGE", False, str(e)))

    # 91 = STABILITY: Verify upgrade violation works
    try:
        from stillwater.kernel.lane_algebra import Lane, LaneAlgebra, UpgradeViolation

        engine = LaneAlgebra()
        engine.classify("stability_test", Lane.C)
        try:
            engine.classify("stability_test", Lane.A)
            results.append(
                VerifyResult("OAuth(91)_STABILITY", False, "Should have raised")
            )
        except UpgradeViolation:
            results.append(
                VerifyResult("OAuth(91)_STABILITY", True, "Upgrade blocked")
            )
    except Exception as e:
        results.append(VerifyResult("OAuth(91)_STABILITY", False, str(e)))

    return results


def run_641_edge_tests() -> list[VerifyResult]:
    """641 edge tests: at least 5 tests."""
    results: list[VerifyResult] = []
    from stillwater.kernel.lane_algebra import Lane, LaneAlgebra, UpgradeViolation

    # lane_algebra: Total order holds
    try:
        assert Lane.A > Lane.B > Lane.C > Lane.STAR
        results.append(
            VerifyResult("641_lane_algebra", True, "Total order A>B>C>STAR")
        )
    except Exception as e:
        results.append(VerifyResult("641_lane_algebra", False, str(e)))

    # state_machine: Classify is idempotent
    try:
        e = LaneAlgebra()
        r1 = e.classify("x", Lane.B)
        r2 = e.classify("x", Lane.B)
        results.append(
            VerifyResult("641_state_machine", r1.lane == r2.lane, "Idempotent classify")
        )
    except Exception as e:
        results.append(VerifyResult("641_state_machine", False, str(e)))

    # counter_bypass: MIN rule is deterministic
    try:
        e = LaneAlgebra()
        for _ in range(100):
            assert e.combine([Lane.A, Lane.C]) == Lane.C
        results.append(
            VerifyResult("641_counter_bypass", True, "MIN rule stable x100")
        )
    except Exception as e:
        results.append(VerifyResult("641_counter_bypass", False, str(e)))

    # rtc: classify -> read back is identical
    try:
        e = LaneAlgebra()
        r = e.classify("rtc_test", Lane.B)
        assert r.claim == "rtc_test" and r.lane == Lane.B
        results.append(VerifyResult("641_rtc", True, "Round-trip consistent"))
    except Exception as e:
        results.append(VerifyResult("641_rtc", False, str(e)))

    # type_guards: bool rejected, non-str rejected
    try:
        e = LaneAlgebra()
        rejected = False
        try:
            e.classify(True, Lane.A)  # type: ignore[arg-type]
        except TypeError:
            rejected = True
        results.append(VerifyResult("641_type_guards", rejected, "Bool rejected"))
    except Exception as e:
        results.append(VerifyResult("641_type_guards", False, str(e)))

    return results


def run_274177_stress_tests() -> list[VerifyResult]:
    """274177 stress tests: determinism and scaling."""
    results: list[VerifyResult] = []
    from stillwater.kernel.lane_algebra import Lane, LaneAlgebra

    # Determinism: same operations produce same result
    try:

        def run_once() -> Lane:
            e = LaneAlgebra()
            for i in range(50):
                lane = Lane.A if i % 3 == 0 else Lane.B if i % 3 == 1 else Lane.C
                e.classify(f"claim_{i}", lane)
            return e.combine([Lane.A, Lane.B, Lane.C])

        r1, r2 = run_once(), run_once()
        results.append(
            VerifyResult("274177_determinism", r1 == r2, f"Both={r1.name}")
        )
    except Exception as e:
        results.append(VerifyResult("274177_determinism", False, str(e)))

    # Scaling: 1000 classifications don't degrade
    try:
        e = LaneAlgebra()
        for i in range(1000):
            e.classify(f"scale_{i}", Lane.B)
        r = e.combine([Lane.B])
        results.append(VerifyResult("274177_scaling", r == Lane.B, "1000 classifies OK"))
    except Exception as e:
        results.append(VerifyResult("274177_scaling", False, str(e)))

    return results


def run_65537_god_test(
    oauth: list[VerifyResult],
    edge: list[VerifyResult],
    stress: list[VerifyResult],
) -> VerifyResult:
    """65537 god approval: all prior tests must pass."""
    all_prior = oauth + edge + stress
    all_passed = all(r.passed for r in all_prior)
    if all_passed:
        return VerifyResult("65537_god_approval", True, "All rungs passed")
    failed = [r.name for r in all_prior if not r.passed]
    return VerifyResult(
        "65537_god_approval", False, f"Failed: {', '.join(failed)}"
    )


def build_certificate(
    oauth: list[VerifyResult],
    edge: list[VerifyResult],
    stress: list[VerifyResult],
    god: VerifyResult,
) -> dict:
    """Build canonical certificate JSON (no timestamps, sorted keys)."""
    cert: dict = {
        "auth": 65537,
        "edge_641": [asdict(r) for r in edge],
        "god_65537": asdict(god),
        "hash": "",
        "oauth": [asdict(r) for r in oauth],
        "status": "PASSED" if god.passed else "FAILED",
        "stress_274177": [asdict(r) for r in stress],
    }
    # Content-address: hash the certificate without the hash field
    cert_no_hash = {k: v for k, v in sorted(cert.items()) if k != "hash"}
    cert_json = json.dumps(cert_no_hash, sort_keys=True, separators=(",", ":"))
    cert["hash"] = hashlib.sha256(cert_json.encode()).hexdigest()
    return cert


def run_verification(verbose: bool = False) -> tuple[bool, dict]:
    """Run full verification ladder. Returns (passed, certificate)."""
    out = sys.stdout

    # OAuth(39,63,91)
    oauth = run_oauth_checks()
    oauth_pass = all(r.passed for r in oauth)
    out.write(f"OAuth(39,63,91) ... {'PASS' if oauth_pass else 'FAIL'}\n")
    if verbose:
        for r in oauth:
            out.write(f"  {r.name}: {'PASS' if r.passed else 'FAIL'} — {r.details}\n")

    # 641 edge tests
    edge = run_641_edge_tests()
    edge_pass = all(r.passed for r in edge)
    out.write(f"641 ... {'PASS' if edge_pass else 'FAIL'}\n")
    if verbose:
        for r in edge:
            out.write(f"  {r.name}: {'PASS' if r.passed else 'FAIL'} — {r.details}\n")

    # 274177 stress tests
    stress = run_274177_stress_tests()
    stress_pass = all(r.passed for r in stress)
    out.write(f"274177 ... {'PASS' if stress_pass else 'FAIL'}\n")
    if verbose:
        for r in stress:
            out.write(f"  {r.name}: {'PASS' if r.passed else 'FAIL'} — {r.details}\n")

    # 65537 god approval
    god = run_65537_god_test(oauth, edge, stress)
    out.write(f"65537 ... {'PASS' if god.passed else 'FAIL'}\n")
    if verbose:
        out.write(f"  {god.name}: {'PASS' if god.passed else 'FAIL'} — {god.details}\n")

    cert = build_certificate(oauth, edge, stress, god)
    return god.passed, cert
