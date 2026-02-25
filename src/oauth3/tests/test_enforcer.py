"""
OAuth3 Enforcer — Comprehensive Test Suite
==========================================

Rung: 65537 (production/security grade)
Coverage: All 6 OAuth3 governance features + adversarial cases + edge cases

Features tested:
  1. Scoped delegation tokens  (OAuth3Scope, DelegationToken, ActionLimits)
  2. Step-up consent           (ConsentRequest PENDING→APPROVED|DENIED|EXPIRED)
  3. Evidence bundles          (SHA-256 hash chaining, GENESIS anchor)
  4. Action limits             (budgets, exhaustion, fail-closed on absence/zero)
  5. Synchronous revocation    (RevocationRegistry O(1), idempotent)
  6. DPoP binding              (thumbprint matching, absent, mismatched)

No float arithmetic. No mocking of security primitives (SHA-256, hmac.compare_digest).
All timestamps are timezone-aware UTC.
"""

import hashlib
import hmac
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC_ROOT = _REPO_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from oauth3 import (
    ActionLimits,
    ConsentRequest,
    ConsentStatus,
    DelegationToken,
    EnforcementResult,
    EvidenceBundle,
    OAuth3ErrorCode,
    OAuth3Enforcer,
    OAuth3Scope,
    RevocationRegistry,
    RiskLevel,
    ValidationResult,
)


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(tz=timezone.utc) - timedelta(seconds=seconds)


FIXED_TOKEN_ID = "aaaaaaaa-0000-0000-0000-000000000001"
FIXED_PRINCIPAL_ID = "principal:phuc"
FIXED_AGENT_ID = "agent:calendar-bot"
FIXED_ISSUER = "https://stillwater.ai"
FIXED_DPOP_THUMBPRINT = "abc123def456" * 5  # 60-char deterministic thumbprint


def _make_token(
    token_id: str = FIXED_TOKEN_ID,
    principal_id: str = FIXED_PRINCIPAL_ID,
    agent_id: str = FIXED_AGENT_ID,
    scope: list = None,
    action_limits: ActionLimits = None,
    expires_at: datetime = None,
    issued_at: datetime = None,
    issuer: str = FIXED_ISSUER,
    dpop_thumbprint: str = None,
    revoked: bool = False,
) -> DelegationToken:
    if scope is None:
        scope = [OAuth3Scope(resource="calendar:events", permission="read")]
    if action_limits is None:
        action_limits = ActionLimits(limits={"read": 10})
    if expires_at is None:
        expires_at = _future(3600)
    if issued_at is None:
        issued_at = _past(60)
    return DelegationToken(
        token_id=token_id,
        principal_id=principal_id,
        agent_id=agent_id,
        scope=scope,
        action_limits=action_limits,
        expires_at=expires_at,
        issued_at=issued_at,
        issuer=issuer,
        dpop_thumbprint=dpop_thumbprint,
        revoked=revoked,
    )


def _make_enforcer(clock_skew_seconds: int = 30) -> OAuth3Enforcer:
    registry = RevocationRegistry()
    return OAuth3Enforcer(registry=registry, clock_skew_seconds=clock_skew_seconds)


# ---------------------------------------------------------------------------
# Section 1: OAuth3Scope — exact match semantics
# ---------------------------------------------------------------------------

class TestOAuth3Scope:

    def test_scope_exact_match(self):
        scope = OAuth3Scope(resource="calendar:events", permission="read")
        assert scope.matches("calendar:events", "read") is True

    def test_scope_resource_mismatch(self):
        scope = OAuth3Scope(resource="calendar:events", permission="read")
        assert scope.matches("calendar:contacts", "read") is False

    def test_scope_permission_mismatch(self):
        scope = OAuth3Scope(resource="calendar:events", permission="read")
        assert scope.matches("calendar:events", "write") is False

    def test_scope_no_prefix_matching(self):
        # Spec Section 3.3: No prefix matching — exact string equality only.
        scope = OAuth3Scope(resource="calendar", permission="read")
        assert scope.matches("calendar:events", "read") is False

    def test_scope_case_sensitive(self):
        scope = OAuth3Scope(resource="Calendar:Events", permission="Read")
        assert scope.matches("calendar:events", "read") is False
        assert scope.matches("Calendar:Events", "Read") is True


# ---------------------------------------------------------------------------
# Section 2: ActionLimits — budgets, exhaustion, fail-closed
# ---------------------------------------------------------------------------

