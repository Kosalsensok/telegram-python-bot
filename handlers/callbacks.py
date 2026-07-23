import html
import logging
import re
from aiogram import Router, types, F
from keyboards.inline import get_welcome_inline_keyboard, get_language_inline_keyboard, get_mode_inline_keyboard
from services.db_service import DatabaseService
from utils.user_count import format_user_count
from config import BOT_DISPLAY_NAME, GEMINI_MODEL
from utils.memory import ConversationMemory
from prompts.mode_prompts import MODE_DESCRIPTIONS, MODE_EXPLANATIONS

router = Router(name="callbacks_router")


def get_callbacks_router(db_service: DatabaseService = None, memory: ConversationMemory = None) -> Router:
    """
    Construct callbacks router with injected database service and conversation memory.
    """

    @router.callback_query(F.data == "cb_mode_menu")
    async def callback_mode_menu(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        current_mode = "general"
        if db_service:
            current_mode = await db_service.get_user_mode(user_id)

        mode_text = (
            "🎯 <b>ជ្រើសរើស AI Operating Mode / Select AI Mode:</b>\n\n"
            "• <b>🤖 General AI Mode:</b> ជំនួយការ AI ទូទៅ (សួរដេញដោល, សរសេរកូដ, វិភាគទូទៅ)\n"
            "• <b>📐 Standard Mode:</b> បម្លែងសមីការ/រូបមន្ត គណិត/គីមី/រូបវិទ្យា/តារាង ជាកូដ LaTeX\n"
            "• <b>🇰🇭 Khmer Math Mode:</b> បម្លែងសមីការ គណិត/គីមី/រូបវិទ្យា/តារាង ជាកូដ LaTeX ភាសាខ្មែរ\n"
            "• <b>🌐 Translate to ខ្មែរ Mode:</b> បកប្រែអត្ថបទ, រូបភាព ឬ ឯកសារ ទៅជាភាសាខ្មែរ\n"
            "• <b>🎨 TikZ Mode:</b> បម្លែងរូបភាព ក្រាហ្វ, Circuit, ធរណីមាត្រ ជាកូដ LaTeX TikZ Diagram\n"
            "• <b>📄 PDF to Text Mode:</b> ទាញយកអត្ថបទពី PDF ភាសាខ្មែរ\n"
            "• <b>✍️ Handwrite Mode:</b> បម្លែងអក្សរដៃ/សមីការដៃ ទៅជាកូដ LaTeX ភ្លាមៗ\n\n"
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

    @router.callback_query(F.data == "cb_ask_ai")
    async def callback_ask_ai(callback: types.CallbackQuery):
        await callback.answer()
        msg = (
            "💬 <b>សូមផ្ញើសំណួរដែលអ្នកចង់សួរមកកាន់ AI Assistant៖</b>\n\n"
            "<i>ឧទាហរណ៍៖ \"តើអ្វីទៅជា Artificial Intelligence?\" ឬ \"Write a Python quicksort algorithm.\"</i>"
        )
        await callback.message.edit_text(msg, parse_mode="HTML")


    @router.callback_query(F.data == "cb_analyze_image")
    async def callback_analyze_image(callback: types.CallbackQuery):
        await callback.answer()
        msg = (
            "🖼 <b>សូមផ្ញើរូបភាព ហើយសរសេរសំណួរនៅក្នុង Caption៖</b>\n\n"
            "1. ចុច <b>Attach File / Photo</b> ក្នុង Telegram\n"
            "2. ជ្រើសរើសរូបភាព ឬ Screenshot របស់អ្នក\n"
            "3. វាយសំណួររបស់អ្នកនៅក្នុងប្រអប់ <b>Caption</b>\n"
            "4. ចុច <b>Send</b> ជាការស្រេច!"
        )
        await callback.message.edit_text(msg, parse_mode="HTML")


    @router.callback_query(F.data == "cb_language")
    async def callback_language(callback: types.CallbackQuery):
        await callback.answer()
        msg = "🌐 <b>សូមជ្រើសរើសភាសាដែលអ្នកពេញចិត្ត / Choose preferred language:</b>"
        await callback.message.edit_text(msg, parse_mode="HTML", reply_markup=get_language_inline_keyboard())



    @router.callback_query(F.data == "cb_lang_km")
    async def callback_lang_km(callback: types.CallbackQuery):
        await callback.answer("ភាសាខ្មែរត្រូវបានជ្រើសរើស")
        await callback.message.edit_text("🇰🇭 <b>ភាសាត្រូវបានកំណត់ជា៖ ភាសាខ្មែរ (Khmer)</b>\nអ្នកអាចសួរសំណួរជាភាសាខ្មែរបាន!", parse_mode="HTML")


    @router.callback_query(F.data == "cb_lang_en")
    async def callback_lang_en(callback: types.CallbackQuery):
        await callback.answer("English selected")
        await callback.message.edit_text("🇬🇧 <b>Language set to: English</b>\nYou can ask your questions in English!", parse_mode="HTML")


    @router.callback_query(F.data == "cb_lang_auto")
    async def callback_lang_auto(callback: types.CallbackQuery):
        await callback.answer("Auto-detect enabled")
        await callback.message.edit_text("🌐 <b>Language detection set to: Automatic (Khmer & English)</b>", parse_mode="HTML")


    @router.callback_query(F.data == "cb_back_main")
    async def callback_back_main(callback: types.CallbackQuery):
        await callback.answer()
        user_name = html.escape(callback.from_user.first_name or "Friend")
        welcome_text = (
            f"<b>🤖 {BOT_DISPLAY_NAME}</b>\n\n"
            f"<blockquote>សួស្តី {user_name}! 👋\n"
            "ខ្ញុំជាជំនួយការ AI ដែលអាចនិយាយភាសាខ្មែរ និង English។</blockquote>\n\n"
            "<b>✨ ខ្ញុំអាចជួយអ្នកបាន៖</b>\n"
            "💬 សួរសំណួរទូទៅ\n"
            "🖼 វិភាគរូបភាព\n"
            "💻 ពន្យល់ និងជួសជុល Code\n"
            "📚 ជួយការសិក្សា និងស្រាវជ្រាវ\n"
            "🌐 បកប្រែ Khmer ↔ English\n\n"
            "<b>🚀 ចាប់ផ្ដើមប្រើប្រាស់</b>\n"
            "ផ្ញើសំណួរមកខ្ញុំ ឬផ្ញើរូបភាពជាមួយ Caption។"
        )
        await callback.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())


    @router.callback_query(F.data == "cb_help")
    async def callback_help(callback: types.CallbackQuery):
        await callback.answer()
        help_text = (
            "📖 <b>ការណែនាំពីរបៀបប្រើប្រាស់ / Usage Guide:</b>\n\n"
            "<b>1. 💬 សួរសំណួរជាអក្សរ (Text Chat):</b>\n"
            "• វាយសំណួរជាភាសាខ្មែរ ឬអង់គ្លេស រួចផ្ញើចេញ។\n\n"
            "<b>2. 🖼 ផ្ញើរូបភាពវិភាគ (Vision AI):</b>\n"
            "• ផ្ញើរូបភាព (Photo) ហើយសរសេរសំណួរនៅក្នុង <b>Caption</b>។\n\n"
            "<b>3. 🧹 បង្កើតការសន្ទនាថ្មី (/new ឬ /clear):</b>\n"
            "• វាយ /new ឬ /clear ដើម្បីលុប Context នៃការសន្ទនាយកសំណួរថ្មី។\n\n"
            "<b>4. 📊 ពិនិត្យស្ថិតិ (/stats):</b>\n"
            "• វាយ /stats ដើម្បីមើលស្ថិតិអ្នកប្រើប្រាស់នៅក្នុងប្រព័ន្ធ។"
        )
        await callback.message.edit_text(help_text, parse_mode="HTML")


    @router.callback_query(F.data == "cb_stats")
    async def callback_stats(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        user_stats = {"total_messages": 0, "text_count": 0, "image_count": 0}
        if db_service:
            user_stats = await db_service.get_user_stats(user_id)
        stats_text = (
            "📊 <b>ស្ថិតិផ្ទាល់ខ្លួនរបស់អ្នក / Your Usage Stats</b>\n\n"
            f"💬 <b>សំណួរសរុប (Total Questions):</b> {user_stats.get('total_messages', 0)}\n"
            f"📝 <b>អត្ថបទ (Text):</b> {user_stats.get('text_count', 0)}\n"
            f"🖼️ <b>រូបភាព (Images):</b> {user_stats.get('image_count', 0)}"
        )
        await callback.message.edit_text(stats_text, parse_mode="HTML")


    @router.callback_query(F.data == "cb_clear")
    async def callback_clear(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        cleared_db = False
        if db_service:
            cleared_db = await db_service.clear_history(user_id)
        cleared_cache = memory.clear_history(user_id) if memory else False
        
        if cleared_cache or cleared_db:
            await callback.message.edit_text("🧹 <b>ប្រវត្តិសន្ទនារបស់អ្នកត្រូវបានលុបរួចរាល់!</b> / Conversation history cleared!", parse_mode="HTML")
        else:
            await callback.message.edit_text("ℹ️ មិនមានប្រវត្តិសន្ទនាដែលត្រូវលុបទេ។ / No active conversation history found.", parse_mode="HTML")


    @router.callback_query(F.data == "cb_about")
    async def callback_about(callback: types.CallbackQuery):
        await callback.answer()
        total_users = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_users = stats.get("total_users", 0)
        formatted = format_user_count(total_users)

        about_text = (
            f"👤 <b>អំពី {BOT_DISPLAY_NAME} / About Bot:</b>\n\n"
            f"🤖 <b>Bot Name:</b> {BOT_DISPLAY_NAME}\n"
            f"⚡ <b>AI Engine:</b> Google Gemini ({GEMINI_MODEL})\n"
            "🌐 <b>Supported Languages:</b> 🇰🇭 Khmer & 🇬🇧 English\n"
            f"👥 <b>Total Registered Users:</b> {total_users} ({formatted} users)\n"
            "🛠 <b>Framework:</b> Python 3.11+ & Aiogram 3.x\n"
            "🗄 <b>Database:</b> MySQL (aiomysql)\n"
            "🔒 <b>Privacy:</b> Secure, in-memory image vision pipeline."
        )
        await callback.message.edit_text(about_text, parse_mode="HTML")


    @router.callback_query(F.data == "cb_privacy")
    async def callback_privacy(callback: types.CallbackQuery):
        await callback.answer()
        privacy_text = (
            "🔒 <b>គោលការណ៍ឯកជនភាព / Privacy Policy:</b>\n\n"
            "• <b>Image Processing:</b> រូបភាពដែលអ្នកផ្ញើមកត្រូវបានដំណើរការក្នុង Memory (RAM) ដោយផ្ទាល់ និងមិនត្រូវបានរក្សាទុកជាអចិន្ត្រៃយ៍លើ Disk ឡើយ。\n"
            "• <b>Conversation Memory:</b> ប្រវត្តិសន្ទនាត្រូវបានប្រើប្រាស់ជា Temporary Context Window សម្រាប់ឆ្លើយតបសំណួររបស់អ្នកប៉ុណ្ណោះ。\n"
            "• <b>API Transmission:</b> សំណួរ និងរូបភាពត្រូវបានផ្ញើទៅកាន់ Google Gemini AI API តាមរយៈ HTTPS encrypted link សុវត្ថិភាព。\n"
            "• <b>User Data:</b> ប្រព័ន្ធរក្សាទុកតែ Telegram User ID, Username, និងឈ្មោះដើម្បីផ្តល់សេវាកម្មរាប់ចំនួនអ្នកប្រើប្រាស់ប៉ុណ្ណោះ។\n"
        )
        await callback.message.edit_text(privacy_text, parse_mode="HTML")

    return router
