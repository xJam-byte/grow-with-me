from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retrieve current user profile, identity statement, and settings."""
    return current_user


@router.put("", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile, identity statement, AI preferences or settings."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.flush()
    await db.refresh(current_user)
    return current_user
