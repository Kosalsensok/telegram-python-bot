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

                caption_lower = message.caption.lower().strip() if message.caption else ""
                enhance_keywords = ["/enhance", "/unblur", "/hd", "កែឲ្យច្បាស់", "ធ្វើឲ្យច្បាស់", "ច្បាស់"]

                if any(kw in caption_lower for kw in enhance_keywords):
                    from services.image_gen_service import enhance_image_hd, IMAGE_CACHE
                    from keyboards.inline import get_enhanced_image_download_keyboard
                    import random, time

                    enhanced_bytes = enhance_image_hd(photo_bytes, sharpness_factor=2.4, contrast_factor=1.18)
                    seed = random.randint(100000, 999999)
                    cache_id = f"img_enh_{seed}_{int(time.time())}"
                    IMAGE_CACHE[cache_id] = {
                        "image_bytes": enhanced_bytes,
                        "prompt": "Enhanced Ultra HD Photo",
                        "optimized_prompt": "Ultra HD 4K Crystal Clear Sharpened Photo",
                        "width": 2048,
                        "height": 2048,
                        "created_at": time.time()
                    }

                    photo_file = types.BufferedInputFile(enhanced_bytes, filename=f"hd_enhanced_{seed}.jpg")
                    caption_text = (
                        "✨ <b>រូបភាពត្រូវបានកែប្រែទៅជា Ultra HD ច្បាស់ត្រជាក់ភ្នែក!</b>\n"
                        "<i>(Super-Resolution Unblur & HD Quality Enhancer)</i>\n\n"
                        "👇 <b>ទាញយករូបភាព HD JPG / PNG ខាងក្រោម៖</b>"
                    )
                    await message.reply_photo(
                        photo=photo_file,
                        caption=caption_text,
                        parse_mode="HTML",
                        reply_markup=get_enhanced_image_download_keyboard(cache_id)
                    )
                    return

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
