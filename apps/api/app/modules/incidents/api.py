"""
Incident API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentAssignment,
)

from app.modules.incidents.service import IncidentService
from app.modules.incidents.enums import IncidentStatus
from app.core.security.dependencies import get_current_user_id

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    incident: IncidentCreate,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an incident only if the user has
    modifying access to the selected cluster.
    """

    service = IncidentService(db)

    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    # ---------------------------------------------
    # 1. Check cluster access
    # ---------------------------------------------

    access = await access_repository.get(
        current_user_id,
        incident.cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    # ---------------------------------------------
    # 2. Check role
    # ---------------------------------------------

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create incidents",
        )

    # ---------------------------------------------
    # 3. Create incident
    # ---------------------------------------------

    created = await service.create_incident(
        incident
    )

    return {
        "success": True,
        "data": created,
    }

@router.get("")
async def list_incidents(
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    List incidents for a cluster accessible
    to the authenticated user.
    """

    service = IncidentService(db)

    # Verify cluster access
    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    incidents, total = await service.list_user_incidents(
        user_id=current_user_id,
        cluster_id=cluster_id,
    )

    return {
        "success": True,
        "data": {
            "items": incidents,
            "total": total,
        },
    }

@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get an incident only if the user has access
    to the selected cluster.
    """

    service = IncidentService(db)

    incident = await service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    return {
        "success": True,
        "data": incident,
    }
    
@router.post("/{incident_id}/acknowledge")
async def acknowledge_incident(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Acknowledge an incident only if the user has
    access to the selected cluster with a modifying role.
    """

    service = IncidentService(db)

    # Check cluster access and role
    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to acknowledge incidents",
        )

    incident = await service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    if not incident.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident is not active",
        )

    if incident.status == IncidentStatus.ACKNOWLEDGED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident is already acknowledged",
        )

    if incident.status == IncidentStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolved incident cannot be acknowledged",
        )

    acknowledged = await service.acknowledge_incident(
        incident
    )

    return {
        "success": True,
        "data": acknowledged,
    }
    
@router.post("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve an incident only if the user has access
    to the selected cluster with a modifying role.
    """

    service = IncidentService(db)

    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to resolve incidents",
        )

    incident = await service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    if not incident.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident is already resolved",
        )

    resolved = await service.resolve_incident(
        incident
    )

    return {
        "success": True,
        "data": resolved,
    }

@router.patch("/{incident_id}/assignment")
async def assign_incident(
    incident_id: str,
    data: IncidentAssignment,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Assign or unassign an incident only if the user
    has modifying access to the selected cluster.
    """

    service = IncidentService(db)

    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    # ---------------------------------------------
    # 1. Check cluster access
    # ---------------------------------------------

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    # ---------------------------------------------
    # 2. Check role
    # ---------------------------------------------

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to assign incidents",
        )

    # ---------------------------------------------
    # 3. Get incident within selected cluster
    # ---------------------------------------------

    incident = await service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    # ---------------------------------------------
    # 4. Check incident status
    # ---------------------------------------------

    if not incident.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolved incident cannot be assigned",
        )

    # ---------------------------------------------
    # 5. Assign / unassign
    # ---------------------------------------------

    try:
        assigned = await service.assign_incident(
            incident,
            data.user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "success": True,
        "data": assigned,
    }
    
@router.patch("/{incident_id}")
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an incident only if the user has
    modifying access to the selected cluster.
    """

    service = IncidentService(db)

    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    # ---------------------------------------------
    # 1. Check cluster access
    # ---------------------------------------------

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    # ---------------------------------------------
    # 2. Check role
    # ---------------------------------------------

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update incidents",
        )

    # ---------------------------------------------
    # 3. Get incident within selected cluster
    # ---------------------------------------------

    incident = await service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    # ---------------------------------------------
    # 4. Update incident
    # ---------------------------------------------

    updated = await service.update_incident(
        incident_id,
        data,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return {
        "success": True,
        "data": updated,
    }

@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an incident only if the user has
    modifying access to the selected cluster.
    """

    service = IncidentService(db)

    from app.modules.clusters.access.repository import (
        ClusterAccessRepository,
    )

    access_repository = ClusterAccessRepository(db)

    # ---------------------------------------------
    # 1. Check cluster access
    # ---------------------------------------------

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    # ---------------------------------------------
    # 2. Check role
    # ---------------------------------------------

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete incidents",
        )

    # ---------------------------------------------
    # 3. Get incident within selected cluster
    # ---------------------------------------------

    incident = await service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    # ---------------------------------------------
    # 4. Delete incident
    # ---------------------------------------------

    deleted = await service.delete_incident(
        incident_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return {
        "success": True,
        "message": "Incident deleted successfully",
    }