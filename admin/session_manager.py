"""
Stillwater LLM Portal — Session Manager
Auth: 65537 | Version: 1.0.0

AES-256-GCM encrypted, memory-only API key storage.
Keys are NEVER written to disk, logged, or exposed in repr/str.

Security model:
  - Each SessionManager instance holds a 32-byte random AES key (session-scoped).
  - API keys are encrypted with AES-256-GCM before storage in the in-memory dict.
  - A fresh random 12-byte nonce is generated per encryption (ensures ciphertext
    uniqueness even for repeated identical plaintexts).
  - __repr__ and __str__ emit only metadata — never raw or encrypted key material.
  - clear() wipes the in-memory dict; the AES key itself is discarded on GC.

Usage:
    from admin.session_manager import SessionManager

    session = SessionManager()
    session.store_key("openai", "sk-...")
    key = session.get_key("openai")     # returns plaintext str or None
    ok  = session.has_key("openai")     # bool
    session.set_active_provider("openai")
    session.clear()                     # wipe all keys
"""

from __future__ import annotations

import os
import secrets
from typing import Optional


# ---------------------------------------------------------------------------
# Internal: AES-256-GCM helpers
# ---------------------------------------------------------------------------

def _aes_encrypt(aes_key: bytes, plaintext: str) -> bytes:
    """Encrypt plaintext string with AES-256-GCM. Returns nonce + ciphertext."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit nonce, fresh per call
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ct  # prepend nonce for later decryption


def _aes_decrypt(aes_key: bytes, blob: bytes) -> str:
    """Decrypt AES-256-GCM blob (nonce + ciphertext). Returns plaintext string."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if len(blob) < 12:
        raise ValueError("Blob too short — corrupted ciphertext")
    nonce = blob[:12]
    ct = blob[12:]
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ct, None).decode("utf-8")


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------

class SessionManager:
    """
    In-memory, AES-256-GCM encrypted storage for user-supplied API keys.

    Thread-safety: Not guaranteed (use one instance per request context or
    protect with a lock if sharing across async tasks).

    Security guarantees:
      - Keys are never written to disk.
      - Keys never appear in repr(), str(), or exception messages from this class.
      - The encryption key is 32 random bytes (256-bit AES) generated at __init__.
      - Each store_key() call uses a fresh 12-byte random nonce.
    """

    def __init__(self) -> None:
        # 256-bit AES key; lives only in this object's memory
        self._aes_key: bytes = secrets.token_bytes(32)
        # provider_id → encrypted blob (nonce + ciphertext)
        self._encrypted_keys: dict[str, bytes] = {}
        # Currently active provider (metadata only — no key material)
        self._active_provider: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store_key(self, provider: str, api_key: str) -> None:
        """
        Encrypt and store an API key for the given provider.

        Args:
            provider: Provider identifier (e.g. "openai", "claude").
            api_key:  Plaintext API key (never logged or persisted).

        Raises:
            ValueError: If provider is empty or api_key is empty/None.
        """
        if not provider or not provider.strip():
            raise ValueError("provider must be a non-empty string")
        if not api_key:
            raise ValueError("api_key must be a non-empty string (null != empty)")

        self._encrypted_keys[provider] = _aes_encrypt(self._aes_key, api_key)

    def get_key(self, provider: str) -> Optional[str]:
        """
        Decrypt and return the API key for the given provider.

        Returns:
            Plaintext API key, or None if no key is stored for this provider.
        """
        blob = self._encrypted_keys.get(provider)
        if blob is None:
            return None
        return _aes_decrypt(self._aes_key, blob)

    def has_key(self, provider: str) -> bool:
        """Return True if an API key has been stored for this provider."""
        return provider in self._encrypted_keys

    def set_active_provider(self, provider: str) -> None:
        """Set the active provider (metadata only — does not require a key)."""
        if not provider or not provider.strip():
            raise ValueError("provider must be a non-empty string")
        self._active_provider = provider

    @property
    def active_provider(self) -> Optional[str]:
        """Currently active provider identifier."""
        return self._active_provider

    def authenticated_providers(self) -> list[str]:
        """Return list of provider IDs that have a stored API key."""
        return list(self._encrypted_keys.keys())

    def clear(self) -> None:
        """
        Wipe all stored API keys from memory.

        After calling clear(), has_key() returns False for all providers
        and get_key() returns None for all providers.
        """
        self._encrypted_keys.clear()
        self._active_provider = None

    # ------------------------------------------------------------------
    # Security: never expose key material in repr/str
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SessionManager("
            f"active_provider={self._active_provider!r}, "
            f"num_keys={len(self._encrypted_keys)}"
            f")"
        )

    def __str__(self) -> str:  # pragma: no cover
        return self.__repr__()