class TestActionLimits:

    def test_action_allowed_positive_budget(self):
        limits = ActionLimits(limits={"read": 5})
        assert limits.is_action_allowed("read") is True

    def test_action_denied_absent_key(self):
        # Spec: absence of key = NOT permitted (not unlimited)
        limits = ActionLimits(limits={"read": 5})
        assert limits.is_action_allowed("write") is False

    def test_action_denied_zero_budget(self):
        limits = ActionLimits(limits={"read": 0})
        assert limits.is_action_allowed("read") is False

    def test_action_denied_corrupt_budget_string(self):
        # Fail-closed: non-integer value treated as 0 (denied)
        limits = ActionLimits(limits={"read": "10"})  # type: ignore
        assert limits.is_action_allowed("read") is False

    def test_decrement_reduces_budget(self):
        limits = ActionLimits(limits={"read": 3})
        assert limits.decrement("read") is True
        assert limits.remaining("read") == 2

    def test_decrement_to_zero_then_denied(self):
        limits = ActionLimits(limits={"read": 1})
        assert limits.decrement("read") is True
        assert limits.remaining("read") == 0
        assert limits.is_action_allowed("read") is False

    def test_decrement_absent_key_returns_false(self):
        limits = ActionLimits(limits={"read": 5})
        assert limits.decrement("delete") is False

    def test_decrement_zero_budget_returns_false(self):
        limits = ActionLimits(limits={"read": 0})
        assert limits.decrement("read") is False

    def test_remaining_absent_key_returns_zero(self):
        limits = ActionLimits(limits={})
        assert limits.remaining("read") == 0

    def test_remaining_corrupt_value_returns_zero(self):
        limits = ActionLimits(limits={"read": "bad"})  # type: ignore
        assert limits.remaining("read") == 0

    def test_budget_exhaustion_sequence(self):
        # Budget: 3 reads → exactly 3 decrements succeed, 4th fails
        limits = ActionLimits(limits={"read": 3})
        for i in range(3):
            assert limits.decrement("read") is True, f"decrement {i+1} should succeed"
        assert limits.decrement("read") is False


# ---------------------------------------------------------------------------
# Section 3: DelegationToken validity
# ---------------------------------------------------------------------------

class TestDelegationTokenValidity:

    def test_valid_token(self):
        token = _make_token()
        assert token.is_valid() is True

    def test_expired_token(self):
        token = _make_token(expires_at=_past(3600), issued_at=_past(7200))
        assert token.is_valid() is False

    def test_future_issued_at_beyond_skew(self):
        # issued_at far in the future = future-dating attack guard
        token = _make_token(issued_at=_future(300))
        assert token.is_valid(clock_skew_seconds=30) is False

    def test_within_clock_skew_still_valid(self):
        # expires_at is 10 seconds ago, but skew=30 → should still be valid
        token = _make_token(
            expires_at=_past(10),
            issued_at=_past(3600),
        )
        assert token.is_valid(clock_skew_seconds=30) is True

    def test_naive_datetime_rejected(self):
        naive_dt = datetime(2030, 1, 1)  # No tzinfo
        token = _make_token(expires_at=naive_dt)
        assert token.is_valid() is False

    def test_advisory_revoked_flag_makes_token_invalid(self):
        token = _make_token(revoked=True)
        assert token.is_valid() is False

    def test_is_action_allowed_scope_and_budget(self):
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        assert token.is_action_allowed("read", "calendar:events") is True

    def test_is_action_allowed_scope_mismatch(self):
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"write": 5}),
        )
        assert token.is_action_allowed("write", "calendar:events") is False

    def test_is_action_allowed_budget_exhausted(self):
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 0}),
        )
        assert token.is_action_allowed("read", "calendar:events") is False


# ---------------------------------------------------------------------------
# Section 4: RevocationRegistry — O(1), idempotent, permanent
# ---------------------------------------------------------------------------

class TestRevocationRegistry:

    def test_initially_empty(self):
        reg = RevocationRegistry()
        assert reg.count() == 0

    def test_revoke_and_is_revoked(self):
        reg = RevocationRegistry()
        reg.revoke("token-abc")
        assert reg.is_revoked("token-abc") is True

    def test_unrevoked_token_not_in_registry(self):
        reg = RevocationRegistry()
        reg.revoke("token-abc")
        assert reg.is_revoked("token-xyz") is False

    def test_revoke_idempotent(self):
        reg = RevocationRegistry()
        assert reg.revoke("token-abc") is True
        assert reg.revoke("token-abc") is True
        assert reg.count() == 1  # Only one entry in set

    def test_count_increments_correctly(self):
        reg = RevocationRegistry()
        reg.revoke("t1")
        reg.revoke("t2")
        reg.revoke("t3")
        assert reg.count() == 3

    def test_revocation_is_permanent(self):
        reg = RevocationRegistry()
        reg.revoke("token-abc")
        # No way to un-revoke: still revoked after multiple checks
        assert reg.is_revoked("token-abc") is True
        assert reg.is_revoked("token-abc") is True


