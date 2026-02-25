#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import webbrowser
try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

try:
    from services.registry import ServiceRegistry
    from services.models import ServiceRegistration, ServiceType
    _SERVICE_REGISTRY = ServiceRegistry()
    _SERVICE_REGISTRY.load()
except Exception:  # pragma: no cover
    _SERVICE_REGISTRY = None  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))

try:
    from llm_config_manager import get_llm_config
except Exception:  # pragma: no cover
    get_llm_config = None  # type: ignore

try:
    from stillwater.llm_cli_support import (
        candidate_ollama_urls,
        choose_preferred_ollama_url,
        probe_ollama_urls,
        update_llm_config_file,
    )
except Exception:  # pragma: no cover
    candidate_ollama_urls = None  # type: ignore
    choose_preferred_ollama_url = None  # type: ignore
    probe_ollama_urls = None  # type: ignore
    update_llm_config_file = None  # type: ignore


CATALOG_GROUPS = [
    {
        "id": "root_skills",
        "title": "Skills",
        "dirs": ["data/default/skills"],
        "patterns": ["*.md"],
        "create_template": "---\nskill_id: new-skill\nversion: 1.0.0\n---\n\n# New Skill\n",
    },
    {
        "id": "swarms",
        "title": "Swarm Agents",
        "dirs": ["data/default/swarms"],
        "patterns": ["**/*.md"],
        "create_template": "---\nagent_type: new-agent\nversion: 1.0.0\n---\n\n# New Swarm Agent\n",
    },
    {
        "id": "root_recipes",
        "title": "Recipes",
        "dirs": ["data/default/recipes"],
        "patterns": ["*.md"],
        "create_template": "---\nid: recipe.new\nversion: 1.0.0\n---\n\n# New Recipe\n",
    },
    {
        "id": "papers",
        "title": "Papers",
        "dirs": ["papers"],
        "patterns": ["*.md"],
        "create_template": "# New Paper\n\n## Abstract\n\n## Introduction\n",
    },
    {
        "id": "community",
        "title": "Community Docs",
        "dirs": ["community"],
        "patterns": ["*.md"],
        "create_template": "# Community Doc\n",
    },
    {
        "id": "recipes",
        "title": "CLI Recipes",
        "dirs": ["src/cli/recipes", "src/cli/extensions/recipes"],
        "patterns": ["*.md"],
        "create_template": "# Recipe\n\n```mermaid\nflowchart TD\n  START --> END\n```\n",
    },
    {
        "id": "skills",
        "title": "CLI Skills",
        "dirs": ["src/cli/extensions/skills"],
        "patterns": ["*.md"],
        "create_template": "# New Skill\n\nDescribe capability and constraints.\n",
    },
    {
        "id": "personas",
        "title": "Personas",
        "dirs": ["src/cli/extensions/personas"],
        "patterns": ["*.md"],
        "create_template": "# Persona\n\nStyle:\n- concise\n- evidence-first\n",
    },
    {
        "id": "identity",
        "title": "Identity",
        "dirs": ["src/cli/identity", "src/cli/extensions/identity"],
        "patterns": ["*.md"],
        "create_template": "# Identity Note\n\nPurpose:\n- ...\n",
    },
    {
        "id": "settings",
        "title": "Settings",
        "dirs": ["src/cli/settings"],
        "patterns": ["*.md"],
        "create_template": "# Setting\n\nSETTING key = value\n",
    },
]

EXTRA_EDITABLE_FILES = [
    "llm_config.yaml",
    "src/cli/extensions/splash.txt",
    "CLAUDE.md",
    "admin/README.md",
]

ALLOWED_WRITE_SUFFIXES = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
}

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "admin"
COMMUNITY_LINK_FILE = ARTIFACT_DIR / "community_link.json"
COMMUNITY_SYNC_LOG = ARTIFACT_DIR / "community_sync.jsonl"
CLOUD_CONFIG_PATHS = (
    REPO_ROOT / "data" / "custom" / "solaceagi-config.yaml",
    REPO_ROOT / "data" / "custom" / "solace_agi_config.yaml",
    REPO_ROOT / "data" / "default" / "solace_agi_config.yaml",
)
DEFAULT_CLOUD_API_URL = "https://www.solaceagi.com/api/v1"

MAX_BODY_SIZE = 2_000_000  # 2 MB — reject request bodies larger than this
COMMUNITY_SYNC_TAIL = 100  # max JSONL lines read from community sync log
SWARMS_ROOT = REPO_ROOT / "data" / "default" / "swarms"
SKILLS_ROOT = REPO_ROOT / "data" / "default" / "skills"
RECIPES_ROOT = REPO_ROOT / "data" / "default" / "recipes"
PERSONAS_ROOT = REPO_ROOT / "data" / "default" / "personas"


def _utc_now() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _all_catalog_dirs() -> list[Path]:
    out: list[Path] = []
    for group in CATALOG_GROUPS:
        for raw in group["dirs"]:
            out.append((REPO_ROOT / raw).resolve())
    return out


def _allowed_paths() -> list[Path]:
    out = _all_catalog_dirs()
    for rel in EXTRA_EDITABLE_FILES:
        out.append((REPO_ROOT / rel).resolve())
    return out


def _safe_resolve_repo_path(raw: str) -> Path:
    candidate = (REPO_ROOT / raw).resolve()
    try:
        candidate.relative_to(REPO_ROOT.resolve())
    except ValueError:
        raise ValueError("path escapes repo")
    return candidate


