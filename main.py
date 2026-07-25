import asyncio
import logging
import os
import sys
import time
import aiohttp

logger = logging.getLogger(__name__)
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
        "subtitle": "Interactive Mini App & Khmer Writing Assistant",
        "response_type": "writing_assistant",
        "sections": []
    }
    return web.json_response(demo_data, status=200)



async def handle_spell_check_api(request):
    """API endpoint for Khmer Spelling & Writing Assistant."""
    try:
        data = await request.json()
    except Exception:
        return web.json_response({
            "success": False,
            "code": "INVALID_JSON",
            "message": "Invalid JSON request payload."
        }, status=400)
    
    text = data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return web.json_response({
            "success": False,
            "code": "EMPTY_TEXT",
            "message": "សូមបញ្ចូលអត្ថបទជាមុនសិន។"
        }, status=400)

    if len(text) > 5000:
        return web.json_response({
            "success": False,
            "code": "TEXT_TOO_LONG",
            "message": "អត្ថបទមានប្រវែងលើស 5,000 តួអក្សរ។"
        }, status=400)

    language = data.get("language", "km")
    mode = data.get("mode", "standard")
    custom_dictionary = data.get("customDictionary", [])

    from utils.khmer_spell_checker import check_khmer_spelling_ai
    result = await check_khmer_spelling_ai(text, language=language, mode=mode, custom_dictionary=custom_dictionary)
    return web.json_response(result, status=200)


async def handle_donate_checkout(request):
    """Generates ABA PayWay KHQR purchase via server API and renders full interactive checkout UI."""
    try:
        from config import ABA_MERCHANT_ID, ABA_API_KEY, ABA_PAYWAY_URL, SERVER_URL
        from services.aba_payway import request_aba_payway_purchase

        chat_id_raw = request.query.get("chat_id", "0")
        try:
            chat_id = int(chat_id_raw)
        except ValueError:
            chat_id = 0

        raw_amount = request.query.get("amount", "2000")
        try:
            if float(raw_amount) < 100:
                amount = "2000"
            else:
                amount = raw_amount
        except (ValueError, TypeError):
            amount = "2000"

        # Execute direct ABA PayWay Purchase API call on server side
        res = await request_aba_payway_purchase(
            chat_id=chat_id,
            merchant_id=ABA_MERCHANT_ID,
            public_key=ABA_API_KEY,
            payway_url=ABA_PAYWAY_URL,
            server_url=SERVER_URL,
            amount=amount
        )

        tran_id = res.get("tran_id", "D100000")
        qr_image = res.get("qr_image", "")
        deeplink = res.get("abapay_deeplink", "")

        if qr_image and not qr_image.startswith("data:image"):
            qr_image = f"data:image/png;base64,{qr_image}"

        html_content = f"""<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ABA Pay KHQR Checkout - Smart AI Assistant</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 25px 15px; background-color: #0f172a; color: #f8fafc; margin: 0; }}
        .card {{ background: #1e293b; max-width: 440px; margin: 20px auto; padding: 30px 20px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid #334155; }}
        h3 {{ color: #38bdf8; margin-top: 0; margin-bottom: 10px; font-size: 22px; font-weight: 700; }}
        p {{ color: #94a3b8; font-size: 14px; line-height: 1.6; margin: 10px 0; }}
        .qr-container {{ background: #ffffff; padding: 18px; border-radius: 16px; display: inline-block; margin: 20px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.4); }}
        .qr-img {{ width: 240px; height: 240px; display: block; border-radius: 8px; margin: 0 auto; }}
        .btn-deeplink {{ display: block; width: 100%; box-sizing: border-box; margin-top: 18px; padding: 15px 20px; background: linear-gradient(135deg, #0284c7, #0369a1); color: #ffffff; border: none; border-radius: 12px; font-weight: 700; font-size: 16px; cursor: pointer; text-decoration: none; transition: all 0.2s ease-in-out; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4); }}
        .btn-deeplink:hover {{ background: linear-gradient(135deg, #0369a1, #075985); transform: translateY(-1px); }}
        .badge {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; display: inline-block; margin-bottom: 15px; }}
        .tran-info {{ font-family: monospace; font-size: 13px; color: #64748b; margin-top: 15px; }}
        .status-dot {{ display: inline-block; width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; margin-right: 6px; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="card">
        <h3>🏦 ABA PAY / KHQR CHECKOUT</h3>
        <div class="badge">បរិច្ចាគ 2,000 ៛ ($0.50 USD)</div>
        <p><span class="status-dot"></span> KHQR Code ត្រូវបានបង្កើតរួចរាល់ហើយ!</p>
        
        <div class="qr-container">
            {"<img class='qr-img' src='" + qr_image + "' alt='ABA KHQR Code' />" if qr_image else "<p style='color:#ef4444'>⚠️ QR Code Generation Failed</p>"}
        </div>
        
        <p style="color: #cbd5e1; font-weight: 500;">សូមស្កែន QR Code ខាងលើ ឬ ចុចប៊ូតុងខាងក្រោមដើម្បីទូទាត់</p>
        
        {"<a href='" + deeplink + "' class='btn-deeplink' target='_blank'>📲 បើក App ABA Bank ដើម្បីទូទាត់</a>" if deeplink else ""}
        
        <div class="tran-info">Transaction ID: {tran_id}</div>
    </div>

    <script>
        // Real-time payment verification status polling
        const tranId = "{tran_id}";
        let checkInterval = setInterval(async function() {{
            try {{
                const res = await fetch("/aba_payment_status?tran_id=" + tranId);
                const data = await res.json();
                if (data.completed) {{
                    clearInterval(checkInterval);
                    window.location.href = "/payment_success?tran_id=" + tranId;
                }}
            }} catch(e) {{
                console.error("Polling status error:", e);
            }}
        }}, 3000);
    </script>
</body>
</html>"""
        return web.Response(text=html_content, content_type="text/html")
    except Exception as e:
        import traceback
        logger.error(f"Error rendering checkout form: {e}\n{traceback.format_exc()}")
        return web.Response(text=f"<h3>Error rendering checkout: {e}</h3>", content_type="text/html", status=500)