# ---------------------------------------------------------------------------
# Section 5: EvidenceBundle — hash chaining
# ---------------------------------------------------------------------------

class TestEvidenceBundle:

    def _make_genesis_bundle(self) -> EvidenceBundle:
        action_id = "00000000-0000-0000-0000-000000000001"
        timestamp = "2026-01-01T00:00:00+00:00"
        payload = f"{action_id}|{FIXED_TOKEN_ID}|{FIXED_AGENT_ID}|{FIXED_PRINCIPAL_ID}|read|calendar:events|{timestamp}|deadbeef"
        evidence_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return EvidenceBundle(
            action_id=action_id,
            token_id=FIXED_TOKEN_ID,
            agent_id=FIXED_AGENT_ID,
            principal_id=FIXED_PRINCIPAL_ID,
            action_type="read",
            resource="calendar:events",
            timestamp=timestamp,
            evidence_hash=evidence_hash,
            previous_hash="GENESIS",
        )

    def test_genesis_bundle_has_genesis_previous_hash(self):
        bundle = self._make_genesis_bundle()
        assert bundle.previous_hash == "GENESIS"

    def test_compute_own_hash_is_sha256_hex(self):
        bundle = self._make_genesis_bundle()
        h = bundle.compute_own_hash()
        # SHA-256 hex: exactly 64 characters
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_compute_own_hash_is_deterministic(self):
        bundle = self._make_genesis_bundle()
        h1 = bundle.compute_own_hash()
        h2 = bundle.compute_own_hash()
        assert h1 == h2

    def test_verify_chain_correct_linkage(self):
        genesis = self._make_genesis_bundle()
        # Build bundle2 referencing genesis
        genesis_hash = genesis.compute_own_hash()
        action_id2 = "00000000-0000-0000-0000-000000000002"
        timestamp2 = "2026-01-01T00:01:00+00:00"
        payload2 = f"{action_id2}|{FIXED_TOKEN_ID}|{FIXED_AGENT_ID}|{FIXED_PRINCIPAL_ID}|write|calendar:events|{timestamp2}|cafebabe"
        evidence_hash2 = hashlib.sha256(payload2.encode("utf-8")).hexdigest()
        bundle2 = EvidenceBundle(
            action_id=action_id2,
            token_id=FIXED_TOKEN_ID,
            agent_id=FIXED_AGENT_ID,
            principal_id=FIXED_PRINCIPAL_ID,
            action_type="write",
            resource="calendar:events",
            timestamp=timestamp2,
            evidence_hash=evidence_hash2,
            previous_hash=genesis_hash,
        )
        assert bundle2.verify_chain(genesis) is True

    def test_verify_chain_detects_tampering(self):
        genesis = self._make_genesis_bundle()
        # Bundle with wrong previous_hash
        action_id2 = "00000000-0000-0000-0000-000000000002"
        timestamp2 = "2026-01-01T00:01:00+00:00"
        payload2 = f"{action_id2}|{FIXED_TOKEN_ID}|{FIXED_AGENT_ID}|{FIXED_PRINCIPAL_ID}|write|calendar:events|{timestamp2}|cafebabe"
        evidence_hash2 = hashlib.sha256(payload2.encode("utf-8")).hexdigest()
        bundle2 = EvidenceBundle(
            action_id=action_id2,
            token_id=FIXED_TOKEN_ID,
            agent_id=FIXED_AGENT_ID,
            principal_id=FIXED_PRINCIPAL_ID,
            action_type="write",
            resource="calendar:events",
            timestamp=timestamp2,
            evidence_hash=evidence_hash2,
            previous_hash="0" * 64,  # Wrong hash — tampering
        )
        assert bundle2.verify_chain(genesis) is False

    def test_to_dict_has_all_required_keys(self):
        bundle = self._make_genesis_bundle()
        d = bundle.to_dict()
        required_keys = [
            "action_id", "token_id", "agent_id", "principal_id",
            "action_type", "resource", "timestamp", "evidence_hash",
            "previous_hash", "dpop_thumbprint",
        ]
        for key in required_keys:
            assert key in d, f"Missing key: {key}"

    def test_evidence_hash_is_full_sha256(self):
        # SHA-256 hex digest is never truncated: 64 hex chars
        bundle = self._make_genesis_bundle()
        assert len(bundle.evidence_hash) == 64

    def test_verify_chain_uses_constant_time_comparison(self):
        # Verify that hmac.compare_digest is used (no early termination on mismatch).
        # We can't directly assert timing, but we confirm the verify_chain path works
        # for both same-length matching and non-matching hashes without exceptions.
        genesis = self._make_genesis_bundle()
        genesis_hash = genesis.compute_own_hash()
        # Construct bundle2 with a tampered hash of same length (64 chars)
        tampered_hash = "f" * 64
        action_id2 = "00000000-0000-0000-0000-000000000002"
        timestamp2 = "2026-01-01T00:01:00+00:00"
        payload2 = f"{action_id2}|{FIXED_TOKEN_ID}|{FIXED_AGENT_ID}|{FIXED_PRINCIPAL_ID}|write|calendar:events|{timestamp2}|cafebabe"
        evidence_hash2 = hashlib.sha256(payload2.encode("utf-8")).hexdigest()
        bundle2 = EvidenceBundle(
            action_id=action_id2,
            token_id=FIXED_TOKEN_ID,
            agent_id=FIXED_AGENT_ID,
            principal_id=FIXED_PRINCIPAL_ID,
            action_type="write",
            resource="calendar:events",
            timestamp=timestamp2,
            evidence_hash=evidence_hash2,
            previous_hash=tampered_hash,
        )
        # Must return False, not raise
        result = bundle2.verify_chain(genesis)
        assert result is False


