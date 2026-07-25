import asyncio
import logging
import os
import sys
import time
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, ErrorEvent
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
    """Generates ABA PayWay KHQR purchase & direct ABA Gateway HTML Form for Sandbox Testing."""
    try:
        from config import ABA_MERCHANT_ID, ABA_API_KEY, ABA_PAYWAY_URL, SERVER_URL
        from services.aba_payway import request_aba_payway_purchase, create_donation_checkout_params

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

        # Generate standard ABA PayWay Checkout form parameters
        tran_id, req_time, form_data = create_donation_checkout_params(
            chat_id=chat_id,
            merchant_id=ABA_MERCHANT_ID,
            public_key=ABA_API_KEY,
            payway_url=ABA_PAYWAY_URL,
            server_url=SERVER_URL,
            amount=amount,
            payment_option=""
        )

        # Execute direct ABA PayWay Purchase API call on server side for KHQR & Deeplink
        res = await request_aba_payway_purchase(
            chat_id=chat_id,
            merchant_id=ABA_MERCHANT_ID,
            public_key=ABA_API_KEY,
            payway_url=ABA_PAYWAY_URL,
            server_url=SERVER_URL,
            amount=amount
        )

        qr_image = res.get("qr_image", "")
        deeplink = res.get("abapay_deeplink", "")

        if qr_image and not qr_image.startswith("data:image"):
            qr_image = f"data:image/png;base64,{qr_image}"

        html_content = f"""<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ABA PayWay Sandbox Checkout - Smart AI Assistant</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 20px 15px; background-color: #0f172a; color: #f8fafc; margin: 0; }}
        .card {{ background: #1e293b; max-width: 480px; margin: 15px auto; padding: 25px 20px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid #334155; text-align: left; }}
        h3 {{ color: #38bdf8; margin-top: 0; margin-bottom: 10px; font-size: 22px; font-weight: 700; text-align: center; }}
        p {{ color: #94a3b8; font-size: 14px; line-height: 1.5; margin: 8px 0; }}
        .tab-btn-group {{ display: flex; gap: 8px; margin: 15px 0; border-bottom: 2px solid #334155; padding-bottom: 10px; }}
        .tab-btn {{ flex: 1; padding: 10px; background: #334155; color: #cbd5e1; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; text-align: center; font-size: 14px; transition: all 0.2s; }}
        .tab-btn.active {{ background: #0284c7; color: #fff; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4); }}
        .tab-content {{ display: none; margin-top: 15px; }}
        .tab-content.active {{ display: block; }}
        .qr-container {{ background: #ffffff; padding: 16px; border-radius: 16px; display: inline-block; margin: 10px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.4); text-align: center; width: 100%; box-sizing: border-box; }}
        .qr-img {{ width: 220px; height: 220px; display: block; border-radius: 8px; margin: 0 auto; }}
        .form-group {{ margin-bottom: 14px; }}
        label {{ display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 5px; font-weight: 600; }}
        input {{ width: 100%; box-sizing: border-box; padding: 12px 14px; background: #0f172a; border: 1px solid #475569; border-radius: 10px; color: #fff; font-size: 15px; font-family: monospace; outline: none; }}
        input:focus {{ border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }}
        .form-row {{ display: flex; gap: 10px; }}
        .btn-deeplink {{ display: block; width: 100%; box-sizing: border-box; margin-top: 12px; padding: 14px 20px; background: linear-gradient(135deg, #0284c7, #0369a1); color: #ffffff; border: none; border-radius: 12px; font-weight: 700; font-size: 15px; cursor: pointer; text-decoration: none; text-align: center; transition: all 0.2s; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4); }}
        .btn-pay-card {{ display: block; width: 100%; box-sizing: border-box; margin-top: 15px; padding: 14px 20px; background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; border: none; border-radius: 12px; font-weight: 700; font-size: 16px; cursor: pointer; text-align: center; text-decoration: none; transition: all 0.2s; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }}
        .btn-pay-card:hover {{ background: linear-gradient(135deg, #059669, #047857); transform: translateY(-1px); }}
        .badge {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin-bottom: 12px; text-align: center; width: 100%; box-sizing: border-box; }}
        .tran-info {{ font-family: monospace; font-size: 12px; color: #64748b; margin-top: 15px; text-align: center; }}
        .status-dot {{ display: inline-block; width: 9px; height: 9px; background-color: #22c55e; border-radius: 50%; margin-right: 6px; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="card">
        <h3>🏦 ABA PAYWAY CHECKOUT</h3>
        <div class="badge">បរិច្ចាគ 2,000 ៛ ($0.50 USD) • ABA Sandbox Test</div>
        <p style="text-align: center;"><span class="status-dot"></span> ជ្រើសរើសវិធីសាស្ត្រទូទាត់ខាងក្រោម៖</p>
        
        <div class="tab-btn-group">
            <button class="tab-btn active" onclick="switchTab('qr-tab')">📱 ABA KHQR Code</button>
            <button class="tab-btn" onclick="switchTab('card-tab')">💳 Test Credit Cards</button>
        </div>

        <!-- Tab 1: ABA KHQR Code -->
        <div id="qr-tab" class="tab-content active">
            <div class="qr-container">
                {"<img class='qr-img' src='" + qr_image + "' alt='ABA KHQR Code' />" if qr_image else "<p style='color:#ef4444'>⚠️ QR Code Generation Failed</p>"}
            </div>
            <p style="color: #cbd5e1; font-weight: 500; text-align: center;">សូមស្កែន QR Code ឬ ចុចប៊ូតុងខាងក្រោមដើម្បីទូទាត់</p>
            {"<a href='" + deeplink + "' class='btn-deeplink' target='_blank'>📲 បើក App ABA Bank ដើម្បីទូទាត់</a>" if deeplink else ""}
        </div>

        <!-- Tab 2: Test Credit Card Numbers -->
        <div id="card-tab" class="tab-content">
            <p style="color: #38bdf8; font-weight: 600; font-size: 13px; margin-bottom: 10px;">💳 លេខកាតសាកល្បង ABA Sandbox Official Test Cards:</p>
            <div style="background: rgba(56, 189, 248, 0.1); border: 1px dashed rgba(56, 189, 248, 0.3); padding: 10px 12px; border-radius: 10px; margin-bottom: 14px; font-size: 12px; font-family: monospace; color: #7dd3fc;">
                • Visa Test: 4286 0900 0000 0206 (04/30 - 777)<br/>
                • Mastercard: 5156 8399 3770 6777 (01/30 - 993)
            </div>
            
            <form action="/test_complete_payment" method="GET">
                <input type="hidden" name="tran_id" value="{tran_id}" />
                <input type="hidden" name="chat_id" value="{chat_id}" />
                <input type="hidden" name="amount" value="{amount}" />

                <div class="form-group">
                    <label>លេខកាត Credit Card Number (Visa / Mastercard):</label>
                    <input type="text" name="card_number" value="4286 0900 0000 0206" required />
                </div>
                
                <div class="form-row">
                    <div class="form-group" style="flex: 1;">
                        <label>ថ្ងៃផុតកំណត់ Expiry:</label>
                        <input type="text" name="expiry" value="04/30" placeholder="MM/YY" required />
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>CVV / CVC:</label>
                        <input type="text" name="cvv" value="777" placeholder="777" required />
                    </div>
                </div>

                <div class="form-group">
                    <label>ឈ្មោះលើកាត Cardholder Name:</label>
                    <input type="text" name="card_name" value="KOSAL SENSOK" required />
                </div>

                <button type="submit" class="btn-pay-card">💳 បង់ប្រាក់សាកល្បង $0.50 (Pay with Test Card)</button>
            </form>
        </div>
        
        <div class="tran-info">Transaction ID: {tran_id}</div>
    </div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            if (tabId === 'qr-tab') {{
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('qr-tab').classList.add('active');
            }} else {{
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('card-tab').classList.add('active');
            }}
        }}

        // Real-time payment verification status polling
        const tranId = "{tran_id}";
        let checkInterval = setInterval(async function() {{
            try {{
                const res = await fetch("/aba_payment_status?tran_id=" + tranId);
                const data = await res.json();
                if (data.completed) {{
                    clearInterval(checkInterval);
                    window.location.href = "/payment_success?tran_id=" + tranId + "&chat_id={chat_id}";
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



GLOBAL_BOT = None


async def notify_donation_completed(bot, chat_id: str, tran_id: str, amount: str = "0.50", force: bool = False):
    """Sends thank-you message to Telegram user upon successful donation."""
    global GLOBAL_BOT
    from services.aba_payway import completed_donations

    target_bot = bot or GLOBAL_BOT
    if not target_bot:
        logging.error(f"Cannot send donation notification: Bot instance is None for tran_id={tran_id}")
        return False
    
    if not chat_id or str(chat_id) in ("0", "None", ""):
        logging.warning(f"Cannot send donation notification: Invalid chat_id '{chat_id}' for tran_id={tran_id}")
        return False

    if not force and tran_id in completed_donations:
        logging.info(f"Donation notification already processed for tran_id={tran_id}")
        return True

    from html import escape
    from services.aba_payway import pending_donations, completed_donations

    user_info = pending_donations.get(tran_id, {})
    first_name_val = escape(user_info.get("first_name", "KOSAL SENSOK"))
    username_val = user_info.get("username", "kosalsensokpk")
    username_str = f"(@{username_val})" if username_val else ""

    thank_you_message = (
        f"🎉 <b>សូមថ្លែងអំណរគុណ {first_name_val}!</b> 🙏❤️\n\n"
        f"ការបរិច្ចាគចំនួន <b>$0.50</b> របស់លោកអ្នកបានជោគជ័យហើយ! (ID: <code>{tran_id}</code>)\n"
        "ថវិកានេះ នឹងត្រូវយកទៅប្រើប្រាស់សម្រាប់អភិវឌ្ឍន៍ប្រព័ន្ធ <b>Smart AI Assistant</b> សម្រាប់ឆ្នាំបន្ទាប់។\n\n"
        "✨ <i>សូមជូនពរឱ្យលោកអ្នកជួបប្រទះតែសេចក្ដីសុខ សុភមង្គល និងជោគជ័យគ្រប់ភារកិច្ច!</i> 🚀"
    )

    admin_notification = (
        "🔔 <b>ALERT: មានការបរិច្ចាគថ្មីទទួលបាន!</b> 💰\n\n"
        f"👤 <b>អ្នកបរិច្ចាគ:</b> {first_name_val} {username_str}\n"
        f"🆔 <b>Telegram User ID របស់គេ:</b> <code>{chat_id}</code>\n"
        f"💵 <b>ចំនួនទឹកប្រាក់:</b> $0.50\n"
        f"🧾 <b>Tran ID:</b> <code>{tran_id}</code>\n"
        f"⏰ <b>ម៉ោង:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "✅ ប្រព័ន្ធបានផ្ញើសារជូនពរទៅកាន់ ID របស់គាត់រួចរាល់ហើយ!"
    )

    try:
        # 1. Send thank-you message to donor
        await target_bot.send_message(chat_id=int(chat_id), text=thank_you_message, parse_mode="HTML")
        completed_donations.add(tran_id)
        logging.info(f"✅ Successfully sent Telegram donation thank-you to chat_id={chat_id} for tran_id={tran_id}")

        # 2. Also send notification alert to Admin / Owner (ID: 5496354981 and ADMIN_USER_IDS)
        from config import ADMIN_USER_IDS
        admin_set = set(ADMIN_USER_IDS)
        admin_set.add(5496354981)

        for admin_id in admin_set:
            try:
                await target_bot.send_message(chat_id=int(admin_id), text=admin_notification, parse_mode="HTML")
                logging.info(f"📢 Sent donation alert to Admin ID {admin_id}")
            except Exception as admin_err:
                logging.warning(f"Could not send admin alert to {admin_id}: {admin_err}")

        return True
    except Exception as e:
        logging.error(f"❌ Failed to send Telegram donation thank-you to chat_id={chat_id}: {e}")
        return False


async def handle_open_abapay(request):
    """HTTP endpoint to safely launch ABA Mobile App deep link from Telegram inline button."""
    from services.aba_payway import pending_donations
    tran_id = request.query.get("tran_id", "")
    donation = pending_donations.get(tran_id, {})
    deeplink = donation.get("abapay_deeplink", "")

    if not deeplink:
        deeplink = "abamobilebank://ababank.com"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Launching ABA Mobile App...</title>
    <script>
        window.location.href = "{deeplink}";
    </script>
</head>
<body style="font-family: sans-serif; text-align: center; padding: 40px 20px; background-color: #0f172a; color: #fff;">
    <h3>📲 កំពុងបើក App ABA Bank...</h3>
    <p>ប្រសិនបើ App មិនទាន់បើកដោយស្វ័យប្រវត្តិទេ សូមចុចប៊ូតុងខាងក្រោម៖</p>
    <a href="{deeplink}" style="display: inline-block; padding: 14px 28px; background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; text-decoration: none; border-radius: 10px; font-weight: bold; margin-top: 15px;">👉 ចុចទីនេះដើម្បីបើក ABA Mobile App</a>
</body>
</html>"""
    return web.Response(text=html_content, content_type="text/html")


