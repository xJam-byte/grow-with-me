from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.habit import Habit
from app.models.user import User
from app.repositories.habit import HabitRepository
from app.schemas.habit import (
    HabitCreate,
    HabitResponse,
    HabitStatsResponse,
    HabitTodayItem,
    HabitToggleRequest,
    HabitToggleResponse,
    HabitUpdate,
)
from app.services.habit import HabitService

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("/today", response_model=List[HabitTodayItem])
async def get_today_habits(
    target_date: Optional[date] = Query(None, description="Date (YYYY-MM-DD), default is today"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all active habits for today with completion status and current streak."""
    service = HabitService(db)
    day = target_date or date.today()
    return await service.get_today_habits(current_user.id, day)


@router.post("/{habit_id}/toggle", response_model=HabitToggleResponse)
async def toggle_habit_completion(
    habit_id: int,
    payload: Optional[HabitToggleRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle completion of a habit for today or a specified date (one-tap action)."""
    service = HabitService(db)
    target_date = payload.target_date if payload and payload.target_date else date.today()
    actual_value = payload.actual_value if payload else None
    note = payload.note if payload else None

    # Check habit ownership
    repo = HabitRepository(db)
    habit = await repo.get_user_habit(habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    return await service.toggle_habit(
        user_id=current_user.id,
        habit_id=habit_id,
        today=target_date,
        actual_value=actual_value,
        note=note,
    )


@router.get("/stats", response_model=HabitStatsResponse)
async def get_habit_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get completion percentages and active streaks."""
    service = HabitService(db)
    return await service.get_stats(current_user.id, date.today())


@router.get("", response_model=List[HabitResponse])
async def list_habits(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all configured habits for the user."""
    repo = HabitRepository(db)
    return await repo.get_user_habits(current_user.id, active_only=active_only)


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom habit."""
    repo = HabitRepository(db)
    habit = Habit(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    return await repo.add(habit)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update habit details, targets, or active status."""
    repo = HabitRepository(db)
    habit = await repo.get_user_habit(habit_id, current_user.id)
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, val)

    await db.flush()
    await db.refresh(habit)
    return habit

