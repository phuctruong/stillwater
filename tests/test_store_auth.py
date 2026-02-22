"""
tests/test_store_auth.py — Security-auditor QA for store/auth.py

Persona: Security Auditor
Approach: Adversarial. Every test assumes the implementation is subtly broken
          until proven otherwise. We probe key format edge cases, HMAC integrity
          guarantees, injection resistance, DB bypass attempts, and rate-limit
          enforcement boundaries.

Rung target: 641
Network: OFF — all DB calls are mocked via unittest.mock.patch
Red-Green gate: tests must FAIL before store/auth.py exists, PASS after.
"""

from __future__ import annotations

import hashlib
import hmac
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# ---------------------------------------------------------------------------
# Path setup — store/ lives at the project root
# ---------------------------------------------------------------------------
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from store.auth import (
    KEY_HEX_LENGTH,
    KEY_PREFIX,
    RATE_LIMIT_MAX,
    RATE_LIMIT_WINDOW_SECONDS,
    _hash_key,
    apply_reputation,
    check_rate_limit,
    generate_api_key,
    lookup_api_key,
    require_api_key,
    validate_key_format,
)
from store.models import APIKey


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_api_key(key_id: str = "acct_abc123", key_hash: str = "deadbeef") -> APIKey:
    """Create a minimal active APIKey fixture."""
    return APIKey(
        key_id=key_id,
        key_hash=key_hash,
        name="test-account",
        account_type="human",
        status="active",
        reputation=0.0,
        accepted_count=0,
        rejected_count=0,
        created_at=datetime.now(timezone.utc),
    )


def _valid_raw_key() -> str:
    """Generate one valid raw key via the real generate_api_key() function."""
    raw_key, _, _ = generate_api_key()
    return raw_key


# ===========================================================================
# CHECKPOINT 1: generate_api_key — format correctness + uniqueness
# ===========================================================================

class TestGenerateApiKey:
    """
    Security Auditor perspective: Key generation is the root of trust.
    If the key format is predictable, truncated, or collides across calls,
    the entire authentication layer is compromised.
    """

    def test_generate_returns_three_tuple(self):
        """generate_api_key() must return exactly (raw_key, key_id, key_hash)."""
        result = generate_api_key()
        assert isinstance(result, tuple), "Expected a 3-tuple"
        assert len(result) == 3, f"Expected tuple of length 3, got {len(result)}"

    def test_raw_key_has_correct_prefix(self):
        """raw_key must start with 'sw_sk_' prefix — no abbreviation, no swap."""
        raw_key, _, _ = generate_api_key()
        assert raw_key.startswith(KEY_PREFIX), (
            f"raw_key '{raw_key}' does not start with expected prefix '{KEY_PREFIX}'"
        )

    def test_raw_key_hex_part_is_exactly_32_chars(self):
        """The hex portion after 'sw_sk_' must be exactly 32 characters (128 bits)."""
        raw_key, _, _ = generate_api_key()
        hex_part = raw_key[len(KEY_PREFIX):]
        assert len(hex_part) == KEY_HEX_LENGTH, (
            f"Expected {KEY_HEX_LENGTH} hex chars, got {len(hex_part)}: '{hex_part}'"
        )

    def test_raw_key_hex_part_is_valid_hex(self):
        """The hex portion must contain only lowercase hex characters [0-9a-f]."""
        raw_key, _, _ = generate_api_key()
        hex_part = raw_key[len(KEY_PREFIX):]
        # Must parse as a hexadecimal integer without error
        int(hex_part, 16)

    def test_key_id_has_acct_prefix(self):
        """key_id must start with 'acct_' — audit trail anchor."""
        _, key_id, _ = generate_api_key()
        assert key_id.startswith("acct_"), (
            f"key_id '{key_id}' does not start with 'acct_'"
        )

    def test_key_id_is_valid_uuid4_hex(self):
        """The suffix of key_id must be a valid UUID4 hex (32 hex chars, no hyphens)."""
        _, key_id, _ = generate_api_key()
        suffix = key_id[len("acct_"):]
        assert len(suffix) == 32, (
            f"key_id suffix should be 32-char UUID4 hex, got {len(suffix)}: '{suffix}'"
        )
        # Must be valid hex
        int(suffix, 16)

    def test_key_hash_is_64_char_hex(self):
        """key_hash must be a 64-char hex string (SHA-256 output)."""
        _, _, key_hash = generate_api_key()
        assert isinstance(key_hash, str), "key_hash must be a string"
        assert len(key_hash) == 64, (
            f"Expected 64-char hex (SHA-256), got {len(key_hash)}: '{key_hash}'"
        )
        int(key_hash, 16)

    def test_two_calls_produce_different_raw_keys(self):
        """Two independent calls must never return the same raw_key (collision = auth bypass)."""
        raw1, _, _ = generate_api_key()
        raw2, _, _ = generate_api_key()
        assert raw1 != raw2, "generate_api_key() returned the same raw_key twice — collision risk"

    def test_two_calls_produce_different_key_ids(self):
        """Two calls must produce different key_ids — duplicate IDs allow privilege escalation."""
        _, id1, _ = generate_api_key()
        _, id2, _ = generate_api_key()
        assert id1 != id2, "generate_api_key() returned duplicate key_ids — identity collision risk"

    def test_validate_format_accepts_generated_key(self):
        """Every key produced by generate_api_key() must pass validate_key_format()."""
        for _ in range(5):
            raw_key, _, _ = generate_api_key()
            assert validate_key_format(raw_key) is True, (
                f"validate_key_format() rejected a key produced by generate_api_key(): '{raw_key}'"
            )


