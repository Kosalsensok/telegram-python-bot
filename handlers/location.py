import logging
import html
from urllib.parse import quote_plus
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from utils.memory import ConversationMemory
from utils.message_utils import send_safe_response

LOCATION_PROMPT_TEMPLATE = (
    "🗺️ **ភារកិច្ចរបស់អ្នក៖ បង្ហាញផ្លូវ ទីតាំង និងទិសដៅ (Navigation & Direction Expert):**\n\n"
    "អ្នកប្រើប្រាស់បានចែករំលែកទីតាំង GPS ដូចខាងក្រោម៖\n"
    "- និយាមកា (Latitude, Longitude): {lat}, {lon}\n\n"
    "សូមវិភាគទីតាំងនេះ ហើយផ្តល់ព័ត៌មានយ៉ាងច្បាស់លាស់ និងមានប្រយោជន៍ជាភាសាខ្មែរ 🇰🇭៖\n"
    "1. **ទីតាំង & តំបន់ (Identified Location/Area):** ប្រាប់ពីឈ្មោះតំបន់ ក្រុង ឬខេត្ត និងកន្លែងសំខាន់ៗដែលនៅជិត (Landmarks)។\n"
    "2. **ការណែនាំផ្លូវ និងទិសដៅ (Navigation & Travel Directions):** ប្រាប់ពីផ្លូវសំខាន់ៗជុំវិញ និងរបៀបធ្វើដំណើរទៅកាន់ទីប្រជុំជន ឬកន្លែងល្បីៗ។\n"
    "3. **កន្លែងសំខាន់ៗជិតៗនោះ (Nearby Points of Interest):** ផ្សារ, មន្ទីរពេទ្យ, ស្ថាប័ន ឬតំបន់ទេសចរណ៍ដែលនៅជិតទីតាំងនេះ។\n\n"
    "សូមរៀបចំទម្រង់ឆ្លើយតបឱ្យមានសោភ័ណភាព ងាយស្រួលមើល និងច្បាស់លាស់បំផុត!"
)

def get_location_keyboard(lat: float, lon: float, place_name: str = "") -> InlineKeyboardMarkup:
    """
    Generates interactive Telegram inline buttons for Google Maps Navigation and Apple Maps.
    """
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    navigation_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
    apple_maps_url = f"https://maps.apple.com/?daddr={lat},{lon}"

    buttons = [
        [
            InlineKeyboardButton(text="🗺️ បើកមើលក្នុង Google Maps", url=google_maps_url),
            InlineKeyboardButton(text="🚗 នាំផ្លូវ (Navigation)", url=navigation_url)
        ],
        [
            InlineKeyboardButton(text="🍎 បើកក្នុង Apple Maps", url=apple_maps_url)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_location_router(gemini_service: GeminiService, memory: ConversationMemory = None, db_service: DatabaseService = None) -> Router:
    """
    Construct location router to handle Telegram GPS Location messages and Venue shares.
    Provides precise Google Maps links, navigation routing, nearby landmarks, and AI analysis.
    """
    router = Router(name="location_router")

    @router.message(F.location | F.venue)
    async def handle_location_message(message: types.Message):
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

        loc = message.location
        if not loc:
            return

        lat = loc.latitude
        lon = loc.longitude

        try:
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="find_location")
            except Exception:
                pass

            prompt = LOCATION_PROMPT_TEMPLATE.format(lat=lat, lon=lon)
            active_mode = "general"
            if db_service:
                active_mode = await db_service.get_user_mode(user_id)

            ai_response = await gemini_service.generate_text_chat(
                user_prompt=prompt,
                mode=active_mode
            )

            if memory:
                await memory.add_user_message_async(user_id, f"[📍 Location Shared: {lat}, {lon}]")
                await memory.add_assistant_message_async(user_id, ai_response)

            venue_title = ""
            if message.venue and message.venue.title:
                venue_title = f"<b>📍 ទីតាំងចែករំលែក: {html.escape(message.venue.title)}</b>\n"

            formatted_response = (
                f"🗺️ <b>ប្រព័ន្ធស្វែងរកទីតាំង & បង្ហាញផ្លូវ (Navigation & Direction)</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{venue_title}"
                f"📍 <b>កូអ័រដោនេ GPS:</b> <code>{lat:.6f}, {lon:.6f}</code>\n\n"
                f"{ai_response}"
            )

            keyboard = get_location_keyboard(lat, lon)
            await send_safe_response(message, formatted_response, reply_markup=keyboard)

        except Exception as e:
            logging.error(f"Error handling location for user {user_id}: {e}", exc_info=True)
            fallback_text = (
                f"🗺️ <b>ទីតាំង GPS ដែលបានទទួល:</b> <code>{lat:.6f}, {lon:.6f}</code>\n\n"
                f"លោកអ្នកអាចចុចប៊ូតុងខាងក្រោមដើម្បីមើលទីតាំង ឬនាំផ្លូវតាម Google Maps បានភ្លាមៗ!"
            )
            keyboard = get_location_keyboard(lat, lon)
            await message.reply(fallback_text, parse_mode="HTML", reply_markup=keyboard)

    return router
