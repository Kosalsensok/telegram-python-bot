import unittest
import json
import time
from utils.response_router import (
    contains_broken_characters,
    clean_broken_characters,
    detect_response_type_from_text,
    parse_ai_structured_response,
    format_telegram_html
)
from utils.message_utils import (
    escape_tg_html,
    sanitize_telegram_html,
    markdown_to_telegram_html,
    split_html_message
)
from utils.solution_card import (
    save_solution_cache,
    get_solution_cache,
    generate_short_solution_id,
    cleanup_expired_solution_cache,
    SOLUTION_CACHE
)
from keyboards.inline import (
    get_welcome_inline_keyboard,
    get_mode_inline_keyboard,
    get_language_inline_keyboard,
    get_ai_result_contextual_keyboard,
    get_image_result_contextual_keyboard
)
from utils.keyboard_utils import get_main_reply_keyboard
from utils.localization import format_ai_result, format_image_analysis_result
from utils.mini_app_auth import validate_telegram_init_data
from aiogram.types import ReplyKeyboardRemove


class TestTelegramAIExperience(unittest.TestCase):
    """
    Comprehensive test suite for Telegram AI Premium Experience & Production Readiness.
    """

    def test_broken_character_detection_and_cleaning(self):
        dirty = "\u25A1 Feature 1: \u25A1 POS Checkout \uFFFD"
        self.assertTrue(contains_broken_characters(dirty))
        cleaned = clean_broken_characters(dirty)
        self.assertNotIn("\u25A1", cleaned)
        self.assertNotIn("\uFFFD", cleaned)
        self.assertIn("• Feature 1: • POS Checkout", cleaned)

    def test_response_type_router(self):
        self.assertEqual(detect_response_type_from_text("hi"), "greeting")
        self.assertEqual(detect_response_type_from_text("hello"), "greeting")
        self.assertEqual(detect_response_type_from_text("សួស្តី"), "greeting")
        self.assertEqual(detect_response_type_from_text("write a code C++ loop"), "code_answer")
        self.assertEqual(detect_response_type_from_text("Feature mart system"), "software_requirements")
        self.assertEqual(detect_response_type_from_text("Build mart system prototype"), "project_prototype")
        self.assertEqual(detect_response_type_from_text("Create database for mart system"), "database_design")
        self.assertEqual(detect_response_type_from_text("Explain microservice architecture"), "system_architecture")
        self.assertEqual(detect_response_type_from_text("Solve \\frac{1}{2} equation"), "mathematics")
        self.assertEqual(detect_response_type_from_text("Stripe payment email unsuccessful"), "email_analysis")

    def test_greeting_formatting(self):
        formatted = format_telegram_html({"response_type": "greeting"})
        self.assertIn("សួស្តី!", formatted)
        self.assertNotIn("MATHEMATICS SOLUTION", formatted)

    def test_main_menu_inline_keyboard_structure(self):
        kb = get_welcome_inline_keyboard()
        buttons = kb.inline_keyboard
        self.assertEqual(len(buttons), 5)  # 5 rows
        self.assertEqual(buttons[0][0].text, "💬 សួរ AI")
        self.assertEqual(buttons[0][1].text, "🖼 វិភាគរូបភាព")
        self.assertEqual(buttons[1][0].text, "🎯 AI Modes")
        self.assertEqual(buttons[1][1].text, "🌐 Mini App")
        self.assertEqual(buttons[4][0].text, "✕ បិទ Menu")
        # Ensure clean labels without commands
        for row in buttons:
            for btn in row:
                self.assertNotIn("(/mode)", btn.text)
                self.assertNotIn("(/miniapp)", btn.text)

    def test_reply_keyboard_removed(self):
        kb = get_main_reply_keyboard()
        self.assertIsInstance(kb, ReplyKeyboardRemove)

    def test_ai_mode_inline_keyboard_checkmarks(self):
        kb = get_mode_inline_keyboard(current_mode="standard")
        texts = [btn.text for row in kb.inline_keyboard for btn in row]
        self.assertIn("✅ 📐 Standard Math", texts)
        self.assertIn("💬 General Assistant", texts)

    def test_language_inline_keyboard_checkmarks(self):
        kb = get_language_inline_keyboard(current_lang="km")
        texts = [btn.text for row in kb.inline_keyboard for btn in row]
        self.assertIn("✅ 🇰🇭 ភាសាខ្មែរ", texts)
        self.assertIn("🇬🇧 English", texts)

    def test_format_ai_result(self):
        res = format_ai_result(
            title="Python Asyncio",
            answer="Asyncio គឺជារបៀបសរសេរកូដ Asynchronous ក្នុង Python",
            explanation="វាប្រើប្រាស់ Event Loop សម្រាប់ដំណើរការ Task ច្រើនក្នុងពេលតែមួយ",
            tips="គួរប្រើ aiohttp ជំនួស requests"
        )
        self.assertIn("🧠 <b>SMART AI ASSISTANT</b>", res)
        self.assertIn("📌 <b>ប្រធានបទ</b>\nPython Asyncio", res)
        self.assertIn("✅ <b>ចម្លើយ</b>", res)
        self.assertIn("📖 <b>ព័ត៌មានលម្អិត</b>", res)
        self.assertIn("💡 <b>គន្លឹះ</b>", res)

    def test_format_image_analysis_result(self):
        res = format_image_analysis_result(
            detected_type="Screenshot",
            observation="រូបថតកូដ Python",
            answer="កូដនេះមាន Syntax Error ត្រង់ line 5",
            suggestion="ថែម : នៅចុងលក្ខខណ្ឌ if"
        )
        self.assertIn("🖼 <b>IMAGE ANALYSIS</b>", res)
        self.assertIn("📌 <b>ប្រភេទរូបភាព</b>\nScreenshot", res)
        self.assertIn("🔎 <b>អ្វីដែលបានរកឃើញ</b>\nរូបថតកូដ Python", res)

    def test_solution_cache_and_short_id(self):
        sid = generate_short_solution_id()
        self.assertEqual(len(sid), 8)

        data = {"title": "Test Solution", "response_type": "code_answer"}
        save_solution_cache(sid, "raw text", data, telegram_user_id=12345)

        cached = get_solution_cache(sid)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["title"], "Test Solution")
        self.assertEqual(cached["telegramUserId"], 12345)

    def test_mini_app_auth_validation(self):
        bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        # Invalid hash should return False
        self.assertFalse(validate_telegram_init_data("query_id=123&user=%7B%22id%22%3A1%7D&hash=invalidhash", bot_token))
        self.assertFalse(validate_telegram_init_data("", bot_token))


if __name__ == "__main__":
    unittest.main()
