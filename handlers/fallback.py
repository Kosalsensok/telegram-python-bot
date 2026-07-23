from aiogram import Router, types, F
from services.db_service import DatabaseService

def get_fallback_router(db_service: DatabaseService = None) -> Router:
    """
    Construct fallback router with injected database service.
    """
    router = Router(name="fallback_router")

    @router.message(F.video | F.sticker | F.contact | F.location | F.animation)
    async def handle_unsupported_messages(message: types.Message):
        """
        Catch-all handler for media types not yet supported for direct text conversion (voice, video, stickers).
        """
        if message.from_user and db_service:
            await db_service.save_or_update_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code or "en"
            )

        unsupported_notice = (
            "ℹ️ <b>ប្រភេទសារនេះមិនទាន់ត្រូវបានគាំទ្រជាផ្លូវការទេ!</b>\n\n"
            "✨ <b>បច្ចុប្បន្ន Bot គាំទ្រ៖</b>\n"
            "1. 💬 <b>សារអក្សរ</b> (Text questions in Khmer & English)\n"
            "2. 🖼 <b>រូបភាព</b> (Photos with optional questions in caption)\n"
            "3. 📄 <b>Code & Document Files</b> (.py, .txt, .json, .csv, .md, .html, .js, .cpp, .sql, etc.)\n\n"
            "👉 សូមផ្ញើសំណួរជាអក្សរ, ផ្ញើរូបភាព ឬ ផ្ញើ File Code មកកាន់ Bot!"
        )
        await message.answer(unsupported_notice, parse_mode="HTML")

    return router

