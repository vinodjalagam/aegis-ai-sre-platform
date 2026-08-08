"""
Authentication service.
"""

from app.core.security.jwt import create_access_token
from app.core.security.password import verify_password
from app.modules.auth.schemas import TokenResponse
from app.modules.users.repository import UserRepository


class AuthService:
    """
    Business logic for authentication.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def login(
        self,
        username: str,
        password: str,
    ) -> TokenResponse:
        """
        Authenticate a user and return a JWT token.
        """

        user = await self.repository.get_by_username(username)

        if not user:
            raise ValueError("Invalid username or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")

        access_token = create_access_token(user.id)

        return TokenResponse(
            access_token=access_token,
        )