import time
import asyncio
import logging
from typing import Dict, Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


class UserThrottlingMiddleware(BaseMiddleware):
    """
    Per-user rate-limiting middleware for Telegram AI Bot.
    Prevents single-user request flooding (spamming) from consuming system resources
    or hitting Gemini API quota limits for other concurrent users.

    Allows up to rate_limit requests per user per time_window seconds.
    If limit is exceeded, responds with a polite warning and drops excess request.
    """
    def __init__(self, time_window: float = 1.0, max_requests: int = 2):
        super().__init__()
        self.time_window = time_window
        self.max_requests = max_requests
        # Dict[user_id, List[timestamp]]
        self._user_timestamps: Dict[int, list] = {}
        self._lock = asyncio.Lock()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None

        if user_id:
            now = time.time()
            async with self._lock:
                timestamps = self._user_timestamps.get(user_id, [])
                # Prune timestamps older than window
                timestamps = [ts for ts in timestamps if now - ts < self.time_window]
                
                if len(timestamps) >= self.max_requests:
                    logging.warning(f"UserThrottlingMiddleware: Throttled user {user_id} (exceeded {self.max_requests} reqs/{self.time_window}s)")
                    if isinstance(event, Message):
                        try:
                            await event.answer(
                                "⚡ <b>សូមមេត្តារង់ចាំបន្តិច</b>\n"
                                "━━━━━━━━━━━━━━━━━━\n\n"
                                "ប្រព័ន្ធកំពុងដំណើរការសារមុនរបស់អ្នក។ សូមផ្ញើសារម្តងទៀតបន្ទាប់ពី ១ វិនាទី!",
                                parse_mode="HTML"
                            )
                        except Exception:
                            pass
                    elif isinstance(event, CallbackQuery):
                        try:
                            await event.answer("⚡ សូមរង់ចាំបន្តិចមុននឹងចុចម្តងទៀត!", show_alert=True)
                        except Exception:
                            pass
                    return None

                timestamps.append(now)
                self._user_timestamps[user_id] = timestamps

                # Periodic cleanup of inactive users (if dict gets large)
                if len(self._user_timestamps) > 2000:
                    expired_users = [
                        uid for uid, tss in self._user_timestamps.items()
                        if not tss or (now - tss[-1] > self.time_window * 2)
                    ]
                    for uid in expired_users:
                        self._user_timestamps.pop(uid, None)

        return await handler(event, data)
