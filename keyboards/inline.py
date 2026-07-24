import os
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.localization import STRINGS, MODE_NAMES

def get_welcome_inline_keyboard(lang: str = "km") -> InlineKeyboardMarkup:
    """
    Build main menu inline keyboard per strict Telegram UX rules.
    Row 1: [💬 សួរ AI] [🖼 វិភាគរូបភាព]
    Row 2: [🎯 AI Modes] [🌐 Mini App]
    Row 3: [🌍 ភាសា] [ℹ️ ជំនួយ]
    Row 4: [🤖 អំពី Bot] [🔐 ឯកជនភាព]
    Row 5: [✕ បិទ Menu]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 សួរ AI" if lang == "km" else "💬 Ask AI", callback_data="cb_ask_ai")
    builder.button(text="🖼 វិភាគរូបភាព" if lang == "km" else "🖼 Analyze Image", callback_data="cb_analyze_image")
    builder.button(text="🎯 AI Modes", callback_data="cb_mode_menu")
    builder.button(text="🌐 Mini App", callback_data="cb_miniapp")
    builder.button(text="🌍 ភាសា" if lang == "km" else "🌍 Language", callback_data="cb_language")
    builder.button(text="ℹ️ ជំនួយ" if lang == "km" else "ℹ️ Help", callback_data="cb_help")
    builder.button(text="🤖 អំពី Bot" if lang == "km" else "🤖 About Bot", callback_data="cb_about")
    builder.button(text="🔐 ឯកជនភាព" if lang == "km" else "🔐 Privacy", callback_data="cb_privacy")
    builder.button(text="✕ បិទ Menu" if lang == "km" else "✕ Close Menu", callback_data="cb_close_menu")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def get_greeting_inline_keyboard(mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Inline keyboard for Greeting responses.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 សួរ AI", callback_data="cb_ask_ai")
    builder.button(text="🖼 វិភាគរូបភាព", callback_data="cb_analyze_image")
    builder.button(text="🎯 AI Modes", callback_data="cb_mode_menu")
    if mini_app_url:
        builder.button(text="🌐 Mini App", web_app=WebAppInfo(url=mini_app_url))
    else:
        builder.button(text="🌐 Mini App", callback_data="cb_miniapp")
    builder.button(text="ℹ️ ជំនួយ", callback_data="cb_help")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_mode_inline_keyboard(current_mode: str = "general", lang: str = "km") -> InlineKeyboardMarkup:
    """
    Build compact AI Operating Modes selection inline keyboard per prompt spec:
    🎯 ជ្រើសរើស AI Mode
    ━━━━━━━━━━━━━━━━━━
    [💬 General Assistant]
    [📐 Standard Math]
    [🇰🇭 Khmer Math]
    [🧪 Chemistry]
    [⚛️ Physics]
    [🖼 Image Analysis]
    [📧 Email Assistant]
    [← ត្រឡប់ក្រោយ]
    """
    builder = InlineKeyboardBuilder()
    
    modes_info = [
        ("general", "💬 General Assistant"),
        ("standard", "📐 Standard Math"),
        ("khmer_math", "🇰🇭 Khmer Math"),
        ("chemistry", "🧪 Chemistry"),
        ("physics", "⚛️ Physics"),
        ("image_analysis", "🖼 Image Analysis"),
        ("email", "📧 Email Assistant"),
    ]

    for mode_key, mode_label in modes_info:
        prefix = "✅ " if mode_key == current_mode else ""
        builder.button(text=f"{prefix}{mode_label}", callback_data=f"set_mode_{mode_key}")

    builder.button(text="← ត្រឡប់ក្រោយ" if lang == "km" else "← Back", callback_data="cb_back_main")
    builder.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return builder.as_markup()


def get_language_inline_keyboard(current_lang: str = "km") -> InlineKeyboardMarkup:
    """
    Build language selection inline keyboard per prompt spec:
    🌍 ជ្រើសរើសភាសា
    ━━━━━━━━━━━━━━━━━━
    [🇰🇭 ភាសាខ្មែរ]
    [🇬🇧 English]
    [🌐 Khmer + English]
    [← ត្រឡប់ក្រោយ]
    """
    builder = InlineKeyboardBuilder()
    p_km = "✅ " if current_lang == "km" else ""
    p_en = "✅ " if current_lang == "en" else ""
    p_kmen = "✅ " if current_lang == "km_en" else ""

    builder.button(text=f"{p_km}🇰🇭 ភាសាខ្មែរ", callback_data="set_lang_km")
    builder.button(text=f"{p_en}🇬🇧 English", callback_data="set_lang_en")
    builder.button(text=f"{p_kmen}🌐 Khmer + English", callback_data="set_lang_km_en")
    builder.button(text="← ត្រឡប់ក្រោយ", callback_data="cb_back_main")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def get_ai_result_contextual_keyboard(solution_id: str = "") -> InlineKeyboardMarkup:
    """
    Contextual buttons for text AI results per spec:
    [💬 ពន្យល់បន្ថែម] [🔁 បង្កើតម្ដងទៀត]
    [📋 ទម្រង់សាមញ្ញ] [🏠 Menu]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16] if solution_id else "def"
    builder.button(text="💬 ពន្យល់បន្ថែម", callback_data=f"ai_explain:{sid}")
    builder.button(text="🔁 បង្កើតម្ដងទៀត", callback_data=f"ai_regen:{sid}")
    builder.button(text="📋 ទម្រង់សាមញ្ញ", callback_data=f"ai_simple:{sid}")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2)
    return builder.as_markup()


