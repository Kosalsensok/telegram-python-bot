import logging
import asyncio
from html import escape
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.image_utils import process_image_bytes
from utils.memory import ConversationMemory
from utils.response_router import parse_ai_structured_response
from utils.solution_card import save_solution_cache, generate_short_solution_id
from utils.localization import format_image_analysis_result
from keyboards.inline import (
    get_image_result_contextual_keyboard,
    get_math_answer_keyboard,
    get_error_retry_keyboard
)
from config import MAX_IMAGE_SIZE_MB

DEFAULT_IMAGE_PROMPT = "សូមពិពណ៌នា និងវិភាគរូបភាពនេះឱ្យបានច្បាស់។ ប្រសិនបើមានអត្ថបទ ឬរូបមន្ត សូមអាន និងពន្យល់ផង។"

def get_image_router(gemini_service: GeminiService, memory: ConversationMemory = None, db_service: DatabaseService = None) -> Router:
    """
    Construct image vision router with fast loading message edit and structured image analysis output.
    """
    router = Router(name="image_router")

    @router.message(F.photo)
    async def handle_photo_message(message: types.Message):
        """
        Handle photo uploads with immediate status message and fast async processing.
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

        # Step 1: Send action
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        except Exception as e:
            logging.warning(f"Could not send chat action: {e}")

        # Step 2: Immediately send loading status message
        loading_msg = await message.answer("🔍 កំពុងវិភាគរូបភាព...\nសូមរង់ចាំបន្តិច។", parse_mode="HTML")

        try:
            # Step 3: Download and validate photo
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)
            photo_bytes_io = await message.bot.download_file(file_info.file_path)
            photo_bytes = photo_bytes_io.read()

            pil_image = process_image_bytes(photo_bytes, max_size_mb=MAX_IMAGE_SIZE_MB)
            prompt = message.caption.strip() if message.caption else DEFAULT_IMAGE_PROMPT

            active_mode = "general"
            if db_service:
                active_mode = await db_service.get_user_mode(user_id)

            # Step 4: Process vision AI asynchronously with timeout
            vision_response = await asyncio.wait_for(
                gemini_service.generate_vision_chat(image=pil_image, prompt=prompt, mode=active_mode),
                timeout=55.0
            )

            if memory:
                await memory.add_user_message_async(user_id, prompt, message_type="image")
                await memory.add_assistant_message_async(user_id, vision_response, message_type="text")

            # Step 5: Parse structured output and format clean result
            parsed_data = parse_ai_structured_response(vision_response, prompt)
            
            detected_type = parsed_data.get("image_type") or parsed_data.get("topic") or "Screenshot / Document"
            observation = parsed_data.get("observation") or parsed_data.get("summary") or "បានរកឃើញអត្ថបទ ឬរូបភាព"
            answer = parsed_data.get("answer") or parsed_data.get("solution_summary") or vision_response
            suggestion = parsed_data.get("suggestion") or parsed_data.get("tips") or ""

            formatted_result = format_image_analysis_result(
                detected_type=detected_type,
                observation=observation,
                answer=answer,
                suggestion=suggestion
            )

            solution_id = generate_short_solution_id()
            save_solution_cache(solution_id, vision_response, parsed_data, user_id, message.chat.id)

            keyboard = get_image_result_contextual_keyboard(solution_id)

            # Step 6: Edit the same status message into final result
            try:
                await loading_msg.edit_text(formatted_result, parse_mode="HTML", reply_markup=keyboard)
            except Exception:
                await message.reply(formatted_result, parse_mode="HTML", reply_markup=keyboard)

        except asyncio.TimeoutError:
            error_msg = (
                "⚠️ <b>មិនអាចបំពេញសំណើបាន</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ ការវិភាគរូបភាពប្រើពេលយូរពេក។ សូមព្យាយាមម្តងទៀត!"
            )
            try:
                await loading_msg.edit_text(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())
            except Exception:
                await message.reply(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())

        except ValueError as ve:
            logging.warning(f"Image validation warning for user {user_id}: {ve}")
            error_msg = (
                "⚠️ <b>មិនអាចបំពេញសំណើបាន</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ រូបភាពមិនត្រឹមត្រូវ ឬមានទំហំធំពេក (អតិបរមា 10MB)។"
            )
            try:
                await loading_msg.edit_text(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())
            except Exception:
                await message.reply(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())

        except Exception as e:
            logging.error(f"Error processing image for user {user_id}: {e}", exc_info=True)
            error_msg = (
                "⚠️ <b>មិនអាចបំពេញសំណើបាន</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ មិនអាចដំណើរការរូបភាពនេះបានទេ។ សូមពិនិត្យរូបភាព ហើយព្យាយាមម្តងទៀត!"
            )
            try:
                await loading_msg.edit_text(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())
            except Exception:
                await message.reply(error_msg, parse_mode="HTML", reply_markup=get_error_retry_keyboard())

    return router
