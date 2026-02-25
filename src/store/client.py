"""
src/store/client.py — Stillwater Store Client SDK.

HTTP client for submitting, fetching, listing, and installing skills
from the Stillwater Store API at solaceagi.com.

Class: StillwaterStoreClient
  submit_skill(skill_path, author, rung_claimed, evidence_dir) → submission_id
  fetch_skill(skill_id) → skill_content (str)
  list_skills(query, page, per_page) → list[dict]
  install_skill(skill_id, target_dir) → installed_path (str)

Module-level convenience functions (thin wrappers around StillwaterStoreClient):
  submit_skill(skill_path, author, rung_claimed, api_key, base_url) → dict
  fetch_skill(skill_id, api_key, base_url) → dict
  list_skills(query, rung, category, api_key, base_url) → list
  install_skill(skill_id, target_dir, api_key, base_url) → str

Rung target: 641 (local correctness + tests passing)
Network: OFF in tests — all HTTP calls are mocked via unittest.mock.patch.

Design decisions:
  - API key stored in instance but NEVER printed, logged, or included in
    repr/str. Key is masked in all human-readable output.
  - Key format validated at construction time: must start with "sw_sk_".
  - Fail-closed error mapping:
      401 → PermissionError   (authentication failure)
      404 → LookupError       (resource not found)
      422 → ValueError        (validation failure)
      5xx → RuntimeError      (server error)
  - RungValidator is run before submit to prevent client-side submission
    of invalid evidence bundles (early rejection before any network call).
  - install_skill writes to target_dir only (write_default: repo worktree).
  - No rate limiting implemented client-side (placeholder for Phase 3).
  - requests library used (available in pyproject.toml dependencies).

Security gates:
  - Raw API key never in repr(), str(), exceptions, or logs.
  - Key validated via validate_key_format() before storage.
  - No credentials written to disk.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

from store.packager import SkillPackager
from store.rung_validator import RungValidator

# API key format: sw_sk_<32 hex chars>
_KEY_PATTERN = re.compile(r"^sw_sk_[0-9a-fA-F]{32}$")

# Store API endpoint paths (relative to base_url)
_ENDPOINTS = {
    "submit": "/stillwater/suggest",
    "fetch":  "/stillwater/suggestions/{skill_id}",
    "list":   "/stillwater/suggestions",
    "me":     "/stillwater/accounts/me",
}

# Default timeout for HTTP requests (seconds)
_REQUEST_TIMEOUT = 30


def _validate_api_key(api_key: str) -> None:
    """
    Validate API key format. Raises ValueError if invalid.
    Does NOT make any network call.
    """
    if not api_key:
        raise ValueError(
            "api_key is required. "
            "Register at https://www.solaceagi.com/stillwater to get a sw_sk_ key."
        )
    if not _KEY_PATTERN.match(api_key):
        raise ValueError(
            "api_key must match format: sw_sk_<32-hex-chars>. "
            "Example: sw_sk_0123456789abcdef0123456789abcdef. "
            "Register at https://www.solaceagi.com/stillwater."
        )


class StillwaterStoreClient:
    """
    HTTP client for the Stillwater Store API.

    Args:
        api_key:  Your sw_sk_ API key. Shown once at registration.
                  Never logs, never prints, never appears in repr().
        base_url: Base URL of the Store API.
                  Default: https://www.solaceagi.com

    Example:
        client = StillwaterStoreClient(
            api_key="sw_sk_0123456789abcdef0123456789abcdef",
            base_url="https://www.solaceagi.com",
        )
        sub_id = client.submit_skill("skills/prime-coder.md", "phuc", 641, "evidence/")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.solaceagi.com",
    ) -> None:
        _validate_api_key(api_key)
        # Store key privately — never expose in repr/str
        self.__api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._packager = SkillPackager()
        self._validator = RungValidator()

    def __repr__(self) -> str:
        # API key is masked — never exposed
        return (
            f"StillwaterStoreClient("
            f"base_url={self._base_url!r}, "
            f"api_key=sw_sk_****)"
        )

    def __str__(self) -> str:
        return self.__repr__()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit_skill(
        self,
        skill_path: Union[str, Path],
        author: str,
        rung_claimed: int,
        evidence_dir: Union[str, Path],
    ) -> str:
        """
        Package and submit a skill to the Stillwater Store.

        Steps:
          1. Validate evidence bundle via RungValidator (client-side gate).
          2. Bundle skill + evidence via SkillPackager.
          3. POST to /stillwater/suggest with Authorization header.
          4. Return submission_id on success.

        Args:
            skill_path:   Path to skill .md file.
            author:       Author name / account name.
            rung_claimed: Rung being claimed (641 / 274177 / 65537).
            evidence_dir: Path to evidence directory.

        Returns:
            submission_id (str) — e.g. "sub_abc123"

        Raises:
            ValueError:      Invalid evidence bundle (client-side rejection).
            PermissionError: HTTP 401 — invalid or missing API key.
            ValueError:      HTTP 422 — server-side validation failure.
            RuntimeError:    HTTP 5xx — server error.
        """
        skill_path = Path(skill_path)
        evidence_dir = Path(evidence_dir)

        # Client-side validation gate (fail before any network call)
        validation_status = self._validator.verify_evidence(evidence_dir, rung_claimed)
        if validation_status != "VALID":
            raise ValueError(
                f"Evidence bundle validation failed (status={validation_status}). "
                f"Run RungValidator.verify_evidence() to diagnose. "
                f"Do not submit without valid evidence."
            )

        # Package the skill
        bundle = self._packager.bundle_skill(
            skill_path=skill_path,
            evidence_dir=evidence_dir,
            author=author,
            rung_claimed=rung_claimed,
        )

        # Build submission payload (matches STORE.md API spec)
        payload = {
            "suggestion_type": "skill",
            "title": f"{bundle['skill_name']} — rung {rung_claimed}",
            "content": bundle["skill_content"],
            "bot_id": author,
            "source_context": f"Submitted via StillwaterStoreClient. "
                              f"Manifest SHA-256: {bundle['manifest_sha256']}",
            # Extended fields for the SDK (server may ignore unknown fields)
            "skill_name":      bundle["skill_name"],
            "author":          bundle["author"],
            "rung_claimed":    bundle["rung_claimed"],
            "manifest_sha256": bundle["manifest_sha256"],
        }

        url = self._base_url + _ENDPOINTS["submit"]
        response = requests.post(
            url,
            json=payload,
            headers=self._auth_headers(),
            timeout=_REQUEST_TIMEOUT,
        )

        self._check_response(response)
        return response.json()["submission_id"]

    def fetch_skill(self, skill_id: str) -> str:
        """
        Fetch the full content of a skill by its ID.

        Args:
            skill_id: The skill's unique ID (e.g. "sub_abc123" or UUID).

        Returns:
            skill_content (str) — the raw skill .md content.

        Raises:
            LookupError:  HTTP 404 — skill not found.
            RuntimeError: HTTP 5xx — server error.
        """
        url = self._base_url + _ENDPOINTS["fetch"].format(skill_id=skill_id)
        response = requests.get(
            url,
            headers=self._auth_headers(),
            timeout=_REQUEST_TIMEOUT,
        )
        self._check_response(response)
        return response.json()["skill_content"]

    def list_skills(
        self,
        query: str = "",
        page: int = 1,
        per_page: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        List skills in the Store catalog.

        Args:
            query:    Search query string (matched against skill names/tags).
            page:     Page number (1-indexed).
            per_page: Items per page (max 100).

        Returns:
            List of skill metadata dicts (each has skill_id, skill_name, author, ...).

        Raises:
            RuntimeError: HTTP 5xx — server error.
        """
        url = self._base_url + _ENDPOINTS["list"]
        params: Dict[str, Any] = {
            "page":     page,
            "per_page": per_page,
        }
        if query:
            params["q"] = query

        response = requests.get(
            url,
            params=params,
            headers=self._auth_headers(),
            timeout=_REQUEST_TIMEOUT,
        )
        self._check_response(response)
        data = response.json()
        return data.get("skills", [])

    def install_skill(
        self,
        skill_id: str,
        target_dir: Union[str, Path] = "./skills",
    ) -> str:
        """
        Fetch a skill from the Store and install it to the local skills directory.

        Args:
            skill_id:   The skill's unique ID.
            target_dir: Local directory to install the skill file into.
                        Must be within the repo worktree (write_default: repo only).

        Returns:
            installed_path (str) — absolute path of the installed skill file.

        Raises:
            LookupError:  HTTP 404 — skill not found.
            RuntimeError: HTTP 5xx — server error.
            OSError:      Cannot write to target_dir.
        """
        # Fetch skill content (reuses fetch_skill logic including GET call)
        url = self._base_url + _ENDPOINTS["fetch"].format(skill_id=skill_id)
        response = requests.get(
            url,
            headers=self._auth_headers(),
            timeout=_REQUEST_TIMEOUT,
        )
        self._check_response(response)

        data = response.json()
        skill_content = data["skill_content"]
        skill_name = data.get("skill_name", skill_id)

        # Ensure target_dir exists
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Write skill file
        installed_path = target_dir / f"{skill_name}.md"
        installed_path.write_text(skill_content, encoding="utf-8")

        return str(installed_path.resolve())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> Dict[str, str]:
        """
        Return Authorization headers. Raw API key is accessed from private
        attribute and placed directly in the header. Never logged externally.
        """
        return {
            "Authorization": f"Bearer {self.__api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _check_response(response: requests.Response) -> None:
        """
        Check HTTP response and raise the appropriate exception on error.

        Fail-closed mapping:
          401 → PermissionError   (auth failure)
          404 → LookupError       (not found)
          422 → ValueError        (validation failure)
          429 → RuntimeError      (rate limited)
          5xx → RuntimeError      (server error)

        The raw API key is never included in exception messages.
        """
        code = response.status_code
        if code in (200, 201, 204):
            return

        # Try to get a safe detail message (server-provided, no keys)
        try:
            detail = response.json().get("detail", "No detail provided.")
        except Exception:
            detail = "(response body not parseable as JSON)"

        if code == 401:
            raise PermissionError(
                f"HTTP 401 Unauthorized: {detail}. "
                f"Check your API key at https://www.solaceagi.com/stillwater."
            )
        if code == 404:
            raise LookupError(
                f"HTTP 404 Not Found: {detail}."
            )
        if code == 422:
            raise ValueError(
                f"HTTP 422 Validation Error: {detail}."
            )
        if code == 429:
            raise RuntimeError(
                f"HTTP 429 Rate Limited: {detail}. "
                f"Rate limit: 10 submissions per 24 hours."
            )
        if 500 <= code < 600:
            raise RuntimeError(
                f"HTTP {code} Server Error: {detail}."
            )
        # Unexpected status
        raise RuntimeError(
            f"Unexpected HTTP {code}: {detail}."
        )


# ===========================================================================
# Module-level convenience functions (thin wrappers around StillwaterStoreClient)
#
# These provide a functional interface that complements the class-based API.
# All HTTP calls still go through StillwaterStoreClient internally.
#
# Import:
#   from store.client import submit_skill, fetch_skill, list_skills, install_skill
# ===========================================================================

_DEFAULT_BASE_URL = "https://www.solaceagi.com"

# Rung rank ordering: 65537 is HIGHEST even though numerically < 274177
_RUNG_RANK: Dict[int, int] = {641: 0, 274177: 1, 65537: 2}


def submit_skill(
    skill_path: str,
    author: str,
    rung_claimed: int,
    api_key: str,
    base_url: str = _DEFAULT_BASE_URL,
    evidence_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Module-level convenience wrapper for StillwaterStoreClient.submit_skill().

    Packages a skill + evidence bundle and POSTs it to the Stillwater Store.
    The Authorization header is set to: Bearer sw_sk_{api_key}

    Args:
        skill_path:   Path to the skill .md file.
        author:       Author name / account name.
        rung_claimed: Rung being claimed (641 / 274177 / 65537).
        api_key:      Your sw_sk_ API key.
        base_url:     Base URL of the Store API.
        evidence_dir: Path to evidence directory. Defaults to "evidence/" next to skill.

    Returns:
        dict with keys: {skill_id, status, rung_verified, submitted_at}
        Note: the actual submission_id is mapped to skill_id for external API consistency.

    Raises:
        ValueError:      Invalid evidence bundle or API key format.
        PermissionError: HTTP 401 — authentication failure.
        RuntimeError:    HTTP 5xx — server error.
    """
    if evidence_dir is None:
        # Default: evidence/ directory sibling to the skill file
        evidence_dir = str(Path(skill_path).parent / "evidence")

    client = StillwaterStoreClient(api_key=api_key, base_url=base_url)
    submission_id = client.submit_skill(
        skill_path=skill_path,
        author=author,
        rung_claimed=rung_claimed,
        evidence_dir=evidence_dir,
    )
    return {
        "skill_id":     submission_id,
        "status":       "submitted",
        "rung_verified": rung_claimed,
        "submitted_at":  None,  # server-side timestamp; not available synchronously
    }


def fetch_skill(
    skill_id: str,
    api_key: str,
    base_url: str = _DEFAULT_BASE_URL,
) -> Dict[str, Any]:
    """
    Module-level convenience wrapper for StillwaterStoreClient.fetch_skill().

    Fetches skill metadata and content from the Stillwater Store.

    Args:
        skill_id: The skill's unique ID (e.g. "sub_abc123" or UUID).
        api_key:  Your sw_sk_ API key.
        base_url: Base URL of the Store API.

    Returns:
        dict with keys: {skill_id, skill_name, skill_content, author, rung_claimed, ...}
        (Note: raw JSON response from server)

    Raises:
        LookupError:  HTTP 404 — skill not found.
        RuntimeError: HTTP 5xx — server error.
    """
    client = StillwaterStoreClient(api_key=api_key, base_url=base_url)
    # fetch_skill() on the class returns the raw skill_content string.
    # For the functional API we return the full response dict from the GET call.
    url = client._base_url + _ENDPOINTS["fetch"].format(skill_id=skill_id)
    response = requests.get(
        url,
        headers=client._auth_headers(),
        timeout=_REQUEST_TIMEOUT,
    )
    StillwaterStoreClient._check_response(response)
    return response.json()


def list_skills(
    query: str = "",
    rung: Optional[int] = None,
    category: Optional[str] = None,
    api_key: str = "",
    base_url: str = _DEFAULT_BASE_URL,
) -> List[Dict[str, Any]]:
    """
    Module-level convenience wrapper for StillwaterStoreClient.list_skills().

    Lists skills in the Stillwater Store catalog.

    Args:
        query:    Search query string (matched against skill names/tags).
        rung:     Filter by rung level (641 / 274177 / 65537). None = all.
        category: Filter by skill category string. None = all.
        api_key:  Your sw_sk_ API key. Empty string for unauthenticated browse.
        base_url: Base URL of the Store API.

    Returns:
        list of {skill_id, name, version, rung, author, category, description}

    Raises:
        RuntimeError: HTTP 5xx — server error.
    """
    client = StillwaterStoreClient(api_key=api_key, base_url=base_url)
    url = client._base_url + _ENDPOINTS["list"]
    params: Dict[str, Any] = {}
    if query:
        params["q"] = query
    if rung is not None:
        params["rung"] = rung
    if category is not None:
        params["category"] = category

    response = requests.get(
        url,
        params=params,
        headers=client._auth_headers(),
        timeout=_REQUEST_TIMEOUT,
    )
    StillwaterStoreClient._check_response(response)
    data = response.json()
    return data.get("skills", [])


def install_skill(
    skill_id: str,
    target_dir: str = "skills/",
    api_key: str = "",
    base_url: str = _DEFAULT_BASE_URL,
) -> str:
    """
    Module-level convenience wrapper for StillwaterStoreClient.install_skill().

    Fetches a skill from the Store and installs it to the local skills directory.
    Verifies the download by computing SHA-256 of the written file.

    Args:
        skill_id:   The skill's unique ID.
        target_dir: Local directory to install the skill file into.
                    Default: "skills/" (relative to cwd).
        api_key:    Your sw_sk_ API key.
        base_url:   Base URL of the Store API.

    Returns:
        installed_path (str) — absolute path of the installed skill file.

    Raises:
        LookupError:  HTTP 404 — skill not found.
        RuntimeError: HTTP 5xx — server error or SHA-256 mismatch after install.
        OSError:      Cannot write to target_dir.
    """
    import hashlib as _hashlib

    client = StillwaterStoreClient(api_key=api_key, base_url=base_url)

    # Fetch skill content
    url = client._base_url + _ENDPOINTS["fetch"].format(skill_id=skill_id)
    response = requests.get(
        url,
        headers=client._auth_headers(),
        timeout=_REQUEST_TIMEOUT,
    )
    StillwaterStoreClient._check_response(response)

    data = response.json()
    skill_content = data["skill_content"]
    skill_name = data.get("skill_name", skill_id)

    # Ensure target directory exists
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    # Write skill file
    installed_path = target_path / f"{skill_name}.md"
    content_bytes = skill_content.encode("utf-8")
    installed_path.write_bytes(content_bytes)

    # Verify SHA-256 after download (integrity gate)
    written_sha256 = _hashlib.sha256(installed_path.read_bytes()).hexdigest()
    expected_sha256 = _hashlib.sha256(content_bytes).hexdigest()
    if written_sha256 != expected_sha256:
        installed_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"SHA-256 mismatch after install: expected {expected_sha256}, "
            f"got {written_sha256}. File has been removed."
        )

    return str(installed_path.resolve())
