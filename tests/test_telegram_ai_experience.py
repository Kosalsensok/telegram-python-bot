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
from services.prototype_service import create_mart_system_prototype_files, generate_prototype_zip_bytes


class TestTelegramAIExperience(unittest.TestCase):
    """
    Comprehensive test suite for Telegram AI Premium Experience.
    """

    def test_broken_character_detection_and_cleaning(self):
        dirty = "\u25A1 Feature 1: \u25A1 POS Checkout \uFFFD"
        self.assertTrue(contains_broken_characters(dirty))
        cleaned = clean_broken_characters(dirty)
        self.assertNotIn("\u25A1", cleaned)
        self.assertNotIn("\uFFFD", cleaned)
        self.assertIn("• Feature 1: • POS Checkout", cleaned)

    def test_response_type_router(self):
        self.assertEqual(detect_response_type_from_text("Write C++ loop code"), "code_answer")
        self.assertEqual(detect_response_type_from_text("Feature mart system"), "software_requirements")
        self.assertEqual(detect_response_type_from_text("Build mart system prototype"), "project_prototype")
        self.assertEqual(detect_response_type_from_text("Create database for mart system"), "database_design")
        self.assertEqual(detect_response_type_from_text("Explain microservice architecture"), "system_architecture")
        self.assertEqual(detect_response_type_from_text("Solve \\frac{1}{2} equation"), "mathematics")
        self.assertEqual(detect_response_type_from_text("Stripe payment email unsuccessful"), "email_analysis")

    def test_structured_ai_parser(self):
        raw_json = json.dumps({
            "response_type": "software_requirements",
            "language": "km",
            "title": "ប្រព័ន្ធគ្រប់គ្រង Mart",
            "summary": "ប្រព័ន្ធគ្រប់គ្រងការលក់ និងស្តុក",
            "tags": ["POS", "Inventory"],
            "sections": [
                {
                    "id": "sec_1",
                    "step_number": 1,
                    "heading_km": "ទិដ្ឋភាពទូទៅ",
                    "content_km": "ការសង្ខេបតម្រូវការ"
                }
            ]
        })
        parsed = parse_ai_structured_response(raw_json)
        self.assertEqual(parsed["response_type"], "software_requirements")
        self.assertEqual(parsed["title"], "ប្រព័ន្ធគ្រប់គ្រង Mart")
        self.assertEqual(len(parsed["sections"]), 1)

    def test_telegram_html_escaping_and_markdown(self):
        raw = "Check <b>code</b> & test `int x = 5;` and <pre><code class=\"language-cpp\">int a = 10;</code></pre>"
        formatted = markdown_to_telegram_html(raw)
        self.assertIn("<code>int x = 5;</code>", formatted)
        self.assertIn("&amp;", formatted)

    def test_html_message_splitting(self):
        long_html = "<p>" + ("Hello World " * 400) + "</p>"
        chunks = split_html_message(long_html, max_length=1000)
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 1050)

    def test_solution_cache_and_short_id(self):
        sid = generate_short_solution_id()
        self.assertEqual(len(sid), 8)

        data = {"title": "Test Solution", "response_type": "code_answer"}
        save_solution_cache(sid, "raw text", data, telegram_user_id=12345)

        cached = get_solution_cache(sid)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["title"], "Test Solution")
        self.assertEqual(cached["telegramUserId"], 12345)

    def test_prototype_generator(self):
        files = create_mart_system_prototype_files("Smart Mart System")
        self.assertGreaterEqual(len(files), 5)
        filenames = [f["filename"] for f in files]
        self.assertIn("README.md", filenames)
        self.assertIn("schema.sql", filenames)
        self.assertIn("pos_service.py", filenames)

        zip_bytes = generate_prototype_zip_bytes(files)
        self.assertGreater(len(zip_bytes), 100)


if __name__ == "__main__":
    unittest.main()