# ---------------------------------------------------------------------------
# Section 6: ConsentRequest — lifecycle transitions
# ---------------------------------------------------------------------------

class TestConsentRequest:

    def _make_consent(self, timeout_seconds: int = 300, past_offset: int = 0) -> ConsentRequest:
        requested_at = _utc_now() - timedelta(seconds=past_offset)
        return ConsentRequest(
            request_id=str(uuid.uuid4()),
            action_description="Delete user data",
            risk_level=RiskLevel.HIGH,
            token_id=FIXED_TOKEN_ID,
            requested_at=requested_at,
            timeout_seconds=timeout_seconds,
            status=ConsentStatus.PENDING,
        )

    def test_initial_status_is_pending(self):
        consent = self._make_consent()
        assert consent.status == ConsentStatus.PENDING

    def test_approve_pending_returns_true(self):
        consent = self._make_consent()
        assert consent.approve() is True
        assert consent.status == ConsentStatus.APPROVED

    def test_deny_pending_returns_true(self):
        consent = self._make_consent()
        assert consent.deny() is True
        assert consent.status == ConsentStatus.DENIED

    def test_approve_already_denied_returns_false(self):
        consent = self._make_consent()
        consent.deny()
        assert consent.approve() is False
        assert consent.status == ConsentStatus.DENIED  # No change

    def test_deny_already_approved_returns_false(self):
        consent = self._make_consent()
        consent.approve()
        assert consent.deny() is False
        assert consent.status == ConsentStatus.APPROVED  # No change

    def test_is_expired_pending_timeout(self):
        # Timeout of 10s, requested 60s ago → expired
        consent = self._make_consent(timeout_seconds=10, past_offset=60)
        assert consent.is_expired() is True
        assert consent.status == ConsentStatus.EXPIRED

    def test_is_expired_pending_not_yet_expired(self):
        # Timeout of 300s, requested 10s ago → not expired
        consent = self._make_consent(timeout_seconds=300, past_offset=10)
        assert consent.is_expired() is False

    def test_approve_expired_returns_false(self):
        consent = self._make_consent(timeout_seconds=10, past_offset=60)
        assert consent.is_expired() is True
        assert consent.approve() is False

    def test_is_expired_already_approved(self):
        consent = self._make_consent()
        consent.approve()
        # Once approved, is_expired returns False (not the timeout-expired sense)
        assert consent.is_expired() is False

    def test_is_expired_already_expired_returns_true(self):
        consent = self._make_consent(timeout_seconds=10, past_offset=60)
        consent.is_expired()  # Transitions to EXPIRED
        # Calling again still returns True
        assert consent.is_expired() is True

    def test_naive_requested_at_treated_as_expired(self):
        # Fail-closed: naive datetime → expired immediately
        consent = ConsentRequest(
            request_id=str(uuid.uuid4()),
            action_description="Naive datetime test",
            risk_level=RiskLevel.HIGH,
            token_id=FIXED_TOKEN_ID,
            requested_at=datetime(2026, 1, 1),  # Naive — no tzinfo
            timeout_seconds=300,
            status=ConsentStatus.PENDING,
        )
        assert consent.is_expired() is True
        assert consent.status == ConsentStatus.EXPIRED


# ---------------------------------------------------------------------------
# Section 7: ValidationResult + EnforcementResult constructors
# ---------------------------------------------------------------------------

