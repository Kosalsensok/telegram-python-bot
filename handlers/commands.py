import asyncio
import logging
import re
from html import escape
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from services.bot_profile_service import update_bot_profile
from keyboards.inline import (
    get_welcome_inline_keyboard, 
    get_language_inline_keyboard, 
    get_mode_inline_keyboard, 
    get_image_gen_inline_keyboard,
    get_image_download_keyboard
)
from utils.keyboard_utils import get_main_reply_keyboard
from utils.memory import ConversationMemory
from utils.user_count import format_user_count
from utils.message_utils import send_safe_response
from config import (
    BOT_DISPLAY_NAME,
    GEMINI_MODEL,
    STATS_PUBLIC,
    ADMIN_USER_IDS
)

def get_command_router(memory: ConversationMemory, db_service: DatabaseService = None, gemini_service: GeminiService = None) -> Router:
    """
    Construct command router with injected conversation memory instance and database service.
    """
    router = Router(name="commands_router")

    async def _register_user(from_user: types.User, bot: types.Bot = None):
        if db_service and from_user:
            await db_service.save_or_update_user(
                telegram_id=from_user.id,
                username=from_user.username,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
                language_code=from_user.language_code or "en"
            )

    @router.message(CommandStart())
    async def cmd_start(message: types.Message):
        """
        Handle /start command with user database registration and modern HTML welcome message.
        """
        if message.from_user:
            await _register_user(message.from_user, message.bot)
            user_name = message.from_user.first_name or "Friend"
        else:
            user_name = "Friend"

        escaped_user_name = escape(user_name)

        total_users = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_users = stats.get("total_users", 0)
        formatted_users = format_user_count(total_users)

        welcome_text = (
            f"<b>🤖 {BOT_DISPLAY_NAME.upper()}</b>\n\n"
            f"<blockquote>សួស្តី {escaped_user_name}! 👋\n"
            "ខ្ញុំជាជំនួយការ AI ដែលអាចនិយាយភាសាខ្មែរ និង English។</blockquote>\n\n"
            f"👥 <b>អ្នកប្រើប្រាស់សរុប (Total Registered Users):</b> {total_users} ({formatted_users} users)\n\n"
            "<b>✨ ខ្ញុំអាចជួយអ្នកបាន៖</b>\n\n"
            "💬 សួរសំណួរទូទៅ (Text Chat)\n"
            "🖼 វិភាគរូបភាព (Vision AI)\n"
            "🎙️ វិភាគ និងបកប្រែសារសំឡេង (Voice Notes AI)\n"
            "📄 វិភាគ និងទាញយកអត្ថបទពី PDF & Code Files\n"
            "🎯 7 Specialized AI Operating Modes (/mode)\n"
            "💻 ពន្យល់ និងដំណើរការកូដ (/run /code)\n"
            "📚 ជួយការសិក្សា និងស្រាវជ្រាវ\n"
            "🌐 បកប្រែ Khmer ↔ English\n\n"
            "<b>🚀 ចាប់ផ្ដើមប្រើប្រាស់</b>\n\n"
            "ផ្ញើសំណួរ, ផ្ញើរូបភាព, ផ្ញើសារសំឡេង ឬប្រើ /mode!"
        )

        await message.answer("👇 <b>Menu ត្រូវបានបើកអូតូ៖</b>", parse_mode="HTML", reply_markup=get_main_reply_keyboard())

        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=get_welcome_inline_keyboard()
        )

    @router.message(F.new_chat_members)
    async def handle_new_chat_members(message: types.Message):
        """
        Handle new members joining a group or channel chat.
        Registers joining members in MySQL database and sends welcome greeting.
        """
        if message.new_chat_members:
            for new_member in message.new_chat_members:
                if not new_member.is_bot:
                    await _register_user(new_member, message.bot)
                    user_name = escape(new_member.first_name or "Friend")
                    welcome_group_msg = (
                        f"👋 <b>សូមស្វាគមន៍ {user_name} មកកាន់ក្រុម! / Welcome {user_name}!</b>\n\n"
                        f"🤖 ខ្ញុំជា <b>{BOT_DISPLAY_NAME}</b> ជំនួយការ AI ឆ្លាតវៃ។\n\n"
                        "👉 វាយ /start ឬ /help ដើម្បីមើលការណែនាំប្រើប្រាស់!"
                    )
                    try:
                        await message.answer(welcome_group_msg, parse_mode="HTML")
                    except Exception as e:
                        logging.error(f"Error sending group welcome message: {e}")

    @router.message(Command("quiz"))
    async def cmd_quiz(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user, message.bot)
            user_id = message.from_user.id
        else:
            user_id = message.chat.id

        args = message.text.split(maxsplit=1)
        topic = args[1] if len(args) > 1 else "ចំណេះដឹងទូទៅ (General Knowledge)"

        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        loading_msg = await message.answer(f"🧩 កំពុងរៀបចំសំណួរ Quiz ប្រធានបទ៖ <b>{escape(topic)}</b>...", parse_mode="HTML")

        prompt = f"Please generate a multiple-choice quiz about {topic}."

        try:
            if gemini_service:
                active_mode = "general"
                if db_service:
                    active_mode = await db_service.get_user_mode(user_id)
                ai_response = await gemini_service.generate_text_chat(user_prompt=prompt, mode=active_mode)
                
                await memory.add_user_message_async(user_id, prompt)
                await memory.add_assistant_message_async(user_id, ai_response)
                
                try:
                    await loading_msg.delete()
                except:
                    pass
                await send_safe_response(message, ai_response)
            else:
                try:
                    await loading_msg.delete()
                except:
                    pass
                await message.answer("⚠️ មុខងារ Quiz មិនទាន់មានដំណើរការទេ (AI Service Offline)។")
        except Exception as e:
            try:
                await loading_msg.delete()
            except:
                pass
            await message.answer("⚠️ មានបញ្ហាក្នុងការបង្កើត Quiz។ សូមព្យាយាមម្តងទៀត! (Error generating quiz)")

    @router.message(Command("mode"))
    @router.message(F.text.contains("ជ្រើសរើស Mode"))
    async def cmd_mode(message: types.Message):
        user_id = message.from_user.id if message.from_user else 0
        if message.from_user:
            await _register_user(message.from_user, message.bot)

        current_mode = "general"
        if db_service:
            current_mode = await db_service.get_user_mode(user_id)

        mode_text = (
            "🎯 <b>ជ្រើសរើស AI Operating Mode / Select AI Mode:</b>\n\n"
            "• <b>🤖 General AI Mode:</b> ជំនួយការ AI ទូទៅ (សួរដេញដោល, សរសេរកូដ, វិភាគទូទៅ)\n"
            "• <b>📐 Standard Mode:</b> បម្លែងសមីការ/រូបមន្ត គណិត/គីមី/រូបវិទ្យា/តារាង ជាកូដ LaTeX\n"
            "• <b>🇰🇭 Khmer Math Mode:</b> បម្លែងសមីការ គណិត/គីមី/រូបវិទ្យា/តារាង ជាកូដ LaTeX ភាសាខ្មែរ\n"
            "• <b>🌐 Translate to ខ្មែរ Mode:</b> បកប្រែអត្ថបទ, រូបភាព ឬ ឯកសារ ទៅជាភាសាខ្មែរ\n"
            "• <b>🎨 TikZ Mode:</b> បម្លែងរូបភាព ក្រាហ្វ, Circuit, ធរណីមាត្រ ជាកូដ LaTeX TikZ Diagram\n"
            "• <b>📄 PDF to Text Mode:</b> ទាញយកអត្ថបទពី PDF ភាសាខ្មែរ\n"
            "• <b>✍️ Handwrite Mode:</b> បម្លែងអក្សរដៃ/សមីការដៃ ទៅជាកូដ LaTeX ភ្លាមៗ\n\n"
            f"📌 Mode បច្ចុប្បន្នរបស់អ្នក៖ <b>{current_mode.upper()}</b>"
        )
        await message.answer(mode_text, parse_mode="HTML", reply_markup=get_mode_inline_keyboard(current_mode))

    @router.message(Command("help"))
    @router.message(F.text.contains("របៀបសួរសំណួរ"))
    async def cmd_help(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)

        help_text = (
            "📖 <b>ការណែនាំពីរបៀបប្រើប្រាស់ / Usage Guide:</b>\n\n"
            "<b>1. 💬 សួរសំណួរជាអក្សរ (Text Chat):</b>\n"
            "• វាយសំណួរជាភាសាខ្មែរ ឬអង់គ្លេស រួចផ្ញើចេញ.\n"
            "• ឧទាហរណ៍៖ <i>\"តើអ្វីទៅជា Python Asyncio?\"</i>\n\n"
            "<b>2. 🖼 ផ្ញើរូបភាពវិភាគ (Vision AI):</b>\n"
            "• ផ្ញើរូបភាព (Photo) ហើយសរសេរសំណួរនៅក្នុង <b>Caption</b>.\n\n"
            "<b>3. 🧹 បង្កើតការសន្ទនាថ្មី (/new ឬ /clear):</b>\n"
            "• វាយ /new ឬ /clear ដើម្បីលុប Context នៃការសន្ទនាយកសំណួរថ្មី.\n\n"
            "<b>4. 📊 ពិនិត្យស្ថិតិ (/stats):</b>\n"
            "• វាយ /stats ដើម្បីមើលស្ថិតិអ្នកប្រើប្រាស់នៅក្នុងប្រព័ន្ធ."
        )
        await message.answer(help_text, parse_mode="HTML", reply_markup=get_welcome_inline_keyboard())

    @router.message(Command("new"))
    @router.message(Command("clear"))
    @router.message(F.text.contains("លុប History"))
    async def cmd_clear(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)
            user_id = message.from_user.id
        else:
            user_id = message.chat.id

        if db_service:
            cleared_db = await db_service.clear_history(user_id)
        cleared_cache = memory.clear_history(user_id)
        
        if cleared_cache or (db_service and cleared_db):
            await message.answer("🧹 <b>ប្រវត្តិសន្ទនារបស់អ្នកត្រូវបានលុបរួចរាល់!</b> / Conversation history cleared!", parse_mode="HTML")
        else:
            await message.answer("ℹ️ មិនមានប្រវត្តិសន្ទនាដែលត្រូវលុបទេ។ / No active conversation history found.", parse_mode="HTML")

    @router.message(Command("language"))
    async def cmd_language(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)

        msg = "🌐 <b>សូមជ្រើសរើសភាសាដែលអ្នកពេញចិត្ត / Choose preferred language:</b>"
        await message.answer(msg, parse_mode="HTML", reply_markup=get_language_inline_keyboard())

    @router.message(Command("about"))
    @router.message(F.text.contains("អំពី Bot"))
    async def cmd_about(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)

        total_users = 0
        if db_service:
            stats = await db_service.get_global_stats()
            total_users = stats.get("total_users", 0)
        formatted = format_user_count(total_users)

        about_text = (
            f"👤 <b>អំពី {BOT_DISPLAY_NAME} / About Bot:</b>\n\n"
            f"🤖 <b>Bot Name:</b> {BOT_DISPLAY_NAME}\n"
            f"⚡ <b>AI Engine:</b> Google Gemini ({GEMINI_MODEL})\n"
            "🌐 <b>Supported Languages:</b> 🇰🇭 Khmer & 🇬🇧 English\n"
            f"👥 <b>Total Registered Users:</b> {total_users} ({formatted} users)\n"
            "🛠 <b>Framework:</b> Python 3.11+ & Aiogram 3.x\n"
            "🗄 <b>Database:</b> MySQL (aiomysql)\n"
            "🔒 <b>Privacy:</b> Secure, in-memory image vision pipeline."
        )
        await message.answer(about_text, parse_mode="HTML")

    @router.message(Command("privacy"))
    async def cmd_privacy(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)

        privacy_text = (
            "🔒 <b>គោលការណ៍ឯកជនភាព / Privacy Policy:</b>\n\n"
            "• <b>Image Processing:</b> រូបភាពដែលអ្នកផ្ញើមកត្រូវបានដំណើរការក្នុង Memory (RAM) ដោយផ្ទាល់ និងមិនត្រូវបានរក្សាទុកជាអចិន្ត្រៃយ៍លើ Disk ឡើយ.\n"
            "• <b>Conversation Memory:</b> ប្រវត្តិសន្ទនាត្រូវបានប្រើប្រាស់ជា Temporary Context Window សម្រាប់ឆ្លើយតបសំណួររបស់អ្នកប៉ុណ្ណោះ.\n"
            "• <b>API Transmission:</b> សំណួរ និងរូបភាពត្រូវបានផ្ញើទៅកាន់ Google Gemini AI API តាមរយៈ HTTPS encrypted link សុវត្ថិភាព.\n"
            "• <b>User Data:</b> ប្រព័ន្ធរក្សាទុកតែ Telegram User ID, Username, និងឈ្មោះដើម្បីផ្តល់សេវាកម្មរាប់ចំនួនអ្នកប្រើប្រាស់ប៉ុណ្ណោះ."
        )
        await message.answer(privacy_text, parse_mode="HTML")

    @router.message(Command("stats"))
    @router.message(F.text.contains("ស្ថិតិ"))
    async def cmd_stats(message: types.Message):
        user_id = message.from_user.id if message.from_user else 0
        if message.from_user:
            await _register_user(message.from_user)

        user_stats = {"total_messages": 0, "text_count": 0, "image_count": 0}
        if db_service:
            user_stats = await db_service.get_user_stats(user_id)
        
        stats_text = (
            "📊 <b>ស្ថិតិផ្ទាល់ខ្លួនរបស់អ្នក / Your Usage Stats</b>\n\n"
            f"💬 <b>សំណួរសរុប (Total Questions):</b> {user_stats.get('total_messages', 0)}\n"
            f"📝 <b>អត្ថបទ (Text):</b> {user_stats.get('text_count', 0)}\n"
            f"🖼️ <b>រូបភាព (Images):</b> {user_stats.get('image_count', 0)}"
        )
        await message.answer(stats_text, parse_mode="HTML")

    @router.message(Command("status"))
    async def cmd_status(message: types.Message):
        user_id = message.from_user.id if message.from_user else 0
        if message.from_user:
            await _register_user(message.from_user)

        # Check permission if not public and user is not admin
        if not STATS_PUBLIC and ADMIN_USER_IDS and user_id not in ADMIN_USER_IDS:
            await message.answer("⚠️ <b>អ្នកមិនមានសិទ្ធិមើលស្ថិតិនេះទេ។ / Access restricted.</b>", parse_mode="HTML")
            return

        total_users = 0
        total_messages = 0
        db_status = "🟡 Active (In-Memory Mode)"
        if db_service:
            if db_service.is_connected:
                db_status = "🟢 Connected (MySQL)"
            global_stats = await db_service.get_global_stats()
            total_users = global_stats.get("total_users", 0)
            total_messages = global_stats.get("total_messages", 0)

        formatted_total = format_user_count(total_users)
        
        status_text = (
            "📊 <b>System Health & Global Stats</b>\n\n"
            f"🗄️ <b>Database:</b> {db_status}\n"
            f"👥 <b>Total Users:</b> {formatted_total} ({total_users})\n"
            f"💬 <b>Total Messages Processed:</b> {total_messages}\n"
            "🤖 <b>Bot Status:</b> Online"
        )
        await message.answer(status_text, parse_mode="HTML")

    @router.message(Command("vision"))
    @router.message(F.text.contains("វិភាគរូបភាព"))
    @router.message(F.text.startswith("🖼"))
    async def cmd_vision(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)
        msg = (
            "🖼 <b>សូមផ្ញើរូបភាព ហើយសរសេរសំណួរនៅក្នុង Caption៖</b>\n\n"
            "1. ចុច <b>Attach File / Photo</b> ក្នុង Telegram\n"
            "2. ជ្រើសរើសរូបភាព ឬ Screenshot របស់អ្នក\n"
            "3. វាយសំណួររបស់អ្នកនៅក្នុងប្រអប់ <b>Caption</b>\n"
            "4. ចុច <b>Send</b> ជាការស្រេច!"
        )
        await message.answer(msg, parse_mode="HTML")

    @router.message(Command("run"))
    @router.message(Command("code"))
    async def cmd_run(message: types.Message):
        if message.from_user:
            await _register_user(message.from_user)

        raw_text = message.text.strip() if message.text else ""
        
        import re
        parts = raw_text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            usage_msg = (
                "⚡ <b>របៀបប្រើប្រាស់ /run ឬ /code (Execute Code):</b>\n\n"
                "• <b>Python:</b> <code>/run python print('Hello World!')</code>\n"
                "• <b>JavaScript:</b> <code>/run js console.log('Hello!')</code>\n"
                "• <b>TypeScript:</b> <code>/run ts const x: number = 10; console.log(x);</code>\n"
                "• <b>Java:</b> <code>/run java public class Main { public static void main(String[] a) { System.out.println(10); } }</code>\n"
                "• <b>Code block:</b> <code>/code ```python\nprint('Hello')\n```</code>\n\n"
                "👉 គាំទ្រភាសា៖ Python, JavaScript, TypeScript, Java"
            )
            await message.answer(usage_msg, parse_mode="HTML")
            return

        body = parts[1].strip()
        LANG_MAP = {
            "py": "python", "python": "python", "python3": "python",
            "js": "javascript", "javascript": "javascript", "node": "javascript", "nodejs": "javascript",
            "ts": "typescript", "typescript": "typescript",
            "java": "java",
            "cpp": "cpp", "c++": "cpp", "c": "cpp",
        }

        lang = "python"
        code_to_run = ""

        fence_pattern = r"^```([a-zA-Z0-9_+\-#]*)\s*\n?(.*?)\n?```$"
        match = re.match(fence_pattern, body, re.DOTALL)
        if match:
            lang_tag = match.group(1).strip().lower()
            code_to_run = match.group(2).strip()
            lang = LANG_MAP.get(lang_tag, "python" if not lang_tag else lang_tag)
        else:
            words = body.split(maxsplit=1)
            first_word = words[0].lower().strip("`:")
            if first_word in LANG_MAP:
                lang = LANG_MAP[first_word]
                code_to_run = words[1].strip() if len(words) > 1 else ""
                inner_match = re.match(fence_pattern, code_to_run, re.DOTALL)
                if inner_match:
                    code_to_run = inner_match.group(2).strip()
            elif body.startswith("```"):
                lines = body.splitlines()
                first_line = lines[0].lstrip("`").strip().lower()
                if first_line in LANG_MAP:
                    lang = LANG_MAP[first_line]
                    lines = lines[1:]
                else:
                    lang = "python"
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                code_to_run = "\n".join(lines).strip()
            else:
                lang = "python"
                code_to_run = body

        if not code_to_run:
            await message.answer("⚠️ សូមបញ្ចូល Code ដែលត្រូវ Run! ឧទាហរណ៍៖ <code>/run python print('Hello')</code>", parse_mode="HTML")
            return

        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        except Exception:
            pass

        loading_msg = await message.answer("⚡ កំពុងដំណើរការកូដ (Running code)...", parse_mode="HTML")

        try:
            from services.piston_service import execute_code
            result = await execute_code(lang, code_to_run)
            output = result.get("run", {}).get("output", "") or result.get("compile", {}).get("output", "No output.")

            try:
                await loading_msg.delete()
            except Exception:
                pass

            escaped_out = escape(output)
            res_msg = (
                f"⚡ <b>លទ្ធផលនៃការរត់ Code ({escape(lang)})៖</b>\n\n"
                f"<pre><code>{escaped_out}</code></pre>"
            )
            await message.answer(res_msg, parse_mode="HTML")
        except Exception as e:
            try:
                await loading_msg.delete()
            except Exception:
                pass
            logging.error(f"Error executing code: {e}")
            await message.answer(f"⚠️ មានបញ្ហាក្នុងការរត់ Code: {escape(str(e))}", parse_mode="HTML")

    @router.message(Command("image"))
    @router.message(Command("imagine"))
    @router.message(Command("draw"))
    @router.message(F.text.contains("បង្កើតរូបភាព"))
    async def cmd_image(message: types.Message):
        """
        Handle HD AI Image Generation command (/image, /imagine, /draw).
        Generates unlimited high definition images using Pollinations AI (Flux HD).
        """
        if message.from_user:
            await _register_user(message.from_user)

        command_text = message.text.strip() if message.text else ""
        prompt = ""
        if command_text:
            clean = command_text
            for prefix in ["🎨 បង្កើតរូបភាព (/image)", "🎨 បង្កើតរូបភាព", "បង្កើតរូបភាព", "/image", "/imagine", "/draw"]:
                if clean.lower().startswith(prefix.lower()):
                    clean = clean[len(prefix):].strip()
            clean = re.sub(r'^\(?\s*/?(image|imagine|draw)\s*\)?', '', clean, flags=re.IGNORECASE).strip()
            clean = re.sub(r'\(?\s*/?(image|imagine|draw)\s*\)?$', '', clean, flags=re.IGNORECASE).strip()
            if clean.lower() not in ("image", "imagine", "draw", "/image", "/imagine", "/draw", "(/image)"):
                prompt = clean

        if not prompt:
            usage_msg = (
                "🎨 <b>បង្កើតរូបភាព AI ឥតដែនកំណត់ (Unlimited HD AI Image Generator):</b>\n\n"
                "👉 <b>របៀបប្រើប្រាស់ / How to use:</b>\n"
                "<code>/image [ការពិពណ៌នារូបភាពជាភាសាខ្មែរ ឬ English]</code>\n\n"
                "<b>ឧទាហរណ៍៖</b>\n"
                "• <code>/image 16:9 នាគរាជខ្មែរ ហោះលើប្រាសាទអង្គរវត្ត ពណ៌មាស 4k</code>\n"
                "• <code>/image 9:16 futuristic Phnom Penh city in 2050, 8k resolution</code>\n"
                "• <code>/draw 1:1 a cute baby cat wearing a space suit on Mars</code>"
            )
            await message.reply(usage_msg, parse_mode="HTML")
            return

        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        except Exception:
            pass

        try:
            from services.image_gen_service import ImageGenService, parse_aspect_ratio
            from utils.thinking_animation import DynamicThinkingAnimation, IMAGE_GEN_STEPS

            img_service = ImageGenService(gemini_service=gemini_service)
            ratio_key, width, height, clean_prompt = parse_aspect_ratio(prompt)

            async with DynamicThinkingAnimation(message, IMAGE_GEN_STEPS) as anim:
                image_bytes, optimized_prompt, seed, cache_id = await img_service.generate_image(
                    prompt=clean_prompt,
                    width=width,
                    height=height
                )

            if image_bytes:
                photo_file = types.BufferedInputFile(image_bytes, filename=f"ai_image_{seed}.jpg")
                caption_text = (
                    f"🎨 <b>រូបភាព AI បង្កើតជោគជ័យ (Ultra HD AI Image):</b>\n\n"
                    f"📝 <b>Prompt:</b> <i>{escape(prompt)}</i>\n"
                    f"⚡ <b>Optimized Prompt:</b> <code>{escape(optimized_prompt[:250])}</code>\n"
                    f"📐 <b>Aspect Ratio:</b> {ratio_key} ({width}x{height} Flux HD Ultra)\n\n"
                    f"👇 <b>ទាញយករូបភាព ឬ ផ្លាស់ប្តូរទំហំខាងក្រោម៖</b>"
                )
                await message.reply_photo(
                    photo=photo_file,
                    caption=caption_text,
                    parse_mode="HTML",
                    reply_markup=get_image_download_keyboard(cache_id, ratio_key)
                )
            else:
                await message.reply("❌ <b>មិនអាចបង្កើតរូបភាពបានទេនៅពេលនេះ!</b> សូមព្យាយាមម្តងទៀតជាមួយការពិពណ៌នាផ្សេង។", parse_mode="HTML")
        except Exception as e:
            logging.error(f"Error in image generation command: {e}")
            await message.reply(f"⚠️ មានបញ្ហាក្នុងការបង្កើតរូបភាព: {escape(str(e))}", parse_mode="HTML")

    @router.message(Command("enhance"))
    @router.message(Command("unblur"))
    @router.message(Command("hd"))
    async def cmd_enhance(message: types.Message):
        """
        Handle Image Enhancement / Unblur command (/enhance, /unblur, /hd).
        Turns blurry or low resolution photos into crystal clear Ultra HD quality.
        """
        if message.from_user:
            await _register_user(message.from_user)

        target_photo = None
        if message.photo:
            target_photo = message.photo[-1]
        elif message.reply_to_message and message.reply_to_message.photo:
            target_photo = message.reply_to_message.photo[-1]

        if not target_photo:
            guide_msg = (
                "✨ <b>មុខងារកែរូបភាពពីស្រពិចស្រពិលទៅជា Ultra HD (AI Image Enhancer & Unblur):</b>\n\n"
                "👉 <b>របៀបប្រើប្រាស់ / How to use:</b>\n"
                "1. <b>វិធីទី 1:</b> ផ្ញើរូបភាព (Photo) មកកាន់ Bot រួចវាយ Caption <code>/enhance</code> ឬ <code>កែឲ្យច្បាស់</code>\n"
                "2. <b>វិធីទី 2:</b> ចុច Reply លើរូបភាពណាមួយដែលបានផ្ញើរួច រួចវាយ <code>/enhance</code> ឬ <code>/hd</code>!"
            )
            await message.reply(guide_msg, parse_mode="HTML")
            return

        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        except Exception:
            pass

        from services.image_gen_service import enhance_image_hd, IMAGE_CACHE
        from keyboards.inline import get_enhanced_image_download_keyboard
        from utils.thinking_animation import DynamicThinkingAnimation, ENHANCE_THINKING_STEPS

        try:
            async with DynamicThinkingAnimation(message, ENHANCE_THINKING_STEPS) as anim:
                file_info = await message.bot.get_file(target_photo.file_id)
                photo_bytes_io = await message.bot.download_file(file_info.file_path)
                photo_bytes = photo_bytes_io.read()

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
        except Exception as e:
            logging.error(f"Error enhancing image: {e}")
            await message.reply(f"⚠️ មានបញ្ហាក្នុងការកែរូបភាពឲ្យច្បាស់: {escape(str(e))}", parse_mode="HTML")

    return router
