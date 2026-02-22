"""StillwaterService — abstract base class for all webservice-first services."""

from abc import ABC, abstractmethod
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import json
import time
import urllib.request
import urllib.error
from datetime import datetime


class StillwaterService(ABC):
    """Base class for Stillwater web services.

    Every service in the mesh inherits from this. Provides:
    - Standard FastAPI app creation with health endpoint
    - Admin registration on startup
    - Evidence capture middleware (logs every request)
    - OAuth3 scope enforcement middleware (placeholder for Phase 4)
    """

    def __init__(
        self,
        service_id: str,
        service_type: str,
        name: str,
        version: str,
        port: int,
        oauth3_scopes: list[str] | None = None,
        evidence_capture: bool = True,
        admin_url: str = "http://127.0.0.1:8787",
    ):
        self.service_id = service_id
        self.service_type = service_type
        self.name = name
        self.version = version
        self.port = port
        self.oauth3_scopes = oauth3_scopes or []
        self.evidence_capture = evidence_capture
        self.admin_url = admin_url
        self._app: FastAPI | None = None

    @abstractmethod
    def health(self) -> dict:
        """Return service health status. Must be implemented by subclasses."""
        ...

    @abstractmethod
    def register_routes(self, app: FastAPI) -> None:
        """Register service-specific routes. Must be implemented by subclasses."""
        ...

    def create_app(self) -> FastAPI:
        """Create the FastAPI application with standard middleware and routes."""
        app = FastAPI(
            title=self.name,
            version=self.version,
            description=f"Stillwater {self.service_type} service: {self.name}",
        )

        # CORS for local development
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Evidence capture middleware
        if self.evidence_capture:
            @app.middleware("http")
            async def evidence_middleware(request: Request, call_next):
                start = time.monotonic()
                response = await call_next(request)
                duration_ms = round((time.monotonic() - start) * 1000, 2)
                # Log to evidence (lightweight — full capture in Phase 3)
                response.headers["X-Service-Id"] = self.service_id
                response.headers["X-Duration-Ms"] = str(duration_ms)
                response.headers["X-Timestamp"] = datetime.utcnow().isoformat()
                return response

        # Standard health endpoint
        @app.get("/api/health")
        async def health_endpoint():
            return {
                "status": "ok",
                "service_id": self.service_id,
                "service_type": self.service_type,
                "version": self.version,
                **self.health(),
            }

        # Service info endpoint
        @app.get("/api/service-info")
        async def service_info():
            return {
                "service_id": self.service_id,
                "service_type": self.service_type,
                "name": self.name,
                "version": self.version,
                "port": self.port,
                "oauth3_scopes": self.oauth3_scopes,
                "evidence_capture": self.evidence_capture,
            }

        # Register service-specific routes
        self.register_routes(app)

        # Register with admin on startup
        @app.on_event("startup")
        async def register_with_admin():
            self._register_with_admin()

        self._app = app
        return app

    def _register_with_admin(self) -> bool:
        """Register this service with the admin gateway. Fail silently if admin not running."""
        payload = json.dumps({
            "service_id": self.service_id,
            "service_type": self.service_type,
            "name": self.name,
            "version": self.version,
            "host": "127.0.0.1",
            "port": self.port,
            "health_endpoint": "/api/health",
            "openapi_endpoint": "/openapi.json",
            "oauth3_scopes": self.oauth3_scopes,
            "evidence_capture": self.evidence_capture,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{self.admin_url}/api/services/register",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            # Admin not running — standalone mode
            return False
