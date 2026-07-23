from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from prompts.mode_prompts import MODE_DESCRIPTIONS

def get_welcome_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build main welcome inline keyboard.
    Row 1: [ 💬 Ask AI ] [ 🖼 Analyze Image ]
    Row 2: [ 🎯 AI Operating Modes ] [ 🌐 Language ]
    Row 3: [ ℹ️ Help ] [ 👤 About Bot ] [ 🔒 Privacy ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ask AI", callback_data="cb_ask_ai")
    builder.button(text="🖼 Analyze Image", callback_data="cb_analyze_image")
    builder.button(text="🎯 AI Modes (/mode)", callback_data="cb_mode_menu")
    builder.button(text="🌐 Language", callback_data="cb_language")
    builder.button(text="ℹ️ Help", callback_data="cb_help")
    builder.button(text="👤 About Bot", callback_data="cb_about")
    builder.button(text="🔒 Privacy", callback_data="cb_privacy")
    builder.adjust(2, 2, 3)
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


def get_image_gen_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for generated AI image options.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🎨 បង្កើតរូបភាពផ្សេងទៀត (Generate Image)", callback_data="cb_prompt_draw")
    builder.button(text="⬅️ Back to Main", callback_data="cb_back_main")
    builder.adjust(1, 1)
    return builder.as_markup()


def get_image_download_keyboard(cache_id: str, current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """
    Build rich inline action keyboard for generated HD AI image:
    Row 1: [ 📥 Download JPG ] [ 🖼 Download PNG ]
    Row 2: [ 📐 1:1 ] [ 🖼 16:9 ] [ 📱 9:16 ] [ 🖥 4:3 ]
    Row 3: [ 🔄 Regenerate ] [ 🎨 New Image ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Download HD JPG", callback_data=f"dl_jpg:{cache_id}")
    builder.button(text="🖼 Download HD PNG", callback_data=f"dl_png:{cache_id}")

    ratios = [("1:1", "1:1"), ("16:9", "16:9"), ("9:16", "9:16"), ("4:3", "4:3")]
    for ratio_key, ratio_label in ratios:
        prefix = "✅ " if ratio_key == current_ratio else ""
        builder.button(text=f"{prefix}{ratio_label}", callback_data=f"img_ratio:{ratio_key}:{cache_id}")

    builder.button(text="🔄 បង្កើតឡើងវិញ (Regenerate)", callback_data=f"img_regen:{cache_id}")
    builder.button(text="🎨 បង្កើតរូបភាពថ្មី (New Image)", callback_data="cb_prompt_draw")

    builder.adjust(2, 4, 1, 1)
    return builder.as_markup()


def get_enhanced_image_download_keyboard(cache_id: str) -> InlineKeyboardMarkup:
    """
    Build inline action keyboard for enhanced Ultra HD image:
    Row 1: [ 📥 Download Ultra HD JPG ] [ 🖼 Download Ultra HD PNG ]
    Row 2: [ ✨ កែឲ្យច្បាស់បន្ថែមទៀត ] [ 🎨 បង្កើតរូបភាព AI ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Download HD JPG", callback_data=f"dl_jpg:{cache_id}")
    builder.button(text="🖼 Download HD PNG", callback_data=f"dl_png:{cache_id}")
    builder.button(text="✨ កែឲ្យច្បាស់បន្ថែម (Re-Enhance)", callback_data=f"enhance_again:{cache_id}")
    builder.button(text="🎨 បង្កើតរូបភាព AI (New Image)", callback_data="cb_prompt_draw")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def get_solution_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline action keyboard for rendered Math PNG Solution Cards:
    Row 1: [ 📄 មើលជាអត្ថបទ ] [ 🔍 រូបភាព HD ]
    Row 2: [ 📥 ទាញយក PDF ] [ 🔄 សាកល្បងម្តងទៀត ]
    Row 3: [ 🏠 Menu ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 មើលជាអត្ថបទ", callback_data="cb_view_text")
    builder.button(text="🔍 រូបភាព HD", callback_data="cb_view_hd")
    builder.button(text="📥 ទាញយក PDF", callback_data="cb_download_pdf")
    builder.button(text="🔄 សាកល្បងម្តងទៀត", callback_data="cb_retry")
    builder.button(text="🏠 Menu", callback_data="cb_back_main")
    builder.adjust(2, 2, 1)
    return builder.as_markup()
