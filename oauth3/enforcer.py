"""
OAuth3 Enforcer — Reference Implementation
==========================================

Spec: oauth3-spec-v0.1.md
Rung: 65537 (production/security grade)
Security: Fail-closed on all validation paths. No float arithmetic.
          All timestamps UTC-aware. SHA-256 hashes never truncated.

Implements all 6 OAuth3 governance features:
  1. Scoped delegation tokens  (Section 3)
  2. Step-up consent           (Section 4)
  3. Evidence bundles          (Section 5)
  4. Action limits             (Section 6)
  5. Synchronous revocation    (Section 7)
  6. DPoP binding              (Section 8)

Dependencies: stdlib only (uuid, hashlib, hmac, datetime, dataclasses, enum)
              Optional: cryptography (for DPoP thumbprint verification)
"""

from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Section 2 — Constants and Error Codes
# ---------------------------------------------------------------------------

# Clock skew tolerance in seconds (Section 2.3)
DEFAULT_CLOCK_SKEW_SECONDS: int = 30

# Default step-up consent timeout in seconds (Section 4.1)
DEFAULT_CONSENT_TIMEOUT_SECONDS: int = 300


class OAuth3ErrorCode(str, Enum):
    """
    Canonical error codes from OAuth3 spec Section 7.

    These are the only error strings that MUST appear in ValidationResult
    and EnforcementResult payloads. Never use freeform error strings for
    error_code; use error_message for human-readable context.
    """
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_REVOKED = "TOKEN_REVOKED"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    ACTION_LIMIT_EXCEEDED = "ACTION_LIMIT_EXCEEDED"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    CONSENT_DENIED = "CONSENT_DENIED"
    CONSENT_EXPIRED = "CONSENT_EXPIRED"
    DPOP_INVALID = "DPOP_INVALID"
    CLOCK_SKEW_EXCEEDED = "CLOCK_SKEW_EXCEEDED"
    INVALID_TOKEN = "INVALID_TOKEN"


