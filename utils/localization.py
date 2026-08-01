# utils/localization.py
"""
Centralized Localization and Khmer Unicode String Manager for Smart AI Assistant Telegram Bot.
Supports Khmer (km), English (en), and Khmer+English (km_en).
"""
from typing import Dict, Any, Optional
from html import escape

DEFAULT_LANG = "km"

STRINGS: Dict[str, Dict[str, str]] = {
    "km": {
        "welcome_header": (
            "🧠 <b>SMART AI ASSISTANT</b> 🤖\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇰🇭 <b>ប្រព័ន្ធ AI ឆ្លាតវៃ បង្កើតឡើងដោយស្នាដៃកូនខ្មែរ 100%</b> 🇰🇭\n"
            "👑 <b>អ្នកបង្កើត (Creator):</b> <a href=\"https://t.me/kosalsensokpk\">@kosalsensokpk</a>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "welcome_intro": (
            "សួស្តី {name}! 👋\n"
            "ខ្ញុំជាជំនួយការ AI ឆ្លាតវៃ បង្កើតឡើងដោយកូនខ្មែរ សម្រាប់អត្ថបទ រូបភាព គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។\n"
            "🔗 អ្នកបង្កើត៖ https://t.me/kosalsensokpk"
        ),
        "menu_header": (
            "🧠 <b>SMART AI ASSISTANT</b> 🤖\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇰🇭 <b>ប្រព័ន្ធ AI ឆ្លាតវៃ បង្កើតឡើងដោយស្នាដៃកូនខ្មែរ 100%</b> 🇰🇭\n"
            "👑 <b>អ្នកបង្កើត (Creator):</b> <a href=\"https://t.me/kosalsensokpk\">@kosalsensokpk</a>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "ជំនួយការ AI សម្រាប់អត្ថបទ រូបភាព\n"
            "គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។"
        ),
        "btn_ask_ai": "💬 សួរ AI",
        "btn_analyze_image": "🖼 វិភាគរូបភាព",
        "btn_ai_modes": "🎯 AI Modes",
        "btn_miniapp": "🌐 Mini App",
        "btn_language": "🌍 ភាសា",
        "btn_help": "ℹ️ ជំនួយ",
        "btn_about": "🤖 អំពី Bot",
        "btn_privacy": "🔐 ឯកជនភាព",
        "btn_close_menu": "✕ បិទ Menu",
        "btn_back_main": "← ត្រឡប់ក្រោយ",
        "btn_explain_more": "💬 ពន្យល់បន្ថែម",
        "btn_regenerate": "🔁 បង្កើតម្ដងទៀត",
        "btn_simple_fmt": "📋 ទម្រង់សាមញ្ញ",
        "btn_main_menu": "🏠 Menu",
        "btn_ask_about_img": "💬 សួរអំពីរូបនេះ",
        "btn_reanalyze_img": "🔁 វិភាគម្ដងទៀត",
        "btn_latex_code": "📋 LaTeX Code",
        "btn_explain_steps": "💡 ពន្យល់ជំហាន",
        "btn_retry": "🔁 សាកល្បងម្ដងទៀត",
        "btn_cancel": "✕ បោះបង់",
        
        "loading_ai": "✨ កំពុងរៀបចំចម្លើយ...",
        "loading_vision": "🔍 កំពុងវិភាគរូបភាព...\nសូមរង់ចាំបន្តិច។",
        "menu_closed": "✅ Menu ត្រូវបានបិទ។",
        
        "image_mode_banner": (
            "🖼 <b>វិភាគរូបភាព</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            "សូមផ្ញើរូបភាពដែលអ្នកចង់ឱ្យ AI វិភាគ។\n\n"
            "AI អាចសម្គាល់៖\n"
            "• Screenshot\n"
            "• ឯកសារ\n"
            "• អត្ថបទ\n"
            "• តារាង\n"
            "• រូបមន្ត\n"
            "• ផលិតផល"
        ),
        "mode_title": "🎯 <b>ជ្រើសរើស AI Mode</b>\n━━━━━━━━━━━━━━━━━━",
        "lang_title": "🌍 <b>ជ្រើសរើសភាសា</b>\n━━━━━━━━━━━━━━━━━━",
        
        "error_header": "⚠️ <b>មិនអាចបំពេញសំណើបាន</b>\n━━━━━━━━━━━━━━━━━━\n\n",
        "error_timeout": "⚠️ ការឆ្លើយតបពី AI ប្រើពេលយូរពេក។ សូមព្យាយាមម្តងទៀត!",
        "error_image_invalid": "⚠️ រូបភាពមិនត្រឹមត្រូវ ឬមានទំហំធំពេក (អតិបរមា 10MB)។",
        "error_general": "⚠️ មានបញ្ហាបច្ចេកទេសមួយបានកើតឡើង។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ。"
    },
    "en": {
        "welcome_header": "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━",
        "welcome_intro": "Hello {name}! 👋\nI am your Smart AI Assistant for Text, Images, Mathematics, Physics, and Chemistry.",
        "menu_header": "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━\n\nAI Assistant for Text, Vision,\nMath, Physics, and Chemistry.",
        "btn_ask_ai": "💬 Ask AI",
        "btn_analyze_image": "🖼 Analyze Image",
        "btn_ai_modes": "🎯 AI Modes",
        "btn_miniapp": "🌐 Mini App",
        "btn_language": "🌍 Language",
        "btn_help": "ℹ️ Help",
        "btn_about": "🤖 About Bot",
        "btn_privacy": "🔐 Privacy",
        "btn_close_menu": "✕ Close Menu",
        "btn_back_main": "← Back",
        "btn_explain_more": "💬 Explain More",
        "btn_regenerate": "🔁 Regenerate",
        "btn_simple_fmt": "📋 Simple Format",
        "btn_main_menu": "🏠 Menu",
        "btn_ask_about_img": "💬 Ask About Image",
        "btn_reanalyze_img": "🔁 Re-analyze",
        "btn_latex_code": "📋 LaTeX Code",
        "btn_explain_steps": "💡 Explain Steps",
        "btn_retry": "🔁 Retry",
        "btn_cancel": "✕ Cancel",
        
        "loading_ai": "✨ Generating response...",
        "loading_vision": "🔍 Analyzing image...\nPlease wait a moment.",
        "menu_closed": "✅ Menu closed.",
        
        "image_mode_banner": (
            "🖼 <b>Image Analysis</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            "Please send the image you would like AI to analyze.\n\n"
            "AI can recognize:\n"
            "• Screenshots\n"
            "• Documents\n"
            "• Text\n"
            "• Tables\n"
            "• Formulas\n"
            "• Products"
        ),
        "mode_title": "🎯 <b>Select AI Mode</b>\n━━━━━━━━━━━━━━━━━━",
        "lang_title": "🌍 <b>Select Language</b>\n━━━━━━━━━━━━━━━━━━",
        
        "error_header": "⚠️ <b>Unable to complete request</b>\n━━━━━━━━━━━━━━━━━━\n\n",
        "error_timeout": "⚠️ AI response took too long. Please try again!",
        "error_image_invalid": "⚠️ Invalid image or size limit exceeded (max 10MB).",
        "error_general": "⚠️ A technical error occurred. Please try again later."
    }
}

