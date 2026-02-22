"""Service registry models — Pydantic v2 data structures for the Stillwater Service Mesh."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ServiceType(str, Enum):
    LLM = "llm"
    BROWSER = "browser"
    RECIPE = "recipe"
    EVIDENCE = "evidence"
    OAUTH3 = "oauth3"
    CPU = "cpu"
    TUNNEL = "tunnel"
    CUSTOM = "custom"


class ServiceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    STARTING = "starting"


class ServiceDescriptor(BaseModel):
    service_id: str = Field(..., description="Unique service identifier")
    service_type: ServiceType
    name: str = Field(..., description="Human-readable service name")
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(..., ge=1, le=65535)
    health_endpoint: str = Field(default="/api/health")
    openapi_endpoint: str = Field(default="/openapi.json")
    oauth3_scopes: list[str] = Field(default_factory=list)
    evidence_capture: bool = Field(default=True)
    status: ServiceStatus = Field(default=ServiceStatus.STARTING)
    registered_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_health_check: str = Field(default="")
    metadata: dict = Field(default_factory=dict)

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        return f"{self.base_url}{self.health_endpoint}"


class ServiceHealth(BaseModel):
    service_id: str
    status: ServiceStatus
    latency_ms: float = Field(default=0.0)
    last_check: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    details: dict = Field(default_factory=dict)


class ServiceRegistration(BaseModel):
    """Request model for service registration."""

    service_id: str
    service_type: ServiceType
    name: str
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int
    health_endpoint: str = "/api/health"
    openapi_endpoint: str = "/openapi.json"
    oauth3_scopes: list[str] = []
    evidence_capture: bool = True
    metadata: dict = {}


class ServiceDiscoveryResult(BaseModel):
    """Result of auto-discovery scan."""

    discovered: list[ServiceDescriptor]
    failed_ports: list[int] = []
    scan_duration_ms: float = 0.0
