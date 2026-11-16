from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.spiritual import (
    AllahNameResponse,
    DailySpiritualResponse,
    SpiritualReflectionUpdate,
)
from app.services.spiritual import SpiritualService

router = APIRouter(prefix="/spiritual", tags=["Spiritual"])


@router.get("/today", response_model=DailySpiritualResponse)
async def get_today_name(
    target_date: Optional[date] = Query(None, description="Date (YYYY-MM-DD), default is today"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve today's Name of Allah (Asma ul-Husna) with explanation and reflection."""
    service = SpiritualService(db)
    day = target_date or date.today()
    return await service.get_today_name(current_user.id, day)


@router.get("/names", response_model=List[AllahNameResponse])
async def get_all_names(
    db: AsyncSession = Depends(get_db),
):
    """Get the full catalog of 99 Names of Allah with transliteration and verified meanings."""
    service = SpiritualService(db)
    return await service.get_all_names()


@router.post("/{daily_id}/reflection", response_model=DailySpiritualResponse)
async def save_reflection(
    daily_id: int,
    payload: SpiritualReflectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or update personal reflection on this Name of Allah."""
    service = SpiritualService(db)
    try:
        return await service.update_reflection(current_user.id, daily_id, payload.reflection)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{daily_id}/favorite")
async def toggle_spiritual_favorite(
    daily_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite status on a daily spiritual entry."""
    service = SpiritualService(db)
    try:
        is_favorite = await service.toggle_favorite(current_user.id, daily_id)
        return {"id": daily_id, "is_favorite": is_favorite}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
