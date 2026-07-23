import logging
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.image_utils import process_image_bytes
from utils.message_utils import send_safe_response
from utils.memory import ConversationMemory
from config import MAX_IMAGE_SIZE_MB

DEFAULT_IMAGE_PROMPT = (
    "សូមពិពណ៌នា និងវិភាគរូបភាពនេះឱ្យបានច្បាស់។ ប្រសិនបើមានអត្ថបទ សូមអាន និងពន្យល់អត្ថបទសំខាន់ៗផង។"
)


def get_image_router(gemini_service: GeminiService, memory: ConversationMemory = None, db_service: DatabaseService = None) -> Router:
    """
    Construct image vision router with injected GeminiService and DatabaseService.
    """
    router = Router(name="image_router")

    @router.message(F.photo)
    async def handle_photo_message(message: types.Message):
        """
        Handle photo uploads with optional text caption.
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

        loading_msg = None
        try:
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except Exception as e:
                logging.warning(f"Could not send typing action: {e}")

            from utils.thinking_animation import DynamicThinkingAnimation, VISION_THINKING_STEPS

            async with DynamicThinkingAnimation(message, VISION_THINKING_STEPS) as anim:
                photo = message.photo[-1]
                file_info = await message.bot.get_file(photo.file_id)
                photo_bytes_io = await message.bot.download_file(file_info.file_path)
                photo_bytes = photo_bytes_io.read()

                pil_image = process_image_bytes(photo_bytes, max_size_mb=MAX_IMAGE_SIZE_MB)
                prompt = message.caption.strip() if message.caption else DEFAULT_IMAGE_PROMPT

                active_mode = "general"
                if db_service:
                    active_mode = await db_service.get_user_mode(user_id)

                vision_response = await gemini_service.generate_vision_chat(image=pil_image, prompt=prompt, mode=active_mode)

                if memory:
                    await memory.add_user_message_async(user_id, prompt, message_type="image")
                    await memory.add_assistant_message_async(user_id, vision_response, message_type="text")

            await send_safe_response(message, vision_response)

        except ValueError as ve:
            logging.warning(f"Image validation warning for user {user_id}: {ve}")
            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
            await message.reply("⚠️ រូបភាពមិនត្រឹមត្រូវ ឬមានទំហំធំពេក។ សូមពិនិត្យរូបភាព ហើយព្យាយាមម្តងទៀត! / ⚠️ Invalid image or size limit exceeded.")

        except Exception as e:
            logging.error(f"Error processing image for user {user_id}: {e}", exc_info=True)
            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
            await message.reply("⚠️ មិនអាចដំណើរការរូបភាពនេះបានទេ។ សូមពិនិត្យរូបភាព ហើយព្យាយាមម្តងទៀត! / ⚠️ Failed to process image.")

    return router
