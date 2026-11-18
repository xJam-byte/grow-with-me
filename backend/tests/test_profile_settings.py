from datetime import date
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.habit_completion import HabitCompletion
from app.models.personal_principle import PersonalPrinciple
from app.repositories.user import UserRepository
from app.services.seed import seed_user_defaults


@pytest.mark.asyncio
async def test_principles_crud(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=888333222, username="principles_tester")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": "tma dev_888333222"},
    ) as ac:
        # 1. List principles
        res = await ac.get("/api/profile/principles")
        assert res.status_code == 200
        principles = res.json()
        assert len(principles) >= 8

        # 2. Create new principle
        create_res = await ac.post(
            "/api/profile/principles",
            json={"text": "Никогда не начинай день без плана", "category": "discipline"},
        )
        assert create_res.status_code == 200
        new_p = create_res.json()
        assert new_p["text"] == "Никогда не начинай день без плана"
        principle_id = new_p["id"]

        # 3. Update principle
        update_res = await ac.put(
            f"/api/profile/principles/{principle_id}",
            json={"is_active": False},
        )
        assert update_res.status_code == 200
        assert update_res.json()["is_active"] is False

        # 4. Delete principle
        del_res = await ac.delete(f"/api/profile/principles/{principle_id}")
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_data_export_and_reset(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=999444111, username="export_tester")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": "tma dev_999444111"},
    ) as ac:
        # 1. Export data
        export_res = await ac.get("/api/profile/export")
        assert export_res.status_code == 200
        data = export_res.json()
        assert "user" in data
        assert "habits" in data
        assert "principles" in data
        assert len(data["habits"]) == 10

        # 2. Reset progress
        reset_res = await ac.post("/api/profile/reset")
        assert reset_res.status_code == 200
        assert reset_res.json()["status"] == "success"

