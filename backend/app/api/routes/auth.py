from fastapi import APIRouter

from app.core.auth import CurrentUser
from app.schemas.user import UserResponse

router = APIRouter(tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
