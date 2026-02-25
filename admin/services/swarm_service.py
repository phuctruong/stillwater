"""Swarm dispatch service — exposes swarms as HTTP endpoints."""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from stillwater.audit_logger import AuditLogger

from .base import StillwaterService
from .key_manager import KeyManager
from .llm_wrapper import LLMWrapper


SERVICE_ID = "swarm-service"
SERVICE_TYPE = "swarm"
VERSION = "0.1.0"
PORT = 8796
logger = logging.getLogger(__name__)


class DispatchRequest(BaseModel):
    task: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    provider: str | None = None
    model: str | None = None
    session_id: str = "swarm-session"
    user_id: str = "api:user"


class ModelUpdateRequest(BaseModel):
    model: str


class _FrontmatterParser:
    _fm_re = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)

    @classmethod
    def parse(cls, text: str) -> dict[str, Any]:
        match = cls._fm_re.match(text)
        if not match:
            return {}
        lines = match.group(1).splitlines()
        out: dict[str, Any] = {}
        current_list_key: str | None = None
        current_section: str | None = None
        for raw_line in lines:
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("- ") and current_list_key:
                item = stripped[2:].strip().split("#", 1)[0].strip()
                if item:
                    out.setdefault(current_list_key, []).append(item)
                continue
            if current_section == "persona" and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip().split("#", 1)[0].strip().strip('"').strip("'")
                if value == "":
                    current_list_key = f"persona_{key}"
                    out.setdefault(current_list_key, [])
                    continue
                out[f"persona_{key}"] = value
                current_list_key = None
                continue
            if ":" in stripped and not stripped.startswith("- "):
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip().split("#", 1)[0].strip().strip('"').strip("'")
                if value == "":
                    current_section = key
                    current_list_key = key
                    out.setdefault(key, [])
                    continue
                out[key] = value
                current_section = key
                current_list_key = None
                continue
        return out


