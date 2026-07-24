import html
import logging
import time
from typing import Dict
from aiogram import Router, types, F
from keyboards.inline import (
    get_welcome_inline_keyboard, 
    get_language_inline_keyboard, 
    get_mode_inline_keyboard,
    get_image_analysis_banner_keyboard,
    get_ai_result_contextual_keyboard,
    get_image_result_contextual_keyboard,
    get_math_answer_keyboard
)
from services.db_service import DatabaseService
from utils.user_count import format_user_count
from utils.localization import STRINGS, MODE_NAMES, get_str
from utils.memory import ConversationMemory
from config import BOT_DISPLAY_NAME, GEMINI_MODEL, RENDER_EXTERNAL_URL

# Short in-memory lock dict for debouncing rapid button taps (idempotency protection)
_callback_locks: Dict[int, float] = {}

def is_callback_locked(user_id: int, lock_time_sec: float = 1.0) -> bool:
    """Check and set lock for user callback action to prevent duplicate button execution."""
    now = time.time()
    last_time = _callback_locks.get(user_id, 0.0)
    if now - last_time < lock_time_sec:
        return True
    _callback_locks[user_id] = now
    return False

def get_callbacks_router(db_service: DatabaseService = None, memory: ConversationMemory = None) -> Router:
    """
    Construct callbacks router with immediate callback acknowledgement and debouncing.
    """
    router = Router(name="callbacks_router")

    # 1. Close Menu Callback Handler
    @router.callback_query(F.data == "cb_close_menu")
    async def callback_close_menu(callback: types.CallbackQuery):
        await callback.answer()
        try:
            await callback.message.delete()
        except Exception:
            await callback.message.edit_text("✅ Menu ត្រូវបានបិទ។", parse_mode="HTML")

    # 2. Main Menu Navigation Callback
    @router.callback_query(F.data == "cb_back_main")
    async def callback_back_main(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        user_name = html.escape(callback.from_user.first_name or "Friend") if callback.from_user else "Friend"
        
        user_lang = "km"
        if db_service:
            user_lang = await db_service.get_user_language(user_id)
            
        total_users = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_users = stats.get("total_users", 0)
        formatted_users = format_user_count(total_users)

        welcome_text = (
            "🧠 <b>SMART AI ASSISTANT</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"សួស្តី {user_name}! 👋\n"
            "ជំនួយការ AI សម្រាប់អត្ថបទ រូបភាព គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។\n\n"
            f"👥 <b>អ្នកប្រើប្រាស់សរុប:</b> {total_users} ({formatted_users} users)\n\n"
            "👇 <b>សូមជ្រើសរើសមុខងារខាងក្រោម៖</b>"
        )
        try:
            await callback.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard(user_lang))
        except Exception as e:
            logging.debug(f"Menu update skipped: {e}")

    # 3. Ask AI Prompt Callback
    @router.callback_query(F.data == "cb_ask_ai")
    async def callback_ask_ai(callback: types.CallbackQuery):
        await callback.answer()
        msg_text = (
            "💬 <b>សួរសំណួរទៅកាន់ AI</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "សូមវាយសំណួររបស់អ្នកជាអក្សរ (Text) រួចផ្ញើមកកាន់ Bot ឥឡូវនេះ!\n\n"
            "<i>ឧទាហរណ៍៖ \"សូមពន្យល់ពី Python Asyncio ឱ្យបានច្បាស់\"</i>"
        )
        try:
            await callback.message.edit_text(msg_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())
        except Exception:
            pass

    # 4. Analyze Image Banner Callback
    @router.callback_query(F.data == "cb_analyze_image")
    async def callback_analyze_image(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        if db_service:
            await db_service.set_user_mode(user_id, "image_analysis")
            
        banner_text = (
            "🖼 <b>វិភាគរូបភាព</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "សូមផ្ញើរូបភាពដែលអ្នកចង់ឱ្យ AI វិភាគ។\n\n"
            "AI អាចសម្គាល់៖\n"
            "• Screenshot\n"
            "• ឯកសារ\n"
            "• អត្ថបទ\n"
            "• តារាង\n"
            "• រូបមន្ត\n"
            "• ផលិតផល"
        )
        try:
            await callback.message.edit_text(banner_text, parse_mode="HTML", reply_markup=get_image_analysis_banner_keyboard())
        except Exception:
            pass

    # 5. Cancel Image Mode
    @router.callback_query(F.data == "cb_cancel_image_mode")
    async def callback_cancel_image_mode(callback: types.CallbackQuery):
        await callback.answer("✅ បានបោះបង់ការវិភាគរូបភាព")
        user_id = callback.from_user.id if callback.from_user else 0
        if db_service:
            await db_service.set_user_mode(user_id, "general")
        await callback_back_main(callback)

    # 6. Mode Menu Callback
    @router.callback_query(F.data == "cb_mode_menu")
    async def callback_mode_menu(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        current_mode = "general"
        if db_service:
            current_mode = await db_service.get_user_mode(user_id)

        mode_text = (
            "🎯 <b>ជ្រើសរើស AI Mode</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "សូមជ្រើសរើស AI Mode ដែលសមស្របនឹងសំណួររបស់អ្នក៖"
        )
        try:
            await callback.message.edit_text(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(current_mode))
        except Exception:
            pass

    # 7. Set Mode Callback
    @router.callback_query(F.data.startswith("set_mode_"))
    async def callback_set_mode(callback: types.CallbackQuery):
        user_id = callback.from_user.id if callback.from_user else 0
        selected_mode = callback.data.replace("set_mode_", "")

        if is_callback_locked(user_id, 0.5):
            await callback.answer()
            return

        if db_service:
            await db_service.set_user_mode(user_id, selected_mode)

        await callback.answer(f"✅ បានកំណត់ Mode: {selected_mode.upper()}")
        mode_text = (
            "🎯 <b>ជ្រើសរើស AI Mode</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ Mode ត្រូវបានប្តូរទៅជា៖ <b>{selected_mode.upper()}</b>"
        )
        try:
            await callback.message.edit_text(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(selected_mode))
        except Exception:
            pass

    # 8. Language Selection Menu
    @router.callback_query(F.data == "cb_language")
    async def callback_language_menu(callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id if callback.from_user else 0
        current_lang = "km"
        if db_service:
            current_lang = await db_service.get_user_language(user_id)

        lang_text = (
            "🌍 <b>ជ្រើសរើសភាសា</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "សូមជ្រើសរើសភាសាសម្រាប់ចម្លើយរបស់ AI ៖"
        )
        try:
            await callback.message.edit_text(lang_text, parse_mode="HTML", reply_markup=get_language_inline_keyboard(current_lang))
        except Exception:
            pass

    # 9. Set Language Callback
    @router.callback_query(F.data.startswith("set_lang_"))
    async def callback_set_lang(callback: types.CallbackQuery):
        user_id = callback.from_user.id if callback.from_user else 0
        selected_lang = callback.data.replace("set_lang_", "")

        if is_callback_locked(user_id, 0.5):
            await callback.answer()
            return

        if db_service:
            await db_service.set_user_language(user_id, selected_lang)

        await callback.answer(f"✅ Language updated: {selected_lang.upper()}")
        lang_text = (
            "🌍 <b>ជ្រើសរើសភាសា</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ ភាសាត្រូវបានប្តូរទៅជា៖ <b>{selected_lang.upper()}</b>"
        )
        try:
            await callback.message.edit_text(lang_text, parse_mode="HTML", reply_markup=get_language_inline_keyboard(selected_lang))
        except Exception:
            pass

    # 10. Mini App Callback
    @router.callback_query(F.data == "cb_miniapp")
    async def callback_miniapp(callback: types.CallbackQuery):
        await callback.answer()
        base_url = (RENDER_EXTERNAL_URL or "http://localhost:8080").rstrip('/')
        mini_app_url = f"{base_url}/answer/demo"

        from aiogram.utils.keyboard import InlineKeyboardBuilder
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
        try:
            await callback.message.edit_text(msg_text, parse_mode="HTML", reply_markup=builder.as_markup())
        except Exception:
            pass

    # 11. Help Callback
    @router.callback_query(F.data == "cb_help")
    async def callback_help(callback: types.CallbackQuery):
        await callback.answer()
        help_text = (
            "ℹ️ <b>ជំនួយ និងការណែនាំ</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "<b>1. 💬 សួរសំណួរ AI:</b> វាយសំណួរជាភាសាខ្មែរ ឬ English រួចផ្ញើចេញ\n"
            "<b>2. 🖼 វិភាគរូបភាព:</b> ផ្ញើរូបភាពលំហាត់ សមរភូមិ ឬអត្ថបទ\n"
            "<b>3. 🎯 AI Modes:</b> ប្តូរ Mode តាមមុខវិជ្ជា (គណិត គីមី រូបវិទ្យា...)\n"
            "<b>4. 🌐 Mini App:</b> ប្រើប្រាស់ Mini App អន្តរកម្មកម្រិតខ្ពស់"
        )
        try:
            await callback.message.edit_text(help_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())
        except Exception:
            pass

    # 12. About Callback
    @router.callback_query(F.data == "cb_about")
    async def callback_about(callback: types.CallbackQuery):
        await callback.answer()
        about_text = (
            f"🤖 <b>អំពី {BOT_DISPLAY_NAME}</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ <b>AI Engine:</b> Google Gemini ({GEMINI_MODEL})\n"
            "🌐 <b>Supported Languages:</b> 🇰🇭 Khmer & 🇬🇧 English\n"
            "🛠 <b>Framework:</b> Python 3.11+ & Aiogram 3.x\n"
            "🔒 <b>Security:</b> Enterprise grade, privacy focused."
        )
        try:
            await callback.message.edit_text(about_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())
        except Exception:
            pass

    # 13. Privacy Callback
    @router.callback_query(F.data == "cb_privacy")
    async def callback_privacy(callback: types.CallbackQuery):
        await callback.answer()
        privacy_text = (
            "🔐 <b>គោលការណ៍ឯកជនភាព</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• រូបភាពត្រូវបានវិភាគក្នុង RAM និងលុបចោលវិញភ្លាមៗ។\n"
            "• ប្រវត្តិសន្ទនាត្រូវបានរក្សាទុកតែក្នុងប្រព័ន្ធសុវត្ថិភាព។\n"
            "• ព័ត៌មានផ្ទាល់ខ្លួនមិនត្រូវបានចែករំលែកទៅភាគីទីបីឡើយ។"
        )
        try:
            await callback.message.edit_text(privacy_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())
        except Exception:
            pass

    # 14. Contextual Result Action Callbacks
    @router.callback_query(F.data.startswith("ai_explain:"))
    @router.callback_query(F.data.startswith("ai_regen:"))
    @router.callback_query(F.data.startswith("ai_simple:"))
    @router.callback_query(F.data.startswith("img_ask:"))
    @router.callback_query(F.data.startswith("img_reanalyze:"))
    @router.callback_query(F.data.startswith("math_latex:"))
    @router.callback_query(F.data.startswith("math_steps:"))
    async def callback_contextual_actions(callback: types.CallbackQuery):
        await callback.answer("✅ Action requested!")

    return router
