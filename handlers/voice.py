import logging
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response

router = Router(name="voice_router")

DEFAULT_VOICE_PROMPT = (
    "🎙️ សូមស្តាប់សំឡេងនេះ ឆ្លើយតប និងពន្យល់ខ្លឹមសារជាភាសាខ្មែរ/អង់គ្លេសឱ្យបានច្បាស់លាស់។"
)


def get_voice_router(gemini_service: GeminiService, memory: ConversationMemory = None, db_service: DatabaseService = None) -> Router:
    """
    Construct voice router to process Telegram voice notes (.ogg) and audio files using Gemini Audio AI.
    """
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

        loading_msg = None
        try:
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except Exception:
                pass

            loading_msg = await message.reply("🎙️ កំពុងស្តាប់ និងវិភាគសំឡេង (Processing voice note)...", parse_mode="HTML")

            voice = message.voice or message.audio
            mime_type = "audio/ogg"
            if message.audio and message.audio.mime_type:
                mime_type = message.audio.mime_type
            elif message.voice and message.voice.mime_type:
                mime_type = message.voice.mime_type

            # Limit file size to 15MB for voice notes
            if voice.file_size and voice.file_size > 15 * 1024 * 1024:
                if loading_msg:
                    await loading_msg.delete()
                await message.reply("⚠️ File សំឡេងនេះមានទំហំធំពេក (លើសពី 15MB)។ / Voice file size exceeds limit (15MB).")
                return

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

            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass

            await send_safe_response(message, ai_response)

        except Exception as e:
            logging.error(f"Error processing voice for user {user_id}: {e}", exc_info=True)
            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
            await message.reply("⚠️ មិនអាចស្ដាប់ ឬដំណើរការសារសំឡេងនេះបានទេ។ សូមព្យាយាមម្តងទៀត! / Could not process voice note.", parse_mode="HTML")

    return router
