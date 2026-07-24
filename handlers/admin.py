import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline import get_admin_inline_keyboard, get_model_selection_keyboard
from services.db_service import DatabaseService
from services.gemini_service import GeminiService
from config import ADMIN_USER_IDS
import os

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()


def get_admin_router(db_service: DatabaseService = None, gemini_service: GeminiService = None) -> Router:
    """
    Construct admin router with injected database and gemini services.
    """
    router = Router(name="admin_router")

    @router.message(Command("admin"))
    async def cmd_admin(message: types.Message):
        user_id = message.from_user.id
        if user_id not in ADMIN_USER_IDS:
            await message.answer("⚠️ អ្នកមិនមានសិទ្ធិចូលក្នុងផ្ទាំងគ្រប់គ្រងនេះទេ។ (Access Denied)")
            return

        welcome_msg = (
            "🛡️ <b>Admin Control Panel</b>\n\n"
            "សូមជ្រើសរើសជម្រើសខាងក្រោម៖ / Please select an option:"
        )
        await message.answer(welcome_msg, parse_mode="HTML", reply_markup=get_admin_inline_keyboard())

    @router.callback_query(F.data == "cb_back_admin")
    async def cb_back_admin_handler(callback: types.CallbackQuery):
        if callback.from_user.id not in ADMIN_USER_IDS:
            await callback.answer("Access Denied", show_alert=True)
            return
        
        await callback.answer()
        welcome_msg = (
            "🛡️ <b>Admin Control Panel</b>\n\n"
            "សូមជ្រើសរើសជម្រើសខាងក្រោម៖ / Please select an option:"
        )
        await callback.message.edit_text(welcome_msg, parse_mode="HTML", reply_markup=get_admin_inline_keyboard())

    @router.callback_query(F.data == "admin_change_model")
    async def admin_change_model_cb(callback: types.CallbackQuery):
        if callback.from_user.id not in ADMIN_USER_IDS:
            await callback.answer("Access Denied", show_alert=True)
            return

        await callback.answer()
        
        current_model = gemini_service.primary_model if gemini_service else "gemini-3.6-flash"
        msg = (
            "🤖 <b>Change AI Model</b>\n\n"
            f"Current Model: <code>{current_model}</code>\n\n"
            "Select a new model to use for all users:"
        )
        await callback.message.edit_text(
            msg, 
            parse_mode="HTML", 
            reply_markup=get_model_selection_keyboard(current_model)
        )

    @router.callback_query(F.data.startswith("set_model_"))
    async def set_model_cb(callback: types.CallbackQuery):
        if callback.from_user.id not in ADMIN_USER_IDS:
            await callback.answer("Access Denied", show_alert=True)
            return

        new_model = callback.data.replace("set_model_", "")
        
        if gemini_service:
            gemini_service.update_primary_model(new_model)
            
            # Persist to .env
            try:
                env_path = ".env"
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(env_path, "w", encoding="utf-8") as f:
                        for line in lines:
                            if line.startswith("GEMINI_MODEL="):
                                f.write(f"GEMINI_MODEL={new_model}\n")
                            else:
                                f.write(line)
            except Exception as e:
                logging.error(f"Failed to update .env: {e}")

        await callback.answer("✅ Model updated successfully!", show_alert=True)
        
        # Update the message to show new current model
        msg = (
            "🤖 <b>Change AI Model</b>\n\n"
            f"Current Model: <code>{new_model}</code>\n\n"
            "Select a new model to use for all users:"
        )
        await callback.message.edit_text(
            msg, 
            parse_mode="HTML", 
            reply_markup=get_model_selection_keyboard(new_model)
        )

    @router.callback_query(F.data == "admin_stats")
    async def admin_stats_cb(callback: types.CallbackQuery):
        if callback.from_user.id not in ADMIN_USER_IDS:
            await callback.answer("Access Denied", show_alert=True)
            return

        await callback.answer()
        total_users = 0
        total_msgs = 0
        if db_service and db_service.is_connected:
            global_stats = await db_service.get_global_stats()
            total_users = global_stats.get('total_users', 0)
            total_msgs = global_stats.get('total_messages', 0)

        from utils.solution_card import SOLUTION_CACHE
        active_cache_count = len(SOLUTION_CACHE)

        msg = (
            "📊 <b>Smart AI System Statistics</b>\n\n"
            f"👥 <b>Total Registered Users:</b> {total_users}\n"
            f"💬 <b>Total Processed Messages:</b> {total_msgs}\n"
            f"⚡ <b>AI Engine Model:</b> {gemini_service.primary_model if gemini_service else 'gemini-3.6-flash'}\n"
            f"📦 <b>Active Solution Cache Entries:</b> {active_cache_count}\n"
            f"🎨 <b>Renderer Health:</b> Playwright HTML + Local KaTeX Ready\n"
            f"🧹 <b>Temp Cleanup Status:</b> Active (TTL 24h)"
        )
        await callback.message.answer(msg, parse_mode="HTML")

    @router.callback_query(F.data == "admin_users")
    async def admin_users_cb(callback: types.CallbackQuery):
        if callback.from_user.id not in ADMIN_USER_IDS:
            await callback.answer("Access Denied", show_alert=True)
            return

        await callback.answer()
        if not db_service or not db_service.is_connected:
            await callback.message.answer("⚠️ Database disconnected.", parse_mode="HTML")
            return

        recent_users = await db_service.get_recent_users(10)
        if not recent_users:
            await callback.message.answer("No users found.")
            return

        lines = ["👥 <b>Recent Users (Last 10 active)</b>\n"]
        for u in recent_users:
            name = u.get("first_name") or u.get("username") or "Unknown"
            uid = u.get("telegram_id")
            lines.append(f"• <b>{name}</b> (ID: {uid})")

        await callback.message.answer("\n".join(lines), parse_mode="HTML")

    @router.callback_query(F.data == "admin_broadcast")
    async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_USER_IDS:
            await callback.answer("Access Denied", show_alert=True)
            return

        await callback.answer()
        await callback.message.answer(
            "📢 <b>Broadcast Mode</b>\n\n"
            "សូមផ្ញើសារដែលអ្នកចង់ Broadcast ទៅកាន់គ្រប់ Users (អាចជាអត្ថបទ ឬរូបភាព)។\n"
            "វាយពាក្យ /cancel ដើម្បីបោះបង់។",
            parse_mode="HTML"
        )
        await state.set_state(AdminStates.waiting_for_broadcast)

    @router.message(Command("cancel"), AdminStates.waiting_for_broadcast)
    async def cancel_broadcast(message: types.Message, state: FSMContext):
        if message.from_user.id not in ADMIN_USER_IDS:
            return
        await state.clear()
        await message.answer("❌ បានបោះបង់ការ Broadcast (Broadcast Cancelled)។", parse_mode="HTML")

    @router.message(AdminStates.waiting_for_broadcast)
    async def handle_broadcast_message(message: types.Message, state: FSMContext):
        if message.from_user.id not in ADMIN_USER_IDS:
            return

        if not db_service or not db_service.is_connected:
            await message.answer("⚠️ Database disconnected. Cannot broadcast.")
            await state.clear()
            return

        users = await db_service.get_all_users()
        if not users:
            await message.answer("⚠️ No users found to broadcast.")
            await state.clear()
            return

        # Send to all users
        success_count = 0
        fail_count = 0
        
        status_msg = await message.answer(f"⏳ កំពុងបញ្ជូនសារទៅកាន់ {len(users)} users...")
        
        for uid in users:
            try:
                await message.copy_to(uid)
                success_count += 1
            except Exception as e:
                fail_count += 1
                logging.error(f"Broadcast failed to user {uid}: {e}")

        await status_msg.delete()
        await message.answer(
            f"✅ <b>Broadcast បញ្ចប់រូចរាល់!</b>\n\n"
            f"📤 បញ្ជូនបានជោគជ័យ: {success_count}\n"
            f"❌ បរាជ័យ: {fail_count}",
            parse_mode="HTML"
        )
        await state.clear()

    return router
