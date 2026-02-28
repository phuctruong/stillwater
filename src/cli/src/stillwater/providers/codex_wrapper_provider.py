"""
Stillwater Codex Wrapper Provider
Version: 1.0.0

Thin provider over the local Codex wrapper webservice.
"""

from __future__ import annotations

import os

from .http_provider import HTTPProvider


class CodexWrapperProvider(HTTPProvider):
    """HTTP provider preset for the local Codex CLI wrapper."""

    def __init__(self, url: str | None = None, **kwargs):
        resolved_url = url or os.environ.get("CODEX_WRAPPER_URL", "http://localhost:8081")
        super().__init__(url=resolved_url, **kwargs)

    @property
    def name(self) -> str:
        return "codex-wrapper"
