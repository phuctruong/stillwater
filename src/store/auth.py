"""
src/store/auth.py — API key validation and rate limiting for the Stillwater Store.

API key format:  sw_sk_<32-char-hex>
Storage:         HMAC-SHA256(raw_key, HMAC_SECRET) stored in DB; raw key never stored
Rate limiting:   10 submissions per 24-hour rolling window per key_id

Rung target: 641
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import string
import uuid
from typing import Optional, Tuple

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .db import get_store
from .models import APIKey

# HMAC secret for key hashing. Kept at function level so importing this module
# does not fail during unrelated test collection.
def _get_hmac_secret() -> bytes:
    raw = os.environ.get("STILLWATER_HMAC_SECRET", "")
    if not raw:
        raise RuntimeError("STILLWATER_HMAC_SECRET env var must be set. No default allowed.")
    return raw.encode()

# Rate limit: max submissions per rolling 24-hour window
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW_SECONDS = 86400  # 24 hours

# Bearer token extraction
_bearer = HTTPBearer(auto_error=False)

# API key prefix
KEY_PREFIX = "sw_sk_"
KEY_HEX_LENGTH = 32  # 32 hex chars = 128 bits


# ============================================================
# Key generation
# ============================================================

def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate a new API key.

    Returns:
        (raw_key, key_id, key_hash)
        - raw_key:  the full key string shown to the user once (sw_sk_<32hex>)
        - key_id:   the account ID (acct_<uuid4-hex>)
        - key_hash: HMAC-SHA256 of raw_key (stored in DB)
    """
    hex_part = secrets.token_hex(KEY_HEX_LENGTH // 2)  # 16 bytes → 32 hex chars
    raw_key = f"{KEY_PREFIX}{hex_part}"
    key_id  = f"acct_{uuid.uuid4().hex}"
    key_hash = _hash_key(raw_key)
    return raw_key, key_id, key_hash


def _hash_key(raw_key: str) -> str:
    """HMAC-SHA256 of raw_key. This is what we store in the DB."""
    return hmac.new(_get_hmac_secret(), raw_key.encode(), hashlib.sha256).hexdigest()


def validate_key_format(raw_key: str) -> bool:
    """
    Check that raw_key matches the expected format: sw_sk_<32hex>.
    Returns True if format is valid, False otherwise.
    Does NOT check against the database.
    """
    if not raw_key or not isinstance(raw_key, str):
        return False
    if not raw_key.startswith(KEY_PREFIX):
        return False
    hex_part = raw_key[len(KEY_PREFIX):]
    if len(hex_part) != KEY_HEX_LENGTH:
        return False
    valid_chars = set(string.hexdigits)
    return all(c in valid_chars for c in hex_part)


# ============================================================
# Auth dependency
# ============================================================

def lookup_api_key(raw_key: str) -> Optional[APIKey]:
    """
    Look up an API key in the DB by its hash.
    Returns the APIKey record if found and active, None otherwise.
    """
    if not validate_key_format(raw_key):
        return None
    key_hash = _hash_key(raw_key)
    store = get_store()
    record = store.get_api_key_by_hash(key_hash)
    if record is None:
        return None
    if record.status != "active":
        return None
    return record


def require_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> APIKey:
    """
    FastAPI dependency: extract and validate the Bearer sw_sk_ key.
    Raises HTTP 401 if missing or invalid.
    Returns the APIKey record on success.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide: Authorization: Bearer sw_sk_<key>",
        )

    raw_key = credentials.credentials.strip()
    api_key = lookup_api_key(raw_key)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key.",
        )

    return api_key


# ============================================================
# Rate limiting
# ============================================================

def check_rate_limit(api_key: APIKey) -> None:
    """
    Check whether this API key has exceeded the rate limit.
    Raises HTTP 429 if the limit is exceeded.

    Rate limit: RATE_LIMIT_MAX submissions per RATE_LIMIT_WINDOW_SECONDS.
    """
    store = get_store()
    count = store.count_recent_submissions(
        key_id=api_key.key_id,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    )
    if count >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded: {RATE_LIMIT_MAX} submissions per 24 hours. "
                f"Current count: {count}. Try again later."
            ),
        )


# ============================================================
# Reputation scoring
# ============================================================

REPUTATION_ACCEPT = 1.0
REPUTATION_REJECT = -0.5


def apply_reputation(key_id: str, accepted: bool) -> None:
    """
    Update reputation score for a key when a skill is accepted or rejected.
    accepted=True → +1.0, accepted=False → -0.5
    """
    store = get_store()
    record = store.get_api_key_by_id(key_id)
    if record is None:
        return

    delta = REPUTATION_ACCEPT if accepted else REPUTATION_REJECT
    new_reputation = record.reputation + delta

    updates: dict = {"reputation": new_reputation}
    if accepted:
        updates["accepted_count"] = record.accepted_count + 1
    else:
        updates["rejected_count"] = record.rejected_count + 1

    store.update_api_key(key_id, updates)