# ===========================================================================
# CHECKPOINT 2: validate_key_format — edge-case coverage
# ===========================================================================

class TestValidateKeyFormat:
    """
    Security Auditor perspective: Input validation is the outer perimeter.
    Any bypass here — via type confusion, off-by-one truncation, or partial
    prefix matches — can allow malformed tokens to reach the HMAC lookup.
    """

    def test_accepts_well_formed_key(self):
        """A properly constructed key (sw_sk_ + 32 hex) must return True."""
        key = "sw_sk_" + "a" * 32
        assert validate_key_format(key) is True

    def test_accepts_mixed_case_hex(self):
        """Hex chars a-f and A-F are both valid per Python string.hexdigits."""
        key = "sw_sk_" + "aAbBcCdD" * 4  # 32 chars
        assert validate_key_format(key) is True

    def test_rejects_empty_string(self):
        """Empty string must return False — never reach HMAC."""
        assert validate_key_format("") is False

    def test_rejects_none_without_exception(self):
        """None input must return False, never raise AttributeError or TypeError."""
        assert validate_key_format(None) is False  # type: ignore[arg-type]

    def test_rejects_wrong_prefix(self):
        """Keys with wrong prefix (e.g. 'sk_sw_') must be rejected."""
        key = "sk_sw_" + "a" * 32
        assert validate_key_format(key) is False

    def test_rejects_no_prefix(self):
        """A bare 38-char hex string without the prefix must be rejected."""
        key = "a" * 38  # len("sw_sk_") + 32 = 38, but no prefix
        assert validate_key_format(key) is False

    def test_rejects_too_short_hex(self):
        """Hex part shorter than 32 chars must be rejected (31 chars)."""
        key = KEY_PREFIX + "a" * (KEY_HEX_LENGTH - 1)
        assert validate_key_format(key) is False

    def test_rejects_too_long_hex(self):
        """Hex part longer than 32 chars must be rejected (33 chars)."""
        key = KEY_PREFIX + "a" * (KEY_HEX_LENGTH + 1)
        assert validate_key_format(key) is False

    def test_rejects_non_hex_chars_in_body(self):
        """Non-hex characters in the key body (e.g. 'g', 'z', '@') must be rejected."""
        key = KEY_PREFIX + "g" * 32  # 'g' is not a hex digit
        assert validate_key_format(key) is False

    def test_rejects_special_chars_injection_attempt(self):
        """SQL-style injection in key body must be rejected cleanly, no exception."""
        key = KEY_PREFIX + "'; DROP TABLE api_keys; --" + "a" * 6
        assert validate_key_format(key) is False

    def test_rejects_non_string_type_int(self):
        """Integer input must return False, not raise TypeError."""
        assert validate_key_format(12345) is False  # type: ignore[arg-type]

    def test_rejects_non_string_type_list(self):
        """List input must return False, not crash."""
        assert validate_key_format(["sw_sk_", "a" * 32]) is False  # type: ignore[arg-type]

    def test_rejects_unicode_lookalike_prefix(self):
        """Unicode homoglyph in prefix (e.g. 'sw_ѕk_') must be rejected."""
        # Cyrillic 's' lookalike
        key = "sw_\u0455k_" + "a" * 32
        assert validate_key_format(key) is False

    def test_rejects_only_prefix_no_hex(self):
        """Key consisting of only the prefix with no hex body must be rejected."""
        assert validate_key_format(KEY_PREFIX) is False

    def test_rejects_whitespace_padded_key(self):
        """Keys with leading/trailing whitespace must be rejected at format check."""
        key = " " + KEY_PREFIX + "a" * 32
        assert validate_key_format(key) is False


