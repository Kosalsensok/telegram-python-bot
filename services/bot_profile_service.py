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
    - Bot name (optional, strictly rate-limited by Telegram)
    - Bot short description (shown on bot profile card)
    - Bot full description
    Only updates when user count actually changes.
    """
    global _last_updated_count, _name_update_cooldown_until

    try:
        total_count = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_count = stats.get("total_users", 0)

        # Skip update if count hasn't changed
        if _last_updated_count is not None and _last_updated_count == total_count:
            return

        formatted_count = format_user_count(total_count)

        # 1. Update Bot Name (Keep clean display name to prevent Telegram setMyName API rate-limit blocks)
        if time.time() >= _name_update_cooldown_until:
            bot_name = BOT_DISPLAY_NAME
            try:
                await bot.set_my_name(name=bot_name)
            except Exception as e:
                error_msg = str(e)
                match = re.search(r'retry after (\d+)', error_msg, re.IGNORECASE)
                if match:
                    retry_seconds = int(match.group(1))
                    _name_update_cooldown_until = time.time() + retry_seconds
                    logging.info(f"Bot Name update rate-limited by Telegram. Cooldown for {retry_seconds}s.")
                else:
                    logging.warning(f"Failed to update Bot Name: {error_msg}")


        # 2. Update Short Description (shown on profile card)
        short_desc = f"🤖 ជំនួយការ AI ឆ្លាតវៃ (Khmer & English) • 👥 {formatted_count} users"
        if len(short_desc) > 120:
            short_desc = short_desc[:120]

        try:
            await bot.set_my_short_description(short_description=short_desc)
        except Exception as e:
            logging.warning(f"Failed to update Bot Short Description: {e}")

        # 3. Update Full Description (What can this bot do?)
        full_desc = (
            f"🤖 {BOT_DISPLAY_NAME}\n\n"
            "ជំនួយការ AI ឆ្លាតវៃ ជួយវិភាគអត្ថបទ រូបភាព សំឡេង គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។\n\n"
            "✨ មុខងារចម្បង៖\n"
            "• 💬 សួរ AI & សរសេរកូដ\n"
            "• 🖼️ វិភាគរូបភាព (Vision OCR)\n"
            "• 🎙️ សំឡេងទៅជាអក្សរ (Speech-to-Text)\n"
            "• 🗺️ បង្ហាញផ្លូវ & ទីតាំង\n"
            "• 🌐 Telegram Mini App\n\n"
            f"📊 អ្នកប្រើប្រាស់សរុប៖ {formatted_count} នាក់"
        )
        if len(full_desc) > 512:
            full_desc = full_desc[:512]

        try:
            await bot.set_my_description(description=full_desc)
        except Exception as e:
            logging.warning(f"Failed to update Bot Full Description: {e}")

        _last_updated_count = total_count
        logging.info(f"🔄 Bot Profile updated successfully for {total_count} users ({formatted_count}).")

    except Exception as e:
        logging.error(f"Error in update_bot_profile: {e}")


async def bot_profile_worker(bot: Bot, db_service: DatabaseService = None) -> None:
    """
    Background worker loop that periodically updates bot profile.
    """
    logging.info("Starting Bot Profile Auto-Update background worker...")
    while True:
        try:
            await update_bot_profile(bot, db_service)
        except asyncio.CancelledError:
            logging.info("Bot Profile background worker cancelled.")
            break
        except Exception as e:
            logging.error(f"Unexpected error in bot profile worker: {e}")
        
        await asyncio.sleep(PROFILE_UPDATE_INTERVAL_MINUTES * 60)
