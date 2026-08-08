from __future__ import annotations


from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Shared user fields.
    """

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """
    Schema used to create a user.
    """

    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """
    Schema used to update a user.
    """

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class UserResponse(UserBase):
    """
    User returned by the API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_superuser: bool


class UserListResponse(BaseModel):
    """
    List of users.
    """

    items: list[UserResponse]
    total: int