import os
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.localization import STRINGS, MODE_NAMES

def get_welcome_inline_keyboard(lang: str = "km") -> InlineKeyboardMarkup:
    """
    Build compact 5-row main menu inline keyboard per user spec:
    Row 1: [ 💬 សួរ AI ] [ 🖼️ វិភាគរូបភាព ]
    Row 2: [ 🎙️ សំឡេងទៅជាអក្សរ ] [ 🗺️ បង្ហាញផ្លូវ & ទីតាំង ]
    Row 3: [ 🎯 AI Modes ] [ 🌐 Mini App ]
    Row 4: [ 💖 បរិច្ចាគ 2,000 ៛ ] [ ℹ️ ជំនួយ & អំពី Bot ]
    Row 5: [ 🔐 ឯកជនភាព ] [ ❌ បិទ Menu ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 សួរ AI" if lang == "km" else "💬 Ask AI", callback_data="cb_ask_ai")
    builder.button(text="🖼️ វិភាគរូបភាព" if lang == "km" else "🖼️ Analyze Image", callback_data="cb_analyze_image")
    
    builder.button(text="🎙️ សំឡេងទៅជាអក្សរ" if lang == "km" else "🎙️ Speech-to-Text", callback_data="cb_speech_to_text")
    builder.button(text="🗺️ បង្ហាញផ្លូវ & ទីតាំង" if lang == "km" else "🗺️ Navigation & Location", callback_data="cb_navigation")
    
    builder.button(text="🎯 AI Modes", callback_data="cb_mode_menu")
    builder.button(text="🌐 Mini App", callback_data="cb_miniapp")
    
    builder.button(text="💖 បរិច្ចាគ 2,000 ៛" if lang == "km" else "💖 Donate 2,000 KHR", callback_data="cb_donate")
    builder.button(text="ℹ️ ជំនួយ & អំពី Bot" if lang == "km" else "ℹ️ Help & About", callback_data="cb_about")
    
    builder.button(text="🔐 ឯកជនភាព" if lang == "km" else "🔐 Privacy", callback_data="cb_privacy")
    builder.button(text="❌ បិទ Menu" if lang == "km" else "❌ Close Menu", callback_data="cb_close_menu")
    
    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()


def get_greeting_inline_keyboard(mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Inline keyboard for Greeting responses (Clean 3-row layout).
    Row 1: [ 💬 សួរ AI ] [ 🖼️ វិភាគរូបភាព ]
    Row 2: [ 🎯 AI Modes ] [ 🌐 Mini App ]
    Row 3: [ ℹ️ ជំនួយ ] [ ❌ បិទ Menu ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 សួរ AI", callback_data="cb_ask_ai")
    builder.button(text="🖼️ វិភាគរូបភាព", callback_data="cb_analyze_image")
    builder.button(text="🎯 AI Modes", callback_data="cb_mode_menu")
    if mini_app_url:
        builder.button(text="🌐 Mini App", web_app=WebAppInfo(url=mini_app_url))
    else:
        builder.button(text="🌐 Mini App", callback_data="cb_miniapp")
    builder.button(text="ℹ️ ជំនួយ", callback_data="cb_help")
    builder.button(text="❌ បិទ Menu", callback_data="cb_close_menu")
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
    Contextual buttons for text AI results per full prompt spec:
    [👍 ចូលចិត្ត] [👎 មិនចូលចិត្ត] [🔄 បង្កើតម្ដងទៀត]
    [💬 ពន្យល់បន្ថែម] [📋 ទម្រង់សាមញ្ញ] [🏠 Menu]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16] if solution_id else "def"
    builder.button(text="👍 ចូលចិត្ត", callback_data=f"ai_like:{sid}")
    builder.button(text="👎 មិនចូលចិត្ត", callback_data=f"ai_dislike:{sid}")
    builder.button(text="🔄 បង្កើតម្ដងទៀត", callback_data=f"ai_regen:{sid}")
    builder.button(text="💬 ពន្យល់បន្ថែម", callback_data=f"ai_explain:{sid}")
    builder.button(text="📋 ទម្រង់សាមញ្ញ", callback_data=f"ai_simple:{sid}")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(3, 3)
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
    Build banner keyboard for image analysis mode per user spec:
    [ 🏠 Menu ដើម ]
    [ ❌ បិទ ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Menu ដើម", callback_data="cb_back_main")
    builder.button(text="❌ បិទ", callback_data="cb_close_menu")
    builder.adjust(1, 1)
    return builder.as_markup()


from config import RENDER_EXTERNAL_URL

def get_stt_banner_keyboard(mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Clean 100% User-Friendly guidance keyboard for Speech-to-Text mode per spec:
    [ 🎙️ បើក Mini App ថតសំឡេង ]
    [ 💬 សួរ AI ] | [ 🏠 Menu ដើម ]
    """
    builder = InlineKeyboardBuilder()
    
    target_url = mini_app_url or RENDER_EXTERNAL_URL or ""
    valid_webapp_url = ""
    if target_url and target_url.startswith("https://"):
        valid_webapp_url = f"{target_url.rstrip('/')}/answer/demo" if not target_url.endswith("/answer/demo") else target_url
        
    if valid_webapp_url:
        builder.button(text="🎙️ បើក Mini App ថតសំឡេង", web_app=WebAppInfo(url=valid_webapp_url))
    else:
        builder.button(text="🎙️ បើក Mini App ថតសំឡេង", callback_data="cb_miniapp")
    
    builder.button(text="💬 សួរ AI", callback_data="cb_ask_ai")
    builder.button(text="🏠 Menu ដើម", callback_data="cb_back_main")
    builder.adjust(1, 2)
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
    Interactive Page Navigation inline keyboard in clean Khmer per user spec:
    Row 1: [ 📋 សង្ខេប ] [ ✨ មុខងារ ]
    Row 2: [ 👥 តួនាទី ] [ 🔄 លំហូរការងារ ]
    Row 3: [ 🗄️ ទិន្នន័យ ] [ 🔌 API ]
    Row 4: [ ◀️ ថយក្រោយ ] [ 📌 1 / 13 ] [ ទៅមុខ ▶️ ]
    Row 5: [ 🏠 Menu ដើម ]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16]

    builder.button(text="📋 សង្ខេប", callback_data=f"req_overview:{sid}")
    builder.button(text="✨ មុខងារ", callback_data=f"req_features:{sid}")
    builder.button(text="👥 តួនាទី", callback_data=f"req_roles:{sid}")
    builder.button(text="🔄 លំហូរការងារ", callback_data=f"req_flows:{sid}")
    builder.button(text="🗄️ ទិន្នន័យ", callback_data=f"req_database:{sid}")
    builder.button(text="🔌 API", callback_data=f"req_api:{sid}")

    prev_page = max(1, current_page - 1)
    next_page = min(total_pages, current_page + 1)
    builder.button(text="◀️ ថយក្រោយ", callback_data=f"req_page:{prev_page}:{sid}")
    builder.button(text=f"📌 {current_page} / {total_pages}", callback_data=f"req_page:{current_page}:{sid}")
    builder.button(text="ទៅមុខ ▶️", callback_data=f"req_page:{next_page}:{sid}")

    builder.button(text="🏠 Menu ដើម", callback_data="cb_back_main")
    builder.adjust(2, 2, 2, 3, 1)
    return builder.as_markup()


def get_image_download_keyboard(cache_id: str = "", ratio_key: str = "1:1") -> InlineKeyboardMarkup:
    """
    Build keyboard for AI Image Generation download & aspect ratio options:
    Row 1: [📥 Download HD JPG] [📥 Download PNG]
    Row 2: [🎨 បង្កើតថ្មី] [🏠 Menu]
    """
    builder = InlineKeyboardBuilder()
    cid = cache_id[:16] if cache_id else "def"
    
    if cache_id:
        builder.button(text="📥 Download HD JPG", callback_data=f"img_dl_jpg:{cid}")
        builder.button(text="📥 Download PNG", callback_data=f"img_dl_png:{cid}")
    
    builder.button(text="🎨 បង្កើតថ្មី", callback_data="cb_image_gen_new")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    
    if cache_id:
        builder.adjust(2, 2)
    else:
        builder.adjust(2)
        
    return builder.as_markup()


def get_image_gen_inline_keyboard(cache_id: str = "", ratio_key: str = "1:1") -> InlineKeyboardMarkup:
    """Alias for get_image_download_keyboard for backward compatibility."""
    return get_image_download_keyboard(cache_id, ratio_key)
