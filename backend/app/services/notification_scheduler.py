import logging
from datetime import datetime
from typing import Optional, Set
from zoneinfo import ZoneInfo
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.bot.bot import get_bot
from app.config import get_settings
from app.database import async_session_maker
from app.models.habit import Habit
from app.models.user import User
from app.services.knowledge import DailyKnowledgeService
from app.services.spiritual import SpiritualService

logger = logging.getLogger("grow_with_me.scheduler")

scheduler: Optional[AsyncIOScheduler] = None
_sent_cache: Set[str] = set()
_last_cache_cleanup_day: Optional[str] = None


def get_user_timezone(user: User) -> ZoneInfo:
    tz_name = user.timezone or "Asia/Almaty"
    # Default UTC users in Kazakhstan region to Asia/Almaty
    if tz_name == "UTC":
        tz_name = "Asia/Almaty"
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo("Asia/Almaty")


async def check_and_send_scheduled_notifications():
    global _sent_cache, _last_cache_cleanup_day
    bot = get_bot()
    if not bot:
        return

    settings = get_settings()
    app_url = settings.telegram_mini_app_url

    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            if not user.telegram_id:
                continue

            user_tz = get_user_timezone(user)
            now = datetime.now(user_tz)
            today_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")
            day_str = now.strftime("%A").lower()

            # Clean cache daily
            if _last_cache_cleanup_day != today_str:
                _sent_cache.clear()
                _last_cache_cleanup_day = today_str

            notif_cfg = user.notification_settings or {}

            # 1. Morning Greeting
            mg = notif_cfg.get("morning_greeting", {})
            if mg.get("enabled", True) and mg.get("time") == time_str:
                cache_key = f"{user.id}:morning:{today_str}"
                if cache_key not in _sent_cache:
                    _sent_cache.add(cache_key)
                    text = (
                        f"🌅 *Доброе утро, {user.first_name or 'друг'}!*\n\n"
                        f"Готовы к новому дню?\n"
                        f"• Проверьте свои привычки на сегодня\n"
                        f"• Изучите знание дня\n"
                        f"• Помните принцип: *«Маленькие шаги каждый день ведут к большим результатам»*.\n\n"
                        f"Продуктивного и вдохновляющего дня! ✨"
                    )
                    markup = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="🚀 Открыть Grow With Me", web_app=WebAppInfo(url=app_url))],
                            [InlineKeyboardButton(text="🎯 Привычки", callback_data="menu:habits")],
                        ]
                    )
                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=markup, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Failed to send morning greeting to {user.telegram_id}: {e}")

            # 2. Daily Knowledge
            dk = notif_cfg.get("daily_knowledge", {})
            if dk.get("enabled", True) and dk.get("time") == time_str:
                cache_key = f"{user.id}:knowledge:{today_str}"
                if cache_key not in _sent_cache:
                    _sent_cache.add(cache_key)
                    try:
                        ks = DailyKnowledgeService(session)
                        item = await ks.get_today_knowledge(user.id, now.date())
                        text = (
                            f"💡 *Знание дня: {item.title}*\n"
                            f"🏷 Категория: #{item.category}\n\n"
                            f"{item.summary}\n\n"
                            f"📖 _Нажмите кнопку ниже, чтобы прочитать полностью и сохранить инсайт:_"
                        )
                        markup = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="📖 Читать полностью", web_app=WebAppInfo(url=f"{app_url}/knowledge"))],
                            ]
                        )
                        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=markup, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Failed to send daily knowledge to {user.telegram_id}: {e}")

            # 3. Spiritual Name of Allah
            sn = notif_cfg.get("spiritual_name", {})
            if sn.get("enabled", True) and sn.get("time") == time_str:
                cache_key = f"{user.id}:spiritual:{today_str}"
                if cache_key not in _sent_cache:
                    _sent_cache.add(cache_key)
                    try:
                        ss = SpiritualService(session)
                        item = await ss.get_today_name(user.id, now.date())
                        text = (
                            f"🤲 *Прекрасное Имя Аллаха на сегодня*\n\n"
                            f"✨ *{item.transliteration}* — {item.arabic}\n"
                            f"«{item.meaning}»\n\n"
                            f"💭 *Вопрос для рефлексии:*\n_{item.reflection_prompt}_"
                        )
                        markup = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="🤲 Открыть духовность", web_app=WebAppInfo(url=f"{app_url}/spiritual"))],
                            ]
                        )
                        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=markup, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Failed to send spiritual name to {user.telegram_id}: {e}")

            # 4. Evening Reflection
            er = notif_cfg.get("evening_reflection", {})
            if er.get("enabled", True) and er.get("time") == time_str:
                cache_key = f"{user.id}:evening:{today_str}"
                if cache_key not in _sent_cache:
                    _sent_cache.add(cache_key)
                    text = (
                        f"🌙 *Добрый вечер, {user.first_name or 'друг'}!*\n\n"
                        f"День подходит к концу. Самое время замедлиться и зафиксировать итоги:\n"
                        f"• За что вы благодарны сегодня?\n"
                        f"• Что удалось сделать, а что отложить?\n"
                        f"• Какой главный урок вы извлекли?\n\n"
                        f"Заполните вечернюю рефлексию в дневнике ✍️"
                    )
                    markup = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="✍️ Заполнить рефлексию", web_app=WebAppInfo(url=f"{app_url}/journal"))],
                        ]
                    )
                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=markup, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Failed to send evening reflection to {user.telegram_id}: {e}")

            # 5. Sleep Reminder
            sr = notif_cfg.get("sleep_reminder", {})
            if sr.get("enabled", True) and sr.get("time") == time_str:
                cache_key = f"{user.id}:sleep:{today_str}"
                if cache_key not in _sent_cache:
                    _sent_cache.add(cache_key)
                    text = (
                        f"😴 *Пора готовиться ко сну*\n\n"
                        f"Здоровый сон восстанавливает силы, память и эмоциональный баланс.\n"
                        f"Отложите экраны, приглушите свет и отдохните.\n\n"
                        f"Спокойной ночи! 🌙"
                    )
                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Failed to send sleep reminder to {user.telegram_id}: {e}")

            # 6. Weekly Review (Sunday)
            wr = notif_cfg.get("weekly_review", {})
            target_day = wr.get("day", "sunday").lower()
            if wr.get("enabled", True) and day_str == target_day and wr.get("time") == time_str:
                cache_key = f"{user.id}:weekly:{today_str}"
                if cache_key not in _sent_cache:
                    _sent_cache.add(cache_key)
                    text = (
                        f"📊 *Воскресный обзор недели*\n\n"
                        f"Завершилась ещё одна неделя! 🚀\n"
                        f"Посмотрите ваш прогресс, процент выполнения привычек и спланируйте следующую неделю."
                    )
                    markup = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="📊 Посмотреть прогресс", web_app=WebAppInfo(url=f"{app_url}/progress"))],
                        ]
                    )
                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=markup, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Failed to send weekly review to {user.telegram_id}: {e}")

            # 7. Habit Reminders
            habits_res = await session.execute(
                select(Habit).where(Habit.user_id == user.id, Habit.is_active.is_(True))
            )
            habits = habits_res.scalars().all()
            for habit in habits:
                r_cfg = habit.reminder_settings or {}
                if r_cfg.get("enabled") and r_cfg.get("time") == time_str:
                    cache_key = f"{user.id}:habit:{habit.id}:{today_str}"
                    if cache_key not in _sent_cache:
                        _sent_cache.add(cache_key)
                        text = (
                            f"⏰ *Напоминание о привычке*\n\n"
                            f"{habit.icon or '✨'} *{habit.name}*\n"
                            f"Принцип: *«Никогда не пропускай дважды»* 💪"
                        )
                        markup = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="✅ Отметить выполненной", callback_data=f"toggle_habit:{habit.id}")],
                                [InlineKeyboardButton(text="🚀 Все привычки", web_app=WebAppInfo(url=f"{app_url}/habits"))],
                            ]
                        )
                        try:
                            await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=markup, parse_mode="Markdown")
                        except Exception as e:
                            logger.error(f"Failed to send habit reminder to {user.telegram_id}: {e}")


def start_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(check_and_send_scheduled_notifications, "interval", minutes=1, id="notifications_checker")
        scheduler.start()
        logger.info("Notification scheduler started successfully (interval: 1 min).")


def stop_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Notification scheduler stopped.")
        scheduler = None

