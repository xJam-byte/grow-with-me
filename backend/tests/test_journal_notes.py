from datetime import date
import pytest

from app.repositories.user import UserRepository
from app.schemas.journal import JournalSaveRequest
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.journal import JournalService
from app.services.note import NoteService


@pytest.mark.asyncio
async def test_journal_flow(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=555444, username="journal_user")
    await db_session.flush()

    service = JournalService(db_session)
    today = date.today()

    # 1. Save journal entry
    req = JournalSaveRequest(
        entry_date=today,
        structured_answers={"0": "Проснулся в 7:00 и прочитал 15 страниц", "4": "За здоровье и мир"},
        free_text="Продуктивный и спокойный день.",
        tomorrow_intentions="Завершить проект и пойти на тренировку.",
        mood="focused",
        tags=["discipline", "reading"],
    )
    saved = await service.save_journal(user.id, req)
    assert saved.id is not None
    assert saved.free_text == "Продуктивный и спокойный день."
    assert saved.structured_answers["0"] == "Проснулся в 7:00 и прочитал 15 страниц"

    # 2. Retrieve by date
    retrieved = await service.get_by_date(user.id, today)
    assert retrieved is not None
    assert retrieved.tomorrow_intentions == "Завершить проект и пойти на тренировку."

    # 3. Check stats
    stats = await service.get_stats(user.id, today)
    assert stats.total_entries >= 1
    assert stats.streak_days >= 1


@pytest.mark.asyncio
async def test_notes_flow(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=444333, username="notes_user")
    await db_session.flush()

    service = NoteService(db_session)

    # 1. Create note
    created = await service.create_note(
        user.id,
        NoteCreate(
            title="Идея нового проекта",
            content="Использовать PostgreSQL fulltext search для мгновенного поиска.",
            category="ideas",
            tags=["tech", "architecture"],
        ),
    )
    assert created.id is not None
    assert created.title == "Идея нового проекта"

    # 2. Search notes
    results = await service.search_notes(user.id, "PostgreSQL")
    assert len(results) >= 1
    assert results[0].id == created.id

    # 3. Toggle favorite
    is_fav = await service.toggle_favorite(user.id, created.id)
    assert is_fav is True

    # 4. Update note
    updated = await service.update_note(
        user.id, created.id, NoteUpdate(title="Идея: Архитектура поиска")
    )
    assert updated.title == "Идея: Архитектура поиска"

    # 5. Delete note
    deleted = await service.delete_note(user.id, created.id)
    assert deleted is True
    assert await service.get_note(user.id, created.id) is None