class TestResultTypes:

    def test_validation_ok(self):
        r = ValidationResult.ok()
        assert r.valid is True
        assert r.error_code == ""
        assert r.error_message == ""

    def test_validation_fail(self):
        r = ValidationResult.fail(OAuth3ErrorCode.TOKEN_EXPIRED, "expired")
        assert r.valid is False
        assert r.error_code == OAuth3ErrorCode.TOKEN_EXPIRED.value
        assert r.error_message == "expired"

    def test_enforcement_permit(self):
        genesis = EvidenceBundle(
            action_id="a1",
            token_id="t1",
            agent_id="ag1",
            principal_id="p1",
            action_type="read",
            resource="r1",
            timestamp="2026-01-01T00:00:00+00:00",
            evidence_hash="a" * 64,
            previous_hash="GENESIS",
        )
        r = EnforcementResult.permit(genesis)
        assert r.allowed is True
        assert r.evidence_bundle is genesis
        assert r.error_code == ""

    def test_enforcement_deny(self):
        r = EnforcementResult.deny(OAuth3ErrorCode.TOKEN_EXPIRED)
        assert r.allowed is False
        assert r.error_code == OAuth3ErrorCode.TOKEN_EXPIRED.value
        assert r.evidence_bundle is None

    def test_enforcement_step_up(self):
        req = ConsentRequest(
            request_id="req-1",
            action_description="test",
            risk_level=RiskLevel.HIGH,
            token_id="t1",
            requested_at=_utc_now(),
        )
        r = EnforcementResult.step_up(req)
        assert r.allowed is False
        assert r.consent_required is True
        assert r.consent_request is req
        assert r.error_code == OAuth3ErrorCode.CONSENT_REQUIRED.value


# ---------------------------------------------------------------------------
# Section 8: OAuth3Enforcer.validate_token()
# ---------------------------------------------------------------------------

class TestValidateToken:

    def test_valid_token_returns_ok(self):
        enforcer = _make_enforcer()
        token = _make_token()
        result = enforcer.validate_token(token)
        assert result.valid is True

    def test_empty_token_id_returns_invalid(self):
        enforcer = _make_enforcer()
        token = _make_token(token_id="")
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.INVALID_TOKEN.value

    def test_revoked_in_registry_returns_token_revoked(self):
        registry = RevocationRegistry()
        enforcer = OAuth3Enforcer(registry=registry)
        token = _make_token()
        registry.revoke(token.token_id)
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value

    def test_advisory_revoked_flag_returns_token_revoked(self):
        enforcer = _make_enforcer()
        token = _make_token(revoked=True)
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value

    def test_expired_token_returns_token_expired(self):
        enforcer = _make_enforcer(clock_skew_seconds=0)
        token = _make_token(expires_at=_past(3600), issued_at=_past(7200))
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_EXPIRED.value

    def test_future_issued_at_returns_clock_skew_exceeded(self):
        enforcer = _make_enforcer(clock_skew_seconds=0)
        token = _make_token(issued_at=_future(600))
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.CLOCK_SKEW_EXCEEDED.value

    def test_naive_datetime_returns_invalid(self):
        enforcer = _make_enforcer()
        token = _make_token(expires_at=datetime(2030, 1, 1))  # naive
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.INVALID_TOKEN.value

    def test_empty_scope_returns_invalid(self):
        enforcer = _make_enforcer()
        token = _make_token(scope=[])
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.INVALID_TOKEN.value

    def test_registry_revocation_takes_priority_over_advisory_flag(self):
        # Even if token.revoked=False, registry says revoked → TOKEN_REVOKED
        registry = RevocationRegistry()
        enforcer = OAuth3Enforcer(registry=registry)
        token = _make_token(revoked=False)
        registry.revoke(token.token_id)
        result = enforcer.validate_token(token)
        assert result.valid is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value


# ---------------------------------------------------------------------------
# Section 9: OAuth3Enforcer.enforce_action() — core enforcement
# ---------------------------------------------------------------------------

