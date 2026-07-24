import unittest
from utils.khmer_spell_checker import check_khmer_spelling, count_khmer_words_and_chars

class TestKhmerSpellChecker(unittest.TestCase):
    """
    Unit test suite for Khmer Spelling & Writing Assistant engine.
    """

    def test_word_and_char_counter(self):
        text = "សួស្តី ពិភពលោក"
        words, chars = count_khmer_words_and_chars(text)
        self.assertEqual(words, 2)
        self.assertEqual(chars, len(text))

    def test_spelling_issue_detection(self):
        text = "សូមរៀបចំទិន្នន័យសំរាប់កិច្ចប្រជុំ"
        res = check_khmer_spelling(text)
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["summary"]["totalIssues"], 1)
        issue_originals = [i["original"] for i in res["issues"]]
        self.assertIn("សំរាប់", issue_originals)
        self.assertEqual(res["correctedText"], "សូមរៀបចំទិន្នន័យសម្រាប់កិច្ចប្រជុំ")

    def test_double_spaces_detection(self):
        text = "អត្ថបទនេះ  មានចន្លោះច្រើន"
        res = check_khmer_spelling(text)
        self.assertTrue(res["success"])
        issue_types = [i["type"] for i in res["issues"]]
        self.assertIn("spacing", issue_types)
        self.assertEqual(res["correctedText"], "អត្ថបទនេះ មានចន្លោះច្រើន")

    def test_punctuation_spacing_detection(self):
        text = "សូមអានអត្ថបទនេះ ។"
        res = check_khmer_spelling(text)
        self.assertTrue(res["success"])
        issue_types = [i["type"] for i in res["issues"]]
        self.assertIn("punctuation", issue_types)

    def test_protection_rules_for_urls_and_code(self):
        text = "សូមចូលទៅកាន់ https://example.com/សំរាប់ និងរត់កូដ `def checkout():`"
        res = check_khmer_spelling(text)
        self.assertTrue(res["success"])
        # Protected URL and code blocks should NOT flag 'សំរាប់' inside URL
        self.assertEqual(res["summary"]["totalIssues"], 0)

    def test_custom_dictionary_exclusion(self):
        text = "ប្រព័ន្ធនេះសំរាប់អតិថិជន"
        res = check_khmer_spelling(text, custom_dictionary=["សំរាប់"])
        self.assertTrue(res["success"])
        issue_originals = [i["original"] for i in res["issues"]]
        self.assertNotIn("សំរាប់", issue_originals)

    def test_empty_text_handling(self):
        res = check_khmer_spelling("")
        self.assertTrue(res["success"])
        self.assertEqual(res["summary"]["totalIssues"], 0)

if __name__ == "__main__":
    unittest.main()
