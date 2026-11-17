from datetime import datetime
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.habit import Habit
from app.models.habit_completion import HabitCompletion
from app.models.journal import JournalEntry
from app.models.note import Note
from app.models.personal_principle import PersonalPrinciple
from app.models.user import User
from app.models.weekly_assessment import WeeklyAssessment
from app.schemas.user import (
    PersonalPrincipleCreate,
    PersonalPrincipleResponse,
    PersonalPrincipleUpdate,
    UserDataExportResponse,
    UserResponse,
    UserUpdate,
)
from app.services.seed import seed_user_defaults

router = APIRouter(prefix="/profile", tags=["Profile & Settings"])


@router.get("", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve current user profile, identity statement, and settings."""
    await seed_user_defaults(current_user.id, db)
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

    await db.commit()
    await db.refresh(current_user)
    return current_user


# --- Personal Principles CRUD ---

@router.get("/principles", response_model=List[PersonalPrincipleResponse])
async def list_principles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all personal principles of the user."""
    await seed_user_defaults(current_user.id, db)
    stmt = (
        select(PersonalPrinciple)
        .where(PersonalPrinciple.user_id == current_user.id)
        .order_by(PersonalPrinciple.sort_order.asc(), PersonalPrinciple.id.asc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/principles", response_model=PersonalPrincipleResponse)
async def create_principle(
    payload: PersonalPrincipleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new personal principle."""
    principle = PersonalPrinciple(
        user_id=current_user.id,
        text=payload.text,
        category=payload.category,
        sort_order=payload.sort_order,
        is_active=True,
    )
    db.add(principle)
    await db.commit()
    await db.refresh(principle)
    return principle


@router.put("/principles/{principle_id}", response_model=PersonalPrincipleResponse)
async def update_principle(
    principle_id: int,
    payload: PersonalPrincipleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates an existing personal principle."""
    stmt = select(PersonalPrinciple).where(
        PersonalPrinciple.id == principle_id, PersonalPrinciple.user_id == current_user.id
    )
    res = await db.execute(stmt)
    record = res.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Принцип не найден")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(record, field, val)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/principles/{principle_id}")
async def delete_principle(
    principle_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a personal principle."""
    stmt = delete(PersonalPrinciple).where(
        PersonalPrinciple.id == principle_id, PersonalPrinciple.user_id == current_user.id
    )
    res = await db.execute(stmt)
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Принцип не найден")
    await db.commit()
    return {"status": "success", "message": "Принцип успешно удален"}


# --- Export & Reset Data ---

@router.get("/export", response_model=UserDataExportResponse)
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exports all user data in JSON format for backup and portability."""
    user_id = current_user.id

    # Habits
    habits_stmt = select(Habit).where(Habit.user_id == user_id)
    habits = list((await db.execute(habits_stmt)).scalars().all())

    # Principles
    principles_stmt = select(PersonalPrinciple).where(PersonalPrinciple.user_id == user_id)
    principles = list((await db.execute(principles_stmt)).scalars().all())

    # Journal
    journal_stmt = select(JournalEntry).where(JournalEntry.user_id == user_id)
    journal_entries = list((await db.execute(journal_stmt)).scalars().all())

    # Notes
    notes_stmt = select(Note).where(Note.user_id == user_id)
    notes = list((await db.execute(notes_stmt)).scalars().all())

    # Weekly Assessments
    assessments_stmt = select(WeeklyAssessment).where(WeeklyAssessment.user_id == user_id)
    assessments = list((await db.execute(assessments_stmt)).scalars().all())

    return UserDataExportResponse(
        export_date=datetime.utcnow().isoformat(),
        user={
            "id": current_user.id,
            "telegram_id": current_user.telegram_id,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "identity_statement": current_user.identity_statement,
            "ai_preferences": current_user.ai_preferences,
            "notification_settings": current_user.notification_settings,
        },
        principles=[
            {"id": p.id, "text": p.text, "category": p.category, "is_active": p.is_active}
            for p in principles
        ],
        habits=[
            {
                "id": h.id,
                "name": h.name,
                "category": h.category,
                "target_value": h.target_value,
                "target_unit": h.target_unit,
                "is_active": h.is_active,
            }
            for h in habits
        ],
        journal_entries=[
            {
                "entry_date": str(j.entry_date),
                "structured_answers": j.structured_answers,
                "free_text": j.free_text,
                "tomorrow_intentions": j.tomorrow_intentions,
            }
            for j in journal_entries
        ],
        notes=[
            {"id": n.id, "title": n.title, "content": n.content, "category": n.category}
            for n in notes
        ],
        weekly_assessments=[
            {
                "week_start": str(a.week_start),
                "week_end": str(a.week_end),
                "scores": {
                    "spirituality": a.score_spirituality,
                    "intellectual": a.score_intellectual,
                    "physical": a.score_physical,
                    "mental": a.score_mental,
                    "academic": a.score_academic,
                },
                "ai_report": a.ai_report,
            }
            for a in assessments
        ],
    )


@router.post("/reset")
async def reset_user_progress_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Clears all habit completions, journal entries, and reset stats while preserving
    user identity, habits catalog, and principles.
    """
    user_id = current_user.id
    await db.execute(delete(HabitCompletion).where(HabitCompletion.user_id == user_id))
    await db.execute(delete(JournalEntry).where(JournalEntry.user_id == user_id))
    await db.commit()
    return {"status": "success", "message": "Прогресс и отметки успешно сброшены"}
