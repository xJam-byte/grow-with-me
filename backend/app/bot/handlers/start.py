from datetime import date
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.bot.keyboards.inline import get_main_menu_keyboard
from app.config import get_settings
from app.database import async_session_maker
from app.repositories.user import UserRepository
from app.services.knowledge import DailyKnowledgeService
from app.services.spiritual import SpiritualService

router = Router(name="start_router")


@router.message(Command("test_notifications"))
@router.message(Command("reminders"))
async def handle_test_notifications(message: Message):
    """Sends current notification schedule and demonstrates notification previews."""
    settings = get_settings()
    app_url = settings.telegram_mini_app_url
    user_id = message.from_user.id

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)
        if not user:
            user = await user_repo.get_or_create(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
            )
            await session.commit()

        ks = DailyKnowledgeService(session)
        knowledge = await ks.get_today_knowledge(user.id, date.today())
        ss = SpiritualService(session)
        spiritual = await ss.get_today_name(user.id, date.today())
        await session.commit()

    schedule_text = (
        "🔔 **Расписание ежедневных напоминаний:**\n\n"
        "• 🌅 **07:30** — Утренний обзор и фокус дня\n"
        "• 💡 **09:00** — Знание дня (психология, история, наука)\n"
        "• 🤲 **12:00** — Прекрасное Имя Аллаха и рефлексия\n"
        "• 🌙 **21:30** — Вечерняя рефлексия и итоги\n"
        "• 😴 **23:00** — Напоминание о подготовке ко сну\n"
        "• 📊 **Вс 19:00** — Итоговый недельный обзор прогресса\n\n"
        "Ниже примеры уведомлений, которые приходят по расписанию 👇"
    )
    await message.answer(schedule_text, parse_mode="Markdown")

    # Sample knowledge notification
    k_text = (
        f"💡 **[Пример в 09:00] Знание дня: {knowledge.title}**\n"
        f"🏷 Категория: #{knowledge.category}\n\n"
        f"{knowledge.summary}\n\n"
        f"📖 *Нажмите кнопку ниже, чтобы прочитать полностью:*"
    )
    k_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Читать статью", web_app=WebAppInfo(url=f"{app_url}/knowledge"))],
        ]
    )
    await message.answer(k_text, reply_markup=k_markup, parse_mode="Markdown")

    # Sample spiritual notification
    s_text = (
        f"🤲 **[Пример в 12:00] Прекрасное Имя Аллаха**\n\n"
        f"✨ *{spiritual.transliteration}* — {spiritual.arabic}\n"
        f"«{spiritual.meaning}»\n\n"
        f"💭 *Вопрос для рефлексии:*\n_{spiritual.reflection_prompt}_"
    )
    s_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤲 Открыть духовность", web_app=WebAppInfo(url=f"{app_url}/spiritual"))],
        ]
    )
    await message.answer(s_text, reply_markup=s_markup, parse_mode="Markdown")


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

