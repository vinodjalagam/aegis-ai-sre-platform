"""
Authentication dependencies.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    """
    Dependency that provides an AuthService instance.
    """

    repository = UserRepository(db)
    return AuthService(repository)