# ===========================================================================
# CHECKPOINT 3: _hash_key — HMAC integrity
# ===========================================================================

class TestHashKey:
    """
    Security Auditor perspective: The HMAC is the only thing preventing
    a stolen raw key from being replayed after DB rotation. We verify
    determinism (needed for lookup) and sensitivity (needed for collision-resistance).
    We also confirm the raw key is never returned — only the hex digest.
    """

    def test_hash_key_is_deterministic(self):
        """Same raw_key must always produce the same hash — required for DB lookup."""
        raw_key = KEY_PREFIX + "0123456789abcdef" * 2
        h1 = _hash_key(raw_key)
        h2 = _hash_key(raw_key)
        assert h1 == h2, "_hash_key() is not deterministic — DB lookup will fail randomly"

    def test_hash_key_different_inputs_produce_different_outputs(self):
        """Two distinct keys must produce distinct hashes — collision = auth bypass."""
        raw_key_a = KEY_PREFIX + "0" * 32
        raw_key_b = KEY_PREFIX + "1" * 32
        assert _hash_key(raw_key_a) != _hash_key(raw_key_b), (
            "_hash_key() collision detected: two different keys produce the same hash"
        )

    def test_hash_key_returns_string(self):
        """_hash_key() must return a str, never bytes."""
        raw_key = KEY_PREFIX + "abcdef01" * 4
        result = _hash_key(raw_key)
        assert isinstance(result, str), f"Expected str, got {type(result)}"

    def test_hash_key_output_is_64_char_hex(self):
        """_hash_key() output must be a 64-char hex string (HMAC-SHA256 digest)."""
        raw_key = KEY_PREFIX + "a" * 32
        result = _hash_key(raw_key)
        assert len(result) == 64, f"Expected 64-char hex, got {len(result)}: '{result}'"
        int(result, 16)  # must be valid hex

    def test_hash_key_does_not_contain_raw_key(self):
        """The hex digest must not contain the raw key — key leakage in hash is a flaw."""
        raw_key = KEY_PREFIX + "cafebabe" * 4
        result = _hash_key(raw_key)
        assert raw_key not in result, "raw_key found embedded inside its own hash — leakage risk"

    def test_hash_key_single_bit_difference_changes_output(self):
        """HMAC must be sensitive: one character difference must produce a completely different hash."""
        base = KEY_PREFIX + "0" * 31 + "0"
        flip = KEY_PREFIX + "0" * 31 + "1"
        assert _hash_key(base) != _hash_key(flip), (
            "_hash_key() is not sensitive to single character changes"
        )


# ===========================================================================
# CHECKPOINT 4: lookup_api_key — format gate + DB interaction
# ===========================================================================

class TestLookupApiKey:
    """
    Security Auditor perspective: lookup_api_key() is the bridge between
    user input and the DB. We verify the format gate fires before any DB
    access, that inactive keys are denied, and that a DB miss returns None
    cleanly without leaking internal state.
    """

    def test_returns_none_for_invalid_format_no_db_call(self):
        """lookup_api_key() must return None immediately for malformed keys — no DB round-trip."""
        with patch("store.auth.get_store") as mock_get_store:
            result = lookup_api_key("not_a_valid_key")
        assert result is None
        # The DB must not have been consulted — format gate fires first
        mock_get_store.assert_not_called()

    def test_returns_none_for_empty_string(self):
        """Empty string must short-circuit at the format gate, return None."""
        with patch("store.auth.get_store") as mock_get_store:
            result = lookup_api_key("")
        assert result is None
        mock_get_store.assert_not_called()

    def test_returns_none_when_key_not_in_db(self):
        """Valid format but hash not in DB → return None (no exception, no 500)."""
        raw_key = KEY_PREFIX + "a" * 32

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = None

        with patch("store.auth.get_store", return_value=mock_store):
            result = lookup_api_key(raw_key)

        assert result is None
        mock_store.get_api_key_by_hash.assert_called_once()

    def test_returns_none_for_inactive_key(self):
        """A key with status='suspended' must be rejected — suspended != active."""
        raw_key = KEY_PREFIX + "b" * 32
        key_hash = _hash_key(raw_key)

        suspended_key = _make_api_key(key_hash=key_hash)
        suspended_key = suspended_key.model_copy(update={"status": "suspended"})

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = suspended_key

        with patch("store.auth.get_store", return_value=mock_store):
            result = lookup_api_key(raw_key)

        assert result is None, "Suspended key must not be returned by lookup_api_key()"

    def test_returns_api_key_for_valid_active_key(self):
        """Valid format + hash in DB + status='active' → return the APIKey record."""
        raw_key = KEY_PREFIX + "c" * 32
        key_hash = _hash_key(raw_key)

        active_key = _make_api_key(key_id="acct_valid001", key_hash=key_hash)

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = active_key

        with patch("store.auth.get_store", return_value=mock_store):
            result = lookup_api_key(raw_key)

        assert result is not None
        assert isinstance(result, APIKey)
        assert result.key_id == "acct_valid001"

    def test_db_is_queried_with_hmac_hash_not_raw_key(self):
        """The DB query must use the HMAC hash, never the raw key — raw key must never persist."""
        raw_key = KEY_PREFIX + "d" * 32
        expected_hash = _hash_key(raw_key)

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = None

        with patch("store.auth.get_store", return_value=mock_store):
            lookup_api_key(raw_key)

        # Verify the DB was called with the hash, not the raw key
        call_args = mock_store.get_api_key_by_hash.call_args
        assert call_args is not None
        queried_hash = call_args[0][0]
        assert queried_hash == expected_hash, (
            f"DB was queried with '{queried_hash}' instead of HMAC hash '{expected_hash}'"
        )
        assert queried_hash != raw_key, "raw_key was passed directly to DB — HMAC bypassed"


# ===========================================================================
# CHECKPOINT 5: require_api_key — FastAPI dependency / 401 enforcement
# ===========================================================================

class TestRequireApiKey:
    """
    Security Auditor perspective: require_api_key() is the FastAPI guard.
    Any path that skips the 401 — missing credentials, None credentials,
    invalid key — is an unauthenticated endpoint.
    """

    def test_raises_401_when_credentials_is_none(self):
        """No Authorization header (credentials=None) must raise HTTP 401."""
        with pytest.raises(HTTPException) as exc_info:
            require_api_key(credentials=None)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_credentials_is_empty_string(self):
        """An empty Bearer token must raise HTTP 401."""
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        with pytest.raises(HTTPException) as exc_info:
            require_api_key(credentials=creds)
        assert exc_info.value.status_code == 401

    def test_raises_401_for_invalid_key_format(self):
        """A malformed token (wrong prefix) must raise HTTP 401, not 500."""
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad_key_format")
        with patch("store.auth.get_store") as mock_get_store:
            mock_get_store.return_value.get_api_key_by_hash.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                require_api_key(credentials=creds)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_key_not_in_db(self):
        """A well-formed key that doesn't exist in the DB must raise HTTP 401."""
        raw_key = KEY_PREFIX + "e" * 32
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=raw_key)

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = None

        with patch("store.auth.get_store", return_value=mock_store):
            with pytest.raises(HTTPException) as exc_info:
                require_api_key(credentials=creds)
        assert exc_info.value.status_code == 401

    def test_returns_api_key_for_valid_credentials(self):
        """Valid Bearer token for an active key must return the APIKey record."""
        raw_key = KEY_PREFIX + "f" * 32
        key_hash = _hash_key(raw_key)
        active_key = _make_api_key(key_id="acct_valid002", key_hash=key_hash)

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=raw_key)

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = active_key

        with patch("store.auth.get_store", return_value=mock_store):
            result = require_api_key(credentials=creds)

        assert isinstance(result, APIKey)
        assert result.key_id == "acct_valid002"

    def test_401_detail_does_not_leak_raw_key(self):
        """The 401 error detail must not echo the submitted key back — no reflection attack."""
        raw_key = KEY_PREFIX + "0123456789abcdef" * 2
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=raw_key)

        mock_store = MagicMock()
        mock_store.get_api_key_by_hash.return_value = None

        with patch("store.auth.get_store", return_value=mock_store):
            with pytest.raises(HTTPException) as exc_info:
                require_api_key(credentials=creds)

        detail = exc_info.value.detail
        assert raw_key not in str(detail), (
            f"401 detail leaks the submitted raw key: '{detail}'"
        )


