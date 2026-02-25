"""Orchestration Service — wraps TripleTwinEngine as HTTP API.

Port: 8795
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from stillwater.audit_logger import AuditLogger
from stillwater.data_registry import DataRegistry
from stillwater.triple_twin import TripleTwinEngine, parse_frontmatter

from .base import StillwaterService


SERVICE_ID = "orchestration-service"
SERVICE_TYPE = "orchestration"
VERSION = "0.1.0"
PORT = 8795


class ProcessRequest(BaseModel):
    text: str = Field(default="")
    session_id: str | None = None
    user_id: str = "api:user"


class PhaseRequest(BaseModel):
    text: str = Field(default="")
    context: dict[str, Any] | None = None
    session_id: str | None = None
    user_id: str = "api:user"


class SeedsRequest(BaseModel):
    seeds: list[dict[str, Any]]


class ConfigUpdateRequest(BaseModel):
    threshold: float | None = None
    labels: list[str] | None = None


class OrchestrationService(StillwaterService):
    """Stillwater orchestration service on port 8795."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.registry = DataRegistry(repo_root=self.repo_root)
        self.audit_logger = AuditLogger(log_dir=self.repo_root / "data" / "logs")
        self.engine = TripleTwinEngine(registry=self.registry, audit_logger=self.audit_logger)
        self._last_test_results: dict[str, dict[str, Any]] = {}

        super().__init__(
            service_id=SERVICE_ID,
            service_type=SERVICE_TYPE,
            name="Orchestration Service",
            version=VERSION,
            port=PORT,
            oauth3_scopes=["orchestrate.process", "swarms.read", "catalog.read"],
            evidence_capture=True,
        )

    def health(self) -> dict:
        return {"stats": self.engine.stats()}

    def _reload_engine(self, session_id: str | None = None, user_id: str = "api:user") -> None:
        self.engine = TripleTwinEngine(
            registry=self.registry,
            audit_logger=self.audit_logger,
            session_id=session_id,
            user_id=user_id,
        )

    def _to_jsonable(self, value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        if isinstance(value, dict):
            return {k: self._to_jsonable(v) for k, v in value.items()}
        return value

    @staticmethod
    def _oauth3_enforcement_enabled() -> bool:
        return os.getenv("STILLWATER_OAUTH3_ENFORCE_MUTATIONS", "").strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _http_error_detail(body: str, fallback: str) -> str:
        try:
            payload = json.loads(body)
            if isinstance(payload, dict):
                detail = payload.get("detail")
                if isinstance(detail, str) and detail.strip():
                    return detail
        except json.JSONDecodeError:
            pass
        return fallback

    def _authorize_mutation(self, request: Request, required_scope: str, action_risk: str = "medium") -> None:
        if not self._oauth3_enforcement_enabled():
            return

        auth_header = request.headers.get("authorization", "").strip()
        if not auth_header.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        token_id = auth_header.split(" ", 1)[1].strip()
        if not token_id:
            raise HTTPException(status_code=401, detail="missing bearer token")

        payload = {
            "token_id": token_id,
            "required_scope": required_scope,
            "action_risk": action_risk,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8791/api/oauth3/validate",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=503, detail=f"oauth3 validate returned http {resp.status}")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 401:
                raise HTTPException(status_code=401, detail=self._http_error_detail(body, "unauthorized")) from exc
            if exc.code == 403:
                raise HTTPException(status_code=403, detail=self._http_error_detail(body, "forbidden")) from exc
            raise HTTPException(status_code=503, detail=f"oauth3 validate http {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise HTTPException(status_code=503, detail=f"oauth3 validate unavailable: {exc}") from exc

    @staticmethod
    def _phase_name(phase_num: int) -> str:
        if phase_num not in (1, 2, 3):
            raise HTTPException(status_code=400, detail=f"invalid phase: {phase_num}")
        return f"phase{phase_num}"

    def _collect_cpu_node_configs(self) -> list[tuple[str, dict[str, Any], str]]:
        items: list[tuple[str, dict[str, Any], str]] = []
        for rel_path, content in sorted(self.registry.load_all_data().items()):
            if not rel_path.startswith("cpu-nodes/") or not rel_path.endswith(".md"):
                continue
            cfg = parse_frontmatter(content)
            raw_phase = cfg.get("phase")
            if raw_phase is None:
                continue
            phase_name = f"phase{raw_phase}" if isinstance(raw_phase, int) else str(raw_phase)
            items.append((phase_name, cfg, rel_path))
        return items

    def _phase_seed_records(self, phase_num: int) -> list[dict[str, Any]]:
        phase_name = self._phase_name(phase_num)
        out: list[dict[str, Any]] = []
        for rel_path, content in sorted(self.registry.load_all_data().items()):
            if not rel_path.startswith("seeds/") or not rel_path.endswith(".jsonl"):
                continue
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("phase") == phase_name:
                    out.append(record)
        return out

    def _catalog(self, root: str, recursive: bool = False) -> list[dict[str, Any]]:
        base = self.repo_root / "data" / "default" / root
        if not base.exists():
            return []

        pattern = "**/*.md" if recursive else "*.md"
        items: list[dict[str, Any]] = []
        for path in sorted(base.glob(pattern)):
            if not path.is_file():
                continue
            rel = path.relative_to(self.repo_root).as_posix()
            text = path.read_text(encoding="utf-8")
            cfg = parse_frontmatter(text)
            title = ""
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            item_id = path.stem
            items.append(
                {
                    "id": item_id,
                    "path": rel,
                    "title": title,
                    "frontmatter": cfg,
                },
            )
        return items

    def register_routes(self, app: FastAPI) -> None:
        @app.post("/api/orchestrate/process")
        async def process(req: ProcessRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            if req.session_id:
                self._reload_engine(session_id=req.session_id, user_id=req.user_id)
            result = self.engine.process(req.text)
            return {"ok": True, "result": self._to_jsonable(result)}

        @app.post("/api/orchestrate/phase1")
        async def process_phase1(req: PhaseRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            if req.session_id:
                self._reload_engine(session_id=req.session_id, user_id=req.user_id)
            phase = self.engine._run_phase("phase1", req.text, req.context)  # noqa: SLF001
            return {"ok": True, "phase1": self._to_jsonable(phase) if phase else None}

        @app.post("/api/orchestrate/phase2")
        async def process_phase2(req: PhaseRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            if req.session_id:
                self._reload_engine(session_id=req.session_id, user_id=req.user_id)
            phase = self.engine._run_phase("phase2", req.text, req.context)  # noqa: SLF001
            return {"ok": True, "phase2": self._to_jsonable(phase) if phase else None}

        @app.post("/api/orchestrate/phase3")
        async def process_phase3(req: PhaseRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            if req.session_id:
                self._reload_engine(session_id=req.session_id, user_id=req.user_id)
            phase = self.engine._run_phase("phase3", req.text, req.context)  # noqa: SLF001
            return {"ok": True, "phase3": self._to_jsonable(phase) if phase else None}

        @app.get("/api/orchestrate/stats")
        async def stats() -> dict[str, Any]:
            return {"ok": True, "stats": self.engine.stats()}

        @app.get("/api/orchestrate/phases")
        async def phases() -> dict[str, Any]:
            stats = self.engine.stats()["phases"]
            payload = []
            for phase_name, phase_data in sorted(stats.items()):
                payload.append(
                    {
                        "phase": phase_name,
                        "name": phase_data["name"],
                        "validator_model": phase_data["validator_model"],
                        "labels": phase_data["labels"],
                        "seed_count": phase_data["learner"]["total_patterns"],
                        "threshold": self.engine._phases[phase_name].learner.threshold,  # noqa: SLF001
                    },
                )
            return {"ok": True, "phases": payload}

        @app.get("/api/phases/{phase_num}/seeds")
        async def get_phase_seeds(phase_num: int) -> dict[str, Any]:
            return {"ok": True, "phase": self._phase_name(phase_num), "seeds": self._phase_seed_records(phase_num)}

        @app.post("/api/phases/{phase_num}/seeds")
        async def post_phase_seeds(phase_num: int, req: SeedsRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            phase_name = self._phase_name(phase_num)
            sanitized: list[dict[str, Any]] = []
            for row in req.seeds:
                keyword = str(row.get("keyword", "")).strip().lower()
                label = str(row.get("label", "")).strip()
                if not keyword or not label:
                    continue
                sanitized.append(
                    {
                        "keyword": keyword,
                        "label": label,
                        "count": int(row.get("count", 25)),
                        "confidence": float(row.get("confidence", 0.8824)),
                        "examples": list(row.get("examples", [])),
                        "phase": phase_name,
                    },
                )

            rel_path = f"seeds/{phase_name}_custom.jsonl"
            content = "\n".join(json.dumps(row, sort_keys=True) for row in sanitized) + ("\n" if sanitized else "")
            self.registry.save_data_file(rel_path, content)
            self._reload_engine()
            return {"ok": True, "phase": phase_name, "written": len(sanitized), "path": f"data/custom/{rel_path}"}

        @app.get("/api/phases/{phase_num}/config")
        async def get_phase_config(phase_num: int) -> dict[str, Any]:
            phase_name = self._phase_name(phase_num)
            for name, cfg, rel_path in self._collect_cpu_node_configs():
                if name == phase_name:
                    return {"ok": True, "phase": phase_name, "config": cfg, "path": rel_path}
            raise HTTPException(status_code=404, detail=f"phase config not found: {phase_name}")

        @app.put("/api/phases/{phase_num}/config")
        async def put_phase_config(phase_num: int, req: ConfigUpdateRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            phase_name = self._phase_name(phase_num)
            selected_cfg: dict[str, Any] | None = None
            selected_path: str | None = None

            for name, cfg, rel_path in self._collect_cpu_node_configs():
                if name == phase_name:
                    selected_cfg = dict(cfg)
                    selected_path = rel_path
                    break
            if selected_cfg is None or selected_path is None:
                raise HTTPException(status_code=404, detail=f"phase config not found: {phase_name}")

            if req.threshold is not None:
                selected_cfg["threshold"] = req.threshold
            if req.labels is not None:
                selected_cfg["labels"] = req.labels

            lines = ["---"]
            for key, value in selected_cfg.items():
                if isinstance(value, list):
                    rendered = "[" + ", ".join(str(v) for v in value) + "]"
                elif isinstance(value, str):
                    rendered = f'"{value}"' if (" " in value or ":" in value) else value
                else:
                    rendered = str(value)
                lines.append(f"{key}: {rendered}")
            lines.append("---")
            lines.append("")
            lines.append(f"# {selected_cfg.get('name', phase_name)}")
            lines.append("")
            lines.append("Updated via /api/phases/{n}/config.")
            content = "\n".join(lines) + "\n"

            self.registry.save_data_file(selected_path, content)
            self._reload_engine()
            return {"ok": True, "phase": phase_name, "path": f"data/custom/{selected_path}", "config": selected_cfg}

        @app.get("/api/swarms")
        async def catalog_swarms() -> dict[str, Any]:
            return {"ok": True, "swarms": self._catalog("swarms", recursive=True)}

        @app.get("/api/swarms/{item_id}")
        async def catalog_swarms_detail(item_id: str) -> dict[str, Any]:
            for row in self._catalog("swarms", recursive=True):
                if row["id"] == item_id:
                    return {"ok": True, "swarm": row}
            raise HTTPException(status_code=404, detail=f"swarm not found: {item_id}")

        @app.get("/api/combos")
        async def catalog_combos() -> dict[str, Any]:
            return {"ok": True, "combos": self._catalog("combos")}

        @app.get("/api/combos/{item_id}")
        async def catalog_combos_detail(item_id: str) -> dict[str, Any]:
            for row in self._catalog("combos"):
                if row["id"] == item_id:
                    return {"ok": True, "combo": row}
            raise HTTPException(status_code=404, detail=f"combo not found: {item_id}")

        @app.post("/api/combos/{item_id}/execute")
        async def execute_combo(item_id: str, req: ProcessRequest, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            for row in self._catalog("combos"):
                if row["id"] == item_id:
                    result = self.engine.process(req.text)
                    return {
                        "ok": True,
                        "combo_id": item_id,
                        "combo": row,
                        "result": self._to_jsonable(result),
                    }
            raise HTTPException(status_code=404, detail=f"combo not found: {item_id}")

        @app.get("/api/skills")
        async def catalog_skills() -> dict[str, Any]:
            return {"ok": True, "skills": self._catalog("skills")}

        @app.get("/api/recipes")
        async def catalog_recipes() -> dict[str, Any]:
            return {"ok": True, "recipes": self._catalog("recipes")}

        @app.get("/api/personas")
        async def catalog_personas() -> dict[str, Any]:
            return {"ok": True, "personas": self._catalog("personas", recursive=True)}

        @app.post("/api/phases/{phase_num}/test")
        async def test_phase(phase_num: int, request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            phase_name = self._phase_name(phase_num)
            target = f"src/cli/tests/test_{phase_name}.py"
            cmd = ["pytest", "-q", target]
            start = time.time()
            proc = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=120, check=False)
            result = {
                "ok": proc.returncode == 0,
                "phase": phase_name,
                "command": cmd,
                "returncode": proc.returncode,
                "duration_s": round(time.time() - start, 3),
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
            }
            self._last_test_results[phase_name] = result
            return result

        @app.get("/api/phases/{phase_num}/test-results")
        async def get_test_results(phase_num: int) -> dict[str, Any]:
            phase_name = self._phase_name(phase_num)
            result = self._last_test_results.get(phase_name)
            if not result:
                return {"ok": False, "phase": phase_name, "message": "no test result yet"}
            return {"ok": True, "phase": phase_name, "result": result}

        @app.post("/api/orchestrate/test")
        async def test_pipeline(request: Request) -> dict[str, Any]:
            self._authorize_mutation(request, required_scope="store.write")
            cmd = ["pytest", "-q", "src/cli/tests/test_triple_twin.py"]
            start = time.time()
            proc = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=180, check=False)
            result = {
                "ok": proc.returncode == 0,
                "command": cmd,
                "returncode": proc.returncode,
                "duration_s": round(time.time() - start, 3),
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
            }
            self._last_test_results["pipeline"] = result
            return result


def create_service(repo_root: Path | None = None) -> OrchestrationService:
    root = repo_root or Path(__file__).resolve().parents[2]
    return OrchestrationService(repo_root=root)


service = create_service()
app = service.create_app()
