"""AdminClient — Thin-glue HTTP client for the Stillwater Admin Server.

Version: 1.0.0 | Rung: 641 | Status: STABLE

Maps every admin server endpoint 1:1 to a Python function.
Uses only stdlib (urllib.request, json) — no pip install required.

Admin server default: http://localhost:8787

Design principles:
- CLI = thin glue between webservices (NOT monolith)
- Each function maps 1:1 to one API endpoint
- Return typed dicts, not raw HTTP responses
- Raise AdminClientError on HTTP errors or server-returned ok=False
- Base URL and timeout configurable per-client or per-call
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

__all__ = [
    "AdminClient",
    "AdminClientError",
]

_DEFAULT_BASE_URL = "http://localhost:8787"
_DEFAULT_TIMEOUT = 10  # seconds


class AdminClientError(RuntimeError):
    """Raised when the admin server returns an error or HTTP failure.

    Attributes
    ----------
    status:
        HTTP status code (int), or 0 if a network-level error.
    payload:
        The parsed JSON response dict, if available.
    """

    def __init__(self, message: str, status: int = 0, payload: dict | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.payload = payload or {}


class AdminClient:
    """HTTP client for the Stillwater Admin Server.

    Parameters
    ----------
    base_url:
        Base URL of the admin server (default: ``http://localhost:8787``).
    timeout:
        Request timeout in seconds (default: 10).

    Examples
    --------
    >>> client = AdminClient()
    >>> catalog = client.get_catalog()
    >>> print(catalog["groups"])
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int | float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        """Build a full URL from a path."""
        return f"{self._base}{path}"

    def _get(self, path: str) -> dict:
        """Make a GET request; return parsed JSON dict.

        Raises AdminClientError on HTTP errors or network failures.
        """
        url = self._url(path)
        req = urllib.request.Request(url, method="GET")
        return self._send(req)

    def _post(self, path: str, body: dict) -> dict:
        """Make a POST request with JSON body; return parsed JSON dict.

        Raises AdminClientError on HTTP errors or network failures.
        """
        url = self._url(path)
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(data)),
            },
            method="POST",
        )
        return self._send(req)

    def _send(self, req: urllib.request.Request) -> dict:
        """Execute a request and return the parsed JSON payload.

        Raises AdminClientError for:
        - Network-level errors (connection refused, timeout, etc.)
        - Non-2xx HTTP responses
        - Responses where ok == False (server-side business logic errors)
        """
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            status = exc.code
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                payload = {"ok": False, "error": raw}
            error_msg = payload.get("error", f"HTTP {status}")
            raise AdminClientError(error_msg, status=status, payload=payload) from exc
        except urllib.error.URLError as exc:
            raise AdminClientError(
                f"Cannot connect to admin server at {self._base}: {exc.reason}",
                status=0,
            ) from exc
        except OSError as exc:
            raise AdminClientError(
                f"Network error: {exc}",
                status=0,
            ) from exc

        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise AdminClientError(
                f"Invalid JSON response (HTTP {status}): {raw[:200]}",
                status=status,
            ) from exc

        if not isinstance(payload, dict):
            raise AdminClientError(
                f"Expected JSON object, got {type(payload).__name__}",
                status=status,
                payload={},
            )

        if not payload.get("ok", False):
            error_msg = payload.get("error", f"Server returned ok=False (HTTP {status})")
            raise AdminClientError(error_msg, status=status, payload=payload)

        return payload

    # ------------------------------------------------------------------
    # GET /api/catalog
    # ------------------------------------------------------------------

    def get_catalog(self) -> dict:
        """List all catalog groups with their files.

        Returns
        -------
        dict with keys:
            ``ok`` (bool),
            ``groups`` (list[dict]) — each has id, title, files, count,
            ``extras`` (list[dict]) — extra editable files.
        """
        return self._get("/api/catalog")

    # ------------------------------------------------------------------
    # GET /api/file?path=X
    # ------------------------------------------------------------------

    def get_file(self, path: str) -> dict:
        """Read a file from the repo (allowed suffixes: .md .yaml .yml .json .toml .txt).

        Parameters
        ----------
        path:
            Repo-relative path, e.g. ``skills/prime-safety.md``.

        Returns
        -------
        dict with keys:
            ``ok``, ``path``, ``content`` (str), ``size`` (int), ``sha256`` (str).

        Raises
        ------
        AdminClientError
            If the path is disallowed, does not exist, or escapes the repo.
        """
        encoded = urllib.parse.urlencode({"path": path})
        return self._get(f"/api/file?{encoded}")

    # ------------------------------------------------------------------
    # POST /api/file/save
    # ------------------------------------------------------------------

    def save_file(self, path: str, content: str) -> dict:
        """Save (overwrite) a file in the repo.

        Parameters
        ----------
        path:
            Repo-relative path of the file to save.
        content:
            New UTF-8 content string.

        Returns
        -------
        dict with keys:
            ``ok``, ``path``, ``content``, ``size``, ``sha256``.

        Raises
        ------
        AdminClientError
            If the path is disallowed, escapes the repo, or content is too large.
        """
        return self._post("/api/file/save", {"path": path, "content": content})

    # ------------------------------------------------------------------
    # POST /api/file/create
    # ------------------------------------------------------------------

    def create_file(self, group: str, filename: str) -> dict:
        """Create a new file from the group template.

        Parameters
        ----------
        group:
            Catalog group id (e.g. ``root_skills``, ``swarms``, ``recipes``).
        filename:
            Filename without or with extension. Extension ``.md`` is added
            automatically if missing.

        Returns
        -------
        dict with keys:
            ``ok``, ``path`` (str), ``created`` (bool).

        Raises
        ------
        AdminClientError
            If group is unknown, filename has invalid characters, or file already exists.
        """
        return self._post("/api/file/create", {"group": group, "filename": filename})

    # ------------------------------------------------------------------
    # GET /api/llm/status
    # ------------------------------------------------------------------

    def get_llm_status(self) -> dict:
        """Get LLM provider status.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``status`` (dict) — contains provider, provider_name, provider_url,
            provider_model, setup_ok, setup_msg, probes, preferred_ollama_url,
            models, ollama_installed.
        """
        return self._get("/api/llm/status")

    # ------------------------------------------------------------------
    # POST /api/llm/config
    # ------------------------------------------------------------------

    def save_llm_config(
        self,
        provider: str = "",
        ollama_url: str = "",
        ollama_model: str = "",
    ) -> dict:
        """Save LLM configuration and return updated status.

        Parameters
        ----------
        provider:
            Provider name (e.g. ``ollama``, ``anthropic``).
        ollama_url:
            Ollama server URL (e.g. ``http://localhost:11434``).
        ollama_model:
            Ollama model name (e.g. ``llama3.3:70b``).

        Returns
        -------
        dict with keys:
            ``ok``, ``status`` (dict, same shape as get_llm_status).

        Raises
        ------
        AdminClientError
            If the llm config helper is unavailable on the server.
        """
        return self._post(
            "/api/llm/config",
            {
                "provider": provider,
                "ollama_url": ollama_url,
                "ollama_model": ollama_model,
            },
        )

    # ------------------------------------------------------------------
    # POST /api/system/install-ollama
    # ------------------------------------------------------------------

    def install_ollama(self, sudo_password: str) -> dict:
        """Trigger ollama installation on the server host.

        Parameters
        ----------
        sudo_password:
            Sudo password for the install script. Required if ollama is not
            already installed.

        Returns
        -------
        dict with keys:
            ``ok`` (bool), ``changed`` (bool), ``message`` (str),
            and optionally ``returncode``, ``stdout``, ``stderr``.
        """
        return self._post("/api/system/install-ollama", {"sudo_password": sudo_password})

    # ------------------------------------------------------------------
    # POST /api/ollama/pull
    # ------------------------------------------------------------------

    def pull_ollama_model(self, model: str, ollama_url: str = "") -> dict:
        """Pull an ollama model on the server host.

        Parameters
        ----------
        model:
            Model name to pull (e.g. ``llama3.3:70b``).
        ollama_url:
            Optional override for the ollama server URL.

        Returns
        -------
        dict with keys:
            ``ok`` (bool), ``message`` (str),
            ``returncode``, ``stdout``, ``stderr``.

        Raises
        ------
        AdminClientError
            If ollama is not installed or model name is empty.
        """
        return self._post("/api/ollama/pull", {"model": model, "ollama_url": ollama_url})

    # ------------------------------------------------------------------
    # GET /api/community/status
    # ------------------------------------------------------------------

    def get_community_status(self) -> dict:
        """Get community link status.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``community`` (dict) — contains linked, email, api_key,
            link_status, login_link_stub, sync_events.
        """
        return self._get("/api/community/status")

    # ------------------------------------------------------------------
    # POST /api/community/link
    # ------------------------------------------------------------------

    def community_link(self, email: str) -> dict:
        """Link a community account via email (stub/mock flow).

        Parameters
        ----------
        email:
            Valid email address.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``link`` (dict) — contains email, status, requested_at_utc,
            login_link_stub, api_key, note.

        Raises
        ------
        AdminClientError
            If the email is not a valid address format.
        """
        return self._post("/api/community/link", {"email": email})

    # ------------------------------------------------------------------
    # POST /api/community/sync
    # ------------------------------------------------------------------

    def community_sync(self, direction: str = "both") -> dict:
        """Sync skills/recipes with the community.

        Parameters
        ----------
        direction:
            Sync direction: ``"both"``, ``"upload"``, or ``"download"``.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``sync`` (dict) — contains timestamp_utc, direction, uploaded,
            remote_available, status.
        """
        return self._post("/api/community/sync", {"direction": direction})

    # ------------------------------------------------------------------
    # GET /api/cli/commands
    # ------------------------------------------------------------------

    def get_cli_commands(self) -> dict:
        """List allowed CLI commands that can be run via the admin server.

        Returns
        -------
        dict with keys:
            ``ok``, ``commands`` (list[str]).
        """
        return self._get("/api/cli/commands")

    # ------------------------------------------------------------------
    # POST /api/cli/run
    # ------------------------------------------------------------------

    def run_cli_command(self, command: str) -> dict:
        """Run an allowlisted CLI command on the server.

        Parameters
        ----------
        command:
            One of the allowed command names (e.g. ``"version"``, ``"doctor"``,
            ``"llm-status"``). Use :meth:`get_cli_commands` to list allowed names.

        Returns
        -------
        dict with keys:
            ``ok`` (bool),
            ``result`` (dict) — contains command, cmd, returncode, stdout, stderr, ok.

        Raises
        ------
        AdminClientError
            If the command is not in the allowlist.
        """
        return self._post("/api/cli/run", {"command": command})

    # ------------------------------------------------------------------
    # GET /api/services
    # ------------------------------------------------------------------

    def list_services(self) -> dict:
        """List all registered services.

        Returns
        -------
        dict with keys:
            ``ok``, ``services`` (list[dict]).

        Raises
        ------
        AdminClientError
            If the service registry is not available.
        """
        return self._get("/api/services")

    # ------------------------------------------------------------------
    # GET /api/services/{id}
    # ------------------------------------------------------------------

    def get_service(self, service_id: str) -> dict:
        """Get a specific registered service by ID.

        Parameters
        ----------
        service_id:
            The service identifier string.

        Returns
        -------
        dict with keys:
            ``ok``, ``service`` (dict).

        Raises
        ------
        AdminClientError
            If the service is not found (404) or registry is unavailable.
        """
        encoded_id = urllib.parse.quote(service_id, safe="")
        return self._get(f"/api/services/{encoded_id}")

    # ------------------------------------------------------------------
    # GET /api/services/{id}/health
    # ------------------------------------------------------------------

    def get_service_health(self, service_id: str) -> dict:
        """Health-check a specific registered service.

        Parameters
        ----------
        service_id:
            The service identifier string.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``health`` (dict) — contains service_id, status
            (``online`` | ``offline`` | ``degraded`` | ``starting``).
        """
        encoded_id = urllib.parse.quote(service_id, safe="")
        return self._get(f"/api/services/{encoded_id}/health")

    # ------------------------------------------------------------------
    # POST /api/services/register
    # ------------------------------------------------------------------

    def register_service(
        self,
        service_id: str,
        service_type: str,
        name: str,
        port: int,
        **extra: Any,
    ) -> dict:
        """Register a service with the admin server.

        Parameters
        ----------
        service_id:
            Unique service identifier.
        service_type:
            Service type string (e.g. ``"custom"``, ``"llm_portal"``).
        name:
            Human-readable service name.
        port:
            Port number the service listens on.
        **extra:
            Additional fields passed through to the registration payload.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``service`` (dict) — contains service_id, service_type, name,
            port, status, and additional descriptor fields.

        Raises
        ------
        AdminClientError
            If registration fails or the service registry is unavailable.
        """
        payload: dict = {
            "service_id": service_id,
            "service_type": service_type,
            "name": name,
            "port": port,
            **extra,
        }
        return self._post("/api/services/register", payload)

    # ------------------------------------------------------------------
    # POST /api/services/deregister
    # ------------------------------------------------------------------

    def deregister_service(self, service_id: str) -> dict:
        """Deregister a service from the admin server.

        Parameters
        ----------
        service_id:
            The service identifier to remove.

        Returns
        -------
        dict with keys:
            ``ok`` (bool, True if the service was removed, False if not found).

        Raises
        ------
        AdminClientError
            If the service registry is unavailable.
        """
        return self._post("/api/services/deregister", {"service_id": service_id})

    # ------------------------------------------------------------------
    # POST /api/services/discover
    # ------------------------------------------------------------------

    def discover_services(self) -> dict:
        """Auto-discover services on known ports.

        Returns
        -------
        dict with keys:
            ``ok``,
            ``discovery`` (dict) — contains discovered (list), failed_ports (list).

        Raises
        ------
        AdminClientError
            If the service registry is unavailable.
        """
        return self._post("/api/services/discover", {})
