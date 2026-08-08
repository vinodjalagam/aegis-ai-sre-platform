from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session.
    """
    async with SessionLocal() as session:
        yield session


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """
    Provide a UserRepository instance.
    """
    return UserRepository(session)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """
    Provide a UserService instance.
    """
    return UserService(repository)