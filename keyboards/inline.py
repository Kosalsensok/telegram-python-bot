import os
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from prompts.mode_prompts import MODE_DESCRIPTIONS

def get_welcome_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build main welcome inline keyboard.
    Row 1: [ 💬 Ask AI ] [ 🖼 Analyze Image ]
    Row 2: [ 🎯 AI Operating Modes ] [ 🌐 Telegram Mini App ]
    Row 3: [ 🌐 Language ] [ ℹ️ Help ]
    Row 4: [ 👤 About Bot ] [ 🔒 Privacy ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ask AI", callback_data="cb_ask_ai")
    builder.button(text="🖼 Analyze Image", callback_data="cb_analyze_image")
    builder.button(text="🎯 AI Modes (/mode)", callback_data="cb_mode_menu")
    builder.button(text="🌐 Mini App (/miniapp)", callback_data="cb_miniapp")
    builder.button(text="🌐 Language", callback_data="cb_language")
    builder.button(text="ℹ️ Help", callback_data="cb_help")
    builder.button(text="👤 About Bot", callback_data="cb_about")
    builder.button(text="🔒 Privacy", callback_data="cb_privacy")
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


def get_greeting_inline_keyboard(mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Phase 7 A & Phase 9: Dedicated inline keyboard for Greeting responses.
    Row 1: [ 💬 Ask AI ] [ 🖼 Analyze Image ]
    Row 2: [ 🎯 AI Modes ] [ 🌐 Mini App ]
    Row 3: [ ℹ️ Help ] [ 🏠 Menu ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ask AI", callback_data="cb_ask_ai")
    builder.button(text="🖼 Analyze Image", callback_data="cb_analyze_image")
    builder.button(text="🎯 AI Modes", callback_data="cb_mode_menu")
    if mini_app_url:
        builder.button(text="🌐 Mini App", web_app=WebAppInfo(url=mini_app_url))
    else:
        builder.button(text="🌐 Mini App", callback_data="cb_miniapp")
    builder.button(text="ℹ️ Help", callback_data="cb_help")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_mode_inline_keyboard(current_mode: str = "general") -> InlineKeyboardMarkup:
    """
    Build AI Operating Modes selection inline keyboard.
    """
    builder = InlineKeyboardBuilder()
    
    modes_info = [
        ("general", "🤖 General AI Mode"),
        ("standard", "📐 Standard LaTeX Mode"),
        ("khmer_math", "🇰🇭 Khmer Math Mode"),
        ("translate_khmer", "🌐 Translate to ខ្មែរ Mode"),
        ("tikz", "🎨 TikZ Diagram Mode"),
        ("pdf_to_text", "📄 PDF to Text Mode"),
        ("handwrite", "✍️ Handwrite to LaTeX Mode"),
    ]

    for mode_key, mode_label in modes_info:
        prefix = "✅ " if mode_key == current_mode else ""
        builder.button(text=f"{prefix}{mode_label}", callback_data=f"set_mode_{mode_key}")

    builder.button(text="⬅️ Back to Main Menu", callback_data="cb_back_main")
    builder.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return builder.as_markup()


def get_language_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build language selection inline keyboard.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🇰🇭 ភាសាខ្មែរ", callback_data="cb_lang_km")
    builder.button(text="🇬🇧 English", callback_data="cb_lang_en")
    builder.button(text="🌐 Auto Detect", callback_data="cb_lang_auto")
    builder.button(text="⬅️ Back", callback_data="cb_back_main")
    builder.adjust(2, 1, 1)
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
    builder.button(text="⬅️ Exit Admin", callback_data="cb_back_main")
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
        
    builder.button(text="⬅️ Back to Admin", callback_data="cb_back_admin")
    builder.adjust(1, 1, 1, 1, 1)
    return builder.as_markup()


def get_requirements_navigation_keyboard(
    solution_id: str,
    current_page: int = 1,
    total_pages: int = 13,
    mini_app_url: str = ""
) -> InlineKeyboardMarkup:
    """
    Requirement 5: Interactive Page Navigation inline keyboard for System Requirements.
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16]

    builder.button(text="📋 Overview", callback_data=f"req_overview:{sid}")
    builder.button(text="💎 Features", callback_data=f"req_features:{sid}")

    builder.button(text="👥 Roles", callback_data=f"req_roles:{sid}")
    builder.button(text="🔁 User Flows", callback_data=f"req_flows:{sid}")

    builder.button(text="🗄 Database", callback_data=f"req_database:{sid}")
    builder.button(text="🔌 API", callback_data=f"req_api:{sid}")

    builder.button(text="🎨 UI Screens", callback_data=f"req_ui:{sid}")
    builder.button(text="💻 Code", callback_data=f"req_code:{sid}")

    builder.button(text="🧪 Testing", callback_data=f"req_tests:{sid}")
    builder.button(text="🚀 Deployment", callback_data=f"req_deploy:{sid}")

    # Pagination controls
    prev_page = max(1, current_page - 1)
    next_page = min(total_pages, current_page + 1)
    builder.button(text="◀ Prev", callback_data=f"req_page:{prev_page}:{sid}")
    builder.button(text=f"📌 {current_page} / {total_pages}", callback_data=f"req_page:{current_page}:{sid}")
    builder.button(text="Next ▶", callback_data=f"req_page:{next_page}:{sid}")

    # Download & HD Card actions
    builder.button(text="🔍 HD Card", callback_data=f"answer_hd:{sid}")
    builder.button(text="📄 PDF", callback_data=f"answer_pdf:{sid}")
    builder.button(text="📦 ZIP Prototype", callback_data=f"req_download:{sid}")

    if mini_app_url:
        builder.button(text="🌐 Telegram Mini App", web_app=WebAppInfo(url=mini_app_url))

    builder.button(text="🏠 Menu", callback_data="cb_back_main")

    if mini_app_url:
        builder.adjust(2, 2, 2, 2, 2, 3, 3, 1, 1)
    else:
        builder.adjust(2, 2, 2, 2, 2, 3, 3, 1)
    return builder.as_markup()


def get_code_answer_keyboard(solution_id: str, mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Phase 9 Primary Keyboard for Programming Code Answers.
    Row 1: [ 📋 Copy Code ] [ 🧠 Explain ]
    Row 2: [ 📥 Download ]  [ 🔍 More Options ]
    Row 3: [ 🏠 Menu ]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16]

    builder.button(text="📋 Copy Code", callback_data=f"code_copy:{sid}")
    builder.button(text="🧠 Explain", callback_data=f"code_explain:{sid}")

    builder.button(text="📥 Download", callback_data=f"code_file:{sid}")
    builder.button(text="🔍 More Options", callback_data=f"code_more:{sid}")

    builder.button(text="🏠 Menu", callback_data="cb_back_main")

    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_code_secondary_keyboard(solution_id: str, mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Phase 9 Secondary Keyboard for Code Actions (opened via More Options).
    Row 1: [ 🔎 Full Code ] [ 🎓 Beginner ]
    Row 2: [ 📄 PDF ]       [ 🖼 HD View ]
    Row 3: [ 🌐 Mini App ]   [ ◀ Back ]
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16]

    builder.button(text="🔎 Full Code", callback_data=f"code_full:{sid}")
    builder.button(text="🎓 Beginner", callback_data=f"code_beginner:{sid}")

    builder.button(text="📄 PDF", callback_data=f"answer_pdf:{sid}")
    builder.button(text="🖼 HD View", callback_data=f"answer_hd:{sid}")

    if mini_app_url:
        builder.button(text="🌐 Mini App", web_app=WebAppInfo(url=mini_app_url))
    else:
        builder.button(text="🔄 Solve Again", callback_data=f"answer_retry:{sid}")

    builder.button(text="◀ Back", callback_data=f"code_back:{sid}")

    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_math_answer_keyboard(solution_id: str, mini_app_url: str = "") -> InlineKeyboardMarkup:
    """
    Requirement 14: Interactive Keyboard for Mathematics / Science solutions.
    """
    builder = InlineKeyboardBuilder()
    sid = solution_id[:16]

    builder.button(text="📄 Text", callback_data=f"math_text:{sid}")
    builder.button(text="🔍 HD Card", callback_data=f"answer_hd:{sid}")
    builder.button(text="📥 PDF", callback_data=f"answer_pdf:{sid}")
    builder.button(text="🔄 Solve Again", callback_data=f"answer_retry:{sid}")
    
    if mini_app_url:
        builder.button(text="🌐 Mini App", web_app=WebAppInfo(url=mini_app_url))
    builder.button(text="🏠 Menu", callback_data="cb_back_main")

    if mini_app_url:
        builder.adjust(2, 2, 1, 1)
    else:
        builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_solution_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Legacy solution keyboard compatibility wrapper.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 មើលជាអត្ថបទ", callback_data="cb_view_text")
    builder.button(text="🔍 រូបភាព HD", callback_data="cb_view_hd")
    builder.button(text="📥 ទាញយក PDF", callback_data="cb_download_pdf")
    builder.button(text="🔄 សាកល្បងម្តងទៀត", callback_data="cb_retry")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_image_gen_inline_keyboard(cache_id: str = "") -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to generated AI image outputs.
    """
    builder = InlineKeyboardBuilder()
    if cache_id:
        builder.button(text="📥 Download HD JPG", callback_data=f"img_dl_jpg:{cache_id[:16]}")
        builder.button(text="📥 Download PNG", callback_data=f"img_dl_png:{cache_id[:16]}")
    builder.button(text="🎨 Create Image", callback_data="cb_image_gen_new")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def get_image_download_keyboard(cache_id: str = "") -> InlineKeyboardMarkup:
    """
    Inline keyboard for image download options.
    """
    return get_image_gen_inline_keyboard(cache_id)

