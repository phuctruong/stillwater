"""External connector interfaces for Stillwater."""

from .gmail import ConnectorBase, GmailConnector, ScopeDeniedError
from .email_sanitizer import sanitize_email_for_llm

__all__ = [
    "ConnectorBase",
    "GmailConnector",
    "ScopeDeniedError",
    "sanitize_email_for_llm",
]

