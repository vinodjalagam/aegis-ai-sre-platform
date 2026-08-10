"""
Incident comment repository.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.comments.models import IncidentComment


class IncidentCommentRepository:
    """
    Database operations for incident comments.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        comment: IncidentComment,
    ) -> IncidentComment:
        """
        Create and persist an incident comment.
        """

        self.db.add(comment)

        await self.db.commit()
        await self.db.refresh(comment)

        return comment

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentComment]:
        """
        Return comments for an incident.
        """

        result = await self.db.execute(
            select(IncidentComment)
            .where(
                IncidentComment.incident_id == incident_id
            )
            .order_by(
                IncidentComment.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        comment_id: str,
    ) -> IncidentComment | None:
        """
        Get a comment by ID.
        """

        result = await self.db.execute(
            select(IncidentComment).where(
                IncidentComment.id == comment_id
            )
        )

        return result.scalar_one_or_none()
