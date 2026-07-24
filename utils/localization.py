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
        "welcome_header": "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━",
        "welcome_intro": "សួស្តី {name}! 👋\nខ្ញុំជាជំនួយការ AI ឆ្លាតវៃ សម្រាប់អត្ថបទ រូបភាព គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។",
        "menu_header": "🧠 <b>SMART AI ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━\n\nជំនួយការ AI សម្រាប់អត្ថបទ រូបភាព\nគណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា។",
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
    header_title: str = "SMART AI ASSISTANT"
) -> str:
    """
    Format standard AI text response cleanly per Telegram spec:
    
    🧠 SMART AI ASSISTANT
    ━━━━━━━━━━━━━━━━━━

    📌 ប្រធានបទ
    [Short detected title]

    ✅ ចម្លើយ
    [Direct and useful answer]

    📖 ព័ត៌មានលម្អិត
    [Structured explanation]

    💡 គន្លឹះ
    [Optional recommendation]
    """
    res = f"🧠 <b>{header_title.upper()}</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    if title:
        res += f"📌 <b>ប្រធានបទ</b>\n{escape(title.strip())}\n\n"
    res += f"✅ <b>ចម្លើយ</b>\n{answer.strip()}\n"
    if explanation:
        res += f"\n📖 <b>ព័ត៌មានលម្អិត</b>\n{explanation.strip()}\n"
    if tips:
        res += f"\n💡 <b>គន្លឹះ</b>\n{tips.strip()}\n"
    return res.strip()

def format_image_analysis_result(
    detected_type: str,
    observation: str,
    answer: str,
    suggestion: str = ""
) -> str:
    """
    Format image analysis result cleanly per Telegram spec:
    
    🖼 IMAGE ANALYSIS
    ━━━━━━━━━━━━━━━━━━

    📌 ប្រភេទរូបភាព
    [Detected type]

    🔎 អ្វីដែលបានរកឃើញ
    [Concise observation]

    ✅ ចម្លើយ
    [Direct result]

    💡 សំណើ
    [Useful next step]
    """
    res = "🖼 <b>IMAGE ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    res += f"📌 <b>ប្រភេទរូបភាព</b>\n{escape(detected_type.strip())}\n\n"
    if observation:
        res += f"🔎 <b>អ្វីដែលបានរកឃើញ</b>\n{escape(observation.strip())}\n\n"
    res += f"✅ <b>ចម្លើយ</b>\n{answer.strip()}\n"
    if suggestion:
        res += f"\n💡 <b>សំណើ</b>\n{suggestion.strip()}\n"
    return res.strip()
