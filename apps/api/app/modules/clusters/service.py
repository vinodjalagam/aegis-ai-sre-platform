from __future__ import annotations

import yaml

from app.modules.clusters.access.models import ClusterAccess
from app.modules.clusters.access.repository import ClusterAccessRepository
from app.modules.clusters.models import Cluster
from app.modules.clusters.repository import ClusterRepository
from app.modules.clusters.schemas import (
    ClusterCreate,
    ClusterUpdate,
)
from app.modules.kubernetes.service import KubernetesService


class ClusterService:
    """
    Business logic for clusters.
    """

    def __init__(
        self,
        repository: ClusterRepository,
        access_repository: ClusterAccessRepository,
    ):
        self.repository = repository
        self.access_repository = access_repository

    async def create_cluster(
        self,
        data: ClusterCreate,
        user_id: str,
    ) -> Cluster:
        """
        Validate a Kubernetes cluster and register it.

        The cluster is only stored if the supplied kubeconfig
        is valid and the Kubernetes API is reachable.
        """

        # -----------------------------------------
        # 1. Check duplicate cluster name
        # -----------------------------------------

        existing = await self.repository.get_by_name(
            data.name
        )

        if existing:
            raise ValueError(
                "Cluster name already exists"
            )

        # -----------------------------------------
        # 2. Validate kubeconfig YAML
        # -----------------------------------------

        try:
            kubeconfig_data = yaml.safe_load(
                data.kubeconfig
            )

            if not isinstance(kubeconfig_data, dict):
                raise ValueError(
                    "Kubeconfig must contain a valid YAML object"
                )

            required_fields = [
                "apiVersion",
                "clusters",
                "contexts",
                "current-context",
                "users",
            ]

            missing = [
                field
                for field in required_fields
                if field not in kubeconfig_data
            ]

            if missing:
                raise ValueError(
                    "Invalid kubeconfig. Missing fields: "
                    + ", ".join(missing)
                )

        except yaml.YAMLError as exc:
            raise ValueError(
                "Invalid kubeconfig YAML"
            ) from exc

        # -----------------------------------------
        # 3. Connect to Kubernetes
        # -----------------------------------------

        try:
            kubernetes_service = KubernetesService(
                data.kubeconfig
            )

            if not kubernetes_service.connect():
                raise ValueError(
                    "Unable to connect to Kubernetes cluster"
                )

            # Verify API access and collect basic information.
            summary = (
                kubernetes_service.get_cluster_summary()
            )

        except Exception as exc:
            raise ValueError(
                f"Unable to validate Kubernetes cluster: {exc}"
            ) from exc

        # -----------------------------------------
        # 4. Create database record
        # -----------------------------------------

        cluster = Cluster(
            name=data.name,
            description=data.description,
            provider=data.provider,
            kubeconfig=data.kubeconfig,
            status="online",
            is_active=True,
        )

        cluster = await self.repository.create(
            cluster
        )

        # -----------------------------------------
        # 5. Give creator owner access
        # -----------------------------------------

        await self.access_repository.create(
            ClusterAccess(
                user_id=user_id,
                cluster_id=cluster.id,
                role="owner",
            )
        )

        return cluster

    async def get_cluster(
        self,
        cluster_id: str,
    ) -> Cluster | None:
        """
        Get a cluster by ID.
        """

        return await self.repository.get_by_id(
            cluster_id
        )
    async def get_user_cluster(
        self,
        user_id: str,
        cluster_id: str,
    ) -> Cluster | None:
        """
        Return an active cluster only if the user has access.
        """

        access = await self.access_repository.get(
            user_id,
            cluster_id,
        )

        if access is None:
            return None

        cluster = await self.repository.get_by_id(
            cluster_id
        )

        if not cluster or not cluster.is_active:
            return None

        return cluster
    async def authorize_cluster_action(
        self,
        user_id: str,
        cluster_id: str,
        allowed_roles: list[str],
    ) -> Cluster:
        """
        Verify cluster access and role before an operation.
        """

        access = await self.access_repository.get(
            user_id,
            cluster_id,
        )

        if access is None:
            raise PermissionError(
                "You do not have access to this cluster"
            )

        if access.role not in allowed_roles:
            raise PermissionError(
                "You do not have permission for this action"
            )

        cluster = await self.repository.get_by_id(
            cluster_id
        )

        if not cluster or not cluster.is_active:
            raise ValueError(
                "Cluster not found"
            )

        return cluster
    async def list_user_clusters(
        self,
        user_id: str,
    ) -> list[Cluster]:
        """
        Return clusters accessible to the user.
        """

        accesses = (
            await self.access_repository.list_user_clusters(
                user_id
            )
        )

        clusters = []

        for access in accesses:
            cluster = await self.repository.get_by_id(
                access.cluster_id
            )

            if cluster and cluster.is_active:
                clusters.append(cluster)

        return clusters

    async def update_cluster(
        self,
        cluster_id: str,
        data: ClusterUpdate,
    ) -> Cluster | None:
        """
        Update a cluster.
        """

        cluster = await self.repository.get_by_id(
            cluster_id
        )

        if not cluster:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(cluster, key, value)

        return await self.repository.update(
            cluster
        )

    async def delete_cluster(
        self,
        cluster_id: str,
    ) -> bool:
        """
        Delete a cluster.
        """

        cluster = await self.repository.get_by_id(
            cluster_id
        )

        if not cluster:
            return False

        await self.repository.delete(cluster)

        return True