def get_image_result_contextual_keyboard(solution_id: str = "") -> InlineKeyboardMarkup:
    """
    Contextual buttons for Image Analysis results per spec:
    [💬 សួរអំពីរូបនេះ]
    [🔁 វិភាគម្ដងទៀត]
    [🏠 Menu]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16] if solution_id else "def"
    builder.button(text="💬 សួរអំពីរូបនេះ", callback_data=f"img_ask:{sid}")
    builder.button(text="🔁 វិភាគម្ដងទៀត", callback_data=f"img_reanalyze:{sid}")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def get_math_answer_keyboard(solution_id: str = "", mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Contextual buttons for Math & Science formulas per spec:
    [📋 LaTeX Code] [💡 ពន្យល់ជំហាន]
    [🔁 ដោះស្រាយម្ដងទៀត] [🏠 Menu]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16] if solution_id else "def"
    builder.button(text="📋 LaTeX Code", callback_data=f"math_latex:{sid}")
    builder.button(text="💡 ពន្យល់ជំហាន", callback_data=f"math_steps:{sid}")
    builder.button(text="🔁 ដោះស្រាយម្ដងទៀត", callback_data=f"answer_retry:{sid}")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2)
    return builder.as_markup()


def get_image_analysis_banner_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard displayed with the initial Image Analysis banner.
    [✕ បោះបង់]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✕ បោះបង់", callback_data="cb_cancel_image_mode")
    builder.adjust(1)
    return builder.as_markup()


def get_error_retry_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for error messages:
    [🔁 សាកល្បងម្ដងទៀត] [🏠 Menu]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🔁 សាកល្បងម្ដងទៀត", callback_data="cb_retry_last")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2)
    return builder.as_markup()


def get_admin_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build admin panel inline keyboard.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 System Stats", callback_data="admin_stats")
    builder.button(text="📢 Broadcast", callback_data="admin_broadcast")
    builder.button(text="👥 Users List", callback_data="admin_users")
    builder.button(text="🤖 Change AI Model", callback_data="admin_change_model")
    builder.button(text="← Exit Admin", callback_data="cb_back_main")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_model_selection_keyboard(current_model: str) -> InlineKeyboardMarkup:
    """
    Build model selection inline keyboard for admin panel.
    """
    builder = InlineKeyboardBuilder()
    models = {
        "gemini-3.5-flash-lite": "3.5 Flash-Lite (Fast)",
        "gemini-3.6-flash": "3.6 Flash (All-around)",
        "gemini-3.1-pro-preview": "3.1 Pro (Advanced)",
        "gemini-omni-flash-preview": "Extended thinking"
    }
    for model_id, model_name in models.items():
        prefix = "✅ " if model_id == current_model else ""
        builder.button(text=f"{prefix}{model_name}", callback_data=f"set_model_{model_id}")
    builder.button(text="← Back to Admin", callback_data="cb_back_admin")
    builder.adjust(1, 1, 1, 1, 1)
    return builder.as_markup()


def get_requirements_navigation_keyboard(
    solution_id: str,
    current_page: int = 1,
    total_pages: int = 13,
    mini_app_url: str = ""
) -> InlineKeyboardMarkup:
    """
    Interactive Page Navigation inline keyboard for System Requirements.
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16]

    builder.button(text="📋 Overview", callback_data=f"req_overview:{sid}")
    builder.button(text="💎 Features", callback_data=f"req_features:{sid}")
    builder.button(text="👥 Roles", callback_data=f"req_roles:{sid}")
    builder.button(text="🔁 User Flows", callback_data=f"req_flows:{sid}")
    builder.button(text="🗄 Database", callback_data=f"req_database:{sid}")
    builder.button(text="🔌 API", callback_data=f"req_api:{sid}")

    prev_page = max(1, current_page - 1)
    next_page = min(total_pages, current_page + 1)
    builder.button(text="◀ Prev", callback_data=f"req_page:{prev_page}:{sid}")
    builder.button(text=f"📌 {current_page} / {total_pages}", callback_data=f"req_page:{current_page}:{sid}")
    builder.button(text="Next ▶", callback_data=f"req_page:{next_page}:{sid}")

    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2, 2, 3, 1)
    return builder.as_markup()


def get_image_gen_inline_keyboard(cache_id: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if cache_id:
        builder.button(text="📥 Download HD JPG", callback_data=f"img_dl_jpg:{cache_id[:16]}")
        builder.button(text="📥 Download PNG", callback_data=f"img_dl_png:{cache_id[:16]}")
    builder.button(text="🎨 Create Image", callback_data="cb_image_gen_new")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def get_image_download_keyboard(cache_id: str = "") -> InlineKeyboardMarkup:
    return get_image_gen_inline_keyboard(cache_id)
