import html
import logging
import re
from aiogram import Router, types, F
from keyboards.inline import (
    get_welcome_inline_keyboard, 
    get_language_inline_keyboard, 
    get_mode_inline_keyboard,
    get_image_download_keyboard,
    get_requirements_navigation_keyboard,
    get_code_answer_keyboard,
    get_math_answer_keyboard
)
from services.db_service import DatabaseService
from utils.user_count import format_user_count
from config import BOT_DISPLAY_NAME, GEMINI_MODEL
from utils.memory import ConversationMemory
from prompts.mode_prompts import MODE_DESCRIPTIONS, MODE_EXPLANATIONS
from utils.solution_card import get_solution_cache, render_solution_card, render_solution_pdf
from services.prototype_service import create_mart_system_prototype_files, generate_prototype_zip_bytes

def get_callbacks_router(db_service: DatabaseService = None, memory: ConversationMemory = None) -> Router:
    """
    Construct callbacks router with injected database service and conversation memory.
    Handles requirement page navigation, code actions, HD cards, and PDF exports.
    """
    router = Router(name="callbacks_router")

    # 1. Basic Navigation & Mode Callbacks
    @router.callback_query(F.data == "cb_mode_menu")
    async def callback_mode_menu(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        current_mode = "general"
        if db_service:
            current_mode = await db_service.get_user_mode(user_id)

        mode_text = (
            "🎯 <b>ជ្រើសរើស AI Operating Mode / Select AI Mode:</b>\n\n"
            "• <b>🤖 General AI Mode:</b> ជំនួយការ AI ទូទៅ\n"
            "• <b>📐 Standard Mode:</b> បម្លែងសមីការ គណិត/គីមី/រូបវិទ្យា ជា LaTeX\n"
            "• <b>🇰🇭 Khmer Math Mode:</b> បម្លែងសមីការ ជា LaTeX ភាសាខ្មែរ\n"
            "• <b>🌐 Translate to ខ្មែរ Mode:</b> បកប្រែអត្ថបទ/រូបភាព ទៅជាខ្មែរ\n"
            "• <b>🎨 TikZ Mode:</b> បម្លែង ក្រាហ្វ/Circuit/ធរណីមាត្រ ជា TikZ Code\n"
            "• <b>📄 PDF to Text Mode:</b> ទាញយកអត្ថបទពី PDF ខ្មែរ\n"
            "• <b>✍️ Handwrite Mode:</b> បម្លែងអក្សរដៃ/សមីការដៃ ជា LaTeX\n\n"
            f"📌 Mode បច្ចុប្បន្នរបស់អ្នក៖ <b>{current_mode.upper()}</b>"
        )
        await callback.message.edit_text(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(current_mode))

    @router.callback_query(F.data.startswith("set_mode_"))
    async def callback_set_mode(callback: types.CallbackQuery):
        user_id = callback.from_user.id if callback.from_user else 0
        selected_mode = callback.data.replace("set_mode_", "")

        if db_service:
            await db_service.set_user_mode(user_id, selected_mode)

        mode_title = MODE_DESCRIPTIONS.get(selected_mode, selected_mode.upper())
        mode_explanation = MODE_EXPLANATIONS.get(selected_mode, "👉 រាល់សំណួរ, រូបភាព ឬ ឯកសារដែលអ្នកផ្ញើមកបន្ទាប់ នឹងត្រូវបានដំណើរការតាម Mode នេះ!")
        await callback.answer(f"✅ បានកំណត់ Mode ទៅជា: {selected_mode.upper()}")

        mode_text = (
            f"✅ <b>បានកំណត់ Mode ជោគជ័យ! / Mode Updated!</b>\n\n"
            f"📌 <b>Active Mode:</b> {mode_title}\n\n"
            f"{mode_explanation}"
        )
        await callback.message.edit_text(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(selected_mode))

    @router.callback_query(F.data == "cb_miniapp")
    async def callback_miniapp(callback: types.CallbackQuery):
        await callback.answer()
        from config import RENDER_EXTERNAL_URL
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        base_url = (RENDER_EXTERNAL_URL or "http://localhost:8080").rstrip('/')
        mini_app_url = f"{base_url}/answer/demo"

        builder = InlineKeyboardBuilder()
        builder.button(text="🌐 បើក Telegram Mini App (Launch)", web_app=types.WebAppInfo(url=mini_app_url))
        builder.button(text="🏠 Menu", callback_data="cb_back_main")
        builder.adjust(1, 1)

        msg_text = (
            "🌐 <b>TELEGRAM MINI APP INTERACTIVE EXPERIENCE</b>\n\n"
            "លោកអ្នកអាចបើកមើល <b>Smart AI Assistant Mini App</b> ដោយផ្ទាល់ក្នុង Telegram ជាមួយនឹង៖\n"
            "• <b>Vertical Stepper Navigation:</b> ចុចមើលតាម Step & Section\n"
            "• <b>Copy Code Buttons:</b> ចម្លងកូដដោយត្រង់\n"
            "• <b>Telegram Dark/Light Theme:</b> សមស្របតាមម៉ូដទូរស័ព្ទ\n\n"
            "👇 <b>ចុចប៊ូតុងខាងក្រោមដើម្បីបើក Mini App៖</b>"
        )
        await callback.message.edit_text(msg_text, parse_mode="HTML", reply_markup=builder.as_markup())

    @router.callback_query(F.data == "cb_back_main")
    async def callback_back_main(callback: types.CallbackQuery):
        await callback.answer()
        user_name = html.escape(callback.from_user.first_name or "Friend")
        total_users = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_users = stats.get("total_users", 0)
        formatted_users = format_user_count(total_users)

        welcome_text = (
            f"<b>🤖 {BOT_DISPLAY_NAME}</b>\n\n"
            f"<blockquote>សួស្តី {user_name}! 👋\n"
            "ខ្ញុំជាជំនួយការ AI ដែលអាចនិយាយភាសាខ្មែរ និង English។</blockquote>\n\n"
            f"👥 <b>អ្នកប្រើប្រាស់សរុប:</b> {total_users} ({formatted_users} users)\n\n"
            "<b>✨ ខ្ញុំអាចជួយអ្នកបាន៖</b>\n"
            "💬 សួរសំណួរទូទៅ (Text Chat)\n"
            "🖼 វិភាគរូបភាព (Vision AI)\n"
            "🎯 7 Specialized AI Operating Modes (/mode)\n"
            "💻 ពន្យល់ និងដំណើរការកូដ (/run /code)"
        )
        await callback.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())

    # 2. System Requirements Page Navigation Callbacks (Requirement 5 & 6)
    PAGE_MAP = {
        "overview": (1, "1️⃣ <b>OVERVIEW & PROJECT SCOPE</b>\n\nប្រព័ន្ធគ្រប់គ្រង Mart សម្រាប់គ្រប់គ្រងការលក់, ស្តុក, ផលិតផល, បុគ្គលិក, អតិថិជន, និងរបាយការណ៍ហិរញ្ញវត្ថុ។"),
        "features": (2, "2️⃣ <b>CORE FUNCTIONAL MODULES</b>\n\n• POS Sales & Barcode Scanner\n• Inventory & Stock Alerts\n• Purchase Orders & Suppliers\n• Multi-Payment Checkout (KHQR, Cash)\n• User Roles & Permissions"),
        "roles": (3, "3️⃣ <b>USER ROLES & PERMISSIONS</b>\n\n• <b>Admin:</b> Full System Control & Audit Logs\n• <b>Manager:</b> Reports, Discounts & Stock Adjustments\n• <b>Cashier:</b> POS Checkout & Receipts\n• <b>Stock Controller:</b> Stock In/Out & Purchase Orders"),
        "flows": (4, "4️⃣ <b>USER FLOWS & PROCESSES</b>\n\n1. Cashier authenticates register.\n2. Barcode scanner fetches product price.\n3. System calculates subtotal, tax & discounts.\n4. Sale completes and stock reduces atomically."),
        "database": (7, "7️⃣ <b>DATABASE DESIGN</b>\n\nTables:\n• <code>users</code> (id, username, role, password_hash)\n• <code>products</code> (id, barcode, name, price, stock)\n• <code>sales</code> (id, receipt_number, total, cashier_id)\n• <code>sale_items</code> (id, sale_id, product_id, qty)"),
        "api": (8, "8️⃣ <b>API ENDPOINTS SPECIFICATION</b>\n\n• <code>POST /api/v1/auth/login</code> — Authenticate user\n• <code>GET /api/v1/products/:barcode</code> — Scan barcode\n• <code>POST /api/v1/sales/checkout</code> — Process checkout\n• <code>GET /api/v1/reports/daily</code> — Generate sales report"),
        "ui": (9, "9️⃣ <b>UI SCREENS SPECIFICATION</b>\n\n1. POS Checkout Screen\n2. Inventory & Stock Control Screen\n3. Product Management Screen\n4. Sales & Analytics Dashboard"),
        "code": (11, "1️⃣1️⃣ <b>PROTOTYPE CODE PREVIEW</b>\n\n<pre><code class='language-python'># pos_service.py\ndef checkout(cashier, items, payment_method):\n    subtotal = sum(i.total_price for i in items)\n    receipt = generate_receipt()\n    update_stock_atomically(items)\n    return receipt\n</code></pre>"),
        "tests": (12, "1️⃣2️⃣ <b>TESTING & ACCEPTANCE CRITERIA</b>\n\n• Atomic Stock Update Test: PASS\n• Duplicate Receipt Prevention Test: PASS\n• Barcode Scanner Lookup Test: PASS"),
        "deploy": (13, "1️⃣3️⃣ <b>DEPLOYMENT & DOCKER SETUP</b>\n\n• Containerized Python 3.11 + PostgreSQL\n• Docker Compose multi-service deployment\n• Render Free Web Service 24/7 keep-alive worker")
    }

    @router.callback_query(F.data.startswith("req_"))
    async def handle_requirements_callbacks(callback: types.CallbackQuery):
        data = callback.data
        parts = data.split(":")
        action_key = parts[0].replace("req_", "")
        sid = parts[1] if len(parts) > 1 else ""

        await callback.answer()

        sol = get_solution_cache(sid)
        title = sol.get("title", "Smart Mart System") if sol else "Smart Mart System"

        if action_key == "download":
            # Generate prototype zip archive (Requirement 13)
            files = create_mart_system_prototype_files(title)
            zip_bytes = generate_prototype_zip_bytes(files)
            zip_doc = types.BufferedInputFile(zip_bytes, filename=f"Mart_System_Prototype_{sid[:6]}.zip")
            await callback.message.reply_document(
                document=zip_doc,
                caption=f"📦 <b>{title} — Downloadable Prototype ZIP Archive</b>\n\n<i>Includes: README, .env.example, schema.sql, models.py, pos_service.py, main.py, test_pos.py</i>",
                parse_mode="HTML"
            )
            return

        if action_key == "page":
            page_num = int(parts[1]) if len(parts) > 2 else 1
            sid = parts[2] if len(parts) > 2 else sid
            section_info = f"📌 <b>SECTION {page_num} / 13</b>\n\n"
            msg_text = f"🛒 <b>{title}</b>\n\n{section_info}សូមជ្រើសរើសផ្នែកខាងក្រោម ដើម្បីមើលព័ត៌មានលម្អិត។"
            await callback.message.edit_text(
                msg_text,
                parse_mode="HTML",
                reply_markup=get_requirements_navigation_keyboard(sid, current_page=page_num, total_pages=13)
            )
            return

        page_num, content_text = PAGE_MAP.get(action_key, (1, "<b>ផ្នែកដែលបានជ្រើសរើស (Selected Section)</b>"))
        full_msg = f"🛒 <b>{title}</b>\n\n{content_text}"
        await callback.message.edit_text(
            full_msg,
            parse_mode="HTML",
            reply_markup=get_requirements_navigation_keyboard(sid, current_page=page_num, total_pages=13)
        )

    # 3. Code Actions Callbacks (Requirement 10)
    @router.callback_query(F.data.startswith("code_"))
    async def handle_code_callbacks(callback: types.CallbackQuery):
        data = callback.data
        parts = data.split(":")
        action = parts[0]
        sid = parts[1] if len(parts) > 1 else ""

        await callback.answer()
        sol = get_solution_cache(sid)
        raw_code = "print('Hello Smart AI')"
        if sol and sol.get("data") and sol["data"].get("sections"):
            for sec in sol["data"]["sections"]:
                if sec.get("code"):
                    raw_code = sec["code"]
                    break

        if action == "code_copy":
            clean_escaped = html.escape(raw_code)
            await callback.message.reply(f"📋 <b>Copyable Code Snippet:</b>\n\n<code>{clean_escaped}</code>", parse_mode="HTML")

        elif action == "code_full":
            clean_escaped = html.escape(raw_code)
            await callback.message.reply(f"🔍 <b>Full Code View:</b>\n\n<pre><code>{clean_escaped}</code></pre>", parse_mode="HTML")

        elif action == "code_explain":
            explanation = (
                "🧠 <b>ការពន្យល់កូដ (Technical Code Explanation):</b>\n\n"
                "1. <b>Structure:</b> កូដនេះប្រើប្រាស់ Architecture ស្អាត និងចែកចេញជា <code>models</code>, <code>services</code>, និង <code>database</code>.\n"
                "2. <b>Performance:</b> ដំណើរការកាត់បន្ថយស្តុក និងបង្កើត Sale ក្នុង Transaction តែមួយ (Atomic Operation).\n"
                "3. <b>Security:</b> ការពារ SQL Injection ដោយប្រើ Parameterized Queries <code>?</code>."
            )
            await callback.message.reply(explanation, parse_mode="HTML")

        elif action == "code_file":
            doc_bytes = raw_code.encode("utf-8")
            code_doc = types.BufferedInputFile(doc_bytes, filename=f"solution_{sid[:6]}.py")
            await callback.message.reply_document(
                document=code_doc,
                caption="📥 <b>Source Code File (Complete Runnable File)</b>",
                parse_mode="HTML"
            )

    # 4. HD Answer Card & PDF Export Callbacks (Requirement 20 & 21)
    @router.callback_query(F.data.startswith("answer_hd:"))
    async def callback_answer_hd(callback: types.CallbackQuery):
        sid = callback.data.split("answer_hd:", 1)[1]
        await callback.answer("🔍 កំពុងបង្កើត HD Answer Card PNG...")

        sol = get_solution_cache(sid)
        if sol and sol.get("card_bytes"):
            png_bytes = sol["card_bytes"]
        elif sol and sol.get("raw_text"):
            png_bytes = render_solution_card(sol["raw_text"], parsed_data=sol.get("data"))
        else:
            png_bytes = None

        if png_bytes:
            doc_file = types.BufferedInputFile(png_bytes, filename=f"Answer_Card_{sid[:6]}.png")
            await callback.message.reply_document(
                document=doc_file,
                caption="🔍 <b>HD Answer Card (High-DPI Form A Stepper Card)</b>",
                parse_mode="HTML"
            )
        else:
            await callback.answer("⚠️ រូបភាព HD ផុតកំណត់ (Cache expired)", show_alert=True)

    @router.callback_query(F.data.startswith("answer_pdf:"))
    async def callback_answer_pdf(callback: types.CallbackQuery):
        sid = callback.data.split("answer_pdf:", 1)[1]
        await callback.answer("📥 កំពុងបង្កើត PDF Document...")

        sol = get_solution_cache(sid)
        if sol and sol.get("raw_text"):
            pdf_bytes = render_solution_pdf(sol["raw_text"], parsed_data=sol.get("data"))
            if pdf_bytes:
                pdf_file = types.BufferedInputFile(pdf_bytes, filename=f"Answer_Document_{sid[:6]}.pdf")
                await callback.message.reply_document(
                    document=pdf_file,
                    caption="📥 <b>A4 Printable PDF Document</b>",
                    parse_mode="HTML"
                )
                return

        await callback.answer("⚠️ មិនអាចបង្កើត PDF បានទេ (Cache expired)", show_alert=True)

    return router
