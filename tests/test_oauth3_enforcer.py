"""
tests/test_oauth3_enforcer.py

Unit tests for skills/oauth3-enforcer.md gate logic.
Tests the four OAuth3 validation gates (G1-G4) and audit JSON output.

Rung target: 641 (local correctness)
Spec ref: papers/oauth3-spec-v0.1.md (Section 1.4, Section 5)

Tests:
    T1:  G1 PASS — valid token (all required fields present)
    T2:  G1 FAIL — null token (OAUTH3_MISSING_TOKEN)
    T3:  G1 FAIL — missing required field (OAUTH3_MALFORMED_TOKEN)
    T4:  G1 FAIL — malformed scope pattern (OAUTH3_MALFORMED_TOKEN)
    T5:  G1 FAIL — empty scopes array (OAUTH3_MALFORMED_TOKEN)
    T6:  G2 PASS — token not expired
    T7:  G2 FAIL — token expired (OAUTH3_TOKEN_EXPIRED)
    T8:  G3 PASS — scope granted
    T9:  G3 FAIL — scope not in granted list (OAUTH3_SCOPE_DENIED)
    T10: G3 FAIL — step-up required (OAUTH3_STEP_UP_REQUIRED)
    T11: G4 PASS — token not revoked
    T12: G4 FAIL — token revoked (OAUTH3_TOKEN_REVOKED)
    T13: G4 FAIL — revocation registry unavailable (OAUTH3_REVOCATION_UNAVAILABLE)
    T13b: G4 FAIL — revocation registry raises exception (OAUTH3_REVOCATION_CHECK_FAILED)
    T14: Full gate run PASS — all 4 gates clear, audit JSON well-formed
    T15: Full gate run BLOCKED — gate failure stops at first failed gate

Run: pytest tests/test_oauth3_enforcer.py -v
"""

import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional


# ============================================================
# Reference implementation of gate logic
# (mirrors pseudocode in skills/oauth3-enforcer.md)
# ============================================================

class GateResult:
    def __init__(
        self,
        gate: str,
        passed: bool,
        error_code: Optional[str] = None,
        error_detail: Optional[str] = None,
        status: Optional[str] = None,
    ):
        self.gate = gate
        self.passed = passed
        self.error_code = error_code
        self.error_detail = error_detail
        # Custom status for STEP_UP_REQUIRED (not BLOCKED)
        self.status = status or ("PASS" if passed else "BLOCKED")


SCOPE_PATTERN = re.compile(
    r'^[a-z][a-z0-9_-]+\.[a-z][a-z0-9_-]+\.[a-z][a-z0-9_-]+$'
)

REQUIRED_FIELDS = [
    "id", "version", "issued_at", "expires_at",
    "scopes", "issuer", "subject", "signature_stub"
]


def check_g1(token) -> GateResult:
    """Gate 1: Schema validation."""
    if token is None:
        return GateResult(
            gate="G1", passed=False,
            error_code="OAUTH3_MISSING_TOKEN",
            error_detail="Token is null. No action may proceed without a token."
        )

    for field in REQUIRED_FIELDS:
        if field not in token or token[field] is None:
            return GateResult(
                gate="G1", passed=False,
                error_code="OAUTH3_MALFORMED_TOKEN",
                error_detail=f"Required field '{field}' is missing or null."
            )

    # Empty string check for string fields
    for field in ["id", "version", "issued_at", "expires_at", "issuer", "subject", "signature_stub"]:
        if token[field] == "":
            return GateResult(
                gate="G1", passed=False,
                error_code="OAUTH3_MALFORMED_TOKEN",
                error_detail=f"Required field '{field}' is empty string."
            )

    if not isinstance(token["scopes"], list) or len(token["scopes"]) == 0:
        return GateResult(
            gate="G1", passed=False,
            error_code="OAUTH3_MALFORMED_TOKEN",
            error_detail="'scopes' must be a non-empty array."
        )

    for scope in token["scopes"]:
        if not SCOPE_PATTERN.match(scope):
            return GateResult(
                gate="G1", passed=False,
                error_code="OAUTH3_MALFORMED_TOKEN",
                error_detail=f"Scope '{scope}' does not match platform.action.resource pattern."
            )

    return GateResult(gate="G1", passed=True)


