"""
Assembles user state and context into compact prompt additions for the AI Coach.
"""

from datetime import date
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_principle import PersonalPrinciple
from app.models.user import User
from app.services.habit import HabitService


async def build_user_context(user: User, db: AsyncSession, context_type: str = "general") -> str:
    """
    Builds a structured contextual summary of the user's current progress,
    habits, and core principles.
    """
    today = date.today()
    day_name_ru = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ][today.weekday()]

    # Load principles
    principles_stmt = (
        select(PersonalPrinciple.text)
        .where(PersonalPrinciple.user_id == user.id, PersonalPrinciple.is_active == True)
        .order_by(PersonalPrinciple.sort_order.asc())
        .limit(8)
    )
    res = await db.execute(principles_stmt)
    principles = list(res.scalars().all())

    # Load today's habits
    habit_service = HabitService(db)
    today_habits = await habit_service.get_today_habits(user.id, today)
    completed_habits = [h.name for h in today_habits if h.completed]
    pending_habits = [h.name for h in today_habits if not h.completed]

    identity = user.identity_statement or {}
    vision = identity.get("vision", "Стань тем, кем ты гордишься.")
    values = identity.get("values", [])

    lines = [
        f"--- ТЕКУЩИЙ КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ ({day_name_ru}, {today.strftime('%d.%m.%Y')}) ---",
        f"Имя: {user.first_name or 'Пользователь'}",
        f"Главный вижн: «{vision}»",
    ]

    if values:
        lines.append(f"Ценности: {', '.join(values[:5])}")

    if principles:
        lines.append("Ключевые личные принципы:")
        for p in principles[:5]:
            lines.append(f"  • {p}")

    lines.append(
        f"Привычки на сегодня ({len(completed_habits)}/{len(today_habits)} выполнено):"
    )
    if completed_habits:
        lines.append(f"  ✅ Сделано: {', '.join(completed_habits)}")
    if pending_habits:
        lines.append(f"  ⏳ Осталось сделать: {', '.join(pending_habits)}")
    else:
        lines.append("  🎉 Все привычки на сегодня выполнены!")

    lines.append("--------------------------------------------------")
    return "\n".join(lines)