class TestEnforceAction:

    def test_basic_allowed_action(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is True
        assert result.evidence_bundle is not None

    def test_scope_mismatch_denied(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"write": 5}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="write",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.SCOPE_MISMATCH.value

    def test_expired_token_denied(self):
        enforcer = _make_enforcer(clock_skew_seconds=0)
        token = _make_token(expires_at=_past(3600), issued_at=_past(7200))
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_EXPIRED.value

    def test_revoked_token_denied(self):
        registry = RevocationRegistry()
        enforcer = OAuth3Enforcer(registry=registry)
        token = _make_token()
        registry.revoke(token.token_id)
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value

    def test_action_limit_exhausted_denied(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 0}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.ACTION_LIMIT_EXCEEDED.value

    def test_action_limit_decremented_after_permit(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 3}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is True
        assert token.action_limits.remaining("read") == 2

    def test_dpop_required_but_absent_denied(self):
        enforcer = _make_enforcer()
        token = _make_token(dpop_thumbprint=FIXED_DPOP_THUMBPRINT)
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            dpop_thumbprint=None,
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.DPOP_INVALID.value

    def test_dpop_mismatched_denied(self):
        enforcer = _make_enforcer()
        token = _make_token(dpop_thumbprint=FIXED_DPOP_THUMBPRINT)
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            dpop_thumbprint="wrong_thumbprint_value",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.DPOP_INVALID.value

    def test_dpop_correct_thumbprint_allowed(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
            dpop_thumbprint=FIXED_DPOP_THUMBPRINT,
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            dpop_thumbprint=FIXED_DPOP_THUMBPRINT,
        )
        assert result.allowed is True

    def test_dpop_not_required_no_thumbprint_in_token_allowed(self):
        # Token has no DPoP thumbprint → DPoP binding not enforced
        enforcer = _make_enforcer()
        token = _make_token(dpop_thumbprint=None)
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            dpop_thumbprint=None,
        )
        assert result.allowed is True

    def test_high_risk_without_consent_returns_step_up(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
        )
        assert result.allowed is False
        assert result.consent_required is True
        assert result.consent_request is not None
        assert result.consent_request.status == ConsentStatus.PENDING

    def test_high_risk_with_approved_consent_allowed(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        # First call: triggers step-up
        step_up_result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
        )
        assert step_up_result.consent_required is True
        consent_req = step_up_result.consent_request
        # Principal approves
        assert consent_req.approve() is True
        # Second call with consent_request_id
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=consent_req.request_id,
        )
        assert result.allowed is True
        assert result.evidence_bundle is not None

    def test_high_risk_with_denied_consent_returns_consent_denied(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        step_up_result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
        )
        consent_req = step_up_result.consent_request
        consent_req.deny()
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=consent_req.request_id,
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.CONSENT_DENIED.value

    def test_high_risk_with_expired_consent_returns_consent_expired(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        # Use a short timeout so we can manually expire it
        step_up_result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
        )
        consent_req = step_up_result.consent_request
        # Simulate expiry by backdating requested_at
        consent_req.requested_at = _past(600)
        # is_expired() will now return True and transition status to EXPIRED
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=consent_req.request_id,
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.CONSENT_EXPIRED.value

    def test_unknown_consent_request_id_returns_invalid_token(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id="non-existent-id",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.INVALID_TOKEN.value

    def test_consent_is_one_time_use(self):
        # After approved consent is consumed, a second call should issue new step-up
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 10}),
        )
        # First HIGH risk call → step-up
        step_up_result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
        )
        consent_req = step_up_result.consent_request
        consent_req.approve()
        # Second call with approved consent → consumes consent, action permitted
        result1 = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=consent_req.request_id,
        )
        assert result1.allowed is True
        # Third call with same (now consumed) consent_request_id → INVALID_TOKEN
        result2 = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=consent_req.request_id,
        )
        assert result2.allowed is False
        assert result2.error_code == OAuth3ErrorCode.INVALID_TOKEN.value


# ---------------------------------------------------------------------------
# Section 10: Evidence chain integrity via enforcer
# ---------------------------------------------------------------------------