def check_g2(token) -> GateResult:
    """Gate 2: TTL check."""
    try:
        expires_at = datetime.fromisoformat(
            token["expires_at"].replace("Z", "+00:00")
        )
    except (ValueError, TypeError) as e:
        return GateResult(
            gate="G2", passed=False,
            error_code="OAUTH3_MALFORMED_TOKEN",
            error_detail=f"'expires_at' is not a valid ISO 8601 datetime: {e}"
        )

    now_utc = datetime.now(timezone.utc)

    if expires_at <= now_utc:
        return GateResult(
            gate="G2", passed=False,
            error_code="OAUTH3_TOKEN_EXPIRED",
            error_detail=(
                f"Token expired at {token['expires_at']}; "
                f"current time is {now_utc.isoformat()}"
            )
        )

    return GateResult(gate="G2", passed=True)


def check_g3(token, requested_scope: str) -> GateResult:
    """Gate 3: Scope validation."""
    if not requested_scope or not SCOPE_PATTERN.match(requested_scope):
        return GateResult(
            gate="G3", passed=False,
            error_code="OAUTH3_SCOPE_DENIED",
            error_detail=f"Requested scope '{requested_scope}' does not match platform.action.resource pattern."
        )

    granted_scopes = set(token["scopes"])

    if requested_scope not in granted_scopes:
        return GateResult(
            gate="G3", passed=False,
            error_code="OAUTH3_SCOPE_DENIED",
            error_detail=(
                f"Scope '{requested_scope}' not in granted scopes: "
                f"{sorted(granted_scopes)}"
            )
        )

    step_up_scopes = set(token.get("step_up_required") or [])
    if requested_scope in step_up_scopes:
        return GateResult(
            gate="G3", passed=False,
            error_code="OAUTH3_STEP_UP_REQUIRED",
            status="STEP_UP_REQUIRED",
            error_detail=(
                f"Scope '{requested_scope}' requires step-up re-consent "
                "before execution."
            )
        )

    return GateResult(gate="G3", passed=True)


def check_g4(token, revocation_registry) -> GateResult:
    """Gate 4: Revocation check."""
    token_id = token["id"]

    if revocation_registry is None:
        return GateResult(
            gate="G4", passed=False,
            error_code="OAUTH3_REVOCATION_UNAVAILABLE",
            error_detail=(
                "Revocation registry is not available. "
                "Cannot proceed without revocation check (fail-closed)."
            )
        )

    try:
        is_revoked = revocation_registry.is_revoked(token_id)
    except Exception as e:
        return GateResult(
            gate="G4", passed=False,
            error_code="OAUTH3_REVOCATION_CHECK_FAILED",
            error_detail=f"Revocation registry lookup failed: {e}. Failing closed."
        )

    if is_revoked:
        return GateResult(
            gate="G4", passed=False,
            error_code="OAUTH3_TOKEN_REVOKED",
            error_detail=f"Token '{token_id}' is in the revocation registry."
        )

    return GateResult(gate="G4", passed=True)


def run_oauth3_gates(
    token,
    requested_scope: str,
    revocation_registry,
    action_description: Optional[str] = None,
    platform: Optional[str] = None,
    audit_output_path: str = "artifacts/oauth3/oauth3_audit.jsonl"
) -> dict:
    """Run all 4 OAuth3 gates. Fail-closed."""
    audit_id = str(uuid.uuid4())
    token_id = token["id"] if (token and "id" in token) else None
    subject = token.get("subject") if token else None
    issuer = token.get("issuer") if token else None
    now_utc = datetime.now(timezone.utc).isoformat()

    gates = [
        ("G1", lambda: check_g1(token)),
        ("G2", lambda: check_g2(token)),
        ("G3", lambda: check_g3(token, requested_scope)),
        ("G4", lambda: check_g4(token, revocation_registry)),
    ]

    gates_passed = []

    for gate_name, gate_fn in gates:
        gate_result = gate_fn()
        if gate_result.passed:
            gates_passed.append(gate_name)
        else:
            audit_record = {
                "audit_id": audit_id,
                "event": "TOKEN_GATE_FAILED",
                "timestamp": now_utc,
                "token_id": token_id,
                "subject": subject,
                "issuer": issuer,
                "scope": requested_scope,
                "platform": platform,
                "status": gate_result.status,
                "gate_failed": gate_name,
                "action_description": action_description,
                "artifact_path": None,
                "artifact_sha256": None,
                "error_code": gate_result.error_code,
                "error_detail": gate_result.error_detail,
                "metadata": None
            }
            _append_audit_record(audit_record, audit_output_path)
            return {
                "status": gate_result.status,
                "token_id": token_id,
                "scope": requested_scope,
                "gate_failed": gate_name,
                "stop_reason": gate_result.error_code,
                "error_detail": gate_result.error_detail,
                "audit_record_id": audit_id,
                "audit_file": audit_output_path
            }

    audit_record = {
        "audit_id": audit_id,
        "event": "TOKEN_VALIDATED",
        "timestamp": now_utc,
        "token_id": token_id,
        "subject": subject,
        "issuer": issuer,
        "scope": requested_scope,
        "platform": platform,
        "status": "PASS",
        "gate_failed": None,
        "action_description": action_description,
        "artifact_path": None,
        "artifact_sha256": None,
        "error_code": None,
        "error_detail": None,
        "metadata": {"gates_passed": gates_passed}
    }
    _append_audit_record(audit_record, audit_output_path)

    return {
        "status": "PASS",
        "token_id": token_id,
        "scope": requested_scope,
        "gates_passed": gates_passed,
        "audit_record_id": audit_id,
        "audit_file": audit_output_path
    }


