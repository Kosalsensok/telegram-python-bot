from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Build persistent main menu reply keyboard at the bottom of the Telegram screen.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎯 ជ្រើសរើស Mode (/mode)"),
                KeyboardButton(text="🖼️ វិភាគរូបភាព (Vision)")
            ],
            [
                KeyboardButton(text="💬 របៀបសួរសំណួរ (Help)"),
                KeyboardButton(text="📊 ស្ថិតិ (Stats)")
            ],
            [
                KeyboardButton(text="🧹 លុប History (Clear)"),
                KeyboardButton(text="ℹ️ អំពី Bot (About)")
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard



def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build quick action inline keyboard for start & help messages.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 ការណែនាំ (Help)", callback_data="cb_help"),
                InlineKeyboardButton(text="📊 ស្ថិតិ (Stats)", callback_data="cb_stats")
            ],
            [
                InlineKeyboardButton(text="🧹 លុប History (Clear)", callback_data="cb_clear"),
                InlineKeyboardButton(text="ℹ️ អំពី Bot (About)", callback_data="cb_about")
            ]
        ]
    )
    return keyboard