async def handle_aba_payment_status(request):
    """API endpoint to query payment status for web checkout auto-redirect."""
    from services.aba_payway import pending_donations, completed_donations
    tran_id = request.query.get("tran_id", "")
    if tran_id in completed_donations:
        return web.json_response({"completed": True, "tran_id": tran_id})
    return web.json_response({"completed": False, "tran_id": tran_id})



async def notify_donation_completed(bot, chat_id: str, tran_id: str, amount: str = "0.50"):
    """Sends thank-you message to Telegram user upon successful donation."""
    from services.aba_payway import completed_donations
    if tran_id in completed_donations:
        return
    completed_donations.add(tran_id)

    thank_you_message = (
        "🎉 <b>សូមថ្លែងអំណរគុណយ៉ាងជ្រាលជ្រៅ!</b> 🙏❤️\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"ការបរិច្ចាគចំនួន <b>${amount}</b> របស់លោកអ្នកបានជោគជ័យហើយ! (ID: <code>{tran_id}</code>)\n"
        "ថវិកានេះនឹងត្រូវយកទៅប្រើប្រាស់សម្រាប់អភិវឌ្ឍន៍ប្រព័ន្ធ <b>Smart AI Assistant</b> "
        "ឱ្យកាន់តែឆ្លាតវៃ និងមានសមត្ថភាពខ្ពស់បន្ថែមទៀតសម្រាប់ឆ្នាំបន្ទាប់។\n\n"
        "✨ <i>សូមជូនពរឱ្យលោកអ្នកជួបប្រទះតែសេចក្ដីសុខ សុភមង្គល និងជោគជ័យគ្រប់ភារកិច្ច!</i> 🚀"
    )
    try:
        await bot.send_message(chat_id=int(chat_id), text=thank_you_message, parse_mode="HTML")
        logging.info(f"Sent Telegram donation thank-you to chat_id={chat_id} for tran_id={tran_id}")
    except Exception as e:
        logging.error(f"Failed to send Telegram donation thank-you to chat_id={chat_id}: {e}")


