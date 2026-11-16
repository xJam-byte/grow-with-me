from datetime import date
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import get_settings
from app.database import async_session_maker
from app.repositories.user import UserRepository
from app.schemas.note import NoteCreate
from app.services.journal import JournalService
from app.services.note import NoteService

router = Router(name="journal_notes_router")
settings = get_settings()


@router.message(Command("journal"))
async def handle_journal_command(message: Message):
    user_id = message.from_user.id
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)
        if not user:
            user = await user_repo.get_or_create(telegram_id=user_id, username=message.from_user.username)
            await session.commit()

        service = JournalService(session)
        entry = await service.get_by_date(user.id, date.today())
        stats = await service.get_stats(user.id, date.today())
        await session.commit()

    if entry:
        status_text = "✅ **Сегодняшняя рефлексия заполнена!**"
        preview = f"\n\nПланы на завтра: *{entry.tomorrow_intentions or 'не указаны'}*"
    else:
        status_text = "📝 **Вечерняя рефлексия ещё не заполнена.**"
        preview = "\n\nВыдели 5-10 минут, чтобы честно подвести итоги дня."

    text = (
        f"{status_text}{preview}\n\n"
        f"🔥 Серия рефлексии: **{stats.streak_days} дн.** | Всего записей: **{stats.total_entries}**"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Открыть Журнал",
                    url=f"{settings.telegram_mini_app_url}/journal",
                )
            ]
        ]
    )
    await message.answer(text=text, reply_markup=markup, parse_mode="Markdown")


@router.message(Command("note"))
async def handle_quick_note(message: Message):
    """
    Usage: /note Текст твоей мысли или идеи...
    Saves directly to user's personal notes in Grow With Me.
    """
    raw_text = message.text or ""
    # Extract content after /note
    parts = raw_text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "✍️ **Быстрая заметка:**\n"
            "Напиши текст после команды, например:\n"
            "`/note Изучить эффект Даннинга-Крюгера в психологии`",
            parse_mode="Markdown",
        )
        return

    content = parts[1].strip()
    # Title is the first line or first 50 chars
    title = content.split("\n")[0][:60]

    user_id = message.from_user.id
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)
        if not user:
            user = await user_repo.get_or_create(telegram_id=user_id, username=message.from_user.username)
            await session.commit()

        service = NoteService(session)
        await service.create_note(
            user.id,
            NoteCreate(
                title=title,
                content=content,
                category="quick_notes",
                tags=["telegram"],
            ),
        )
        await session.commit()

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Открыть все заметки",
                    url=f"{settings.telegram_mini_app_url}/notes",
                )
            ]
        ]
    )
    await message.answer(
        f"✅ **Заметка сохранена в базу знаний!**\n\n"
        f"📌 *{title}*",
        reply_markup=markup,
        parse_mode="Markdown",
    )