def _append_audit_record(record: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


# ============================================================
# Test fixtures
# ============================================================

def make_valid_token(
    token_id: Optional[str] = None,
    expires_delta: timedelta = timedelta(hours=1),
    scopes: Optional[list] = None,
    step_up_required: Optional[list] = None,
) -> dict:
    """Return a well-formed AgencyToken for testing."""
    now = datetime.now(timezone.utc)
    return {
        "id": token_id or str(uuid.uuid4()),
        "version": "0.1.0",
        "issued_at": now.isoformat(),
        "expires_at": (now + expires_delta).isoformat(),
        "scopes": scopes or ["linkedin.read.feed", "linkedin.react.like"],
        "issuer": "https://www.solaceagi.com",
        "subject": "user:phuc@example.com",
        "agent_id": "solace-browser:twin:test",
        "step_up_required": step_up_required or [],
        "signature_stub": "sha256:abc123def456",
    }


class InMemoryRevocationRegistry:
    """Simple in-memory revocation registry for testing."""

    def __init__(self, revoked_ids: Optional[set] = None):
        self._revoked = set(revoked_ids or [])

    def is_revoked(self, token_id: str) -> bool:
        return token_id in self._revoked


class BrokenRevocationRegistry:
    """Registry that always raises on lookup (simulates unavailable registry)."""

    def is_revoked(self, token_id: str) -> bool:
        raise ConnectionError("Registry unreachable")


# ============================================================
# Tests
# ============================================================

class TestGate1Schema:
    """T1–T5: Gate 1 (Schema / G1) tests."""

    def test_t1_g1_pass_valid_token(self):
        """T1: G1 PASS — valid token with all required fields."""
        token = make_valid_token()
        result = check_g1(token)
        assert result.passed is True, f"Expected G1 PASS but got: {result.error_detail}"
        assert result.gate == "G1"
        assert result.error_code is None

    def test_t2_g1_fail_null_token(self):
        """T2: G1 FAIL — null token (OAUTH3_MISSING_TOKEN)."""
        result = check_g1(None)
        assert result.passed is False
        assert result.gate == "G1"
        assert result.error_code == "OAUTH3_MISSING_TOKEN"
        assert result.status == "BLOCKED"
        assert "null" in result.error_detail.lower()

    def test_t3_g1_fail_missing_required_field(self):
        """T3: G1 FAIL — missing required field 'subject' (OAUTH3_MALFORMED_TOKEN)."""
        token = make_valid_token()
        del token["subject"]
        result = check_g1(token)
        assert result.passed is False
        assert result.gate == "G1"
        assert result.error_code == "OAUTH3_MALFORMED_TOKEN"
        assert "subject" in result.error_detail

    def test_t4_g1_fail_malformed_scope_pattern(self):
        """T4: G1 FAIL — scope does not match platform.action.resource (OAUTH3_MALFORMED_TOKEN)."""
        token = make_valid_token(scopes=["linkedin.*.*"])  # wildcard — not allowed
        result = check_g1(token)
        assert result.passed is False
        assert result.gate == "G1"
        assert result.error_code == "OAUTH3_MALFORMED_TOKEN"
        assert "pattern" in result.error_detail.lower()

    def test_t5_g1_fail_empty_scopes_array(self):
        """T5: G1 FAIL — scopes is an empty array (OAUTH3_MALFORMED_TOKEN)."""
        token = make_valid_token()
        token["scopes"] = []
        result = check_g1(token)
        assert result.passed is False
        assert result.gate == "G1"
        assert result.error_code == "OAUTH3_MALFORMED_TOKEN"
        assert "non-empty" in result.error_detail.lower()


class TestGate2TTL:
    """T6–T7: Gate 2 (TTL / G2) tests."""

    def test_t6_g2_pass_token_not_expired(self):
        """T6: G2 PASS — token expires in the future."""
        token = make_valid_token(expires_delta=timedelta(hours=1))
        result = check_g2(token)
        assert result.passed is True, f"Expected G2 PASS but got: {result.error_detail}"
        assert result.gate == "G2"
        assert result.error_code is None

    def test_t7_g2_fail_token_expired(self):
        """T7: G2 FAIL — token expired in the past (OAUTH3_TOKEN_EXPIRED)."""
        token = make_valid_token(expires_delta=timedelta(hours=-1))
        result = check_g2(token)
        assert result.passed is False
        assert result.gate == "G2"
        assert result.error_code == "OAUTH3_TOKEN_EXPIRED"
        assert result.status == "BLOCKED"
        assert "expired" in result.error_detail.lower()


class TestGate3Scope:
    """T8–T10: Gate 3 (Scope / G3) tests."""

    def test_t8_g3_pass_scope_granted(self):
        """T8: G3 PASS — requested scope is in token's granted scopes."""
        token = make_valid_token(scopes=["linkedin.read.feed", "linkedin.react.like"])
        result = check_g3(token, "linkedin.read.feed")
        assert result.passed is True, f"Expected G3 PASS but got: {result.error_detail}"
        assert result.gate == "G3"
        assert result.error_code is None

    def test_t9_g3_fail_scope_mismatch(self):
        """T9: G3 FAIL — requested scope not in granted scopes (OAUTH3_SCOPE_DENIED)."""
        token = make_valid_token(scopes=["linkedin.read.feed", "linkedin.react.like"])
        result = check_g3(token, "linkedin.delete.post")
        assert result.passed is False
        assert result.gate == "G3"
        assert result.error_code == "OAUTH3_SCOPE_DENIED"
        assert result.status == "BLOCKED"
        assert "linkedin.delete.post" in result.error_detail

    def test_t10_g3_fail_step_up_required(self):
        """T10: G3 FAIL — scope granted but requires step-up re-consent (OAUTH3_STEP_UP_REQUIRED)."""
        token = make_valid_token(
            scopes=["linkedin.read.feed", "linkedin.post.text"],
            step_up_required=["linkedin.post.text"]
        )
        result = check_g3(token, "linkedin.post.text")
        assert result.passed is False
        assert result.gate == "G3"
        assert result.error_code == "OAUTH3_STEP_UP_REQUIRED"
        assert result.status == "STEP_UP_REQUIRED"
        assert "step-up" in result.error_detail.lower()


class TestGate4Revocation:
    """T11–T13: Gate 4 (Revocation / G4) tests."""

    def test_t11_g4_pass_token_not_revoked(self):
        """T11: G4 PASS — token not in revocation registry."""
        token = make_valid_token()
        registry = InMemoryRevocationRegistry(revoked_ids=set())
        result = check_g4(token, registry)
        assert result.passed is True, f"Expected G4 PASS but got: {result.error_detail}"
        assert result.gate == "G4"
        assert result.error_code is None

    def test_t12_g4_fail_token_revoked(self):
        """T12: G4 FAIL — token is in revocation registry (OAUTH3_TOKEN_REVOKED)."""
        token_id = str(uuid.uuid4())
        token = make_valid_token(token_id=token_id)
        registry = InMemoryRevocationRegistry(revoked_ids={token_id})
        result = check_g4(token, registry)
        assert result.passed is False
        assert result.gate == "G4"
        assert result.error_code == "OAUTH3_TOKEN_REVOKED"
        assert result.status == "BLOCKED"
        assert token_id in result.error_detail

    def test_t13_g4_fail_revocation_registry_unavailable(self):
        """T13: G4 FAIL — revocation registry is None (fail-closed: OAUTH3_REVOCATION_UNAVAILABLE)."""
        token = make_valid_token()
        result = check_g4(token, None)
        assert result.passed is False
        assert result.gate == "G4"
        assert result.error_code == "OAUTH3_REVOCATION_UNAVAILABLE"
        assert result.status == "BLOCKED"
        assert "fail-closed" in result.error_detail.lower()

    def test_t13b_g4_fail_revocation_registry_exception(self):
        """T13b: G4 FAIL — revocation registry raises exception (fail-closed: OAUTH3_REVOCATION_CHECK_FAILED)."""
        token = make_valid_token()
        registry = BrokenRevocationRegistry()
        result = check_g4(token, registry)
        assert result.passed is False
        assert result.gate == "G4"
        assert result.error_code == "OAUTH3_REVOCATION_CHECK_FAILED"
        assert result.status == "BLOCKED"
        assert "failed" in result.error_detail.lower()


class TestFullGateRunner:
    """T14–T15: Full gate runner tests (all 4 gates, audit JSON)."""

    def test_t14_full_pass_all_gates_clear_audit_well_formed(self):
        """T14: Full gate run PASS — all 4 gates clear, audit JSON record is well-formed."""
        token = make_valid_token(scopes=["linkedin.read.feed"])
        registry = InMemoryRevocationRegistry()

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = os.path.join(tmpdir, "oauth3", "oauth3_audit.jsonl")
            result = run_oauth3_gates(
                token=token,
                requested_scope="linkedin.read.feed",
                revocation_registry=registry,
                action_description="Test: read LinkedIn feed",
                platform="linkedin.com",
                audit_output_path=audit_path
            )

            # Check result structure
            assert result["status"] == "PASS"
            assert result["scope"] == "linkedin.read.feed"
            assert result["gates_passed"] == ["G1", "G2", "G3", "G4"]
            assert "audit_record_id" in result
            assert result["audit_record_id"] is not None

            # Verify audit JSON was written and is well-formed
            # (check must happen inside 'with' block before tmpdir is deleted)
            assert os.path.exists(audit_path), "Audit file was not created"
            with open(audit_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            assert len(lines) == 1, f"Expected 1 audit record, got {len(lines)}"

            record = json.loads(lines[0])

            # Verify all required schema fields are present (spec Section 5.2)
            required_fields = [
                "audit_id", "event", "timestamp", "token_id", "subject",
                "issuer", "scope", "platform", "status", "gate_failed",
                "action_description", "artifact_path", "artifact_sha256",
                "error_code", "error_detail", "metadata"
            ]
            for field in required_fields:
                assert field in record, f"Audit record missing required field: '{field}'"

            # Verify field values
            assert record["event"] == "TOKEN_VALIDATED"
            assert record["status"] == "PASS"
            assert record["gate_failed"] is None
            assert record["error_code"] is None
            assert record["scope"] == "linkedin.read.feed"
            assert record["platform"] == "linkedin.com"
            assert record["action_description"] == "Test: read LinkedIn feed"
            assert record["audit_id"] == result["audit_record_id"]

    def test_t15_full_blocked_gate_failure_stops_at_first_failed_gate(self):
        """T15: Full gate run BLOCKED — gate 2 failure stops run, audit record has gate_failed=G2."""
        # Token expired → G2 should fail; G3 and G4 should NOT run
        token = make_valid_token(
            expires_delta=timedelta(hours=-2),
            scopes=["linkedin.read.feed"]
        )
        registry = InMemoryRevocationRegistry()

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = os.path.join(tmpdir, "oauth3", "oauth3_audit.jsonl")
            result = run_oauth3_gates(
                token=token,
                requested_scope="linkedin.read.feed",
                revocation_registry=registry,
                action_description="Test: read feed with expired token",
                platform="linkedin.com",
                audit_output_path=audit_path
            )

            # Check result
            assert result["status"] == "BLOCKED"
            assert result["gate_failed"] == "G2"
            assert result["stop_reason"] == "OAUTH3_TOKEN_EXPIRED"
            assert "gates_passed" not in result  # not present when blocked

            # Verify audit record (inside 'with' block before tmpdir is deleted)
            with open(audit_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            assert len(lines) == 1
            record = json.loads(lines[0])
            assert record["event"] == "TOKEN_GATE_FAILED"
            assert record["status"] == "BLOCKED"
            assert record["gate_failed"] == "G2"
            assert record["error_code"] == "OAUTH3_TOKEN_EXPIRED"
            assert record["audit_id"] == result["audit_record_id"]