def make_payment_success_handler(bot):
    async def handle_payment_success(request):
        from services.aba_payway import pending_donations
        tran_id = request.query.get("tran_id", "")
        donation = pending_donations.get(tran_id, {})
        chat_id = donation.get("chat_id")
        amount = donation.get("amount", "0.50")

        if chat_id and bot:
            await notify_donation_completed(bot, chat_id=chat_id, tran_id=tran_id, amount=amount)
            if tran_id in pending_donations:
                del pending_donations[tran_id]

        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Donation Successful!</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px 20px; background: #eef9f1; color: #2e7d32; }
        .card { background: #ffffff; max-width: 500px; margin: 0 auto; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); }
        .icon { font-size: 60px; margin-bottom: 15px; }
        h2 { margin-bottom: 10px; color: #1b5e20; }
        p { color: #4e4e4e; line-height: 1.6; font-size: 16px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✅</div>
        <h2>ការបង់ប្រាក់បរិច្ចាគបានជោគជ័យ!</h2>
        <p>សូមអរគុណយ៉ាងជ្រាលជ្រៅសម្រាប់ការគាំទ្រអភិវឌ្ឍន៍ <strong>Smart AI Assistant</strong>។<br/>សារជូនពរត្រូវបានផ្ញើទៅកាន់ Telegram របស់លោកអ្នករួចរាល់ហើយ!</p>
        <p>លោកអ្នកអាចបិទទំព័រនេះ ហើយត្រឡប់ទៅ Telegram វិញបាន។</p>
    </div>
</body>
</html>"""
        return web.Response(text=html_content, content_type="text/html")
    return handle_payment_success


def make_aba_webhook_handler(bot):
    async def handle_aba_webhook(request):
        import base64
        from services.aba_payway import pending_donations
        try:
            if request.method == "POST":
                try:
                    payload = await request.post()
                except Exception:
                    payload = {}
                if not payload:
                    try:
                        payload = await request.json()
                    except Exception:
                        payload = {}
            else:
                payload = request.query

            logging.info(f"Received ABA Webhook callback: {dict(payload)}")
            status = str(payload.get("status", payload.get("status_code", "")))
            tran_id = str(payload.get("tran_id", payload.get("transaction_id", "")))
            
            return_params = str(payload.get("return_params", ""))
            chat_id = None
            if return_params:
                try:
                    decoded = base64.b64decode(return_params).decode('utf-8')
                    if "chat_id=" in decoded:
                        chat_id = decoded.split("chat_id=")[1].split("&")[0]
                except Exception:
                    pass

            if not chat_id and tran_id in pending_donations:
                chat_id = pending_donations[tran_id].get("chat_id")

            if status in ("0", "00", "SUCCESS", "APPROVED") and tran_id and chat_id and bot:
                await notify_donation_completed(bot, chat_id=chat_id, tran_id=tran_id)
                return web.json_response({"status": "SUCCESS", "message": "Donation recorded successfully"})

            return web.json_response({"status": "ACK", "message": "Notification received"})
        except Exception as e:
            logging.error(f"Error handling ABA Webhook: {e}")
            return web.json_response({"status": "ERROR", "message": str(e)}, status=400)
    return handle_aba_webhook


async def start_health_server(bot=None):
    """Starts a lightweight web server for Render Free Web Service deployment, ABA PayWay Webhook, and Telegram Mini App."""
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
    app.router.add_post("/api/spell-check", handle_spell_check_api)

    # ABA PayWay Donation routes
    app.router.add_get("/donate_checkout", handle_donate_checkout)
    app.router.add_get("/aba_payment_status", handle_aba_payment_status)
    if bot:
        app.router.add_get("/payment_success", make_payment_success_handler(bot))
        app.router.add_post("/aba_webhook", make_aba_webhook_handler(bot))
        app.router.add_get("/aba_webhook", make_aba_webhook_handler(bot))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Health check, ABA Webhook & Mini App HTTP server started on 0.0.0.0:{port}")
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

    # Start HTTP Health Server for Render Web Service & ABA Webhook Notification Receiver
    runner = None
    try:
        runner = await start_health_server(bot=bot)
    except Exception as e:
        logging.warning(f"Could not start HTTP health server: {e}")

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
        BotCommand(command="donate", description="💖 បរិច្ចាគ $0.50 គាំទ្រ AI (Donate $0.50)"),
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