def _is_allowed_edit_path(path: Path) -> bool:
    resolved = path.resolve()
    if resolved.suffix.lower() not in ALLOWED_WRITE_SUFFIXES:
        return False
    for allowed in _allowed_paths():
        if allowed.is_file() and resolved == allowed:
            return True
        if allowed.is_dir():
            try:
                resolved.relative_to(allowed)
                return True
            except ValueError:
                pass
    return False


def _catalog() -> dict:
    groups: list[dict] = []
    for group in CATALOG_GROUPS:
        files: list[dict] = []
        for raw_dir in group["dirs"]:
            base = (REPO_ROOT / raw_dir).resolve()
            if not base.exists():
                continue
            for pattern in group["patterns"]:
                for file_path in sorted(base.glob(pattern)):
                    if not file_path.is_file():
                        continue
                    rel = str(file_path.relative_to(REPO_ROOT))
                    files.append(
                        {
                            "path": rel,
                            "name": file_path.name,
                            "group": group["id"],
                            "dir": raw_dir,
                        }
                    )
        files = sorted(files, key=lambda row: row["path"])
        groups.append(
            {
                "id": group["id"],
                "title": group["title"],
                "files": files,
                "count": len(files),
            }
        )
    extras: list[dict] = []
    for rel in EXTRA_EDITABLE_FILES:
        path = REPO_ROOT / rel
        if path.exists():
            extras.append({"path": rel, "name": path.name, "group": "extras", "dir": str(path.parent.relative_to(REPO_ROOT))})
    return {"groups": groups, "extras": extras}


def _require_yaml() -> None:
    if yaml is None:
        raise RuntimeError("pyyaml is required for swarm studio endpoints")


def _iter_markdown_rows(base_dir: Path, *, recursive: bool = True) -> list[dict[str, str]]:
    if not base_dir.exists():
        return []
    iterator = base_dir.rglob("*.md") if recursive else base_dir.glob("*.md")
    rows: list[dict[str, str]] = []
    for file_path in sorted(iterator):
        if not file_path.is_file():
            continue
        if file_path.name.startswith("README"):
            continue
        rel_repo = file_path.relative_to(REPO_ROOT)
        rel_base = file_path.relative_to(base_dir)
        category = rel_base.parent.as_posix() if rel_base.parent.as_posix() != "." else ""
        rows.append(
            {
                "id": file_path.stem,
                "name": file_path.stem.replace("-", " ").title(),
                "path": str(rel_repo),
                "category": category,
            },
        )
    return rows


def _slugify_token(value: str) -> str:
    cleaned = re.sub(r"\(.*?\)", "", value).strip()
    cleaned = cleaned.split(",", 1)[0].strip()
    return re.sub(r"[^a-z0-9]+", "-", cleaned.lower()).strip("-")


def _split_frontmatter(markdown: str) -> tuple[dict, str]:
    _require_yaml()
    normalized = markdown.replace("\r\n", "\n")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", normalized, flags=re.DOTALL)
    if not match:
        raise ValueError("missing yaml frontmatter")
    raw_frontmatter = match.group(1)
    body = match.group(2)
    parsed = yaml.safe_load(raw_frontmatter)  # type: ignore[arg-type]
    if not isinstance(parsed, dict):
        raise ValueError("frontmatter must be a mapping")
    return parsed, body


def _dump_frontmatter(frontmatter: dict) -> str:
    _require_yaml()
    payload = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=False).strip()  # type: ignore[arg-type]
    return f"---\n{payload}\n---\n"