MODE_NAMES: Dict[str, Dict[str, str]] = {
    "general": {"km": "💬 General Assistant", "en": "💬 General Assistant"},
    "standard": {"km": "📐 Standard Math", "en": "📐 Standard Math"},
    "khmer_math": {"km": "🇰🇭 Khmer Math", "en": "🇰🇭 Khmer Math"},
    "chemistry": {"km": "🧪 Chemistry", "en": "🧪 Chemistry"},
    "physics": {"km": "⚛️ Physics", "en": "⚛️ Physics"},
    "image_analysis": {"km": "🖼 Image Analysis", "en": "🖼 Image Analysis"},
    "email": {"km": "📧 Email Assistant", "en": "📧 Email Assistant"}
}

def get_str(key: str, lang: str = "km", **kwargs) -> str:
    """Retrieve string by key and language with optional keyword replacements."""
    lang_dict = STRINGS.get(lang, STRINGS["km"])
    text = lang_dict.get(key, STRINGS["km"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

def format_ai_result(
    title: str,
    answer: str,
    explanation: str = "",
    tips: str = "",
    header_title: str = ""
) -> str:
    """
    Format standard AI text response cleanly per Telegram spec:
    - Strips metadata overhead (🧠 SMART AI ASSISTANT, 📌 សង្ខេប, 🏷 Tags, 1️⃣ headers).
    - Formats sub-bullets and code explanations with clean line breaks (\n• ).
    """
    import re
    ans_strip = answer.strip()

    # Strip metadata overhead
    ans_strip = re.sub(r'🧠\s*\**SMART AI ASSISTANT\**\n?', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'📌\s*\**សង្ខេប\**.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'🏷️?\s*\**Tags\**.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'•\s*(?:CPP|CodeExplanation|Loops|AI|Programming)\b.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'1️⃣\s*\**\s*([^\n]+)', r'<b>\1</b>', ans_strip)
    ans_strip = re.sub(r'─{3,}', '───────────────', ans_strip)

    # Format arrow sub-bullets cleanly with line breaks
    ans_strip = re.sub(r'(?<=\S)\s*-\s*([a-zA-Z0-9_\s=<+]+)->\s*', r'\n• `\1` ➔ ', ans_strip)
    ans_strip = re.sub(r'(?<=\S)\s*-\s*', r'\n• ', ans_strip)

    # Convert **bold** to <b>bold</b> cleanly
    ans_strip = re.sub(r'\*\*([\s\S]+?)\*\*', r'<b>\1</b>', ans_strip)

    # Ensure clean line breaks before bullets
    ans_strip = re.sub(r'(?<=\S)\s*(•|\-)\s+', r'\n• ', ans_strip)

    res = ans_strip
    if explanation and "ព័ត៌មានលម្អិត" not in res and "ការដកស្រង់កូដ" not in res:
        exp_clean = re.sub(r'\*\*([\s\S]+?)\*\*', r'<b>\1</b>', explanation.strip())
        exp_clean = re.sub(r'(?<=\S)\s*(•|\-)\s+', r'\n• ', exp_clean)
        res += f"\n\n💻 <b>ការដកស្រង់កូដ និងអត្ថន័យ៖</b>\n{exp_clean}"

    if tips and "ចំណុចសំខាន់" not in res and "លទ្ធផល" not in res:
        tips_clean = re.sub(r'\*\*([\s\S]+?)\*\*', r'<b>\1</b>', tips.strip())
        tips_clean = re.sub(r'(?<=\S)\s*(•|\-)\s+', r'\n• ', tips_clean)
        res += f"\n\n💡 <b>ចំណុចសំខាន់ៗដែលត្រូវដឹង៖</b>\n{tips_clean}"

    return res.strip()

def format_image_analysis_result(
    detected_type: str,
    observation: str,
    answer: str,
    suggestion: str = ""
) -> str:
    """
    Format image analysis result cleanly per Telegram spec:
    - Converts **bold** to <b>bold</b> so Telegram HTML renders cleanly without raw **.
    - Strips top headers like '🧠 SMART AI ASSISTANT', '📌 សង្ខេប', '🏷 Tags', and raw technical jargon.
    - Ensures clean line breaks (\n• ) for all bullet points.
    """
    import re
    ans_strip = answer.strip()
    
    # Strip any stray headers and tags lines
    ans_strip = re.sub(r'🧠\s*\**SMART AI ASSISTANT\**\n?', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'🖼\s*\**IMAGE ANALYSIS\**\n?', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'📌\s*\**សង្ខេប៖\**.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'🏷\s*\**Tags:\**.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'•\s*TelegramMiniApp.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'•\s*SpeechToText.*?\n', '', ans_strip, flags=re.IGNORECASE)
    ans_strip = re.sub(r'•\s*LiveTranscription.*?\n', '', ans_strip, flags=re.IGNORECASE)

    # Convert **bold** to <b>bold</b> cleanly
    ans_strip = re.sub(r'\*\*([\s\S]+?)\*\*', r'<b>\1</b>', ans_strip)
    ans_strip = re.sub(r'\*([^\*]+)\*', r'<b>\1</b>', ans_strip)

    # Ensure clean line breaks before bullets and numbered items
    ans_strip = re.sub(r'(?<=\S)\s*(\-|\•|\*)\s+', r'\n• ', ans_strip)
    ans_strip = re.sub(r'(?<=\S)\s+(\d+\.\s+)', r'\n\1', ans_strip)

    # Clean any orphan asterisks
    ans_strip = re.sub(r'\*+', '', ans_strip)
    ans_strip = ans_strip.strip()

    if ans_strip.startswith("📝"):
        return ans_strip

    res = "📝 <b>លទ្ធផលនៃការវិភាគមុខងារ (UI Analysis)៖</b>\n\n"
    res += ans_strip
    if suggestion and "សំណើ" not in ans_strip and "ព័ត៌មានបន្ថែម" not in ans_strip:
        sug_clean = re.sub(r'\*\*([\s\S]+?)\*\*', r'<b>\1</b>', suggestion.strip())
        sug_clean = re.sub(r'(?<=\S)\s*(\-|\•|\*)\s+', r'\n• ', sug_clean)
        res += f"\n\n💡 <b>ចំណុចបន្ថែម៖</b>\n{sug_clean}"
    return res.strip()

