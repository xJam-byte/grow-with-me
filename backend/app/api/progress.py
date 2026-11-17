from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.progress import (
    AreaProgressItem,
    DashboardProgressResponse,
    WeeklyAssessmentCreate,
    WeeklyAssessmentResponse,
)
from app.services.progress import ProgressService

router = APIRouter(tags=["Progress & Analytics"])


@router.get("/progress/dashboard", response_model=DashboardProgressResponse)
async def get_progress_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns overall progress dashboard: today, weekly, monthly stats, heatmaps, and streaks."""
    service = ProgressService(db)
    return await service.get_dashboard(user.id)


@router.get("/progress/areas", response_model=List[AreaProgressItem])
async def get_areas_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns breakdown across the 5 development areas (objective vs subjective)."""
    service = ProgressService(db)
    return await service.get_areas_progress(user.id)


@router.post("/assessment", response_model=WeeklyAssessmentResponse)
async def save_weekly_assessment(
    payload: WeeklyAssessmentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates or updates user's weekly self-assessment."""
    service = ProgressService(db)
    return await service.save_assessment(user.id, payload)


@router.get("/assessment/latest", response_model=Optional[WeeklyAssessmentResponse])
async def get_latest_assessment(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the most recent weekly assessment for the user."""
    service = ProgressService(db)
    return await service.get_latest_assessment(user.id)


@router.get("/assessment/history", response_model=List[WeeklyAssessmentResponse])
async def get_assessment_history(
    limit: int = Query(12, ge=1, le=52),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns history of weekly self-assessments."""
    service = ProgressService(db)
    return await service.get_assessment_history(user.id, limit=limit)


@router.post("/assessment/{assessment_id}/generate-report", response_model=WeeklyAssessmentResponse)
async def generate_weekly_report(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates comprehensive AI weekly review for the given assessment."""
    service = ProgressService(db)
    try:
        return await service.generate_ai_report(user.id, assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
