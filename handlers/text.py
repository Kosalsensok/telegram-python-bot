import logging
import os
from html import escape
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response
from utils.response_router import parse_ai_structured_response, format_telegram_html
from utils.solution_card import save_solution_cache, generate_short_solution_id
from keyboards.inline import (
    get_mode_inline_keyboard,
    get_requirements_navigation_keyboard,
    get_code_answer_keyboard,
    get_math_answer_keyboard
)
from config import RENDER_EXTERNAL_URL

def get_text_router(gemini_service: GeminiService, memory: ConversationMemory, db_service: DatabaseService = None) -> Router:
    """
    Construct text chat router with injected Gemini service, memory, and database service.
    Implements Response Type Router, structured AI parsing, short solution caching, and Layer 1 summary message.
    """
    router = Router(name="text_router")

    @router.message(F.text & ~F.text.startswith("/"))
    async def handle_text_message(message: types.Message):
        """
        Handle incoming user text messages.
        """
        if message.from_user:
            if db_service:
                await db_service.save_or_update_user(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    language_code=message.from_user.language_code or "en"
                )
            user_id = message.from_user.id
        else:
            user_id = message.chat.id

        user_text = message.text.strip()
        if not user_text:
            return

        # Reply Keyboard Fast Action Intercepts
        if "ជ្រើសរើស Mode" in user_text:
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
            await message.answer(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(current_mode))
            return

        if "បង្កើតរូបភាព" in user_text:
            msg = (
                "🎨 <b>បង្កើតរូបភាព AI ឥតដែនកំណត់ (Unlimited HD AI Image Generator):</b>\n\n"
                "👉 <b>របៀបប្រើប្រាស់ / How to use:</b>\n"
                "<code>/image [ការពិពណ៌នារូបភាពជាភាសាខ្មែរ ឬ English]</code>\n\n"
                "<b>ឧទាហរណ៍៖</b>\n"
                "• <code>/image 16:9 នាគរាជខ្មែរ ហោះលើប្រាសាទអង្គរវត្ត ពណ៌មាស 4k</code>\n"
                "• <code>/image 9:16 futuristic Phnom Penh city in 2050, 8k resolution</code>"
            )
            await message.answer(msg, parse_mode="HTML")
            return

        if "វិភាគរូបភាព" in user_text:
            msg = (
                "🖼 <b>សូមផ្ញើរូបភាព ហើយសរសេរសំណួរនៅក្នុង Caption៖</b>\n\n"
                "1. ចុច <b>Attach File / Photo</b> ក្នុង Telegram\n"
                "2. ជ្រើសរើសរូបភាព ឬ Screenshot របស់អ្នក\n"
                "3. វាយសំណួររបស់អ្នកនៅក្នុងប្រអប់ <b>Caption</b>\n"
                "4. ចុច <b>Send</b> ជាការស្រេច!"
            )
            await message.answer(msg, parse_mode="HTML")
            return

        if "របៀបសួរសំណួរ" in user_text or "Help" in user_text:
            help_text = (
                "📖 <b>ការណែនាំពីរបៀបប្រើប្រាស់ / Usage Guide:</b>\n\n"
                "<b>1. 💬 សួរសំណួរជាអក្សរ (Text Chat):</b>\n"
                "• វាយសំណួរជាភាសាខ្មែរ ឬអង់គ្លេស រួចផ្ញើចេញ.\n\n"
                "<b>2. 🖼 ផ្ញើរូបភាពវិភាគ (Vision AI):</b>\n"
                "• ផ្ញើរូបភាពលំហាត់ សមរភូមិ កូដ ឬសំណួរ រួចដាក់ Caption.\n\n"
                "<b>3. 🎨 បង្កើតរូបភាព AI (/image /imagine):</b>\n"
                "• វាយ <code>/image [prompt]</code> ដើម្បីបង្កើតរូបភាព HD 4K.\n\n"
                "<b>4. 🎯 7 Specialized AI Operating Modes (/mode):</b>\n"
                "• ជ្រើសរើស Mode តាមតម្រូវការការងាររបស់អ្នក!"
            )
            await message.answer(help_text, parse_mode="HTML")
            return

        if "ស្ថិតិ" in user_text:
            user_stats = {"total_messages": 0, "text_count": 0, "image_count": 0}
            if db_service:
                user_stats = await db_service.get_user_stats(user_id)
            stats_text = (
                "📊 <b>ស្ថិតិផ្ទាល់ខ្លួនរបស់អ្នក / Your Usage Stats</b>\n\n"
                f"💬 <b>សំណួរសរុប (Total Questions):</b> {user_stats.get('total_messages', 0)}\n"
                f"📝 <b>អត្ថបទ (Text):</b> {user_stats.get('text_count', 0)}\n"
                f"🖼️ <b>រូបភាព (Images):</b> {user_stats.get('image_count', 0)}"
            )
            await message.answer(stats_text, parse_mode="HTML")
            return

        if "លុប History" in user_text:
            cleared_db = False
            if db_service:
                cleared_db = await db_service.clear_history(user_id)
            cleared_cache = memory.clear_history(user_id) if memory else False
            if cleared_cache or cleared_db:
                await message.answer("🧹 <b>ប្រវត្តិសន្ទនារបស់អ្នកត្រូវបានលុបរួចរាល់!</b>", parse_mode="HTML")
            else:
                await message.answer("ℹ️ មិនមានប្រវត្តិសន្ទនាដែលត្រូវលុបទេ។", parse_mode="HTML")
            return

        loading_msg = None
        try:
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except Exception as e:
                logging.warning(f"Could not send typing action: {e}")

            from utils.thinking_animation import DynamicThinkingAnimation, TEXT_THINKING_STEPS

            async with DynamicThinkingAnimation(message, TEXT_THINKING_STEPS) as anim:
                active_mode = "general"
                if db_service:
                    active_mode = await db_service.get_user_mode(user_id)

                history = await memory.get_history_async(user_id)
                ai_response = await gemini_service.generate_text_chat(user_prompt=user_text, history=history, mode=active_mode)

                await memory.add_user_message_async(user_id, user_text)
                await memory.add_assistant_message_async(user_id, ai_response)

                # Parse AI response into structured JSON schema
                parsed_data = parse_ai_structured_response(ai_response, user_prompt=user_text)
                response_type = parsed_data.get("response_type", "general_answer")

                # Generate short solution ID and cache in memory with TTL
                solution_id = generate_short_solution_id()
                save_solution_cache(
                    solution_id=solution_id,
                    raw_text=ai_response,
                    parsed_data=parsed_data,
                    telegram_user_id=user_id,
                    chat_id=message.chat.id
                )

                # Build Mini App URL if configured
                mini_app_url = ""
                if RENDER_EXTERNAL_URL:
                    base_url = RENDER_EXTERNAL_URL.rstrip('/')
                    mini_app_url = f"{base_url}/answer/{solution_id}"

                # Format Layer 1 Telegram Native summary response
                summary_html = format_telegram_html(parsed_data)

                # Attach keyboard matching response type
                if response_type == "code_answer":
                    keyboard = get_code_answer_keyboard(solution_id, mini_app_url)
                elif response_type in ["mathematics", "chemistry", "physics"]:
                    keyboard = get_math_answer_keyboard(solution_id, mini_app_url)
                else:
                    keyboard = get_requirements_navigation_keyboard(solution_id, current_page=1, total_pages=13, mini_app_url=mini_app_url)

                await message.reply(summary_html, parse_mode="HTML", reply_markup=keyboard)

        except Exception as e:
            logging.error(f"Error in text handler for user {user_id}: {e}", exc_info=True)
            await message.reply("⚠️ មានបញ្ហាក្នុងការភ្ជាប់ទៅ AI Server។ សូមព្យាយាមម្តងទៀតបន្តិចក្រោយនេះ / ⚠️ The AI service is temporarily unavailable. Please try again.")

    return router
