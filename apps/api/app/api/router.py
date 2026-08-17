from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.auth.api import router as auth_router
from app.modules.users.api import router as users_router
from app.modules.clusters.api import router as clusters_router
from app.modules.clusters.access.api import router as cluster_access_router
from app.modules.kubernetes.api import router as kubernetes_router
from app.modules.discovery.api import router as discovery_router
from app.modules.metrics.api import router as metrics_router
from app.modules.incidents.api import router as incidents_router
from app.modules.incidents.remediation.api import (
    router as remediation_router,
)
from app.core.config import settings
from app.modules.incidents.evidence.api import (
    router as incident_evidence_router,
)
from app.modules.incidents.timeline.api import (
    router as incident_timeline_router,
)
from app.modules.rca.api import router as rca_router
from app.modules.incidents.comments.api import router as incident_comments_router

api_router = APIRouter(prefix=settings.api_v1_prefix)

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(clusters_router)
api_router.include_router(cluster_access_router)
api_router.include_router(kubernetes_router)
api_router.include_router(discovery_router)
api_router.include_router(metrics_router)
api_router.include_router(incidents_router)
api_router.include_router(incident_evidence_router)
api_router.include_router(incident_timeline_router)
api_router.include_router(rca_router)
api_router.include_router(incident_comments_router)
api_router.include_router(remediation_router)
