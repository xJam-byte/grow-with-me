from datetime import date
import pytest
from httpx import ASGITransport, AsyncClient

from app.database import async_session_maker
from app.main import app
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.habit import HabitService


@pytest.mark.asyncio
async def test_habit_service_seed_and_toggle():
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_or_create(telegram_id=999888, username="testuser")
        await session.commit()

        service = HabitService(session)
        today = date.today()

        # 1. Get today's habits (triggers auto-seeding of 10 habits)
        habits = await service.get_today_habits(user.id, today)
        assert len(habits) >= 10
        first_habit = habits[0]
        assert first_habit.completed is False

        # 2. Toggle completion on
        res = await service.toggle_habit(user.id, first_habit.id, today)
        assert res.completed is True
        assert res.streak == 1

        # 3. Toggle completion off
        res_off = await service.toggle_habit(user.id, first_habit.id, today)
        assert res_off.completed is False
        assert res_off.streak == 0