# ===========================================================================
# CHECKPOINT 6: check_rate_limit — 429 enforcement + boundary
# ===========================================================================

class TestCheckRateLimit:
    """
    Security Auditor perspective: Rate limiting is the DoS and abuse-prevention
    control. Off-by-one errors (>= vs >) mean the limit fires at 9 or 11 instead
    of 10. We test at limit-1, limit, and limit+1.
    """

    def _make_key(self, key_id: str = "acct_ratelimit") -> APIKey:
        return _make_api_key(key_id=key_id)

    def test_does_not_raise_when_under_limit(self):
        """count = RATE_LIMIT_MAX - 1 must not raise — user still has one request left."""
        api_key = self._make_key()

        mock_store = MagicMock()
        mock_store.count_recent_submissions.return_value = RATE_LIMIT_MAX - 1

        with patch("store.auth.get_store", return_value=mock_store):
            # Should complete without raising
            check_rate_limit(api_key)

    def test_raises_429_at_exactly_limit(self):
        """count == RATE_LIMIT_MAX must trigger HTTP 429 — at-limit means exhausted."""
        api_key = self._make_key()

        mock_store = MagicMock()
        mock_store.count_recent_submissions.return_value = RATE_LIMIT_MAX

        with patch("store.auth.get_store", return_value=mock_store):
            with pytest.raises(HTTPException) as exc_info:
                check_rate_limit(api_key)

        assert exc_info.value.status_code == 429

    def test_raises_429_above_limit(self):
        """count > RATE_LIMIT_MAX must also raise HTTP 429."""
        api_key = self._make_key()

        mock_store = MagicMock()
        mock_store.count_recent_submissions.return_value = RATE_LIMIT_MAX + 5

        with patch("store.auth.get_store", return_value=mock_store):
            with pytest.raises(HTTPException) as exc_info:
                check_rate_limit(api_key)

        assert exc_info.value.status_code == 429

    def test_rate_limit_store_called_with_correct_key_id(self):
        """check_rate_limit() must pass the api_key's key_id to the store."""
        api_key = self._make_key(key_id="acct_specific_key")

        mock_store = MagicMock()
        mock_store.count_recent_submissions.return_value = 0

        with patch("store.auth.get_store", return_value=mock_store):
            check_rate_limit(api_key)

        call_kwargs = mock_store.count_recent_submissions.call_args
        assert call_kwargs is not None
        # key_id must be passed
        passed_key_id = call_kwargs.kwargs.get("key_id") or call_kwargs.args[0]
        assert passed_key_id == "acct_specific_key", (
            f"Expected key_id='acct_specific_key', got '{passed_key_id}'"
        )

    def test_rate_limit_window_passed_to_store(self):
        """check_rate_limit() must pass RATE_LIMIT_WINDOW_SECONDS to the store."""
        api_key = self._make_key()

        mock_store = MagicMock()
        mock_store.count_recent_submissions.return_value = 0

        with patch("store.auth.get_store", return_value=mock_store):
            check_rate_limit(api_key)

        call_kwargs = mock_store.count_recent_submissions.call_args
        passed_window = call_kwargs.kwargs.get("window_seconds") or (
            call_kwargs.args[1] if len(call_kwargs.args) > 1 else None
        )
        assert passed_window == RATE_LIMIT_WINDOW_SECONDS, (
            f"Expected window_seconds={RATE_LIMIT_WINDOW_SECONDS}, got {passed_window}"
        )

    def test_429_detail_includes_current_count(self):
        """The 429 detail message must include the current count for diagnostics."""
        api_key = self._make_key()
        current_count = RATE_LIMIT_MAX + 2

        mock_store = MagicMock()
        mock_store.count_recent_submissions.return_value = current_count

        with patch("store.auth.get_store", return_value=mock_store):
            with pytest.raises(HTTPException) as exc_info:
                check_rate_limit(api_key)

        detail = str(exc_info.value.detail)
        assert str(current_count) in detail, (
            f"429 detail should include current count {current_count}, got: '{detail}'"
        )


