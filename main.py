import asyncio
import logging
import sys
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import (
    BOT_TOKEN,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LOG_LEVEL,
    MAX_HISTORY_MESSAGES,
    BOT_DISPLAY_NAME,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    USE_DATABASE
)
from services import GeminiService, DatabaseService, bot_profile_worker
from utils import ConversationMemory, UserTrackerMiddleware
from handlers import (
    get_command_router,
    get_callbacks_router,
    get_text_router,
    get_image_router,
    get_document_router,
    get_fallback_router,
    get_admin_router
)

# Configure logging format: Timestamp - Level - Logger Name - Message
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("google_genai.models").setLevel(logging.WARNING)


async def main():
    """
    Main entry point for starting Smart AI Assistant Telegram Bot.
    """
    logging.info("Initializing Smart AI Assistant services...")

    # 1. Initialize MySQL Database Service
    db_service = DatabaseService(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    if USE_DATABASE:
        await db_service.init_db()

    # 2. Initialize Gemini AI Service and Conversation Memory
    gemini_service = GeminiService(api_key=GEMINI_API_KEY, primary_model=GEMINI_MODEL)
    memory = ConversationMemory(max_history=MAX_HISTORY_MESSAGES, db_service=db_service)

    # 3. Initialize Bot & Dispatcher with Default HTML Properties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher()

    # Register User Tracking Outer Middleware
    tracker_mw = UserTrackerMiddleware(db_service)
    dp.message.outer_middleware(tracker_mw)
    dp.callback_query.outer_middleware(tracker_mw)
    dp.chat_member.outer_middleware(tracker_mw)
    dp.my_chat_member.outer_middleware(tracker_mw)

    # 4. Start Bot Profile Auto-Update Background Worker Task
    profile_task: Optional[asyncio.Task] = asyncio.create_task(bot_profile_worker(bot, db_service))

    # 5. Create & Register Routers in proper priority order
    commands_router = get_command_router(memory, db_service, gemini_service)
    callbacks_router = get_callbacks_router(db_service, memory)
    admin_router = get_admin_router(db_service, gemini_service)
    image_router = get_image_router(gemini_service, memory, db_service)
    document_router = get_document_router(gemini_service, memory, db_service)
    text_router = get_text_router(gemini_service, memory, db_service)
    fallback_router = get_fallback_router(db_service)

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(admin_router)
    dp.include_router(image_router)
    dp.include_router(document_router)
    dp.include_router(text_router)
    dp.include_router(fallback_router)

    logging.info("Routers and Middleware registered successfully: [UserTrackerMiddleware, Commands, Callbacks, Admin, Image, Document, Text, Fallback]")



    # 6. Delete any pending webhook updates to ensure smooth Long Polling
    await bot.delete_webhook(drop_pending_updates=True)

    # 7. Set Bot Commands Menu
    commands = [
        BotCommand(command="start", description="🚀 ចាប់ផ្តើមប្រើប្រាស់ (Start)"),
        BotCommand(command="mode", description="🎯 ជ្រើសរើស AI Mode (Change Mode)"),
        BotCommand(command="new", description="🧹 បង្កើតការសន្ទនាថ្មី (New Chat)"),
        BotCommand(command="clear", description="🗑 លុបប្រវត្តិសន្ទនា (Clear History)"),
        BotCommand(command="help", description="ℹ️ ជំនួយ និងការណែនាំ (Help)"),
        BotCommand(command="quiz", description="📊 បង្កើតកម្រងសំណួរ (Generate Quiz)"),
        BotCommand(command="stats", description="📊 ស្ថិតិប្រើប្រាស់ផ្ទាល់ខ្លួន (Stats)"),
        BotCommand(command="language", description="🌐 ជ្រើសរើសភាសា (Language)"),
        BotCommand(command="about", description="👤 អំពី Bot នេះ (About)"),
        BotCommand(command="privacy", description="🔒 គោលការណ៍ឯកជនភាព (Privacy)"),
    ]
    try:
        await bot.set_my_commands(commands)
        logging.info("Bot commands menu set successfully.")
    except Exception as e:
        logging.error(f"Failed to set bot commands: {e}")

    logging.info(f"🚀 {BOT_DISPLAY_NAME} (Gemini AI + MySQL) កំពុងដំណើរការ...")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error during bot execution: {e}", exc_info=True)
    finally:
        logging.info("Shutting down bot session and background tasks...")
        if profile_task and not profile_task.done():
            profile_task.cancel()
            try:
                await profile_task
            except asyncio.CancelledError:
                pass
        await bot.session.close()
        if db_service:
            await db_service.close()
        logging.info("Bot session and background tasks closed successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot ត្រូវបានបញ្ឈប់ (Bot stopped by user)!")
