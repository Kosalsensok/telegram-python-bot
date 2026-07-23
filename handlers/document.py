import logging
from html import escape
from aiogram import Router, types, F
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response

router = Router(name="document_router")

SUPPORTED_EXTENSIONS = {
    ".txt", ".py", ".json", ".csv", ".md", ".js", ".html", 
    ".css", ".cpp", ".c", ".java", ".sql", ".xml", ".log", 
    ".yaml", ".yml", ".php", ".sh", ".bat", ".rs", ".go"
}

DEFAULT_DOC_PROMPT = (
    "សូមពិនិត្យ វិភាគ និងពន្យល់អំពីខ្លឹមសារ ឬ Code នៅក្នុង File/Document នេះជាភាសាខ្មែរឱ្យបានច្បាស់លាស់។"
)


def get_document_router(gemini_service: GeminiService, memory: ConversationMemory = None, db_service: DatabaseService = None) -> Router:
    """
    Construct document router to process code files and text documents.
    """
    @router.message(F.document)
    async def handle_document_message(message: types.Message):
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

        document = message.document
        file_name = document.file_name or "document.txt"
        file_ext = "." + file_name.split(".")[-1].lower() if "." in file_name else ""

        # Limit file size to 10MB
        if document.file_size and document.file_size > 10 * 1024 * 1024:
            await message.answer("⚠️ File នេះមានទំហំធំពេក (លើសពី 10MB)។ សូមផ្ញើ File ដែលមានទំហំតូចជាងនេះ! / File size exceeds limit (10MB).")
            return

        loading_msg = None
        try:
            # Show typing chat action safely
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except Exception as e:
                logging.warning(f"Could not send typing action: {e}")

            loading_msg = await message.answer(f"📄 កំពុងអាន និងវិភាគ <b>{escape(file_name)}</b>...", parse_mode="HTML")

            # Download document
            file_info = await message.bot.get_file(document.file_id)
            file_bytes_io = await message.bot.download_file(file_info.file_path)
            file_bytes = file_bytes_io.read()

            caption = message.caption.strip() if message.caption else DEFAULT_DOC_PROMPT

            # Get user active mode
            active_mode = "general"
            if db_service:
                active_mode = await db_service.get_user_mode(user_id)

            is_pdf = file_ext == ".pdf" or (document.mime_type and "pdf" in document.mime_type.lower())
            is_image_doc = document.mime_type and document.mime_type.startswith("image/")

            if is_pdf or is_image_doc:
                mime = document.mime_type or ("application/pdf" if is_pdf else "image/png")
                doc_prompt = f"File Name: {file_name}\nTask: {caption}"
                ai_response = await gemini_service.generate_document_chat(
                    file_bytes=file_bytes,
                    mime_type=mime,
                    prompt=doc_prompt,
                    mode=active_mode
                )
            else:
                # Decode text content for code and plain text files
                try:
                    content_text = file_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    content_text = file_bytes.decode("latin-1", errors="ignore")

                # Limit text content length to 15,000 characters for optimal processing
                if len(content_text) > 15000:
                    content_text = content_text[:15000] + "\n...[File Content Truncated for Analysis]"

                full_prompt = (
                    f"📁 <b>File Name:</b> <code>{escape(file_name)}</code>\n\n"
                    f"<b>Question/Task:</b> {caption}\n\n"
                    f"<b>File Content:</b>\n```\n{content_text}\n```"
                )
                ai_response = await gemini_service.generate_text_chat(user_prompt=full_prompt, mode=active_mode)


            # Add to memory if available
            if memory:
                await memory.add_user_message_async(user_id, f"[Document: {file_name}] {caption}")
                await memory.add_assistant_message_async(user_id, ai_response)

            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass

            await send_safe_response(message, ai_response)

        except Exception as e:
            logging.error(f"Error processing document {file_name} for user {user_id}: {e}", exc_info=True)
            if loading_msg:
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
            await message.answer(f"⚠️ មិនអាចវិភាគ File <b>{escape(file_name)}</b> បានទេ។ សូមពិនិត្យ File ហើយព្យាយាមម្តងទៀត!", parse_mode="HTML")

    return router
