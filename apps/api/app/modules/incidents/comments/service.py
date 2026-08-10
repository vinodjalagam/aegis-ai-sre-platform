"""
Incident comment service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.comments.models import IncidentComment
from app.modules.incidents.comments.repository import (
    IncidentCommentRepository,
)
from app.modules.incidents.comments.schemas import (
    IncidentCommentCreate,
)
from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
)
from app.modules.incidents.timeline.service import (
    IncidentTimelineService,
)


class IncidentCommentService:
    """
    Business logic for incident comments.
    """

    def __init__(self, db: AsyncSession):
        self.repository = IncidentCommentRepository(db)
        self.incident_repository = IncidentRepository(db)
        self.timeline_service = IncidentTimelineService(db)

    async def create_comment(
        self,
        incident_id: str,
        user_id: str,
        data: IncidentCommentCreate,
    ) -> IncidentComment:
        """
        Create a comment for an incident.
        """

        incident = await self.incident_repository.get_by_id(
            incident_id
        )

        if incident is None:
            raise ValueError("Incident not found")

        if not incident.is_active:
            raise ValueError(
                "Resolved incident cannot receive comments"
            )

        comment = IncidentComment(
            incident_id=incident_id,
            user_id=user_id,
            content=data.content,
        )

        created = await self.repository.create(comment)

        await self.timeline_service.create(
            incident_id=incident_id,
            data=IncidentTimelineEventCreate(
                event_type="comment_added",
                title="Comment added",
                description=(
                    f"Comment added by user {user_id}"
                ),
            ),
        )

        return created

    async def list_comments(
        self,
        incident_id: str,
    ) -> list[IncidentComment]:
        """
        Return all comments for an incident.
        """

        incident = await self.incident_repository.get_by_id(
            incident_id
        )

        if incident is None:
            raise ValueError("Incident not found")

        return await self.repository.list_by_incident(
            incident_id
        )