# ===========================================================================
# CHECKPOINT 7: apply_reputation — score mutations
# ===========================================================================

class TestApplyReputation:
    """
    Security Auditor perspective: Reputation updates must be idempotent in their
    effect (no double-counting), target the correct counter, and silently no-op
    for unknown key_ids rather than creating phantom records.
    """

    def test_accept_increments_accepted_count(self):
        """apply_reputation(accepted=True) must increment accepted_count by 1."""
        key_id = "acct_rep001"
        record = _make_api_key(key_id=key_id)
        # accepted_count starts at 0

        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = record

        with patch("store.auth.get_store", return_value=mock_store):
            apply_reputation(key_id, accepted=True)

        mock_store.update_api_key.assert_called_once()
        _, update_dict = mock_store.update_api_key.call_args[0]
        assert update_dict.get("accepted_count") == 1, (
            f"Expected accepted_count=1 on accept, got {update_dict}"
        )

    def test_accept_adds_positive_reputation_delta(self):
        """apply_reputation(accepted=True) must add +1.0 to reputation score."""
        key_id = "acct_rep002"
        record = _make_api_key(key_id=key_id)
        record = record.model_copy(update={"reputation": 5.0})

        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = record

        with patch("store.auth.get_store", return_value=mock_store):
            apply_reputation(key_id, accepted=True)

        _, update_dict = mock_store.update_api_key.call_args[0]
        assert update_dict.get("reputation") == pytest.approx(6.0), (
            f"Expected reputation=6.0 after +1.0, got {update_dict.get('reputation')}"
        )

    def test_reject_increments_rejected_count(self):
        """apply_reputation(accepted=False) must increment rejected_count by 1."""
        key_id = "acct_rep003"
        record = _make_api_key(key_id=key_id)

        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = record

        with patch("store.auth.get_store", return_value=mock_store):
            apply_reputation(key_id, accepted=False)

        _, update_dict = mock_store.update_api_key.call_args[0]
        assert update_dict.get("rejected_count") == 1, (
            f"Expected rejected_count=1 on reject, got {update_dict}"
        )

    def test_reject_subtracts_reputation_delta(self):
        """apply_reputation(accepted=False) must subtract 0.5 from reputation score."""
        key_id = "acct_rep004"
        record = _make_api_key(key_id=key_id)
        record = record.model_copy(update={"reputation": 3.0})

        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = record

        with patch("store.auth.get_store", return_value=mock_store):
            apply_reputation(key_id, accepted=False)

        _, update_dict = mock_store.update_api_key.call_args[0]
        assert update_dict.get("reputation") == pytest.approx(2.5), (
            f"Expected reputation=2.5 after -0.5, got {update_dict.get('reputation')}"
        )

    def test_noop_when_key_id_not_found(self):
        """apply_reputation() must silently no-op if key_id is unknown — no exception, no phantom record."""
        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = None

        with patch("store.auth.get_store", return_value=mock_store):
            # Must not raise
            apply_reputation("acct_ghost_does_not_exist", accepted=True)

        # update_api_key must never be called for a missing record
        mock_store.update_api_key.assert_not_called()

    def test_accept_does_not_touch_rejected_count(self):
        """Accepting a skill must not modify rejected_count — no cross-counter corruption."""
        key_id = "acct_rep005"
        record = _make_api_key(key_id=key_id)
        record = record.model_copy(update={"rejected_count": 2})

        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = record

        with patch("store.auth.get_store", return_value=mock_store):
            apply_reputation(key_id, accepted=True)

        _, update_dict = mock_store.update_api_key.call_args[0]
        assert "rejected_count" not in update_dict, (
            f"accept updated rejected_count unexpectedly: {update_dict}"
        )

    def test_reject_does_not_touch_accepted_count(self):
        """Rejecting a skill must not modify accepted_count — no cross-counter corruption."""
        key_id = "acct_rep006"
        record = _make_api_key(key_id=key_id)
        record = record.model_copy(update={"accepted_count": 5})

        mock_store = MagicMock()
        mock_store.get_api_key_by_id.return_value = record

        with patch("store.auth.get_store", return_value=mock_store):
            apply_reputation(key_id, accepted=False)

        _, update_dict = mock_store.update_api_key.call_args[0]
        assert "accepted_count" not in update_dict, (
            f"reject updated accepted_count unexpectedly: {update_dict}"
        )