def _frontmatter_to_spec(
    swarm_id: str,
    category: str,
    rel_path: str,
    frontmatter: dict,
) -> dict[str, object]:
    persona = frontmatter.get("persona", {})
    persona_primary = ""
    persona_alternatives: list[str] = []
    if isinstance(persona, dict):
        if isinstance(persona.get("primary"), str):
            persona_primary = str(persona.get("primary")).strip()
        alt = persona.get("alternatives")
        if isinstance(alt, list):
            persona_alternatives = [str(v).strip() for v in alt if str(v).strip()]
    elif isinstance(persona, str):
        persona_primary = persona.strip()

    skill_pack = frontmatter.get("skill_pack") or []
    if not isinstance(skill_pack, list):
        skill_pack = []
    skills = [str(v).strip() for v in skill_pack if str(v).strip()]

    recipes = frontmatter.get("recipes")
    if recipes is None:
        recipes = frontmatter.get("recipe_pack")
    if not isinstance(recipes, list):
        recipes = []
    recipe_list = [str(v).strip() for v in recipes if str(v).strip()]

    artifacts = frontmatter.get("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = []
    artifact_list = [str(v).strip() for v in artifacts if str(v).strip()]

    rung_default = frontmatter.get("rung_default", 641)
    try:
        rung_default = int(rung_default)
    except Exception:
        rung_default = 641

    return {
        "id": swarm_id,
        "agent_type": str(frontmatter.get("agent_type", swarm_id)).strip(),
        "category": category,
        "path": rel_path,
        "version": str(frontmatter.get("version", "1.0.0")).strip(),
        "authority": str(frontmatter.get("authority", "641")).strip(),
        "model_preferred": str(frontmatter.get("model_preferred", "sonnet")).strip(),
        "rung_default": rung_default,
        "skill_pack": skills,
        "recipes": recipe_list,
        "persona_primary": persona_primary,
        "persona_alternatives": persona_alternatives,
        "artifacts": artifact_list,
    }


def _spec_to_frontmatter(spec: dict[str, object]) -> dict[str, object]:
    frontmatter: dict[str, object] = {
        "agent_type": str(spec.get("agent_type", spec.get("id", "new-agent"))).strip(),
        "version": str(spec.get("version", "1.0.0")).strip(),
        "authority": str(spec.get("authority", "641")).strip(),
        "skill_pack": [str(s).strip() for s in (spec.get("skill_pack") or []) if str(s).strip()],
        "persona": {
            "primary": str(spec.get("persona_primary", "")).strip(),
            "alternatives": [
                str(v).strip()
                for v in (spec.get("persona_alternatives") or [])
                if str(v).strip()
            ],
        },
        "model_preferred": str(spec.get("model_preferred", "sonnet")).strip(),
        "rung_default": int(spec.get("rung_default", 641)),
        "artifacts": [str(a).strip() for a in (spec.get("artifacts") or []) if str(a).strip()],
    }
    recipes = [str(r).strip() for r in (spec.get("recipes") or []) if str(r).strip()]
    if recipes:
        frontmatter["recipes"] = recipes
    return frontmatter


def _mmd_safe(label: str) -> str:
    return label.replace('"', "'")


def _swarm_spec_to_mermaid(spec: dict[str, object]) -> str:
    spec_json = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    swarm_id = str(spec.get("id", "swarm")).strip() or "swarm"
    agent_type = str(spec.get("agent_type", swarm_id)).strip() or swarm_id
    model = str(spec.get("model_preferred", "sonnet")).strip() or "sonnet"
    rung = int(spec.get("rung_default", 641))
    lines = [
        f"%% SWARM_SPEC: {spec_json}",
        "flowchart TD",
        f'    SWARM["{_mmd_safe(agent_type)}<br/>model: {_mmd_safe(model)}<br/>rung: {rung}"]',
    ]
    persona_primary = str(spec.get("persona_primary", "")).strip()
    if persona_primary:
        lines.append(f'    P_PRIMARY["persona: {_mmd_safe(persona_primary)}"]')
        lines.append("    P_PRIMARY --> SWARM")

    for idx, skill in enumerate(spec.get("skill_pack") or []):
        skill_name = str(skill).strip()
        if not skill_name:
            continue
        lines.append(f'    SK_{idx}["skill: {_mmd_safe(skill_name)}"]')
        lines.append(f"    SK_{idx} --> SWARM")

    for idx, recipe in enumerate(spec.get("recipes") or []):
        recipe_name = str(recipe).strip()
        if not recipe_name:
            continue
        lines.append(f'    RC_{idx}["recipe: {_mmd_safe(recipe_name)}"]')
        lines.append(f"    RC_{idx} --> SWARM")

    for idx, artifact in enumerate(spec.get("artifacts") or []):
        artifact_name = str(artifact).strip()
        if not artifact_name:
            continue
        lines.append(f'    AR_{idx}["artifact: {_mmd_safe(artifact_name)}"]')
        lines.append(f"    SWARM --> AR_{idx}")

    return "\n".join(lines)


def _extract_spec_from_mermaid(diagram_mermaid: str) -> dict[str, object]:
    for raw_line in diagram_mermaid.splitlines():
        line = raw_line.strip()
        if line.startswith("%% SWARM_SPEC:"):
            payload = line.split("%% SWARM_SPEC:", 1)[1].strip()
            spec = json.loads(payload)
            if not isinstance(spec, dict):
                raise ValueError("SWARM_SPEC must be a json object")
            return spec
    raise ValueError("diagram is missing %% SWARM_SPEC JSON comment")


def _swarm_catalog_payload() -> dict[str, object]:
    return {
        "swarms": _iter_markdown_rows(SWARMS_ROOT, recursive=True),
        "skills": _iter_markdown_rows(SKILLS_ROOT, recursive=True),
        "recipes": _iter_markdown_rows(RECIPES_ROOT, recursive=True),
        "personas": _iter_markdown_rows(PERSONAS_ROOT, recursive=True),
    }


def _validate_swarm_spec(spec: dict[str, object], catalog: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    swarm_id = str(spec.get("id", "")).strip()
    if not swarm_id:
        errors.append("spec.id is required")

    agent_type = str(spec.get("agent_type", "")).strip()
    if not agent_type:
        errors.append("spec.agent_type is required")

    model = str(spec.get("model_preferred", "")).strip()
    if not model:
        errors.append("spec.model_preferred is required")

    rung = spec.get("rung_default")
    try:
        int(rung)
    except Exception:
        errors.append("spec.rung_default must be an integer")

    skill_ids = {row["id"] for row in catalog["skills"]}  # type: ignore[index]
    recipe_ids = {row["id"] for row in catalog["recipes"]}  # type: ignore[index]
    persona_ids = {row["id"] for row in catalog["personas"]}  # type: ignore[index]
    persona_slugs = {_slugify_token(pid) for pid in persona_ids}

    for skill in spec.get("skill_pack") or []:
        skill_name = str(skill).strip()
        if skill_name and skill_name not in skill_ids:
            errors.append(f"unknown skill: {skill_name}")

    for recipe in spec.get("recipes") or []:
        recipe_name = str(recipe).strip()
        if recipe_name and recipe_name not in recipe_ids:
            warnings.append(f"unknown recipe: {recipe_name}")

    persona_values = []
    primary = str(spec.get("persona_primary", "")).strip()
    if primary:
        persona_values.append(primary)
    for alt in spec.get("persona_alternatives") or []:
        token = str(alt).strip()
        if token:
            persona_values.append(token)

    for token in persona_values:
        token_slug = _slugify_token(token)
        if token in persona_ids or token_slug in persona_slugs:
            continue
        warnings.append(f"unknown persona: {token}")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def _resolve_swarm_path(swarm_id: str) -> Path:
    swarm_norm = swarm_id.strip()
    if not swarm_norm:
        raise ValueError("swarm_id is required")
    matches = sorted(
        p
        for p in SWARMS_ROOT.rglob(f"{swarm_norm}.md")
        if p.is_file() and not p.name.startswith("README")
    )
    if not matches:
        raise FileNotFoundError(f"swarm not found: {swarm_norm}")
    if len(matches) > 1:
        dup = ", ".join(str(p.relative_to(REPO_ROOT)) for p in matches)
        raise ValueError(f"duplicate swarm id '{swarm_norm}': {dup}")
    return matches[0]


def _load_swarm_studio_payload(swarm_id: str) -> dict[str, object]:
    swarm_path = _resolve_swarm_path(swarm_id)
    markdown = swarm_path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(markdown)
    category = swarm_path.parent.relative_to(SWARMS_ROOT).as_posix()
    rel_path = str(swarm_path.relative_to(REPO_ROOT))
    spec = _frontmatter_to_spec(swarm_id, category, rel_path, frontmatter)
    catalog = _swarm_catalog_payload()
    validation = _validate_swarm_spec(spec, catalog)
    diagram_mermaid = _swarm_spec_to_mermaid(spec)
    return {
        "id": swarm_id,
        "path": rel_path,
        "category": category,
        "markdown": markdown,
        "frontmatter": frontmatter,
        "body": body,
        "spec": spec,
        "diagram_mermaid": diagram_mermaid,
        "validation": validation,
    }


def _compile_main_swarms_diagram() -> str:
    swarms = _iter_markdown_rows(SWARMS_ROOT, recursive=True)
    by_category: dict[str, list[dict[str, str]]] = {}
    for row in swarms:
        by_category.setdefault(row["category"] or "root", []).append(row)

    lines = ["graph TD"]
    node_by_id: dict[str, str] = {}
    for category in sorted(by_category.keys()):
        cat_safe = re.sub(r"[^A-Za-z0-9_]", "_", category)
        cat_title = category.replace("-", " ").title()
        lines.append(f'  subgraph CAT_{cat_safe}["{_mmd_safe(cat_title)}"]')
        for row in sorted(by_category[category], key=lambda r: r["id"]):
            node_id = f"N_{cat_safe}_{re.sub(r'[^A-Za-z0-9_]', '_', row['id'])}"
            node_by_id[row["id"]] = node_id
            lines.append(f'    {node_id}["{_mmd_safe(row["id"])}"]')
        lines.append("  end")

    core_spine = ["scout", "forecaster", "judge", "planner", "coder", "skeptic", "final-audit"]
    for src, dst in zip(core_spine, core_spine[1:]):
        if src in node_by_id and dst in node_by_id:
            lines.append(f"  {node_by_id[src]} --> {node_by_id[dst]}")
    if "security-auditor" in node_by_id and "final-audit" in node_by_id:
        lines.append(f"  {node_by_id['security-auditor']} --> {node_by_id['final-audit']}")
    return "\n".join(lines)


def _file_payload(rel_path: str) -> dict:
    path = _safe_resolve_repo_path(rel_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(rel_path)
    if not _is_allowed_edit_path(path):
        raise PermissionError(rel_path)
    text = path.read_text(encoding="utf-8")
    return {
        "path": rel_path,
        "content": text,
        "size": len(text.encode("utf-8")),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def _save_file(rel_path: str, content: str) -> dict:
    path = _safe_resolve_repo_path(rel_path)
    if not _is_allowed_edit_path(path):
        raise PermissionError(rel_path)
    if len(content.encode("utf-8")) > 2_000_000:
        raise ValueError("file too large")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return _file_payload(rel_path)


def _create_file(group_id: str, filename: str) -> dict:
    filename_norm = filename.strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", filename_norm):
        raise ValueError("filename must match [A-Za-z0-9._-]+")
    group = next((g for g in CATALOG_GROUPS if g["id"] == group_id), None)
    if not group:
        raise ValueError(f"unknown group: {group_id}")
    base = (REPO_ROOT / group["dirs"][0]).resolve()
    if not base.exists():
        base.mkdir(parents=True, exist_ok=True)
    if "." not in filename_norm:
        filename_norm += ".md"
    target = (base / filename_norm).resolve()
    if not _is_allowed_edit_path(target):
        raise PermissionError(str(target))
    if target.exists():
        raise FileExistsError(filename_norm)
    template = str(group.get("create_template", "# New File\n"))
    target.write_text(template, encoding="utf-8")
    return {"path": str(target.relative_to(REPO_ROOT)), "created": True}


def _llm_status() -> dict:
    provider = ""
    provider_name = ""
    provider_url = ""
    provider_model = ""
    setup_ok = False
    setup_msg = "llm_config_manager unavailable"
    if get_llm_config is not None:
        try:
            cfg = get_llm_config()
            provider = cfg.active_provider
            provider_name = cfg.get_provider_name()
            provider_url = cfg.get_provider_url()
            provider_model = cfg.get_provider_model()
            setup_ok, setup_msg = cfg.validate_setup()
        except Exception as ex:
            setup_msg = f"status check failed: {ex}"

    probes: list[dict] = []
    preferred = ""
    if candidate_ollama_urls and probe_ollama_urls and choose_preferred_ollama_url:
        try:
            urls = candidate_ollama_urls(repo_root=REPO_ROOT, explicit_urls=[])
            probes = probe_ollama_urls(urls=urls, timeout_seconds=2.0)
            preferred = choose_preferred_ollama_url(probes)
        except Exception:
            probes = []
            preferred = ""

    models: list[str] = []
    if preferred and requests is not None:
        try:
            resp = requests.get(f"{preferred}/api/tags", timeout=3.0)
            resp.raise_for_status()
            payload = resp.json()
            for row in payload.get("models", []) if isinstance(payload, dict) else []:
                if isinstance(row, dict) and isinstance(row.get("name"), str):
                    models.append(row["name"])
        except Exception:
            models = []

    return {
        "provider": provider,
        "provider_name": provider_name,
        "provider_url": provider_url,
        "provider_model": provider_model,
        "setup_ok": bool(setup_ok),
        "setup_msg": setup_msg,
        "probes": probes,
        "preferred_ollama_url": preferred,
        "models": sorted(set(models)),
        "ollama_installed": shutil.which("ollama") is not None,
    }


def _update_llm_config(provider: str, ollama_url: str, ollama_model: str) -> dict:
    if update_llm_config_file is None:
        raise RuntimeError("llm config helper unavailable")
    kwargs = {
        "repo_root": REPO_ROOT,
        "provider": provider.strip() or None,
        "ollama_url": ollama_url.strip() or None,
        "ollama_model": ollama_model.strip() or None,
    }
    update_llm_config_file(**kwargs)
    return _llm_status()


def _run_command(cmd: list[str], *, input_text: str = "", timeout: float = 600.0, env: dict | None = None) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        text=True,
        input=input_text if input_text else None,
        capture_output=True,
        timeout=timeout,
        env=env,
        check=False,
    )
    return {
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[-5000:],
        "stderr": (proc.stderr or "")[-5000:],
    }


def _open_vscode_path(rel_path: str) -> dict:
    path = _safe_resolve_repo_path(rel_path)
    if not path.exists():
        return {"success": False, "message": f"path not found: {rel_path}"}
    code_bin = shutil.which("code")
    if code_bin is None:
        return {"success": False, "message": f"VSCode 'code' binary not found. Path: {path}"}
    subprocess.Popen([code_bin, str(path)], cwd=str(REPO_ROOT))
    return {"success": True, "message": f"Opening {rel_path} in VSCode"}


def _install_ollama(sudo_password: str) -> dict:
    if shutil.which("ollama"):
        return {"ok": True, "message": "Ollama already installed.", "changed": False}
    if not sudo_password:
        raise ValueError("sudo password is required")

    os_release = (Path("/etc/os-release").read_text(encoding="utf-8") if Path("/etc/os-release").exists() else "").lower()
    if "ubuntu" in os_release or "debian" in os_release or "fedora" in os_release or "arch" in os_release:
        cmd = ["sudo", "-S", "-k", "bash", "-lc", "curl -fsSL https://ollama.com/install.sh | sh"]
    elif sys.platform == "darwin":
        cmd = ["sudo", "-S", "-k", "brew", "install", "ollama"]
    else:
        cmd = ["sudo", "-S", "-k", "bash", "-lc", "curl -fsSL https://ollama.com/install.sh | sh"]
    result = _run_command(cmd, input_text=f"{sudo_password}\n", timeout=1200.0)
    ok = result["returncode"] == 0
    return {
        "ok": ok,
        "changed": ok,
        "message": "Ollama install completed." if ok else "Ollama install failed.",
        **result,
    }


def _pull_ollama_model(model: str, ollama_url: str) -> dict:
    model_name = model.strip()
    if not model_name:
        raise ValueError("model is required")
    if not shutil.which("ollama"):
        raise RuntimeError("ollama binary is not installed")
    env = dict(os.environ)
    if ollama_url.strip():
        env["OLLAMA_HOST"] = ollama_url.strip()
    cmd = ["ollama", "pull", model_name]
    result = _run_command(cmd, timeout=3600.0, env=env)
    ok = result["returncode"] == 0
    return {"ok": ok, "message": "model pull completed" if ok else "model pull failed", **result}


def _community_status() -> dict:
    link: dict[str, str] = {}
    if COMMUNITY_LINK_FILE.exists():
        try:
            link = _load_json(COMMUNITY_LINK_FILE)
        except Exception:
            link = {}
    sync_count = 0
    if COMMUNITY_SYNC_LOG.exists():
        with COMMUNITY_SYNC_LOG.open("r", encoding="utf-8") as _fh:
            lines = _fh.readlines()
        sync_count = len(lines)
    cloud = _cloud_health()
    linked = cloud.get("status") == "ok"
    out: dict[str, object] = {
        "linked": linked,
        "email": link.get("email", ""),
        "api_key": "",
        "link_status": cloud.get("status", "not_configured"),
        "sync_events": sync_count,
        "cloud": cloud,
    }
    if "tier" in cloud:
        out["tier"] = cloud.get("tier")
    return out


def _extract_yaml_bool(content: str, key: str) -> bool | None:
    pattern = rf"^\s*{re.escape(key)}\s*:\s*(true|false)\s*$"
    match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return match.group(1).lower() == "true"


def _extract_yaml_str(content: str, keys: tuple[str, ...]) -> str:
    for key in keys:
        pattern = rf'^\s*{re.escape(key)}\s*:\s*"?([^"\n#]+)"?\s*$'
        match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    return ""


def _normalize_cloud_url(url: str) -> str:
    clean = url.strip().rstrip("/")
    if not clean:
        return DEFAULT_CLOUD_API_URL
    if clean.endswith("/api"):
        return f"{clean}/v1"
    return clean


def _load_cloud_config() -> dict[str, object]:
    env_key = os.getenv("SOLACEAGI_API_KEY", "").strip()
    content = ""
    for path in CLOUD_CONFIG_PATHS:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if content:
                break
    enabled = _extract_yaml_bool(content, "enabled")
    if enabled is None:
        enabled = bool(env_key)
    api_key = env_key or _extract_yaml_str(content, ("api_key",))
    api_url = _extract_yaml_str(content, ("api_url", "base_url"))
    return {
        "enabled": bool(enabled),
        "api_key": api_key,
        "api_url": _normalize_cloud_url(api_url),
    }


def _request_cloud(
    method: str,
    endpoint: str,
    api_key: str,
    payload: dict[str, object] | None = None,
    timeout: float = 8.0,
) -> tuple[int, object, str | None]:
    if requests is None:
        return 0, {}, "requests dependency unavailable"
    cfg = _load_cloud_config()
    url = f"{_normalize_cloud_url(str(cfg.get('api_url', DEFAULT_CLOUD_API_URL)))}{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.request(method, url, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.Timeout:
        return 0, {}, "connection timeout to www.solaceagi.com"
    except requests.exceptions.RequestException as exc:
        return 0, {}, f"connection error to www.solaceagi.com: {exc}"
    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}
    return response.status_code, body, None


def _cloud_health() -> dict:
    cfg = _load_cloud_config()
    if not cfg["enabled"] or not cfg["api_key"]:
        return {
            "status": "not_configured",
            "message": "run: PUT /api/llm/keys/solaceagi to configure",
        }

    status, body, error = _request_cloud("GET", "/health", str(cfg["api_key"]), payload=None)
    if error:
        return {"status": "unreachable", "error": error}
    if status in (401, 403):
        return {"status": "auth_failed", "error": "invalid API key"}
    if status < 200 or status >= 300:
        return {"status": "error", "error": f"cloud health http {status}"}

    tier = "unknown"
    if isinstance(body, dict):
        raw_tier = body.get("tier")
        if isinstance(raw_tier, str) and raw_tier.strip():
            tier = raw_tier.strip()
    if tier == "unknown":
        tier_status, tier_body, tier_error = _request_cloud("GET", "/account/tier", str(cfg["api_key"]), payload=None)
        if tier_error is None and tier_status == 200 and isinstance(tier_body, dict):
            raw_tier = tier_body.get("tier")
            if isinstance(raw_tier, str) and raw_tier.strip():
                tier = raw_tier.strip()
    return {"status": "ok", "tier": tier, "api_url": cfg["api_url"]}


def _community_link(email: str) -> dict:
    email_norm = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email_norm):
        raise ValueError("valid email required")

    cloud = _cloud_health()
    if cloud.get("status") != "ok":
        return cloud

    cfg = _load_cloud_config()
    status, body, error = _request_cloud(
        "POST",
        "/auth/link",
        str(cfg["api_key"]),
        payload={"email": email_norm},
    )
    if error:
        return {"status": "unreachable", "error": error}
    if status in (401, 403):
        return {"status": "auth_failed", "error": "invalid API key"}
    if status < 200 or status >= 300:
        return {"status": "error", "error": f"cloud link http {status}", "response": body}

    linked = {
        "email": email_norm,
        "status": "linked",
        "linked_at": _utc_now(),
        "tier": str(cloud.get("tier", "unknown")),
    }
    _write_json(COMMUNITY_LINK_FILE, linked)
    return {"status": "linked", "email": email_norm, "tier": linked["tier"], "response": body}


def _community_sync(direction: str) -> dict:
    direction_norm = direction.strip().lower() or "both"
    if direction_norm not in {"up", "down", "both"}:
        raise ValueError("direction must be one of: up, down, both")

    cloud = _cloud_health()
    if cloud.get("status") != "ok":
        return cloud

    cfg = _load_cloud_config()
    status, body, error = _request_cloud(
        "POST",
        "/sync/skills",
        str(cfg["api_key"]),
        payload={"direction": direction_norm},
    )
    if error:
        return {"status": "unreachable", "error": error}
    if status in (401, 403):
        return {"status": "auth_failed", "error": "invalid API key"}
    if status < 200 or status >= 300:
        return {"status": "error", "error": f"cloud sync http {status}", "response": body}

    event = {
        "ts": _utc_now(),
        "direction": direction_norm,
        "status": "ok",
    }
    _append_jsonl(COMMUNITY_SYNC_LOG, event)
    return {"status": "ok", "direction": direction_norm, "synced_at": event["ts"], "response": body}


SAFE_CLI_COMMANDS = {
    "version": ["python", "-m", "stillwater", "--version"],
    "doctor": ["python", "-m", "stillwater", "doctor"],
    "llm-status": ["python", "-m", "stillwater", "llm", "status"],
}


def _run_cli_command(command: str) -> dict:
    """Run a safe, allowlisted CLI command from the web UI."""
    if command not in SAFE_CLI_COMMANDS:
        raise ValueError(f"command not allowed: {command!r}. Allowed: {list(SAFE_CLI_COMMANDS.keys())}")
    cmd = SAFE_CLI_COMMANDS[command]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(CLI_SRC)
    result = _run_command(cmd, timeout=30.0, env=env)
    return {
        "command": command,
        "cmd": cmd,
        "returncode": result["returncode"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "ok": result["returncode"] == 0,
    }


class AdminHandler(BaseHTTPRequestHandler):
    server_version = "StillwaterAdmin/0.2"

    def log_message(self, fmt: str, *args) -> None:
        sys.stdout.write("[admin] " + (fmt % args) + "\n")

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, content: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY_SIZE:
            raise ValueError(f"request body too large ({length} > {MAX_BODY_SIZE})")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
        raise ValueError("invalid json payload")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/health":
            services_registered = 0
            if _SERVICE_REGISTRY is not None:
                try:
                    services_registered = len(_SERVICE_REGISTRY.list_all())
                except Exception:
                    services_registered = 0
            self._send_json(
                {
                    "status": "ok",
                    "service_id": "admin-server",
                    "service_type": "admin",
                    "services_registered": services_registered,
                },
            )
            return
        if path == "/api/health/cloud":
            cloud = _cloud_health()
            self._send_json({"ok": cloud.get("status") == "ok", "cloud": cloud})
            return
        if path == "/":
            file_path = REPO_ROOT / "admin" / "static" / "index.html"
            self._send_bytes(file_path.read_bytes(), "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            rel = path[len("/static/") :]
            file_path = (REPO_ROOT / "admin" / "static" / rel).resolve()
            static_root = (REPO_ROOT / "admin" / "static").resolve()
            try:
                file_path.relative_to(static_root)
            except ValueError:
                self._send_json({"ok": False, "error": "not found"}, status=404)
                return
            if not file_path.exists():
                self._send_json({"ok": False, "error": "not found"}, status=404)
                return
            ctype, _ = mimetypes.guess_type(str(file_path))
            self._send_bytes(file_path.read_bytes(), ctype or "application/octet-stream")
            return

        if path == "/api/catalog":
            self._send_json({"ok": True, **_catalog()})
            return
        if path == "/api/swarms/studio/catalog":
            try:
                catalog = _swarm_catalog_payload()
                self._send_json({"ok": True, **catalog})
            except Exception as ex:
                self._send_json({"ok": False, "error": str(ex)}, status=400)
            return
        if path == "/api/swarms/studio/main-diagram":
            try:
                diagram = _compile_main_swarms_diagram()
                self._send_json({"ok": True, "diagram_mermaid": diagram})
            except Exception as ex:
                self._send_json({"ok": False, "error": str(ex)}, status=400)
            return
        if path == "/api/swarms/studio/swarm":
            try:
                query = parse_qs(parsed.query)
                swarm_id = (query.get("swarm_id", [""])[0] or "").strip()
                payload = _load_swarm_studio_payload(swarm_id)
                self._send_json({"ok": True, **payload})
            except Exception as ex:
                self._send_json({"ok": False, "error": str(ex)}, status=400)
            return
        if path == "/api/file":
            query = parse_qs(parsed.query)
            rel_path = (query.get("path", [""])[0] or "").strip()
            try:
                payload = _file_payload(rel_path)
                self._send_json({"ok": True, **payload})
            except Exception as ex:
                self._send_json({"ok": False, "error": str(ex)}, status=400)
            return
        if path == "/api/llm/status":
            self._send_json({"ok": True, "status": _llm_status()})
            return
        if path == "/api/community/status":
            self._send_json({"ok": True, "community": _community_status()})
            return
        if path == "/api/cli/commands":
            self._send_json({"ok": True, "commands": list(SAFE_CLI_COMMANDS.keys())})
            return

        # Service registry GET routes
        if _SERVICE_REGISTRY is not None:
            if path == "/api/services":
                services = [s.model_dump() for s in _SERVICE_REGISTRY.list_all()]
                self._send_json({"ok": True, "services": services})
                return
            if path.startswith("/api/services/") and path.endswith("/health"):
                sid = path[len("/api/services/"):-len("/health")]
                health = _SERVICE_REGISTRY.health_check(sid)
                self._send_json({"ok": True, "health": health.model_dump()})
                return
            if path.startswith("/api/services/"):
                sid = path.split("/api/services/")[1].rstrip("/")
                desc = _SERVICE_REGISTRY.get(sid)
                if desc:
                    self._send_json({"ok": True, "service": desc.model_dump()})
                else:
                    self._send_json({"ok": False, "error": "service not found"}, status=404)
                return

        self._send_json({"ok": False, "error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._read_json_body()
        except Exception as ex:
            self._send_json({"ok": False, "error": str(ex)}, status=400)
            return

        try:
            if path == "/api/vscode/open":
                rel_path = str(payload.get("file", "")).strip()
                if not rel_path:
                    raise ValueError("file is required")
                result = _open_vscode_path(rel_path)
                self._send_json(result, status=200 if result.get("success") else 400)
                return
            if path == "/api/swarms/studio/compile-diagram":
                markdown = str(payload.get("markdown", ""))
                if not markdown.strip():
                    raise ValueError("markdown is required")
                frontmatter, body = _split_frontmatter(markdown)
                swarm_id = str(payload.get("swarm_id", frontmatter.get("agent_type", ""))).strip()
                if not swarm_id:
                    raise ValueError("swarm_id is required (or frontmatter.agent_type)")
                rel_path = str(payload.get("path", "")).strip()
                category = str(payload.get("category", "")).strip()
                if not category and rel_path:
                    rel_obj = Path(rel_path)
                    if rel_obj.suffix == ".md":
                        parts = rel_obj.parts
                        if len(parts) >= 5 and parts[:3] == ("data", "default", "swarms"):
                            category = "/".join(parts[3:-1])
                if not category:
                    category = "uncategorized"
                if not rel_path:
                    rel_path = f"data/default/swarms/{category}/{swarm_id}.md"
                spec = _frontmatter_to_spec(swarm_id, category, rel_path, frontmatter)
                validation = _validate_swarm_spec(spec, _swarm_catalog_payload())
                diagram_mermaid = _swarm_spec_to_mermaid(spec)
                self._send_json(
                    {
                        "ok": True,
                        "spec": spec,
                        "frontmatter": frontmatter,
                        "body": body,
                        "diagram_mermaid": diagram_mermaid,
                        "validation": validation,
                    },
                )
                return
            if path == "/api/swarms/studio/compile-swarm":
                diagram_mermaid = str(payload.get("diagram_mermaid", ""))
                if not diagram_mermaid.strip():
                    raise ValueError("diagram_mermaid is required")
                spec = _extract_spec_from_mermaid(diagram_mermaid)
                validation = _validate_swarm_spec(spec, _swarm_catalog_payload())
                frontmatter = _spec_to_frontmatter(spec)
                default_title = str(spec.get("agent_type", spec.get("id", "new-swarm"))).replace("-", " ").title()
                body = str(payload.get("body", "")).strip()
                if not body:
                    body = (
                        f"# {default_title} Agent Type\n\n"
                        "## Role\n"
                        "Describe role, constraints, and expected artifacts.\n"
                    )
                markdown = _dump_frontmatter(frontmatter) + "\n" + body.strip() + "\n"
                self._send_json(
                    {
                        "ok": True,
                        "spec": spec,
                        "frontmatter": frontmatter,
                        "markdown": markdown,
                        "validation": validation,
                    },
                )
                return
            if path == "/api/swarms/studio/validate":
                catalog = _swarm_catalog_payload()
                source = "unknown"
                spec: dict[str, object]
                if str(payload.get("markdown", "")).strip():
                    source = "markdown"
                    frontmatter, _body = _split_frontmatter(str(payload.get("markdown", "")))
                    swarm_id = str(payload.get("swarm_id", frontmatter.get("agent_type", ""))).strip()
                    if not swarm_id:
                        swarm_id = "unknown"
                    rel_path = str(payload.get("path", f"data/default/swarms/unknown/{swarm_id}.md")).strip()
                    category = str(payload.get("category", "unknown")).strip() or "unknown"
                    spec = _frontmatter_to_spec(swarm_id, category, rel_path, frontmatter)
                elif str(payload.get("diagram_mermaid", "")).strip():
                    source = "diagram"
                    spec = _extract_spec_from_mermaid(str(payload.get("diagram_mermaid", "")))
                else:
                    swarm_id = str(payload.get("swarm_id", "")).strip()
                    if not swarm_id:
                        raise ValueError("provide markdown, diagram_mermaid, or swarm_id")
                    source = "swarm_id"
                    spec = _load_swarm_studio_payload(swarm_id)["spec"]  # type: ignore[index]
                validation = _validate_swarm_spec(spec, catalog)
                self._send_json({"ok": True, "source": source, "spec": spec, "validation": validation})
                return
            if path == "/api/file/save":
                rel_path = str(payload.get("path", "")).strip()
                content = str(payload.get("content", ""))
                file_payload = _save_file(rel_path, content)
                self._send_json({"ok": True, **file_payload})
                return
            if path == "/api/file/create":
                group_id = str(payload.get("group", "")).strip()
                filename = str(payload.get("filename", "")).strip()
                created = _create_file(group_id, filename)
                self._send_json({"ok": True, **created})
                return
            if path == "/api/llm/config":
                provider = str(payload.get("provider", ""))
                ollama_url = str(payload.get("ollama_url", ""))
                ollama_model = str(payload.get("ollama_model", ""))
                status = _update_llm_config(provider, ollama_url, ollama_model)
                self._send_json({"ok": True, "status": status})
                return
            if path == "/api/system/install-ollama":
                sudo_password = str(payload.get("sudo_password", ""))
                result = _install_ollama(sudo_password)
                self._send_json(result, status=200 if result.get("ok") else 500)
                return
            if path == "/api/ollama/pull":
                model = str(payload.get("model", ""))
                ollama_url = str(payload.get("ollama_url", ""))
                result = _pull_ollama_model(model, ollama_url)
                self._send_json(result, status=200 if result.get("ok") else 500)
                return
            if path == "/api/community/link":
                email = str(payload.get("email", ""))
                result = _community_link(email)
                ok = result.get("status") in {"linked", "ok"}
                self._send_json({"ok": ok, "link": result}, status=200 if ok else 503)
                return
            if path == "/api/community/sync":
                direction = str(payload.get("direction", "both"))
                result = _community_sync(direction)
                ok = result.get("status") == "ok"
                self._send_json({"ok": ok, "sync": result}, status=200 if ok else 503)
                return
            if path == "/api/cli/run":
                command = str(payload.get("command", "")).strip()
                result = _run_cli_command(command)
                self._send_json({"ok": result["ok"], "result": result})
                return

            # Service registry POST routes
            if _SERVICE_REGISTRY is not None:
                if path == "/api/services/register":
                    try:
                        reg = ServiceRegistration(**payload)
                        desc = _SERVICE_REGISTRY.register(reg)
                        self._send_json({"ok": True, "service": desc.model_dump()})
                    except Exception as ex:
                        self._send_json({"ok": False, "error": str(ex)}, status=400)
                    return
                if path == "/api/services/deregister":
                    sid = str(payload.get("service_id", "")).strip()
                    removed = _SERVICE_REGISTRY.deregister(sid)
                    self._send_json({"ok": removed})
                    return
                if path == "/api/services/discover":
                    result = _SERVICE_REGISTRY.discover()
                    self._send_json({"ok": True, "discovery": result.model_dump()})
                    return
        except Exception as ex:
            self._send_json({"ok": False, "error": str(ex)}, status=400)
            return

        self._send_json({"ok": False, "error": "not found"}, status=404)


def _open_browser(url: str) -> None:
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stillwater admin web app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--open", action="store_true", help="Open browser after server starts")
    ns = parser.parse_args(argv)

    server = ThreadingHTTPServer((ns.host, ns.port), AdminHandler)
    url = f"http://{ns.host}:{ns.port}"
    print(f"[admin] repo_root: {REPO_ROOT}")
    print(f"[admin] serving: {url}")
    if ns.open:
        _open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
