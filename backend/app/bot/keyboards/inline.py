from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def get_main_menu_keyboard(mini_app_url: str) -> InlineKeyboardMarkup:
    """Creates inline keyboard with a direct button to open the Telegram Mini App and quick content."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть Grow With Me",
                    web_app=WebAppInfo(url=mini_app_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="✨ Привычки",
                    callback_data="menu:habits",
                ),
                InlineKeyboardButton(
                    text="📖 Тема дня",
                    callback_data="menu:knowledge",
                ),
                InlineKeyboardButton(
                    text="🤲 Имя Аллаха",
                    callback_data="menu:spiritual",
                ),
            ],
        ]
    )
