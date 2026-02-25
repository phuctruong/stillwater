"""
Stdlib-only HTTP helpers for LLM providers.
Version: 1.0.0

Uses only urllib.request and http.client from the standard library.
Zero external dependencies.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any


class HTTPError(Exception):
    """Raised when an HTTP request fails."""
    def __init__(self, status_code: int, body: str, url: str) -> None:
        self.status_code = status_code
        self.body = body
        self.url = url
        super().__init__(f"HTTP {status_code} from {url}: {body[:200]}")


def http_post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    POST JSON payload to URL, return parsed JSON response.

    Args:
        url: Full URL to POST to.
        payload: Dict to serialize as JSON body.
        headers: Additional headers (Content-Type is always set).
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        HTTPError: On non-2xx status.
        json.JSONDecodeError: If response is not valid JSON.
        urllib.error.URLError: On network errors.
    """
    data = json.dumps(payload).encode("utf-8")
    all_headers = {"Content-Type": "application/json"}
    if headers:
        all_headers.update(headers)

    req = urllib.request.Request(url, data=data, headers=all_headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            pass
        raise HTTPError(exc.code, body, url) from exc


def http_get_json(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    GET URL and return parsed JSON response.

    Args:
        url: Full URL to GET.
        headers: Additional headers.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        HTTPError: On non-2xx status.
    """
    all_headers = {}
    if headers:
        all_headers.update(headers)

    req = urllib.request.Request(url, headers=all_headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            pass
        raise HTTPError(exc.code, body, url) from exc
