from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.journal import JournalResponse, JournalSaveRequest, JournalStatsResponse
from app.services.journal import JournalService

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.get("/today", response_model=Optional[JournalResponse])
async def get_today_journal(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve today's reflection entry if it exists."""
    service = JournalService(db)
    return await service.get_by_date(current_user.id, date.today())


@router.post("", response_model=JournalResponse)
async def save_journal_entry(
    payload: JournalSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update daily reflection (structured answers, free text, intentions)."""
    service = JournalService(db)
    return await service.save_journal(current_user.id, payload)


@router.get("/history", response_model=List[JournalResponse])
async def get_journal_history(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List historical journal reflections."""
    service = JournalService(db)
    return await service.get_history(current_user.id, limit=limit, offset=offset)


@router.get("/stats", response_model=JournalStatsResponse)
async def get_journal_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get reflection streak and total entries count."""
    service = JournalService(db)
    return await service.get_stats(current_user.id, date.today())


@router.get("/{entry_date}", response_model=JournalResponse)
async def get_journal_by_date(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve journal reflection for a specific date."""
    service = JournalService(db)
    entry = await service.get_by_date(current_user.id, entry_date)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No journal entry found for {entry_date}",
        )
    return entry

