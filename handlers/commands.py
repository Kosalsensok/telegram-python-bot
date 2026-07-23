import asyncio
import logging
from html import escape
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from services.bot_profile_service import update_bot_profile
from keyboards.inline import get_welcome_inline_keyboard, get_language_inline_keyboard, get_mode_inline_keyboard
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

router = Router(name="commands_router")


def get_command_router(memory: ConversationMemory, db_service: DatabaseService = None, gemini_service: GeminiService = None) -> Router:
    """
    Construct command router with injected conversation memory instance and database service.
    """

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

        welcome_text = (
            f"<b>🤖 {BOT_DISPLAY_NAME.upper()}</b>\n\n"
            f"<blockquote>សួស្តី {escaped_user_name}! 👋\n"
            "ខ្ញុំជាជំនួយការ AI ដែលអាចនិយាយភាសាខ្មែរ និង English។</blockquote>\n\n"
            "<b>✨ ខ្ញុំអាចជួយអ្នកបាន៖</b>\n\n"
            "💬 សួរសំណួរទូទៅ\n"
            "🖼 វិភាគរូបភាព\n"
            "🎯 7 Specialized AI Operating Modes (/mode)\n"
            "💻 ពន្យល់ និងជួសជុល Code\n"
            "📚 ជួយការសិក្សា និងស្រាវជ្រាវ\n"
            "🌐 បកប្រែ Khmer ↔ English\n\n"
            "<b>🚀 ចាប់ផ្ដើមប្រើប្រាស់</b>\n\n"
            "ផ្ញើសំណួរមកខ្ញុំ, ផ្ញើរូបភាព ឬប្រើប្រាស់ពាក្យបញ្ជា /mode!"
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
            "• វាយសំណួរជាភាសាខ្មែរ ឬអង់គ្លេស រួចផ្ញើចេញ。\n"
            "• ឧទាហរណ៍៖ <i>\"តើអ្វីទៅជា Python Asyncio?\"</i>\n\n"
            "<b>2. 🖼 ផ្ញើរូបភាពវិភាគ (Vision AI):</b>\n"
            "• ផ្ញើរូបភាព (Photo) ហើយសរសេរសំណួរនៅក្នុង <b>Caption</b>。\n\n"
            "<b>3. 🧹 បង្កើតការសន្ទនាថ្មី (/new ឬ /clear):</b>\n"
            "• វាយ /new ឬ /clear ដើម្បីលុប Context នៃការសន្ទនាយកសំណួរថ្មី。\n\n"
            "<b>4. 📊 ពិនិត្យស្ថិតិ (/stats):</b>\n"
            "• វាយ /stats ដើម្បីមើលស្ថិតិអ្នកប្រើប្រាស់នៅក្នុងប្រព័ន្ធ。"
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
            "• <b>Image Processing:</b> រូបភាពដែលអ្នកផ្ញើមកត្រូវបានដំណើរការក្នុង Memory (RAM) ដោយផ្ទាល់ និងមិនត្រូវបានរក្សាទុកជាអចិន្ត្រៃយ៍លើ Disk ឡើយ。\n"
            "• <b>Conversation Memory:</b> ប្រវត្តិសន្ទនាត្រូវបានប្រើប្រាស់ជា Temporary Context Window សម្រាប់ឆ្លើយតបសំណួររបស់អ្នកប៉ុណ្ណោះ。\n"
            "• <b>API Transmission:</b> សំណួរ និងរូបភាពត្រូវបានផ្ញើទៅកាន់ Google Gemini AI API តាមរយៈ HTTPS encrypted link សុវត្ថិភាព。\n"
            "• <b>User Data:</b> ប្រព័ន្ធរក្សាទុកតែ Telegram User ID, Username, និងឈ្មោះដើម្បីផ្តល់សេវាកម្មរាប់ចំនួនអ្នកប្រើប្រាស់ប៉ុណ្ណោះ。"
        )
        await message.answer(privacy_text, parse_mode="HTML")

    @router.message(Command("stats"))
    @router.message(F.text.contains("ស្ថិតិ"))
    async def cmd_stats(message: types.Message):
        user_id = message.from_user.id if message.from_user else 0
        if message.from_user:
            await _register_user(message.from_user)

        if not db_service or not db_service.is_connected:
            await message.answer("⚠️ មូលដ្ឋានទិន្នន័យមិនដំណើរការ។ សូមសាកល្បងម្ដងទៀតនៅពេលក្រោយ។", parse_mode="HTML")
            return

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
        db_status = "🔴 Disconnected"
        if db_service and db_service.is_connected:
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

        raw_text = message.text.strip()
        parts = raw_text.split(maxsplit=2)

        if len(parts) < 2:
            usage_msg = (
                "⚡ <b>របៀបប្រើប្រាស់ /run ឬ /code (Execute Code):</b>\n\n"
                "• <b>Python:</b> <code>/run python print('Hello World!')</code>\n"
                "• <b>JavaScript:</b> <code>/run js console.log('Hello!')</code>\n"
                "• <b>Auto-detect (Python):</b> <code>/run print('Hello!')</code>\n\n"
                "👉 គាំទ្រភាសា៖ Python, JavaScript, Java"
            )
            await message.answer(usage_msg, parse_mode="HTML")
            return

        first_arg = parts[1].lower().strip()
        if len(parts) == 2:
            if first_arg in ["py", "python", "js", "javascript", "java"]:
                await message.answer("⚠️ សូមបញ្ចូល Code ដែលត្រូវ Run! ឧទាហរណ៍៖ <code>/run python print('Hello')</code>", parse_mode="HTML")
                return
            lang = "python"
            code_to_run = parts[1]
        else:
            if first_arg in ["py", "python", "js", "javascript", "java"]:
                lang = first_arg
                code_to_run = parts[2]
            else:
                lang = "python"
                code_to_run = parts[1] + " " + parts[2]

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

    return router
