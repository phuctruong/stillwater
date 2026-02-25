"""Email sanitization helpers for untrusted inbox content."""

from __future__ import annotations

import html
import re
from typing import Any


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_BASE64_BLOB_RE = re.compile(r"[A-Za-z0-9+/]{80,}={0,2}")
_URL_RE = re.compile(r"\b(?:https?|ftp|file)://[^\s<>{}\"]+")

_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("inst_tag", re.compile(r"\[INST\]", re.IGNORECASE)),
    ("im_start", re.compile(r"<\|im_start\|>", re.IGNORECASE)),
    ("im_end", re.compile(r"<\|im_end\|>", re.IGNORECASE)),
    ("ignore_instructions", re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE)),
    ("system_override", re.compile(r"system\s+prompt", re.IGNORECASE)),
]


def _strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub(" ", text)


def _escape_structural_chars(text: str) -> str:
    # Neutralize prompt-structure symbols frequently used in injection payloads.
    return (
        text.replace("{", "\\{")
        .replace("}", "\\}")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _sanitize_text(text: str, *, truncate: int = 500) -> tuple[str, list[str]]:
    if not isinstance(text, str):
        text = ""

    detected: list[str] = []
    working = html.unescape(text)
    working = _strip_html(working)
    working = _BASE64_BLOB_RE.sub("[ATTACHMENT_REDACTED]", working)

    def _replace_url(match: re.Match[str]) -> str:
        url = match.group(0)
        if url.lower().startswith("https://"):
            return "[LINK]"
        return "[URL_REDACTED]"

    working = _URL_RE.sub(_replace_url, working)

    for name, pattern in _INJECTION_PATTERNS:
        if pattern.search(working):
            detected.append(name)
            working = pattern.sub("[INJECTION_REDACTED]", working)

    working = _escape_structural_chars(working)
    working = re.sub(r"\s+", " ", working).strip()
    if truncate > 0:
        working = working[:truncate]
    return working, detected


def sanitize_email_for_llm(email: dict[str, Any]) -> dict[str, Any]:
    """Return sanitized email payload safe for classification prompts.

    Output fields:
      - subject_sanitized
      - snippet_sanitized
      - body_sanitized
      - from_sanitized
      - quarantine
      - injection_patterns_removed
    """
    if not isinstance(email, dict):
        raise TypeError("email must be a dict")

    subject, subj_hits = _sanitize_text(str(email.get("subject", "")), truncate=200)
    snippet, snip_hits = _sanitize_text(str(email.get("snippet", "")), truncate=500)
    body, body_hits = _sanitize_text(str(email.get("body", "")), truncate=500)
    from_s, from_hits = _sanitize_text(str(email.get("from", "")), truncate=200)

    hits = sorted(set(subj_hits + snip_hits + body_hits + from_hits))
    out = dict(email)
    out.update(
        {
            "subject_sanitized": subject,
            "snippet_sanitized": snippet,
            "body_sanitized": body,
            "from_sanitized": from_s,
            "quarantine": bool(hits),
            "injection_patterns_removed": hits,
        }
    )
    return out

