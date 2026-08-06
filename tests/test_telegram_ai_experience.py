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

    def test_code_block_html_and_line_number_stripping(self):
        dirty_code = "```cpp\n1: <b>#include</b> <iostream>\n2: int main() { return 0; }\n```"
        formatted = markdown_to_telegram_html(dirty_code)
        self.assertNotIn("<b>", formatted)
        self.assertNotIn("1:", formatted)
        self.assertIn("&lt;iostream&gt;", formatted)
        self.assertIn('<pre><code class="language-cpp">#include &lt;iostream&gt;\nint main() { return 0; }</code></pre>', formatted)

    def test_multi_backtick_code_block_parsing(self):
        multi_backtick_code = "````cpp\n#include <iostream>\nint main() {\n    return 0;\n}\n````"
        formatted = markdown_to_telegram_html(multi_backtick_code)
        self.assertIn('<pre><code class="language-cpp">#include &lt;iostream&gt;\nint main() {\n    return 0;\n}</code></pre>', formatted)
        self.assertNotIn("````", formatted)

    def test_orphan_asterisks_and_spacing_cleaning(self):
        raw_text = "📌 **សង្ខេប៖** 1 **កូដឧទាហរណ៍ C++ Loops**"
        formatted = markdown_to_telegram_html(raw_text)
        self.assertNotIn("**", formatted)
        self.assertIn("📌 <b>សង្ខេប៖</b> 1 <b>កូដឧទាហរណ៍ C++ Loops</b>", formatted)

    def test_no_raw_html_tag_leak_and_code_filtering(self):
        data = {
            "summary": "C++ Loop Explanation",
            "code": {"language": "cpp", "content": "#include <iostream>\nint main() { return 0; }"},
            "sections": [
                {
                    "heading": "Core Components",
                    "content": "Initialization (int i = 1): Start from 1\nfor (int i = 1; i <= 5; i++) {\nstd::cout << i;\n}"
                },
                {
                    "heading": "Execution Flow",
                    "content": "1. 1️⃣ Step 1: Start i = 1\n2. 2️⃣ Step 2: Loop running"
                }
            ]
        }
        from utils.response_router import format_code_answer_telegram
        formatted = format_code_answer_telegram(data)
        # Verify no raw escaped HTML tags like &lt;b&gt;
        self.assertNotIn("&lt;b&gt;", formatted)
        self.assertIn("<b>", formatted)
        # Verify raw code statement is filtered out from components
        self.assertNotIn("for (int i = 1; i &lt;= 5; i++)", formatted)
        # Verify no duplicate numbering like "1. 1️⃣"
        self.assertNotIn("1. 1️⃣", formatted)
        self.assertIn("1️⃣ Start i = 1", formatted)

    def test_contextual_inline_keyboard_3_row_hierarchy(self):
        kb = get_ai_result_contextual_keyboard("test_sid")
        rows = kb.inline_keyboard
        self.assertEqual(len(rows), 3)  # 3 rows
        self.assertEqual(len(rows[0]), 3)  # Row 1: 3 buttons (👍 ចូលចិត្ត, 👎 មិនចូលចិត្ត, 🔄 ធ្វើឡើងវិញ)
        self.assertEqual(len(rows[1]), 2)  # Row 2: 2 buttons (💬 ពន្យល់បន្ថែម, 📋 ទម្រង់សាមញ្ញ)
        self.assertEqual(len(rows[2]), 1)  # Row 3: 1 button (🏠 Menu ដើម)
        self.assertEqual(rows[0][2].text, "🔄 ធ្វើឡើងវិញ")
        self.assertEqual(rows[2][0].text, "🏠 ម៉ឺនុយដើម")

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
        self.assertIn("Smart AI Assistant", formatted)
        self.assertNotIn("MATHEMATICS SOLUTION", formatted)

    def test_main_menu_inline_keyboard_structure(self):
        kb = get_welcome_inline_keyboard()
        buttons = kb.inline_keyboard
        self.assertEqual(len(buttons), 5)  # 5 compact rows
        self.assertEqual(buttons[0][0].text, "💬 សួរ AI")
        self.assertEqual(buttons[0][1].text, "🖼️ វិភាគរូបភាព")
        self.assertEqual(buttons[1][0].text, "🎙️ សំឡេងទៅជាអក្សរ")
        self.assertEqual(buttons[1][1].text, "🗺️ បង្ហាញផ្លូវ & ទីតាំង")
        self.assertEqual(buttons[2][0].text, "🎯 AI Modes")
        self.assertEqual(buttons[2][1].text, "🌐 Mini App")
        self.assertEqual(buttons[3][0].text, "💖 បរិច្ចាគ (Donate)")
        self.assertEqual(buttons[3][1].text, "ℹ️ ជំនួយ & អំពី Bot")
        self.assertEqual(buttons[4][0].text, "🔐 ឯកជនភាព")
        self.assertEqual(buttons[4][1].text, "❌ បិទ Menu")
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
        self.assertIn("SMART AI ASSISTANT", res)
        self.assertIn("Python Asyncio", res)
        self.assertIn("ចម្លើយ", res)
        self.assertIn("ព័ត៌មានលម្អិត", res)

    def test_format_image_analysis_result(self):
        res = format_image_analysis_result(
            detected_type="Screenshot",
            observation="រូបថតកូដ Python",
            answer="កូដនេះមាន Syntax Error ត្រង់ line 5",
            suggestion="ថែម : នៅចុងលក្ខខណ្ឌ if"
        )
        self.assertTrue("UI/UX Analysis" in res or "លទ្ធផលនៃ" in res or "កូដនេះមាន" in res)
        self.assertIn("កូដនេះមាន Syntax Error", res)

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
