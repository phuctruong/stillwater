"""Stillwater Service Mesh — Webservice-First Architecture.

Every recipe node is a web service. The admin gateway (port 8787)
manages the service registry, health checks, and auto-discovery.
"""

from .models import ServiceDescriptor, ServiceHealth, ServiceRegistration
from .registry import ServiceRegistry

__all__ = ["ServiceDescriptor", "ServiceHealth", "ServiceRegistration", "ServiceRegistry"]
