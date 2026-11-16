from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.inline import get_main_menu_keyboard
from app.config import get_settings
from app.database import async_session_maker
from app.repositories.user import UserRepository

router = Router(name="start_router")


@router.message(CommandStart())
async def handle_start(message: Message):
    settings = get_settings()
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Auto-register or update user in database
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        await user_repo.get_or_create(
            telegram_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        await session.commit()

    greeting = (
        f"Ассаляму алейкум, {first_name or 'друг'}!\n\n"
        f"🌟 **Добро пожаловать в Grow With Me** — твою персональную систему развития.\n\n"
        f"Здесь ты сможешь:\n"
        f"• Держать дисциплину и отслеживать привычки\n"
        f"• Изучать каждый день что-то новое и углублять духовность\n"
        f"• Вести вечернюю рефлексию и заметки\n"
        f"• Работать с личным AI-коучем\n\n"
        f"Нажми кнопку ниже, чтобы открыть приложение 👇"
    )

    await message.answer(
        text=greeting,
        reply_markup=get_main_menu_keyboard(settings.telegram_mini_app_url),
        parse_mode="Markdown",
    )
