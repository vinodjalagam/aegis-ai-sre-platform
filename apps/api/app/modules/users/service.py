from __future__ import annotations

from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.core.security.password import hash_password


class UserService:
    """
    Business logic for users.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
        """
        Create a new user.
        """

        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ValueError("Email already exists")

        existing = await self.repository.get_by_username(data.username)
        if existing:
            raise ValueError("Username already exists")

        user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )

        return await self.repository.create(user)

    async def get_user(self, user_id: str) -> User | None:
        """
        Get user by ID.
        """
        return await self.repository.get_by_id(user_id)
    async def get_current_user(self, user_id: str) -> User | None:
        """
        Get the currently authenticated user.
        """
        return await self.repository.get_by_id(user_id)

    async def list_users(self) -> list[User]:
        """
        List all users.
        """
        return await self.repository.list()

    async def update_user(
        self,
        user_id: str,
        data: UserUpdate,
    ) -> User | None:
        """
        Update a user.
        """

        user = await self.repository.get_by_id(user_id)

        if not user:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = hash_password(
                update_data.pop("password")
            )
        for key, value in update_data.items():
            setattr(user, key, value)

        return await self.repository.update(user)

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        """

        user = await self.repository.get_by_id(user_id)

        if not user:
            return False

        await self.repository.delete(user)
        return True