"""
Authentication API.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.service import AuthService
from app.shared.responses.success import success_response

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/login")
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate a user and return a JWT access token.
    """

    try:
        token = await service.login(
            username=payload.username,
            password=payload.password,
        )

        return success_response(token)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc