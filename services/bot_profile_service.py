import asyncio
import logging
import time
import re
from typing import Optional
from aiogram import Bot
from config import (
    BOT_DISPLAY_NAME,
    SHOW_USER_COUNT_IN_BOT_NAME,
    PROFILE_UPDATE_INTERVAL_MINUTES
)
from services.db_service import DatabaseService
from utils.user_count import format_user_count

_last_updated_count: Optional[int] = None
_name_update_cooldown_until: float = 0


async def update_bot_profile(bot: Bot, db_service: DatabaseService = None) -> None:
    """
    Get the current total user count from the database and update:
    - Bot name
    - Bot short description
    - Bot full description
    Only updates when user count actually changes.
    """
    global _last_updated_count, _name_update_cooldown_until

    # Skip all profile updates if we are currently rate-limited
    if time.time() < _name_update_cooldown_until:
        return

    try:
        total_count = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_count = stats.get("total_users", 0)

        # Skip update if count hasn't changed
        if _last_updated_count is not None and _last_updated_count == total_count:
            return

        formatted_count = format_user_count(total_count)
        has_error = False

        # 1. Update Bot Name
        if SHOW_USER_COUNT_IN_BOT_NAME:
            bot_name = f"{BOT_DISPLAY_NAME} • {formatted_count} Users"
            if len(bot_name) > 64:
                bot_name = bot_name[:64]
        else:
            bot_name = BOT_DISPLAY_NAME

        try:
            await bot.set_my_name(name=bot_name)
        except Exception as e:
            error_msg = str(e)
            match = re.search(r'retry after (\d+)', error_msg, re.IGNORECASE)
            if match:
                retry_seconds = int(match.group(1))
                _name_update_cooldown_until = time.time() + retry_seconds
                # Log silently to avoid console spam for the user
                logging.info(f"Bot Profile update rate-limited. Silencing further attempts for {retry_seconds} seconds.")
            else:
                logging.warning(f"Failed to update Bot Name: {error_msg}")
            has_error = True

        # 2. Update Short Description
        short_desc = f"🤖 Smart Khmer & English AI • 👥 {formatted_count} users"
        if len(short_desc) > 120:
            short_desc = short_desc[:120]

        try:
            await bot.set_my_short_description(short_description=short_desc)
        except Exception as e:
            error_msg = str(e)
            match = re.search(r'retry after (\d+)', error_msg, re.IGNORECASE)
            if match:
                retry_seconds = int(match.group(1))
                _name_update_cooldown_until = time.time() + retry_seconds
            else:
                logging.warning(f"Failed to update Bot Short Description: {error_msg}")
            has_error = True

        # 3. Update Full Description
        full_desc = (
            f"🤖 {BOT_DISPLAY_NAME}\n\n"
            "សួរជាភាសាខ្មែរ ឬ English。\n"
            "ផ្ញើរូបភាព ដើម្បីឱ្យ AI មើល វិភាគ និងពន្យល់。\n\n"
            "✨ AI Chat\n"
            "🖼 Image Analysis\n"
            "💻 Code Assistance\n"
            "📚 Learning Support\n"
            "🌐 Khmer & English\n\n"
            f"👥 Trusted by {formatted_count} users"
        )
        if len(full_desc) > 512:
            full_desc = full_desc[:512]

        try:
            await bot.set_my_description(description=full_desc)
        except Exception as e:
            error_msg = str(e)
            match = re.search(r'retry after (\d+)', error_msg, re.IGNORECASE)
            if match:
                retry_seconds = int(match.group(1))
                _name_update_cooldown_until = time.time() + retry_seconds
            else:
                logging.warning(f"Failed to update Bot Full Description: {error_msg}")
            has_error = True

        if not has_error:
            _last_updated_count = total_count
            logging.info(f"🔄 Bot Profile updated successfully for {total_count} users ({formatted_count}).")
        else:
            logging.info(f"⚠️ Bot Profile update for {total_count} users had errors (likely rate-limited). Will retry later.")

    except Exception as e:
        logging.error(f"Error in update_bot_profile: {e}")


async def bot_profile_worker(bot: Bot, db_service: DatabaseService = None) -> None:
    """
    Background worker loop that periodically updates bot profile.
    """
    logging.info("Starting Bot Profile Auto-Update background worker...")
    try:
        while True:
            await update_bot_profile(bot, db_service)
            # Sleep for configured interval
            await asyncio.sleep(PROFILE_UPDATE_INTERVAL_MINUTES * 60)
    except asyncio.CancelledError:
        logging.info("Bot Profile background worker cancelled.")
    except Exception as e:
        logging.error(f"Unexpected error in bot profile worker: {e}")
