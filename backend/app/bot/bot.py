import logging
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import content, habits, journal_notes, start
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

bot: Optional[Bot] = None
dp: Dispatcher = Dispatcher()

# Register routers
dp.include_router(start.router)
dp.include_router(habits.router)
dp.include_router(content.router)
dp.include_router(journal_notes.router)


def get_bot() -> Optional[Bot]:
    global bot
    if bot is None and settings.telegram_bot_token:
        bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        )
    return bot
