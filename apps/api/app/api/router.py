from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.auth.api import router as auth_router
from app.modules.users.api import router as users_router
from app.modules.clusters.api import router as clusters_router
from app.modules.kubernetes.api import router as kubernetes_router
from app.modules.discovery.api import router as discovery_router
from app.modules.metrics.api import router as metrics_router
from app.modules.incidents.api import router as incidents_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.api_v1_prefix)

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(clusters_router)
api_router.include_router(kubernetes_router)
api_router.include_router(discovery_router)
api_router.include_router(metrics_router)
api_router.include_router(incidents_router)