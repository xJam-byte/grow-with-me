from datetime import date
import pytest

from app.repositories.user import UserRepository
from app.services.knowledge import DailyKnowledgeService
from app.services.spiritual import SpiritualService


@pytest.mark.asyncio
async def test_daily_knowledge_flow(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=888777, username="content_tester")
    await db_session.flush()

    service = DailyKnowledgeService(db_session)
    today = date.today()

    # 1. Generate / retrieve topic
    topic = await service.get_or_create_daily(user.id, today)
    assert topic.topic_title is not None
    assert topic.category is not None
    assert len(topic.explanation) > 20
    assert topic.is_read is False

    # 2. Mark as read
    read_topic = await service.mark_as_read(user.id, topic.id)
    assert read_topic.is_read is True

    # 3. Update notes
    updated = await service.update_notes(user.id, topic.id, "Отличный концепт, применю в работе.")
    assert updated.user_notes == "Отличный концепт, применю в работе."


@pytest.mark.asyncio
async def test_spiritual_names_flow(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=777666, username="spiritual_tester")
    await db_session.flush()

    service = SpiritualService(db_session)
    today = date.today()

    # 1. Retrieve today's name of Allah
    daily = await service.get_today_name(user.id, today)
    assert daily.name.arabic_name is not None
    assert daily.name.transliteration is not None
    assert len(daily.name.explanation) > 10

    # 2. Add reflection
    saved = await service.update_reflection(user.id, daily.id, "Это напоминает мне быть терпеливее.")
    assert saved.user_reflection == "Это напоминает мне быть терпеливее."

    # 3. Catalog of names
    all_names = await service.get_all_names()
    assert len(all_names) >= 40