class SwarmService(StillwaterService):
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.swarm_dir = self.repo_root / "data" / "default" / "swarms"
        self.key_manager = KeyManager(self.repo_root)
        self.llm = LLMWrapper(self.repo_root)
        self.audit_logger = AuditLogger(self.repo_root / "data" / "logs")
        self.dispatch_history: dict[str, list[dict[str, Any]]] = {}
        super().__init__(
            service_id=SERVICE_ID,
            service_type=SERVICE_TYPE,
            name="Swarm Dispatch Service",
            version=VERSION,
            port=PORT,
            oauth3_scopes=["swarms.read", "swarms.dispatch"],
            evidence_capture=True,
        )

    def health(self) -> dict:
        return {
            "swarm_count": len(self._swarm_paths()),
            "history_items": sum(len(v) for v in self.dispatch_history.values()),
        }

    def _swarm_paths(self) -> list[Path]:
        if not self.swarm_dir.exists():
            return []
        return sorted(
            [
                p
                for p in self.swarm_dir.rglob("*.md")
                if p.is_file() and not p.name.startswith("README")
            ]
        )

    def _resolve_swarm_path(self, swarm_id: str) -> Path:
        matches = [p for p in self._swarm_paths() if p.stem == swarm_id]
        if not matches:
            raise HTTPException(status_code=404, detail=f"swarm not found: {swarm_id}")
        if len(matches) > 1:
            dup_paths = [p.relative_to(self.repo_root).as_posix() for p in matches]
            raise HTTPException(status_code=409, detail=f"duplicate swarm id '{swarm_id}': {dup_paths}")
        return matches[0]

    def _load_swarm(self, swarm_id: str) -> dict[str, Any]:
        path = self._resolve_swarm_path(swarm_id)
        text = path.read_text(encoding="utf-8")
        fm = _FrontmatterParser.parse(text)
        title = ""
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        skills = list(fm.get("skill_pack", []))
        if "prime-safety" not in skills:
            skills.insert(0, "prime-safety")
        elif skills[0] != "prime-safety":
            skills.remove("prime-safety")
            skills.insert(0, "prime-safety")
        model_preferred = str(fm.get("model_preferred", "sonnet"))
        model = self.key_manager.get_swarm_model(swarm_id, model_preferred)
        return {
            "id": swarm_id,
            "path": path.relative_to(self.repo_root).as_posix(),
            "title": title,
            "agent_type": fm.get("agent_type", swarm_id),
            "skills": skills,
            "persona_primary": fm.get("persona_primary", ""),
            "model_preferred": model_preferred,
            "model_selected": model,
            "rung_default": fm.get("rung_default", "641"),
            "frontmatter": fm,
        }

    def _build_prompt(self, swarm: dict[str, Any], task: str, context: dict[str, Any]) -> str:
        capsule = json.dumps(context, indent=2, sort_keys=True)
        skills = ", ".join(swarm["skills"])
        persona = swarm.get("persona_primary") or "none"
        return (
            f"You are swarm '{swarm['id']}' ({swarm['agent_type']}).\n"
            f"Model tier: {swarm['model_selected']}\n"
            f"Skills: {skills}\n"
            f"Persona: {persona}\n\n"
            f"Task:\n{task}\n\n"
            f"Context:\n{capsule}\n"
        )

    def register_routes(self, app: FastAPI) -> None:
        @app.get("/api/swarms")
        async def list_swarms() -> dict[str, Any]:
            swarms = [self._load_swarm(p.stem) for p in self._swarm_paths()]
            return {"ok": True, "count": len(swarms), "swarms": swarms}

        @app.get("/api/swarms/{swarm_id}")
        async def get_swarm(swarm_id: str) -> dict[str, Any]:
            return {"ok": True, "swarm": self._load_swarm(swarm_id)}

        @app.get("/api/swarms/{swarm_id}/model")
        async def get_swarm_model(swarm_id: str) -> dict[str, Any]:
            swarm = self._load_swarm(swarm_id)
            return {
                "ok": True,
                "swarm_id": swarm_id,
                "model_selected": swarm["model_selected"],
                "model_preferred": swarm["model_preferred"],
            }

        @app.put("/api/swarms/{swarm_id}/model")
        async def put_swarm_model(swarm_id: str, req: ModelUpdateRequest) -> dict[str, Any]:
            self._load_swarm(swarm_id)
            data = self.key_manager.set_swarm_model(swarm_id, req.model)
            return {"ok": True, **data}

        @app.post("/api/swarms/{swarm_id}/dispatch")
        async def dispatch_swarm(swarm_id: str, req: DispatchRequest) -> dict[str, Any]:
            swarm = self._load_swarm(swarm_id)
            selected_model = req.model or swarm["model_selected"]
            prompt = self._build_prompt(swarm, req.task, req.context)
            start = time.time()
            result = self.llm.complete(prompt=prompt, model=selected_model, provider=req.provider)
            duration = round(time.time() - start, 3)

            entry = {
                "swarm_id": swarm_id,
                "task": req.task,
                "provider": result.get("provider"),
                "model": selected_model,
                "ok": result.get("ok", False),
                "duration_s": duration,
                "timestamp": time.time(),
            }
            self.dispatch_history.setdefault(swarm_id, []).append(entry)
            self.dispatch_history[swarm_id] = self.dispatch_history[swarm_id][-50:]

            try:
                if result.get("ok"):
                    self.audit_logger.log_llm_call(
                        user_id=req.user_id,
                        model=str(result.get("provider") or "unknown"),
                        input_text=prompt,
                        output_text=str(result.get("completion", "")),
                        label=f"swarm:{swarm_id}",
                        confidence=1.0,
                        tokens={"input": 0, "output": 0},
                        session_id=req.session_id,
                    )
            except Exception as exc:
                logger.error("audit log failed: %s", exc)

            return {"ok": bool(result.get("ok")), "swarm_id": swarm_id, "result": result, "duration_s": duration}

        @app.get("/api/swarms/{swarm_id}/history")
        async def swarm_history(swarm_id: str) -> dict[str, Any]:
            self._load_swarm(swarm_id)
            return {"ok": True, "swarm_id": swarm_id, "history": self.dispatch_history.get(swarm_id, [])}

        @app.post("/api/swarms/{swarm_id}/test")
        async def swarm_test(swarm_id: str) -> dict[str, Any]:
            req = DispatchRequest(task=f"Test dispatch for {swarm_id}", context={"mode": "test"})
            return await dispatch_swarm(swarm_id, req)


def create_service(repo_root: Path | None = None) -> SwarmService:
    root = repo_root or Path(__file__).resolve().parents[2]
    return SwarmService(root)


service = create_service()
app = service.create_app()
