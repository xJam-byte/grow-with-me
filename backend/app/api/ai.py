from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.coach_service import AICoachService
from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.ai import (
    AIAnalysisResponse,
    AIChatRequest,
    AIChatResponse,
    AIMessageResponse,
    AIPreferencesUpdate,
    AIUsageResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Coach"])


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_coach(
    payload: AIChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Interactive message with personal AI Coach with tool calling and context injection."""
    service = AICoachService(db)
    return await service.chat(user, payload.message, payload.context_type)


@router.get("/history", response_model=List[AIMessageResponse])
async def get_chat_history(
    limit: int = Query(30, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns conversation history with the AI Coach."""
    service = AICoachService(db)
    return await service.get_history(user.id, limit=limit)


@router.delete("/history")
async def clear_chat_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resets chat history with the coach."""
    service = AICoachService(db)
    await service.clear_history(user.id)
    return {"status": "success", "message": "История диалога очищена"}


@router.post("/analyze/week", response_model=AIAnalysisResponse)
async def analyze_week(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deep weekly analysis of habits, consistency, and growth areas."""
    service = AICoachService(db)
    return await service.analyze_week(user)


@router.get("/usage", response_model=AIUsageResponse)
async def get_ai_usage(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns token consumption and budget stats for the user."""
    service = AICoachService(db)
    return await service.get_token_usage_stats(user)


@router.put("/preferences")
async def update_ai_preferences(
    payload: AIPreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates AI coach preferences (tone, privacy permissions for journal/notes, daily token limit)."""
    current_prefs = dict(user.ai_preferences or {})
    if payload.tone is not None:
        current_prefs["tone"] = payload.tone
    if payload.allow_journal_access is not None:
        current_prefs["allow_journal_access"] = payload.allow_journal_access
    if payload.allow_notes_access is not None:
        current_prefs["allow_notes_access"] = payload.allow_notes_access
    if payload.max_daily_tokens is not None:
        current_prefs["max_daily_tokens"] = payload.max_daily_tokens

    user.ai_preferences = current_prefs
    await db.commit()
    await db.refresh(user)
    return {"status": "success", "ai_preferences": user.ai_preferences}

