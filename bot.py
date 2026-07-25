import base64
import hashlib
import hmac
import logging
import os
import sys
import time
from datetime import datetime
import asyncio
from typing import Dict

# UTF-8 Console output fix for Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("ABAPaywayDonateBot")

try:
    from fastapi import FastAPI, Request  # type: ignore
    from fastapi.responses import HTMLResponse, JSONResponse  # type: ignore
    import uvicorn  # type: ignore
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update  # type: ignore
    from telegram.ext import Application, CommandHandler, ContextTypes  # type: ignore
    HAS_STANDALONE_DEPS = True
except ImportError:
    HAS_STANDALONE_DEPS = False

if not HAS_STANDALONE_DEPS:
    # Delegate to main project entry point (aiogram 3.x + aiohttp)
    from main import main
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            logging.info("🛑 Bot ត្រូវបានបញ្ឈប់ (Bot stopped by user)!")
else:
    # Standalone FastAPI + python-telegram-bot implementation
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN").strip()
    MERCHANT_ID = os.getenv("ABA_MERCHANT_ID", "ec477154").strip()
    PUBLIC_KEY = os.getenv("ABA_API_KEY", "758d62f9bc45bf0322aadf778999bf833a9d68a0").strip()
    PAYWAY_URL = os.getenv("ABA_PAYWAY_URL", "https://checkout-sandbox.payway.com.kh/api/payment-gateway/v1/payments/purchase").strip()
    YOUR_SERVER_URL = os.getenv("SERVER_URL", os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")).rstrip("/")

    pending_donations: Dict[str, dict] = {}
    completed_donations: set = set()

    def generate_aba_hash(
        req_time: str,
        merchant_id: str,
        tran_id: str,
        amount: str,
        items: str = "",
        shipping: str = "",
        firstname: str = "",
        lastname: str = "",
        email: str = "",
        phone: str = "",
        type_val: str = "",
        payment_option: str = "",
        continue_success_url: str = "",
        return_params: str = "",
        public_key: str = PUBLIC_KEY
    ) -> str:
        str_to_hash = (
            str(req_time) + str(merchant_id) + str(tran_id) + str(amount) +
            str(items) + str(shipping) + str(firstname) + str(lastname) +
            str(email) + str(phone) + str(type_val) + str(payment_option) +
            str(continue_success_url) + str(return_params)
        )
        hashed = hmac.new(public_key.encode('utf-8'), str_to_hash.encode('utf-8'), hashlib.sha512).digest()
        return base64.b64encode(hashed).decode('utf-8')

    app_web = FastAPI(title="ABA PayWay Telegram Donation Server")

    @app_web.get("/")
    async def root():
        return {"status": "online", "message": "ABA PayWay Donation Webhook Server is active!"}

    @app_web.get("/donate_checkout", response_class=HTMLResponse)
    async def donate_checkout(tran_id: str, amount: str, req_time: str, chat_id: str):
        pending_donations[tran_id] = {
            "chat_id": chat_id,
            "amount": amount,
            "time": req_time
        }
        
        success_url = f"{YOUR_SERVER_URL}/payment_success?tran_id={tran_id}"
        continue_success_url_b64 = base64.b64encode(success_url.encode('utf-8')).decode('utf-8')
        return_params = base64.b64encode(f"chat_id={chat_id}".encode('utf-8')).decode('utf-8')

        hash_val = generate_aba_hash(
            req_time=req_time,
            merchant_id=MERCHANT_ID,
            tran_id=tran_id,
            amount=amount,
            payment_option="abapay",
            continue_success_url=continue_success_url_b64,
            return_params=return_params
        )
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Connecting to ABA Pay...</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 40px 20px; background-color: #f8f9fa; color: #333; }}
        .card {{ background: #fff; max-width: 450px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #0056b3; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        h3 {{ color: #0056b3; margin-bottom: 10px; }}
        p {{ color: #666; font-size: 15px; }}
    </style>
</head>
<body onload="document.forms[0].submit()">
    <div class="card">
        <div class="spinner"></div>
        <h3>កំពុងបញ្ជូនទៅកាន់ទំព័របង់ប្រាក់ ABA Pay...</h3>
        <p>សូមរង់ចាំមួយភ្លែត ប្រព័ន្ធកំពុងដំណើរការបង្កើតប្រតិបត្តិការបរិច្ចាគ ${amount}...</p>
        <form method="POST" action="{PAYWAY_URL}">
            <input type="hidden" name="req_time" value="{req_time}" />
            <input type="hidden" name="merchant_id" value="{MERCHANT_ID}" />
            <input type="hidden" name="tran_id" value="{tran_id}" />
            <input type="hidden" name="amount" value="{amount}" />
            <input type="hidden" name="payment_option" value="abapay" />
            <input type="hidden" name="hash" value="{hash_val}" />
            <input type="hidden" name="continue_success_url" value="{continue_success_url_b64}" />
            <input type="hidden" name="return_params" value="{return_params}" />
        </form>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)

    async def notify_user_donation_success(chat_id: str, tran_id: str, amount: str = "0.50"):
        if tran_id in completed_donations:
            return
        completed_donations.add(tran_id)

        thank_you_message = (
            "🎉 **សូមថ្លែងអំណរគុណយ៉ាងជ្រាលជ្រៅ!** 🙏❤️\n\n"
            f"ការបរិច្ចាគចំនួន **${amount}** របស់លោកអ្នកបានជោគជ័យហើយ! (ID: `{tran_id}`)\n"
            "ថវិកានេះនឹងត្រូវយកទៅប្រើប្រាស់សម្រាប់អភិវឌ្ឍន៍ប្រព័ន្ធ **Smart AI Assistant** "
            "ឱ្យកាន់តែឆ្លាតវៃ និងមានសមត្ថភាពខ្ពស់បន្ថែមទៀតសម្រាប់ឆ្នាំបន្ទាប់។\n\n"
            "✨ *សូមជូនពរឱ្យលោកអ្នកជួបប្រទះតែសេចក្ដីសុខ សុភមង្គល ទទួលបានជោគជ័យ និងមានសុខភាពល្អបរិបូរណ៍!* 🚀"
        )
        try:
            await tg_app.bot.send_message(chat_id=chat_id, text=thank_you_message, parse_mode="Markdown")
            logger.info(f"Sent donation thank you message to chat_id={chat_id} for tran_id={tran_id}")
        except Exception as e:
            logger.error(f"Failed to send Telegram thank you message to chat_id={chat_id}: {e}")

    @app_web.get("/payment_success", response_class=HTMLResponse)
    async def payment_success(tran_id: str):
        donation = pending_donations.get(tran_id, {})
        chat_id = donation.get("chat_id")
        amount = donation.get("amount", "0.50")

        if chat_id:
            await notify_user_donation_success(chat_id=chat_id, tran_id=tran_id, amount=amount)
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
        return HTMLResponse(content=html_content)

    @app_web.post("/aba_webhook")
    @app_web.get("/aba_webhook")
    async def aba_webhook(request: Request):
        try:
            if request.method == "POST":
                try:
                    payload = await request.form()
                except Exception:
                    payload = {}
                if not payload:
                    try:
                        payload = await request.json()
                    except Exception:
                        payload = {}
            else:
                payload = request.query_params

            logger.info(f"Received ABA Webhook notification: {dict(payload)}")
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

            if status in ("0", "00", "SUCCESS", "APPROVED") and tran_id and chat_id:
                await notify_user_donation_success(chat_id=chat_id, tran_id=tran_id)
                return JSONResponse({"status": "SUCCESS", "message": "Donation recorded successfully"})

            return JSONResponse({"status": "ACK", "message": "Notification received"})
        except Exception as e:
            logger.error(f"Error handling ABA Webhook: {e}")
            return JSONResponse({"status": "ERROR", "message": str(e)}, status_code=400)

    tg_app = Application.builder().token(BOT_TOKEN).build()

    async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        req_time = datetime.now().strftime("%Y%m%d%H%M%S")
        chat_str = str(chat_id)[-6:]
        time_str = str(int(time.time()))[-8:]
        tran_id = f"D{chat_str}{time_str}"
        amount = "0.50"
        
        checkout_url = f"{YOUR_SERVER_URL}/donate_checkout?tran_id={tran_id}&amount={amount}&req_time={req_time}&chat_id={chat_id}"

        message_text = (
            "🤖 **ចូលរួមគាំទ្រការអភិវឌ្ឍន៍ Smart AI Assistant** 🚀\n\n"
            "ដើម្បីជួយឱ្យប្រព័ន្ធ **Smart AI Assistant** អាចបន្តដំណើរការ និងអភិវឌ្ឍមុខងារថ្មីៗកាន់តែឆ្លាតវៃសម្រាប់ឆ្នាំក្រោយ "
            "លោកអ្នកអាចចូលរួមបរិច្ចាគថវិកាចំនួន **$0.50** តាមរយៈ ABA Pay បាន។\n\n"
            "សូមចុចប៊ូតុងខាងក្រោមដើម្បីធ្វើការបរិច្ចាគ៖"
        )

        keyboard = [
            [InlineKeyboardButton("💖 បរិច្ចាគ $0.50 តាម ABA Pay", url=checkout_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)

    tg_app.add_handler(CommandHandler("donate", donate_command))
    tg_app.add_handler(CommandHandler("buy", donate_command))

    async def run_bot_and_server():
        config = uvicorn.Config(app_web, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)

        logger.info("Starting ABA PayWay Donation Webhook server on port 8000...")
        logger.info("Starting Telegram Bot with /donate & /buy commands...")

        async with tg_app:
            await tg_app.start()
            await tg_app.updater.start_polling(drop_pending_updates=True)
            await server.serve()
            await tg_app.updater.stop()
            await tg_app.stop()

    if __name__ == "__main__":
        try:
            asyncio.run(run_bot_and_server())
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 Bot and Server stopped gracefully.")
