from datetime import date, timedelta
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit
from app.repositories.habit import HabitRepository
from app.schemas.habit import (
    HabitStatsResponse,
    HabitTodayItem,
    HabitToggleResponse,
)
from app.services.seed import seed_user_defaults


class HabitService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = HabitRepository(db)

    async def get_today_habits(self, user_id: int, today: date) -> List[HabitTodayItem]:
        # Seed defaults if user has no habits yet
        await seed_user_defaults(user_id, self.db)

        habits = await self.repo.get_user_habits(user_id, active_only=True)
        completions_map = await self.repo.get_user_completions_for_date(user_id, today)

        items = []
        for h in habits:
            c = completions_map.get(h.id)
            streak = await self.repo.calculate_streak(h.id, user_id, today)
            items.append(
                HabitTodayItem(
                    id=h.id,
                    user_id=h.user_id,
                    name=h.name,
                    description=h.description,
                    icon=h.icon,
                    category=h.category,
                    target_type=h.target_type,
                    target_value=h.target_value,
                    target_unit=h.target_unit,
                    min_value=h.min_value,
                    bonus_value=h.bonus_value,
                    reminder_settings=h.reminder_settings,
                    sort_order=h.sort_order,
                    is_active=h.is_active,
                    created_at=h.created_at,
                    completed=c is not None,
                    actual_value=c.actual_value if c else None,
                    streak=streak,
                )
            )
        return items

    async def toggle_habit(
        self,
        user_id: int,
        habit_id: int,
        today: date,
        actual_value: int | None = None,
        note: str | None = None,
    ) -> HabitToggleResponse:
        completed, _ = await self.repo.toggle_completion(
            habit_id=habit_id,
            user_id=user_id,
            target_date=today,
            actual_value=actual_value,
            note=note,
        )
        streak = await self.repo.calculate_streak(habit_id, user_id, today)
        return HabitToggleResponse(
            habit_id=habit_id,
            target_date=today,
            completed=completed,
            streak=streak,
        )

    async def get_stats(self, user_id: int, today: date) -> HabitStatsResponse:
        await seed_user_defaults(user_id, self.db)
        habits = await self.repo.get_user_habits(user_id, active_only=True)
        today_completions = await self.repo.get_user_completions_for_date(user_id, today)

        today_total = len(habits)
        today_completed = len([h for h in habits if h.id in today_completions])
        percentage = (today_completed / today_total * 100) if today_total > 0 else 0.0

        # Calculate weekly completion
        week_start = today - timedelta(days=6)
        # Count all completions in the last 7 days
        weekly_completed_total = 0
        for i in range(7):
            d = week_start + timedelta(days=i)
            c_map = await self.repo.get_user_completions_for_date(user_id, d)
            weekly_completed_total += len([h for h in habits if h.id in c_map])

        weekly_possible = today_total * 7
        weekly_percentage = (
            (weekly_completed_total / weekly_possible * 100)
            if weekly_possible > 0
            else 0.0
        )

        streaks: Dict[int, int] = {}
        for h in habits:
            streaks[h.id] = await self.repo.calculate_streak(h.id, user_id, today)

        return HabitStatsResponse(
            today_completed=today_completed,
            today_total=today_total,
            completion_percentage=round(percentage, 1),
            weekly_completion_percentage=round(weekly_percentage, 1),
            active_streaks=streaks,
        )
