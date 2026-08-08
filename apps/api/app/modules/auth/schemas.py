from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    User login request.
    """

    username: str
    password: str


class TokenResponse(BaseModel):
    """
    JWT access token response.
    """

    access_token: str
    token_type: str = "bearer"