import logging
from html import escape
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response

router = Router(name="text_router")


def get_text_router(gemini_service: GeminiService, memory: ConversationMemory, db_service: DatabaseService = None) -> Router:
    """
    Construct text chat router with injected Gemini service, memory, and database service.
    """
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

        loading_msg = None
        try:
            # Show typing chat action safely
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except Exception as e:
                logging.warning(f"Could not send typing action: {e}")

            # Send Loading Message
            loading_msg = await message.reply("🤖 កំពុងគិត...")

            # Fetch user active mode
            active_mode = "general"
            if db_service:
                active_mode = await db_service.get_user_mode(user_id)

            # Fetch user conversation history
            history = await memory.get_history_async(user_id)

            # Generate AI response asynchronously with active mode
            ai_response = await gemini_service.generate_text_chat(user_prompt=user_text, history=history, mode=active_mode)


            # Record turn in memory
            await memory.add_user_message_async(user_id, user_text)
            await memory.add_assistant_message_async(user_id, ai_response)

            # Clean up loading message
            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass

            # Formats Markdown cleanly, splits long messages, and sends with HTML parse_mode
            await send_safe_response(message, ai_response)

        except Exception as e:
            logging.error(f"Error in text handler for user {user_id}: {e}", exc_info=True)
            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
            await message.reply("⚠️ មានបញ្ហាក្នុងការភ្ជាប់ទៅ AI Server។ សូមព្យាយាមម្តងទៀតបន្តិចក្រោយនេះ / ⚠️ The AI service is temporarily unavailable. Please try again.")

    return router
