from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit
from app.models.habit_completion import HabitCompletion
from app.repositories.base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    def __init__(self, db: AsyncSession):
        super().__init__(Habit, db)

    async def get_user_habits(self, user_id: int, active_only: bool = True) -> List[Habit]:
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)
            .order_by(Habit.sort_order.asc(), Habit.id.asc())
        )
        if active_only:
            stmt = stmt.where(Habit.is_active == True)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_user_habit(self, habit_id: int, user_id: int) -> Optional[Habit]:
        stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_completion(
        self, habit_id: int, user_id: int, target_date: date
    ) -> Optional[HabitCompletion]:
        stmt = select(HabitCompletion).where(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date == target_date,
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_user_completions_for_date(
        self, user_id: int, target_date: date
    ) -> Dict[int, HabitCompletion]:
        stmt = select(HabitCompletion).where(
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date == target_date,
        )
        res = await self.db.execute(stmt)
        completions = res.scalars().all()
        return {c.habit_id: c for c in completions}

    async def toggle_completion(
        self,
        habit_id: int,
        user_id: int,
        target_date: date,
        actual_value: Optional[int] = None,
        note: Optional[str] = None,
    ) -> Tuple[bool, HabitCompletion | None]:
        """Toggles habit completion for the date. Returns (is_completed, record)."""
        existing = await self.get_completion(habit_id, user_id, target_date)
        if existing:
            await self.db.execute(
                delete(HabitCompletion).where(HabitCompletion.id == existing.id)
            )
            await self.db.flush()
            return False, None
        else:
            habit = await self.get_user_habit(habit_id, user_id)
            target = habit.target_value if habit else 1
            val = actual_value if actual_value is not None else target

            level = "target"
            if habit and habit.bonus_value and val >= habit.bonus_value:
                level = "bonus"
            elif habit and habit.min_value and val < habit.target_value:
                level = "min"

            new_c = HabitCompletion(
                habit_id=habit_id,
                user_id=user_id,
                completion_date=target_date,
                actual_value=val,
                completion_level=level,
                note=note,
            )
            self.db.add(new_c)
            await self.db.flush()
            await self.db.refresh(new_c)
            return True, new_c

    async def calculate_streak(
        self, habit_id: int, user_id: int, reference_date: date
    ) -> int:
        """
        Calculates consecutive completed days ending at today or yesterday.
        Respects 'Never miss twice' principle.
        """
        stmt = (
            select(HabitCompletion.completion_date)
            .where(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.user_id == user_id,
                HabitCompletion.completion_date <= reference_date,
            )
            .order_by(desc(HabitCompletion.completion_date))
        )
        res = await self.db.execute(stmt)
        dates = set(res.scalars().all())

        if not dates:
            return 0

        streak = 0
        check_date = reference_date

        # If today is not completed, streak could be active up to yesterday
        if check_date not in dates:
            check_date -= timedelta(days=1)
            if check_date not in dates:
                return 0

        while check_date in dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak
