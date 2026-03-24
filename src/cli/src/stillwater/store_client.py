from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class StoreClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _base_url(value: str | None = None) -> str:
    raw = value or os.environ.get("SOLACE_STORE_BASE_URL", "http://127.0.0.1:8090")
    return raw.rstrip("/")


def request_json(
    *,
    path: str,
    method: str = "GET",
    base_url: str | None = None,
    token: str | None = None,
    body: dict[str, Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    url = f"{_base_url(base_url)}{path}"
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=payload, method=method.upper())
    request.add_header("Accept", "application/json")
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        detail = raw
        try:
            parsed = json.loads(raw) if raw else {}
            detail = str(parsed.get("detail") or parsed)
        except Exception:
            detail = raw or str(exc)
        raise StoreClientError(
            f"{method.upper()} {path} failed: {exc.code} {detail}".strip(),
            status_code=exc.code,
        ) from exc
    except urllib.error.URLError as exc:
        raise StoreClientError(f"{method.upper()} {path} failed: {exc.reason}") from exc

    if not raw:
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"data": data}


def catalog_status(*, base_url: str | None = None, token: str | None = None, timeout: float = 10.0) -> dict[str, Any]:
    return request_json(path="/api/v1/store/catalog/status", base_url=base_url, token=token, timeout=timeout)


def list_apps(
    *,
    base_url: str | None = None,
    token: str | None = None,
    category: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    path = "/api/v1/store/apps"
    if category:
        path = f"{path}?category={urllib.parse.quote(category)}"
    return request_json(path=path, base_url=base_url, token=token, timeout=timeout)


def get_app(app_id: str, *, base_url: str | None = None, token: str | None = None, timeout: float = 10.0) -> dict[str, Any]:
    return request_json(path=f"/api/v1/store/apps/{app_id}", base_url=base_url, token=token, timeout=timeout)


def install_app(
    app_id: str,
    *,
    optional_scopes_enabled: list[str] | None = None,
    base_url: str | None = None,
    token: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    body = {"optional_scopes_enabled": list(optional_scopes_enabled or [])}
    return request_json(
        path=f"/api/v1/store/apps/{app_id}/install",
        method="POST",
        base_url=base_url,
        token=token,
        body=body,
        timeout=timeout,
    )


def uninstall_app(app_id: str, *, base_url: str | None = None, token: str | None = None, timeout: float = 10.0) -> dict[str, Any]:
    return request_json(
        path=f"/api/v1/store/apps/{app_id}/install",
        method="DELETE",
        base_url=base_url,
        token=token,
        timeout=timeout,
    )
