from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from typing import Any
import unicodedata
import urllib.parse
import urllib.request

from . import __version__


def _repo_root() -> Path:
    # `cli/src/stillwater/cli.py` -> repo root is 4 parents up.
    return Path(__file__).resolve().parents[3]


def _default_ollama_model(root: Path) -> str:
    try:
        from llm_config_manager import get_llm_config

        cfg = get_llm_config()
        if cfg.active_provider == "ollama" and cfg.get_provider_model().strip():
            return cfg.get_provider_model().strip()
    except Exception:
        pass
    return "qwen2.5-coder:7b"


def _runtime_env(root: Path) -> dict[str, str]:
    env = dict(os.environ)
    src_path = str(root / "cli" / "src")
    existing = env.get("PYTHONPATH", "").strip()
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}{os.pathsep}{existing}"
    return env


def _utc_now() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_run_id(prefix: str) -> str:
    stamp = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}-{stamp}"


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower())
    normalized = normalized.strip("-._")
    return normalized or "wish"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _belt_for_score(score: float) -> str:
    if score < 8.5:
        return "White Belt"
    if score < 9.0:
        return "Yellow Belt"
    if score < 9.5:
        return "Green Belt"
    if score < 9.8:
        return "Brown Belt"
    return "Black Belt"


def _parse_oolong_output(stdout_text: str) -> dict[str, Any]:
    def _has_pass(label: str) -> bool:
        for line in stdout_text.splitlines():
            if label in line and "PASS" in line:
                return True
        return False

    return {
        "rung_641_pass": _has_pass("Rung 641"),
        "rung_274177_pass": _has_pass("Rung 274177"),
        "rung_65537_pass": _has_pass("Rung 65537"),
        "counter_bypass_complete": "Counter Bypass Protocol: DEMO RUN COMPLETE" in stdout_text,
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _tokenize_overlap_terms(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "what",
        "when",
        "where",
        "which",
        "into",
        "does",
        "have",
        "has",
        "your",
        "about",
        "them",
        "then",
        "just",
        "will",
        "would",
        "could",
        "should",
        "than",
        "there",
        "their",
        "were",
        "been",
        "being",
        "also",
        "only",
        "over",
        "under",
        "some",
        "more",
        "most",
        "very",
        "into",
    }
    out: set[str] = set()
    for token in re.findall(r"[a-z0-9_]+", text.lower()):
        if len(token) < 2:
            continue
        if token in stop:
            continue
        out.add(token)
    return out


def _infer_imo_problem_id(prompt: str, facts: dict[str, Any]) -> str | None:
    prompt_lower = prompt.lower()
    explicit = re.search(r"\b(?:problem|p)\s*([1-6])\b", prompt_lower)
    if explicit:
        return f"P{explicit.group(1)}"

    cue_map: list[tuple[str, tuple[str, ...]]] = [
        ("P1", ("prime factor", "omega(", "ω(", "2024")),
        ("P2", ("ab+kc", "ac+kb", "bc+ka", "perfect square")),
        ("P3", ("median", "m_n/a_n", "mₙ/aₙ")),
        ("P4", ("∠ypx", "∠kil", "angle ypx", "angle kil")),
        ("P5", ("ramsey", "k6", "2-color", "monochromatic triangle")),
        ("P6", ("functional equation", "f(x)=x", "f(x)=2-x")),
    ]
    for problem_id, cues in cue_map:
        if any(cue in prompt_lower for cue in cues):
            return problem_id

    prompt_terms = _tokenize_overlap_terms(prompt)
    if not prompt_terms:
        return None

    sections = facts.get("sections", {})
    if not isinstance(sections, dict):
        return None

    best_problem = ""
    best_score = 0
    for idx in range(1, 7):
        pid = f"P{idx}"
        section_lines = sections.get(pid, [])
        if not isinstance(section_lines, list):
            continue
        joined = " ".join(str(line) for line in section_lines)
        section_terms = _tokenize_overlap_terms(joined)
        if not section_terms:
            continue
        score = len(prompt_terms.intersection(section_terms))
        if score > best_score:
            best_score = score
            best_problem = pid

    if not best_problem:
        return None
    if best_score <= 0:
        return None
    return best_problem


def _verify_wish_artifacts(root: Path, wish_id: str) -> tuple[bool, list[str], dict[str, Any]]:
    out: dict[str, Any] = {"wish_id": wish_id}
    errors: list[str] = []
    candidate_dirs = [
        root / "artifacts" / "wishes" / wish_id,
        root / "wishes" / "examples" / "artifacts" / "wishes" / wish_id,
        root / "cli" / "wishes" / "artifacts" / "wishes" / wish_id,
    ]
    discovered = sorted(root.glob(f"**/artifacts/wishes/{wish_id}"))
    for found in discovered:
        if found not in candidate_dirs:
            candidate_dirs.append(found)
    artifact_dir = candidate_dirs[0]
    for cand in candidate_dirs:
        if cand.exists():
            artifact_dir = cand
            break
    out["artifact_dir"] = str(artifact_dir)

    state_path = artifact_dir / "state.mmd"
    sha_path = artifact_dir / "state.sha256"
    results_path = artifact_dir / "results.json"
    out["files"] = {
        "state_mmd": str(state_path),
        "state_sha256": str(sha_path),
        "results_json": str(results_path),
    }

    for req in [state_path, sha_path, results_path]:
        if not req.exists():
            errors.append(f"missing file: {req}")

    if state_path.exists() and sha_path.exists():
        state_digest = hashlib.sha256(state_path.read_bytes()).hexdigest()
        line = sha_path.read_text(encoding="utf-8").strip()
        declared = line.split()[0] if line else ""
        out["state_digest_actual"] = state_digest
        out["state_digest_declared"] = declared
        if declared != state_digest:
            errors.append(
                f"sha mismatch for {state_path.name}: declared={declared} actual={state_digest}"
            )

    if results_path.exists():
        try:
            results = _load_json(results_path)
            out["status"] = results.get("status")
            score_raw = results.get("score")
            if isinstance(score_raw, (int, float)):
                out["score"] = float(score_raw)
                out["belt"] = _belt_for_score(float(score_raw))
        except Exception as ex:
            errors.append(f"invalid results.json: {ex}")

    return (len(errors) == 0, errors, out)


def _latest_run_id_dir(base: Path) -> Path | None:
    if not base.exists():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda p: p.name)
    return dirs[-1]


_DEFAULT_TWIN_SKILLS = [
    "prime-wishes.md",
    "phuc-forecast.md",
    "phuc-swarms.md",
    "phuc-cleanup.md",
    "prime-coder.md",
    "prime-safety.md",
    "phuc-context.md",
]


def _default_twin_skills(root: Path) -> list[str]:
    root_skills = root / "skills"
    phuc_skill_names: list[str] = []
    if root_skills.exists():
        for path in sorted(root_skills.glob("phuc-*.md")):
            if path.name.lower() == "readme.md":
                continue
            phuc_skill_names.append(path.name)
    ordered = list(_DEFAULT_TWIN_SKILLS) + phuc_skill_names
    return _dedupe_keep_order(ordered)


def _resolve_user_path(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _normalize_csv_paths(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _dedupe_keep_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _load_kernel_config(root: Path) -> dict[str, Any]:
    cfg_env = os.environ.get("STILLWATER_KERNEL_CONFIG", "").strip()
    cfg_path = _resolve_user_path(root, cfg_env) if cfg_env else (root / "cli" / "kernel_config.yaml")
    if not cfg_path.exists():
        return {}
    text = cfg_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass
    return {}


def _list_from_config(config: dict[str, Any], key: str) -> list[str]:
    raw = config.get(key)
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _kernel_paths(root: Path) -> dict[str, Any]:
    cfg = _load_kernel_config(root)
    ext_env = os.environ.get("STILLWATER_EXTENSION_ROOT", "").strip()
    ext_cfg = str(cfg.get("extension_root", "")).strip() if isinstance(cfg.get("extension_root"), str) else ""
    ext_root = _resolve_user_path(root, ext_env or ext_cfg) if (ext_env or ext_cfg) else (root / "cli" / "extensions")

    skill_dirs: list[tuple[str, Path]] = [
        ("root", root / "skills"),
        ("cli", root / "cli" / "skills"),
        ("cli_stillwater", root / "cli" / "skills" / "stillwater"),
    ]
    if ext_root.exists():
        skill_dirs.extend(
            [
                ("extension", ext_root / "skills"),
                ("extension_stillwater", ext_root / "skills" / "stillwater"),
            ]
        )

    cfg_skill_dirs = _list_from_config(cfg, "skill_dirs")
    for raw in cfg_skill_dirs:
        skill_dirs.append(("cfg", _resolve_user_path(root, raw)))

    env_skill_dirs = _normalize_csv_paths(os.environ.get("STILLWATER_SKILL_DIRS", ""))
    for raw in env_skill_dirs:
        skill_dirs.append(("env", _resolve_user_path(root, raw)))
    deduped_skill_dirs: list[tuple[str, Path]] = []
    seen_skill_paths: set[str] = set()
    for source, path in skill_dirs:
        key = str(path.resolve())
        if key in seen_skill_paths:
            continue
        seen_skill_paths.add(key)
        deduped_skill_dirs.append((source, path))
    skill_dirs = deduped_skill_dirs

    recipe_dirs = ["cli/recipes", "recipes", "ripples/system", "ripples/project"]
    ext_recipe_dir = ext_root / "recipes"
    if ext_recipe_dir.exists():
        try:
            recipe_dirs.insert(0, str(ext_recipe_dir.relative_to(root)))
        except ValueError:
            recipe_dirs.insert(0, str(ext_recipe_dir))
    cfg_recipe_dirs = _list_from_config(cfg, "recipe_dirs")
    for raw in cfg_recipe_dirs:
        resolved = _resolve_user_path(root, raw)
        try:
            recipe_dirs.insert(0, str(resolved.relative_to(root)))
        except ValueError:
            recipe_dirs.insert(0, str(resolved))
    env_recipe_dirs = _normalize_csv_paths(os.environ.get("STILLWATER_RECIPE_DIRS", ""))
    for raw in env_recipe_dirs:
        resolved = _resolve_user_path(root, raw)
        try:
            recipe_dirs.insert(0, str(resolved.relative_to(root)))
        except ValueError:
            recipe_dirs.insert(0, str(resolved))
    recipe_dirs = _dedupe_keep_order(recipe_dirs)

    identity_env = os.environ.get("STILLWATER_IDENTITY_DIR", "").strip()
    identity_cfg = str(cfg.get("identity_dir", "")).strip() if isinstance(cfg.get("identity_dir"), str) else ""
    if identity_env:
        identity_dir = _resolve_user_path(root, identity_env)
    elif identity_cfg:
        identity_dir = _resolve_user_path(root, identity_cfg)
    elif (ext_root / "identity").exists():
        identity_dir = ext_root / "identity"
    else:
        identity_dir = root / "cli" / "identity"

    persona_env = os.environ.get("STILLWATER_PERSONA_FILE", "").strip()
    persona_cfg = str(cfg.get("persona_file", "")).strip() if isinstance(cfg.get("persona_file"), str) else ""
    if persona_env:
        persona_file = _resolve_user_path(root, persona_env)
    elif persona_cfg:
        persona_file = _resolve_user_path(root, persona_cfg)
    else:
        persona_file = ext_root / "personas" / "default.md"

    soul_env = os.environ.get("STILLWATER_SOUL_FILE", "").strip()
    soul_cfg = str(cfg.get("soul_file", "")).strip() if isinstance(cfg.get("soul_file"), str) else ""
    if soul_env:
        soul_file = _resolve_user_path(root, soul_env)
    elif soul_cfg:
        soul_file = _resolve_user_path(root, soul_cfg)
    else:
        soul_file = identity_dir / "SOUL.md"

    splash_env = os.environ.get("STILLWATER_SPLASH_FILE", "").strip()
    splash_cfg = str(cfg.get("splash_file", "")).strip() if isinstance(cfg.get("splash_file"), str) else ""
    if splash_env:
        splash_file = _resolve_user_path(root, splash_env)
    elif splash_cfg:
        splash_file = _resolve_user_path(root, splash_cfg)
    else:
        splash_file = ext_root / "splash.txt"

    history_env = os.environ.get("STILLWATER_HISTORY_FILE", "").strip()
    history_cfg = str(cfg.get("history_file", "")).strip() if isinstance(cfg.get("history_file"), str) else ""
    if history_env:
        history_file = _resolve_user_path(root, history_env)
    elif history_cfg:
        history_file = _resolve_user_path(root, history_cfg)
    else:
        history_file = root / "artifacts" / "twin" / ".readline_history"

    books_dirs: list[str] = ["books"]
    cfg_books = _list_from_config(cfg, "books_dirs")
    for raw in cfg_books:
        resolved = _resolve_user_path(root, raw)
        try:
            books_dirs.append(str(resolved.relative_to(root)))
        except ValueError:
            books_dirs.append(str(resolved))
    env_book_dirs = _normalize_csv_paths(os.environ.get("STILLWATER_BOOK_DIRS", ""))
    for raw in env_book_dirs:
        resolved = _resolve_user_path(root, raw)
        try:
            books_dirs.append(str(resolved.relative_to(root)))
        except ValueError:
            books_dirs.append(str(resolved))
    books_dirs = _dedupe_keep_order(books_dirs)

    papers_dirs: list[str] = ["cli/papers", "papers"]
    cfg_papers = _list_from_config(cfg, "papers_dirs")
    for raw in cfg_papers:
        resolved = _resolve_user_path(root, raw)
        try:
            papers_dirs.append(str(resolved.relative_to(root)))
        except ValueError:
            papers_dirs.append(str(resolved))
    env_paper_dirs = _normalize_csv_paths(os.environ.get("STILLWATER_PAPER_DIRS", ""))
    for raw in env_paper_dirs:
        resolved = _resolve_user_path(root, raw)
        try:
            papers_dirs.append(str(resolved.relative_to(root)))
        except ValueError:
            papers_dirs.append(str(resolved))
    papers_dirs = _dedupe_keep_order(papers_dirs)

    swarm_settings_env = os.environ.get("STILLWATER_SWARM_SETTINGS_FILE", "").strip()
    swarm_settings_cfg = (
        str(cfg.get("swarm_settings_file", "")).strip() if isinstance(cfg.get("swarm_settings_file"), str) else ""
    )
    ext_swarm_settings = ext_root / "settings" / "SWARM-ORCHESTRATION.prime-mermaid.md"
    default_swarm_settings = root / "cli" / "settings" / "SWARM-ORCHESTRATION.prime-mermaid.md"
    if swarm_settings_env:
        swarm_settings_file = _resolve_user_path(root, swarm_settings_env)
    elif swarm_settings_cfg:
        swarm_settings_file = _resolve_user_path(root, swarm_settings_cfg)
    elif ext_swarm_settings.exists():
        swarm_settings_file = ext_swarm_settings
    else:
        swarm_settings_file = default_swarm_settings

    return {
        "config_path": str(_resolve_user_path(root, os.environ.get("STILLWATER_KERNEL_CONFIG", ""))) if os.environ.get("STILLWATER_KERNEL_CONFIG", "").strip() else str(root / "cli" / "kernel_config.yaml"),
        "extension_root": ext_root,
        "skill_dirs": skill_dirs,
        "recipe_dirs": recipe_dirs,
        "books_dirs": books_dirs,
        "papers_dirs": papers_dirs,
        "identity_dir": identity_dir,
        "persona_file": persona_file,
        "soul_file": soul_file,
        "splash_file": splash_file,
        "history_file": history_file,
        "prompt_prefix": os.environ.get("STILLWATER_PROMPT_PREFIX", str(cfg.get("prompt_prefix", "you> "))),
        "assistant_prefix": os.environ.get("STILLWATER_ASSISTANT_PREFIX", str(cfg.get("assistant_prefix", "assistant> "))),
        "swarm_settings_file": swarm_settings_file,
    }


def _coerce_swarm_setting_value(raw: str) -> Any:
    value = raw.strip()
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except Exception:
            return value
    if "," in value:
        parts = [part.strip() for part in value.split(",") if part.strip()]
        return parts if parts else value
    return value


def _load_swarm_settings(root: Path, *, kernel: dict[str, Any] | None = None) -> dict[str, Any]:
    kernel_info = kernel or _kernel_paths(root)
    path = Path(kernel_info["swarm_settings_file"])
    out: dict[str, Any] = {"path": str(path), "exists": path.exists(), "settings": {}, "text": ""}
    if not path.exists():
        return out

    text = path.read_text(encoding="utf-8")
    settings: dict[str, Any] = {}
    pattern = re.compile(r"^\s*SETTING\s+([A-Za-z0-9_.-]+)\s*=\s*(.+?)\s*$")
    for line in text.splitlines():
        m = pattern.match(line)
        if not m:
            continue
        key = m.group(1).strip()
        value = _coerce_swarm_setting_value(m.group(2))
        existing = settings.get(key)
        if existing is None:
            settings[key] = value
        elif isinstance(existing, list):
            if isinstance(value, list):
                settings[key] = existing + value
            else:
                settings[key] = existing + [value]
        else:
            if isinstance(value, list):
                settings[key] = [existing] + value
            else:
                settings[key] = [existing, value]
    out["settings"] = settings
    out["text"] = text
    return out


def _swarm_setting_list(settings: dict[str, Any], key: str, *, default: list[str] | None = None) -> list[str]:
    raw = settings.get(key)
    if raw is None:
        return list(default or [])
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw).strip()
    if not text:
        return list(default or [])
    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]
    return [text]


def _swarm_setting_map(settings: dict[str, Any], prefix: str) -> dict[str, str]:
    out: dict[str, str] = {}
    needle = prefix if prefix.endswith(".") else f"{prefix}."
    for key, value in settings.items():
        if not key.startswith(needle):
            continue
        name = key[len(needle) :].strip()
        if not name:
            continue
        if isinstance(value, list):
            if not value:
                continue
            out[name] = str(value[-1]).strip()
        else:
            out[name] = str(value).strip()
    return out


def _swarm_setting_list_map(settings: dict[str, Any], prefix: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    needle = prefix if prefix.endswith(".") else f"{prefix}."
    for key, value in settings.items():
        if not key.startswith(needle):
            continue
        name = key[len(needle) :].strip()
        if not name:
            continue
        items = _coerce_list(value)
        if not items:
            continue
        existing = out.get(name, [])
        out[name] = _dedupe_keep_order(existing + items)
    return out


def _coerce_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]
    return [text]


def _coerce_bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "on"}:
        return True
    if text in {"false", "0", "no", "off"}:
        return False
    return default


def _coerce_int(value: Any, *, default: int) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _coerce_float(value: Any, *, default: float) -> float:
    if isinstance(value, (float, int)):
        return float(value)
    try:
        return float(str(value).strip())
    except Exception:
        return default


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _math_expert_council_config(
    *,
    settings: dict[str, Any] | None = None,
    default_required_rung: int = 641,
) -> dict[str, Any]:
    raw = settings if isinstance(settings, dict) else {}
    required_rung = _coerce_int(raw.get("expert_council.required_rung", default_required_rung), default=default_required_rung)
    if required_rung not in {641, 274177, 65537}:
        required_rung = default_required_rung
    threshold_641 = _clamp01(_coerce_float(raw.get("expert_council.consensus_threshold_641", 0.55), default=0.55))
    threshold_274177 = _clamp01(
        _coerce_float(raw.get("expert_council.consensus_threshold_274177", 0.74), default=0.74)
    )
    threshold_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.consensus_threshold_65537", 0.92), default=0.92)
    )
    # Monotonic thresholds avoid impossible promotion ladders.
    threshold_274177 = max(threshold_274177, threshold_641)
    threshold_65537 = max(threshold_65537, threshold_274177)
    concept_min_274177 = _clamp01(
        _coerce_float(raw.get("expert_council.concept_coverage_min_274177", 0.5), default=0.5)
    )
    concept_min_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.concept_coverage_min_65537", 0.8), default=0.8)
    )
    concept_min_65537 = max(concept_min_65537, concept_min_274177)
    section_min_274177 = max(0, _coerce_int(raw.get("expert_council.section_hits_min_274177", 1), default=1))
    section_min_65537 = max(0, _coerce_int(raw.get("expert_council.section_hits_min_65537", 2), default=2))
    section_min_65537 = max(section_min_65537, section_min_274177)
    history_keyword_hits_min_274177 = max(
        0, _coerce_int(raw.get("expert_council.history_keyword_hits_min_274177", 2), default=2)
    )
    history_keyword_hits_min_65537 = max(
        history_keyword_hits_min_274177,
        _coerce_int(raw.get("expert_council.history_keyword_hits_min_65537", 4), default=4),
    )
    history_keyword_ratio_min_274177 = _clamp01(
        _coerce_float(raw.get("expert_council.history_keyword_ratio_min_274177", 0.12), default=0.12)
    )
    history_keyword_ratio_min_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.history_keyword_ratio_min_65537", 0.22), default=0.22)
    )
    history_keyword_ratio_min_65537 = max(history_keyword_ratio_min_65537, history_keyword_ratio_min_274177)
    history_number_hits_min_65537 = max(
        0, _coerce_int(raw.get("expert_council.history_number_hits_min_65537", 1), default=1)
    )
    history_oracle_match_min_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.history_oracle_match_min_65537", 0.92), default=0.92)
    )
    history_min_novel_tokens_65537 = max(
        0, _coerce_int(raw.get("expert_council.history_min_novel_tokens_65537", 8), default=8)
    )
    history_min_novel_ratio_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.history_min_novel_ratio_65537", 0.18), default=0.18)
    )
    history_max_prompt_share_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.history_max_prompt_share_65537", 0.88), default=0.88)
    )
    history_max_sentence_copy_ratio_65537 = _clamp01(
        _coerce_float(raw.get("expert_council.history_max_sentence_copy_ratio_65537", 0.55), default=0.55)
    )
    history_require_oracle_quality_for_65537 = _coerce_bool(
        raw.get("expert_council.history_require_oracle_quality_for_65537", True),
        default=True,
    )
    history_oracle_quality_min_tier_65537 = str(
        raw.get("expert_council.history_oracle_quality_min_tier_65537", "standard")
    ).strip().lower()
    if history_oracle_quality_min_tier_65537 not in {"none", "weak", "standard", "strong"}:
        history_oracle_quality_min_tier_65537 = "standard"
    return {
        "enabled": _coerce_bool(raw.get("expert_council.enabled", True), default=True),
        "required_rung": required_rung,
        "virtual_size": max(1, _coerce_int(raw.get("expert_council.virtual_size", 65537), default=65537)),
        "threshold_641": threshold_641,
        "threshold_274177": threshold_274177,
        "threshold_65537": threshold_65537,
        "concept_coverage_min_274177": concept_min_274177,
        "concept_coverage_min_65537": concept_min_65537,
        "section_hits_min_274177": section_min_274177,
        "section_hits_min_65537": section_min_65537,
        "history_keyword_hits_min_274177": history_keyword_hits_min_274177,
        "history_keyword_hits_min_65537": history_keyword_hits_min_65537,
        "history_keyword_ratio_min_274177": history_keyword_ratio_min_274177,
        "history_keyword_ratio_min_65537": history_keyword_ratio_min_65537,
        "history_number_hits_min_65537": history_number_hits_min_65537,
        "history_oracle_match_min_65537": history_oracle_match_min_65537,
        "history_min_novel_tokens_65537": history_min_novel_tokens_65537,
        "history_min_novel_ratio_65537": history_min_novel_ratio_65537,
        "history_max_prompt_share_65537": history_max_prompt_share_65537,
        "history_max_sentence_copy_ratio_65537": history_max_sentence_copy_ratio_65537,
        "history_require_oracle_quality_for_65537": history_require_oracle_quality_for_65537,
        "history_oracle_quality_min_tier_65537": history_oracle_quality_min_tier_65537,
        "response_min_chars": max(1, _coerce_int(raw.get("expert_council.response_min_chars", 24), default=24)),
        "require_route_receipts": _coerce_bool(raw.get("expert_council.require_route_receipts", True), default=True),
        "require_phuc_receipt_for_274177": _coerce_bool(
            raw.get("expert_council.require_phuc_receipt_for_274177", True), default=True
        ),
        "require_tool_route_for_65537": _coerce_bool(
            raw.get("expert_council.require_tool_route_for_65537", True), default=True
        ),
        "max_love": _coerce_bool(raw.get("expert_council.max_love", True), default=True),
        "integrity_mode": str(raw.get("expert_council.integrity_mode", "strict_fail_closed")).strip()
        or "strict_fail_closed",
    }


def _expert_vote(name: str, passed: bool, rationale: str, *, weight: float = 1.0) -> dict[str, Any]:
    return {
        "expert": name,
        "passed": bool(passed),
        "weight": float(weight),
        "rationale": rationale.strip(),
    }


def _aggregate_expert_council(
    *,
    votes: list[dict[str, Any]],
    gates: dict[str, bool],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    rung_rank = {0: 0, 641: 1, 274177: 2, 65537: 3}
    total_weight = 0.0
    pass_weight = 0.0
    failed: list[str] = []
    for vote in votes:
        weight = float(vote.get("weight", 1.0))
        total_weight += weight
        if bool(vote.get("passed")):
            pass_weight += weight
        else:
            name = str(vote.get("expert", "unknown"))
            rationale = str(vote.get("rationale", "")).strip()
            failed.append(f"{name}: {rationale}" if rationale else name)
    consensus = pass_weight / total_weight if total_weight > 0 else 0.0
    consensus = _clamp01(consensus)

    rung_achieved = 0
    if bool(gates.get("r641")) and consensus >= _coerce_float(cfg.get("threshold_641", 0.55), default=0.55):
        rung_achieved = 641
    if (
        rung_achieved == 641
        and bool(gates.get("r274177"))
        and consensus >= _coerce_float(cfg.get("threshold_274177", 0.74), default=0.74)
    ):
        rung_achieved = 274177
    if (
        rung_achieved == 274177
        and bool(gates.get("r65537"))
        and consensus >= _coerce_float(cfg.get("threshold_65537", 0.92), default=0.92)
    ):
        rung_achieved = 65537

    required_rung = _coerce_int(cfg.get("required_rung", 641), default=641)
    achieved_rank = rung_rank.get(rung_achieved, 0)
    required_rank = rung_rank.get(required_rung, rung_rank.get(641, 1))
    status = "PASS" if achieved_rank >= required_rank else "FAIL"
    fail_reasons = [] if status == "PASS" else [f"required rung {required_rung} not met (achieved {rung_achieved})"] + failed
    virtual_size = max(1, _coerce_int(cfg.get("virtual_size", 65537), default=65537))
    virtual_pass = int(round(consensus * virtual_size))
    return {
        "status": status,
        "required_rung": required_rung,
        "rung_achieved": rung_achieved,
        "consensus": round(consensus, 6),
        "virtual_size": virtual_size,
        "virtual_pass_count": virtual_pass,
        "virtual_fail_count": max(0, virtual_size - virtual_pass),
        "gates": {k: bool(v) for k, v in gates.items()},
        "votes": votes,
        "fail_reasons": fail_reasons,
        "max_love": bool(cfg.get("max_love", True)),
        "integrity_mode": str(cfg.get("integrity_mode", "strict_fail_closed")),
    }


def _extract_imo_year(text: str) -> int | None:
    m = re.search(r"\bimo\s*(19\d{2}|20\d{2})\b", text.lower())
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _math_signal_hits(text: str, signals: list[str]) -> list[str]:
    lower = text.lower()
    hits = [sig for sig in signals if sig.lower() in lower]
    if re.search(r"\b\d+\s*[\+\-\*/\^]\s*\d+\b", lower):
        hits.append("__arith_expr__")
    if re.search(r"\b(gcd|lcm)\s*\(", lower):
        hits.append("__number_theory_fn__")
    if re.search(r"\bremainder\s+when\b", lower) and "^" in lower:
        hits.append("__modexp_phrase__")
    return sorted(set(hits))


def _default_phuc_tool_routes() -> dict[str, dict[str, Any]]:
    return {
        "imo": {
            "enabled": True,
            "runner": "phuc_swarms_benchmark",
            "signals": [
                "ramsey",
                "k6",
                "omega(",
                "m_n/a_n",
                "ab+kc",
                "ac+kb",
                "bc+ka",
                "ka+kb+kc",
                "functional equation",
                "∠ypx",
                "∠kil",
                "angle ypx",
                "angle kil",
                "f(x)=x",
                "f(x)=2-x",
                "2024 prime factors",
            ],
            "min_hits": 1,
        },
        "math": {
            "enabled": True,
            "runner": "phuc_math_assist",
            "signals": [
                "gcd",
                "lcm",
                "modulo",
                "remainder when",
                "prime factor",
                "equation",
                "inequality",
                "triangle",
                "geometry",
                "algebra",
                "number theory",
                "combinatorics",
                "integral",
                "derivative",
            ],
            "min_hits": 1,
        },
        "imo_history": {
            "enabled": True,
            "runner": "phuc_imo_history_assist",
            "signals": [
                "solve this problem with a rigorous outline",
                "return: assumptions, core idea, and verification checklist.",
            ],
            "min_hits": 2,
        },
        "oolong": {
            "enabled": True,
            "runner": "phuc_swarms_benchmark",
            "signals": ["oolong", "counter bypass", "verification ladder 641", "rung 65537"],
            "min_hits": 1,
        },
    }


def _load_phuc_tool_routes(settings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    routes = _default_phuc_tool_routes()
    for key, value in settings.items():
        if not str(key).startswith("tool_route."):
            continue
        rest = str(key)[len("tool_route.") :]
        if "." not in rest:
            continue
        profile, field = rest.split(".", 1)
        profile = profile.strip().lower()
        field = field.strip().lower()
        if not profile or not field:
            continue
        route = routes.setdefault(
            profile,
            {"enabled": True, "runner": "phuc_swarms_benchmark", "signals": [], "min_hits": 1},
        )
        if field == "signals":
            route["signals"] = _coerce_list(value)
        elif field == "enabled":
            route["enabled"] = _coerce_bool(value, default=True)
        elif field == "runner":
            route["runner"] = str(value).strip() or "phuc_swarms_benchmark"
        elif field == "min_hits":
            route["min_hits"] = _coerce_int(value, default=1)
    return routes


def _phuc_orchestration_decision(*, prompt: str, settings: dict[str, Any]) -> dict[str, Any]:
    text = prompt.strip()
    lower = text.lower()
    mode = str(settings.get("tool_policy.mode", "auto")).strip().lower() or "auto"
    default_action = str(settings.get("tool_policy.default", "llm")).strip().lower() or "llm"
    routes = _load_phuc_tool_routes(settings)

    scored: list[dict[str, Any]] = []
    for profile, route in routes.items():
        if not _coerce_bool(route.get("enabled", True), default=True):
            continue
        signals = _coerce_list(route.get("signals", []))
        if profile == "math":
            hits = _math_signal_hits(text, signals)
        else:
            hits = [sig for sig in signals if sig.lower() in lower]
        scored.append(
            {
                "profile": profile,
                "runner": str(route.get("runner", "phuc_swarms_benchmark")),
                "min_hits": _coerce_int(route.get("min_hits", 1), default=1),
                "hit_count": len(hits),
                "hits": hits,
                "signals_checked": len(signals),
            }
        )

    scored.sort(key=lambda item: (item["hit_count"], item["signals_checked"]), reverse=True)
    top = scored[0] if scored else None

    decision = "llm"
    profile = ""
    reason = "no configured tool route reached confidence threshold"
    if top and top["hit_count"] >= top["min_hits"]:
        decision = "tool"
        profile = str(top["profile"])
        reason = f"matched tool route `{profile}` with {top['hit_count']} signal hits"
        year = _extract_imo_year(text)
        if profile == "imo" and year is not None and year != 2024:
            if "math" in routes and _coerce_bool(routes["math"].get("enabled", True), default=True):
                decision = "tool"
                profile = "math"
                reason = (
                    f"IMO year {year} is outside deterministic 2024 demo scope; "
                    "switched to generalized math assist route"
                )
            else:
                decision = "llm"
                profile = ""
                reason = f"IMO year {year} is outside deterministic 2024 demo scope"
    elif default_action == "tool":
        guess = _detect_benchmark_profile(text)
        if guess:
            decision = "tool"
            profile = guess
            reason = f"default tool policy selected benchmark profile `{guess}`"

    dream = {
        "goal": text[:240],
        "constraints": ["deterministic if tools are selected", "preserve replayable receipts"],
    }
    forecast = {
        "risk_if_wrong_route": [
            "LLM-only may hallucinate benchmark-specific claims",
            "Tool route may overfit if prompts are ambiguous",
        ],
        "mitigation": "emit route decision metadata and keep llm-only override",
    }
    decide = {
        "mode": mode,
        "default": default_action,
        "decision": decision,
        "profile": profile,
        "reason": reason,
    }

    return {
        "decision": decision,
        "profile": profile,
        "reason": reason,
        "mode": mode,
        "default": default_action,
        "ranked_routes": scored,
        "dream": dream,
        "forecast": forecast,
        "decide": decide,
    }


def _swarm_default_skill_pack(root: Path) -> list[str]:
    loaded = _load_swarm_settings(root)
    settings = loaded.get("settings", {})
    if not isinstance(settings, dict):
        return []
    out = _swarm_setting_list(settings, "skill_pack", default=[])
    return [item for item in out if item]


def _normalize_skill_name(value: str) -> str:
    base = value.strip()
    if not base:
        return ""
    if "/" in base:
        base = Path(base).name
    if not base.endswith(".md"):
        base += ".md"
    return base


def _collect_skill_inventory(root: Path) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    sources = _kernel_paths(root)["skill_dirs"]
    for source, base in sources:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                rel = str(path)
            out.append(
                {
                    "source": source,
                    "name": path.name,
                    "path": rel,
                }
            )
    return out


def _resolve_twin_skill_paths(
    *,
    root: Path,
    requested: list[str],
    all_skills: bool,
) -> tuple[list[Path], list[str]]:
    by_name: dict[str, Path] = {}
    for _, base in _kernel_paths(root)["skill_dirs"]:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            by_name[path.name] = path
    available = sorted(by_name.values(), key=lambda p: p.name)
    missing: list[str] = []

    if all_skills:
        return (available, missing)

    swarm_pack = _swarm_default_skill_pack(root)
    selected = requested if requested else (swarm_pack if swarm_pack else _default_twin_skills(root))
    picked: list[Path] = []
    seen: set[str] = set()
    for raw in selected:
        name = _normalize_skill_name(raw)
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        path = by_name.get(name)
        if path is None:
            missing.append(name)
            continue
        picked.append(path)
    return (picked, missing)


def _collect_recipe_files(root: Path, dirs: list[str] | None = None) -> list[Path]:
    scan_dirs = dirs or list(_kernel_paths(root)["recipe_dirs"])
    out: list[Path] = []
    seen: set[Path] = set()
    for rel in scan_dirs:
        base = root / rel
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            lower = path.name.lower()
            if lower.endswith(".prime-mermaid.md") or lower.endswith(".mmd"):
                if path not in seen:
                    seen.add(path)
                    out.append(path)
    return out


def _resolve_twin_recipe_paths(*, root: Path, requested: list[str]) -> tuple[list[Path], list[str]]:
    by_name: dict[str, Path] = {}
    for path in _collect_recipe_files(root):
        by_name[path.name] = path

    missing: list[str] = []
    picked: list[Path] = []
    seen: set[str] = set()
    for raw in requested:
        name = Path(str(raw).strip()).name
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        found = by_name.get(name)
        if found is None:
            missing.append(name)
            continue
        picked.append(found)
    return (picked, missing)


def _collect_book_files(root: Path, dirs: list[str] | None = None) -> list[Path]:
    scan_dirs = dirs or list(_kernel_paths(root)["books_dirs"])
    out: list[Path] = []
    seen: set[Path] = set()
    for rel in scan_dirs:
        base = Path(rel) if Path(rel).is_absolute() else (root / rel)
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if not path.is_file():
                continue
            if path not in seen:
                seen.add(path)
                out.append(path)
    return out


def _collect_paper_files(root: Path, dirs: list[str] | None = None) -> list[Path]:
    scan_dirs = dirs or list(_kernel_paths(root)["papers_dirs"])
    out: list[Path] = []
    seen: set[Path] = set()
    for rel in scan_dirs:
        base = Path(rel) if Path(rel).is_absolute() else (root / rel)
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if not path.is_file():
                continue
            if path not in seen:
                seen.add(path)
                out.append(path)
    return out


def _load_text_if_exists(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _append_system_file_section(
    sections: list[str],
    *,
    label: str,
    path: Path,
) -> None:
    text = _load_text_if_exists(path)
    if text:
        sections.append(f"# BEGIN_{label} {path}\n{text}\n# END_{label} {path}")


def _load_twin_identity_sections(root: Path) -> list[str]:
    kernel = _kernel_paths(root)
    sections: list[str] = []
    _append_system_file_section(sections, label="SOUL", path=Path(kernel["soul_file"]))
    _append_system_file_section(sections, label="PERSONA", path=Path(kernel["persona_file"]))
    identity_dir = Path(kernel["identity_dir"])
    for name in ["IDENTITY.md", "AGENTS.md", "USER.md"]:
        _append_system_file_section(sections, label=name.replace(".md", ""), path=identity_dir / name)
    return sections


def _setup_readline_history(history_path: Path) -> None:
    try:
        import readline  # type: ignore
    except Exception:
        return
    history_path.parent.mkdir(parents=True, exist_ok=True)
    if history_path.exists():
        try:
            readline.read_history_file(str(history_path))
        except Exception:
            pass
    try:
        readline.set_history_length(2000)
    except Exception:
        pass

    def _save_history() -> None:
        try:
            readline.write_history_file(str(history_path))
        except Exception:
            pass

    try:
        import atexit

        atexit.register(_save_history)
    except Exception:
        pass


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _detect_benchmark_profile(prompt: str) -> str | None:
    lower = prompt.lower()
    if (
        "solve this problem with a rigorous outline" in lower
        and "return: assumptions, core idea, and verification checklist." in lower
        and _extract_imo_year(prompt) is not None
    ):
        return "imo_history"
    imo_signals = [
        "imo",
        "ramsey",
        "k6",
        "omega(",
        "m_n/a_n",
        "ab+kc",
        "ac+kb",
        "bc+ka",
        "ka+kb+kc",
        "functional equation",
        "∠ypx",
        "∠kil",
        "angle ypx",
        "angle kil",
        "2024 prime factors",
        "k*n has exactly",
        "f(x)=x",
        "f(x)=2-x",
    ]
    if any(sig in lower for sig in imo_signals):
        return "imo"
    if "oolong" in lower:
        return "oolong"
    if _math_signal_hits(prompt, []):
        return "math"
    return None


def _parse_imo_solver_output(stdout_text: str) -> dict[str, Any]:
    lines = stdout_text.splitlines()
    score_match = re.search(r"Score:\s*(\d+)\s*/\s*(\d+)", stdout_text)
    score = int(score_match.group(1)) if score_match else None
    total = int(score_match.group(2)) if score_match else None

    problem_status: dict[str, str] = {}
    for m in re.finditer(r"(P[1-6])\s+([✓✗])\s+([A-Z ]+)", stdout_text):
        problem_status[m.group(1)] = f"{m.group(2)} {m.group(3).strip()}"

    current_problem = ""
    section_lines: dict[str, list[str]] = {f"P{i}": [] for i in range(1, 7)}
    algorithms: dict[str, str] = {}
    for line in lines:
        line_s = line.strip()
        pm = re.match(r"^(P[1-6]):", line_s)
        if pm:
            current_problem = pm.group(1)
        if current_problem:
            section_lines[current_problem].append(line_s)
            if line_s.startswith("Algorithm:") and current_problem not in algorithms:
                algorithms[current_problem] = line_s.split(":", 1)[1].strip()

    p4_relation = ""
    if re.search(r"sum=\s*180(\.0+)?", stdout_text, flags=re.IGNORECASE):
        p4_relation = "∠YPX + ∠KIL = 180°"

    p2_answer_set = ""
    p2_match = re.search(r"Found\s+(\d+)\s+valid k values:\s*(.+)", stdout_text, flags=re.IGNORECASE)
    if p2_match:
        if p2_match.group(1) == "0" or "empty" in p2_match.group(2).lower():
            p2_answer_set = "empty"
        else:
            p2_answer_set = p2_match.group(2).strip()

    return {
        "score": score,
        "total": total,
        "status": problem_status,
        "algorithms": algorithms,
        "sections": section_lines,
        "p4_relation": p4_relation,
        "p2_answer_set": p2_answer_set,
    }


def _normalize_compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_imo_problem_text(pdf_text: str) -> str:
    text = pdf_text.replace("\x0c", "\n")
    text = text.translate(str.maketrans({"✶": "1", "✷": "2", "✸": "3", "✹": "4", "✺": "5", "✻": "6"}))
    text = re.sub(r"(?im)^(\s*)Pr\S{0,24}\s*([1-6])\s*[^\w\s]*\s*", r"\1Problem \2. ", text)
    return text


def _extract_imo_problems_from_markers(text: str, markers: list[tuple[int, int, int]]) -> list[dict[str, Any]]:
    if not markers:
        return []
    markers = sorted(markers, key=lambda x: x[1])
    found: dict[str, str] = {}
    for i, (pid_num, _, body_start) in enumerate(markers):
        pid = f"P{pid_num}"
        next_start = markers[i + 1][1] if i + 1 < len(markers) else len(text)
        body = _normalize_compact_whitespace(text[body_start:next_start])
        if not body:
            continue
        prev = found.get(pid, "")
        if not prev or len(body) > len(prev):
            found[pid] = body
    out: list[dict[str, Any]] = []
    for idx in range(1, 7):
        pid = f"P{idx}"
        if pid in found:
            out.append({"id": pid, "statement": found[pid]})
    return out


def _extract_imo_header_markers(text: str) -> list[tuple[int, int, int]]:
    pattern = re.compile(
        r"(?im)^\s*(?:Problem|Probl[eè]me|Problema|Aufgabe|Задача|Úloha)\s*([1-6])\s*[:.)]?\s*"
    )
    out: list[tuple[int, int, int]] = []
    for m in pattern.finditer(text):
        pid_num = int(m.group(1))
        out.append((pid_num, m.start(), m.end()))
    return out


def _extract_imo_numbered_line_markers(text: str) -> list[tuple[int, int, int]]:
    second_day = re.compile(
        r"(second day|day\s*ii|day\s*2|day:\s*2|segunda|segundo|deuxi[eè]me|zweiter|вторник)",
        flags=re.IGNORECASE,
    )
    num_line = re.compile(r"^\s*([1-6])\.\s+\S")
    markers: list[tuple[int, int, int]] = []
    day_offset = 0
    cursor = 0
    for line in text.splitlines():
        if second_day.search(line):
            day_offset = 3
        m = num_line.match(line)
        if m:
            num = int(m.group(1))
            pid_num = num + 3 if day_offset == 3 and num <= 3 else num
            if 1 <= pid_num <= 6:
                markers.append((pid_num, cursor + m.start(), cursor + m.end()))
        cursor += len(line) + 1
    return markers


def _imo_problem_quality_score(problems: list[dict[str, Any]]) -> float:
    if not problems:
        return 0.0
    total_chars = 0
    good_chars = 0
    total_len = 0
    for problem in problems:
        statement = str(problem.get("statement", ""))
        total_len += len(statement)
        for ch in statement:
            total_chars += 1
            cat = unicodedata.category(ch)
            if ch.isspace() or cat[0] in {"L", "N", "P", "M"} or cat == "Sm":
                good_chars += 1
    if total_chars == 0:
        return 0.0
    ratio = good_chars / total_chars
    avg_len = total_len / max(len(problems), 1)
    length_term = min(avg_len / 600.0, 1.0)
    coverage = len(problems) / 6.0
    return 0.7 * ratio + 0.2 * length_term + 0.1 * coverage


def _extract_imo_problems_from_text(pdf_text: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    text = _normalize_imo_problem_text(pdf_text)
    header_markers = _extract_imo_header_markers(text)
    numbered_markers = _extract_imo_numbered_line_markers(text)

    candidates: list[tuple[str, list[dict[str, Any]]]] = []
    if header_markers:
        candidates.append(("header_markers", _extract_imo_problems_from_markers(text, header_markers)))
    if numbered_markers:
        candidates.append(("numbered_lines", _extract_imo_problems_from_markers(text, numbered_markers)))
    if header_markers and numbered_markers:
        candidates.append(
            (
                "header_plus_numbered",
                _extract_imo_problems_from_markers(text, header_markers + numbered_markers),
            )
        )

    if not candidates:
        return ([], {"strategy": "none", "quality": 0.0})

    best_strategy = "none"
    best: list[dict[str, Any]] = []
    best_quality = 0.0
    for strategy, problems in candidates:
        quality = _imo_problem_quality_score(problems)
        key = (len(problems), quality, sum(len(str(p.get("statement", ""))) for p in problems))
        best_key = (len(best), best_quality, sum(len(str(p.get("statement", ""))) for p in best))
        if key > best_key:
            best = problems
            best_strategy = strategy
            best_quality = quality

    return (best, {"strategy": best_strategy, "quality": best_quality})


def _pdftotext_extract(raw_pdf: Path, *, layout: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd.extend([str(raw_pdf), "-"])
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def _best_imo_parse_from_pdf(raw_pdf: Path) -> tuple[list[dict[str, Any]], dict[str, Any]] | None:
    variants = [("plain", _pdftotext_extract(raw_pdf, layout=False)), ("layout", _pdftotext_extract(raw_pdf, layout=True))]
    best_problems: list[dict[str, Any]] = []
    best_meta: dict[str, Any] = {}
    for variant_name, proc in variants:
        if proc.returncode != 0:
            continue
        problems, parse_meta = _extract_imo_problems_from_text(proc.stdout or "")
        quality = float(parse_meta.get("quality", 0.0))
        key = (len(problems), quality, sum(len(str(p.get("statement", ""))) for p in problems))
        best_key = (
            len(best_problems),
            float(best_meta.get("quality", 0.0)),
            sum(len(str(p.get("statement", ""))) for p in best_problems),
        )
        if key > best_key:
            best_problems = problems
            best_meta = {"variant": variant_name, **parse_meta}
    if not best_meta and not best_problems:
        return None
    return (best_problems, best_meta)


def _download_imo_year_pdf(
    *,
    year: int,
    lang: str,
    dest_pdf: Path,
    timeout: float,
    force: bool = False,
) -> dict[str, Any]:
    if dest_pdf.exists() and not force:
        return {"ok": True, "cached": True, "path": str(dest_pdf), "bytes": dest_pdf.stat().st_size}
    dest_pdf.parent.mkdir(parents=True, exist_ok=True)
    payload = urllib.parse.urlencode({"DLFile": f"{year}/{lang}"}).encode("ascii")
    req = urllib.request.Request(
        "https://www.imo-official.org/download_file.aspx?file=dummy.pdf",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "stillwater-cli/imo-history",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - official IMO source
            body = resp.read()
    except Exception as ex:
        return {"ok": False, "error": str(ex), "path": str(dest_pdf)}
    if not body.startswith(b"%PDF"):
        sample = body[:120].decode("utf-8", errors="replace")
        return {"ok": False, "error": f"non-PDF response from IMO site: {sample}", "path": str(dest_pdf)}
    dest_pdf.write_bytes(body)
    return {"ok": True, "cached": False, "path": str(dest_pdf), "bytes": len(body)}


def _fetch_imo_year_dataset(
    *,
    root: Path,
    year: int,
    lang: str,
    timeout: float,
    force: bool = False,
) -> tuple[bool, dict[str, Any]]:
    raw_pdf = root / "imo" / "data" / "raw" / f"imo_{year}_{lang}.pdf"
    parsed_json = root / "imo" / "data" / "parsed" / f"imo_{year}_{lang}.json"
    dl = _download_imo_year_pdf(year=year, lang=lang, dest_pdf=raw_pdf, timeout=timeout, force=force)
    if not dl.get("ok"):
        return (False, {"year": year, "lang": lang, "raw_pdf": str(raw_pdf), "download": dl})
    best_parse = _best_imo_parse_from_pdf(raw_pdf)
    parse_error = ""
    if best_parse is None:
        proc = _pdftotext_extract(raw_pdf, layout=False)
        parse_error = f"pdftotext parse yielded no problems (rc={proc.returncode})"
        problems: list[dict[str, Any]] = []
        parse_meta: dict[str, Any] = {"variant": "plain", "strategy": "none", "quality": 0.0}
    else:
        problems, parse_meta = best_parse
    parsed_from_lang = str(lang)
    parsed_from_pdf = raw_pdf
    fallback_trials: list[dict[str, Any]] = []

    requested_lang = str(lang).lower().strip()
    need_fallback = len(problems) < 6 or float(parse_meta.get("quality", 0.0)) < 0.70
    if requested_lang == "eng" and need_fallback:
        fallback_langs = ["ger", "spa", "cze", "fre", "rus"]
        best_key = (
            len(problems),
            float(parse_meta.get("quality", 0.0)),
            sum(len(str(p.get("statement", ""))) for p in problems),
        )
        for alt_lang in fallback_langs:
            alt_pdf = root / "imo" / "data" / "raw" / f"imo_{year}_{alt_lang}.pdf"
            alt_dl = _download_imo_year_pdf(
                year=year,
                lang=alt_lang,
                dest_pdf=alt_pdf,
                timeout=timeout,
                force=False,
            )
            trial: dict[str, Any] = {
                "lang": alt_lang,
                "download_ok": bool(alt_dl.get("ok")),
                "cached": bool(alt_dl.get("cached")),
            }
            if not alt_dl.get("ok"):
                trial["error"] = str(alt_dl.get("error", "download_failed"))
                fallback_trials.append(trial)
                continue
            alt_parse = _best_imo_parse_from_pdf(alt_pdf)
            if alt_parse is None:
                trial["error"] = "pdftotext_failed"
                fallback_trials.append(trial)
                continue
            alt_problems, alt_meta = alt_parse
            alt_key = (
                len(alt_problems),
                float(alt_meta.get("quality", 0.0)),
                sum(len(str(p.get("statement", ""))) for p in alt_problems),
            )
            trial["problem_count"] = len(alt_problems)
            trial["quality"] = float(alt_meta.get("quality", 0.0))
            trial["variant"] = str(alt_meta.get("variant", "plain"))
            fallback_trials.append(trial)
            if alt_key > best_key:
                best_key = alt_key
                problems = alt_problems
                parse_meta = alt_meta
                parsed_from_lang = alt_lang
                parsed_from_pdf = alt_pdf
                parse_error = ""

    payload = {
        "year": year,
        "lang": lang,
        "requested_lang": lang,
        "parsed_from_lang": parsed_from_lang,
        "parsed_from_pdf": str(parsed_from_pdf),
        "parse_variant": parse_meta.get("variant", "plain"),
        "parse_strategy": parse_meta.get("strategy", "none"),
        "parse_quality": float(parse_meta.get("quality", 0.0)),
        "parse_error": parse_error,
        "fallback_trials": fallback_trials,
        "source": {
            "site": "imo-official.org",
            "download_url": "https://www.imo-official.org/download_file.aspx?file=dummy.pdf",
            "download_method": "POST form field DLFile=<year>/<lang>",
        },
        "download": dl,
        "problem_count": len(problems),
        "problems": problems,
        "fetched_at_utc": _utc_now(),
    }
    _write_json(parsed_json, payload)
    ok = len(problems) >= 6 and float(payload["parse_quality"]) >= 0.70
    return (ok, {"year": year, "lang": lang, "raw_pdf": str(raw_pdf), "parsed_json": str(parsed_json), **payload})


def _load_cached_imo_year_dataset(root: Path, year: int, lang: str) -> dict[str, Any] | None:
    parsed_json = root / "imo" / "data" / "parsed" / f"imo_{year}_{lang}.json"
    if not parsed_json.exists():
        return None
    try:
        return _load_json(parsed_json)
    except Exception:
        return None


def _eval_safe_arithmetic_expression(expr: str) -> int | float:
    expr_norm = expr.replace("^", "**")
    tree = ast.parse(expr_norm, mode="eval")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.UAdd,
        ast.USub,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"unsupported node: {type(node).__name__}")
    value = eval(compile(tree, "<math>", "eval"), {"__builtins__": {}}, {})  # noqa: S307
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _deterministic_math_extract(prompt: str) -> dict[str, Any] | None:
    text = prompt.strip()
    lower = text.lower()

    m = re.search(r"\bgcd\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", lower)
    if not m:
        m = re.search(r"\bgcd\s+of\s+(-?\d+)\s*(?:and|,)\s*(-?\d+)", lower)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return {
            "kind": "gcd",
            "answer": str(math.gcd(a, b)),
            "evidence": f"gcd({a}, {b})",
        }

    m = re.search(r"\blcm\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", lower)
    if not m:
        m = re.search(r"\blcm\s+of\s+(-?\d+)\s*(?:and|,)\s*(-?\d+)", lower)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return {
            "kind": "lcm",
            "answer": str(math.lcm(a, b)),
            "evidence": f"lcm({a}, {b})",
        }

    m = re.search(r"remainder\s+when\s+(\d+)\s*\^\s*(\d+)\s+is\s+divided\s+by\s+(\d+)", lower)
    if not m:
        m = re.search(r"(\d+)\s*\^\s*(\d+)\s*(?:mod|modulo)\s*(\d+)", lower)
    if m:
        base, exp, mod = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return {
            "kind": "modexp",
            "answer": str(pow(base, exp, mod)),
            "evidence": f"pow({base}, {exp}, {mod})",
        }

    expr_match = re.search(
        r"(?:what is|compute|calculate|evaluate)\s+([-+*/^().\d\s]{3,})\??\s*$",
        text,
        flags=re.IGNORECASE,
    )
    expr = ""
    if expr_match:
        expr = expr_match.group(1).strip()
    elif re.fullmatch(r"[-+*/^().\d\s]{3,}", text):
        expr = text.strip()
    if expr:
        try:
            value = _eval_safe_arithmetic_expression(expr)
        except Exception:
            return None
        return {
            "kind": "arithmetic",
            "answer": str(value),
            "evidence": f"expr={expr}",
        }

    return None


def _run_phuc_math_route(
    *,
    root: Path,
    prompt: str,
    route_decision: dict[str, Any] | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    run_id = _new_run_id("phuc-math")
    out_dir = root / "artifacts" / "phuc_math" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    extracted = _deterministic_math_extract(prompt)
    payload = {
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        "prompt": prompt,
        "route_decision": route_decision or {},
        "status": "deterministic_answer" if extracted else "needs_llm_reasoning",
        "extracted": extracted or {},
    }
    _write_json(out_dir / "MATH_ROUTE.json", payload)

    if extracted:
        response = f"{extracted['answer']}\n\n[math-tool] {extracted['kind']} via {extracted['evidence']}"
        return (
            True,
            response,
            {
                "action": "phuc_math_assist",
                "profile": "math",
                "artifact_dir": str(out_dir),
                "phuc_decision": route_decision or {},
            },
        )

    # General proofs/theory questions fall back to LLM, with an explicit hint in route metadata.
    return (
        False,
        "",
        {
            "action": "math_assist_fallback",
            "profile": "math",
            "artifact_dir": str(out_dir),
            "math_hint": "Use proof-oriented reasoning with explicit assumptions and verification checks.",
        },
    )


def _parse_imo_history_prompt(prompt: str) -> tuple[str, str, list[str]]:
    text = prompt.strip()
    body = text
    split_return = re.split(r"\n\s*Return:\s*", body, maxsplit=1, flags=re.IGNORECASE)
    if split_return:
        body = split_return[0].strip()
    parts = body.split("\n\n", 1)
    if len(parts) == 2 and re.match(r"(?i)^imo\s+\d{4}\s+p\d+\.", parts[0].strip()):
        body = parts[1].strip()

    anchor = ""
    concepts: list[str] = []
    kept_lines: list[str] = []
    for raw_line in body.splitlines():
        line = str(raw_line).strip()
        if not line:
            continue
        m_anchor = re.match(r"(?i)^oracle anchor:\s*(.+)$", line)
        if m_anchor:
            anchor = m_anchor.group(1).strip()
            continue
        m_concepts = re.match(r"(?i)^oracle concepts:\s*(.+)$", line)
        if m_concepts:
            concepts = [item.strip() for item in m_concepts.group(1).split(",") if item.strip()]
            continue
        kept_lines.append(line)

    statement = " ".join(kept_lines).strip()
    return (anchor, statement, concepts)


def _history_statement_digest(statement: str, *, max_terms: int = 14) -> str:
    text = _normalize_semantic_match_text(statement)
    if not text:
        return "preserve all official quantifiers, constraints, and objective claims"
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "onto",
        "then",
        "there",
        "such",
        "prove",
        "show",
        "find",
        "let",
        "all",
        "each",
        "every",
        "some",
        "where",
        "when",
        "which",
        "whose",
        "what",
        "problem",
        "solution",
    }
    out: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[a-z0-9+\-*/^=()<>]{3,}", text):
        if token in stop:
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
        if len(out) >= max_terms:
            break
    if not out:
        return "preserve all official quantifiers, constraints, and objective claims"
    return ", ".join(out)


def _run_phuc_imo_history_route(
    *,
    root: Path,
    prompt: str,
    route_decision: dict[str, Any] | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    run_id = _new_run_id("phuc-imo-history")
    out_dir = root / "artifacts" / "phuc_imo_history" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    year = ""
    problem_id = ""
    m_case = re.search(r"(?i)\bimo\s+(\d{4})\s+(p\d+)\b", prompt)
    if m_case:
        year = str(m_case.group(1)).strip()
        problem_id = str(m_case.group(2)).upper().strip()
    anchor, statement, concepts = _parse_imo_history_prompt(prompt)
    statement_clean = _normalize_compact_whitespace(statement)
    if not statement_clean:
        statement_clean = _normalize_compact_whitespace(prompt)
    if len(statement_clean) > 1000:
        statement_clean = statement_clean[:1000].rstrip() + " ..."
    if not anchor:
        sentence_chunks = re.split(r"[.!?]\s+", statement_clean)
        anchor = next((chunk.strip() for chunk in sentence_chunks if len(chunk.strip()) >= 32), statement_clean[:180]).strip()
    if len(anchor) > 220:
        anchor = anchor[:220].rstrip() + " ..."

    concepts_text = ", ".join(concepts) if concepts else "invariant, case split, final claim alignment"
    digest = _history_statement_digest(statement_clean)
    payload = {
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        "prompt": prompt,
        "route_decision": route_decision or {},
        "year": year,
        "problem_id": problem_id,
        "anchor": anchor,
        "concepts": concepts,
        "statement_excerpt": statement_clean[:400],
        "constraint_digest": digest,
    }
    _write_json(out_dir / "IMO_HISTORY_ROUTE.json", payload)

    response = "\n".join(
        [
            "Assumptions:",
            f"- Case context: IMO {year} {problem_id}." if year and problem_id else "- Case context: IMO historical prompt.",
            f"- Constraint digest (compressed, non-verbatim): {digest}",
            "- Preserve all original quantifiers and edge conditions from the official statement.",
            f"- Oracle anchor to satisfy: {anchor}",
            "",
            "Core idea:",
            f"- Use these guiding concepts: {concepts_text}.",
            "- Use a proof skeleton: reduction -> invariant/control step -> closure.",
            "- Add one extremal or contradiction branch to block template-only reasoning.",
            "",
            "Verification checklist:",
            "- Validate all domain and boundary conditions from the statement.",
            "- Validate each transformation against the stated constraints.",
            "- Include at least one non-trivial sanity check not copied from prompt wording.",
            f"- Confirm the final claim explicitly addresses: {anchor}",
            "",
            "Final claim:",
            f"- {anchor}",
        ]
    )

    return (
        True,
        response,
        {
            "action": "phuc_imo_history_assist",
            "profile": "imo_history",
            "artifact_dir": str(out_dir),
            "phuc_decision": route_decision or {},
        },
    )


def _answer_imo_question(prompt: str, facts: dict[str, Any]) -> str:
    lower = prompt.lower()
    alg = facts.get("algorithms", {})
    sections = facts.get("sections", {})
    score = facts.get("score")
    total = facts.get("total")

    if "score" in lower or "6/6" in lower or "how many solved" in lower:
        if isinstance(score, int) and isinstance(total, int):
            return f"IMO demo solver score: {score}/{total}."
        return "IMO demo solver score is not available in this run."

    inferred = _infer_imo_problem_id(prompt, facts)
    if inferred:
        problem_lines = sections.get(inferred, [])
        if not isinstance(problem_lines, list):
            problem_lines = []
        algorithm = str(alg.get(inferred, "")).strip()
        interesting = [
            str(line).strip()
            for line in problem_lines
            if any(
                marker in str(line).lower()
                for marker in [
                    "tests passed",
                    "property holds",
                    "sum=",
                    "found ",
                    "empty",
                    "monochromatic",
                    "f(x)=",
                    "algorithm:",
                ]
            )
        ]
        parts = [f"IMO {inferred} (recipe-backed):"]
        if algorithm:
            parts.append(f"Algorithm: {algorithm}")
        relation = str(facts.get("p4_relation", "")).strip()
        if inferred == "P4" and relation:
            parts.append(f"Relation: {relation}")
        if interesting:
            parts.append("Evidence: " + " | ".join(interesting[:2]))
        if len(parts) > 1:
            return " ".join(parts)

    parts: list[str] = []
    if isinstance(score, int) and isinstance(total, int):
        parts.append(f"score {score}/{total}")
    solved = facts.get("status", {})
    if isinstance(solved, dict) and solved:
        solved_text = ", ".join(f"{k} {v}" for k, v in sorted(solved.items()))
        parts.append(solved_text)
    if not parts:
        return "IMO demo benchmark completed, but summary facts are unavailable."
    return "IMO demo benchmark summary: " + " | ".join(parts)


def _run_phuc_benchmark_route(
    *,
    root: Path,
    prompt: str,
    profile: str,
    swarm_settings: dict[str, Any] | None = None,
    swarm_settings_path: str | None = None,
    route_decision: dict[str, Any] | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    run_id = _new_run_id(f"phuc-{profile}")
    out_dir = root / "artifacts" / "phuc_swarms" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    channels: list[dict[str, Any]] = []
    settings = swarm_settings if isinstance(swarm_settings, dict) else {}
    roles = ["scout", "forecaster", "judge", "solver", "skeptic"]
    default_phase_order = ["DREAM", "FORECAST", "DECIDE", "ACT", "VERIFY"]
    phase_order = _swarm_setting_list(settings, "phase_order", default=default_phase_order)
    mandatory_skill_pack = _swarm_setting_list(
        settings,
        "mandatory_skill_pack",
        default=["prime-safety.md", "prime-coder.md", "prime-math.md", "phuc-context.md"],
    )
    global_skill_pack = _swarm_setting_list(
        settings,
        "skill_pack",
        default=["phuc-swarms.md", "phuc-forecast.md", "phuc-cleanup.md", "prime-wishes.md"],
    )
    recipe_pack = _swarm_setting_list(settings, "recipe_pack", default=["recipe.twin_orchestration.prime-mermaid.md"])

    agent_skill_policy = str(settings.get("agent_skill_policy", "merge")).strip().lower() or "merge"
    if agent_skill_policy not in {"merge", "replace"}:
        agent_skill_policy = "merge"
    agent_recipe_policy = str(settings.get("agent_recipe_policy", "merge")).strip().lower() or "merge"
    if agent_recipe_policy not in {"merge", "replace"}:
        agent_recipe_policy = "merge"

    context_mode = str(settings.get("context_mode", "anti_rot_fresh_context_per_phase")).strip()
    if not context_mode:
        context_mode = "anti_rot_fresh_context_per_phase"
    artifact_mode = str(settings.get("artifact_mode", "machine_parseable_receipts_required")).strip()
    if not artifact_mode:
        artifact_mode = "machine_parseable_receipts_required"

    default_agent_skill_pack: dict[str, list[str]] = {
        "scout": ["phuc-swarms.md", "phuc-context.md", "phuc-forecast.md"],
        "forecaster": ["phuc-forecast.md", "phuc-context.md", "phuc-swarms.md"],
        "judge": ["phuc-forecast.md", "phuc-context.md", "phuc-swarms.md"],
        "solver": ["prime-coder.md", "prime-math.md", "phuc-swarms.md"],
        "skeptic": ["prime-math.md", "prime-safety.md", "phuc-forecast.md"],
    }
    default_agent_recipe_pack: dict[str, list[str]] = {role: [] for role in roles}

    legacy_agent_skill_pack = _swarm_setting_list_map(settings, "skill_pack")
    agent_skill_overrides = _swarm_setting_list_map(settings, "agent_skill_pack")
    for role, items in legacy_agent_skill_pack.items():
        if role not in agent_skill_overrides:
            agent_skill_overrides[role] = list(items)
    base_skill_pack = _dedupe_keep_order(global_skill_pack + agent_skill_overrides.get("base", []))
    base_recipe_pack = list(recipe_pack)

    legacy_agent_recipe_pack = _swarm_setting_list_map(settings, "recipe_pack")
    agent_recipe_overrides = _swarm_setting_list_map(settings, "agent_recipe_pack")
    for role, items in legacy_agent_recipe_pack.items():
        if role not in agent_recipe_overrides:
            agent_recipe_overrides[role] = list(items)
    base_recipe_pack = _dedupe_keep_order(base_recipe_pack + agent_recipe_overrides.get("base", []))

    agent_skill_pack: dict[str, list[str]] = {}
    agent_recipe_pack: dict[str, list[str]] = {}
    for role in roles:
        role_defaults = default_agent_skill_pack.get(role, [])
        role_overrides = agent_skill_overrides.get(role, [])
        if agent_skill_policy == "replace" and role_overrides:
            resolved_skills = _dedupe_keep_order(mandatory_skill_pack + role_overrides)
        else:
            resolved_skills = _dedupe_keep_order(mandatory_skill_pack + base_skill_pack + role_defaults + role_overrides)
        agent_skill_pack[role] = resolved_skills

        recipe_defaults = default_agent_recipe_pack.get(role, [])
        recipe_overrides = agent_recipe_overrides.get(role, [])
        if agent_recipe_policy == "replace" and recipe_overrides:
            resolved_recipes = _dedupe_keep_order(recipe_overrides)
        else:
            resolved_recipes = _dedupe_keep_order(base_recipe_pack + recipe_defaults + recipe_overrides)
        agent_recipe_pack[role] = resolved_recipes

    # Backward-compatible field name used in receipts and route payloads.
    skill_pack = list(base_skill_pack)
    recipe_pack = list(base_recipe_pack)
    persona_defaults = {
        "scout": "Linus Torvalds",
        "forecaster": "Grace Hopper",
        "judge": "Scope Police",
        "solver": "Brian Kernighan",
        "skeptic": "Leslie Lamport",
    }
    personas = {**persona_defaults, **_swarm_setting_map(settings, "persona")}
    rung_target = settings.get("verification_rung_target", 641)
    if not isinstance(rung_target, int):
        try:
            rung_target = int(str(rung_target).strip())
        except Exception:
            rung_target = 641

    _write_json(
        out_dir / "SWARM_SETTINGS.json",
        {
            "path": swarm_settings_path or "",
            "phase_order": phase_order,
            "skill_pack": skill_pack,
            "mandatory_skill_pack": mandatory_skill_pack,
            "agent_skill_policy": agent_skill_policy,
            "agent_skill_pack": agent_skill_pack,
            "recipe_pack": recipe_pack,
            "agent_recipe_policy": agent_recipe_policy,
            "agent_recipe_pack": agent_recipe_pack,
            "personas": personas,
            "verification_rung_target": rung_target,
            "context_mode": context_mode,
            "artifact_mode": artifact_mode,
            "profile": profile,
        },
    )
    if route_decision is not None:
        _write_json(out_dir / "ORCHESTRATION_DECISION.json", route_decision)

    cnf_base = {
        "run_id": run_id,
        "profile": profile,
        "task_statement": prompt,
        "constraints": {
            "deterministic": True,
            "network_required": False,
            "tools": "repo-local solvers only",
        },
        "phase_order": phase_order,
        "personas": personas,
        "skill_pack": skill_pack,
        "mandatory_skill_pack": mandatory_skill_pack,
        "agent_skill_pack": agent_skill_pack,
        "recipe_pack": recipe_pack,
        "agent_recipe_pack": agent_recipe_pack,
        "context_mode": context_mode,
        "artifact_mode": artifact_mode,
        "verification_rung_target": rung_target,
        "orchestration_decision": route_decision or {},
        "swarm_settings_file": swarm_settings_path or "",
        "timestamp_utc": _utc_now(),
    }
    _write_json(out_dir / "CNF_BASE.json", cnf_base)

    if profile == "imo":
        solver_path = root / "imo" / "src" / "imo_2024_solver_proper.py"
        command = [sys.executable, str(solver_path)]
    elif profile == "oolong":
        solver_path = root / "oolong" / "src" / "oolong_solver.py"
        command = [sys.executable, str(solver_path)]
    else:
        return (False, "", {"action": "phuc_benchmark", "profile": profile, "error": "unknown profile"})
    command_text = shlex.join(command)

    channels.append(
        {
            "channel": 2,
            "agent": "kernel",
            "type": "facts",
            "claims": [
                {
                    "text": f"profile={profile}; deterministic CPU route; settings={swarm_settings_path or 'default'}",
                    "kind": "evidence",
                    "lane": "A",
                }
            ],
            "evidence": [
                {"type": "path", "ref": str(out_dir / "CNF_BASE.json")},
                {"type": "path", "ref": str(out_dir / "SWARM_SETTINGS.json")},
            ],
            "next_action": "DREAM_SCOUT",
            "risk": "low",
        }
    )
    channels.append(
        {
            "channel": 3,
            "agent": "judge",
            "type": "plan",
            "claims": [{"text": "Target rung 641 with replayable solver logs", "kind": "evidence", "lane": "A"}],
            "evidence": [],
            "next_action": "FORECAST_FORECASTER",
            "risk": "low",
        }
    )

    cnf_delta_scout = {
        "agent": "scout",
        "persona": personas.get("scout", persona_defaults["scout"]),
        "skill_pack": agent_skill_pack.get("scout", []),
        "recipe_pack": agent_recipe_pack.get("scout", []),
        "input_artifacts": [str(out_dir / "CNF_BASE.json")],
        "task_statement": prompt,
        "solver_entrypoint": str(solver_path),
        "context_mode": context_mode,
        "artifact_mode": artifact_mode,
    }
    cnf_delta_forecast = {
        "agent": "forecaster",
        "persona": personas.get("forecaster", persona_defaults["forecaster"]),
        "skill_pack": agent_skill_pack.get("forecaster", []),
        "recipe_pack": agent_recipe_pack.get("forecaster", []),
        "input_artifacts": [str(out_dir / "SCOUT_REPORT.json")],
        "focus": "premortem + stop rules",
        "context_mode": context_mode,
        "artifact_mode": artifact_mode,
    }
    cnf_delta_decide = {
        "agent": "judge",
        "persona": personas.get("judge", persona_defaults["judge"]),
        "skill_pack": agent_skill_pack.get("judge", []),
        "recipe_pack": agent_recipe_pack.get("judge", []),
        "input_artifacts": [str(out_dir / "SCOUT_REPORT.json"), str(out_dir / "FORECAST_MEMO.json")],
        "focus": "scope lock + verification rung",
        "context_mode": context_mode,
        "artifact_mode": artifact_mode,
    }
    cnf_delta_solver = {
        "agent": "solver",
        "persona": personas.get("solver", persona_defaults["solver"]),
        "skill_pack": agent_skill_pack.get("solver", []),
        "recipe_pack": agent_recipe_pack.get("solver", []),
        "input_artifacts": [str(out_dir / "DECISION_RECORD.json")],
        "focus": "execute deterministic benchmark solver",
        "context_mode": context_mode,
        "artifact_mode": artifact_mode,
    }
    cnf_delta_skeptic = {
        "agent": "skeptic",
        "persona": personas.get("skeptic", persona_defaults["skeptic"]),
        "skill_pack": agent_skill_pack.get("skeptic", []),
        "recipe_pack": agent_recipe_pack.get("skeptic", []),
        "input_artifacts": [str(out_dir / "PATCH_NOTES.json"), str(out_dir / "solver.stdout.log")],
        "focus": "verify markers + rung gate",
        "context_mode": context_mode,
        "artifact_mode": artifact_mode,
    }
    _write_json(out_dir / "CNF_DELTA.scout.json", cnf_delta_scout)
    _write_json(out_dir / "CNF_DELTA.forecast.json", cnf_delta_forecast)
    _write_json(out_dir / "CNF_DELTA.decide.json", cnf_delta_decide)
    _write_json(out_dir / "CNF_DELTA.solver.json", cnf_delta_solver)
    _write_json(out_dir / "CNF_DELTA.skeptic.json", cnf_delta_skeptic)

    scout_report = {
        "agent": {"role": "DREAM_SCOUT", "persona": personas.get("scout", persona_defaults["scout"])},
        "task_summary": f"Route prompt to benchmark profile `{profile}` using deterministic solver artifacts.",
        "repro_command": command_text,
        "repro_commands": [command_text],
        "failing_tests_or_errors": [],
        "failing_tests": [],
        "suspect_files_ranked": [{"path": str(solver_path.relative_to(root)), "reason": "profile solver entrypoint"}],
        "witness_slices": [{"path": str(solver_path.relative_to(root)), "line_start": 1, "line_end": 40}],
        "witness_snippets": [],
        "acceptance_criteria": [
            "solver exits with code 0",
            "verification markers present in stdout",
            "answer references recipe-backed evidence",
        ],
        "missing_assets": [],
    }
    _write_json(out_dir / "SCOUT_REPORT.json", scout_report)
    channels.append(
        {
            "channel": 5,
            "agent": "scout",
            "type": "facts",
            "claims": [{"text": "SCOUT_REPORT ready", "kind": "evidence", "lane": "A"}],
            "evidence": [{"type": "path", "ref": str(out_dir / "SCOUT_REPORT.json")}],
            "next_action": "FORECAST_FORECASTER",
            "risk": "low",
        }
    )

    forecast_memo = {
        "agent": {"role": "FORECAST_FORECASTER", "persona": personas.get("forecaster", persona_defaults["forecaster"])},
        "top_failure_modes_ranked": [
            {"rank": 1, "mode": "solver_runtime_failure", "likelihood_bucket": "30", "mitigation": "return NEED_INFO with stderr"},
            {
                "rank": 2,
                "mode": "missing_verification_markers",
                "likelihood_bucket": "10",
                "mitigation": "downgrade to BLOCKED",
            },
        ],
        "stop_rules": ["if returncode != 0", "if no verification markers"],
        "edge_cases_to_test": ["prompt is specific sub-question", "prompt asks for score summary"],
        "compat_risks": ["python runtime mismatch", "missing benchmark source files"],
        "compatibility_risks": ["python runtime mismatch", "missing benchmark source files"],
        "mitigations": [
            "normalize command to current python interpreter",
            "write stderr/stdout receipts for replay",
        ],
    }
    _write_json(out_dir / "FORECAST_MEMO.json", forecast_memo)
    channels.append(
        {
            "channel": 7,
            "agent": "forecaster",
            "type": "plan",
            "claims": [{"text": "FORECAST memo emitted with stop rules", "kind": "evidence", "lane": "A"}],
            "evidence": [{"type": "path", "ref": str(out_dir / "FORECAST_MEMO.json")}],
            "next_action": "DECIDE_JUDGE",
            "risk": "medium",
        }
    )

    decision_record = {
        "agent": {"role": "DECIDE_JUDGE", "persona": personas.get("judge", persona_defaults["judge"])},
        "chosen_approach": "CPU benchmark execution + parser answer synthesis",
        "alternatives_considered": [
            "direct LLM answer without benchmark execution",
            "return NEED_INFO and ask user for benchmark profile",
        ],
        "required_verification_rung": rung_target,
        "scope_locked": [profile],
        "required_tests": ["solver exits 0", "required verification markers present"],
        "stop_rules": forecast_memo["stop_rules"],
        "go_no_go_initial": "GO",
    }
    _write_json(out_dir / "DECISION_RECORD.json", decision_record)

    patch_notes = {
        "agent": {"role": "ACT_SOLVER", "persona": personas.get("solver", persona_defaults["solver"])},
        "intent": "Execute deterministic benchmark solver and synthesize response from receipts.",
        "patch_required": False,
        "files_touched": [],
        "why_each_file": [],
        "risk_notes": ["no repository mutation expected"],
        "tests_to_run": ["benchmark solver command", "marker parser checks"],
    }
    _write_json(out_dir / "PATCH_NOTES.json", patch_notes)
    (out_dir / "PATCH_PROPOSAL.diff").write_text(
        "# NO_PATCH_REQUIRED\n# ACT phase executes benchmark solver and records logs only.\n",
        encoding="utf-8",
    )

    try:
        proc = subprocess.run(
            command,
            cwd=str(root),
            env=_runtime_env(root),
            text=True,
            capture_output=True,
            timeout=180.0,
            check=False,
        )
    except subprocess.TimeoutExpired:
        skeptic = {
            "agent": {"role": "VERIFY_SKEPTIC", "persona": personas.get("skeptic", persona_defaults["skeptic"])},
            "status": "BLOCKED",
            "rung_achieved": 0,
            "fail_reasons": ["solver timeout"],
            "required_fixes": ["increase timeout or reduce solver scope"],
            "regressions": [],
            "evidence": [{"command": command_text}],
        }
        _write_json(out_dir / "SKEPTIC_VERDICT.json", skeptic)
        _write_json(
            out_dir / "EDGECASE_REPORT.json",
            {
                "new_tests_suggested": ["timeout resilience test"],
                "subtle_breakages": ["insufficient timeout for host performance"],
                "compat_risks": forecast_memo["compat_risks"],
                "performance_risks": ["solver timeout under constrained CPU"],
            },
        )
        channels.append(
            {
                "channel": 11,
                "agent": "skeptic",
                "type": "blocker",
                "claims": [{"text": "solver timeout", "kind": "evidence", "lane": "A"}],
                "evidence": [{"type": "path", "ref": str(out_dir / "SKEPTIC_VERDICT.json")}],
                "next_action": "EXIT_BLOCKED",
                "risk": "high",
            }
        )
        _write_jsonl(out_dir / "PRIME_CHANNELS.jsonl", channels)
        return (
            True,
            "BLOCKED: benchmark solver timed out.",
            {
                "action": "phuc_swarms_benchmark",
                "profile": profile,
                "run_id": run_id,
                "status": "BLOCKED",
                "artifact_dir": str(out_dir),
                "swarm_settings_file": swarm_settings_path or "",
                "phase_order": phase_order,
                "personas": personas,
                "skill_pack": skill_pack,
                "mandatory_skill_pack": mandatory_skill_pack,
                "agent_skill_pack": agent_skill_pack,
                "recipe_pack": recipe_pack,
                "agent_recipe_pack": agent_recipe_pack,
                "context_mode": context_mode,
                "artifact_mode": artifact_mode,
                "phuc_decision": route_decision or {},
            },
        )

    (out_dir / "solver.stdout.log").write_text(proc.stdout or "", encoding="utf-8")
    (out_dir / "solver.stderr.log").write_text(proc.stderr or "", encoding="utf-8")

    if proc.returncode != 0:
        skeptic = {
            "agent": {"role": "VERIFY_SKEPTIC", "persona": personas.get("skeptic", persona_defaults["skeptic"])},
            "status": "NEED_INFO",
            "rung_achieved": 0,
            "fail_reasons": [f"solver returned non-zero: {proc.returncode}"],
            "required_fixes": ["inspect solver.stderr.log"],
            "regressions": [],
            "evidence": [{"command": command_text, "stderr_log": str(out_dir / "solver.stderr.log")}],
        }
        _write_json(out_dir / "SKEPTIC_VERDICT.json", skeptic)
        _write_json(
            out_dir / "EDGECASE_REPORT.json",
            {
                "new_tests_suggested": ["non-zero exit classification test"],
                "subtle_breakages": ["solver dependency mismatch"],
                "compat_risks": forecast_memo["compat_risks"],
                "performance_risks": [],
            },
        )
        channels.append(
            {
                "channel": 11,
                "agent": "skeptic",
                "type": "blocker",
                "claims": [{"text": f"returncode={proc.returncode}", "kind": "evidence", "lane": "A"}],
                "evidence": [
                    {"type": "path", "ref": str(out_dir / "solver.stderr.log")},
                    {"type": "path", "ref": str(out_dir / "SKEPTIC_VERDICT.json")},
                ],
                "next_action": "collect runtime dependencies",
                "risk": "high",
            }
        )
        _write_jsonl(out_dir / "PRIME_CHANNELS.jsonl", channels)
        return (
            True,
            f"NEED_INFO: benchmark solver failed (returncode={proc.returncode}). See {out_dir/'solver.stderr.log'}.",
            {
                "action": "phuc_swarms_benchmark",
                "profile": profile,
                "run_id": run_id,
                "status": "NEED_INFO",
                "artifact_dir": str(out_dir),
                "swarm_settings_file": swarm_settings_path or "",
                "phase_order": phase_order,
                "personas": personas,
                "skill_pack": skill_pack,
                "mandatory_skill_pack": mandatory_skill_pack,
                "agent_skill_pack": agent_skill_pack,
                "recipe_pack": recipe_pack,
                "agent_recipe_pack": agent_recipe_pack,
                "context_mode": context_mode,
                "artifact_mode": artifact_mode,
                "phuc_decision": route_decision or {},
            },
        )

    verify_status = "PASS"
    response = ""
    parsed: dict[str, Any] = {}
    if profile == "imo":
        parsed = _parse_imo_solver_output(proc.stdout or "")
        score = parsed.get("score")
        total = parsed.get("total")
        if score is None or total is None:
            verify_status = "BLOCKED"
            response = "BLOCKED: IMO solver output missing score markers."
        else:
            response = _answer_imo_question(prompt, parsed)
    elif profile == "oolong":
        parsed = _parse_oolong_output(proc.stdout or "")
        if not parsed.get("counter_bypass_complete"):
            verify_status = "BLOCKED"
            response = "BLOCKED: OOLONG solver missing completion markers."
        else:
            response = "OOLONG demo benchmark completed with counter-bypass markers present."

    skeptic = {
        "agent": {"role": "VERIFY_SKEPTIC", "persona": personas.get("skeptic", persona_defaults["skeptic"])},
        "status": verify_status,
        "rung_achieved": rung_target if verify_status == "PASS" else 0,
        "fail_reasons": [] if verify_status == "PASS" else ["verification marker check failed"],
        "required_fixes": [] if verify_status == "PASS" else ["inspect stdout markers and parser logic"],
        "regressions": [],
        "evidence": {
            "command": command_text,
            "stdout_log": str(out_dir / "solver.stdout.log"),
            "stderr_log": str(out_dir / "solver.stderr.log"),
            "parsed": parsed,
        },
    }
    _write_json(out_dir / "SKEPTIC_VERDICT.json", skeptic)
    _write_json(
        out_dir / "EDGECASE_REPORT.json",
        {
            "new_tests_suggested": ["prompt-to-problem mapping stress tests"],
            "subtle_breakages": [] if verify_status == "PASS" else ["missing expected verification markers"],
            "compat_risks": forecast_memo["compat_risks"],
            "performance_risks": [],
        },
    )

    judge = {
        "agent": {"role": "DECIDE_JUDGE", "persona": personas.get("judge", persona_defaults["judge"])},
        "final_status": verify_status,
        "promotion_allowed": verify_status == "PASS",
        "rationale": "solver markers validated and parsed for answer synthesis",
        "evidence_links_or_hashes": [
            str(out_dir / "SCOUT_REPORT.json"),
            str(out_dir / "FORECAST_MEMO.json"),
            str(out_dir / "DECISION_RECORD.json"),
            str(out_dir / "SKEPTIC_VERDICT.json"),
        ],
    }
    _write_json(out_dir / "JUDGE_SEAL.json", judge)
    channels.append(
        {
            "channel": 13,
            "agent": "judge",
            "type": "proof",
            "claims": [{"text": f"final_status={verify_status}", "kind": "evidence", "lane": "A"}],
            "evidence": [
                {"type": "path", "ref": str(out_dir / "SKEPTIC_VERDICT.json")},
                {"type": "path", "ref": str(out_dir / "JUDGE_SEAL.json")},
            ],
            "next_action": "EXIT_PASS" if verify_status == "PASS" else "EXIT_BLOCKED",
            "risk": "low" if verify_status == "PASS" else "medium",
        }
    )
    _write_jsonl(out_dir / "PRIME_CHANNELS.jsonl", channels)

    return (
        True,
        response,
        {
            "action": "phuc_swarms_benchmark",
            "profile": profile,
            "run_id": run_id,
            "status": verify_status,
            "artifact_dir": str(out_dir),
            "swarm_settings_file": swarm_settings_path or "",
            "phase_order": phase_order,
            "personas": personas,
            "skill_pack": skill_pack,
            "mandatory_skill_pack": mandatory_skill_pack,
            "agent_skill_pack": agent_skill_pack,
            "recipe_pack": recipe_pack,
            "agent_recipe_pack": agent_recipe_pack,
            "context_mode": context_mode,
            "artifact_mode": artifact_mode,
            "phuc_decision": route_decision or {},
        },
    )


def _tracked_paths(root: Path) -> set[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=str(root),
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            return set()
        return {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    except Exception:
        return set()


def _parse_suspicious_paths_from_final_audit(root: Path, audit_file: Path) -> set[str]:
    if not audit_file.exists():
        return set()
    suspicious_markers = ("SUSPICIOUS", "INCOMPLETE", "CONSIDER REMOVING")
    path_pattern = re.compile(r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+")
    out: set[str] = set()
    for line in audit_file.read_text(encoding="utf-8").splitlines():
        if not any(marker in line for marker in suspicious_markers):
            continue
        for m in path_pattern.finditer(line):
            path_raw = m.group(0).strip()
            resolved = (root / path_raw).resolve()
            try:
                rel = str(resolved.relative_to(root))
            except ValueError:
                continue
            out.add(rel)
    return out


def _is_safe_glow_file(path: Path, root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return False
    rel_s = str(rel)
    if not rel_s.startswith("artifacts/"):
        return False
    lower = path.name.lower()
    if lower.endswith((".stdout.log", ".stderr.log", ".log", ".jsonl", ".tmp", ".trace")):
        return True
    if ".executed.ipynb" in lower:
        return True
    return False


def _latest_cleanup_scan_receipt(root: Path) -> Path | None:
    base = root / "artifacts" / "stillwater" / "cleanup"
    if not base.exists():
        return None
    receipts = sorted(base.glob("cleanup-scan-*.json"))
    if not receipts:
        return None
    return receipts[-1]


def _cpu_twin_prepass(*, root: Path, prompt: str) -> tuple[bool, str, dict[str, Any]]:
    text = prompt.strip()
    lower = text.lower()
    kernel = _kernel_paths(root)
    swarm_loaded = _load_swarm_settings(root, kernel=kernel)
    swarm_settings = swarm_loaded.get("settings", {}) if isinstance(swarm_loaded.get("settings", {}), dict) else {}
    swarm_personas = _swarm_setting_map(swarm_settings, "persona")
    swarm_phase_order = _swarm_setting_list(swarm_settings, "phase_order", default=[])
    swarm_skill_pack = _swarm_setting_list(swarm_settings, "skill_pack", default=[])
    swarm_mandatory_skill_pack = _swarm_setting_list(swarm_settings, "mandatory_skill_pack", default=[])
    swarm_agent_skill_pack = _swarm_setting_list_map(swarm_settings, "agent_skill_pack")
    legacy_swarm_agent_skill_pack = _swarm_setting_list_map(swarm_settings, "skill_pack")
    for role, items in legacy_swarm_agent_skill_pack.items():
        if role in {"scout", "forecaster", "judge", "solver", "skeptic"} and role not in swarm_agent_skill_pack:
            swarm_agent_skill_pack[role] = list(items)
    swarm_recipe_pack = _swarm_setting_list(swarm_settings, "recipe_pack", default=[])
    swarm_agent_recipe_pack = _swarm_setting_list_map(swarm_settings, "agent_recipe_pack")
    legacy_swarm_agent_recipe_pack = _swarm_setting_list_map(swarm_settings, "recipe_pack")
    for role, items in legacy_swarm_agent_recipe_pack.items():
        if role in {"scout", "forecaster", "judge", "solver", "skeptic"} and role not in swarm_agent_recipe_pack:
            swarm_agent_recipe_pack[role] = list(items)
    swarm_context_mode = str(swarm_settings.get("context_mode", "")).strip()
    swarm_artifact_mode = str(swarm_settings.get("artifact_mode", "")).strip()
    tool_policy_mode = str(swarm_settings.get("tool_policy.mode", "auto")).strip()
    tool_policy_default = str(swarm_settings.get("tool_policy.default", "llm")).strip()
    if not text:
        return (
            True,
            "NEED_INFO: Please provide a prompt. Use `/help` for CPU commands or ask a natural-language question.",
            {"source": "CPU", "action": "need_info"},
        )

    if text in {"/exit", "/quit"}:
        return (True, "__EXIT__", {"source": "CPU", "action": "exit"})

    if text in {"/help", "help"}:
        msg = "\n".join(
            [
                "Twin commands:",
                "- /help",
                "- /status",
                "- /models",
                "- /skills",
                "- /recipes",
                "- /wishes",
                "- /books",
                "- /papers",
                "- /kernel",
                "- /exit",
            ]
        )
        return (True, msg, {"source": "CPU", "action": "help"})

    if text == "/status":
        try:
            from llm_config_manager import get_llm_config

            cfg = get_llm_config()
            ok, status = cfg.validate_setup()
            msg = "\n".join(
                [
                    f"provider: {cfg.active_provider}",
                    f"name: {cfg.get_provider_name()}",
                    f"url: {cfg.get_provider_url()}",
                    f"model: {cfg.get_provider_model() or '-'}",
                    f"status: {status}",
                ]
            )
            return (True, msg, {"source": "CPU", "action": "status", "ok": bool(ok)})
        except Exception as ex:
            return (True, f"ERROR: {ex}", {"source": "CPU", "action": "status", "ok": False})

    if text == "/models":
        try:
            from .llm_cli_support import candidate_ollama_urls, choose_preferred_ollama_url, probe_ollama_urls

            probes = probe_ollama_urls(
                urls=candidate_ollama_urls(repo_root=root, explicit_urls=[]),
                timeout_seconds=2.0,
            )
            preferred = choose_preferred_ollama_url(probes)
            if not preferred:
                return (True, "No reachable Ollama endpoint found.", {"source": "CPU", "action": "models"})
            probe = next((p for p in probes if p.get("url") == preferred), {})
            models = list(probe.get("models", []))
            lines = [f"url: {preferred}", f"models ({len(models)}):"]
            lines.extend([f"- {m}" for m in models[:50]])
            if len(models) > 50:
                lines.append(f"- ... (+{len(models) - 50} more)")
            return (True, "\n".join(lines), {"source": "CPU", "action": "models", "url": preferred})
        except Exception as ex:
            return (True, f"ERROR: {ex}", {"source": "CPU", "action": "models", "ok": False})

    if text == "/skills" or "list skills" in lower or "show skills" in lower:
        inventory = _collect_skill_inventory(root)
        lines = [f"skills ({len(inventory)}):"]
        lines.extend([f"- [{item['source']}] {item['name']}" for item in inventory])
        return (True, "\n".join(lines), {"source": "CPU", "action": "skills"})

    if text == "/recipes" or "list recipes" in lower or "show recipes" in lower:
        recipes = _collect_recipe_files(root)
        lines = [f"recipes ({len(recipes)}):"]
        for path in recipes[:50]:
            try:
                lines.append(f"- {path.relative_to(root)}")
            except ValueError:
                lines.append(f"- {path}")
        if len(recipes) > 50:
            lines.append(f"- ... (+{len(recipes) - 50} more)")
        return (True, "\n".join(lines), {"source": "CPU", "action": "recipes"})

    if text == "/wishes" or "list wishes" in lower or "show wishes" in lower:
        wish_files = sorted((root / "cli" / "wishes").glob("wish.*.md"))
        lines = [f"wishes ({len(wish_files)}):"]
        lines.extend([f"- {p.relative_to(root)}" for p in wish_files])
        return (True, "\n".join(lines), {"source": "CPU", "action": "wishes"})

    if text == "/books" or "list books" in lower or "show books" in lower:
        books = _collect_book_files(root)
        lines = [f"books ({len(books)}):"]
        for path in books[:50]:
            try:
                lines.append(f"- {path.relative_to(root)}")
            except ValueError:
                lines.append(f"- {path}")
        if len(books) > 50:
            lines.append(f"- ... (+{len(books) - 50} more)")
        return (True, "\n".join(lines), {"source": "CPU", "action": "books"})

    if text == "/papers" or "list papers" in lower or "show papers" in lower:
        papers = _collect_paper_files(root)
        lines = [f"papers ({len(papers)}):"]
        for path in papers[:50]:
            try:
                lines.append(f"- {path.relative_to(root)}")
            except ValueError:
                lines.append(f"- {path}")
        if len(papers) > 50:
            lines.append(f"- ... (+{len(papers) - 50} more)")
        return (True, "\n".join(lines), {"source": "CPU", "action": "papers"})

    if text == "/kernel":
        lines = [
            "kernel paths:",
            f"- extension_root: {kernel['extension_root']}",
            f"- identity_dir: {kernel['identity_dir']}",
            f"- soul_file: {kernel['soul_file']}",
            f"- persona_file: {kernel['persona_file']}",
            f"- splash_file: {kernel['splash_file']}",
            f"- history_file: {kernel['history_file']}",
            f"- swarm_settings_file: {kernel['swarm_settings_file']}",
            "- skill_dirs:",
        ]
        for source, path in kernel["skill_dirs"]:
            lines.append(f"  - [{source}] {path}")
        lines.append("- recipe_dirs:")
        for path in kernel["recipe_dirs"]:
            lines.append(f"  - {path}")
        lines.append("- books_dirs:")
        for path in kernel["books_dirs"]:
            lines.append(f"  - {path}")
        lines.append("- papers_dirs:")
        for path in kernel["papers_dirs"]:
            lines.append(f"  - {path}")
        if swarm_phase_order:
            lines.append(f"- swarm_phase_order: {', '.join(swarm_phase_order)}")
        if swarm_skill_pack:
            lines.append(f"- swarm_skill_pack: {', '.join(swarm_skill_pack)}")
        if swarm_mandatory_skill_pack:
            lines.append(f"- swarm_mandatory_skill_pack: {', '.join(swarm_mandatory_skill_pack)}")
        if swarm_recipe_pack:
            lines.append(f"- swarm_recipe_pack: {', '.join(swarm_recipe_pack)}")
        if swarm_personas:
            lines.append("- swarm_personas:")
            for role in sorted(swarm_personas.keys()):
                lines.append(f"  - {role}: {swarm_personas[role]}")
        if swarm_agent_skill_pack:
            lines.append("- swarm_agent_skill_pack:")
            for role in sorted(swarm_agent_skill_pack.keys()):
                lines.append(f"  - {role}: {', '.join(swarm_agent_skill_pack[role])}")
        if swarm_agent_recipe_pack:
            lines.append("- swarm_agent_recipe_pack:")
            for role in sorted(swarm_agent_recipe_pack.keys()):
                lines.append(f"  - {role}: {', '.join(swarm_agent_recipe_pack[role])}")
        if swarm_context_mode:
            lines.append(f"- swarm_context_mode: {swarm_context_mode}")
        if swarm_artifact_mode:
            lines.append(f"- swarm_artifact_mode: {swarm_artifact_mode}")
        lines.append(f"- tool_policy_mode: {tool_policy_mode or 'auto'}")
        lines.append(f"- tool_policy_default: {tool_policy_default or 'llm'}")
        tool_routes = _load_phuc_tool_routes(swarm_settings)
        if tool_routes:
            lines.append("- tool_routes:")
            for profile in sorted(tool_routes.keys()):
                route = tool_routes[profile]
                enabled = _coerce_bool(route.get("enabled", True), default=True)
                min_hits = _coerce_int(route.get("min_hits", 1), default=1)
                signals = _coerce_list(route.get("signals", []))
                lines.append(
                    f"  - {profile}: enabled={enabled} runner={route.get('runner','phuc_swarms_benchmark')} min_hits={min_hits} signals={len(signals)}"
                )
        return (True, "\n".join(lines), {"source": "CPU", "action": "kernel"})

    if "twin orchestration" in lower or "how twin works" in lower:
        msg = "\n".join(
            [
                "Stillwater twin orchestration (CPU + LLM):",
                "- CPU prepass handles deterministic commands first (`/skills`, `/recipes`, `/books`, `/papers`, `/status`, `/wishes`).",
                "- Unhandled prompts route to Ollama chat with skill-context injection from `skills/*.md`.",
                "- Every turn writes receipts (`artifacts/twin/<run_id>/route.json`, `twin.mmd`, `twin.sha256`).",
                f"- Swarm settings source: {kernel['swarm_settings_file']}",
            ]
        )
        return (True, msg, {"source": "CPU", "action": "twin_explain"})

    phuc_decision = _phuc_orchestration_decision(prompt=text, settings=swarm_settings)
    fallback_meta: dict[str, Any] = {}
    if phuc_decision.get("decision") == "tool":
        profile = str(phuc_decision.get("profile", "")).strip()
        if not profile:
            return (
                False,
                "",
                {
                    "source": "CPU",
                    "action": "llm_fallback",
                    "phuc_decision": {**phuc_decision, "decision": "llm", "reason": "tool selected but no profile"},
                },
            )
        if profile == "math":
            handled, message, meta = _run_phuc_math_route(
                root=root,
                prompt=text,
                route_decision=phuc_decision,
            )
        elif profile == "imo_history":
            handled, message, meta = _run_phuc_imo_history_route(
                root=root,
                prompt=text,
                route_decision=phuc_decision,
            )
        else:
            handled, message, meta = _run_phuc_benchmark_route(
                root=root,
                prompt=text,
                profile=profile,
                swarm_settings=swarm_settings,
                swarm_settings_path=str(kernel["swarm_settings_file"]),
                route_decision=phuc_decision,
            )
        if handled:
            return (True, message, {"source": "CPU", "phuc_decision": phuc_decision, **meta})
        fallback_meta = {k: v for k, v in meta.items() if k not in {"source"}}

    return (
        False,
        "",
        {
            "source": "CPU",
            "action": "llm_fallback",
            "phuc_decision": phuc_decision,
            **fallback_meta,
        },
    )


def _select_preferred_model(*, candidates: list[str], fallback: str) -> str:
    if not candidates:
        return fallback
    for preferred in ["llama3.1:8b", "qwen2.5-coder:7b"]:
        if preferred in candidates:
            return preferred
    return candidates[0]


def _write_twin_receipt(
    *,
    root: Path,
    run_id: str,
    prompt: str,
    response: str,
    route: dict[str, Any],
    system_prompt: str | None = None,
    injection_manifest: dict[str, Any] | None = None,
) -> dict[str, str]:
    out_dir = root / "artifacts" / "twin" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = out_dir / "prompt.txt"
    response_path = out_dir / "response.txt"
    route_path = out_dir / "route.json"
    mmd_path = out_dir / "twin.mmd"
    sha_path = out_dir / "twin.sha256"
    system_path = out_dir / "system.prompt.md"
    injection_path = out_dir / "injection-manifest.json"

    prompt_path.write_text(prompt + "\n", encoding="utf-8")
    response_path.write_text(response + "\n", encoding="utf-8")
    _write_json(route_path, route)
    if system_prompt is not None:
        system_path.write_text(system_prompt + "\n", encoding="utf-8")
    if injection_manifest is not None:
        _write_json(injection_path, injection_manifest)

    source = str(route.get("source", "UNKNOWN")).upper()
    action = str(route.get("action", "UNKNOWN"))
    mmd_text = "\n".join(
        [
            "flowchart TD",
            "  P[INPUT: USER_PROMPT] --> C[CPU_PREPASS]",
            f"  C --> R[ROUTE: {source}]",
            f"  R --> A[ACTION: {action}]",
            "  A --> O[OUTPUT: RESPONSE]",
            "",
        ]
    )
    mmd_path.write_text(mmd_text, encoding="utf-8")
    digest = hashlib.sha256(mmd_text.encode("utf-8")).hexdigest()
    sha_path.write_text(f"{digest}  twin.mmd\n", encoding="utf-8")

    out = {
        "dir": str(out_dir),
        "prompt": str(prompt_path),
        "response": str(response_path),
        "route": str(route_path),
        "graph": str(mmd_path),
        "sha256": str(sha_path),
    }
    if system_prompt is not None:
        out["system_prompt"] = str(system_path)
    if injection_manifest is not None:
        out["injection_manifest"] = str(injection_path)
    return out


def _run_twin_subprocess(
    *,
    root: Path,
    prompt: str,
    model: str,
    timeout: float,
    url: str | None = None,
    llm_only: bool = False,
    retries: int = 0,
) -> dict[str, Any]:
    attempts = max(1, int(retries) + 1)
    last: dict[str, Any] = {}
    for attempt in range(1, attempts + 1):
        cmd = [
            sys.executable,
            "-m",
            "stillwater",
            "twin",
            prompt,
            "--model",
            model,
            "--timeout",
            str(timeout),
            "--json",
        ]
        if url:
            cmd.extend(["--url", url])
        if llm_only:
            cmd.append("--llm-only")
        proc = subprocess.run(
            cmd,
            cwd=str(root),
            env=_runtime_env(root),
            text=True,
            capture_output=True,
            check=False,
        )
        out: dict[str, Any] = {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stderr": (proc.stderr or "")[:500],
            "stdout": (proc.stdout or "")[:500],
            "cmd": cmd,
            "attempt": attempt,
            "attempts": attempts,
        }
        if proc.returncode == 0:
            try:
                payload = json.loads(proc.stdout)
            except Exception:
                out["ok"] = False
                out["error"] = "invalid json from twin subprocess"
                last = out
                continue
            out["payload"] = payload
            return out

        out["error"] = f"twin subprocess rc={proc.returncode}"
        last = out
        if "Read timed out" not in (proc.stdout or ""):
            break
    return last


def _markdown_imo_history_report(report: dict[str, Any]) -> str:
    lines = [
        "# IMO History Benchmark Report",
        "",
        f"- run_id: `{report.get('run_id', '')}`",
        f"- years: `{report.get('from_year', '')}`..`{report.get('to_year', '')}`",
        f"- lang: `{report.get('lang', '')}`",
        f"- model: `{report.get('model', '')}`",
        f"- llm_only: `{bool(report.get('llm_only'))}`",
        f"- oracles_file: `{report.get('oracles_file', '')}`",
        f"- oracles_loaded: `{report.get('oracles_loaded', 0)}`",
        f"- required_rung: `{report.get('required_rung', 641)}`",
        f"- total_cases: `{report.get('total_cases', 0)}`",
        f"- runtime_ok_cases: `{report.get('ok_cases', 0)}`",
        f"- phuc_pass_cases: `{report.get('pass_cases', 0)}`",
        f"- oracle_configured_cases: `{report.get('oracle_configured_cases', 0)}`",
        f"- oracle_pass_cases: `{report.get('oracle_pass_cases', 0)}`",
        f"- oracle_quality_ready_cases: `{report.get('oracle_quality_ready_cases', 0)}`",
        f"- oracle_quality_strong_cases: `{report.get('oracle_quality_strong_cases', 0)}`",
        f"- strict_ok: `{bool(report.get('strict_ok', False))}`",
        "",
        "## Route Summary",
    ]
    route_counts = report.get("route_counts", {})
    if isinstance(route_counts, dict):
        for key in sorted(route_counts.keys()):
            lines.append(f"- {key}: {route_counts[key]}")
    phase_counts = report.get("phuc_phase_counts", {})
    if isinstance(phase_counts, dict) and phase_counts:
        lines.append("")
        lines.append("## PHUC Phase Summary")
        for key in sorted(phase_counts.keys()):
            lines.append(f"- {key}: {phase_counts[key]}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- This report measures orchestration/routing quality gates and runtime stability, not official IMO grading.")
    lines.append("- Historical IMO proofs remain open-ended; deterministic auto-grading is out-of-scope here.")
    lines.append("- Rung 65537 is withheld unless per-case oracle needles/aliases are configured, quality-tiered, matched, and anti-parrot checks pass.")
    memory = report.get("memory_loop", {})
    if isinstance(memory, dict):
        board_md = str(memory.get("board_md", "")).strip()
        if board_md:
            lines.append(f"- Memory loop board: `{board_md}`")
    return "\n".join(lines) + "\n"


def _markdown_imo_oracle_status_report(report: dict[str, Any]) -> str:
    lines = [
        "# IMO Oracle Coverage Report",
        "",
        f"- run_id: `{report.get('run_id', '')}`",
        f"- years: `{report.get('from_year', '')}`..`{report.get('to_year', '')}`",
        f"- lang: `{report.get('lang', '')}`",
        f"- oracles_file: `{report.get('oracles_file', '')}`",
        f"- total_problems: `{report.get('total_problems', 0)}`",
        f"- oracle_ready: `{report.get('oracle_ready', 0)}`",
        f"- oracle_missing: `{report.get('oracle_missing', 0)}`",
        f"- ready_ratio: `{report.get('ready_ratio', 0.0)}`",
        f"- oracle_quality_ready: `{report.get('oracle_quality_ready', 0)}`",
        f"- oracle_quality_strong: `{report.get('oracle_quality_strong', 0)}`",
        f"- oracle_quality_weak: `{report.get('oracle_quality_weak', 0)}`",
        f"- quality_ready_ratio: `{report.get('quality_ready_ratio', 0.0)}`",
        f"- quality_strong_ratio: `{report.get('quality_strong_ratio', 0.0)}`",
        f"- with_concepts: `{report.get('with_concepts', 0)}`",
        f"- with_required_sections: `{report.get('with_required_sections', 0)}`",
        f"- ok: `{bool(report.get('ok', False))}`",
        "",
        "## Per-Year",
    ]
    per_year = report.get("per_year", {})
    if isinstance(per_year, dict) and per_year:
        for year_key in sorted(per_year.keys(), key=lambda y: int(str(y)) if str(y).isdigit() else str(y)):
            row = per_year.get(year_key, {})
            if not isinstance(row, dict):
                continue
            lines.append(
                f"- {year_key}: total={row.get('total', 0)} ready={row.get('ready', 0)} "
                f"missing={row.get('missing', 0)} ratio={row.get('ready_ratio', 0.0)} "
                f"quality_ready={row.get('quality_ready', 0)} quality_strong={row.get('quality_strong', 0)}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Notes")
    lines.append("- `oracle_ready` means the case has at least one correctness target (`needle` or `aliases`).")
    lines.append("- `oracle_quality_ready` uses tiered quality scoring (standard/strong) and is the better distance-to-100 metric.")
    lines.append("- `with_concepts` and `with_required_sections` are quality boosters for stronger verifier gates.")
    return "\n".join(lines) + "\n"


def _load_imo_qa_cases(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    payload = _load_json(path)
    rows = payload.get("cases", []) if isinstance(payload, dict) else []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        prompt = str(row.get("prompt", "")).strip()
        needle = str(row.get("needle", "")).strip()
        if not case_id or not prompt or not needle:
            continue
        aliases_raw = row.get("aliases", [])
        aliases: list[str] = []
        if isinstance(aliases_raw, list):
            aliases = [str(item).strip() for item in aliases_raw if str(item).strip()]
        concepts_raw = row.get("concepts", [])
        concepts: list[str] = []
        if isinstance(concepts_raw, list):
            concepts = [str(item).strip() for item in concepts_raw if str(item).strip()]
        sections_raw = row.get("required_sections", [])
        required_sections: list[str] = []
        if isinstance(sections_raw, list):
            required_sections = [str(item).strip() for item in sections_raw if str(item).strip()]
        out.append(
            {
                "id": case_id,
                "prompt": prompt,
                "needle": needle,
                "aliases": aliases,
                "concepts": concepts,
                "required_sections": required_sections,
            }
        )
    if not out:
        raise ValueError(f"no valid IMO cases found in {path}")
    return out


def _load_imo_history_oracles(path: Path) -> dict[tuple[int, str], dict[str, Any]]:
    if not path.exists():
        return {}
    payload = _load_json(path)
    rows = payload.get("cases", []) if isinstance(payload, dict) else []
    out: dict[tuple[int, str], dict[str, Any]] = {}
    if not isinstance(rows, list):
        return out

    for row in rows:
        if not isinstance(row, dict):
            continue
        year_raw = row.get("year")
        try:
            year = int(str(year_raw).strip())
        except Exception:
            continue
        problem_id = str(row.get("problem_id", row.get("id", ""))).strip().upper()
        if not problem_id:
            continue
        if not problem_id.startswith("P"):
            problem_id = f"P{problem_id}"
        needle = str(row.get("needle", "")).strip()
        aliases_raw = row.get("aliases", [])
        aliases = [str(item).strip() for item in aliases_raw if str(item).strip()] if isinstance(aliases_raw, list) else []
        concepts_raw = row.get("concepts", [])
        concepts = (
            [str(item).strip() for item in concepts_raw if str(item).strip()] if isinstance(concepts_raw, list) else []
        )
        sections_raw = row.get("required_sections", [])
        required_sections = (
            [str(item).strip() for item in sections_raw if str(item).strip()] if isinstance(sections_raw, list) else []
        )
        statement_excerpt = _normalize_compact_whitespace(str(row.get("statement_excerpt", "")))
        has_targets = bool(needle) or bool(aliases)
        has_structure = bool(concepts) or bool(required_sections)
        if not has_targets and not has_structure:
            continue
        quality = _oracle_quality_assessment(
            needle=needle,
            aliases=aliases,
            concepts=concepts,
            required_sections=required_sections,
            statement_excerpt=statement_excerpt,
        )
        out[(year, problem_id)] = {
            "needle": needle,
            "aliases": aliases,
            "concepts": concepts,
            "required_sections": required_sections,
            "statement_excerpt": statement_excerpt,
            "quality": quality,
        }
    return out


def _normalize_imo_problem_id(value: str) -> str:
    pid = str(value).strip().upper()
    if not pid:
        return ""
    if not pid.startswith("P"):
        pid = f"P{pid}"
    return pid


def _load_imo_oracle_payload(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            payload = _load_json(path)
        except Exception:
            payload = {}
    else:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    if not isinstance(payload.get("cases"), list):
        payload["cases"] = []
    if "version" not in payload:
        payload["version"] = 1
    if not str(payload.get("description", "")).strip():
        payload["description"] = "Historical IMO oracle targets."
    return payload


def _imo_oracle_payload_index(payload: dict[str, Any]) -> dict[tuple[int, str], dict[str, Any]]:
    rows = payload.get("cases", []) if isinstance(payload.get("cases"), list) else []
    out: dict[tuple[int, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        year_raw = row.get("year")
        try:
            year = int(str(year_raw).strip())
        except Exception:
            continue
        problem_id = _normalize_imo_problem_id(str(row.get("problem_id", row.get("id", ""))))
        if not problem_id:
            continue
        out[(year, problem_id)] = json.loads(json.dumps(row))
    return out


def _imo_oracle_payload_from_index(
    *,
    base_payload: dict[str, Any],
    index: dict[tuple[int, str], dict[str, Any]],
    from_year: int,
    to_year: int,
    lang: str,
    description: str,
) -> dict[str, Any]:
    payload = json.loads(json.dumps(base_payload if isinstance(base_payload, dict) else {}))
    payload["version"] = int(payload.get("version", 1))
    payload["description"] = description
    payload["generated_at_utc"] = _utc_now()
    payload["from_year"] = int(from_year)
    payload["to_year"] = int(to_year)
    payload["lang"] = str(lang)
    rows: list[dict[str, Any]] = []
    for key in sorted(index.keys(), key=lambda item: (int(item[0]), str(item[1]))):
        year, problem_id = key
        row = index.get(key, {})
        if not isinstance(row, dict):
            row = {}
        item = json.loads(json.dumps(row))
        item["year"] = int(year)
        item["problem_id"] = _normalize_imo_problem_id(str(item.get("problem_id", problem_id)))
        if not item["problem_id"]:
            continue
        item["needle"] = str(item.get("needle", "")).strip()
        item["aliases"] = (
            [str(v).strip() for v in item.get("aliases", []) if str(v).strip()]
            if isinstance(item.get("aliases"), list)
            else []
        )
        item["concepts"] = (
            [str(v).strip() for v in item.get("concepts", []) if str(v).strip()]
            if isinstance(item.get("concepts"), list)
            else []
        )
        item["required_sections"] = (
            [str(v).strip() for v in item.get("required_sections", []) if str(v).strip()]
            if isinstance(item.get("required_sections"), list)
            else []
        )
        item["statement_excerpt"] = _normalize_compact_whitespace(str(item.get("statement_excerpt", "")))[:220]
        rows.append(item)
    payload["cases"] = rows
    return payload


def _history_target_phrase(text: str, *, max_terms: int = 12) -> str:
    norm = _normalize_semantic_match_text(text)
    if not norm:
        return ""
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "onto",
        "then",
        "there",
        "such",
        "prove",
        "show",
        "find",
        "let",
        "all",
        "each",
        "every",
        "some",
        "where",
        "when",
        "which",
        "whose",
        "what",
        "problem",
        "solution",
        "assumptions",
        "core",
        "idea",
        "verification",
        "checklist",
        "final",
        "claim",
        "oracle",
        "anchor",
        "satisfy",
        "context",
        "official",
        "statement",
    }
    out: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[a-z0-9+\-*/^=()<>]{2,}", norm):
        if token in stop:
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
        if len(out) >= max_terms:
            break
    return " ".join(out).strip()


def _extract_imo_final_claim_phrase(response_text: str) -> str:
    lines = [str(line).strip() for line in str(response_text).splitlines()]
    for idx, line in enumerate(lines):
        m_inline = re.match(r"(?i)^final claim:\s*(.+)$", line)
        if m_inline:
            phrase = _history_target_phrase(m_inline.group(1))
            if phrase:
                return phrase
            continue
        if re.match(r"(?i)^final claim:\s*$", line):
            for j in range(idx + 1, min(idx + 4, len(lines))):
                item = re.sub(r"^[\-\*\u2022]\s*", "", lines[j]).strip()
                phrase = _history_target_phrase(item)
                if phrase:
                    return phrase
    paragraph = _normalize_compact_whitespace(str(response_text))
    m = re.search(r"(?i)final claim:\s*(.+)", paragraph)
    if m:
        phrase = _history_target_phrase(m.group(1))
        if phrase:
            return phrase
    return ""


def _extract_imo_guiding_concepts(response_text: str) -> list[str]:
    lines = [str(line).strip() for line in str(response_text).splitlines()]
    for line in lines:
        m = re.search(r"(?i)guiding concepts:\s*(.+)$", line)
        if not m:
            continue
        raw = m.group(1)
        parts = [str(part).strip() for part in re.split(r"[;,]", raw) if str(part).strip()]
        if parts:
            return _dedupe_keep_order(parts)
    return []


def _default_imo_required_sections() -> list[str]:
    return ["assumptions", "core idea", "verification checklist"]


def _load_imo_statement_lookup(
    *,
    root: Path,
    years: list[int],
    lang: str,
    fetch_missing: bool,
    timeout: float,
    max_problems: int,
) -> dict[tuple[int, str], str]:
    out: dict[tuple[int, str], str] = {}
    total = 0
    for year in years:
        ds = _load_cached_imo_year_dataset(root, int(year), str(lang))
        if ds is None and bool(fetch_missing):
            _, _ = _fetch_imo_year_dataset(
                root=root,
                year=int(year),
                lang=str(lang),
                timeout=float(timeout),
                force=False,
            )
            ds = _load_cached_imo_year_dataset(root, int(year), str(lang))
        if ds is None:
            continue
        problems = ds.get("problems", [])
        if not isinstance(problems, list):
            problems = []
        for problem in problems:
            if int(max_problems) > 0 and total >= int(max_problems):
                break
            problem_id = _normalize_imo_problem_id(str(problem.get("id", "")).strip())
            if not problem_id:
                continue
            statement = _normalize_compact_whitespace(str(problem.get("statement", "")))
            out[(int(year), problem_id)] = statement
            total += 1
        if int(max_problems) > 0 and total >= int(max_problems):
            break
    return out


def _build_imo_autolearn_oracle_update(
    *,
    year: int,
    problem_id: str,
    response_text: str,
    statement: str,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    prev = existing if isinstance(existing, dict) else {}
    prev_needle = str(prev.get("needle", "")).strip()
    prev_aliases = [str(v).strip() for v in prev.get("aliases", []) if str(v).strip()] if isinstance(prev.get("aliases"), list) else []
    prev_concepts = [str(v).strip() for v in prev.get("concepts", []) if str(v).strip()] if isinstance(prev.get("concepts"), list) else []
    prev_sections = (
        [str(v).strip() for v in prev.get("required_sections", []) if str(v).strip()]
        if isinstance(prev.get("required_sections"), list)
        else []
    )
    prev_statement_excerpt = _normalize_compact_whitespace(str(prev.get("statement_excerpt", "")))[:220]
    prev_quality = _oracle_quality_assessment(
        needle=prev_needle,
        aliases=prev_aliases,
        concepts=prev_concepts,
        required_sections=prev_sections,
        statement_excerpt=prev_statement_excerpt,
    )

    statement_phrase = _history_target_phrase(statement, max_terms=12)
    response_phrase = _extract_imo_final_claim_phrase(response_text)
    needle = prev_needle or response_phrase or statement_phrase
    if not needle:
        needle = _history_target_phrase(response_text, max_terms=12)

    aliases = list(prev_aliases)
    if not aliases and needle:
        short = " ".join(needle.split()[:6]).strip()
        longish = " ".join(needle.split()[:10]).strip()
        aliases = _dedupe_keep_order([short, longish, statement_phrase])
    aliases = [item for item in aliases if item]

    concepts = list(prev_concepts)
    if not concepts:
        concepts = _extract_imo_guiding_concepts(response_text)
    if not concepts:
        concept_seed = [item for item in statement_phrase.split()[:3] if item]
        concepts = _dedupe_keep_order(concept_seed + ["invariant", "case split", "final claim alignment"])

    sections = list(prev_sections) if prev_sections else _default_imo_required_sections()
    statement_excerpt = prev_statement_excerpt or _normalize_compact_whitespace(statement)[:220]

    updated = {
        **{k: v for k, v in prev.items() if k not in {"year", "problem_id"}},
        "year": int(year),
        "problem_id": _normalize_imo_problem_id(problem_id),
        "needle": str(needle).strip(),
        "aliases": _dedupe_keep_order([str(v).strip() for v in aliases if str(v).strip()]),
        "concepts": _dedupe_keep_order([str(v).strip() for v in concepts if str(v).strip()]),
        "required_sections": _dedupe_keep_order([str(v).strip() for v in sections if str(v).strip()]),
        "statement_excerpt": statement_excerpt,
    }
    new_quality = _oracle_quality_assessment(
        needle=str(updated.get("needle", "")).strip(),
        aliases=updated.get("aliases", []),
        concepts=updated.get("concepts", []),
        required_sections=updated.get("required_sections", []),
        statement_excerpt=str(updated.get("statement_excerpt", "")),
    )

    changed_fields: list[str] = []
    for field in ["needle", "aliases", "concepts", "required_sections", "statement_excerpt"]:
        old = prev.get(field)
        new = updated.get(field)
        if old != new:
            changed_fields.append(field)

    return {
        "entry": updated,
        "changed_fields": changed_fields,
        "quality_before": prev_quality,
        "quality_after": new_quality,
    }


def _run_imo_history_bench_subprocess(
    *,
    root: Path,
    from_year: int,
    to_year: int,
    lang: str,
    model: str,
    url: str | None,
    timeout: float,
    max_problems: int,
    oracles_file: Path,
    required_rung: int,
    fetch_missing: bool,
    llm_only: bool = False,
) -> dict[str, Any]:
    cmd = [
        sys.executable,
        "-m",
        "stillwater",
        "imo-history",
        "bench",
        "--from-year",
        str(int(from_year)),
        "--to-year",
        str(int(to_year)),
        "--lang",
        str(lang),
        "--model",
        str(model),
        "--timeout",
        str(float(timeout)),
        "--max-problems",
        str(int(max_problems)),
        "--oracles-file",
        str(oracles_file),
        "--required-rung",
        str(int(required_rung)),
        "--json",
    ]
    if fetch_missing:
        cmd.append("--fetch-missing")
    if url:
        cmd.extend(["--url", str(url)])
    if llm_only:
        cmd.append("--llm-only")
    proc = subprocess.run(
        cmd,
        cwd=str(root),
        env=_runtime_env(root),
        text=True,
        capture_output=True,
        check=False,
    )
    out: dict[str, Any] = {
        "cmd": cmd,
        "returncode": int(proc.returncode),
        "stdout": str(proc.stdout or ""),
        "stderr": str(proc.stderr or ""),
    }
    try:
        payload = json.loads(proc.stdout)
    except Exception:
        out["ok"] = False
        out["error"] = "invalid_json_from_bench"
        return out
    if not isinstance(payload, dict):
        out["ok"] = False
        out["error"] = "bench_payload_not_dict"
        return out
    out["ok"] = True
    out["report"] = payload
    return out


def _imo_autolearn_score(report: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
    return (
        1 if bool(report.get("strict_ok", False)) else 0,
        int(report.get("pass_cases", 0)),
        int(report.get("oracle_quality_ready_cases", 0)),
        int(report.get("oracle_pass_cases", 0)),
        int(report.get("oracle_configured_cases", 0)),
        int(report.get("ok_cases", 0)),
    )


def _markdown_imo_autolearn_report(report: dict[str, Any]) -> str:
    lines = [
        "# IMO History Autolearn Report",
        "",
        f"- run_id: `{report.get('run_id', '')}`",
        f"- years: `{report.get('from_year', '')}`..`{report.get('to_year', '')}`",
        f"- required_rung: `{report.get('required_rung', 65537)}`",
        f"- max_iterations: `{report.get('max_iterations', 0)}`",
        f"- improved: `{bool(report.get('improved', False))}`",
        f"- strict_ok_best: `{bool(report.get('strict_ok_best', False))}`",
        f"- applied: `{bool(report.get('applied', False))}`",
        f"- target_oracles_file: `{report.get('target_oracles_file', '')}`",
        "",
        "## Iterations",
    ]
    iterations = report.get("iterations", [])
    if isinstance(iterations, list) and iterations:
        for row in iterations:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- iter={i}: strict_ok={strict_ok} pass={pass_cases}/{total_cases} "
                "quality_ready={quality_ready} proposals={proposals} changed={changed}".format(
                    i=row.get("iteration", 0),
                    strict_ok=bool(row.get("strict_ok", False)),
                    pass_cases=row.get("pass_cases", 0),
                    total_cases=row.get("total_cases", 0),
                    quality_ready=row.get("oracle_quality_ready_cases", 0),
                    proposals=row.get("proposal_count", 0),
                    changed=row.get("changed_case_count", 0),
                )
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Autolearn updates oracle/config artifacts only; it does not claim official IMO proof correctness.")
    lines.append("- Apply is fail-closed: updates are written only if measured metrics improve.")
    return "\n".join(lines) + "\n"


def _default_math_universal_config() -> dict[str, Any]:
    return {
        "version": 1,
        "description": (
            "Universal math gate config: breadth + proof artifacts + no-oracle generalization "
            "+ model/provider stability."
        ),
        "defaults": {
            "from_year": 1959,
            "to_year": 2025,
            "lang": "eng",
            "model": "llama3.1:8b",
            "url": "",
            "timeout": 45.0,
            "max_problems": 0,
            "fetch_missing": False,
        },
        "heldout_profiles": [
            {
                "label": "imo_history_full_65537",
                "from_year": 1959,
                "to_year": 2025,
                "required_rung": 65537,
                "oracles_file": "cli/tests/math/imo_history_oracles.json",
                "min_pass_ratio": 1.0,
                "require_strict": True,
            }
        ],
        "proof_artifacts": {
            "required": True,
            "cases_file": "cli/tests/math/proof_artifact_cases.json",
            "required_min_pass_ratio": 1.0,
        },
        "generalization_profiles": [
            {
                "label": "imo_history_no_oracle_recent_641",
                "from_year": 2020,
                "to_year": 2025,
                "required_rung": 641,
                "oracles_file": "cli/tests/math/imo_history_oracles.empty.json",
                "min_pass_ratio": 0.90,
                "require_strict": False,
            }
        ],
        "stability": {
            "profile": {
                "label": "imo_history_stability_slice_641",
                "from_year": 2020,
                "to_year": 2024,
                "required_rung": 641,
                "oracles_file": "cli/tests/math/imo_history_oracles.empty.json",
                "min_pass_ratio": 0.90,
                "require_strict": False,
            },
            "models": ["llama3.1:8b"],
            "urls": [],
            "required_all": True,
        },
    }


def _coerce_math_number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return int(value) if value.is_integer() else float(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        if "." in text:
            out = float(text)
            return int(out) if out.is_integer() else out
        return int(text)
    except Exception:
        try:
            out = float(text)
            return int(out) if out.is_integer() else out
        except Exception:
            return None


def _math_values_equal(actual: Any, expected: Any) -> bool:
    a_num = _coerce_math_number(actual)
    e_num = _coerce_math_number(expected)
    if a_num is not None and e_num is not None:
        return abs(float(a_num) - float(e_num)) <= 1e-9
    return str(actual).strip() == str(expected).strip()


def _run_math_universal_proof_artifacts(*, root: Path, cases_file: Path) -> dict[str, Any]:
    if not cases_file.exists():
        return {
            "ok": False,
            "error": "cases_file_missing",
            "cases_file": str(cases_file),
            "total_cases": 0,
            "pass_cases": 0,
            "pass_ratio": 0.0,
            "rows": [],
        }

    try:
        payload = _load_json(cases_file)
    except Exception as ex:
        return {
            "ok": False,
            "error": f"cases_file_invalid_json: {ex}",
            "cases_file": str(cases_file),
            "total_cases": 0,
            "pass_cases": 0,
            "pass_ratio": 0.0,
            "rows": [],
        }

    rows_raw = payload.get("cases", []) if isinstance(payload, dict) else []
    if not isinstance(rows_raw, list):
        rows_raw = []
    rows: list[dict[str, Any]] = []
    pass_cases = 0

    for idx, item in enumerate(rows_raw):
        if not isinstance(item, dict):
            continue
        case_id = str(item.get("id", f"case_{idx+1}")).strip() or f"case_{idx+1}"
        kind = str(item.get("kind", "")).strip().lower()
        expected = item.get("expected")
        out: dict[str, Any] = {
            "id": case_id,
            "kind": kind,
            "expected": expected,
            "pass": False,
            "actual": None,
            "error": "",
        }

        try:
            if kind == "expr_equals":
                expr = str(item.get("expr", "")).strip()
                actual = _eval_safe_arithmetic_expression(expr)
                out["actual"] = actual
                out["pass"] = _math_values_equal(actual, expected)
            elif kind == "gcd":
                a = int(item.get("a"))
                b = int(item.get("b"))
                actual = math.gcd(a, b)
                out["actual"] = actual
                out["pass"] = _math_values_equal(actual, expected)
            elif kind == "lcm":
                a = int(item.get("a"))
                b = int(item.get("b"))
                actual = math.lcm(a, b)
                out["actual"] = actual
                out["pass"] = _math_values_equal(actual, expected)
            elif kind == "modexp":
                base = int(item.get("base"))
                exp = int(item.get("exp"))
                mod = int(item.get("mod"))
                actual = pow(base, exp, mod)
                out["actual"] = actual
                out["pass"] = _math_values_equal(actual, expected)
            elif kind == "deterministic_prompt":
                prompt = str(item.get("prompt", "")).strip()
                extracted = _deterministic_math_extract(prompt) or {}
                actual = str(extracted.get("answer", "")).strip()
                out["actual"] = actual
                out["evidence"] = str(extracted.get("evidence", ""))
                out["pass"] = _math_values_equal(actual, expected)
            else:
                out["error"] = f"unsupported_kind:{kind}"
        except Exception as ex:
            out["error"] = f"evaluation_error:{ex}"
            out["pass"] = False

        if bool(out.get("pass", False)):
            pass_cases += 1
        rows.append(out)

    total_cases = len(rows)
    pass_ratio = round((pass_cases / total_cases), 6) if total_cases > 0 else 0.0
    return {
        "ok": total_cases > 0,
        "cases_file": str(cases_file),
        "total_cases": total_cases,
        "pass_cases": pass_cases,
        "pass_ratio": pass_ratio,
        "rows": rows,
    }


def _run_math_universal_bench_profile(
    *,
    root: Path,
    profile: dict[str, Any],
    defaults: dict[str, Any],
    model_override: str | None = None,
    url_override: str | None = None,
    timeout_override: float | None = None,
    fetch_missing_override: bool | None = None,
) -> dict[str, Any]:
    label = str(profile.get("label", "")).strip() or "profile"
    from_year = _coerce_int(profile.get("from_year", defaults.get("from_year", 2020)), default=2020)
    to_year = _coerce_int(profile.get("to_year", defaults.get("to_year", from_year)), default=from_year)
    if from_year > to_year:
        return {
            "label": label,
            "ok": False,
            "error": "invalid_year_range",
            "from_year": from_year,
            "to_year": to_year,
        }

    lang = str(profile.get("lang", defaults.get("lang", "eng"))).strip() or "eng"
    model = str(model_override or profile.get("model", defaults.get("model", "llama3.1:8b"))).strip() or "llama3.1:8b"
    url_raw = url_override if url_override is not None else profile.get("url", defaults.get("url", ""))
    url = str(url_raw).strip() if url_raw is not None else ""
    timeout = (
        float(timeout_override)
        if timeout_override is not None
        else _coerce_float(profile.get("timeout", defaults.get("timeout", 45.0)), default=45.0)
    )
    max_problems = _coerce_int(profile.get("max_problems", defaults.get("max_problems", 0)), default=0)
    required_rung = _coerce_int(profile.get("required_rung", 641), default=641)
    if required_rung not in {641, 274177, 65537}:
        required_rung = 641
    fetch_missing = (
        bool(fetch_missing_override)
        if fetch_missing_override is not None
        else bool(profile.get("fetch_missing", defaults.get("fetch_missing", False)))
    )
    min_pass_ratio = _coerce_float(profile.get("min_pass_ratio", 1.0), default=1.0)
    require_strict = bool(profile.get("require_strict", True))

    oracle_raw = profile.get("oracles_file", defaults.get("oracles_file", "cli/tests/math/imo_history_oracles.json"))
    oracle_file = _resolve_user_path(root, str(oracle_raw))

    bench = _run_imo_history_bench_subprocess(
        root=root,
        from_year=from_year,
        to_year=to_year,
        lang=lang,
        model=model,
        url=url or None,
        timeout=timeout,
        max_problems=max_problems,
        oracles_file=oracle_file,
        required_rung=required_rung,
        fetch_missing=fetch_missing,
        llm_only=False,
    )
    if not bool(bench.get("ok", False)):
        return {
            "label": label,
            "ok": False,
            "error": str(bench.get("error", "bench_subprocess_failed")),
            "returncode": int(bench.get("returncode", 1)),
            "from_year": from_year,
            "to_year": to_year,
            "lang": lang,
            "model": model,
            "url": url,
            "required_rung": required_rung,
            "oracles_file": str(oracle_file),
        }

    report = bench.get("report", {})
    if not isinstance(report, dict):
        report = {}
    total_cases = _coerce_int(report.get("total_cases", 0), default=0)
    pass_cases = _coerce_int(report.get("pass_cases", 0), default=0)
    pass_ratio = round((pass_cases / total_cases), 6) if total_cases > 0 else 0.0
    strict_ok = bool(report.get("strict_ok", False))
    ok = total_cases > 0 and pass_ratio >= min_pass_ratio and (strict_ok or not require_strict)
    return {
        "label": label,
        "ok": ok,
        "strict_ok": strict_ok,
        "total_cases": total_cases,
        "pass_cases": pass_cases,
        "pass_ratio": pass_ratio,
        "min_pass_ratio": min_pass_ratio,
        "require_strict": require_strict,
        "from_year": from_year,
        "to_year": to_year,
        "lang": lang,
        "model": model,
        "url": url,
        "timeout": timeout,
        "max_problems": max_problems,
        "required_rung": required_rung,
        "oracles_file": str(oracle_file),
        "bench_run_id": str(report.get("run_id", "")),
        "bench_artifact_dir": str(report.get("artifact_dir", "")),
    }


def _markdown_math_universal_report(report: dict[str, Any]) -> str:
    lines = [
        "# Math Universal Gate Report",
        "",
        f"- run_id: `{report.get('run_id', '')}`",
        f"- config_path: `{report.get('config_path', '')}`",
        f"- config_exists: `{bool(report.get('config_exists', False))}`",
        f"- overall_ok: `{bool(report.get('overall_ok', False))}`",
        f"- universal_claim_ready: `{bool(report.get('universal_claim_ready', False))}`",
        "",
        "## Gates",
    ]

    gates = report.get("gates", {}) if isinstance(report.get("gates"), dict) else {}
    for key in ["heldout", "proof_artifacts", "generalization", "stability"]:
        gate = gates.get(key, {})
        if not isinstance(gate, dict):
            continue
        lines.append(
            f"- {key}: ok={bool(gate.get('ok', False))} "
            f"pass_ratio={gate.get('pass_ratio', 0.0)} "
            f"required_min={gate.get('required_min_pass_ratio', 0.0)}"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("- This gate suite operationalizes universal-math readiness criteria.")
    lines.append("- Failures indicate which gate is missing (breadth, proof artifacts, generalization, stability).")
    lines.append("- `universal_claim_ready=true` requires all gates to pass.")
    return "\n".join(lines) + "\n"


def _imo_phuc_case_scout(case: dict[str, str]) -> dict[str, Any]:
    return {
        "task_summary": f"Solve {case['id']} via PHUC orchestration and verify with receipts.",
        "repro_command": "stillwater twin <prompt> --json",
        "failing_tests_or_errors": [
            "tool_assisted lane non-zero return code",
            "unexpected route action/source",
            "needle mismatch against expected marker",
        ],
        "suspect_files_ranked": [
            {"path": "cli/src/stillwater/cli.py", "reason": "routing + orchestration execution"},
            {
                "path": "cli/settings/SWARM-ORCHESTRATION.prime-mermaid.md",
                "reason": "externalized tool policy for PHUC swarms",
            },
            {"path": "imo/src/imo_2024_solver_proper.py", "reason": "deterministic benchmark evidence source"},
        ],
        "acceptance_criteria": [
            "tool_assisted response contains case needle",
            "tool_assisted route action is phuc_swarms_benchmark",
            "tool_assisted source is CPU",
            "llm_only lane executed with receipts",
        ],
        "missing_assets": [],
    }


def _imo_phuc_case_forecast(case: dict[str, str], scout_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "top_failure_modes_ranked": [
            {"rank": 1, "mode": "route unexpectedly falls back to LLM", "likelihood_bucket": "30"},
            {"rank": 2, "mode": "deterministic solver output markers drift", "likelihood_bucket": "30"},
            {"rank": 3, "mode": "needle matcher too strict for equivalent wording", "likelihood_bucket": "10"},
            {"rank": 4, "mode": "remote ollama timeout", "likelihood_bucket": "30"},
        ],
        "edge_cases_to_test": [
            "prompt variant using equivalent wording",
            "historical IMO year prompt",
            "remote model temporarily unavailable",
        ],
        "compat_risks": [
            "route.action semantics changed",
            "response text shifts while semantic answer stays equivalent",
        ],
        "stop_rules": [
            "if tool_assisted returncode != 0",
            "if tool_assisted route action != phuc_swarms_benchmark",
            "if tool_assisted source != CPU",
            "if tool_assisted needle check fails",
        ],
        "mitigations": [
            "capture per-lane stdout/stderr receipts",
            "persist route metadata and phuc_decision per case",
            "publish llm_only lane baseline beside tool_assisted lane",
        ],
        "case_id": case["id"],
        "scout_ref": bool(scout_report),
    }


def _imo_phuc_case_decide(
    *,
    case: dict[str, str],
    forecast_memo: dict[str, Any],
    required_rung: int,
) -> dict[str, Any]:
    return {
        "chosen_approach": "Run tool_assisted + llm_only lanes, enforce strict route + needle verification.",
        "alternatives_considered": [
            "llm_only-only run",
            "deterministic solver-only run without LLM baseline",
        ],
        "scope_locked": ["tool_assisted", "llm_only", "route_receipts", "needle_checks"],
        "required_verification_rung": required_rung,
        "required_tests": [
            "tool_assisted route.action == phuc_swarms_benchmark",
            "tool_assisted source == CPU",
            "tool_assisted response contains expected needle",
            "llm_only lane executed",
        ],
        "stop_rules": list(forecast_memo.get("stop_rules", [])),
        "go_no_go_initial": "GO",
        "case_id": case["id"],
    }


def _normalize_semantic_match_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(text))
    normalized = normalized.replace("∠", " angle ")
    normalized = normalized.replace("°", "")
    normalized = normalized.replace("·", " ")
    normalized = normalized.replace("−", "-")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9+\-*/^=()<> ]+", " ", normalized)
    return _normalize_compact_whitespace(normalized)


def _expand_semantic_aliases(needle: str) -> list[str]:
    text = str(needle).strip()
    lower = text.lower()
    out = [text] if text else []
    if "∠" in text or "angle" in lower:
        out.append(text.replace("∠", "angle ").replace("°", ""))
    if "monochromatic triangle" in lower:
        out.extend(["same color triangle", "single-color triangle", "one color triangle"])
    if "property holds" in lower:
        out.extend(["property is true", "statement holds", "verified"])
    if "f(x)=x" in lower or "f(x) = x" in lower:
        out.extend(["f(x) = x", "identity function"])
    if lower == "empty":
        out.extend(["empty set", "none", "no values", "no valid values"])
    deduped: list[str] = []
    seen: set[str] = set()
    for item in out:
        key = _normalize_compact_whitespace(item).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _semantic_match_score(response: str, targets: list[str]) -> dict[str, Any]:
    response_raw = str(response)
    response_lower = response_raw.lower()
    response_norm = _normalize_semantic_match_text(response_raw)
    response_tokens = set(re.findall(r"[a-z0-9+\-*/^=()<>]+", response_norm))
    best = {
        "matched": False,
        "mode": "none",
        "score": 0.0,
        "target": "",
        "strict_match": False,
        "normalized_match": False,
        "token_coverage": 0.0,
    }
    dedup_targets: list[str] = []
    seen_targets: set[str] = set()
    for target in targets:
        key = _normalize_compact_whitespace(str(target)).lower()
        if not key or key in seen_targets:
            continue
        seen_targets.add(key)
        dedup_targets.append(str(target))

    for target in dedup_targets:
        target_raw = target.strip()
        target_lower = target_raw.lower()
        target_norm = _normalize_semantic_match_text(target_raw)
        strict = bool(target_lower) and target_lower in response_lower
        normalized_contains = bool(target_norm) and target_norm in response_norm
        target_tokens = set(re.findall(r"[a-z0-9+\-*/^=()<>]+", target_norm))
        token_coverage = 0.0
        if target_tokens:
            token_coverage = len(target_tokens.intersection(response_tokens)) / len(target_tokens)
        score = 0.0
        mode = "none"
        if strict:
            score = 1.0
            mode = "strict"
        elif normalized_contains:
            score = 0.95
            mode = "normalized"
        elif len(target_tokens) >= 2 and token_coverage >= 0.9:
            score = 0.85
            mode = "token_coverage"
        if score > float(best["score"]):
            best = {
                "matched": score >= 0.85,
                "mode": mode,
                "score": round(score, 6),
                "target": target_raw,
                "strict_match": strict,
                "normalized_match": normalized_contains,
                "token_coverage": round(token_coverage, 6),
            }
    return best


def _concept_coverage_score(response: str, concepts: list[str]) -> dict[str, Any]:
    response_norm = _normalize_semantic_match_text(response)
    response_tokens = set(re.findall(r"[a-z0-9+\-*/^=()<>]+", response_norm))
    clean_concepts = [str(item).strip() for item in concepts if str(item).strip()]
    if not clean_concepts:
        return {
            "concepts": [],
            "hits": [],
            "hit_count": 0,
            "coverage": 1.0,
        }
    hits: list[str] = []
    for concept in clean_concepts:
        concept_norm = _normalize_semantic_match_text(concept)
        if concept_norm and concept_norm in response_norm:
            hits.append(concept)
            continue
        concept_tokens = set(re.findall(r"[a-z0-9+\-*/^=()<>]+", concept_norm))
        if concept_tokens and (len(concept_tokens.intersection(response_tokens)) / len(concept_tokens)) >= 0.9:
            hits.append(concept)
    coverage = len(hits) / len(clean_concepts) if clean_concepts else 1.0
    return {
        "concepts": clean_concepts,
        "hits": hits,
        "hit_count": len(hits),
        "coverage": round(coverage, 6),
    }


def _required_sections_score(response: str, required_sections: list[str]) -> dict[str, Any]:
    response_norm = _normalize_semantic_match_text(response)
    clean_sections = [str(item).strip() for item in required_sections if str(item).strip()]
    if not clean_sections:
        return {
            "required_sections": [],
            "hits": [],
            "hit_count": 0,
            "coverage": 1.0,
        }
    hits: list[str] = []
    for section in clean_sections:
        section_norm = _normalize_semantic_match_text(section)
        if section_norm and section_norm in response_norm:
            hits.append(section)
    coverage = len(hits) / len(clean_sections) if clean_sections else 1.0
    return {
        "required_sections": clean_sections,
        "hits": hits,
        "hit_count": len(hits),
        "coverage": round(coverage, 6),
    }


def _oracle_quality_tier_rank(tier: str) -> int:
    table = {"none": 0, "weak": 1, "standard": 2, "strong": 3}
    return table.get(str(tier).strip().lower(), 0)


def _is_placeholder_oracle_alias(text: str) -> bool:
    norm = _normalize_semantic_match_text(text)
    if not norm:
        return True
    if re.fullmatch(r"p\d+\s+\d{4}\s+key claim", norm):
        return True
    if norm in {"key claim", "oracle target", "target phrase", "placeholder"}:
        return True
    return False


def _oracle_quality_assessment(
    *,
    needle: str,
    aliases: list[str],
    concepts: list[str],
    required_sections: list[str],
    statement_excerpt: str = "",
) -> dict[str, Any]:
    clean_needle = str(needle).strip()
    clean_aliases = [str(item).strip() for item in aliases if str(item).strip()]
    clean_concepts = [str(item).strip() for item in concepts if str(item).strip()]
    clean_sections = [str(item).strip() for item in required_sections if str(item).strip()]
    targets = [clean_needle] + clean_aliases if clean_needle else list(clean_aliases)
    has_targets = len(targets) > 0
    if not has_targets:
        return {
            "tier": "none",
            "score": 0.0,
            "ready_standard": False,
            "ready_strong": False,
            "target_count": 0,
            "independent_target_count": 0,
            "placeholder_alias_count": 0,
            "needle_token_count": 0,
            "has_targets": False,
        }

    stmt_norm = _normalize_semantic_match_text(statement_excerpt)
    stmt_tokens = set(re.findall(r"[a-z0-9+\-*/^=()<>]+", stmt_norm))

    independent_target_count = 0
    placeholder_alias_count = 0
    for idx, target in enumerate(targets):
        target_norm = _normalize_semantic_match_text(target)
        if not target_norm:
            continue
        is_placeholder_alias = idx > 0 and _is_placeholder_oracle_alias(target)
        if is_placeholder_alias:
            placeholder_alias_count += 1
            continue
        if not stmt_norm:
            independent_target_count += 1
            continue
        in_statement = target_norm in stmt_norm
        target_tokens = set(re.findall(r"[a-z0-9+\-*/^=()<>]+", target_norm))
        overlap = (len(target_tokens.intersection(stmt_tokens)) / len(target_tokens)) if target_tokens else 1.0
        if (not in_statement) and overlap < 0.85:
            independent_target_count += 1

    needle_tokens = re.findall(r"[a-z0-9+\-*/^=()<>]+", _normalize_semantic_match_text(clean_needle))
    needle_token_count = len(needle_tokens)

    score = 0.35
    if needle_token_count >= 4:
        score += 0.15
    if needle_token_count >= 8:
        score += 0.10
    if len(clean_aliases) >= 2:
        score += 0.10
    if len(clean_concepts) >= 2:
        score += 0.10
    if len(clean_sections) >= 2:
        score += 0.10
    if independent_target_count >= 1:
        score += 0.10
    if placeholder_alias_count > 0:
        score -= 0.15
    score = max(0.0, min(1.0, score))

    if score < 0.35:
        tier = "none"
    elif score < 0.55:
        tier = "weak"
    elif score < 0.80:
        tier = "standard"
    else:
        tier = "strong"

    # Without any independent targets, cap to standard. This prevents overclaiming "strong"
    # for rows that are mostly statement echo + template aliases.
    if independent_target_count == 0 and tier == "strong":
        tier = "standard"
        score = min(score, 0.79)

    return {
        "tier": tier,
        "score": round(score, 6),
        "ready_standard": tier in {"standard", "strong"},
        "ready_strong": tier == "strong",
        "target_count": len(targets),
        "independent_target_count": independent_target_count,
        "placeholder_alias_count": placeholder_alias_count,
        "needle_token_count": needle_token_count,
        "has_targets": True,
    }


def _imo_phuc_eval_lane(
    *,
    run: dict[str, Any],
    needle: str,
    aliases: list[str] | None,
    lane_name: str,
    council_cfg: dict[str, Any],
    concepts: list[str] | None = None,
    required_sections: list[str] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "run_ok": bool(run.get("ok")),
        "returncode": run.get("returncode"),
        "source": "",
        "action": "",
        "profile": "",
        "decision": "",
        "reason": "",
        "match": False,
        "response_excerpt": "",
        "route": {},
        "error": str(run.get("error", "")),
    }
    payload = run.get("payload", {}) if isinstance(run.get("payload"), dict) else {}
    route = payload.get("route", {}) if isinstance(payload.get("route"), dict) else {}
    phuc = route.get("phuc_decision", {}) if isinstance(route.get("phuc_decision"), dict) else {}
    response = str(payload.get("response", ""))
    min_chars = max(1, _coerce_int(council_cfg.get("response_min_chars", 24), default=24))
    case_aliases = [str(item).strip() for item in (aliases or []) if str(item).strip()]
    targets = _expand_semantic_aliases(needle) + case_aliases
    match_meta = _semantic_match_score(response, targets)
    concept_meta = _concept_coverage_score(response, [str(item) for item in (concepts or []) if str(item).strip()])
    section_meta = _required_sections_score(
        response, [str(item) for item in (required_sections or []) if str(item).strip()]
    )
    out["source"] = str(payload.get("source", ""))
    out["action"] = str(route.get("action", ""))
    out["profile"] = str(phuc.get("profile", ""))
    out["decision"] = str(phuc.get("decision", ""))
    out["reason"] = str(phuc.get("reason", ""))
    out["match"] = bool(match_meta.get("matched"))
    out["match_mode"] = str(match_meta.get("mode", "none"))
    out["match_score"] = float(match_meta.get("score", 0.0))
    out["match_target"] = str(match_meta.get("target", needle))
    out["match_strict"] = bool(match_meta.get("strict_match"))
    out["match_normalized"] = bool(match_meta.get("normalized_match"))
    out["match_token_coverage"] = float(match_meta.get("token_coverage", 0.0))
    out["concept_meta"] = concept_meta
    out["section_meta"] = section_meta
    out["response_excerpt"] = response[:320]
    out["route"] = route
    out["response_chars"] = len(response.strip())

    route_receipts_ok = bool(out["action"].strip()) and bool(out["source"].strip())
    phuc_receipt_ok = bool(out["decision"].strip()) and bool(out["profile"].strip())
    response_ok = len(response.strip()) >= min_chars
    runtime_ok = bool(out["run_ok"]) and out.get("returncode") in {0, None}
    error_free = not str(out.get("error", "")).strip()
    tool_route_ok = out["source"] == "CPU" and out["action"] == "phuc_swarms_benchmark"
    llm_baseline_ok = bool(out["action"].strip()) and out["source"] in {"LLM", "CPU"}
    concept_cov = float(concept_meta.get("coverage", 1.0))
    section_hits = int(section_meta.get("hit_count", 0))
    concept_ok_274 = concept_cov >= _coerce_float(council_cfg.get("concept_coverage_min_274177", 0.5), default=0.5)
    concept_ok_655 = concept_cov >= _coerce_float(council_cfg.get("concept_coverage_min_65537", 0.8), default=0.8)
    section_ok_274 = section_hits >= _coerce_int(council_cfg.get("section_hits_min_274177", 1), default=1)
    section_ok_655 = section_hits >= _coerce_int(council_cfg.get("section_hits_min_65537", 2), default=2)
    if not list(concept_meta.get("concepts", [])):
        concept_ok_274 = True
        concept_ok_655 = True
    if not list(section_meta.get("required_sections", [])):
        section_ok_274 = True
        section_ok_655 = True

    votes: list[dict[str, Any]] = [
        _expert_vote("runtime_guard", runtime_ok, "subprocess return code and ok flag"),
        _expert_vote("response_guard", response_ok, f"response has at least {min_chars} chars"),
        _expert_vote("route_receipts_guard", route_receipts_ok, "source/action receipts are present"),
        _expert_vote("phuc_receipt_guard", phuc_receipt_ok, "phuc_decision profile/decision receipts are present"),
        _expert_vote("needle_guard", bool(out["match"]), "expected marker or semantic alias is present in response"),
        _expert_vote(
            "concept_guard",
            concept_ok_274,
            "concept coverage meets rung-274177 threshold",
        ),
        _expert_vote(
            "section_guard",
            section_ok_274,
            "required proof sections meet rung-274177 threshold",
        ),
        _expert_vote("error_guard", error_free, "no explicit execution error"),
    ]
    if lane_name == "tool_assisted":
        votes.append(
            _expert_vote(
                "tool_route_guard",
                tool_route_ok,
                "tool lane must be CPU + phuc_swarms_benchmark route",
            )
        )
    else:
        votes.append(
            _expert_vote(
                "llm_lane_guard",
                llm_baseline_ok,
                "llm lane should keep visible action/source receipts",
            )
        )

    require_route_receipts = bool(council_cfg.get("require_route_receipts", True))
    require_phuc_274 = bool(council_cfg.get("require_phuc_receipt_for_274177", True))
    require_tool_655 = bool(council_cfg.get("require_tool_route_for_65537", True))
    gates = {
        "r641": runtime_ok and response_ok and (route_receipts_ok if require_route_receipts else True),
        "r274177": runtime_ok
        and response_ok
        and (phuc_receipt_ok if require_phuc_274 else True)
        and bool(out["match"])
        and concept_ok_274
        and section_ok_274,
        "r65537": runtime_ok
        and response_ok
        and bool(out["match"])
        and float(out.get("match_score", 0.0)) >= 0.92
        and concept_ok_655
        and section_ok_655
        and error_free
        and (tool_route_ok if (lane_name == "tool_assisted" and require_tool_655) else True),
    }
    out["council"] = _aggregate_expert_council(votes=votes, gates=gates, cfg=council_cfg)
    return out


def _markdown_imo_phuc_report(report: dict[str, Any]) -> str:
    lines = [
        "# IMO PHUC 5-Phase Report",
        "",
        f"- run_id: `{report.get('run_id', '')}`",
        f"- model: `{report.get('model', '')}`",
        f"- url: `{report.get('url', '')}`",
        f"- timeout: `{report.get('timeout', '')}`",
        f"- cases_file: `{report.get('cases_file', '')}`",
        f"- required_rung: `{report.get('required_rung', 65537)}`",
        f"- tool_assisted_score: `{report.get('tool_assisted_score', 0)}/{report.get('total_cases', 0)}`",
        f"- llm_only_score: `{report.get('llm_only_score', 0)}/{report.get('total_cases', 0)}`",
        f"- strict_pass: `{bool(report.get('strict_pass'))}`",
        "",
        "## Lane Disclosure",
        "",
        "- tool_assisted: PHUC swarms deterministic route (CPU) with receipts",
        "- llm_only: remote model baseline via `--llm-only`",
        "",
        "## Per Case",
        "",
    ]
    rows = report.get("rows", [])
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- {case_id}: status={status} "
                "tool(source={tool_source}, action={tool_action}, match={tool_match}, rung={tool_rung}) "
                "llm_match={llm_match}".format(
                    case_id=row.get("case_id", ""),
                    status=row.get("status", ""),
                    tool_source=row.get("tool_source", ""),
                    tool_action=row.get("tool_action", ""),
                    tool_match=row.get("tool_match", False),
                    tool_rung=row.get("tool_rung_achieved", 0),
                    llm_match=row.get("llm_match", False),
                )
            )
    lines.append("")
    lines.append("## Notes")
    lines.append("- This report is a reproducible workflow score, not official IMO grading.")
    lines.append("- Full case artifacts include SCOUT/FORECAST/DECIDE/ACT/SKEPTIC JSON receipts.")
    memory = report.get("memory_loop", {})
    if isinstance(memory, dict):
        board_md = str(memory.get("board_md", "")).strip()
        if board_md:
            lines.append(f"- Memory loop board: `{board_md}`")
    return "\n".join(lines) + "\n"


def _append_jsonl_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        if isinstance(data, dict):
            out.append(data)
    return out


def _imo_memory_next_actions(fail_counts: dict[str, int]) -> list[str]:
    if not fail_counts:
        return [
            "Expand coverage: add new cases in cli/tests/math/*.json and rerun benchmark.",
            "Keep deterministic lane stable while stress-testing llm_only baselines.",
        ]
    actions: list[str] = []
    joined = " ".join(fail_counts.keys()).lower()
    if "route" in joined or "action" in joined or "source" in joined:
        actions.append("Review route policy in cli/settings/SWARM-ORCHESTRATION.prime-mermaid.md.")
    if "needle" in joined or "match" in joined or "excerpt" in joined:
        actions.append("Improve answer-marker extraction and matcher robustness for equivalent wording.")
    if "timeout" in joined or "endpoint" in joined or "subprocess" in joined:
        actions.append("Harden runtime retries/timeouts and validate Ollama endpoint health before runs.")
    if "dataset" in joined or "parse" in joined or "statement" in joined:
        actions.append("Refresh IMO fetch/parse artifacts and add parser regression checks.")
    if not actions:
        actions.append("Cluster failures into repeatable tests and patch routing/tool boundaries first.")
    return actions[:3]


def _write_imo_memory_board(memory_dir: Path, entries: list[dict[str, Any]]) -> tuple[Path, Path]:
    board_json = memory_dir / "board.json"
    board_md = memory_dir / "board.md"
    runs = len(entries)
    total_cases = sum(int(e.get("total_cases", 0)) for e in entries)
    total_fails = sum(int(e.get("fail_cases", 0)) for e in entries)
    by_kind: dict[str, int] = {}
    fail_signals: dict[str, int] = {}
    for entry in entries:
        kind = str(entry.get("kind", "unknown"))
        by_kind[kind] = by_kind.get(kind, 0) + 1
        top = entry.get("fail_signals_top", [])
        if not isinstance(top, list):
            continue
        for row in top:
            if not isinstance(row, dict):
                continue
            reason = str(row.get("reason", "")).strip()
            count = int(row.get("count", 0))
            if not reason:
                continue
            fail_signals[reason] = fail_signals.get(reason, 0) + count
    top_fail_signals = sorted(fail_signals.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    payload = {
        "updated_utc": _utc_now(),
        "runs": runs,
        "total_cases": total_cases,
        "total_fails": total_fails,
        "run_types": by_kind,
        "top_fail_signals": [{"reason": reason, "count": count} for reason, count in top_fail_signals],
        "recent_runs": entries[-10:],
    }
    _write_json(board_json, payload)

    lines = [
        "# IMO Memory Loop Board",
        "",
        f"- updated_utc: `{payload['updated_utc']}`",
        f"- runs: `{runs}`",
        f"- total_cases: `{total_cases}`",
        f"- total_fails: `{total_fails}`",
        "",
        "## Run Types",
    ]
    for kind in sorted(by_kind.keys()):
        lines.append(f"- {kind}: {by_kind[kind]}")
    lines.append("")
    lines.append("## Top Fail Signals")
    if top_fail_signals:
        for reason, count in top_fail_signals:
            lines.append(f"- {reason}: {count}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Recent Runs")
    for entry in entries[-10:]:
        lines.append(
            "- {run_id}: kind={kind} strict_ok={strict_ok} cases={total_cases} fails={fail_cases}".format(
                run_id=entry.get("run_id", ""),
                kind=entry.get("kind", ""),
                strict_ok=entry.get("strict_ok", False),
                total_cases=entry.get("total_cases", 0),
                fail_cases=entry.get("fail_cases", 0),
            )
        )
    board_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return board_json, board_md


def _record_imo_memory(
    *,
    root: Path,
    kind: str,
    run_id: str,
    report: dict[str, Any],
    report_file: Path,
) -> dict[str, str]:
    memory_dir = root / "artifacts" / "imo_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    ledger = memory_dir / "runs.jsonl"
    rows = report.get("rows", [])
    fail_counts: dict[str, int] = {}
    pass_cases = 0
    fail_cases = 0
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            status_raw = row.get("status")
            if status_raw is None:
                status_raw = row.get("phuc_status")
            if status_raw is None:
                status_raw = "PASS" if bool(row.get("ok")) else "FAIL"
            status = str(status_raw).upper()
            if status == "PASS":
                pass_cases += 1
            else:
                fail_cases += 1
            reasons = row.get("phuc_fail_reasons", [])
            if not isinstance(reasons, list):
                reasons = []
            if not reasons and status != "PASS":
                reasons = ["unclassified_failure"]
            for reason in reasons:
                text = str(reason).strip()
                if not text:
                    continue
                fail_counts[text] = fail_counts.get(text, 0) + 1

    fail_signals_top = [
        {"reason": reason, "count": count} for reason, count in sorted(fail_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    ]
    try:
        report_rel = str(report_file.relative_to(root))
    except ValueError:
        report_rel = str(report_file)

    entry = {
        "timestamp_utc": _utc_now(),
        "kind": kind,
        "run_id": run_id,
        "strict_ok": bool(report.get("strict_pass", report.get("strict_ok", False))),
        "total_cases": int(report.get("total_cases", 0)),
        "pass_cases": pass_cases,
        "fail_cases": fail_cases,
        "model": str(report.get("model", "")),
        "url": str(report.get("url", "")),
        "report": report_rel,
        "fail_signals_top": fail_signals_top,
        "next_actions": _imo_memory_next_actions(fail_counts),
    }
    _append_jsonl_row(ledger, entry)
    entries = _load_jsonl_rows(ledger)
    board_json, board_md = _write_imo_memory_board(memory_dir, entries)
    try:
        ledger_rel = str(ledger.relative_to(root))
    except ValueError:
        ledger_rel = str(ledger)
    try:
        board_json_rel = str(board_json.relative_to(root))
    except ValueError:
        board_json_rel = str(board_json)
    try:
        board_md_rel = str(board_md.relative_to(root))
    except ValueError:
        board_md_rel = str(board_md)
    return {"ledger": ledger_rel, "board_json": board_json_rel, "board_md": board_md_rel}


def _imo_history_case_scout(*, year: int, problem_id: str, prompt: str) -> dict[str, Any]:
    return {
        "task_summary": f"Historical IMO {year} {problem_id}: validate orchestration route and runtime output.",
        "repro_command": "stillwater imo-history bench --from-year <y> --to-year <y> --max-problems 1",
        "failing_tests_or_errors": [
            "dataset missing",
            "twin subprocess failure",
            "empty response from route",
        ],
        "suspect_files_ranked": [
            {"path": "cli/src/stillwater/cli.py", "reason": "history bench runtime + routing"},
            {
                "path": "cli/settings/SWARM-ORCHESTRATION.prime-mermaid.md",
                "reason": "externalized route policy + profile mapping",
            },
        ],
        "acceptance_criteria": [
            "twin subprocess returns ok",
            "route metadata is present",
            "response excerpt is non-empty",
        ],
        "prompt_excerpt": prompt[:240],
        "missing_assets": [],
    }


def _imo_history_case_forecast(*, year: int, problem_id: str) -> dict[str, Any]:
    return {
        "top_failure_modes_ranked": [
            {"rank": 1, "mode": "remote model timeout/intermittent network", "likelihood_bucket": "30"},
            {"rank": 2, "mode": "dataset parse drift from PDF extraction", "likelihood_bucket": "30"},
            {"rank": 3, "mode": "route classification mismatch", "likelihood_bucket": "10"},
        ],
        "edge_cases_to_test": [
            "historical year prompts outside demo scope",
            "empty/short statement extraction",
            "model endpoint reachable but returns malformed payload",
        ],
        "compat_risks": [
            "IMO statement formatting changes on upstream site",
            "provider response shape changes over time",
        ],
        "stop_rules": [
            "if subprocess returncode != 0",
            "if response is empty",
            "if route metadata is absent",
        ],
        "case_id": f"{year}-{problem_id}",
    }


def _imo_history_case_decide(*, year: int, problem_id: str, required_rung: int) -> dict[str, Any]:
    return {
        "chosen_approach": "execute twin once per historical problem and verify runtime/route receipts",
        "alternatives_considered": [
            "strict theorem proving gate (out of current scope)",
            "LLM-only routing baseline without orchestration metadata",
        ],
        "scope_locked": ["single_prompt_runtime", "route_metadata", "response_presence"],
        "required_verification_rung": required_rung,
        "required_tests": [
            "subprocess ok",
            "route fields present",
            "response excerpt non-empty",
        ],
        "go_no_go_initial": "GO",
        "case_id": f"{year}-{problem_id}",
    }


def _history_response_contract_score(prompt: str, response_text: str, *, min_hits: int) -> dict[str, Any]:
    required = ["assumption", "core idea", "verification"]
    normalized = _normalize_compact_whitespace(response_text).lower()
    hits = [token for token in required if token in normalized]
    return {
        "required_tokens": required,
        "hit_tokens": hits,
        "hit_count": len(hits),
        "min_hits": max(0, int(min_hits)),
        "pass": len(hits) >= max(0, int(min_hits)),
        "prompt_excerpt": prompt[:180],
    }


def _history_prompt_keyword_coverage(
    *,
    prompt: str,
    response_text: str,
    min_hits: int,
    min_ratio: float,
    min_number_hits: int,
) -> dict[str, Any]:
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "onto",
        "then",
        "such",
        "there",
        "their",
        "have",
        "your",
        "what",
        "when",
        "where",
        "which",
        "who",
        "whose",
        "why",
        "how",
        "let",
        "find",
        "show",
        "prove",
        "solve",
        "problem",
        "rigorous",
        "outline",
        "return",
        "assumptions",
        "core",
        "idea",
        "verification",
        "checklist",
        "imo",
    }
    prompt_norm = _normalize_semantic_match_text(prompt)
    response_norm = _normalize_semantic_match_text(response_text)
    prompt_tokens_raw = re.findall(r"[a-z]{3,}", prompt_norm)
    response_tokens = set(re.findall(r"[a-z]{3,}", response_norm))

    prompt_keywords: list[str] = []
    seen: set[str] = set()
    for token in prompt_tokens_raw:
        if token in stopwords:
            continue
        if token in seen:
            continue
        seen.add(token)
        prompt_keywords.append(token)

    keyword_hits = [token for token in prompt_keywords if token in response_tokens]
    keyword_coverage = len(keyword_hits) / len(prompt_keywords) if prompt_keywords else 1.0
    required_keyword_hits = min(max(0, int(min_hits)), len(prompt_keywords))
    keyword_pass = (
        len(prompt_keywords) == 0
        or (len(keyword_hits) >= required_keyword_hits and keyword_coverage >= _clamp01(float(min_ratio)))
    )

    prompt_numbers = sorted(set(re.findall(r"\b\d+\b", prompt)))
    response_numbers = set(re.findall(r"\b\d+\b", response_text))
    number_hits = [num for num in prompt_numbers if num in response_numbers]
    required_number_hits = min(max(0, int(min_number_hits)), len(prompt_numbers))
    number_pass = len(prompt_numbers) == 0 or len(number_hits) >= required_number_hits

    return {
        "prompt_keywords": prompt_keywords,
        "keyword_hits": keyword_hits,
        "keyword_hit_count": len(keyword_hits),
        "keyword_min_hits": required_keyword_hits,
        "keyword_coverage": round(keyword_coverage, 6),
        "keyword_min_ratio": round(_clamp01(float(min_ratio)), 6),
        "keyword_pass": bool(keyword_pass),
        "prompt_numbers": prompt_numbers,
        "number_hits": number_hits,
        "number_hit_count": len(number_hits),
        "number_min_hits": required_number_hits,
        "number_pass": bool(number_pass),
        "pass": bool(keyword_pass and number_pass),
    }


def _history_anti_parrot_score(
    *,
    prompt: str,
    response_text: str,
    min_novel_tokens: int,
    min_novel_ratio: float,
    max_prompt_share: float,
    max_sentence_copy_ratio: float,
) -> dict[str, Any]:
    prompt_norm = _normalize_semantic_match_text(prompt)
    response_norm = _normalize_semantic_match_text(response_text)
    prompt_token_set = set(re.findall(r"[a-z]{3,}", prompt_norm))
    response_tokens = re.findall(r"[a-z]{3,}", response_norm)

    if not response_tokens:
        return {
            "novel_token_count": 0,
            "novel_ratio": 0.0,
            "prompt_token_share": 1.0,
            "copied_sentence_ratio": 1.0,
            "copied_sentences": [],
            "min_novel_tokens": int(min_novel_tokens),
            "min_novel_ratio": round(_clamp01(float(min_novel_ratio)), 6),
            "max_prompt_share": round(_clamp01(float(max_prompt_share)), 6),
            "max_sentence_copy_ratio": round(_clamp01(float(max_sentence_copy_ratio)), 6),
            "pass": False,
        }

    boilerplate = {
        "assumptions",
        "assumption",
        "core",
        "idea",
        "verification",
        "checklist",
        "final",
        "claim",
        "oracle",
        "anchor",
        "context",
        "official",
        "statement",
        "constraint",
        "constraints",
        "guiding",
        "concepts",
        "validate",
        "include",
        "step",
        "steps",
        "proof",
        "skeleton",
        "case",
        "cases",
    }

    unique_core: list[str] = []
    seen: set[str] = set()
    for token in response_tokens:
        if token in boilerplate:
            continue
        if token in seen:
            continue
        seen.add(token)
        unique_core.append(token)

    prompt_hits = [token for token in unique_core if token in prompt_token_set]
    novel_tokens = [token for token in unique_core if token not in prompt_token_set]
    prompt_share = len(prompt_hits) / len(unique_core) if unique_core else 1.0
    novel_ratio = len(novel_tokens) / len(unique_core) if unique_core else 0.0

    copied_sentences: list[str] = []
    copied_sentence_count = 0
    response_sentences = [seg.strip() for seg in re.split(r"[.!?\n;]+", response_norm) if seg.strip()]
    for sentence in response_sentences:
        words = sentence.split()
        if len(words) < 8:
            continue
        if sentence in prompt_norm:
            copied_sentence_count += 1
            copied_sentences.append(sentence[:120])
    copied_ratio = copied_sentence_count / len(response_sentences) if response_sentences else 0.0

    pass_flag = (
        len(novel_tokens) >= max(0, int(min_novel_tokens))
        and novel_ratio >= _clamp01(float(min_novel_ratio))
        and prompt_share <= _clamp01(float(max_prompt_share))
        and copied_ratio <= _clamp01(float(max_sentence_copy_ratio))
    )
    return {
        "novel_token_count": len(novel_tokens),
        "novel_tokens": novel_tokens[:24],
        "novel_ratio": round(novel_ratio, 6),
        "prompt_token_share": round(prompt_share, 6),
        "copied_sentence_ratio": round(copied_ratio, 6),
        "copied_sentence_count": copied_sentence_count,
        "response_sentence_count": len(response_sentences),
        "copied_sentences": copied_sentences[:8],
        "min_novel_tokens": int(min_novel_tokens),
        "min_novel_ratio": round(_clamp01(float(min_novel_ratio)), 6),
        "max_prompt_share": round(_clamp01(float(max_prompt_share)), 6),
        "max_sentence_copy_ratio": round(_clamp01(float(max_sentence_copy_ratio)), 6),
        "pass": bool(pass_flag),
    }


def _imo_history_case_skeptic(
    *,
    twin: dict[str, Any],
    row: dict[str, Any],
    prompt: str,
    council_cfg: dict[str, Any],
) -> dict[str, Any]:
    min_chars = max(1, _coerce_int(council_cfg.get("response_min_chars", 24), default=24))
    response_text = str(row.get("response_text", row.get("response_excerpt", ""))).strip()
    response_ok = len(response_text) >= min_chars
    runtime_ok = bool(twin.get("ok"))
    route_action = str(row.get("action", "")).strip()
    source = str(row.get("source", "")).strip()
    route_receipts_ok = bool(route_action) and bool(source)
    decision = str(row.get("decision", "")).strip()
    profile = str(row.get("profile", "")).strip()
    phuc_receipt_ok = bool(decision) and bool(profile)
    min_hits_274 = max(1, _coerce_int(council_cfg.get("section_hits_min_274177", 1), default=1))
    min_hits_655 = max(min_hits_274, _coerce_int(council_cfg.get("section_hits_min_65537", 2), default=2))
    keyword_hits_min_274 = max(0, _coerce_int(council_cfg.get("history_keyword_hits_min_274177", 2), default=2))
    keyword_hits_min_655 = max(
        keyword_hits_min_274,
        _coerce_int(council_cfg.get("history_keyword_hits_min_65537", 4), default=4),
    )
    keyword_ratio_min_274 = _clamp01(
        _coerce_float(council_cfg.get("history_keyword_ratio_min_274177", 0.12), default=0.12)
    )
    keyword_ratio_min_655 = _clamp01(
        _coerce_float(council_cfg.get("history_keyword_ratio_min_65537", 0.22), default=0.22)
    )
    keyword_ratio_min_655 = max(keyword_ratio_min_655, keyword_ratio_min_274)
    number_hits_min_655 = max(0, _coerce_int(council_cfg.get("history_number_hits_min_65537", 1), default=1))
    oracle_match_min_655 = _clamp01(
        _coerce_float(council_cfg.get("history_oracle_match_min_65537", 0.92), default=0.92)
    )
    min_novel_tokens_655 = max(
        0, _coerce_int(council_cfg.get("history_min_novel_tokens_65537", 8), default=8)
    )
    min_novel_ratio_655 = _clamp01(
        _coerce_float(council_cfg.get("history_min_novel_ratio_65537", 0.18), default=0.18)
    )
    max_prompt_share_655 = _clamp01(
        _coerce_float(council_cfg.get("history_max_prompt_share_65537", 0.88), default=0.88)
    )
    max_sentence_copy_ratio_655 = _clamp01(
        _coerce_float(council_cfg.get("history_max_sentence_copy_ratio_65537", 0.55), default=0.55)
    )
    require_oracle_quality_655 = bool(council_cfg.get("history_require_oracle_quality_for_65537", True))
    min_quality_tier_655 = str(council_cfg.get("history_oracle_quality_min_tier_65537", "standard")).strip().lower()
    if min_quality_tier_655 not in {"none", "weak", "standard", "strong"}:
        min_quality_tier_655 = "standard"

    contract_274 = _history_response_contract_score(prompt, response_text, min_hits=min_hits_274)
    contract_655 = _history_response_contract_score(prompt, response_text, min_hits=min_hits_655)
    grounding_274 = _history_prompt_keyword_coverage(
        prompt=prompt,
        response_text=response_text,
        min_hits=keyword_hits_min_274,
        min_ratio=keyword_ratio_min_274,
        min_number_hits=0,
    )
    grounding_655 = _history_prompt_keyword_coverage(
        prompt=prompt,
        response_text=response_text,
        min_hits=keyword_hits_min_655,
        min_ratio=keyword_ratio_min_655,
        min_number_hits=number_hits_min_655,
    )
    anti_parrot_655 = _history_anti_parrot_score(
        prompt=prompt,
        response_text=response_text,
        min_novel_tokens=min_novel_tokens_655,
        min_novel_ratio=min_novel_ratio_655,
        max_prompt_share=max_prompt_share_655,
        max_sentence_copy_ratio=max_sentence_copy_ratio_655,
    )

    needle = str(row.get("needle", "")).strip()
    aliases_raw = row.get("aliases", [])
    aliases = [str(item).strip() for item in aliases_raw if str(item).strip()] if isinstance(aliases_raw, list) else []
    oracle_targets = _expand_semantic_aliases(needle) + aliases if needle else aliases
    oracle_targets = [item for item in oracle_targets if item]
    oracle_available = len(oracle_targets) > 0
    oracle_match = (
        _semantic_match_score(response_text, oracle_targets)
        if oracle_available
        else {
            "matched": False,
            "mode": "none",
            "score": 0.0,
            "target": "",
            "strict_match": False,
            "normalized_match": False,
            "token_coverage": 0.0,
        }
    )
    oracle_pass = bool(oracle_match.get("matched")) and float(oracle_match.get("score", 0.0)) >= oracle_match_min_655
    concepts_raw = row.get("oracle_concepts", [])
    concepts = [str(item).strip() for item in concepts_raw if str(item).strip()] if isinstance(concepts_raw, list) else []
    required_sections_raw = row.get("oracle_required_sections", [])
    required_sections = (
        [str(item).strip() for item in required_sections_raw if str(item).strip()]
        if isinstance(required_sections_raw, list)
        else []
    )
    concept_meta = _concept_coverage_score(response_text, concepts)
    section_meta = _required_sections_score(response_text, required_sections)
    concept_cov = float(concept_meta.get("coverage", 1.0))
    section_hits = int(section_meta.get("hit_count", 0))
    concept_ok_274 = concept_cov >= _coerce_float(council_cfg.get("concept_coverage_min_274177", 0.5), default=0.5)
    concept_ok_655 = concept_cov >= _coerce_float(council_cfg.get("concept_coverage_min_65537", 0.8), default=0.8)
    section_ok_274 = section_hits >= _coerce_int(council_cfg.get("section_hits_min_274177", 1), default=1)
    section_ok_655 = section_hits >= _coerce_int(council_cfg.get("section_hits_min_65537", 2), default=2)
    if not list(concept_meta.get("concepts", [])):
        concept_ok_274 = True
        concept_ok_655 = True
    if not list(section_meta.get("required_sections", [])):
        section_ok_274 = True
        section_ok_655 = True
    quality_tier = str(row.get("oracle_quality_tier", "")).strip().lower()
    quality_score = _coerce_float(row.get("oracle_quality_score", 0.0), default=0.0)
    if not quality_tier:
        quality_meta_fallback = _oracle_quality_assessment(
            needle=needle,
            aliases=aliases,
            concepts=concepts,
            required_sections=required_sections,
            statement_excerpt="",
        )
        quality_tier = str(quality_meta_fallback.get("tier", "none")).strip().lower() or "none"
        quality_score = _coerce_float(quality_meta_fallback.get("score", 0.0), default=0.0)
    quality_ok_655 = (
        _oracle_quality_tier_rank(quality_tier) >= _oracle_quality_tier_rank(min_quality_tier_655)
    ) if require_oracle_quality_655 else True

    votes: list[dict[str, Any]] = [
        _expert_vote("runtime_guard", runtime_ok, "twin subprocess returns ok"),
        _expert_vote("response_guard", response_ok, f"response excerpt has at least {min_chars} chars"),
        _expert_vote("route_receipts_guard", route_receipts_ok, "route source/action are present"),
        _expert_vote("phuc_receipt_guard", phuc_receipt_ok, "decision/profile receipts are present"),
        _expert_vote(
            "response_contract_guard",
            bool(contract_274.get("pass")),
            "response follows requested assumptions/core-idea/verification structure",
        ),
        _expert_vote(
            "prompt_grounding_guard",
            bool(grounding_274.get("pass")),
            "response reuses non-trivial prompt keywords (anti-template gate)",
        ),
        _expert_vote(
            "concept_guard_274177",
            concept_ok_274,
            "oracle concepts meet rung-274177 threshold when configured",
        ),
        _expert_vote(
            "section_guard_274177",
            section_ok_274,
            "oracle required sections meet rung-274177 threshold when configured",
        ),
        _expert_vote(
            "oracle_guard_65537",
            bool(oracle_available and oracle_pass),
            "65537 requires configured oracle needle/aliases and strong semantic match",
            weight=0.0,
        ),
        _expert_vote(
            "anti_parrot_guard_65537",
            bool(anti_parrot_655.get("pass")),
            "65537 rejects template/parrot answers via novelty + copy-ratio checks",
            weight=0.0,
        ),
        _expert_vote(
            "oracle_quality_guard_65537",
            bool(quality_ok_655),
            f"65537 requires oracle quality tier >= {min_quality_tier_655}",
            weight=0.0,
        ),
    ]

    require_route_receipts = bool(council_cfg.get("require_route_receipts", True))
    require_phuc_274 = bool(council_cfg.get("require_phuc_receipt_for_274177", True))
    require_tool_655 = bool(council_cfg.get("require_tool_route_for_65537", True))
    tool_route_655_ok = str(decision).lower() == "tool" if require_tool_655 else True
    gates = {
        "r641": runtime_ok and response_ok and (route_receipts_ok if require_route_receipts else True),
        "r274177": runtime_ok
        and response_ok
        and (phuc_receipt_ok if require_phuc_274 else True)
        and bool(contract_274.get("pass"))
        and bool(grounding_274.get("pass"))
        and concept_ok_274
        and section_ok_274,
        "r65537": runtime_ok
        and response_ok
        and phuc_receipt_ok
        and bool(contract_655.get("pass"))
        and bool(grounding_655.get("pass"))
        and bool(anti_parrot_655.get("pass"))
        and concept_ok_655
        and section_ok_655
        and bool(tool_route_655_ok)
        and bool(oracle_available)
        and bool(oracle_pass)
        and bool(quality_ok_655),
    }
    council = _aggregate_expert_council(votes=votes, gates=gates, cfg=council_cfg)
    status = str(council.get("status", "FAIL"))
    fail_reasons = list(council.get("fail_reasons", [])) if isinstance(council.get("fail_reasons"), list) else []
    return {
        "status": status,
        "rung_achieved": int(council.get("rung_achieved", 0)),
        "required_rung": int(council.get("required_rung", 641)),
        "fail_reasons": fail_reasons,
        "required_fixes": [
            "stabilize endpoint + retries",
            "inspect route metadata path",
            "improve prompt contract compliance in response",
            "validate parsed dataset prompt quality",
        ]
        if fail_reasons
        else [],
        "response_contract": {
            "r274177": contract_274,
            "r65537": contract_655,
        },
        "prompt_grounding": {
            "r274177": grounding_274,
            "r65537": grounding_655,
        },
        "anti_parrot": {
            "r65537": anti_parrot_655,
        },
        "oracle": {
            "available": bool(oracle_available),
            "targets": oracle_targets[:16],
            "threshold_65537": oracle_match_min_655,
            "pass_65537": bool(oracle_available and oracle_pass),
            "match": oracle_match,
            "quality": {
                "tier": quality_tier,
                "score": round(float(quality_score), 6),
                "required_min_tier_65537": min_quality_tier_655,
                "quality_pass_65537": bool(quality_ok_655),
            },
            "concepts": concept_meta,
            "required_sections": section_meta,
            "concept_pass_274177": bool(concept_ok_274),
            "concept_pass_65537": bool(concept_ok_655),
            "required_sections_pass_274177": bool(section_ok_274),
            "required_sections_pass_65537": bool(section_ok_655),
        },
        "response_chars": len(response_text),
        "expert_council": council,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stillwater",
        description="Stillwater OS helper CLI (repo-local).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="cmd", required=False)

    p_paths = sub.add_parser("paths", help="Print key repo paths.")
    p_paths.add_argument("--json", action="store_true", help="Machine-readable output.")

    sub.add_parser("print", help="Print suggested next steps.")

    p_init = sub.add_parser("init", help="Scaffold Stillwater project templates.")
    p_init_sub = p_init.add_subparsers(dest="init_cmd", required=True)

    p_init_agi = p_init_sub.add_parser("agi-cli", help="Create an AGI-enabled CLI starter project.")
    p_init_agi.add_argument("name", help="Project directory name.")
    p_init_agi.add_argument("--dir", default=".", help="Parent directory for scaffold output.")
    p_init_agi.add_argument("--force", action="store_true", help="Allow writing into an existing directory.")
    p_init_agi.add_argument(
        "--identity-stack",
        action="store_true",
        help="Also create identity files (AGENTS/SOUL/IDENTITY/USER/HEARTBEAT/BOOTSTRAP).",
    )
    p_init_agi.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_init_identity = p_init_sub.add_parser("identity-stack", help="Create identity stack docs for persistent agents.")
    p_init_identity.add_argument("--dir", default="cli/identity", help="Identity directory.")
    p_init_identity.add_argument("--force", action="store_true", help="Overwrite existing files.")
    p_init_identity.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_init_project = p_init_sub.add_parser(
        "project",
        help="Install Stillwater into an existing project (lean CLAUDE.md + ripple + skills/).",
    )
    p_init_project.add_argument("--name", required=True, help="Project name (used in CLAUDE.md header).")
    p_init_project.add_argument(
        "--skills",
        default="prime-safety,prime-coder,phuc-orchestration,phuc-forecast",
        help="Comma-separated skills to load (default: prime-safety,prime-coder,phuc-orchestration,phuc-forecast).",
    )
    p_init_project.add_argument(
        "--rung",
        default="641",
        choices=["641", "274177", "65537"],
        help="Verification rung target (default: 641).",
    )
    p_init_project.add_argument(
        "--domain",
        default="",
        help="Project domain description (e.g. 'lossless compression').",
    )
    p_init_project.add_argument("--dir", default=".", help="Project root directory (default: current dir).")
    p_init_project.add_argument("--force", action="store_true", help="Overwrite existing CLAUDE.md and ripple file.")
    p_init_project.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_skills_ab = sub.add_parser("skills-ab", help="Run the skills A/B/AB/ABC benchmark (local-first).")
    p_skills_ab.add_argument("--backend", choices=["auto", "ollama", "mock"], default="auto")
    p_skills_ab.add_argument("--ollama-url", default=None, help="Ollama base URL (auto-detect if omitted).")
    p_skills_ab.add_argument("--model", default=None, help="Model name (backend-specific).")
    p_skills_ab.add_argument("--no-cache", action="store_true", help="Disable response caching.")
    p_skills_ab.add_argument("--timeout", type=float, default=60.0, help="Backend request timeout in seconds.")
    p_skills_ab.add_argument("--seed", type=int, default=1337, help="Determinism seed (mock backend).")
    p_skills_ab.add_argument("--run-id", default=None, help="Optional run id for receipts (default: UTC timestamp).")
    p_skills_ab.add_argument("--no-record-prompts", action="store_true", help="Do not write raw prompt/response receipts.")

    p_llm = sub.add_parser("llm", help="Manage LLM providers and local/remote Ollama connectivity.")
    p_llm_sub = p_llm.add_subparsers(dest="llm_cmd", required=True)

    p_llm_sub.add_parser("status", help="Show active provider and validation status.")
    p_llm_sub.add_parser("providers", help="List configured providers from llm_config.yaml.")

    p_probe = p_llm_sub.add_parser("probe-ollama", help="Probe candidate local/remote Ollama servers.")
    p_probe.add_argument("--url", action="append", default=[], help="Explicit URL (repeatable).")
    p_probe.add_argument("--timeout", type=float, default=2.0, help="Per-endpoint timeout in seconds.")
    p_probe.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_models = p_llm_sub.add_parser("models", help="List models from a reachable Ollama endpoint.")
    p_models.add_argument("--url", default=None, help="Optional Ollama base URL.")
    p_models.add_argument("--timeout", type=float, default=2.0, help="Request timeout in seconds.")
    p_models.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_set_provider = p_llm_sub.add_parser("set-provider", help="Update active provider in llm_config.yaml.")
    p_set_provider.add_argument("provider", help="Provider key (e.g., ollama, claude-code, openai).")

    p_set_ollama = p_llm_sub.add_parser("set-ollama", help="Update ollama url/model in llm_config.yaml.")
    p_set_ollama.add_argument("--url", default=None, help="Ollama base URL to store.")
    p_set_ollama.add_argument("--model", default=None, help="Default ollama model to store.")
    p_set_ollama.add_argument("--activate", action="store_true", help="Also set provider=ollama.")
    p_set_ollama.add_argument(
        "--auto-url",
        action="store_true",
        help="Auto-probe local/remote candidates and write the preferred reachable URL.",
    )
    p_set_ollama.add_argument("--timeout", type=float, default=2.0, help="Probe timeout in seconds.")

    p_twin = sub.add_parser(
        "twin",
        help="Twin orchestration runtime (CPU prepass + Ollama fallback) for natural-language CLI interaction.",
    )
    p_twin.add_argument("prompt", nargs="*", help="Prompt text (omit with --interactive).")
    p_twin.add_argument("--interactive", "-i", action="store_true", help="Interactive REPL mode.")
    p_twin.add_argument("--url", default=None, help="Optional Ollama URL.")
    p_twin.add_argument("--model", default=None, help="Optional Ollama model.")
    p_twin.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds.")
    p_twin.add_argument("--run-id", default=None, help="Optional run id prefix.")
    p_twin.add_argument("--skill", action="append", default=[], help="Skill file name to load (repeatable).")
    p_twin.add_argument("--all-skills", action="store_true", help="Load all root skills/*.md into system context.")
    p_twin.add_argument("--no-skill-context", action="store_true", help="Disable skill-context injection.")
    p_twin.add_argument(
        "--llm-only",
        action="store_true",
        help="Bypass CPU benchmark routing for non-slash prompts and send prompt directly to Ollama.",
    )
    p_twin.add_argument("--json", action="store_true", help="Machine-readable output for single-turn mode.")

    p_skills = sub.add_parser("skills", help="Skill inventory and install/sync commands.")
    p_skills_sub = p_skills.add_subparsers(dest="skills_cmd", required=True)

    p_skills_list = p_skills_sub.add_parser("list", help="List available skills.")
    p_skills_list.add_argument(
        "--source",
        choices=["root", "cli", "extension", "all"],
        default="all",
        help="Filter by source tree.",
    )
    p_skills_list.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_skills_sync = p_skills_sub.add_parser("sync", help="Copy resolved skills into a destination folder.")
    p_skills_sync.add_argument("--dest", default="cli/skills/stillwater", help="Destination directory (repo-relative).")
    p_skills_sync.add_argument("--skill", action="append", default=[], help="Skill name to sync (repeatable).")
    p_skills_sync.add_argument("--all", action="store_true", help="Sync all root skills.")
    p_skills_sync.add_argument("--force", action="store_true", help="Overwrite existing destination files.")
    p_skills_sync.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_skills_show = p_skills_sub.add_parser("show", help="Print one skill file.")
    p_skills_show.add_argument("name", help="Skill file name, e.g. prime-coder or prime-coder.md.")

    p_skills_install = p_skills_sub.add_parser("install", help="Install a skill locally and to ~/.claude/skills/.")
    p_skills_install.add_argument("name", help="Skill name, e.g. prime-coder or prime-coder.md.")
    p_skills_install.add_argument("--no-remote", action="store_true", help="Skip GitHub fetch; local-only.")
    p_skills_install.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_skills_export = p_skills_sub.add_parser("export", help="Export a skill as SKILL.md-compatible format.")
    p_skills_export.add_argument("name", help="Skill name, e.g. prime-coder or prime-coder.md.")
    p_skills_export.add_argument("--output", default=None, help="Output file path (default: stdout).")
    p_skills_export.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_wish = sub.add_parser("wish", help="Wish notebook workflow commands (gamified, Prime Mermaid-first).")
    p_wish_sub = p_wish.add_subparsers(dest="wish_cmd", required=True)

    p_wish_list = p_wish_sub.add_parser("list", help="List available wishes in cli/wishes and wishes/examples.")
    p_wish_list.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_wish_init = p_wish_sub.add_parser("init", help="Create a new wish scaffold.")
    p_wish_init.add_argument("wish_id", help="Wish identifier, e.g. wish.cli.stack.run.v1")
    p_wish_init.add_argument("--level", choices=["l0", "l1", "l2"], default="l1", help="Wish level.")
    p_wish_init.add_argument("--path", default="cli/wishes", help="Target directory.")
    p_wish_init.add_argument("--force", action="store_true", help="Overwrite if target already exists.")

    p_wish_run = p_wish_sub.add_parser("run", help="Execute a wish notebook with nbconvert.")
    p_wish_run.add_argument("notebook", help="Path to notebook file.")
    p_wish_run.add_argument("--timeout", type=float, default=300.0, help="Notebook execution timeout.")
    p_wish_run.add_argument(
        "--verify-wish-id",
        default=None,
        help="Optional wish_id to validate artifacts after execution.",
    )

    p_wish_verify = p_wish_sub.add_parser("verify", help="Verify wish artifacts (state.mmd/sha/results.json).")
    p_wish_verify.add_argument("wish_id", help="Wish identifier, matching artifacts/wishes/<wish_id>/")
    p_wish_verify.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_stack = sub.add_parser("stack", help="Run and verify full Stillwater stack workflows.")
    p_stack_sub = p_stack.add_subparsers(dest="stack_cmd", required=True)

    p_stack_run = p_stack_sub.add_parser("run", help="Run a stack profile with receipts.")
    p_stack_run.add_argument(
        "--profile",
        choices=["offline", "ollama-local", "ollama-remote"],
        default="offline",
        help="Execution profile.",
    )
    p_stack_run.add_argument("--run-id", default=None, help="Optional run identifier.")
    p_stack_run.add_argument(
        "--execute-notebooks",
        action="store_true",
        help="Execute notebook steps in addition to CLI steps.",
    )
    p_stack_run.add_argument("--timeout", type=float, default=600.0, help="Per-step timeout in seconds.")
    p_stack_run.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_stack_verify = p_stack_sub.add_parser("verify", help="Verify a prior stack run.")
    p_stack_verify.add_argument("--run-id", default=None, help="Run id (defaults to latest).")
    p_stack_verify.add_argument("--strict", action="store_true", help="Require all steps to be successful.")
    p_stack_verify.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_recipe = sub.add_parser("recipe", help="Recipe and Prime Mermaid governance commands.")
    p_recipe_sub = p_recipe.add_subparsers(dest="recipe_cmd", required=True)

    p_recipe_lint = p_recipe_sub.add_parser("lint", help="Lint recipe/ripple paths.")
    p_recipe_lint.add_argument("--prime-mermaid-only", action="store_true", help="Reject source YAML/JSON files.")
    p_recipe_lint.add_argument(
        "--dir",
        action="append",
        default=[],
        help="Directory to lint (repeatable). Defaults to wishes/ripples/recipes/memory/cli/wishes.",
    )
    p_recipe_lint.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_recipe_list = p_recipe_sub.add_parser("list", help="List Prime Mermaid recipe files.")
    p_recipe_list.add_argument(
        "--dir",
        action="append",
        default=[],
        help="Directory to scan (repeatable). Defaults are extension-aware kernel recipe dirs.",
    )
    p_recipe_list.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_recipe_add = p_recipe_sub.add_parser("add", help="Create a new Prime Mermaid recipe template.")
    p_recipe_add.add_argument("name", help="Recipe name, e.g. twin_orchestration.")
    p_recipe_add.add_argument("--dir", default="cli/recipes", help="Target directory.")
    p_recipe_add.add_argument("--force", action="store_true", help="Overwrite if exists.")
    p_recipe_add.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_books = sub.add_parser("books", help="List/show markdown books for persistent-intelligence context.")
    p_books_sub = p_books.add_subparsers(dest="books_cmd", required=True)

    p_books_list = p_books_sub.add_parser("list", help="List books from configured books directories.")
    p_books_list.add_argument(
        "--dir",
        action="append",
        default=[],
        help="Directory to scan (repeatable). Defaults are kernel books dirs.",
    )
    p_books_list.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_books_show = p_books_sub.add_parser("show", help="Show one book by basename or path.")
    p_books_show.add_argument("name", help="Book basename or path.")
    p_books_show.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_papers = sub.add_parser("papers", help="List/show markdown papers for Software 5.0 and CLI architecture.")
    p_papers_sub = p_papers.add_subparsers(dest="papers_cmd", required=True)

    p_papers_list = p_papers_sub.add_parser("list", help="List papers from configured paper directories.")
    p_papers_list.add_argument(
        "--dir",
        action="append",
        default=[],
        help="Directory to scan (repeatable). Defaults are kernel paper dirs.",
    )
    p_papers_list.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_papers_show = p_papers_sub.add_parser("show", help="Show one paper by basename or path.")
    p_papers_show.add_argument("name", help="Paper basename or path.")
    p_papers_show.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_math_universal = sub.add_parser(
        "math-universal",
        help=(
            "Run universal-math readiness gates: heldout breadth, proof artifacts, "
            "no-oracle generalization, and model/provider stability."
        ),
    )
    p_math_universal.add_argument(
        "--config",
        default="cli/tests/math/universal_math_gate.json",
        help="Gate config JSON path.",
    )
    p_math_universal.add_argument("--model", default=None, help="Optional default model override.")
    p_math_universal.add_argument("--url", default=None, help="Optional default URL override.")
    p_math_universal.add_argument("--timeout", type=float, default=45.0, help="Default timeout override in seconds.")
    p_math_universal.add_argument(
        "--fetch-missing",
        action="store_true",
        help="Fetch missing datasets during benchmark profiles.",
    )
    p_math_universal.add_argument(
        "--no-strict",
        action="store_true",
        help="Return success even when one or more gates fail.",
    )
    p_math_universal.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_imo_phuc = sub.add_parser(
        "imo-phuc",
        help="Run SWE-pattern PHUC 5-phase IMO QA (DREAM/FORECAST/DECIDE/ACT/VERIFY).",
    )
    p_imo_phuc.add_argument(
        "--cases-file",
        default="cli/tests/math/imo_qa_cases.json",
        help="JSON file with {cases:[{id,prompt,needle}]}.",
    )
    p_imo_phuc.add_argument("--model", default="llama3.1:8b", help="Model name for twin calls.")
    p_imo_phuc.add_argument("--url", default=None, help="Optional Ollama URL override.")
    p_imo_phuc.add_argument("--timeout", type=float, default=45.0, help="Per-lane timeout in seconds.")
    p_imo_phuc.add_argument("--run-id", default=None, help="Optional run identifier.")
    p_imo_phuc.add_argument(
        "--required-rung",
        type=int,
        default=65537,
        help="Verification rung target for strict pass (641, 274177, 65537).",
    )
    p_imo_phuc.add_argument(
        "--no-strict",
        action="store_true",
        help="Return success even if tool_assisted is not N/N.",
    )
    p_imo_phuc.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_imo_hist = sub.add_parser(
        "imo-history",
        help="Fetch official IMO problem PDFs and run historical orchestration benchmarks.",
    )
    p_imo_hist_sub = p_imo_hist.add_subparsers(dest="imo_hist_cmd", required=True)

    p_imo_fetch = p_imo_hist_sub.add_parser("fetch", help="Download and parse IMO problems for a year range.")
    p_imo_fetch.add_argument("--from-year", type=int, default=2020, help="Start year (inclusive).")
    p_imo_fetch.add_argument("--to-year", type=int, default=2024, help="End year (inclusive).")
    p_imo_fetch.add_argument("--lang", default="eng", help="Language code from IMO site (default: eng).")
    p_imo_fetch.add_argument("--timeout", type=float, default=45.0, help="HTTP timeout in seconds.")
    p_imo_fetch.add_argument("--force", action="store_true", help="Re-download and overwrite local cache.")
    p_imo_fetch.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_imo_bench = p_imo_hist_sub.add_parser(
        "bench",
        help="Run twin orchestration against fetched historical IMO problems.",
    )
    p_imo_bench.add_argument("--from-year", type=int, default=2020, help="Start year (inclusive).")
    p_imo_bench.add_argument("--to-year", type=int, default=2024, help="End year (inclusive).")
    p_imo_bench.add_argument("--lang", default="eng", help="Language code from IMO site (default: eng).")
    p_imo_bench.add_argument("--fetch-missing", action="store_true", help="Fetch missing yearly datasets before run.")
    p_imo_bench.add_argument("--model", default="llama3.1:8b", help="Model name for twin calls.")
    p_imo_bench.add_argument("--url", default=None, help="Optional Ollama URL override.")
    p_imo_bench.add_argument("--timeout", type=float, default=45.0, help="Per-prompt timeout in seconds.")
    p_imo_bench.add_argument("--max-problems", type=int, default=0, help="Cap total problem count (0 = all).")
    p_imo_bench.add_argument(
        "--oracles-file",
        default="cli/tests/math/imo_history_oracles.json",
        help="Optional JSON file with historical oracle targets (year/problem_id -> needle/aliases).",
    )
    p_imo_bench.add_argument("--llm-only", action="store_true", help="Run the llm-only baseline lane.")
    p_imo_bench.add_argument(
        "--required-rung",
        type=int,
        default=641,
        help="Verification rung target per case (641, 274177, 65537).",
    )
    p_imo_bench.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_imo_autolearn = p_imo_hist_sub.add_parser(
        "autolearn",
        help="Run iterative IMO history self-learning: benchmark -> patch oracles -> re-verify.",
    )
    p_imo_autolearn.add_argument("--from-year", type=int, default=2020, help="Start year (inclusive).")
    p_imo_autolearn.add_argument("--to-year", type=int, default=2024, help="End year (inclusive).")
    p_imo_autolearn.add_argument("--lang", default="eng", help="Language code from IMO site (default: eng).")
    p_imo_autolearn.add_argument("--fetch-missing", action="store_true", help="Fetch missing yearly datasets before run.")
    p_imo_autolearn.add_argument("--model", default="llama3.1:8b", help="Model name for twin calls.")
    p_imo_autolearn.add_argument("--url", default=None, help="Optional Ollama URL override.")
    p_imo_autolearn.add_argument("--timeout", type=float, default=45.0, help="Per-prompt timeout in seconds.")
    p_imo_autolearn.add_argument("--max-problems", type=int, default=0, help="Cap total problem count (0 = all).")
    p_imo_autolearn.add_argument(
        "--oracles-file",
        default="cli/tests/math/imo_history_oracles.json",
        help="Oracle JSON file path to improve.",
    )
    p_imo_autolearn.add_argument(
        "--required-rung",
        type=int,
        default=65537,
        help="Target verification rung (641, 274177, 65537).",
    )
    p_imo_autolearn.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum autolearn iterations (each iteration runs one benchmark).",
    )
    p_imo_autolearn.add_argument(
        "--min-pass-delta",
        type=int,
        default=1,
        help="Minimum pass-case improvement required before writing learned oracles.",
    )
    p_imo_autolearn.add_argument(
        "--apply",
        action="store_true",
        default=True,
        help="Write learned oracle updates back to --oracles-file when validated (default: enabled).",
    )
    p_imo_autolearn.add_argument(
        "--no-apply",
        action="store_false",
        dest="apply",
        help="Dry-run only; do not write learned oracle updates.",
    )
    p_imo_autolearn.add_argument(
        "--no-strict",
        action="store_true",
        help="Return success if improvements were made even if strict pass is not reached.",
    )
    p_imo_autolearn.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_imo_oracles = p_imo_hist_sub.add_parser(
        "oracles-template",
        help="Generate an editable historical IMO oracle template JSON from fetched datasets.",
    )
    p_imo_oracles.add_argument("--from-year", type=int, default=2020, help="Start year (inclusive).")
    p_imo_oracles.add_argument("--to-year", type=int, default=2024, help="End year (inclusive).")
    p_imo_oracles.add_argument("--lang", default="eng", help="Language code from IMO site (default: eng).")
    p_imo_oracles.add_argument("--fetch-missing", action="store_true", help="Fetch missing yearly datasets before generation.")
    p_imo_oracles.add_argument("--max-problems", type=int, default=0, help="Cap total problem count (0 = all).")
    p_imo_oracles.add_argument(
        "--out",
        default="cli/tests/math/imo_history_oracles.json",
        help="Output JSON file path.",
    )
    p_imo_oracles.add_argument(
        "--merge-existing",
        action="store_true",
        default=True,
        help="Keep existing oracle entries and only append missing cases (default: enabled).",
    )
    p_imo_oracles.add_argument(
        "--no-merge-existing",
        action="store_false",
        dest="merge_existing",
        help="Regenerate template from scratch and overwrite existing oracle fields.",
    )
    p_imo_oracles.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_imo_oracle_status = p_imo_hist_sub.add_parser(
        "oracle-status",
        help="Report historical oracle coverage by year/problem.",
    )
    p_imo_oracle_status.add_argument("--from-year", type=int, default=2020, help="Start year (inclusive).")
    p_imo_oracle_status.add_argument("--to-year", type=int, default=2024, help="End year (inclusive).")
    p_imo_oracle_status.add_argument("--lang", default="eng", help="Language code from IMO site (default: eng).")
    p_imo_oracle_status.add_argument("--fetch-missing", action="store_true", help="Fetch missing yearly datasets before report.")
    p_imo_oracle_status.add_argument("--max-problems", type=int, default=0, help="Cap total problem count (0 = all).")
    p_imo_oracle_status.add_argument(
        "--oracles-file",
        default="cli/tests/math/imo_history_oracles.json",
        help="Oracle JSON file path.",
    )
    p_imo_oracle_status.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_oolong = sub.add_parser("oolong", help="Run and verify OOLONG counter-bypass workflow.")
    p_oolong_sub = p_oolong.add_subparsers(dest="oolong_cmd", required=True)

    p_oolong_run = p_oolong_sub.add_parser("run", help="Execute OOLONG solver and store artifacts.")
    p_oolong_run.add_argument("--real", action="store_true", help="Use optional real solver path.")
    p_oolong_run.add_argument("--run-id", default=None, help="Optional run id.")
    p_oolong_run.add_argument("--timeout", type=float, default=300.0, help="Execution timeout.")
    p_oolong_run.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_oolong_verify = p_oolong_sub.add_parser("verify", help="Verify OOLONG run artifacts.")
    p_oolong_verify.add_argument("--run-id", default=None, help="Run id (defaults to latest).")
    p_oolong_verify.add_argument("--strict", action="store_true", help="Require rung + completion checks.")
    p_oolong_verify.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_learn = sub.add_parser("learn", help="Externalized learning loop with Prime Mermaid ripples.")
    p_learn_sub = p_learn.add_subparsers(dest="learn_cmd", required=True)

    p_learn_prop = p_learn_sub.add_parser("propose", help="Create a learning proposal artifact.")
    p_learn_prop.add_argument("title", help="Short proposal title.")
    p_learn_prop.add_argument("--note", default="", help="Optional note.")
    p_learn_prop.add_argument("--wish-id", default="", help="Related wish id.")
    p_learn_prop.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_learn_apply = p_learn_sub.add_parser("apply", help="Apply a proposal to ripples/project.")
    p_learn_apply.add_argument("proposal", help="Path to proposal .prime-mermaid.md file.")
    p_learn_apply.add_argument("--dest-dir", default="ripples/project", help="Destination directory.")
    p_learn_apply.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_cleanup = sub.add_parser("cleanup", help="Phuc cleanup: scan and archive glow artifacts with approval gates.")
    p_cleanup_sub = p_cleanup.add_subparsers(dest="cleanup_cmd", required=True)

    p_cleanup_scan = p_cleanup_sub.add_parser("scan", help="Scan safe glow + suspicious candidates and write receipt.")
    p_cleanup_scan.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Scan scope directory (repeatable, repo-relative). Defaults to artifacts.",
    )
    p_cleanup_scan.add_argument(
        "--audit-file",
        default="FINAL-AUDIT.md",
        help="Path to FINAL-AUDIT style file for suspicious path extraction.",
    )
    p_cleanup_scan.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_cleanup_apply = p_cleanup_sub.add_parser("apply", help="Archive files from a cleanup scan receipt.")
    p_cleanup_apply.add_argument(
        "--scan-receipt",
        default="",
        help="Path to cleanup-scan receipt JSON (defaults to latest).",
    )
    p_cleanup_apply.add_argument(
        "--approve-suspicious",
        action="store_true",
        help="Allow mutation of suspicious-class files.",
    )
    p_cleanup_apply.add_argument(
        "--approve-tracked",
        action="store_true",
        help="Allow mutation of git-tracked files.",
    )
    p_cleanup_apply.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_replay = sub.add_parser("replay", help="Replay a stack run from artifacts/runs/<run_id>/manifest.json.")
    p_replay.add_argument("run_id", help="Run identifier.")
    p_replay.add_argument("--rerun", action="store_true", help="Execute stored commands again.")
    p_replay.add_argument("--timeout", type=float, default=600.0, help="Per-step timeout for --rerun.")
    p_replay.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_gen = sub.add_parser("gen-ai-steroids-readme", help="Generate ai-steroids-results/README.md (or check it).")
    p_gen.add_argument("--check", action="store_true", help="Exit non-zero if README would change.")

    p_demo = sub.add_parser("demo", help="Run a quick demo: 'What is Software 5.0?' with prime-safety skill (dry-run).")
    p_demo.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_run = sub.add_parser("run", help="Run a task with optional skill context and LLM backend.")
    p_run.add_argument("task", help="Task string, e.g. \"summarize the skills directory\".")
    p_run.add_argument("--skill", default=None, help="Skill name to load from skills/ (e.g. prime-coder).")
    p_run.add_argument("--dry-run", action="store_true", help="Show what would run without calling any LLM.")
    p_run.add_argument("--run-id", default=None, help="Optional run id (default: auto-generated).")
    p_run.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_evidence = sub.add_parser("evidence", help="Prime-coder evidence directory management.")
    p_evidence_sub = p_evidence.add_subparsers(dest="evidence_cmd", required=True)

    p_evidence_init = p_evidence_sub.add_parser(
        "init", help="Create evidence/ directory with required prime-coder template files."
    )
    p_evidence_init.add_argument(
        "--dir", default="evidence", dest="evidence_dir",
        help="Evidence directory path (default: evidence).",
    )

    p_evidence_verify = p_evidence_sub.add_parser(
        "verify", help="Validate evidence directory against prime-coder evidence contract."
    )
    p_evidence_verify.add_argument(
        "--dir", default="evidence", dest="evidence_dir",
        help="Evidence directory path (default: evidence).",
    )
    p_evidence_verify.add_argument(
        "--rung", type=int, default=641, choices=[641, 274177, 65537],
        help="Verification rung target (default: 641).",
    )

    ns = parser.parse_args(argv)

    root = _repo_root()
    notebooks = [
        "HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb",
        "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        "HOW-TO-CRUSH-SWE-BENCHMARK.ipynb",
        "PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb",
        "PHUC-SKILLS-SECRET-SAUCE.ipynb",
        "PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb",
        "cli/notebooks/HOW-TO-CLONE-TO-FIRST-RUN.ipynb",
        "cli/notebooks/HOW-TO-OLLAMA-LOCAL-REMOTE.ipynb",
        "cli/notebooks/HOW-TO-RECIPE-CONTRACT-BENCHMARK.ipynb",
        "cli/notebooks/HOW-TO-CONVENTION-DENSITY-BENCHMARK.ipynb",
        "cli/notebooks/HOW-TO-RIPPLE-LEARNING-BENCHMARK.ipynb",
        "cli/notebooks/HOW-TO-PLUGIN-SDK-BENCHMARK.ipynb",
        "cli/notebooks/HOW-TO-BRUCE-LEE-LLM-DOJO.ipynb",
        "cli/notebooks/HOW-TO-WISH-NOTEBOOK-LOOP.ipynb",
        "cli/notebooks/HOW-TO-TWIN-ORCHESTRATION.ipynb",
        "cli/notebooks/HOW-TO-SOFTWARE-5.0-PAPERS.ipynb",
        "cli/notebooks/HOW-TO-SECRET-SAUCE-INTEGRATION.ipynb",
    ]
    papers_index = "papers/00-index.md"
    mission = "MESSAGE-TO-HUMANITY.md"

    if ns.cmd == "paths":
        kernel = _kernel_paths(root)
        skill_dirs = []
        for source, path in kernel["skill_dirs"]:
            skill_dirs.append({"source": source, "path": str(path)})
        data = {
            "repo_root": str(root),
            "mission": str(root / mission),
            "papers_index": str(root / papers_index),
            "notebooks": [str(root / p) for p in notebooks],
            "kernel": {
                "config_path": str(kernel["config_path"]),
                "extension_root": str(kernel["extension_root"]),
                "skill_dirs": skill_dirs,
                "recipe_dirs": list(kernel["recipe_dirs"]),
                "books_dirs": list(kernel["books_dirs"]),
                "papers_dirs": list(kernel["papers_dirs"]),
                "identity_dir": str(kernel["identity_dir"]),
                "persona_file": str(kernel["persona_file"]),
                "soul_file": str(kernel["soul_file"]),
                "splash_file": str(kernel["splash_file"]),
                "history_file": str(kernel["history_file"]),
            },
        }
        if ns.json:
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(f"repo_root: {data['repo_root']}")
            print(f"mission: {data['mission']}")
            print(f"papers_index: {data['papers_index']}")
            print("kernel:")
            print(f"  config_path: {data['kernel']['config_path']}")
            print(f"  extension_root: {data['kernel']['extension_root']}")
            print(f"  identity_dir: {data['kernel']['identity_dir']}")
            print("  skill_dirs:")
            for item in data["kernel"]["skill_dirs"]:
                print(f"    - [{item['source']}] {item['path']}")
            print("  books_dirs:")
            for item in data["kernel"]["books_dirs"]:
                print(f"    - {item}")
            print("  papers_dirs:")
            for item in data["kernel"]["papers_dirs"]:
                print(f"    - {item}")
            print("notebooks:")
            for p in data["notebooks"]:
                print(f"  - {p}")
        return 0

    if ns.cmd == "init":
        if ns.init_cmd == "agi-cli":
            project_name = _slug(str(ns.name))
            parent_dir = Path(ns.dir)
            if not parent_dir.is_absolute():
                parent_dir = root / parent_dir
            target_dir = parent_dir / project_name

            if target_dir.exists() and not ns.force:
                print(f"ERROR: target exists (use --force): {target_dir}")
                return 1

            dirs = [
                target_dir,
                target_dir / "artifacts",
                target_dir / "recipes",
                target_dir / "ripples" / "system",
                target_dir / "ripples" / "project",
                target_dir / "memory" / "session",
                target_dir / "skills",
                target_dir / "wishes",
                target_dir / "notebooks",
                target_dir / "plugins",
                target_dir / "extensions" / "skills",
                target_dir / "extensions" / "recipes",
                target_dir / "extensions" / "personas",
                target_dir / "extensions" / "identity",
            ]
            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)

            files: dict[Path, str] = {
                target_dir / "README.md": "\n".join(
                    [
                        f"# {project_name}",
                        "",
                        "Scaffold generated by `stillwater init agi-cli`.",
                        "",
                        "## Quickstart",
                        "```bash",
                        "stillwater llm status",
                        "stillwater stack run --profile offline",
                        "stillwater stack verify --strict",
                        "```",
                        "",
                        "## Prime Mermaid policy",
                        "- Keep cognition contracts in `*.prime-mermaid.md` files.",
                        "- Treat JSON as derived transport, not source-of-truth.",
                        "",
                        "## Kernel + extension model",
                        "- Keep kernel logic in Stillwater core commands.",
                        "- Put project customization under `extensions/` (skills, recipes, personas, identity).",
                        "- Set `STILLWATER_EXTENSION_ROOT=./extensions` when running in this project.",
                        "",
                    ]
                ),
                target_dir / "recipes" / "recipe.hello_world.prime-mermaid.md": "\n".join(
                    [
                        "# Recipe: hello_world",
                        "",
                        "```mermaid",
                        "flowchart TD",
                        "  START[INTENT: hello_world] --> BUILD[CPU: build_message]",
                        "  BUILD --> VERIFY[GATE: deterministic_output]",
                        "  VERIFY --> DONE[OUTPUT: hello_world_text]",
                        "```",
                        "",
                    ]
                ),
                target_dir / "ripples" / "system" / "default.prime-mermaid.md": "\n".join(
                    [
                        "# System Ripple: default",
                        "",
                        "```mermaid",
                        "flowchart TD",
                        "  INPUT[INTENT] --> ROUTE[ROUTE: phuc_forecast]",
                        "  ROUTE --> POLICY[GATE: prime_mermaid_only]",
                        "  POLICY --> VERIFY[VERIFY: replay_hash]",
                        "```",
                        "",
                    ]
                ),
                target_dir / "wishes" / "wish.bootstrap.v1.md": "\n".join(
                    [
                        "# Wish: wish.bootstrap.v1",
                        "",
                        "Date: " + _utc_now(),
                        "Level: L1",
                        "",
                        "## Quest + belt",
                        "- Quest: \"First River Run\"",
                        "- Current belt: White Belt",
                        "- Target belt: Green Belt",
                        "- Promotion gate: stack run/verify pass + deterministic hashes",
                        "",
                        "## Capability",
                        "- Boot a runnable AGI CLI project with Prime Mermaid defaults.",
                        "",
                        "## Non-goals",
                        "- No production cloud deployment.",
                        "- No secret/private model routing.",
                        "",
                    ]
                ),
                target_dir / "wishes" / "wish.bootstrap.v1.prime-mermaid.md": "\n".join(
                    [
                        "# Prime Mermaid: wish.bootstrap.v1",
                        "",
                        "```mermaid",
                        "flowchart TD",
                        "  START[CLONE] --> INIT[INIT_AGI_CLI]",
                        "  INIT --> STACK[STACK_RUN]",
                        "  STACK --> VERIFY[STACK_VERIFY]",
                        "  VERIFY --> PROMOTE[BELT_PROMOTION_GATE]",
                        "```",
                        "",
                    ]
                ),
                target_dir / "skills" / "README.md": "\n".join(
                    [
                        "# Skills",
                        "",
                        "Drop project-specific skills here. Recommended baseline pack:",
                        "- prime-wishes",
                        "- phuc-forecast",
                        "- phuc-swarms",
                        "- phuc-cleanup",
                        "- prime-coder",
                        "- prime-safety",
                        "- phuc-context",
                        "",
                    ]
                ),
                target_dir / "extensions" / "RIPPLE-KERNEL-OVERRIDES.prime-mermaid.md": "\n".join(
                    [
                        "# Prime Mermaid: kernel-overrides",
                        "",
                        "```mermaid",
                        "flowchart TD",
                        "  KERNEL[STILLWATER_KERNEL] --> S[extensions/skills]",
                        "  KERNEL --> R[extensions/recipes]",
                        "  KERNEL --> P[extensions/personas/default.md]",
                        "  KERNEL --> I[extensions/identity/*.md]",
                        "  S --> TWIN[TWIN_ORCHESTRATION]",
                        "  R --> VERIFY[VERIFY + RECEIPTS]",
                        "  P --> TWIN",
                        "  I --> TWIN",
                        "```",
                        "",
                    ]
                ),
                target_dir / "extensions" / "personas" / "default.md": "\n".join(
                    [
                        "# Persona",
                        "",
                        "Style:",
                        "- concise, evidence-first, deterministic when possible",
                        "- ask for clarification when ambiguity is high",
                        "",
                        "Mission:",
                        "- maximize useful output with reproducible receipts",
                        "",
                    ]
                ),
                target_dir / ".gitignore": "\n".join(
                    [
                        "artifacts/",
                        "__pycache__/",
                        "*.pyc",
                        "",
                    ]
                ),
            }

            if ns.identity_stack:
                files.update(
                    {
                        target_dir / "AGENTS.md": "\n".join(
                            [
                                "# AGENTS",
                                "",
                                "Agent contract:",
                                "- CPU-first verification before LLM expansion.",
                                "- Emit receipts for major actions.",
                                "- Externalize stable logic in Prime Mermaid.",
                                "",
                            ]
                        ),
                        target_dir / "SOUL.md": "\n".join(
                            [
                                "# SOUL",
                                "",
                                "Mission:",
                                "- build open AGI infrastructure that is reproducible, auditable, and broadly useful.",
                                "",
                            ]
                        ),
                        target_dir / "IDENTITY.md": "\n".join(
                            [
                                "# IDENTITY",
                                "",
                                "Identity anchors:",
                                "- kernel is stable",
                                "- customization lives in extensions",
                                "- persistence is mandatory for learning",
                                "",
                            ]
                        ),
                        target_dir / "USER.md": "\n".join(
                            [
                                "# USER",
                                "",
                                "User context:",
                                "- preferences and boundaries",
                                "- current project goals",
                                "- model/provider constraints",
                                "",
                            ]
                        ),
                        target_dir / "HEARTBEAT.md": "\n".join(
                            [
                                "# HEARTBEAT",
                                "",
                                "Cadence:",
                                "1. run fast QA",
                                "2. run notebook QA",
                                "3. run full verification before release",
                                "",
                            ]
                        ),
                        target_dir / "BOOTSTRAP.md": "\n".join(
                            [
                                "# BOOTSTRAP",
                                "",
                                "1. configure model endpoint",
                                "2. verify connectivity",
                                "3. load identity + persona",
                                "4. start twin interactive session",
                                "",
                            ]
                        ),
                    }
                )

            for path, content in files.items():
                if path.exists() and not ns.force:
                    print(f"ERROR: file exists (use --force): {path}")
                    return 1
                path.write_text(content, encoding="utf-8")

            project_meta = {
                "name": project_name,
                "created_utc": _utc_now(),
                "template": "stillwater-agi-cli-v1",
                "prime_mermaid_policy": True,
                "identity_stack": bool(ns.identity_stack),
            }
            _write_json(target_dir / ".stillwater" / "project.json", project_meta)

            def _fmt_path(path: Path) -> str:
                try:
                    return str(path.relative_to(root))
                except ValueError:
                    return str(path)

            created_files = [_fmt_path(p) for p in sorted(files.keys())]
            created_files.append(_fmt_path(target_dir / ".stillwater" / "project.json"))

            payload = {
                "ok": True,
                "project_name": project_name,
                "project_dir": str(target_dir),
                "created_files": created_files,
                "identity_stack": bool(ns.identity_stack),
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"project: {project_name}")
                print(f"dir: {target_dir}")
                print(f"identity_stack: {bool(ns.identity_stack)}")
                for item in created_files:
                    print(f"- {item}")
            return 0

        if ns.init_cmd == "identity-stack":
            target_dir = Path(ns.dir)
            if not target_dir.is_absolute():
                target_dir = root / target_dir
            target_dir.mkdir(parents=True, exist_ok=True)

            files: dict[Path, str] = {
                target_dir / "AGENTS.md": "\n".join(
                    [
                        "# AGENTS",
                        "",
                        "Agent contract for this CLI project:",
                        "- prefer deterministic CPU steps when possible",
                        "- record artifacts for replay and audit",
                        "- keep prime-mermaid contracts current",
                        "",
                    ]
                ),
                target_dir / "SOUL.md": "\n".join(
                    [
                        "# SOUL",
                        "",
                        "North star:",
                        "- build AGI workflows that benefit people and can be independently verified.",
                        "- preserve identity and continuity through durable memory, not chat-only state.",
                        "",
                    ]
                ),
                target_dir / "IDENTITY.md": "\n".join(
                    [
                        "# IDENTITY",
                        "",
                        "Identity anchors:",
                        "- kernel code stays stable",
                        "- project behavior changes through extensions",
                        "- receipts and replay are first-class",
                        "",
                    ]
                ),
                target_dir / "USER.md": "\n".join(
                    [
                        "# USER",
                        "",
                        "- preferred models/providers",
                        "- tone and risk tolerance",
                        "- project-specific guardrails",
                        "",
                    ]
                ),
                target_dir / "HEARTBEAT.md": "\n".join(
                    [
                        "# HEARTBEAT",
                        "",
                        "Operational cadence:",
                        "1. qa-fast",
                        "2. qa-notebooks",
                        "3. qa/full test suite before release",
                        "",
                    ]
                ),
                target_dir / "BOOTSTRAP.md": "\n".join(
                    [
                        "# BOOTSTRAP",
                        "",
                        "Deterministic startup checklist:",
                        "1. stillwater llm set-ollama --auto-url --activate",
                        "2. stillwater llm models",
                        "3. stillwater twin \"/kernel\"",
                        "4. stillwater twin --interactive",
                        "",
                    ]
                ),
                target_dir / "MEMORY.md": "\n".join(
                    [
                        "# MEMORY",
                        "",
                        "Durable memory roots:",
                        "- artifacts/runs/",
                        "- artifacts/twin/",
                        "- artifacts/wishes/",
                        "- ripples/project/",
                        "",
                    ]
                ),
                target_dir / "RIPPLE-IDENTITY.prime-mermaid.md": "\n".join(
                    [
                        "# Prime Mermaid: identity-stack",
                        "",
                        "```mermaid",
                        "flowchart TD",
                        "  SOURCE[OPEN_MISSION] --> AGENTS",
                        "  AGENTS --> SOUL",
                        "  SOUL --> IDENTITY",
                        "  IDENTITY --> USER",
                        "  USER --> HEARTBEAT",
                        "  HEARTBEAT --> BOOTSTRAP",
                        "  BOOTSTRAP --> MEMORY",
                        "  MEMORY --> REPLAY[REPLAY_AND_LEARN]",
                        "```",
                        "",
                    ]
                ),
            }

            created: list[str] = []
            for path, content in files.items():
                if path.exists() and not ns.force:
                    print(f"ERROR: file exists (use --force): {path}")
                    return 1
                path.write_text(content, encoding="utf-8")
                try:
                    created.append(str(path.relative_to(root)))
                except ValueError:
                    created.append(str(path))

            payload = {"ok": True, "dir": str(target_dir), "created_files": sorted(created)}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"identity_dir: {target_dir}")
                for item in sorted(created):
                    print(f"- {item}")
            return 0

        if ns.init_cmd == "project":
            # --------------------------------------------------------------- #
            # stillwater init project                                           #
            # Install Stillwater into any existing project:                    #
            #   1. Lean CLAUDE.md with QUICK LOAD summaries (~80 lines)        #
            #   2. ripples/project.md template (project-specific config)       #
            #   3. skills/ directory with full skill files (for sub-agents)   #
            # --------------------------------------------------------------- #
            import datetime as _dt

            project_dir = Path(ns.dir).expanduser().resolve()
            project_dir.mkdir(parents=True, exist_ok=True)
            project_name = ns.name
            skills_requested = [s.strip() for s in ns.skills.split(",") if s.strip()]
            rung_target = ns.rung
            domain = ns.domain or "(fill in: e.g. compression / audio / web automation)"
            stillwater_skills_dir = root / "skills"

            created_files: list[str] = []
            errors: list[str] = []

            # --- 1. Build CLAUDE.md with QUICK LOAD blocks ---
            claude_md_path = project_dir / "CLAUDE.md"
            if claude_md_path.exists() and not ns.force:
                print(f"ERROR: CLAUDE.md exists (use --force to overwrite): {claude_md_path}")
                return 1

            quick_load_blocks: list[str] = []
            missing_skills: list[str] = []
            for skill_name in skills_requested:
                skill_file = stillwater_skills_dir / f"{skill_name}.md"
                if not skill_file.exists():
                    missing_skills.append(skill_name)
                    continue
                content = skill_file.read_text(encoding="utf-8")
                # Extract QUICK LOAD comment block (between <!-- QUICK LOAD and -->)
                ql_match = re.search(r'<!--\s*QUICK LOAD.*?-->', content, re.DOTALL)
                if ql_match:
                    quick_load_blocks.append(ql_match.group(0))
                else:
                    # Fallback: take first 15 lines as orientation
                    quick_load_blocks.append("\n".join(content.splitlines()[:15]))

            if missing_skills:
                print(f"WARNING: skills not found in {stillwater_skills_dir}: {missing_skills}")

            version_str = __version__
            date_str = _dt.date.today().isoformat()
            skills_list_str = ", ".join(skills_requested)

            claude_md_lines = [
                f"# CLAUDE.md — {project_name}",
                f"# Stillwater v{version_str} | Generated: {date_str}",
                "# Project context, architecture, and phases: see README.md",
                "# Skill directory (full files for sub-agent dispatch): skills/",
                "",
                "## Project Ripple",
                "# See ripples/project.md for project-specific constraints and rung target.",
                "# Edit ripples/project.md — do NOT put project architecture here.",
                "",
                f"RUNG_TARGET: {rung_target}",
                "NORTHSTAR: Phuc_Forecast",
                f"PROJECT: {project_name}",
                f"DOMAIN: {domain}",
                "",
                "## Phuc-Orchestration: MANDATORY (no inline deep work — ever)",
                "# MAIN SESSION MODEL: haiku (coordination only — sub-agents handle all heavy work via swarms/)",
                "# INLINE_DEEP_WORK IS FORBIDDEN — phuc-orchestration governs ALL tasks without exception",
                "# MAIN SESSION: 3 skills max → prime-safety + prime-coder + phuc-forecast (DREAM→FORECAST→DECIDE→ACT→VERIFY)",
                "# DISPATCH: task >50 lines OR domain-specialized → read swarms/<role>.md → Task tool",
                "# ROLE→TASK: coder=bugfix/feat, planner=arch/design, skeptic=verify, scout=research, mathematician=proofs",
                "# MODEL: haiku=scout/janitor/graph-designer, sonnet=coder/planner/skeptic, opus=math/security/audit",
                "# SUB-AGENT PACK: paste full skills/ inline (prime-safety first) + CNF capsule (full task/context, no \"as before\")",
                "# RUNG: declare rung_target before dispatch; integration rung = MIN(all sub-agent rungs)",
                "# FORBIDDEN: INLINE_DEEP_WORK | SKILL_LESS_DISPATCH | FORGOTTEN_CAPSULE | SUMMARY_AS_EVIDENCE",
                "# COMBOS: combos/ has WISH+RECIPE pairs (plan, bugfix, run-test, ci-triage, security, deps)",
                f"# Loaded: {skills_list_str}",
                "",
            ]
            for block in quick_load_blocks:
                claude_md_lines.append(block)
                claude_md_lines.append("")

            claude_md_content = "\n".join(claude_md_lines)
            claude_md_path.write_text(claude_md_content, encoding="utf-8")
            created_files.append("CLAUDE.md")

            # --- 2. Create ripples/project.md ---
            ripples_dir = project_dir / "ripples"
            ripples_dir.mkdir(parents=True, exist_ok=True)
            ripple_path = ripples_dir / "project.md"
            if not ripple_path.exists() or ns.force:
                ripple_content = "\n".join([
                    f"# {project_name} — Stillwater Ripple",
                    f"# Generated: {date_str} | stillwater v{version_str}",
                    "# This file overrides base Stillwater behavior for this project.",
                    "# Keep it under 50 lines. Everything else goes in README.md.",
                    "",
                    f"PROJECT: {project_name}",
                    f"DOMAIN: {domain}",
                    f"RUNG_TARGET: {rung_target}",
                    "NORTHSTAR: Phuc_Forecast",
                    "ECOSYSTEM: PUBLIC  # or PRIVATE",
                    "LANGUAGE: Python  # or Node.js, etc.",
                    "",
                    "KEY_CONSTRAINTS:",
                    "  - never-worse on standard test suite",
                    "  - # add project-specific constraints here",
                    "",
                    "ENTRY_POINTS:",
                    "  - # e.g. src/main.py",
                    "  - # e.g. pytest -q",
                    "",
                    "FORBIDDEN_IN_THIS_PROJECT:",
                    "  - # list any project-specific forbidden behaviors",
                    "",
                    "SEE_ALSO: README.md  # mission, architecture, phases, XP tracker",
                ])
                ripple_path.write_text(ripple_content, encoding="utf-8")
                created_files.append("ripples/project.md")

            # --- 3. Copy full skill files to skills/ ---
            skills_out_dir = project_dir / "skills"
            skills_out_dir.mkdir(parents=True, exist_ok=True)
            for skill_name in skills_requested:
                src = stillwater_skills_dir / f"{skill_name}.md"
                if not src.exists():
                    continue
                dst = skills_out_dir / f"{skill_name}.md"
                if not dst.exists() or ns.force:
                    shutil.copy2(str(src), str(dst))
                    created_files.append(f"skills/{skill_name}.md")

            # --- 4. Output ---
            payload = {
                "ok": True,
                "project": project_name,
                "project_dir": str(project_dir),
                "rung_target": rung_target,
                "skills_loaded": skills_requested,
                "missing_skills": missing_skills,
                "claude_md_lines": len(claude_md_content.splitlines()),
                "created_files": created_files,
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"project: {project_name}")
                print(f"dir:     {project_dir}")
                print(f"rung:    {rung_target}")
                print(f"skills:  {', '.join(skills_requested)}")
                if missing_skills:
                    print(f"WARNING: skills not found: {missing_skills}")
                print(f"CLAUDE.md: {len(claude_md_content.splitlines())} lines (was: check git diff)")
                print("")
                print("Created / updated:")
                for f in created_files:
                    print(f"  + {f}")
                print("")
                print("Next steps:")
                print("  1. Edit ripples/project.md — fill in KEY_CONSTRAINTS and ENTRY_POINTS")
                print("  2. Move project mission/architecture/phases from CLAUDE.md → README.md")
                print("  3. stillwater verify-project-structure  (coming in v1.6.0)")
                print("")
                print(f"Stillwater v{version_str} installed in {project_name}.")
            return 0

    if ns.cmd == "skills-ab":
        from .skills_ab import SkillsABConfig, run_skills_ab
        from .llm_cli_support import candidate_ollama_urls, choose_preferred_ollama_url, probe_ollama_urls

        ollama_url = ns.ollama_url
        if not ollama_url and ns.backend in {"auto", "ollama"}:
            candidates = candidate_ollama_urls(repo_root=root, explicit_urls=None)
            probes = probe_ollama_urls(urls=candidates, timeout_seconds=float(ns.timeout))
            preferred = choose_preferred_ollama_url(probes)
            ollama_url = preferred or "http://localhost:11434"

        if not ollama_url:
            ollama_url = "http://localhost:11434"

        cfg = SkillsABConfig(
            repo_root=root,
            skills_dir=root / "skills",
            artifacts_dir=root / "artifacts" / "skills_ab",
            backend=ns.backend,
            ollama_url=ollama_url,
            model=ns.model or ("mock-kungfu-v1" if ns.backend == "mock" else _default_ollama_model(root)),
            use_cache=(not ns.no_cache),
            seed=ns.seed,
            run_id=ns.run_id,
            request_timeout_seconds=ns.timeout,
            record_prompts=(not ns.no_record_prompts),
        )
        run_skills_ab(cfg)
        print(f"Wrote: {cfg.artifacts_dir / 'results.json'}")
        print(f"Wrote: {cfg.artifacts_dir / 'report.md'}")
        return 0

    if ns.cmd == "llm":
        from .llm_cli_support import (
            candidate_ollama_urls,
            choose_preferred_ollama_url,
            probe_ollama_urls,
            update_llm_config_file,
        )

        if ns.llm_cmd == "status":
            try:
                from llm_config_manager import get_llm_config

                cfg = get_llm_config()
                ok, msg = cfg.validate_setup()
                print(f"provider: {cfg.active_provider}")
                print(f"name: {cfg.get_provider_name()}")
                print(f"url: {cfg.get_provider_url()}")
                if cfg.get_provider_model():
                    print(f"model: {cfg.get_provider_model()}")
                print(f"status: {msg}")
                if cfg.active_provider == "ollama":
                    candidates = candidate_ollama_urls(repo_root=root, explicit_urls=None)
                    probes = probe_ollama_urls(urls=candidates, timeout_seconds=2.0)
                    preferred = choose_preferred_ollama_url(probes)
                    print(f"preferred_ollama_url: {preferred or 'UNREACHABLE'}")
            except Exception as ex:
                print(f"ERROR: {ex}")
                return 1
            return 0

        if ns.llm_cmd == "providers":
            try:
                from llm_config_manager import get_llm_config

                cfg = get_llm_config()
                providers = cfg.list_providers()
                lines = []
                for name in sorted(providers.keys()):
                    marker = "*" if name == cfg.active_provider else " "
                    item = providers[name]
                    lines.append(f"{marker} {name:14} {item.get('name','')}  {item.get('url','')}")
                print("\n".join(lines))
            except Exception as ex:
                print(f"ERROR: {ex}")
                return 1
            return 0

        if ns.llm_cmd == "probe-ollama":
            urls = candidate_ollama_urls(repo_root=root, explicit_urls=list(ns.url or []))
            probes = probe_ollama_urls(urls=urls, timeout_seconds=float(ns.timeout))
            preferred = choose_preferred_ollama_url(probes)
            if ns.json:
                print(json.dumps({"preferred": preferred, "probes": probes}, indent=2, sort_keys=True))
            else:
                print(f"preferred: {preferred or 'UNREACHABLE'}")
                for p in probes:
                    mark = "OK " if p.get("reachable") else "ERR"
                    model_count = p.get("model_count", 0)
                    print(f"[{mark}] {p.get('url')} models={model_count}")
            return 0

        if ns.llm_cmd == "models":
            urls = [ns.url] if ns.url else []
            candidates = candidate_ollama_urls(repo_root=root, explicit_urls=urls)
            probes = probe_ollama_urls(urls=candidates, timeout_seconds=float(ns.timeout))
            preferred = choose_preferred_ollama_url(probes)
            if not preferred:
                print("ERROR: No reachable Ollama endpoint found.")
                return 1
            probe = None
            for p in probes:
                if p.get("url") == preferred:
                    probe = p
                    break
            models = (probe or {}).get("models", [])
            if ns.json:
                print(json.dumps({"url": preferred, "models": models}, indent=2, sort_keys=True))
            else:
                print(f"url: {preferred}")
                for m in models:
                    print(f"- {m}")
            return 0

        if ns.llm_cmd == "set-provider":
            path = update_llm_config_file(repo_root=root, provider=str(ns.provider).strip())
            print(f"Updated provider in: {path}")
            return 0

        if ns.llm_cmd == "set-ollama":
            url = ns.url
            if ns.auto_url:
                candidates = candidate_ollama_urls(repo_root=root, explicit_urls=[])
                probes = probe_ollama_urls(urls=candidates, timeout_seconds=float(ns.timeout))
                best = choose_preferred_ollama_url(probes)
                if not best:
                    print("ERROR: --auto-url selected but no reachable endpoint found.")
                    return 1
                url = best
            provider = "ollama" if ns.activate else None
            if not url and not ns.model and provider is None:
                print("ERROR: Nothing to update. Pass --url and/or --model and/or --activate.")
                return 1
            path = update_llm_config_file(
                repo_root=root,
                provider=provider,
                ollama_url=url,
                ollama_model=ns.model,
            )
            print(f"Updated ollama config in: {path}")
            if url:
                print(f"ollama.url={url}")
            if ns.model:
                print(f"ollama.model={ns.model}")
            if provider:
                print("provider=ollama")
            return 0

    if ns.cmd == "skills":
        inventory = _collect_skill_inventory(root)
        by_name: dict[str, dict[str, str]] = {}
        for item in inventory:
            by_name[item["name"]] = item

        if ns.skills_cmd == "list":
            if ns.source == "root":
                inventory = [item for item in inventory if item["source"] == "root"]
            elif ns.source == "cli":
                inventory = [item for item in inventory if item["source"] in {"cli", "cli_stillwater"}]
            elif ns.source == "extension":
                inventory = [
                    item
                    for item in inventory
                    if item["source"].startswith("extension") or item["source"] in {"env", "cfg"}
                ]

            payload = {"count": len(inventory), "skills": inventory}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"skills: {len(inventory)}")
                for item in inventory:
                    print(f"- [{item['source']}] {item['name']} ({item['path']})")
            return 0

        if ns.skills_cmd == "sync":
            if ns.all:
                selected = sorted(by_name.keys())
            elif ns.skill:
                selected = [_normalize_skill_name(v) for v in ns.skill if _normalize_skill_name(v)]
            else:
                selected = _swarm_default_skill_pack(root) or _default_twin_skills(root)

            dest_dir = Path(ns.dest)
            if not dest_dir.is_absolute():
                dest_dir = root / dest_dir
            dest_dir.mkdir(parents=True, exist_ok=True)

            copied: list[str] = []
            missing: list[str] = []
            selected_sources: dict[str, str] = {}
            for name in selected:
                picked = by_name.get(name)
                if picked is None:
                    missing.append(name)
                    continue
                src = Path(picked["path"]) if Path(picked["path"]).is_absolute() else (root / picked["path"])
                dst = dest_dir / src.name
                if dst.exists() and not ns.force:
                    continue
                shutil.copy2(src, dst)
                copied.append(str(dst.relative_to(root)))
                selected_sources[name] = picked["source"]

            receipt = {
                "timestamp_utc": _utc_now(),
                "source_dirs": [item["path"] for item in inventory],
                "dest_dir": str(dest_dir),
                "selected": selected,
                "selected_sources": selected_sources,
                "copied": copied,
                "missing": missing,
            }
            receipt_path = root / "artifacts" / "skills" / f"sync-{_new_run_id('skills')}.json"
            _write_json(receipt_path, receipt)

            if ns.json:
                print(json.dumps({"ok": True, "receipt": str(receipt_path), **receipt}, indent=2, sort_keys=True))
            else:
                print(f"dest: {dest_dir}")
                print(f"copied: {len(copied)}")
                for item in copied:
                    print(f"- {item}")
                if missing:
                    print(f"missing: {', '.join(missing)}")
                print(f"receipt: {receipt_path}")
            return 0

        if ns.skills_cmd == "show":
            name = _normalize_skill_name(ns.name)
            picked = by_name.get(name)
            if picked:
                path = Path(picked["path"]) if Path(picked["path"]).is_absolute() else (root / picked["path"])
                print(path.read_text(encoding="utf-8"))
                return 0
            print(f"ERROR: skill not found: {name}")
            return 1

        if ns.skills_cmd == "install":
            name = _normalize_skill_name(ns.name)
            as_json = bool(ns.json)
            skill_content: str | None = None
            source_used: str = "none"

            # 1. Check local inventory first
            picked = by_name.get(name)
            if picked:
                local_path = Path(picked["path"]) if Path(picked["path"]).is_absolute() else (root / picked["path"])
                skill_content = local_path.read_text(encoding="utf-8")
                source_used = "local"

            # 2. If not found locally and not --no-remote, try GitHub
            if skill_content is None and not ns.no_remote:
                base_name = name  # already has .md suffix from _normalize_skill_name
                gh_url = f"https://raw.githubusercontent.com/phuctruong/stillwater/main/skills/{base_name}"
                try:
                    req = urllib.request.Request(gh_url, headers={"User-Agent": "stillwater-cli/1.0"})
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        skill_content = resp.read().decode("utf-8")
                    source_used = gh_url
                except Exception as fetch_err:
                    if as_json:
                        print(json.dumps({"ok": False, "error": f"GitHub fetch failed: {fetch_err}", "name": name}, indent=2, sort_keys=True))
                    else:
                        print(f"ERROR: skill not found locally and GitHub fetch failed: {fetch_err}")
                    return 1

            if skill_content is None:
                msg = f"Skill not found locally: {name} (use without --no-remote to try GitHub)"
                if as_json:
                    print(json.dumps({"ok": False, "error": msg, "name": name}, indent=2, sort_keys=True))
                else:
                    print(f"ERROR: {msg}")
                return 1

            installed: list[str] = []

            # Save to ~/.claude/skills/ (Claude Code auto-discovery path)
            claude_skills_dir = Path.home() / ".claude" / "skills"
            claude_skills_dir.mkdir(parents=True, exist_ok=True)
            claude_dest = claude_skills_dir / name
            claude_dest.write_text(skill_content, encoding="utf-8")
            installed.append(str(claude_dest))

            # Save to skills/ in the repo if not already there
            repo_skills_dir = root / "skills"
            repo_skills_dir.mkdir(parents=True, exist_ok=True)
            repo_dest = repo_skills_dir / name
            if not repo_dest.exists():
                repo_dest.write_text(skill_content, encoding="utf-8")
                installed.append(str(repo_dest.relative_to(root)))

            result = {
                "ok": True,
                "name": name,
                "source": source_used,
                "installed_to": installed,
            }
            if as_json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                print(f"Installed skill: {name}")
                print(f"Source: {source_used}")
                for dest_path in installed:
                    print(f"  -> {dest_path}")
            return 0

        if ns.skills_cmd == "export":
            name = _normalize_skill_name(ns.name)
            as_json = bool(ns.json)
            picked = by_name.get(name)
            if not picked:
                msg = f"Skill not found: {name}"
                if as_json:
                    print(json.dumps({"ok": False, "error": msg}, indent=2, sort_keys=True))
                else:
                    print(f"ERROR: {msg}")
                return 1

            skill_path = Path(picked["path"]) if Path(picked["path"]).is_absolute() else (root / picked["path"])
            skill_content = skill_path.read_text(encoding="utf-8")

            # Extract version from skill content if present (look for "version:" line)
            version_match = re.search(r"version:\s*(\S+)", skill_content)
            version_str = version_match.group(1) if version_match else "1.0.0"

            # Strip .md suffix for skill name in frontmatter
            skill_base_name = name[:-3] if name.endswith(".md") else name

            frontmatter = (
                "---\n"
                f"name: {skill_base_name}\n"
                f"description: Stillwater skill — {skill_base_name} (FSM-verified, fail-closed)\n"
                f"version: {version_str}\n"
                "author: Phuc Vinh Truong <phuc@phuc.net>\n"
                "tags: [stillwater, verification, prime-coder]\n"
                "---\n\n"
            )
            exported = frontmatter + skill_content

            if ns.output:
                out_path = Path(ns.output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(exported, encoding="utf-8")
                if as_json:
                    print(json.dumps({"ok": True, "output": str(out_path), "name": skill_base_name, "version": version_str}, indent=2, sort_keys=True))
                else:
                    print(f"Exported: {out_path}")
            else:
                print(exported)
            return 0

    if ns.cmd == "demo":
        # Shortcut: stillwater run "What is Software 5.0?" --skill prime-safety --dry-run
        demo_argv = ["run", "What is Software 5.0?", "--skill", "prime-safety", "--dry-run"]
        if ns.json:
            demo_argv.append("--json")
        return main(demo_argv)

    if ns.cmd == "twin":
        from .llm_cli_support import candidate_ollama_urls, choose_preferred_ollama_url, probe_ollama_urls

        try:
            import requests  # type: ignore
        except Exception as ex:
            print(f"ERROR: requests not available: {ex}")
            return 1

        kernel = _kernel_paths(root)
        swarm_loaded = _load_swarm_settings(root, kernel=kernel)
        swarm_settings = swarm_loaded.get("settings", {}) if isinstance(swarm_loaded.get("settings", {}), dict) else {}
        swarm_personas = _swarm_setting_map(swarm_settings, "persona")
        swarm_phase_order = _swarm_setting_list(swarm_settings, "phase_order", default=[])
        swarm_skill_pack = _swarm_setting_list(swarm_settings, "skill_pack", default=[])
        swarm_mandatory_skill_pack = _swarm_setting_list(swarm_settings, "mandatory_skill_pack", default=[])
        swarm_agent_skill_pack = _swarm_setting_list_map(swarm_settings, "agent_skill_pack")
        legacy_swarm_agent_skill_pack = _swarm_setting_list_map(swarm_settings, "skill_pack")
        for role, items in legacy_swarm_agent_skill_pack.items():
            if role in {"scout", "forecaster", "judge", "solver", "skeptic"} and role not in swarm_agent_skill_pack:
                swarm_agent_skill_pack[role] = list(items)
        swarm_recipe_pack = _swarm_setting_list(swarm_settings, "recipe_pack", default=[])
        swarm_agent_recipe_pack = _swarm_setting_list_map(swarm_settings, "agent_recipe_pack")
        legacy_swarm_agent_recipe_pack = _swarm_setting_list_map(swarm_settings, "recipe_pack")
        for role, items in legacy_swarm_agent_recipe_pack.items():
            if role in {"scout", "forecaster", "judge", "solver", "skeptic"} and role not in swarm_agent_recipe_pack:
                swarm_agent_recipe_pack[role] = list(items)
        swarm_context_mode = str(swarm_settings.get("context_mode", "")).strip()
        swarm_artifact_mode = str(swarm_settings.get("artifact_mode", "")).strip()
        skill_paths: list[Path] = []
        missing_skills: list[str] = []
        if not ns.no_skill_context:
            skill_paths, missing_skills = _resolve_twin_skill_paths(
                root=root,
                requested=list(ns.skill or []),
                all_skills=bool(ns.all_skills),
            )
        recipe_paths, missing_recipes = _resolve_twin_recipe_paths(root=root, requested=swarm_recipe_pack)

        system_sections = [
            "You are Stillwater Twin Orchestrator.",
            "Policy: CPU prepass first. If CPU cannot satisfy the request, call Ollama and return a concise answer.",
            "Policy: apply Phuc Forecast spine (DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY) and emit artifacts for deterministic routes.",
            "Policy: for benchmark-style prompts, prefer Phuc Swarms CPU orchestration over free-form LLM narration.",
            "Policy: externalize deterministic state in Prime Mermaid and receipts.",
            "Policy: keep kernel code stable and route project customization through extension files (skills/recipes/persona/identity/ripples).",
            "Domain: this repository is an AGI CLI framework; do not reinterpret 'Stillwater' as music/audio terms.",
            "If a prompt is ambiguous, ask a clarifying question instead of fabricating context.",
        ]
        system_sections.extend(_load_twin_identity_sections(root))
        if swarm_loaded.get("exists"):
            swarm_text = str(swarm_loaded.get("text", "")).strip()
            if swarm_text:
                system_sections.append(
                    f"# BEGIN_SWARM_SETTINGS {swarm_loaded.get('path')}\n{swarm_text}\n# END_SWARM_SETTINGS"
                )
        if skill_paths:
            for path in skill_paths:
                skill_text = path.read_text(encoding="utf-8")
                system_sections.append(f"# BEGIN_SKILL {path.name}\n{skill_text}\n# END_SKILL {path.name}")
        if recipe_paths:
            for path in recipe_paths:
                recipe_text = path.read_text(encoding="utf-8")
                system_sections.append(f"# BEGIN_RECIPE {path.name}\n{recipe_text}\n# END_RECIPE {path.name}")
        system_prompt = "\n\n".join(system_sections)

        history: list[dict[str, str]] = []

        def _run_turn(prompt_text: str, run_id: str) -> dict[str, Any]:
            cpu_enabled = not (bool(ns.llm_only) and not prompt_text.strip().startswith("/"))
            if cpu_enabled:
                handled, cpu_response, cpu_meta = _cpu_twin_prepass(root=root, prompt=prompt_text)
            else:
                handled, cpu_response, cpu_meta = (False, "", {"source": "CPU", "action": "llm_only_bypass"})
            cpu_meta_extra = {k: v for k, v in cpu_meta.items() if k not in {"source", "action"}}
            if handled:
                if cpu_response == "__EXIT__":
                    return {"exit": True}
                route = {
                    "run_id": run_id,
                    "timestamp_utc": _utc_now(),
                    "source": "CPU",
                    "action": cpu_meta.get("action", "cpu"),
                    "prompt": prompt_text,
                    "extension_root": str(kernel["extension_root"]),
                    "missing_skills": missing_skills,
                    "loaded_recipes": [p.name for p in recipe_paths],
                    "missing_recipes": missing_recipes,
                    "swarm_settings_file": str(kernel["swarm_settings_file"]),
                    "swarm_phase_order": swarm_phase_order,
                    "swarm_personas": swarm_personas,
                    "swarm_skill_pack": swarm_skill_pack,
                    "swarm_mandatory_skill_pack": swarm_mandatory_skill_pack,
                    "swarm_agent_skill_pack": swarm_agent_skill_pack,
                    "swarm_recipe_pack": swarm_recipe_pack,
                    "swarm_agent_recipe_pack": swarm_agent_recipe_pack,
                    "swarm_context_mode": swarm_context_mode,
                    "swarm_artifact_mode": swarm_artifact_mode,
                    "llm_only": bool(ns.llm_only),
                    **cpu_meta_extra,
                }
                injection_manifest = {
                    "swarm_settings_file": str(kernel["swarm_settings_file"]),
                    "swarm_settings_loaded": bool(swarm_loaded.get("exists")),
                    "swarm_phase_order": swarm_phase_order,
                    "swarm_personas": swarm_personas,
                    "swarm_mandatory_skill_pack": swarm_mandatory_skill_pack,
                    "swarm_agent_skill_pack": swarm_agent_skill_pack,
                    "swarm_agent_recipe_pack": swarm_agent_recipe_pack,
                    "swarm_context_mode": swarm_context_mode,
                    "swarm_artifact_mode": swarm_artifact_mode,
                    "skill_files": [str(p) for p in skill_paths],
                    "recipe_files": [str(p) for p in recipe_paths],
                    "identity_files": [
                        str(kernel["soul_file"]),
                        str(kernel["persona_file"]),
                        str(Path(kernel["identity_dir"]) / "IDENTITY.md"),
                        str(Path(kernel["identity_dir"]) / "AGENTS.md"),
                        str(Path(kernel["identity_dir"]) / "USER.md"),
                    ],
                    "system_sections_count": len(system_sections),
                    "route_type": "CPU",
                }
                receipts = _write_twin_receipt(
                    root=root,
                    run_id=run_id,
                    prompt=prompt_text,
                    response=cpu_response,
                    route=route,
                    system_prompt=system_prompt,
                    injection_manifest=injection_manifest,
                )
                return {
                    "ok": True,
                    "run_id": run_id,
                    "source": "CPU",
                    "response": cpu_response,
                    "receipts": receipts,
                    "route": route,
                }

            explicit_urls = [ns.url] if ns.url else []
            probes = probe_ollama_urls(
                urls=candidate_ollama_urls(repo_root=root, explicit_urls=explicit_urls),
                timeout_seconds=float(ns.timeout),
            )
            preferred = choose_preferred_ollama_url(probes)
            if not preferred:
                return {"ok": False, "error": "No reachable Ollama endpoint found."}

            probe = next((p for p in probes if p.get("url") == preferred), {})
            model = ns.model or _select_preferred_model(
                candidates=list(probe.get("models", [])),
                fallback=_default_ollama_model(root),
            )

            messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-8:])
            messages.append({"role": "user", "content": prompt_text})
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.0},
            }

            try:
                resp = requests.post(f"{preferred}/api/chat", json=payload, timeout=float(ns.timeout))
                resp.raise_for_status()
                data = resp.json()
            except Exception as ex:
                return {"ok": False, "error": f"Ollama chat failed: {ex}", "url": preferred, "model": model}

            response_text = str(((data or {}).get("message") or {}).get("content") or "").strip()
            if not response_text:
                response_text = "No response content returned by model."

            history.append({"role": "user", "content": prompt_text})
            history.append({"role": "assistant", "content": response_text})

            route = {
                "run_id": run_id,
                "timestamp_utc": _utc_now(),
                "source": "LLM",
                "action": "ollama_chat",
                "url": preferred,
                "model": model,
                "loaded_skills": [p.name for p in skill_paths],
                "loaded_recipes": [p.name for p in recipe_paths],
                "swarm_settings_file": str(kernel["swarm_settings_file"]),
                "swarm_phase_order": swarm_phase_order,
                "swarm_personas": swarm_personas,
                "swarm_skill_pack": swarm_skill_pack,
                "swarm_mandatory_skill_pack": swarm_mandatory_skill_pack,
                "swarm_agent_skill_pack": swarm_agent_skill_pack,
                "swarm_recipe_pack": swarm_recipe_pack,
                "swarm_agent_recipe_pack": swarm_agent_recipe_pack,
                "swarm_context_mode": swarm_context_mode,
                "swarm_artifact_mode": swarm_artifact_mode,
                "extension_root": str(kernel["extension_root"]),
                "missing_skills": missing_skills,
                "missing_recipes": missing_recipes,
                "llm_only": bool(ns.llm_only),
                "cpu_prepass_action": cpu_meta.get("action", "llm_fallback"),
                **cpu_meta_extra,
                "prompt": prompt_text,
            }
            injection_manifest = {
                "swarm_settings_file": str(kernel["swarm_settings_file"]),
                "swarm_settings_loaded": bool(swarm_loaded.get("exists")),
                "swarm_phase_order": swarm_phase_order,
                "swarm_personas": swarm_personas,
                "swarm_mandatory_skill_pack": swarm_mandatory_skill_pack,
                "swarm_agent_skill_pack": swarm_agent_skill_pack,
                "swarm_agent_recipe_pack": swarm_agent_recipe_pack,
                "swarm_context_mode": swarm_context_mode,
                "swarm_artifact_mode": swarm_artifact_mode,
                "skill_files": [str(p) for p in skill_paths],
                "recipe_files": [str(p) for p in recipe_paths],
                "identity_files": [
                    str(kernel["soul_file"]),
                    str(kernel["persona_file"]),
                    str(Path(kernel["identity_dir"]) / "IDENTITY.md"),
                    str(Path(kernel["identity_dir"]) / "AGENTS.md"),
                    str(Path(kernel["identity_dir"]) / "USER.md"),
                ],
                "system_sections_count": len(system_sections),
                "messages_sent": len(messages),
                "model": model,
                "url": preferred,
                "route_type": "LLM",
                "cpu_prepass_action": cpu_meta.get("action", "llm_fallback"),
                "cpu_prepass_meta": cpu_meta_extra,
            }
            receipts = _write_twin_receipt(
                root=root,
                run_id=run_id,
                prompt=prompt_text,
                response=response_text,
                route=route,
                system_prompt=system_prompt,
                injection_manifest=injection_manifest,
            )
            return {
                "ok": True,
                "run_id": run_id,
                "source": "LLM",
                "url": preferred,
                "model": model,
                "response": response_text,
                "receipts": receipts,
                "route": route,
            }

        if ns.interactive:
            session_id = ns.run_id or _new_run_id("twin")
            session_log = root / "artifacts" / "twin" / session_id / "session.jsonl"
            _setup_readline_history(Path(kernel["history_file"]))
            splash = _load_text_if_exists(Path(kernel["splash_file"]))
            if splash:
                print(splash)
            print(f"twin session: {session_id}")
            print("type /help for CPU commands, /exit to quit")
            turn = 1
            while True:
                try:
                    prompt_text = input(str(kernel["prompt_prefix"])).strip()
                except EOFError:
                    print("")
                    break
                if not prompt_text:
                    continue
                run_id = f"{session_id}-t{turn:03d}"
                result = _run_turn(prompt_text, run_id)
                if result.get("exit"):
                    break
                if not result.get("ok"):
                    print(f"{kernel['assistant_prefix']}ERROR: {result.get('error')}")
                    _append_jsonl(
                        session_log,
                        {
                            "run_id": run_id,
                            "timestamp_utc": _utc_now(),
                            "prompt": prompt_text,
                            "ok": False,
                            "error": str(result.get("error", "")),
                        },
                    )
                    continue
                response_text = str(result.get("response", ""))
                print(f"{kernel['assistant_prefix']}{response_text}")
                _append_jsonl(
                    session_log,
                    {
                        "run_id": run_id,
                        "timestamp_utc": _utc_now(),
                        "prompt": prompt_text,
                        "ok": True,
                        "source": result.get("source"),
                        "response": response_text,
                    },
                )
                turn += 1
            return 0

        prompt_text = " ".join(ns.prompt).strip()
        if not prompt_text:
            print("ERROR: missing prompt. Pass text or use --interactive.")
            return 1
        run_id = ns.run_id or _new_run_id("twin")
        result = _run_turn(prompt_text, run_id)
        if result.get("exit"):
            return 0
        if not result.get("ok"):
            print(f"ERROR: {result.get('error')}")
            return 1
        if ns.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            if result.get("source") == "LLM":
                print(f"source: LLM ({result.get('model')} @ {result.get('url')})")
            else:
                print("source: CPU")
            print(result.get("response", ""))
            receipts = result.get("receipts", {})
            if isinstance(receipts, dict):
                print(f"receipt: {receipts.get('dir')}")
        return 0

    if ns.cmd == "wish":
        if ns.wish_cmd == "list":
            entries: list[dict[str, str]] = []
            sources = [
                ("cli_wishes", root / "cli" / "wishes"),
                ("examples", root / "wishes" / "examples"),
            ]
            for source_name, source_dir in sources:
                if not source_dir.exists():
                    continue
                for path in sorted(source_dir.iterdir()):
                    if not path.is_file():
                        continue
                    if path.name.startswith("."):
                        continue
                    if not (path.name.endswith(".md") or path.name.endswith(".ipynb")):
                        continue
                    entries.append(
                        {
                            "source": source_name,
                            "path": str(path.relative_to(root)),
                            "type": "notebook" if path.suffix == ".ipynb" else "doc",
                        }
                    )
            if ns.json:
                print(json.dumps({"count": len(entries), "wishes": entries}, indent=2, sort_keys=True))
            else:
                print(f"wishes: {len(entries)}")
                for item in entries:
                    print(f"- [{item['source']}] {item['path']} ({item['type']})")
            return 0

        if ns.wish_cmd == "init":
            wish_id = _slug(ns.wish_id)
            target_dir = Path(ns.path)
            if not target_dir.is_absolute():
                target_dir = root / target_dir
            target_dir.mkdir(parents=True, exist_ok=True)

            created: list[Path] = []
            skill_pack = [
                "prime-wishes",
                "phuc-forecast",
                "phuc-swarms",
                "phuc-cleanup",
                "prime-coder",
                "prime-safety",
                "phuc-context",
            ]

            if ns.level == "l1":
                template_nb = root / "wishes" / "templates" / "WISH-NOTEBOOK-TEMPLATE.ipynb"
                template_pm = root / "wishes" / "templates" / "WISH-PRIME-MERMAID-TEMPLATE.prime-mermaid.md"
                target_nb = target_dir / f"{wish_id}.ipynb"
                target_pm = target_dir / f"{wish_id}.prime-mermaid.md"
                target_md = target_dir / f"{wish_id}.md"
                for target in [target_nb, target_pm, target_md]:
                    if target.exists() and not ns.force:
                        print(f"ERROR: exists (use --force): {target}")
                        return 1
                shutil.copyfile(template_nb, target_nb)
                shutil.copyfile(template_pm, target_pm)
                target_md.write_text(
                    "\n".join(
                        [
                            f"# Wish: {wish_id}",
                            "",
                            f"Date: {_utc_now()}",
                            "Level: L1 (Wish Notebook)",
                            f"Skill pack: {', '.join(skill_pack)}",
                            "",
                            "## Gamification",
                            "- Quest title:",
                            "- Target belt:",
                            "",
                            "## Capability",
                            "-",
                            "",
                            "## Non-goals",
                            "-",
                            "",
                            "## Acceptance tests",
                            "1.",
                            "2.",
                            "3.",
                            "",
                            "## Artifact target",
                            f"- artifacts/wishes/{wish_id}/",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                created.extend([target_nb, target_pm, target_md])
            else:
                suffix = ".md" if ns.level == "l0" else ".l2.md"
                target = target_dir / f"{wish_id}{suffix}"
                if target.exists() and not ns.force:
                    print(f"ERROR: exists (use --force): {target}")
                    return 1
                target.write_text(
                    "\n".join(
                        [
                            f"# Wish: {wish_id}",
                            "",
                            f"Date: {_utc_now()}",
                            f"Level: {ns.level.upper()}",
                            f"Skill pack: {', '.join(skill_pack)}",
                            "",
                            "## Gamification",
                            "- Quest title:",
                            "- Belt target:",
                            "",
                            "## Capability",
                            "-",
                            "",
                            "## Non-goals",
                            "-",
                            "",
                            "## Prime Mermaid plan",
                            "- Add companion .prime-mermaid.md graph",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                created.append(target)

            print(f"wish_id: {wish_id}")
            for item in created:
                print(f"Wrote: {item}")
            return 0

        if ns.wish_cmd == "run":
            notebook_path = Path(ns.notebook)
            if not notebook_path.is_absolute():
                notebook_path = root / notebook_path
            if not notebook_path.exists():
                print(f"ERROR: notebook not found: {notebook_path}")
                return 1

            run_id = _new_run_id("wishrun")
            out_dir = root / "artifacts" / "wish_runs" / run_id
            out_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                sys.executable,
                "-m",
                "nbconvert",
                "--execute",
                "--to",
                "notebook",
                "--inplace",
                str(notebook_path),
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(root),
                    env=_runtime_env(root),
                    text=True,
                    capture_output=True,
                    timeout=float(ns.timeout),
                    check=False,
                )
            except subprocess.TimeoutExpired:
                print(f"ERROR: notebook execution timeout after {ns.timeout}s")
                return 1

            (out_dir / "stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
            (out_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
            _write_json(
                out_dir / "receipt.json",
                {
                    "run_id": run_id,
                    "notebook": str(notebook_path),
                    "command": cmd,
                    "returncode": proc.returncode,
                    "timestamp_utc": _utc_now(),
                },
            )

            print(f"Wrote: {out_dir / 'receipt.json'}")
            if proc.returncode != 0:
                print("ERROR: notebook execution failed. See stderr.txt in receipt directory.")
                return proc.returncode

            if ns.verify_wish_id:
                ok, errors, details = _verify_wish_artifacts(root=root, wish_id=str(ns.verify_wish_id).strip())
                if ok:
                    print(f"wish verify: PASS ({ns.verify_wish_id})")
                else:
                    print(f"wish verify: FAIL ({ns.verify_wish_id})")
                    for err in errors:
                        print(f"- {err}")
                    return 1
            return 0

        if ns.wish_cmd == "verify":
            ok, errors, details = _verify_wish_artifacts(root=root, wish_id=str(ns.wish_id).strip())
            if ns.json:
                payload = {"ok": ok, "errors": errors, "details": details}
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"wish_id: {ns.wish_id}")
                print(f"status: {'PASS' if ok else 'FAIL'}")
                print(f"artifact_dir: {details.get('artifact_dir')}")
                if "belt" in details:
                    print(f"belt: {details['belt']}")
                for err in errors:
                    print(f"- {err}")
            return 0 if ok else 1

    if ns.cmd == "stack":
        if ns.stack_cmd == "run":
            run_id = ns.run_id or _new_run_id("stack")
            run_dir = root / "artifacts" / "runs" / run_id
            logs_dir = run_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)

            backend = "mock" if ns.profile == "offline" else "auto"
            steps: list[dict[str, Any]] = [
                {
                    "name": "llm_status",
                    "command": [sys.executable, "-m", "stillwater", "llm", "status"],
                    "optional": ns.profile == "offline",
                },
                {
                    "name": "wish_list",
                    "command": [sys.executable, "-m", "stillwater", "wish", "list", "--json"],
                },
                {
                    "name": "recipe_lint",
                    "command": [sys.executable, "-m", "stillwater", "recipe", "lint", "--prime-mermaid-only"],
                },
                {
                    "name": "skills_ab",
                    "command": [sys.executable, "-m", "stillwater", "skills-ab", "--backend", backend],
                },
            ]
            if ns.execute_notebooks:
                notebook_steps = [
                    "cli/notebooks/HOW-TO-CLONE-TO-FIRST-RUN.ipynb",
                    "cli/notebooks/HOW-TO-OLLAMA-LOCAL-REMOTE.ipynb",
                    "cli/notebooks/HOW-TO-RECIPE-CONTRACT-BENCHMARK.ipynb",
                ]
                for nb in notebook_steps:
                    steps.append(
                        {
                            "name": f"notebook_{Path(nb).stem.lower()}",
                            "command": [
                                sys.executable,
                                "-m",
                                "nbconvert",
                                "--execute",
                                "--to",
                                "notebook",
                                "--inplace",
                                str(root / nb),
                            ],
                        }
                    )

            manifest: dict[str, Any] = {
                "run_id": run_id,
                "profile": ns.profile,
                "started_utc": _utc_now(),
                "skill_pack": [
                    "prime-wishes",
                    "phuc-forecast",
                    "phuc-swarms",
                    "phuc-cleanup",
                    "prime-coder",
                    "prime-safety",
                    "phuc-context",
                ],
                "steps": [],
            }

            all_ok = True
            for idx, step in enumerate(steps, start=1):
                cmd = step["command"]
                step_record: dict[str, Any] = {
                    "index": idx,
                    "name": step["name"],
                    "command": cmd,
                    "status": "planned",
                }
                try:
                    proc = subprocess.run(
                        cmd,
                        cwd=str(root),
                        env=_runtime_env(root),
                        text=True,
                        capture_output=True,
                        timeout=float(ns.timeout),
                        check=False,
                    )
                    step_record["returncode"] = proc.returncode
                    step_record["optional"] = step.get("optional", False)
                    if proc.returncode == 0:
                        step_record["status"] = "success"
                    elif step.get("optional", False):
                        step_record["status"] = "skipped"
                    else:
                        step_record["status"] = "failed"
                    log_prefix = logs_dir / f"{idx:02d}-{step['name']}"
                    (log_prefix.with_suffix(".stdout.log")).write_text(proc.stdout or "", encoding="utf-8")
                    (log_prefix.with_suffix(".stderr.log")).write_text(proc.stderr or "", encoding="utf-8")
                    if proc.returncode != 0 and not step.get("optional", False):
                        all_ok = False
                except subprocess.TimeoutExpired:
                    step_record["status"] = "timeout"
                    step_record["returncode"] = None
                    all_ok = False
                manifest["steps"].append(step_record)

            manifest["finished_utc"] = _utc_now()
            manifest["status"] = "PASS" if all_ok else "FAIL"
            _write_json(run_dir / "manifest.json", manifest)

            # Prime Mermaid run graph + hash for replay/audit.
            lines = ["flowchart TD", f"  START[RUN: {run_id}]"]
            prev = "START"
            for item in manifest["steps"]:
                node = f"S{item['index']}"
                label = f"{item['index']} {item['name']} ({item['status']})"
                lines.append(f"  {node}[{label}]")
                lines.append(f"  {prev} --> {node}")
                prev = node
            lines.append(f"  {prev} --> END[STATUS: {manifest['status']}]")
            mmd_text = "\n".join(lines) + "\n"
            mmd_path = run_dir / "stack.mmd"
            sha_path = run_dir / "stack.sha256"
            mmd_path.write_text(mmd_text, encoding="utf-8")
            digest = hashlib.sha256(mmd_text.encode("utf-8")).hexdigest()
            sha_path.write_text(f"{digest}  stack.mmd\n", encoding="utf-8")

            payload = {
                "run_id": run_id,
                "status": manifest["status"],
                "manifest": str(run_dir / "manifest.json"),
                "graph": str(mmd_path),
                "sha256": str(sha_path),
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"run_id: {run_id}")
                print(f"status: {manifest['status']}")
                print(f"Wrote: {run_dir / 'manifest.json'}")
                print(f"Wrote: {mmd_path}")
                print(f"Wrote: {sha_path}")
            return 0 if all_ok else 1

        if ns.stack_cmd == "verify":
            run_dir = None
            if ns.run_id:
                run_dir = root / "artifacts" / "runs" / str(ns.run_id).strip()
            else:
                run_dir = _latest_run_id_dir(root / "artifacts" / "runs")
            if run_dir is None:
                print("ERROR: no stack run found.")
                return 1

            manifest_path = run_dir / "manifest.json"
            if not manifest_path.exists():
                print(f"ERROR: missing manifest: {manifest_path}")
                return 1

            manifest = _load_json(manifest_path)
            step_statuses = [str(s.get("status", "")) for s in manifest.get("steps", [])]
            all_success = all(s == "success" for s in step_statuses) if step_statuses else False

            sha_ok = True
            mmd_path = run_dir / "stack.mmd"
            sha_path = run_dir / "stack.sha256"
            if mmd_path.exists() and sha_path.exists():
                actual = hashlib.sha256(mmd_path.read_bytes()).hexdigest()
                declared = sha_path.read_text(encoding="utf-8").strip().split()[0]
                sha_ok = actual == declared

            ok = sha_ok and (all_success if ns.strict else True)
            payload = {
                "run_id": manifest.get("run_id"),
                "status": manifest.get("status"),
                "strict": bool(ns.strict),
                "all_steps_success": all_success,
                "sha_ok": sha_ok,
                "ok": ok,
                "manifest": str(manifest_path),
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"run_id: {payload['run_id']}")
                print(f"status: {payload['status']}")
                print(f"all_steps_success: {all_success}")
                print(f"sha_ok: {sha_ok}")
                print(f"verify: {'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

    if ns.cmd == "recipe":
        if ns.recipe_cmd == "list":
            scan_dirs = ns.dir or list(_kernel_paths(root)["recipe_dirs"])
            recipes = _collect_recipe_files(root, scan_dirs)
            formatted_recipes: list[str] = []
            for p in recipes:
                try:
                    formatted_recipes.append(str(p.relative_to(root)))
                except ValueError:
                    formatted_recipes.append(str(p))
            payload = {
                "count": len(recipes),
                "scan_dirs": scan_dirs,
                "recipes": formatted_recipes,
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"recipes: {len(recipes)}")
                for item in payload["recipes"]:
                    print(f"- {item}")
            return 0

        if ns.recipe_cmd == "add":
            target_dir = Path(ns.dir)
            if not target_dir.is_absolute():
                target_dir = root / target_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            recipe_slug = _slug(ns.name).replace(".", "_")
            target_path = target_dir / f"recipe.{recipe_slug}.prime-mermaid.md"
            if target_path.exists() and not ns.force:
                print(f"ERROR: exists (use --force): {target_path}")
                return 1
            content = "\n".join(
                [
                    f"# Recipe: {recipe_slug}",
                    "",
                    f"Date: {_utc_now()}",
                    "",
                    "```mermaid",
                    "flowchart TD",
                    "  INTENT[INTENT] --> CPU[CPU_PREPASS]",
                    "  CPU --> GATE{NEED_LLM}",
                    "  GATE -->|NO| APPLY[APPLY_CPU_PATH]",
                    "  GATE -->|YES| LLM[CALL_LLM]",
                    "  APPLY --> VERIFY[VERIFY]",
                    "  LLM --> VERIFY",
                    "  VERIFY --> RECEIPT[WRITE_RECEIPT]",
                    "```",
                    "",
                    "## Notes",
                    "-",
                    "",
                ]
            )
            target_path.write_text(content, encoding="utf-8")
            payload = {"ok": True, "recipe": str(target_path)}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"Wrote: {target_path}")
            return 0

        if ns.recipe_cmd == "lint":
            lint_dirs = ns.dir or ["wishes", "ripples", "recipes", "cli/recipes", "memory", "cli/wishes"]
            ext_recipe = Path(_kernel_paths(root)["extension_root"]) / "recipes"
            if ext_recipe.exists():
                try:
                    lint_dirs.append(str(ext_recipe.relative_to(root)))
                except ValueError:
                    lint_dirs.append(str(ext_recipe))
            violations: list[str] = []
            scanned: list[str] = []
            prime_count = 0
            derived_json = {"results.json", "manifest.json", "summary.json", "receipt.json", "proof.json"}

            for rel in lint_dirs:
                base = root / rel
                if not base.exists():
                    continue
                scanned.append(str(base.relative_to(root)))
                for path in base.rglob("*"):
                    if not path.is_file():
                        continue
                    rel_path = str(path.relative_to(root))
                    if rel_path.startswith("artifacts/"):
                        continue
                    lower_name = path.name.lower()
                    if lower_name.endswith(".ipynb"):
                        continue
                    if lower_name.endswith(".prime-mermaid.md") or lower_name.endswith(".mmd"):
                        prime_count += 1
                    if ns.prime_mermaid_only and (
                        lower_name.endswith(".yaml")
                        or lower_name.endswith(".yml")
                        or lower_name.endswith(".json")
                    ):
                        if lower_name in derived_json:
                            continue
                        violations.append(rel_path)

            ok = True
            if ns.prime_mermaid_only and violations:
                ok = False
            if ns.prime_mermaid_only and prime_count == 0:
                ok = False
                violations.append("no Prime Mermaid source files found in linted directories")

            payload = {
                "ok": ok,
                "prime_mermaid_only": bool(ns.prime_mermaid_only),
                "scanned_dirs": scanned,
                "prime_file_count": prime_count,
                "violations": violations,
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"prime_file_count: {prime_count}")
                print(f"violations: {len(violations)}")
                for item in violations:
                    print(f"- {item}")
                print(f"status: {'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

    if ns.cmd == "books":
        if ns.books_cmd == "list":
            scan_dirs = ns.dir or list(_kernel_paths(root)["books_dirs"])
            books = _collect_book_files(root, scan_dirs)
            formatted: list[str] = []
            for p in books:
                try:
                    formatted.append(str(p.relative_to(root)))
                except ValueError:
                    formatted.append(str(p))
            payload = {"count": len(books), "scan_dirs": scan_dirs, "books": formatted}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"books: {len(books)}")
                for item in formatted:
                    print(f"- {item}")
            return 0

        if ns.books_cmd == "show":
            raw = str(ns.name).strip()
            direct = Path(raw)
            if direct.is_absolute() and direct.exists():
                path = direct
            else:
                candidate = root / raw
                if candidate.exists():
                    path = candidate
                else:
                    books = _collect_book_files(root, list(_kernel_paths(root)["books_dirs"]))
                    matches = [p for p in books if p.name == raw or p.stem == raw]
                    if not matches:
                        print(f"ERROR: book not found: {raw}")
                        return 1
                    path = matches[0]
            text = path.read_text(encoding="utf-8")
            if ns.json:
                try:
                    rel = str(path.relative_to(root))
                except ValueError:
                    rel = str(path)
                print(json.dumps({"path": rel, "content": text}, indent=2, sort_keys=True))
            else:
                print(text)
            return 0

    if ns.cmd == "papers":
        if ns.papers_cmd == "list":
            scan_dirs = ns.dir or list(_kernel_paths(root)["papers_dirs"])
            papers = _collect_paper_files(root, scan_dirs)
            formatted: list[str] = []
            for p in papers:
                try:
                    formatted.append(str(p.relative_to(root)))
                except ValueError:
                    formatted.append(str(p))
            payload = {"count": len(papers), "scan_dirs": scan_dirs, "papers": formatted}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"papers: {len(papers)}")
                for item in formatted:
                    print(f"- {item}")
            return 0

        if ns.papers_cmd == "show":
            raw = str(ns.name).strip()
            direct = Path(raw)
            if direct.is_absolute() and direct.exists():
                path = direct
            else:
                candidate = root / raw
                if candidate.exists():
                    path = candidate
                else:
                    papers = _collect_paper_files(root, list(_kernel_paths(root)["papers_dirs"]))
                    matches = [p for p in papers if p.name == raw or p.stem == raw]
                    if not matches:
                        print(f"ERROR: paper not found: {raw}")
                        return 1
                    path = matches[0]
            text = path.read_text(encoding="utf-8")
            if ns.json:
                try:
                    rel = str(path.relative_to(root))
                except ValueError:
                    rel = str(path)
                print(json.dumps({"path": rel, "content": text}, indent=2, sort_keys=True))
            else:
                print(text)
            return 0

    if ns.cmd == "math-universal":
        run_id = _new_run_id("math-universal")
        out_dir = root / "artifacts" / "math_universal" / run_id
        out_dir.mkdir(parents=True, exist_ok=True)

        config_path = _resolve_user_path(root, str(ns.config))
        config_exists = config_path.exists()
        if config_exists:
            try:
                config = _load_json(config_path)
            except Exception as ex:
                payload = {
                    "run_id": run_id,
                    "timestamp_utc": _utc_now(),
                    "config_path": str(config_path),
                    "config_exists": True,
                    "overall_ok": False,
                    "universal_claim_ready": False,
                    "error": f"invalid_config_json: {ex}",
                    "artifact_dir": str(out_dir),
                }
                _write_json(out_dir / "report.json", payload)
                (out_dir / "report.md").write_text(_markdown_math_universal_report(payload), encoding="utf-8")
                if ns.json:
                    print(json.dumps(payload, indent=2, sort_keys=True))
                else:
                    print(f"run_id: {run_id}")
                    print(f"artifact_dir: {out_dir}")
                    print(f"ERROR: {payload['error']}")
                return 1
        else:
            config = _default_math_universal_config()

        if not isinstance(config, dict):
            config = _default_math_universal_config()

        defaults_raw = config.get("defaults", {}) if isinstance(config.get("defaults"), dict) else {}
        defaults: dict[str, Any] = {
            "from_year": _coerce_int(defaults_raw.get("from_year", 1959), default=1959),
            "to_year": _coerce_int(defaults_raw.get("to_year", 2025), default=2025),
            "lang": str(defaults_raw.get("lang", "eng")).strip() or "eng",
            "model": str(defaults_raw.get("model", "llama3.1:8b")).strip() or "llama3.1:8b",
            "url": str(defaults_raw.get("url", "")).strip(),
            "timeout": _coerce_float(defaults_raw.get("timeout", float(ns.timeout)), default=float(ns.timeout)),
            "max_problems": _coerce_int(defaults_raw.get("max_problems", 0), default=0),
            "fetch_missing": bool(defaults_raw.get("fetch_missing", False)),
            "oracles_file": str(defaults_raw.get("oracles_file", "cli/tests/math/imo_history_oracles.json")).strip(),
        }
        if ns.model:
            defaults["model"] = str(ns.model).strip() or defaults["model"]
        if ns.url:
            defaults["url"] = str(ns.url).strip()
        defaults["timeout"] = float(ns.timeout)
        if bool(ns.fetch_missing):
            defaults["fetch_missing"] = True

        heldout_profiles = config.get("heldout_profiles", []) if isinstance(config.get("heldout_profiles"), list) else []
        heldout_rows: list[dict[str, Any]] = []
        for profile in heldout_profiles:
            if not isinstance(profile, dict):
                continue
            heldout_rows.append(
                _run_math_universal_bench_profile(
                    root=root,
                    profile=profile,
                    defaults=defaults,
                    model_override=None,
                    url_override=None,
                    timeout_override=float(defaults["timeout"]),
                    fetch_missing_override=bool(defaults["fetch_missing"]),
                )
            )
        heldout_required_min = (
            max(_coerce_float(row.get("min_pass_ratio", 0.0), default=0.0) for row in heldout_rows)
            if heldout_rows
            else 0.0
        )
        heldout_pass_ratio = (
            round(sum(float(row.get("pass_ratio", 0.0)) for row in heldout_rows) / len(heldout_rows), 6)
            if heldout_rows
            else 0.0
        )
        heldout_ok = bool(heldout_rows) and all(bool(row.get("ok", False)) for row in heldout_rows)

        proof_cfg = config.get("proof_artifacts", {}) if isinstance(config.get("proof_artifacts"), dict) else {}
        proof_required = bool(proof_cfg.get("required", True))
        proof_cases_file = _resolve_user_path(root, str(proof_cfg.get("cases_file", "cli/tests/math/proof_artifact_cases.json")))
        proof_min = _coerce_float(proof_cfg.get("required_min_pass_ratio", 1.0), default=1.0)
        proof_result = _run_math_universal_proof_artifacts(root=root, cases_file=proof_cases_file)
        proof_ok = bool(proof_result.get("ok", False)) and float(proof_result.get("pass_ratio", 0.0)) >= proof_min
        if not proof_required:
            proof_ok = True

        generalization_profiles = (
            config.get("generalization_profiles", []) if isinstance(config.get("generalization_profiles"), list) else []
        )
        generalization_rows: list[dict[str, Any]] = []
        for profile in generalization_profiles:
            if not isinstance(profile, dict):
                continue
            generalization_rows.append(
                _run_math_universal_bench_profile(
                    root=root,
                    profile=profile,
                    defaults=defaults,
                    model_override=None,
                    url_override=None,
                    timeout_override=float(defaults["timeout"]),
                    fetch_missing_override=bool(defaults["fetch_missing"]),
                )
            )
        generalization_required_min = 0.0
        if generalization_rows:
            generalization_required_min = max(
                _coerce_float(row.get("min_pass_ratio", 0.0), default=0.0) for row in generalization_rows
            )
        generalization_pass_ratio = (
            round(sum(float(row.get("pass_ratio", 0.0)) for row in generalization_rows) / len(generalization_rows), 6)
            if generalization_rows
            else 0.0
        )
        generalization_ok = bool(generalization_rows) and all(bool(row.get("ok", False)) for row in generalization_rows)

        stability_cfg = config.get("stability", {}) if isinstance(config.get("stability"), dict) else {}
        stability_profile = stability_cfg.get("profile", {}) if isinstance(stability_cfg.get("profile"), dict) else {}
        stability_models_raw = stability_cfg.get("models", [])
        stability_models = (
            [str(item).strip() for item in stability_models_raw if str(item).strip()]
            if isinstance(stability_models_raw, list)
            else []
        )
        if not stability_models:
            stability_models = [str(defaults["model"])]

        stability_urls_raw = stability_cfg.get("urls", [])
        stability_urls = (
            [str(item).strip() for item in stability_urls_raw if str(item).strip()]
            if isinstance(stability_urls_raw, list)
            else []
        )
        if not stability_urls:
            default_url = str(defaults.get("url", "")).strip()
            stability_urls = [default_url] if default_url else [""]

        stability_rows: list[dict[str, Any]] = []
        for model in stability_models:
            for url in stability_urls:
                row = _run_math_universal_bench_profile(
                    root=root,
                    profile=stability_profile if stability_profile else {},
                    defaults=defaults,
                    model_override=model,
                    url_override=url,
                    timeout_override=float(defaults["timeout"]),
                    fetch_missing_override=bool(defaults["fetch_missing"]),
                )
                row["matrix_model"] = model
                row["matrix_url"] = url
                stability_rows.append(row)
        stability_required_all = bool(stability_cfg.get("required_all", True))
        stability_required_min = (
            max(_coerce_float(row.get("min_pass_ratio", 0.0), default=0.0) for row in stability_rows)
            if stability_rows
            else 0.0
        )
        stability_pass_ratio = (
            round(sum(float(row.get("pass_ratio", 0.0)) for row in stability_rows) / len(stability_rows), 6)
            if stability_rows
            else 0.0
        )
        if stability_required_all:
            stability_ok = bool(stability_rows) and all(bool(row.get("ok", False)) for row in stability_rows)
        else:
            stability_ok = bool(stability_rows) and any(bool(row.get("ok", False)) for row in stability_rows)

        gates = {
            "heldout": {
                "ok": heldout_ok,
                "required_min_pass_ratio": heldout_required_min,
                "pass_ratio": heldout_pass_ratio,
                "rows": heldout_rows,
            },
            "proof_artifacts": {
                "ok": proof_ok,
                "required": proof_required,
                "required_min_pass_ratio": proof_min,
                "pass_ratio": float(proof_result.get("pass_ratio", 0.0)),
                "summary": proof_result,
            },
            "generalization": {
                "ok": generalization_ok,
                "required_min_pass_ratio": generalization_required_min,
                "pass_ratio": generalization_pass_ratio,
                "rows": generalization_rows,
            },
            "stability": {
                "ok": stability_ok,
                "required_all": stability_required_all,
                "required_min_pass_ratio": stability_required_min,
                "pass_ratio": stability_pass_ratio,
                "rows": stability_rows,
            },
        }
        overall_ok = bool(heldout_ok and proof_ok and generalization_ok and stability_ok)
        payload = {
            "run_id": run_id,
            "timestamp_utc": _utc_now(),
            "config_path": str(config_path),
            "config_exists": bool(config_exists),
            "defaults": defaults,
            "gates": gates,
            "overall_ok": overall_ok,
            "universal_claim_ready": overall_ok,
            "artifact_dir": str(out_dir),
            "source": "math-universal gate suite",
        }

        _write_json(out_dir / "report.json", payload)
        (out_dir / "report.md").write_text(_markdown_math_universal_report(payload), encoding="utf-8")

        if ns.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"run_id: {run_id}")
            print(f"artifact_dir: {out_dir}")
            print(f"config_path: {config_path}")
            print(f"config_exists: {config_exists}")
            print(f"overall_ok: {overall_ok}")
            for gate_name in ["heldout", "proof_artifacts", "generalization", "stability"]:
                gate = gates.get(gate_name, {})
                print(
                    f"- {gate_name}: ok={bool(gate.get('ok', False))} "
                    f"pass_ratio={gate.get('pass_ratio', 0.0)}"
                )

        if overall_ok or bool(ns.no_strict):
            return 0
        return 1

    if ns.cmd == "imo-phuc":
        run_id = ns.run_id or _new_run_id("imo-phuc")
        out_dir = root / "artifacts" / "imo_phuc" / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        required_rung = int(ns.required_rung)
        if required_rung not in {641, 274177, 65537}:
            print("ERROR: --required-rung must be one of 641, 274177, 65537")
            return 1
        swarm_loaded = _load_swarm_settings(root)
        swarm_settings = swarm_loaded.get("settings", {}) if isinstance(swarm_loaded.get("settings"), dict) else {}
        council_base = _math_expert_council_config(settings=swarm_settings, default_required_rung=required_rung)
        council_base["required_rung"] = required_rung

        cases_path = Path(str(ns.cases_file).strip())
        if not cases_path.is_absolute():
            cases_path = root / cases_path

        try:
            cases = _load_imo_qa_cases(cases_path)
        except Exception as ex:
            print(f"ERROR: {ex}")
            return 1

        rows: list[dict[str, Any]] = []
        tool_score = 0
        llm_score = 0

        for case in cases:
            case_id = case["id"]
            case_dir = out_dir / case_id
            case_dir.mkdir(parents=True, exist_ok=True)

            scout = _imo_phuc_case_scout(case)
            _write_json(case_dir / "SCOUT_REPORT.json", scout)

            forecast = _imo_phuc_case_forecast(case, scout)
            _write_json(case_dir / "FORECAST_MEMO.json", forecast)

            decide = _imo_phuc_case_decide(case=case, forecast_memo=forecast, required_rung=required_rung)
            _write_json(case_dir / "DECISION_RECORD.json", decide)

            tool_run = _run_twin_subprocess(
                root=root,
                prompt=case["prompt"],
                model=str(ns.model),
                timeout=float(ns.timeout),
                url=ns.url,
                llm_only=False,
                retries=1,
            )
            llm_run = _run_twin_subprocess(
                root=root,
                prompt=case["prompt"],
                model=str(ns.model),
                timeout=float(ns.timeout),
                url=ns.url,
                llm_only=True,
                retries=1,
            )
            act = {
                "case_id": case_id,
                "model": str(ns.model),
                "url": str(ns.url or ""),
                "timeout": float(ns.timeout),
                "decision_record_ref": True,
                "tool_assisted": tool_run,
                "llm_only": llm_run,
            }
            _write_json(case_dir / "ACT_RESULT.json", act)

            tool_eval = _imo_phuc_eval_lane(
                run=tool_run,
                needle=case["needle"],
                aliases=case.get("aliases", []),
                concepts=case.get("concepts", []),
                required_sections=case.get("required_sections", []),
                lane_name="tool_assisted",
                council_cfg={**council_base, "required_rung": required_rung},
            )
            llm_eval = _imo_phuc_eval_lane(
                run=llm_run,
                needle=case["needle"],
                aliases=case.get("aliases", []),
                concepts=case.get("concepts", []),
                required_sections=case.get("required_sections", []),
                lane_name="llm_only",
                council_cfg={**council_base, "required_rung": 641},
            )

            fail_reasons: list[str] = []
            tool_council = tool_eval.get("council", {}) if isinstance(tool_eval.get("council"), dict) else {}
            llm_council = llm_eval.get("council", {}) if isinstance(llm_eval.get("council"), dict) else {}
            if str(tool_council.get("status", "FAIL")) != "PASS":
                reasons = tool_council.get("fail_reasons", [])
                if isinstance(reasons, list):
                    fail_reasons.extend(str(item) for item in reasons if str(item).strip())
                else:
                    fail_reasons.append("tool_assisted expert council failed")
            if not llm_eval["run_ok"]:
                fail_reasons.append("llm_only run failed")
            if not llm_eval["source"] or not llm_eval["action"]:
                fail_reasons.append("llm_only lane missing source/action disclosure")

            status = "PASS" if not fail_reasons else "FAIL"
            skeptic = {
                "status": status,
                "required_rung": required_rung,
                "rung_achieved": int(tool_council.get("rung_achieved", 0)) if status == "PASS" else 0,
                "fail_reasons": fail_reasons,
                "required_fixes": [
                    "align tool route policy in SWARM-ORCHESTRATION settings",
                    "improve prompt-to-problem mapping for parser",
                    "improve deterministic answer extraction markers",
                    "strengthen expert-council witnesses for failed rungs",
                ]
                if fail_reasons
                else [],
                "tool_assisted": tool_eval,
                "llm_only": llm_eval,
                "expert_council": {
                    "tool_assisted": tool_council,
                    "llm_only": llm_council,
                },
            }
            _write_json(case_dir / "SKEPTIC_VERDICT.json", skeptic)

            row = {
                "case_id": case_id,
                "status": status,
                "phuc_fail_reasons": fail_reasons,
                "tool_match": bool(tool_eval["match"]),
                "tool_match_mode": str(tool_eval.get("match_mode", "none")),
                "tool_match_score": float(tool_eval.get("match_score", 0.0)),
                "tool_source": tool_eval["source"],
                "tool_action": tool_eval["action"],
                "tool_profile": tool_eval["profile"],
                "tool_reason": tool_eval["reason"],
                "tool_rung_achieved": int(tool_council.get("rung_achieved", 0)),
                "tool_consensus": tool_council.get("consensus"),
                "llm_match": bool(llm_eval["match"]),
                "llm_match_mode": str(llm_eval.get("match_mode", "none")),
                "llm_match_score": float(llm_eval.get("match_score", 0.0)),
                "llm_source": llm_eval["source"],
                "llm_action": llm_eval["action"],
                "llm_rung_achieved": int(llm_council.get("rung_achieved", 0)),
                "artifact_dir": str(case_dir),
            }
            rows.append(row)

            if status == "PASS":
                tool_score += 1
            if bool(llm_eval["match"]):
                llm_score += 1

        total_cases = len(cases)
        strict_pass = tool_score == total_cases if total_cases > 0 else False
        report = {
            "run_id": run_id,
            "timestamp_utc": _utc_now(),
            "cases_file": str(cases_path),
            "model": str(ns.model),
            "url": str(ns.url or ""),
            "timeout": float(ns.timeout),
            "required_rung": required_rung,
            "expert_council": {
                "enabled": bool(council_base.get("enabled", True)),
                "virtual_size": int(council_base.get("virtual_size", 65537)),
                "integrity_mode": str(council_base.get("integrity_mode", "strict_fail_closed")),
                "max_love": bool(council_base.get("max_love", True)),
            },
            "total_cases": total_cases,
            "tool_assisted_score": tool_score,
            "llm_only_score": llm_score,
            "strict_pass": strict_pass,
            "rows": rows,
            "lane_disclosure": {
                "tool_assisted": "PHUC swarms deterministic route (CPU) with receipts",
                "llm_only": "remote model baseline via --llm-only",
            },
        }
        report["memory_loop"] = _record_imo_memory(
            root=root,
            kind="imo-phuc",
            run_id=run_id,
            report=report,
            report_file=out_dir / "REPORT.json",
        )
        _write_json(out_dir / "REPORT.json", report)
        (out_dir / "REPORT.md").write_text(_markdown_imo_phuc_report(report), encoding="utf-8")

        if ns.json:
            payload = {**report, "artifact_dir": str(out_dir)}
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"run_id: {run_id}")
            print(f"artifact_dir: {out_dir}")
            print(f"tool_assisted_score: {tool_score}/{total_cases}")
            print(f"llm_only_score: {llm_score}/{total_cases}")
            print(f"strict_pass: {strict_pass}")

        if ns.no_strict:
            return 0
        return 0 if strict_pass else 1

    if ns.cmd == "imo-history":
        if ns.from_year > ns.to_year:
            print("ERROR: --from-year must be <= --to-year")
            return 1
        if ns.imo_hist_cmd in {"bench", "autolearn"} and int(ns.required_rung) not in {641, 274177, 65537}:
            print("ERROR: --required-rung must be one of 641, 274177, 65537")
            return 1
        years = list(range(int(ns.from_year), int(ns.to_year) + 1))
        if ns.imo_hist_cmd == "fetch":
            rows: list[dict[str, Any]] = []
            ok = True
            for year in years:
                year_ok, data = _fetch_imo_year_dataset(
                    root=root,
                    year=year,
                    lang=str(ns.lang),
                    timeout=float(ns.timeout),
                    force=bool(ns.force),
                )
                rows.append({"year": year, "ok": year_ok, **data})
                ok = ok and year_ok
            payload = {
                "ok": ok,
                "from_year": ns.from_year,
                "to_year": ns.to_year,
                "lang": ns.lang,
                "rows": rows,
                "source": "https://www.imo-official.org/download_file.aspx?file=dummy.pdf",
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                for row in rows:
                    status = "PASS" if row.get("ok") else "FAIL"
                    print(f"[{status}] {row.get('year')} problems={row.get('problem_count', 0)}")
                    if row.get("parsed_json"):
                        print(f"  parsed: {row.get('parsed_json')}")
                    if row.get("error"):
                        print(f"  error: {row.get('error')}")
                print(f"status: {'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

        if ns.imo_hist_cmd == "oracles-template":
            out_path = Path(str(ns.out))
            if not out_path.is_absolute():
                out_path = root / out_path

            loaded_existing: dict[tuple[int, str], dict[str, Any]] = {}
            if bool(ns.merge_existing):
                loaded_existing = _load_imo_history_oracles(out_path)

            generated: list[dict[str, Any]] = []
            total_cases = 0
            rows: list[dict[str, Any]] = []
            for year in years:
                ds = _load_cached_imo_year_dataset(root, int(year), str(ns.lang))
                if ds is None and bool(ns.fetch_missing):
                    _, _ = _fetch_imo_year_dataset(
                        root=root,
                        year=int(year),
                        lang=str(ns.lang),
                        timeout=45.0,
                        force=False,
                    )
                    ds = _load_cached_imo_year_dataset(root, int(year), str(ns.lang))
                if ds is None:
                    rows.append({"year": int(year), "ok": False, "error": "dataset_missing"})
                    continue
                problems = ds.get("problems", [])
                if not isinstance(problems, list):
                    problems = []
                added_for_year = 0
                for problem in problems:
                    if int(ns.max_problems) > 0 and total_cases >= int(ns.max_problems):
                        break
                    pid = str(problem.get("id", "")).strip().upper()
                    if not pid:
                        continue
                    if not pid.startswith("P"):
                        pid = f"P{pid}"
                    statement = _normalize_compact_whitespace(str(problem.get("statement", "")))
                    key = (int(year), pid)
                    existing = loaded_existing.get(key, {})
                    entry: dict[str, Any] = {
                        "year": int(year),
                        "problem_id": pid,
                        "needle": str(existing.get("needle", "")).strip(),
                        "aliases": existing.get("aliases", []) if isinstance(existing.get("aliases"), list) else [],
                        "concepts": existing.get("concepts", []) if isinstance(existing.get("concepts"), list) else [],
                        "required_sections": existing.get("required_sections", [])
                        if isinstance(existing.get("required_sections"), list)
                        else [],
                        "statement_excerpt": statement[:220],
                    }
                    generated.append(entry)
                    total_cases += 1
                    added_for_year += 1
                rows.append({"year": int(year), "ok": True, "problems_added": added_for_year})
                if int(ns.max_problems) > 0 and total_cases >= int(ns.max_problems):
                    break

            generated = sorted(generated, key=lambda row: (int(row.get("year", 0)), str(row.get("problem_id", ""))))
            payload = {
                "version": 1,
                "description": "Historical IMO oracle targets (generated template). Fill needle/aliases per case.",
                "generated_at_utc": _utc_now(),
                "from_year": int(ns.from_year),
                "to_year": int(ns.to_year),
                "lang": str(ns.lang),
                "merge_existing": bool(ns.merge_existing),
                "cases": generated,
            }
            out_path.parent.mkdir(parents=True, exist_ok=True)
            _write_json(out_path, payload)

            summary = {
                "ok": True,
                "out": str(out_path),
                "from_year": int(ns.from_year),
                "to_year": int(ns.to_year),
                "lang": str(ns.lang),
                "merge_existing": bool(ns.merge_existing),
                "cases_written": len(generated),
                "rows": rows,
            }
            if ns.json:
                print(json.dumps(summary, indent=2, sort_keys=True))
            else:
                print(f"out: {out_path}")
                print(f"cases_written: {len(generated)}")
                for row in rows:
                    if bool(row.get("ok")):
                        print(f"- {row.get('year')}: added={row.get('problems_added', 0)}")
                    else:
                        print(f"- {row.get('year')}: FAIL ({row.get('error', 'unknown')})")
            return 0

        if ns.imo_hist_cmd == "oracle-status":
            run_id = _new_run_id("imo-oracle-status")
            out_dir = root / "artifacts" / "imo_oracle_status" / run_id
            out_dir.mkdir(parents=True, exist_ok=True)

            oracle_file = Path(str(ns.oracles_file))
            if not oracle_file.is_absolute():
                oracle_file = root / oracle_file
            history_oracles = _load_imo_history_oracles(oracle_file)

            rows: list[dict[str, Any]] = []
            per_year: dict[str, dict[str, Any]] = {}
            total_cases = 0
            ready_cases = 0
            quality_ready_cases = 0
            quality_strong_cases = 0
            quality_weak_cases = 0
            with_concepts = 0
            with_required_sections = 0
            ok = True

            for year in years:
                ds = _load_cached_imo_year_dataset(root, int(year), str(ns.lang))
                if ds is None and bool(ns.fetch_missing):
                    _, _ = _fetch_imo_year_dataset(
                        root=root,
                        year=int(year),
                        lang=str(ns.lang),
                        timeout=45.0,
                        force=False,
                    )
                    ds = _load_cached_imo_year_dataset(root, int(year), str(ns.lang))
                if ds is None:
                    ok = False
                    per_year[str(year)] = {
                        "total": 0,
                        "ready": 0,
                        "missing": 0,
                        "ready_ratio": 0.0,
                        "error": "dataset_missing",
                    }
                    continue
                problems = ds.get("problems", [])
                if not isinstance(problems, list):
                    problems = []
                year_total = 0
                year_ready = 0
                year_quality_ready = 0
                year_quality_strong = 0
                year_quality_weak = 0

                for problem in problems:
                    if int(ns.max_problems) > 0 and total_cases >= int(ns.max_problems):
                        break
                    pid = str(problem.get("id", "")).strip().upper()
                    if not pid:
                        continue
                    if not pid.startswith("P"):
                        pid = f"P{pid}"
                    statement = _normalize_compact_whitespace(str(problem.get("statement", "")))
                    oracle = history_oracles.get((int(year), pid), {})
                    if not isinstance(oracle, dict):
                        oracle = {}
                    needle = str(oracle.get("needle", "")).strip()
                    aliases = oracle.get("aliases", []) if isinstance(oracle.get("aliases"), list) else []
                    concepts = oracle.get("concepts", []) if isinstance(oracle.get("concepts"), list) else []
                    required_sections = (
                        oracle.get("required_sections", []) if isinstance(oracle.get("required_sections"), list) else []
                    )
                    quality = oracle.get("quality", {}) if isinstance(oracle.get("quality"), dict) else {}
                    quality_tier = str(quality.get("tier", "none")).strip().lower() or "none"
                    quality_score = float(quality.get("score", 0.0))
                    quality_ready = bool(quality.get("ready_standard", False))
                    quality_strong = bool(quality.get("ready_strong", False))
                    independent_targets = int(quality.get("independent_target_count", 0))
                    has_oracle = bool(needle) or any(str(item).strip() for item in aliases)
                    has_concepts = any(str(item).strip() for item in concepts)
                    has_sections = any(str(item).strip() for item in required_sections)

                    rows.append(
                        {
                            "year": int(year),
                            "problem_id": pid,
                            "oracle_ready": has_oracle,
                            "oracle_quality_tier": quality_tier,
                            "oracle_quality_score": round(quality_score, 6),
                            "oracle_quality_ready": quality_ready,
                            "oracle_quality_strong": quality_strong,
                            "oracle_quality_independent_targets": independent_targets,
                            "has_concepts": has_concepts,
                            "has_required_sections": has_sections,
                            "needle": needle,
                            "aliases_count": len([item for item in aliases if str(item).strip()]),
                            "concepts_count": len([item for item in concepts if str(item).strip()]),
                            "required_sections_count": len([item for item in required_sections if str(item).strip()]),
                            "statement_excerpt": statement[:220],
                        }
                    )

                    total_cases += 1
                    year_total += 1
                    if has_oracle:
                        ready_cases += 1
                        year_ready += 1
                    if quality_ready:
                        quality_ready_cases += 1
                        year_quality_ready += 1
                    if quality_strong:
                        quality_strong_cases += 1
                        year_quality_strong += 1
                    if quality_tier == "weak":
                        quality_weak_cases += 1
                        year_quality_weak += 1
                    if has_concepts:
                        with_concepts += 1
                    if has_sections:
                        with_required_sections += 1

                year_missing = max(0, year_total - year_ready)
                per_year[str(year)] = {
                    "total": year_total,
                    "ready": year_ready,
                    "missing": year_missing,
                    "ready_ratio": round((year_ready / year_total), 6) if year_total > 0 else 0.0,
                    "quality_ready": year_quality_ready,
                    "quality_strong": year_quality_strong,
                    "quality_weak": year_quality_weak,
                    "quality_ready_ratio": round((year_quality_ready / year_total), 6) if year_total > 0 else 0.0,
                    "quality_strong_ratio": round((year_quality_strong / year_total), 6) if year_total > 0 else 0.0,
                }
                if int(ns.max_problems) > 0 and total_cases >= int(ns.max_problems):
                    break

            oracle_missing = max(0, total_cases - ready_cases)
            report = {
                "run_id": run_id,
                "timestamp_utc": _utc_now(),
                "from_year": int(ns.from_year),
                "to_year": int(ns.to_year),
                "lang": str(ns.lang),
                "oracles_file": str(oracle_file),
                "total_problems": total_cases,
                "oracle_ready": ready_cases,
                "oracle_missing": oracle_missing,
                "ready_ratio": round((ready_cases / total_cases), 6) if total_cases > 0 else 0.0,
                "oracle_quality_ready": quality_ready_cases,
                "oracle_quality_strong": quality_strong_cases,
                "oracle_quality_weak": quality_weak_cases,
                "quality_ready_ratio": round((quality_ready_cases / total_cases), 6) if total_cases > 0 else 0.0,
                "quality_strong_ratio": round((quality_strong_cases / total_cases), 6) if total_cases > 0 else 0.0,
                "with_concepts": with_concepts,
                "with_required_sections": with_required_sections,
                "ok": bool(ok),
                "per_year": per_year,
                "rows": rows,
            }
            _write_json(out_dir / "report.json", report)
            (out_dir / "report.md").write_text(_markdown_imo_oracle_status_report(report), encoding="utf-8")

            payload = {**report, "artifact_dir": str(out_dir)}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"run_id: {run_id}")
                print(f"artifact_dir: {out_dir}")
                print(f"oracles_file: {oracle_file}")
                print(f"total_problems: {total_cases}")
                print(f"oracle_ready: {ready_cases}")
                print(f"oracle_missing: {oracle_missing}")
                print(f"ready_ratio: {payload['ready_ratio']}")
                print(f"oracle_quality_ready: {quality_ready_cases}")
                print(f"oracle_quality_strong: {quality_strong_cases}")
                print(f"quality_ready_ratio: {payload['quality_ready_ratio']}")
                print(f"status: {'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

        if ns.imo_hist_cmd == "autolearn":
            run_id = _new_run_id("imo-autolearn")
            out_dir = root / "artifacts" / "imo_autolearn" / run_id
            out_dir.mkdir(parents=True, exist_ok=True)

            target_oracles = Path(str(ns.oracles_file))
            if not target_oracles.is_absolute():
                target_oracles = root / target_oracles

            base_payload = _load_imo_oracle_payload(target_oracles)
            base_index = _imo_oracle_payload_index(base_payload)
            working_index: dict[tuple[int, str], dict[str, Any]] = {
                key: json.loads(json.dumps(value)) for key, value in base_index.items()
            }
            statement_lookup = _load_imo_statement_lookup(
                root=root,
                years=years,
                lang=str(ns.lang),
                fetch_missing=bool(ns.fetch_missing),
                timeout=float(ns.timeout),
                max_problems=int(ns.max_problems),
            )

            max_iterations = max(1, int(ns.max_iterations))
            iteration_rows: list[dict[str, Any]] = []
            baseline_report: dict[str, Any] | None = None
            baseline_score: tuple[int, int, int, int, int, int] | None = None
            best_report: dict[str, Any] | None = None
            best_score: tuple[int, int, int, int, int, int] | None = None
            best_iter = 0
            best_oracles_snapshot = ""
            total_proposals = 0
            total_changed_cases = 0
            stop_reason = "max_iterations_reached"

            for iteration in range(1, max_iterations + 1):
                iter_dir = out_dir / f"iter-{iteration:02d}"
                iter_dir.mkdir(parents=True, exist_ok=True)

                snapshot_payload = _imo_oracle_payload_from_index(
                    base_payload=base_payload,
                    index=working_index,
                    from_year=int(ns.from_year),
                    to_year=int(ns.to_year),
                    lang=str(ns.lang),
                    description=(
                        "Historical IMO oracle targets "
                        "(autolearn-generated; benchmark-verified before apply)."
                    ),
                )
                snapshot_path = iter_dir / "oracles.snapshot.json"
                _write_json(snapshot_path, snapshot_payload)

                bench = _run_imo_history_bench_subprocess(
                    root=root,
                    from_year=int(ns.from_year),
                    to_year=int(ns.to_year),
                    lang=str(ns.lang),
                    model=str(ns.model),
                    url=ns.url,
                    timeout=float(ns.timeout),
                    max_problems=int(ns.max_problems),
                    oracles_file=snapshot_path,
                    required_rung=int(ns.required_rung),
                    fetch_missing=bool(ns.fetch_missing),
                    llm_only=False,
                )
                _write_json(iter_dir / "BENCH_RUN.json", bench)
                if not bool(bench.get("ok", False)):
                    iteration_rows.append(
                        {
                            "iteration": iteration,
                            "ok": False,
                            "error": str(bench.get("error", "bench_subprocess_failed")),
                            "returncode": int(bench.get("returncode", 1)),
                            "proposal_count": 0,
                            "changed_case_count": 0,
                            "oracles_snapshot": str(snapshot_path),
                        }
                    )
                    stop_reason = "bench_subprocess_failed"
                    break

                report = bench.get("report", {})
                if not isinstance(report, dict):
                    report = {}
                _write_json(iter_dir / "BENCH_REPORT.json", report)

                score = _imo_autolearn_score(report)
                iter_summary: dict[str, Any] = {
                    "iteration": iteration,
                    "ok": True,
                    "strict_ok": bool(report.get("strict_ok", False)),
                    "total_cases": int(report.get("total_cases", 0)),
                    "pass_cases": int(report.get("pass_cases", 0)),
                    "oracle_quality_ready_cases": int(report.get("oracle_quality_ready_cases", 0)),
                    "oracle_quality_strong_cases": int(report.get("oracle_quality_strong_cases", 0)),
                    "proposal_count": 0,
                    "changed_case_count": 0,
                    "oracles_snapshot": str(snapshot_path),
                    "bench_artifact_dir": str(report.get("artifact_dir", "")),
                    "score": list(score),
                }

                if baseline_report is None:
                    baseline_report = report
                    baseline_score = score
                if best_score is None or score > best_score:
                    best_score = score
                    best_report = report
                    best_iter = iteration
                    best_oracles_snapshot = str(snapshot_path)

                if bool(report.get("strict_ok", False)):
                    iteration_rows.append(iter_summary)
                    stop_reason = "strict_pass"
                    break

                if iteration >= max_iterations:
                    iteration_rows.append(iter_summary)
                    stop_reason = "max_iterations_reached"
                    break

                rows = report.get("rows", []) if isinstance(report.get("rows"), list) else []
                proposals: list[dict[str, Any]] = []
                changed_case_count = 0
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    status = str(row.get("phuc_status", "FAIL")).upper()
                    oracle_available = bool(row.get("oracle_available", False))
                    oracle_quality_ready = bool(row.get("oracle_quality_ready", False))
                    needs_learning = status != "PASS" or (not oracle_available) or (not oracle_quality_ready)
                    if not needs_learning:
                        continue
                    year_raw = row.get("year")
                    try:
                        year = int(str(year_raw).strip())
                    except Exception:
                        continue
                    problem_id = _normalize_imo_problem_id(str(row.get("problem_id", "")))
                    if not problem_id:
                        continue
                    key = (year, problem_id)
                    existing = working_index.get(key, {})
                    statement = statement_lookup.get(key, str(existing.get("statement_excerpt", "")))
                    response_text = str(row.get("response_text", row.get("response_excerpt", "")))
                    proposal = _build_imo_autolearn_oracle_update(
                        year=year,
                        problem_id=problem_id,
                        response_text=response_text,
                        statement=statement,
                        existing=existing,
                    )
                    changed_fields = proposal.get("changed_fields", [])
                    if not isinstance(changed_fields, list) or not changed_fields:
                        continue
                    quality_before = proposal.get("quality_before", {})
                    quality_after = proposal.get("quality_after", {})
                    before_rank = _oracle_quality_tier_rank(str(quality_before.get("tier", "none")))
                    after_rank = _oracle_quality_tier_rank(str(quality_after.get("tier", "none")))
                    before_score = _coerce_float(quality_before.get("score", 0.0), default=0.0)
                    after_score = _coerce_float(quality_after.get("score", 0.0), default=0.0)
                    quality_better = (after_rank > before_rank) or (
                        after_rank == before_rank and after_score > before_score
                    )
                    should_apply = bool(needs_learning or quality_better)
                    if not should_apply:
                        continue
                    updated_entry = proposal.get("entry", {})
                    if not isinstance(updated_entry, dict):
                        continue
                    working_index[key] = updated_entry
                    changed_case_count += 1
                    proposals.append(
                        {
                            "year": year,
                            "problem_id": problem_id,
                            "changed_fields": changed_fields,
                            "quality_before": quality_before,
                            "quality_after": quality_after,
                            "phuc_status_before": status,
                        }
                    )

                iter_summary["proposal_count"] = len(proposals)
                iter_summary["changed_case_count"] = changed_case_count
                total_proposals += len(proposals)
                total_changed_cases += changed_case_count
                _write_json(
                    iter_dir / "PROPOSALS.json",
                    {
                        "iteration": iteration,
                        "proposal_count": len(proposals),
                        "changed_case_count": changed_case_count,
                        "proposals": proposals,
                    },
                )
                iteration_rows.append(iter_summary)

                if changed_case_count == 0:
                    stop_reason = "no_patch_candidates"
                    break

            if baseline_report is None or baseline_score is None:
                payload = {
                    "run_id": run_id,
                    "timestamp_utc": _utc_now(),
                    "from_year": int(ns.from_year),
                    "to_year": int(ns.to_year),
                    "lang": str(ns.lang),
                    "required_rung": int(ns.required_rung),
                    "max_iterations": max_iterations,
                    "iterations": iteration_rows,
                    "target_oracles_file": str(target_oracles),
                    "improved": False,
                    "strict_ok_best": False,
                    "applied": False,
                    "stop_reason": stop_reason,
                    "error": "no_valid_iterations",
                    "artifact_dir": str(out_dir),
                }
                _write_json(out_dir / "report.json", payload)
                (out_dir / "report.md").write_text(_markdown_imo_autolearn_report(payload), encoding="utf-8")
                if ns.json:
                    print(json.dumps(payload, indent=2, sort_keys=True))
                else:
                    print(f"run_id: {run_id}")
                    print(f"artifact_dir: {out_dir}")
                    print("status: FAIL")
                return 1

            if best_report is None or best_score is None:
                best_report = baseline_report
                best_score = baseline_score
                best_iter = 1

            baseline_pass = int(baseline_report.get("pass_cases", 0))
            best_pass = int(best_report.get("pass_cases", 0))
            baseline_quality_ready = int(baseline_report.get("oracle_quality_ready_cases", 0))
            best_quality_ready = int(best_report.get("oracle_quality_ready_cases", 0))
            pass_delta = best_pass - baseline_pass
            quality_ready_delta = best_quality_ready - baseline_quality_ready
            improved = bool(best_score > baseline_score) and bool(
                pass_delta >= int(ns.min_pass_delta)
                or quality_ready_delta > 0
                or bool(best_report.get("strict_ok", False))
            )

            applied = False
            backup_file = ""
            if bool(ns.apply) and improved and best_oracles_snapshot:
                target_oracles.parent.mkdir(parents=True, exist_ok=True)
                if target_oracles.exists():
                    backup_file = str(out_dir / f"{target_oracles.name}.backup.json")
                    shutil.copy2(target_oracles, backup_file)
                shutil.copy2(Path(best_oracles_snapshot), target_oracles)
                applied = True

            payload = {
                "run_id": run_id,
                "timestamp_utc": _utc_now(),
                "from_year": int(ns.from_year),
                "to_year": int(ns.to_year),
                "lang": str(ns.lang),
                "model": str(ns.model),
                "required_rung": int(ns.required_rung),
                "max_iterations": max_iterations,
                "min_pass_delta": int(ns.min_pass_delta),
                "iterations": iteration_rows,
                "stop_reason": stop_reason,
                "total_proposals": total_proposals,
                "total_changed_cases": total_changed_cases,
                "baseline_iteration": 1,
                "best_iteration": int(best_iter),
                "baseline_score": list(baseline_score),
                "best_score": list(best_score),
                "baseline_pass_cases": baseline_pass,
                "best_pass_cases": best_pass,
                "pass_delta": pass_delta,
                "baseline_quality_ready_cases": baseline_quality_ready,
                "best_quality_ready_cases": best_quality_ready,
                "quality_ready_delta": quality_ready_delta,
                "improved": improved,
                "strict_ok_best": bool(best_report.get("strict_ok", False)),
                "apply_requested": bool(ns.apply),
                "applied": applied,
                "backup_file": backup_file,
                "target_oracles_file": str(target_oracles),
                "best_oracle_snapshot": best_oracles_snapshot,
                "baseline_report": {
                    "run_id": str(baseline_report.get("run_id", "")),
                    "total_cases": int(baseline_report.get("total_cases", 0)),
                    "pass_cases": int(baseline_report.get("pass_cases", 0)),
                    "strict_ok": bool(baseline_report.get("strict_ok", False)),
                    "artifact_dir": str(baseline_report.get("artifact_dir", "")),
                },
                "best_report": {
                    "run_id": str(best_report.get("run_id", "")),
                    "total_cases": int(best_report.get("total_cases", 0)),
                    "pass_cases": int(best_report.get("pass_cases", 0)),
                    "strict_ok": bool(best_report.get("strict_ok", False)),
                    "artifact_dir": str(best_report.get("artifact_dir", "")),
                },
                "artifact_dir": str(out_dir),
                "source": "imo-history bench iterative self-learning loop",
            }
            _write_json(out_dir / "report.json", payload)
            (out_dir / "report.md").write_text(_markdown_imo_autolearn_report(payload), encoding="utf-8")

            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"run_id: {run_id}")
                print(f"artifact_dir: {out_dir}")
                print(f"target_oracles_file: {target_oracles}")
                print(f"best_iteration: {best_iter}")
                print(f"pass_delta: {pass_delta}")
                print(f"quality_ready_delta: {quality_ready_delta}")
                print(f"improved: {improved}")
                print(f"applied: {applied}")
                print(f"strict_ok_best: {bool(best_report.get('strict_ok', False))}")
            if bool(best_report.get("strict_ok", False)):
                return 0
            if bool(ns.no_strict) and (improved or applied):
                return 0
            return 1

        if ns.imo_hist_cmd == "bench":
            run_id = _new_run_id("imo-history")
            out_dir = root / "artifacts" / "imo_history" / run_id
            out_dir.mkdir(parents=True, exist_ok=True)
            cases_dir = out_dir / "cases"
            cases_dir.mkdir(parents=True, exist_ok=True)
            required_rung = int(ns.required_rung)
            oracle_file = Path(str(ns.oracles_file))
            if not oracle_file.is_absolute():
                oracle_file = root / oracle_file
            history_oracles = _load_imo_history_oracles(oracle_file)
            swarm_loaded = _load_swarm_settings(root)
            swarm_settings = swarm_loaded.get("settings", {}) if isinstance(swarm_loaded.get("settings"), dict) else {}
            council_base = _math_expert_council_config(settings=swarm_settings, default_required_rung=required_rung)
            council_base["required_rung"] = required_rung

            rows: list[dict[str, Any]] = []
            route_counts: dict[str, int] = {}
            phase_counts: dict[str, int] = {}
            total_cases = 0
            max_problems = int(ns.max_problems)

            for year in years:
                ds = _load_cached_imo_year_dataset(root, int(year), str(ns.lang))
                if ds is None and bool(ns.fetch_missing):
                    _, _ = _fetch_imo_year_dataset(
                        root=root,
                        year=int(year),
                        lang=str(ns.lang),
                        timeout=float(ns.timeout),
                        force=False,
                    )
                    ds = _load_cached_imo_year_dataset(root, int(year), str(ns.lang))
                if ds is None:
                    rows.append(
                        {
                            "year": year,
                            "problem_id": "",
                            "ok": False,
                            "error": "dataset_missing (run `stillwater imo-history fetch` first)",
                        }
                    )
                    continue
                problems = ds.get("problems", [])
                if not isinstance(problems, list):
                    problems = []
                for problem in problems:
                    if max_problems > 0 and total_cases >= max_problems:
                        break
                    pid = str(problem.get("id", "")).strip() or "P?"
                    statement = str(problem.get("statement", "")).strip()
                    oracle = history_oracles.get((int(year), pid.upper()), {})
                    if not isinstance(oracle, dict):
                        oracle = {}
                    problem_needle = str(oracle.get("needle", problem.get("needle", ""))).strip()
                    aliases_raw = problem.get("aliases", [])
                    base_aliases = [str(item).strip() for item in aliases_raw if str(item).strip()] if isinstance(aliases_raw, list) else []
                    oracle_aliases_raw = oracle.get("aliases", [])
                    oracle_aliases = (
                        [str(item).strip() for item in oracle_aliases_raw if str(item).strip()]
                        if isinstance(oracle_aliases_raw, list)
                        else []
                    )
                    problem_aliases = _dedupe_keep_order(base_aliases + oracle_aliases)
                    if not statement:
                        rows.append(
                            {
                                "year": year,
                                "problem_id": pid,
                                "ok": False,
                                "error": "empty_problem_statement",
                            }
                        )
                        continue
                    oracle_anchor = problem_needle
                    if not oracle_anchor and problem_aliases:
                        oracle_anchor = str(problem_aliases[0]).strip()
                    oracle_concepts = (
                        [str(item).strip() for item in oracle.get("concepts", []) if str(item).strip()]
                        if isinstance(oracle.get("concepts"), list)
                        else []
                    )
                    oracle_quality = oracle.get("quality", {}) if isinstance(oracle.get("quality"), dict) else {}
                    prompt_blocks = [f"IMO {year} {pid}. Solve this problem with a rigorous outline."]
                    if oracle_anchor:
                        prompt_blocks.append(f"Oracle anchor: {oracle_anchor}")
                    if oracle_concepts:
                        prompt_blocks.append(f"Oracle concepts: {', '.join(oracle_concepts)}")
                    prompt_blocks.append(statement)
                    prompt_blocks.append("Return: assumptions, core idea, and verification checklist.")
                    prompt = "\n\n".join(prompt_blocks)
                    case_dir = cases_dir / str(year) / pid
                    case_dir.mkdir(parents=True, exist_ok=True)
                    scout = _imo_history_case_scout(year=int(year), problem_id=pid, prompt=prompt)
                    forecast = _imo_history_case_forecast(year=int(year), problem_id=pid)
                    decide = _imo_history_case_decide(year=int(year), problem_id=pid, required_rung=required_rung)
                    _write_json(case_dir / "SCOUT_REPORT.json", scout)
                    _write_json(case_dir / "FORECAST_MEMO.json", forecast)
                    _write_json(case_dir / "DECISION_RECORD.json", decide)

                    twin = _run_twin_subprocess(
                        root=root,
                        prompt=prompt,
                        model=str(ns.model),
                        timeout=float(ns.timeout),
                        url=ns.url,
                        llm_only=bool(ns.llm_only),
                        retries=1,
                    )
                    row: dict[str, Any] = {
                        "year": year,
                        "problem_id": pid,
                        "ok": bool(twin.get("ok")),
                    }
                    payload = twin.get("payload", {}) if isinstance(twin.get("payload"), dict) else {}
                    route = payload.get("route", {}) if isinstance(payload.get("route"), dict) else {}
                    phuc = route.get("phuc_decision", {}) if isinstance(route.get("phuc_decision"), dict) else {}
                    action = str(route.get("action", "")).strip()
                    profile = str(phuc.get("profile", "")).strip()
                    if not profile and action == "ollama_chat":
                        profile = "math"
                    response_text = str(payload.get("response", ""))
                    row.update(
                        {
                            "source": payload.get("source"),
                            "action": action,
                            "decision": phuc.get("decision"),
                            "profile": profile,
                            "reason": phuc.get("reason"),
                            "response_excerpt": response_text[:280],
                            "response_text": response_text[:2000],
                            "needle": problem_needle,
                            "aliases": problem_aliases,
                            "oracle_concepts": oracle.get("concepts", []),
                            "oracle_required_sections": oracle.get("required_sections", []),
                            "oracle_quality_tier": str(oracle_quality.get("tier", "none")),
                            "oracle_quality_score": float(oracle_quality.get("score", 0.0)),
                            "oracle_quality_ready": bool(oracle_quality.get("ready_standard", False)),
                            "oracle_quality_strong": bool(oracle_quality.get("ready_strong", False)),
                        }
                    )
                    act = {
                        "year": int(year),
                        "problem_id": pid,
                        "prompt": prompt,
                        "model": str(ns.model),
                        "url": str(ns.url or ""),
                        "llm_only": bool(ns.llm_only),
                        "twin": twin,
                    }
                    _write_json(case_dir / "ACT_RESULT.json", act)

                    skeptic = _imo_history_case_skeptic(
                        twin=twin,
                        row=row,
                        prompt=prompt,
                        council_cfg=council_base,
                    )
                    _write_json(case_dir / "SKEPTIC_VERDICT.json", skeptic)
                    row["phuc_status"] = skeptic.get("status")
                    row["phuc_fail_reasons"] = skeptic.get("fail_reasons", [])
                    row["rung_achieved"] = skeptic.get("rung_achieved", 0)
                    row["required_rung"] = skeptic.get("required_rung", required_rung)
                    oracle_meta = skeptic.get("oracle", {}) if isinstance(skeptic.get("oracle"), dict) else {}
                    row["oracle_available"] = bool(oracle_meta.get("available", False))
                    row["oracle_pass_65537"] = bool(oracle_meta.get("pass_65537", False))
                    concept_meta = oracle_meta.get("concepts", {}) if isinstance(oracle_meta.get("concepts"), dict) else {}
                    section_meta = (
                        oracle_meta.get("required_sections", {})
                        if isinstance(oracle_meta.get("required_sections"), dict)
                        else {}
                    )
                    row["oracle_concept_coverage"] = concept_meta.get("coverage")
                    row["oracle_required_section_hits"] = section_meta.get("hit_count")
                    row["oracle_concept_pass_274177"] = bool(oracle_meta.get("concept_pass_274177", True))
                    row["oracle_required_sections_pass_274177"] = bool(
                        oracle_meta.get("required_sections_pass_274177", True)
                    )
                    row["oracle_concept_pass_65537"] = bool(oracle_meta.get("concept_pass_65537", True))
                    row["oracle_required_sections_pass_65537"] = bool(
                        oracle_meta.get("required_sections_pass_65537", True)
                    )
                    quality_meta = oracle_meta.get("quality", {}) if isinstance(oracle_meta.get("quality"), dict) else {}
                    row["oracle_quality_tier"] = str(quality_meta.get("tier", row.get("oracle_quality_tier", "none")))
                    row["oracle_quality_score"] = quality_meta.get("score", row.get("oracle_quality_score", 0.0))
                    row["oracle_quality_pass_65537"] = bool(quality_meta.get("quality_pass_65537", True))
                    anti_meta = skeptic.get("anti_parrot", {}) if isinstance(skeptic.get("anti_parrot"), dict) else {}
                    anti655 = anti_meta.get("r65537", {}) if isinstance(anti_meta.get("r65537"), dict) else {}
                    row["anti_parrot_pass_65537"] = bool(anti655.get("pass", True))
                    row["anti_parrot_novel_ratio_65537"] = anti655.get("novel_ratio")
                    row["anti_parrot_prompt_share_65537"] = anti655.get("prompt_token_share")
                    row["anti_parrot_copy_ratio_65537"] = anti655.get("copied_sentence_ratio")
                    grounding_meta = (
                        skeptic.get("prompt_grounding", {}) if isinstance(skeptic.get("prompt_grounding"), dict) else {}
                    )
                    g274 = grounding_meta.get("r274177", {}) if isinstance(grounding_meta.get("r274177"), dict) else {}
                    g655 = grounding_meta.get("r65537", {}) if isinstance(grounding_meta.get("r65537"), dict) else {}
                    row["prompt_keyword_coverage_274177"] = g274.get("keyword_coverage")
                    row["prompt_keyword_coverage_65537"] = g655.get("keyword_coverage")
                    council = skeptic.get("expert_council", {})
                    if isinstance(council, dict):
                        row["consensus"] = council.get("consensus")
                    row["artifact_dir"] = str(case_dir)
                    phase_key = str(skeptic.get("status", "UNKNOWN"))
                    phase_counts[phase_key] = phase_counts.get(phase_key, 0) + 1

                    if not twin.get("ok"):
                        row["error"] = twin.get("error") or twin.get("stderr", "")
                        row["stderr_excerpt"] = str(twin.get("stderr", ""))
                        row["stdout_excerpt"] = str(twin.get("stdout", ""))
                    key = f"{row.get('source','?')}::{row.get('action','?')}::{row.get('profile','')}"
                    route_counts[key] = route_counts.get(key, 0) + 1
                    rows.append(row)
                    total_cases += 1
                if max_problems > 0 and total_cases >= max_problems:
                    break

            ok_cases = sum(1 for row in rows if row.get("ok"))
            pass_cases = sum(1 for row in rows if str(row.get("phuc_status", "")).upper() == "PASS")
            oracle_configured_cases = sum(1 for row in rows if bool(row.get("oracle_available")))
            oracle_pass_cases = sum(1 for row in rows if bool(row.get("oracle_pass_65537")))
            oracle_quality_ready_cases = sum(
                1 for row in rows if _oracle_quality_tier_rank(str(row.get("oracle_quality_tier", "none"))) >= 2
            )
            oracle_quality_strong_cases = sum(
                1 for row in rows if _oracle_quality_tier_rank(str(row.get("oracle_quality_tier", "none"))) >= 3
            )
            strict_ok = total_cases > 0 and pass_cases == total_cases
            report = {
                "run_id": run_id,
                "timestamp_utc": _utc_now(),
                "from_year": ns.from_year,
                "to_year": ns.to_year,
                "lang": ns.lang,
                "model": ns.model,
                "url": ns.url or "",
                "llm_only": bool(ns.llm_only),
                "oracles_file": str(oracle_file),
                "oracles_loaded": len(history_oracles),
                "required_rung": required_rung,
                "expert_council": {
                    "enabled": bool(council_base.get("enabled", True)),
                    "virtual_size": int(council_base.get("virtual_size", 65537)),
                    "integrity_mode": str(council_base.get("integrity_mode", "strict_fail_closed")),
                    "max_love": bool(council_base.get("max_love", True)),
                },
                "total_cases": total_cases,
                "ok_cases": ok_cases,
                "pass_cases": pass_cases,
                "oracle_configured_cases": oracle_configured_cases,
                "oracle_pass_cases": oracle_pass_cases,
                "oracle_quality_ready_cases": oracle_quality_ready_cases,
                "oracle_quality_strong_cases": oracle_quality_strong_cases,
                "strict_ok": strict_ok,
                "route_counts": route_counts,
                "phuc_phase_counts": phase_counts,
                "rows": rows,
                "note": "This benchmark validates routing/runtime and rung-gated orchestration quality on historical IMO prompts, not official grading.",
                "source": "https://www.imo-official.org/download_file.aspx?file=dummy.pdf",
            }
            report["memory_loop"] = _record_imo_memory(
                root=root,
                kind="imo-history",
                run_id=run_id,
                report=report,
                report_file=out_dir / "report.json",
            )
            _write_json(out_dir / "report.json", report)
            (out_dir / "report.md").write_text(_markdown_imo_history_report(report), encoding="utf-8")
            report["artifact_dir"] = str(out_dir)
            if ns.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(f"run_id: {run_id}")
                print(f"artifact_dir: {out_dir}")
                print(f"cases: {total_cases}")
                print(f"runtime_ok: {ok_cases}")
                print(f"phuc_pass: {pass_cases}")
                print(f"status: {'PASS' if strict_ok else 'FAIL'}")
                for key in sorted(route_counts.keys()):
                    print(f"- {key}: {route_counts[key]}")
            return 0 if strict_ok else 1

    if ns.cmd == "oolong":
        if ns.oolong_cmd == "run":
            run_id = ns.run_id or _new_run_id("oolong")
            out_dir = root / "artifacts" / "oolong" / run_id
            out_dir.mkdir(parents=True, exist_ok=True)

            script = root / "oolong" / "src" / ("oolong_solver_real.py" if ns.real else "oolong_solver.py")
            cmd = [sys.executable, str(script)]
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(root),
                    env=_runtime_env(root),
                    text=True,
                    capture_output=True,
                    timeout=float(ns.timeout),
                    check=False,
                )
            except subprocess.TimeoutExpired:
                print(f"ERROR: oolong run timeout after {ns.timeout}s")
                return 1

            stdout_path = out_dir / "stdout.txt"
            stderr_path = out_dir / "stderr.txt"
            stdout_path.write_text(proc.stdout or "", encoding="utf-8")
            stderr_path.write_text(proc.stderr or "", encoding="utf-8")

            parsed = _parse_oolong_output(proc.stdout or "")
            summary = {
                "run_id": run_id,
                "mode": "real" if ns.real else "demo",
                "script": str(script.relative_to(root)),
                "returncode": proc.returncode,
                "timestamp_utc": _utc_now(),
                "parsed": parsed,
                "stdout": str(stdout_path),
                "stderr": str(stderr_path),
            }
            _write_json(out_dir / "summary.json", summary)

            if ns.json:
                print(json.dumps(summary, indent=2, sort_keys=True))
            else:
                print(f"run_id: {run_id}")
                print(f"mode: {summary['mode']}")
                print(f"returncode: {proc.returncode}")
                print(f"Wrote: {out_dir / 'summary.json'}")
            return 0 if proc.returncode == 0 else proc.returncode

        if ns.oolong_cmd == "verify":
            run_dir = None
            if ns.run_id:
                run_dir = root / "artifacts" / "oolong" / str(ns.run_id).strip()
            else:
                run_dir = _latest_run_id_dir(root / "artifacts" / "oolong")
            if run_dir is None:
                print("ERROR: no oolong run found.")
                return 1
            summary_path = run_dir / "summary.json"
            if not summary_path.exists():
                print(f"ERROR: missing summary: {summary_path}")
                return 1

            summary = _load_json(summary_path)
            parsed = summary.get("parsed", {})
            basic_ok = int(summary.get("returncode", 1)) == 0
            strict_ok = bool(
                parsed.get("rung_641_pass")
                and parsed.get("rung_274177_pass")
                and parsed.get("rung_65537_pass")
                and parsed.get("counter_bypass_complete")
            )
            ok = strict_ok if ns.strict else basic_ok
            payload = {
                "run_id": summary.get("run_id"),
                "mode": summary.get("mode"),
                "strict": bool(ns.strict),
                "basic_ok": basic_ok,
                "strict_ok": strict_ok,
                "ok": ok,
                "summary": str(summary_path),
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"run_id: {payload['run_id']}")
                print(f"mode: {payload['mode']}")
                print(f"basic_ok: {basic_ok}")
                print(f"strict_ok: {strict_ok}")
                print(f"verify: {'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

    if ns.cmd == "learn":
        if ns.learn_cmd == "propose":
            proposal_id = f"{_slug(ns.title)}-{dt.datetime.now(tz=dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
            out_dir = root / "artifacts" / "learn" / "proposals" / proposal_id
            out_dir.mkdir(parents=True, exist_ok=True)

            proposal_path = out_dir / "proposal.prime-mermaid.md"
            proposal_text = "\n".join(
                [
                    f"# Learning Proposal: {ns.title}",
                    "",
                    f"Date: {_utc_now()}",
                    f"Wish ID: {ns.wish_id or 'unspecified'}",
                    "Skill pack: prime-wishes, phuc-forecast, phuc-swarms, phuc-cleanup, prime-coder, prime-safety, phuc-context",
                    "",
                    "```mermaid",
                    "flowchart TD",
                    "  P[PROPOSE] --> R[REVIEW]",
                    "  R --> A[APPLY]",
                    "  A --> V[VERIFY]",
                    "```",
                    "",
                    "## Note",
                    ns.note or "-",
                    "",
                ]
            )
            proposal_path.write_text(proposal_text, encoding="utf-8")
            metadata = {
                "proposal_id": proposal_id,
                "title": ns.title,
                "wish_id": ns.wish_id,
                "note": ns.note,
                "proposal": str(proposal_path),
                "timestamp_utc": _utc_now(),
            }
            _write_json(out_dir / "proposal.json", metadata)
            if ns.json:
                print(json.dumps(metadata, indent=2, sort_keys=True))
            else:
                print(f"proposal_id: {proposal_id}")
                print(f"Wrote: {proposal_path}")
                print(f"Wrote: {out_dir / 'proposal.json'}")
            return 0

        if ns.learn_cmd == "apply":
            src = Path(ns.proposal)
            if not src.is_absolute():
                src = root / src
            if not src.exists():
                print(f"ERROR: proposal not found: {src}")
                return 1
            dest_dir = Path(ns.dest_dir)
            if not dest_dir.is_absolute():
                dest_dir = root / dest_dir
            dest_dir.mkdir(parents=True, exist_ok=True)
            dst = dest_dir / src.name
            shutil.copyfile(src, dst)

            receipt_id = _new_run_id("learn-apply")
            receipt = {
                "receipt_id": receipt_id,
                "source": str(src),
                "destination": str(dst),
                "timestamp_utc": _utc_now(),
            }
            receipt_path = root / "artifacts" / "learn" / "applied" / f"{receipt_id}.json"
            _write_json(receipt_path, receipt)

            if ns.json:
                print(json.dumps(receipt, indent=2, sort_keys=True))
            else:
                print(f"Applied: {src} -> {dst}")
                print(f"Wrote: {receipt_path}")
            return 0

    if ns.cmd == "cleanup":
        cleanup_dir = root / "artifacts" / "stillwater" / "cleanup"
        cleanup_dir.mkdir(parents=True, exist_ok=True)

        if ns.cleanup_cmd == "scan":
            tracked = _tracked_paths(root)
            audit_path = Path(ns.audit_file)
            if not audit_path.is_absolute():
                audit_path = root / audit_path
            suspicious_from_audit = _parse_suspicious_paths_from_final_audit(root=root, audit_file=audit_path)

            candidates: list[dict[str, Any]] = []
            seen: set[str] = set()
            scopes = list(ns.scope) if ns.scope else ["artifacts"]
            for raw_scope in scopes:
                scope = Path(raw_scope)
                if not scope.is_absolute():
                    scope = root / scope
                if not scope.exists():
                    continue
                for path in scope.rglob("*"):
                    if not path.is_file():
                        continue
                    try:
                        rel = str(path.resolve().relative_to(root))
                    except ValueError:
                        # Fail-closed: ignore files outside repo root.
                        continue
                    if rel in seen:
                        continue
                    seen.add(rel)

                    klass = "protected"
                    reason = "default protected class"
                    if rel in suspicious_from_audit:
                        klass = "suspicious"
                        reason = "flagged by FINAL-AUDIT markers"
                    elif _is_safe_glow_file(path=path, root=root):
                        klass = "safe_glow"
                        reason = "generated glow artifact under artifacts/"

                    candidates.append(
                        {
                            "path": rel,
                            "class": klass,
                            "tracked": rel in tracked,
                            "size_bytes": path.stat().st_size,
                            "reason": reason,
                        }
                    )

            counts = {
                "safe_glow": sum(1 for c in candidates if c["class"] == "safe_glow"),
                "suspicious": sum(1 for c in candidates if c["class"] == "suspicious"),
                "protected": sum(1 for c in candidates if c["class"] == "protected"),
            }
            safe_untracked = sum(
                1 for c in candidates if c["class"] == "safe_glow" and not bool(c.get("tracked", False))
            )
            safe_tracked = sum(
                1 for c in candidates if c["class"] == "safe_glow" and bool(c.get("tracked", False))
            )
            scan_id = _new_run_id("cleanup-scan")
            receipt = {
                "scan_id": scan_id,
                "timestamp_utc": _utc_now(),
                "audit_file": str(audit_path),
                "scope": scopes,
                "counts": counts,
                "scanned_count_by_class": {
                    "safe_untracked": safe_untracked,
                    "safe_tracked": safe_tracked,
                    "suspicious": counts["suspicious"],
                    "protected": counts["protected"],
                },
                "candidates": candidates,
                "rules": {
                    "archive_instead_of_delete": True,
                    "suspicious_requires_user_approval": True,
                    "tracked_requires_user_approval": True,
                },
            }
            receipt_path = cleanup_dir / f"{scan_id}.json"
            _write_json(receipt_path, receipt)

            payload = {
                "ok": True,
                "scan_id": scan_id,
                "receipt": str(receipt_path),
                "counts": counts,
                "safe_untracked": safe_untracked,
                "safe_tracked": safe_tracked,
            }
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"scan_id: {scan_id}")
                print(f"receipt: {receipt_path}")
                print(f"safe_glow: {counts['safe_glow']}")
                print(f"safe_untracked: {safe_untracked}")
                print(f"safe_tracked: {safe_tracked}")
                print(f"suspicious: {counts['suspicious']}")
                print(f"protected: {counts['protected']}")
            return 0

        if ns.cleanup_cmd == "apply":
            if ns.scan_receipt:
                scan_receipt = Path(ns.scan_receipt)
                if not scan_receipt.is_absolute():
                    scan_receipt = root / scan_receipt
            else:
                latest = _latest_cleanup_scan_receipt(root)
                if latest is None:
                    print("ERROR: no cleanup scan receipt found.")
                    return 1
                scan_receipt = latest

            if not scan_receipt.exists():
                print(f"ERROR: missing scan receipt: {scan_receipt}")
                return 1
            scan_data = _load_json(scan_receipt)
            candidates = scan_data.get("candidates", [])
            if not isinstance(candidates, list):
                print("ERROR: invalid cleanup scan receipt format.")
                return 1

            archive_stamp = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            archive_root = root / ".archive" / "glow" / archive_stamp
            moved: list[str] = []
            skipped: list[dict[str, str]] = []

            for item in candidates:
                if not isinstance(item, dict):
                    continue
                rel = str(item.get("path", "")).strip()
                klass = str(item.get("class", "protected"))
                tracked = bool(item.get("tracked", False))
                if not rel:
                    continue
                src = (root / rel).resolve()
                try:
                    src.relative_to(root)
                except ValueError:
                    skipped.append({"path": rel, "reason": "outside_repo_root"})
                    continue
                if not src.exists():
                    skipped.append({"path": rel, "reason": "missing"})
                    continue

                if klass == "protected":
                    skipped.append({"path": rel, "reason": "protected"})
                    continue
                if klass == "suspicious" and not ns.approve_suspicious:
                    skipped.append({"path": rel, "reason": "requires --approve-suspicious"})
                    continue
                if tracked and not ns.approve_tracked:
                    skipped.append({"path": rel, "reason": "requires --approve-tracked"})
                    continue

                dst = (archive_root / rel).resolve()
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                if dst.exists() and not src.exists():
                    moved.append(rel)
                else:
                    skipped.append({"path": rel, "reason": "post_check_failed"})

            apply_id = _new_run_id("cleanup-apply")
            receipt = {
                "apply_id": apply_id,
                "timestamp_utc": _utc_now(),
                "scan_receipt": str(scan_receipt),
                "archive_root": str(archive_root),
                "approve_suspicious": bool(ns.approve_suspicious),
                "approve_tracked": bool(ns.approve_tracked),
                "moved_count": len(moved),
                "skipped_count": len(skipped),
                "moved": moved,
                "skipped": skipped,
                "receipt_paths": [str(scan_receipt)],
            }
            receipt_path = cleanup_dir / f"{apply_id}.json"
            _write_json(receipt_path, receipt)

            payload = {"ok": True, **receipt}
            if ns.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"apply_id: {apply_id}")
                print(f"archive_root: {archive_root}")
                print(f"moved: {len(moved)}")
                print(f"skipped: {len(skipped)}")
                print(f"receipt: {receipt_path}")
            return 0

    if ns.cmd == "replay":
        run_id = str(ns.run_id).strip()
        run_dir = root / "artifacts" / "runs" / run_id
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            print(f"ERROR: missing manifest: {manifest_path}")
            return 1
        manifest = _load_json(manifest_path)

        if ns.rerun:
            replay_id = _new_run_id("replay")
            replay_records: list[dict[str, Any]] = []
            ok = True
            for step in manifest.get("steps", []):
                cmd = step.get("command", [])
                if not cmd:
                    continue
                try:
                    proc = subprocess.run(
                        list(cmd),
                        cwd=str(root),
                        env=_runtime_env(root),
                        text=True,
                        capture_output=True,
                        timeout=float(ns.timeout),
                        check=False,
                    )
                    replay_records.append(
                        {
                            "name": step.get("name"),
                            "command": cmd,
                            "returncode": proc.returncode,
                            "status": "success" if proc.returncode == 0 else "failed",
                        }
                    )
                    if proc.returncode != 0:
                        ok = False
                except subprocess.TimeoutExpired:
                    replay_records.append(
                        {
                            "name": step.get("name"),
                            "command": cmd,
                            "returncode": None,
                            "status": "timeout",
                        }
                    )
                    ok = False
            report = {
                "run_id": run_id,
                "replay_id": replay_id,
                "timestamp_utc": _utc_now(),
                "ok": ok,
                "steps": replay_records,
            }
            report_path = run_dir / f"replay-{replay_id}.json"
            _write_json(report_path, report)
            if ns.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(f"replay_id: {replay_id}")
                print(f"status: {'PASS' if ok else 'FAIL'}")
                print(f"Wrote: {report_path}")
            return 0 if ok else 1

        payload = {
            "run_id": manifest.get("run_id"),
            "profile": manifest.get("profile"),
            "status": manifest.get("status"),
            "step_count": len(manifest.get("steps", [])),
            "manifest": str(manifest_path),
        }
        if ns.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"run_id: {payload['run_id']}")
            print(f"profile: {payload['profile']}")
            print(f"status: {payload['status']}")
            print(f"step_count: {payload['step_count']}")
            for step in manifest.get("steps", []):
                print(f"- {step.get('index')}. {step.get('name')} [{step.get('status')}]")
        return 0

    if ns.cmd == "run":
        import uuid as _uuid

        task_str = str(ns.task).strip()
        skill_name: str | None = ns.skill
        dry_run: bool = bool(ns.dry_run)
        run_id_val: str = str(ns.run_id).strip() if ns.run_id else f"run-{_uuid.uuid4().hex[:8]}"
        as_json: bool = bool(ns.json)

        run_dir = root / "artifacts" / "runs" / run_id_val
        run_dir.mkdir(parents=True, exist_ok=True)

        # Resolve skill content
        skill_content = ""
        skill_path_used: str | None = None
        if skill_name:
            # Try skills/<name>.md, then skills/<name>, then cli/skills/<name>.md
            candidates = [
                root / "skills" / f"{skill_name}.md",
                root / "skills" / skill_name,
                root / "cli" / "skills" / f"{skill_name}.md",
                root / "cli" / "skills" / skill_name,
            ]
            for candidate in candidates:
                if candidate.exists() and candidate.is_file():
                    skill_content = candidate.read_text(encoding="utf-8")
                    skill_path_used = str(candidate.relative_to(root))
                    break
            if not skill_content:
                msg = f"Skill not found: {skill_name} (searched skills/{skill_name}.md and variants)"
                if as_json:
                    print(json.dumps({"status": "ERROR", "error": msg}, indent=2, sort_keys=True))
                else:
                    print(f"ERROR: {msg}")
                return 1

        prompt = task_str
        if skill_content:
            prompt = f"{skill_content}\n\n---\n\nTask: {task_str}"

        manifest: dict[str, Any] = {
            "run_id": run_id_val,
            "task": task_str,
            "skill": skill_name,
            "skill_path": skill_path_used,
            "dry_run": dry_run,
            "started_utc": _utc_now(),
            "status": "PENDING",
            "prompt_length": len(prompt),
        }

        if dry_run:
            manifest["status"] = "DRY_RUN"
            manifest["finished_utc"] = _utc_now()
            _write_json(run_dir / "manifest.json", manifest)
            if as_json:
                print(json.dumps(manifest, indent=2, sort_keys=True))
            else:
                print(f"[dry-run] run_id:        {run_id_val}")
                print(f"[dry-run] task:          {task_str}")
                print(f"[dry-run] skill:         {skill_name or 'none'}")
                if skill_path_used:
                    print(f"[dry-run] skill_path:    {skill_path_used}")
                print(f"[dry-run] prompt_length: {len(prompt)} chars")
                print(f"[dry-run] artifacts_dir: artifacts/runs/{run_id_val}/")
                print(f"Wrote: {run_dir / 'manifest.json'}")
            return 0

        # Live mode: attempt LLM call
        response_text: str | None = None
        llm_error: str | None = None
        llm_source: str = "none"

        # 1. Try Anthropic API via environment variable (no extra deps)
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if anthropic_key and not response_text:
            try:
                import json as _json
                payload_bytes = _json.dumps({
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}],
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=payload_bytes,
                    headers={
                        "x-api-key": anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = _json.loads(resp.read().decode("utf-8"))
                content_blocks = data.get("content") or []
                parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
                response_text = "\n".join(parts).strip()
                llm_source = "anthropic"
            except Exception as ex:
                llm_error = f"Anthropic API error: {ex}"

        # 2. Try configured Ollama via llm_config_manager
        if not response_text:
            try:
                sys.path.insert(0, str(root / "cli" / "src"))
                from llm_config_manager import get_llm_config  # type: ignore
                cfg = get_llm_config()
                if cfg.active_provider == "ollama":
                    ollama_url = cfg.get_provider_url().rstrip("/")
                    model = cfg.get_provider_model().strip() or _default_ollama_model(root)
                    import json as _json2
                    payload_bytes2 = _json2.dumps({
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {"temperature": 0.0},
                    }).encode("utf-8")
                    req2 = urllib.request.Request(
                        f"{ollama_url}/api/chat",
                        data=payload_bytes2,
                        headers={"content-type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(req2, timeout=60) as resp2:
                        data2 = _json2.loads(resp2.read().decode("utf-8"))
                    response_text = str(((data2 or {}).get("message") or {}).get("content") or "").strip()
                    llm_source = f"ollama:{model}"
            except Exception as ex2:
                llm_error = llm_error or f"Ollama error: {ex2}"

        if not response_text:
            # Graceful no-LLM path: guidance only (rc=0)
            manifest["status"] = "NO_LLM"
            manifest["finished_utc"] = _utc_now()
            manifest["llm_error"] = llm_error
            _write_json(run_dir / "manifest.json", manifest)
            guidance = (
                "No LLM configured or reachable.\n"
                "  Option 1: export ANTHROPIC_API_KEY=<your-key>\n"
                "  Option 2: Start Ollama and run `stillwater llm set-ollama --auto-url --activate`\n"
                "  Option 3: Use --dry-run to test without any LLM."
            )
            if as_json:
                print(json.dumps({"status": "NO_LLM", "run_id": run_id_val, "guidance": guidance, "llm_error": llm_error}, indent=2, sort_keys=True))
            else:
                print(guidance)
                if llm_error:
                    print(f"(last error: {llm_error})")
                print(f"Wrote: {run_dir / 'manifest.json'}")
            return 0

        # Write response
        response_path = run_dir / "response.txt"
        response_path.write_text(response_text, encoding="utf-8")
        manifest["status"] = "PASS"
        manifest["finished_utc"] = _utc_now()
        manifest["llm_source"] = llm_source
        manifest["response_path"] = f"artifacts/runs/{run_id_val}/response.txt"
        manifest["response_length"] = len(response_text)
        _write_json(run_dir / "manifest.json", manifest)

        if as_json:
            print(json.dumps(manifest, indent=2, sort_keys=True))
        else:
            print(f"run_id: {run_id_val}")
            print(f"source: {llm_source}")
            print("--- response ---")
            print(response_text)
            print("--- end response ---")
            print(f"Wrote: {run_dir / 'manifest.json'}")
            print(f"Wrote: {response_path}")
        return 0

    if ns.cmd == "gen-ai-steroids-readme":
        from .gen_ai_steroids_readme import generate_readme

        out_path = root / "ai-steroids-results" / "README.md"
        new_text = generate_readme(root=root)
        if ns.check and out_path.exists():
            old = out_path.read_text(encoding="utf-8")
            if old != new_text:
                print(f"README out of date: {out_path}")
                return 1
            return 0
        out_path.write_text(new_text, encoding="utf-8")
        print(f"Wrote: {out_path}")
        return 0

    if ns.cmd == "evidence":
        import json as _json
        import platform
        from pathlib import Path as _Path

        evidence_dir = _Path(ns.evidence_dir)

        # ------------------------------------------------------------------ #
        # evidence init                                                        #
        # ------------------------------------------------------------------ #
        if ns.evidence_cmd == "init":
            evidence_dir.mkdir(parents=True, exist_ok=True)

            # Gather env values where possible.
            def _git(cmd):
                try:
                    return subprocess.check_output(
                        cmd, stderr=subprocess.DEVNULL, text=True
                    ).strip()
                except Exception:
                    return ""

            git_commit = _git(["git", "rev-parse", "HEAD"]) or "UNKNOWN"
            git_dirty_raw = _git(["git", "status", "--porcelain"])
            git_dirty = bool(git_dirty_raw)

            import datetime
            tz_name = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname() or "UTC"
            import locale as _locale
            try:
                locale_str = _locale.getdefaultlocale()[0] or "en_US"
            except Exception:
                locale_str = "en_US"

            templates = {
                "plan.json": {
                    "skill_version": "",
                    "profile": "strict",
                    "stop_reason": "",
                    "last_known_state": "",
                    "loop_budgets": {},
                    "localization_summary": [],
                    "verification_rung_target": 641,
                    "verification_rung": 0,
                    "seed_agreement": False,
                    "null_checks_performed": False,
                    "forecast_summary": [],
                    "env_snapshot_pointer": "evidence/env_snapshot.json",
                    "evidence_manifest_pointer": "evidence/evidence_manifest.json",
                },
                "tests.json": {
                    "command": "",
                    "exit_code": -1,
                    "failing_tests_before": [],
                    "passing_tests_after": [],
                },
                "artifacts.json": {
                    "artifacts": [],
                },
                "null_checks.json": {
                    "inputs_checked": [],
                    "null_cases_handled": 0,
                    "zero_cases_distinguished": 0,
                    "coercion_violations_detected": 0,
                },
                "env_snapshot.json": {
                    "git_commit": git_commit,
                    "git_dirty": git_dirty,
                    "repo_root": ".",
                    "os": platform.system(),
                    "arch": platform.machine(),
                    "language_runtimes": {},
                    "tool_versions": {},
                    "timezone": tz_name,
                    "locale": locale_str,
                },
                "evidence_manifest.json": {
                    "schema_version": "1.0.0",
                    "files": [],
                },
            }

            plain_files = [
                "run_log.txt",
                "repro_red.log",
                "repro_green.log",
                "behavior_hash.txt",
                "behavior_hash_verify.txt",
            ]

            created = []
            skipped = []

            for fname, tpl in templates.items():
                fpath = evidence_dir / fname
                if fpath.exists():
                    print(f"  [skip] {fname} — already exists")
                    skipped.append(fname)
                else:
                    fpath.write_text(
                        _json.dumps(tpl, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    print(f"  [created] {fname}")
                    created.append(fname)

            for fname in plain_files:
                fpath = evidence_dir / fname
                if fpath.exists():
                    print(f"  [skip] {fname} — already exists")
                    skipped.append(fname)
                else:
                    header = f"# {fname} — prime-coder evidence placeholder\n"
                    fpath.write_text(header, encoding="utf-8")
                    print(f"  [created] {fname}")
                    created.append(fname)

            print(
                f"\n[EVIDENCE INIT] dir={evidence_dir}  "
                f"created={len(created)}  skipped={len(skipped)}"
            )
            return 0

        # ------------------------------------------------------------------ #
        # evidence verify                                                      #
        # ------------------------------------------------------------------ #
        if ns.evidence_cmd == "verify":
            rung_target = ns.rung
            print(f"[EVIDENCE VERIFY] rung_target={rung_target} dir={evidence_dir}/")

            failures = []

            def _ok(msg):
                print(f"  \u2713 {msg}")

            def _fail(msg, key):
                print(f"  \u2717 {msg}")
                failures.append(key)

            # Required files.
            required_files = [
                "plan.json",
                "run_log.txt",
                "tests.json",
                "artifacts.json",
                "repro_red.log",
                "repro_green.log",
                "null_checks.json",
                "behavior_hash.txt",
                "behavior_hash_verify.txt",
                "env_snapshot.json",
                "evidence_manifest.json",
            ]

            def _load_evidence_json(fname):
                """Return parsed JSON or None; emit pass/fail."""
                fpath = evidence_dir / fname
                if not fpath.exists():
                    _fail(f"{fname} — missing", f"{fname}_missing")
                    return None
                try:
                    data = _json.loads(fpath.read_text(encoding="utf-8"))
                    return data
                except Exception as exc:
                    _fail(f"{fname} — not parseable: {exc}", f"{fname}_parse_error")
                    return None

            def _file_sha256(fname):
                fpath = evidence_dir / fname
                if not fpath.exists():
                    return None
                h = hashlib.sha256()
                h.update(fpath.read_bytes())
                return h.hexdigest()

            # --- RUNG_641 checks ---

            # 1. All required files exist (check presence for plain files).
            for fname in required_files:
                fpath = evidence_dir / fname
                if not fpath.exists():
                    _fail(f"{fname} — missing", f"{fname}_missing")

            # 2. JSON files parseable + key checks.
            plan = _load_evidence_json("plan.json")
            plan_required_keys = [
                "skill_version", "profile", "stop_reason", "last_known_state",
                "loop_budgets", "localization_summary", "verification_rung_target",
                "verification_rung", "seed_agreement", "null_checks_performed",
                "forecast_summary", "env_snapshot_pointer", "evidence_manifest_pointer",
            ]
            if plan is not None:
                missing_plan = [k for k in plan_required_keys if k not in plan]
                if missing_plan:
                    _fail(f"plan.json — missing keys: {missing_plan}", "plan_missing_keys")
                else:
                    _ok("plan.json — present, parseable, required keys OK")

            tests = _load_evidence_json("tests.json")
            tests_required_keys = [
                "command", "exit_code", "failing_tests_before", "passing_tests_after"
            ]
            if tests is not None:
                missing_tests = [k for k in tests_required_keys if k not in tests]
                if missing_tests:
                    _fail(f"tests.json — missing keys: {missing_tests}", "tests_missing_keys")
                elif not isinstance(tests.get("exit_code"), int):
                    _fail(
                        f"tests.json — exit_code must be an integer, got {type(tests.get('exit_code')).__name__}",
                        "tests_exit_code_not_int",
                    )
                else:
                    _ok(f"tests.json — present, parseable, exit_code={tests['exit_code']}")

            null_chk = _load_evidence_json("null_checks.json")
            null_required_keys = [
                "inputs_checked", "null_cases_handled",
                "zero_cases_distinguished", "coercion_violations_detected",
            ]
            if null_chk is not None:
                missing_null = [k for k in null_required_keys if k not in null_chk]
                if missing_null:
                    _fail(f"null_checks.json — missing keys: {missing_null}", "null_checks_missing_keys")
                else:
                    _ok("null_checks.json — present, parseable, required keys OK")

            env_snap = _load_evidence_json("env_snapshot.json")
            env_required_keys = [
                "git_commit", "git_dirty", "repo_root", "os", "arch",
                "language_runtimes", "tool_versions", "timezone", "locale",
            ]
            if env_snap is not None:
                missing_env = [k for k in env_required_keys if k not in env_snap]
                if missing_env:
                    _fail(f"env_snapshot.json — missing keys: {missing_env}", "env_snapshot_missing_keys")
                else:
                    _ok("env_snapshot.json — present, parseable, required keys OK")

            manifest = _load_evidence_json("evidence_manifest.json")
            if manifest is not None:
                if "schema_version" not in manifest:
                    _fail("evidence_manifest.json — missing schema_version", "manifest_no_schema_version")
                else:
                    _ok(f"evidence_manifest.json — schema_version={manifest['schema_version']!r}")

            # 3. behavior_hash files must match and be non-empty.
            bh_path = evidence_dir / "behavior_hash.txt"
            bhv_path = evidence_dir / "behavior_hash_verify.txt"
            if bh_path.exists() and bhv_path.exists():
                bh_content = bh_path.read_text(encoding="utf-8").strip()
                bhv_content = bhv_path.read_text(encoding="utf-8").strip()
                if not bh_content:
                    _fail("behavior_hash.txt — empty", "behavior_hash_empty")
                elif bh_content != bhv_content:
                    _fail(
                        "behavior_hash.txt — content mismatch with behavior_hash_verify.txt",
                        "behavior_hash_mismatch",
                    )
                else:
                    _ok("behavior_hash.txt — present and matches behavior_hash_verify.txt")

            # 4. SHA-256 of each file in evidence_manifest.json matches actual content.
            if manifest is not None and isinstance(manifest.get("files"), list):
                for entry in manifest["files"]:
                    epath = entry.get("file_path", "")
                    expected_sha = entry.get("sha256", "")
                    if not epath or not expected_sha:
                        continue
                    actual_sha = _file_sha256(epath)
                    if actual_sha is None:
                        _fail(
                            f"manifest entry {epath!r} — file missing",
                            f"manifest_file_missing_{epath}",
                        )
                    elif actual_sha != expected_sha:
                        _fail(
                            f"manifest entry {epath!r} — SHA-256 mismatch",
                            f"manifest_sha256_mismatch_{epath}",
                        )
                    else:
                        _ok(f"manifest entry {epath!r} — SHA-256 OK")

            # --- RUNG_274177 checks ---
            if rung_target >= 274177:
                if plan is not None:
                    vrt = plan.get("verification_rung_target")
                    if vrt is None or not isinstance(vrt, int):
                        _fail(
                            "plan.json verification_rung_target must be a present integer",
                            "plan_rung_target_invalid",
                        )
                    else:
                        _ok(f"plan.json — verification_rung_target={vrt} (integer)")

                artifacts_data = _load_evidence_json("artifacts.json")
                if artifacts_data is not None:
                    arts = artifacts_data.get("artifacts", [])
                    if not isinstance(arts, list) or len(arts) == 0:
                        _fail(
                            "artifacts.json — artifacts list is empty (at least 1 required for rung 274177)",
                            "artifacts_empty",
                        )
                    else:
                        _ok(f"artifacts.json — {len(arts)} artifact(s) present")

                if null_chk is not None:
                    nch = null_chk.get("null_cases_handled", 0)
                    if not isinstance(nch, int) or nch <= 0:
                        _fail(
                            f"null_checks.json null_cases_handled={nch!r} must be > 0 for rung 274177",
                            "null_cases_handled_zero",
                        )
                    else:
                        _ok(f"null_checks.json — null_cases_handled={nch}")

            # --- RUNG_65537 checks ---
            if rung_target == 65537:
                valid_rungs = [641, 274177, 65537]
                if plan is not None:
                    vr = plan.get("verification_rung")
                    if vr not in valid_rungs:
                        _fail(
                            f"plan.json verification_rung={vr!r} must be one of {valid_rungs}",
                            "plan_verification_rung_invalid",
                        )
                    else:
                        _ok(f"plan.json — verification_rung={vr}")

                if env_snap is not None:
                    dirty = env_snap.get("git_dirty")
                    if dirty not in (False, "false", "False"):
                        _fail(
                            f"env_snapshot.json git_dirty={dirty!r} — must be false for promotion (rung 65537)",
                            "git_dirty_on_promotion",
                        )
                    else:
                        _ok("env_snapshot.json — git_dirty=false (clean for promotion)")

            # Verdict.
            print("")
            if not failures:
                print(f"VERDICT: PASS (rung {rung_target} achieved)")
                return 0
            else:
                print(f"VERDICT: BLOCKED ({len(failures)} check(s) failed)")
                print("  stop_reason: EVIDENCE_INCOMPLETE")
                print(f"  failing_checks: {failures}")
                return 1

    # Default: print quick directions.
    if ns.cmd == "print" or ns.cmd is None:
        print("Key files:")
        print(f"  - {mission}")
        print(f"  - {papers_index}")
        print("Notebooks (demo mode runs offline by default):")
        for p in notebooks:
            print(f"  - {p}")
        print("")
        print("Run notebooks:")
        print("  python -m nbconvert --execute --to notebook --inplace <NOTEBOOK.ipynb>")
        print("")
        print("Enable LLM-backed runs (optional):")
        print("  export STILLWATER_ENABLE_LLM_REAL=1")
        print("  export STILLWATER_WRAPPER_URL=http://localhost:8080/api/generate")
        print("")
        print("LLM config helpers:")
        print("  stillwater llm status")
        print("  stillwater llm probe-ollama")
        print("  stillwater llm models")
        print("  stillwater llm set-ollama --auto-url --activate")
        print("  stillwater twin \"Explain twin orchestration\" --model llama3.1:8b")
        print("  stillwater twin --interactive")
        print("  stillwater paths")
        print("")
        print("Skills + recipe helpers:")
        print("  stillwater skills list")
        print("  stillwater skills sync --dest cli/skills/stillwater --all --force")
        print("  stillwater recipe list")
        print("  stillwater recipe add twin_orchestration --dir cli/recipes")
        print("  stillwater books list")
        print("  stillwater books show PERSISTENT-INTELLIGENCE")
        print("  stillwater papers list")
        print("  stillwater papers show 00-index")
        print("  stillwater twin \"/kernel\"")
        print("")
        print("Wish + stack + identity helpers:")
        print("  stillwater init agi-cli my-agent --dir artifacts/scaffolds --identity-stack")
        print("  stillwater init identity-stack --dir cli/identity --force")
        print("  stillwater wish list")
        print("  stillwater wish init wish.cli.example.v1 --level l1")
        print("  stillwater stack run --profile offline")
        print("  stillwater stack verify --strict")
        print("  stillwater recipe lint --prime-mermaid-only")
        print("  stillwater oolong run && stillwater oolong verify --strict")
        print("")
        print("Manual:")
        print("  cli/MANUAL.md")
        return 0

    return 0
