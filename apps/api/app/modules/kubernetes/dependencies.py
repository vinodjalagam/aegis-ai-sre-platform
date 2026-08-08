from __future__ import annotations

from app.modules.kubernetes.service import KubernetesService


def get_kubernetes_service() -> KubernetesService:
    """
    Return a KubernetesService instance.
    """
    return KubernetesService()