from __future__ import annotations

from app.modules.clusters.access.models import ClusterAccess
from app.modules.clusters.access.repository import (
    ClusterAccessRepository,
)


class ClusterAccessService:
    """
    Business logic for cluster access.
    """

    def __init__(
        self,
        repository: ClusterAccessRepository,
    ):
        self.repository = repository

    async def grant_access(
        self,
        user_id: str,
        cluster_id: str,
        role: str = "viewer",
    ) -> ClusterAccess:

        existing = await self.repository.get(
            user_id,
            cluster_id,
        )

        if existing:
            raise ValueError(
                "User already has access to this cluster"
            )

        access = ClusterAccess(
            user_id=user_id,
            cluster_id=cluster_id,
            role=role,
        )

        return await self.repository.create(access)

    async def has_access(
        self,
        user_id: str,
        cluster_id: str,
    ) -> bool:

        access = await self.repository.get(
            user_id,
            cluster_id,
        )

        return access is not None

    async def get_access(
        self,
        user_id: str,
        cluster_id: str,
    ) -> ClusterAccess | None:

        return await self.repository.get(
            user_id,
            cluster_id,
        )
    async def require_access(
        self,
        user_id: str,
        cluster_id: str,
        allowed_roles: list[str] | None = None,
    ) -> ClusterAccess:
        """
        Return access if the user is authorized for the cluster.

        Raises ValueError when the user has no access or
        insufficient role.
        """

        access = await self.repository.get(
            user_id,
            cluster_id,
        )

        if access is None:
            raise PermissionError(
                "You do not have access to this cluster"
            )

        if (
            allowed_roles is not None
            and access.role not in allowed_roles
        ):
            raise PermissionError(
                "You do not have permission for this action"
            )

        return access
    
    async def list_user_clusters(
        self,
        user_id: str,
    ) -> list[ClusterAccess]:

        return await self.repository.list_user_clusters(
            user_id
        )
