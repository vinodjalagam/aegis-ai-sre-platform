from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security.dependencies import get_current_user_id
from app.core.security.jwt import create_access_token
from app.core.security.password import verify_password
from app.modules.users.dependencies import get_user_service
from app.modules.users.schemas import UserResponse
from app.modules.users.service import UserService
from app.shared.responses.success import success_response
from app.modules.auth.schemas import LoginRequest, TokenResponse
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me")
async def get_me(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """
    Return the currently authenticated user.
    """

    user = await user_service.get_current_user(current_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return success_response(
        UserResponse.model_validate(user)
    )