from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:
    """
    Repository for User database operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """
        Create a new user.
        """
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """
        Get a user by ID.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Get a user by email.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by username.
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[User]:
        """
        Return all users.
        """
        result = await self.session.execute(
            select(User).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, user: User) -> User:
        """
        Persist updates.
        """
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """
        Delete a user.
        """
        await self.session.delete(user)
        await self.session.commit()