"""Gmail connector with explicit OAuth3 scope checks.

This module is intentionally API-client agnostic for testability.
All external calls are routed through ``_request`` so tests can patch it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Optional


class ScopeDeniedError(PermissionError):
    """Raised when a required OAuth3 scope is missing."""


class ConnectorBase(ABC):
    """Base class contract for external API connectors."""

    @abstractmethod
    def connect(self, oauth3_token: dict[str, Any]) -> None:
        """Authenticate using an OAuth3 token payload."""

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Return connector health details."""


class GmailConnector(ConnectorBase):
    """Gmail API client wrapper with OAuth3 scope enforcement."""

    def __init__(
        self,
        *,
        request_fn: Optional[Callable[[str, str, Optional[dict[str, Any]]], dict[str, Any]]] = None,
        audit_fn: Optional[Callable[[str, dict[str, Any]], None]] = None,
    ) -> None:
        self._request_fn = request_fn
        self._audit_fn = audit_fn
        self._token: Optional[dict[str, Any]] = None

    def connect(self, oauth3_token: dict[str, Any]) -> None:
        """Validate token shape and activation state before use."""
        if not isinstance(oauth3_token, dict):
            raise TypeError("oauth3_token must be a dict")

        scopes = oauth3_token.get("scopes")
        if not isinstance(scopes, list):
            raise ValueError("oauth3_token.scopes must be a list")
        if not scopes:
            raise ScopeDeniedError("oauth3_token has no scopes")

        if oauth3_token.get("revoked", False):
            raise ScopeDeniedError("oauth3 token is revoked")

        expires_at = oauth3_token.get("expires_at")
        if isinstance(expires_at, str) and expires_at.strip():
            try:
                exp = datetime.fromisoformat(expires_at)
            except ValueError as exc:
                raise ValueError("oauth3_token.expires_at is invalid ISO timestamp") from exc
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > exp:
                raise ScopeDeniedError("oauth3 token is expired")

        self._token = oauth3_token

    def health_check(self) -> dict[str, Any]:
        """Expose connector state for diagnostics."""
        connected = self._token is not None
        scopes = list(self._token.get("scopes", [])) if connected else []
        return {
            "ok": connected,
            "connector": "gmail",
            "connected": connected,
            "scope_count": len(scopes),
            "scopes": scopes,
        }

    def fetch_unread(self, max_results: int = 50) -> list[dict[str, Any]]:
        """Fetch unread inbox messages. Requires: gmail.read.inbox."""
        self._require_scope("gmail.read.inbox")
        if max_results <= 0:
            raise ValueError("max_results must be positive")
        payload = {"max_results": int(max_results), "query": "is:unread in:inbox"}
        resp = self._request("GET", "/gmail/messages", payload)
        messages = resp.get("messages", [])
        if not isinstance(messages, list):
            raise ValueError("gmail response field 'messages' must be a list")
        self._audit("gmail.fetch_unread", {"count": len(messages)})
        return messages

    def get_message(self, message_id: str) -> dict[str, Any]:
        """Get full message payload. Requires: gmail.read.inbox."""
        self._require_scope("gmail.read.inbox")
        if not message_id:
            raise ValueError("message_id is required")
        resp = self._request("GET", f"/gmail/messages/{message_id}", None)
        self._audit("gmail.get_message", {"message_id": message_id})
        return resp

    def apply_label(self, message_id: str, label: str) -> None:
        """Apply label to a message. Requires: gmail.modify.label."""
        self._require_scope("gmail.modify.label")
        if not message_id:
            raise ValueError("message_id is required")
        if not label:
            raise ValueError("label is required")
        self._request("POST", f"/gmail/messages/{message_id}/labels", {"label": label})
        self._audit("gmail.apply_label", {"message_id": message_id, "label": label})

    def archive(self, message_id: str) -> None:
        """Archive a message. Requires: gmail.modify.archive."""
        self._require_scope("gmail.modify.archive")
        if not message_id:
            raise ValueError("message_id is required")
        self._request("POST", f"/gmail/messages/{message_id}/archive", None)
        self._audit("gmail.archive", {"message_id": message_id})

    def _require_scope(self, required_scope: str) -> None:
        if self._token is None:
            raise ScopeDeniedError("connector is not connected")
        scopes = self._token.get("scopes", [])
        if required_scope not in scopes:
            raise ScopeDeniedError(f"missing required scope: {required_scope}")

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if self._request_fn is None:
            raise RuntimeError(
                "No request_fn configured for GmailConnector. "
                "Inject request_fn for tests/integration wiring."
            )
        response = self._request_fn(method, path, payload)
        if not isinstance(response, dict):
            raise ValueError("request_fn must return dict response")
        return response

    def _audit(self, event: str, details: dict[str, Any]) -> None:
        if self._audit_fn is not None:
            self._audit_fn(event, details)

