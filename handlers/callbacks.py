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
    Construct callbacks router with immediate callback acknowledgement, safe photo/text caption edits, and debouncing.
    """
    router = Router(name="callbacks_router")

    async def safe_edit_message(message: types.Message, text: str, reply_markup=None):
        """Safely edit message caption if photo message or text if normal text message."""
        try:
            if message.photo or message.caption is not None:
                await message.edit_caption(caption=text, parse_mode="HTML", reply_markup=reply_markup)
            else:
                await message.edit_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
        except Exception:
            try:
                await message.edit_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
            except Exception:
                try:
                    await message.answer(text, parse_mode="HTML", reply_markup=reply_markup)
                except Exception:
                    pass

    # 1. Close Menu Callback Handler
    @router.callback_query(F.data == "cb_close_menu")
    async def callback_close_menu(callback: types.CallbackQuery):
        await callback.answer()
        try:
            await callback.message.delete()
        except Exception:
            await safe_edit_message(callback.message, "✅ Menu ត្រូវបានបិទ។")

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
            "🧠 <b>SMART AI ASSISTANT</b> 🤖\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇰🇭 <b>ប្រព័ន្ធ AI ឆ្លាតវៃ បង្កើតឡើងដោយស្នាដៃកូនខ្មែរ 100%</b> 🇰🇭\n"
            "👑 <b>អ្នកបង្កើត (Creator):</b> <a href=\"https://t.me/kosalsensokpk\">@kosalsensokpk</a>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"សួស្តី <b>{user_name}</b>! 👋\n\n"
            "ជំនួយការ AI សម្រាប់អត្ថបទ រូបភាព គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។\n\n"
            f"👥 <b>អ្នកប្រើប្រាស់សរុប:</b> {total_users} ({formatted_users} users)\n\n"
            "👇 <b>សូមជ្រើសរើសមុខងារខាងក្រោម៖</b>"
        )
        await safe_edit_message(callback.message, welcome_text, reply_markup=get_welcome_inline_keyboard(user_lang))

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
        await safe_edit_message(callback.message, msg_text, reply_markup=get_welcome_inline_keyboard())

    # 3b. Speech-to-Text Callback
    @router.callback_query(F.data == "cb_speech_to_text")
    async def callback_speech_to_text(callback: types.CallbackQuery):
        await callback.answer()
        msg_text = (
            "🎙️ <b>មុខងារបម្លែងសំឡេងទៅជាអក្សរ (Speech-to-Text)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨ <b>គាំទ្រភាសាខ្មែរ 🇰🇭 និងភាសាអង់គ្លេស 🇺🇸 យ៉ាងត្រឹមត្រូវខ្ពស់!</b>\n\n"
            "👉 <b>របៀបប្រើប្រាស់៖</b>\n"
            "1. ចុចលើរូប <b>មេក្រូ 🎤</b> (នៅខាងស្តាំក្រោមនៃប្រអប់សារ)\n"
            "2. និយាយសារសំឡេងរបស់អ្នក (Voice Note) ឬ ផ្ញើ File សំឡេង (.mp3, .m4a, .wav)\n"
            "3. Bot នឹងបម្លែងសំឡេងទៅជាអក្សរ និងឆ្លើយតបយ៉ាងក្បោះក្បាយភ្លាមៗ!"
        )
        await safe_edit_message(callback.message, msg_text, reply_markup=get_welcome_inline_keyboard())

    # 3c. Navigation & Location Callback
    @router.callback_query(F.data == "cb_navigation")
    async def callback_navigation(callback: types.CallbackQuery):
        await callback.answer()
        msg_text = (
            "🗺️ <b>មុខងារបង្ហាញផ្លូវ & ស្វែងរកទីតាំង (Navigation & Direction)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨ <b>ជួយស្វែងរកទីតាំង បង្ហាញផ្លូវ និងទិសដៅទៅកាន់គោលដៅ!</b>\n\n"
            "👉 <b>របៀបប្រើប្រាស់៖</b>\n"
            "1. <b>Share Location:</b> ចុចរូប Clip 📎 ➡️ ជ្រើសរើស <b>Location</b> ដើម្បីផ្ញើទីតាំង GPS\n"
            "2. <b>វាយសារសួរផ្លូវ:</b> វាយសារដូចជា <i>\"បង្ហាញផ្លូវទៅផ្សារថ្មី\"</i> ឬ <i>\"ទិសដៅទៅកាន់អាកាសយានដ្ឋានភ្នំពេញ\"</i>\n"
            "3. Bot នឹងវិភាគទីតាំង និងផ្តល់ប៊ូតុង <b>Google Maps Direct Navigation</b> (នាំផ្លូវ) ភ្លាមៗ!"
        )
        await safe_edit_message(callback.message, msg_text, reply_markup=get_welcome_inline_keyboard())

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
        await safe_edit_message(callback.message, banner_text, reply_markup=get_image_analysis_banner_keyboard())

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
        await safe_edit_message(callback.message, mode_text, reply_markup=get_mode_inline_keyboard(current_mode))

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
        await safe_edit_message(callback.message, mode_text, reply_markup=get_mode_inline_keyboard(selected_mode))

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
        await safe_edit_message(callback.message, lang_text, reply_markup=get_language_inline_keyboard(current_lang))

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
        await safe_edit_message(callback.message, lang_text, reply_markup=get_language_inline_keyboard(selected_lang))

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
        await safe_edit_message(callback.message, msg_text, reply_markup=builder.as_markup())

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
        await safe_edit_message(callback.message, help_text, reply_markup=get_welcome_inline_keyboard())

    @router.callback_query(F.data == "cb_about")
    async def callback_about(callback: types.CallbackQuery):
        await callback.answer()
        about_text = (
            f"🤖 <b>អំពី {BOT_DISPLAY_NAME} / About Bot</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇰🇭 <b>បង្កើតឡើងដោយស្នាដៃកូនខ្មែរ 100%</b> 🇰🇭\n"
            "👑 <b>អ្នកបង្កើត (Creator):</b> <a href=\"https://t.me/kosalsensokpk\">@kosalsensokpk</a>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ <b>AI Engine:</b> Google Gemini ({GEMINI_MODEL})\n"
            "🌐 <b>Supported Languages:</b> 🇰🇭 Khmer & 🇬🇧 English\n"
            "🛠 <b>Framework:</b> Python 3.11+ & Aiogram 3.x\n"
            "🔒 <b>Security:</b> Enterprise grade, privacy focused."
        )
        await safe_edit_message(callback.message, about_text, reply_markup=get_welcome_inline_keyboard())

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
        await safe_edit_message(callback.message, privacy_text, reply_markup=get_welcome_inline_keyboard())

    # 14. Contextual Result Action Callbacks
    @router.callback_query(F.data.startswith("ai_like:"))
    async def callback_ai_like(callback: types.CallbackQuery):
        await callback.answer("❤️ អរគុណសម្រាប់ការវាយតម្លៃ! (Thank you for your feedback!)", show_alert=False)

    @router.callback_query(F.data.startswith("ai_dislike:"))
    async def callback_ai_dislike(callback: types.CallbackQuery):
        await callback.answer("🙏 អរគុណសម្រាប់មតិរិះគន់! យើងនឹងកែប្រែ AI ឱ្យកាន់តែប្រសើរ។", show_alert=False)

    @router.callback_query(F.data.startswith("img_dl_jpg:"))
    @router.callback_query(F.data.startswith("img_dl_png:"))
    async def callback_image_download(callback: types.CallbackQuery):
        await callback.answer("📥 បានផ្ញើសំណើទាញយករូបភាព (Downloading image...)")

    @router.callback_query(F.data == "cb_image_gen_new")
    async def callback_image_gen_new(callback: types.CallbackQuery):
        await callback.answer()
        guide_msg = (
            "🎨 <b>បង្កើតរូបភាព AI ថ្មី (New AI Image):</b>\n\n"
            "សូមវាយ <code>/image [ការពិពណ៌នារូបភាពជាភាសាខ្មែរ ឬ English]</code>\n\n"
            "<b>ឧទាហរណ៍៖</b>\n"
            "• <code>/image 16:9 logo e lms cool, modern vector</code>"
        )
        try:
            await callback.message.reply(guide_msg, parse_mode="HTML")
        except Exception:
            pass

    # 14. Contextual AI Actions Callbacks
    @router.callback_query(F.data.startswith("ai_explain:"))
    async def callback_ai_explain(callback: types.CallbackQuery):
        await callback.answer()
        guide_msg = "💡 <b>សូមវាយសំណួរ៖</b> <i>\"សូមពន្យល់ចំណុចខាងលើឱ្យបានលម្អិតបន្ថែម\"</i>"
        try:
            await callback.message.reply(guide_msg, parse_mode="HTML")
        except Exception:
            pass

    @router.callback_query(F.data.startswith("ai_regen:"))
    async def callback_ai_regen(callback: types.CallbackQuery):
        await callback.answer("🔄 កំពុងបង្កើតចម្លើយឡើងវិញ...", show_alert=False)

    @router.callback_query(F.data.startswith("ai_simple:"))
    async def callback_ai_simple(callback: types.CallbackQuery):
        await callback.answer()
        guide_msg = "📋 <b>សូមវាយសំណួរ៖</b> <i>\"សូមសង្ខេបចម្លើយខាងលើឱ្យខ្លី និងសាមញ្ញបំផុត\"</i>"
        try:
            await callback.message.reply(guide_msg, parse_mode="HTML")
        except Exception:
            pass

    @router.callback_query(F.data.startswith("img_ask:"))
    async def callback_img_ask(callback: types.CallbackQuery):
        await callback.answer()
        guide_msg = "💬 <b>សូមវាយសំណួរបន្ថែម៖</b> <i>\"តើរូបភាពនេះមានន័យដូចម្តេច?\"</i>"
        try:
            await callback.message.reply(guide_msg, parse_mode="HTML")
        except Exception:
            pass

    @router.callback_query(F.data.startswith("img_reanalyze:"))
    async def callback_img_reanalyze(callback: types.CallbackQuery):
        await callback.answer()
        guide_msg = "🔁 <b>សូមផ្ញើរូបភាពម្តងទៀត</b> ដើម្បីឱ្យ AI ធ្វើការវិភាគឡើងវិញ!"
        try:
            await callback.message.reply(guide_msg, parse_mode="HTML")
        except Exception:
            pass

    @router.callback_query(F.data.startswith("math_latex:"))
    async def callback_math_latex(callback: types.CallbackQuery):
        await callback.answer()
        msg_text = callback.message.text or callback.message.caption or ""
        import re
        latex_matches = re.findall(r'(\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\))', msg_text, re.DOTALL)
        if latex_matches:
            extracted = "\n\n".join(latex_matches)
            resp = f"📋 <b>LaTeX Code:</b>\n\n<pre><code>{html.escape(extracted)}</code></pre>"
        else:
            resp = f"📋 <b>Text / Math Content:</b>\n\n<pre><code>{html.escape(msg_text[:1000])}</code></pre>"
        try:
            await callback.message.reply(resp, parse_mode="HTML")
        except Exception:
            pass

    @router.callback_query(F.data.startswith("math_steps:"))
    async def callback_math_steps(callback: types.CallbackQuery):
        await callback.answer()
        guide_msg = "💡 <b>សូមវាយសំណួរ៖</b> <i>\"សូមបង្ហាញជំហានគណនាឱ្យបានលម្អិតគ្រប់ Step\"</i>"
        try:
            await callback.message.reply(guide_msg, parse_mode="HTML")
        except Exception:
            pass

    # 15. ABA PayWay Donation Callback
    @router.callback_query(F.data == "cb_donate")
    async def callback_donate(callback: types.CallbackQuery):
        await callback.answer()
        chat_id = callback.from_user.id if callback.from_user else callback.message.chat.id
        from services.aba_payway import request_aba_payway_purchase
        from config import ABA_MERCHANT_ID, ABA_API_KEY, ABA_PAYWAY_URL, SERVER_URL
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        import base64

        first_name = callback.from_user.first_name if callback.from_user else "Donor"
        username = callback.from_user.username if callback.from_user and callback.from_user.username else ""

        res = await request_aba_payway_purchase(
            chat_id=chat_id,
            merchant_id=ABA_MERCHANT_ID,
            public_key=ABA_API_KEY,
            payway_url=ABA_PAYWAY_URL,
            server_url=SERVER_URL,
            amount="2000",
            first_name=first_name,
            username=username
        )

        tran_id = res.get("tran_id", "")
        req_time = res.get("req_time", "")
        qr_image_b64 = res.get("qr_image", "")
        checkout_url = f"{SERVER_URL.rstrip('/')}/donate_checkout?tran_id={tran_id}&amount=2000&req_time={req_time}&chat_id={chat_id}"
        open_app_url = f"{SERVER_URL.rstrip('/')}/open_abapay?tran_id={tran_id}"

        builder = InlineKeyboardBuilder()
        builder.button(text="📲 បើក App ABA Bank ដើម្បីទូទាត់", url=open_app_url)
        builder.button(text="🌐 ទំព័រ Web Checkout", url=checkout_url)
        builder.button(text="🏠 Menu", callback_data="cb_back_main")
        builder.adjust(1, 1, 1)

        message_text = (
            "🤖 <b>ចូលរួមគាំទ្រការអភិវឌ្ឍន៍ Smart AI Assistant</b> 🚀\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "ដើម្បីជួយឱ្យប្រព័ន្ធ <b>Smart AI Assistant</b> អាចបន្តដំណើរការ និងអភិវឌ្ឍមុខងារថ្មីៗកាន់តែឆ្លាតវៃសម្រាប់ឆ្នាំក្រោយ "
            "លោកអ្នកអាចចូលរួមបរិច្ចាគថវិកាចំនួន <b>2,000 ៛ ($0.50)</b> តាមរយៈ ABA Pay KHQR បាន។\n\n"
            "👇 <b>សូមស្កែន KHQR ខាងលើ ឬ ចុចប៊ូតុងខាងក្រោមដើម្បីទូទាត់៖</b>"
        )

        if qr_image_b64:
            try:
                clean_b64 = qr_image_b64.split(",")[-1] if "," in qr_image_b64 else qr_image_b64
                img_bytes = base64.b64decode(clean_b64)
                photo_file = types.BufferedInputFile(img_bytes, filename=f"aba_khqr_{tran_id}.png")
                await callback.message.answer_photo(
                    photo=photo_file,
                    caption=message_text,
                    parse_mode="HTML",
                    reply_markup=builder.as_markup()
                )
                return
            except Exception as img_err:
                logging.warning(f"Could not send KHQR photo in callback: {img_err}")

        try:
            await callback.message.reply(message_text, parse_mode="HTML", reply_markup=builder.as_markup())
        except Exception:
            await callback.message.answer(message_text, parse_mode="HTML", reply_markup=builder.as_markup())

    return router


