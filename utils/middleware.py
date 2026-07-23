import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, ChatMemberUpdated

from services.db_service import DatabaseService


class UserTrackerMiddleware(BaseMiddleware):
    """
    Aiogram Outer Middleware to automatically track and save user details 
    for all incoming Telegram messages, callback queries, and chat member updates.
    Also triggers real-time updates for Bot profile stats if user count changes.
    """
    def __init__(self, db_service: DatabaseService = None):
        super().__init__()
        self.db_service = db_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        from_user = None
        if isinstance(event, Message):
            from_user = event.from_user
        elif isinstance(event, CallbackQuery):
            from_user = event.from_user
        elif isinstance(event, ChatMemberUpdated):
            from_user = event.new_chat_member.user if (event.new_chat_member and hasattr(event.new_chat_member, 'user')) else event.from_user

        if from_user and not from_user.is_bot and self.db_service:
            try:
                await self.db_service.save_or_update_user(
                    telegram_id=from_user.id,
                    username=from_user.username,
                    first_name=from_user.first_name,
                    last_name=from_user.last_name,
                    language_code=from_user.language_code or "en"
                )

                # Trigger real-time profile check if bot instance is available in context
                bot = data.get("bot")
                if bot:
                    from services.bot_profile_service import update_bot_profile
                    asyncio.create_task(update_bot_profile(bot, self.db_service))
            except Exception as e:
                logging.error(f"UserTrackerMiddleware error for user {from_user.id}: {e}")

        return await handler(event, data)

