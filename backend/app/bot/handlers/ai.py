import logging
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.ai.coach_service import AICoachService
from app.config import get_settings
from app.database import async_session_maker
from app.repositories.user import UserRepository

logger = logging.getLogger(__name__)
router = Router(name="ai_coach_router")
settings = get_settings()


@router.message(Command("coach"))
@router.message(Command("ask"))
async def handle_coach_command(message: Message):
    """
    Usage:
    /coach Как мне лучше распределить фокус на сегодня?
    /ask Что делать если сорвал режим сна?
    """
    user_id = message.from_user.id
    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)
    prompt = parts[1].strip() if len(parts) > 1 else ""

    if not prompt:
        await message.answer(
            "💬 **AI-Коуч Grow With Me**\n\n"
            "Напиши вопрос после команды, например:\n"
            "`/ask Как у меня дела на этой неделе?`\n"
            "`/ask Помоги настроиться на завтра`\n\n"
            "Или просто напиши мне любое сообщение в чат без слэша!",
            parse_mode="Markdown",
        )
        return

    # Send typing indicator
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

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

        service = AICoachService(session)
        res = await service.chat(user, prompt)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 Открыть AI-Коуча в приложении",
                    url=f"{settings.telegram_mini_app_url}/ai",
                )
            ]
        ]
    )

    try:
        await message.answer(res.message, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        # Fallback if markdown contains formatting characters
        await message.answer(res.message, reply_markup=markup, parse_mode=None)


@router.message(Command("analyze"))
async def handle_analyze_command(message: Message):
    """Deep analysis of user habits and consistency."""
    user_id = message.from_user.id
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

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

        service = AICoachService(session)
        analysis = await service.analyze_week(user)

    strengths_text = "\n".join(f"  • {s}" for s in analysis.strengths)
    weaknesses_text = "\n".join(f"  • {w}" for w in analysis.weaknesses)
    action_text = "\n".join(f"  {idx+1}. {a}" for idx, a in enumerate(analysis.action_plan))

    reply = (
        f"📊 **Анализ прогресса ({analysis.period})**\n\n"
        f"🎯 **Общая оценка:** {analysis.overall_score} / 10\n\n"
        f"💪 **Сильные стороны:**\n{strengths_text}\n\n"
        f"⚠️ **Узкие места:**\n{weaknesses_text}\n\n"
        f"💡 **Главный инсайт:**\n_{analysis.key_insight}_\n\n"
        f"📋 **План действий:**\n{action_text}"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📈 Полный дашборд",
                    url=f"{settings.telegram_mini_app_url}/growth",
                )
            ]
        ]
    )

    try:
        await message.answer(reply, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        await message.answer(reply, reply_markup=markup, parse_mode=None)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_direct_chat_with_coach(message: Message):
    """Answers any non-command message with the AI Coach."""
    user_id = message.from_user.id
    prompt = message.text.strip()
    if not prompt:
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

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

        service = AICoachService(session)
        res = await service.chat(user, prompt)

    try:
        await message.answer(res.message, parse_mode="Markdown")
    except Exception:
        await message.answer(res.message, parse_mode=None)

