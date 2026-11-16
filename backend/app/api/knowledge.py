from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeAskRequest,
    KnowledgeAskResponse,
    KnowledgeNoteUpdate,
    KnowledgeResponse,
)
from app.services.knowledge import DailyKnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("/today", response_model=KnowledgeResponse)
async def get_today_knowledge(
    target_date: Optional[date] = Query(None, description="Date (YYYY-MM-DD), default is today"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve today's educational knowledge topic (generates if not yet created)."""
    service = DailyKnowledgeService(db)
    day = target_date or date.today()
    return await service.get_or_create_daily(current_user.id, day)


@router.post("/{knowledge_id}/read", response_model=KnowledgeResponse)
async def mark_knowledge_read(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a daily knowledge topic as read."""
    service = DailyKnowledgeService(db)
    try:
        return await service.mark_as_read(current_user.id, knowledge_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{knowledge_id}/favorite")
async def toggle_knowledge_favorite(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite status on a knowledge topic."""
    service = DailyKnowledgeService(db)
    try:
        is_favorite = await service.toggle_favorite(current_user.id, knowledge_id)
        return {"id": knowledge_id, "is_favorite": is_favorite}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{knowledge_id}/notes", response_model=KnowledgeResponse)
async def update_knowledge_notes(
    knowledge_id: int,
    payload: KnowledgeNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Attach personal insights / notes to this topic."""
    service = DailyKnowledgeService(db)
    try:
        return await service.update_notes(current_user.id, knowledge_id, payload.notes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/history", response_model=List[KnowledgeResponse])
async def get_knowledge_history(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List previously studied knowledge topics."""
    service = DailyKnowledgeService(db)
    return await service.get_history(current_user.id, limit=limit)


@router.post("/{knowledge_id}/ask", response_model=KnowledgeAskResponse)
async def ask_topic_question(
    knowledge_id: int,
    payload: KnowledgeAskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ask AI a follow-up question regarding this specific topic."""
    service = DailyKnowledgeService(db)
    try:
        return await service.ask_question(current_user.id, knowledge_id, payload.question)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

