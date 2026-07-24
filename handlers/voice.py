import logging
import os
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response
from utils.response_router import (
    parse_ai_structured_response,
    format_telegram_html
)
from utils.solution_card import save_solution_cache, generate_short_solution_id
from keyboards.inline import get_requirements_navigation_keyboard
from config import RENDER_EXTERNAL_URL

DEFAULT_VOICE_PROMPT = (
    "🎙️ សូមស្តាប់សំឡេងនេះ ឆ្លើយតប និងពន្យល់ខ្លឹមសារជាភាសាខ្មែរ/អង់គ្លេសឱ្យបានច្បាស់លាស់។"
)


def get_voice_router(gemini_service: GeminiService, memory: ConversationMemory = None, db_service: DatabaseService = None) -> Router:
    """
    Construct voice router to process Telegram voice notes (.ogg) and audio files using Gemini Audio AI.
    Integrates Response Type Router, structured AI response, short solution caching, and Layer 1 summary replies.
    """
    router = Router(name="voice_router")

    @router.message(F.voice | F.audio)
    async def handle_voice_message(message: types.Message):
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

        voice = message.voice or message.audio
        mime_type = "audio/ogg"
        if message.audio and message.audio.mime_type:
            mime_type = message.audio.mime_type
        elif message.voice and message.voice.mime_type:
            mime_type = message.voice.mime_type

        # Limit file size to 15MB for voice notes
        if voice.file_size and voice.file_size > 15 * 1024 * 1024:
            await message.reply("⚠️ File សំឡេងនេះមានទំហំធំពេក (លើសពី 15MB)។ / Voice file size exceeds limit (15MB).")
            return

        try:
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except Exception:
                pass

            from utils.thinking_animation import DynamicThinkingAnimation, VOICE_THINKING_STEPS

            async with DynamicThinkingAnimation(message, VOICE_THINKING_STEPS) as anim:
                file_info = await message.bot.get_file(voice.file_id)
                file_bytes_io = await message.bot.download_file(file_info.file_path)
                voice_bytes = file_bytes_io.read()

                caption = message.caption.strip() if message.caption else DEFAULT_VOICE_PROMPT

                active_mode = "general"
                if db_service:
                    active_mode = await db_service.get_user_mode(user_id)

                ai_response = await gemini_service.generate_audio_chat(
                    file_bytes=voice_bytes,
                    mime_type=mime_type,
                    prompt=caption,
                    mode=active_mode
                )

                if memory:
                    await memory.add_user_message_async(user_id, "[Voice Message]")
                    await memory.add_assistant_message_async(user_id, ai_response)

                parsed_data = parse_ai_structured_response(ai_response, "Voice Note Analysis")
                solution_id = generate_short_solution_id()
                save_solution_cache(solution_id, ai_response, parsed_data, user_id, message.chat.id)

                mini_app_url = ""
                if RENDER_EXTERNAL_URL:
                    base_url = RENDER_EXTERNAL_URL.rstrip('/')
                    mini_app_url = f"{base_url}/answer/{solution_id}"

                formatted_html = format_telegram_html(parsed_data)
                keyboard = get_requirements_navigation_keyboard(solution_id, current_page=1, total_pages=13, mini_app_url=mini_app_url)

            await send_safe_response(message, formatted_html, reply_markup=keyboard)

        except Exception as e:
            logging.error(f"Error processing voice for user {user_id}: {e}", exc_info=True)
            await message.reply("⚠️ មិនអាចស្ដាប់ ឬដំណើរការសារសំឡេងនេះបានទេ។ សូមព្យាយាមម្តងទៀត! / Could not process voice note.", parse_mode="HTML")

    return router
