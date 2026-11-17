import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import get_settings
from app.database import async_session_maker
from app.repositories.user import UserRepository
from app.services.progress import ProgressService

logger = logging.getLogger(__name__)
router = Router(name="progress_router")
settings = get_settings()


@router.message(Command("progress"))
@router.message(Command("growth"))
async def handle_progress_command(message: Message):
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

        service = ProgressService(session)
        dash = await service.get_dashboard(user.id)
        areas = await service.get_areas_progress(user.id)

    areas_lines = []
    for a in areas:
        trend_symbol = "↑" if a.trend == "up" else ("↓" if a.trend == "down" else "→")
        areas_lines.append(
            f"• {a.name}: **{a.objective_percentage}%** (оценка: {a.subjective_score}/5 {trend_symbol})"
        )

    text = (
        f"📊 **Твой прогресс в Grow With Me**\n\n"
        f"🎯 Сегодня: **{dash.today_completed}/{dash.today_total} привычек** ({dash.today_completion_rate}%)\n"
        f"📈 За неделю: **{dash.weekly_completion_rate}%**\n"
        f"🔥 Лучшая активная серия: **{dash.best_active_streak} дн.**\n\n"
        f"🌟 **5 областей развития (за 7 дней):**\n"
        + "\n".join(areas_lines)
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📈 Открыть полный дашборд",
                    url=f"{settings.telegram_mini_app_url}/growth",
                )
            ]
        ]
    )
    await message.answer(text=text, reply_markup=markup, parse_mode="Markdown")


@router.message(Command("assessment"))
async def handle_assessment_command(message: Message):
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

        service = ProgressService(session)
        latest = await service.get_latest_assessment(user.id)

    if latest:
        report_status = "✅ AI-отчёт сформирован" if latest.ai_report else "⏳ Ожидает генерации AI-отчёта"
        text = (
            f"📋 **Недельная самооценка ({latest.week_start} — {latest.week_end})**\n\n"
            f"• Духовность: **{latest.score_spirituality}/5**\n"
            f"• Интеллект: **{latest.score_intellectual}/5**\n"
            f"• Тело: **{latest.score_physical}/5**\n"
            f"• Ментальность: **{latest.score_mental}/5**\n"
            f"• Академическое: **{latest.score_academic}/5**\n\n"
            f"Статус: {report_status}\n"
            f"Приоритеты: _{latest.next_week_priorities or 'не указаны'}_"
        )
    else:
        text = (
            "📋 **Недельная самооценка**\n\n"
            "Ты ещё не заполнял самооценку на этой неделе.\n"
            "Каждое воскресенье выделяй 10 минут, чтобы оценить 5 областей и получить глубокий AI-анализ!"
        )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Заполнить самооценку",
                    url=f"{settings.telegram_mini_app_url}/growth",
                )
            ]
        ]
    )
    await message.answer(text=text, reply_markup=markup, parse_mode="Markdown")