class TestEvidenceChainIntegrity:

    def test_first_bundle_has_genesis_previous_hash(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 10}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is True
        assert result.evidence_bundle.previous_hash == "GENESIS"

    def test_second_bundle_references_first(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 10}),
        )
        result1 = enforcer.enforce_action(
            token=token, action_type="read", resource="calendar:events"
        )
        result2 = enforcer.enforce_action(
            token=token, action_type="read", resource="calendar:events"
        )
        bundle1 = result1.evidence_bundle
        bundle2 = result2.evidence_bundle
        assert bundle2.verify_chain(bundle1) is True

    def test_three_bundle_chain_integrity(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 10}),
        )
        r1 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        r2 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        r3 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        b1 = r1.evidence_bundle
        b2 = r2.evidence_bundle
        b3 = r3.evidence_bundle
        assert b1.previous_hash == "GENESIS"
        assert b2.verify_chain(b1) is True
        assert b3.verify_chain(b2) is True

    def test_evidence_hash_is_64_hex_chars(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        result = enforcer.enforce_action(
            token=token, action_type="read", resource="calendar:events"
        )
        h = result.evidence_bundle.evidence_hash
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_tokens_have_independent_chains(self):
        enforcer = _make_enforcer()
        token_a = _make_token(
            token_id="token-A",
            scope=[OAuth3Scope(resource="r", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        token_b = _make_token(
            token_id="token-B",
            scope=[OAuth3Scope(resource="r", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        ra = enforcer.enforce_action(token=token_a, action_type="read", resource="r")
        rb = enforcer.enforce_action(token=token_b, action_type="read", resource="r")
        # Both should anchor at GENESIS independently
        assert ra.evidence_bundle.previous_hash == "GENESIS"
        assert rb.evidence_bundle.previous_hash == "GENESIS"


# ---------------------------------------------------------------------------
# Section 11: Adversarial tests
# ---------------------------------------------------------------------------

class TestAdversarialCases:

    def test_expired_consent_reuse(self):
        # Attacker tries to reuse an expired consent request.
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        step_up_result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
        )
        consent_req = step_up_result.consent_request
        # Expire the consent by backdating
        consent_req.requested_at = _past(600)
        # Attacker re-presents the expired consent
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=consent_req.request_id,
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.CONSENT_EXPIRED.value

    def test_double_spending_budget(self):
        # Attacker tries to use same action twice with budget=1
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 1}),
        )
        result1 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        assert result1.allowed is True  # Budget consumed (1 → 0)
        result2 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        assert result2.allowed is False
        assert result2.error_code == OAuth3ErrorCode.ACTION_LIMIT_EXCEEDED.value

    def test_revoke_after_allowed_action(self):
        # Revocation is permanent and synchronous: future actions denied
        registry = RevocationRegistry()
        enforcer = OAuth3Enforcer(registry=registry)
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 10}),
        )
        result1 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        assert result1.allowed is True
        # Now revoke the token
        registry.revoke(token.token_id)
        result2 = enforcer.enforce_action(token=token, action_type="read", resource="calendar:events")
        assert result2.allowed is False
        assert result2.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value

    def test_dpop_replay_attack_with_wrong_thumbprint(self):
        # Attacker presents a different DPoP key: must be denied
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
            dpop_thumbprint=FIXED_DPOP_THUMBPRINT,
        )
        attacker_thumbprint = hashlib.sha256(b"attacker-public-key").hexdigest()
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            dpop_thumbprint=attacker_thumbprint,
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.DPOP_INVALID.value

    def test_future_dated_token_rejected(self):
        # Token issued far in the future — future-dating guard
        enforcer = _make_enforcer(clock_skew_seconds=0)
        token = _make_token(issued_at=_future(3600))
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.CLOCK_SKEW_EXCEEDED.value

    def test_revoked_token_bypassing_advisory_flag(self):
        # Token has advisory revoked=False, but registry says revoked → denied
        registry = RevocationRegistry()
        enforcer = OAuth3Enforcer(registry=registry)
        token = _make_token(revoked=False)  # Advisory says OK
        registry.revoke(token.token_id)  # Registry says revoked
        result = enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value

    def test_scope_narrower_than_requested_denied(self):
        # Token has read scope but action requests write
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"write": 5}),
        )
        result = enforcer.enforce_action(
            token=token,
            action_type="write",
            resource="calendar:events",
        )
        assert result.allowed is False
        assert result.error_code == OAuth3ErrorCode.SCOPE_MISMATCH.value

    def test_budget_not_decremented_on_scope_fail(self):
        # Budget must only decrement AFTER all checks pass
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"write": 5}),
        )
        initial_budget = token.action_limits.remaining("write")
        enforcer.enforce_action(
            token=token,
            action_type="write",
            resource="calendar:events",  # Scope mismatch: calendar:events/write not in scope
        )
        # Budget should be unchanged since scope check failed first
        assert token.action_limits.remaining("write") == initial_budget

    def test_budget_not_decremented_on_dpop_fail(self):
        # Budget must only decrement AFTER all checks pass (DPoP fails before budget)
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="calendar:events", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
            dpop_thumbprint=FIXED_DPOP_THUMBPRINT,
        )
        initial_budget = token.action_limits.remaining("read")
        enforcer.enforce_action(
            token=token,
            action_type="read",
            resource="calendar:events",
            dpop_thumbprint="wrong",
        )
        assert token.action_limits.remaining("read") == initial_budget


# ---------------------------------------------------------------------------
# Section 12: All OAuth3ErrorCode enum values covered
# ---------------------------------------------------------------------------

