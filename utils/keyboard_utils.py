from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardRemove
)

def get_main_reply_keyboard() -> ReplyKeyboardRemove:
    """
    Removed persistent main menu reply keyboard per prompt UX specification.
    Returns ReplyKeyboardRemove to clean up any leftover reply keyboards on client devices.
    """
    return ReplyKeyboardRemove()

def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build quick action inline keyboard.
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
