from datetime import date
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.database import async_session_maker
from app.repositories.user import UserRepository
from app.services.habit import HabitService

router = Router(name="habits_router")


async def build_habits_markup(habits_list) -> InlineKeyboardMarkup:
    """Builds inline keyboard with one-tap toggle buttons for each habit."""
    buttons = []
    for h in habits_list:
        status_icon = "✅" if h.completed else "⬜"
        streak_str = f" 🔥{h.streak}" if h.streak > 0 else ""
        text = f"{status_icon} {h.icon} {h.name[:20]}{streak_str}"
        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"toggle_habit:{h.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("habits"))
async def handle_habits_command(message: Message):
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

        service = HabitService(session)
        today = date.today()
        today_habits = await service.get_today_habits(user.id, today)
        stats = await service.get_stats(user.id, today)
        await session.commit()

    completed = stats.today_completed
    total = stats.today_total
    percent = int(stats.completion_percentage)

    text = (
        f"🎯 **Твои привычки на сегодня:**\n\n"
        f"Выполнено: **{completed} из {total}** ({percent}%)\n"
        f"Принцип: *«Никогда не пропускай дважды»*\n\n"
        f"Нажми на кнопку, чтобы отметить:"
    )

    markup = await build_habits_markup(today_habits)
    await message.answer(text=text, reply_markup=markup, parse_mode="Markdown")


@router.callback_query(F.data.startswith("toggle_habit:"))
async def handle_toggle_callback(callback: CallbackQuery):
    habit_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        service = HabitService(session)
        today = date.today()
        res = await service.toggle_habit(user.id, habit_id, today)
        today_habits = await service.get_today_habits(user.id, today)
        stats = await service.get_stats(user.id, today)
        await session.commit()

    action_text = "Выполнено! 🎉" if res.completed else "Отметка снята"
    await callback.answer(f"{action_text} (серия: {res.streak} дн.)")

    completed = stats.today_completed
    total = stats.today_total
    percent = int(stats.completion_percentage)

    text = (
        f"🎯 **Твои привычки на сегодня:**\n\n"
        f"Выполнено: **{completed} из {total}** ({percent}%)\n"
        f"Принцип: *«Никогда не пропускай дважды»*\n\n"
        f"Нажми на кнопку, чтобы отметить:"
    )

    markup = await build_habits_markup(today_habits)
    try:
        await callback.message.edit_text(text=text, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        pass  # Message already up to date

