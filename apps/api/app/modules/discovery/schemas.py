from __future__ import annotations

from pydantic import BaseModel


class ServiceDiscovery(BaseModel):
    namespace: str
    service: str
    port: int


class DiscoveryResponse(BaseModel):
    prometheus: ServiceDiscovery | None = None
    grafana: ServiceDiscovery | None = None
    metrics_server: ServiceDiscovery | None = None
    ingress_controller: ServiceDiscovery | None = None