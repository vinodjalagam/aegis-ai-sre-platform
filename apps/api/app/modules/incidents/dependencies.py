from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.service import IncidentService


async def get_incident_service(
    db: AsyncSession = Depends(get_db),
) -> IncidentService:
    repository = IncidentRepository(db)
    return IncidentService(repository)