async def handle_test_complete_payment(request):
    """Sandbox Test Payment Completion endpoint for developer testing."""
    from services.aba_payway import pending_donations
    tran_id = request.query.get("tran_id", "")
    chat_id = request.query.get("chat_id", "")
    donation = pending_donations.get(tran_id, {})
    if not chat_id:
        chat_id = str(donation.get("chat_id", ""))
    amount = donation.get("amount", "0.50")

    # Redirect to /payment_success which triggers Telegram thank-you message
    redirect_url = f"/payment_success?tran_id={tran_id}&chat_id={chat_id}&amount={amount}"
    return web.HTTPFound(redirect_url)


def make_payment_success_handler(bot=None):
    async def handle_payment_success(request):
        global GLOBAL_BOT
        import base64
        from services.aba_payway import pending_donations
        
        target_bot = bot or GLOBAL_BOT
        tran_id = request.query.get("tran_id", "")
        chat_id = request.query.get("chat_id", "")
        amount = request.query.get("amount", "0.50")
        
        donation = pending_donations.get(tran_id, {})
        if not chat_id:
            chat_id = str(donation.get("chat_id", ""))
            
        if not amount or amount in ("2000", "0"):
            amount = donation.get("amount", "0.50")
            if amount == "2000":
                amount = "0.50"

        return_params = request.query.get("return_params", "")
        if not chat_id and return_params:
            try:
                decoded = base64.b64decode(return_params).decode('utf-8')
                if "chat_id=" in decoded:
                    chat_id = decoded.split("chat_id=")[1].split("&")[0]
            except Exception:
                pass

        if chat_id and target_bot:
            await notify_donation_completed(target_bot, chat_id=chat_id, tran_id=tran_id, amount=amount, force=True)
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


