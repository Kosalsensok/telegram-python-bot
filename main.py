import asyncio
import logging
import os
import sys
import time
import aiohttp
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiohttp import web

from config import (
    BOT_TOKEN,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LOG_LEVEL,
    MAX_HISTORY_MESSAGES,
    BOT_DISPLAY_NAME,
    RENDER_EXTERNAL_URL,
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
    get_voice_router,
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

_start_time = time.time()


async def handle_health_check(request):
    """HTTP 200 OK handler for Render Web Service health checks and keep-alive pings."""
    uptime_seconds = int(time.time() - _start_time)
    return web.json_response({
        "status": "online",
        "bot": BOT_DISPLAY_NAME,
        "uptime_seconds": uptime_seconds,
        "message": "Smart AI Assistant Telegram Bot is active and running 24/7!",
        "timestamp": time.time()
    }, status=200)


async def handle_mini_app(request):
    """Serves Telegram Mini App interactive interface."""
    html_path = os.path.join(os.path.dirname(__file__), "src", "web", "answer.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type="text/html")
    return web.Response(text="Mini App HTML not found", status=404)


async def handle_solution_api(request):
    """API endpoint returning structured solution data for Telegram Mini App."""
    solution_id = request.match_info.get("solution_id", "")
    from utils.solution_card import get_solution_cache
    sol = get_solution_cache(solution_id)
    if sol and sol.get("data"):
        return web.json_response(sol["data"], status=200)

    # Fallback/Demo payload if solution_id is 'demo' or expired
    demo_data = {
        "title": "Smart AI Assistant Mini App",
        "subtitle": "Interactive Software Requirements & Prototype Stepper",
        "response_type": "software_requirements",
        "sections": [
            {
                "step_number": 1,
                "heading_km": "1️⃣ ទិដ្ឋភាពទូទៅ (System Overview)",
                "content_km": "ប្រព័ន្ធគ្រប់គ្រង Mart និងលក់ទំនិញ (Smart Mart Management System) សម្រាប់គ្រប់គ្រងការលក់ POS, ស្តុកផលិតផល, បុគ្គលិក, អតិថិជន, និងរបាយការណ៍ហិរញ្ញវត្ថុ។"
            },
            {
                "step_number": 2,
                "heading_km": "2️⃣ Functional Modules",
                "content_km": "• POS Sales & Barcode Checkout\n• Inventory & Stock Low Alerts\n• Supplier Purchase Orders\n• Multi-Payment (KHQR + Cash)\n• User Roles & Permissions"
            },
            {
                "step_number": 3,
                "heading_km": "3️⃣ User Roles & Permissions",
                "content_km": "• Admin: Full System Audit Logs\n• Manager: Reports & Stock Adjustments\n• Cashier: POS Register & Receipt Printing"
            },
            {
                "step_number": 4,
                "heading_km": "4️⃣ User Flows & Processes",
                "content_km": "1. Cashier logs in to register.\n2. Barcode scanner reads product ID.\n3. System calculates tax, discount & subtotal.\n4. Sale is committed and stock updates atomically."
            },
            {
                "step_number": 5,
                "heading_km": "5️⃣ Prototype Code Preview",
                "content_km": "pos_service.py — Atomic Stock Checkout Service:",
                "code": "# pos_service.py\ndef checkout(cashier, items, payment_method):\n    subtotal = sum(i.total_price for i in items)\n    receipt = generate_receipt()\n    update_stock_atomically(items)\n    return receipt"
            },
            {
                "step_number": 6,
                "heading_km": "6️⃣ Deployment & Docker Setup",
                "content_km": "• Python 3.11 Containerized Microservice\n• PostgreSQL Multi-tenant DB\n• 24/7 Keep-Alive Worker on Render"
            }
        ]
    }
    return web.json_response(demo_data, status=200)



async def start_health_server():
    """Starts a lightweight web server for Render Free Web Service deployment and Telegram Mini App."""
    port_str = os.getenv("PORT", "8080").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 8080

    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    app.router.add_get("/ping", handle_health_check)
    app.router.add_head("/", handle_health_check)
    app.router.add_head("/health", handle_health_check)
    app.router.add_head("/ping", handle_health_check)
    
    # Mini App routes
    app.router.add_get("/answer/{solution_id}", handle_mini_app)
    app.router.add_get("/api/solution/{solution_id}", handle_solution_api)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Health check & Mini App HTTP server started on 0.0.0.0:{port}")
    return runner


async def keep_alive_worker():
    """
    Background worker that self-pings the HTTP server every 3 minutes (180s)
    to prevent Render Free Tier Web Services from spinning down due to inactivity.
    """
    logging.info("Starting Self-Keep-Alive background worker for 24/7 uptime...")
    port_str = os.getenv("PORT", "8080").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 8080

    urls_to_ping = [
        f"http://127.0.0.1:{port}/health",
    ]

    if RENDER_EXTERNAL_URL:
        clean_url = RENDER_EXTERNAL_URL.rstrip('/')
        if not clean_url.endswith('/health'):
            clean_url = f"{clean_url}/health"
        urls_to_ping.append(clean_url)

    # Allow health web server to start before pinging
    await asyncio.sleep(10)

    try:
        async with aiohttp.ClientSession() as session:
            while True:
                for target_url in urls_to_ping:
                    try:
                        async with session.get(target_url, timeout=15) as resp:
                            if resp.status == 200:
                                logging.debug(f"Keep-Alive self-ping to {target_url} successful (200 OK).")
                            else:
                                logging.warning(f"Keep-Alive ping to {target_url} returned status {resp.status}")
                    except Exception as ping_err:
                        logging.warning(f"Keep-Alive ping to {target_url} error: {ping_err}")
                await asyncio.sleep(180)  # Self-ping every 3 minutes
    except asyncio.CancelledError:
        logging.info("Self-Keep-Alive background worker cancelled.")
    except Exception as e:
        logging.error(f"Unexpected error in Keep-Alive worker: {e}")


async def main():
    """
    Main entry point for starting Smart AI Assistant Telegram Bot.
    """
    logging.info("Initializing Smart AI Assistant services...")

    # Start HTTP Health Server for Render Web Service (Free Tier)
    runner = None
    try:
        runner = await start_health_server()
    except Exception as e:
        logging.warning(f"Could not start HTTP health server: {e}")

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

    # 4. Start Background Worker Tasks (Profile Updater + Keep Alive Pinger)
    profile_task: Optional[asyncio.Task] = asyncio.create_task(bot_profile_worker(bot, db_service))
    keep_alive_task: Optional[asyncio.Task] = asyncio.create_task(keep_alive_worker())

    # 5. Create & Register Routers in proper priority order
    commands_router = get_command_router(memory, db_service, gemini_service)
    callbacks_router = get_callbacks_router(db_service, memory)
    admin_router = get_admin_router(db_service, gemini_service)
    image_router = get_image_router(gemini_service, memory, db_service)
    document_router = get_document_router(gemini_service, memory, db_service)
    voice_router = get_voice_router(gemini_service, memory, db_service)
    text_router = get_text_router(gemini_service, memory, db_service)
    fallback_router = get_fallback_router(db_service)

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(admin_router)
    dp.include_router(image_router)
    dp.include_router(document_router)
    dp.include_router(voice_router)
    dp.include_router(text_router)
    dp.include_router(fallback_router)

    logging.info("Routers and Middleware registered successfully: [UserTrackerMiddleware, Commands, Callbacks, Admin, Image, Document, Voice, Text, Fallback]")

    # 6. Delete any pending webhook updates to ensure smooth Long Polling
    await bot.delete_webhook(drop_pending_updates=True)

    # 7. Set Bot Commands Menu
    commands = [
        BotCommand(command="start", description="🚀 ចាប់ផ្តើមប្រើប្រាស់ (Start)"),
        BotCommand(command="miniapp", description="🌐 បើក Telegram Mini App (Open Mini App)"),
        BotCommand(command="image", description="🎨 បង្កើតរូបភាព AI កម្រិត HD (Generate AI Image)"),
        BotCommand(command="imagine", description="🎨 បង្កើតរូបភាព AI (Imagine Image)"),
        BotCommand(command="mode", description="🎯 ជ្រើសរើស AI Mode (Change Mode)"),
        BotCommand(command="run", description="⚡ ដំណើរការកូដ (Execute Code)"),
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

    logging.info(f"🚀 {BOT_DISPLAY_NAME} (Gemini AI + MySQL) កំពុងដំណើរការ 24/7...")

    # 8. Run Bot Polling with Auto-Reconnect resilience
    retry_count = 0
    while True:
        if sys.is_finalizing():
            break
        try:
            await dp.start_polling(bot, handle_signals=False)
            break
        except asyncio.CancelledError:
            logging.info("Bot polling loop cancelled.")
            break
        except Exception as e:
            retry_count += 1
            logging.error(f"Error during bot execution (Attempt #{retry_count}): {e}. Retrying in 5 seconds...", exc_info=True)
            await asyncio.sleep(5)

    # Clean shutdown of tasks and connections
    logging.info("Shutting down bot session and background tasks...")
    if profile_task and not profile_task.done():
        profile_task.cancel()
        try:
            await profile_task
        except asyncio.CancelledError:
            pass

    if keep_alive_task and not keep_alive_task.done():
        keep_alive_task.cancel()
        try:
            await keep_alive_task
        except asyncio.CancelledError:
            pass

    if runner:
        await runner.cleanup()
    await bot.session.close()
    if db_service:
        await db_service.close()
    logging.info("Bot session and background tasks closed successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot ត្រូវបានបញ្ឈប់ (Bot stopped by user)!")