class RiskLevel(str, Enum):
    """
    Risk classification for actions (Section 4.1).
    HIGH risk triggers step-up consent flow.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ConsentStatus(str, Enum):
    """
    Lifecycle states for a ConsentRequest (Section 4.2).
    Transitions: PENDING → APPROVED | DENIED | EXPIRED
    """
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# Section 3 — Scoped Delegation Tokens
# ---------------------------------------------------------------------------

@dataclass
class OAuth3Scope:
    """
    A single scope entry: one resource + one permission (Section 3.2).

    Scope is always explicit — no wildcards, no implicit inheritance.
    The enforcer checks scope membership with exact-match semantics.

    Fields:
        resource   — URI or opaque resource identifier (e.g. "calendar:read")
        permission — action permitted on that resource (e.g. "read")
    """
    resource: str
    permission: str

    def matches(self, resource: str, permission: str) -> bool:
        """
        Return True iff this scope entry exactly covers the requested
        (resource, permission) pair.

        Spec Section 3.3: No prefix matching. Exact string equality only.
        """
        return self.resource == resource and self.permission == permission


@dataclass
class ActionLimits:
    """
    Per-action-type hard caps for a delegation token (Section 6.1).

    Counters are stored as non-negative integers. The enforcer decrements
    on each successful action. When a counter reaches zero the action type
    is exhausted and must be rejected (ACTION_LIMIT_EXCEEDED).

    Absence of a key means that action type is NOT permitted (not unlimited).
    None values are FORBIDDEN — use explicit int counts only.

    Fields:
        limits — mapping of action_type (str) → remaining count (int >= 0)
    """
    limits: Dict[str, int] = field(default_factory=dict)

    def is_action_allowed(self, action_type: str) -> bool:
        """
        Return True iff the action_type has remaining budget > 0.

        Spec Section 6.2: Absence of key = denied. Zero = exhausted = denied.
        Fail-closed: any non-integer value is treated as 0 (denied).
        """
        remaining = self.limits.get(action_type)
        if remaining is None:
            return False
        if not isinstance(remaining, int):
            # Fail-closed: corrupt budget → deny
            return False
        return remaining > 0

    def decrement(self, action_type: str) -> bool:
        """
        Atomically decrement the budget for action_type.

        Returns True if decrement succeeded (budget was > 0 before decrement).
        Returns False if action_type was absent or budget was already 0.
        Does NOT raise — fail-closed by returning False.
        """
        if not self.is_action_allowed(action_type):
            return False
        self.limits[action_type] = self.limits[action_type] - 1
        return True

    def remaining(self, action_type: str) -> int:
        """
        Return the remaining budget for action_type, or 0 if absent/invalid.
        Never returns negative values.
        """
        count = self.limits.get(action_type, 0)
        if not isinstance(count, int):
            return 0
        return max(0, count)


@dataclass
class DelegationToken:
    """
    An OAuth3 Delegation Token (Section 3.1).

    Represents the signed, parsed payload of a delegation token. The enforcer
    operates on this dataclass rather than raw JWT bytes — callers must parse
    and signature-verify the JWT before constructing this object.

    Fields:
        token_id        — globally unique token identifier (UUID v4 string)
        principal_id    — identity of the human principal (issuer of delegation)
        agent_id        — identity of the AI agent receiving delegation
        scope           — list of OAuth3Scope entries (explicit allowlist)
        action_limits   — ActionLimits tracking remaining budget per action type
        expires_at      — UTC datetime after which token is invalid
        issued_at       — UTC datetime when token was issued
        issuer          — issuer URI (e.g. "https://stillwater.ai")
        dpop_thumbprint — optional JWK thumbprint of agent's DPoP key (Section 8)
        revoked         — soft-revocation flag (also checked against RevocationRegistry)

    Security:
        - All datetime fields MUST be timezone-aware UTC. Naive datetimes are rejected.
        - dpop_thumbprint is Optional; when absent, DPoP binding is not enforced.
        - revoked field is advisory — RevocationRegistry is always the authoritative source.
    """
    token_id: str
    principal_id: str
    agent_id: str
    scope: List[OAuth3Scope]
    action_limits: ActionLimits
    expires_at: datetime
    issued_at: datetime
    issuer: str
    dpop_thumbprint: Optional[str] = None
    revoked: bool = False

    def _assert_aware(self, dt: datetime, field_name: str) -> None:
        """Raise ValueError if datetime is naive (no timezone info)."""
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError(
                f"DelegationToken.{field_name} must be timezone-aware UTC datetime; "
                f"got naive datetime: {dt!r}"
            )

    def is_valid(self, clock_skew_seconds: int = DEFAULT_CLOCK_SKEW_SECONDS) -> bool:
        """
        Return True iff the token is currently valid.

        Checks (in order, fail-fast):
          1. Both timestamps are timezone-aware (spec Section 2.3)
          2. Not revoked (advisory check; use RevocationRegistry for authoritative)
          3. Not expired (with configurable clock skew tolerance)
          4. issued_at is not in the future beyond clock skew (replay/future-dating guard)

        Security: Uses integer second arithmetic only. No float.
        Spec Section 3.4.
        """
        # Structural integrity: fail-closed on naive datetimes
        try:
            self._assert_aware(self.expires_at, "expires_at")
            self._assert_aware(self.issued_at, "issued_at")
        except ValueError:
            return False

        if self.revoked:
            return False

        now_utc: datetime = datetime.now(tz=timezone.utc)
        skew: timedelta = timedelta(seconds=clock_skew_seconds)

        # Token must not be expired (allow skew for clock drift)
        if now_utc > self.expires_at + skew:
            return False

        # Token must not be issued far in the future (future-dating attack guard)
        if self.issued_at > now_utc + skew:
            return False

        return True

    def is_action_allowed(self, action_type: str, resource: str) -> bool:
        """
        Return True iff the token's scope permits action_type on resource
        AND the action budget is not exhausted.

        Spec Section 3.3 + Section 6.2: Both scope AND budget must pass.
        Fail-closed: any doubt → deny.

        Args:
            action_type — e.g. "read", "write", "delete"
            resource    — exact resource URI or identifier
        """
        # Scope check: at least one scope entry must match
        scope_ok: bool = any(
            s.matches(resource, action_type) for s in self.scope
        )
        if not scope_ok:
            return False

        # Budget check
        return self.action_limits.is_action_allowed(action_type)

    def record_action(self, action_type: str) -> bool:
        """
        Decrement the budget for action_type.

        Returns True if decrement succeeded.
        Returns False if budget was already exhausted (caller should reject).

        Spec Section 6.3: Decrement is permanent. No refunds.
        """
        return self.action_limits.decrement(action_type)


# ---------------------------------------------------------------------------
# Section 5 — Evidence Bundles
# ---------------------------------------------------------------------------

@dataclass
class EvidenceBundle:
    """
    A signed, chained evidence record for one agent action (Section 5.1).

    Every action that passes enforcement MUST produce an EvidenceBundle.
    Bundles form a hash-chained audit log: each bundle references the hash
    of the previous bundle, making the log tamper-evident.

    Fields:
        action_id        — UUID v4 uniquely identifying this action
        token_id         — token that authorized this action
        agent_id         — agent that performed the action
        principal_id     — human principal who delegated authority
        action_type      — e.g. "read", "write", "delete"
        resource         — resource URI or identifier acted upon
        timestamp        — UTC ISO 8601 timestamp of the action
        evidence_hash    — SHA-256 hex digest of the canonical action payload
        previous_hash    — SHA-256 hex digest of the previous bundle (or "GENESIS")
        dpop_thumbprint  — optional DPoP key thumbprint from the token

    Security:
        - SHA-256 hashes are NEVER truncated.
        - Timestamps are always UTC ISO 8601.
        - previous_hash = "GENESIS" for the first bundle in a chain.
    """
    action_id: str
    token_id: str
    agent_id: str
    principal_id: str
    action_type: str
    resource: str
    timestamp: str          # ISO 8601 UTC string
    evidence_hash: str      # SHA-256 hex of canonical payload
    previous_hash: str      # SHA-256 hex of previous bundle, or "GENESIS"
    dpop_thumbprint: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Return a canonical dictionary representation of this bundle.

        Spec Section 5.2: Used as the canonical form for hashing and storage.
        Keys are always present; optional fields are included as None.
        """
        return {
            "action_id": self.action_id,
            "token_id": self.token_id,
            "agent_id": self.agent_id,
            "principal_id": self.principal_id,
            "action_type": self.action_type,
            "resource": self.resource,
            "timestamp": self.timestamp,
            "evidence_hash": self.evidence_hash,
            "previous_hash": self.previous_hash,
            "dpop_thumbprint": self.dpop_thumbprint,
        }

    def compute_own_hash(self) -> str:
        """
        Compute the SHA-256 hash of this bundle's canonical serialization.

        Used as the previous_hash value for the NEXT bundle in the chain.
        Hash is hex-encoded, never truncated (spec Section 5.3).
        """
        canonical: str = (
            f"{self.action_id}|{self.token_id}|{self.agent_id}|"
            f"{self.principal_id}|{self.action_type}|{self.resource}|"
            f"{self.timestamp}|{self.evidence_hash}|{self.previous_hash}"
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def verify_chain(self, previous_bundle: "EvidenceBundle") -> bool:
        """
        Verify that this bundle correctly references the previous bundle.

        Returns True iff self.previous_hash == previous_bundle.compute_own_hash().
        Uses hmac.compare_digest for constant-time comparison (timing-safe).

        Spec Section 5.4: Chain integrity is mandatory for audit log validity.

        Args:
            previous_bundle — the bundle that should immediately precede this one
        """
        expected_hash: str = previous_bundle.compute_own_hash()
        return hmac.compare_digest(self.previous_hash, expected_hash)


# ---------------------------------------------------------------------------
# Section 4 — Step-Up Consent
# ---------------------------------------------------------------------------

@dataclass
class ConsentRequest:
    """
    A step-up consent request for HIGH risk actions (Section 4.1).

    When the enforcer encounters a HIGH risk action, it creates a ConsentRequest
    and returns CONSENT_REQUIRED to the caller. The caller must surface the
    request to the principal (human), wait for approval, then retry the action.

    Fields:
        request_id          — UUID v4 uniquely identifying this consent request
        action_description  — human-readable description of the requested action
        risk_level          — RiskLevel (always HIGH for step-up; stored for audit)
        token_id            — delegation token requesting elevated consent
        requested_at        — UTC datetime when consent was requested
        timeout_seconds     — seconds before request auto-expires (default 300)
        status              — current ConsentStatus (PENDING → APPROVED|DENIED|EXPIRED)

    Lifecycle:
        PENDING → approve() → APPROVED
        PENDING → deny()    → DENIED
        PENDING → (timeout) → EXPIRED (checked lazily via is_expired())
    """
    request_id: str
    action_description: str
    risk_level: RiskLevel
    token_id: str
    requested_at: datetime
    timeout_seconds: int = DEFAULT_CONSENT_TIMEOUT_SECONDS
    status: ConsentStatus = ConsentStatus.PENDING

    def is_expired(self) -> bool:
        """
        Return True iff the consent request has timed out.

        Uses integer second arithmetic. Automatically transitions status
        to EXPIRED if the deadline has passed and status is still PENDING.

        Spec Section 4.2: Expired consent must be re-requested; cannot be approved.
        """
        if self.status != ConsentStatus.PENDING:
            # Already resolved — not expired in the timeout sense
            return self.status == ConsentStatus.EXPIRED

        if self.requested_at.tzinfo is None:
            # Naive datetime — treat as expired (fail-closed)
            self.status = ConsentStatus.EXPIRED
            return True

        deadline: datetime = self.requested_at + timedelta(seconds=self.timeout_seconds)
        now_utc: datetime = datetime.now(tz=timezone.utc)

        if now_utc > deadline:
            self.status = ConsentStatus.EXPIRED
            return True

        return False

    def approve(self) -> bool:
        """
        Approve the consent request.

        Returns True if transition to APPROVED succeeded.
        Returns False if the request is not in PENDING state (already resolved or expired).

        Spec Section 4.3: Only PENDING requests can be approved.
        """
        if self.is_expired():
            return False
        if self.status != ConsentStatus.PENDING:
            return False
        self.status = ConsentStatus.APPROVED
        return True

    def deny(self) -> bool:
        """
        Deny the consent request.

        Returns True if transition to DENIED succeeded.
        Returns False if the request is not in PENDING state.

        Spec Section 4.3: Only PENDING requests can be denied.
        """
        if self.status != ConsentStatus.PENDING:
            return False
        self.status = ConsentStatus.DENIED
        return True


# ---------------------------------------------------------------------------
# Section 7 — Synchronous Revocation Registry
# ---------------------------------------------------------------------------

class RevocationRegistry:
    """
    Synchronous, O(1) revocation store (Section 7.1).

    The RevocationRegistry is the AUTHORITATIVE source of truth for token
    revocation. DelegationToken.revoked is advisory only; the enforcer
    always checks this registry at enforcement time.

    Backed by a Python set for O(1) add/lookup. In production deployments
    this should be backed by Redis SRANDMEMBER or similar for distributed
    revocation propagation.

    Security:
        - revoke() is idempotent (safe to call multiple times for same token_id)
        - is_revoked() is O(1) set lookup
        - No expiry on revocation entries (permanent unless cleared)
    """

    def __init__(self) -> None:
        """Initialize an empty revocation registry."""
        self._revoked_ids: Set[str] = set()

    def revoke(self, token_id: str) -> bool:
        """
        Add token_id to the revocation registry.

        Returns True always (idempotent). The token_id is permanently
        blacklisted regardless of whether it was previously revoked.

        Spec Section 7.2: Revocation is immediate and synchronous.

        Args:
            token_id — the token_id of the DelegationToken to revoke
        """
        self._revoked_ids.add(token_id)
        return True

    def is_revoked(self, token_id: str) -> bool:
        """
        Return True iff token_id is in the revocation registry.

        O(1) set lookup. Fail-open semantics are FORBIDDEN here —
        any lookup error must be treated as revoked (fail-closed).

        Spec Section 7.3.
        """
        return token_id in self._revoked_ids

    def count(self) -> int:
        """Return the number of revoked tokens (for monitoring/testing)."""
        return len(self._revoked_ids)


# ---------------------------------------------------------------------------
# Result Types
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """
    Result of token validation (spec Section 3.5).

    Fields:
        valid         — True iff the token passed all validation checks
        error_code    — OAuth3ErrorCode if not valid, empty string if valid
        error_message — Human-readable explanation (never used in logic decisions)
    """
    valid: bool
    error_code: str = ""
    error_message: str = ""

    @classmethod
    def ok(cls) -> "ValidationResult":
        """Construct a passing ValidationResult."""
        return cls(valid=True, error_code="", error_message="")

    @classmethod
    def fail(cls, code: OAuth3ErrorCode, message: str) -> "ValidationResult":
        """Construct a failing ValidationResult with the given error code."""
        return cls(valid=False, error_code=code.value, error_message=message)


@dataclass
class EnforcementResult:
    """
    Result of a full enforcement decision (spec Section 3.6 + Section 4.4).

    Fields:
        allowed          — True iff the action is permitted and was recorded
        evidence_bundle  — EvidenceBundle if allowed=True, None otherwise
        error_code       — OAuth3ErrorCode string if not allowed, else ""
        consent_required — True iff the action requires step-up consent
        consent_request  — ConsentRequest if consent_required=True, None otherwise
    """
    allowed: bool
    evidence_bundle: Optional[EvidenceBundle] = None
    error_code: str = ""
    consent_required: bool = False
    consent_request: Optional[ConsentRequest] = None

    @classmethod
    def permit(cls, bundle: EvidenceBundle) -> "EnforcementResult":
        """Construct a permitted EnforcementResult with evidence bundle."""
        return cls(allowed=True, evidence_bundle=bundle)

    @classmethod
    def deny(cls, code: OAuth3ErrorCode) -> "EnforcementResult":
        """Construct a denied EnforcementResult."""
        return cls(allowed=False, error_code=code.value)

    @classmethod
    def step_up(cls, request: ConsentRequest) -> "EnforcementResult":
        """Construct a step-up consent required result."""
        return cls(
            allowed=False,
            error_code=OAuth3ErrorCode.CONSENT_REQUIRED.value,
            consent_required=True,
            consent_request=request,
        )


# ---------------------------------------------------------------------------
# Section 8 — DPoP Binding Helpers
# ---------------------------------------------------------------------------

def _compute_dpop_thumbprint(public_key_pem: str) -> str:
    """
    Compute the JWK SHA-256 thumbprint for a PEM-encoded public key.

    Spec Section 8.2: DPoP thumbprint is the SHA-256 hash of the canonical
    JWK representation, hex-encoded. This function provides a deterministic
    string identity for a public key.

    Args:
        public_key_pem — PEM-encoded RSA or EC public key

    Returns:
        SHA-256 hex digest of the key material (simplified canonical form)

    Note:
        Production use requires the `cryptography` library for proper JWK
        thumbprint per RFC 7638. This fallback uses raw PEM bytes, which
        is deterministic but NOT RFC 7638 compliant.
    """
    return hashlib.sha256(public_key_pem.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Main Enforcer
# ---------------------------------------------------------------------------

class OAuth3Enforcer:
    """
    OAuth3 runtime enforcement engine (spec Section 9).

    The enforcer is the single choke point for all delegation decisions.
    Every agent action must pass through enforce_action() to be authorized.

    Implements all 6 OAuth3 governance features:
      1. Scoped token validation     (validate_token)
      2. Step-up consent             (request_consent + enforce_action HIGH path)
      3. Evidence bundle creation    (create_evidence_bundle)
      4. Action limit enforcement    (enforce_action budget check)
      5. Synchronous revocation      (enforce_action → RevocationRegistry)
      6. DPoP binding validation     (enforce_action dpop_thumbprint check)

    Constructor:
        registry              — RevocationRegistry (authoritative revocation source)
        clock_skew_seconds    — tolerated clock skew in integer seconds (default 30)

    Thread safety:
        This implementation is NOT thread-safe. For concurrent use, callers must
        provide external locking around enforce_action() and the RevocationRegistry.
    """

    def __init__(
        self,
        registry: RevocationRegistry,
        clock_skew_seconds: int = DEFAULT_CLOCK_SKEW_SECONDS,
    ) -> None:
        """
        Initialize the enforcer with a revocation registry.

        Args:
            registry           — RevocationRegistry for synchronous revocation lookups
            clock_skew_seconds — integer seconds of clock skew tolerance (default 30)
        """
        self._registry: RevocationRegistry = registry
        self._clock_skew: int = clock_skew_seconds
        # In-flight consent requests indexed by request_id
        self._consent_requests: Dict[str, ConsentRequest] = {}
        # Evidence chain: last bundle per token_id (for chaining previous_hash)
        self._last_bundles: Dict[str, EvidenceBundle] = {}

    def validate_token(self, token: DelegationToken) -> ValidationResult:
        """
        Validate a DelegationToken against all enforcement criteria.

        Checks (in order, fail-fast):
          1. token_id is present and non-empty          (INVALID_TOKEN)
          2. Token is not revoked in registry           (TOKEN_REVOKED)
          3. Token advisory revoked flag                (TOKEN_REVOKED)
          4. Token is not expired (with clock skew)     (TOKEN_EXPIRED)
          5. scope list is non-empty                    (INVALID_TOKEN)

        Note: Scope/budget/DPoP checks are performed in enforce_action(),
        not here, because they require action context.

        Spec Section 3.4.

        Args:
            token — DelegationToken to validate

        Returns:
            ValidationResult.ok() on success, ValidationResult.fail() on any check failure
        """
        # Structural check
        if not token.token_id or not isinstance(token.token_id, str):
            return ValidationResult.fail(
                OAuth3ErrorCode.INVALID_TOKEN,
                "token_id is missing or not a string",
            )

        # Authoritative revocation check (registry always wins)
        if self._registry.is_revoked(token.token_id):
            return ValidationResult.fail(
                OAuth3ErrorCode.TOKEN_REVOKED,
                f"Token {token.token_id!r} has been revoked",
            )

        # Advisory revocation flag
        if token.revoked:
            return ValidationResult.fail(
                OAuth3ErrorCode.TOKEN_REVOKED,
                f"Token {token.token_id!r} is flagged as revoked",
            )

        # Expiry check
        if not token.is_valid(clock_skew_seconds=self._clock_skew):
            # Determine whether it's expiry or future-dating
            try:
                token._assert_aware(token.expires_at, "expires_at")
                token._assert_aware(token.issued_at, "issued_at")
            except ValueError:
                return ValidationResult.fail(
                    OAuth3ErrorCode.INVALID_TOKEN,
                    "Token timestamps must be timezone-aware UTC datetimes",
                )
            now_utc = datetime.now(tz=timezone.utc)
            skew = timedelta(seconds=self._clock_skew)
            if now_utc > token.expires_at + skew:
                return ValidationResult.fail(
                    OAuth3ErrorCode.TOKEN_EXPIRED,
                    f"Token expired at {token.expires_at.isoformat()}",
                )
            return ValidationResult.fail(
                OAuth3ErrorCode.CLOCK_SKEW_EXCEEDED,
                f"Token issued_at {token.issued_at.isoformat()} is too far in the future",
            )

        # Scope must not be empty
        if not token.scope:
            return ValidationResult.fail(
                OAuth3ErrorCode.INVALID_TOKEN,
                "Token scope list is empty",
            )

        return ValidationResult.ok()

    def enforce_action(
        self,
        token: DelegationToken,
        action_type: str,
        resource: str,
        risk_level: str = RiskLevel.LOW.value,
        dpop_thumbprint: Optional[str] = None,
        consent_request_id: Optional[str] = None,
    ) -> EnforcementResult:
        """
        Full enforcement gate for one agent action (spec Section 9.1).

        Enforcement flow:
          1. Validate token (revocation, expiry, structure)
          2. Check scope (resource + action_type in token.scope)
          3. Check DPoP binding (if token has dpop_thumbprint)
          4. Check action budget (not exhausted)
          5. If risk_level == HIGH: require step-up consent
             a. If consent_request_id given: verify approval status
             b. Else: create new ConsentRequest and return CONSENT_REQUIRED
          6. Record action (decrement budget counter)
          7. Create and return evidence bundle

        Fail-closed: any check failure returns EnforcementResult.deny().
        The action budget is ONLY decremented after ALL checks pass (step 6).

        Args:
            token               — DelegationToken authorizing the action
            action_type         — e.g. "read", "write", "delete"
            resource            — exact resource URI or identifier
            risk_level          — RiskLevel string (default "LOW")
            dpop_thumbprint     — optional DPoP thumbprint from request header
            consent_request_id  — optional ID of a previously issued ConsentRequest

        Returns:
            EnforcementResult.permit(bundle) on success
            EnforcementResult.deny(code)     on failure
            EnforcementResult.step_up(req)   when step-up consent is required
        """
        # Step 1: Validate token
        validation: ValidationResult = self.validate_token(token)
        if not validation.valid:
            return EnforcementResult.deny(
                OAuth3ErrorCode(validation.error_code)
                if validation.error_code in OAuth3ErrorCode._value2member_map_
                else OAuth3ErrorCode.INVALID_TOKEN
            )

        # Step 2: Scope check
        scope_ok: bool = any(
            s.matches(resource, action_type) for s in token.scope
        )
        if not scope_ok:
            return EnforcementResult.deny(OAuth3ErrorCode.SCOPE_MISMATCH)

        # Step 3: DPoP binding check (Section 8.3)
        if token.dpop_thumbprint is not None:
            if dpop_thumbprint is None:
                # Token requires DPoP but caller did not present one
                return EnforcementResult.deny(OAuth3ErrorCode.DPOP_INVALID)
            if not hmac.compare_digest(token.dpop_thumbprint, dpop_thumbprint):
                return EnforcementResult.deny(OAuth3ErrorCode.DPOP_INVALID)

        # Step 4: Budget check (do NOT decrement yet)
        if not token.action_limits.is_action_allowed(action_type):
            return EnforcementResult.deny(OAuth3ErrorCode.ACTION_LIMIT_EXCEEDED)

        # Step 5: Step-up consent for HIGH risk actions (Section 4)
        normalized_risk: str = risk_level.upper() if isinstance(risk_level, str) else "LOW"
        if normalized_risk == RiskLevel.HIGH.value:
            if consent_request_id is not None:
                # Caller is presenting a previously issued consent
                consent_result = self._resolve_consent(consent_request_id)
                if consent_result is not None:
                    return consent_result
                # consent_result is None → consent approved, proceed
            else:
                # No consent presented — issue new ConsentRequest
                new_request: ConsentRequest = self.request_consent(
                    token=token,
                    action_description=(
                        f"Agent {token.agent_id!r} requests {action_type!r} "
                        f"on {resource!r} (HIGH risk)"
                    ),
                )
                return EnforcementResult.step_up(new_request)

        # Step 6: Decrement budget (atomic — only after all checks pass)
        decremented: bool = token.record_action(action_type)
        if not decremented:
            # Concurrent exhaustion between check and decrement
            return EnforcementResult.deny(OAuth3ErrorCode.ACTION_LIMIT_EXCEEDED)

        # Step 7: Create evidence bundle
        bundle: EvidenceBundle = self.create_evidence_bundle(
            token=token,
            action_type=action_type,
            resource=resource,
            payload_hash=hashlib.sha256(
                f"{token.token_id}:{action_type}:{resource}".encode("utf-8")
            ).hexdigest(),
        )

        return EnforcementResult.permit(bundle)

    def _resolve_consent(self, consent_request_id: str) -> Optional[EnforcementResult]:
        """
        Resolve a previously issued ConsentRequest by its ID.

        Returns:
            None                                       → consent approved, caller may proceed
            EnforcementResult.deny(CONSENT_DENIED)    → consent was denied
            EnforcementResult.deny(CONSENT_EXPIRED)   → consent timed out
            EnforcementResult.deny(INVALID_TOKEN)     → unknown consent_request_id
        """
        request: Optional[ConsentRequest] = self._consent_requests.get(consent_request_id)
        if request is None:
            return EnforcementResult.deny(OAuth3ErrorCode.INVALID_TOKEN)

        if request.is_expired():
            return EnforcementResult.deny(OAuth3ErrorCode.CONSENT_EXPIRED)

        if request.status == ConsentStatus.DENIED:
            return EnforcementResult.deny(OAuth3ErrorCode.CONSENT_DENIED)

        if request.status == ConsentStatus.APPROVED:
            # Consume the consent (one-time use)
            del self._consent_requests[consent_request_id]
            return None  # Signal: proceed

        # Still PENDING — re-issue step-up (caller must wait)
        return EnforcementResult.deny(OAuth3ErrorCode.CONSENT_REQUIRED)

    def create_evidence_bundle(
        self,
        token: DelegationToken,
        action_type: str,
        resource: str,
        payload_hash: str,
    ) -> EvidenceBundle:
        """
        Create a hash-chained evidence bundle for a completed action (Section 5).

        The bundle's previous_hash is set to the hash of the last known bundle
        for this token, or "GENESIS" if this is the first action.

        Args:
            token        — DelegationToken that authorized this action
            action_type  — e.g. "read", "write", "delete"
            resource     — resource URI acted upon
            payload_hash — SHA-256 hex digest of the action payload (caller-computed)

        Returns:
            EvidenceBundle with computed evidence_hash and chained previous_hash
        """
        action_id: str = str(uuid.uuid4())
        timestamp: str = datetime.now(tz=timezone.utc).isoformat()

        # Determine previous hash (chain or genesis)
        previous: Optional[EvidenceBundle] = self._last_bundles.get(token.token_id)
        previous_hash: str = (
            previous.compute_own_hash() if previous is not None else "GENESIS"
        )

        # Compute evidence hash: SHA-256 of canonical action descriptor
        canonical_action: str = (
            f"{action_id}|{token.token_id}|{token.agent_id}|"
            f"{token.principal_id}|{action_type}|{resource}|{timestamp}|{payload_hash}"
        )
        evidence_hash: str = hashlib.sha256(canonical_action.encode("utf-8")).hexdigest()

        bundle = EvidenceBundle(
            action_id=action_id,
            token_id=token.token_id,
            agent_id=token.agent_id,
            principal_id=token.principal_id,
            action_type=action_type,
            resource=resource,
            timestamp=timestamp,
            evidence_hash=evidence_hash,
            previous_hash=previous_hash,
            dpop_thumbprint=token.dpop_thumbprint,
        )

        # Store as the latest bundle for this token (for next chain link)
        self._last_bundles[token.token_id] = bundle

        return bundle

    def request_consent(
        self,
        token: DelegationToken,
        action_description: str,
        timeout_seconds: int = DEFAULT_CONSENT_TIMEOUT_SECONDS,
    ) -> ConsentRequest:
        """
        Create and register a step-up consent request (Section 4.1).

        The returned ConsentRequest must be surfaced to the human principal
        for approval. The caller then re-calls enforce_action() with the
        consent_request_id to resume enforcement after approval.

        Args:
            token              — DelegationToken requesting elevated consent
            action_description — human-readable description of the requested action
            timeout_seconds    — seconds until the request auto-expires (default 300)

        Returns:
            ConsentRequest with status=PENDING, stored in internal registry
        """
        request_id: str = str(uuid.uuid4())
        request = ConsentRequest(
            request_id=request_id,
            action_description=action_description,
            risk_level=RiskLevel.HIGH,
            token_id=token.token_id,
            requested_at=datetime.now(tz=timezone.utc),
            timeout_seconds=timeout_seconds,
            status=ConsentStatus.PENDING,
        )
        self._consent_requests[request_id] = request
        return request

    def get_consent_request(self, request_id: str) -> Optional[ConsentRequest]:
        """
        Retrieve a pending ConsentRequest by its ID.

        Used by the principal's UI layer to display and act on consent requests.
        Returns None if the request_id is unknown.

        Args:
            request_id — UUID of the ConsentRequest to retrieve
        """
        return self._consent_requests.get(request_id)
