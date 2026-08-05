import logging
import asyncio
from html import escape
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response, markdown_to_telegram_html, split_html_message
from utils.response_router import parse_ai_structured_response, format_telegram_html, detect_response_type_from_text
from utils.solution_card import save_solution_cache, generate_short_solution_id
from utils.localization import format_ai_result, get_str
from config import RENDER_EXTERNAL_URL
from keyboards.inline import (
    get_welcome_inline_keyboard,
    get_mode_inline_keyboard,
    get_greeting_inline_keyboard,
    get_stt_banner_keyboard,
    get_ai_result_contextual_keyboard,
    get_error_retry_keyboard
)

from utils.thinking_animation import DynamicThinkingAnimation, TEXT_THINKING_STEPS

def get_text_router(gemini_service: GeminiService, memory: ConversationMemory, db_service: DatabaseService = None) -> Router:
    """
    Construct text chat router with Fast AI Request Workflow and Loading State Editing.
    """
    router = Router(name="text_router")

    @router.message(F.text & ~F.text.startswith("/"))
    async def handle_text_message(message: types.Message):
        """
        Handle incoming user text messages with fast status message edit.
        """
        if message.from_user:
            if db_service:
                asyncio.create_task(db_service.save_or_update_user(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    language_code=message.from_user.language_code or "en"
                ))
            user_id = message.from_user.id
        else:
            user_id = message.chat.id

        user_text = message.text.strip()
        if not user_text:
            return

        # 1. Fast Intercept for Greetings
        if detect_response_type_from_text("", user_prompt=user_text) == "greeting":
            greeting_html = format_telegram_html({"response_type": "greeting"})
            await message.answer(greeting_html, parse_mode="HTML", reply_markup=get_greeting_inline_keyboard())
            return

        # 2. Fast Intercepts for Keyword Commands
        if "ជ្រើសរើស Mode" in user_text or "AI Modes" in user_text:
            current_mode = "general"
            if db_service:
                current_mode = await db_service.get_user_mode(user_id)
            mode_text = (
                "🎯 <b>ជ្រើសរើស AI Mode</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "សូមជ្រើសរើស AI Mode ដែលសមស្របនឹងសំណួររបស់អ្នក៖"
            )
            await message.answer(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(current_mode))
            return

        if "វិភាគរូបភាព" in user_text:
            from keyboards.inline import get_image_analysis_banner_keyboard
            banner_text = (
                "🖼 <b>វិភាគរូបភាព</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "សូមផ្ញើរូបភាពដែលអ្នកចង់ឱ្យ AI វិភាគ។\n\n"
                "AI អាចសម្គាល់៖\n"
                "• Screenshot\n• ឯកសារ\n• អត្ថបទ\n• តារាង\n• រូបមន្ត\n• ផលិតផល"
            )
            await message.answer(banner_text, parse_mode="HTML", reply_markup=get_image_analysis_banner_keyboard())
            return

        if "សំឡេងទៅជាអក្សរ" in user_text or "Speech-to-Text" in user_text:
            if db_service:
                await db_service.set_user_mode(user_id, "speech_to_text")
            mini_app_url = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else ""
            stt_text = (
                "🎙️ <b>មុខងារបម្លែងសំឡេងទៅជាអក្សរ (Speech-to-Text)</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "✨ <b>គាំទ្រភាសាខ្មែរ 🇰🇭 និងភាសាអង់គ្លេស 🇺🇸 យ៉ាងត្រឹមត្រូវខ្ពស់!</b>\n\n"
                "👉 <b>របៀបប្រើប្រាស់៖</b>\n"
                "1. 🎤 <b>និយាយសារសំឡេង (Voice Note):</b> ចុចលើរូប <b>មេក្រូ 🎤</b> (នៅខាងស្តាំក្រោមនៃប្រអប់សារ) រួចនិយាយសារសំឡេង\n"
                "2. 🌐 <b>ថតសំឡេងក្នុង Mini App:</b> ចុចប៊ូតុង <i>\"🎙️ បើក Mini App ថតសំឡេង\"</i> ខាងក្រោម ដើម្បីថត និងបម្លែងសំឡេងផ្សាយផ្ទាល់\n"
                "3. 📁 <b>ផ្ញើ File សំឡេង:</b> ផ្ញើ File សំឡេង (.mp3, .m4a, .wav, .ogg) ចូលក្នុងឆាតនេះ\n\n"
                "⚡ Bot នឹងបម្លែងសំឡេងទៅជាអក្សរ និងវិភាគឆ្លើយតបយ៉ាងក្បោះក្បាយភ្លាមៗ!"
            )
            await message.answer(stt_text, parse_mode="HTML", reply_markup=get_stt_banner_keyboard(mini_app_url))
            return

        if "របៀបសួរសំណួរ" in user_text or "Help" in user_text:
            help_text = (
                "ℹ️ <b>ជំនួយ និងការណែនាំ</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "<b>1. 💬 សួរសំណួរ AI:</b> វាយសំណួរជាភាសាខ្មែរ ឬ English រួចផ្ញើចេញ\n"
                "<b>2. 🖼 វិភាគរូបភាព:</b> ផ្ញើរូបភាពលំហាត់ សមរភូមិ ឬអត្ថបទ\n"
                "<b>3. 🎯 AI Modes:</b> ប្តូរ Mode តាមមុខវិជ្ជា\n"
                "<b>4. 🌐 Mini App:</b> ប្រើប្រាស់ Mini App"
            )
            await message.answer(help_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())
            return

        # 3. Fast AI Workflow Implementation
        # Step A: Send typing action
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        except Exception as e:
            logging.warning(f"Could not send typing action: {e}")

        # Step B: Immediately start animated loading status message
        anim = DynamicThinkingAnimation(message, TEXT_THINKING_STEPS, interval=0.9)
        loading_msg = await anim.start()

        # Step C: Start AI request asynchronously with strict timeout
        try:
            active_mode = "general"
            user_lang = "km"
            if db_service:
                active_mode = await db_service.get_user_mode(user_id)
                user_lang = await db_service.get_user_language(user_id)

            history = memory.get_history(user_id) if memory else []

            # 45-second timeout for AI request
            ai_response = await asyncio.wait_for(
                gemini_service.generate_text_chat(
                    user_prompt=user_text,
                    history=history,
                    mode=active_mode
                ),
                timeout=45.0
            )

            await anim.stop()

            if memory:
                await memory.add_user_message_async(user_id, user_text)
                await memory.add_assistant_message_async(user_id, ai_response)

            # Parse structured output and format clean result
            parsed_data = parse_ai_structured_response(ai_response, user_text)
            
            res_type = parsed_data.get("response_type", "general_answer")
            if res_type in ["code_answer", "software_requirements", "project_prototype", "system_architecture", "database_design", "api_design", "mathematics", "physics", "chemistry", "speech_to_text", "stt"]:
                formatted_html = format_telegram_html(parsed_data)
            else:
                title = parsed_data.get("topic") or parsed_data.get("title") or user_text[:35]
                answer = parsed_data.get("answer") or parsed_data.get("solution_summary") or ai_response
                explanation = parsed_data.get("explanation") or parsed_data.get("details") or ""
                tips = parsed_data.get("tips") or parsed_data.get("recommendation") or ""

                formatted_result = format_ai_result(
                    title=title,
                    answer=answer,
                    explanation=explanation,
                    tips=tips,
                    header_title="SMART AI ASSISTANT"
                )
                formatted_html = markdown_to_telegram_html(formatted_result)

            solution_id = generate_short_solution_id()
            save_solution_cache(solution_id, ai_response, parsed_data, user_id, message.chat.id)

            keyboard = get_ai_result_contextual_keyboard(solution_id)

            chunks = split_html_message(formatted_html, max_length=3800)

            # Step D: Edit the same loading message into the result
            if chunks:
                try:
                    await loading_msg.edit_text(chunks[0], parse_mode="HTML", reply_markup=keyboard if len(chunks) == 1 else None)
                    for chunk in chunks[1:]:
                        current_markup = keyboard if chunk == chunks[-1] else None
                        await message.reply(chunk, parse_mode="HTML", reply_markup=current_markup)
                except Exception as edit_err:
                    logging.warning(f"edit_text failed for user {user_id}, falling back to send_safe_response: {edit_err}")
                    await send_safe_response(message, formatted_html, reply_markup=keyboard)



        except asyncio.TimeoutError:
            error_msg = (
                "⚠️ <b>មិនអាចបំពេញសំណើបាន</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ ការឆ្លើយតបពី AI ប្រើពេលយូរពេក។ សូមព្យាយាមម្តងទៀត!"
            )
            try:
                await loading_msg.edit_text(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())
            except Exception:
                await message.answer(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())

        except Exception as e:
            logging.error(f"Error handling AI text request for user {user_id}: {e}", exc_info=True)
            error_msg = (
                "⚠️ <b>មិនអាចបំពេញសំណើបាន</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ មានបញ្ហាបច្ចេកទេសមួយបានកើតឡើង។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ។"
            )
            try:
                await loading_msg.edit_text(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())
            except Exception:
                await message.answer(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())

    return router
