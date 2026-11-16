from datetime import date
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import get_settings
from app.database import async_session_maker
from app.repositories.user import UserRepository
from app.services.knowledge import DailyKnowledgeService
from app.services.spiritual import SpiritualService

router = Router(name="content_router")
settings = get_settings()


@router.message(Command("knowledge"))
@router.callback_query(F.data == "menu:knowledge")
async def handle_knowledge(event: Message | CallbackQuery):
    user_id = event.from_user.id
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)
        if not user:
            user = await user_repo.get_or_create(telegram_id=user_id, username=event.from_user.username)
            await session.commit()

        service = DailyKnowledgeService(session)
        topic = await service.get_or_create_daily(user.id, date.today())
        await session.commit()

    text = (
        f"📖 **Тема дня: {topic.topic_title}**\n"
        f"Категория: *{topic.category}*\n\n"
        f"💡 {topic.introduction}\n\n"
        f"🔬 **Факт:** {topic.facts}\n\n"
        f"🎯 **Практика:** {topic.practical_application}\n\n"
        f"❓ **Вопрос для размышления:**\n"
        f"*{topic.reflection_question}*"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 Открыть в Mini App",
                    url=f"{settings.telegram_mini_app_url}/knowledge",
                )
            ]
        ]
    )

    if isinstance(event, CallbackQuery):
        await event.answer()
        await event.message.answer(text=text, reply_markup=markup, parse_mode="Markdown")
    else:
        await event.answer(text=text, reply_markup=markup, parse_mode="Markdown")


@router.message(Command("spiritual"))
@router.callback_query(F.data == "menu:spiritual")
async def handle_spiritual(event: Message | CallbackQuery):
    user_id = event.from_user.id
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)
        if not user:
            user = await user_repo.get_or_create(telegram_id=user_id, username=event.from_user.username)
            await session.commit()

        service = SpiritualService(session)
        daily = await service.get_today_name(user.id, date.today())
        await session.commit()

    name = daily.name
    text = (
        f"🤲 **Имя Аллаха дня (#{name.number} из 99)**\n\n"
        f"🌟 **{name.arabic_name}** — *{name.transliteration}*\n"
        f"«**{name.meaning_ru}**»\n\n"
        f"📖 **Толкование:**\n{name.explanation}\n\n"
        f"✨ **Связь с характером:**\n{name.life_reflection}\n\n"
        f"📚 *{name.source_reference or ''}*"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤲 Открыть в Mini App",
                    url=f"{settings.telegram_mini_app_url}/spiritual",
                )
            ]
        ]
    )

    if isinstance(event, CallbackQuery):
        await event.answer()
        await event.message.answer(text=text, reply_markup=markup, parse_mode="Markdown")
    else:
        await event.answer(text=text, reply_markup=markup, parse_mode="Markdown")