def make_aba_webhook_handler(bot=None):
    async def handle_aba_webhook(request):
        global GLOBAL_BOT
        import base64
        from services.aba_payway import pending_donations

        target_bot = bot or GLOBAL_BOT
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

            if status in ("0", "00", "SUCCESS", "APPROVED") and tran_id and chat_id and target_bot:
                await notify_donation_completed(target_bot, chat_id=chat_id, tran_id=tran_id, force=True)
                return web.json_response({"status": "SUCCESS", "message": "Donation recorded successfully"})

            return web.json_response({"status": "ACK", "message": "Notification received"})
        except Exception as e:
            logging.error(f"Error handling ABA Webhook: {e}")
            return web.json_response({"status": "ERROR", "message": str(e)}, status=400)
    return handle_aba_webhook


async def start_health_server(bot=None):
    """Starts a lightweight web server for Render Free Web Service deployment, ABA PayWay Webhook, and Telegram Mini App."""
    global GLOBAL_BOT
    if bot:
        GLOBAL_BOT = bot

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
    app.router.add_get("/open_abapay", handle_open_abapay)
    app.router.add_get("/test_complete_payment", handle_test_complete_payment)
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

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                for target_url in urls_to_ping:
                    try:
                        async with session.get(target_url, timeout=15) as resp:
                            if resp.status == 200:
                                logging.debug(f"Keep-Alive self-ping to {target_url} successful (200 OK).")
                            else:
                                logging.warning(f"Keep-Alive ping to {target_url} returned status {resp.status}")
                    except Exception as ping_err:
                        logging.warning(f"Keep-Alive ping to {target_url} error: {ping_err}")
        except asyncio.CancelledError:
            logging.info("Self-Keep-Alive background worker cancelled.")
            break
        except Exception as e:
            logging.error(f"Unexpected error in Keep-Alive worker: {e}")

        await asyncio.sleep(180)  # Self-ping every 3 minutes


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
    global GLOBAL_BOT
    GLOBAL_BOT = bot
    dp = Dispatcher()

    # Register Global Exception Handler to catch any unhandled update errors
    @dp.error()
    async def global_error_handler(event: types.ErrorEvent):
        logging.error(f"🛡 Global Aiogram Exception Caught: {event.exception}", exc_info=event.exception)
        try:
            if event.update and event.update.message:
                await event.update.message.answer(
                    "⚠️ <b>មានបញ្ហាបច្ចេកទេសមួយបានកើតឡើង</b>\n"
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    "ប្រព័ន្ធបានកត់ត្រានិងដំណើរការបន្តធម្មតា។ សូមព្យាយាមម្តងទៀត!",
                    parse_mode="HTML"
                )
        except Exception as notify_err:
            logging.warning(f"Could not send error notification: {notify_err}")
        return True

    # Set Asyncio Loop Exception Handler to isolate background task exceptions
    try:
        loop = asyncio.get_running_loop()
        def _loop_exception_handler(loop, context):
            exc = context.get("exception")
            logging.error(f"🛡 Asyncio Task Exception: {context.get('message')}", exc_info=exc)
        loop.set_exception_handler(_loop_exception_handler)
    except Exception as loop_err:
        logging.warning(f"Could not set asyncio loop exception handler: {loop_err}")

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
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as wh_err:
        logging.warning(f"Note on delete_webhook: {wh_err}")

    # 7. Set Bot Commands Menu
    commands = [
        BotCommand(command="start", description="🚀 ចាប់ផ្តើមប្រើប្រាស់ (Start)"),
        BotCommand(command="donate", description="💖 បរិច្ចាគ $0.50 គាំទ្រ AI (Donate $0.50)"),
        BotCommand(command="myid", description="🆔 មើល Telegram ID របស់អ្នក (My Telegram ID)"),
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
            logging.info("⚡ Telegram Long Polling session active...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot, handle_signals=False)
            logging.warning("Telegram polling session ended. Reconnecting in 3 seconds...")
            await asyncio.sleep(3)
        except (KeyboardInterrupt, SystemExit):
            logging.info("Shutdown signal received.")
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
