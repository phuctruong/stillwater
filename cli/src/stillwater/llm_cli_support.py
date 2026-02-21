from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

import requests


def _norm_url(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return ""
    if "://" not in s:
        s = f"http://{s}"
    return s.rstrip("/")


def _dedupe_keep_order(values: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for raw in values:
        v = _norm_url(raw)
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


def _split_urls(value: str) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _load_llm_config(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / "llm_config.yaml"
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if isinstance(data, dict):
        return data
    return {}


def _solace_remote_url(solace_settings_path: Path) -> str:
    if not solace_settings_path.exists():
        return ""
    try:
        payload = json.loads(solace_settings_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    if not isinstance(payload, dict):
        return ""
    host = str(payload.get("ollama_host", "")).strip()
    port = payload.get("ollama_port")
    if not host:
        return ""
    try:
        port_int = int(port)
    except Exception:
        port_int = 11434
    return _norm_url(f"http://{host}:{port_int}")


def candidate_ollama_urls(
    *,
    repo_root: Path,
    explicit_urls: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    solace_settings_path: Optional[Path] = None,
) -> List[str]:
    e = env if env is not None else os.environ
    urls: List[str] = []

    # Caller intent first.
    if explicit_urls:
        urls.extend(explicit_urls)

    # Local defaults are always first-class.
    urls.extend(
        [
            e.get("STILLWATER_OLLAMA_URL", ""),
            "http://localhost:11434",
            "http://127.0.0.1:11434",
        ]
    )

    # Env-compatible remote hints.
    if e.get("SOLACE_OLLAMA_HOST", "").strip():
        port = e.get("SOLACE_OLLAMA_PORT", "11434").strip() or "11434"
        urls.append(f"http://{e['SOLACE_OLLAMA_HOST'].strip()}:{port}")
    if e.get("OLLAMA_HOST", "").strip():
        port = e.get("OLLAMA_PORT", "11434").strip() or "11434"
        urls.append(f"http://{e['OLLAMA_HOST'].strip()}:{port}")

    # llm_config.yaml ollama.url and override urls from env list.
    cfg = _load_llm_config(repo_root)
    ollama_cfg = cfg.get("ollama", {}) if isinstance(cfg.get("ollama"), dict) else {}
    urls.append(str(ollama_cfg.get("url", "")).strip())
    urls.extend(_split_urls(e.get("STILLWATER_OLLAMA_URLS", "")))

    # Solace remote reference if available.
    default_solace = Path.home() / "projects" / "solace-cli" / "solace_cli" / "settings.json"
    remote = _solace_remote_url(solace_settings_path or default_solace)
    if remote:
        urls.append(remote)

    return _dedupe_keep_order(urls)


def probe_ollama_url(*, url: str, timeout_seconds: float = 2.0) -> Dict[str, Any]:
    u = _norm_url(url)
    started = requests.get(f"{u}/api/tags", timeout=timeout_seconds)
    started.raise_for_status()
    payload = started.json()
    models_raw = payload.get("models", []) if isinstance(payload, dict) else []
    models: List[str] = []
    if isinstance(models_raw, list):
        for m in models_raw:
            if isinstance(m, dict) and isinstance(m.get("name"), str):
                models.append(m["name"])
    models = sorted(set(models))
    p = urlparse(u)
    host = p.hostname or ""
    return {
        "url": u,
        "reachable": True,
        "host": host,
        "model_count": len(models),
        "models": models,
    }


def probe_ollama_urls(*, urls: List[str], timeout_seconds: float = 2.0) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for raw in urls:
        u = _norm_url(raw)
        if not u:
            continue
        try:
            out.append(probe_ollama_url(url=u, timeout_seconds=timeout_seconds))
        except Exception as ex:
            p = urlparse(u)
            out.append(
                {
                    "url": u,
                    "reachable": False,
                    "host": p.hostname or "",
                    "model_count": 0,
                    "models": [],
                    "error": str(ex),
                }
            )
    return out


def choose_preferred_ollama_url(probes: List[Dict[str, Any]]) -> str:
    for p in probes:
        if p.get("reachable") and p.get("host") in {"localhost", "127.0.0.1"}:
            return str(p["url"])
    for p in probes:
        if p.get("reachable"):
            return str(p["url"])
    return ""


def update_llm_config_text(
    text: str,
    *,
    provider: Optional[str] = None,
    ollama_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
) -> str:
    lines = text.splitlines()

    def replace_top_level_scalar(key: str, value: str) -> None:
        prefix = f"{key}:"
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                lines[i] = f'{key}: "{value}"'
                return
        lines.insert(0, f'{key}: "{value}"')

    def replace_section_scalar(section: str, key: str, value: str) -> None:
        section_header = f"{section}:"
        sec_start = -1
        for i, line in enumerate(lines):
            if line.startswith(section_header):
                sec_start = i
                break
        if sec_start < 0:
            lines.extend(["", section_header, f'  {key}: "{value}"'])
            return

        sec_end = len(lines)
        for i in range(sec_start + 1, len(lines)):
            line = lines[i]
            if line and not line[0].isspace() and line.endswith(":"):
                sec_end = i
                break

        key_prefix = f"  {key}:"
        for i in range(sec_start + 1, sec_end):
            if lines[i].startswith(key_prefix):
                lines[i] = f'  {key}: "{value}"'
                return

        lines.insert(sec_start + 1, f'  {key}: "{value}"')

    if provider:
        replace_top_level_scalar("provider", provider)
    if ollama_url:
        replace_section_scalar("ollama", "url", _norm_url(ollama_url))
    if ollama_model:
        replace_section_scalar("ollama", "model", ollama_model.strip())

    return "\n".join(lines).rstrip("\n") + "\n"


def update_llm_config_file(
    *,
    repo_root: Path,
    provider: Optional[str] = None,
    ollama_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
) -> Path:
    path = repo_root / "llm_config.yaml"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    new = update_llm_config_text(
        old,
        provider=provider,
        ollama_url=ollama_url,
        ollama_model=ollama_model,
    )
    path.write_text(new, encoding="utf-8")
    return path