class TestAllErrorCodesCovered:
    """
    Ensure every error code in OAuth3ErrorCode can be produced by the enforcer.
    This test class documents which scenario produces each error code.
    """

    def test_error_code_token_expired(self):
        enforcer = _make_enforcer(clock_skew_seconds=0)
        token = _make_token(expires_at=_past(3600), issued_at=_past(7200))
        r = enforcer.validate_token(token)
        assert r.error_code == OAuth3ErrorCode.TOKEN_EXPIRED.value

    def test_error_code_token_revoked(self):
        registry = RevocationRegistry()
        enforcer = OAuth3Enforcer(registry=registry)
        token = _make_token()
        registry.revoke(token.token_id)
        r = enforcer.validate_token(token)
        assert r.error_code == OAuth3ErrorCode.TOKEN_REVOKED.value

    def test_error_code_scope_mismatch(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"write": 5}),
        )
        r = enforcer.enforce_action(token=token, action_type="write", resource="r1")
        assert r.error_code == OAuth3ErrorCode.SCOPE_MISMATCH.value

    def test_error_code_action_limit_exceeded(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 0}),
        )
        r = enforcer.enforce_action(token=token, action_type="read", resource="r1")
        assert r.error_code == OAuth3ErrorCode.ACTION_LIMIT_EXCEEDED.value

    def test_error_code_consent_required(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        r = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
        )
        assert r.error_code == OAuth3ErrorCode.CONSENT_REQUIRED.value

    def test_error_code_consent_denied(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        step_up = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
        )
        step_up.consent_request.deny()
        r = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=step_up.consent_request.request_id,
        )
        assert r.error_code == OAuth3ErrorCode.CONSENT_DENIED.value

    def test_error_code_consent_expired(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        step_up = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
        )
        step_up.consent_request.requested_at = _past(600)
        r = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=step_up.consent_request.request_id,
        )
        assert r.error_code == OAuth3ErrorCode.CONSENT_EXPIRED.value

    def test_error_code_dpop_invalid(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
            dpop_thumbprint=FIXED_DPOP_THUMBPRINT,
        )
        r = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            dpop_thumbprint=None,
        )
        assert r.error_code == OAuth3ErrorCode.DPOP_INVALID.value

    def test_error_code_clock_skew_exceeded(self):
        enforcer = _make_enforcer(clock_skew_seconds=0)
        token = _make_token(issued_at=_future(600))
        r = enforcer.validate_token(token)
        assert r.error_code == OAuth3ErrorCode.CLOCK_SKEW_EXCEEDED.value

    def test_error_code_invalid_token_empty_id(self):
        enforcer = _make_enforcer()
        token = _make_token(token_id="")
        r = enforcer.validate_token(token)
        assert r.error_code == OAuth3ErrorCode.INVALID_TOKEN.value

    def test_all_error_codes_have_test_coverage(self):
        # Enumerate all error codes and verify each has a string value
        all_codes = set(e.value for e in OAuth3ErrorCode)
        expected = {
            "TOKEN_EXPIRED", "TOKEN_REVOKED", "SCOPE_MISMATCH",
            "ACTION_LIMIT_EXCEEDED", "CONSENT_REQUIRED", "CONSENT_DENIED",
            "CONSENT_EXPIRED", "DPOP_INVALID", "CLOCK_SKEW_EXCEEDED", "INVALID_TOKEN",
        }
        assert all_codes == expected


# ---------------------------------------------------------------------------
# Section 13: get_consent_request API
# ---------------------------------------------------------------------------

class TestGetConsentRequest:

    def test_get_consent_request_returns_stored_request(self):
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        step_up = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
        )
        req_id = step_up.consent_request.request_id
        fetched = enforcer.get_consent_request(req_id)
        assert fetched is not None
        assert fetched.request_id == req_id

    def test_get_consent_request_unknown_id_returns_none(self):
        enforcer = _make_enforcer()
        result = enforcer.get_consent_request("not-a-real-id")
        assert result is None

    def test_consent_consumed_after_approval(self):
        # After approved consent is consumed in enforce_action, it's removed from registry
        enforcer = _make_enforcer()
        token = _make_token(
            scope=[OAuth3Scope(resource="r1", permission="read")],
            action_limits=ActionLimits(limits={"read": 5}),
        )
        step_up = enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
        )
        req_id = step_up.consent_request.request_id
        step_up.consent_request.approve()
        enforcer.enforce_action(
            token=token, action_type="read", resource="r1",
            risk_level=RiskLevel.HIGH.value,
            consent_request_id=req_id,
        )
        # After consumption, get_consent_request should return None
        assert enforcer.get_consent_request(req_id) is None


# ---------------------------------------------------------------------------
# Section 14: request_consent API
# ---------------------------------------------------------------------------

class TestRequestConsent:

    def test_request_consent_creates_pending_request(self):
        enforcer = _make_enforcer()
        token = _make_token()
        req = enforcer.request_consent(
            token=token,
            action_description="Urgent: delete all files",
        )
        assert req.status == ConsentStatus.PENDING
        assert req.risk_level == RiskLevel.HIGH
        assert req.token_id == token.token_id

    def test_request_consent_stored_in_registry(self):
        enforcer = _make_enforcer()
        token = _make_token()
        req = enforcer.request_consent(token=token, action_description="Test action")
        fetched = enforcer.get_consent_request(req.request_id)
        assert fetched is req

    def test_request_consent_custom_timeout(self):
        enforcer = _make_enforcer()
        token = _make_token()
        req = enforcer.request_consent(
            token=token,
            action_description="Short timeout",
            timeout_seconds=60,
        )
        assert req.timeout_seconds == 60
